from run import ROOT,WORK,D,run
import shutil
r=WORK/'software';r.mkdir(exist_ok=True)
base='/tmp/csi-preprocess-20261031-r3-arm'
run('configure',[D,'exec','-w','/workspace/software/pose180_pipeline','FPAI','cmake','--preset','csi-v3-arm64','-B',base],r)
run('build',[D,'exec','FPAI','cmake','--build',base,'--parallel','2','--target','pose180_demo'],r)
run('copy',[D,'cp','FPAI:'+base+'/pose180_demo',r/'pose180_demo'],r)
p='/workspace/software/pose180_pipeline/src/preprocess'
run('benchmark-build',[D,'exec','FPAI','aarch64-linux-gnu-g++','-O2','-std=c++17','-ffp-contract=off','-pthread','-I'+p,
 '/workspace/FPGA/csi_preprocess/board_benchmark.cpp',p+'/pl_preprocess.cpp',p+'/polar_finish.cpp',p+'/preprocess.cpp',
 '-o','/workspace/'+(r/'board_benchmark').relative_to(ROOT).as_posix()],r)
