#pragma once

#include "topk_plan.hpp"

#include <array>
#include <stdexcept>

namespace topk {

// AXI4-Lite local window, ABI 1.0. Platform MMIO and SDK ownership are separate.
constexpr std::uint32_t register_magic = 0x544b4731;
constexpr std::uint32_t register_abi = 0x00010000;
constexpr std::uint32_t command_offset = 0x0c;
constexpr std::uint32_t descriptor_offset = 0x40;
using RegisterImage = std::array<std::uint32_t, 22>;
constexpr std::uint32_t command_register_abi = 0x00020000;
using CommandImage = std::array<std::uint32_t, 32>;
constexpr std::uint32_t format_policy_offset = 0x2c;
enum class HalfPolicy : std::uint32_t { preserve = 0, flush_to_positive_zero = 1 };

// Read the actual CSR identity before START. A compiled compatibility variant
// must never be silently used as an IEEE bit-preserving FP16 kernel.
inline void validate_register_contract(std::uint32_t magic, std::uint32_t abi,
                                      std::uint32_t policy, bool generic, HalfPolicy expected) {
    const auto requested = static_cast<std::uint32_t>(expected);
    if (requested > 1 || magic != register_magic || policy != requested ||
        abi != ((generic ? command_register_abi : register_abi) | requested))
        throw std::invalid_argument("device ABI or FP16 numeric policy does not match the job");
}

// Use the validated make_kernel_descriptor() result. Write all words while
// idle, establish producer visibility, then write START=1 to command_offset.
// Completion is retained until ACK=2. A timeout does not authorize reset/free.
inline RegisterImage make_register_image(std::uint64_t job_id, const KernelDescriptor& descriptor) {
    if (!job_id) throw std::invalid_argument("job identity must be nonzero");
    const auto& g = descriptor.gather;
    return {{static_cast<std::uint32_t>(job_id), static_cast<std::uint32_t>(job_id >> 32),
             g.candidates, g.keep, g.channels,
             descriptor.scores.base, descriptor.scores.allocation_bytes, descriptor.score_element_bytes,
             g.element_bytes,
             (g.source.layout == Layout::blocked16 ? 1u : 0u) |
                 (g.destination.layout == Layout::blocked16 ? 2u : 0u),
             g.source.base, g.source.allocation_bytes, g.source_row_stride, g.source_block_stride,
             g.destination.base, g.destination.allocation_bytes, g.destination_row_stride, g.destination_block_stride,
             descriptor.selected_scores.base, descriptor.selected_scores.allocation_bytes,
             descriptor.selected_indices.base, descriptor.selected_indices.allocation_bytes}};
}

inline CommandImage make_tile_command(std::uint64_t job_id, const TileDescriptor& d) {
    if (!job_id) throw std::invalid_argument("job identity must be nonzero");
    CommandImage image{};
    image[0] = static_cast<std::uint32_t>(job_id); image[1] = static_cast<std::uint32_t>(job_id >> 32);
    image[2] = d.count; image[3] = d.keep; image[5] = d.scores.base; image[6] = d.scores.allocation_bytes;
    image[7] = d.score_element_bytes; image[14] = d.destination.base; image[15] = d.destination.allocation_bytes;
    image[26] = static_cast<std::uint32_t>(d.index_base); image[27] = static_cast<std::uint32_t>(d.index_base >> 32);
    return image;
}

inline CommandImage make_merge_command(std::uint64_t job_id, const MergeDescriptor& d) {
    if (!job_id) throw std::invalid_argument("job identity must be nonzero");
    CommandImage image{};
    image[0] = static_cast<std::uint32_t>(job_id); image[1] = static_cast<std::uint32_t>(job_id >> 32);
    image[2] = d.left_count; image[3] = d.keep; image[5] = d.left.base; image[6] = d.left.allocation_bytes;
    image[14] = d.destination.base; image[15] = d.destination.allocation_bytes; image[22] = 1;
    image[23] = d.right.base; image[24] = d.right.allocation_bytes; image[25] = d.right_count;
    image[28] = static_cast<std::uint32_t>(d.index_limit); image[29] = static_cast<std::uint32_t>(d.index_limit >> 32);
    return image;
}

inline CommandImage make_run_gather_command(std::uint64_t job_id, const RunGatherDescriptor& d) {
    // The first 22 fields share their physical ABI locations; element size 0
    // is unused for a packed run. Validation was performed by its own factory.
    const auto common = make_register_image(job_id, {d.gather, d.records, d.selected_scores, d.selected_indices, 0});
    CommandImage image{};
    for (std::size_t i = 0; i < common.size(); ++i) image[i] = common[i];
    image[22] = 2;
    return image;
}

}  // namespace topk
