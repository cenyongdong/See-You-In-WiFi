// Isolated old-model experiment: three original NPU stages, with either CPU
// TopK/Gather references or two copies of the same runtime-mask NPU candidate.
// Candidate intermediate tensors remain in the shared PL DDR allocations.
#include "shared_npu_session.hpp"
#include <algorithm>
#include <chrono>
#include <cmath>
#include <csignal>
#include <cstring>
#include <filesystem>
#include <fstream>
#include <iostream>
#include <memory>
#include <numeric>
#include <stdexcept>
#include <thread>
#include <fcntl.h>
#include <sys/file.h>
#include <unistd.h>

namespace {
namespace fs = std::filesystem;
namespace xir = icraft::xir;
using namespace icraft::xrt;
using topk::board::Json;
using topk::board::SharedNpuSession;
using Bytes = std::vector<char>;
using Clock = std::chrono::steady_clock;
volatile std::sig_atomic_t stop_requested = 0;

void require(bool condition, const std::string& message) {
    if (!condition) throw std::runtime_error(message);
}
Bytes read_bytes(const fs::path& path) {
    std::ifstream input(path, std::ios::binary);
    require(bool(input), "Cannot read " + path.string());
    return Bytes(std::istreambuf_iterator<char>(input), {});
}
Json read_json(const fs::path& path) {
    std::ifstream input(path);
    require(bool(input), "Cannot read " + path.string());
    Json value;
    input >> value;
    return value;
}
void save_bytes(const fs::path& path, const Bytes& value) {
    std::ofstream output(path, std::ios::binary);
    output.write(value.data(), static_cast<std::streamsize>(value.size()));
    output.flush();
    require(bool(output), "Cannot preserve " + path.string());
}
void save_json(const fs::path& path, const Json& value) {
    const auto text = value.dump(2) + "\n";
    auto temporary = path;
    temporary += ".tmp";
    save_bytes(temporary, Bytes(text.begin(), text.end()));
    fs::rename(temporary, path);
}
std::string boot_id() {
    std::ifstream input("/proc/sys/kernel/random/boot_id");
    std::string value;
    input >> value;
    require(!value.empty(), "Missing boot identity");
    return value;
}
bool has_device_owner() {
    for (const auto& process : fs::directory_iterator("/proc")) {
        const auto name = process.path().filename().string();
        if (name.empty() || name.find_first_not_of("0123456789") != std::string::npos) continue;
        std::error_code error;
        for (const auto& fd : fs::directory_iterator(process.path() / "fd", error)) {
            const auto target = fs::read_symlink(fd.path(), error).string();
            if (error) { error.clear(); continue; }
            for (const char* prefix : {"/dev/axi", "/dev/udmabuf", "/dev/u-dma", "/dev/video", "/dev/mem"})
                if (target.rfind(prefix, 0) == 0) return true;
        }
    }
    return false;
}
double milliseconds(Clock::time_point begin) {
    return std::chrono::duration<double, std::milli>(Clock::now() - begin).count();
}
void finite(const Bytes& bytes) {
    require(bytes.size() % sizeof(float) == 0, "FP32 extent differs");
    for (std::size_t i = 0; i < bytes.size(); i += sizeof(float)) {
        float value;
        std::memcpy(&value, bytes.data() + i, sizeof(value));
        require(std::isfinite(value), "Nonfinite data; isolate result");
    }
}

class Lease {
    int fd_ = -1;
public:
    Lease() {
        fd_ = ::open("/run/pose180-resident.lock", O_RDWR | O_CREAT | O_CLOEXEC, 0600);
        require(fd_ >= 0, "Cannot open global lease");
        if (::flock(fd_, LOCK_EX | LOCK_NB) != 0) {
            ::close(fd_); fd_ = -1;
            throw std::runtime_error("Global lease is occupied");
        }
    }
    ~Lease() { if (fd_ >= 0) ::close(fd_); }
    Lease(const Lease&) = delete;
    Lease& operator=(const Lease&) = delete;
};

class ModelExperiment {
    fs::path root_;
    Json manifest_, plan_, results_ = Json::array();
    std::map<std::string, xir::Network> graphs_;
    Device device_;
    MemRegion region_;
    topk::board::Allocations allocations_;
    std::map<std::string, std::unique_ptr<SharedNpuSession>> stages_;
    std::map<std::string, Bytes> initial_buffers_;
    Bytes input_, cpu_scores_, cpu_features_, selected_scores_, selected_features_;
    std::vector<float> numeric_scores_;
    std::vector<std::size_t> winners_;
    std::vector<Bytes> actual_, oracle_, cpu_reference_;
    std::size_t frames_ = 0, forwards_ = 0;
    bool closed_ = false;
    bool io_completed_ = false;

    void gate(const std::string& name) {
        const auto path = root_ / name;
        while (!fs::exists(path)) {
            require(!stop_requested || name == "release.json", "Stop requested while awaiting controller");
            std::this_thread::sleep_for(std::chrono::milliseconds(200));
        }
        const auto request = read_json(path);
        require(request.at("boot_id") == manifest_.at("boot_id") && request.at("frames") == frames_ &&
                request.at("hardware_reviewed") == true, "Controller gate identity differs");
        require(!stop_requested || name == "release.json", "Stop requested");
    }

    void write(const std::string& key, Bytes& bytes) {
        auto& chunk = allocations_.at(key);
        require(bytes.size() <= chunk->byte_size, "Write exceeds allocation");
        io_completed_ = false;
        chunk.write(0, bytes.data(), bytes.size());
        io_completed_ = true; // The installed plugin returns after DMA completion.
    }

    void read(const std::string& key, Bytes& bytes) {
        auto& chunk = allocations_.at(key);
        require(bytes.size() <= chunk->byte_size, "Read exceeds allocation");
        io_completed_ = false;
        chunk.read(bytes.data(), 0, bytes.size());
        io_completed_ = true;
    }

    void load() {
        plan_ = read_json(root_ / "plan.json");
        input_ = read_bytes(root_ / "input.bin");
        require(input_.size() == 43200, "Old-model input extent differs");
        finite(input_);
        for (int id : {3483, 3487}) oracle_.push_back(read_bytes(root_ / ("expected_" + std::to_string(id) + ".bin")));
        require(oracle_[0].size() == 400 && oracle_[1].size() == 16800, "Old-model output extent differs");
        for (const auto& name : {"model", "rank_A", "rank_B"}) {
            const auto stem = std::string(name) == "model" ? "model" : "candidate";
            auto network = xir::Network::CreateFromJsonFile((root_ / (std::string(stem) + ".json")).string());
            network.loadParamsFromFile((root_ / (std::string(stem) + ".raw")).string());
            graphs_.emplace(name, network);
        }
        require(plan_.at("stages").size() == 5 && manifest_.at("benchmark_pairs") == 10 &&
                manifest_.at("maximum_forward_calls") == 88, "Finite experiment budget differs");
    }

    void initialize() {
        load();
        report("opening_sdk");
        started = true;
        save_json(root_ / "sdk-attempt.json", {{"boot_id", boot_id()}, {"opens", 1}, {"maximum_forward_calls", 88}});
        device_ = Device::Open("axi://zg330aiu?npu=0x40000000&dma=0x80000000");
        device_.setWaitTime(10000);
        const auto version = device_.version();
        require(version.at("device") == "25122301" && version.at("icore") == "FMSHZGV3TECH-AID - 24160628",
                "Device/icore identity differs");
        require(device_.readReg(0x1c, true) == 0x25122301, "Relative FPGA register region identity differs");
        topk::board::check_ddr_idle(device_);
        region_ = device_.defaultMemRegion();
        require(region_.memManager().getAllMemChunk().empty(), "Unexpected initial device allocations");
        io_completed_ = true;
        for (auto item = plan_.at("allocations").begin(); item != plan_.at("allocations").end(); ++item) {
            const auto size = item.value().get<uint64_t>();
            require(size > 0 && size <= 1024 * 1024 && size % 64 == 0, "Allocation budget/alignment differs");
            allocations_[item.key()] = region_.malloc(size, false, 4096);
            initial_buffers_[item.key()].assign(size, 0);
        }
        Json bindings = Json::array();
        for (const auto& specification : plan_.at("stages")) {
            const auto name = specification.at("name").get<std::string>();
            stages_[name] = std::make_unique<SharedNpuSession>();
            bindings.push_back(stages_.at(name)->initialize(
                graphs_.at(specification.at("graph").get<std::string>()), specification, allocations_, device_, root_ / "uploads"));
        }
        save_json(root_ / "bindings.json", bindings);
        // Initialize each entire shared allocation once. The N=100 producer may
        // overwrite its logical prefix; the remaining capacity stays finite.
        for (auto& item : initial_buffers_) write(item.first, item.second);
        for (const auto& name : {"rank_A", "rank_B"}) {
            const auto count = std::string(name) == "rank_A" ? 180U : 100U;
            for (const auto& suffix : {":input_mask", ":output_mask"}) {
                auto& bytes = initial_buffers_.at(std::string(name) + suffix);
                const auto active = std::string(suffix) == ":input_mask" ? count : 100U;
                const float one = 1.0f;
                for (std::size_t i = 0; i < active; ++i) std::memcpy(bytes.data() + i * 4, &one, 4);
                write(std::string(name) + suffix, bytes);
            }
        }
        topk::board::check_ddr_idle(device_);
        device_.showStatus(1);
        device_.showStatus(3);
        release_available = true;
        report("ready_for_reference", {{"version", version}, {"direct_port_bindings", 27}});
    }

    double npu(const std::string& stage) {
        require(forwards_ < 88, "Forward budget exhausted");
        ++forwards_;
        return stages_.at(stage)->forward(device_);
    }

    double cpu_cut(const Json& cut, const fs::path& directory, bool preserve_boundary) {
        const auto begin = Clock::now();
        const auto n = cut.at("n").get<std::size_t>();
        const auto k = cut.at("k").get<std::size_t>();
        const auto score_key = "model:" + std::to_string(cut.at("score").get<int>());
        const auto feature_key = "model:" + std::to_string(cut.at("features").get<int>());
        require(k == 100 && (n == 100 || n == 180) && cut.at("channels") == 42, "CPU reference shape differs");
        cpu_scores_.resize(n * 4);
        cpu_features_.resize(n * 168);
        read(score_key, cpu_scores_);
        read(feature_key, cpu_features_);
        finite(cpu_scores_); finite(cpu_features_);
        numeric_scores_.resize(n);
        std::memcpy(numeric_scores_.data(), cpu_scores_.data(), cpu_scores_.size());
        winners_.resize(n);
        std::iota(winners_.begin(), winners_.end(), 0);
        std::sort(winners_.begin(), winners_.end(), [&](std::size_t a, std::size_t b) {
            return numeric_scores_[a] == numeric_scores_[b] ? a < b : numeric_scores_[a] > numeric_scores_[b];
        });
        selected_scores_.resize(k * 4);
        selected_features_.resize(k * 168);
        for (std::size_t i = 0; i < k; ++i) {
            std::memcpy(selected_scores_.data() + i * 4, cpu_scores_.data() + winners_[i] * 4, 4);
            std::memcpy(selected_features_.data() + i * 168, cpu_features_.data() + winners_[i] * 168, 168);
        }
        const auto outputs = cut.at("outputs").get<std::vector<int>>();
        write("model:" + std::to_string(outputs[0]), selected_features_);
        if (cut.at("selected_scores_used").get<bool>()) write("model:" + std::to_string(outputs[1]), selected_scores_);
        topk::board::check_ddr_idle(device_);
        const auto duration = milliseconds(begin);
        if (preserve_boundary) {
            const auto name = cut.at("name").get<std::string>();
            save_bytes(directory / (name + ".input_scores.bin"), cpu_scores_);
            save_bytes(directory / (name + ".input_features.bin"), cpu_features_);
            save_bytes(directory / (name + ".output_scores.bin"), selected_scores_);
            save_bytes(directory / (name + ".output_features.bin"), selected_features_);
        }
        return duration;
    }

    void frame(bool candidate, bool measured) {
        require(!stop_requested, "Stop requested between completed frames");
        release_available = false;
        const auto mode = candidate ? "candidate" : "cpu_reference";
        const auto name = std::to_string(frames_) + "_" + mode;
        const auto directory = root_ / "frames" / name;
        fs::create_directories(directory);
        report("frame_running", {{"mode", mode}, {"measured", measured}});
        const auto begin = Clock::now();
        write("model:0", input_);
        const auto input_ms = milliseconds(begin);
        Json times = Json::object();
        times["npu_0"] = npu("npu_0");
        if (candidate) times["rank_A"] = npu("rank_A");
        else times["cpu_A_including_io"] = cpu_cut(plan_.at("cuts")[0], directory, !measured);
        times["npu_1"] = npu("npu_1");
        if (candidate) times["rank_B"] = npu("rank_B");
        else times["cpu_B_including_io"] = cpu_cut(plan_.at("cuts")[1], directory, !measured);
        times["npu_2"] = npu("npu_2");
        const auto pipeline_ms = milliseconds(begin);
        actual_.resize(2);
        std::size_t index = 0;
        for (int id : {3483, 3487}) {
            actual_[index].resize(oracle_[index].size());
            read("model:" + std::to_string(id), actual_[index]);
            ++index;
        }
        topk::board::check_ddr_idle(device_);
        const auto total_ms = milliseconds(begin);
        // Save the complete first reads before any comparison or publication.
        save_bytes(directory / "scores.actual.bin", actual_[0]);
        save_bytes(directory / "poses.actual.bin", actual_[1]);
        release_available = true;
        for (const auto& data : actual_) finite(data);
        const bool simulator_equal = actual_ == oracle_;
        if (frames_ == 0) cpu_reference_ = actual_;
        const bool reference_equal = actual_ == cpu_reference_;
        Json result{{"mode", mode}, {"measured", measured}, {"frame", frames_},
                    {"input_write_ms", input_ms}, {"pipeline_ms", pipeline_ms}, {"total_io_ms", total_ms},
                    {"stages_ms", times}, {"simulator_bitwise_equal", simulator_equal},
                    {"board_cpu_bitwise_equal", reference_equal}, {"boundary_host_transfer_calls", candidate ? 0 : 7}};
        save_json(directory / "result.json", result);
        results_.push_back(result);
        ++frames_;
        save_json(root_ / "results.json", results_);
        report("frame_complete", {{"result", result}});
        require(simulator_equal && reference_equal, "First model outputs differ; stop without retry");
    }

public:
    bool started = false, release_available = false;
    std::string stage = "before_sdk";
    ModelExperiment(fs::path root, Json manifest) : root_(std::move(root)), manifest_(std::move(manifest)) {}
    ~ModelExperiment() {
        if (started && !closed_) {
            static constexpr char message[] = "SDK_RELEASE_BLOCKED: retaining model experiment and lease\n";
            const auto written = ::write(STDERR_FILENO, message, sizeof(message) - 1);
            (void)written;
            for (;;) ::sleep(1);
        }
    }
    void report(const std::string& phase, Json fields = Json::object()) {
        stage = phase;
        fields["phase"] = phase; fields["frames"] = frames_; fields["forward_calls"] = forwards_;
        fields["pid"] = ::getpid(); fields["boot_id"] = manifest_.at("boot_id");
        fields["release_available"] = release_available;
        save_json(root_ / "state.json", fields);
        std::cout << fields.dump() << std::endl;
    }
    void run() {
        initialize();
        gate("run_reference.json");
        frame(false, false);
        device_.showStatus(1); device_.showStatus(3);
        report("reference_review");
        gate("run_candidate.json");
        frame(true, false);
        device_.showStatus(1); device_.showStatus(3);
        report("correctness_review");
        gate("run_benchmark.json");
        const auto begin = Clock::now();
        for (unsigned pair = 0; pair < 10; ++pair) {
            require(milliseconds(begin) < 60000, "Benchmark active budget exhausted between frames");
            frame(pair % 2 == 0, true);
            frame(pair % 2 != 0, true);
        }
        device_.showStatus(1); device_.showStatus(3);
        report("release_review");
        finish();
    }
    void finish() {
        gate("release.json");
        report("releasing");
        release_available = false;
        topk::board::check_ddr_idle(device_);
        for (auto& item : stages_) item.second->release();
        stages_.clear();
        for (auto& item : allocations_) item.second.free();
        allocations_.clear();
        require(region_.memManager().getAllMemChunk().empty(), "Model allocations remain after cleanup");
        Device::Close(device_);
        closed_ = true;
        report("complete", {{"allocation_count_after", 0}, {"sdk_opens", 1}});
    }

    bool can_release_after_error() const {
        if (!started || closed_ || !io_completed_) return false;
        for (const auto& item : stages_) if (!item.second->operation_completed()) return false;
        // Completed synchronous transfers and final-output callbacks are the
        // primary evidence. Status registers additionally reject busy/errors.
        try { topk::board::check_ddr_idle(device_); return true; }
        catch (...) { return false; }
    }
};
}

int main(int argc, char** argv) {
    if (argc != 2) { std::cerr << "Usage: topk_model_board_validation <isolated-directory>\n"; return 2; }
    for (int signal : {SIGTERM, SIGINT, SIGHUP}) std::signal(signal, [](int) { stop_requested = 1; });
    const auto root = fs::canonical(argv[1]);
    const auto manifest = read_json(root / "manifest.json");
    require(manifest.at("boot_id") == boot_id() && !has_device_owner(), "Boot/ownership differs");
    Lease lease;
    require(!has_device_owner() && !fs::exists("/run/pose180-resident.active.json"), "Startup already reserved");
    require(!fs::exists(root / "sdk-attempt.json"), "SDK startup already attempted in this batch");
    save_json("/run/pose180-resident.active.json", {{"boot_id", boot_id()}, {"run", root.string()}});
    auto experiment = std::make_unique<ModelExperiment>(root, manifest);
    try { experiment->run(); return 0; }
    catch (...) {
        std::string message = "Non-standard exception";
        try { throw; } catch (const std::exception& error) { message = error.what(); } catch (...) {}
        const auto prior = experiment->stage;
        experiment->release_available = experiment->can_release_after_error();
        experiment->report("retained_after_error", {{"error", message}, {"prior_stage", prior}});
        if (!experiment->started) {
            fs::remove("/run/pose180-resident.active.json");
            return 1;
        }
        for (;;) {
            if (experiment->release_available && fs::exists(root / "release.json")) {
                try { experiment->finish(); return 1; }
                catch (...) { experiment->release_available = false; }
            }
            std::this_thread::sleep_for(std::chrono::seconds(1));
        }
    }
}
