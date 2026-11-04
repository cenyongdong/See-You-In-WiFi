// Read only: the package must bind an already verified new candidate/runtime.
#include "r9_startup_observer.hpp"
#include "r9_observer_mapping.hpp"
#include <filesystem>
#include <fstream>
#include <iostream>
int main(int argc, char **argv) {
    using namespace pose::r9_startup;
    using namespace pose::dma_probe_evidence;
    try {
        need(argc == 4 && std::filesystem::path(argv[1]).is_absolute(),
            "Absolute output, expected FREEZE generation and runtime boot ID required");
        const std::string text = argv[2];
        std::size_t used = 0;
        const auto parsed = std::stoul(text, &used);
        need(used == text.size() && parsed >= 2 && parsed <= 0xffffffffUL && parsed % 2 == 0,
            "Explicit even FREEZE generation required");
        const auto expected = static_cast<std::uint32_t>(parsed);
        std::ifstream boot_file("/proc/sys/kernel/random/boot_id");
        std::string boot;
        std::getline(boot_file, boot);
        need(boot.size() == 36 && boot == argv[3], "Runtime changed: no MMIO access");
        EvidenceLog evidence(argv[1]);
        Mapping mapping(true);
        const auto a = mapping.read(4), count = mapping.read(0x10), status = mapping.read(0),
                   request = mapping.read(8), response = mapping.read(12);
        auto &out = evidence.stream();
        out << "{\"event\":\"boot_witness_initial\",\"boot_id\":" << quoted(boot)
            << ",\"expected_sequence\":" << expected << ",\"abi\":" << a << ",\"count\":" << count
            << ",\"status\":" << status << ",\"request\":" << request << ",\"response\":" << response
            << "}\n";
        evidence.commit();
        need(a == abi && count == 104 && status == 0 && request == expected && response == expected,
            "Observer not at expected completed FREEZE");
        std::array<std::uint32_t, 19> words{};
        for (unsigned i = 0; i < words.size(); ++i)
            words[i] = mapping.read(i < 11 ? 0x14 + 4 * i : 0x1e0 + 4 * (i - 11));
        const auto after_status = mapping.read(0), after_request = mapping.read(8),
                   after_response = mapping.read(12);
        out << "{\"event\":\"boot_witness_snapshot\",\"words\":[";
        for (unsigned i = 0; i < words.size(); ++i) {
            if (i)
                out << ',';
            out << words[i];
        }
        out << "],\"after\":{\"status\":" << after_status << ",\"request\":" << after_request
            << ",\"response\":" << after_response << "}}\n";
        evidence.commit();
        need(words[0] == 0x42545201 && (words[18] & 128) != 0 && after_status == 0 &&
                after_request == expected && after_response == expected,
            "Witness identity/publication/generation changed; raw saved");
        std::cout << "BOOT_WITNESS_CAPTURE_VALID no MMIO writes, no SDK" << std::endl;
        return 0;
    } catch (const std::exception &e) {
        std::cerr << "BOOT_WITNESS_CAPTURE_STOP " << e.what() << std::endl;
        return 1;
    }
}
