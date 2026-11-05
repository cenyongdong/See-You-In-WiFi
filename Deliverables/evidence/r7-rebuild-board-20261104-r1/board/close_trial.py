from pathlib import Path
import json,sys,fcntl
root=Path('/root/pose180-r7-rebuild-20261104-r1')
sys.path[:0]=[str(root/'board'),str(root/'boot')]
import board_support as b
from run_hdmi_trial import owners
from process_guard import live
b.ROOT=root;b.META=root/'boot-operations';b.MOUNT=root/'boot-mount'
run=root/'board/runs'/json.loads((root/'board/latest.json').read_text())['run']
outcome=json.loads((run/'outcome.json').read_text())
complete=json.loads((run/'run/completion.json').read_text())
assert outcome['native_exit']==0 and outcome['native_shutdown_complete'] is True
assert complete['native_shutdown_complete'] is True
assert not complete['status']['release_blocked'] and complete['status']['state']!='isolated'
assert not live(json.loads((run/'supervisor.json').read_text()))
assert not live(json.loads((run/'metadata/process.json').read_text())['identity'])
assert not owners() and not b.owners()
assert (run/'network-closed.json').exists()
with Path('/run/pose180-resident.lock').open('a') as lock:
    fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
    identity=json.loads((root/'board/identity.json').read_text())
    audit=b.audit(identity['BOOT_sha256'])
    (root/'posttrial-audit.json').write_text(json.dumps(audit,indent=2)+'\n')
    rows=[]
    for p in (run/'run').glob('*.jsonl'):
        for line in p.read_text().splitlines():
            try:row=json.loads(line)
            except ValueError:continue
            if row.get('event')=='csi_pl':rows.append(row)
    last=max(rows,key=lambda x:x['calls']) if rows else None
    summary=dict(safe_to_restore=True,boot_id=b.boot_id(),native_exit=0,active_seconds=complete['active_elapsed_ns']/1e9,inferred=complete['status']['inferred'],adopted=complete['status']['adopted'],csi=last,device_owners=[])
    (root/'trial-close.json').write_text(json.dumps(summary,indent=2)+'\n')
    print(json.dumps(summary))
