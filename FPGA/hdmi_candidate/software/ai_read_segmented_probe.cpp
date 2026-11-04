// One Device, three independent observation epochs, only 64 B then 4 KiB.
#include <icraft-xrt/core/device.h>
#include "ai_read_monitor_sdk.hpp"
#include "ai_monitor_sdk.hpp"
#include "dma_probe_evidence.hpp"
#include <chrono>
#include <cstdlib>
#include <filesystem>
#include <iostream>
#include <memory>
#include <thread>

namespace {
using namespace pose::dma_probe_evidence;
using pose::ai_read_monitor::Capture;
using pose::ai_read_monitor::Epoch;
using pose::ai_read_monitor::ExpectedSequence;
const auto began = std::chrono::steady_clock::now();
struct Options {
    unsigned open_ms = 20, after64_ms = 0, sequence = 0;
    std::size_t maximum = 4096;
    bool timing = false;
};
Options options;

void event(EvidenceLog &evidence, const char *name, std::size_t bytes = 0) {
    const auto us =
        std::chrono::duration_cast<std::chrono::microseconds>(std::chrono::steady_clock::now() - began)
            .count();
    evidence.stream() << "{\"event\":" << quoted(name) << ",\"us\":" << us << ",\"bytes\":" << bytes << "}\n";
    // Keep critical-gap logging identical across timing cases, without a
    // flash fsync at every timestamp. Complete byte files still fsync before compare.
    if (options.timing)
        flush_log(evidence.stream());
    else
        evidence.commit();
}

void diagnose(const icraft::xrt::Device &device, Capture &capture, EvidenceLog &evidence) noexcept {
    if (capture.can_freeze()) {
        try {
            static_cast<void>(capture.freeze());
        } catch (const std::exception &error) {
            std::cerr << "SNAPSHOT_FAILED " << error.what() << std::endl;
        }
    }
    try {
        capture.save_cached();
    } catch (const std::exception &error) {
        std::cerr << "CACHE_SAVE_FAILED " << error.what() << std::endl;
    }
    if (capture.was_armed()) {
        try {
            pose::ai_monitor::save(device, evidence.stream());
        } catch (const std::exception &error) {
            std::cerr << "MIG_CAPTURE_FAILED " << error.what() << std::endl;
        }
    }
    try {
        evidence.commit();
    } catch (const std::exception &error) {
        std::cerr << "COMMIT_FAILED " << error.what() << std::endl;
    }
}

[[noreturn]] void stop(const std::exception &original, const char *phase, int code,
    const icraft::xrt::Device &device, Capture &capture, EvidenceLog &evidence) {
    std::cerr << "SEGMENTED_STOP " << phase << " " << original.what() << std::endl;
    try {
        event(evidence, phase);
    } catch (...) {
    }
    diagnose(device, capture, evidence);
    // An in-flight allocation must not be freed/reused after SDK failure.
    std::_Exit(code);
}

int run(const std::string &trace) {
    EvidenceLog evidence(trace);
    std::vector<std::size_t> sizes{64, 4096};
    if (options.maximum == 1048576) {
        sizes.push_back(65536);
        sizes.push_back(1048576);
    }
    for (const auto bytes : sizes)
        for (const auto role : {"source", "actual"})
            if (std::filesystem::exists(artifact(trace, bytes, role)))
                throw std::runtime_error("Evidence already exists; no Device::Open");
    if (options.timing) {
        evidence.stream() << "{\"event\":\"timing_options\",\"open_ms\":" << options.open_ms
                          << ",\"after64_ms\":" << options.after64_ms
                          << ",\"initial_sequence\":" << options.sequence
                          << ",\"maximum_bytes\":" << options.maximum << "}\n";
        // Source persistence is outside the Open-to-DMA timing interval.
        for (const auto bytes : sizes) {
            std::vector<char> source(bytes);
            for (std::size_t i = 0; i < bytes; ++i)
                source[i] = static_cast<char>((i * 37) ^ (i >> 9) ^ bytes);
            save_binary_fresh(artifact(trace, bytes, "source"), source);
        }
        evidence.commit();
    }
    event(evidence, "before_Device_Open");
    auto device = icraft::xrt::Device::Open("axi://zg330aiu?npu=0x40000000&dma=0x80000000");
    event(evidence, "Device_Open_returned");
    Capture after_open(device, evidence.stream(), ExpectedSequence{options.sequence});
    try {
        // The observer command/CSR sampling overhead remains in every case.
        event(evidence, "epoch_after_open");
        after_open.arm();
        std::this_thread::sleep_for(std::chrono::milliseconds(options.open_ms));
        const auto initial_snapshot = after_open.freeze();
        evidence.commit();
        if (options.timing && options.sequence == 2 && initial_snapshot.words[8 + 16 * 4 + 7] != 0)
            stop(std::runtime_error("HDMI RVALID already active after Open; no DMA"), "early_HDMI_stop", 73,
                device, after_open, evidence);
        device.setWaitTime(1000);
        const auto versions = device.version();
        if (versions.at("device") != "25122301" || versions.at("icore") != "FMSHZGV3TECH-AID - 24160628")
            throw std::runtime_error("Device identity changed; no DMA");
        if (device.defaultRegRegion().read(0x40584, true) != 0)
            throw std::runtime_error("Initial DMA status not zero; no transfer");
    } catch (const std::exception &original) {
        stop(original, "after_open_stop", 71, device, after_open, evidence);
    }
    Capture small(device, evidence.stream(), ExpectedSequence{options.sequence + 2});
    try {
        event(evidence, "epoch_64B");
        small.arm();
    } catch (const std::exception &original) {
        stop(original, "arm_64B_stop", 71, device, small, evidence);
    }
    auto region = [&]() {
        try {
            return device.defaultMemRegion();
        } catch (const std::exception &original) {
            stop(original, "region_stop", 71, device, small, evidence);
        }
    }();
    if (std::string(region->typeKey()) != "AXIZG330AIPLDDRMemRegionNode")
        stop(std::runtime_error("PL DDR region changed"), "region_stop", 74, device, small, evidence);
    auto chunk = [&]() {
        try {
            return region.malloc(1048576, false, 64);
        } catch (const std::exception &original) {
            stop(original, "malloc_stop", 71, device, small, evidence);
        }
    }();
    evidence.stream() << "{\"event\":\"allocation\",\"address\":" << chunk->begin.addr()
                      << ",\"bytes\":" << chunk->byte_size << "}\n";
    if (chunk->byte_size != 1048576 || chunk->begin.addr() % 64 != 0)
        stop(std::runtime_error("Allocation changed"), "allocation_stop", 74, device, small, evidence);
    std::unique_ptr<Capture> later;
    for (std::size_t index = 0; index < sizes.size(); ++index) {
        const auto bytes = sizes[index];
        if (index != 0)
            later = std::make_unique<Capture>(device, evidence.stream(),
                ExpectedSequence{options.sequence + 2 + 2 * static_cast<unsigned>(index)});
        auto &capture = index == 0 ? small : *later;
        if (index != 0) {
            try {
                event(evidence, "epoch_next_DMA", bytes);
                capture.arm();
            } catch (const std::exception &original) {
                stop(original, "arm_next_stop", 71, device, capture, evidence);
            }
        }
        std::vector<char> source(bytes), actual(bytes);
        for (std::size_t i = 0; i < bytes; ++i)
            source[i] = static_cast<char>((i * 37) ^ (i >> 9) ^ bytes);
        try {
            if (!options.timing)
                save_binary_fresh(artifact(trace, bytes, "source"), source);
        } catch (const std::exception &original) {
            stop(original, "source_save_stop", 74, device, capture, evidence);
        }
        const char *phase = "write_begin";
        try {
            event(evidence, phase, bytes);
            chunk.write(0, source.data(), bytes);
            event(evidence, "write_returned", bytes);
            phase = "post_write_status";
            const auto status = device.defaultRegRegion().read(0x40584, true);
            evidence.stream() << "{\"event\":\"DMA_status\",\"bytes\":" << bytes << ",\"value\":" << status
                              << "}\n";
            if (status != 0)
                throw std::runtime_error("Post-write DMA status is not zero");
            phase = "read_begin";
            event(evidence, phase, bytes);
            chunk.read(actual.data(), 0, bytes);
            event(evidence, "read_returned", bytes);
            if (bytes == 64)
                std::this_thread::sleep_for(std::chrono::milliseconds(options.after64_ms));
        } catch (const std::exception &original) {
            stop(original, phase, 71, device, capture, evidence);
        }
        try {
            save_binary_fresh(artifact(trace, bytes, "actual"), actual);
        } catch (const std::exception &original) {
            stop(original, "actual_save_stop", 74, device, capture, evidence);
        }
        if (source != actual) {
            const auto mismatch = std::mismatch(source.begin(), source.end(), actual.begin());
            evidence.stream() << "{\"event\":\"mismatch\",\"bytes\":" << bytes
                              << ",\"offset\":" << (mismatch.first - source.begin()) << "}\n";
            stop(std::runtime_error("Complete saved bytes differ"), "mismatch_stop", 72, device, capture,
                evidence);
        }
        try {
            event(evidence, "roundtrip_pass", bytes);
            const auto snapshot = capture.freeze();
            event(evidence, "snapshot_complete", bytes);
            if (options.timing && options.sequence == 2 && snapshot.words[8 + 16 * 4 + 7] != 0)
                stop(std::runtime_error("HDMI RVALID appeared; no later DMA"), "early_HDMI_stop", 73, device,
                    capture, evidence);
        } catch (const std::exception &original) {
            stop(original, "freeze_stop", 71, device, capture, evidence);
        }
    }
    try {
        pose::ai_monitor::save(device, evidence.stream());
        chunk.free();
    } catch (const std::exception &original) {
        stop(original, "release_stop", 71, device, *later, evidence);
    }
    event(evidence, "completed_and_released");
    evidence.commit();
    std::cout << "SEGMENTED_64B_4KiB_PASS" << std::endl;
    return 0;
}
}

int main(int argc, char **argv) {
    try {
        if ((argc != 2 && argc != 6) || !std::filesystem::path(argv[1]).is_absolute())
            throw std::runtime_error("One fresh absolute trace path required");
        if (argc == 6) {
            options.timing = true;
            options.open_ms = static_cast<unsigned>(std::stoul(argv[2]));
            options.after64_ms = static_cast<unsigned>(std::stoul(argv[3]));
            options.sequence = static_cast<unsigned>(std::stoul(argv[4]));
            options.maximum = std::stoul(argv[5]);
            if ((options.open_ms != 0 && options.open_ms != 20) ||
                (options.after64_ms != 0 && options.after64_ms != 20) || options.sequence > 24 ||
                (options.sequence % 6 != 0 && options.sequence != 2) ||
                (options.maximum != 4096 && options.maximum != 1048576))
                throw std::runtime_error("Unsupported fixed timing plan");
        }
        return run(argv[1]);
    } catch (const std::exception &original) {
        std::cerr << "SEGMENTED_PRELOAD_STOP " << original.what() << std::endl;
        // Covers Open/initial setup errors; no reopen, reset or failed-load retry.
        std::_Exit(71);
    }
}
