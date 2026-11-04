"""Fresh bounded rounds, reusing the already qualified r1 hardware/software."""
from pathlib import Path
import argparse
import hashlib
import json
import py_compile
import shutil
import tarfile

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
OLD = ROOT / '.local/hdmi-probe-free-drain-20261026-r1'
parser = argparse.ArgumentParser()
parser.add_argument('--batch', choices=('r2', 'r3'), default='r2')
parser.add_argument('--rounds', type=int, choices=(1, 3), default=1)
parser.add_argument('--session-base', type=int, default=20261026195600)
args = parser.parse_args()
WORK = ROOT / ('.local/hdmi-probe-free-drain-20261026-' + args.batch)
E = ROOT / ('tools/pose-v1/evidence/hdmi-probe-free-drain-20261026-' + args.batch)
REMOTE = '/root/demo-v1-20261022-r1/' + WORK.name

def put(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding='utf-8', newline='\n')

def digest(path):
    return dict(bytes=path.stat().st_size, sha256=hashlib.sha256(path.read_bytes()).hexdigest())

def pack(folder, target):
    with tarfile.open(target, 'x:gz') as archive:
        for path in sorted(folder.rglob('*')):
            if path.is_file():
                info = archive.gettarinfo(str(path), arcname=path.relative_to(folder).as_posix())
                info.mode = 0o755 if path.name == 'pose180_demo' else 0o600
                with path.open('rb') as stream:
                    archive.addfile(info, stream)

WORK.mkdir()
E.mkdir()
bundle = WORK / 'board-bundle'
bundle.mkdir()
common = bundle / 'common'
shutil.copytree(OLD / 'board-bundle/common', common)
software = WORK / 'software'
software.mkdir()
with tarfile.open(OLD / 'board-bundle/round-1/software-package.tar.gz') as archive:
    for member in archive.getmembers():
        if not member.isfile() or Path(member.name).name != member.name:
            raise RuntimeError('Unexpected software archive path')
    archive.extractall(software)
identity = json.loads((software / 'identity.json').read_text())
for index in range(1, args.rounds + 1):
    name = 'round-' + str(index)
    folder = bundle / name
    folder.mkdir()
    identifier = WORK.name + '-' + name
    identity['session'] = args.session_base + index
    put(software / 'identity.json', json.dumps(identity, indent=2) + '\n')
    pack(software, folder / 'software-package.tar.gz')
    controller = (OLD / 'board-bundle/round-1/controller.py').read_text().replace(OLD.name, WORK.name).replace(WORK.name + '-round-1',
        identifier)
    put(folder / 'controller.py', controller)
    py_compile.compile(str(folder / 'controller.py'), doraise=True, cfile=str(WORK / (name + '-controller.pyc')))
    manifest = json.loads((OLD / 'board-bundle/round-1/manifest.json').read_text())
    manifest.update(package_id=identifier, base=REMOTE + '/' + name, status='authorized_onsite_300_seconds')
    manifest['board']['remote_root'] = manifest['base']
    manifest['files'] = {path.relative_to(folder).as_posix(): digest(path) for path in folder.iterdir() if path.is_file()}
    manifest['files'].update({'../common/' + path.name: digest(path) for path in common.iterdir()})
    put(folder / 'manifest.json', json.dumps(manifest, indent=2) + '\n')
    put(folder / 'authorization.json', json.dumps(dict(package_id=identifier, active=True, caps=manifest['caps'],
        user_confirmation=f'2026-10-26 user is beside the board and explicitly requested {args.rounds} further stability test(s). This fresh round has one candidate boot, one SDK attempt, 300 seconds actual CSI/NPU/HDMI, and one original-BOOT fallback reserved. Reuse qualified r1 assets; no failed-load retry.'),
        indent=2) + '\n')
    put(WORK / (name + '-network.py'), (OLD / 'round-1-network.py').read_text().replace(OLD.name, WORK.name).replace('/round-1/network',
        '/' + name + '/network'))
pack(bundle, WORK / 'board-package.tar.gz')
for name in ('board_call.py', 'capture_uart.py', 'capture_hdmi_startup.ps1'):
    put(WORK / name, (OLD / name).read_text(encoding='utf-8-sig').replace(OLD.name, WORK.name))
choices = 'choices=' + repr(tuple(range(1, args.rounds + 1)))
host = (HERE / 'board_host.py').read_text().replace('parents[3]', 'parents[2]').replace(OLD.name, WORK.name).replace('DRAIN_R1_',
    'DRAIN_' + args.batch.upper() + '_').replace('choices=(1,2,3)', choices)
put(WORK / 'board_host.py', host)
observer = (HERE / 'observe_pc.py').read_text().replace('from prepare import ROOT,WORK', "ROOT=Path(__file__).resolve().parents[2]\nWORK=Path(__file__).resolve().parent").replace('choices=(1,2,3)',
    choices)
put(WORK / 'observe_pc.py', observer)
put(E / 'state.json', json.dumps(dict(status='prepared', scope=f'{args.rounds} onsite 300-second full-chain round(s)',
    reused_assets=str(OLD), candidate_BOOT_sha256=manifest['candidate_boot_sha256'],
    native_binary_sha256=identity['files']['pose180_demo'], candidate_starts=0, SDK_Open=0, original_fallbacks=0,
    caps=manifest['caps']), indent=2) + '\n')
print(json.dumps(dict(prepared=True, work=str(WORK), caps=manifest['caps'], BOOT_sha256=manifest['candidate_boot_sha256'])))
