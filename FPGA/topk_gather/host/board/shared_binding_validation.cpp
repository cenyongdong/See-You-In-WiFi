// Exercise the exact shared-session upload checker on a software-only device.
#include "shared_npu_session.hpp"
#include <filesystem>
#include <fstream>
#include <iostream>
#include <memory>

int main(int argc, char** argv) {
    if (argc != 2) return 2;
    using namespace icraft::xrt;
    namespace xir = icraft::xir;
    using topk::board::Json;
    const std::filesystem::path root(argv[1]);
    Json plan;
    std::ifstream(root / "plan.json") >> plan;
    std::map<std::string, xir::Network> graphs;
    for (const auto& name : {"model", "rank_A", "rank_B"}) {
        const auto stem = std::string(name) == "model" ? "model" : "candidate";
        auto network = xir::Network::CreateFromJsonFile((root / (std::string(stem) + ".json")).string());
        network.loadParamsFromFile((root / (std::string(stem) + ".raw")).string());
        graphs.emplace(name, network);
    }
    auto device = Device::Open("mock://zg330"); // Literal mock; no hardware URL argument exists.
    auto region = device.defaultMemRegion();
    topk::board::Allocations allocations;
    std::vector<std::unique_ptr<topk::board::SharedNpuSession>> sessions;
    int result = 0;
    try {
        for (auto item = plan.at("allocations").begin(); item != plan.at("allocations").end(); ++item)
            allocations[item.key()] = region.malloc(item.value().get<std::uint64_t>(), false, 4096);
        Json report = Json::array();
        for (const auto& specification : plan.at("stages")) {
            sessions.push_back(std::make_unique<topk::board::SharedNpuSession>());
            report.push_back(sessions.back()->initialize(graphs.at(specification.at("graph").get<std::string>()),
                             specification, allocations, device, root / "mock-uploads",
                             topk::board::UploadCheck::MockMetadata));
        }
        std::ofstream(root / "mock-bindings.json") << report.dump(2) << '\n';
        std::cout << "SHARED_BINDING_PASS stages=" << report.size() << " hardware_opens=0\n";
    } catch (const std::exception& error) {
        std::cerr << error.what() << '\n';
        result = 1;
    }
    for (auto& session : sessions) session->release();
    sessions.clear();
    for (auto& item : allocations) item.second.free();
    if (!region.memManager().getAllMemChunk().empty()) result = 1;
    Device::Close(device);
    return result;
}
