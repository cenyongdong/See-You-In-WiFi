#include "ingress.hpp"
#include <cmath>
#include <cstring>
#include <functional>
#include <iostream>
#include <limits>
#include <stdexcept>
#include <vector>

using namespace nexmon_board;

namespace {
void check(bool ok, const char* why) {
	if (!ok)
		throw std::runtime_error(why);
}

void throws(const std::function<void()>& f) {
	bool caught = false;
	try {
		f();
	} catch (const std::exception&) {
		caught = true;
	}
	check(caught, "Expected rejection");
}

ContinuityDiagnostic continuity(const std::function<void()>& f) {
	try {
		f();
	} catch (const ContinuityError& e) {
		return e.diagnostic();
	}
	throw std::runtime_error("Expected typed continuity rejection");
}

void ordinary_error(const std::function<void()>& f) {
	try {
		f();
	} catch (const ContinuityError&) {
		throw std::runtime_error("Identity/format failure classified as recoverable continuity");
	} catch (const std::runtime_error&) {
		return;
	}
	throw std::runtime_error("Expected identity/format rejection");
}

void put(std::vector<std::uint8_t>& b, std::size_t at, std::uint64_t v, std::size_t n) {
	for (std::size_t i = 0; i < n; ++i)
		b[at + i] = std::uint8_t(v >> (8 * i));
}

Config config() {
	Config c;
	c.session_id = "test-job";
	c.receiver_ids = {"one", "two", "three"};
	c.transmitter_mac = {2, 17, 34, 51, 68, 85};
	c.chanspec = 0xd0a1;
	c.expected_events = 800;
	c.gains = {1, 2, 3};
	return c;
}

struct Source {
	std::size_t counter[3]{};

	struct Pair {
		std::vector<std::uint8_t> csi, meta;
		std::int64_t arrival;
	};

	static Pair pair(int ordinal, int core, std::size_t count, int origin = 0, int clock_offset = 0,
		bool retry = false, int seq_override = -1, int offset_us = 0) {
		auto c = config();
		auto timestamp =
			std::int64_t(std::llround(double(ordinal) * 1000000 / 300)) + clock_offset + offset_us;
		auto arrival =
			100000000 + std::int64_t(std::llround(double(ordinal) * 1000000 / 300)) + offset_us + core;
		auto seq = seq_override >= 0 ? seq_override : ((ordinal + origin) & 4095) << 4;
		std::vector<std::uint8_t> b(274), d(50);
		put(b, 0, 0x1111, 2);
		std::copy(c.transmitter_mac.begin(), c.transmitter_mac.end(), b.begin() + 4);
		put(b, 10, std::uint64_t(seq), 2);
		put(b, 12, std::uint64_t(core << 8), 2);
		put(b, 14, c.chanspec, 2);
		put(b, 16, 106, 2);
		for (int i = 0; i < 64; ++i)
			put(b, 18 + std::size_t(i) * 4, std::uint64_t((i + 1) << 18), 4);
		std::memcpy(d.data(), "NMD3", 4);
		put(d, 4, 3, 2);
		put(d, 6, 50, 2);
		std::copy(c.transmitter_mac.begin(), c.transmitter_mac.end(), d.begin() + 8);
		put(d, 14, std::uint64_t(seq), 2);
		put(d, 16, std::uint64_t(core << 8), 2);
		put(d, 18, c.chanspec, 2);
		put(d, 20, 8 | (retry ? 0x800 : 0), 2);
		put(d, 22, 0xaaaa, 2);
		put(d, 24, std::uint64_t(timestamp), 2);
		put(d, 26, count, 2);
		put(d, 28, 28, 2);
		put(d, 30, 3, 2);
		for (int i = 0; i < 3; ++i)
			put(d, 32 + std::size_t(i) * 4, std::uint64_t((100 + i) << 18), 4);
		put(d, 44, 59, 2);
		put(d, 46, std::uint64_t(timestamp + 80), 4);
		return {std::move(b), std::move(d), arrival};
	}

	void event(Ingress& in, std::size_t r, int ordinal, int origin = 0, int clock_offset = 0,
		bool retry = false, int cores = 3, bool lose_diag = false, int seq_override = -1, int offset_us = 0) {
		for (int core = 0; core < cores; ++core) {
			auto p = pair(ordinal, core, counter[r], origin, clock_offset, retry, seq_override, offset_us);
			in.feed(r, config().session_id, p.arrival, 5500, p.csi.data(), p.csi.size());
			if (!lose_diag)
				in.feed(r, config().session_id, p.arrival, 5501, p.meta.data(), p.meta.size());
		}
		++counter[r];
	}
};

void suffix(Ingress& in, std::size_t receiver, int first_record) {
	for (int record = first_record; record < 6; ++record) {
		auto p = Source::pair(0, record / 2, 0);
		const auto& bytes = record % 2 ? p.meta : p.csi;
		in.feed(
			receiver, config().session_id, p.arrival, record % 2 ? 5501 : 5500, bytes.data(), bytes.size());
	}
}

BatchResult run(int origin = 0, int drop = -1, bool retry = false, bool partial_tail = false,
	WindowDiagnostics* diagnostic = nullptr) {
	Ingress in(config());
	Source source;
	std::size_t emitted = 0;
	bool before_eof = false;
	for (int ordinal = 0; ordinal < 800; ++ordinal)
		for (std::size_t r = 0; r < 3; ++r) {
			if (r == 1 && ordinal == drop)
				continue;
			source.event(in, r, ordinal, origin, int(r) * 12345, false,
				partial_tail && ordinal == 799 && r == 2 ? 2 : 3);
			if (retry && r == 1 && ordinal == 410)
				source.event(in, r, ordinal, origin, int(r) * 12345, true, 3, false, -1, 400);
			auto ready = in.take_ready();
			emitted += ready.size();
			if (!ready.empty() && ordinal < 799)
				before_eof = true;
		}
	if (diagnostic)
		*diagnostic = in.diagnostics();
	auto result = in.finish();
	check(before_eof, "No output before EOF");
	check(emitted == result.windows.size(), "Incremental/final window mismatch");
	throws([&] {
		in.finish();
	});
	return result;
}
}

int main() {
	int passed = 0;
	try {
		auto baseline = run();
		check(!baseline.windows.empty() && baseline.windows.size() == baseline.decisions.size(),
			"Uniform data rejected");
		++passed;
		auto missing = run(0, 410);
		check(missing.windows.size() + 1 == missing.decisions.size(),
			"Missing event did not reject one whole window");
		++passed;
		auto rollover = run(4000);
		for (const auto& n : rollover.nodes)
			check(n.wraps == 1, "Safe modulo4096 rollover not retained");
		++passed;
		auto retry = run(0, -1, true);
		check(retry.nodes[1].retransmissions == 1 && retry.windows.size() == baseline.windows.size(),
			"Retry did not preserve first valid");
		++passed;
		auto partial = run(0, -1, false, true);
		check(partial.nodes[2].trailing_cores == 2, "Unfinished core tail not retained in diagnostic");
		++passed;
		auto c = config();
		c.gains[1] = 0;
		throws([&] {
			Ingress bad(c);
		});
		c.gains[1] = std::numeric_limits<double>::quiet_NaN();
		throws([&] {
			Ingress bad(c);
		});
		++passed;
		{
			Ingress in(config());
			std::uint8_t b = 0;
			throws([&] {
				in.feed(0, "another-job", 0, 5500, &b, 1);
			});
			Source s;
			throws([&] {
				s.event(in, 0, 0);
			});
		}
		++passed;
		{
			Ingress in(config());
			std::uint8_t b = 0;
			throws([&] {
				in.feed(0, "test-job", 0, 5500, &b, 1);
			});
		}
		++passed;
		{
			Ingress in(config());
			Source s;
			s.event(in, 0, 0, 0, 0, false, 2);
			throws([&] {
				s.event(in, 0, 1);
			});
		}
		++passed;
		{
			Ingress in(config());
			Source s;
			s.event(in, 0, 0, 0, 0, false, 1, true);
			throws([&] {
				s.event(in, 0, 1);
			});
		}
		++passed;
		{
			Ingress in(config());
			Source s;
			s.event(in, 0, 0);
			throws([&] {
				s.event(in, 0, 1, 0, 0, false, 3, false, 0);
			});
		}
		++passed;
		{
			Ingress in(config());
			Source s;
			s.event(in, 0, 0);
			throws([&] {
				s.event(in, 0, 1, 0, 0, false, 3, false, 2048 << 4);
			});
		}
		++passed;
		{
			Ingress in(config());
			Source s;
			s.event(in, 0, 0);
			throws([&] {
				in.expire(0, 100032770);
			});
		}
		++passed;
		{
			auto w = baseline.windows.front();
			auto b = encode_piwcsi2(w, 42, 123);
			check(b.size() == 86432 && std::memcmp(b.data(), "PIWCSI2\0", 8) == 0, "Protocol header changed");
			check(b[8] == 2 && b[16] == 42 && b[24] == 123, "Protocol fields changed");
			w.csi[0] = {std::numeric_limits<double>::infinity(), 0};
			throws([&] {
				encode_piwcsi2(w, 0, 0);
			});
		}
		++passed;
		{
			auto z = decode_acphy((17u << 18) | (9u << 6) | (1u << 29) | (1u << 17) | 63u);
			check(z == std::complex<double>(-8.5, -4.5), "Signed mantissa/exponent decode changed");
		}
		++passed;
		{
			Ingress in(config());
			Source s;
			s.event(in, 2, 0, 0, 12345);
			s.counter[2] = 5;
			const auto d = continuity([&] {
				s.event(in, 2, 1, 0, 12345);
			});
			check(d.receiver == 2 && d.reason == ContinuityReason::counter_step && d.have_previous &&
					d.event_clock_known,
				"Counter diagnostic identity missing");
			check(d.arrival_us == 100003333 && d.previous_arrival_us == 100000000 && d.host_delta_us == 3333,
				"Counter diagnostic lost raw arrival values");
			check(d.tsf_before == 12345 && d.tsf_after == 15678 && d.tsf_delta_us == 3333 &&
					d.counter_before == 0 && d.counter_after == 5 && d.counter_step == 5,
				"Counter/TSF diagnostic lost raw values");
			check(d.sequence_before == 0 && d.sequence_after == 16, "Diagnostic lost sequence values");
			throws([&] {
				in.take_ready();
			});
			throws([&] {
				s.event(in, 0, 2);
			});
		}
		++passed;
		{
			Ingress in(config());
			Source s;
			s.event(in, 0, 0);
			const auto d = continuity([&] {
				in.expire(0, 100032770);
			});
			check(d.reason == ContinuityReason::arrival_gap && d.arrival_us == 100032770 &&
					d.previous_arrival_us == 100000002 && d.host_delta_us == 32768,
				"Arrival gap threshold/raw values changed");
			check(!d.event_clock_known, "Expire invented event clock values");
		}
		++passed;
		{
			Ingress in(config());
			Source s;
			s.event(in, 1, 0, 0, 0, false, 1, true);
			const auto d = continuity([&] {
				s.event(in, 1, 1);
			});
			check(d.receiver == 1 && d.reason == ContinuityReason::missing_metadata &&
					d.host_delta_us == 3333 && d.sequence_before == 0 && d.sequence_after == 16,
				"Pairing diagnostic missing");
		}
		++passed;
		{
			Ingress in(config());
			Source s;
			s.event(in, 0, 0);
			const auto d = continuity([&] {
				s.event(in, 0, 1, 0, 0, false, 3, false, 2048 << 4);
			});
			check(d.reason == ContinuityReason::sequence_step && d.sequence_before == 0 &&
					d.sequence_after == 32768 && d.counter_step == 1,
				"Ambiguous sequence raw values missing");
		}
		++passed;
		{
			Ingress in(config());
			Source s;
			const auto d = continuity([&] {
				for (int ordinal = 0; ordinal < 400; ++ordinal)
					s.event(in, 1, ordinal, 0, 0, false, 3, false, -1, (ordinal % 2) * 1667);
			});
			check(d.reason == ContinuityReason::phase_lock && d.receiver == 1 && d.phase_samples >= 120 &&
					d.phase_concentration < .75,
				"Phase-lock rejection lost concentration/sample count");
		}
		++passed;
		{
			auto c = config();
			c.streaming = true;
			for (int first_record = 1; first_record < 6; ++first_record) {
				Ingress joined(c), clean(c);
				Source a, b;
				std::size_t count = 0;
				for (std::size_t r = 0; r < 3; ++r)
					suffix(joined, r, first_record);
				for (auto n : joined.retained_events())
					check(n == 0, "Streaming prefix entered event history");
				for (int ordinal = 1; ordinal < 800; ++ordinal)
					for (std::size_t r = 0; r < 3; ++r) {
						a.event(joined, r, ordinal);
						b.event(clean, r, ordinal);
						auto actual = joined.take_ready(), expected = clean.take_ready();
						check(
							actual.size() == expected.size(), "Mid-event join changed ready window boundary");
						for (std::size_t i = 0; i < actual.size(); ++i) {
							check(actual[i].csi == expected[i].csi &&
									actual[i].event_indices == expected[i].event_indices &&
									actual[i].source_time_ns == expected[i].source_time_ns,
								"Partial prefix leaked into accepted window");
							++count;
						}
					}
				check(count > 0, "Mid-event streaming join never produced fresh windows");
				Ingress finite(config());
				Source s;
				continuity([&] {
					suffix(finite, 0, first_record);
					s.event(finite, 0, 1);
				});
			}
		}
		++passed;
		{
			auto c = config();
			c.streaming = true;
			for (bool metadata : {false, true})
				for (int fault = 0; fault < 4; ++fault) {
					Ingress in(c);
					auto p = Source::pair(0, 2, 0);
					auto bytes = metadata ? p.meta : p.csi;
					if (fault == 0)
						bytes[metadata ? 8 : 4] ^= 1; // Wrong transmitter in skipped prefix.
					if (fault == 1)
						bytes[metadata ? 18 : 14] ^= 1; // Wrong channel in skipped prefix.
					if (fault == 2)
						bytes[0] ^= 1;
					if (fault == 3)
						put(bytes, metadata ? 16 : 12, 768, 2);
					ordinary_error([&] {
						in.feed(
							0, c.session_id, p.arrival, metadata ? 5501 : 5500, bytes.data(), bytes.size());
					});
				}
			Ingress in(c);
			Source s;
			s.event(in, 0, 0);
			auto p = Source::pair(1, 1, 1);
			const auto d = continuity([&] {
				in.feed(0, c.session_id, p.arrival, 5501, p.meta.data(), p.meta.size());
			});
			check(d.reason == ContinuityReason::pairing_mismatch, "Streaming skipped metadata after start");
		}
		++passed;
		{
			auto c = config();
			c.streaming = true;
			Ingress in(c);
			Source source;
			std::size_t count = 0, early = 0;
			// More than 16 sequence wraps, a 16-bit NMD3 counter wrap and
			// 233 seconds of capture time; retained memory must stay bounded.
			for (int ordinal = 0; ordinal < 70000; ++ordinal)
				for (std::size_t r = 0; r < 3; ++r) {
					source.event(in, r, ordinal, 0, int(r) * 12345);
					auto ready = in.take_ready();
					count += ready.size();
					if (ordinal < 800) {
						for (const auto& w : ready) {
							check(
								w.csi == baseline.windows.at(early).csi, "Rolling mode changed model input");
							check(w.event_indices == baseline.windows.at(early).event_indices,
								"Rolling mode changed source association");
							++early;
						}
					}
					for (auto n : in.retained_events())
						check(n <= 1202, "Rolling event history leaked");
					for (auto n : in.retained_cells())
						check(n <= 40, "Consumed grid history leaked");
				}
			check(
				early == baseline.windows.size() && count > 3400, "Continuous wrap stream stopped producing");
		}
		++passed;
		{
			WindowDiagnostics d;
			auto result = run(0, 410, false, false, &d);
			check(d.anchored && d.decided == result.decisions.size() && d.accepted == result.windows.size(),
				"Window decision census differs from finite truth");
			check(d.missing == 1 && d.missing_points == std::array<std::uint64_t, 3>{0, 1, 0},
				"Missing grid point attributed to wrong receiver");
			check(d.point_error == 0 && d.different_event == 0, "Missing point invented other causes");
			Ingress in(config());
			Source source;
			for (int ordinal = 0; ordinal < 800; ++ordinal)
				for (std::size_t r = 0; r < 3; ++r)
					source.event(
						in, r, ordinal, 0, 0, false, 3, false, -1, (ordinal == 450 && r == 1) ? 1000 : 0);
			d = in.diagnostics();
			check(d.point_error == 1 && d.point_errors == std::array<std::uint64_t, 3>{0, 1, 0},
				"Out-of-tolerance sample not attributed to RX2");
			check(d.missing == 0 && d.different_event == 0 && d.accepted + 1 == d.decided,
				"Point diagnostics relaxed or misclassified validity");
		}
		++passed;
		{
			// Synthetic oscillator mismatch, not a claim about any real RX.
			// Compare the exact unchanged grid under long-lived and bounded
			// fresh-generation policies; samples/tolerances are identical.
			std::size_t counts[3]{}, max_gap[3]{}, resets[3]{};
			for (unsigned recovery = 0; recovery < 3; ++recovery) {
				auto c = config();
				c.streaming = true;
				auto in = std::make_unique<Ingress>(c);
				Source source;
				bool ready = false;
				int last_good = 0;
				std::uint64_t errors = 0, mismatch = 0;
				for (int ordinal = 0; ordinal < 54000; ++ordinal) {
					for (std::size_t r = 0; r < 3; ++r) {
						const int ppm = r == 1 ? 20 : r == 2 ? -15 : 0;
						source.event(*in, r, ordinal, 0, int(r) * 12345, false, 3, false, -1,
							int(std::llround(double(ordinal) * ppm / 300)));
						for (const auto& w : in->take_ready()) {
							for (std::size_t t = 0; t < 20; ++t)
								check(w.event_indices[0][t] == w.event_indices[1][t] &&
										w.event_indices[1][t] == w.event_indices[2][t],
									"Drift policy admitted different source events");
							++counts[recovery];
							last_good = ordinal;
							ready = true;
						}
					}
					if (counts[recovery])
						max_gap[recovery] = std::max(max_gap[recovery], std::size_t(ordinal - last_good));
					if (ordinal % 300 == 0) {
						for (auto n : in->retained_events())
							check(n <= 1210, "Drifting stream retained unbounded events");
						for (auto n : in->retained_cells())
							check(n <= 80, "Drifting stream retained unbounded cells");
					}
					if (recovery && ready && ordinal - last_good >= (recovery == 1 ? 3000 : 600)) {
						const auto d = in->diagnostics();
						errors += d.point_error;
						mismatch += d.different_event;
						check(d.rejected_streak > 0, "Drift recovery triggered without rejected windows");
						in = std::make_unique<Ingress>(c);
						ready = false;
						++resets[recovery];
					}
				}
				const auto d = in->diagnostics();
				errors += d.point_error;
				mismatch += d.different_event;
				check(errors > 0, "Drift test did not exercise point rejection");
				if (!recovery)
					check(mismatch > 0 && d.last_mismatch_sequences[0] != d.last_mismatch_sequences[1],
						"Long drift did not expose raw event mismatch");
			}
			check(max_gap[0] > 3000 && max_gap[1] > 3000 && max_gap[2] < 1050 && counts[2] > counts[1] &&
					counts[1] > counts[0] && resets[2] > 0,
				"Bounded relearning did not reduce synthetic starvation");
			std::cout << "drift_180s policies=none,10s,2s windows=" << counts[0] << '/' << counts[1] << '/'
					  << counts[2] << " max_gap_ms=" << max_gap[0] * 1000 / 300 << '/'
					  << max_gap[1] * 1000 / 300 << '/' << max_gap[2] * 1000 / 300 << " resets=" << resets[0]
					  << '/' << resets[1] << '/' << resets[2] << '\n';
		}
		++passed;
		{
			auto c = config();
			c.track_clock = true;
			throws([&] {
				Ingress finite(c);
			});
			c.streaming = true;
			Ingress in(c);
			Source source;
			std::size_t emitted = 0;
			for (int ordinal = 0; ordinal < 800; ++ordinal)
				for (std::size_t r = 0; r < 3; ++r) {
					source.event(in, r, ordinal);
					for (const auto& w : in.take_ready()) {
						check(w.csi == baseline.windows.at(emitted).csi &&
								w.event_indices == baseline.windows.at(emitted).event_indices,
							"Tracking changed uniform source association/model input");
						++emitted;
					}
				}
			check(emitted == baseline.windows.size(), "Tracking lost uniform windows");
		}
		++passed;
		for (unsigned dirty = 0; dirty < 2; ++dirty) {
			auto c = config();
			c.streaming = true;
			c.track_clock = true;
			Ingress in(c);
			Source source;
			std::size_t count = 0, max_gap = 0;
			int last_good = 0;
			std::array<std::int64_t, 3> last_index{-1, -1, -1};
			const int length = dirty ? 36000 : 180000;
			for (int ordinal = 0; ordinal < length; ++ordinal) {
				for (std::size_t r = 0; r < 3; ++r) {
					if (dirty && r == 2 && ordinal > 400 && ordinal % 997 == 0)
						continue;
					const int ppm = r == 0 ? -20 : r == 1 ? 12 : -7;
					const int jitter = dirty ? (ordinal * 31 + int(r) * 17) % 81 - 40 : 0;
					const int spike = dirty && r == 1 && ordinal > 400 && ordinal % 1237 == 0 ? 1200 : 0;
					source.event(in, r, ordinal, 0, int(r) * 12345, false, 3, false, -1,
						int(std::llround(double(ordinal) * ppm / 300)) + jitter + spike);
					for (const auto& w : in.take_ready()) {
						for (std::size_t rx = 0; rx < 3; ++rx)
							for (auto index : w.event_indices[rx]) {
								check(std::int64_t(index) > last_index[rx],
									"Tracking reused or reordered an event");
								last_index[rx] = index;
							}
						if (!dirty)
							for (std::size_t t = 0; t < 20; ++t)
								check(w.event_indices[0][t] == w.event_indices[1][t] &&
										w.event_indices[1][t] == w.event_indices[2][t],
									"Tracking admitted different events");
						if (count)
							max_gap = std::max(max_gap, std::size_t(ordinal - last_good));
						++count;
						last_good = ordinal;
					}
				}
				if (count)
					max_gap = std::max(max_gap, std::size_t(ordinal - last_good));
				if (ordinal % 300 == 0) {
					for (auto n : in.retained_events())
						check(n <= 1210, "Tracked event history grew");
					for (auto n : in.retained_cells())
						check(n <= 80, "Tracked cell history grew");
					for (const auto& n : in.diagnostics().nodes)
						check(n.phase_samples <= 15 && std::abs(n.phase_step_scaled) <= 6000,
							"Phase tracking exceeded bounds");
				}
			}
			const auto d = in.diagnostics();
			check(count > std::size_t(length / 20 - 100) && max_gap < 65,
				"Tracked gradual drift still starved");
			check(d.different_event == 0, "Tracked drift shifted event identities");
			if (!dirty)
				check(d.point_error == 0 && d.missing == 0 && d.nodes[0].phase_correction_scaled < -3000000,
					"Unwrapped phase tracking failed");
			else
				check(d.point_errors[1] > 0 && d.missing_points[2] > 0,
					"Tracking concealed spike/missing data");
			std::cout << "tracked_drift seconds=" << length / 300 << " dirty=" << dirty
					  << " windows=" << count << " max_gap_ms=" << max_gap * 1000 / 300
					  << " correction_scaled=" << d.nodes[0].phase_correction_scaled << '/'
					  << d.nodes[1].phase_correction_scaled << '/' << d.nodes[2].phase_correction_scaled
					  << '\n';
			++passed;
		}
		{
			auto c = config();
			c.streaming = true;
			c.track_clock = true;
			Ingress in(c);
			Source source;
			std::size_t before = 0, after = 0;
			for (int ordinal = 0; ordinal < 2700; ++ordinal)
				for (std::size_t r = 0; r < 3; ++r) {
					source.event(
						in, r, ordinal, 0, 0, false, 3, false, -1, r == 1 && ordinal >= 900 ? 1200 : 0);
					for (const auto& w : in.take_ready()) {
						if (w.event_indices[0][19] < 900)
							++before;
						else
							++after;
					}
				}
			const auto d = in.diagnostics();
			check(
				before > 0 && after == 0 && d.point_errors[1] > 1000, "Tracking concealed abrupt phase step");
			check(std::abs(d.nodes[1].phase_correction_scaled) < 300 && d.nodes[1].phase_rejected_blocks > 70,
				"Tracker chased untrusted phase step");
		}
		++passed;
		std::cout << "ingress directed checks passed=" << passed << '\n';
		return 0;
	} catch (const std::exception& e) {
		std::cerr << "directed ingress failure after " << passed << " checks: " << e.what() << '\n';
		return 1;
	}
}
