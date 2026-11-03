"""Relocate and run the qualified FPGA flow; never accesses a board or SDK."""
from pathlib import Path
import argparse
import json
import os
import shutil
import subprocess
import time

STAGES = ('synthesis-banked', 'opt-banked', 'place-csi-incremental',
          'route-csi-incremental', 'report-closure', 'bit-closure', 'procise')
TEXT = {'.tcl', '.xpr', '.xci', '.xml', '.bif', '.bat', '.cfg', '.json'}


def relocate(data, suffix, mappings):
    if suffix.lower() not in TEXT:
        return data
    try:
        text = data.decode('utf-8-sig')
    except UnicodeDecodeError:
        return data  # Encrypted vendor Tcl is preserved byte for byte.
    import re
    for old, new in sorted(mappings.items(), key=lambda x: -len(x[0])):
        text = re.sub(re.escape(old), lambda _m, value=new: value, text, flags=re.I)
    return text.encode('utf-8')


def prepare(package, output, procise):
    if output.exists():
        raise FileExistsError('Choose a fresh build directory: ' + str(output))
    metadata = json.loads((package / 'metadata/fpga-inputs.json').read_text(encoding='utf-8'))
    output.mkdir(parents=True)
    inputs, factory = output / 'inputs', output / 'factory'
    mapping = {'@ROOT@': inputs.as_posix(), '@FACTORY@': factory.as_posix(), '@BUILD@': output.as_posix()}
    for old, target in metadata['legacy_paths'].items():
        for key, value in mapping.items():
            target = target.replace(key, value)
        mapping[old] = target
    for rel in metadata['project_files']:
        src, dst = package / rel, inputs / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        dst.write_bytes(relocate(src.read_bytes(), src.suffix, mapping))
    # Preserve the vendor's internal relative layout in a generated view. No
    # hard links: IP tools must never be able to modify the packaged inputs.
    for original, rel in metadata['factory_files'].items():
        src, dst = package / rel, factory / original
        dst.parent.mkdir(parents=True, exist_ok=True)
        dst.write_bytes(relocate(src.read_bytes(), src.suffix, mapping))
    logs = output / 'logs'
    logs.mkdir()
    for rel in ('reports/physical', 'reports/pipeline-physical', 'reports/physical-final-closure',
                'reports/physical-final-closure/frames', 'ip_patch', 'ip-cache', 'fpai_demo_vivado.runs/impl_pose_filter'):
        (output / rel).mkdir(parents=True, exist_ok=True)
    for stage in STAGES:
        src = package / 'FPGA/scripts' / (stage + '.tcl.in')
        dst = output / (stage + '.tcl')
        dst.write_bytes(relocate(src.read_bytes(), '.tcl', mapping))
    (output / 'candidate.bif').write_bytes(relocate(
        (package / 'FPGA/boot/candidate.bif.in').read_bytes(), '.bif', mapping))
    # The factory post-bit hook is deliberately deferred to the explicit
    # Procise stage, retaining the existing routed-context guard.
    launcher = output / 'call_procise_disable_icap.bat'
    launcher.write_text('@echo off\n' +
        'set "PROCISE_DIR=' + procise.as_posix() + '"\n' +
        'set "TCL_LIBRARY=%PROCISE_DIR%/tcl8.4"\n' +
        'set "PATH=%PROCISE_DIR%/dll;%PROCISE_DIR%/bin;%PATH%"\n' +
        'set "ICTIME_HOME=%PROCISE_DIR%"\nset "APP_DIR=%PROCISE_DIR%"\n' +
        'set "FMSH_DB=%PROCISE_DIR%/db"\n' +
        '"%PROCISE_DIR%/bin/procise.exe" "' + (output / 'procise.tcl').as_posix() + '"\n', encoding='utf-8')
    plan = {'package_root': str(package), 'build_root': str(output), 'procise': str(procise),
            'stages': list(STAGES), 'project_files': len(metadata['project_files']),
            'vendor_files': len(metadata['factory_files']), 'device_operations': 0}
    (output / 'build-plan.json').write_text(json.dumps(plan, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(plan), flush=True)


def run_stage(output, stage, vivado):
    plan = json.loads((output / 'build-plan.json').read_text(encoding='utf-8'))
    record = output / 'logs' / (stage + '.json')
    if record.exists():
        raise FileExistsError('Preserve prior stage results; use a fresh build directory: ' + str(record))
    if stage == 'procise':
        command = ['cmd.exe', '/d', '/c', str(output / 'call_procise_disable_icap.bat')]
    else:
        command = [str(vivado), '-mode', 'batch', '-nojournal', '-log',
                   str(output / 'logs' / (stage + '.vivado.log')), '-source', str(output / (stage + '.tcl'))]
    started = time.time()
    with (output / 'logs' / (stage + '.stdout.log')).open('xb') as stream:
        process = subprocess.Popen(command, cwd=output, stdout=stream, stderr=subprocess.STDOUT)
        info = {'stage': stage, 'pid': process.pid, 'command': command, 'started': started, 'state': 'running'}
        record.write_text(json.dumps(info, indent=2), encoding='utf-8')
        print(json.dumps(info), flush=True)
        rc = process.wait()  # No outer timeout or automatic process-tree kill.
    info.update(state='completed', exit_code=rc, seconds=time.time() - started)
    record.write_text(json.dumps(info, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(info), flush=True)
    if rc:
        raise SystemExit(rc)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=('prepare', 'run'))
    parser.add_argument('--build-dir', type=Path, required=True)
    parser.add_argument('--stage', choices=(*STAGES, 'all'), default='all')
    parser.add_argument('--vivado', type=Path, default=Path('D:/vivado18.3/Vivado/2018.3/bin/vivado.bat'))
    parser.add_argument('--procise', type=Path, default=Path('C:/FudanMicro/Procise'))
    args = parser.parse_args()
    package, output = Path(__file__).resolve().parents[1], args.build_dir.resolve()
    if args.action == 'prepare':
        prepare(package, output, args.procise.resolve())
    else:
        stages = STAGES if args.stage == 'all' else (args.stage,)
        for stage in stages:
            run_stage(output, stage, args.vivado)


if __name__ == '__main__':
    main()
