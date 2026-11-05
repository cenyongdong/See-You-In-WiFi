"""Finalize this fresh r7 reproduction only after all seven native stages succeed."""
from pathlib import Path
import hashlib
import json
import shutil
import subprocess
import sys
import time

WORK = Path(__file__).resolve().parent
HARDWARE = WORK / 'hardware'
PACKAGE = WORK / 'source/pose180-current-sources-20261104-r7'


def digest(path):
    value = hashlib.sha256()
    with path.open('rb') as stream:
        for data in iter(lambda: stream.read(1048576), b''):
            value.update(data)
    return value.hexdigest()


def main():
    plan = json.loads((HARDWARE / 'build-plan.json').read_text())
    stages = [json.loads((HARDWARE / 'logs' / (stage + '.json')).read_text())
              for stage in plan['stages']]
    assert all(row.get('state') == 'completed' and row.get('exit_code') == 0 for row in stages)
    for label, command in (
        ('post-build-source-integrity', [sys.executable, str(PACKAGE / 'tools/check_package.py')]),
        ('physical-qualification', [sys.executable, str(WORK / 'qualify_hardware.py')]),
    ):
        with (WORK / (label + '.log')).open('xb') as stream:
            result = subprocess.run(command, stdout=stream, stderr=subprocess.STDOUT)
        if result.returncode:
            raise RuntimeError(label + ' failed; inspect original log')

    boot = WORK / 'boot'
    boot.mkdir()
    output = HARDWARE / 'fpai_demo_vivado.runs/impl_pose_filter'
    # 保留已部署 BOOT 的映像名称，避免改动 PL 分区以外的映像名称表。
    adapted = output / 'ai7030_edif_top_disable_icap.bit'
    boot_bit = boot / 'ai7030_top_disable_icap.bit'
    shutil.copyfile(adapted, boot_bit)
    bif = boot / 'candidate.bif'
    bif.write_text((HARDWARE / 'candidate.bif').read_text().replace(
        adapted.as_posix(), boot_bit.as_posix()))
    tcl = boot / 'generate.tcl'
    tcl.write_text('if {[catch {\nset_device JFMQL30TAI676H\ncreate_boot_image {' +
                   bif.as_posix() + '} {' + (boot / 'BOOT.BIN').as_posix() +
                   '} -fmql\n} message]} {puts $message; exit 1}\nexit\n')
    launcher = boot / 'generate.bat'
    launcher.write_text((HARDWARE / 'call_procise_disable_icap.bat').read_text().replace(
        (HARDWARE / 'procise.tcl').as_posix(), tcl.as_posix()))
    command = ['cmd.exe', '/d', '/c', str(launcher)]
    started = time.time()
    with (boot / 'native.log').open('xb') as stream:
        result = subprocess.run(command, cwd=boot, stdout=stream, stderr=subprocess.STDOUT)
    record = dict(command=command, native_exit=result.returncode, seconds=time.time()-started)
    (boot / 'native.json').write_text(json.dumps(record, indent=2)+'\n')
    assert result.returncode == 0, record
    assert (boot / 'BOOT.BIN').stat().st_size == 7023552
    sys.path.insert(0, str(WORK.parents[1] / 'tools/pose-v1'))
    from inspect_selected_boot import bit_payload
    payload, header = bit_payload(adapted.read_bytes())
    baseline = WORK.parents[1] / 'Deliverables/pose180-csi-release-20261031-r4/boot/BOOT.BIN'
    assert digest(baseline) == '23922f488d9d4842f217f1b318624c82607e35c6dc0c0b2ea3c803ca4023aa35'
    old, new = baseline.read_bytes(), (boot / 'BOOT.BIN').read_bytes()
    offset, end = 186816, 6167280
    swapped = b''.join(new[i:i+4][::-1] for i in range(offset, end, 4))
    composition = dict(PL_offset=offset, PL_bytes=end-offset,
        payload_bytes=len(payload), bit_header=header,
        PL_matches_new_Procise_bit=swapped[:len(payload)] == payload,
        non_PL_identical_to_r4=old[:offset] == new[:offset] and old[end:] == new[end:],
        padding_identical=old[offset+len(payload):end] == new[offset+len(payload):end],
        firmware_inputs={name:digest(HARDWARE/'inputs/FPGA/boot'/name)
                         for name in ('FSBL251210_ddr400_demo.out','bl31.elf','u-boot')})
    (boot/'composition.json').write_text(json.dumps(composition,indent=2)+'\n')
    assert len(payload) == 5980460 and composition['PL_matches_new_Procise_bit']
    assert composition['non_PL_identical_to_r4'] and composition['padding_identical']
    artifacts = dict(raw_bit=output/'ai7030_edif_top.bit',
                     procise_bit=output/'ai7030_edif_top_disable_icap.bit',
                     BOOT=boot/'BOOT.BIN',
                     application=WORK/'application/pose180_demo',
                     routed_checkpoint=HARDWARE/'pipeline-routed-csi-incremental.dcp')
    identity = dict(source=json.loads((WORK/'download.json').read_text()),
                    stages=stages, target='JFMQL30TAI676H', board_tested=False,
                    artifacts={name:dict(path=str(path), bytes=path.stat().st_size,
                                         sha256=digest(path)) for name,path in artifacts.items()})
    (WORK/'local-result.json').write_text(json.dumps(identity,indent=2)+'\n')
    print(json.dumps(identity['artifacts'], indent=2), flush=True)


if __name__ == '__main__':
    main()
