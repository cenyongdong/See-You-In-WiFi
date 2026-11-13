#include "topk_scratch.hpp"

#include <algorithm>
#include <cstring>
#include <iostream>
#include <random>
#include <stdexcept>
#include <vector>

namespace {

using topk::ScratchRecord;

void require(bool condition, const char* message) {
    if (!condition) throw std::runtime_error(message);
}

template <typename Function> void rejects(Function function) {
    bool rejected = false;
    try { function(); } catch (const std::exception&) { rejected = true; }
    require(rejected, "invalid scratch allocation was accepted");
}

float score(const ScratchRecord& record) {
    float value;
    std::memcpy(&value, &record.score_bits, sizeof(value));
    return value;
}

bool before(const ScratchRecord& a, const ScratchRecord& b) {
    return score(a) == score(b) ? a.index < b.index : score(a) > score(b);
}

// Execute the DAG against ONLY the two physical arenas. A separate full sort
// checks the result; live-interval checks catch overwrite before consumption.
void exercise(std::uint64_t batches, std::uint64_t n, std::uint64_t k,
              std::uint32_t capacity, std::mt19937& random) {
    const auto plan = topk::make_plan({batches, n, k, 42, 2}, {capacity, 64 * 1024 * 1024, 1000000});
    const auto bytes = static_cast<std::uint32_t>(plan.scratch_bytes / 2);
    const topk::TensorMemory allocations[] = {{0x100000, bytes, topk::Layout::dense},
                                             {0x10000000, bytes, topk::Layout::dense}};
    const auto bindings = topk::bind_scratch(plan, allocations[0], allocations[1]);
    if (plan.jobs.empty()) {
        require(bindings.runs.empty() && plan.scratch_bytes == 0, "empty plan allocated scratch");
        return;
    }
    std::vector<ScratchRecord> memory[] = {std::vector<ScratchRecord>(bytes / 16),
                                          std::vector<ScratchRecord>(bytes / 16)};
    std::vector<std::vector<ScratchRecord>> input(batches, std::vector<ScratchRecord>(n));
    for (auto& batch : input) {
        for (std::size_t i = 0; i < batch.size(); ++i) {
            const float value = static_cast<int>(random() % 31) - 15.0f;
            std::uint32_t word;
            std::memcpy(&word, &value, sizeof(word));
            if (i % 17 == 0) word = i % 2 ? 0x80000000u : 0;
            batch[i] = {word, 0, i};
        }
    }
    std::vector<bool> live(bindings.runs.size(), false);
    const auto read = [&](std::uint64_t id) {
        require(live.at(id), "read of an unproduced or consumed run");
        const auto& allocation = bindings.runs.at(id);
        const auto offset = (allocation.address - allocations[allocation.arena_index].base) / 16;
        const auto first = memory[allocation.arena_index].begin() + offset;
        return std::vector<ScratchRecord>(first, first + allocation.record_count);
    };
    const auto write = [&](std::uint64_t id, const std::vector<ScratchRecord>& records) {
        const auto& allocation = bindings.runs.at(id);
        require(!live[id] && records.size() == allocation.record_count, "run output extent differs");
        for (std::size_t other_id = 0; other_id < live.size(); ++other_id) {
            if (!live[other_id]) continue;
            const auto& other = bindings.runs[other_id];
            require(!(std::uint64_t{allocation.address} < std::uint64_t{other.address} + other.reserved_bytes &&
                      std::uint64_t{other.address} < std::uint64_t{allocation.address} + allocation.reserved_bytes),
                    "output overwrites a still-live scratch interval");
        }
        const auto offset = (allocation.address - allocations[allocation.arena_index].base) / 16;
        std::copy(records.begin(), records.end(), memory[allocation.arena_index].begin() + offset);
        live[id] = true;
    };
    for (const auto& job : plan.jobs) {
        if (job.kind == topk::JobKind::sort_tile) {
            const auto first = input[job.batch].begin() + job.input_offset;
            std::vector<ScratchRecord> records(first, first + job.input_count);
            std::sort(records.begin(), records.end(), before);
            records.resize(job.keep);
            write(job.output, records);
        } else if (job.kind == topk::JobKind::merge_runs) {
            const auto left = read(job.left), right = read(job.right);
            require(bindings.runs[job.left].arena_index == bindings.runs[job.right].arena_index &&
                    bindings.runs[job.left].arena_index != bindings.runs[job.output].arena_index,
                    "merge source and destination arenas are not separated");
            std::vector<ScratchRecord> records;
            std::merge(left.begin(), left.end(), right.begin(), right.end(), std::back_inserter(records), before);
            records.resize(job.keep);
            write(job.output, records); // Inputs are deliberately still live here.
            live[job.left] = live[job.right] = false;
        } else {
            const auto actual = read(job.left);
            auto expected = input[job.batch];
            std::sort(expected.begin(), expected.end(), before);
            expected.resize(job.keep);
            require(actual.size() == expected.size() &&
                    std::memcmp(actual.data(), expected.data(), actual.size() * sizeof(ScratchRecord)) == 0,
                    "physical scratch execution lost score bits or winner indices");
            live[job.left] = false;
        }
    }
    require(std::none_of(live.begin(), live.end(), [](bool value) { return value; }), "scratch run remains live");
}

}  // namespace

int main() {
    try {
        std::mt19937 random(330256);
        std::size_t cases = 0;
        for (const auto [n, k] : std::vector<std::pair<std::uint64_t, std::uint64_t>>{
                 {1, 1}, {180, 100}, {100, 50}, {513, 400}, {1025, 513},
                 {1025, 1025}, {1537, 1000}, {4097, 4000}, {0, 0}, {33, 0}}) {
            for (auto capacity : {127u, 256u}) { exercise(3, n, k, capacity, random); ++cases; }
        }
        for (auto capacity : {1u, 3u, 7u}) { exercise(2, 33, 17, capacity, random); ++cases; }
        for (int i = 0; i < 100; ++i) {
            const std::uint64_t n = random() % 4096 + 1;
            exercise(2, n, random() % n + 1, 256, random); ++cases;
        }
        const auto plan = topk::make_plan({1, 1025, 513, 42, 2});
        const auto bytes = static_cast<std::uint32_t>(plan.scratch_bytes / 2);
        const topk::TensorMemory a{0x100000, bytes, topk::Layout::dense}, b{0x200000, bytes, topk::Layout::dense};
        require(topk::make_plan({1, 1, 1, 1, 2}).scratch_bytes == 128, "single-record cache-line budget");
        require(topk::make_plan({1, 33, 17, 1, 2}, {3, 65536, 1000}).scratch_bytes == 1408,
                "non-multiple-of-four leaf padding budget");
        rejects([&] { topk::bind_scratch(plan, a, a); });
        rejects([&] { topk::bind_scratch(plan, a, {0xfffff000, bytes, topk::Layout::dense}); });
        rejects([&] { topk::bind_scratch(plan, a, {b.base, bytes - 64, topk::Layout::dense}); });
        auto invalid = plan;
        invalid.jobs[0].input_offset = 1;
        rejects([&] { topk::bind_scratch(invalid, a, b); });
        invalid = plan; invalid.jobs.back().left = 0;
        rejects([&] { topk::bind_scratch(invalid, a, b); });
        std::cout << "TOPK_SCRATCH_PASS physical_schedule_cases=" << cases << " boundary_checks=pass\n";
    } catch (const std::exception& error) {
        std::cerr << error.what() << '\n';
        return 1;
    }
}
