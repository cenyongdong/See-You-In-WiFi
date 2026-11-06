// SDK-independent tests of unchanged 100-slot output and new 180-slot display.
#include "hdmi_renderer.hpp"
#include <algorithm>
#include <array>
#include <cmath>
#include <cstring>
#include <iostream>
#include <limits>
#include <stdexcept>
#include <utility>
#include <fstream>

namespace {
namespace hdmi = pose::hdmi;
using Status = pose_v1::render::Status;

void expect(bool yes, const char* message) {
	if (!yes)
		throw std::runtime_error(message);
}

template <std::size_t Candidates>
void fill_model(
	std::array<float, Candidates>& scores, std::array<float, Candidates * 42>& poses, std::size_t selected) {
	scores.fill(0.125f);
	scores[selected] = 0.9375f;
	for (std::size_t slot = 0; slot < Candidates; ++slot)
		for (std::size_t joint = 0; joint < 14; ++joint) {
			const auto offset = slot * 42 + joint * 3;
			poses[offset] = 1.25f + float(joint % 4) * 0.125f + float(slot) / 1024.0f;
			poses[offset + 1] = 1.5f + float(joint % 3) * 0.1875f;
			poses[offset + 2] = 2.75f + float(joint) * 0.0625f;
		}
}

void compare_display_values(const hdmi::Rendered& old, const hdmi::Rendered& current) {
	expect(old.rgb565 == current.rgb565, "100-slot compatibility changed RGB565 pixels");
	expect(old.top_index == current.top_index && old.score == current.score,
		"100-slot compatibility changed the highest score selection");
	expect(old.selected_raw == current.selected_raw && old.projected == current.projected &&
			old.clipped_joints == current.clipped_joints,
		"100-slot compatibility changed selected model coordinates or projection");
}

void old_100_wrapper_matches_pointer_100() {
	std::array<float, 100> scores;
	std::array<float, 4200> poses;
	fill_model(scores, poses, 73);
	for (auto status : {Status::Result, Status::NoInput, Status::Stopped}) {
		const auto original_scores = scores;
		const auto original_poses = poses;
		const auto old = hdmi::render(scores, poses, 12345678901234567890ull, status);
		auto background = hdmi::prepare_background();
		const auto current = hdmi::render(std::move(background), scores.data(), poses.data(), scores.size(),
			12345678901234567890ull, status);
		compare_display_values(old, current);
		expect(
			scores == original_scores && poses == original_poses, "Rendering modified model output values");
	}
}

void new_180_selects_last_candidate_and_reuses_canvas() {
	std::array<float, 180> scores;
	std::array<float, 7560> poses;
	fill_model(scores, poses, 179);
	const auto original_scores = scores;
	const auto original_poses = poses;
	auto background = hdmi::prepare_background();
	auto* const canvas = background.rgb565.data();
	const auto capacity = background.rgb565.capacity();
	expect(background.rgb565.size() == hdmi::frameBytes, "Prepared canvas dimensions differ");
	for (std::uint64_t frame = 1; frame <= 3; ++frame) {
		auto rendered =
			hdmi::render(std::move(background), scores.data(), poses.data(), scores.size(), frame);
		expect(rendered.rgb565.data() == canvas && rendered.rgb565.capacity() == capacity,
			"Rendering allocated another CPU frame instead of moving reusable storage");
		expect(rendered.top_index == 179 && rendered.score == scores[179],
			"180-slot renderer ignored the highest candidate at index 179");
		expect(!std::memcmp(rendered.selected_raw.data(), poses.data() + 179 * 42, 168),
			"180-slot renderer selected another candidate's pose bytes");
		for (std::size_t joint = 0; joint < 14; ++joint) {
			const auto p = rendered.projected[joint];
			expect(std::isfinite(p[0]) && std::isfinite(p[1]) && p[0] >= 0 && p[0] < 1920 && p[1] >= 250 &&
					p[1] < 1040,
				"Perspective fixture escaped the scene or entered the status header");
		}
		// A fresh canvas for the same frame detects stale skeletons/labels when
		// the recycled buffer is refilled from the immutable prepared base.
		auto fresh = hdmi::prepare_background();
		auto reference = hdmi::render(std::move(fresh), scores.data(), poses.data(), scores.size(), frame);
		expect(rendered.rgb565 == reference.rgb565, "Reused CPU canvas retained a previous frame's pixels");
		background.rgb565 = std::move(rendered.rgb565);
		hdmi::prepare_background(background);
		expect(background.rgb565.data() == canvas && background.rgb565.capacity() == capacity,
			"Replenishing the reusable background allocated another frame buffer");
	}
	expect(scores == original_scores && poses == original_poses, "180-slot rendering modified model outputs");
}

bool same_scene(const std::vector<uint8_t>& a, const std::vector<uint8_t>& b) {
	return std::equal(a.begin() + 250 * 1920 * 2, a.begin() + 1040 * 1920 * 2, b.begin() + 250 * 1920 * 2);
}

void top_three_then_strict_threshold() {
	std::array<float, 180> scores;
	std::array<float, 7560> poses;
	fill_model(scores, poses, 179);
	scores[4] = 0.8f;
	scores[6] = 0.7f;
	scores[8] = 0.6f;
	const auto source_scores = scores;
	const auto source_poses = poses;
	auto render = [&] {
		return hdmi::render(
			hdmi::prepare_background(), scores.data(), poses.data(), 180, 9, Status::Result, {3, 0.2f});
	};
	auto three = render();
	expect(three.detection_count == 3, "Top-k did not cap qualified candidates at three");
	const unsigned indices[] = {179, 4, 6};
	for (unsigned i = 0; i < 3; ++i) {
		expect(three.detections[i].index == indices[i], "Candidates not ranked by score");
		expect(!std::memcmp(three.detections[i].raw.data(), poses.data() + indices[i] * 42, 168),
			"Top-k pose no longer matches its original score index");
	}
	expect(scores == source_scores && poses == source_poses, "Top-k mutated raw output");
	auto held =
		hdmi::render_notice(hdmi::prepare_background(), &three, 9, {hdmi::NoticeKind::Stale, true, false, 2});
	expect(held.detection_count == 3 && same_scene(held.rgb565, three.rgb565),
		"Stale notice lost or changed a qualified skeleton");
	scores.fill(0.1f);
	scores[3] = 0.2f;
	scores[5] = std::nextafter(0.2f, 1.f);
	scores[7] = 0.9f;
	auto two = render();
	expect(two.detection_count == 2 && two.detections[0].index == 7 && two.detections[1].index == 5,
		"Threshold must strictly exclude exactly 0.2 and include its next float");
	scores.fill(0.1f);
	scores[1] = scores[2] = scores[3] = scores[4] = 0.5f;
	auto ties = render();
	expect(ties.detection_count == 3 && ties.detections[0].index == 1 && ties.detections[1].index == 2 &&
			ties.detections[2].index == 3,
		"Tie selection is not deterministic");
	scores.fill(0.2f);
	hdmi::PreparedBackground reused{std::move(three.rgb565)};
	hdmi::prepare_background(reused);
	auto none =
		hdmi::render(std::move(reused), scores.data(), poses.data(), 180, 10, Status::Result, {3, 0.2f});
	expect(none.detection_count == 0 && same_scene(none.rgb565, hdmi::prepare_background().rgb565),
		"No qualified detection retained an old skeleton or forced a top-1 pose");
	auto empty_stale =
		hdmi::render_notice(hdmi::prepare_background(), &none, 10, {hdmi::NoticeKind::Stale, true, false, 2});
	expect(empty_stale.detection_count == 0 && same_scene(empty_stale.rgb565, none.rgb565),
		"Stale empty result manufactured a skeleton");
	scores[179] = std::numeric_limits<float>::quiet_NaN();
	bool rejected = false;
	try {
		render();
	} catch (const std::runtime_error&) {
		rejected = true;
	}
	expect(rejected, "Nonfinite output accepted by top-k");
}
} // namespace

int main(int argc, char** argv) {
	try {
		old_100_wrapper_matches_pointer_100();
		new_180_selects_last_candidate_and_reuses_canvas();
		top_three_then_strict_threshold();
		pose::post::PresentationFrame frame;
		frame.id = {1, 2, 2, 1067000000};
		pose::post::Person person;
		person.track = 7;
		person.candidate = 19;
		person.score = .8f;
		person.observed_ns = frame.id.source_ns;
		person.held = true;
		for (unsigned j = 0; j < 14; ++j) {
			person.joints[3 * j] = (int(j % 3) - 1) * .3f;
			person.joints[3 * j + 1] = 1;
			person.joints[3 * j + 2] = j * .1f;
		}
		frame.poses.push_back(person);
		frame.score_threshold = .35f;
		frame.top_k = 1;
		auto derived = hdmi::render_presentation(hdmi::prepare_background(), frame);
		expect(derived.selection.threshold == .35f, "Presentation threshold metadata lost");
		expect(derived.selection.top_k == 1, "Presentation TopK metadata lost");
		expect(derived.detection_count == 1 && derived.detections[0].track == 7 &&
				derived.detections[0].held && derived.detections[0].remaining_ns == 250000000,
			"Presentation metadata lost");
		frame.score_threshold.reset();
		frame.poses[0].score = 0;
		auto unfiltered = hdmi::render_presentation(hdmi::prepare_background(), frame);
		expect(!unfiltered.selection.threshold && unfiltered.detection_count == 1 &&
				unfiltered.detections[0].score == 0,
			"Unfiltered presentation changed by HDMI");
		std::array<float, 180> low_scores{};
		std::array<float, 7560> low_poses{};
		auto zero = hdmi::render(hdmi::prepare_background(), low_scores.data(), low_poses.data(), 180, 3,
			pose_v1::render::Status::Result, {1, std::nullopt});
		expect(zero.detection_count == 1 && zero.detections[0].index == 0,
			"Zero-score Top1 removed by raster selection");
		if (argc > 1) {
			std::ofstream out(argv[1], std::ios::binary);
			out << "P6\n1920 1080\n255\n";
			for (std::size_t i = 0; i < derived.rgb565.size(); i += 2) {
				unsigned v = derived.rgb565[i] | (unsigned(derived.rgb565[i + 1]) << 8);
				char rgb[3]{char(((v >> 11) & 31) * 255 / 31), char(((v >> 5) & 63) * 255 / 63),
					char((v & 31) * 255 / 31)};
				out.write(rgb, 3);
			}
			expect(bool(out), "Cannot save offline raster");
		}
		std::cout << "pose180 renderer compatibility/reuse contracts passed\n";
		return 0;
	} catch (const std::exception& e) {
		std::cerr << "pose180 renderer test failed: " << e.what() << '\n';
		return 1;
	}
}
