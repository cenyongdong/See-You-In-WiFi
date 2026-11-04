#include <icraft-xrt/core/device.h>
#include <unistd.h>
#include <cstdlib>
#include <iostream>
#include <optional>
#include <stdexcept>
namespace {
int command_fd = -1, response_fd = -1;
char command() {
    char c = 0;
    if (::read(command_fd, &c, 1) != 1)
        std::_Exit(74);
    if (c == 'A')
        std::_Exit(73);
    return c;
}
void send(char c) {
    if (::write(response_fd, &c, 1) != 1)
        std::_Exit(74);
}
}
int main(int argc, char **argv) {
    if (argc != 4 || std::string(argv[1]) != "--coordinated")
        return 2;
    command_fd = std::stoi(argv[2]);
    response_fd = std::stoi(argv[3]);
    if (command_fd < 3 || response_fd < 3 || command_fd == response_fd)
        return 2;
    send('R'); // Dynamic loader/SDK constructors completed; no Device::Open yet.
    std::optional<icraft::xrt::Device> device;
    try {
        if (command() != 'G')
            std::_Exit(74);
        device.emplace(icraft::xrt::Device::Open("axi://zg330aiu?npu=0x40000000&dma=0x80000000"));
        send('O');
        if (command() != 'V')
            std::_Exit(74);
        const auto v = device->version();
        if (v.at("device") != "25122301" || v.at("icore") != "FMSHZGV3TECH-AID - 24160628")
            throw std::runtime_error("Device identity changed");
        send('V');
        if (command() != 'C')
            std::_Exit(74);
        device.reset();
        send('C');
        return 0;
    } catch (const std::exception &e) {
        std::cerr << "SDK_ORIGINAL_EXCEPTION " << e.what() << std::endl;
        send('E');
        std::_Exit(71);
    }
}
