"""Build and test an extracted delivery using external SDK/toolchain; no board access."""
from pathlib import Path
import argparse,hashlib,json,shutil,subprocess,time

def main():
 p=argparse.ArgumentParser()
 for n in ('source-root','deploy-root','output','host-workspace'):p.add_argument('--'+n,type=Path,required=True)
 p.add_argument('--container',default='FPAI');p.add_argument('--container-workspace',default='/workspace')
 p.add_argument('--vivado-bin',type=Path,default=Path('D:/vivado18.3/Vivado/2018.3/bin'))
 a=p.parse_args();root=a.source_root.resolve();out=a.output.resolve();out.mkdir(parents=True,exist_ok=False)
 def mapped(path):return a.container_workspace.rstrip('/')+'/'+path.resolve().relative_to(a.host_workspace.resolve()).as_posix()
 steps=[]
 def run(stage,args,cwd=None):
  start=time.monotonic();log=out/(stage+'.log')
  with log.open('wb') as f:rc=subprocess.run(list(map(str,args)),cwd=cwd,stdout=f,stderr=subprocess.STDOUT).returncode
  steps.append(dict(stage=stage,command=list(map(str,args)),cwd=str(cwd) if cwd else None,exit_code=rc,seconds=time.monotonic()-start))
  (out/'steps.json').write_text(json.dumps(steps,indent=2)+'\n')
  if rc:raise RuntimeError(stage+': '+log.read_text(errors='replace')[-2500:])
  print(stage,'PASS',flush=True)
 docker=['docker','exec',a.container];src=mapped(root/'software/pose180_pipeline');build='/tmp/'+out.name
 if subprocess.run([*docker,'test','-e',build]).returncode==0:raise FileExistsError('Use a new output directory name; build already exists: '+build)
 for preset,sub,targets in [('csi-v3-arm64','arm64',['pose180_demo']),('native-offline','native',['pose180_demo_mock','overlay_tests','renderer_tests'])]:
  run(sub+'-configure',['docker','exec','-w',src,a.container,'cmake','--preset',preset,'-B',build+'/'+sub])
  run(sub+'-build',[*docker,'cmake','--build',build+'/'+sub,'--target',*targets,'--parallel','2'])
 run('overlay-software',[*docker,build+'/native/overlay_tests',mapped(out)])
 run('renderer-software',[*docker,build+'/native/renderer_tests'])
 # Use the first 420 windows of the paired deployment archive; no workspace dataset.
 with (a.deploy_root/'board/dataset.piwcsi2').open('rb') as f:(out/'input-420.piwcsi2').write_bytes(f.read(86432*420))
 csi=root/'FPGA/csi_preprocess';pre=root/'software/pose180_pipeline/src/preprocess'
 run('numeric-build',[*docker,'g++','-O2','-std=c++17','-ffp-contract=off','-I'+mapped(csi),'-I'+mapped(pre),mapped(csi/'numeric_test.cpp'),mapped(csi/'polar_model.cpp'),mapped(pre/'polar_finish.cpp'),mapped(pre/'preprocess.cpp'),'-o',build+'/numeric_test'])
 run('numeric-test',[*docker,build+'/numeric_test',mapped(out/'input-420.piwcsi2'),mapped(out/'vectors.hex'),mapped(out/'numeric.json')])
 for tag,top,folder,names,token in [('csi','tb_batch',csi,['polar.sv','batch.sv','tb_batch.sv'],'CSI_BATCH_PASS'),('overlay','tb_overlay',root/'FPGA/hdmi_candidate/skeleton_overlay',['palette_fifo.sv','overlay.sv','tb_overlay.sv'],'OVERLAY_PASS')]:
  work=out/tag;work.mkdir();(work/'run.tcl').write_text('run all\nquit\n')
  if tag=='csi':shutil.copyfile(out/'vectors.hex',work/'vectors.hex')
  run(tag+'-compile',[a.vivado_bin/'xvlog.bat','-sv','-i',folder,*[folder/n for n in names]],work)
  run(tag+'-elaborate',[a.vivado_bin/'xelab.bat',top,'-s','verify_sim','-timescale','1ns/1ps','-mt','2'],work)
  run(tag+'-simulate',[a.vivado_bin/'xsim.bat','verify_sim','-tclbatch','run.tcl'],work)
  text=(out/(tag+'-simulate.log')).read_text(errors='replace')
  assert token in text and 'Fatal' not in text,tag
 actual=subprocess.check_output([*docker,'sha256sum',build+'/arm64/pose180_demo'],text=True).split()[0]
 expected=json.loads((a.deploy_root/'board/identity.json').read_text())['files']['pose180_demo']
 run('toolchain',[*docker,'bash','-lc','cmake --version; aarch64-linux-gnu-g++ --version; g++ --version'])
 run('arm64-file',[*docker,'file',build+'/arm64/pose180_demo'])
 bit=json.loads((root/'FPGA/hdmi_candidate/current-bit.json').read_text())
 assert hashlib.sha256((root/bit['archive_path']).read_bytes()).hexdigest()==bit['sha256']
 q=json.loads((root/'Deliverables/evidence/csi-v3/qualification-closure.json').read_text())
 for original,h in q['source_sha256'].items():
  rel=Path(original).relative_to(a.host_workspace.resolve())
  assert hashlib.sha256((root/rel).read_bytes()).hexdigest()==h,str(rel)
 result=dict(status='passed',source_root=str(root),build_directory=build,ARM64_build_pass=True,native_build_pass=True,overlay_software_pass=True,renderer_software_pass=True,CSI_numeric_pass=True,CSI_streaming_RTL_pass=True,overlay_RTL_pass=True,qualified_source_hashes_match=True,qualified_BIT_hash_match=True,software_sha256=actual,published_binary_sha256=expected,byte_identical_to_published=actual==expected,external_dependencies=['existing ARM64 Icraft/customop 3.39 SDK and GNU toolchain in FPAI','Vivado 2018.3 simulator','paired deployment official CSI input'],full_FPGA_rebuild=False,full_FPGA_rebuild_reason='This software/core-RTL test does not run full FPGA place/route; use rebuild_fpga.py with the packaged vendor dependencies',board_operations=0,SDK_runs=0)
 (out/'result.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 print(json.dumps(result,ensure_ascii=False),flush=True)
if __name__=='__main__':main()
