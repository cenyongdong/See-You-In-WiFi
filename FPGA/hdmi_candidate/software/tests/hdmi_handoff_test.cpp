// SDK-free tests of the actual exported handoff header.
// g++ -std=c++17 -pthread -Wall -Wextra -Wpedantic -Itests/mock
//     -Isource/board tests/hdmi_handoff_test.cpp -o tests/hdmi_handoff_test
#include <chrono>
#include <cstdint>
#include <exception>
#include <future>
#include <iostream>
#include <stdexcept>
#include <string>
#include <thread>
#include "hdmi_handoff.hpp"

using Result = pose_v1::application::Result;
using namespace std::chrono_literals;

static void need(bool accepted, const char *why) {
    if (!accepted)
        throw std::runtime_error(why);
}

template <class F> static std::string exception_text(F action) {
    try {
        action();
    } catch (const std::exception &error) {
        return error.what();
    }
    throw std::runtime_error("Expected exception was not raised");
}

static std::exception_ptr failure(const char *message) {
    return std::make_exception_ptr(std::runtime_error(message));
}

template <class T> static void ready(std::future<T> &result, const char *why) {
    need(result.wait_for(2s) == std::future_status::ready, why);
}

static void multiple_frames() {
    HdmiHandoff handoff;
    auto publisher = std::async(std::launch::async, [&] {
        for (uint64_t i = 0; i != 32; ++i) {
            Result result;
            result.invocation = i;
            result.frame_id = 1000000 + i;
            handoff.submit(result);
        }
    });
    try {
        for (uint64_t i = 0; i != 32; ++i) {
            auto result = handoff.take();
            need(result.invocation == i && result.frame_id == 1000000 + i,
                "Owned handoff order or frame identity changed");
            // Modify the received owned copy: it must not change the stored identity.
            result.invocation = 999999;
            handoff.complete(i);
        }
        ready(publisher, "Final completion did not release publisher");
        publisher.get();
    } catch (...) {
        handoff.fail(std::current_exception());
        throw;
    }
}

static void gate_failure_wakes_main() {
    HdmiHandoff handoff;
    std::promise<void> entered;
    auto started = entered.get_future();
    auto main = std::async(std::launch::async, [&] {
        entered.set_value();
        return exception_text([&] {
            (void)handoff.take();
        });
    });
    started.get();
    handoff.fail(failure("numeric gate failed"));
    handoff.fail(failure("later diagnostic failed"));
    ready(main, "Gate failure did not wake main within 2s");
    need(main.get() == "numeric gate failed", "First gate failure was replaced");
    need(exception_text([&] {
        (void)handoff.take();
    }) == "numeric gate failed",
        "Failure was not retained for a later take");
}

static void main_failure_wakes_publisher() {
    HdmiHandoff handoff;
    auto publisher = std::async(std::launch::async, [&] {
        Result result;
        result.invocation = 7;
        result.frame_id = 1000007;
        return exception_text([&] {
            handoff.submit(result);
        });
    });
    try {
        const auto result = handoff.take();
        need(result.invocation == 7, "Publisher did not submit expected identity");
        handoff.fail(failure("HDMI show failed"));
        ready(publisher, "Display failure did not wake publisher within 2s");
        need(publisher.get() == "HDMI show failed", "Publisher lost display failure");
    } catch (...) {
        handoff.fail(std::current_exception());
        throw;
    }
}

static void rejects_invalid_completion() {
    HdmiHandoff handoff;
    (void)exception_text([&] {
        handoff.complete(42);
    });
    auto publisher = std::async(std::launch::async, [&] {
        Result result;
        result.invocation = 42;
        result.frame_id = 1000042;
        handoff.submit(result);
    });
    try {
        const auto result = handoff.take();
        need(result.invocation == 42, "Unexpected completion test identity");
        (void)exception_text([&] {
            handoff.complete(43);
        });
        // The failed identity check must leave the right completion usable.
        handoff.complete(42);
        ready(publisher, "Correct completion did not release publisher");
        publisher.get();
        (void)exception_text([&] {
            handoff.complete(42);
        });
    } catch (...) {
        handoff.fail(std::current_exception());
        throw;
    }
}

int main() {
    try {
        multiple_frames();
        std::cout << "PASS owned multi-frame order\n";
        gate_failure_wakes_main();
        std::cout << "PASS gate failure wakes main; first error retained\n";
        main_failure_wakes_publisher();
        std::cout << "PASS main failure wakes publisher\n";
        rejects_invalid_completion();
        std::cout << "PASS invalid completion identity\n";
        return 0;
    } catch (const std::exception &error) {
        std::cerr << "FAIL " << error.what() << '\n';
        return 1;
    }
}
