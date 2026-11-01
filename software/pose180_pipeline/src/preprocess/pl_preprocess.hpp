#pragma once
#include "polar_finish.hpp"
#include <cstdint>
#include <string>
#include <thread>
namespace pose_v1 {
struct CsiPlMetrics {
 std::uint64_t calls=0,software_fallbacks=0,hardware_faults=0,boundary_fallbacks=0;
 std::uint64_t upload_ns=0,wait_ns=0,download_ns=0,finish_ns=0,compute_cycles=0;
 std::uint64_t streamed_groups=0,groups_read_while_busy=0;
 std::uint64_t boundary_window_fallbacks=0;
};
class PlPreprocess {
public:
 explicit PlPreprocess(const std::string& hardware_profile);
 ~PlPreprocess();
 PlPreprocess(const PlPreprocess&)=delete;PlPreprocess& operator=(const PlPreprocess&)=delete;
 Tokens process(const RawCsi&);
 const CsiPlMetrics& metrics()const{return metrics_;}
 bool isolated()const{return isolated_;}
 const std::string& fault()const{return fault_;}
private:
 int fd_=-1;void* mapping_=nullptr;volatile std::uint32_t* csr_=nullptr;
 std::uint32_t tag_=0;bool isolated_=false,streaming_=false;std::string fault_;
 std::thread::id owner_=std::this_thread::get_id();CsiPlMetrics metrics_;
 std::uint32_t read(unsigned)const;void write(unsigned,std::uint32_t);
};
}
