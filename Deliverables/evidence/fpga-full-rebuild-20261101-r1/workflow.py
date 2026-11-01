from pathlib import Path
import datetime,json,subprocess,sys,time,os
work=Path(__file__).resolve().parent;source=work/'source';build=work/'build';state=work/'workflow-state.json'
assert (work/'identity.json').is_file()
stages=['synthesis-banked','opt-banked','place-csi-incremental','route-csi-incremental','report-closure']
def save(v):state.write_text(json.dumps(v,indent=2)+'\n')
v=dict(pid=os.getpid(),started_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),state='running',completed=[],board_operations=0)
for stage in stages:
 v.update(stage=stage,stage_started=time.time());save(v);print('START '+stage,flush=True)
 command=[sys.executable,str(source/'tools/release/rebuild_fpga.py'),'run','--output',str(build),'--stage',stage]
 rc=subprocess.call(command)
 if rc:
  v.update(state='stopped_on_native_failure',exit_code=rc,finished=time.time());save(v);raise SystemExit(rc)
 v['completed'].append(stage);save(v);print('COMPLETE '+stage,flush=True)
v.update(state='physical_reports_ready_for_review',finished=time.time());save(v)
print('Physical reports ready; inspect full timing/DRC before bit generation',flush=True)
