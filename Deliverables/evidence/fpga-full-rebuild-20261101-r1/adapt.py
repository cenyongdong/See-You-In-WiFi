from pathlib import Path
import json,subprocess,time,hashlib
w=Path(__file__).resolve().parent;b=w/'build';h=b/'.local/csi-preprocess-20261031-r3';logs=b/'rebuild-logs'
assert json.loads((logs/'bit-closure.json').read_text())['exit_code']==0
assert json.loads((w/'physical-result.json').read_text())['physical_qualification_under_existing_exceptions']
script=(h/'procise_run_disable_icap.tcl').read_text();commands=[l.strip() for l in script.splitlines() if l.strip() and not l.lstrip().startswith('#')]
assert len(commands)==2 and commands[0]=='set_device JFMQL30TAI676H' and commands[1].startswith('increment_bit_cfg_v3 ')
assert (h/'fpai_demo_vivado.runs/impl_pose_filter/ai7030_edif_top.bit').is_file()
cmd=['cmd.exe','/d','/c',str(h/'call_procise_disable_icap.bat')];start=time.time()
with (logs/'procise.log').open('w') as f:rc=subprocess.call(cmd,cwd=b,stdout=f,stderr=subprocess.STDOUT)
v=dict(command=cmd,exit_code=rc,seconds=time.time()-start,device='JFMQL30TAI676H',operation='increment_bit_cfg_v3 -disable_icap',board_operations=0)
(logs/'procise.json').write_text(json.dumps(v,indent=2)+'\n');print(json.dumps(v),flush=True)
assert rc==0
