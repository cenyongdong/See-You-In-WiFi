#include "r9_startup_observer.hpp"
#include <iostream>
#include <vector>
int main() {
    using namespace pose::r9_startup;
    for (unsigned mode = 0; mode < 9; ++mode) {
        unsigned initial = mode == 7 ? 2 : mode == 8 ? 10 : 0;
        unsigned seq = initial, writes = 0, actions = 0;
        std::vector<std::string> log;
        auto read = [&](unsigned off) -> std::uint32_t {
            if (off == 4)
                return mode == 1 ? 0 : abi;
            if (off == 0x10)
                return 104;
            if (off == 8 || off == 12)
                return seq;
            if (off == 0)
                return 0;
            if (off == 0x40)
                return abi;
            if (off == 0x44)
                return 4000000;
            if (off == 0x48)
                return 0x19;
            if (off == 0x40 + 4 * (8 + 16 * 4 + 7) && mode == 5)
                return 123;
            if (off == 0x40 + 4 * (8 + 16 * 5 + 7) && mode == 6)
                return 123;
            return 0;
        };
        auto write = [&](unsigned off, unsigned op) {
            need(off == 0 && (op == 1 || op == 2), "Unexpected test command");
            ++writes;
            if (mode != 4)
                ++seq;
        };
        auto persist = [&](const std::string &line) {
            log.push_back(line);
        };
        Observer observer(read, write, persist);
        bool failed = false;
        std::string error;
        try {
            auto s = observer.epoch("test", initial, [&] {
                ++actions;
                if (mode == 2)
                    throw std::runtime_error("original SDK error");
                if (mode == 3)
                    seq = 0;
            });
            need(idle_healthy(s), "Unhealthy pre-Open gate");
        } catch (const std::exception &e) {
            failed = true;
            error = e.what();
        }
        need(failed == (mode != 0 && mode != 7 && mode != 8), "Failure classification differs");
        need(writes == (mode == 1 ? 0u : (mode == 3 || mode == 4) ? 1u : 2u), "Unexpected command retry");
        need(actions == (mode == 1 || mode == 4 ? 0u : 1u), "Action ran before valid ARM");
        bool raw = false, exception = false;
        for (const auto &line : log) {
            raw |= line.find("startup_snapshot") != std::string::npos;
            exception |= line.find("action_exception") != std::string::npos;
        }
        if (mode == 2)
            need(error == "original SDK error" && exception && raw, "Original error or raw snapshot lost");
        if (mode == 0 || mode == 5)
            need(raw, "Complete raw output absent before gate");
    }
    std::cout
        << "STARTUP_OBSERVER_TEST_PASS 9 cases: healthy, wrong ABI, SDK error, generation reset, stalled command, HDMI/HP2 RVALID, fixed sequences 2/10\n";
}
