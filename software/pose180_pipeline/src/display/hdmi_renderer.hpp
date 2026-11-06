// Native HDMI raster; model outputs remain unmodified owning values.
#pragma once
#include <cstddef>
#include "skeleton_render.hpp"
#include "hdmi_format.hpp"
#include "../pose/postprocess.hpp"
#include <array>
#include <cstdint>
#include <limits>
#include <vector>

namespace pose::hdmi {
struct SelectionPolicy {
	unsigned top_k = 1;
	std::optional<float> threshold; // No cutoff unless explicitly selected.
};

struct CandidatePose {
	std::uint64_t track = 0;
	bool held = false;
	std::uint64_t remaining_ns = std::numeric_limits<std::uint64_t>::max();
	unsigned index = 0;
	float score = 0;
	std::array<float, 42> raw{};
	std::array<std::array<double, 2>, 14> projected{};
};

struct Rendered {
	std::vector<uint8_t> rgb565;
	std::vector<uint32_t> commands;
	bool hardware_overlay = false;
	unsigned top_index = 0, clipped_joints = 0;
	float score = 0;
	std::array<float, 42> selected_raw{};
	std::array<std::array<double, 2>, 14> projected{};
	SelectionPolicy selection;
	std::array<CandidatePose, 3> detections{};
	unsigned detection_count = 0;
	double render_ms = 0;
};

// Ordinary owning memory only; no model-value processing or SDK access.
struct PreparedBackground {
	std::vector<uint8_t> rgb565;
};
enum class NoticeKind {
	Result,
	WaitingInput,
	Resynchronizing,
	Stale
};

struct Notice {
	NoticeKind kind = NoticeKind::WaitingInput;
	bool has_result = false, resynchronizing = false;
	std::uint64_t age_seconds = 0;
};

// last_result contains only owning render metadata; its pixel vector may be
// empty. A null pointer draws seven standby bars, never model values.
Rendered render_notice(PreparedBackground&& prepared, const Rendered* last_result, uint64_t last_frame_id,
	const Notice& notice, bool hardware_overlay = false);
PreparedBackground prepare_background();
void prepare_background(PreparedBackground& reusable);
Rendered render_presentation(
	PreparedBackground&&, const pose::post::PresentationFrame&, bool hardware_overlay = false);
Rendered render(PreparedBackground&& prepared, const float* scores, const float* poses,
	std::size_t candidates, uint64_t id, pose_v1::render::Status status = pose_v1::render::Status::Result,
	SelectionPolicy selection = {});
Rendered render(PreparedBackground&& prepared, const std::array<float, 100>& scores,
	const std::array<float, 4200>& poses, uint64_t id,
	pose_v1::render::Status status = pose_v1::render::Status::Result);

Rendered render(const std::array<float, 100>& scores, const std::array<float, 4200>& poses, uint64_t id,
	pose_v1::render::Status status = pose_v1::render::Status::Result);
}
