"""Local CSI numerical and RTL verification; no device access."""
from pathlib import Path
import sys, subprocess, json, math, time
ROOT = Path(__file__).resolve().parents[2]
SRC = Path(__file__).resolve().parent
WORK = ROOT / '.local/csi-preprocess-20261031-r3'
V = Path('D:/vivado18.3/Vivado/2018.3/bin')
D = 'C:/Program Files/Docker/Docker/resources/bin/docker.exe'
def run(name, argv, cwd):
    with (cwd / (name + '.log')).open('w') as f:
        p = subprocess.Popen(list(map(str, argv)), cwd=cwd, stdout=f, stderr=subprocess.STDOUT)
        (cwd / (name + '-process.json')).write_text(json.dumps(dict(pid=p.pid, argv=list(map(str, argv)),
            started=time.time(), automatic_kill=False), indent=2))
        rc = p.wait()
    (cwd / (name + '-exit.json')).write_text(json.dumps(dict(native_exit=rc)))
    print(name, rc, flush=True)
    if rc:
        print((cwd / (name + '.log')).read_text(errors='replace')[-5000:])
        raise SystemExit(rc)
def main():
    (WORK / 'reports').mkdir(parents=True, exist_ok=True)
    rows = [f"5'd{k}:atan_step=32'sd{round(math.atan(2**-k)/math.pi*2**30)};" for k in range(31)]
    (SRC / 'atan_table.vh').write_text('function signed [31:0] atan_step(input [4:0] k);begin case(k)\n' + '\n'.join(rows) + '\ndefault:atan_step=0;endcase end endfunction\n')
    mode = sys.argv[1]
    r = WORK / 'reports' / (mode + '-' + time.strftime('%H%M%S'))
    r.mkdir(exist_ok=False)
    (WORK / 'reports' / (mode + '-latest.json')).write_text(json.dumps(dict(directory=str(r))))
    base = '/workspace/' + WORK.relative_to(ROOT).as_posix()
    if mode == 'numeric':
        p = '/workspace/software/pose180_pipeline/src/preprocess'
        run('compile', [D, 'exec', 'FPAI', 'g++', '-O2', '-std=c++17', '-ffp-contract=off', '-I/workspace/FPGA/csi_preprocess',
            '-I' + p,
            '/workspace/FPGA/csi_preprocess/numeric_test.cpp', '/workspace/FPGA/csi_preprocess/polar_model.cpp',
            p + '/polar_finish.cpp', p + '/preprocess.cpp', '-o', base + '/numeric_test'], r)
        dataset = '/workspace/.local/skeleton-overlay-20261031-r2/pose180-skeleton-overlay-20261031-r2/board/dataset.piwcsi2'
        run('compare', [D, 'exec', 'FPAI', base + '/numeric_test', dataset, base + '/reports/vectors.hex',
            base + '/reports/numeric.json'], r)
    elif mode in ('sim', 'batch'):
        import shutil
        vectors = WORK / 'reports/vectors.hex'
        if not vectors.exists():
            vectors = ROOT / '.local/csi-preprocess-20261031-r1/reports/vectors.hex'
        shutil.copyfile(vectors, r / 'vectors.hex')
        (r / 'run.tcl').write_text('run all\nquit\n')
        top = 'tb_polar' if mode == 'sim' else 'tb_batch'
        run('compile', [V / 'xvlog.bat', '-sv', '-i', SRC, SRC / 'polar.sv', SRC / 'batch.sv', SRC / (top + '.sv')],
            r)
        run('elaborate', [V / 'xelab.bat', top, '-s', 'polar_sim', '-timescale', '1ns/1ps', '-mt', '2'],
            r)
        run('simulate', [V / 'xsim.bat', 'polar_sim', '-tclbatch', 'run.tcl'], r)
        text = (r / 'simulate.log').read_text()
        print(text[-2000:])
        if ('CSI_POLAR_PASS' if mode == 'sim' else 'CSI_BATCH_PASS') not in text or 'Fatal' in text:
            raise SystemExit(1)
    else:
        raise SystemExit('numeric or sim')
if __name__ == '__main__':
    main()
