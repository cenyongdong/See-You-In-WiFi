#pragma once
#include "types.hpp"
#include <filesystem>
#include <functional>
#include <memory>

namespace icraft::xrt {
class Device;
}

namespace pose180_pipeline {
struct Config {
	std::filesystem::path graph, raw, evidence;
	// Runs on the same SDK thread after apply. HDMI must allocate on this Device.
	std::function<void(const icraft::xrt::Device&)> on_device_ready;
	// Best-effort control-plane notification only; must not call SDK or free IO.
	std::function<void(const char*)> on_release_blocked;
	std::function<pose_v1::Tokens(const pose_v1::RawCsi&)> preprocess;
};

// Construct, infer and destroy on one thread. Exactly one Runtime owns the SDK
// in this process. A failure permanently disables inference; no implicit reset,
// reopening, reread, retry, file deployment or BOOT operation is performed.
class Runtime {
public:
	explicit Runtime(const Config&);
	~Runtime();
	Runtime(const Runtime&) = delete;
	Runtime& operator=(const Runtime&) = delete;
	Runtime(Runtime&&) = delete;
	Runtime& operator=(Runtime&&) = delete;

	// Writes into an already acquired output pool slot. Normal frames do not
	// create per-frame files. The caller must retain full input/scores/poses
	// before validation/display: strict validation archives them; the resident
	// demo retains owned values in its bounded diagnostic ring and recorder.
	// Nonfinite first outputs are preserved and returned with finite_outputs
	// false, while permanently stopping this Runtime, so the archive can finish.
	void infer(const Window&, Result&);
	double init_ms() const;
	bool release_permitted() const noexcept;
	void retain_if_unproved() const noexcept;

private:
	struct Impl;
	std::unique_ptr<Impl> impl_;
};

// Declare AFTER the Runtime and its dependent HDMI owner, so exceptional stack
// unwinding checks NPU ownership before either owner can begin destruction.
struct RuntimeShutdownGuard {
	const std::unique_ptr<Runtime>& runtime;

	~RuntimeShutdownGuard() {
		if (runtime)
			runtime->retain_if_unproved();
	}
};
} // namespace pose180_pipeline
