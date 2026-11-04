#include "hdmi_output.hpp"
#include <icraft-xrt/core/device.h>
#include <chrono>
#include <filesystem>
#include <fstream>
#include <iostream>
#include <stdexcept>
#include <thread>

namespace {
void acknowledgeKnownFault(const icraft::xrt::Device &device, const std::filesystem::path &out) {
    const auto &reg = device.defaultRegRegion();
    constexpr uint64_t base = 0x400b0000;
    auto rd = [&](unsigned offset) {
        return uint32_t(reg.read(base + offset));
    };
    auto wr = [&](unsigned offset, uint32_t value) {
        reg.write(base + offset, value);
    };
    if (rd(0) != 0x48444d01 || rd(0x40) != 0x48445301 || rd(0x2c) != 0)
        throw std::runtime_error("Repeat precheck ABI/mailbox differs");
    std::ofstream log(out / "user-requested-fault-ack.jsonl");
    auto command = [&](unsigned op) {
        const auto issued = rd(0x24), response = rd(0x28);
        if (issued != response)
            throw std::runtime_error("Repeat precheck command in flight");
        wr(0x04, 0);
        wr(0x08, 0);
        wr(0x0c, op);
        const auto end = std::chrono::steady_clock::now() + std::chrono::milliseconds(200);
        while (rd(0x28) == response) {
            if (std::chrono::steady_clock::now() > end)
                throw std::runtime_error("Repeat precheck response deadline");
        }
        if (rd(0x24) != issued + 1 || rd(0x28) != response + 1)
            throw std::runtime_error("Repeat precheck response generation differs");
        const auto status = rd(0x10), stopped = rd(0x14), faults = rd(0x20);
        log << "{\"op\":" << op << ",\"status\":" << status << ",\"stopped\":" << stopped
            << ",\"faults\":" << faults << ",\"response\":" << response + 1 << "}\n";
        log.flush();
        if (!log || (status & 0x80000000u))
            throw std::runtime_error("Repeat precheck rejected or evidence failed");
        return std::array<uint32_t, 3>{status, stopped, faults};
    };
    const auto before = command(0);
    if (!(before[0] & 1) || (before[0] & 0x3e) || before[1] != 0x70000013 || before[2] != 2)
        throw std::runtime_error("Expected archived first-failure STOP state absent; no clear");
    command(4); // 仅按用户明确重播要求确认已封存故障，不复位设备或伪装原失败通过。
    const auto after = command(0);
    if (!(after[0] & 1) || (after[0] & 0x3e) || after[2] != 0)
        throw std::runtime_error("Known-fault acknowledgement failed; no DMA start");
}

std::vector<uint8_t> pattern(unsigned index) {
    std::vector<uint8_t> frame(pose::hdmi::frameBytes);
    const uint16_t colors[2][4] = {{0xf800, 0x07e0, 0x001f, 0xffff}, {0xf81f, 0x07ff, 0xffe0, 0x0000}};
    for (unsigned y = 0; y < 1080; ++y)
        for (unsigned x = 0; x < 1920; ++x) {
            uint16_t v = colors[index][(x >= 960) + 2 * (y >= 540)];
            if (x < 8 || x >= 1912 || y < 8 || y >= 1072)
                v = 0xffff;
            const size_t offset = (size_t(y) * 1920 + x) * 2;
            frame[offset] = uint8_t(v);
            frame[offset + 1] = uint8_t(v >> 8);
        }
    return frame;
}
}

int main(int argc, char **argv) {
    try {
        if (argc != 3 ||
            (std::string(argv[1]) != "--memory" && std::string(argv[1]) != "--patterns" &&
                std::string(argv[1]) != "--user-requested-repeat"))
            throw std::runtime_error(
                "Expected --memory, --patterns or --user-requested-repeat and fresh evidence directory");
        const std::filesystem::path out(argv[2]);
        if (std::filesystem::exists(out) || !std::filesystem::create_directory(out))
            throw std::runtime_error("Fresh output required");
        auto device = icraft::xrt::Device::Open("axi://zg330aiu?npu=0x40000000&dma=0x80000000");
        device.setWaitTime(1000);
        if (std::string(argv[1]) == "--user-requested-repeat")
            acknowledgeKnownFault(device, out);
        pose::hdmi::Output sink(device, out / "hdmi.jsonl");
        sink.verifyMemory();
        if (std::string(argv[1]) != "--memory") {
            for (unsigned i = 0; i < 2; ++i) {
                auto pixels = pattern(i);
                std::ofstream raw(out / ("pattern-" + std::to_string(i) + ".rgb565"), std::ios::binary);
                raw.write(reinterpret_cast<const char *>(pixels.data()), pixels.size());
                raw.close();
                if (!raw)
                    throw std::runtime_error("Cannot save pattern source");
                sink.show(pixels, 100 + i);
                std::cout << "HDMI_PATTERN_VISIBLE " << i << std::endl;
                for (unsigned n = 0; n < 80; ++n) {
                    std::this_thread::sleep_for(std::chrono::milliseconds(100));
                    sink.observe();
                }
            }
        }
        sink.close();
        std::cout << "HDMI_FRAME_PROBE_PASS mode=" << argv[1] << std::endl;
        return 0;
    } catch (const std::exception &e) {
        std::cerr << "HDMI_FRAME_PROBE_STOP " << e.what() << std::endl;
        return 1;
    }
}
