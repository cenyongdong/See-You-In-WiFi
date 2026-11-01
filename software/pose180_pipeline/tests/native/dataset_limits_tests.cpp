// Exercise bounded replay validation and stop/join before SDK initialization.
#include "dataset.hpp"
#include <filesystem>
#include <fstream>
#include <iostream>
#include <stdexcept>
using namespace pose180_demo;
int main(int argc,char** argv) {
 if(argc!=2)return 2;
 const auto file=std::filesystem::path(argv[1]);
 std::ofstream(file,std::ios::binary).close();
 std::filesystem::resize_file(file,9000ull*pp::input_bytes);
 {Shared shared;Dataset input(shared,file,123,4);}
 for(unsigned passes:{0u,5u,31u}) {
  bool rejected=false;Shared shared;
  try{Dataset input(shared,file,123,passes);}catch(const std::runtime_error&){rejected=true;}
  if(!rejected)throw std::runtime_error("Unbounded/invalid replay accepted");
 }
 std::filesystem::resize_file(file,9001ull*pp::input_bytes);
 bool rejected=false;Shared shared;
 try{Dataset input(shared,file,123,1);}catch(const std::runtime_error&){rejected=true;}
 if(!rejected)throw std::runtime_error("Per-file cap changed");
 std::cout<<"DATASET_LIMITS_PASS 36000 accepted; 45000/invalid passes/oversized file rejected; pre-init thread stopped and joined\n";
}
