#include "core.hpp"
#include "io.hpp"
#include "journal.hpp"
#include "csi.hpp"
#include "dataset.hpp"
#include "option_value.hpp"
#include "postprocess.hpp"
#include "lean_admission.hpp"
#include "exception_message.hpp"
#include "release_guard.hpp"
#ifdef POSE180_DEMO_PL_CSI
#include "pl_preprocess.hpp"
#endif
#ifdef POSE180_DEMO_PL_FILTER
#include "pl_filter.hpp"
#endif
#ifdef POSE180_DEMO_SDK
#include "runtime.hpp"
#include "hdmi_output.hpp"
#include "hdmi_renderer.hpp"
#include "display_state.hpp"
#ifdef POSE180_DEMO_PROBE_FREE_DRAIN
#include "startup_consumer.hpp"
#endif
#ifndef POSE180_DEMO_PROBE_FREE
#include "r9_startup_observer.hpp"
#include "r9_observer_mapping.hpp"
#endif
#endif
#include <csignal>
#include <cmath>
#include <fstream>
#include <iostream>
#include <sstream>
#include <map>
#include <sys/prctl.h>
#include <unistd.h>

namespace pd = pose180_demo;
namespace pp = pose180_pipeline;
namespace fs = std::filesystem;

namespace {
volatile std::sig_atomic_t stopping = 0;

void stop(int) {
	stopping = 1;
}

void need(bool ok, const char* why) {
	if (!ok)
		throw std::runtime_error(why);
}

// Retains the live control plane before a submitted operation's stack unwinds.
// Used for functional startup MMIO and for explicit no-SDK fault injection.
struct ActivityOwner {
	pd::Shared& shared;
	pp::ReleaseGuard activity;

	void retain() const noexcept {
		activity.retain_if_unproved([&](const char*) {
			shared.stats.release_blocked = true;
			shared.stats.isolated = true;
		});
	}

	~ActivityOwner() {
		retain();
	}
};

std::vector<std::uint64_t> parse_dataset_segments(
	const std::string& segment_sizes, const std::string& dataset_file) {
	std::vector<std::uint64_t> dataset_segments;
	if (!segment_sizes.empty()) {
		need(!dataset_file.empty() && segment_sizes.back() != ',',
			"Dataset segments require complete sizes and a file");
		std::istringstream entries(segment_sizes);
		std::string count;
		while (std::getline(entries, count, ',')) {
			const auto value = pd::unsigned_option(count, "--dataset-segment-frames", 9000);
			need(value > 0 && dataset_segments.size() < 9000, "Invalid dataset segments");
			dataset_segments.push_back(value);
		}
	}
	return dataset_segments;
}

struct ApplicationOptions {
	fs::path package;
	fs::path output;
	std::string bind;
	std::string csi_config;
	std::string dataset_file;
	std::uint64_t dataset_repetitions;
	std::vector<std::uint64_t> dataset_segments;
	std::uint64_t session;
	std::uint64_t seconds;
	std::uint64_t input_port;
	std::uint64_t result_port;
	std::uint64_t status_port;
	std::uint64_t max_age;
	bool hdmi;
	bool pl_renderer;
	bool mock;
	std::string preprocess_backend;
	std::string hardware_profile;
	std::string filter_backend;
	std::string single_stability;
	std::uint64_t view_port;
	pose::post::Config presentation_config;
	bool compare_ps;
#ifndef POSE180_DEMO_SDK
	std::uint64_t delay;
	std::uint64_t slow_at;
	std::uint64_t fail_at;
	std::uint64_t nonstandard_at;
	std::uint64_t unproved_at;
#endif
};

// 解析顺序与失败信息保持原样；这里只绑定监督信号，不创建 SDK 或显示资源。
ApplicationOptions parse_options(int argc, char** argv) {
	std::map<std::string, std::string> options;
	for (int i = 1; i < argc; i += 2) {
		need(i + 1 < argc, "Expected --option value");
		need(options.emplace(argv[i], argv[i + 1]).second, "Repeated option");
	}
	auto take = [&](const char* key, const std::string& fallback) {
		auto it = options.find(key);
		if (it == options.end())
			return fallback;
		auto v = it->second;
		options.erase(it);
		return v;
	};
	auto integer = [&](const char* key, const char* fallback, std::uint64_t maximum = UINT64_MAX) {
		return pd::unsigned_option(take(key, fallback), key, maximum);
	};
	auto real = [&](const char* key, const char* fallback) {
		return pd::real_option(take(key, fallback), key);
	};
	const auto supervisor = integer("--supervisor-pid", "0", std::numeric_limits<int>::max());
	if (supervisor) {
		// A lost supervisor requests the same graceful stop as a user.
		// Never send a fatal signal to an SDK owner with work in flight.
		need(::prctl(PR_SET_PDEATHSIG, SIGTERM) == 0, "Cannot bind supervisor lifetime");
		need(!stopping && unsigned(::getppid()) == supervisor, "Supervisor ended before initialization");
	}
	const fs::path package = take("--package", ".");
	const fs::path output = take("--output", "");
	const auto bind = take("--bind", "127.0.0.1");
	const auto csi_config = take("--csi", "");
	const auto dataset_file = take("--dataset", "");
	const auto dataset_repetitions = integer("--dataset-repetitions", "1", 30);
	const auto segment_sizes = take("--dataset-segment-frames", "");
	const auto dataset_segments = parse_dataset_segments(segment_sizes, dataset_file);
	const auto session = integer("--session", "0");
	const auto seconds = integer("--seconds", "60", UINT64_MAX / 1000000000ull);
	const auto input_port =
		integer("--input-port", csi_config.empty() && dataset_file.empty() ? "39382" : "0", 65535);
	const auto result_port = integer("--result-port", "39383", 65535);
	const auto status_port = integer("--status-port", "39384", 65535);
	const auto max_age = integer("--max-input-age-ms", "500", 60000) * 1000000ull;
	const auto hdmi_arg = take("--hdmi", "0");
	const bool hdmi = hdmi_arg == "1";
	const auto renderer_backend = take("--renderer-backend", "ps");
	need(renderer_backend == "ps" || renderer_backend == "pl", "Unknown renderer backend");
	const bool pl_renderer = renderer_backend == "pl";
	const auto preprocess_backend = take("--preprocess-backend", "ps");
	need(preprocess_backend == "ps" || preprocess_backend == "pl", "Unknown CSI preprocessing backend");
#ifndef POSE180_DEMO_PL_CSI
	need(preprocess_backend == "ps", "PL CSI requires matching hardware build");
#endif
#ifndef POSE180_DEMO_PL_OVERLAY
	need(!pl_renderer, "PL renderer requires the overlay hardware build");
#endif
#ifdef POSE180_DEMO_SDK
	constexpr bool mock = false;
#else
	constexpr bool mock = true;
	const auto delay = integer("--mock-delay-ms", "10", 60000);
	const auto slow_at = integer("--mock-slow-at", "0");
	const auto fail_at = integer("--mock-fail-at", "0");
	const auto nonstandard_at = integer("--mock-nonstandard-at", "0");
	const auto unproved_at = integer("--mock-unproved-at", "0");
	need(!hdmi, "Mock cannot access HDMI");
#endif
	const auto view_port = integer("--view-port", mock ? "0" : "39385", 65535);
#ifdef POSE180_DEMO_PROBE_FREE
#ifdef POSE180_DEMO_PROBE_FREE_DRAIN
#ifdef POSE180_DEMO_PL_FILTER
#ifdef POSE180_DEMO_PL_CSI
	const auto hardware_profile = take("--hardware-profile", "probe-free-drain-overlay-csi-v3");
	need(hardware_profile == "probe-free-drain-overlay-csi-v2" ||
			hardware_profile == "probe-free-drain-overlay-csi-v3",
		"Build/profile mismatch");
#elif defined(POSE180_DEMO_PL_OVERLAY)
	const auto hardware_profile = take("--hardware-profile", "probe-free-drain-overlay-v1");
	need(hardware_profile == "probe-free-drain-overlay-v1", "Build/profile mismatch");
#elif defined(POSE180_DEMO_PL_POST)
	const auto hardware_profile = take("--hardware-profile", "probe-free-drain-post-v2");
	need(hardware_profile == "probe-free-drain-post-v2", "Build/profile mismatch");
#else
	const auto hardware_profile = take("--hardware-profile", "probe-free-drain-filter-v1");
	need(hardware_profile == "probe-free-drain-filter-v1", "Build/profile mismatch");
#endif
#else
	const auto hardware_profile = take("--hardware-profile", "probe-free-drain-v1");
	need(hardware_profile == "probe-free-drain-v1", "Build/profile mismatch");
#endif
#else
	const auto hardware_profile = take("--hardware-profile", "legacy-probe-free");
	need(hardware_profile == "legacy-probe-free", "Build/profile mismatch");
#endif
#else
	const auto hardware_profile = take("--hardware-profile", "r45");
	if (hardware_profile == "pose-stabilizer-offline-v1")
		pose::post::require_lean_deployment_qualification(false);
	need(hardware_profile == "r45", "Unknown hardware profile");
#endif
	const auto filter_backend = take("--filter-backend", "cpu");
	pose::post::Config presentation_config;
	const auto top_k = integer("--top-k", "3", 3);
	need(top_k >= 1 && top_k <= 3, "Invalid TopK");
	presentation_config.top_k = unsigned(top_k);
	const auto single_stability = take("--single-person-stability", "0");
	need(single_stability == "0" || single_stability == "1", "Invalid single-person stability option");
	presentation_config.single_person_stability = single_stability == "1";
	need(!presentation_config.single_person_stability || (top_k == 1 && filter_backend == "cpu"),
		"Single-person stability requires CPU Top1");
	const auto score_threshold = take("--score-threshold", "0.2");
	if (score_threshold == "none")
		presentation_config.score_threshold.reset();
	else {
		std::size_t consumed = 0;
		const float cutoff = std::stof(score_threshold, &consumed);
		need(consumed == score_threshold.size() && std::isfinite(cutoff) && cutoff >= 0 && cutoff <= 1,
			"Invalid score threshold");
		presentation_config.score_threshold = cutoff;
	}
	presentation_config.min_cutoff = real("--min-cutoff", "0.5");
	presentation_config.beta = real("--beta", "0.3");
	presentation_config.d_cutoff = real("--d-cutoff", "1");
	need(std::isfinite(presentation_config.min_cutoff) && presentation_config.min_cutoff > 0 &&
			std::isfinite(presentation_config.beta) && presentation_config.beta >= 0 &&
			std::isfinite(presentation_config.d_cutoff) && presentation_config.d_cutoff > 0,
		"Invalid One Euro parameters");
	// Existing PL images retain their original fixed coefficients. Do not
	// silently run a different filter when the PS demonstration is tuned.
	need(filter_backend != "pl" ||
			(presentation_config.min_cutoff == 1 && presentation_config.beta == .5 &&
				presentation_config.d_cutoff == 1),
		"Existing PL backend requires the original 1/0.5/1 coefficients; use CPU for tuned filtering");
	const auto compare_arg = take("--compare-ps", "0");
	const bool compare_ps = compare_arg == "1";
	need((compare_arg == "0" || compare_arg == "1") && (!compare_ps || filter_backend == "pl"),
		"PS comparison requires PL backend");
#ifdef POSE180_DEMO_PL_FILTER
	need(filter_backend == "cpu" || filter_backend == "pl", "Unknown filter backend");
	need(hdmi || filter_backend == "cpu", "PL filter uses the single HDMI/SDK device owner");
#else
	need(filter_backend == "cpu", "PL backend requires the matching new hardware build");
#endif
	need(options.empty(), "Unknown option");
	need(session && session < 0xffffffffffff0000ull, "Explicit session required");
	need(view_port <= 65535 &&
			(!view_port || (view_port != input_port && view_port != result_port && view_port != status_port)),
		"Invalid presentation port");
	need(input_port <= 65535 && result_port > 0 && result_port <= 65535 && status_port > 0 &&
			status_port <= 65535,
		"Port out of range");
	need(result_port != status_port &&
			(!input_port || (input_port != result_port && input_port != status_port)),
		"Listeners require distinct ports");
	need(max_age > 0 && max_age <= 60000000000ull && (hdmi_arg == "0" || hdmi_arg == "1"),
		"Invalid age or HDMI option");
	need(csi_config.empty() || !input_port, "Use exactly one input adapter");
	need(dataset_file.empty() || (csi_config.empty() && !input_port),
		"Dataset excludes live CSI and TCP input");
	need(dataset_repetitions >= 1 && dataset_repetitions <= 30 &&
			(!dataset_file.empty() || dataset_repetitions == 1),
		"Dataset repetitions require an explicit bounded dataset");
	return {package, output, bind, csi_config, dataset_file, dataset_repetitions, dataset_segments, session,
		seconds, input_port, result_port, status_port, max_age, hdmi, pl_renderer, mock, preprocess_backend,
		hardware_profile, filter_backend, single_stability, view_port, presentation_config, compare_ps
#ifndef POSE180_DEMO_SDK
		,
		delay, slow_at, fail_at, nonstandard_at, unproved_at
#endif
	};
}

#ifdef POSE180_DEMO_PL_CSI
void record_csi_metrics(pd::Journal& journal, const pose_v1::CsiPlMetrics& m) {

	journal.status("{\"event\":\"csi_pl\",\"calls\":" + std::to_string(m.calls) + ",\"fallbacks\":" +
		std::to_string(m.software_fallbacks) + ",\"faults\":" + std::to_string(m.hardware_faults) +
		",\"boundary_fallbacks\":" + std::to_string(m.boundary_fallbacks) +
		",\"upload_ns\":" + std::to_string(m.upload_ns) + ",\"wait_ns\":" + std::to_string(m.wait_ns) +
		",\"download_ns\":" + std::to_string(m.download_ns) +
		",\"finish_ns\":" + std::to_string(m.finish_ns) + ",\"cycles\":" + std::to_string(m.compute_cycles) +
		",\"streamed_groups\":" + std::to_string(m.streamed_groups) +
		",\"groups_read_while_busy\":" + std::to_string(m.groups_read_while_busy) +
		",\"boundary_window_fallbacks\":" + std::to_string(m.boundary_window_fallbacks) + "}\n");
}
#endif

}

int main(int argc, char** argv) {
	std::signal(SIGINT, stop);
	std::signal(SIGTERM, stop);
	std::signal(SIGHUP, stop);
	// A dead stdout/stderr collector must not kill an in-flight SDK call.
	std::signal(SIGPIPE, SIG_IGN);
	fs::path cleanup_output;
	bool hardware_attempted = false;
	try {
		const auto options = parse_options(argc, argv);
		const auto& package = options.package;
		const auto& output = options.output;
		const auto& bind = options.bind;
		const auto& csi_config = options.csi_config;
		const auto& dataset_file = options.dataset_file;
		const auto& dataset_repetitions = options.dataset_repetitions;
		const auto& dataset_segments = options.dataset_segments;
		const auto& session = options.session;
		const auto& seconds = options.seconds;
		const auto& input_port = options.input_port;
		const auto& result_port = options.result_port;
		const auto& status_port = options.status_port;
		const auto& max_age = options.max_age;
		const auto& hdmi = options.hdmi;
		const auto& pl_renderer = options.pl_renderer;
		const auto& mock = options.mock;
		const auto& preprocess_backend = options.preprocess_backend;
		const auto& hardware_profile = options.hardware_profile;
		const auto& filter_backend = options.filter_backend;
		const auto& single_stability = options.single_stability;
		const auto& view_port = options.view_port;
		const auto& presentation_config = options.presentation_config;
		const auto& compare_ps = options.compare_ps;
#ifndef POSE180_DEMO_SDK
		const auto& delay = options.delay;
		const auto& slow_at = options.slow_at;
		const auto& fail_at = options.fail_at;
		const auto& nonstandard_at = options.nonstandard_at;
		const auto& unproved_at = options.unproved_at;
#endif
		need(!output.empty() && !fs::exists(output) && fs::create_directory(output),
			"Fresh output directory required");
		cleanup_output = output;

		// 共享状态先于各消费者创建；输入来源只用于诊断，不改变展示画面。
		pd::Shared shared;
		shared.stats.score_threshold = presentation_config.score_threshold;
		shared.stats.top_k = presentation_config.top_k;
		shared.stats.single_person_stability = presentation_config.single_person_stability;
		shared.stats.input_source = !dataset_file.empty() ? "official_dataset"
			: !csi_config.empty()						  ? "live_csi"
														  : "tcp_window";

		// 日志子进程必须先创建，避免 fork 继承 SDK 设备句柄和 IO／CSI 线程状态。
		pd::Journal journal(shared, output);
		pd::Io io(
			shared, bind, input_port, result_port, status_port, session, mock, hdmi, unsigned(view_port));
#ifndef POSE180_DEMO_SDK
		ActivityOwner mock_owner{shared, {}};
#endif
		pose::post::Postprocessor postprocessor(presentation_config);
		pose::post::Postprocessor ps_reference(presentation_config);
		journal.status("selection=top" + std::to_string(presentation_config.top_k) +
			"; strict_score_threshold=" +
			(presentation_config.score_threshold ? std::to_string(*presentation_config.score_threshold)
												 : std::string("none")) +
			"\n");
		journal.status("single_person_stability=" + single_stability + "\n");
		journal.status("presentation=tracked-one-euro-v5; requested_backend=" + filter_backend +
			"; min_cutoff=" + std::to_string(presentation_config.min_cutoff) +
			"; beta=" + std::to_string(presentation_config.beta) +
			"; d_cutoff=" + std::to_string(presentation_config.d_cutoff) +
			"; tracking_cutoff=3; velocity_cutoff=1; local_quality_gate=1; duplicate_centre=0.3; duplicate_pose=0.3; duplicate_translation=0.7; duplicate_shape=0.2; confirmation_hits=3; hold_ms=250; identity_ms=250; temporal_representative=1; shadow_support_margin=0.25; view_port=" +
			std::to_string(view_port) + "\n");
#ifdef POSE180_DEMO_PL_FILTER
		std::unique_ptr<pose::post::PlFilter> pl_filter;
		std::unique_ptr<pose::post::PlFilterBackend> pl_backend;
#endif

		// 参数校验已保证实时 CSI 与官方数据集互斥，两者写入同一个最新窗口槽。
		std::unique_ptr<pd::Csi> csi;
		if (!csi_config.empty())
			csi = std::make_unique<pd::Csi>(shared, csi_config, session);
		std::unique_ptr<pd::Dataset> dataset;
		if (!dataset_file.empty())
			dataset = std::make_unique<pd::Dataset>(
				shared, dataset_file, session, unsigned(dataset_repetitions), dataset_segments);
		std::cout << "RESIDENT_READY mock=" << mock << " recorder_pid=" << journal.child_pid() << std::endl;
#ifdef POSE180_DEMO_SDK
		std::unique_ptr<pp::Runtime> runtime;
		// Declared after Runtime: the callback is used only during infer(), and
		// this GP-only object owns no in-flight external memory.
#ifdef POSE180_DEMO_PL_CSI
		std::unique_ptr<pose_v1::PlPreprocess> pl_preprocess;
#endif
		std::unique_ptr<pose::hdmi::Output> display;
#ifndef POSE180_DEMO_PROBE_FREE
		std::unique_ptr<Mapping> mapping;
#endif
		pp::RuntimeShutdownGuard runtime_shutdown{runtime};
		ActivityOwner startup_owner{shared, {}};
		try {
			need(!stopping, "Stop requested before SDK initialization");
			hardware_attempted = true; // Includes functional startup MMIO before Runtime.
			pp::Config config;
			config.graph = package / "models/piw24_pose180_ZG.json";
			config.raw = package / "models/piw24_pose180_ZG.raw";
			config.evidence = output / "engine";
#ifdef POSE180_DEMO_PL_CSI
			if (preprocess_backend == "pl")
				config.preprocess = [&](const pose_v1::RawCsi& raw) {
					if (!pl_preprocess)
						pl_preprocess = std::make_unique<pose_v1::PlPreprocess>(hardware_profile);
					auto tokens = pl_preprocess->process(raw);
					record_csi_metrics(journal, pl_preprocess->metrics());
					return tokens;
				};
#endif
			config.on_release_blocked = [&](const char*) {
				shared.stats.release_blocked = true;
				shared.stats.isolated = true;
			};
			if (hdmi) {
#ifndef POSE180_DEMO_PROBE_FREE
				std::ifstream mode_file(package / "startup-mode.txt");
				std::string mode;
				mode_file >> mode;
				need(mode == "healthy" || mode == "consumed", "Fresh same-boot startup admission required");
				// The deployment guard checks boot_id and candidate/SDK identities.
				mapping = std::make_unique<Mapping>();
				auto read = [&](unsigned at) {
					return mapping->read(at);
				};
				auto write = [&](unsigned at, std::uint32_t n) {
					mapping->write(at, n);
				};
				auto persist = [&](const std::string& line) {
					journal.status(line);
				};
				pose::r9_startup::Observer observer(read, write, persist);
				auto before = observer.epoch("resident_before_Engine", 4, [] {
					std::this_thread::sleep_for(std::chrono::milliseconds(20));
				});
				need(mode == "consumed" ? pose::r9_startup::idle_after_drain(before, false)
										: pose::r9_startup::idle_healthy(before) && before.words[4] == 0,
					"Unhealthy pre-SDK return path");
#endif
				config.on_device_ready = [&](const icraft::xrt::Device& device) {
					display = std::make_unique<pose::hdmi::Output>(device, output / "hdmi.jsonl", &journal);
					display->verifyMemory();
#ifdef POSE180_DEMO_PL_FILTER
					if (filter_backend == "pl") {
						try {
							// Use the already established owner/Device register API.
							pl_filter = std::make_unique<pose::post::PlFilter>(
								hardware_profile,
								[device](unsigned offset) {
									need(offset <= 0x9f4 && !(offset & 3), "Filter read out of range");
									return std::uint32_t(
										device.defaultRegRegion().read(0x400b1000ull + offset));
								},
								[device](unsigned offset, std::uint32_t value) {
									need(offset <= 0x5f4 && !(offset & 3), "Filter write out of range");
									device.defaultRegRegion().write(0x400b1000ull + offset, value);
								});
							const auto lanes = pl_filter->lanes();
							need(lanes == 1 || lanes == 4, "Invalid filter lane identity");
							const auto tested = pose::post::verify_pl_filter(*pl_filter);
							const auto geometry_tested = pose::post::verify_pl_geometry(*pl_filter);
							pl_filter->reset_metrics();
							pl_backend = std::make_unique<pose::post::PlFilterBackend>(*pl_filter);
							postprocessor.set_backend(pl_backend.get());
							shared.stats.filter_lanes = lanes;
							journal.status("PL_FILTER_SELFTEST_PASS coordinates=" + std::to_string(tested) +
								" lanes=" + std::to_string(lanes) +
								" geometry_frames=" + std::to_string(geometry_tested) + "\n");
						} catch (const pose::post::PlFilterError& error) {
							++shared.stats.filter_fallbacks;
							postprocessor.set_backend(nullptr);
							if (pl_filter)
								pl_filter->reset_metrics();
							journal.status(
								std::string("PL_FILTER_ISOLATED CPU selected; ") + error.what() + "\n");
						}
					}
#endif
				};
#ifdef POSE180_DEMO_PROBE_FREE
#ifdef POSE180_DEMO_PROBE_FREE_DRAIN
				journal.status("hardware_profile=" + hardware_profile +
					"; passive_diagnostic_MMIO=0; functional_startup_control=0x400b0800\n");
				std::ofstream startup_record(output / "startup-consumer.jsonl");
				startup_owner.activity.begin("functional_startup_control");
				pd::startup_consumer::prepare([&](const std::string& line) {
					if (startup_record) {
						startup_record << line;
						startup_record.flush();
					}
					journal.status(line);
				});
				startup_owner.activity.complete();
#else
				// This build has no diagnostic CSR mapping. The deployment
				// guard binds the new BOOT and current boot_id; Output keeps
				// the functional ABI, idle, ownership and STOP/drain checks.
				journal.status("hardware_profile=probe_free; diagnostic_MMIO=0\n");
#endif
				need(!stopping, "Stop requested before SDK initialization");
				runtime = std::make_unique<pp::Runtime>(config);
#else
				auto initialized = observer.epoch("resident_Engine_apply", 6, [&] {
					runtime = std::make_unique<pp::Runtime>(config);
				});
				need(
					pose::r9_startup::return_path_healthy(initialized), "Initialization return path changed");
#endif
			} else
				runtime = std::make_unique<pp::Runtime>(config);
		} catch (...) {
			shared.stats.isolated = true;
			if (!startup_owner.activity.permitted())
				shared.stats.release_blocked = true;
			try {
				journal.status(
					std::string("SDK initialization isolated: ") + pp::current_exception_message() + "\n");
			} catch (...) {
			}
		}
		pose::hdmi::PreparedBackground canvas;
		// Metadata only: the reusable pixel vector stays in canvas, so holding
		// the last actual pose adds no full-frame cache or model output copy.
		pose::hdmi::Rendered last_picture;
		std::uint64_t last_picture_id = 0, last_picture_at = 0;
		pd::DisplayState presentation;
		bool overlay_background_ready = false;
		if (hdmi)
			canvas.rgb565.resize(pose::hdmi::frameBytes);
		auto show = [&](pose::hdmi::Rendered& rendered) {
			if (rendered.hardware_overlay && !overlay_background_ready) {
				auto static_background = pose::hdmi::prepare_background();
				display->show(static_background.rgb565, presentation.next_tag());
				overlay_background_ready = true;
			}
			const auto tag = presentation.next_tag();
			if (rendered.hardware_overlay) {
				display->show_overlay(rendered.commands, tag, rendered.render_ms);
				return tag;
			}
			display->begin_show(rendered.rgb565, tag);
			canvas.rgb565 = std::move(rendered.rgb565);
			// Same owner thread and adoption proof for hints and actual poses.
			while (!display->poll_show())
				std::this_thread::sleep_for(std::chrono::milliseconds(1));
			return tag;
		};
		auto show_wait = [&] {
			if (!hdmi || !display || shared.stats.isolated)
				return;
			const auto now = pd::now_ns();
			bool expired = false;
			unsigned kept = 0;
			for (unsigned i = 0; i < last_picture.detection_count; ++i) {
				const auto& d = last_picture.detections[i];
				if (now - last_picture_at > d.remaining_ns)
					expired = true;
				else
					last_picture.detections[kept++] = d;
			}
			last_picture.detection_count = kept;
			auto notice = presentation.hint(now, shared.stats.resynchronizing, shared.stats.isolated);
			if (expired)
				notice = pose::hdmi::Notice{
					pose::hdmi::NoticeKind::WaitingInput, true, shared.stats.resynchronizing, 0};
			if (!notice)
				return;
			if (!pl_renderer)
				pose::hdmi::prepare_background(canvas);
			auto rendered = pose::hdmi::render_notice(std::move(canvas),
				notice->has_result ? &last_picture : nullptr, last_picture_id, *notice, pl_renderer);
			const auto tag = show(rendered);
			presentation.adopted_hint(*notice, pd::now_ns());
			shared.stats.display_updates = presentation.updates();
			shared.stats.display_hints = presentation.hints();
			const char* state = notice->kind == pose::hdmi::NoticeKind::Stale ? "stale"
				: notice->kind == pose::hdmi::NoticeKind::Resynchronizing	  ? "resynchronizing"
																			  : "waiting_input";
			journal.status("{\"event\":\"hdmi_hint\",\"tag\":" + std::to_string(tag) + ",\"state\":\"" +
				state + "\"" + ",\"has_result\":" + (notice->has_result ? "true" : "false") +
				",\"result_age_seconds\":" + std::to_string(notice->age_seconds) +
				",\"resynchronizing\":" + (notice->resynchronizing ? "true" : "false") + "}\n");
		};
#endif
		const auto started = pd::now_ns();
		auto last_status = started;
		pd::Input input;
		pp::Result result;
		pd::Record record{};
		std::uint64_t sequence = 0;
		auto isolate = [&](const char* error) noexcept {
			shared.stats.forward_start = 0;
			shared.stats.isolated = true;
#ifdef POSE180_DEMO_SDK
			if (runtime && !runtime->release_permitted())
				shared.stats.release_blocked = true;
#else
			if (!mock_owner.activity.permitted())
				shared.stats.release_blocked = true;
#endif
			try {
				shared.input.clear();
				shared.output.clear();
				journal.freeze();
				journal.status(std::string("isolated: ") + error + "\n");
			} catch (...) {
			} // Diagnostics must not turn the original fault into terminate.
			// Keep listeners/status alive, never reopen or retry failed SDK.
		};
#ifdef POSE180_DEMO_SDK
		// Submit standby even when a dataset's first window is already ready.
		// It uses the same owner, fresh tag and adoption proof as later frames.
		try {
			show_wait();
		} catch (...) {
			isolate(pp::current_exception_message());
		}
#endif

		// 借用当前线程的资源处理一个完整窗口；过期结果只结束本次处理。
		const auto process_input = [&] {
			const auto began = pd::now_ns();
			shared.stats.forward_start = began;
			try {
#ifdef POSE180_DEMO_SDK
				runtime->infer(input.window, result);
#else
				const auto invocation = shared.stats.inferred.load();
				std::this_thread::sleep_for(
					std::chrono::milliseconds(slow_at && invocation + 1 == slow_at ? 1500 : delay));
				if (unproved_at && invocation + 1 == unproved_at) {
					mock_owner.activity.begin("mock_unproved_forward");
					throw 71;
				}
				if (nonstandard_at && invocation + 1 == nonstandard_at)
					throw 72;
				if (fail_at && invocation + 1 == fail_at)
					throw std::runtime_error("Injected mock SDK failure");
				result = {};
				result.frame_id = input.window.frame_id;
				result.source_time_ns = input.window.source_time_ns;
				result.invocation = invocation;
				result.input = pose_v1::preprocess(input.window.csi);
				result.scores.fill(0.5f);
				result.poses.fill(float(invocation % 100) / 100);
				result.selected_pose.fill(result.poses[0]);
				result.finite_outputs = true;
				result.process_ms = double(pd::now_ns() - began) / 1e6;
#endif
				const auto returned = pd::now_ns();
				shared.stats.forward_start = 0;
				pp::encode_full(
					record, result, input.epoch, ++sequence, input.arrived, began, returned, returned, 1);
				journal.record(record); // Complete first values before validity checks.
				need(result.finite_outputs && result.best_index < 180, "Invalid output isolated");
				++shared.stats.inferred;
				auto previous = shared.stats.last_result.exchange(returned);
				if (previous)
					shared.stats.longest_gap = std::max(shared.stats.longest_gap.load(), returned - previous);
				// Calls returning late are counted as real inference, not fresh display.
				if (returned - input.arrived > max_age || input.epoch != shared.stats.input_epoch) {
					++shared.stats.stale;
#ifdef POSE180_DEMO_SDK
					show_wait();
#endif
					return;
				}

				// PC 消费者独立取走副本；其发送速度不阻塞后处理与本地 HDMI。
				if (shared.output.put(record))
					++shared.stats.pc_dropped;
				const auto post_start = pd::now_ns();
				const pose::post::Identity view_id{
					input.epoch, result.frame_id, sequence, result.source_time_ns};
				pose::post::PresentationFrame view;
#ifdef POSE180_DEMO_PL_FILTER
				try {
					view = postprocessor.update(view_id, result.scores.data(), result.poses.data());
				} catch (const pose::post::PlFilterError& error) {
					shared.stats.filter_lanes = 0;
					++shared.stats.filter_fallbacks;
					postprocessor.set_backend(nullptr); // Discard partial frame; reconfirm on CPU.
					journal.status(std::string("PL_FILTER_ISOLATED CPU selected; ") + error.what() + "\n");
					view = postprocessor.update(view_id, result.scores.data(), result.poses.data());
				}
#else
				view = postprocessor.update(view_id, result.scores.data(), result.poses.data());
#endif
				const auto post_ns = pd::now_ns() - post_start;
				const auto& post_metrics = postprocessor.metrics();
				++shared.stats.post_frames;
				shared.stats.post_ns += post_ns;
				shared.stats.post_max_ns = std::max(shared.stats.post_max_ns.load(), post_ns);
				shared.stats.post_births = post_metrics.births;
				shared.stats.post_duplicates = post_metrics.duplicates;
				shared.stats.post_display_duplicates = post_metrics.display_duplicates;
				shared.stats.post_resets = post_metrics.resets;
				shared.stats.post_history_selections = post_metrics.history_selections;
				shared.stats.post_reacquired = post_metrics.reacquired;
				shared.stats.post_held_handoffs = post_metrics.held_handoffs;
				shared.stats.post_hidden_frames = post_metrics.hidden_frames;
				shared.stats.post_shadow_deferred = post_metrics.shadow_deferred;
				shared.stats.single_rejected = post_metrics.single_rejected;
				shared.stats.single_relocations = post_metrics.single_relocations;
				shared.stats.single_limited = post_metrics.single_limited;
				shared.stats.joint_gate_rejections = post_metrics.joint_gate_rejections;
				shared.stats.bone_gate_rejections = post_metrics.bone_gate_rejections;
				shared.stats.cpu_filter_frames = post_metrics.cpu_filter_frames;
				shared.stats.cpu_filter_coordinates = post_metrics.cpu_filter_coordinates;
				shared.stats.cpu_filter_ns = post_metrics.cpu_filter_ns;
				shared.stats.cpu_filter_max_ns = post_metrics.cpu_filter_max_ns;
#ifdef POSE180_DEMO_PL_FILTER
				if (pl_filter) {
					const auto& m = pl_filter->metrics();
					shared.stats.pl_filter_calls = m.calls;
					shared.stats.pl_filter_coordinates = m.coordinates;
					shared.stats.pl_input_ns = m.input_ns;
					shared.stats.pl_wait_ns = m.wait_ns;
					shared.stats.pl_output_ns = m.output_ns;
					shared.stats.pl_total_ns = m.total_ns;
					shared.stats.pl_max_ns = m.max_ns;
					shared.stats.pl_compute_cycles = m.compute_cycles;
					shared.stats.pl_max_cycles = m.max_cycles;
					const auto& g = pl_filter->geometry_metrics();
					shared.stats.pl_geometry_calls = g.calls;
					shared.stats.pl_geometry_input_ns = g.input_ns;
					shared.stats.pl_geometry_wait_ns = g.wait_ns;
					shared.stats.pl_geometry_output_ns = g.output_ns;
					shared.stats.pl_geometry_total_ns = g.total_ns;
					shared.stats.pl_geometry_max_ns = g.max_ns;
					shared.stats.pl_geometry_cycles = g.compute_cycles;
				}
				if (compare_ps && shared.stats.filter_lanes) {
					const auto begin = pd::now_ns();
					const auto reference =
						ps_reference.update(view_id, result.scores.data(), result.poses.data());
					const auto elapsed = pd::now_ns() - begin;
					++shared.stats.ps_reference_frames;
					shared.stats.ps_reference_ns += elapsed;
					shared.stats.ps_reference_max_ns =
						std::max(shared.stats.ps_reference_max_ns.load(), elapsed);
					const auto& m = ps_reference.metrics();
					shared.stats.ps_reference_filter_frames = m.cpu_filter_frames;
					shared.stats.ps_reference_filter_ns = m.cpu_filter_ns;
					shared.stats.ps_reference_filter_max_ns = m.cpu_filter_max_ns;
					shared.stats.ps_reference_filter_coordinates = m.cpu_filter_coordinates;
					bool mismatch = reference.poses.size() != view.poses.size();
					double error = 0;
					for (unsigned i = 0; i < std::min(reference.poses.size(), view.poses.size()); ++i) {
						const auto& a = reference.poses[i];
						const auto& b = view.poses[i];
						mismatch |= a.track != b.track || a.candidate != b.candidate || a.held != b.held;
						for (unsigned j = 0; j < 42; ++j)
							error = std::max(error, std::abs(double(a.joints[j]) - b.joints[j]));
					}
					shared.stats.reference_max_error_nano =
						std::max(shared.stats.reference_max_error_nano.load(),
							std::uint64_t(std::llround(error * 1e9)));
					if (mismatch || error > .001)
						++shared.stats.reference_mismatch_frames;
				}
#endif
				if (shared.presentation.put(view.json()))
					++shared.stats.view_dropped;
#ifdef POSE180_DEMO_SDK
				if (hdmi) {
					if (!pl_renderer)
						pose::hdmi::prepare_background(canvas);
					auto rendered = pose::hdmi::render_presentation(std::move(canvas), view, pl_renderer);
					show(rendered); // Prove adoption before another forward call.
					shared.stats.selected_count = rendered.detection_count;
					++shared.stats.selection_counts[rendered.detection_count];
					last_picture = std::move(rendered);
					last_picture_id = result.frame_id;
					const auto adopted = pd::now_ns();
					last_picture_at = adopted;
					presentation.adopted_result(adopted);
					++shared.stats.adopted;
					shared.stats.last_adopt = adopted;
					shared.stats.display_updates = presentation.updates();
				}
#endif
			} catch (...) {
				isolate(pp::current_exception_message());
			}
		};

		// 初始化结束后才放行输入；推理始终由当前线程串行执行。
		shared.stats.initialized = true;
		while (!stopping && (!seconds || pd::now_ns() - started < seconds * 1000000000ull)) {
			if (pd::now_ns() - last_status > 1000000000ull) {
				for (const auto& event : shared.stats.take_input_events())
					journal.diagnostic(event);
				journal.status(shared.stats.json(mock, hdmi));
				last_status = pd::now_ns();
			}
			if (shared.stats.isolated) {
				std::this_thread::sleep_for(std::chrono::milliseconds(5));
				continue;
			}

			// 只消费最新完整窗口。过期或旧轮次输入丢弃，不积压追赶。
			bool ready = shared.input.take(input);
			if (!ready && dataset && shared.stats.dataset_done) {
				ready = shared.input.take(input); // Pair EOF with a final pending-slot check.
				if (!ready)
					break;
			}
			if (ready &&
				(pd::now_ns() - input.arrived > max_age || input.epoch != shared.stats.input_epoch)) {
				++shared.stats.stale;
				ready = false;
			}
			if (!ready) {
#ifdef POSE180_DEMO_SDK
				try {
					show_wait();
				} catch (...) {
					isolate(pp::current_exception_message());
				}
#endif
				std::this_thread::sleep_for(std::chrono::milliseconds(5));
				continue;
			}

			process_input();
		}
		const auto active_elapsed_ns = pd::now_ns() - started;
		// Preserve status listeners/lease as well as SDK handles if hardware
		// release remains unproved. No completion receipt may follow this case.
#ifdef POSE180_DEMO_SDK
		startup_owner.retain();
		if (runtime)
			runtime->retain_if_unproved();
#else
		mock_owner.retain();
#endif

		// 先停止并回收输入线程，再关闭显示，最后销毁推理资源。
		shared.stop = true;
		csi.reset();
		dataset.reset();
#ifdef POSE180_DEMO_SDK
		// Output retains its unchanged tagged STOP/drain proof before any free.
		if (display) {
			display->close();
			display.reset();
		}
#ifdef POSE180_DEMO_PL_FILTER
		postprocessor.set_backend(nullptr);
		pl_backend.reset();
		pl_filter.reset();
#endif
		runtime.reset();
#endif
		for (const auto& event : shared.stats.take_input_events())
			journal.diagnostic(event);
		journal.status(shared.stats.json(mock, hdmi));

		// 只有 HDMI 完成 STOP／排空且 Runtime 已销毁，才能写安全退出回执。
		// 进程消失或状态轮询结束本身不能证明硬件资源可以释放。
		{
			std::ofstream done(output / "completion.json");
			done << "{\"native_shutdown_complete\":true,\"active_elapsed_ns\":" << active_elapsed_ns
				 << ",\"requested_seconds\":" << seconds << ",\"status\":" << shared.stats.json(mock, hdmi)
				 << "}\n";
		}
		std::cout << shared.stats.json(mock, hdmi);
		return shared.stats.isolated ? 3 : 0;
	} catch (...) {
		const char* error = pp::current_exception_message();
		// This catch runs after IO/CSI/Journal RAII teardown. A bind/config
		// failure before any hardware access can safely release its own alias.
		if (!hardware_attempted && !cleanup_output.empty())
			try {
				std::ofstream done(cleanup_output / "completion.json");
				done
					<< "{\"native_shutdown_complete\":true,\"failure_before_hardware\":true,\"status\":{\"state\":\"failed_before_hardware\"}}\n";
			} catch (...) {
			}
		try {
			std::cerr << "RESIDENT_STOP " << error << std::endl;
		} catch (...) {
		}
		return 1;
	}
}
