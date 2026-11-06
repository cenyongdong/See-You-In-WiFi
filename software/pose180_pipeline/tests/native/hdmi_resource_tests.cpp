#include "hdmi_output.hpp"
#include <sys/mman.h>
#include <sys/wait.h>
#include <unistd.h>
#include <sstream>
#include <iostream>
#include <new>
#include <stdexcept>

void need(bool ok) {
	if (!ok)
		throw std::runtime_error("HDMI resource test failed");
}

int main() {
	using namespace icraft::xrt;
	std::ostringstream sink;
	for (int mode : {0, 1, 2, 3, 4, 9}) {
		default_state = {};
		default_state.mode = mode;
		bool failed = false;
		try {
			pose::hdmi::Output output(Device{}, "/nonexistent-test-hdmi-output", sink.rdbuf());
			output.close();
			output.close();
		} catch (...) {
			failed = true;
		}
		need(failed == (mode != 0));
		need(default_state.outstanding == 0 && default_state.duplicates == 0);
		need(default_state.free_calls == (mode == 9 ? 0 : (mode == 1 || mode == 3) ? 1 : 2));
		need(default_state.stop_calls == (mode == 0 ? 1 : 0));
	}
	auto* shared = static_cast<TestState*>(
		::mmap(nullptr, sizeof(TestState), PROT_READ | PROT_WRITE, MAP_SHARED | MAP_ANONYMOUS, -1, 0));
	need(shared != MAP_FAILED);
	new (shared) TestState();
	for (int mode : {5, 6, 8}) {
		*shared = {};
		shared->mode = mode;
		test_state = shared;
		const auto child = ::fork();
		need(child >= 0);
		if (!child) {
			pose::hdmi::Output output(Device{}, "/nonexistent-test-hdmi-output", sink.rdbuf());
			// Partial free and STOP failures remain uncertain. Repeated close
			// must never repeat a STOP or a free with unknown side effects.
			try {
				output.close();
			} catch (...) {
			}
			try {
				output.close();
			} catch (...) {
			}
			// Destructor takes the existing exit-70 protection, including ints.
			return 99;
		}
		int status = 0;
		need(::waitpid(child, &status, 0) == child);
		need(WIFEXITED(status) && WEXITSTATUS(status) == 70);
		need(shared->duplicates == 0);
		need(shared->free_calls == (mode == 5 ? 2 : mode == 6 ? 0 : 1));
		need(shared->stop_calls == (mode == 8 ? 0 : 1));
	}
	test_state = &default_state;
	::munmap(shared, sizeof(TestState));
	std::cout
		<< "{\"SDK\":false,\"board_access\":false,\"cases\":9,\"partial_allocation_rollback\":true,\"repeat_close_no_duplicate_free\":true,\"nonstandard_stop_retained\":true}\n";
}
