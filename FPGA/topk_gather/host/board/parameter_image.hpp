#pragma once
#include <algorithm>
#include <cstdint>
#include <stdexcept>
#include <vector>

namespace topk::board {
struct ParameterPart {
    const char* data;
    std::uint64_t offset;
    std::uint64_t bytes;
};

// Assemble a completely covered image from separate host allocations. Never
// infer adjacency between allocations or read beyond a part's declared size.
inline std::vector<char> parameter_image(std::uint64_t bytes, std::vector<ParameterPart> parts) {
    if (bytes > 64 * 1024 * 1024) throw std::runtime_error("Parameter image exceeds diagnostic budget");
    std::sort(parts.begin(), parts.end(), [](const auto& a, const auto& b) { return a.offset < b.offset; });
    std::uint64_t end = 0;
    for (const auto& part : parts) {
        if (!part.data || !part.bytes || part.offset != end || part.offset > bytes || part.bytes > bytes - part.offset)
            throw std::runtime_error("Parameter parts overlap, leave a gap, or exceed the image");
        end += part.bytes;
    }
    if (end != bytes) throw std::runtime_error("Parameter image is not fully covered");
    std::vector<char> result(static_cast<std::size_t>(bytes));
    for (const auto& part : parts) std::copy_n(part.data, part.bytes, result.data() + part.offset);
    return result;
}
} // namespace topk::board
