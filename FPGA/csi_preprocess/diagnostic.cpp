// Bounded synthetic GP/BRAM diagnostic; no SDK, DMA or external memory master.
#include <atomic>
#include <chrono>
#include <cstdint>
#include <cstdio>
#include <fcntl.h>
#include <stdexcept>
#include <sys/mman.h>
#include <thread>
#include <unistd.h>
int main(){try{
 int fd=open("/dev/mem",O_RDWR|O_SYNC|O_CLOEXEC);if(fd<0)throw std::runtime_error("open");
 void* map=mmap(nullptr,4096,PROT_READ|PROT_WRITE,MAP_SHARED,fd,0x400b3000);if(map==MAP_FAILED)throw std::runtime_error("map");
 auto r=static_cast<volatile std::uint32_t*>(map);
 auto fence=[](){std::atomic_thread_fence(std::memory_order_seq_cst);};
 auto rd=[&](unsigned off){fence();auto v=r[off/4];fence();return v;};
 auto wr=[&](unsigned off,std::uint32_t v){fence();r[off/4]=v;fence();};
 if(rd(0)!=0x43534901 || (rd(4)&1))throw std::runtime_error("ABI or not idle");
 for(unsigned mode=0;mode<3;++mode){
  // Proven local idle; this reset changes only counters and this BRAM core.
  if(rd(4)&1)throw std::runtime_error("No reset while busy");
  wr(16,2);wr(12,100+mode);
  for(unsigned i=0;i<5400;++i){
   const auto re=mode==2 ? 0x3f800000u : 0x40400000u;
   const auto im=mode==2 ? 0u : 0x40800000u;
   if(mode==0){wr(32,re);wr(32,im);}else{r[8]=re;r[8]=im;}
  }
  fence();std::printf("mode=%u loaded=%u status_before=%x\n",mode,rd(8),rd(4));
  wr(16,1);auto deadline=std::chrono::steady_clock::now()+std::chrono::milliseconds(200);
  while(rd(4)&1){if(std::chrono::steady_clock::now()>deadline)throw std::runtime_error("deadline");std::this_thread::sleep_for(std::chrono::microseconds(100));}
  const auto status=rd(4);std::printf("status=%x cycles=%u tag=%u completed=%u\n",status,rd(24),rd(20),rd(28));
  if(status!=2)break;
  unsigned bad=0;const auto expected=mode==2?0x3f800000u:0x40a00000u;
  for(unsigned i=0;i<5400;++i){const auto m=rd(36),a=rd(36);if(m!=expected)++bad;
   if(i<12 || i>5396)std::printf("sample=%u magnitude=%08x angle=%08x\n",i,m,a);
  }
  std::printf("magnitude_mismatches=%u read_count=%u\n",bad,rd(40));
 }
 munmap(map,4096);close(fd);return 0;
 }catch(const std::exception&e){std::fprintf(stderr,"%s\n",e.what());return 1;}}
