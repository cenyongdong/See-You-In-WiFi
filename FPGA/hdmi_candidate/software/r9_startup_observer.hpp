// 观察器只核验既有释放序列；状态快照不替代硬件 STOP/排空证明。
#pragma once
#include "dma_probe_evidence.hpp"
#include <array>
#include <chrono>
#include <cstdint>
#include <exception>
#include <iostream>
#include <thread>

namespace pose::r9_startup {
constexpr std::uint32_t abi = 0x41495201;
struct Tuple {
    std::uint32_t status, request, response;
};
struct Snapshot {
    std::array<std::uint32_t, 104> words{};
};
inline void need(bool ok, const char *why) {
    if (!ok)
        throw std::runtime_error(why);
}
inline bool idle_healthy(const Snapshot &s) {
    const auto &w = s.words;
    if (w[0] != abi || w[1] == 0 || (w[2] & 31) != 0x19 || w[3] != 0)
        return false;
    for (unsigned c = 0; c < 6; ++c)
        if (w[8 + 16 * c] != 0 || w[9 + 16 * c] != 0 || w[15 + 16 * c] != 0)
            return false;
    return w[8 + 16 * 4 + 7] == 0;
}
inline bool return_path_healthy(const Snapshot &s) {
    if (s.words[8 + 16 * 4 + 7] != 0)
        return false;
    for (unsigned c = 0; c < 6; ++c)
        if (s.words[8 + 16 * c + 3] != 0)
            return false;
    return true;
}
// Independent CSR transport survives an SDK exception. Writes are ARM/FREEZE
// only; generations come from the fixed plan, never from observed registers.
template <class Read, class Write, class Persist> class Observer {
public:
    Observer(Read read, Write write, Persist persist) : read_(read), write_(write), persist_(persist) {
    }
    template <class Action> Snapshot epoch(const char *phase, std::uint32_t initial, Action action) {
        need(initial <= 10 && initial % 2 == 0, "Unsupported fixed startup epoch");
        need(read_(4) == abi && read_(0x10) == 104, "Observer ABI/count differs; no command");
        exact(observe(phase), initial);
        command(1, initial + 1, phase);
        std::exception_ptr original;
        try {
            action();
        } catch (const std::exception &e) {
            original = std::current_exception();
            std::cerr << "STARTUP_ACTION_ORIGINAL_EXCEPTION " << e.what() << std::endl;
            try {
                persist_(std::string("{\"event\":\"action_exception\",\"phase\":") +
                    dma_probe_evidence::quoted(phase) + ",\"error\":" + dma_probe_evidence::quoted(e.what()) +
                    "}\n");
            } catch (...) {
                std::cerr << "STARTUP_EXCEPTION_LOG_FAILED" << std::endl;
            }
        }
        try {
            // Reset can erase an epoch. Save the tuple, stop, and never re-arm to replace it.
            exact(observe(phase), initial + 1);
            command(2, initial + 2, phase);
            exact(observe(phase), initial + 2);
            Snapshot s;
            for (unsigned i = 0; i < 104; ++i)
                s.words[i] = read_(0x40 + 4 * i);
            const auto after = observe(phase);
            std::string raw = "{\"event\":\"startup_snapshot\",\"phase\":";
            raw += dma_probe_evidence::quoted(phase) + ",\"sequence\":" + std::to_string(initial + 2) +
                ",\"words\":[";
            for (unsigned i = 0; i < 104; ++i) {
                if (i)
                    raw += ',';
                raw += std::to_string(s.words[i]);
            }
            persist_(raw + "]}\n"); // Complete raw output before payload validation.
            exact(after, initial + 2);
            need(s.words[0] == abi, "Raw snapshot ABI differs");
            if (original)
                std::rethrow_exception(original);
            return s;
        } catch (const std::exception &e) {
            if (original) {
                try {
                    persist_(std::string("{\"event\":\"diagnostic_after_exception\",\"error\":") +
                        dma_probe_evidence::quoted(e.what()) + "}\n");
                } catch (...) {
                }
                std::rethrow_exception(original);
            }
            throw;
        }
    }

private:
    Read read_;
    Write write_;
    Persist persist_;
    static void exact(Tuple t, std::uint32_t seq) {
        need(t.status == 0 && t.request == seq && t.response == seq,
            "Observer generation/status changed; no retry");
    }
    Tuple observe(const char *phase) {
        const Tuple t{read_(0), read_(8), read_(12)};
        persist_(std::string("{\"event\":\"startup_csr\",\"phase\":") + dma_probe_evidence::quoted(phase) +
            ",\"status\":" + std::to_string(t.status) + ",\"request\":" + std::to_string(t.request) +
            ",\"response\":" + std::to_string(t.response) + "}\n");
        return t;
    }
    void command(std::uint32_t op, std::uint32_t seq, const char *phase) {
        write_(0, op);
        const auto deadline = std::chrono::steady_clock::now() + std::chrono::milliseconds(100);
        for (;;) {
            const Tuple t{read_(0), read_(8), read_(12)};
            if (t.status == 0 && t.request == seq && t.response == seq)
                return;
            if ((t.status & ~1u) != 0 || (t.request != seq - 1 && t.request != seq) ||
                (t.response != seq - 1 && t.response != seq) ||
                std::chrono::steady_clock::now() >= deadline) {
                observe(phase);
                throw std::runtime_error("Observer command failed or 100ms deadline; no retry");
            }
            std::this_thread::sleep_for(std::chrono::microseconds(100));
        }
    }
};
}
