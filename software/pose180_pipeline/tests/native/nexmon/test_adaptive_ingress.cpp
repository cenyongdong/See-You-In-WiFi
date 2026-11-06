#include "adaptive_ingress.hpp"
#include <cmath>
#include <cstring>
#include <functional>
#include <iostream>
#include <set>

using namespace nexmon_board;

namespace {
void check(bool v, const char* s) {
	if (!v)
		throw std::runtime_error(s);
}

void rejects(const std::function<void()>& f) {
	bool rejected = false;
	try {
		f();
	} catch (const std::exception&) {
		rejected = true;
	}
	check(rejected, "Expected rejection");
}

void put(std::vector<std::uint8_t>& b, std::size_t at, std::uint64_t n, std::size_t bytes) {
	for (std::size_t i = 0; i < bytes; ++i)
		b[at + i] = std::uint8_t(n >> (8 * i));
}

AdaptiveConfig config() {
	AdaptiveConfig c;
	c.source.session_id = "adaptive-test";
	c.source.streaming = true;
	c.source.receiver_ids = {"rx1", "rx2", "rx3"};
	c.source.gains = {1, 2, 3};
	c.source.transmitter_mac = {2, 17, 34, 51, 68, 85};
	c.source.chanspec = 0xd0a1;
	return c;
}

struct Source {
	void event(AdaptiveIngress& in, std::size_t r, int ordinal, std::int64_t observed, double ppm = 0,
		int phase = 0, bool invalid = false, int counter_offset = 0, int origin = 0) {
		const auto c = config();
		const auto time = std::int64_t(std::llround(ordinal * 1000000.0 / 300));
		const auto tsf =
			std::int64_t(std::llround(double(time) * (1 + ppm / 1000000))) + std::int64_t(r) * 12345 + phase;
		const auto seq = ((ordinal + origin) & 4095) << 4;
		for (int a = 0; a < 3; ++a) {
			std::vector<std::uint8_t> b(274), d(50);
			put(b, 0, 0x1111, 2);
			std::copy(c.source.transmitter_mac.begin(), c.source.transmitter_mac.end(), b.begin() + 4);
			put(b, 10, seq, 2);
			put(b, 12, a << 8, 2);
			put(b, 14, c.source.chanspec, 2);
			put(b, 16, 106, 2);
			for (int n = 0; n < 64; ++n)
				put(b, 18 + 4 * std::size_t(n),
					invalid ? 0 : std::uint64_t((ordinal % 512 + a * 64 + n + 1) << 18), 4);
			std::memcpy(d.data(), "NMD3", 4);
			put(d, 4, 3, 2);
			put(d, 6, 50, 2);
			std::copy(c.source.transmitter_mac.begin(), c.source.transmitter_mac.end(), d.begin() + 8);
			put(d, 14, seq, 2);
			put(d, 16, a << 8, 2);
			put(d, 18, c.source.chanspec, 2);
			put(d, 20, 8, 2);
			put(d, 22, 0xaaaa, 2);
			put(d, 24, std::uint64_t(tsf), 2);
			put(d, 26, ordinal + counter_offset, 2);
			put(d, 28, 28, 2);
			put(d, 30, 3, 2);
			for (int n = 0; n < 3; ++n)
				put(d, 32 + 4 * std::size_t(n), std::uint64_t((ordinal % 512 + a * 64 + 100 + n) << 18), 4);
			put(d, 44, 59, 2);
			put(d, 46, std::uint64_t(tsf + 80), 4);
			in.feed(r, c.source.session_id, 100000000 + time + a, 5500, b.data(), b.size(), observed);
			in.feed(r, c.source.session_id, 100000000 + time + a, 5501, d.data(), d.size(), observed);
		}
	}
};

struct Ledger {
	std::uint64_t windows = 0, approximate = 0, last_version = 0;
	std::array<std::int64_t, 3> last{-1, -1, -1};
	std::uint64_t last_time = 0, max_gap = 0, first_time = 0;

	void consume(AdaptiveIngress& in, int origin = 0) {
		for (const auto& w : in.take_ready()) {
			check(w.alignment_version >= last_version, "Alignment version moved backwards");
			last_version = w.alignment_version;
			if (last_time)
				max_gap = std::max(max_gap, w.window.source_time_ns - last_time);
			last_time = w.window.source_time_ns;
			if (!first_time)
				first_time = last_time;
			check(w.span_us <= 100000, "Excessive window time span");
			for (std::size_t r = 0; r < 3; ++r)
				for (std::size_t t = 0; t < 20; ++t) {
					const auto sequence = w.sequences[r][t];
					check(sequence > last[r], "Repeated/out-of-order event in published windows");
					last[r] = sequence;
					check(std::abs(sequence - w.sequences[0][t]) <= 1, "Sequence skew cap exceeded");
					const auto ordinal = sequence - origin;
					for (std::size_t a = 0; a < 3; ++a)
						for (std::size_t n = 0; n < 30; ++n) {
							const auto bin = (ht20_ng2[n] + 64) % 64;
							const auto raw = ordinal % 512 + std::int64_t(a) * 64 +
								(bin >= 28 && bin <= 30 ? 100 + bin - 28 : bin + 1);
							const auto expected = double(raw) * double(r + 1);
							check(w.window.csi[((r * 3 + a) * 20 + t) * 30 + n] ==
									std::complex<double>(expected, 0),
								"CSI changed or antenna/event pairing lost");
						}
				}
			if (w.approximate_points) {
				++approximate;
				check(w.max_skew_us <= 5000, "Learned time skew exceeded hard cap");
			}
			++windows;
		}
	}
};
}

int main() {
	int passed = 0;
	try {
		{
			AdaptiveIngress in(config());
			Source s;
			Ledger l;
			for (int n = 0; n < 1200; ++n) {
				for (std::size_t r = 0; r < 3; ++r)
					s.event(in, r, n, std::int64_t(n) * 10000 / 3);
				l.consume(in);
			}
			check(l.windows == 60 && l.approximate == 0, "Uniform input was dropped");
			check(l.first_time < 100100000000ull, "Grid calibration blocked startup");
			check(in.diagnostics().switches > 0, "Shadow model never committed");
			++passed;
		}
		{
			AdaptiveIngress in(config());
			Source s;
			Ledger l;
			for (int n = 0; n < 180000; ++n) {
				const auto before = in.diagnostics();
				for (std::size_t r = 0; r < 3; ++r)
					s.event(in, r, n, std::int64_t(n) * 10000 / 3,
						r == 0		 ? -20
							: r == 1 ? 12
									 : -7,
						n >= 900 && r == 1 ? 1200 : 0);
				const auto after = in.diagnostics();
				if (after.alignment_version != before.alignment_version)
					check(before.partial_points == 0, "Fit committed within an existing window");
				l.consume(in);
			}
			check(
				l.windows == 9000 && l.max_gap < 70000000, "Clock drift/phase step interrupted exact input");
			for (auto n : in.diagnostics().queued_events)
				check(n <= 256, "Unbounded adaptive history");
			++passed;
		}
		{
			AdaptiveIngress in(config());
			Source s;
			Ledger l;
			for (int n = 0; n < 2400; ++n) {
				for (std::size_t r = 0; r < 3; ++r)
					s.event(in, r, n, std::int64_t(n) * 10000 / 3, 0, 0, r == 1 && n >= 700 && n % 97 == 0);
				l.consume(in);
			}
			check(l.approximate > 0, "Neighbouring real-event fallback was never used");
			check(l.windows >= 115 && l.max_gap < 150000000, "Isolated missing samples stopped input");
			check(in.diagnostics().approximate_points < 60, "Fallback failed to return to exact association");
			++passed;
		}
		{
			AdaptiveIngress in(config());
			Source s;
			Ledger l;
			for (int n = 0; n < 1800; ++n) {
				for (std::size_t r = 0; r < 3; ++r)
					s.event(in, r, n, std::int64_t(n) * 10000 / 3, 0, 0, false, r == 1 && n >= 900 ? 2 : 0);
				l.consume(in);
			}
			const auto d = in.diagnostics();
			check(d.decoder_resets[1] == 1 && d.decoder_resets[0] == 0 && d.decoder_resets[2] == 0,
				"Decoder error reset healthy receivers");
			check(l.windows >= 88 && l.max_gap < 200000000, "Decoder recovery blocked inference windows");
			++passed;
		}
		{
			AdaptiveIngress in(config());
			Source s;
			Ledger l;
			for (int n = 0; n < 1200; ++n) {
				for (const auto r : {1u, 2u, 0u})
					s.event(in, r, n, std::int64_t(n) * 10000 / 3, 0, 0, false, 0, 4090);
				l.consume(in, 4090);
			}
			check(l.windows == 60, "Startup order/sequence wrap lost windows");
			++passed;
		}
		{
			AdaptiveIngress in(config());
			Source s;
			for (int n = 0; n < 19; ++n)
				for (std::size_t r = 0; r < 3; ++r)
					s.event(in, r, n, std::int64_t(n) * 10000 / 3);
			in.poll(1000000);
			check(in.take_ready().empty(), "Stale/partial data published");
			check(in.diagnostics().partial_points == 0, "Expired partial window retained");
			for (int n = 300; n < 360; ++n)
				for (std::size_t r = 0; r < 3; ++r)
					s.event(in, r, n, std::int64_t(n) * 10000 / 3);
			auto windows = in.take_ready();
			check(!windows.empty(), "Fresh same-event input failed to recover");
			for (const auto& w : windows)
				check(w.sequences[0][0] >= 300, "Pre-gap window replayed");
			++passed;
		}
		{
			auto c = config();
			c.max_sequence_skew = 0;
			AdaptiveIngress in(c);
			Source s;
			Ledger l;
			for (int n = 0; n < 1200; ++n) {
				for (std::size_t r = 0; r < 3; ++r)
					s.event(in, r, n, std::int64_t(n) * 10000 / 3, 0, 0, r == 1 && n == 700);
				l.consume(in);
			}
			check(l.approximate == 0 && l.windows >= 58, "Exact-event-only mode changed semantics");
			++passed;
		}
		{
			auto c = config();
			c.source.streaming = false;
			rejects([&] {
				AdaptiveIngress in(c);
			});
			c = config();
			c.max_sequence_skew = 4;
			rejects([&] {
				AdaptiveIngress in(c);
			});
			AdaptiveIngress in(config());
			std::vector<std::uint8_t> b(274);
			put(b, 0, 0x1111, 2);
			put(b, 16, 106, 2);
			rejects([&] {
				in.feed(0, "adaptive-test", 0, 5500, b.data(), b.size(), 0);
			});
			rejects([&] {
				Source{}.event(in, 0, 1, 3333);
			});
			++passed;
		}
		std::cout << "adaptive cases passed=" << passed << "; drift_seconds=600; CSI_live=false; SDK=false\n";
		return 0;
	} catch (const std::exception& e) {
		std::cerr << "adaptive cases passed=" << passed << " failed: " << e.what() << '\n';
		return 1;
	}
}
