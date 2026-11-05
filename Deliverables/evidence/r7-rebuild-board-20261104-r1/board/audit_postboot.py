from pathlib import Path
import sys,json
root=Path('/root/pose180-r7-rebuild-20261104-r1')
sys.path.insert(0,str(root/'boot'))
import board_support as b
b.ROOT=root;b.META=root/'boot-operations';b.MOUNT=root/'boot-mount'
identity=json.loads((root/'board/identity.json').read_text())
old=json.loads((root/'pretest-audit.json').read_text())
assert b.boot_id()!=old['boot_id']
audit=b.audit(identity['BOOT_sha256'])
(root/'postboot-audit.json').write_text(json.dumps(audit,indent=2)+'\n')
print(json.dumps(dict(boot_id=audit['boot_id'],previous_boot_id=old['boot_id'],BOOT_sha256=identity['BOOT_sha256'],fpga_state=audit['fpga_state'],device_owners=audit['device_owners'],SDK_matches=True)))
