"""Owned, finite raw and view observers; no user-visible console windows."""
from run import ROOT,WORK
import subprocess,time,json
NODE='C:/Users/cenyongdong/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe'
out=WORK/'reports/pc';out.mkdir(exist_ok=False)
children=[];records=[];handles=[]
for mode,port in [('raw',39381),('view',39380)]:
 argv=[NODE,str(ROOT/'software/pose180_pipeline/host/resident.mjs'),'--mode',mode,'--board','192.168.126.49',
  '--local-address','192.168.126.100','--http-port',str(port),'--metrics-port','0','--seconds','180']
 if mode=='raw':argv+=['--output',str(out/'actual.full')]
 stdout=(out/(mode+'.stdout.log')).open('w');stderr=(out/(mode+'.stderr.log')).open('w');handles.extend([stdout,stderr])
 p=subprocess.Popen(argv,cwd=ROOT,stdout=stdout,stderr=stderr,creationflags=subprocess.CREATE_NO_WINDOW)
 children.append(p);records.append(dict(mode=mode,pid=p.pid,started=time.time(),argv=argv,bounded_seconds=180))
(out/'processes.json').write_text(json.dumps(records,indent=2));print(json.dumps(records),flush=True)
for p in children:p.wait()
for f in handles:f.close()
(out/'exit.json').write_text(json.dumps([dict(pid=p.pid,native_exit=p.returncode) for p in children]))
print('PC observers completed',flush=True)
