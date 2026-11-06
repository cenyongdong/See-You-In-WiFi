#include "postprocess.hpp"
#include <cmath>
#include <iostream>
#include <limits>
#include <random>
#include <stdexcept>
using namespace pose::post;

static void check(bool p, const char* s) {
	if (!p)
		throw std::runtime_error(s);
}

struct Sample {
	std::array<float, 180> scores{};
	std::array<float, 7560> poses{};
	std::uint64_t ns = 1000000000, seq = 1, session = 1;

	void person(unsigned i, double x, float score = .8f) {
		scores[i] = score;
		for (unsigned j = 0; j < 14; ++j) {
			poses[i * 42 + j * 3] = float(x + .05 * (int(j % 3) - 1));
			poses[i * 42 + j * 3 + 1] = float(.1 * (int(j % 2) - 1));
			poses[i * 42 + j * 3 + 2] = float(.15 * j);
		}
	}

	PresentationFrame run(Postprocessor& p) {
		return p.update({session, seq, seq, ns}, scores.data(), poses.data());
	}

	void next(unsigned ms = 67) {
		ns += std::uint64_t(ms) * 1000000;
		++seq;
	}
};

int main() {
	try {
		Config two_hits;
		two_hits.confirmation_hits = 2;
		two_hits.identity_ns = two_hits.hold_ns;
		Config one_policy = two_hits;
		one_policy.top_k = 1;
		Postprocessor top_one(one_policy);
		Sample single;
		single.person(7, 0, .8f);
		single.person(19, 3, .8f);
		auto single_frame = single.run(top_one);
		check(single_frame.raw_poses.size() == 1 && single_frame.raw_poses[0].candidate == 7 &&
				single_frame.top_k == 1,
			"Top1 tie/ranking policy");
		single.next();
		check(single.run(top_one).poses.size() == 1, "Top1 confirmation");
		single.person(19, 3, .95f);
		single.next();
		single.run(top_one);
		single.next();
		single_frame = single.run(top_one);
		check(single_frame.poses.size() == 1 && single_frame.poses[0].candidate == 19,
			"Top1 held/current hypotheses exceeded one displayed body");
		single.scores.fill(.2f);
		single.next();
		check(single.run(top_one).raw_poses.empty(), "Top1 strict 0.2 threshold");
		single.next(251);
		check(single.run(top_one).poses.empty(), "Top1 held pose expiry");
		// Disabled means no score predicate, including exact zero and negative finite
		// values. Ranking, confirmation, geometry and nonfinite rejection still apply.
		Config no_cutoff = one_policy;
		no_cutoff.score_threshold.reset();
		Postprocessor unfiltered(no_cutoff);
		Sample low;
		low.scores.fill(-1);
		low.person(179, 0, .001f);
		const auto original_low = low.scores;
		auto low_frame = low.run(unfiltered);
		check(low_frame.raw_poses.size() == 1 && low_frame.raw_poses[0].candidate == 179 &&
				!low_frame.score_threshold,
			"disabled cutoff lost low-scoring Top1");
		check(low.scores == original_low, "disabled cutoff changed model scores");
		low.person(179, 0, 0);
		low.next();
		low_frame = low.run(unfiltered);
		check(low_frame.poses.size() == 1 && low_frame.raw_poses[0].score == 0,
			"zero score incorrectly filtered");
		low.person(179, 0, -.5f);
		low.next();
		low_frame = low.run(unfiltered);
		check(low_frame.poses.size() == 1 && low_frame.poses[0].score == -.5f,
			"negative finite Top1 incorrectly filtered");
		low.scores.fill(0);
		low.next();
		low_frame = low.run(unfiltered);
		check(low_frame.raw_poses.size() == 1 && low_frame.raw_poses[0].candidate == 0,
			"disabled cutoff tie order");
		low.scores[17] = std::numeric_limits<float>::quiet_NaN();
		low.next();
		bool low_rejected = false;
		try {
			low.run(unfiltered);
		} catch (...) {
			low_rejected = true;
		}
		check(low_rejected, "disabled cutoff accepted nonfinite scores");
		Config invalid_top;
		invalid_top.top_k = 0;
		Postprocessor bad_top(invalid_top);
		bool invalid_top_rejected = false;
		try {
			single.run(bad_top);
		} catch (...) {
			invalid_top_rejected = true;
		}
		check(invalid_top_rejected, "invalid TopK rejected");
		Config high = two_hits;
		high.score_threshold = .35f;
		Postprocessor threshold(high);
		Sample boundary;
		boundary.person(0, 0, .35f);
		boundary.person(1, 2, std::nextafter(.35f, 0.f));
		boundary.person(2, 4, std::nextafter(.35f, 1.f));
		const auto boundary_scores = boundary.scores;
		auto threshold_frame = boundary.run(threshold);
		check(boundary.scores == boundary_scores, "threshold selection rewrote raw scores");
		check(threshold_frame.raw_poses.size() == 1 && threshold_frame.raw_poses[0].candidate == 2 &&
				threshold_frame.score_threshold == .35f,
			"strict configurable float32 score threshold");
		boundary.next();
		check(boundary.run(threshold).poses.size() == 1, "above-threshold candidate confirms");
		boundary.scores.fill(.35f);
		boundary.next();
		threshold_frame = boundary.run(threshold);
		check(threshold_frame.raw_poses.empty() && threshold_frame.poses.size() == 1 &&
				threshold_frame.poses[0].held,
			"threshold miss retains bounded valid history");
		boundary.next(251);
		check(boundary.run(threshold).poses.empty(), "threshold miss expires");
		Config half = two_hits;
		half.score_threshold = .5f;
		Postprocessor threshold_half(half);
		Sample half_boundary;
		half_boundary.person(0, 0, .5f);
		half_boundary.person(1, 2, std::nextafter(.5f, 0.f));
		half_boundary.person(2, 4, std::nextafter(.5f, 1.f));
		const auto half_frame = half_boundary.run(threshold_half);
		check(half_frame.raw_poses.size() == 1 && half_frame.raw_poses[0].candidate == 2 &&
				half_frame.score_threshold == .5f,
			"prepared 0.5 threshold boundary");
		Config invalid_threshold;
		invalid_threshold.score_threshold = std::numeric_limits<float>::quiet_NaN();
		Postprocessor invalid_score(invalid_threshold);
		bool invalid_score_rejected = false;
		try {
			boundary.run(invalid_score);
		} catch (...) {
			invalid_score_rejected = true;
		}
		check(invalid_score_rejected, "nonfinite score threshold rejected");
		Postprocessor p(two_hits);
		Sample s;
		s.person(7, 1);
		check(s.run(p).poses.empty(), "birth confirmation");
		s.next();
		auto f = s.run(p);
		check(f.poses.size() == 1, "second confirmation");
		auto id = f.poses[0].track;
		s.scores[7] = 0;
		s.person(19, 1.01);
		s.next();
		f = s.run(p);
		check(f.poses[0].track == id && f.poses[0].candidate == 19, "query is not identity");
		s.person(20, 1.01, .79f);
		s.next();
		f = s.run(p);
		check(f.poses.size() == 1 && p.metrics().duplicates > 0, "dedup");
		s.scores.fill(.2f);
		s.next();
		f = s.run(p);
		check(f.poses.size() == 1 && f.poses[0].held, "strict threshold/hold");
		s.next(251);
		check(s.run(p).poses.empty(), "expiry");
		s.person(1, 1);
		s.next();
		check(s.run(p).poses.empty(), "reappearance first");
		s.next();
		f = s.run(p);
		check(f.poses.size() == 1 && f.poses[0].track != id, "new identity after expiry");
		id = f.poses[0].track;
		s.person(1, 10);
		s.next();
		f = s.run(p);
		check(f.poses.size() == 1 && f.poses[0].held && f.poses[0].joints[0] < 2,
			"single spike must not drag track");
		s.person(1, 1);
		s.next();
		f = s.run(p);
		check(f.poses[0].track == id && !f.poses[0].held, "recover from spike");
		s.session = 2;
		s.next();
		check(s.run(p).poses.empty(), "epoch reset");
		s.next();
		s.run(p);
		s.ns -= 100000000;
		check(s.run(p).poses.empty(), "time regression reset");
		s.poses[0] = std::numeric_limits<float>::quiet_NaN();
		bool rejected = false;
		try {
			s.run(p);
		} catch (...) {
			rejected = true;
		}
		check(rejected, "nonfinite rejected");
		Postprocessor multi(two_hits);
		Sample m;
		m.person(1, 0);
		m.person(2, 2);
		m.person(3, 4);
		m.person(4, 6, .7f);
		auto before = m.poses;
		m.run(multi);
		m.next();
		auto mf = m.run(multi);
		check(mf.poses.size() == 3, "top3 cap");
		check(m.poses == before, "immutable raw");
		m.scores[1] = .7;
		m.scores[2] = .9;
		m.next();
		auto mf2 = m.run(multi);
		check(mf2.poses[0].track == mf.poses[0].track, "rank reorder keeps ID ordering");
		// Real r3 retained candidates had centre/RMS separation ~0.254 of body
		// radius: the original 0.2 gate let near-identical skeletons through.
		Postprocessor overlap(two_hits);
		Config old_config = two_hits;
		old_config.duplicate_centre = old_config.duplicate_pose = .2;
		old_config.duplicate_translation = 0;
		Postprocessor old_overlap(old_config);
		Sample o;
		o.person(1, 0, .8f);
		o.person(2, .16, .7f);
		const auto untouched = o.poses;
		o.run(overlap);
		o.run(old_overlap);
		o.next();
		auto one = o.run(overlap), two = o.run(old_overlap);
		check(one.poses.size() == 1 && one.poses[0].candidate == 1 && two.poses.size() == 2,
			"near duplicate keeps higher score");
		check(one.raw_poses.size() == 2 && o.poses == untouched, "dedup preserves raw comparison");
		Postprocessor separate(two_hits);
		Sample sep;
		sep.person(1, 0);
		sep.person(2, .55);
		sep.run(separate);
		sep.next();
		check(sep.run(separate).poses.size() == 2, "nearby separate people retained");
		Postprocessor pending(two_hits);
		Sample q;
		q.person(0, 0);
		q.run(pending);
		q.next();
		q.scores.fill(0);
		q.run(pending);
		q.person(0, 0);
		q.next();
		check(q.run(pending).poses.empty(), "nonconsecutive confirmation");
		q.next();
		check(q.run(pending).poses.size() == 1, "consecutive confirmation after miss");
		q.person(0, 10);
		q.next(110);
		auto displaced = q.run(pending);
		check(displaced.poses.size() == 1 && displaced.poses[0].held,
			"persistent displacement first observation");
		q.next(61);
		displaced = q.run(pending);
		check(displaced.poses.size() == 2 && !displaced.poses[0].held && displaced.poses[0].joints[0] > 9,
			"persistent new location confirmed before old expires");
		Postprocessor crossing(two_hits);
		Sample c;
		std::uint64_t left = 0, right = 0;
		for (unsigned n = 0; n < 18; ++n) {
			c.scores.fill(0);
			c.person(n % 2 ? 2 : 1, -.7 + .09 * n);
			c.person(n % 2 ? 1 : 2, .7 - .09 * n);
			// Distinct relative skeletons remain distinguishable as centres cross.
			for (unsigned j = 0; j < 14; ++j)
				c.poses[(n % 2 ? 1 : 2) * 42 + j * 3 + 2] += (j % 2 ? .35f : -.35f);
			auto cf = c.run(crossing);
			if (n == 1) {
				left = cf.poses[0].track;
				right = cf.poses[1].track;
			}
			if (n > 1) {
				check(cf.poses.size() == 2, "crossing count");
				for (const auto& person : cf.poses) {
					check(person.track == left || person.track == right, "crossing identity rebuild");
					check(person.candidate == (person.track == left ? (n % 2 ? 2u : 1u) : (n % 2 ? 1u : 2u)),
						"crossing swapped identities");
				}
			}
			c.next(n % 2 ? 61 : 110);
		}
		Postprocessor stable_birth;
		Sample sb;
		sb.person(0, 0);
		sb.run(stable_birth);
		sb.next();
		check(sb.run(stable_birth).poses.empty(), "two-frame transient stays pending");
		sb.next();
		check(sb.run(stable_birth).poses.size() == 1, "third consistent observation confirms");
		check(stable_birth.metrics().confirmation_max_ns == 134000000,
			"confirmation latency includes entire pending interval");
		Postprocessor interrupted_birth;
		Sample ib;
		ib.person(0, 0);
		ib.run(interrupted_birth);
		ib.next();
		ib.run(interrupted_birth);
		ib.scores.fill(0);
		ib.next();
		ib.run(interrupted_birth);
		ib.person(0, 0);
		ib.next();
		check(ib.run(interrupted_birth).poses.empty(), "three-hit confirmation restarts after miss");
		ib.next();
		check(ib.run(interrupted_birth).poses.empty(), "old pending hits cannot be reused");
		ib.next();
		check(ib.run(interrupted_birth).poses.size() == 1, "three new consecutive observations confirm");
		Postprocessor translated;
		Sample tr;
		tr.person(0, 0, .9f);
		tr.person(1, .3, .7f);
		for (unsigned k = 0; k < 3; ++k) {
			auto tf = tr.run(translated);
			check(tf.raw_poses.size() == 2, "translated copy remains in raw output");
			if (k == 2)
				check(tf.poses.size() == 1 && tf.poses[0].candidate == 0,
					"translated shape duplicate suppressed");
			tr.next();
		}
		// Score swaps inside a duplicate group must not move an established body.
		Postprocessor winner;
		Sample w;
		w.person(0, 0, .8f);
		PresentationFrame wf;
		for (unsigned k = 0; k < 3; ++k) {
			wf = w.run(winner);
			w.next();
		}
		auto winner_id = wf.poses.at(0).track;
		for (unsigned k = 0; k < 8; ++k) {
			w.person(0, 0, k % 2 ? .9f : .7f);
			w.person(1, .3, k % 2 ? .7f : .9f);
			wf = w.run(winner);
			check(wf.poses.size() == 1 && wf.poses[0].track == winner_id && wf.poses[0].candidate == 0,
				"score swap displaced established representative");
			check(wf.raw_poses.size() == 2 && wf.raw_poses[0].candidate == (k % 2 ? 0u : 1u),
				"raw ranking was rewritten");
			w.next();
		}
		check(winner.metrics().history_selections > 0, "history selection not observed");
		// A missed old track and a newly confirmed replacement must share one ID
		// after two compatible witnesses. A stale velocity alone must not fork it.
		Postprocessor handoff;
		Sample h;
		h.person(0, 0);
		PresentationFrame hf;
		for (unsigned k = 0; k < 3; ++k) {
			hf = h.run(handoff);
			h.next();
		}
		auto handoff_id = hf.poses.at(0).track;
		h.person(0, .45);
		h.run(handoff);
		h.next();
		for (unsigned k = 0; k < 3; ++k) {
			h.scores.fill(0);
			h.person(10, 0);
			hf = h.run(handoff);
			h.next();
		}
		check(hf.poses.size() == 1 && hf.poses[0].track == handoff_id && !hf.poses[0].held,
			"replacement produced a second body");
		Postprocessor reversal;
		Sample rv;
		PresentationFrame rf;
		for (unsigned k = 0; k < 12; ++k) {
			rv.person(0, .15 * (int(k) - 11));
			rf = rv.run(reversal);
			rv.next();
		}
		auto reversal_id = rf.poses.at(0).track;
		rv.person(0, -.4);
		rv.run(reversal);
		rv.next();
		for (unsigned k = 0; k < 3; ++k) {
			rv.scores.fill(0);
			rv.person(9, -.88);
			rf = rv.run(reversal);
			rv.next();
		}
		check(rf.poses.size() == 1 && rf.poses[0].track == reversal_id && !rf.poses[0].held,
			"reversal failed to retain the old filter identity");
		Postprocessor independent;
		Sample ip;
		ip.person(0, 0);
		for (unsigned k = 0; k < 3; ++k) {
			ip.run(independent);
			ip.next();
		}
		for (unsigned k = 0; k < 3; ++k) {
			ip.person(1, .45);
			hf = ip.run(independent);
			ip.next();
		}
		check(hf.poses.size() == 2 && independent.metrics().held_handoffs == 0,
			"simultaneous nearby people were merged");
		Postprocessor shadow;
		Sample ss;
		ss.person(0, 0, .95f);
		for (unsigned k = 0; k < 3; ++k) {
			ss.run(shadow);
			ss.next();
		}
		for (unsigned k = 0; k < 5; ++k) {
			ss.person(1, .55, .3f);
			auto sf = ss.run(shadow);
			check(sf.poses.size() == 1 && sf.raw_poses.size() == 2,
				"weak translated shadow became a second body");
			ss.next();
		}
		check(shadow.metrics().shadow_deferred > 0, "shadow confirmation never delayed");
		for (unsigned k = 0; k < 6; ++k) {
			ss.person(1, .55, .95f);
			hf = ss.run(shadow);
			ss.next();
		}
		check(hf.poses.size() == 2, "independently supported neighbour stayed suppressed");
		Postprocessor weak_far;
		Sample far;
		far.person(0, 0, .95f);
		far.person(1, 2, .21f);
		for (unsigned k = 0; k < 3; ++k) {
			hf = far.run(weak_far);
			far.next();
		}
		check(hf.poses.size() == 2, "shadow rule became a global score threshold");
		// Optional identity retention is invisible, bounded, and reset by epoch.
		Config retained;
		retained.identity_ns = 600000000;
		Postprocessor dormant(retained);
		Sample ds;
		ds.person(0, 0);
		PresentationFrame df;
		for (unsigned k = 0; k < 3; ++k) {
			df = ds.run(dormant);
			ds.next();
		}
		auto retained_id = df.poses.at(0).track;
		ds.scores.fill(0);
		ds.next(260);
		check(ds.run(dormant).poses.empty(), "hidden identity leaked an expired pose");
		ds.person(1, .02);
		ds.next();
		df = ds.run(dormant);
		check(df.poses.size() == 1 && df.poses[0].track == retained_id && !df.poses[0].held,
			"strict hidden reacquisition failed");
		ds.scores.fill(0);
		ds.next(601);
		check(ds.run(dormant).poses.empty(), "identity expiry drew a pose");
		ds.person(1, 0);
		ds.next();
		check(ds.run(dormant).poses.empty(), "expired identity skipped confirmation");
		ds.session = 7;
		ds.next();
		check(ds.run(dormant).poses.empty(), "retained identity crossed a recovery epoch");
		// A single limb spike can hide inside an all-joint RMS gate. It must not
		// update position, derivative, velocity, or last-valid time of the old track.
		Postprocessor limb;
		Sample ls;
		ls.person(0, 0);
		PresentationFrame lf;
		for (unsigned k = 0; k < 3; ++k) {
			lf = ls.run(limb);
			ls.next();
		}
		const auto valid_limb = lf.poses.at(0);
		ls.poses[12 * 3] += 2.f;
		const auto bad_limb = ls.poses;
		lf = ls.run(limb);
		check(lf.poses.size() == 1 && lf.poses[0].held && lf.poses[0].observed_ns == valid_limb.observed_ns &&
				lf.poses[0].joints == valid_limb.joints,
			"limb spike contaminated committed state");
		check(ls.poses == bad_limb && lf.raw_poses[0].joints[12 * 3] == bad_limb[12 * 3],
			"limb rejection rewrote raw output");
		check(limb.metrics().joint_gate_rejections + limb.metrics().bone_gate_rejections > 0,
			"local quality gate was not exercised");
		ls.person(0, 0);
		ls.next();
		lf = ls.run(limb);
		check(lf.poses.size() == 1 && lf.poses[0].track == valid_limb.track && !lf.poses[0].held &&
				lf.poses[0].joints == valid_limb.joints,
			"rejected limb left a filter tail");
		Postprocessor bone;
		Sample bs;
		bs.person(0, 0);
		PresentationFrame bf;
		for (unsigned k = 0; k < 3; ++k) {
			bf = bs.run(bone);
			bs.next();
		}
		const auto valid_bone = bf.poses.at(0);
		bs.poses[12 * 3] += 1.f;
		bf = bs.run(bone);
		check(bone.metrics().bone_gate_rejections > 0 && bone.metrics().joint_gate_rejections == 0,
			"bone evidence was hidden by the larger joint gate");
		check(bf.poses.size() == 1 && bf.poses[0].held && bf.poses[0].joints == valid_bone.joints &&
				bf.poses[0].observed_ns == valid_bone.observed_ns,
			"bone anomaly contaminated a valid pose");
		// Presentation smoothing may lag without forcing a moving identity to split.
		Config slow;
		slow.min_cutoff = .05;
		slow.beta = .01;
		Postprocessor fast_track, slow_track(slow);
		Sample motion;
		std::uint64_t fast_id = 0, slow_id = 0;
		for (unsigned k = 0; k < 80; ++k) {
			motion.person(0, .1 * k);
			auto a = motion.run(fast_track), b = motion.run(slow_track);
			check(a.poses.size() == b.poses.size(), "display cutoff changed isolated association");
			if (k == 2) {
				fast_id = a.poses[0].track;
				slow_id = b.poses[0].track;
			}
			if (k >= 2)
				check(a.poses[0].track == fast_id && b.poses[0].track == slow_id && !a.poses[0].held &&
						!b.poses[0].held,
					"display lag rebuilt a moving track");
			motion.next();
		}
		OneEuro noise;
		std::mt19937 rng(42);
		std::normal_distribution<double> n(0, .025);
		double raw = 0, filtered = 0;
		for (unsigned i = 0; i < 1000; ++i) {
			double x = n(rng), y = noise.update(x, 1. / 15, {});
			if (i > 100) {
				raw += x * x;
				filtered += y * y;
			}
		}
		const double reduction = 1 - std::sqrt(filtered / raw);
		check(reduction >= .4, "jitter target");
		OneEuro moving;
		std::vector<double> truth, shown;
		for (unsigned i = 0; i < 600; ++i) {
			double x = std::sin(i / 15. * 6.283185307179586);
			truth.push_back(x);
			shown.push_back(moving.update(x, 1. / 15, {}));
		}
		unsigned lag = 0;
		double minerr = 1e99;
		for (unsigned k = 0; k < 5; ++k) {
			double err = 0;
			for (unsigned i = 100; i < 600; ++i)
				err += std::pow(shown[i] - truth[i - k], 2);
			if (err < minerr) {
				minerr = err;
				lag = k;
			}
		}
		check(lag <= 1, "15Hz motion latency target");
		std::cout << "{\"passed\":true,\"jitter_reduction\":" << reduction
				  << ",\"motion_lag_ms\":" << lag * 1000. / 15 << "}\n";
	} catch (const std::exception& e) {
		std::cerr << e.what() << '\n';
		return 1;
	}
}
