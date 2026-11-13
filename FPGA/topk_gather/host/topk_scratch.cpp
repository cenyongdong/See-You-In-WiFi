#include "topk_scratch.hpp"

#include <stdexcept>

namespace topk {
namespace {

struct Node {
    std::uint64_t parent = no_run;
    std::uint64_t offset, bytes, records, first_candidate, candidate_count, batch;
    std::uint32_t arena = 0;
    bool root = false;
};

bool overlaps(TensorMemory a, TensorMemory b) {
    return std::uint64_t{a.base} < std::uint64_t{b.base} + b.allocation_bytes &&
           std::uint64_t{b.base} < std::uint64_t{a.base} + a.allocation_bytes;
}

void validate_arena(TensorMemory memory, std::uint64_t required) {
    if (memory.layout != Layout::dense || memory.base % 64 || memory.allocation_bytes % 64 ||
        memory.allocation_bytes < required ||
        std::uint64_t{memory.base} + memory.allocation_bytes > (std::uint64_t{1} << 32))
        throw std::invalid_argument("scratch arena is unaligned, undersized, or outside DDR window");
}

}  // namespace

ScratchBindings bind_scratch(const Plan& plan, TensorMemory first, TensorMemory second) {
    ScratchBindings bindings{plan.scratch_bytes / 2, {}};
    if (plan.jobs.empty()) {
        if (plan.scratch_bytes || !plan.result_runs.empty() || (plan.shape.batches && plan.shape.keep))
            throw std::invalid_argument("nonempty shape has an empty scratch plan");
        return bindings;
    }
    if (!bindings.arena_bytes || plan.scratch_bytes % 2 ||
        plan.result_runs.size() != plan.shape.batches)
        throw std::invalid_argument("invalid scratch budget or batch roots");
    validate_arena(first, bindings.arena_bytes);
    validate_arena(second, bindings.arena_bytes);
    if (overlaps(first, second)) throw std::invalid_argument("scratch arenas overlap");

    std::vector<Node> nodes;
    std::uint64_t batch = 0, cursor = 0, candidate_cursor = 0;
    for (const auto& job : plan.jobs) {
        if (job.batch != batch || batch >= plan.shape.batches)
            throw std::invalid_argument("scratch jobs must finish each batch before reuse");
        if (job.kind == JobKind::sort_tile) {
            if (job.output != nodes.size() || !job.input_count || job.input_count > 256 ||
                !job.keep || job.keep > job.input_count || job.input_offset != candidate_cursor ||
                job.input_count > plan.shape.candidates - candidate_cursor)
                throw std::invalid_argument("invalid or noncontiguous scratch leaf");
            const auto bytes = (job.input_count * sizeof(ScratchRecord) + 63) / 64 * 64;
            if (bytes > bindings.arena_bytes - cursor)
                throw std::invalid_argument("leaf padding exceeds scratch budget");
            nodes.push_back({no_run, cursor, bytes, job.keep, job.input_offset,
                             job.input_count, batch, 0, false});
            cursor += bytes;
            candidate_cursor += job.input_count;
        } else if (job.kind == JobKind::merge_runs) {
            if (job.output != nodes.size() || job.left >= nodes.size() || job.right >= nodes.size() ||
                job.left == job.right)
                throw std::invalid_argument("merge references a missing or repeated run");
            auto& left = nodes[job.left];
            auto& right = nodes[job.right];
            if (left.parent != no_run || right.parent != no_run || left.batch != batch || right.batch != batch ||
                left.root || right.root || left.offset + left.bytes != right.offset ||
                left.first_candidate + left.candidate_count != right.first_candidate ||
                !job.keep || job.input_count != left.records + right.records || job.keep > job.input_count)
                throw std::invalid_argument("merge inputs are not adjacent live runs");
            const Node output{no_run, left.offset, left.bytes + right.bytes, job.keep,
                              left.first_candidate, left.candidate_count + right.candidate_count, batch, 0, false};
            left.parent = right.parent = job.output;
            nodes.push_back(output);
        } else if (job.kind == JobKind::gather) {
            if (job.left >= nodes.size() || candidate_cursor != plan.shape.candidates ||
                cursor != bindings.arena_bytes || job.left != plan.result_runs[batch])
                throw std::invalid_argument("invalid final scratch run");
            auto& root = nodes[job.left];
            if (root.batch != batch || root.parent != no_run || root.root || root.first_candidate != 0 ||
                root.candidate_count != plan.shape.candidates || root.records != plan.shape.keep)
                throw std::invalid_argument("final run does not cover the batch");
            root.root = true;
            ++batch; cursor = 0; candidate_cursor = 0;
        } else throw std::invalid_argument("unknown scratch job kind");
    }
    if (batch != plan.shape.batches) throw std::invalid_argument("unfinished scratch batch");

    bindings.runs.resize(nodes.size());
    const TensorMemory arenas[] = {first, second};
    for (std::size_t id = nodes.size(); id-- > 0;) {
        auto& node = nodes[id];
        if (!node.root) {
            if (node.parent <= id || node.parent >= nodes.size())
                throw std::invalid_argument("unconsumed or cyclic scratch run");
            node.arena = nodes[node.parent].arena ^ 1u;
        }
        const auto address = std::uint64_t{arenas[node.arena].base} + node.offset;
        if (node.offset + node.bytes > bindings.arena_bytes || node.records * sizeof(ScratchRecord) > node.bytes)
            throw std::invalid_argument("scratch run exceeds its reserved interval");
        bindings.runs[id] = {static_cast<std::uint32_t>(address), static_cast<std::uint32_t>(node.bytes),
                             node.records, node.batch, node.arena};
    }
    return bindings;
}

}  // namespace topk
