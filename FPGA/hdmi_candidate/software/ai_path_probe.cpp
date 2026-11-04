// Bounded, read-only observation of DMA registers used by the matched ARM SDK.
// No application reset, Session, memory transfer, START or CLEAR command.
// Device::Open retains the SDK's ordinary initialization/configuration semantics;
// these are application-level read observations, not pre-initialization state.
#include <icraft-xrt/core/device.h>
#include <array>
#include <chrono>
#include <iostream>
#include <stdexcept>
#include <thread>

int main() {
    try {
        auto device = icraft::xrt::Device::Open("axi://zg330aiu?npu=0x40000000&dma=0x80000000");
        device.setWaitTime(1000);
        const auto versions = device.version();
        if (versions.at("device") != "25122301" || versions.at("icore") != "FMSHZGV3TECH-AID - 24160628")
            throw std::runtime_error("Device identity changed");
        const auto &registers = device.defaultRegRegion();
        // These exact logical offsets and isOffset=true occur in the matched
        // SDK's DMA timeout diagnostics. No inferred register write semantics.
        constexpr std::array<uint64_t, 4> addresses = {0x40584, 0x40588, 0x4058c, 0x405fc};
        for (unsigned sample = 0; sample < 3; ++sample) {
            std::cout << "{\"sample\":" << sample << ",\"registers\":[";
            for (size_t i = 0; i < addresses.size(); ++i) {
                if (i)
                    std::cout << ',';
                std::cout << "{\"logical_offset\":" << addresses[i]
                          << ",\"value\":" << registers.read(addresses[i], true) << '}';
            }
            std::cout << "]}" << std::endl;
            std::this_thread::sleep_for(std::chrono::milliseconds(100));
        }
        std::cout << "AI_PATH_READONLY_PASS" << std::endl;
        return 0;
    } catch (const std::exception &e) {
        std::cerr << "AI_PATH_READONLY_STOP " << e.what() << std::endl;
        return 1;
    }
}
