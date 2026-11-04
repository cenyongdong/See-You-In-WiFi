// Only the documented r9 observer CSR page. No SDK, AI/DMA/control reset or HDMI START.
#include "dma_probe_evidence.hpp"
#include <algorithm>
#include <array>
#include <atomic>
#include <chrono>
#include <cstdint>
#include <filesystem>
#include <iostream>
#ifndef _WIN32
#include <sys/mman.h>
#endif
#include <sys/stat.h>
#include <thread>

namespace {
using Clock = std::chrono::steady_clock;
using namespace pose::dma_probe_evidence;
constexpr std::uint32_t abi = 0x41495201;
struct Snapshot {
    std::array<std::uint32_t, 104> words{};
    std::uint32_t request = 0, response = 0, status = 0, stop_flags = 0;
    double observed_seconds = 0;
};
// Sticky flags remain readable before the first FREEZE publishes the bank.
// No PS/video requests or returns are expected during the no-SDK soak.
constexpr std::uint32_t unexpected_release_flags =
    (1u << 2) | (1u << 5) | (1u << 6) | (1u << 7) | (1u << 8) | (1u << 10);

template <class Read, class Write>
Snapshot capture(Read read, Write write, std::chrono::milliseconds window = std::chrono::milliseconds(20),
    bool watch_release = false) {
    auto need = [](bool good, const char *message) {
        if (!good)
            throw std::runtime_error(message);
    };
    const auto observed_abi = read(4), count = read(0x10);
    const auto initial_status = read(0), initial_request = read(8), initial_response = read(12);
    // Preserve all initial values even when freshness fails; issue no command
    // and do not reinterpret a retained generation as a successful reset.
    std::cerr << "PREOPEN_CSR_INITIAL {\"abi\":" << observed_abi << ",\"count\":" << count
              << ",\"status\":" << initial_status << ",\"request\":" << initial_request
              << ",\"response\":" << initial_response << "}" << std::endl;
    need(observed_abi == abi && count == 104, "Not the r9 observer: no command issued");
    need(initial_status == 0 && initial_request == 0 && initial_response == 0,
        "Not a fresh observer: no command issued");
    auto command = [&](std::uint32_t op, std::uint32_t seq) {
        write(0, op);
        const auto deadline = Clock::now() + std::chrono::milliseconds(100);
        for (;;) {
            const auto status = read(0), req = read(8), resp = read(12);
            need((status & ~1u) == 0 && (req == seq - 1 || req == seq) && (resp == seq - 1 || resp == seq),
                "Command status/generation error");
            if (status == 0 && req == seq && resp == seq)
                break;
            need(Clock::now() < deadline, "Observer command 100ms deadline; no retry");
            std::this_thread::sleep_for(std::chrono::microseconds(100));
        }
    };
    if (watch_release)
        need(read(0x200) == 0x50534c01, "Missing PS release recorder: no ARM issued");
    command(1, 1);
    Snapshot s;
    const auto started = Clock::now(), until = started + window;
    auto heartbeat = started;
    while (Clock::now() < until) {
        if (watch_release) {
            const auto flags = read(0x204);
            s.stop_flags = flags & unexpected_release_flags;
            if (s.stop_flags)
                break;
            if (Clock::now() >= heartbeat) {
                std::cerr << "PASSIVE_SOAK_HEARTBEAT {\"elapsed_seconds\":"
                          << std::chrono::duration<double>(Clock::now() - started).count()
                          << ",\"release_flags\":" << flags << "}" << std::endl;
                heartbeat = Clock::now() + std::chrono::seconds(30);
            }
        }
        const auto remaining = std::chrono::duration_cast<std::chrono::milliseconds>(until - Clock::now());
        if (remaining.count() > 0)
            std::this_thread::sleep_for(std::min(std::chrono::milliseconds(50), remaining));
    }
    s.observed_seconds = std::chrono::duration<double>(Clock::now() - started).count();
    command(2, 2);
    for (unsigned i = 0; i < 104; ++i)
        s.words[i] = read(0x40 + 4 * i);
    s.status = read(0);
    s.request = read(8);
    s.response = read(12);
    // Validation follows complete raw serialization by the caller.
    return s;
}

int self_test() {
    for (unsigned mode = 0; mode < 7; ++mode) {
        unsigned writes = 0;
        std::uint32_t seq = mode == 4 ? 2 : 0;
        auto read = [&](unsigned off) -> std::uint32_t {
            if (off == 4)
                return mode == 1 ? 0 : abi;
            if (off == 0x10)
                return 104;
            if (off == 0)
                return mode == 2 ? 1 : 0;
            if (off == 8 || off == 12)
                return seq;
            if (off == 0x200)
                return mode == 6 ? 0 : 0x50534c01;
            if (off == 0x204)
                return mode == 5 ? (1u << 5) : 0;
            return off == 0x40 ? abi : 0;
        };
        auto write = [&](unsigned off, unsigned op) {
            if (off != 0 || (op != 1 && op != 2))
                throw std::runtime_error("Unexpected test write");
            ++writes;
            if (mode != 3)
                ++seq;
        };
        bool failed = false;
        try {
            auto s = capture(read, write, std::chrono::milliseconds(20), mode >= 5);
            if (s.words[0] != abi || s.request != 2)
                throw std::runtime_error("Bad test snapshot");
            if (mode == 5 && (s.stop_flags != (1u << 5) || s.observed_seconds >= 0.02))
                return 1;
        } catch (const std::exception &) {
            failed = true;
        }
        if (failed != (mode != 0 && mode != 5) ||
            writes !=
                ((mode == 0 || mode == 5) ? 2u
                        : mode == 3       ? 1u
                                          : 0u))
            return 1;
    }
    std::cout << "PREOPEN_CSR_SELF_TEST_PASS 7 cases" << std::endl;
    return 0;
}
}

int main(int argc, char **argv) {
    if (argc == 2 && std::string(argv[1]) == "--self-test")
        return self_test();
#ifdef _WIN32
    std::cerr << "Only --self-test is available on Windows" << std::endl;
    return 2;
#else
    int fd = -1;
    void *mapping = MAP_FAILED;
    try {
        if ((argc != 2 && argc != 4) || !std::filesystem::path(argv[1]).is_absolute())
            throw std::runtime_error("Fresh absolute evidence path [--seconds 1..1800] required");
        auto window = std::chrono::milliseconds(20);
        if (argc == 4) {
            std::size_t consumed = 0;
            const auto seconds = std::stoul(argv[3], &consumed);
            if (std::string(argv[2]) != "--seconds" || consumed != std::string(argv[3]).size() ||
                seconds < 1 || seconds > 1800)
                throw std::runtime_error("Passive soak must be bounded to 1..1800 seconds");
            window = std::chrono::milliseconds(1000 * seconds);
        }
        EvidenceLog evidence(argv[1]);
        fd = ::open("/dev/mem", O_RDWR | O_SYNC | O_CLOEXEC);
        if (fd < 0)
            throw io_error("Cannot open physical CSR device", "/dev/mem");
        struct stat st{};
        if (::fstat(fd, &st) != 0 || !S_ISCHR(st.st_mode))
            throw std::runtime_error("Expected physical register character device");
        // Physical page is fixed by the implemented PS address map. Offset
        // 0x400 is the passive observer; no SDK ADDR/BOTH pointer is dereferenced.
        mapping = ::mmap(nullptr, 4096, PROT_READ | PROT_WRITE, MAP_SHARED, fd, 0x400b0000);
        if (mapping == MAP_FAILED)
            throw io_error("Cannot map r9 observer CSR page", "/dev/mem");
        auto *csr = reinterpret_cast<volatile std::uint32_t *>(static_cast<char *>(mapping) + 0x400);
        auto read = [&](unsigned off) {
            const auto x = csr[off / 4];
            std::atomic_thread_fence(std::memory_order_seq_cst);
            return x;
        };
        auto write = [&](unsigned off, std::uint32_t value) {
            std::atomic_thread_fence(std::memory_order_seq_cst);
            csr[off / 4] = value;
            std::atomic_thread_fence(std::memory_order_seq_cst);
        };
        const auto s = capture(read, write, window, argc == 4);
        auto &out = evidence.stream();
        out << "{\"event\":\"pre_Device_Open_snapshot\",\"physical_CSR\":\"0x400b0400\",\"request\":"
            << s.request << ",\"response\":" << s.response << ",\"status\":" << s.status << ",\"words\":[";
        for (unsigned i = 0; i < 104; ++i) {
            if (i)
                out << ',';
            out << s.words[i];
        }
        out << "]}\n";
        evidence.commit();
        if (argc == 4) {
            out << "{\"event\":\"passive_soak_window\",\"observed_seconds\":" << s.observed_seconds
                << ",\"requested_seconds\":" << window.count() / 1000 << ",\"stop_flags\":" << s.stop_flags
                << "}\n";
            evidence.commit();
        }
        if (s.words[0] != abi || s.status != 0 || s.request != 2 || s.response != 2)
            throw std::runtime_error("Complete raw snapshot saved; generation/ABI validation failed");
        ::munmap(mapping, 4096);
        mapping = MAP_FAILED;
        ::close(fd);
        fd = -1;
        // A valid observation is not a healthy data-path verdict. Controller
        // must inspect the saved values before allowing Device::Open.
        std::cout << "PREOPEN_CSR_SNAPSHOT_SAVED" << std::endl;
        return 0;
    } catch (const std::exception &error) {
        if (mapping != MAP_FAILED)
            ::munmap(mapping, 4096);
        if (fd >= 0)
            ::close(fd);
        std::cerr << "PREOPEN_CSR_STOP " << error.what() << std::endl;
        return 1;
    }
#endif
}
