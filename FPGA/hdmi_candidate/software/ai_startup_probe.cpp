// r9 startup only: no DMA allocation/copy, model, reset command or HDMI START.
#include "r9_startup_observer.hpp"
#include <icraft-xrt/core/device.h>
#include <atomic>
#include <cstdlib>
#include <filesystem>
#include <iostream>
#include <optional>
#include <sys/mman.h>
#include <sys/stat.h>
#include "r9_observer_mapping.hpp"

int main(int argc, char **argv) {
    using namespace pose::r9_startup;
    using pose::dma_probe_evidence::quoted;
    try {
        need(argc == 3 && std::string(argv[2]) == "--allow-device-init" &&
                std::filesystem::path(argv[1]).is_absolute(),
            "Fresh absolute trace path and --allow-device-init required");
        pose::dma_probe_evidence::EvidenceLog evidence(argv[1]);
        const auto began = std::chrono::steady_clock::now();
        auto persist = [&](const std::string &line) {
            evidence.stream() << line;
            evidence.commit();
        };
        auto event = [&](const char *phase) {
            persist("{\"event\":" + quoted(phase) + ",\"us\":" +
                std::to_string(std::chrono::duration_cast<std::chrono::microseconds>(
                    std::chrono::steady_clock::now() - began)
                        .count()) +
                "}\n");
        };
        Mapping mapping;
        auto read = [&](unsigned off) {
            return mapping.read(off);
        };
        auto write = [&](unsigned off, std::uint32_t value) {
            mapping.write(off, value);
        };
        Observer observer(read, write, persist);
        auto idle = []() {
            std::this_thread::sleep_for(std::chrono::milliseconds(20));
        };
        const auto pre = observer.epoch("before_Open", 0, idle);
        need(idle_healthy(pre), "Pre-Open abnormal: Device::Open skipped");
        // On failure _Exit avoids SDK destruction changing hardware evidence.
        std::optional<icraft::xrt::Device> device;
        try {
            const auto during = observer.epoch("during_Open", 2, [&] {
                event("before_Device_Open");
                device.emplace(icraft::xrt::Device::Open("axi://zg330aiu?npu=0x40000000&dma=0x80000000"));
                event("Device_Open_returned");
            });
            need(return_path_healthy(during), "Return-path abnormal during Open; no further epochs");
            const auto post = observer.epoch("after_Open", 4, idle);
            need(idle_healthy(post), "Post-Open abnormal; no further epochs");
            const auto version = device->version();
            need(version.at("device") == "25122301" && version.at("icore") == "FMSHZGV3TECH-AID - 24160628",
                "Device identity changed");
            persist("{\"event\":\"device_identity\",\"device\":" + quoted(version.at("device")) +
                ",\"icore\":" + quoted(version.at("icore")) + "}\n");
            const auto closed = observer.epoch("during_Close", 6, [&] {
                event("before_Device_Close");
                device.reset();
                event("Device_Close_returned");
            });
            need(return_path_healthy(closed), "Return-path abnormal during Close");
        } catch (const std::exception &e) {
            std::cerr << "STARTUP_STOP " << e.what() << std::endl;
            try {
                persist("{\"event\":\"startup_stop\",\"error\":" + quoted(e.what()) + "}\n");
            } catch (...) {
            }
            std::_Exit(71);
        }
        event("STARTUP_OBSERVATION_COMPLETE");
        return 0;
    } catch (const std::exception &e) {
        std::cerr << "STARTUP_PREOPEN_STOP " << e.what() << std::endl;
        return 72;
    }
}
