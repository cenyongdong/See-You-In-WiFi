"""Finite independent PC subscriber; never controls the board or acknowledges frames."""
from pathlib import Path
import argparse
import json
import shutil
import subprocess
import time
import urllib.request
from prepare import ROOT, WORK

parser = argparse.ArgumentParser()
parser.add_argument('round', type=int, choices=(1, 2, 3))
args = parser.parse_args()
folder = WORK / ('pc-round-' + str(args.round))
folder.mkdir()
node = shutil.which('node')
if not node:
    raise RuntimeError('Existing Node runtime unavailable')
command = [node, str(ROOT / 'software/pose180_pipeline/host/resident.mjs'),
    '--board', '192.168.126.49', '--mode', 'raw', '--port', '39383',
    '--http-port', '39380', '--seconds', '360', '--output', str(folder / 'records')]
with (folder / 'stdout.log').open('xb') as out, (folder / 'stderr.log').open('xb') as err:
    child = subprocess.Popen(command, stdout=out, stderr=err, creationflags=subprocess.CREATE_NO_WINDOW)
    (folder / 'process.json').write_text(json.dumps(dict(pid=child.pid, command=command, seconds=360,
        started_unix=time.time())))
    print(json.dumps(dict(PC_started=True, pid=child.pid, seconds=360)), flush=True)
    last = {}
    with (folder / 'states.jsonl').open('x') as log:
        while child.poll() is None:
            try:
                with urllib.request.urlopen('http://127.0.0.1:39380/api/state', timeout=2) as response:
                    last = json.load(response)
                compact = {key: last[key] for key in ('connected', 'received', 'invalid', 'duplicates',
                    'reconnects', 'recorded', 'recordDrops', 'archiveError', 'phase', 'age_ms')}
                compact['session'] = last.get('frame', {}).get('session') if last.get('frame') else None
                log.write(json.dumps(dict(at_unix=time.time(), **compact)) + '\n')
                log.flush()
                (folder / 'latest.json').write_text(json.dumps(last))
            except (OSError, ValueError):
                pass
            try:
                child.wait(timeout=5)
            except subprocess.TimeoutExpired:
                pass
    code = child.wait()
(folder / 'completed.json').write_text(json.dumps(dict(native_exit=code, last_state=last)))
print(json.dumps(dict(native_exit=code, received=last.get('received', 0), invalid=last.get('invalid',
    0))), flush=True)
raise SystemExit(code)
