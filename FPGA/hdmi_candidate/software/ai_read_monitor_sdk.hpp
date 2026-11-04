#pragma once

#include <icraft-xrt/core/device.h>
#include <array>
#include <chrono>
#include <cstddef>
#include <cstdint>
#include <ostream>
#include <stdexcept>
#include <thread>

namespace pose::ai_read_monitor {

constexpr std::uint64_t kBase = 0x400b0400;
constexpr std::uint32_t kAbi = 0x41495201;
constexpr std::size_t kWords = 104;

class MonitorError : public std::runtime_error {
public:
    using std::runtime_error::runtime_error;
};

// Fixed package stages, never inferred from the hardware's current sequence.
enum class Epoch {
    FreshBoot,
    AfterSuccessfulProbe,
    AfterTwoSnapshots
};
// Selected by a bounded execution plan, never adopted from a register read.
struct ExpectedSequence {
    std::uint32_t value;
};

struct Snapshot {
    std::array<std::uint32_t, kWords> words{};
    std::size_t words_read = 0;
    std::uint32_t request_before = 0;
    std::uint32_t response_before = 0;
    std::uint32_t status_before = 0;
    std::uint32_t request_after = 0;
    std::uint32_t response_after = 0;
    std::uint32_t status_after = 0;
    bool generation_before_valid = false;
    bool generation_after_valid = false;
    bool verified = false;
};

// Owns one diagnostic ARM/FREEZE lifecycle; the caller owns Device and log.
// Device must outlive every arm/freeze call. After Device destruction, only
// cached/local-state methods and the destructor are allowed; they never use
// device_. Log must outlive every logging call. No copy/move, device Open/reset,
// normal-path synchronization, retry, or destructor SDK access.
class Capture final {
public:
    Capture(const icraft::xrt::Device &device, std::ostream &log, Epoch epoch = Epoch::FreshBoot)
        : device_(device), log_(log), initial_sequence_(epoch_sequence(epoch)) {
    }
    Capture(const icraft::xrt::Device &device, std::ostream &log, ExpectedSequence sequence)
        : device_(device), log_(log), initial_sequence_(sequence.value) {
        need(sequence.value <= 64 && sequence.value % 2 == 0, "Unsupported bounded read-monitor sequence");
    }
    Capture(const Capture &) = delete;
    Capture &operator=(const Capture &) = delete;
    Capture(Capture &&) = delete;
    Capture &operator=(Capture &&) = delete;

    void arm() {
        need(state_ == State::Fresh, "Read monitor ARM lifecycle already consumed");
        state_ = State::ArmAttempted;
        try {
            const auto &regs = device_.defaultRegRegion();
            const auto abi = static_cast<std::uint32_t>(regs.read(kBase + 4));
            const auto count = static_cast<std::uint32_t>(regs.read(kBase + 0x10));
            const auto initial = observe("initial");
            log_ << "{\"event\":\"ai_read_monitor_identity\",\"abi\":" << abi << ",\"word_count\":" << count
                 << ",\"expected_initial_sequence\":" << initial_sequence_ << "}\n";
            checked_flush();
            need(abi == kAbi && count == kWords, "Read monitor ABI/count mismatch; no DMA");
            need(initial.status == 0 && initial.request == initial_sequence_ &&
                    initial.response == initial_sequence_,
                "Read monitor initial sequence/status differs from the selected fixed epoch; no DMA");
            const auto deadline = std::chrono::steady_clock::now() + std::chrono::milliseconds(100);
            regs.write(kBase, 1);
            wait_command("arm", initial_sequence_, initial_sequence_ + 1, deadline);
            state_ = State::Armed;
            armed_once_ = true;
        } catch (...) {
            state_ = State::Failed;
            throw;
        }
    }

    Snapshot freeze() {
        need(state_ == State::Armed, "Read monitor FREEZE requires this object's successful ARM");
        state_ = State::FreezeAttempted;
        try {
            const auto before = observe("before_freeze");
            need(before.status == 0 && before.request == initial_sequence_ + 1 &&
                    before.response == initial_sequence_ + 1,
                "Read monitor FREEZE requires the selected epoch's completed ARM generation");
            const auto &regs = device_.defaultRegRegion();
            const auto deadline = std::chrono::steady_clock::now() + std::chrono::milliseconds(100);
            regs.write(kBase, 2);
            wait_command("freeze", initial_sequence_ + 1, initial_sequence_ + 2, deadline);
            const auto generation = observe("before_words");
            snapshot_.status_before = generation.status;
            snapshot_.request_before = generation.request;
            snapshot_.response_before = generation.response;
            snapshot_.generation_before_valid = true;
            need(generation.status == 0 && generation.request == initial_sequence_ + 2 &&
                    generation.response == initial_sequence_ + 2,
                "Read monitor snapshot generation/status invalid before words");
            for (std::size_t i = 0; i < kWords; ++i) {
                snapshot_.words[i] = static_cast<std::uint32_t>(regs.read(kBase + 0x40 + 4 * i));
                snapshot_.words_read = i + 1;
            }
            const auto after = observe("after_words");
            snapshot_.status_after = after.status;
            snapshot_.request_after = after.request;
            snapshot_.response_after = after.response;
            snapshot_.generation_after_valid = true;
            // Preserve complete raw values before validating the held payload.
            save_cached();
            need(after.status == 0 && after.request == initial_sequence_ + 2 &&
                    after.response == initial_sequence_ + 2,
                "Read monitor generation/status changed during word reads");
            need(snapshot_.words[0] == kAbi, "Read monitor snapshot word0 ABI mismatch");
            snapshot_.verified = true;
            state_ = State::Frozen;
            log_ << "{\"event\":\"ai_read_monitor_snapshot_verified\",\"request\":" << initial_sequence_ + 2
                 << ",\"response\":" << initial_sequence_ + 2 << "}\n";
            checked_flush();
            return snapshot_;
        } catch (...) {
            state_ = State::Failed;
            throw;
        }
    }

    bool can_freeze() const noexcept {
        return state_ == State::Armed;
    }
    bool was_armed() const noexcept {
        return armed_once_;
    }
    bool verified() const noexcept {
        return snapshot_.verified;
    }

    // Reads owned cached bytes only, including a partial capture after a CSR
    // exception. Unread entries are omitted; zeros are never fabricated data.
    // A caller handling an SDK exception prints the original error first.
    void save_cached() const {
        log_ << "{\"event\":\"ai_read_monitor_snapshot_raw\",\"word_count_expected\":" << kWords
             << ",\"expected_initial_sequence\":" << initial_sequence_
             << ",\"expected_freeze_sequence\":" << initial_sequence_ + 2
             << ",\"words_read\":" << snapshot_.words_read
             << ",\"generation_before_valid\":" << (snapshot_.generation_before_valid ? "true" : "false")
             << ",\"status_before\":" << snapshot_.status_before
             << ",\"request_before\":" << snapshot_.request_before
             << ",\"response_before\":" << snapshot_.response_before
             << ",\"generation_after_valid\":" << (snapshot_.generation_after_valid ? "true" : "false")
             << ",\"status_after\":" << snapshot_.status_after
             << ",\"request_after\":" << snapshot_.request_after
             << ",\"response_after\":" << snapshot_.response_after
             << ",\"verified\":" << (snapshot_.verified ? "true" : "false") << ",\"words\":[";
        for (std::size_t i = 0; i < snapshot_.words_read; ++i) {
            if (i != 0)
                log_ << ',';
            log_ << snapshot_.words[i];
        }
        log_ << "]}\n";
        checked_flush();
    }

private:
    enum class State {
        Fresh,
        ArmAttempted,
        Armed,
        FreezeAttempted,
        Frozen,
        Failed
    };
    struct Observation {
        std::uint32_t status;
        std::uint32_t request;
        std::uint32_t response;
    };
    const icraft::xrt::Device &device_;
    std::ostream &log_;
    const std::uint32_t initial_sequence_;
    State state_ = State::Fresh;
    bool armed_once_ = false;
    Snapshot snapshot_{};

    static void need(bool okay, const char *message) {
        if (!okay)
            throw MonitorError(message);
    }
    static std::uint32_t epoch_sequence(Epoch epoch) {
        switch (epoch) {
            case Epoch::FreshBoot:
                return 0;
            case Epoch::AfterSuccessfulProbe:
                return 2;
            case Epoch::AfterTwoSnapshots:
                return 4;
        }
        throw MonitorError("Unsupported fixed read-monitor epoch");
    }
    void checked_flush() const {
        log_.flush();
        need(static_cast<bool>(log_), "Read monitor evidence log write failed");
    }
    Observation observe(const char *phase) const {
        const auto &regs = device_.defaultRegRegion();
        const Observation value{static_cast<std::uint32_t>(regs.read(kBase)),
            static_cast<std::uint32_t>(regs.read(kBase + 8)),
            static_cast<std::uint32_t>(regs.read(kBase + 12))};
        log_ << "{\"event\":\"ai_read_monitor_csr\",\"phase\":\"" << phase
             << "\",\"expected_initial_sequence\":" << initial_sequence_ << ",\"status\":" << value.status
             << ",\"request\":" << value.request << ",\"response\":" << value.response << "}\n";
        checked_flush();
        return value;
    }
    void wait_command(const char *phase, std::uint32_t previous, std::uint32_t next,
        std::chrono::steady_clock::time_point deadline) const {
        for (;;) {
            need(std::chrono::steady_clock::now() < deadline, "Read monitor 100ms command deadline");
            const auto value = observe(phase);
            need(std::chrono::steady_clock::now() < deadline, "Read monitor 100ms command deadline");
            need((value.status & ~std::uint32_t{1}) == 0, "Read monitor command error/status bits");
            // These three CSR reads are not atomic. A completion between
            // reads may expose a previous request and a next response; wait
            // for the complete next/next/status0 tuple instead of rejecting
            // that harmless intermediate sampling skew.
            need((value.request == previous || value.request == next) &&
                    (value.response == previous || value.response == next),
                "Read monitor unexpected command generation");
            if (value.request == next && value.response == next && value.status == 0)
                return;
            std::this_thread::sleep_for(std::chrono::microseconds(100));
        }
    }
};

} // namespace pose::ai_read_monitor
