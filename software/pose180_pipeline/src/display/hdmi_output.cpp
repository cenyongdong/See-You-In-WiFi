#include "hdmi_output.hpp"
#include "adoption_state.hpp"
#include <chrono>
#include <cstdlib>
#include <fstream>
#include <iostream>
#include <stdexcept>
#include <string>
#include <thread>
#include <exception>
#include <unistd.h>

namespace pose::hdmi {
namespace {
using Clock = std::chrono::steady_clock;

static int64_t mono_ns() {
	return std::chrono::duration_cast<std::chrono::nanoseconds>(Clock::now().time_since_epoch()).count();
}

void need(bool ok, const char* message) {
	if (!ok)
		throw std::runtime_error(message);
}
}

struct Output::Impl {
	icraft::xrt::Device device;
	icraft::xrt::MemRegion region;
	icraft::xrt::MemChunk frames[2];
	std::ofstream log_file;
	std::ostream log{nullptr};
	std::filesystem::path evidence_dir;
	std::thread::id owner = std::this_thread::get_id();
	uint32_t sequence = 0;
	detail::AdoptionState adoption;
	int64_t last_command_begin_ns = 0, last_snapshot_read_ns = 0, last_log_done_ns = 0;
	bool mayRead = false, closed = false;
	bool allocated[2]{}, release_attempted[2]{}, released[2]{};
	bool stop_attempted = false, stop_proved = false;
	static constexpr uint64_t base = 0x400b0000;

	uint32_t rd(unsigned offset) const {
		return uint32_t(device.defaultRegRegion().read(base + offset));
	}

	void wr(unsigned offset, uint32_t value) const {
		device.defaultRegRegion().write(base + offset, value);
	}

	void checkThread() const {
		need(owner == std::this_thread::get_id(), "HDMI accessed outside owner thread");
	}

	Snapshot command(uint32_t op, uint32_t address = 0, uint32_t id = 0) {
		const auto command_begin_ns = mono_ns();
		checkThread();
		need(!closed, "HDMI output already closed");
		need(rd(0x2c) == 0, "HDMI mailbox not ready or CSR error");
		const uint32_t issued = rd(0x24), replies = rd(0x28);
		need(issued == replies, "HDMI command already in flight");
		wr(0x04, address);
		wr(0x08, id);
		wr(0x0c, op);
		const auto request_sent_ns = mono_ns();
		const auto deadline = Clock::now() + std::chrono::milliseconds(200);
		while (rd(0x28) == replies) {
			need(Clock::now() < deadline, "HDMI command response deadline");
			std::this_thread::sleep_for(std::chrono::microseconds(100));
		}
		need(rd(0x24) == issued + 1 && rd(0x28) == replies + 1, "HDMI response generation mismatch");
		const auto response_observed_ns = mono_ns();
		Snapshot s{rd(0x10), rd(0x14), rd(0x18), rd(0x1c), rd(0x20)};
		const auto snapshot_read_ns = mono_ns();
		last_command_begin_ns = command_begin_ns;
		last_snapshot_read_ns = snapshot_read_ns;
		log << "{\"event\":\"command\",\"sequence\":" << ++sequence << ",\"begin_ns\":" << command_begin_ns
			<< ",\"request_sent_ns\":" << request_sent_ns
			<< ",\"response_observed_ns\":" << response_observed_ns
			<< ",\"snapshot_read_ns\":" << snapshot_read_ns << ",\"op\":" << op
			<< ",\"argument_address\":" << address << ",\"argument_id\":" << id
			<< ",\"issued\":" << issued + 1 << ",\"response\":" << replies + 1 << ",\"status\":" << s.status
			<< ",\"stopped\":" << s.stopped << ",\"address\":" << s.address << ",\"accepted\":" << s.accepted
			<< ",\"faults\":" << s.faults << "}\n";
		log.flush();
		last_log_done_ns = mono_ns();
		need(bool(log), "HDMI evidence write failed");
		need(!(s.status & 0x80000000u), "HDMI command rejected");
		return s;
	}

	Snapshot healthy() {
		auto s = command(0);
		need(s.faults == 0 && (s.status & 0x40), "HDMI fault or PLL lock lost");
		need((rd(0x30) & 9) == 1 && rd(0x2c) == 0, "HDMI adapter/CSR fault");
		return s;
	}

	void stop() {
		if (stop_proved)
			return;
		need(!stop_attempted, "Prior HDMI STOP was not proved; retain frames");
		stop_attempted = true;
		// 即使发生欠载，也发一次STOP取得独立停止标签；不清故障或重试负载。
		const uint32_t tag = 0x70000000u | (sequence + 1);
		command(3, 0, tag);
		const auto deadline = Clock::now() + std::chrono::milliseconds(500);
		while (true) {
			auto s = command(0);
			if (s.idle() && s.stopped == tag && !(s.status & 0x3e)) {
				adoption.prove_stop({s.status, s.stopped, s.address, s.accepted, s.faults}, tag);
				break;
			}
			need(Clock::now() < deadline, "HDMI STOP drain not proved; retain frames");
			std::this_thread::sleep_for(std::chrono::milliseconds(1));
		}
		mayRead = false;
		stop_proved = true;
		log << "{\"event\":\"stop_proved\",\"tag\":" << tag << "}\n";
		log.flush();
	}

	void release_owned() {
		// SDK free may throw before or after mutation. Never repeat a free
		// whose result is unknown; still attempt the other independent slot.
		std::exception_ptr first_error;
		for (int i = 0; i < 2; ++i) {
			if (!allocated[i] || released[i])
				continue;
			try {
				need(!release_attempted[i], "HDMI frame free outcome unknown; no duplicate free");
				release_attempted[i] = true;
				frames[i].free();
				released[i] = true;
			} catch (...) {
				if (!first_error)
					first_error = std::current_exception();
			}
		}
		if (first_error)
			std::rethrow_exception(first_error);
	}
};

Output::Output(const icraft::xrt::Device& device, const std::filesystem::path& evidence,
	std::streambuf* asynchronous_log)
	: impl_(std::make_unique<Impl>()) {
	auto& p = *impl_;
	p.device = device;
	need(!std::filesystem::exists(evidence), "Fresh HDMI evidence file required");
	p.evidence_dir = evidence.parent_path();
	if (asynchronous_log)
		p.log.rdbuf(asynchronous_log);
	else {
		p.log_file.open(evidence);
		p.log.rdbuf(p.log_file.rdbuf());
		need(bool(p.log_file), "Cannot open HDMI evidence");
	}
	need(bool(p.log), "Cannot open HDMI evidence");
	const auto versions = device.version();
	need(versions.at("device") == "25122301" && versions.at("icore") == "FMSHZGV3TECH-AID - 24160628",
		"HDMI device identity differs");
	need(p.rd(0) == 0x48444d01 && p.rd(0x40) == 0x48445301, "HDMI candidate ABI absent");
	need(p.rd(0x44) == 148500000 && p.rd(0x48) == 742500000, "HDMI clock contract differs");
	const auto s = p.healthy();
	need(s.idle(), "HDMI not initially idle; existing owner must stop it");
	p.region = device.getMemRegion("udma");
	need(std::string(p.region->typeKey()) == "AXIZG330AIUdmaMemRegionNode", "HDMI UDMA region differs");
	try {
		for (int i = 0; i < 2; ++i) {
			// 禁止自动释放；显式STOP快照是唯一的帧块释放入口。
			p.frames[i] = p.region.malloc(frameBytes, false, 64);
			p.allocated[i] = true;
			const auto address = p.frames[i]->begin.addr();
			need(p.frames[i].isOn(p.region) && p.frames[i]->byte_size == frameBytes &&
					address >= 0x30100000 && address + frameBytes <= 0x38100000 && address % 64 == 0,
				"Allocated HDMI frame outside validated bounds");
			p.log << "{\"event\":\"allocation\",\"slot\":" << i << ",\"address\":" << address
				  << ",\"bytes\":" << frameBytes << ",\"pointer_type\":" << int(p.frames[i]->begin.ptype())
				  << "}\n";
		}
		const uint64_t a = p.frames[0]->begin.addr(), b = p.frames[1]->begin.addr();
		need(a + frameBytes <= b || b + frameBytes <= a, "HDMI frames overlap");
		p.log.flush();
	} catch (...) {
		const auto original = std::current_exception();
		// Constructor has issued no START/FLIP and has never published these
		// addresses. The outer Output destructor does not run on failure.
		try {
			p.release_owned();
		} catch (...) {
			static constexpr char message[] = "HDMI_CONSTRUCTION_RELEASE_WITHHELD\n";
			const auto diagnostic_bytes = ::write(STDERR_FILENO, message, sizeof(message) - 1);
			(void)diagnostic_bytes;
			std::_Exit(70); // Preserve the existing uncertain-release policy.
		}
		std::rethrow_exception(original);
	}
}

void Output::show_overlay(const std::vector<uint32_t>& words, uint32_t frameId, double prepare_ms) {
	auto& p = *impl_;
	p.checkThread();
	need(!p.closed && p.mayRead && !p.adoption.pending(), "Overlay requires an adopted background");
	need(words.size() <= 512 && words.size() % 2 == 0, "Invalid overlay command count");
	constexpr uint64_t base = 0x400b2000;
	auto rd = [&](unsigned offset) {
		return uint32_t(p.device.defaultRegRegion().read(base + offset));
	};
	auto wr = [&](unsigned offset, uint32_t value) {
		p.device.defaultRegRegion().write(base + offset, value);
	};
	need(rd(0) == 0x534b4c01, "Skeleton overlay ABI absent");
	need((rd(4) & 3) == 0, "Overlay busy or faulted; do not overwrite commands");
	const uint32_t generation = rd(36);
	if (generation == 0) {
		std::ofstream sample(p.evidence_dir / "overlay-first-commands.u32", std::ios::binary);
		sample.write(reinterpret_cast<const char*>(words.data()), words.size() * sizeof(uint32_t));
	}
	const auto begin = mono_ns();
	wr(16, 4);
	for (auto word : words)
		wr(32, word);
	wr(12, frameId);
	wr(16, 1);
	const auto submitted = mono_ns();
	const auto deadline = Clock::now() + std::chrono::milliseconds(500);
	while (rd(4) & 1) {
		need(Clock::now() < deadline, "Overlay adoption timeout");
		std::this_thread::sleep_for(std::chrono::milliseconds(1));
	}
	const auto adopted = mono_ns();
	const uint32_t status = rd(4), done_tag = rd(20), completed = rd(36);
	need(!(status & 2) && done_tag == frameId && completed == generation + 1,
		"Overlay frame rejected or completion mismatch");
	p.log << "{\"event\":\"overlay_adopted\",\"tag\":" << frameId << ",\"hardware_done_tag\":" << done_tag
		  << ",\"hardware_completed\":" << completed << ",\"command_bytes\":" << words.size() * 4
		  << ",\"prepare_ms\":" << prepare_ms << ",\"submit_ms\":" << double(submitted - begin) / 1e6
		  << ",\"submit_and_adopt_ms\":" << double(adopted - begin) / 1e6 << ",\"draw_cycles\":" << rd(24)
		  << ",\"overlay_underflow_seen\":" << ((status >> 3) & 1) << "}\n";
	p.log.flush();
}

void Output::verifyMemory() {
	auto& p = *impl_;
	p.checkThread();
	need(!p.mayRead && p.healthy().idle(), "Memory verification requires idle HDMI");
	std::vector<uint8_t> source(frameBytes), actual(frameBytes);
	auto save = [&](const std::string& name, const std::vector<uint8_t>& data) {
		const auto path = p.evidence_dir / name;
		need(!std::filesystem::exists(path), "Fresh memory evidence required");
		std::ofstream file(path, std::ios::binary);
		file.write(reinterpret_cast<const char*>(data.data()), data.size());
		file.close();
		need(bool(file), "Cannot retain complete memory evidence");
	};
	for (int i = 0; i < 2; ++i) {
		for (size_t n = 0; n < source.size(); ++n)
			source[n] = uint8_t((n * 37) ^ (n >> 9) ^ (i * 0x95));
		save("memory-source-" + std::to_string(i) + ".bin", source);
		p.frames[i].write(0, reinterpret_cast<char*>(source.data()), source.size());
		try {
			p.frames[i].read(reinterpret_cast<char*>(actual.data()), 0, actual.size());
		} catch (...) {
			const auto original = std::current_exception();
			try {
				save("memory-partial-after-read-exception-" + std::to_string(i) + ".bin", actual);
			} catch (...) {
				std::cerr << "MEMORY_EXCEPTION_EVIDENCE_FAILED" << std::endl;
			}
			std::rethrow_exception(original);
		}
		save("memory-actual-" + std::to_string(i) + ".bin", actual);
		need(source == actual, "Full HDMI SDK write/read mismatch");
		p.log << "{\"event\":\"memory_verified\",\"slot\":" << i << ",\"bytes\":" << frameBytes << "}\n";
	}
	p.log.flush();
}

void Output::begin_show(const std::vector<uint8_t>& rgb565, uint32_t frameId) {
	auto& p = *impl_;
	p.checkThread();
	try {
		need(!p.closed && rgb565.size() == frameBytes, "HDMI output closed or frame size invalid");
		const int slot = p.adoption.next_slot(frameId);
		const auto prior = p.healthy();
		const auto begin_ns = mono_ns();
		const uint32_t address = uint32_t(p.frames[slot]->begin.addr());
		p.adoption.reserve(slot, frameId, address,
			{prior.status, prior.stopped, prior.address, prior.accepted, prior.faults}, begin_ns);
		// Public synchronous SDK write only; no ADDR/BOTH dereference/cache guess.
		p.frames[slot].write(0, reinterpret_cast<char*>(const_cast<uint8_t*>(rgb565.data())), rgb565.size());
		if (!p.mayRead) {
			p.wr(0x34, 0);
			need(p.rd(0x34) == 0, "Cannot disable static HDMI pattern");
			p.mayRead = true;
			p.command(1, address, frameId);
		} else {
			p.command(2, address, frameId);
		}
		// Exact original anchor: after START/FLIP command() has returned.
		const auto deadline = Clock::now() + std::chrono::milliseconds(200);
		p.adoption.wait_after_command(
			std::chrono::duration_cast<std::chrono::nanoseconds>(deadline.time_since_epoch()).count());
		p.log << "{\"event\":\"submitted\",\"id\":" << frameId << ",\"slot\":" << slot
			  << ",\"address\":" << address << ",\"begin_ns\":" << begin_ns
			  << ",\"deadline_ns\":" << p.adoption.deadline_ns() << "}\n";
		p.log.flush();
		need(bool(p.log), "HDMI evidence write failed");
	} catch (...) {
		p.adoption.fail();
		throw;
	}
}

bool Output::poll_show() {
	auto& p = *impl_;
	p.checkThread();
	need(!p.closed, "HDMI output already closed");
	if (!p.adoption.pending())
		return false;
	need(p.adoption.waiting(), "HDMI adoption failed/not acknowledged; STOP required");
	Snapshot s;
	try {
		s = p.healthy();
	} catch (...) {
		p.adoption.fail();
		throw;
	}
	const auto decision_ns = mono_ns();
	bool accepted = false;
	try {
		accepted = p.adoption.poll({s.status, s.stopped, s.address, s.accepted, s.faults}, decision_ns);
	} catch (const std::exception& error) {
		const bool expired = std::string(error.what()) == "HDMI frame adoption deadline";
		p.log << "{\"event\":\"" << (expired ? "adoption_deadline" : "adoption_failure")
			  << "\",\"wanted_id\":" << p.adoption.target_id()
			  << ",\"wanted_address\":" << p.adoption.target_address() << ",\"accepted\":" << s.accepted
			  << ",\"address\":" << s.address << ",\"status\":" << s.status << ",\"faults\":" << s.faults
			  << ",\"deadline_ns\":" << p.adoption.deadline_ns() << ",\"decision_ns\":" << decision_ns
			  << ",\"last_command_begin_ns\":" << p.last_command_begin_ns
			  << ",\"last_snapshot_read_ns\":" << p.last_snapshot_read_ns
			  << ",\"last_log_done_ns\":" << p.last_log_done_ns << "}\n";
		p.log.flush();
		throw;
	}
	if (accepted) {
		p.log << "{\"event\":\"adopted\",\"id\":" << p.adoption.target_id()
			  << ",\"slot\":" << p.adoption.current_slot() << ",\"address\":" << p.adoption.target_address()
			  << ",\"write_and_adopt_ms\":" << double(mono_ns() - p.adoption.begin_ns()) / 1e6 << "}\n";
		p.log.flush();
		if (!p.log) {
			p.adoption.fail();
			need(false, "HDMI evidence write failed");
		}
	}
	return accepted;
}

bool Output::pending() const {
	impl_->checkThread();
	return !impl_->closed && impl_->adoption.pending();
}

void Output::show(const std::vector<uint8_t>& rgb565, uint32_t frameId) {
	begin_show(rgb565, frameId);
	while (!poll_show())
		std::this_thread::sleep_for(std::chrono::milliseconds(1));
}

Snapshot Output::observe() {
	return impl_->healthy();
}

void Output::close() {
	auto& p = *impl_;
	p.checkThread();
	if (p.closed)
		return;

	// stop() 负责证明硬件已停止并排空；成功返回后才释放帧缓冲区。
	p.stop();
	p.release_owned();
	p.closed = true;
	p.log << "{\"event\":\"frames_released_after_stop\"}\n";
	p.log.flush();
}

Output::~Output() {
	if (impl_ && !impl_->closed) {
		try {
			close();
		} catch (...) {
			static constexpr char message[] = "HDMI_RELEASE_WITHHELD\n";
			const auto diagnostic_bytes = ::write(STDERR_FILENO, message, sizeof(message) - 1);
			(void)diagnostic_bytes;
			// 无STOP证明时不运行SDK析构／释放；保留日志及物理块身份，禁止继续新负载。
			std::_Exit(70);
		}
	}
}
}
