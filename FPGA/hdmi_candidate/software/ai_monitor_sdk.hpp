#pragma once
#include <icraft-xrt/core/device.h>
#include <array>
#include <chrono>
#include <ostream>
#include <stdexcept>
#include <thread>

namespace pose::ai_monitor {
inline void validate(const icraft::xrt::Device &device) {
    const auto &r = device.defaultRegRegion();
    if (r.read(0x400b0104) != 0x41494401 || r.read(0x400b0110) != 24)
        throw std::runtime_error("Diagnostic monitor ABI absent; no DMA permitted");
}
// Capture through the already-open SDK device, including after a failure.
// Does not open/reset a device, transfer data, clear a fault or retry a load.
inline void save(const icraft::xrt::Device &device, std::ostream &log) {
    constexpr uint64_t base = 0x400b0100;
    const auto &r = device.defaultRegRegion();
    auto need = [](bool ok, const char *message) {
        if (!ok)
            throw std::runtime_error(message);
    };
    validate(device);
    need(r.read(base) == 0, "Diagnostic monitor busy or command error");
    const uint32_t request = r.read(base + 8), response = r.read(base + 12);
    need(request == response, "Diagnostic snapshot already pending");
    r.write(base, 1);
    const auto deadline = std::chrono::steady_clock::now() + std::chrono::milliseconds(100);
    while (r.read(base + 12) == response) {
        need(std::chrono::steady_clock::now() < deadline, "Diagnostic source snapshot deadline");
        std::this_thread::sleep_for(std::chrono::microseconds(100));
    }
    const uint32_t new_request = r.read(base + 8), new_response = r.read(base + 12);
    need(new_request == request + 1 && new_response == new_request && r.read(base) == 0,
        "Diagnostic snapshot generation/status mismatch");
    std::array<uint32_t, 24> words{};
    for (size_t i = 0; i < words.size(); ++i)
        words[i] = r.read(base + 0x40 + 4 * i);
    need(r.read(base + 12) == new_response && r.read(base + 8) == new_request,
        "Diagnostic snapshot changed while reading");
    log << "{\"event\":\"ai_monitor_snapshot\",\"request\":" << new_request
        << ",\"response\":" << new_response << ",\"words\":[";
    for (size_t i = 0; i < words.size(); ++i) {
        if (i)
            log << ',';
        log << words[i];
    }
    log << "]}\n";
    log.flush();
    need(bool(log), "Diagnostic snapshot save failed");
}
}
