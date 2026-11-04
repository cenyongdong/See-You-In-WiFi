// Independent, bounded SDK PL-DDR transfer diagnostic; no model or NPU forward.
#include <icraft-xrt/core/device.h>
#include <array>
#include <cstdlib>
#include <filesystem>
#include <fstream>
#include <iostream>
#include <stdexcept>
#include <vector>
#include "ai_monitor_sdk.hpp"

int main(int argc, char **argv) {
    try {
        const bool observed = argc == 3 && std::string(argv[2]) == "--with-monitor";
        if ((argc != 2 && !observed) || std::filesystem::exists(argv[1]))
            throw std::runtime_error("Fresh evidence file and optional --with-monitor required");
        std::ofstream log(argv[1]);
        if (!log)
            throw std::runtime_error("Cannot create evidence");
        auto device = icraft::xrt::Device::Open("axi://zg330aiu?npu=0x40000000&dma=0x80000000");
        device.setWaitTime(1000);
        const auto versions = device.version();
        if (versions.at("device") != "25122301" || versions.at("icore") != "FMSHZGV3TECH-AID - 24160628")
            throw std::runtime_error("Device identity changed");
        const auto &regs = device.defaultRegRegion();
        if (regs.read(0x40584, true) != 0)
            throw std::runtime_error("Initial SDK DMA status is not zero; no transfer");
        // Identity reads only; no snapshot/reset or DMA before this gate.
        if (observed)
            pose::ai_monitor::validate(device);
        auto region = device.defaultMemRegion();
        if (std::string(region->typeKey()) != "AXIZG330AIPLDDRMemRegionNode")
            throw std::runtime_error("PL DDR region changed");
        auto chunk = region.malloc(1048576, false, 64);
        log << "{\"event\":\"allocation\",\"address\":" << chunk->begin.addr()
            << ",\"bytes\":" << chunk->byte_size << "}\n";
        log.flush();
        const std::array<size_t, 4> sizes = {64, 4096, 65536, 1048576};
        for (const auto n : sizes) {
            std::vector<char> source(n), actual(n);
            for (size_t i = 0; i < n; ++i)
                source[i] = char((i * 37) ^ (i >> 9) ^ n);
            log << "{\"event\":\"write_begin\",\"bytes\":" << n << "}\n";
            log.flush();
            try {
                chunk.write(0, source.data(), n);
                log << "{\"event\":\"write_returned\",\"bytes\":" << n
                    << ",\"status\":" << regs.read(0x40584, true) << "}\n";
                log.flush();
                chunk.read(actual.data(), 0, n);
            } catch (const std::exception &e) {
                log << "{\"event\":\"SDK_exception_transfer_stopped_frames_retained\"}\n";
                log.flush();
                std::cerr << "AI_DMA_STOP " << e.what() << std::endl;
                // Preserve the SDK error first. Observation is only CSR access
                // through this same device; no intervening Device::Open/reset.
                if (observed)
                    try {
                        pose::ai_monitor::save(device, log);
                    } catch (const std::exception &diagnostic) {
                        std::cerr << "AI_MONITOR_CAPTURE_FAILED " << diagnostic.what() << std::endl;
                    }
                std::_Exit(71);
            }
            if (source != actual) {
                log << "{\"event\":\"mismatch_stop\",\"bytes\":" << n << "}\n";
                log.flush();
                std::_Exit(72);
            }
            log << "{\"event\":\"roundtrip_pass\",\"bytes\":" << n << "}\n";
            log.flush();
        }
        if (observed)
            pose::ai_monitor::save(device, log);
        chunk.free();
        log << "{\"event\":\"completed_and_released\"}\n";
        log.flush();
        std::cout << "AI_DMA_ROUNDTRIP_PASS" << std::endl;
        return 0;
    } catch (const std::exception &e) {
        std::cerr << "AI_DMA_PRETRANSFER_STOP " << e.what() << std::endl;
        return 1;
    }
}
