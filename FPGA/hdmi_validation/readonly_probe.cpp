#include <icraft-xrt/dev/zg330_device.h>
#include <icraft-xrt/core/device.h>
#include <cstdint>
#include <iostream>
#include <stdexcept>
#include <string>
#include <utility>

// Read-only at the application register level. Device::Open and destruction
// execute the existing SDK lifecycle; their private internals are not replaced.
// No Session, memory allocation, camera object, register write, reset or DMA.
int main() {
    try {
        std::cout << "PROBE_BEGIN explicit_register_writes=0 allocations=0" << std::endl;
        {
            auto device = icraft::xrt::Device::Open("axi://zg330aiu?npu=0x40000000&dma=0x80000000");
            device.setWaitTime(1000);
            const auto versions = device.version();
            if (versions.at("device") != "25122301" || versions.at("icore") != "FMSHZGV3TECH-AID - 24160628")
                throw std::runtime_error("Device/icore identity differs; stop before display read");
            std::cout << "DEVICE " << versions.at("device") << " ICORE " << versions.at("icore") << std::endl;
            const auto &registers = device.defaultRegRegion();
            const auto frame_version = registers.read(0x4008000c);
            std::cout << "REG frame_ctrl_version 0x4008000c 0x" << std::hex << frame_version << std::dec
                      << std::endl;
            if (frame_version != 0x20230218)
                throw std::runtime_error("Frame controller version differs; stop without further reads");
            const std::pair<const char *, uint64_t> reads[] = {{"display_read_addr_units8", 0x40080054},
                {"disable_hdmi", 0x40080078}, {"input_hsync", 0x40080094}, {"input_hback", 0x40080098},
                {"input_hactive", 0x4008009c}, {"input_hfront", 0x400800a0}, {"input_vsync", 0x400800a4},
                {"input_vback", 0x400800a8}, {"input_vactive", 0x400800ac}, {"input_vfront", 0x400800b0},
                {"input_vtc_enable", 0x400800b4}};
            for (const auto &item : reads) {
                auto value = registers.read(item.second);
                std::cout << "REG " << item.first << " 0x" << std::hex << item.second << " 0x" << value
                          << std::dec << std::endl;
            }
        }
        std::cout << "PROBE_END sdk_device_scope_destroyed=1 scanout_started=0" << std::endl;
        return 0;
    } catch (const std::exception &e) {
        std::cerr << "PROBE_STOP " << e.what() << std::endl;
        return 1;
    }
}
