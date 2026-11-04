// 从已有真实板端输出生成离线HDMI帧；不连接SDK或板卡。
#include "hdmi_canvas.hpp"
#include "skeleton_render.hpp"
#include <array>
#include <filesystem>
#include <fstream>
#include <iostream>
#include <stdexcept>

namespace {
template <class T> T load(const std::filesystem::path &p) {
    if (std::filesystem::file_size(p) != sizeof(T))
        throw std::runtime_error("Actual output size differs");
    T data;
    std::ifstream in(p, std::ios::binary);
    if (!in.read(reinterpret_cast<char *>(data.data()), sizeof(data)))
        throw std::runtime_error("Cannot load actual output");
    return data;
}
void selfTest() {
    bool rejected = false;
    try {
        pose::hdmi::canvas({});
    } catch (const std::runtime_error &) {
        rejected = true;
    }
    if (!rejected)
        throw std::runtime_error("Bad RGB size accepted");
    for (unsigned c = 0; c < 4; ++c) {
        std::vector<uint8_t> rgb(1280 * 720 * 3);
        for (size_t n = 0; n < rgb.size(); ++n)
            rgb[n] = c == 3 || n % 3 == c ? 255 : 0;
        const auto actual = pose::hdmi::canvas(rgb);
        const uint16_t expected[4] = {0xf800, 0x07e0, 0x001f, 0xffff};
        if (actual.size() != pose::hdmi::frameBytes)
            throw std::runtime_error("Canvas length differs");
        for (size_t n = 0; n < actual.size(); n += 2)
            if ((unsigned(actual[n]) | (unsigned(actual[n + 1]) << 8)) != expected[c])
                throw std::runtime_error("RGB565 channel/byte order differs");
    }
}
}

int main(int argc, char **argv) {
    try {
        selfTest();
        if (argc != 4)
            throw std::runtime_error(
                "Expected actual frame folder, fresh output directory and original frame ID");
        const std::filesystem::path input(argv[1]), output(argv[2]);
        const uint64_t frameId = std::stoull(argv[3]);
        if (std::filesystem::exists(output) || !std::filesystem::create_directory(output))
            throw std::runtime_error("Fresh rendering directory required");
        const auto scores = load<std::array<float, 100>>(input / "scores.f32");
        const auto poses = load<std::array<float, 4200>>(input / "poses.f32");
        const auto original = pose_v1::render::draw(scores, poses, frameId);
        const auto pixels = pose::hdmi::canvas(original.rgb);
        std::ofstream raw(output / "skeleton.rgb565", std::ios::binary);
        raw.write(reinterpret_cast<const char *>(pixels.data()), pixels.size());
        raw.close();
        if (!raw)
            throw std::runtime_error("Cannot save HDMI source");
        std::ofstream ppm(output / "skeleton.ppm", std::ios::binary);
        ppm << "P6\n1920 1080\n255\n";
        for (size_t n = 0; n < pixels.size(); n += 2) {
            const unsigned v = unsigned(pixels[n]) | (unsigned(pixels[n + 1]) << 8);
            const unsigned r = (v >> 11) & 31, g = (v >> 5) & 63, b = v & 31;
            const char rgb[3] = {
                char((r << 3) | (r >> 2)), char((g << 2) | (g >> 4)), char((b << 3) | (b >> 2))};
            ppm.write(rgb, 3);
        }
        ppm.close();
        if (!ppm)
            throw std::runtime_error("Cannot save pixel preview");
        std::ofstream meta(output / "render.json");
        meta
            << "{\"offline_render_only\":true,\"new_board_inference\":false,\"HDMI_display_verified\":false,\"input_frame_id\":"
            << frameId << ",\"selected_candidate\":" << original.top_index
            << ",\"clipped_joints\":" << original.clipped_joints
            << ",\"format\":\"1920x1080 RGB565LE\",\"bytes\":" << pixels.size() << "}\n";
        if (!meta)
            throw std::runtime_error("Cannot save render metadata");
        std::cout << "HDMI_CANVAS_OFFLINE_PASS candidate=" << original.top_index
                  << " clipped=" << original.clipped_joints << "\n";
        return 0;
    } catch (const std::exception &e) {
        std::cerr << e.what() << '\n';
        return 1;
    }
}
