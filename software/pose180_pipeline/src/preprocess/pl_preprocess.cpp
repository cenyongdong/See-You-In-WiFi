#include "pl_preprocess.hpp"
#include <atomic>
#include <chrono>
#include <cmath>
#include <cstring>
#include <fcntl.h>
#include <stdexcept>
#include <sys/mman.h>
#include <sys/stat.h>
#include <unistd.h>

namespace pose_v1 {
namespace {
// CSR 偏移的单位为字节；FIFO 每次访问必须单独完成。
constexpr unsigned kAbi = 0;
constexpr unsigned kStatus = 4;
constexpr unsigned kInputCount = 8;
constexpr unsigned kTag = 12;
constexpr unsigned kCommand = 16;
constexpr unsigned kCompletedTag = 20;
constexpr unsigned kComputeCycles = 24;
constexpr unsigned kCompletionCount = 28;
constexpr unsigned kOutputCount = 40;
constexpr unsigned kSentinelAddress = 44;
constexpr unsigned kSentinelData = 48;
constexpr unsigned kFaultSample = 52;
constexpr unsigned kFaultReal = 56;
constexpr unsigned kFaultImaginary = 60;
constexpr unsigned kFaultReason = 64;
constexpr unsigned kPublishedWords = 68;
constexpr unsigned kInputFifoWord = 8;
constexpr unsigned kOutputFifoWord = 9;
// 状态位可组合；完成核验仍要求状态恰为 kDone，不能只测试该位。
constexpr std::uint32_t kBusy = 1;
constexpr std::uint32_t kDone = 2;
constexpr std::uint32_t kFault = 4;
constexpr std::uint32_t kStartCommand = 1;
constexpr std::uint32_t kClearCommand = 2;
// 一组为一个接收机的一个时刻，含 3 天线 × 30 子载波 × 幅相两字。
constexpr unsigned kWordsPerGroup = 180;
constexpr unsigned kGroupsPerWindow = 60;
using Clock = std::chrono::steady_clock;

std::uint64_t ns() {
	return std::chrono::duration_cast<std::chrono::nanoseconds>(Clock::now().time_since_epoch()).count();
}

void require(bool v, const char* message) {
	if (!v)
		throw std::runtime_error(message);
}

void barrier() {
	std::atomic_thread_fence(std::memory_order_seq_cst);
}

// 转换与重排只处理 CPU 拥有值；非法数值在设备提交之前拒绝。
bool pack_input(
	const RawCsi& raw, bool streaming, std::array<std::uint32_t, kComplexCount * 2>& words, bool supported) {
	for (std::size_t i = 0; i < raw.size(); ++i)
		for (unsigned c = 0; c < 2; ++c) {
			const auto source = streaming ? raw_index(i / 1800, (i % 90) / 30, i % 30, (i / 90) % 20) : i;
			const double v = c ? raw[source].imag() : raw[source].real();
			require(std::isfinite(v), "Non-finite raw CSI");
			const float f = float(v);
			std::uint32_t u;
			std::memcpy(&u, &f, 4);
			words[2 * i + c] = u;
			const unsigned exponent = (u >> 23) & 255;
			if ((v != 0 && exponent == 0) || exponent >= 253)
				supported = false;
		}
	return supported;
}

// 只消费已经完整发布的 90 点；相邻两次 FIFO 读取分别为幅度和相位。
void read_polar_group(volatile std::uint32_t* csr, PolarWindow& polar, unsigned r, unsigned t) {
	barrier();
	for (unsigned a = 0; a < 3; ++a)
		for (unsigned n = 0; n < 30; ++n) {
			auto& p = polar[raw_index(r, a, n, t)];
			const auto m = csr[kOutputFifoWord];
			const auto angle = csr[kOutputFifoWord];
			std::memcpy(&p.magnitude, &m, 4);
			p.angle = std::int32_t(angle);
		}
	barrier();
}

}

PlPreprocess::PlPreprocess(const std::string& profile) {
	streaming_ = profile == "probe-free-drain-overlay-csi-v3";
	require(streaming_ || profile == "probe-free-drain-overlay-csi-v2",
		"CSI mapping requires matching qualified hardware profile");
	fd_ = ::open("/dev/mem", O_RDWR | O_SYNC | O_CLOEXEC);
	require(fd_ >= 0, "Cannot open CSI GP mapping");
	try {
		struct stat st{};
		require(::fstat(fd_, &st) == 0 && S_ISCHR(st.st_mode),
			"CSI mapping requires physical memory character device");
		mapping_ = ::mmap(nullptr, 4096, PROT_READ | PROT_WRITE, MAP_SHARED, fd_, 0x400b3000);
		require(mapping_ != MAP_FAILED, "Cannot map CSI GP page");
		csr_ = static_cast<volatile std::uint32_t*>(mapping_);
		require(read(kAbi) == (streaming_ ? 0x43534903u : 0x43534902u), "CSI ABI mismatch");
		require((read(kStatus) & (kBusy | kFault)) == 0, "CSI core not idle and healthy");
	} catch (...) {
		if (mapping_ && mapping_ != MAP_FAILED)
			::munmap(mapping_, 4096);
		::close(fd_);
		throw;
	}
}

PlPreprocess::~PlPreprocess() {
	// The core has only internal BRAM. Unmapping a CSR view never frees a DMA
	// buffer or SDK resource; no abort/reset is issued during destruction.
	if (mapping_ && mapping_ != MAP_FAILED)
		::munmap(mapping_, 4096);
	if (fd_ >= 0)
		::close(fd_);
}

std::uint32_t PlPreprocess::read(unsigned off) const {
	barrier();
	auto v = csr_[off / 4];
	barrier();
	return v;
}

void PlPreprocess::write(unsigned off, std::uint32_t v) {
	barrier();
	csr_[off / 4] = v;
	barrier();
}

Tokens PlPreprocess::process(const RawCsi& raw) {
	require(owner_ == std::this_thread::get_id(), "CSI core accessed outside owner thread");
	++metrics_.calls;
	std::array<std::uint32_t, kComplexCount * 2> words{};
	bool supported = !isolated_;
	supported = pack_input(raw, streaming_, words, supported);
	if (!supported) {
		++metrics_.software_fallbacks;
		return preprocess(raw);
	}
	try {
		require((read(kStatus) & (kBusy | kFault)) == 0, "CSI core busy or fault before submission");
		require(tag_ != 0xffffffff, "CSI tag exhausted");
		const auto start = ns();
		write(kCommand, kClearCommand);
		write(kTag, ++tag_);
		// Ordered device stores to a fixed FIFO address. No private SDK pointers,
		// DMA addresses, cache operations or memcpy to MMIO are used.
		barrier();
		for (auto word : words)
			csr_[kInputFifoWord] = word;
		barrier();
		require(read(kInputCount) == words.size(), "CSI input count mismatch");
		// Small bounded transport/BRAM sentinel check, outside the NPU path.
		for (unsigned at : {0u, 1u, 5399u, 5400u, 10798u, 10799u}) {
			write(kSentinelAddress, at);
			const auto got = read(kSentinelData);
			if (got != words[at])
				throw std::runtime_error("CSI BRAM input mismatch word=" + std::to_string(at) +
					" expected=" + std::to_string(words[at]) + " actual=" + std::to_string(got));
		}
		const auto previous = read(kCompletionCount);
		write(kCommand, kStartCommand);
		const auto sent = ns();
		const auto deadline = Clock::now() + std::chrono::milliseconds(200);
		if (streaming_) {
			PolarWindow polar{};
			Tokens output{};
			unsigned boundaries = 0;
			bool exact_fallback = false;
			std::uint64_t waiting = 0;
			std::uint64_t downloading = 0;
			std::uint64_t finishing = 0;
			for (unsigned group = 0; group < kGroupsPerWindow; ++group) {
				const auto before_wait = ns();
				for (;;) {
					const auto status = read(kStatus);
					if (status & kFault)
						throw std::runtime_error(
							"CSI stream fault reason=" + std::to_string(read(kFaultReason)) +
							" sample_word=" + std::to_string(read(kFaultSample)));
					const auto published = read(kPublishedWords);
					require(published <= words.size() && published % kWordsPerGroup == 0,
						"CSI partial/invalid published group");
					if (published >= (group + 1) * kWordsPerGroup)
						break;
					require(Clock::now() < deadline, "CSI stream deadline: isolate core, no retry");
					std::this_thread::sleep_for(std::chrono::microseconds(20));
				}
				if (read(kStatus) & kBusy)
					++metrics_.groups_read_while_busy;
				++metrics_.streamed_groups;
				const auto ready = ns();
				waiting += ready - before_wait;
				const unsigned r = group / 20;
				const unsigned t = group % 20;
				read_polar_group(csr_, polar, r, t);
				const auto downloaded = ns();
				downloading += downloaded - ready;
				if (!exact_fallback)
					exact_fallback = !finish_polar_group(raw, polar, r, t, output, boundaries);
				finishing += ns() - downloaded;
			}
			// A ready group is not a whole-window completion proof. Verify the final
			// status/tag/count before exposing any tensor or doing a full PS fallback.
			require(read(kStatus) == kDone && read(kCompletedTag) == tag_ &&
					read(kCompletionCount) == previous + 1 && read(kOutputCount) == words.size(),
				"CSI stream final completion mismatch");
			const auto cycles = read(kComputeCycles);
			if (exact_fallback) {
				++metrics_.boundary_window_fallbacks;
				const auto began = ns();
				output = preprocess(raw);
				finishing += ns() - began;
			}
			metrics_.upload_ns += sent - start;
			metrics_.wait_ns += waiting;
			metrics_.download_ns += downloading;
			metrics_.finish_ns += finishing;
			metrics_.compute_cycles += cycles;
			metrics_.boundary_fallbacks += boundaries;
			return output;
		}
		std::this_thread::sleep_for(std::chrono::milliseconds(1));
		for (;;) {
			const auto status = read(kStatus);
			if (status & kFault)
				throw std::runtime_error("CSI hardware fault reason=" + std::to_string(read(kFaultReason)) +
					" sample_word=" + std::to_string(read(kFaultSample)) + " re=" +
					std::to_string(read(kFaultReal)) + " im=" + std::to_string(read(kFaultImaginary)));
			if (status == kDone)
				break;
			require(Clock::now() < deadline, "CSI deadline: isolate core, no retry");
			std::this_thread::sleep_for(std::chrono::microseconds(100));
		}
		require(read(kCompletedTag) == tag_ && read(kCompletionCount) == previous + 1,
			"CSI completion identity mismatch");
		const auto cycles = read(kComputeCycles);
		const auto ready = ns();
		PolarWindow polar{};
		barrier();
		for (auto& p : polar) {
			const auto m = csr_[kOutputFifoWord];
			const auto a = csr_[kOutputFifoWord];
			std::memcpy(&p.magnitude, &m, 4);
			p.angle = std::int32_t(a);
		}
		barrier();
		require(read(kOutputCount) == words.size() && read(kStatus) == kDone && read(kCompletedTag) == tag_,
			"CSI result read count/identity mismatch");
		const auto downloaded = ns();
		unsigned boundaries = 0;
		auto output = finish_polar(raw, polar, &boundaries);
		const auto finished = ns();
		metrics_.upload_ns += sent - start;
		metrics_.wait_ns += ready - sent;
		metrics_.download_ns += downloaded - ready;
		metrics_.finish_ns += finished - downloaded;
		metrics_.compute_cycles += cycles;
		metrics_.boundary_fallbacks += boundaries;
		return output;
	} catch (const std::exception& e) {
		// Independent GP-only core: permanently disable this backend for the run.
		// Future inference uses PS. Never restart a failed NPU or touch its memory.
		isolated_ = true;
		fault_ = e.what();
		++metrics_.hardware_faults;
		++metrics_.software_fallbacks;
		return preprocess(raw);
	}
}
}
