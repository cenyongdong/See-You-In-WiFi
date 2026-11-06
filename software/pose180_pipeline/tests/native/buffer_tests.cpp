// SDK-independent contract tests. Build separately from the board runtime.
#include <cstdint>
#include "fixed_pool.hpp"
#include "handoff.hpp"
#include "wire.hpp"
#include <chrono>
#include <cstring>
#include <future>
#include <fstream>
#include <filesystem>
#include <iostream>
#include <optional>
#include <stdexcept>
#include <string>
#include <utility>

namespace {
namespace pp = pose180_pipeline;
using namespace std::chrono_literals;

void expect(bool yes, const char* message) {
	if (!yes)
		throw std::runtime_error(message);
}

template <class F> void throws(F&& function, const char* message) {
	bool rejected = false;
	try {
		function();
	} catch (const std::exception&) {
		rejected = true;
	}
	expect(rejected, message);
}

template <class F> void throws_sentinel(F&& function) {
	bool original = false;
	try {
		function();
	} catch (const std::runtime_error& e) {
		original = std::string(e.what()) == "upstream test failure";
	}
	expect(original, "A waiting operation lost the original upstream error");
}

struct Slot {
	std::uint64_t invocation = 0, payload = 0;
};

void pool_ownership_and_reuse() {
	pp::FixedPool<Slot, 2> pool;
	auto first = pool.acquire(100ms);
	auto second = pool.acquire(100ms);
	auto* first_address = &first.value();
	auto* second_address = &second.value();
	expect(first_address != second_address, "Live pool leases alias the same slot");
	first.value() = {11, 111};
	second.value() = {22, 222};
	pool.publish(std::move(second));
	pool.publish(std::move(first));
	expect(pool.high_water() == 2, "Pool high water missed two queued slots");
	throws(
		[&] {
			first.value();
		},
		"Published producer retained access to its lease");
	bool eof = true;
	auto consumer = pool.pop(100ms, eof);
	expect(consumer && !eof && consumer->value().invocation == 22,
		"Ready pool records are not consumed in publication order");
	throws(
		[&] {
			pool.acquire(20ms);
		},
		"A consumed but unreleased slot was overwritten");
	expect(consumer->value().payload == 222 && first_address->payload == 111,
		"Backpressure changed a record still owned by a consumer");
	consumer.reset();
	auto reused = pool.acquire(100ms);
	expect(&reused.value() == second_address, "Released pool storage did not retain its address");
	reused.value() = {33, 333};
	auto other = pool.pop(100ms, eof);
	expect(other && &other->value() == first_address && other->value().payload == 111,
		"Reusing a released slot changed the other outstanding record");
	auto moved = std::move(reused);
	throws(
		[&] {
			reused.value();
		},
		"Moved-from lease still exposes pool storage");
	expect(moved.value().payload == 333, "Lease move lost the owned payload");
}

void pool_wait_resumes_after_release() {
	pp::FixedPool<Slot, 1> pool;
	using Lease = pp::FixedPool<Slot, 1>::Lease;
	std::optional<Lease> held(pool.acquire(100ms));
	auto* address = &held->value();
	std::promise<void> started;
	auto ready = started.get_future();
	auto waiting = std::async(std::launch::async, [&] {
		started.set_value();
		auto lease = pool.acquire(1500ms);
		lease.value().payload = 444;
		return lease;
	});
	ready.wait();
	const bool was_blocked = waiting.wait_for(30ms) == std::future_status::timeout;
	held.reset();
	auto recovered = waiting.get();
	expect(was_blocked, "Full pool did not hold the waiting producer");
	expect(&recovered.value() == address && recovered.value().payload == 444,
		"Released slot did not wake and transfer to the waiting producer");
}

void pool_failure_wakes_waiters() {
	pp::FixedPool<Slot, 1> producer_pool;
	auto held = producer_pool.acquire(100ms);
	std::promise<void> producer_started;
	auto producer_ready = producer_started.get_future();
	auto producer = std::async(std::launch::async, [&] {
		producer_started.set_value();
		throws_sentinel([&] {
			producer_pool.acquire(1500ms);
		});
	});
	producer_ready.wait();
	producer_pool.fail(std::make_exception_ptr(std::runtime_error("upstream test failure")));
	producer.get();
	throws_sentinel([&] {
		producer_pool.check();
	});

	pp::FixedPool<Slot, 1> consumer_pool;
	std::promise<void> consumer_started;
	auto consumer_ready = consumer_started.get_future();
	auto consumer = std::async(std::launch::async, [&] {
		consumer_started.set_value();
		bool eof = false;
		throws_sentinel([&] {
			consumer_pool.pop(1500ms, eof);
		});
	});
	consumer_ready.wait();
	consumer_pool.fail(std::make_exception_ptr(std::runtime_error("upstream test failure")));
	consumer.get();
}

void pool_eof_drains_published_records() {
	pp::FixedPool<Slot, 1> pool;
	bool eof = true;
	expect(!pool.pop(5ms, eof) && !eof, "An empty live pool incorrectly reports EOF");
	auto value = pool.acquire(100ms);
	value.value() = {55, 555};
	pool.publish(std::move(value));
	pool.close();
	auto last = pool.pop(100ms, eof);
	expect(last && !eof && last->value().payload == 555, "EOF discarded an already published record");
	last.reset();
	expect(!pool.pop(100ms, eof) && eof, "Closed and drained pool did not report EOF");
	throws(
		[&] {
			pool.acquire(5ms);
		},
		"Closed pool accepted a new producer");
}

void handoff_holds_the_pool_lease_until_completion() {
	pp::FixedPool<Slot, 1> pool;
	pp::Handoff<Slot> display;
	auto lease = pool.acquire(100ms);
	lease.value() = {77, 777};
	auto* address = &lease.value();
	auto publisher = std::async(std::launch::async, [owned = std::move(lease), &display]() mutable {
		display.submit(owned.value());
	});
	const auto& adopted = display.take();
	const bool same_reference = &adopted == address && adopted.payload == 777;
	const bool publisher_blocked = publisher.wait_for(20ms) == std::future_status::timeout;
	bool pool_blocked = false;
	try {
		pool.acquire(20ms);
	} catch (const std::runtime_error&) {
		pool_blocked = true;
	}
	bool rejected_wrong_id = false;
	try {
		display.complete(78);
	} catch (const std::logic_error&) {
		rejected_wrong_id = true;
	}
	display.complete(77);
	publisher.get();
	auto recycled = pool.acquire(100ms);
	expect(same_reference, "Handoff copied or changed the immutable result reference");
	expect(publisher_blocked && pool_blocked, "Handoff released the pool lease before display completion");
	expect(rejected_wrong_id, "Handoff accepted completion for another invocation");
	expect(&recycled.value() == address, "Completed display storage was not recycled");
}

void handoff_failure_wakes_publisher_and_consumer() {
	pp::Handoff<Slot> pending;
	Slot value{88, 888};
	auto publisher = std::async(std::launch::async, [&] {
		throws_sentinel([&] {
			pending.submit(value);
		});
	});
	const auto& observed = pending.take();
	const bool retained = &observed == &value;
	pending.fail(std::make_exception_ptr(std::runtime_error("upstream test failure")));
	publisher.get();
	expect(retained, "Failure handoff did not expose the original owned record");

	pp::Handoff<Slot> empty;
	std::promise<void> started;
	auto ready = started.get_future();
	auto consumer = std::async(std::launch::async, [&] {
		started.set_value();
		throws_sentinel([&] {
			empty.take();
		});
	});
	ready.wait();
	empty.fail(std::make_exception_ptr(std::runtime_error("upstream test failure")));
	consumer.get();
}

// Independent fixed-offset readers make the wire layout assertions explicit.
std::uint32_t le32(const unsigned char* bytes) {
	return std::uint32_t(bytes[0]) | (std::uint32_t(bytes[1]) << 8) | (std::uint32_t(bytes[2]) << 16) |
		(std::uint32_t(bytes[3]) << 24);
}

std::uint64_t le64(const unsigned char* bytes) {
	return std::uint64_t(le32(bytes)) | (std::uint64_t(le32(bytes + 4)) << 32);
}

void simulated_input_decodes_every_axis() {
	std::array<unsigned char, pp::input_bytes> bytes{};
	std::memcpy(bytes.data(), "PIWCSI2\0", 8);
	pp::put32(bytes.data() + 8, 2);
	pp::put32(bytes.data() + 12, 86400);
	pp::put64(bytes.data() + 16, 0x0102030405060708ull);
	pp::put64(bytes.data() + 24, 0x1112131415161718ull);
	for (std::size_t r = 0; r < 3; ++r)
		for (std::size_t a = 0; a < 3; ++a)
			for (std::size_t t = 0; t < 20; ++t)
				for (std::size_t n = 0; n < 30; ++n) {
					const std::size_t offset = 32 + (((r * 3 + a) * 20 + t) * 30 + n) * 16;
					const double re = 10000.0 * r + 1000.0 * a + 32.0 * t + n + 0.25;
					const double im = -re - 0.5;
					std::memcpy(bytes.data() + offset, &re, 8);
					std::memcpy(bytes.data() + offset + 8, &im, 8);
				}
	pp::Window decoded;
	pp::decode_input(bytes, decoded);
	expect(decoded.frame_id == 0x0102030405060708ull && decoded.source_time_ns == 0x1112131415161718ull,
		"Input decoding changed 64-bit frame identity");
	for (std::size_t r = 0; r < 3; ++r)
		for (std::size_t a = 0; a < 3; ++a)
			for (std::size_t n = 0; n < 30; ++n)
				for (std::size_t t = 0; t < 20; ++t) {
					const auto& value = decoded.csi[(((r * 3 + a) * 30 + n) * 20 + t)];
					const double expected = 10000.0 * r + 1000.0 * a + 32.0 * t + n + 0.25;
					expect(value.real() == expected && value.imag() == -expected - 0.5,
						"Input decoding changed receiver/antenna/time/carrier order");
				}
	bytes[0] = 'X';
	throws(
		[&] {
			pp::decode_input(bytes, decoded);
		},
		"Input accepted a different record magic");
	bytes[0] = 'P';
	const std::uint64_t qnan = 0x7ff8000000012345ull;
	std::memcpy(bytes.data() + bytes.size() - 8, &qnan, 8);
	throws(
		[&] {
			pp::decode_input(bytes, decoded);
		},
		"Input accepted nonfinite raw CSI");
}

void full_result_layout_and_first_bit_preservation() {
	static_assert(pp::full_bytes == 74544, "The new result record must remain 74544 bytes");
	pp::Result result;
	result.frame_id = 0x2122232425262728ull;
	result.invocation = 0x3132333435363738ull;
	result.source_time_ns = 0x4142434445464748ull;
	result.best_index = 179;
	result.process_ms = 12.5;
	result.preprocess_ms = 1.25;
	result.forward_ms = 8.5;
	result.output_ms = 2.75;
	for (std::size_t i = 0; i < result.input.size(); ++i)
		result.input[i] = float(i) * 0.125f;
	for (std::size_t i = 0; i < result.scores.size(); ++i)
		result.scores[i] = float(i) / 256.0f;
	for (std::size_t i = 0; i < result.poses.size(); ++i)
		result.poses[i] = float(i) * -0.25f;
	const std::uint32_t score_nan = 0x7fc12345u, input_nan = 0xffc54321u;
	const std::uint32_t pose_inf = 0x7f800000u, negative_zero = 0x80000000u;
	std::memcpy(&result.scores[17], &score_nan, 4);
	std::memcpy(&result.input[19], &input_nan, 4);
	std::memcpy(&result.poses[42], &pose_inf, 4);
	std::memcpy(&result.poses[0], &negative_zero, 4);
	std::copy_n(result.poses.begin() + 179 * 42, 42, result.selected_pose.begin());
	std::array<unsigned char, pp::full_bytes> bytes;
	bytes.fill(0xa5);
	const std::uint64_t session = 0x0102030405060708ull, sequence = 0x5152535455565758ull;
	pp::encode_full(bytes, result, session, sequence, 111, 222, 333, 444, 7);
	expect(!std::memcmp(bytes.data(), "PIWFUL3\0", 8) && le32(bytes.data() + 8) == 3 &&
			le32(bytes.data() + 12) == 74544,
		"Complete result version or byte count differs");
	const std::uint64_t expected_fields[] = {
		session, result.frame_id, result.invocation, result.source_time_ns, 111, 222, 333, sequence};
	for (std::size_t i = 0; i < 8; ++i)
		expect(
			le64(bytes.data() + 16 + i * 8) == expected_fields[i], "Complete result identity field differs");
	const double timings[] = {12.5, 1.25, 8.5, 2.75};
	expect(!std::memcmp(bytes.data() + 80, timings, sizeof(timings)), "Complete result timing values differ");
	expect(le32(bytes.data() + 112) == 7 && le32(bytes.data() + 116) == 180 &&
			le32(bytes.data() + 120) == 179 && le32(bytes.data() + 124) == 0,
		"Complete result depth/candidate count/top candidate fields differ");
	const auto pose = bytes.data() + 128;
	expect(!std::memcmp(pose, "PIWPOSE1", 8) && pose[8] == 1 && pose[9] == 0 && pose[10] == 88 &&
			pose[11] == 0 && le32(pose + 12) == 256,
		"Embedded display record header differs");
	const std::uint64_t display_fields[] = {
		session, result.frame_id, result.invocation, result.source_time_ns, 444};
	for (std::size_t i = 0; i < 5; ++i)
		expect(le64(pose + 16 + 8 * i) == display_fields[i], "Embedded display identity field differs");
	expect(le32(pose + 56) == 179 && le32(pose + 60) == 14 && le64(pose + 80) == sequence,
		"Embedded display record rejected candidate 179 or changed joint count");
	expect(!std::memcmp(pose + 64, &result.scores[179], 4) &&
			!std::memcmp(pose + 88, result.selected_pose.data(), 168),
		"Selected candidate payload differs");
	expect(!std::memcmp(bytes.data() + 384, result.input.data(), 43200),
		"Full input bytes were filtered or reordered");
	expect(!std::memcmp(bytes.data() + 43584, result.scores.data(), 720),
		"Full score bytes were filtered or reordered");
	expect(!std::memcmp(bytes.data() + 44304, result.poses.data(), 30240),
		"Full pose bytes were filtered or reordered");
	expect(le32(bytes.data() + 384 + 19 * 4) == input_nan &&
			le32(bytes.data() + 43584 + 17 * 4) == score_nan &&
			le32(bytes.data() + 44304 + 42 * 4) == pose_inf && le32(bytes.data() + 44304) == negative_zero,
		"First nonfinite payload bits or signed zero were altered before archiving");
}
} // namespace

int main(int argc, char** argv) {
	try {
		pool_ownership_and_reuse();
		pool_wait_resumes_after_release();
		pool_failure_wakes_waiters();
		pool_eof_drains_published_records();
		handoff_holds_the_pool_lease_until_completion();
		handoff_failure_wakes_publisher_and_consumer();
		simulated_input_decodes_every_axis();
		full_result_layout_and_first_bit_preservation();
		if (argc == 2) {
			expect(!std::filesystem::exists(argv[1]), "Preserve existing cross-language fixture");
			pp::Result result;
			result.frame_id = 1000000;
			result.source_time_ns = 123;
			result.best_index = 179;
			result.scores[179] = 0.75f;
			result.finite_outputs = true;
			for (std::size_t i = 0; i < result.input.size(); ++i)
				result.input[i] = float(i) / 1024;
			for (std::size_t i = 0; i < result.poses.size(); ++i)
				result.poses[i] = float(i) / 256;
			std::copy_n(result.poses.begin() + 179 * 42, 42, result.selected_pose.begin());
			std::array<unsigned char, pp::full_bytes> bytes;
			pp::encode_full(bytes, result, 42, 1, 1, 2, 3, 4, 7);
			std::ofstream fixture(argv[1], std::ios::binary);
			fixture.write(reinterpret_cast<const char*>(bytes.data()), bytes.size());
			fixture.close();
			expect(bool(fixture), "Cross-language fixture write failed");
		}
		std::cout << "pose180 buffer/wire contracts passed\n";
		return 0;
	} catch (const std::exception& e) {
		std::cerr << "pose180 buffer/wire test failed: " << e.what() << '\n';
		return 1;
	}
}
