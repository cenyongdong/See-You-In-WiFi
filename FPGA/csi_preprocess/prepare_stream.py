"""Reuse the qualified r2 integration; only CSI batch publication changes."""
from run import ROOT, WORK, SRC
import json, shutil
BASE = ROOT / '.local/csi-preprocess-20261031-r2'
assert WORK.name == 'csi-preprocess-20261031-r3'
sources = WORK / 'sources'
shutil.copytree(BASE / 'sources', sources)
shutil.copyfile(SRC / 'batch.sv', sources / 'batch_banked.sv')
# No second unused batch definition in this new source snapshot.
(sources / 'batch.sv').unlink()
r = WORK / 'reports'
for name in ('physical', 'pipeline-physical', 'physical-final-closure'):
    (r / name).mkdir(exist_ok=True)
(WORK / 'ip_patch').mkdir(exist_ok=True)
stages = ('synthesis-banked', 'opt-banked', 'place-csi-incremental', 'route-csi-incremental', 'report-closure',
    'bit-closure')
for name in stages:
    v = (BASE / 'reports' / (name + '.tcl')).read_text().replace(BASE.as_posix(), WORK.as_posix())
    if name == 'place-csi-incremental':
        v = v.replace((ROOT / '.local/csi-preprocess-20261031-r1/pipeline-routed-direct.dcp').as_posix(),
            (BASE / 'pipeline-routed-csi-incremental.dcp').as_posix())
    (r / (name + '.tcl')).write_text(v)
for name in ('run_stage.py', 'qualify_closure.py'):
    (WORK / name).write_text((BASE / name).read_text().replace(BASE.as_posix(), WORK.as_posix()))
for name in ('call_procise_disable_icap.bat', 'procise_run_disable_icap.tcl'):
    (WORK / name).write_text((BASE / name).read_text().replace(BASE.as_posix(), WORK.as_posix()))
manifest = json.loads((BASE / 'manifest.json').read_text())
manifest.update(profile='probe-free-drain-overlay-csi-v3', baseline=str(BASE), csi_ABI='0x43534903', group_complex_samples=90,
    groups=60,
    baseline_BOOT_sha256=json.loads((BASE / 'reports/package-review.json').read_text())['BOOT_sha256'],
    board_tested=False, deployment_qualified=False,
    group_ready_CSR='0x44 published_words', sample_order='receiver,time,antenna,carrier', CORDIC_unchanged=True)
(WORK / 'manifest.json').write_text(json.dumps(manifest, indent=2))
print('Prepared new streaming netlist with qualified r2 physical reuse')
