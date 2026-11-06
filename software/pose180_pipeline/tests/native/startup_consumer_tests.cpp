#include "startup_consumer.hpp"
#include <iostream>
using namespace pose180_demo::startup_consumer;

int main() {
	Snapshot idle{0, 1, 1, 0, 12};
	need(healthy(idle), "Released idle path rejected");
	for (unsigned bit : {1u, 4u, 5u, 6u, 7u, 16u}) {
		auto bad = idle;
		bad.flags |= 1u << bit;
		need(!healthy(bad), "Unhealthy live condition accepted");
	}
	for (unsigned bit : {2u, 3u}) {
		auto bad = idle;
		bad.flags &= ~(1u << bit);
		need(!healthy(bad), "Reset path accepted");
	}
	auto previous = idle;
	previous.status = 5;
	need(!healthy(previous), "Prior request/abort accepted");
	auto stale = idle;
	stale.response = 0;
	need(!healthy(stale), "Stale CSR reply accepted");
	Snapshot done{4, 4, 4, (1u << 25) | (80u << 12) | (16u << 3) | 2u, 13};
	need(consumed(done), "Completed 16-beat bounded consumption rejected");
	for (unsigned bit : {26u, 27u, 31u}) {
		auto bad = done;
		bad.status |= 1u << bit;
		need(!consumed(bad), "Consumer error accepted");
	}
	for (unsigned state : {0u, 1u, 3u, 4u, 5u}) {
		auto bad = done;
		bad.status = (bad.status & ~7u) | state;
		need(!consumed(bad), "Non-quiet terminal accepted");
	}
	for (unsigned beats : {0u, 256u}) {
		auto bad = done;
		bad.status = (bad.status & ~(511u << 3)) | (beats << 3);
		need(!consumed(bad), "Invalid consumption count accepted");
	}
	auto no_last = done;
	no_last.status &= ~(1u << 25);
	need(!consumed(no_last), "Missing RLAST accepted");
	auto late = done;
	late.flags |= 1u << 16;
	need(!consumed(late), "PS return still active accepted");
	late = done;
	late.flags |= 1u << 7;
	need(!consumed(late), "S01 return still active accepted");
	std::cout << "STARTUP_CONSUMER_PREDICATES_PASS\n";
}
