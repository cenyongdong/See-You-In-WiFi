#include "polar_finish.hpp"
#include <cmath>
#include <stdexcept>
namespace pose_v1 {
bool finish_polar_group(const RawCsi& raw,const PolarWindow& polar,std::size_t r,std::size_t t,Tokens& out,unsigned& count){
 constexpr double pi=3.1415926535897932384626433832795,period=2*pi;
 constexpr double uncertainty=2e-6;
 auto phase=[&](std::size_t i){return raw[i]==std::complex<double>{} ? std::arg(raw[i]) : polar[i].angle*(pi/1073741824.);};
 // For the common bounded ranges, fmod returns x or x-period exactly.
 // Keep the same additions/subtractions (including endpoint/signed-zero
 // behavior); arbitrary larger values still use the original libm path.
 auto wrap=[&](double v){
  v+=pi;
  if(v>=0 && v<period)return v-pi;
  if(v>=period && v<2*period)return (v-period)-pi;
  if(v<0 && v>-period)return (v+period)-pi;
  v=std::fmod(v,period);if(v<0)v+=period;return v-pi;
 };
 constexpr double step=2*pi*625;
 static const auto fit=[](){std::array<double,3> sums{};
  for(unsigned a=0;a<3;++a)for(unsigned n=0;n<30;++n){const double x=step*n;sums[0]+=x*x;sums[1]+=x;sums[2]+=1;}
  return sums;
 }();
 const double A=fit[0],B=fit[1],C=fit[2],denominator=A*C-B*B;
  double p[3][30]{};bool boundary=false;
  for(std::size_t a=0;a<3;++a){
   double previous=0,correction=0;
   for(std::size_t n=0;n<30;++n){
    const auto i=raw_index(r,a,n,t);double v=phase(i);
    if(a){const auto j=raw_index(r,a-1,n,t);double diff=wrap(v-phase(j));
     if(raw[i]==std::complex<double>{} || raw[j]==std::complex<double>{} || std::abs(std::abs(diff)-pi)<uncertainty){
      diff=std::arg(raw[i]*std::conj(raw[j]));++count;
     }
     v=p[a-1][n]+diff;
    }
    if(n){const double delta=v-previous;double adjusted=wrap(delta);
     if(std::abs(std::abs(adjusted)-pi)<uncertainty)boundary=true;
     if(adjusted==-pi && delta>0)adjusted=pi;
     if(std::abs(delta)>=pi)correction+=adjusted-delta;
    }
    previous=v;p[a][n]=v+correction;
   }
  }
  // Ambiguous unwrap branches are uncommon but can change all 90 features.
  // Recompute this group in double precision, without discarding the PL work
  // for the other 59 independent receiver/time groups.
  if(boundary){++count;
   for(std::size_t a=0;a<3;++a){double previous=0,correction=0;
    for(std::size_t n=0;n<30;++n){const auto i=raw_index(r,a,n,t);
     double v=a ? p[a-1][n]+std::arg(raw[i]*std::conj(raw[raw_index(r,a-1,n,t)])) : std::arg(raw[i]);
     if(n){const auto delta=v-previous;double adjusted=wrap(delta);
      if(adjusted==-pi && delta>0)adjusted=pi;
      if(std::abs(delta)>=pi)correction+=adjusted-delta;}
     previous=v;p[a][n]=v+correction;
    }
   }
  }
  // Retain the reference operation order and constants in the small fit.
  double D=0,E=0;
  for(unsigned a=0;a<3;++a)for(unsigned n=0;n<30;++n){double x=step*n;D+=x*p[a][n];E+=p[a][n];}
  const double rho=(B*E-C*D)/denominator,beta=(B*D-A*E)/denominator;
  for(unsigned a=0;a<3;++a)for(unsigned n=0;n<30;++n){const auto i=raw_index(r,a,n,t),offset=((r*3+a)*20+t)*60;
   const double corrected=p[a][n]+step*n*rho+beta;
   const double magnitude=polar[i].magnitude;
   // A final +/-pi crossing is a scalar feature discontinuity. A zero bin
   // also has signed-zero quadrant boundaries. Use the exact reference for
   // these rare ambiguous windows rather than choosing from rounded angles.
   const double principal=wrap(corrected);
   if(std::abs(std::abs(principal)-pi)<uncertainty ||
      (magnitude==0 && std::abs(std::abs(principal)-pi/2)<uncertainty)){
    ++count;return false;
   }
   // Preserve the reference complex multiply's signed zero convention.
   double angle=magnitude==0 ? std::arg(std::complex<double>(0,0)*std::exp(std::complex<double>(0,corrected))) : principal;
   if(boundary || std::abs(std::abs(angle)-pi)<uncertainty){
    const double m=std::abs(raw[i]);
    angle=std::arg(std::complex<double>(m,0)*std::exp(std::complex<double>(0,corrected)));
   }
   out[offset+n]=float(magnitude);out[offset+30+n]=float(angle);
   if(!std::isfinite(out[offset+n]) || !std::isfinite(out[offset+30+n]))throw std::runtime_error("Invalid PL CSI output");
  }
 return true;
}
Tokens finish_polar(const RawCsi& raw,const PolarWindow& polar,unsigned* fallbacks){
 Tokens out{};unsigned count=0;
 for(std::size_t r=0;r<3;++r)for(std::size_t t=0;t<20;++t){
  if(!finish_polar_group(raw,polar,r,t,out,count)){
   if(fallbacks)*fallbacks=count;return preprocess(raw);
  }
 }
 if(fallbacks)*fallbacks=count;
 return out;
}
}
