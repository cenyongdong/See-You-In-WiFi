#include "topk_plan.hpp"

#include <algorithm>
#include <limits>
#include <stdexcept>
#include <utility>

namespace topk {
namespace {

std::uint64_t multiply(std::uint64_t left, std::uint64_t right) {
    if (right && left > UINT64_MAX / right) throw std::overflow_error("shape product overflow");
    return left * right;
}

std::uint64_t round_up(std::uint64_t value, std::uint64_t alignment) {
    const auto remainder = value % alignment;
    const auto extra = remainder ? alignment - remainder : 0;
    if (value > UINT64_MAX - extra) throw std::overflow_error("alignment overflow");
    return value + extra;
}

void validate_shape(Shape shape) {
    if (shape.keep > shape.candidates || !shape.channels ||
        (shape.element_bytes != 2 && shape.element_bytes != 4))
        throw std::invalid_argument("require K <= N, C > 0, and FP16/FP32 storage");
    multiply(multiply(multiply(shape.batches, shape.candidates), shape.channels), shape.element_bytes);
}

std::uint32_t narrow(std::uint64_t value) {
    if (value > UINT32_MAX) throw std::overflow_error("descriptor field exceeds 32 bits");
    return static_cast<std::uint32_t>(value);
}

std::uint64_t required_bytes(std::uint64_t rows, std::uint64_t columns,
                             std::uint32_t bytes, Layout layout) {
    if (layout != Layout::dense && layout != Layout::blocked16)
        throw std::invalid_argument("unknown physical layout");
    const auto padded = layout == Layout::blocked16 ? round_up(columns, 16) : columns;
    return round_up(multiply(multiply(rows, padded), bytes), 64);
}

void validate_memory(TensorMemory memory, std::uint64_t required) {
    if ((memory.base % 64) || (memory.allocation_bytes % 64) || !memory.allocation_bytes ||
        memory.allocation_bytes < required ||
        std::uint64_t{memory.base} + memory.allocation_bytes > (std::uint64_t{1} << 32))
        throw std::invalid_argument("unaligned, undersized, or out-of-range device allocation");
}

void validate_dense(TensorMemory memory, std::uint64_t count, std::uint32_t bytes) {
    if (memory.layout != Layout::dense)
        throw std::invalid_argument("record, score and index allocations must be dense");
    validate_memory(memory, required_bytes(count, 1, bytes, Layout::dense));
}

void validate_output_aliases(const TensorMemory (&allocations)[5]) {
    // Inputs occupy slots 0 and 1 and may alias. Every other pair has a writer.
    for (std::size_t left = 0; left < 5; ++left) {
        for (std::size_t right = left + 1; right < 5; ++right) {
            if (left == 0 && right == 1) continue;
            const auto a = allocations[left], b = allocations[right];
            if (std::uint64_t{a.base} < std::uint64_t{b.base} + b.allocation_bytes &&
                std::uint64_t{b.base} < std::uint64_t{a.base} + a.allocation_bytes)
                throw std::invalid_argument("kernel output allocation overlaps another buffer");
        }
    }
}

void reject_overlap(TensorMemory a, TensorMemory b) {
    if (std::uint64_t{a.base} < std::uint64_t{b.base} + b.allocation_bytes &&
        std::uint64_t{b.base} < std::uint64_t{a.base} + a.allocation_bytes)
        throw std::invalid_argument("command allocations overlap");
}

}  // namespace

Plan make_plan(Shape shape, Limits limits) {
    validate_shape(shape);
    if (!limits.tile_capacity || limits.tile_capacity > 256)
        throw std::invalid_argument("tile capacity must match the synthesized core (1..256)");
    Plan plan{shape, {}, {}, 0};
    if (!shape.batches || !shape.keep) return plan;
    const auto tiles = (shape.candidates - 1) / limits.tile_capacity + 1;
    const auto jobs_per_batch = multiply(tiles, 2);  // tiles + (tiles-1) merges + gather
    if (multiply(jobs_per_batch, shape.batches) > limits.max_jobs)
        throw std::length_error("job count exceeds the explicit planning budget");
    // Each leaf owns complete cache lines in both arenas. Rounding only the
    // total would undercount padding when the tile capacity is not a multiple
    // of four records. Batches execute sequentially and reuse these arenas.
    const auto leaf_bytes = round_up(multiply(limits.tile_capacity, 16), 64);
    const auto last_count = shape.candidates - (tiles - 1) * limits.tile_capacity;
    const auto prefix_bytes = multiply(tiles - 1, leaf_bytes);
    const auto tail_bytes = round_up(multiply(last_count, 16), 64);
    if (prefix_bytes > UINT64_MAX - tail_bytes) throw std::overflow_error("scratch extent overflow");
    plan.scratch_bytes = multiply(prefix_bytes + tail_bytes, 2);
    if (plan.scratch_bytes > limits.scratch_bytes)
        throw std::length_error("scratch allocation budget exceeded");
    std::uint64_t next_run = 0;
    for (std::uint64_t batch = 0; batch < shape.batches; ++batch) {
        std::vector<std::pair<std::uint64_t, std::uint64_t>> runs;
        for (std::uint64_t offset = 0; offset < shape.candidates;) {
            const auto count = std::min<std::uint64_t>(limits.tile_capacity, shape.candidates - offset);
            const auto keep = std::min(shape.keep, count);
            plan.jobs.push_back({JobKind::sort_tile, batch, offset, count, keep, no_run, no_run, next_run});
            runs.emplace_back(next_run++, keep);
            offset += count;
        }
        while (runs.size() > 1) {
            std::vector<std::pair<std::uint64_t, std::uint64_t>> merged;
            for (std::size_t i = 0; i < runs.size(); i += 2) {
                if (i + 1 == runs.size()) {
                    merged.push_back(runs[i]);
                    continue;
                }
                const auto count = runs[i].second + runs[i + 1].second;
                const auto keep = std::min(shape.keep, count);
                plan.jobs.push_back({JobKind::merge_runs, batch, 0, count, keep,
                                     runs[i].first, runs[i + 1].first, next_run});
                merged.emplace_back(next_run++, keep);
            }
            runs = std::move(merged);
        }
        plan.result_runs.push_back(runs.front().first);
        plan.jobs.push_back({JobKind::gather, batch, 0, shape.candidates, shape.keep,
                             runs.front().first, no_run, no_run});
    }
    return plan;
}

GatherDescriptor make_gather_descriptor(Shape shape, TensorMemory source,
                                        TensorMemory destination) {
    validate_shape(shape);
    if (shape.batches != 1 || !shape.keep)
        throw std::invalid_argument("gather descriptor requires one nonempty batch");
    validate_memory(source, required_bytes(shape.candidates, shape.channels, shape.element_bytes, source.layout));
    validate_memory(destination, required_bytes(shape.keep, shape.channels, shape.element_bytes, destination.layout));
    if (std::uint64_t{source.base} < std::uint64_t{destination.base} + destination.allocation_bytes &&
        std::uint64_t{destination.base} < std::uint64_t{source.base} + source.allocation_bytes)
        throw std::invalid_argument("source and destination allocations overlap");
    const auto source_row = multiply(source.layout == Layout::blocked16 ? 16 : shape.channels, shape.element_bytes);
    const auto destination_row = multiply(destination.layout == Layout::blocked16 ? 16 : shape.channels, shape.element_bytes);
    return {narrow(shape.candidates), narrow(shape.keep), narrow(shape.channels), shape.element_bytes,
            source, destination, narrow(source_row), narrow(multiply(shape.candidates, source_row)),
            narrow(destination_row), narrow(multiply(shape.keep, destination_row))};
}

KernelDescriptor make_kernel_descriptor(Shape shape, std::uint32_t score_element_bytes,
                                        const KernelMemory& memory) {
    if (shape.candidates > 256 || (score_element_bytes != 2 && score_element_bytes != 4))
        throw std::invalid_argument("memory kernel requires N <= 256 and FP16/FP32 scores");
    auto gather = make_gather_descriptor(shape, memory.features, memory.selected_features);
    validate_dense(memory.scores, shape.candidates, score_element_bytes);
    validate_dense(memory.selected_scores, shape.keep, 4);
    validate_dense(memory.selected_indices, shape.keep, 8);
    const TensorMemory allocations[] = {memory.scores, memory.features, memory.selected_scores,
                                       memory.selected_indices, memory.selected_features};
    validate_output_aliases(allocations);
    return {gather, memory.scores, memory.selected_scores, memory.selected_indices, score_element_bytes};
}

RunGatherDescriptor make_run_gather_descriptor(Shape shape, const RunGatherMemory& memory) {
    auto gather = make_gather_descriptor(shape, memory.features, memory.selected_features);
    validate_dense(memory.records, shape.keep, 16);
    validate_dense(memory.selected_scores, shape.keep, 4);
    validate_dense(memory.selected_indices, shape.keep, 8);
    const TensorMemory allocations[] = {memory.records, memory.features, memory.selected_scores,
                                       memory.selected_indices, memory.selected_features};
    validate_output_aliases(allocations);
    return {gather, memory.records, memory.selected_scores, memory.selected_indices};
}

TileDescriptor make_tile_descriptor(TensorMemory scores, TensorMemory destination,
    std::uint32_t count, std::uint32_t keep, std::uint32_t score_element_bytes, std::uint64_t index_base) {
    if (!count || count > 256 || !keep || keep > count ||
        (score_element_bytes != 2 && score_element_bytes != 4) || index_base > UINT64_MAX-(count-1))
        throw std::invalid_argument("invalid score tile shape or index range");
    validate_dense(scores, count, score_element_bytes);
    validate_dense(destination, keep, 16);
    reject_overlap(scores, destination);
    return {scores, destination, count, keep, score_element_bytes, index_base};
}

MergeDescriptor make_merge_descriptor(TensorMemory left, TensorMemory right, TensorMemory destination,
    std::uint32_t left_count, std::uint32_t right_count, std::uint32_t keep, std::uint64_t index_limit) {
    if (!left_count || !right_count || !keep || !index_limit ||
        keep > std::uint64_t{left_count}+right_count)
        throw std::invalid_argument("invalid merge counts or index limit");
    validate_dense(left, left_count, 16);
    validate_dense(right, right_count, 16);
    validate_dense(destination, keep, 16);
    reject_overlap(left, right); reject_overlap(left, destination); reject_overlap(right, destination);
    return {left, right, destination, left_count, right_count, keep, index_limit};
}

void JobGuard::reserve(std::uint64_t id) {
    if (state_ != State::idle || id <= last_id_)
        throw std::logic_error("job must be idle and have a new monotonic identity");
    id_ = last_id_ = id;
    valid_output_ = false;
    state_ = State::waiting_for_producer;
}

bool JobGuard::producer_completed(std::uint64_t id, bool writes_visible) {
    if (id != id_ || state_ != State::waiting_for_producer || !writes_visible) return false;
    state_ = State::ready;
    return true;
}

void JobGuard::start() {
    if (state_ != State::ready) throw std::logic_error("producer data is not ready for device reads");
    state_ = State::running;
}

bool JobGuard::completed(std::uint64_t id, bool writes_visible, std::uint64_t outstanding,
                         bool valid_output) {
    if (id != id_ || state_ != State::running) return false;
    if (!writes_visible || outstanding) return false;
    valid_output_ = valid_output;
    state_ = State::complete;
    return true;
}

void JobGuard::fault() {
    if (state_ == State::idle || state_ == State::complete)
        throw std::logic_error("no active job to quarantine");
    valid_output_ = false;
    state_ = State::quarantined;
}

bool JobGuard::stopped_and_drained(std::uint64_t id, bool hardware_stopped,
                                  std::uint64_t outstanding) {
    if (id != id_ || state_ != State::quarantined || !hardware_stopped || outstanding) return false;
    valid_output_ = false;
    state_ = State::complete;
    return true;
}

void JobGuard::release() {
    if (!releasable()) throw std::logic_error("in-flight allocations must remain owned");
    state_ = State::idle;
    valid_output_ = false;
}

}  // namespace topk
