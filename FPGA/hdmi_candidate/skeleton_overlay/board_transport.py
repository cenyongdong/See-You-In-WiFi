"""Reuse pinned OpenSSH + in-memory credentials, with this candidate's paths."""
import argparse, importlib.util, sys, time
from pathlib import Path
from run import ROOT, WORK
sys.path.insert(0, str(ROOT / 'tools'))
from device_credentials import credentials
p = argparse.ArgumentParser()
p.add_argument('label')
p.add_argument('mode', choices=['ssh', 'put', 'get'])
p.add_argument('source')
p.add_argument('destination', nargs='?')
p.add_argument('--timeout', type=int, default=60)
a = p.parse_args()
if not a.label.replace('-', '').replace('_', '').isalnum():
    raise ValueError('Invalid label')
path = ROOT / 'demo_v1/tools/ssh.py'
spec = importlib.util.spec_from_file_location('_overlay_ssh', path)
module = importlib.util.module_from_spec(spec)
text = path.read_text()
old = "remote.startswith('/root/demo-v1-20261022-r1/')"
new = "(remote.startswith('/root/pose180-skeleton-overlay-20261031-r2/') or remote.startswith('/root/pose180-overlay-ps-reference-20261031/') or remote in ('/tmp/pose180-overlay-ps-reference-20261031.tar.gz','/tmp/pose180-skeleton-overlay-20261031-r2.tar.gz','/tmp/overlay-tests-20261031','/tmp/overlay-evidence-20261031.tar.gz'))"
assert text.count(old) == 1
exec(compile(text.replace(old, new), str(path), 'exec'), module.__dict__)
def password(_):
    user, secret = credentials('192.168.126.49', 'root')
    if user != 'root':
        raise ValueError('Unexpected board account')
    return secret
module.getpass.getpass = password
out = WORK / 'reports/board'
out.mkdir(exist_ok=True)
sys.argv = [str(path), a.mode, a.source]
if a.destination:
    sys.argv.append(a.destination)
sys.argv += ['--timeout', str(a.timeout), '--log', str(out / (a.label + '-' + time.strftime('%H%M%S') + '.log'))]
module.main()
