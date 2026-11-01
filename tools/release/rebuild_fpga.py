"""Prepare/run the existing CSI v3 FPGA flow in a new directory, without device access."""
from pathlib import Path
import argparse,json,re,shutil,subprocess,time
from fpga_dependencies import collect,REF,HW,INCREMENTAL
OLD='D:/FPGACompetitionProject'
STAGES=['synthesis-banked','opt-banked','inputs-check','place-csi-incremental','route-csi-incremental','report-closure','bit-closure']
def prepare(src,out):
 src=src.resolve();out=out.resolve()
 if out.exists():raise FileExistsError('Choose a new isolated output directory: '+str(out))
 files=collect(src)
 for base in [src/'FPGA',src/HW/'sources']:
  for p in base.rglob('*'):
   if p.is_file() and p.suffix.lower() in {'.v','.sv','.vh','.vhd','.xdc','.tcl','.py','.json','.bat'}:files[p.relative_to(src).as_posix()]=p
 for p in (src/HW).iterdir():
  if p.is_file() and p.suffix.lower() in {'.py','.tcl','.bat','.json'}:files[p.relative_to(src).as_posix()]=p
 for p in (src/HW/'reports').glob('*.tcl'):files[p.relative_to(src).as_posix()]=p
 out.mkdir(parents=True)
 rewritten=[]
 for rel,p in files.items():
  q=out/rel;q.parent.mkdir(parents=True,exist_ok=True);data=p.read_bytes()
  if p.suffix.lower() in {'.tcl','.xpr','.xci','.xml','.bif','.bat','.cfg','.json','.py'}:
   try:
    text=data.decode('utf-8-sig')
    new=re.sub(re.escape(OLD),lambda _:out.as_posix(),text,flags=re.I)
    if new!=text:data=new.encode('utf-8');rewritten.append(rel)
   except UnicodeDecodeError:pass # Preserve encrypted vendor Tcl verbatim.
  q.write_bytes(data)
 for rel in ['reports/physical','reports/pipeline-physical','reports/physical-final-closure']:(out/HW/rel).mkdir(parents=True,exist_ok=True)
 (out/HW/'reports/inputs-check.tcl').write_text(f"""if {{[catch {{
set_param general.maxThreads 2
open_checkpoint {{{(out/HW/'pipeline-opt-banked.dcp').as_posix()}}}
set bb [get_cells -hier -filter {{IS_BLACKBOX == 1}}]
puts "UNRESOLVED_BLACKBOXES [llength $bb] $bb"
if {{[llength $bb]}} {{error "Unresolved black boxes after PS/IP import"}}
read_checkpoint -incremental {{{(out/INCREMENTAL).as_posix()}}}
puts "INCREMENTAL_BASELINE_LOADED"
}} result]}} {{puts $result; puts $::errorInfo; exit 1}}
exit
""")
 (out/'rebuild-logs').mkdir()
 plan=dict(source_root=str(src),output_root=str(out),copied_files=len(files),rewritten_path_files=rewritten,target='JFMQL30TAI676H / adapted xc7z030ffg676-2',stages=STAGES,tools_external=True,device_operations=0)
 (out/'rebuild-plan.json').write_text(json.dumps(plan,indent=2)+'\n')
 print('Prepared',len(files),'files;',len(rewritten),'path relocations',flush=True)
def run(out,stage,vivado):
 out=out.resolve();plan=json.loads((out/'rebuild-plan.json').read_text());assert plan['output_root']==str(out)
 logdir=out/'rebuild-logs';record=logdir/(stage+'.json')
 if record.exists():raise FileExistsError('Stage already recorded; preserve original result before choosing a new work directory')
 script=out/HW/'reports'/(stage+'.tcl');start=time.time()
 cmd=[str(vivado),'-mode','batch','-nojournal','-log',str(logdir/(stage+'.vivado.log')),'-source',str(script)]
 with (logdir/(stage+'.stdout.log')).open('wb') as f:
  p=subprocess.Popen(cmd,cwd=out,stdout=f,stderr=subprocess.STDOUT)
  record.write_text(json.dumps(dict(stage=stage,pid=p.pid,command=cmd,started=start,state='running'),indent=2))
  rc=p.wait()
 v=dict(stage=stage,pid=p.pid,command=cmd,started=start,seconds=time.time()-start,exit_code=rc,state='completed')
 record.write_text(json.dumps(v,indent=2)+'\n');print(json.dumps(v),flush=True)
 if rc:raise SystemExit(rc)
def main():
 p=argparse.ArgumentParser();p.add_argument('action',choices=['prepare','run']);p.add_argument('--source-root',type=Path,default=Path(__file__).resolve().parents[2]);p.add_argument('--output',type=Path,required=True);p.add_argument('--stage',choices=STAGES);p.add_argument('--vivado',type=Path,default=Path('D:/vivado18.3/Vivado/2018.3/bin/vivado.bat'));a=p.parse_args()
 if a.action=='prepare':prepare(a.source_root,a.output)
 else:
  if not a.stage:p.error('--stage is required')
  run(a.output,a.stage,a.vivado)
if __name__=='__main__':main()
