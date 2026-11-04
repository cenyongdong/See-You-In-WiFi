#include <icraft-xrt/core/device.h>
#include <chrono>
#include <cstdint>
#include <iostream>
#include <stdexcept>
#include <string>
#include <thread>

// No allocation, Session, camera object, NPU reset or display DMA.
// Every write is gated by BOTH candidate ABI words on the actual device.
int main(int argc, char **argv) {
    try {
        const std::string mode = argc == 2 ? argv[1] : "--read-only";
        if (mode != "--read-only" && mode != "--bars" && mode != "--black")
            throw std::runtime_error("Expected --read-only, --bars or --black");
        auto device = icraft::xrt::Device::Open("axi://zg330aiu?npu=0x40000000&dma=0x80000000");
        device.setWaitTime(1000);
        const auto versions = device.version();
        if (versions.at("device") != "25122301" || versions.at("icore") != "FMSHZGV3TECH-AID - 24160628")
            throw std::runtime_error("Device/icore identity differs; no candidate access");
        const auto &regs = device.defaultRegRegion();
        constexpr uint64_t base = 0x400b0000;
        auto rd = [&](uint64_t offset) {
            const auto v = regs.read(base + offset);
            std::cout << "REG 0x" << std::hex << (base + offset) << " 0x" << v << std::dec << std::endl;
            return v;
        };
        if (rd(0) != 0x48444d01 || rd(0x40) != 0x48445301)
            throw std::runtime_error("Corrected full-system ABI absent; no writes");
        if (rd(0x44) != 148500000 || rd(0x48) != 742500000)
            throw std::runtime_error("Clock target contract differs");
        const auto initial = rd(0x30);
        if ((initial & 0xb) != 3)
            throw std::runtime_error("PLL/idle/adapter error gate failed");
        if (mode != "--read-only") {
            const uint32_t value = mode == "--bars" ? 1 : 0;
            regs.write(base + 0x34, value);
            if (rd(0x34) != value || (rd(0x30) & 0xb) != 3)
                throw std::runtime_error("Pattern write rejected");
        }
        using Clock = std::chrono::steady_clock;
        const auto t0a = Clock::now();
        const uint32_t p0 = rd(0x38);
        const auto t0b = Clock::now();
        const uint32_t c0 = rd(0x3c);
        std::this_thread::sleep_for(std::chrono::milliseconds(100));
        const auto t1a = Clock::now();
        const uint32_t p1 = rd(0x38);
        const auto t1b = Clock::now();
        const uint32_t c1 = rd(0x3c);
        const double minSeconds = std::chrono::duration<double>(t1a - t0b).count();
        const double maxSeconds = std::chrono::duration<double>(t1b - t0a).count();
        const uint32_t pixels = p1 - p0, csrticks = c1 - c0;
        if (minSeconds <= 0 || maxSeconds <= 0 || csrticks == 0)
            throw std::runtime_error("Invalid frequency observation interval");
        const double lower = double(pixels) / maxSeconds, upper = double(pixels) / minSeconds;
        std::cout << "FREQUENCY pixels=" << pixels << " csr_ticks=" << csrticks
                  << " min_seconds=" << minSeconds << " max_seconds=" << maxSeconds
                  << " pixel_hz_lower=" << lower << " pixel_hz_upper=" << upper << std::endl;
        if (lower > 148500000.0 * 1.01 || upper < 148500000.0 * 0.99)
            throw std::runtime_error("Pixel count incompatible with 148.5MHz target");
        if ((rd(0x30) & 0xb) != 3)
            throw std::runtime_error("Final PLL/idle/error gate failed");
        std::cout << "HDMI_STATIC_PROBE_PASS mode=" << mode << " DMA_started=0 display_memory_allocations=0"
                  << std::endl;
        return 0;
    } catch (const std::exception &e) {
        std::cerr << "HDMI_STATIC_PROBE_STOP " << e.what() << std::endl;
        return 1;
    }
}
