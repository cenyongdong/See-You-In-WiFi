// Host-only diagnostic: load the original graph and inspect public Params data.
// No device, backend, session, register access, or inference is created.
#include <icraft-xir/core/network.h>
#include <icraft-xir/ops/hard_op.h>
#include <icraft-xir/utils/json.hpp>
#include <iostream>
#include <stdexcept>

int main(int argc, char** argv) {
    try {
        if (argc != 3) throw std::runtime_error("Usage: parameter_layout_probe <model.json> <model.raw>");
        using namespace icraft::xir;
        auto graph = Network::CreateFromJsonFile(argv[1]);
        graph.loadParamsFromFile(argv[2]);
        auto op = graph.getOpById(7612).cast<HardOp>();
        nlohmann::json rows = nlohmann::json::array();
        std::uintptr_t preceding_end = 0;
        for (const auto& param : op->params) {
            const auto data = param.data<char>();
            const auto address = reinterpret_cast<std::uintptr_t>(data.get());
            const auto bytes = param.storageBytes();
            if (!data || !param->mtype.is<ChunkMem>()) throw std::runtime_error("Unexpected parameter storage");
            const auto memory = param->mtype.cast<ChunkMem>();
            rows.push_back({{"param_id", param->v_id}, {"bytes", bytes}, {"host_address", address},
                            {"chunk_id", memory->chunk_id}, {"offset", memory->offset},
                            {"adjacent_to_previous", preceding_end == address}});
            preceding_end = address + bytes;
        }
        std::cout << nlohmann::json({{"op_id", 7612}, {"params", rows}, {"hardware_opens", 0}}).dump(2) << '\n';
        return 0;
    } catch (const std::exception& error) {
        std::cerr << error.what() << '\n';
        return 1;
    }
}
