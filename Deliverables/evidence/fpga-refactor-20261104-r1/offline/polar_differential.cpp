#include "polar_model.hpp"
#include <array>
#include <cmath>
#include <cstdint>
#include <cstring>
#include <fstream>
#include <iostream>
#include <random>
#include <stdexcept>
#include <string>
#include <vector>
namespace csi_pl_baseline {
struct Polar { std::uint32_t magnitude; std::int32_t angle; };
Polar polar(std::uint32_t, std::uint32_t);
}
struct Output { std::uint32_t magnitude; std::int32_t angle; std::uint32_t error; };
int main(int argc, char** argv) {
    if(argc != 3) return 1;
    std::ifstream input(argv[1], std::ios::binary);
    std::ofstream actual(std::string(argv[2])+"/actual.bin",std::ios::binary);
    std::ofstream expected(std::string(argv[2])+"/expected.bin",std::ios::binary);
    std::ofstream inputs(std::string(argv[2])+"/inputs.bin",std::ios::binary);
    if(!input || !actual || !expected || !inputs) return 1;
    std::uint64_t count=0, invalid=0;
    auto compare=[&](std::uint32_t re, std::uint32_t im) {
        Output a{},b{};std::string ea,eb;
        try { auto p=csi_pl::polar(re,im);a={p.magnitude,p.angle,0}; }
        catch(const std::exception& e) { a.error=1;ea=e.what(); }
        try { auto p=csi_pl_baseline::polar(re,im);b={p.magnitude,p.angle,0}; }
        catch(const std::exception& e) { b.error=1;eb=e.what(); }
        inputs.write(reinterpret_cast<const char*>(&re),4);inputs.write(reinterpret_cast<const char*>(&im),4);
        actual.write(reinterpret_cast<const char*>(&a),sizeof(a));
        expected.write(reinterpret_cast<const char*>(&b),sizeof(b));
        ++count;invalid+=a.error;
        if(a.magnitude!=b.magnitude || a.angle!=b.angle || a.error!=b.error || ea!=eb) {
            actual.flush();expected.flush();inputs.flush();
            throw std::runtime_error("Differential mismatch at sample "+std::to_string(count));
        }
    };
    std::array<std::uint32_t,14> edge={0u,0x80000000u,1u,0x80000001u,0x007fffffu,0x00800000u,
        0x3f800000u,0xbf800000u,0x7f7fffffu,0xff7fffffu,0x7f800000u,0xff800000u,0x7fc00001u,0xffc00001u};
    for(auto re:edge)for(auto im:edge)compare(re,im);
    std::mt19937 generator(0x43534901);
    for(unsigned i=0;i<20000;++i) { auto re=generator();auto im=generator();compare(re,im); }
    std::vector<char> record(86432);
    while(input.read(record.data(),record.size())) {
        if(std::memcmp(record.data(),"PIWCSI2\0",8))return 1;
        for(unsigned i=0;i<5400;++i) {
            double re,im;std::memcpy(&re,record.data()+32+16*i,8);std::memcpy(&im,record.data()+40+16*i,8);
            float rf=float(re),imf=float(im);std::uint32_t rb,ib;std::memcpy(&rb,&rf,4);std::memcpy(&ib,&imf,4);
            compare(rb,ib);
        }
    }
    if(input.gcount())return 1;
    actual.flush();expected.flush();inputs.flush();if(!actual || !expected || !inputs)return 1;
    std::cout<<"POLAR_DIFFERENTIAL_PASS samples="<<count<<" rejected="<<invalid<<'\n';
}
