#include "release_guard.hpp"
#include <sys/mman.h>
#include <sys/wait.h>
#include <sys/file.h>
#include <fcntl.h>
#include <signal.h>
#include <atomic>
#include <memory>
#include <vector>
#include <iostream>
#include <new>
#include <stdexcept>

namespace {
void need(bool ok) {
	if (!ok)
		throw std::runtime_error("Release guard test failed");
}

struct Counts {
	std::atomic<int> blocked{0}, freed{0}, completed{0};
};

struct Handle {
	Counts& counts;

	~Handle() {
		++counts.freed;
	}
};

struct Owner {
	Counts& counts;
	std::vector<std::unique_ptr<Handle>> outputs;
	pose180_pipeline::ReleaseGuard activity;

	Owner(Counts& counts) : counts(counts) {
		outputs.emplace_back(new Handle{counts});
		outputs.emplace_back(new Handle{counts});
	}

	~Owner() {
		activity.retain_if_unproved([&](const char*) {
			counts.blocked = 1;
		});
	}
};
}

int main() {
	Counts normal;
	{
		Owner owner(normal);
		owner.activity.begin("forward");
		owner.activity.complete();
	}
	need(normal.freed == 2 && normal.blocked == 0);
	auto* counts = static_cast<Counts*>(
		::mmap(nullptr, sizeof(Counts), PROT_READ | PROT_WRITE, MAP_SHARED | MAP_ANONYMOUS, -1, 0));
	need(counts != MAP_FAILED);
	new (counts) Counts();
	char path[] = "/tmp/pose180-release-test-XXXXXX";
	const int original = ::mkstemp(path);
	need(original >= 0);
	::close(original);
	for (bool initialization : {false, true}) {
		counts->freed = 0;
		counts->blocked = 0;
		counts->completed = 0;
		const auto child = ::fork();
		need(child >= 0);
		if (!child) {
			::signal(SIGTERM, [](int) {
			});
			::signal(SIGINT, [](int) {
			});
			::signal(SIGHUP, [](int) {
			});
			int lease = ::open(path, O_RDWR);
			if (lease < 0 || ::flock(lease, LOCK_EX | LOCK_NB))
				::_exit(91);
			try {
				auto owner = std::make_unique<Owner>(*counts);
				owner->activity.begin(initialization ? "initialization" : "final_wait_timeout");
				throw 71; // Both construction-stage and forward-stage unwinding.
			} catch (...) {
			}
			counts->completed = 1;
			::_exit(92);
		}
		bool ready = false;
		for (int n = 0; n < 200 && !ready; ++n) {
			ready = counts->blocked.load();
			::usleep(10000);
		}
		if (!ready) {
			::kill(child, SIGKILL);
			::waitpid(child, nullptr, 0);
			need(false);
		}
		need(counts->freed == 0 && counts->completed == 0);
		::kill(child, SIGTERM);
		::kill(child, SIGHUP);
		::usleep(50000);
		need(::kill(child, 0) == 0 && counts->freed == 0);
		int contender = ::open(path, O_RDWR);
		need(contender >= 0);
		need(::flock(contender, LOCK_EX | LOCK_NB) != 0);
		::kill(child, SIGKILL); // This child contains fake handles only; never an SDK.
		int status = 0;
		need(::waitpid(child, &status, 0) == child && WIFSIGNALED(status));
		need(::flock(contender, LOCK_EX | LOCK_NB) == 0);
		::close(contender);
	}
	::unlink(path);
	::munmap(counts, sizeof(Counts));
	std::cout
		<< "{\"SDK\":false,\"board_access\":false,\"complete_releases\":true,\"initialization_and_wait_fault_retained\":true,\"lease_retained\":true,\"no_false_completion\":true}\n";
}
