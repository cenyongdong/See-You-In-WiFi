#include "topk_plan.hpp"
#include "topk_scratch.hpp"
#include "topk_registers.hpp"

#include <algorithm>
#include <cstring>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <map>
#include <numeric>
#include <random>
#include <stdexcept>
#include <string>
#include <vector>

namespace {

void require(bool condition, const char* message) {
    if (!condition) throw std::runtime_error(message);
}

template <typename Function>
void rejects(Function function) {
    bool threw = false;
    try { function(); } catch (const std::exception&) { threw = true; }
    require(threw, "invalid operation was accepted");
}

// This checks the scheduling algorithm with a software backend. RTL tile and
// merge implementations are tested separately; this is not a hardware test.
void test_plan(std::uint64_t batches, std::uint64_t n, std::uint64_t k, std::mt19937& random) {
    const auto plan = topk::make_plan({batches, n, k, 42, 2});
    std::vector<std::vector<float>> scores(batches, std::vector<float>(n));
    for (auto& batch : scores)
        for (auto& score : batch) score = static_cast<int>(random() % 19) - 9.0f;
    std::map<std::uint64_t, std::vector<std::uint64_t>> runs;
    std::size_t gathered = 0;
    for (const auto& job : plan.jobs) {
        auto before = [&](std::uint64_t left, std::uint64_t right) {
            const auto a = scores[job.batch][left], b = scores[job.batch][right];
            return a == b ? left < right : a > b;
        };
        if (job.kind == topk::JobKind::sort_tile) {
            auto& run = runs[job.output];
            run.resize(job.input_count);
            std::iota(run.begin(), run.end(), job.input_offset);
            std::sort(run.begin(), run.end(), before);
            run.resize(job.keep);
        } else if (job.kind == topk::JobKind::merge_runs) {
            const auto& left = runs.at(job.left);
            const auto& right = runs.at(job.right);
            auto& output = runs[job.output];
            std::merge(left.begin(), left.end(), right.begin(), right.end(),
                       std::back_inserter(output), before);
            output.resize(job.keep);
            runs.erase(job.left);
            runs.erase(job.right);
        } else {
            std::vector<std::uint64_t> reference(n);
            std::iota(reference.begin(), reference.end(), 0);
            std::sort(reference.begin(), reference.end(), before);
            reference.resize(k);
            require(runs.at(job.left) == reference, "tile/merge schedule lost a global winner");
            require(plan.result_runs.at(job.batch) == job.left, "wrong final run");
            runs.erase(job.left);
            ++gathered;
        }
    }
    require(gathered == (k ? batches : 0), "wrong gather count");
    require(runs.empty(), "schedule left an unconsumed run");
}

void test_descriptors() {
    const auto d = topk::make_gather_descriptor({1, 180, 100, 42, 2},
        {0x10000, 17280, topk::Layout::blocked16}, {0x20000, 9600, topk::Layout::blocked16});
    require(d.source_row_stride == 32 && d.source_block_stride == 5760, "source C16 strides");
    require(d.destination_row_stride == 32 && d.destination_block_stride == 3200, "destination C16 strides");
    const auto dense = topk::make_gather_descriptor({1, 100, 50, 42, 4},
        {0x10000, 16832, topk::Layout::dense}, {0x20000, 8448, topk::Layout::dense});
    require(dense.source_row_stride == 168 && dense.destination_row_stride == 168, "dense row stride");
    rejects([] { topk::make_gather_descriptor({1, 180, 100, 42, 2},
        {0x10000, 15168, topk::Layout::blocked16}, {0x20000, 9600, topk::Layout::blocked16}); });
    rejects([] { topk::make_gather_descriptor({1, 180, 100, 42, 2},
        {0x10000, 17280, topk::Layout::blocked16}, {0x11000, 9600, topk::Layout::blocked16}); });
    rejects([] { topk::make_gather_descriptor({1, 180, 100, 42, 2},
        {0xfffff000, 17280, topk::Layout::blocked16}, {0x20000, 9600, topk::Layout::blocked16}); });
    rejects([] { topk::make_gather_descriptor({1, 180, 100, 42, 2},
        {0x10001, 17280, topk::Layout::blocked16}, {0x20000, 9600, topk::Layout::blocked16}); });
}

void test_lifetime() {
    topk::JobGuard guard;
    guard.reserve(1);
    rejects([&] { guard.start(); });
    rejects([&] { guard.release(); });
    require(!guard.producer_completed(0, true), "stale producer completion accepted");
    require(!guard.producer_completed(1, false), "unfenced producer accepted");
    require(guard.producer_completed(1, true), "producer completion rejected");
    guard.start();
    require(!guard.completed(0, true, 0, true), "stale consumer completion accepted");
    require(!guard.completed(1, true, 1, true), "in-flight transaction ignored");
    require(!guard.completed(1, false, 0, true), "write acceptance treated as completion");
    require(guard.completed(1, true, 0, true), "valid completion rejected");
    require(guard.publishable() && guard.releasable(), "completed result unavailable");
    guard.release();
    rejects([&] { guard.reserve(1); });
    guard.reserve(2);
    guard.producer_completed(2, true);
    guard.start();
    guard.fault();
    require(!guard.publishable() && !guard.releasable(), "fault released live memory");
    require(!guard.completed(2, true, 0, true), "quarantined output published");
    rejects([&] { guard.release(); });
    require(!guard.stopped_and_drained(2, false, 0), "no hardware STOP proof");
    require(!guard.stopped_and_drained(2, true, 1), "outstanding requests ignored");
    require(!guard.stopped_and_drained(1, true, 0), "old STOP proof accepted");
    require(guard.stopped_and_drained(2, true, 0), "drained fault cannot be reclaimed");
    require(!guard.publishable() && guard.releasable(), "invalid output published after recovery");
    guard.release();
}

void test_kernel_descriptors() {
    const topk::KernelMemory memory{
        {0x100000, 1024, topk::Layout::dense}, {0x200000, 65536, topk::Layout::blocked16},
        {0x300000, 1024, topk::Layout::dense}, {0x400000, 2048, topk::Layout::dense},
        {0x500000, 65536, topk::Layout::blocked16}};
    for (const auto [n, k] : std::vector<std::pair<std::uint64_t, std::uint64_t>>{
             {180, 100}, {100, 50}, {100, 100}, {1, 1}, {256, 256}}) {
        for (auto bytes : {2u, 4u}) {
            const auto d = topk::make_kernel_descriptor({1, n, k, 42, 2}, bytes, memory);
            require(d.gather.candidates == n && d.gather.keep == k &&
                    d.score_element_bytes == bytes && d.selected_indices.base == 0x400000,
                    "memory kernel descriptor changed shape or allocation");
        }
    }
    rejects([&] { topk::make_kernel_descriptor({1, 257, 100, 42, 2}, 2, memory); });
    rejects([&] { topk::make_kernel_descriptor({2, 180, 100, 42, 2}, 2, memory); });
    rejects([&] { topk::make_kernel_descriptor({1, 180, 0, 42, 2}, 2, memory); });
    rejects([&] { topk::make_kernel_descriptor({1, 180, 100, 42, 2}, 1, memory); });
    auto invalid = memory;
    invalid.selected_scores.allocation_bytes = 64;
    rejects([&] { topk::make_kernel_descriptor({1, 180, 100, 42, 2}, 2, invalid); });
    invalid = memory; invalid.selected_indices.base = memory.features.base;
    rejects([&] { topk::make_kernel_descriptor({1, 180, 100, 42, 2}, 2, invalid); });
    invalid = memory; invalid.scores.base = memory.selected_features.base;
    rejects([&] { topk::make_kernel_descriptor({1, 180, 100, 42, 2}, 2, invalid); });
    invalid = memory; invalid.scores.base = 0xffffffc0;
    rejects([&] { topk::make_kernel_descriptor({1, 180, 100, 42, 2}, 2, invalid); });
    invalid = memory; invalid.scores.layout = topk::Layout::blocked16;
    rejects([&] { topk::make_kernel_descriptor({1, 180, 100, 42, 2}, 2, invalid); });
    auto shared_inputs = memory;
    shared_inputs.scores.base = shared_inputs.features.base;
    topk::make_kernel_descriptor({1, 180, 100, 42, 2}, 2, shared_inputs);
}

void test_run_gather_descriptors() {
    const topk::RunGatherMemory memory{
        {0x100000, 65536, topk::Layout::dense}, {0x200000, 1048576, topk::Layout::blocked16},
        {0x400000, 16384, topk::Layout::dense}, {0x500000, 32768, topk::Layout::dense},
        {0x600000, 1048576, topk::Layout::blocked16}};
    for (const auto [n, k] : std::vector<std::pair<std::uint64_t, std::uint64_t>>{
             {180, 100}, {100, 50}, {513, 400}, {1025, 513}, {1025, 1025}, {4096, 4096}}) {
        for (auto bytes : {2u, 4u}) {
            const auto d = topk::make_run_gather_descriptor({1, n, k, 42, bytes}, memory);
            require(d.gather.candidates == n && d.gather.keep == k && d.records.base == 0x100000 &&
                    d.gather.source_block_stride == n*16*bytes,
                    "completed-run descriptor lost shape or layout");
        }
    }
    const topk::Shape shape{1, 1025, 513, 42, 2};
    rejects([&] { topk::make_run_gather_descriptor({2, 1025, 513, 42, 2}, memory); });
    rejects([&] { topk::make_run_gather_descriptor({1, 1025, 1026, 42, 2}, memory); });
    rejects([&] { topk::make_run_gather_descriptor({1, 1025, 0, 42, 2}, memory); });
    auto invalid = memory;
    invalid.records.allocation_bytes = 8192; // 513 records require 8256 bytes.
    rejects([&] { topk::make_run_gather_descriptor(shape, invalid); });
    invalid = memory; invalid.records.layout = topk::Layout::blocked16;
    rejects([&] { topk::make_run_gather_descriptor(shape, invalid); });
    invalid = memory; invalid.records.base = 0xffffffc0;
    rejects([&] { topk::make_run_gather_descriptor(shape, invalid); });
    invalid = memory; invalid.selected_indices.base = memory.records.base;
    rejects([&] { topk::make_run_gather_descriptor(shape, invalid); });
    invalid = memory; invalid.selected_scores.base = memory.selected_features.base;
    rejects([&] { topk::make_run_gather_descriptor(shape, invalid); });
    invalid = memory; invalid.selected_features.base = memory.records.base;
    rejects([&] { topk::make_run_gather_descriptor(shape, invalid); });
}

void test_stage_descriptors() {
    const topk::TensorMemory scores{0x1000, 1024, topk::Layout::dense};
    const topk::TensorMemory left{0x10000, 4096, topk::Layout::dense};
    const topk::TensorMemory right{0x20000, 4096, topk::Layout::dense};
    const topk::TensorMemory output{0x30000, 8192, topk::Layout::dense};
    const auto tile = topk::make_tile_descriptor(scores, left, 180, 100, 4, 0x100000000ull);
    const auto tile_image = topk::make_tile_command(0x3301000001ull, tile);
    require(tile_image[22] == 0 && tile_image[27] == 1 && tile_image[1] == 0x33 && tile_image[3] == 100,
            "tile command lost high bits or dimensions");
    const auto merge = topk::make_merge_descriptor(left, right, output, 256, 256, 400, 0x100000200ull);
    const auto merge_image = topk::make_merge_command(1, merge);
    require(merge_image[22] == 1 && merge_image[25] == 256 && merge_image[28] == 512 && merge_image[29] == 1,
            "merge command changed count or index limit");
    rejects([&] { topk::make_tile_command(0, tile); });
    rejects([&] { topk::make_merge_command(0, merge); });
    rejects([&] { topk::make_tile_descriptor(scores, left, 257, 100, 4, 0); });
    rejects([&] { topk::make_tile_descriptor(scores, left, 180, 181, 4, 0); });
    rejects([&] { topk::make_tile_descriptor(scores, left, 180, 100, 0x104, 0); });
    rejects([&] { topk::make_tile_descriptor(scores, left, 180, 100, 4, UINT64_MAX-100); });
    rejects([&] { topk::make_tile_descriptor(scores, scores, 180, 100, 4, 0); });
    auto short_output = left; short_output.allocation_bytes = 64;
    rejects([&] { topk::make_tile_descriptor(scores, short_output, 180, 100, 4, 0); });
    auto unaligned = scores; unaligned.base += 4;
    rejects([&] { topk::make_tile_descriptor(unaligned, left, 180, 100, 4, 0); });
    rejects([&] { topk::make_merge_descriptor(left, right, output, 0, 256, 100, 512); });
    rejects([&] { topk::make_merge_descriptor(left, right, output, 256, 256, 513, 512); });
    rejects([&] { topk::make_merge_descriptor(left, right, output, 256, 256, 400, 0); });
    rejects([&] { topk::make_merge_descriptor(left, left, output, 256, 256, 400, 512); });
    rejects([&] { topk::make_merge_descriptor(left, right, right, 256, 256, 400, 512); });
    rejects([&] { topk::make_merge_descriptor(left, right, output, 257, 256, 400, 513); });
}

void dump_rtl_jobs(const std::string& path) {
    std::ofstream stream(path);
    std::ofstream scratch(path + ".scratch");
    if (!stream || !scratch) throw std::runtime_error("cannot create RTL job vectors");
    const std::vector<std::pair<std::uint64_t, std::uint64_t>> shapes{
        {180, 100}, {100, 50}, {100, 100}, {513, 400}, {1025, 513}, {1025, 1025}};
    std::mt19937 random(33013);
    stream << shapes.size() << '\n';
    scratch << shapes.size() << '\n';
    for (const auto [n, k] : shapes) {
        const auto plan = topk::make_plan({2, n, k, 42, 2});
        const auto arena_bytes = static_cast<std::uint32_t>(plan.scratch_bytes / 2);
        const auto bindings = topk::bind_scratch(plan, {0x10000, arena_bytes, topk::Layout::dense},
                                                {0x40000, arena_bytes, topk::Layout::dense});
        scratch << bindings.arena_bytes << ' ' << bindings.runs.size() << '\n';
        for (const auto& allocation : bindings.runs)
            scratch << std::hex << allocation.address << std::dec << ' ' << allocation.reserved_bytes << ' '
                    << allocation.record_count << ' ' << allocation.batch << ' ' << allocation.arena_index << '\n';
        stream << "2 " << n << ' ' << k << ' ' << plan.jobs.size() << '\n';
        std::vector<std::vector<float>> scores(2, std::vector<float>(n));
        for (auto& batch : scores) {
            for (auto& score : batch) {
                score = static_cast<int>(random() % 31) - 15.0f;
                std::uint32_t word;
                std::memcpy(&word, &score, sizeof(word));
                stream << std::hex << word << std::dec << '\n';
            }
        }
        for (const auto& job : plan.jobs) {
            auto id = [](std::uint64_t run) { return run == topk::no_run ? -1 : static_cast<int>(run); };
            stream << static_cast<int>(job.kind) << ' ' << job.batch << ' ' << job.input_offset << ' '
                   << job.input_count << ' ' << job.keep << ' ' << id(job.left) << ' '
                   << id(job.right) << ' ' << id(job.output) << '\n';
        }
        for (const auto& batch : scores) {
            std::vector<std::uint64_t> reference(n);
            std::iota(reference.begin(), reference.end(), 0);
            std::sort(reference.begin(), reference.end(), [&](auto a, auto b) {
                return batch[a] == batch[b] ? a < b : batch[a] > batch[b];
            });
            for (std::size_t rank = 0; rank < k; ++rank) {
                std::uint32_t word;
                std::memcpy(&word, &batch[reference[rank]], sizeof(word));
                stream << std::hex << word << ' ' << reference[rank] << std::dec << '\n';
            }
        }
    }
}

void test_device_contract() {
    for (const bool generic : {false, true}) {
        const auto abi = generic ? topk::command_register_abi : topk::register_abi;
        topk::validate_register_contract(topk::register_magic, abi, 0, generic, topk::HalfPolicy::preserve);
        topk::validate_register_contract(topk::register_magic, abi|1, 1, generic, topk::HalfPolicy::flush_to_positive_zero);
        rejects([&] { topk::validate_register_contract(topk::register_magic, abi|1, 1, generic, topk::HalfPolicy::preserve); });
        rejects([&] { topk::validate_register_contract(topk::register_magic, abi, 0, generic, topk::HalfPolicy::flush_to_positive_zero); });
        rejects([&] { topk::validate_register_contract(topk::register_magic, abi|1, 0, generic, topk::HalfPolicy::flush_to_positive_zero); });
        rejects([&] { topk::validate_register_contract(0, abi, 0, generic, topk::HalfPolicy::preserve); });
        rejects([&] { topk::validate_register_contract(topk::register_magic, abi, 0, !generic, topk::HalfPolicy::preserve); });
    }
}
}  // namespace

int main(int argc, char** argv) {
    try {
        std::mt19937 random(330);
        for (const auto [n, k] : std::vector<std::pair<std::uint64_t, std::uint64_t>>{
                 {180, 100}, {100, 50}, {100, 100}, {1, 1}, {0, 0}, {180, 0},
                 {257, 257}, {513, 400}, {1025, 513}, {4097, 4000}, {8193, 13}})
            test_plan(3, n, k, random);
        for (int i = 0; i < 300; ++i) {
            const std::uint64_t n = random() % 4096 + 1;
            test_plan(random() % 4 + 1, n, random() % (n + 1), random);
        }
        test_descriptors();
        test_kernel_descriptors();
        test_run_gather_descriptors();
        test_stage_descriptors();
        test_lifetime();
        test_device_contract();
        rejects([] { topk::make_plan({1, 180, 181, 42, 2}); });
        rejects([] { topk::make_plan({1, 180, 100, 42, 3}); });
        rejects([] { topk::make_plan({UINT64_MAX, UINT64_MAX, 1, 42, 2}); });
        rejects([] { topk::make_plan({1, 1025, 513, 42, 2}, {256, 1024, 100}); });
        rejects([] { topk::make_plan({4, 1025, 513, 42, 2}, {256, 65536, 4}); });
        if (argc == 2) dump_rtl_jobs(argv[1]);
        std::cout << "TOPK_HOST_PASS scheduling_cases=311 descriptor_and_lifetime_checks=pass\n";
    } catch (const std::exception& error) {
        std::cerr << error.what() << '\n';
        return 1;
    }
}
