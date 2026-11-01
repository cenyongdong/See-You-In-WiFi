"""Latest-BOOT delivery with identity-checked install/readback recovery; no SDK initialization.

Reuse the proven FAT audit/atomic mounted replacement, never its old workflow.
"""
import argparse,fcntl,json,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'board'))
sys.path.insert(0,str(ROOT/'boot'))
import board_support as b
from run_hdmi_trial import owners
from service import atomic

def main():
    p=argparse.ArgumentParser();p.add_argument('action',choices=['audit','install','reboot','fallback','fallback-reboot']);a=p.parse_args()
    ident=json.loads((ROOT/'board/identity.json').read_text())
    review=json.loads((ROOT/'boot/package-review.json').read_text())
    q=json.loads((ROOT/'boot/qualification.json').read_text())
    b.need(q['bit_generation_prerequisite_pass'] and ident['BOOT_sha256']==review['BOOT_sha256'],'Candidate qualification/identity differs')
    b.ROOT=ROOT;b.PACKAGE=ROOT/'boot';b.META=ROOT/'boot-operations';b.MOUNT=ROOT/'boot-mount'
    b.META.mkdir(exist_ok=True);b.MOUNT.mkdir(exist_ok=True)
    b.CFG['package_id']=ident['package'];b.identity_record=lambda v:dict(v,package_id=ident['package'])
    baseline=review['baseline_BOOT_sha256'];candidate=review['BOOT_sha256']
    with Path('/run/pose180-resident.lock').open('a') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        b.need(not owners() and not b.owners(),'Device still owned; no BOOT operation')
        if a.action=='audit':
            files=b.fat_files();print(json.dumps(dict(boot_id=b.boot_id(),files=files,device_owners=[])));return
        if a.action in ('install','fallback'):
            before,after=(baseline,candidate) if a.action=='install' else (candidate,baseline)
            source=ROOT/'boot/BOOT.BIN' if a.action=='install' else b.META/'BOOT-before.readback.bin'
            b.need(source.is_file(),'Missing latest BOOT or verified pre-install readback; operation refused')
            audit=b.audit(before)
            b.save_new(b.META/(a.action+'-before.json'),audit)
            if a.action=='install':
                b.fat_files(b.META/'BOOT-before.readback.bin')
                b.need(b.digest(b.META/'BOOT-before.readback.bin')==baseline,'Actual backup differs')
            value=b.replace_boot(source,before,after,a.action,a.action+'.json')
            if a.action=='install':
                atomic(ROOT/'board/next-boot.json',dict(previous_boot_id=b.boot_id(),BOOT_sha256=candidate))
            print(json.dumps({k:value[k] for k in ('passed','boot_id','BOOT_sha256','boot_partition_unmounted')}))
        else:
            expected=candidate if a.action=='reboot' else baseline
            b.audit(expected)
            b.reserve(a.action,dict(BOOT_sha256=expected))
            process=subprocess.Popen(['/bin/sh','-c','sleep 2; exec /sbin/reboot'],stdin=subprocess.DEVNULL,
                stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,start_new_session=True)
            print(json.dumps(dict(reboot_issued=True,pid=process.pid,previous_boot_id=b.boot_id(),BOOT_sha256=expected)))
if __name__=='__main__':main()
