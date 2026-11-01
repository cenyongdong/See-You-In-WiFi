"""Keep the qualified r2 binaries intact; build this optimization separately."""
from run import ROOT,D,run
from pathlib import Path
import sys
W=ROOT/'.local/csi-optimization-20261031-r1';R=W/'reports'
P=ROOT/'software/pose180_pipeline/src/preprocess'
base='/workspace/'+W.relative_to(ROOT).as_posix();p='/workspace/'+P.relative_to(ROOT).as_posix()
mode=sys.argv[1]
if mode=='numeric':
 source=(ROOT/'FPGA/csi_preprocess/numeric_test.cpp').read_text().replace('finish_polar(', 'checked_finish(')
 anchor='using namespace pose_v1;'
 extra='''
namespace pose_v1 { Tokens finish_polar_baseline(const RawCsi&,const PolarWindow&,unsigned*); }
Tokens checked_finish(const RawCsi& raw,const PolarWindow& polar,unsigned* count=nullptr){
 unsigned before=0,after=0;auto a=finish_polar_baseline(raw,polar,&before),b=finish_polar(raw,polar,&after);
 if(before!=after || std::memcmp(a.data(),b.data(),sizeof(a)))throw std::runtime_error("Optimized finish differs from qualified baseline");
 if(count)*count=after;return b;
}
'''
 (W/'equivalence_test.cpp').write_text(source.replace(anchor,anchor+extra))
 run('baseline-host',[D,'exec','FPAI','g++','-O2','-std=c++17','-ffp-contract=off','-I'+p,'-Dfinish_polar=finish_polar_baseline','-c',base+'/baseline/polar_finish.cpp','-o',base+'/baseline_finish.o'],R)
 run('equivalence-build',[D,'exec','FPAI','g++','-O2','-std=c++17','-ffp-contract=off','-I'+p,'-I/workspace/FPGA/csi_preprocess',base+'/equivalence_test.cpp','/workspace/FPGA/csi_preprocess/polar_model.cpp',p+'/polar_finish.cpp',p+'/preprocess.cpp',base+'/baseline_finish.o','-o',base+'/equivalence_test'],R)
 run('equivalence',[D,'exec','FPAI',base+'/equivalence_test','/workspace/.local/skeleton-overlay-20261031-r2/pose180-skeleton-overlay-20261031-r2/board/dataset.piwcsi2',base+'/reports/vectors.hex',base+'/reports/numeric.json'],R)
elif mode=='board':
 run('fast-benchmark-build',[D,'exec','FPAI','aarch64-linux-gnu-g++','-O2','-std=c++17','-ffp-contract=off','-pthread','-I'+p,
  '/workspace/FPGA/csi_preprocess/board_benchmark.cpp',p+'/pl_preprocess.cpp',p+'/polar_finish.cpp',p+'/preprocess.cpp','-o',base+'/benchmark-fast'],R)
else:raise ValueError(mode)
