#include "parameter_image.hpp"
#include <iostream>
#include <limits>

int main() {
    using namespace topk::board;
    unsigned checks = 0;
    const std::vector<char> first{'a', 'b'}, second{'c', 'd', 'e'};
    if (parameter_image(5, {{second.data(), 2, 3}, {first.data(), 0, 2}}) != std::vector<char>({'a','b','c','d','e'})) return 1;
    ++checks;
    auto rejects = [&](std::uint64_t bytes, std::vector<ParameterPart> parts) {
        try { (void)parameter_image(bytes, parts); }
        catch (const std::runtime_error&) { ++checks; return; }
        throw std::runtime_error("Invalid parameter layout was accepted");
    };
    rejects(5, {{first.data(),0,2},{second.data(),1,3}}); // overlap
    rejects(6, {{first.data(),0,2},{second.data(),3,3}}); // gap
    rejects(4, {{first.data(),0,2},{second.data(),2,3}}); // overrun
    rejects(5, {{first.data(),0,2}});                   // missing part
    rejects(2, {{nullptr,0,2}});
    rejects(2, {{first.data(),std::numeric_limits<std::uint64_t>::max(),2}});
    rejects(65 * 1024 * 1024, {});
    if (!parameter_image(0, {}).empty()) return 1;
    ++checks;
    std::cout << "PARAMETER_IMAGE_PASS checks=" << checks << '\n';
}
