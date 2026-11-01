#include "pl_preprocess.hpp"
#include <atomic>
#include <chrono>
#include <cmath>
#include <cstring>
#include <fcntl.h>
#include <stdexcept>
#include <sys/mman.h>
#include <sys/stat.h>
#include <unistd.h>
namespace pose_v1 {
namespace {
using Clock=std::chrono::steady_clock;
std::uint64_t ns(){return std::chrono::duration_cast<std::chrono::nanoseconds>(Clock::now().time_since_epoch()).count();}
void require(bool v,const char* message){if(!v)throw std::runtime_error(message);}
void barrier(){std::atomic_thread_fence(std::memory_order_seq_cst);}
}
PlPreprocess::PlPreprocess(const std::string& profile){
 streaming_=profile=="probe-free-drain-overlay-csi-v3";
 require(streaming_ || profile=="probe-free-drain-overlay-csi-v2","CSI mapping requires matching qualified hardware profile");
 fd_=::open("/dev/mem",O_RDWR|O_SYNC|O_CLOEXEC);
 require(fd_>=0,"Cannot open CSI GP mapping");
 try{
  struct stat st{};require(::fstat(fd_,&st)==0 && S_ISCHR(st.st_mode),"CSI mapping requires physical memory character device");
  mapping_=::mmap(nullptr,4096,PROT_READ|PROT_WRITE,MAP_SHARED,fd_,0x400b3000);
  require(mapping_!=MAP_FAILED,"Cannot map CSI GP page");
  csr_=static_cast<volatile std::uint32_t*>(mapping_);
  require(read(0)==(streaming_?0x43534903u:0x43534902u),"CSI ABI mismatch");
  require((read(4)&5)==0,"CSI core not idle and healthy");
 }catch(...){if(mapping_ && mapping_!=MAP_FAILED)::munmap(mapping_,4096);::close(fd_);throw;}
}
PlPreprocess::~PlPreprocess(){
 // The core has only internal BRAM. Unmapping a CSR view never frees a DMA
 // buffer or SDK resource; no abort/reset is issued during destruction.
 if(mapping_ && mapping_!=MAP_FAILED)::munmap(mapping_,4096);
 if(fd_>=0)::close(fd_);
}
std::uint32_t PlPreprocess::read(unsigned off)const{barrier();auto v=csr_[off/4];barrier();return v;}
void PlPreprocess::write(unsigned off,std::uint32_t v){barrier();csr_[off/4]=v;barrier();}
Tokens PlPreprocess::process(const RawCsi& raw){
 require(owner_==std::this_thread::get_id(),"CSI core accessed outside owner thread");
 ++metrics_.calls;
 std::array<std::uint32_t,kComplexCount*2> words{};
 bool supported=!isolated_;
 for(std::size_t i=0;i<raw.size();++i)for(unsigned c=0;c<2;++c){
  const auto source=streaming_?raw_index(i/1800,(i%90)/30,i%30,(i/90)%20):i;
  const double v=c?raw[source].imag():raw[source].real();require(std::isfinite(v),"Non-finite raw CSI");
  const float f=float(v);std::uint32_t u;std::memcpy(&u,&f,4);words[2*i+c]=u;
  const unsigned exponent=(u>>23)&255;
  if((v!=0 && exponent==0) || exponent>=253)supported=false;
 }
 if(!supported){++metrics_.software_fallbacks;return preprocess(raw);}
 try{
  require((read(4)&5)==0,"CSI core busy or fault before submission");
  require(tag_!=0xffffffff,"CSI tag exhausted");
  const auto start=ns();write(16,2);write(12,++tag_);
  // Ordered device stores to a fixed FIFO address. No private SDK pointers,
  // DMA addresses, cache operations or memcpy to MMIO are used.
  barrier();for(auto word:words)csr_[8]=word;barrier();
  require(read(8)==words.size(),"CSI input count mismatch");
  // Small bounded transport/BRAM sentinel check, outside the NPU path.
  for(unsigned at:{0u,1u,5399u,5400u,10798u,10799u}){
   write(44,at);const auto got=read(48);
   if(got!=words[at])throw std::runtime_error("CSI BRAM input mismatch word="+std::to_string(at)+" expected="+std::to_string(words[at])+" actual="+std::to_string(got));
  }
  const auto previous=read(28);write(16,1);const auto sent=ns();
  const auto deadline=Clock::now()+std::chrono::milliseconds(200);
  if(streaming_){
   PolarWindow polar{};Tokens output{};unsigned boundaries=0;bool exact_fallback=false;
   std::uint64_t waiting=0,downloading=0,finishing=0;
   for(unsigned group=0;group<60;++group){
    const auto before_wait=ns();
    for(;;){
     const auto status=read(4);
     if(status&4)throw std::runtime_error("CSI stream fault reason="+std::to_string(read(64))+" sample_word="+std::to_string(read(52)));
     const auto published=read(68);
     require(published<=words.size() && published%180==0,"CSI partial/invalid published group");
     if(published>=(group+1)*180)break;
     require(Clock::now()<deadline,"CSI stream deadline: isolate core, no retry");
     std::this_thread::sleep_for(std::chrono::microseconds(20));
    }
    if(read(4)&1)++metrics_.groups_read_while_busy;
    ++metrics_.streamed_groups;
    const auto ready=ns();waiting+=ready-before_wait;
    const unsigned r=group/20,t=group%20;
    barrier();
    for(unsigned a=0;a<3;++a)for(unsigned n=0;n<30;++n){
     auto& p=polar[raw_index(r,a,n,t)];const auto m=csr_[9],angle=csr_[9];
     std::memcpy(&p.magnitude,&m,4);p.angle=std::int32_t(angle);
    }
    barrier();const auto downloaded=ns();downloading+=downloaded-ready;
    if(!exact_fallback)exact_fallback=!finish_polar_group(raw,polar,r,t,output,boundaries);
    finishing+=ns()-downloaded;
   }
   // A ready group is not a whole-window completion proof. Verify the final
   // status/tag/count before exposing any tensor or doing a full PS fallback.
   require(read(4)==2 && read(20)==tag_ && read(28)==previous+1 && read(40)==words.size(),"CSI stream final completion mismatch");
   const auto cycles=read(24);
   if(exact_fallback){++metrics_.boundary_window_fallbacks;const auto began=ns();output=preprocess(raw);finishing+=ns()-began;}
   metrics_.upload_ns+=sent-start;metrics_.wait_ns+=waiting;metrics_.download_ns+=downloading;
   metrics_.finish_ns+=finishing;metrics_.compute_cycles+=cycles;metrics_.boundary_fallbacks+=boundaries;
   return output;
  }
  std::this_thread::sleep_for(std::chrono::milliseconds(1));
  for(;;){const auto status=read(4);
   if(status&4)throw std::runtime_error("CSI hardware fault reason="+std::to_string(read(64))+" sample_word="+std::to_string(read(52))+" re="+std::to_string(read(56))+" im="+std::to_string(read(60)));
   if(status==2)break;
   require(Clock::now()<deadline,"CSI deadline: isolate core, no retry");
   std::this_thread::sleep_for(std::chrono::microseconds(100));
  }
  require(read(20)==tag_ && read(28)==previous+1,"CSI completion identity mismatch");
  const auto cycles=read(24);const auto ready=ns();PolarWindow polar{};
  barrier();for(auto& p:polar){const auto m=csr_[9],a=csr_[9];std::memcpy(&p.magnitude,&m,4);p.angle=std::int32_t(a);}barrier();
  require(read(40)==words.size() && read(4)==2 && read(20)==tag_,"CSI result read count/identity mismatch");
  const auto downloaded=ns();unsigned boundaries=0;auto output=finish_polar(raw,polar,&boundaries);const auto finished=ns();
  metrics_.upload_ns+=sent-start;metrics_.wait_ns+=ready-sent;metrics_.download_ns+=downloaded-ready;
  metrics_.finish_ns+=finished-downloaded;metrics_.compute_cycles+=cycles;metrics_.boundary_fallbacks+=boundaries;
  return output;
 }catch(const std::exception& e){
  // Independent GP-only core: permanently disable this backend for the run.
  // Future inference uses PS. Never restart a failed NPU or touch its memory.
  isolated_=true;fault_=e.what();++metrics_.hardware_faults;++metrics_.software_fallbacks;return preprocess(raw);
 }
}
}
