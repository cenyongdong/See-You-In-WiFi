"""Own one native EDA invocation without a timeout that kills the tool."""
from pathlib import Path
import json
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[3]
WORK = ROOT / '.local/hdmi-probe-free-drain-20261026-r1'
EVIDENCE = ROOT / 'tools/pose-v1/evidence/hdmi-probe-free-drain-20261026-r1'
stage = sys.argv[1]
cwd = WORK / stage
cwd.mkdir(exist_ok=True)
metadata = EVIDENCE / (stage + '-process.json')
if metadata.exists():
    raise RuntimeError('Stage already has a native invocation; inspect it before continuing')
argv = ['D:/vivado18.3/Vivado/2018.3/bin/vivado.bat', '-mode', 'batch', '-nojournal', '-log', str(EVIDENCE / (stage + '.vivado.log')),
    '-source', str(EVIDENCE / (stage + '.tcl'))]
with (EVIDENCE / (stage + '.stdout.log')).open('xb') as out, (EVIDENCE / (stage + '.stderr.log')).open('xb') as err:
    process = subprocess.Popen(argv, cwd=cwd, stdout=out, stderr=err, stdin=subprocess.DEVNULL)
    metadata.write_text(json.dumps(dict(stage=stage, pid=process.pid, command=argv, cwd=str(cwd), started_unix=time.time(),
        automatic_kill=False), indent=2) + '\n')
    print(json.dumps(dict(stage=stage, pid=process.pid)), flush=True)
    while process.poll() is None:
        try:
            process.wait(timeout=25)
        except subprocess.TimeoutExpired:
            print(json.dumps(dict(stage=stage, pid=process.pid, running=True, stdout_bytes=out.tell())),
                flush=True)
    result = dict(stage=stage, native_exit=process.returncode, exit_code=process.returncode, completed_unix=time.time())
    (EVIDENCE / (stage + '-execution.json')).write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result), flush=True)
sys.exit(process.returncode)
