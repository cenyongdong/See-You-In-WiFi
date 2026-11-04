"""Offline CSI and overlay RTL simulation with the matching Vivado tools."""
import argparse
import json
from pathlib import Path
import shutil
import subprocess


def simulation_commands(root, vivado_bin):
    # 顺序保持为每组编译、展开、运行；记录索引继续对应既有日志编号。
    commands = []
    for top, rels in (
        ('tb_batch', ['FPGA/rtl/csi/polar.sv', 'FPGA/rtl/csi/batch_banked.sv', 'FPGA/sim/tb_batch.sv']),
        ('tb_overlay', ['FPGA/rtl/skeleton_overlay/palette_fifo.sv', 'FPGA/rtl/skeleton_overlay/overlay.sv',
        'FPGA/sim/tb_overlay.sv'])):
        commands += [
            [str(vivado_bin / 'xvlog.bat'), '-sv', '-i', str(root / 'FPGA/rtl/csi'), '-i', str(root / 'FPGA/rtl/skeleton_overlay'),
            *[str(root / p) for p in rels]],
            [str(vivado_bin / 'xelab.bat'), top, '-s', top + '_sim'],
            [str(vivado_bin / 'xsim.bat'), top + '_sim', '-tclbatch', 'run.tcl']]
    return commands


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--vivado-bin', required=True, type=Path)
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--vectors', type=Path)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    output = args.output.resolve()
    if output.exists():
        parser.error('Choose a new output directory')
    output.mkdir(parents=True)
    vectors = args.vectors or root / 'tests/fixtures/vectors.hex'
    shutil.copyfile(vectors, output / 'vectors.hex')
    (output / 'run.tcl').write_text('run all\nquit\n', encoding='utf-8')
    commands = simulation_commands(root, args.vivado_bin)
    for i, command in enumerate(commands):
        with (output / ('step-' + str(i) + '.log')).open('xb') as log:
            rc = subprocess.run(command, cwd=output, stdout=log, stderr=subprocess.STDOUT).returncode
        (output / ('step-' + str(i) + '.json')).write_text(json.dumps(dict(command=command, exit_code=rc),
            indent=2), encoding='utf-8')
        if rc:
            raise SystemExit(rc)
        print('simulation step', i, 'native exit 0', flush=True)
    for number, marker in ((2, 'CSI_BATCH_PASS'), (5, 'OVERLAY_PASS')):
        text = (output / ('step-' + str(number) + '.log')).read_text(encoding='utf-8', errors='replace')
        if marker not in text or 'Fatal:' in text:
            raise RuntimeError('Testbench did not finish successfully: ' + marker)
    print('CSI and overlay testbenches passed; synthetic/offline scope only')

if __name__ == '__main__':
    main()
