// 子进程监督与退出回执沿用原流程；进程退出本身不证明硬件在途对象已释放。
// Standard C/C++/POSIX only. This process never links or invokes Icraft.
#include "r9_startup_observer.hpp"
#include "r9_observer_mapping.hpp"
#include <csignal>
#include <filesystem>
#include <iostream>
#include <poll.h>
#include <sys/wait.h>
namespace {
using namespace pose::r9_startup;
class Child {
public:
    pid_t pid = -1;
    int tx = -1, rx = -1, status = 0;
    bool gone = false;
    void launch(const std::string &executable, const std::string &trace) {
        int cmd[2], response[2];
        need(::pipe(cmd) == 0 && ::pipe(response) == 0, "Cannot create private protocol pipes");
        const int out =
            ::open((trace + ".child.stdout").c_str(), O_WRONLY | O_CREAT | O_EXCL | O_CLOEXEC, 0600);
        const int err =
            ::open((trace + ".child.stderr").c_str(), O_WRONLY | O_CREAT | O_EXCL | O_CLOEXEC, 0600);
        need(out >= 0 && err >= 0, "Fresh child logs required");
        const std::string in_fd = std::to_string(cmd[0]), out_fd = std::to_string(response[1]);
        pid = ::fork();
        need(pid >= 0, "Cannot fork SDK child");
        if (pid == 0) {
            ::close(cmd[1]);
            ::close(response[0]);
            ::dup2(out, 1);
            ::dup2(err, 2);
            ::close(out);
            ::close(err);
            ::execl(executable.c_str(), executable.c_str(), "--coordinated", in_fd.c_str(), out_fd.c_str(),
                nullptr);
            std::_Exit(75);
        }
        ::close(cmd[0]);
        ::close(response[1]);
        ::close(out);
        ::close(err);
        tx = cmd[1];
        rx = response[0];
        std::cerr << "SDK_CHILD_PID " << pid << std::endl;
    }
    void send(char c) {
        need(::write(tx, &c, 1) == 1, "SDK child protocol write failed");
    }
    void expect(char expected) {
        unsigned soft = 0;
        for (;;) {
            pollfd p{rx, POLLIN, 0};
            const auto n = ::poll(&p, 1, 1000);
            if (n < 0 && errno == EINTR)
                continue;
            need(n >= 0, "SDK child protocol poll failed");
            if (n > 0) {
                char actual = 0;
                need(::read(rx, &actual, 1) == 1, "SDK child ended before protocol response");
                need(actual == expected, "SDK child reported failure; preserve original child.stderr");
                return;
            }
            if (++soft % 25 == 0)
                std::cerr << "SDK_CHILD_STILL_RUNNING pid=" << pid << " seconds=" << soft << std::endl;
        }
    }
    void join() {
        if (gone || pid < 0)
            return;
        while (::waitpid(pid, &status, 0) < 0) {
            if (errno != EINTR)
                throw std::runtime_error("Cannot reap SDK child");
        }
        gone = true;
    }
    void abort_waiting() noexcept {
        if (pid < 0 || gone)
            return;
        const auto result = ::waitpid(pid, &status, WNOHANG);
        if (result == pid) {
            gone = true;
            return;
        }
        // Called only after a response/return from the action. No SDK workload kill.
        const char abort = 'A';
        static_cast<void>(::write(tx, &abort, 1));
        try {
            join();
        } catch (...) {
        }
    }
    ~Child() {
        if (tx >= 0)
            ::close(tx);
        if (rx >= 0)
            ::close(rx);
    }
};
}
int main(int argc, char **argv) {
    using namespace pose::r9_startup;
    using pose::dma_probe_evidence::quoted;
    std::signal(SIGPIPE, SIG_IGN);
    Child child;
    try {
        need((argc == 3 || (argc == 4 && std::string(argv[3]) == "--library-first")) &&
                std::filesystem::path(argv[1]).is_absolute() && std::filesystem::path(argv[2]).is_absolute(),
            "Absolute trace, fixed SDK child and optional library-first mode required");
        const bool library_first = argc == 4;
        pose::dma_probe_evidence::EvidenceLog evidence(argv[1]);
        auto persist = [&](const std::string &x) {
            evidence.stream() << x;
            evidence.commit();
        };
        auto event = [&](const char *x) {
            persist("{\"event\":" + quoted(x) + "}\n");
        };
        // Reverse-order experiment deliberately performs no /dev/mem open, mapping,
        // CSR read or ARM before the SDK child reports completion of library load.
        if (library_first) {
            event("before_SDK_process_load_no_CSR_access");
            child.launch(argv[2], argv[1]);
            child.expect('R');
            event("SDK_loaded_no_Open_no_CSR_yet");
        }
        Mapping m;
        auto read = [&](unsigned off) {
            return m.read(off);
        };
        auto write = [&](unsigned off, std::uint32_t x) {
            m.write(off, x);
        };
        Observer observer(read, write, persist);
        auto idle = []() {
            std::this_thread::sleep_for(std::chrono::milliseconds(20));
        };
        Snapshot s;
        if (library_first) {
            s = observer.epoch("after_library_before_Open", 0, idle);
            need(idle_healthy(s), "After-library pre-Open abnormal: Device::Open skipped");
        } else {
            s = observer.epoch("pure_before_library", 2, idle);
            need(idle_healthy(s), "Pure pre-library abnormal: SDK child not launched");
            s = observer.epoch("library_load", 4, [&] {
                event("before_SDK_process_load");
                child.launch(argv[2], argv[1]);
                child.expect('R');
                event("SDK_loaded_no_Open");
            });
            need(idle_healthy(s), "SDK load window abnormal: Device::Open skipped");
        }
        const unsigned open_sequence = library_first ? 2 : 6;
        s = observer.epoch("Device_Open", open_sequence, [&] {
            event("before_Device_Open");
            child.send('G');
            child.expect('O');
            event("Device_Open_returned");
        });
        need(return_path_healthy(s), "Return-path abnormal during Open");
        s = observer.epoch("idle_after_Open", open_sequence + 2, idle);
        need(idle_healthy(s), "Post-Open idle abnormal");
        child.send('V');
        child.expect('V');
        event("Device_identity_verified");
        s = observer.epoch("Device_Close_and_unload", open_sequence + 4, [&] {
            child.send('C');
            child.expect('C');
            child.join();
        });
        need(return_path_healthy(s), "Return-path abnormal during Close/unload");
        need(WIFEXITED(child.status) && WEXITSTATUS(child.status) == 0, "SDK child exit differs");
        event("SOFTWARE_INIT_OBSERVATION_COMPLETE");
        return 0;
    } catch (const std::exception &e) {
        std::cerr << "INIT_SUPERVISOR_STOP " << e.what() << std::endl;
        child.abort_waiting();
        return 71;
    }
}
