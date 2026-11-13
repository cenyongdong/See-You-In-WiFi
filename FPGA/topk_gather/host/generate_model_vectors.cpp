// Feed preserved model tensors to the complete AXI peripheral testbench.
// The full-sort oracle is independent of the RTL insertion/merge algorithm.
#include "topk_registers.hpp"

#include <algorithm>
#include <cmath>
#include <cstring>
#include <fstream>
#include <iostream>
#include <numeric>
#include <string>
#include <vector>

namespace {
using Bytes = std::vector<std::uint8_t>;
constexpr std::uint32_t score_base = 0x1000, feature_base = 0x4000;
constexpr std::uint32_t output_base = 0x20000, selected_base = 0x40000, index_base = 0x41000;

std::uint32_t count(const char* text) {
    std::size_t consumed = 0;
    const auto value = std::stoul(text, &consumed);
    if (consumed != std::strlen(text) || value == 0 || value > 256)
        throw std::invalid_argument("fixture dimensions must be in [1,256]");
    return static_cast<std::uint32_t>(value);
}

std::uint32_t aligned(std::uint32_t bytes) { return (bytes + 63) / 64 * 64; }

Bytes read_exact(const char* path, std::uint32_t bytes, std::uint32_t allocation) {
    std::ifstream stream(path, std::ios::binary | std::ios::ate);
    if (!stream || stream.tellg() != std::streampos(bytes))
        throw std::invalid_argument("input tensor byte count does not match its shape");
    if (allocation < aligned(bytes)) throw std::invalid_argument("allocation is too small");
    Bytes data(allocation, 0xa5);
    stream.seekg(0);
    if (!stream.read(reinterpret_cast<char*>(data.data()), bytes))
        throw std::runtime_error("cannot read complete input tensor");
    return data;
}

float float_at(const Bytes& bytes, std::size_t index) {
    std::uint32_t word = 0;
    for (unsigned i = 0; i < 4; ++i) word |= std::uint32_t{bytes.at(index*4+i)} << (8*i);
    float result;
    static_assert(sizeof(result) == sizeof(word));
    std::memcpy(&result, &word, sizeof(result));
    if (!std::isfinite(result)) throw std::invalid_argument("model fixture contains nonfinite data");
    return result;
}

std::uint16_t half_at(const Bytes& bytes, std::size_t index) {
    return std::uint16_t(bytes.at(index*2)) | (std::uint16_t(bytes.at(index*2+1)) << 8);
}

std::uint16_t compatible_half(std::uint16_t word) {
    // Explicit compatibility with the measured original NPU conversion chain.
    return (word & 0x7c00) == 0 ? 0 : word;
}

float half_value(std::uint16_t word) {
    const auto exponent = (word >> 10) & 31;
    if (exponent == 31) throw std::invalid_argument("model fixture contains nonfinite FP16");
    const auto magnitude = exponent ? std::ldexp(float(1024 + (word & 1023)), int(exponent)-25)
                                    : std::ldexp(float(word & 1023), -24);
    return std::copysign(magnitude, word & 0x8000 ? -1.0f : 1.0f);
}

std::size_t element_at(unsigned row, unsigned channel, unsigned rows, unsigned channels,
                       topk::Layout layout) {
    return layout == topk::Layout::dense ? row*channels+channel
                                        : (channel/16)*rows*16 + row*16 + channel%16;
}

void store_float(Bytes& bytes, std::size_t index, float value) {
    std::uint32_t word;
    std::memcpy(&word, &value, sizeof(word));
    for (unsigned i = 0; i < 4; ++i) bytes.at(index*4+i) = std::uint8_t(word >> (8*i));
}

void dump(std::ostream& stream, const Bytes& bytes) {
    for (auto value : bytes) stream << std::hex << unsigned(value) << '\n';
    stream << std::dec;
}

void generate(unsigned n, unsigned k, unsigned c, const char* scores_path,
              const char* features_path, const char* output_path, const char* memory_path,
              const std::string& format) {
    if (format != "dense-f32" && format != "native-f16-c16" && format != "native-f16-dense")
        throw std::invalid_argument("unknown model boundary format");
    const bool native = format != "dense-f32";
    const unsigned bytes = native ? 2 : 4;
    const auto src_layout = native ? topk::Layout::blocked16 : topk::Layout::dense;
    const auto dst_layout = format == "native-f16-c16" ? topk::Layout::blocked16 : topk::Layout::dense;
    const unsigned src_columns = native ? (c+15)/16*16 : c;
    const unsigned dst_columns = dst_layout == topk::Layout::blocked16 ? (c+15)/16*16 : c;
    if (k > n || n*c*4 > output_base-feature_base)
        throw std::invalid_argument("fixture exceeds the fixed simulation memory regions");
    topk::KernelMemory memory{
        {score_base, aligned(n*bytes), topk::Layout::dense},
        {feature_base, aligned(n*src_columns*bytes), src_layout},
        {selected_base, aligned(k*4), topk::Layout::dense},
        {index_base, aligned(k*8), topk::Layout::dense},
        {output_base, aligned(k*dst_columns*bytes), dst_layout}};
    if (memory_path) {
        std::ifstream stream(memory_path);
        for (auto* port : {&memory.scores, &memory.features, &memory.selected_scores,
                           &memory.selected_indices, &memory.selected_features}) {
            std::uint64_t base, bytes;
            if (!(stream >> base >> bytes) || base > 524288 || bytes > 524288 || base+bytes > 524288)
                throw std::invalid_argument("memory fixture exceeds the testbench window");
            port->base = static_cast<std::uint32_t>(base);
            port->allocation_bytes = static_cast<std::uint32_t>(bytes);
        }
        std::string extra;
        if (stream >> extra) throw std::invalid_argument("unexpected memory fixture fields");
    }
    const auto descriptor = topk::make_kernel_descriptor({1,n,k,c,bytes}, bytes, memory);
    const auto image = topk::make_register_image(0x3302000001, descriptor);
    const auto scores = read_exact(scores_path, n*bytes, memory.scores.allocation_bytes);
    const auto features = read_exact(features_path, n*src_columns*bytes, memory.features.allocation_bytes);
    std::vector<float> numeric(n);
    for (unsigned i = 0; i < n; ++i)
        numeric[i] = native ? half_value(compatible_half(half_at(scores, i))) : float_at(scores, i);
    for (unsigned row = 0; row < n; ++row) for (unsigned channel = 0; channel < c; ++channel) {
        const auto offset = element_at(row, channel, n, c, src_layout);
        if (native) (void)half_value(half_at(features, offset));
        else (void)float_at(features, offset);
    }
    std::vector<unsigned> indices(n);
    std::iota(indices.begin(), indices.end(), 0);
    std::sort(indices.begin(), indices.end(), [&](unsigned a, unsigned b) {
        return numeric[a] == numeric[b] ? a < b : numeric[a] > numeric[b];
    });
    Bytes selected(memory.selected_scores.allocation_bytes, 0xa5);
    Bytes output(memory.selected_features.allocation_bytes, 0xa5), ids(memory.selected_indices.allocation_bytes, 0xa5);
    for (unsigned i = 0; i < k; ++i) {
        store_float(selected, i, numeric[indices[i]]);
        for (unsigned channel = 0; channel < dst_columns; ++channel) {
            const auto dst = element_at(i, channel, k, c, dst_layout);
            if (channel >= c) {
                std::fill_n(output.begin()+dst*bytes, bytes, 0);
            } else {
                const auto src = element_at(indices[i], channel, n, c, src_layout);
                if (native) {
                    const auto word = compatible_half(half_at(features, src));
                    output.at(dst*2) = std::uint8_t(word);
                    output.at(dst*2+1) = std::uint8_t(word >> 8);
                } else std::copy_n(features.begin()+src*4, 4, output.begin()+dst*4);
            }
        }
        for (unsigned byte = 0; byte < 8; ++byte)
            ids.at(i*8+byte) = static_cast<std::uint8_t>(std::uint64_t{indices[i]} >> (8*byte));
    }
    std::ofstream stream(output_path);
    if (!stream) throw std::runtime_error("cannot create model vectors");
    stream << "1\n0 0\n";
    for (auto word : image) stream << std::hex << word << '\n';
    stream << std::dec;
    dump(stream, scores); dump(stream, features); dump(stream, output); dump(stream, selected); dump(stream, ids);
    if (!stream) throw std::runtime_error("cannot write complete model vectors");
}
}  // namespace

int main(int argc, char** argv) {
    try {
        if (argc < 7 || argc > 9)
            throw std::invalid_argument("supply N K C scores features output.txt [memory.txt|-] [dense-f32|native-f16-c16|native-f16-dense]");
        const char* memory = argc >= 8 && std::string(argv[7]) != "-" ? argv[7] : nullptr;
        generate(count(argv[1]), count(argv[2]), count(argv[3]), argv[4], argv[5], argv[6], memory,
                 argc == 9 ? argv[8] : "dense-f32");
        std::cout << "TOPK_MODEL_VECTORS_PASS cases=1 validated_cpp_descriptor=1\n";
    } catch (const std::exception& error) {
        std::cerr << error.what() << '\n';
        return 1;
    }
}
