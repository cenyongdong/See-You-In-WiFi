"""Local candidate assembly. BOOT operations are separate and finite."""
from run import ROOT,WORK,run
from pathlib import Path
import argparse,hashlib,json,shutil,tarfile,os
BASE=ROOT/'.local/csi-preprocess-20261031-r2'
NAME='pose180-csi-preprocess-20261031-r3'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def software():
 release=WORK/NAME;release.mkdir(exist_ok=False)
 old=BASE/'pose180-csi-preprocess-20261031-r2'
 shutil.copytree(old/'board',release/'board',ignore=shutil.ignore_patterns('__pycache__','runs','next-boot.json','verified-boot.json'))
 board=release/'board'
 for n in ('pose180_demo','board_benchmark'):shutil.copyfile(WORK/'software'/n,board/n)
 shutil.copyfile(ROOT/'software/pose180_pipeline/control/startup.py',board/'startup.py')
 ident=json.loads((board/'identity.json').read_text())
 ident.update(package=NAME,hardware_profile='probe-free-drain-overlay-csi-v3',preprocess_backend='pl',
  renderer_backend='pl',verified_boot_ids=[],board_tested=False,BOOT_sha256='PENDING_PHYSICAL_QUALIFICATION',csi_ABI='0x43534903')
 ident['boot_files']['BOOT.BIN']=ident['BOOT_sha256']
 for n in ('pose180_demo','board_benchmark','startup.py'):ident['files'][n]=sha(board/n)
 (board/'identity.json').write_text(json.dumps(ident,indent=2))
 for n in ('start.sh','stop.sh','status.sh','check.sh','recover.sh','prepare-boot.sh'):shutil.copyfile(old/n,release/n)
 script=(ROOT/'FPGA/hdmi_candidate/skeleton_overlay/boot_control.py').read_text().replace('BOOT-baseline-filter-v1.bin','BOOT-baseline-csi-v2.bin')
 (release/'boot_control.py').write_text(script)
 shutil.copyfile(ROOT/'FPGA/csi_preprocess/benchmark_control.py',release/'benchmark_control.py')
 (release/'README.md').write_text('''# CSI 分组流水 + PL 骨架候选

PS 保留组窗、相位展开/线性校正/边界回退和坐标投影；PL 保留 CORDIC 幅度与原始相位计算，新增90点完整组发布，PS读取/收尾与PL计算重叠，保留已通过的二维绘图合成。原模型、NPU 和 PC 协议不变。默认官方训练集三片段输入，非新现场采集。

本地包生成不表示时序或实板通过。安装须有完整物理资格；独立预算为 1 次候选安装/重启、1 次有限 GP 比较、1 次最长120秒 SDK 演示，必要时 1 次r2 CSI基线回退。没有自启动。BOOT 管理入口 boot_control.py，GP 比较入口 benchmark_control.py，演示入口 start.sh，停止 stop.sh。当前启动的一次性 SDK 消费规则保持。

完整原始结果在 board/runs 和 benchmark 目录。CSI 日志区分上传、等待、下载、PS收尾和实际硬件周期；流水模式下硬件计算与PS计时重叠，不能把纯计算周期加到完整延迟或当作端到端加速。r2 CSI基线 BOOT 和原演示包保留。
''',encoding='utf-8')
 print(release)
def boot():
 r=WORK/'reports';q=json.loads((r/'qualification-closure.json').read_text())
 bit_stage='bit-qualified' if (r/'bit-qualified-execution.json').exists() else 'bit-closure'
 if not q['bit_generation_prerequisite_pass'] or json.loads((r/(bit_stage+'-execution.json')).read_text())['native_exit']!=0:raise ValueError('Physical/bit prerequisite missing')
 b=WORK/'boot-package';b.mkdir(exist_ok=True)
 for n in ('FSBL251210_ddr400_demo.out','bl31.elf','u-boot'):shutil.copyfile(BASE/'boot-package'/n,b/n)
 for stage in ('icap','boot-package'):
  v=(BASE/'reports'/(stage+'.tcl')).read_text().replace(BASE.as_posix(),WORK.as_posix()).replace('BOOT-skeleton-overlay.bin','BOOT-csi-preprocess.bin')
  (r/(stage+'.tcl')).write_text(v)
 (b/'candidate.bif').write_text((BASE/'boot-package/candidate.bif').read_text().replace(BASE.as_posix(),WORK.as_posix()))
 procise=Path('C:/FudanMicro/Procise');env=os.environ.copy()
 env.update(APP_DIR=str(procise),ICTIME_HOME=str(procise),FMSH_DB=str(procise/'db'),PROCISE_DIR=str(procise),TCL_LIBRARY=str(procise/'tcl8.4'))
 env['PATH']=str(procise/'dll')+';'+str(procise/'bin')+';'+env['PATH']
 # Preserve native commands/results, with the established Procise environment.
 for stage in ('icap','boot-package'):
  import subprocess,time
  with (r/(stage+'.log')).open('x') as f:
   p=subprocess.Popen([str(procise/'bin/procise.exe'),str(r/(stage+'.tcl'))],cwd=r,env=env,stdout=f,stderr=subprocess.STDOUT)
   (r/(stage+'-process.json')).write_text(json.dumps(dict(pid=p.pid,started=time.time(),automatic_kill=False)))
   rc=p.wait()
  (r/(stage+'-exit.json')).write_text(json.dumps(dict(native_exit=rc)))
  if rc:raise RuntimeError('Procise '+stage+' failed; inspect original log')
 release=WORK/NAME;target=release/'boot';target.mkdir(exist_ok=True)
 for n in ('pose180_demo','board_benchmark'):shutil.copyfile(WORK/'software'/n,release/'board'/n)
 shutil.copyfile(ROOT/'software/pose180_pipeline/control/startup.py',release/'board/startup.py')
 shutil.copyfile(ROOT/'FPGA/csi_preprocess/benchmark_control.py',release/'benchmark_control.py')
 shutil.copyfile(BASE/'pose180-csi-preprocess-20261031-r2/boot/board_support.py',target/'board_support.py')
 shutil.copyfile(b/'BOOT-csi-preprocess.bin',target/'BOOT.BIN')
 shutil.copyfile(BASE/'boot-package/BOOT-csi-preprocess.bin',target/'BOOT-baseline-csi-v2.bin')
 shutil.copyfile(r/'qualification-closure.json',target/'qualification.json')
 ident=json.loads((release/'board/identity.json').read_text());ident['BOOT_sha256']=sha(target/'BOOT.BIN');ident['boot_files']['BOOT.BIN']=ident['BOOT_sha256']
 for n in ('pose180_demo','board_benchmark','startup.py'):ident['files'][n]=sha(release/'board'/n)
 (release/'board/identity.json').write_text(json.dumps(ident,indent=2))
 review=dict(BOOT_sha256=ident['BOOT_sha256'],baseline_BOOT_sha256=sha(target/'BOOT-baseline-csi-v2.bin'),
  raw_bit_sha256=sha(WORK/'fpai_demo_vivado.runs/impl_pose_filter/ai7030_edif_top.bit'),adapted_bit_sha256=sha(b/'ai7030_top_disable_icap.bit'),
  physical_qualified=True,board_tested=False,checkpoint=q['checkpoint'],bit_native_stage=bit_stage,new_SDK_budget=1,finite_seconds=120)
 (target/'package-review.json').write_text(json.dumps(review,indent=2))
 def permissions(m):
  if m.name.endswith('.sh') or Path(m.name).name in ('pose180_demo','board_benchmark','overlay_tests'):m.mode=0o755
  return m
 archive=WORK/(NAME+'.tar.gz')
 with tarfile.open(archive,'w:gz') as t:t.add(release,arcname=NAME,filter=permissions)
 review.update(archive=str(archive),archive_sha256=sha(archive))
 (r/'package-review.json').write_text(json.dumps(review,indent=2));print(json.dumps(review))
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('stage',choices=['software','boot']);a=p.parse_args()
 (software if a.stage=='software' else boot)()
