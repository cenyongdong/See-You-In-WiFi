#include "polar_model.hpp"
#include "polar_finish.hpp"
#include <algorithm>
#include <chrono>
#include <cmath>
#include <cstring>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <random>
#include <stdexcept>
#include <vector>
using namespace pose_v1;
std::uint32_t bits(float f){std::uint32_t v;std::memcpy(&v,&f,4);return v;}
float value(std::uint32_t v){float f;std::memcpy(&f,&v,4);return f;}
int main(int argc,char**argv){try{
 if(argc!=4)throw std::runtime_error("numeric_test dataset.piwcsi2 vectors.hex report.json");
 std::ifstream input(argv[1],std::ios::binary);std::ofstream vectors(argv[2]),report(argv[3]);
 if(!input || !vectors || !report)throw std::runtime_error("Open test input/output");
 double amplitude_max=0,phase_max=0,phase_sum2=0,polar_angle_max=0,polar_relative_max=0;
 std::uint64_t frames=0,fallbacks=0,phase_bad=0,samples=0,zero=0,vector_count=0;
 auto emit=[&](float x,float y){auto p=csi_pl::polar(bits(x),bits(y));
  vectors<<std::hex<<std::setfill('0')<<std::setw(8)<<bits(x)<<' '<<std::setw(8)<<bits(y)<<' '<<std::setw(8)<<p.magnitude<<' '<<std::setw(8)<<std::uint32_t(p.angle)<<'\n';++vector_count;
  const double expected=std::atan2(double(y),double(x)),actual=p.angle*(std::acos(-1.)/1073741824.);
  polar_angle_max=std::max(polar_angle_max,std::abs(std::remainder(expected-actual,2*std::acos(-1.))));
  const double m=std::hypot(double(x),double(y));if(m)polar_relative_max=std::max(polar_relative_max,std::abs(value(p.magnitude)/m-1));
 };
 for(float x:{-100.f,-1.f,-0.f,0.f,1.f,100.f})for(float y:{-100.f,-1.f,-0.f,0.f,1.f,100.f})emit(x,y);
 std::mt19937 gen(0x43534901);std::uniform_real_distribution<float> dist(-1,1);
 for(unsigned k=0;k<1500;++k)emit(std::ldexp(dist(gen),int(k%81)-40),std::ldexp(dist(gen),int((k*7)%81)-40));
 std::vector<char> record(86432);
 while(input.read(record.data(),record.size())){
  if(std::memcmp(record.data(),"PIWCSI2\0",8))throw std::runtime_error("Input framing");
  RawCsi raw{};PolarWindow polar{};
  for(unsigned r=0;r<3;++r)for(unsigned a=0;a<3;++a)for(unsigned t=0;t<20;++t)for(unsigned n=0;n<30;++n){
   const auto i=raw_index(r,a,n,t);const auto j=(((r*3+a)*20+t)*30+n)*16+32;
   double x,y;std::memcpy(&x,record.data()+j,8);std::memcpy(&y,record.data()+j+8,8);raw[i]={x,y};
   const auto p=csi_pl::polar(bits(float(x)),bits(float(y)));polar[i]={value(p.magnitude),p.angle};
   if(x==0 && y==0)++zero;if(frames==0 && i<300)emit(float(x),float(y));
  }
  unsigned boundary=0;const auto ref=preprocess(raw),candidate=finish_polar(raw,polar,&boundary);fallbacks+=boundary;
  for(unsigned i=0;i<kTokenCount;++i){const double e=std::abs(double(ref[i])-candidate[i]);
   if(i%60<30)amplitude_max=std::max(amplitude_max,e);
   else{phase_max=std::max(phase_max,e);phase_sum2+=e*e;++samples;if(e>1e-4)++phase_bad;}
  }++frames;
 }
 if(!input.eof() || input.gcount())throw std::runtime_error("Partial record");
 double synthetic_max=0;unsigned synthetic_bad=0;
 for(unsigned scenario=0;scenario<48;++scenario){
  RawCsi raw{};PolarWindow polar{};
  for(unsigned r=0;r<3;++r)for(unsigned a=0;a<3;++a)for(unsigned n=0;n<30;++n)for(unsigned t=0;t<20;++t){
   const auto i=raw_index(r,a,n,t);const double pi=std::acos(-1.);
   double angle=.23*n+.07*t+.41*r+pi*a+(int(scenario%3)-1)*1e-8;
   double amplitude=1+double((i*17)%101)/13.;
   if(scenario>=12 && scenario<24)angle=dist(gen)*pi;
   if(scenario>=24 && scenario<36)angle=double(int(n%4)-2)*pi/2+(int(scenario%3)-1)*1e-9;
   if(scenario>=36)angle=0;
   raw[i]=std::polar(amplitude,angle);
   if(scenario%4==0 && (i%7==0))raw[i]={0.,-0.};
   const auto p=csi_pl::polar(bits(float(raw[i].real())),bits(float(raw[i].imag())));
   polar[i]={value(p.magnitude),p.angle};
  }
  const auto ref=preprocess(raw),candidate=finish_polar(raw,polar);
  for(unsigned i=0;i<kTokenCount;++i)if(i%60>=30){const auto e=std::abs(double(ref[i])-candidate[i]);synthetic_max=std::max(synthetic_max,e);if(e>1e-4)++synthetic_bad;}
 }
 report<<std::setprecision(12)<<"{\n  \"frames\": "<<frames<<",\n  \"phase_samples\": "<<samples<<",\n  \"zero_bins\": "<<zero<<",\n  \"boundary_fallback_operations\": "<<fallbacks<<",\n  \"amplitude_max_abs\": "<<amplitude_max<<",\n  \"phase_max_abs_rad\": "<<phase_max<<",\n  \"phase_rmse_rad\": "<<std::sqrt(phase_sum2/samples)<<",\n  \"phase_errors_above_1e_4\": "<<phase_bad<<",\n  \"polar_angle_max_rad\": "<<polar_angle_max<<",\n  \"polar_magnitude_max_relative\": "<<polar_relative_max<<",\n  \"rtl_vectors\": "<<vector_count<<"\n}\n";
 std::cout<<"frames="<<frames<<" phase_max="<<phase_max<<" amplitude_max="<<amplitude_max<<" fallbacks="<<fallbacks<<" vectors="<<vector_count<<'\n';
 std::cout<<"synthetic_windows=48 phase_max="<<synthetic_max<<" errors_above_1e_4="<<synthetic_bad<<'\n';
 return frames && !phase_bad && !synthetic_bad && polar_angle_max<1e-6 && polar_relative_max<1e-6 ? 0 : 2;
 }catch(const std::exception&e){std::cerr<<e.what()<<'\n';return 1;}}
