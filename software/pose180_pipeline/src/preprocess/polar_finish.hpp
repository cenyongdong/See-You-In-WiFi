#pragma once
#include "preprocess.hpp"
#include <array>
#include <cstdint>

namespace pose_v1 {
struct PolarSample {
	float magnitude;
	std::int32_t angle;
};

using PolarWindow = std::array<PolarSample, kComplexCount>;
// Lightweight PS stage: phase branch reconstruction, unwrap and affine fit.
// Raw values are retained for exact signed-zero and branch-boundary handling.
Tokens finish_polar(const RawCsi&, const PolarWindow&, unsigned* boundary_fallbacks = nullptr);
// One complete (receiver,time) group. False requests an exact full-window
// fallback; the caller must first finish/contain any outstanding PL work.
bool finish_polar_group(const RawCsi&, const PolarWindow&, std::size_t receiver, std::size_t time, Tokens&,
	unsigned& boundary_fallbacks);
}
