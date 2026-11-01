#include "polar_model.hpp"
#include <algorithm>
#include <cmath>
#include <cstring>
#include <stdexcept>
#include <array>
namespace csi_pl {
Polar polar(std::uint32_t re, std::uint32_t im) {
 const auto er=(re>>23)&255, ei=(im>>23)&255;
 if(er==255 || ei==255 || (er==0 && (re&0x7fffff)) || (ei==0 && (im&0x7fffff)))
  throw std::runtime_error("Polar requires finite normal or zero FP32");
 const bool sr=re>>31, si=im>>31;
 const auto ar=re&0x7fffffff, ai=im&0x7fffffff;
 if(!ai) return {ar, sr ? (si ? -1073741824 : 1073741824) : 0};
 if(!ar) return {ai, si ? -536870912 : 536870912};
 const unsigned exponent=std::max(er,ei);
 auto norm=[&](std::uint32_t v,unsigned e) -> std::int64_t {
  const auto shift=exponent-e;
  const auto m=shift>=40 ? 0 : (std::int64_t((v&0x7fffff)|0x800000)<<16)>>shift;
  return (v>>31) ? -m : m;
 };
 std::int64_t x=norm(re,er), y=norm(im,ei), z=0;
 if(sr){x=-x;y=-y;z=si ? -1073741824LL : 1073741824LL;}
 static const auto table=[](){std::array<std::int64_t,31> a{};for(unsigned k=0;k<31;++k)a[k]=std::llround(std::atan(std::ldexp(1.,-int(k)))*1073741824./std::acos(-1.));return a;}();
 for(unsigned k=0;k<31;++k){
  const auto a=table[k];
  const auto old=x;
  if(y>=0){x+=y>>k;y-=old>>k;z+=a;}
  else{x-=y>>k;y+=old>>k;z-=a;}
 }
 // K in Q31. Exact wide product is also used by the RTL.
 const std::uint64_t magnitude=(__int128(x)*1304065748LL)>>31;
 unsigned leading=0;for(unsigned b=0;b<42;++b)if(magnitude>>b)leading=b;
 const unsigned shift=leading-23;
 std::uint64_t mantissa=magnitude>>shift;
 if(shift){const auto rem=magnitude&((1ULL<<shift)-1),half=1ULL<<(shift-1);
  if(rem>half || (rem==half && (mantissa&1)))++mantissa;}
 int output_exp=int(exponent)+int(leading)-39;
 if(mantissa&(1ULL<<24)){mantissa>>=1;++output_exp;}
 if(output_exp<=0 || output_exp>=255)throw std::runtime_error("Polar magnitude exponent outside normal FP32");
 return {std::uint32_t(output_exp<<23)|(std::uint32_t(mantissa)&0x7fffff),std::int32_t(z)};
}
}
