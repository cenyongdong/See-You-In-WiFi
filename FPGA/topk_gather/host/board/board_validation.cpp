// Finite, supervised validation using the installed public C++ SDK.
// The experiment owns every buffer until hardware completion is reviewed.
// Exceptions during hardware access retain the experiment and exclusive lease.
#include <icraft-backends/zg330backend/zg330backend.h>
#include <icraft-xir/ops/ops.h>
#include <icraft-xir/utils/json.hpp>
#include <icraft-xrt/core/session.h>
#include <icraft-xrt/dev/zg330_device.h>
#include <algorithm>
#include <chrono>
#include <csignal>
#include <filesystem>
#include <fstream>
#include <iostream>
#include <map>
#include <memory>
#include <set>
#include <stdexcept>
#include <string>
#include <thread>
#include <vector>
#include <fcntl.h>
#include <sys/file.h>
#include <unistd.h>

namespace {
namespace fs = std::filesystem;
namespace xir = icraft::xir;
using namespace icraft::xrt;
using Json = nlohmann::json;
using Clock = std::chrono::steady_clock;
using Bytes = std::vector<char>;
volatile std::sig_atomic_t stop_requested = 0;

void require(bool condition, const std::string& message) {
    if (!condition) throw std::runtime_error(message);
}

Bytes read_bytes(const fs::path& path) {
    std::ifstream stream(path, std::ios::binary);
    require(bool(stream), "Cannot read " + path.string());
    return Bytes(std::istreambuf_iterator<char>(stream), {});
}

Json read_json(const fs::path& path) {
    std::ifstream stream(path);
    require(bool(stream), "Cannot read " + path.string());
    Json result;
    stream >> result;
    return result;
}

void save_bytes(const fs::path& path, const Bytes& bytes) {
    std::ofstream stream(path, std::ios::binary);
    stream.write(bytes.data(), static_cast<std::streamsize>(bytes.size()));
    stream.flush();
    require(bool(stream), "Cannot preserve " + path.string());
}

void save_json(const fs::path& path, const Json& value) {
    const auto text = value.dump(2) + "\n";
    auto temporary = path;
    temporary += ".tmp";
    save_bytes(temporary, Bytes(text.begin(), text.end()));
    fs::rename(temporary, path);
}

std::string current_boot() {
    std::ifstream stream("/proc/sys/kernel/random/boot_id");
    std::string value;
    stream >> value;
    require(!value.empty(), "Missing boot identity");
    return value;
}

bool has_device_owner() {
    for (const auto& entry : fs::directory_iterator("/proc")) {
        const auto name = entry.path().filename().string();
        if (name.empty() || name.find_first_not_of("0123456789") != std::string::npos) continue;
        std::error_code error;
        for (const auto& fd : fs::directory_iterator(entry.path() / "fd", error)) {
            const auto target = fs::read_symlink(fd.path(), error).string();
            if (error) { error.clear(); continue; }
            for (const auto* prefix : {"/dev/axi", "/dev/udmabuf", "/dev/u-dma", "/dev/video", "/dev/mem"})
                if (target.rfind(prefix, 0) == 0) return true;
        }
    }
    return false;
}

class Lease {
    int fd_ = -1;
public:
    Lease() {
        fd_ = ::open("/run/pose180-resident.lock", O_RDWR | O_CREAT | O_CLOEXEC, 0600);
        require(fd_ >= 0, "Cannot open global lease");
        if (::flock(fd_, LOCK_EX | LOCK_NB) != 0) {
            ::close(fd_);
            fd_ = -1;
            throw std::runtime_error("Global lease already owned");
        }
    }
    ~Lease() { if (fd_ >= 0) ::close(fd_); }
    Lease(const Lease&) = delete;
    Lease& operator=(const Lease&) = delete;
};

struct TestCase {
    std::string name;
    std::vector<Bytes> inputs, expected;
};

class Experiment {
    fs::path root_;
    Json manifest_;
    std::string boot_;
    Device device_;
    MemRegion region_;
    MemChunk scratch_;
    xir::Network network_;
    xir::NetworkView view_;
    zg330::ZG330Backend backend_;
    Session session_;
    std::map<int64_t, MemChunk> chunks_;
    std::vector<Tensor> inputs_, outputs_;
    std::vector<TestCase> cases_;
    std::vector<Bytes> actual_outputs_;
    Bytes dma_original_, dma_pattern_, dma_expected_, dma_actual_;
    std::vector<int64_t> hardops_;
    const std::vector<int64_t> input_ids_{0, 1, 2, 3}, output_ids_{167, 169, 171};
    std::size_t completed_ = 0, forwards_ = 0, initial_allocations_ = 0;
    uint32_t final_count_ = 0;
    bool device_closed_ = false;

    void gate(const std::string& name) {
        const auto path = root_ / name;
        while (!fs::exists(path)) std::this_thread::sleep_for(std::chrono::milliseconds(200));
        const auto request = read_json(path);
        require(request.at("boot_id") == boot_ && request.at("completed") == completed_ &&
                request.at("hardware_reviewed") == true, "Controller gate identity differs");
        require(!stop_requested || name == "release.json", "Stop requested; no new hardware work");
    }

    void hardware_status(const std::string& label) {
        std::cout << "HARDWARE_STATUS_BEGIN " << label << std::endl;
        for (int level : {1, 2, 3, 4, 5}) {
            std::cout << "STATUS_LEVEL " << level << std::endl;
            device_.showStatus(level);
        }
        std::cout << "HARDWARE_STATUS_END " << label << std::endl;
    }

    void load_cases() {
        network_ = xir::Network::CreateFromJsonFile((root_ / "candidate.json").string());
        network_.loadParamsFromFile((root_ / "candidate.raw").string());
        for (const auto& op : network_->ops) if (op.is<xir::HardOp>()) hardops_.push_back(op->op_id);
        require(network_->ops.size() == 56 && hardops_.size() == 54, "Candidate graph identity differs");
        view_ = network_.view(hardops_);
        std::vector<int64_t> actual_inputs, actual_outputs;
        for (const auto& v : view_.inputs()) actual_inputs.push_back(v->v_id);
        for (const auto& v : view_.outputs()) actual_outputs.push_back(v->v_id);
        require(actual_inputs == input_ids_ && actual_outputs == output_ids_, "Candidate port order differs");
        require(manifest_.at("cases").size() == 7, "Finite case budget differs");
        for (const auto& row : manifest_.at("cases")) {
            TestCase test;
            test.name = row.at("name").get<std::string>();
            require(test.name.find_first_not_of("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_") ==
                    std::string::npos, "Unsafe case path");
            for (auto id : input_ids_) {
                auto bytes = read_bytes(root_ / test.name / ("input_" + std::to_string(id) + ".bin"));
                require(bytes.size() == network_.getValueById(id).storageBytes(), "Input extent differs");
                test.inputs.push_back(std::move(bytes));
            }
            for (auto id : output_ids_) {
                auto bytes = read_bytes(root_ / test.name / ("expected_" + std::to_string(id) + ".bin"));
                require(bytes.size() == network_.getValueById(id).storageBytes(), "Oracle extent differs");
                test.expected.push_back(std::move(bytes));
            }
            cases_.push_back(std::move(test));
        }
    }

    void check_dma() {
        report("dma_running");
        scratch_ = region_.malloc(30400, false, 4096);
        Json results = Json::array();
        bool equal = true;
        for (std::size_t size : {64, 768, 30272}) {
            dma_original_.assign(30400, static_cast<char>(0xa5));
            dma_pattern_.resize(size);
            for (std::size_t i = 0; i < size; ++i) dma_pattern_[i] = static_cast<char>((i * 73 + size / 64) & 255);
            dma_expected_ = dma_original_;
            std::copy(dma_pattern_.begin(), dma_pattern_.end(), dma_expected_.begin() + 64);
            dma_actual_.resize(30400);
            scratch_.write(0, dma_original_.data(), dma_original_.size());
            scratch_.write(64, dma_pattern_.data(), dma_pattern_.size());
            scratch_.read(dma_actual_.data(), 0, dma_actual_.size());
            const auto stem = "dma_" + std::to_string(size);
            save_bytes(root_ / (stem + ".actual.bin"), dma_actual_);
            save_bytes(root_ / (stem + ".expected.bin"), dma_expected_);
            equal = dma_actual_ == dma_expected_;
            results.push_back({{"bytes", size}, {"first_read_equal", equal},
                               {"guard_lines_equal", std::equal(dma_actual_.begin(), dma_actual_.begin()+64, dma_expected_.begin()) &&
                                   std::equal(dma_actual_.begin()+64+size, dma_actual_.end(), dma_expected_.begin()+64+size)}});
            save_json(root_ / "dma.json", results);
            if (!equal) break; // Never reread a failed transfer to make it pass.
        }
        hardware_status("after_dma");
        release_review_available = true;
        report("dma_review", {{"dma", results}});
        require(equal, "First DMA read differs; no deployment or retry");
    }

    void deploy() {
        gate("deploy.json");
        report("deploying");
        release_review_available = false;
        backend_ = Backend::Create<zg330::ZG330Backend>(view_, device_);
        auto bind = [&](const xir::Value& value) {
            auto& chunk = chunks_[value->v_id];
            chunk = region_.malloc((value.storageBytes() + 63) / 64 * 64, false, 4096);
            backend_.userConnectNetwork(chunk, value->v_id);
        };
        for (const auto& value : view_.inputs()) bind(value);
        for (const auto& value : view_.outputs()) bind(value);
        session_ = Session::CreateWithBackends(view_, {backend_});
        session_.apply();
        require(backend_.precheck(), "Uploaded instruction/parameter precheck failed");
        Json bindings = Json::array(), groups = Json::array();
        bool direct_all = true;
        for (const auto& item : chunks_) {
            const auto memory = backend_->forward_info->memchunk_map.at(item.first);
            const auto value = backend_->value_info.at(item.first);
            const auto address = item.second->begin.addr();
            const bool direct = memory->user_used && memory->staged_chunk.empty() && !value->is_host &&
                !value->is_ocm && memory->memChunk->begin.addr() == address && value->phy_addr == address;
            bindings.push_back({{"value_id", item.first}, {"address", address},
                                {"bytes", item.second->byte_size}, {"direct", direct}});
            direct_all = direct_all && direct;
        }
        std::set<int64_t> members;
        std::map<int, int> intervals;
        for (const auto& item : session_.backendBindings()) {
            require(item.second.is<zg330::ZG330Backend>(), "Unexpected Host compute binding");
            const auto info = backend_->forward_info->hardop_map.at(item.first);
            auto covered = info->merge_from;
            if (covered.empty()) covered.push_back(item.first);
            for (auto id : covered) require(members.insert(id).second, "Repeated HardOp member");
            require(intervals.emplace(info->sync_idx).second, "Repeated sync interval");
            groups.push_back({{"op_id", item.first}, {"sync", {info->sync_idx.first, info->sync_idx.second}}, {"members", covered}});
        }
        require(members == std::set<int64_t>(hardops_.begin(), hardops_.end()), "HardOp coverage differs");
        for (const auto& interval : intervals) {
            require(interval.first >= 0 && static_cast<uint32_t>(interval.first) == final_count_ && interval.second > 0,
                    "Sync intervals are not contiguous");
            final_count_ += static_cast<uint32_t>(interval.second);
        }
        save_json(root_ / "binding.json", {{"bindings", bindings}, {"groups", groups}, {"final_count", final_count_}});
        hardware_status("after_deploy");
        release_review_available = true;
        require(direct_all && final_count_ > 0, "Candidate ports did not bind directly");
        for (auto id : input_ids_) inputs_.emplace_back(network_.getValueById(id).tensorType(), chunks_.at(id));
        report("ready_for_case", {{"next_case", 0}});
    }

    void execute(TestCase& test) {
        gate("continue_" + std::to_string(completed_) + ".json");
        report("case_running", {{"case", test.name}});
        release_review_available = false;
        for (std::size_t i = 0; i < inputs_.size(); ++i) inputs_[i].write(0, test.inputs[i].data(), test.inputs[i].size());
        // reset(1) clears FPGA status only after preceding hardware completion review.
        device_.reset(1);
        require(device_.cast<ZG330Device>().layerCount() == 0, "Initial layer count did not clear");
        const auto start = Clock::now();
        ++forwards_;
        outputs_ = session_.forward(inputs_);
        for (const auto& tensor : outputs_) require(tensor.waitForReady(std::chrono::seconds(10)), "Native completion timed out");
        const auto compute_ms = std::chrono::duration<double, std::milli>(Clock::now() - start).count();
        const auto count = device_.cast<ZG330Device>().layerCount();
        require(count == final_count_ && outputs_.size() == output_ids_.size(), "Final sync count/output extent differs");
        const auto read_start = Clock::now();
        actual_outputs_.resize(outputs_.size());
        Json comparisons = Json::array();
        bool passed = true;
        for (std::size_t i = 0; i < outputs_.size(); ++i) {
            const auto id = output_ids_[i];
            auto& actual = actual_outputs_[i];
            actual.resize(test.expected[i].size());
            outputs_[i].read(actual.data(), 0, actual.size());
            save_bytes(root_ / test.name / ("actual_" + std::to_string(id) + ".bin"), actual);
            const bool equal = actual == test.expected[i];
            const bool direct = outputs_[i].data().addr() == chunks_.at(id)->begin.addr();
            comparisons.push_back({{"value_id", id}, {"bytes", actual.size()}, {"bitwise_equal", equal}, {"direct_address", direct}});
            passed = passed && equal && direct;
        }
        const auto read_ms = std::chrono::duration<double, std::milli>(Clock::now() - read_start).count();
        Json result{{"case", test.name}, {"comparisons", comparisons}, {"forward_and_wait_ms", compute_ms},
                    {"readback_ms", read_ms}, {"layer_count", count}, {"passed", passed}};
        save_json(root_ / test.name / "result.json", result);
        ++completed_;
        hardware_status("after_" + test.name);
        release_review_available = true;
        report("case_review", {{"result", result}});
        require(passed, "First outputs differ; no next case or retry");
    }

public:
    bool hardware_started = false;
    bool release_review_available = false;
    std::string stage = "before_sdk";
    Experiment(fs::path root, Json manifest) : root_(std::move(root)), manifest_(std::move(manifest)),
        boot_(manifest_.at("boot_id").get<std::string>()) {}

    ~Experiment() {
        // Last resort: even a diagnostic/unknown exception must not destroy live handles.
        if (hardware_started && !device_closed_) {
            static constexpr char message[] = "SDK_RELEASE_BLOCKED: retaining experiment and lease\n";
            const auto written = ::write(STDERR_FILENO, message, sizeof(message) - 1);
            (void)written;
            for (;;) ::sleep(1);
        }
    }

    void report(const std::string& phase, Json fields = Json::object()) {
        stage = phase;
        fields["phase"] = phase;
        fields["pid"] = ::getpid();
        fields["boot_id"] = boot_;
        fields["completed"] = completed_;
        fields["forward_calls"] = forwards_;
        fields["hardware_started"] = hardware_started;
        fields["release_review_available"] = release_review_available;
        save_json(root_ / "state.json", fields);
        std::cout << fields.dump() << std::endl;
    }

    void run() {
        load_cases(); // Parse all files and validate their extents before device access.
        report("opening_sdk");
        hardware_started = true;
        save_json(root_ / "sdk-attempt.json", {{"opens", 1}, {"maximum_forward_calls", 7}, {"boot_id", boot_}});
        device_ = Device::Open("axi://zg330aiu?npu=0x40000000&dma=0x80000000");
        device_.setWaitTime(10000);
        const auto version = device_.version();
        require(version.at("device") == "25122301" && version.at("icore") == "FMSHZGV3TECH-AID - 24160628",
                "Device/icore identity differs");
        region_ = device_.defaultMemRegion();
        initial_allocations_ = region_.memManager().getAllMemChunk().size();
        report("sdk_opened", {{"version", version}, {"initial_allocations", initial_allocations_}});
        hardware_status("before_dma");
        check_dma();
        deploy();
        for (auto& test : cases_) execute(test);
        finish();
    }

    void finish() {
        report("release_review");
        gate("release.json");
        report("releasing");
        release_review_available = false;
        outputs_.clear();
        inputs_.clear();
        session_ = {};
        if (backend_.defined()) backend_.deinit();
        backend_ = {};
        for (auto& item : chunks_) item.second.free();
        chunks_.clear();
        if (scratch_.defined()) scratch_.free();
        const auto allocations = region_.memManager().getAllMemChunk().size();
        require(allocations == initial_allocations_, "SDK allocations remain after cleanup");
        Device::Close(device_);
        device_closed_ = true;
        report("complete", {{"allocation_count_after", allocations}, {"sdk_opens", 1}, {"boot_writes", 0}, {"reboots", 0}});
    }
};
} // namespace

int main(int argc, char** argv) {
    if (argc != 2) { std::cerr << "Usage: topk_board_validation <isolated-directory>\n"; return 2; }
    for (int signal : {SIGINT, SIGTERM, SIGHUP}) std::signal(signal, [](int) { stop_requested = 1; });
    const auto root = fs::canonical(argv[1]);
    const auto manifest = read_json(root / "manifest.json");
    require(manifest.at("boot_id") == current_boot() && !has_device_owner(), "Boot/device ownership differs");
    Lease lease;
    require(!has_device_owner() && !fs::exists("/run/pose180-resident.active.json"), "Existing startup reservation");
    require(!fs::exists(root / "sdk-attempt.json"), "This experiment already attempted SDK startup");
    save_json("/run/pose180-resident.active.json", {{"boot_id", current_boot()}, {"run", root.string()}});
    auto experiment = std::make_unique<Experiment>(root, manifest);
    try {
        experiment->run();
        return 0;
    } catch (...) {
        const auto prior = experiment->stage;
        std::string message = "Non-standard SDK exception";
        try { throw; } catch (const std::exception& error) { message = error.what(); } catch (...) {}
        std::cerr << "EXPERIMENT_ERROR " << message << std::endl;
        experiment->report("retained_after_error", {{"error", message}, {"prior_stage", prior}});
        if (!experiment->hardware_started) {
            fs::remove("/run/pose180-resident.active.json");
            experiment->report("failed_before_sdk", {{"sdk_opens", 0}});
            return 1;
        }
        // Keep every SDK object and buffer, including on a failed synchronous call.
        // A controller release is accepted only after a normal completion boundary.
        for (;;) {
            if (experiment->release_review_available && fs::exists(root / "release.json")) {
                try { experiment->finish(); return 1; }
                catch (const std::exception& cleanup) {
                    experiment->release_review_available = false;
                    experiment->report("retained_after_cleanup_error", {{"error", cleanup.what()}});
                }
            }
            std::this_thread::sleep_for(std::chrono::seconds(1));
        }
    }
}
