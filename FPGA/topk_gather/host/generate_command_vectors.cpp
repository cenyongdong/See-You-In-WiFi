// Exercise one ABI 2.0 peripheral across complete, differently shaped plans.
// Expected scratch bytes are never reloaded into the RTL memory model: every
// merge and final Gather must consume actual outputs of preceding commands.
#include "topk_registers.hpp"
#include "topk_scratch.hpp"

#include <algorithm>
#include <array>
#include <cmath>
#include <cstring>
#include <fstream>
#include <iostream>
#include <numeric>
#include <random>

namespace {
using Bytes = std::vector<std::uint8_t>;
constexpr std::uint32_t memory_bytes = 2*1024*1024;
constexpr std::uint32_t score_base = 0x1000, feature_base = 0x10000, output_base = 0x80000;
constexpr std::uint32_t selected_score_base = 0xc0000, selected_index_base = 0xc8000;
constexpr std::uint32_t first_arena = 0x100000, second_arena = 0x140000;

std::uint32_t aligned(std::uint64_t value) { return static_cast<std::uint32_t>((value+63)/64*64); }

void put(Bytes& bytes, std::size_t address, std::uint64_t value, unsigned size) {
    for (unsigned b = 0; b < size; ++b) bytes.at(address+b) = static_cast<std::uint8_t>(value >> (8*b));
}

std::size_t feature_offset(unsigned rows, unsigned row, unsigned channel, bool blocked) {
    return 2*(blocked ? (std::size_t{channel/16}*rows+row)*16+channel%16 : std::size_t{row}*42+channel);
}

void dump_region(std::ostream& stream, const Bytes& oracle, topk::TensorMemory region) {
    stream << std::hex << region.base << ' ' << std::dec << region.allocation_bytes << '\n';
    for (std::uint32_t i = 0; i < region.allocation_bytes; ++i)
        stream << std::hex << unsigned(oracle.at(region.base+i)) << '\n';
    stream << std::dec;
}

topk::TensorMemory run_memory(const topk::RunAllocation& run) {
    return {run.address, run.reserved_bytes, topk::Layout::dense};
}

void generate(const std::string& path, bool flush_half_zero) {
    const std::vector<std::pair<unsigned, unsigned>> shapes{{180,100}, {100,50}, {513,400}, {1025,513}, {1025,1025}};
    std::size_t commands = 1; // One failed first tile followed by the normal retry after completion.
    for (const auto [n,k] : shapes) commands += topk::make_plan({1,n,k,42,2}).jobs.size();
    std::ofstream stream(path);
    if (!stream) throw std::runtime_error("cannot create command vectors");
    stream << commands << '\n';
    std::uint64_t id = 0x3301000001;
    std::mt19937 random(3301313);
    unsigned shape_number = 0;
    for (const auto [n,k] : shapes) {
        const bool source_blocked = shape_number != 1, destination_blocked = shape_number != 2;
        const auto source_layout = source_blocked ? topk::Layout::blocked16 : topk::Layout::dense;
        const auto destination_layout = destination_blocked ? topk::Layout::blocked16 : topk::Layout::dense;
        const topk::Shape shape{1,n,k,42,2};
        // Keep one FP32 case to prove the FP16 policy does not affect -0 bits.
        const unsigned score_bytes = flush_half_zero && shape_number != 1 ? 2 : 4;
        const auto plan = topk::make_plan(shape);
        const auto arena_bytes = static_cast<std::uint32_t>(plan.scratch_bytes/2);
        const auto binding = topk::bind_scratch(plan, {first_arena, arena_bytes, topk::Layout::dense},
                                                    {second_arena, arena_bytes, topk::Layout::dense});
        const topk::TensorMemory scores{score_base, aligned(n*score_bytes), topk::Layout::dense};
        const topk::TensorMemory features{feature_base, aligned(n*(source_blocked ? 48 : 42)*2), source_layout};
        const topk::TensorMemory output{output_base, aligned(k*(destination_blocked ? 48 : 42)*2), destination_layout};
        const topk::TensorMemory selected_scores{selected_score_base, aligned(k*4), topk::Layout::dense};
        const topk::TensorMemory selected_indices{selected_index_base, aligned(k*8), topk::Layout::dense};
        Bytes oracle(memory_bytes, 0xa5);
        std::vector<float> values(n);
        std::vector<std::uint32_t> words(n), global(n);
        constexpr std::array<std::uint16_t, 12> half_edges{
            0, 0x8000, 1, 0x8001, 0x3ff, 0x83ff, 0x400, 0x8400, 0x3c00, 0xbc00, 0x7bff, 0xfbff};
        for (unsigned i = 0; i < n; ++i) {
            values[i] = float(int(random()%31)-15);
            if (i%7 == 0) values[i] = i%2 ? -0.0f : 0.0f;
            const auto half = half_edges[i % half_edges.size()];
            if (score_bytes == 2) {
                const int exponent = (half >> 10) & 31;
                const auto magnitude = exponent ? std::ldexp(float(1024 + (half & 1023)), exponent-25) : 0.0f;
                values[i] = exponent && (half & 0x8000) ? -magnitude : magnitude;
            }
            std::memcpy(&words[i], &values[i], 4);
            put(oracle, score_base+score_bytes*i, score_bytes == 2 ? half : words[i], score_bytes);
            for (unsigned c = 0; c < (source_blocked ? 48u : 42u); ++c)
                put(oracle, feature_base+feature_offset(n,i,c,source_blocked), random(), 2);
        }
        auto precedes = [&](auto a, auto b) { return values[a] == values[b] ? a < b : values[a] > values[b]; };
        std::iota(global.begin(), global.end(), 0);
        std::sort(global.begin(), global.end(), precedes);
        global.resize(k);
        std::vector<std::vector<std::uint32_t>> reference_runs(binding.runs.size());
        bool initialize = true;
        for (const auto& job : plan.jobs) {
            topk::CommandImage image{};
            std::vector<topk::TensorMemory> outputs;
            if (job.kind != topk::JobKind::gather) {
                const auto destination = run_memory(binding.runs.at(job.output));
                auto& winners = reference_runs.at(job.output);
                if (job.kind == topk::JobKind::sort_tile) {
                    winners.resize(job.input_count);
                    std::iota(winners.begin(), winners.end(), static_cast<std::uint32_t>(job.input_offset));
                    const auto tile_scores = topk::TensorMemory{score_base+static_cast<std::uint32_t>(job.input_offset*score_bytes),
                        aligned(job.input_count*score_bytes), topk::Layout::dense};
                    image = topk::make_tile_command(id, topk::make_tile_descriptor(tile_scores, destination,
                        static_cast<std::uint32_t>(job.input_count), static_cast<std::uint32_t>(job.keep), score_bytes, job.input_offset));
                } else {
                    winners = reference_runs.at(job.left);
                    const auto& right = reference_runs.at(job.right);
                    winners.insert(winners.end(), right.begin(), right.end());
                    image = topk::make_merge_command(id, topk::make_merge_descriptor(
                        run_memory(binding.runs.at(job.left)), run_memory(binding.runs.at(job.right)), destination,
                        static_cast<std::uint32_t>(reference_runs.at(job.left).size()), static_cast<std::uint32_t>(right.size()),
                        static_cast<std::uint32_t>(job.keep), n));
                }
                // Independent full sort, not the DUT insertion/merge algorithm.
                std::sort(winners.begin(), winners.end(), precedes); winners.resize(job.keep);
                for (std::size_t rank = 0; rank < winners.size(); ++rank) {
                    put(oracle, destination.base+rank*16, words[winners[rank]], 4);
                    put(oracle, destination.base+rank*16+4, 0, 4);
                    put(oracle, destination.base+rank*16+8, winners[rank], 8);
                }
                outputs.push_back(destination);
            } else {
                if (reference_runs.at(job.left) != global) throw std::runtime_error("plan differs from global oracle");
                image = topk::make_run_gather_command(id, topk::make_run_gather_descriptor(shape,
                    {run_memory(binding.runs.at(job.left)), features, selected_scores, selected_indices, output}));
                for (unsigned rank = 0; rank < k; ++rank) {
                    put(oracle, selected_score_base+4*rank, words[global[rank]], 4);
                    put(oracle, selected_index_base+8*rank, global[rank], 8);
                    for (unsigned c = 0; c < (destination_blocked ? 48u : 42u); ++c) {
                        std::uint16_t word = 0;
                        if (c < 42) {
                            const auto address = feature_base+feature_offset(n,global[rank],c,source_blocked);
                            word = std::uint16_t(oracle.at(address)) | (std::uint16_t(oracle.at(address+1)) << 8);
                        }
                        if (flush_half_zero && (word & 0x7c00) == 0) word = 0;
                        put(oracle, output_base+feature_offset(k,rank,c,destination_blocked), word, 2);
                    }
                }
                outputs = {output, selected_scores, selected_indices};
            }
            const bool inject_failure = shape_number == 0 && initialize;
            for (unsigned attempt = 0; attempt < (inject_failure ? 2u : 1u); ++attempt) {
                const bool failed_read = inject_failure && attempt == 0;
                image[0] = static_cast<std::uint32_t>(id); image[1] = static_cast<std::uint32_t>(id++ >> 32);
                stream << (failed_read ? 1 : 0) << ' ' << (failed_read ? 5 : 0) << ' ' << initialize << ' '
                       << (initialize ? 2 : 0) << ' ' << outputs.size() << '\n';
                for (auto word : image) stream << std::hex << word << '\n';
                stream << std::dec;
                if (initialize) { dump_region(stream, oracle, scores); dump_region(stream, oracle, features); }
                for (const auto& region : outputs) dump_region(stream, oracle, region);
                initialize = false;
            }
        }
        ++shape_number;
    }
    std::cout << "TOPK_COMMAND_VECTORS_PASS shapes=" << shapes.size() << " commands=" << commands << '\n';
}
}  // namespace

int main(int argc, char** argv) {
    try {
        if (argc != 2 && (argc != 3 || std::string(argv[2]) != "--flush-half-zero"))
            throw std::invalid_argument("supply output path [--flush-half-zero]");
        generate(argv[1], argc == 3);
    } catch (const std::exception& error) {
        std::cerr << error.what() << '\n'; return 1;
    }
}
