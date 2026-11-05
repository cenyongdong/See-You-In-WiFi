from pathlib import Path
import json,sys,fcntl,tarfile,hashlib,subprocess
root=Path('/root/pose180-r7-rebuild-20261104-r1')
sys.path[:0]=[str(root/'board'),str(root/'boot')]
import board_support as b
from run_hdmi_trial import owners
b.ROOT=root;b.META=root/'boot-operations';b.MOUNT=root/'boot-mount'
baseline=json.loads((root/'pretest-audit.json').read_text())
candidate=json.loads((root/'postboot-audit.json').read_text())
assert b.boot_id()!=candidate['boot_id']
assert not owners() and not b.owners()
with Path('/run/pose180-resident.lock').open('a') as lock:
    fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
    audit=b.audit(baseline['backup_sha256'])
    audit['network']=json.loads(subprocess.check_output(['ip','-j','addr','show','dev','eth0']))
    audit['active_receipt_present']=Path('/run/pose180-resident.active.json').exists()
    ports=[]
    for table in ('tcp','tcp6'):
        for line in Path('/proc/net/'+table).read_text().splitlines()[1:]:
            row=line.split()
            port=int(row[1].split(':')[-1],16)
            if row[3]=='0A' and port in (39383,39384,39385):ports.append(port)
    audit['test_ports_listening']=ports
    assert not ports and not audit['active_receipt_present']
    assert not any(x.get('local')=='192.168.50.49' for n in audit['network'] for x in n['addr_info'])
    audit.update(restored_baseline=True,SDK_started_after_fallback=False)
    (root/'final-audit.json').write_text(json.dumps(audit,indent=2)+'\n')
files=[]
for name in ('pretest-audit.json','postboot-audit.json','posttrial-audit.json','final-audit.json','trial-close.json','transfer-verified.json'):
    files.append(root/name)
files+=list((root/'boot-operations').glob('*.json'))
files+=[p for p in (root/'board/runs').rglob('*') if p.is_file()]
files+=[root/'board/identity.json',root/'board/latest.json',root/'board/next-boot.json']
archive=Path('/tmp/pose180-r7-rebuild-20261104-r1-evidence.tar.gz')
assert not archive.exists()
with tarfile.open(archive,'w:gz') as tar:
    for p in files:
        assert not p.is_symlink()
        tar.add(str(p),arcname=p.relative_to(root).as_posix(),recursive=False)
h=hashlib.sha256(archive.read_bytes()).hexdigest()
receipt=dict(restored=True,boot_id=audit['boot_id'],BOOT_sha256=baseline['backup_sha256'],device_owners=[],test_ports_listening=[],SDK_started_after_fallback=False,evidence_sha256=h,evidence_bytes=archive.stat().st_size,evidence_files=len(files))
(root/'closed.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(json.dumps(receipt))
