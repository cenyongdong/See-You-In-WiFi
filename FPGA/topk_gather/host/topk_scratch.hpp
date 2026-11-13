#pragma once

#include "topk_plan.hpp"

namespace topk {

// Wire format in little-endian device DDR: score bits, zero padding, index.
// No float conversion occurs while records move between tile/merge stages.
struct ScratchRecord {
    std::uint32_t score_bits;
    std::uint32_t reserved;
    std::uint64_t index;
};
static_assert(sizeof(ScratchRecord) == 16, "scratch record wire size");

struct RunAllocation {
    std::uint32_t address;
    std::uint32_t reserved_bytes;
    std::uint64_t record_count;
    std::uint64_t batch;
    std::uint32_t arena_index;
};

struct ScratchBindings {
    std::uint64_t arena_bytes;
    std::vector<RunAllocation> runs;  // Indexed by Job::{left,right,output}.
};

// Bind a make_plan() DAG to two already-owned, disjoint DDR allocations.
// A run reserves its original candidate interval, including leaf padding.
// Assign arena parity BACKWARDS from each root: even an odd carried run then
// shares the opposite arena with its sibling. No carry copy or in-place merge
// is needed. Sequential batches reuse storage only after the prior job drains.
ScratchBindings bind_scratch(const Plan& plan, TensorMemory first, TensorMemory second);

}  // namespace topk
