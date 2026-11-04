"""Sequential continuation of the already-started banked synthesis.

Never terminates EDA on a wall-clock timeout and never duplicates a stage.
"""
from run import WORK
import json, subprocess, sys, time
r = WORK / 'reports'
for stage in ('synthesis-banked', 'opt-banked', 'place-csi-incremental', 'route-csi-incremental', 'report-closure'):
    done = r / (stage + '-execution.json')
    if not done.exists():
        if (r / (stage + '-process.json')).exists():
            if stage != 'synthesis-banked':
                raise RuntimeError('Inspect existing native process: ' + stage)
            while not done.exists():
                time.sleep(10)
        else:
            rc = subprocess.call([sys.executable, str(WORK / 'run_stage.py'), stage])
            if rc:
                sys.exit(rc)
    if json.loads(done.read_text())['native_exit'] != 0:
        raise RuntimeError('Native failure: ' + stage)
rc = subprocess.call([sys.executable, str(WORK / 'qualify_closure.py')])
if rc:
    sys.exit(rc)
stage = 'bit-closure'
if (r / (stage + '-process.json')).exists():
    raise RuntimeError('Inspect prior bit invocation')
sys.exit(subprocess.call([sys.executable, str(WORK / 'run_stage.py'), stage]))
