// HDMI资源在SDK所属主线程持有；显示worker仍保持SDK无关。
#pragma once
#include "hdmi_format.hpp"
#include <icraft-xrt/core/device.h>
#include <cstdint>
#include <filesystem>
#include <memory>
#include <streambuf>
#include <vector>

namespace pose::hdmi {
struct Snapshot {
	uint32_t status, stopped, address, accepted, faults;

	bool idle() const {
		return status & 1;
	}
};

class Output {
public:
	Output(const icraft::xrt::Device& device, const std::filesystem::path& evidence,
		std::streambuf* asynchronous_log = nullptr);
	~Output();
	Output(const Output&) = delete;
	Output& operator=(const Output&) = delete;
	// 只在未运行时核对两块真实分配的完整SDK写／读，不作为PL读完成证明。
	void verifyMemory();
	// Same owner thread only. begin writes once and acknowledges START/FLIP;
	// poll performs one snapshot and never reissues the frame command.
	void begin_show(const std::vector<uint8_t>& rgb565, uint32_t frameId);
	bool poll_show();
	void show_overlay(const std::vector<uint32_t>& commands, uint32_t frameId, double prepare_ms);
	bool pending() const;
	void show(const std::vector<uint8_t>& rgb565, uint32_t frameId);
	Snapshot observe();
	// 必须取得新响应代数及对应stopped ID后，才显式释放两帧。
	void close();

private:
	struct Impl;
	std::unique_ptr<Impl> impl_;
};
}
