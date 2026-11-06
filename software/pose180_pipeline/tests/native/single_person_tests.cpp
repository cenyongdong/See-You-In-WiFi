#include "postprocess.hpp"
#include "geometry.hpp"
#include <cmath>
#include <iostream>
#include <limits>
#include <random>
#include <stdexcept>
using namespace pose::post;
using namespace pose::post::geometry;

static void require(bool ok, const char* message) {
	if (!ok)
		throw std::runtime_error(message);
}

struct Stream {
	std::array<float, 180> scores{};
	std::array<float, 7560> poses{};
	Identity id{1, 1, 1, 1000000000};

	void set(double x, unsigned query = 0) {
		scores.fill(-1);
		scores[query] = 0;
		for (unsigned j = 0; j < 14; ++j) {
			poses[42 * query + 3 * j] = float(x + .12 * (int(j % 3) - 1));
			poses[42 * query + 3 * j + 1] = float(.1 * (int(j % 2) - 1));
			poses[42 * query + 3 * j + 2] = float(.13 * j);
		}
	}

	PresentationFrame run(Postprocessor& p, unsigned ms = 67) {
		auto f = p.update(id, scores.data(), poses.data());
		id.source_ns += std::uint64_t(ms) * 1000000;
		++id.sequence;
		++id.frame;
		return f;
	}
};

int main() {
	try {
		Config config;
		config.top_k = 1;
		config.score_threshold.reset();
		config.single_person_stability = true;
		config.min_cutoff = .5;
		config.beta = .3;
		Postprocessor stable(config);
		Stream s;
		s.set(0);
		PresentationFrame f;
		for (unsigned i = 0; i < 8; ++i)
			f = s.run(stable);
		const auto original = f.poses.at(0);
		for (unsigned i = 0; i < 2; ++i) {
			s.set(2, 179);
			f = s.run(stable);
			require(f.raw_poses[0].candidate == 179 && f.raw_poses[0].score == 0, "Top1/no-cutoff changed");
			require(f.poses.size() == 1 && f.poses[0].held && f.poses[0].joints == original.joints &&
					f.poses[0].observed_ns == original.observed_ns,
				"spike contaminated committed filter");
		}
		s.set(0, 17);
		f = s.run(stable);
		require(
			f.poses[0].track == original.track && !f.poses[0].held && f.poses[0].joints == original.joints,
			"return left a spike tail");
		auto previous = f.poses[0];
		double largest_step = 0;
		for (unsigned i = 0; i < 55; ++i) {
			s.set(2, i % 2 ? 7 : 179);
			f = s.run(stable);
			require(f.poses.size() <= 1, "single-person cap lost");
			if (!f.poses.empty()) {
				const auto current = f.poses[0];
				require(current.track == original.track, "relocation discarded smoothing identity");
				largest_step =
					std::max(largest_step, distance(centre(current.joints), centre(previous.joints)));
				previous = current;
			}
		}
		require(largest_step < .2, "confirmed relocation snapped");
		require(std::abs(centre(f.poses[0].joints)[0] - 2) < .15,
			"persistent movement stayed locked to old location");
		require(stable.metrics().single_relocations > 0 && stable.metrics().single_limited > 0,
			"relocation limiter not exercised");
		// Pending outliers cannot keep an expired pose visible or forge freshness.
		s.set(9);
		f = s.run(stable, 300);
		s.set(-9);
		f = s.run(stable);
		require(f.poses.empty(), "expired hold leaked while rejecting outliers");
		s.id.session = 2;
		s.set(0);
		require(s.run(stable).poses.empty(), "identity crossed input epoch");
		for (unsigned i = 0; i < 3; ++i)
			f = s.run(stable);
		require(f.poses.size() == 1 && f.poses[0].track != original.track,
			"new epoch did not confirm independently");
		s.scores[5] = std::numeric_limits<float>::quiet_NaN();
		bool rejected = false;
		try {
			s.run(stable);
		} catch (...) {
			rejected = true;
		}
		require(rejected, "NaN bypassed validity checks");
		// Fixed-seed noise and a known continuous trajectory quantify the tradeoff.
		Config baseline = config;
		baseline.single_person_stability = false;
		Postprocessor old(baseline), enhanced(config);
		Stream noise;
		std::mt19937 random(123);
		std::normal_distribution<double> jitter(0, .06);
		double old_sq = 0, new_sq = 0;
		unsigned count = 0;
		for (unsigned i = 0; i < 600; ++i) {
			noise.set(jitter(random), i % 2 ? 0 : 179);
			auto a = noise.run(old);
			auto b = enhanced.update(a.id, noise.scores.data(), noise.poses.data());
			if (i > 80) {
				old_sq += std::pow(centre(a.poses.at(0).joints)[0], 2);
				new_sq += std::pow(centre(b.poses.at(0).joints)[0], 2);
				++count;
			}
		}
		require(new_sq < old_sq * .9, "stronger centre filter did not reduce stationary noise");
		Postprocessor moving(config);
		Stream motion;
		double error = 0;
		unsigned steps = 0;
		for (unsigned i = 0; i < 140; ++i) {
			motion.set(.03 * i, i % 2 ? 0 : 179);
			f = motion.run(moving);
			if (i > 30) {
				require(f.poses.size() == 1 && !f.poses[0].held, "normal motion was quarantined");
				error += std::abs(centre(f.poses[0].joints)[0] - .03 * i);
				++steps;
			}
		}
		require(error / steps < .3, "continuous motion lag excessive");
		std::cout << "{\"passed\":true,\"stationary_rms_v5\":" << std::sqrt(old_sq / count)
				  << ",\"stationary_rms_enhanced\":" << std::sqrt(new_sq / count)
				  << ",\"max_relocation_step\":" << largest_step
				  << ",\"continuous_motion_mean_error\":" << error / steps << "}\n";
	} catch (const std::exception& e) {
		std::cerr << e.what() << '\n';
		return 1;
	}
}
