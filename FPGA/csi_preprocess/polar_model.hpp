#pragma once
#include <cstdint>
namespace csi_pl {
struct Polar { std::uint32_t magnitude; std::int32_t angle; };
// Integer model of the RTL: IEEE FP32 input, magnitude FP32, angle pi*2^-30.
Polar polar(std::uint32_t real, std::uint32_t imag);
}
