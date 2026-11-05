from pathlib import Path
import sys,json,fcntl,shutil,os
root=Path('/root/pose180-r7-rebuild-20261104-r1')
sys.path.insert(0,str(root/'boot'))
import board_support as b
b.ROOT=root;b.PACKAGE=root/'boot';b.META=root/'boot-operations';b.MOUNT=root/'boot-mount'
b.META.mkdir();b.MOUNT.mkdir()
with Path('/run/pose180-resident.lock').open('a') as lock:
    fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
    files=b.fat_files()
    baseline=files['BOOT.BIN']['sha256']
    audit=b.audit(baseline)
    b.fat_files(root/'pretest-BOOT.bin')
    assert b.digest(root/'pretest-BOOT.bin')==baseline
    audit.update(backup_sha256=baseline,SDK_initialized=False,boot_written=False)
    (root/'pretest-audit.json').write_text(json.dumps(audit,indent=2)+'\n')
    print(json.dumps(dict(boot_id=b.boot_id(),BOOT_sha256=baseline,SDK_matches=True,device_owners=audit['device_owners'],root_free_bytes=shutil.disk_usage('/').free,readback_saved=True)))
