// Finite GP-only check. The deployment wrapper must verify candidate BOOT and
// exclusive ownership before launch. No SDK/NPU initialization or reset here.
#include "pl_preprocess.hpp"
#include <algorithm>
#include <chrono>
#include <cmath>
#include <cstring>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <stdexcept>
#include <time.h>
#include <vector>
using namespace pose_v1;
double cpu(){timespec t{};if(clock_gettime(CLOCK_THREAD_CPUTIME_ID,&t))throw std::runtime_error("Thread CPU clock");return t.tv_sec*1000.+t.tv_nsec/1e6;}
double wall(){return std::chrono::duration<double,std::milli>(std::chrono::steady_clock::now().time_since_epoch()).count();}
int main(int argc,char**argv){try{
 if(argc!=4 || (std::string(argv[2])!="probe-free-drain-overlay-csi-v2" && std::string(argv[2])!="probe-free-drain-overlay-csi-v3"))throw std::runtime_error("benchmark dataset matching-profile report.json");
 std::ifstream input(argv[1],std::ios::binary);std::ofstream report(argv[3]);if(!input||!report)throw std::runtime_error("Input/report open");
 PlPreprocess pl(argv[2]);std::vector<char> record(86432);unsigned frames=0,bad=0;
 double ps_cpu=0,ps_wall=0,pl_cpu=0,pl_wall=0,amplitude_error=0,phase_error=0;
 unsigned amplitude_bad=0,nonfinite=0;
 std::vector<double> ps_latency,pl_latency;
 while(input.read(record.data(),record.size())){
  if(++frames>9000 || std::memcmp(record.data(),"PIWCSI2\0",8))throw std::runtime_error("Framing/count");
  RawCsi raw{};
  for(unsigned r=0;r<3;++r)for(unsigned a=0;a<3;++a)for(unsigned t=0;t<20;++t)for(unsigned n=0;n<30;++n){
   const auto j=(((r*3+a)*20+t)*30+n)*16+32;double x,y;std::memcpy(&x,record.data()+j,8);std::memcpy(&y,record.data()+j+8,8);raw[raw_index(r,a,n,t)]={x,y};
  }
  Tokens ref{},actual{};
  auto reference=[&](){const auto c=cpu(),w=wall();ref=preprocess(raw);const auto elapsed=wall()-w;ps_cpu+=cpu()-c;ps_wall+=elapsed;ps_latency.push_back(elapsed);};
  auto accelerated=[&](){const auto c=cpu(),w=wall();actual=pl.process(raw);const auto elapsed=wall()-w;pl_cpu+=cpu()-c;pl_wall+=elapsed;pl_latency.push_back(elapsed);};
  // Alternate execution order to reduce systematic cache/order bias.
  if(frames&1){reference();accelerated();}else{accelerated();reference();}
  if(pl.isolated())throw std::runtime_error("CSI isolated: "+pl.fault());
  for(unsigned i=0;i<kTokenCount;++i){
   if(!std::isfinite(actual[i])){++nonfinite;continue;}
   const double e=std::abs(double(ref[i])-actual[i]);
   if(i%60<30){amplitude_error=std::max(amplitude_error,e);if(e>2e-6*std::max(1.,std::abs(double(ref[i]))))++amplitude_bad;}
   else {phase_error=std::max(phase_error,e);if(e>1e-4)++bad;}
  }
  if(frames==1 || frames%60==0)std::cout<<"CSI_PROGRESS frames="<<frames<<" amplitude_max="<<amplitude_error<<" phase_max="<<phase_error<<" invalid="<<nonfinite<<" amplitude_bad="<<amplitude_bad<<" phase_bad="<<bad<<std::endl;
 }
 if(input.gcount() || !frames)throw std::runtime_error("Truncated/empty input");const auto& m=pl.metrics();
 std::sort(ps_latency.begin(),ps_latency.end());std::sort(pl_latency.begin(),pl_latency.end());const auto p95=std::size_t(std::ceil(frames*.95))-1;
 report<<std::setprecision(12)<<"{\n\"frames\":"<<frames<<",\n\"PS_CPU_ms_per_window\":"<<ps_cpu/frames<<",\n\"PS_wall_ms_per_window\":"<<ps_wall/frames
 <<",\n\"PL_CPU_ms_per_window\":"<<pl_cpu/frames<<",\n\"PL_wall_ms_per_window\":"<<pl_wall/frames<<",\n\"amplitude_max_abs\":"<<amplitude_error
 <<",\n\"phase_max_abs_rad\":"<<phase_error<<",\n\"phase_errors_above_1e_4\":"<<bad<<",\n\"amplitude_errors_above_tolerance\":"<<amplitude_bad<<",\n\"nonfinite_outputs\":"<<nonfinite<<",\n\"software_fallbacks\":"<<m.software_fallbacks
 <<",\n\"hardware_faults\":"<<m.hardware_faults<<",\n\"boundary_fallback_operations\":"<<m.boundary_fallbacks<<",\n\"upload_ms_per_window\":"<<m.upload_ns/1e6/frames
 <<",\n\"wait_ms_per_window\":"<<m.wait_ns/1e6/frames<<",\n\"download_ms_per_window\":"<<m.download_ns/1e6/frames<<",\n\"finish_ms_per_window\":"<<m.finish_ns/1e6/frames
 <<",\n\"compute_cycles_per_window\":"<<double(m.compute_cycles)/frames
 <<",\n\"streamed_groups\":"<<m.streamed_groups<<",\n\"groups_read_while_busy\":"<<m.groups_read_while_busy
 <<",\n\"boundary_window_fallbacks\":"<<m.boundary_window_fallbacks
 <<",\n\"PS_wall_p95_ms\":"<<ps_latency[p95]<<",\n\"PL_wall_p95_ms\":"<<pl_latency[p95]
 <<",\n\"PS_wall_max_ms\":"<<ps_latency.back()<<",\n\"PL_wall_max_ms\":"<<pl_latency.back()<<"\n}\n";
 std::cout<<"CSI_BOARD_BENCHMARK frames="<<frames<<" ps_cpu_ms="<<ps_cpu/frames<<" pl_cpu_ms="<<pl_cpu/frames<<" phase_error="<<phase_error<<'\n';return (bad || amplitude_bad || nonfinite)?2:0;
 }catch(const std::exception&e){std::cerr<<e.what()<<'\n';return 1;}}
