from pathlib import Path
from run import ROOT,WORK,run
import subprocess
D='C:/Program Files/Docker/Docker/resources/bin/docker.exe'
work=WORK/'software';work.mkdir(exist_ok=True)
base='/workspace/'+work.relative_to(ROOT).as_posix()
src='/workspace/software/pose180_pipeline'
state=subprocess.check_output([D,'inspect','--format','{{.State.Status}}','FPAI']).strip()
if state==b'exited':run('container-start',[D,'start','FPAI'],work)
run('native-configure',[D,'exec','FPAI','cmake','-S',src,'-B',base+'/native','-DCMAKE_BUILD_TYPE=Release'],work)
run('native-build',[D,'exec','FPAI','cmake','--build',base+'/native','--parallel','2','--target','overlay_tests','renderer_tests','display_state_tests','hdmi_resource_tests'],work)
for target in ('renderer_tests','display_state_tests','hdmi_resource_tests','overlay_tests'):
    run(target,[D,'exec','FPAI',base+'/native/'+target,*([base] if target=='overlay_tests' else [])],work)
run('arm-configure',[D,'exec','FPAI','cmake','-S',src,'-B',base+'/arm64','-DCMAKE_SYSTEM_NAME=Linux','-DCMAKE_SYSTEM_PROCESSOR=aarch64',
 '-DCMAKE_CXX_COMPILER=aarch64-linux-gnu-g++','-DCMAKE_PREFIX_PATH=/usr/cmake','-DCMAKE_BUILD_TYPE=Release',
 '-DPOSE180_BUILD_SDK=ON','-DPOSE180_DEMO_PROBE_FREE_DRAIN=ON','-DPOSE180_DEMO_PL_FILTER=ON','-DPOSE180_DEMO_PL_OVERLAY=ON'],work)
run('arm-build',[D,'exec','FPAI','cmake','--build',base+'/arm64','--parallel','2','--target','pose180_demo','overlay_tests'],work)
