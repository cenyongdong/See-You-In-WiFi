// Produce validated C++ register images and an independent full-sort oracle
// for the complete AXI4-Lite/AXI4 RTL peripheral. No SDK/device access occurs.
#include "topk_registers.hpp"

#include <algorithm>
#include <cstring>
#include <fstream>
#include <iostream>
#include <numeric>
#include <random>
#include <vector>

namespace {
using Bytes = std::vector<std::uint8_t>;
constexpr std::uint32_t score_base = 0x1000, source_base = 0x4000, destination_base = 0x20000;
constexpr std::uint32_t selected_score_base = 0x40000, selected_index_base = 0x41000;

std::uint32_t aligned(std::uint64_t bytes) {
    return static_cast<std::uint32_t>((bytes + 63) / 64 * 64);
}

void put(Bytes& data, std::size_t offset, std::uint64_t word, unsigned size) {
    for (unsigned i = 0; i < size; ++i) data.at(offset + i) = static_cast<std::uint8_t>(word >> (8*i));
}

std::size_t offset(std::uint32_t rows, std::uint32_t row, std::uint32_t channel,
                   std::uint32_t channels, unsigned size, bool blocked) {
    return (blocked ? (std::size_t{channel / 16} * rows + row) * 16 + channel % 16
                    : std::size_t{row} * channels + channel) * size;
}

void dump(std::ostream& stream, const Bytes& bytes) {
    for (auto value : bytes) stream << std::hex << unsigned(value) << '\n';
    stream << std::dec;
}

struct Case { unsigned n, k, channels, size; bool source_blocked, destination_blocked; unsigned fault; };

void generate(const std::string& path) {
    const std::vector<Case> cases{
        {180, 100, 42, 2, true, true, 0}, {100, 50, 42, 2, true, true, 0},
        {100, 100, 42, 4, false, false, 0}, {256, 256, 17, 4, true, false, 0},
        {33, 17, 3, 2, false, true, 0}, {1, 1, 1, 4, false, false, 0},
        {17, 7, 65, 2, true, true, 0}, {180, 100, 42, 4, true, true, 1},
        {180, 100, 42, 2, true, true, 2}, {100, 50, 42, 2, true, true, 3},
        {100, 50, 42, 2, true, true, 4}, {100, 50, 42, 2, true, true, 5},
        {100, 50, 42, 2, true, true, 0}};
    std::ofstream stream(path);
    if (!stream) throw std::runtime_error("cannot create device vectors");
    stream << cases.size() << '\n';
    std::mt19937 random(3301312);
    std::uint64_t id = 0x3300000001;
    for (const auto& c : cases) {
        auto layout = [](bool blocked) { return blocked ? topk::Layout::blocked16 : topk::Layout::dense; };
        const auto src_channels = c.source_blocked ? (c.channels + 15) / 16 * 16 : c.channels;
        const auto dst_channels = c.destination_blocked ? (c.channels + 15) / 16 * 16 : c.channels;
        topk::KernelMemory memory{{score_base, aligned(c.n * 4), topk::Layout::dense},
            {source_base, aligned(c.n * src_channels * c.size), layout(c.source_blocked)},
            {selected_score_base, aligned(c.k * 4), topk::Layout::dense},
            {selected_index_base, aligned(c.k * 8), topk::Layout::dense},
            {destination_base, aligned(c.k * dst_channels * c.size), layout(c.destination_blocked)}};
        const auto descriptor = topk::make_kernel_descriptor({1, c.n, c.k, c.channels, c.size}, 4, memory);
        auto image = topk::make_register_image(id++, descriptor);
        Bytes scores(memory.scores.allocation_bytes, 0xa5), payload(memory.features.allocation_bytes, 0xa5);
        Bytes selected_scores(memory.selected_scores.allocation_bytes, 0xa5);
        Bytes selected_indices(memory.selected_indices.allocation_bytes, 0xa5);
        Bytes selected_features(memory.selected_features.allocation_bytes, 0xa5);
        std::vector<float> values(c.n);
        std::vector<std::uint32_t> words(c.n), indices(c.n);
        for (unsigned i = 0; i < c.n; ++i) {
            values[i] = float(int(random() % 31) - 15);
            if (i % 7 == 0) values[i] = i % 2 ? -0.0f : 0.0f;
            std::memcpy(&words[i], &values[i], 4);
            put(scores, i * 4, words[i], 4);
            for (unsigned channel = 0; channel < src_channels; ++channel)
                put(payload, offset(c.n, i, channel, c.channels, c.size, c.source_blocked), random(), c.size);
        }
        std::iota(indices.begin(), indices.end(), 0);
        std::sort(indices.begin(), indices.end(), [&](auto a, auto b) {
            return values[a] == values[b] ? a < b : values[a] > values[b];
        });
        for (unsigned rank = 0; rank < c.k; ++rank) {
            const auto index = indices[rank];
            put(selected_scores, rank * 4, words[index], 4);
            put(selected_indices, rank * 8, index, 8);
            for (unsigned channel = 0; channel < dst_channels; ++channel) {
                const auto dst = offset(c.k, rank, channel, c.channels, c.size, c.destination_blocked);
                for (unsigned byte = 0; byte < c.size; ++byte)
                    selected_features.at(dst + byte) = channel < c.channels
                        ? payload.at(offset(c.n, index, channel, c.channels, c.size, c.source_blocked) + byte) : 0;
            }
        }
        // Invalid descriptors bypass the host validator deliberately, to test
        // the independent hardware boundary. Fault 4 is a foreign read ID.
        if (c.fault == 5) image[18] = source_base;
        stream << c.fault << ' ' << (c.fault == 3 ? 7 : c.fault == 5 ? 1 : c.fault ? 5 : 0) << '\n';
        for (auto word : image) stream << std::hex << word << '\n';
        stream << std::dec;
        dump(stream, scores); dump(stream, payload); dump(stream, selected_features);
        dump(stream, selected_scores); dump(stream, selected_indices);
    }
}
}  // namespace

int main(int argc, char** argv) {
    try {
        if (argc != 2) throw std::invalid_argument("supply output path");
        generate(argv[1]);
        std::cout << "TOPK_DEVICE_VECTORS_PASS cases=13 validated_cpp_descriptors=13\n";
    } catch (const std::exception& error) {
        std::cerr << error.what() << '\n'; return 1;
    }
}
