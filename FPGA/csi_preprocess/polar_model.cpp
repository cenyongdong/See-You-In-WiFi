#include "polar_model.hpp"
#include <algorithm>
#include <cmath>
#include <cstring>
#include <stdexcept>
#include <array>

namespace csi_pl {
namespace {
constexpr std::uint32_t kFractionMask = 0x7fffff;
constexpr std::uint32_t kMagnitudeMask = 0x7fffffff;
constexpr unsigned kIterations = 31;
constexpr long long kInverseGainQ31 = 1304065748LL;

// 对齐到共同指数，保留原 16 位保护位和 40 位移位截断边界。
std::int64_t align_component(std::uint32_t bits, unsigned exponent, unsigned shared_exponent) {
    const auto shift = shared_exponent - exponent;
    const auto mantissa = shift >= 40 ? 0 : (std::int64_t((bits & kFractionMask) | 0x800000) << 16) >> shift;
    return (bits >> 31) ? -mantissa : mantissa;
}

const std::array<std::int64_t, kIterations> &angle_table() {
    // 保留初始化时的浮点运算顺序；该表对应 RTL atan_step 的 pi * 2^-30 单位。
    static const auto table = []() {
        std::array<std::int64_t, kIterations> angles{};
        for (unsigned iteration = 0; iteration < kIterations; ++iteration) {
            angles[iteration] =
                std::llround(std::atan(std::ldexp(1., -int(iteration))) * 1073741824. / std::acos(-1.));
        }
        return angles;
    }();
    return table;
}

std::uint32_t pack_magnitude(std::int64_t x, unsigned exponent) {
    // Q31 增益补偿必须先做宽乘法，再右移；不能改用浮点乘法。
    const std::uint64_t magnitude = (__int128(x) * kInverseGainQ31) >> 31;
    unsigned leading = 0;
    for (unsigned bit = 0; bit < 42; ++bit) {
        if (magnitude >> bit) {
            leading = bit;
        }
    }
    const unsigned shift = leading - 23;
    std::uint64_t mantissa = magnitude >> shift;
    if (shift) {
        const auto remainder = magnitude & ((1ULL << shift) - 1);
        const auto half = 1ULL << (shift - 1);
        // IEEE ties-to-even：恰在中点时，只对奇数尾数进位。
        if (remainder > half || (remainder == half && (mantissa & 1))) {
            ++mantissa;
        }
    }
    int output_exponent = int(exponent) + int(leading) - 39;
    if (mantissa & (1ULL << 24)) {
        mantissa >>= 1;
        ++output_exponent;
    }
    if (output_exponent <= 0 || output_exponent >= 255) {
        throw std::runtime_error("Polar magnitude exponent outside normal FP32");
    }
    return std::uint32_t(output_exponent << 23) | (std::uint32_t(mantissa) & kFractionMask);
}
} // namespace

Polar polar(std::uint32_t re, std::uint32_t im) {
    const auto real_exponent = (re >> 23) & 255;
    const auto imag_exponent = (im >> 23) & 255;
    if (real_exponent == 255 || imag_exponent == 255 || (real_exponent == 0 && (re & kFractionMask)) ||
        (imag_exponent == 0 && (im & kFractionMask))) {
        throw std::runtime_error("Polar requires finite normal or zero FP32");
    }

    // 先处理轴上点，保留正负零对负实轴相位符号的影响。
    const bool real_negative = re >> 31;
    const bool imag_negative = im >> 31;
    const auto real_magnitude = re & kMagnitudeMask;
    const auto imag_magnitude = im & kMagnitudeMask;
    if (!imag_magnitude) {
        return {real_magnitude, real_negative ? (imag_negative ? -1073741824 : 1073741824) : 0};
    }
    if (!real_magnitude) {
        return {imag_magnitude, imag_negative ? -536870912 : 536870912};
    }

    const unsigned exponent = std::max(real_exponent, imag_exponent);
    std::int64_t x = align_component(re, real_exponent, exponent);
    std::int64_t y = align_component(im, imag_exponent, exponent);
    std::int64_t z = 0;
    if (real_negative) {
        x = -x;
        y = -y;
        z = imag_negative ? -1073741824LL : 1073741824LL;
    }

    const auto &table = angle_table();
    for (unsigned iteration = 0; iteration < kIterations; ++iteration) {
        const auto step_angle = table[iteration];
        const auto previous_x = x;
        // y 的更新使用旧 x，与 RTL 同一时钟沿的非阻塞赋值一致。
        if (y >= 0) {
            x += y >> iteration;
            y -= previous_x >> iteration;
            z += step_angle;
        } else {
            x -= y >> iteration;
            y += previous_x >> iteration;
            z -= step_angle;
        }
    }
    return {pack_magnitude(x, exponent), std::int32_t(z)};
}
} // namespace csi_pl
