"""Pinned host-key SSH, in-memory credential callback, this candidate only."""
import argparse, importlib.util, sys, time, re
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
p.add_argument('--revision', choices=['r1', 'r2', 'r3'], default='r3')
p.add_argument('--evidence-directory')
p.add_argument('--package')
a = p.parse_args()
WORK = ROOT / ('.local/csi-preprocess-20261031-' + a.revision)
if not a.label.replace('-', '').replace('_', '').isalnum():
    raise ValueError('Invalid label')
path = ROOT / 'demo_v1/tools/ssh.py'
spec = importlib.util.spec_from_file_location('_csi_ssh', path)
module = importlib.util.module_from_spec(spec)
source = path.read_text()
old = "remote.startswith('/root/demo-v1-20261022-r1/')"
package = a.package or 'pose180-csi-preprocess-20261031-' + a.revision
if not re.fullmatch(r'pose180-csi-(?:preprocess|longrun|release)-\d{8}-r\d+', package):
    raise ValueError('Invalid candidate package')
new = "(remote.startswith('/root/PKG/') or remote in ('/tmp/PKG.tar.gz','/tmp/csi-preprocess-evidence-20261031-REV.tar.gz','/tmp/PKG-evidence.tar.gz'))".replace('PKG',
    package).replace('REV', a.revision)
assert source.count(old) == 1
exec(compile(source.replace(old, new), str(path), 'exec'), module.__dict__)
def password(_):
    user, secret = credentials('192.168.126.49', 'root')
    if user != 'root':
        raise ValueError('Unexpected account')
    return secret
module.getpass.getpass = password
out = Path(a.evidence_directory).resolve() if a.evidence_directory else WORK / 'reports/board'
if not out.is_relative_to((ROOT / '.local').resolve()):
    raise ValueError('Evidence must stay in the project local directory')
out.mkdir(parents=True, exist_ok=True)
sys.argv = [str(path), a.mode, a.source]
if a.destination:
    sys.argv.append(a.destination)
sys.argv += ['--timeout', str(a.timeout), '--log', str(out / (a.label + '-' + time.strftime('%H%M%S') + '.log'))]
module.main()
