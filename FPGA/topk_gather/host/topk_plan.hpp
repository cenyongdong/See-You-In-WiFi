#pragma once

#include <cstdint>
#include <vector>

namespace topk {

enum class Layout { dense, blocked16 };

// Logical payload shape [batches, candidates, channels]; scores have one value
// per candidate. Leading/trailing dimensions may be flattened by the caller.
struct Shape {
    std::uint64_t batches;
    std::uint64_t candidates;
    std::uint64_t keep;
    std::uint64_t channels;
    std::uint32_t element_bytes;
};

struct Limits {
    std::uint32_t tile_capacity = 256;
    std::uint64_t scratch_bytes = 64 * 1024 * 1024;
    std::uint64_t max_jobs = 1000000;
};

enum class JobKind { sort_tile, merge_runs, gather };
constexpr std::uint64_t no_run = UINT64_MAX;

struct Job {
    JobKind kind;
    std::uint64_t batch;
    std::uint64_t input_offset;
    std::uint64_t input_count;
    std::uint64_t keep;
    std::uint64_t left = no_run;
    std::uint64_t right = no_run;
    std::uint64_t output = no_run;
};

struct Plan {
    Shape shape;
    std::vector<Job> jobs;
    std::vector<std::uint64_t> result_runs;
    std::uint64_t scratch_bytes = 0;
};

// Batches execute sequentially and reuse two scratch arenas. Local truncation
// always keeps min(global K, tile size), including when K exceeds tile capacity.
Plan make_plan(Shape shape, Limits limits = {});

struct TensorMemory {
    std::uint32_t base;
    std::uint32_t allocation_bytes;
    Layout layout;
};

struct GatherDescriptor {
    std::uint32_t candidates, keep, channels, element_bytes;
    TensorMemory source, destination;
    std::uint32_t source_row_stride, source_block_stride;
    std::uint32_t destination_row_stride, destination_block_stride;
};

// One batch, canonical dense/C16 layout. Addresses are device DDR offsets,
// never host pointers. Full cache-line tails must belong to the allocations.
GatherDescriptor make_gather_descriptor(Shape shape, TensorMemory source,
                                        TensorMemory destination);

struct KernelMemory {
    TensorMemory scores, features;
    TensorMemory selected_scores, selected_indices, selected_features;
};

struct KernelDescriptor {
    GatherDescriptor gather;
    TensorMemory scores, selected_scores, selected_indices;
    std::uint32_t score_element_bytes;
};

// One memory-to-memory fast-path job (N <= 256). Scores are dense FP16/FP32;
// selected scores are dense FP32 and indices are dense uint64. Every output
// allocation is disjoint from all inputs and other outputs, including padding.
KernelDescriptor make_kernel_descriptor(Shape shape, std::uint32_t score_element_bytes,
                                        const KernelMemory& memory);

struct RunGatherMemory {
    TensorMemory records, features, selected_scores, selected_indices, selected_features;
};

struct RunGatherDescriptor {
    GatherDescriptor gather;
    TensorMemory records, selected_scores, selected_indices;
};

// Final tiled-plan stage. The completed run holds K packed 16-byte records.
// This descriptor is for INPUT_IS_SORTED_RUN=1, not the ABI 1.0 fast-path CSR.
RunGatherDescriptor make_run_gather_descriptor(Shape shape, const RunGatherMemory& memory);

struct TileDescriptor {
    TensorMemory scores, destination;
    std::uint32_t count, keep, score_element_bytes;
    std::uint64_t index_base;
};
struct MergeDescriptor {
    TensorMemory left, right, destination;
    std::uint32_t left_count, right_count, keep;
    std::uint64_t index_limit;
};
TileDescriptor make_tile_descriptor(TensorMemory scores, TensorMemory destination,
    std::uint32_t count, std::uint32_t keep, std::uint32_t score_element_bytes, std::uint64_t index_base);
MergeDescriptor make_merge_descriptor(TensorMemory left, TensorMemory right, TensorMemory destination,
    std::uint32_t left_count, std::uint32_t right_count, std::uint32_t keep, std::uint64_t index_limit);

// Device-specific code must supply actual completion/STOP evidence. This state
// machine cannot create it, and deliberately has no timeout-to-success path.
class JobGuard {
public:
    enum class State { idle, waiting_for_producer, ready, running, quarantined, complete };

    void reserve(std::uint64_t id);
    bool producer_completed(std::uint64_t id, bool writes_visible);
    void start();
    bool completed(std::uint64_t id, bool writes_visible, std::uint64_t outstanding,
                   bool valid_output);
    void fault();
    bool stopped_and_drained(std::uint64_t id, bool hardware_stopped,
                             std::uint64_t outstanding);
    void release();

    State state() const noexcept { return state_; }
    bool publishable() const noexcept { return state_ == State::complete && valid_output_; }
    bool releasable() const noexcept { return state_ == State::complete; }

private:
    State state_ = State::idle;
    std::uint64_t id_ = 0;
    std::uint64_t last_id_ = 0;
    bool valid_output_ = false;
};

}  // namespace topk
