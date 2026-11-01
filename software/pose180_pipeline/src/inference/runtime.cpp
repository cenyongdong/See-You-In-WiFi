#include "runtime.hpp"
#include "release_guard.hpp"
#include <icraft-backends/zg330backend/zg330backend.h>
#include <icraft-backends/hostbackend/backend.h>
#include <icraft-xir/ops/ops.h>
#include <icraft-xrt/core/session.h>
#include <icraft-xrt/dev/host_device.h>
#include <icraft-xrt/dev/zg330_device.h>
#include <algorithm>
#include <atomic>
#include <chrono>
#include <cmath>
#include <cstring>
#include <exception>
#include <fstream>
#include <iomanip>
#include <limits>
#include <map>
#include <ostream>
#include <set>
#include <sstream>
#include <stdexcept>
#include <streambuf>
#include <thread>
#include <vector>

namespace pose180_pipeline {
namespace {
namespace fs = std::filesystem;
namespace xir = icraft::xir;
using namespace icraft::xrt;
using Clock = std::chrono::steady_clock;

void require(bool yes, const std::string& message) {
	if (!yes)
		throw std::runtime_error(message);
}

double elapsed(Clock::time_point start) {
	return std::chrono::duration<double, std::milli>(Clock::now() - start).count();
}

std::string quote(const std::string& value) {
	std::ostringstream out;
	out << '"';
	for (unsigned char c : value) {
		if (c == '"' || c == '\\')
			out << '\\' << c;
		else if (c < 32)
			out << "\\u" << std::hex << std::setw(4) << std::setfill('0') << unsigned(c) << std::dec;
		else
			out << c;
	}
	return out.str() + '"';
}

void bytes_file(const fs::path& path, const char* bytes, std::size_t size) {
	std::ofstream out(path, std::ios::binary);
	require(bool(out), "Cannot open evidence " + path.string());
	out.write(bytes, static_cast<std::streamsize>(size));
	out.flush();
	require(bool(out), "Cannot preserve evidence " + path.string());
}

void text_file(const fs::path& path, const std::string& text) {
	bytes_file(path, text.data(), text.size());
}

bool shape(const xir::TensorType& type, std::initializer_list<int64_t> expected) {
	return type->element_dtype.isFP32() && type->shape.size() == expected.size() &&
		std::equal(type->shape.begin(), type->shape.end(), expected.begin());
}

std::atomic_flag runtime_owned = ATOMIC_FLAG_INIT;

struct RuntimeLease {
	RuntimeLease() {
		require(!runtime_owned.test_and_set(), "Exactly one SDK Runtime is permitted per process");
	}

	~RuntimeLease() {
		runtime_owned.clear();
	}

	RuntimeLease(const RuntimeLease&) = delete;
	RuntimeLease& operator=(const RuntimeLease&) = delete;
};

// Preserve the validated public dump(..., "SFB") transformation. This stream
// changes only application storage, never hardware layout, dtype or SDK reads.
// A spare byte detects an overlength dump without growing the buffer.
template <std::size_t Bytes> class FixedDumpBuffer final : public std::streambuf {
public:
	FixedDumpBuffer() {
		reset();
	}

	void reset() {
		setp(bytes_.data(), bytes_.data() + bytes_.size());
	}

	std::size_t written() const {
		return static_cast<std::size_t>(pptr() - pbase());
	}

	const char* data() const {
		return bytes_.data();
	}

private:
	std::array<char, Bytes + 1> bytes_{};
};

template <std::size_t Bytes> void dump_first(const Tensor& tensor, FixedDumpBuffer<Bytes>& buffer) {
	buffer.reset();
	std::ostream stream(&buffer);
	tensor.dump(stream, "SFB");
	require(bool(stream) && buffer.written() == Bytes,
		"Actual first output SFB length differs: copied=" + std::to_string(buffer.written()) +
			"; expected=" + std::to_string(Bytes));
}

// Derive completion from the actual applied graph. Do not substitute any count
// from the old TopK/Gather graph or equate forward() return with hardware finish.
uint32_t validate_fusion(const Session& session, const xir::Network& graph, const fs::path& output) {
	std::set<int64_t> originals, covered;
	for (const auto& op : graph->ops)
		if (op.is<xir::HardOp>())
			originals.insert(op->op_id);
	std::map<int, int> spans;
	std::ofstream evidence(output / "fusion.jsonl");
	require(bool(evidence), "Cannot open fusion evidence");
	auto bindings = session.backendBindings();
	std::size_t groups = 0, host_ports = 0;
	for (const auto& item : bindings) {
		if (item.second.is<HostBackend>()) {
			auto op = graph.getOpById(item.first);
			require(op.is<xir::Input>() || op.is<xir::Output>(), "Unexpected Host compute binding");
			++host_ports;
			continue;
		}
		require(item.second.is<zg330::ZG330Backend>(), "Unexpected backend binding");
		auto info = item.second.cast<zg330::ZG330Backend>()->forward_info;
		require(info.defined(), "Missing actual ZG metadata");
		auto found = info->hardop_map.find(item.first);
		require(found != info->hardop_map.end() && found->second.defined(), "Missing fused member metadata");
		auto entry = found->second;
		require(entry->net_hardop.defined() && entry->net_hardop->op_id == item.first,
			"Fused node identity differs");
		auto sync = info->idx_map.find(item.first);
		require(
			sync != info->idx_map.end() && sync->second == entry->sync_idx, "Completion metadata differs");
		require(sync->second.first >= 0 && sync->second.second > 0 && spans.emplace(sync->second).second,
			"Invalid or repeated completion interval");
		std::vector<int64_t> members(entry->merge_from.begin(), entry->merge_from.end());
		if (members.empty())
			members.push_back(item.first);
		evidence << "{\"group\":" << item.first << ",\"sync_start\":" << sync->second.first
				 << ",\"layer_count\":" << sync->second.second << ",\"members\":[";
		for (std::size_t i = 0; i < members.size(); ++i) {
			if (i)
				evidence << ',';
			evidence << members[i];
			require(originals.count(members[i]) && covered.insert(members[i]).second,
				"Invalid/repeated original HardOp member");
		}
		evidence << "]}\n";
		++groups;
	}
	evidence.flush();
	require(bool(evidence), "Cannot preserve fusion evidence");
	require(covered == originals && host_ports == 2 && groups > 0, "Incomplete graph ownership");
	uint32_t next = 0;
	for (const auto& span : spans) {
		require(uint32_t(span.first) == next, "Gap or overlap in runtime completion intervals");
		next += uint32_t(span.second);
	}
	require(next > 0 && next < 100000, "Invalid final completion count");
	text_file(output / "fusion-summary.json",
		"{\"hardops\":" + std::to_string(originals.size()) + ",\"groups\":" + std::to_string(groups) +
			",\"host_compute\":0,\"host_ports\":2,\"final_count\":" + std::to_string(next) +
			",\"coverage_complete\":true}\n");
	return next;
}
} // namespace

struct Runtime::Impl {
	RuntimeLease lease;
	const std::thread::id owner = std::this_thread::get_id();
	const Config config;
	// Reverse destruction order retains Device until Tensor and Session die.
	xir::Network graph;
	Device device;
	Session session;
	Tensor input_tensor;
	// Preserve returned handles even if forward validation/final waiting throws.
	// A local vector would unwind before the failure handler can retain them.
	std::vector<Tensor> forward_inputs, outputs;
	ReleaseGuard activity;
	FixedDumpBuffer<candidate_count * sizeof(float)> score_dump;
	FixedDumpBuffer<pose_values * sizeof(float)> pose_dump;
	uint32_t final_count = 0;
	uint64_t npu_calls = 0, host_compute_calls = 0, next_invocation = 0;
	bool failed = false, evidence_ready = false;
	double initialized_ms = 0;
	std::string identity;

	explicit Impl(const Config& value) : config(value) {
	}

	// Impl is already fully constructed: initialization exceptions therefore
	// pass through its guarded destructor before any device members unwind.
	void initialize() {
		const auto start = Clock::now();
		try {
			require(!config.graph.empty() && !config.raw.empty() && !config.evidence.empty(),
				"Graph, raw and fresh evidence paths are required");
			if (fs::exists(config.evidence))
				require(fs::is_directory(config.evidence) && fs::is_empty(config.evidence),
					"Preserve existing runtime evidence");
			else
				require(fs::create_directory(config.evidence), "Cannot create runtime evidence directory");
			evidence_ready = true;
			identity = "\"graph\":" + quote(config.graph.string()) + ",\"raw\":" + quote(config.raw.string());
			require(
				fs::is_regular_file(config.graph) && fs::is_regular_file(config.raw), "Graph/raw missing");
			identity += ",\"graph_bytes\":" + std::to_string(fs::file_size(config.graph)) +
				",\"raw_bytes\":" + std::to_string(fs::file_size(config.raw));
			graph = xir::Network::CreateFromJsonFile(config.graph.string());
			require(graph->icraft_version == "v3.39.0" && !graph->swap_mode, "Graph version/swap differs");
			auto in = graph.inputs(), out = graph.outputs();
			require(in.size() == 1 && out.size() == 2 && shape(in[0].tensorType(), {1, 180, 60}) &&
					shape(out[0].tensorType(), {1, 180}) && shape(out[1].tensorType(), {1, 180, 14, 3}),
				"180-query graph ports differ");
			for (const auto& op : graph->ops)
				require(op.is<xir::HardOp>() || op.is<xir::Input>() || op.is<xir::Output>(),
					"Host compute/TopK remains");
			graph.lazyLoadParamsFromFile(config.raw.string());
			activity.begin("SDK_initialization");
			device = Device::Open("axi://zg330aiu?npu=0x40000000&dma=0x80000000");
			device.setWaitTime(10000);
			const auto version = device.version();
			const auto device_id = version.count("device") ? version.at("device") : "<missing>";
			const auto icore_id = version.count("icore") ? version.at("icore") : "<missing>";
			identity += ",\"device\":" + quote(device_id) + ",\"icore\":" + quote(icore_id) +
				",\"icraft_version\":" + quote(graph->icraft_version);
			require(device_id == "25122301" && icore_id == "FMSHZGV3TECH-AID - 24160628",
				"Actual device/icore identity differs: device=" + device_id + "; icore=" + icore_id);
			session = Session::Create<zg330::ZG330Backend, HostBackend>(
				graph.view(), {device, HostDevice::Default()});
			session.enableTimeProfile(false);
			session.apply();
			activity.complete(); // apply returned normally; no forward was issued.
			final_count = validate_fusion(session, graph, config.evidence);
			session.setPostCallBack([this](const Session&, const xir::Operation& op, const Backend& backend,
										std::vector<Tensor>&) {
				assert_owner();
				if (backend.is<zg330::ZG330Backend>())
					++npu_calls;
				else if (!op.is<xir::Input>() && !op.is<xir::Output>())
					++host_compute_calls;
			});
			input_tensor = Tensor(in[0]).mallocOn(HostDevice::MemRegion());
			forward_inputs.push_back(input_tensor);
			if (config.on_device_ready) {
				activity.begin("device_ready_callback"); // May perform synchronous SDK memory IO.
				config.on_device_ready(device);
				activity.complete();
			}
			initialized_ms = elapsed(start);
			text_file(config.evidence / "initialized.json",
				"{" + identity + ",\"initialization_ms\":" + std::to_string(initialized_ms) +
					",\"final_count\":" + std::to_string(final_count) +
					",\"host_compute\":0,\"input_tensor_reused\":true,\"application_dump_storage_reused\":true}\n");
		} catch (const std::exception& e) {
			preserve_failure("initialization", e.what(), nullptr, nullptr);
			throw;
		} catch (...) {
			preserve_failure("initialization", "Non-standard SDK exception", nullptr, nullptr);
			throw;
		}
	}

	~Impl() {
		// A wrong-thread destructor must not silently release SDK handles there.
		if (owner != std::this_thread::get_id())
			activity.begin("wrong_owner_thread");
		retain_if_unproved();
		if (session.defined()) {
			try {
				session.setPostCallBack(Session::CallBackFunc{});
			} catch (...) {
			}
		}
	}

	void retain_if_unproved() const noexcept {
		activity.retain_if_unproved([&](const char* stage) {
			if (config.on_release_blocked)
				config.on_release_blocked(stage);
		});
	}

	void assert_owner() const {
		require(owner == std::this_thread::get_id(), "SDK operation attempted outside its owning thread");
	}

	void preserve_failure(const std::string& stage, const std::string& error, const Window* window,
		const Result* result) noexcept {
		failed = true;
		if (!evidence_ready)
			return;
		// Independent best-effort saves must not mask the original SDK error.
		auto save = [](auto&& task) {
			try {
				task();
			} catch (...) {
			}
		};
		if (window)
			save([&] {
				bytes_file(config.evidence / "failed-raw-csi.bin",
					reinterpret_cast<const char*>(window->csi.data()), sizeof(window->csi));
			});
		if (result)
			save([&] {
				bytes_file(config.evidence / "failed-input.f32",
					reinterpret_cast<const char*>(result->input.data()), sizeof(result->input));
			});
		save([&] {
			bytes_file(
				config.evidence / "failed-first-scores.sfb.bin", score_dump.data(), score_dump.written());
		});
		save([&] {
			bytes_file(config.evidence / "failed-first-poses.sfb.bin", pose_dump.data(), pose_dump.written());
		});
		save([&] {
			text_file(config.evidence / "failure.json",
				"{" + (identity.empty() ? std::string{} : identity + ',') + "\"stage\":" + quote(stage) +
					",\"invocation\":" + std::to_string(next_invocation) +
					",\"frame_id\":" + std::to_string(window ? window->frame_id : 0) +
					",\"source_time_ns\":" + std::to_string(window ? window->source_time_ns : 0) +
					",\"error\":" + quote(error) +
					",\"score_dump_bytes\":" + std::to_string(score_dump.written()) +
					",\"pose_dump_bytes\":" + std::to_string(pose_dump.written()) +
					",\"release_permitted\":" + (activity.permitted() ? "true" : "false") +
					",\"pending_stage\":" + quote(activity.stage()) +
					",\"automatic_retry\":false,\"late_output_reread\":false}\n");
		});
	}

	void infer(const Window& window, Result& result) {
		assert_owner();
		require(!failed, "Runtime stopped after its first failure; automatic retry forbidden");
		const auto start = Clock::now();
		const char* stage = "preprocess";
		score_dump.reset();
		pose_dump.reset();
		result.frame_id = window.frame_id;
		result.source_time_ns = window.source_time_ns;
		result.invocation = next_invocation;
		result.finite_outputs = false;
		result.best_index = 0;
		result.selected_pose.fill(0);
		result.input.fill(0);
		try {
			result.input = config.preprocess ? config.preprocess(window.csi) : pose_v1::preprocess(window.csi);
			result.preprocess_ms = elapsed(start);

			stage = "input_write";
			auto begin = Clock::now();
			// This pool slot owns mutable input bytes; no temporary tensor or
			// const_cast is needed for the public write(char*) API.
			activity.begin("input_write");
			input_tensor.write(0, reinterpret_cast<char*>(result.input.data()), sizeof(result.input));
			activity.complete(); // Public synchronous host input write returned.
			result.prepare_ms = elapsed(begin);

			stage = "status_clear";
			begin = Clock::now();
			activity.begin("status_clear");
			result.before_clear = device.cast<ZG330Device>().layerCount();
			device.reset(1);
			result.before_forward = device.cast<ZG330Device>().layerCount();
			require(result.before_forward == 0,
				"Status-only frame clear did not reach zero: actual=" +
					std::to_string(result.before_forward));
			activity.complete();
			result.state_clear_ms = elapsed(begin);

			// 标记在途后才调用 SDK；异常路径保留该状态，禁止提前释放资源。
			npu_calls = 0;
			host_compute_calls = 0;
			stage = "forward";
			begin = Clock::now();
			outputs.clear(); // Previous invocation was proved complete.
			activity.begin("forward_or_final_wait");
			outputs = session.forward(forward_inputs);
			result.forward_ms = elapsed(begin);
			require(outputs.size() == 2, "Runtime output count differs");

			// 原生输出等待和实际图层计数必须同时满足，ready 标志不能单独作为释放证明。
			stage = "native_final_wait";
			begin = Clock::now();
			for (const auto& tensor : outputs) {
				require(
					tensor.waitForReady(std::chrono::milliseconds(10000)), "Native final output wait failed");
				require(tensor.isReady(), "Final tensor not ready after native final wait");
			}
			result.final_wait_ms = elapsed(begin);
			result.completed_layers = device.cast<ZG330Device>().layerCount();
			result.zg_callbacks = static_cast<std::size_t>(npu_calls);
			result.host_callbacks = static_cast<std::size_t>(host_compute_calls);
			require(result.completed_layers == final_count,
				"Runtime final completion count differs: actual=" + std::to_string(result.completed_layers) +
					"; expected=" + std::to_string(final_count));
			require(npu_calls > 0 && host_compute_calls == 0, "Unexpected actual Host computation");
			activity.complete(); // Both native waits AND actual graph count passed.

			stage = "first_output_dump";
			begin = Clock::now();
			activity.begin("first_output_dump");
			dump_first(outputs[0], score_dump);
			std::memcpy(result.scores.data(), score_dump.data(), sizeof(result.scores));
			dump_first(outputs[1], pose_dump);
			std::memcpy(result.poses.data(), pose_dump.data(), sizeof(result.poses));
			activity.complete();
			result.output_ms = elapsed(begin);

			// 首次读取的分数和姿态已保存到本帧；后续校验失败也不重读或修补 SDK 输出。
			begin = Clock::now();
			bool finite = true;
			float best_score = -std::numeric_limits<float>::infinity();
			for (std::size_t i = 0; i < result.scores.size(); ++i) {
				const float score = result.scores[i];
				finite = finite && std::isfinite(score);
				if (score > best_score) {
					best_score = score;
					result.best_index = i;
				}
			}
			for (float value : result.poses)
				finite = finite && std::isfinite(value);
			result.finite_outputs = finite;
			std::copy_n(result.poses.begin() + result.best_index * joint_count * 3,
				result.selected_pose.size(), result.selected_pose.begin());
			result.selection_ms = elapsed(begin);
			result.process_ms = elapsed(start);
			if (!finite)
				preserve_failure("first_output_finiteness",
					"Nonfinite model output; preserve and stop without retry", &window, &result);
			++next_invocation;
		} catch (const std::exception& e) {
			preserve_failure(stage, e.what(), &window, &result);
			throw;
		} catch (...) {
			preserve_failure(stage, "Non-standard SDK exception", &window, &result);
			throw;
		}
	}
};

Runtime::Runtime(const Config& config) : impl_(std::make_unique<Impl>(config)) {
	impl_->initialize();
}

Runtime::~Runtime() = default;

void Runtime::infer(const Window& window, Result& result) {
	impl_->infer(window, result);
}

double Runtime::init_ms() const {
	impl_->assert_owner();
	return impl_->initialized_ms;
}

bool Runtime::release_permitted() const noexcept {
	return impl_->activity.permitted();
}

void Runtime::retain_if_unproved() const noexcept {
	impl_->retain_if_unproved();
}
} // namespace pose180_pipeline
