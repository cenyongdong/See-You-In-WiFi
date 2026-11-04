// 先前已验收板端输出的独立HDMI回放；无Session、NPU前向或PL DDR读写。
#include "hdmi_output.hpp"
#include "hdmi_canvas.hpp"
#include "skeleton_render.hpp"
#include <array>
#include <chrono>
#include <fstream>
#include <iostream>
#include <stdexcept>
#include <thread>

namespace {
template <class T> T load(const std::filesystem::path &file) {
    if (std::filesystem::file_size(file) != sizeof(T))
        throw std::runtime_error("Saved output size differs");
    T value;
    std::ifstream stream(file, std::ios::binary);
    if (!stream.read(reinterpret_cast<char *>(value.data()), sizeof(value)))
        throw std::runtime_error("Saved output read failed");
    return value;
}
}

int main(int argc, char **argv) {
    try {
        if (argc != 3)
            throw std::runtime_error("Expected saved package and fresh output directory");
        const std::filesystem::path package(argv[1]), output(argv[2]);
        if (std::filesystem::exists(output) || !std::filesystem::create_directory(output))
            throw std::runtime_error("Fresh output required");
        auto device = icraft::xrt::Device::Open("axi://zg330aiu?npu=0x40000000&dma=0x80000000");
        device.setWaitTime(1000);
        pose::hdmi::Output sink(device, output / "hdmi.jsonl");
        std::ofstream records(output / "frames.jsonl");
        for (unsigned i = 0; i < 3; ++i) {
            const auto source = package / ("frame-" + std::to_string(i));
            const auto scores = load<std::array<float, 100>>(source / "scores.f32");
            const auto poses = load<std::array<float, 4200>>(source / "poses.f32");
            const uint32_t originalId = 1000000 + i;
            const auto frame = pose_v1::render::draw(scores, poses, originalId);
            const auto pixels = pose::hdmi::canvas(frame.rgb);
            std::ofstream raw(output / ("frame-" + std::to_string(i) + ".rgb565"), std::ios::binary);
            raw.write(reinterpret_cast<const char *>(pixels.data()), pixels.size());
            raw.close();
            if (!raw)
                throw std::runtime_error("Rendered frame save failed");
            sink.show(pixels, originalId);
            records << "{\"source\":\"archived_real_board_output\",\"fresh_inference\":false,\"frame_id\":"
                    << originalId << ",\"selected_candidate\":" << frame.top_index
                    << ",\"clipped_joints\":" << frame.clipped_joints << ",\"bytes\":" << pixels.size()
                    << "}\n";
            records.flush();
            if (!records)
                throw std::runtime_error("Render evidence write failed");
            std::cout << "ARCHIVED_HDMI_SKELETON_VISIBLE " << originalId << std::endl;
            for (unsigned n = 0; n < 80; ++n) {
                std::this_thread::sleep_for(std::chrono::milliseconds(100));
                sink.observe();
            }
        }
        sink.close();
        std::cout << "HDMI_SAVED_SKELETON_PASS fresh_inferences=0 archived_results=3" << std::endl;
        return 0;
    } catch (const std::exception &error) {
        std::cerr << "HDMI_SAVED_SKELETON_STOP " << error.what() << std::endl;
        return 1;
    }
}
