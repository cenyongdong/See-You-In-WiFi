#pragma once
#include <icraft-backends/zg330backend/zg330backend.h>
#include <icraft-xir/utils/json.hpp>
#include <icraft-xrt/core/session.h>
#include <map>
#include <filesystem>
#include <string>
#include <vector>

namespace topk::board {
using Json = nlohmann::json;
using Allocations = std::map<std::string, icraft::xrt::MemChunk>;

// Own this object before initialize(). The enclosing device owner must retain it
// on any hardware exception; release() requires proven completion of all work.
class SharedNpuSession {
    icraft::xir::Network graph_;
    icraft::xir::NetworkView view_;
    icraft::xrt::zg330::ZG330Backend backend_;
    icraft::xrt::Session session_;
    std::vector<icraft::xrt::Tensor> inputs_, outputs_;
    uint32_t final_count_ = 0;
    std::string name_;
    std::vector<char> readback_; // Retained if a synchronous transfer throws.
    bool operation_completed_ = true;
    Json verify_upload(const icraft::xrt::Device& device, const std::filesystem::path& directory);
public:
    Json initialize(const icraft::xir::Network& graph, const Json& specification,
                    Allocations& allocations, const icraft::xrt::Device& device,
                    const std::filesystem::path& evidence_directory);
    double forward(icraft::xrt::Device& device);
    bool operation_completed() const noexcept { return operation_completed_; }
    void release();
};

// These relative addresses are qualified for the checked 25122301 FPGA image.
// They supplement the native final-output callback and applied sync metadata.
// They are not a replacement for either of those completion contracts.
void check_ddr_idle(const icraft::xrt::Device& device);
} // namespace topk::board
