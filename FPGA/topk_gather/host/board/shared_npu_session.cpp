#include "shared_npu_session.hpp"
#include "parameter_image.hpp"
#include <icraft-xrt/dev/zg330_device.h>
#include <chrono>
#include <fstream>
#include <set>
#include <stdexcept>

namespace topk::board {
using namespace icraft::xrt;
namespace {
void require(bool condition, const std::string& message) {
    if (!condition) throw std::runtime_error(message);
}
}

void check_ddr_idle(const Device& device) {
    for (uint64_t offset : {0x08, 0x4c, 0x50, 0x20, 0x42094, 0x44094}) {
        const auto value = device.readReg(offset, true);
        require(value == 0, "DDR/handshake/instruction-DMA not idle at relative offset " +
                std::to_string(offset) + ": " + std::to_string(value));
    }
    // The installed AXIZG330AIPLDDRMemRegionNode DMA implementation polls this
    // relative register: bits 0/2 are busy, 1/3 are errors. It is not AXI DMA's
    // usual DMASR layout. Qualified against the actual 3.39.0 plugin and image.
    require((device.readReg(0x40584, true) & 0xf) == 0, "Host/PL DDR DMA is busy or reports an error");
}

Json SharedNpuSession::verify_upload(const Device& device, const std::filesystem::path& directory) {
    std::filesystem::create_directories(directory);
    Json report = Json::array();
    auto verify = [&](const zg330::HardOpInfo& info, bool weights) {
        const auto bytes = weights ? info->weights_size : info->instr_size;
        if (!bytes) return;
        const auto& params = weights ? info->net_hardop->params : info->net_hardop->instr;
        require(!params.empty(), name_ + ": missing applied parameters");
        const auto kind = weights ? "weights" : "instructions";
        const auto id = info->net_hardop->op_id;
        const auto physical = weights ? info->weight_phy_addr : info->instr_phy_addr;
        const auto segment_type = weights ? zg330::SegmentType::WEIGHT : zg330::SegmentType::INSTR;
        auto segment = backend_->phy_segment_map.at(segment_type);
        const auto chunk = segment.getSingleMemChunk()->memChunk;
        const auto base = chunk->begin.addr();
        require(physical >= base && physical - base <= chunk->byte_size &&
                bytes <= chunk->byte_size - (physical - base), name_ + ": readback exceeds segment");
        std::vector<ParameterPart> parts;
        Json layout = Json::array();
        std::uint64_t cursor = 0;
        for (const auto& param : params) {
            const auto data = param.data<char>();
            const auto extent = param.storageBytes();
            require(bool(data), name_ + ": unloaded parameter data");
            // SDK HardOpInfo defines weights_size as the sum of Params sizes.
            // Chunk offsets must agree with that packed layout; host pointers
            // need not be adjacent and are never used beyond their own extent.
            if (weights) {
                require(param->mtype.is<icraft::xir::ChunkMem>(), name_ + ": unsupported weight memory type");
                const auto memory = param->mtype.cast<icraft::xir::ChunkMem>();
                const auto first = params[0]->mtype.cast<icraft::xir::ChunkMem>();
                require(memory->chunk_id == first->chunk_id && memory->offset >= first->offset &&
                        memory->offset - first->offset == cursor, name_ + ": weight chunk layout differs");
            }
            parts.push_back({data.get(), cursor, extent});
            layout.push_back({{"param_id", param->v_id}, {"offset", cursor}, {"bytes", extent},
                              {"host_address", reinterpret_cast<std::uintptr_t>(data.get())}});
            require(cursor <= bytes && extent <= bytes - cursor, name_ + ": parameter extent differs");
            cursor += extent;
        }
        const auto expected = parameter_image(bytes, parts);
        readback_.resize(bytes);
        operation_completed_ = false;
        chunk.read(readback_.data(), physical - base, bytes);
        check_ddr_idle(device);
        operation_completed_ = true;
        const auto filename = std::to_string(id) + "." + kind + ".actual.bin";
        std::ofstream output(directory / filename, std::ios::binary);
        output.write(readback_.data(), static_cast<std::streamsize>(readback_.size()));
        output.close();
        require(bool(output), "Cannot preserve first parameter readback");
        const auto difference = std::mismatch(readback_.begin(), readback_.end(), expected.begin());
        const bool equal = difference.first == readback_.end();
        report.push_back({{"op_id", id}, {"kind", kind}, {"bytes", bytes}, {"physical_address", physical},
                          {"parts", layout}, {"actual_file", filename}, {"bitwise_equal", equal},
                          {"first_difference", equal ? -1 : std::distance(readback_.begin(), difference.first)}});
        std::ofstream metadata(directory / "readback.json");
        metadata << report.dump(2) << '\n';
        metadata.close();
        require(bool(metadata), "Cannot preserve parameter readback metadata");
        if (!equal) {
            std::ofstream reference(directory / (std::to_string(id) + "." + kind + ".expected.bin"), std::ios::binary);
            reference.write(expected.data(), static_cast<std::streamsize>(expected.size()));
            reference.close();
            require(bool(reference), "Cannot preserve expected parameter image");
            throw std::runtime_error(name_ + ": first " + kind + " readback differs at op " + std::to_string(id));
        }
    };
    for (const auto& item : backend_->params_chunk_ids) verify(item.second, true);
    for (const auto& item : session_.backendBindings())
        verify(backend_->forward_info->hardop_map.at(item.first), false);
    return {{"checked_images", report.size()}, {"all_bitwise_equal", true}};
}

Json SharedNpuSession::initialize(const icraft::xir::Network& graph, const Json& specification,
                                 Allocations& allocations, const Device& device,
                                 const std::filesystem::path& evidence_directory) {
    graph_ = graph;
    name_ = specification.at("name").get<std::string>();
    const auto op_ids = specification.at("op_ids").get<std::vector<int64_t>>();
    view_ = graph_.view(op_ids);
    const auto mapping = specification.at("mapping").get<std::map<std::string, std::string>>();
    std::set<int64_t> ports;
    for (const auto& v : view_.inputs()) ports.insert(v->v_id);
    for (const auto& v : view_.outputs()) ports.insert(v->v_id);
    require(ports.size() == mapping.size(), name_ + ": port count differs");
    operation_completed_ = false;
    backend_ = Backend::Create<zg330::ZG330Backend>(view_, device);
    for (auto id : ports) {
        auto& chunk = allocations.at(mapping.at(std::to_string(id)));
        require(chunk->begin.addr() % 4096 == 0 && chunk->byte_size >= graph_.getValueById(id).storageBytes(),
                name_ + ": allocation alignment/extent differs");
        backend_.userConnectNetwork(chunk, id);
    }
    session_ = Session::CreateWithBackends(view_, {backend_});
    session_.apply();
    check_ddr_idle(device);
    operation_completed_ = true;
    const auto upload = verify_upload(device, evidence_directory / name_);
    Json bindings = Json::array(), groups = Json::array();
    for (auto id : ports) {
        const auto key = mapping.at(std::to_string(id));
        const auto& chunk = allocations.at(key);
        const auto memory = backend_->forward_info->memchunk_map.at(id);
        const auto value = backend_->value_info.at(id);
        const bool direct = memory->user_used && memory->staged_chunk.empty() && !value->is_host &&
            !value->is_ocm && memory->memChunk->begin.addr() == chunk->begin.addr() &&
            value->phy_addr == chunk->begin.addr();
        require(direct, name_ + ": port staged or relocated");
        bindings.push_back({{"value_id", id}, {"shared_key", key}, {"address", chunk->begin.addr()},
                            {"allocated_bytes", chunk->byte_size}, {"tensor_bytes", value->byte_size}, {"direct", direct}});
    }
    std::set<int64_t> members;
    std::map<int, int> intervals;
    for (const auto& item : session_.backendBindings()) {
        require(item.second.is<zg330::ZG330Backend>(), name_ + ": unexpected Host compute");
        const auto info = backend_->forward_info->hardop_map.at(item.first);
        auto covered = info->merge_from;
        if (covered.empty()) covered.push_back(item.first);
        for (auto id : covered) require(members.insert(id).second, name_ + ": duplicate HardOp member");
        require(intervals.emplace(info->sync_idx).second, name_ + ": duplicate sync interval");
        groups.push_back({{"op_id", item.first}, {"sync", {info->sync_idx.first, info->sync_idx.second}}, {"members", covered}});
    }
    require(members == std::set<int64_t>(op_ids.begin(), op_ids.end()), name_ + ": HardOp coverage differs");
    for (const auto& interval : intervals) {
        require(interval.first >= 0 && static_cast<uint32_t>(interval.first) == final_count_ && interval.second > 0,
                name_ + ": sync intervals differ");
        final_count_ += static_cast<uint32_t>(interval.second);
    }
    for (const auto& value : view_.inputs())
        inputs_.emplace_back(value.tensorType(), allocations.at(mapping.at(std::to_string(value->v_id))));
    return {{"name", name_}, {"bindings", bindings}, {"groups", groups}, {"final_count", final_count_}, {"upload", upload}};
}

double SharedNpuSession::forward(Device& device) {
    check_ddr_idle(device);
    operation_completed_ = false;
    device.reset(1); // Previous work is complete; this only clears FPGA status.
    require(device.cast<ZG330Device>().layerCount() == 0, name_ + ": sync count did not clear");
    const auto begin = std::chrono::steady_clock::now();
    outputs_ = session_.forward(inputs_);
    require(outputs_.size() == view_.outputs().size(), name_ + ": missing native outputs");
    for (const auto& tensor : outputs_)
        require(tensor.waitForReady(std::chrono::seconds(10)), name_ + ": native final-output callback timed out");
    require(device.cast<ZG330Device>().layerCount() == final_count_, name_ + ": final applied sync count differs");
    check_ddr_idle(device);
    operation_completed_ = true;
    return std::chrono::duration<double, std::milli>(std::chrono::steady_clock::now() - begin).count();
}

void SharedNpuSession::release() {
    outputs_.clear();
    inputs_.clear();
    session_ = {};
    if (backend_.defined()) backend_.deinit();
    backend_ = {};
}
} // namespace topk::board
