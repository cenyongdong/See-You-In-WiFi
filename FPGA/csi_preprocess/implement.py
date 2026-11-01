"""Serial native implementation, retained logs, no timeout kill or board access."""
from run import WORK
import subprocess,sys,json
stages=('place-nonincremental','route-direct','physopt-direct','report-closure')
for stage in stages:
 rc=subprocess.call([sys.executable,str(WORK/'run_stage.py'),stage])
 if rc:raise SystemExit(rc)
rc=subprocess.call([sys.executable,str(WORK/'qualify_closure.py')])
if rc:raise SystemExit(rc)
raise SystemExit(subprocess.call([sys.executable,str(WORK/'run_stage.py'),'bit-closure']))
