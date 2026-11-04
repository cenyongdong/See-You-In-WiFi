"""Compile the explicit probe-free SDK owner using the installed FPAI toolchain."""
from pathlib import Path
import json
import subprocess
import time

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / '.local/hdmi-probe-free-drain-20261026-r1/software-build'
OUT.mkdir(parents=True, exist_ok=True)
steps = []

def run(stage, *args):
    started = time.monotonic()
    with (OUT / (stage + '.stdout.log')).open('xb') as out, (OUT / (stage + '.stderr.log')).open('xb') as err:
        child = subprocess.run(['docker', *args], stdout=out, stderr=err)
    row = dict(stage=stage, argv=args, native_exit=child.returncode, seconds=time.monotonic() - started)
    steps.append(row)
    (OUT / 'execution.json').write_text(json.dumps(steps, indent=2) + '\n')
    print(json.dumps(row), flush=True)
    if child.returncode:
        raise RuntimeError((OUT / (stage + '.stderr.log')).read_text(errors='replace')[-3000:])

started_here = subprocess.check_output(['docker', 'inspect', '--format', '{{.State.Status}}', 'FPAI']).strip() == b'exited'
if started_here:
    run('start', 'start', 'FPAI')
try:
    arm = '/workspace/.local/hdmi-probe-free-drain-20261026-r1/software-build/arm64'
    run('configure', 'exec', 'FPAI', 'cmake', '-S', '/workspace/software/pose180_pipeline', '-B', arm,
        '-DCMAKE_SYSTEM_NAME=Linux', '-DCMAKE_SYSTEM_PROCESSOR=aarch64', '-DCMAKE_CXX_COMPILER=aarch64-linux-gnu-g++',
        '-DCMAKE_PREFIX_PATH=/usr/cmake', '-DCMAKE_BUILD_TYPE=Release', '-DPOSE180_BUILD_SDK=ON', '-DPOSE180_DEMO_PROBE_FREE_DRAIN=ON')
    run('compile', 'exec', 'FPAI', 'cmake', '--build', arm, '--target', 'pose180_demo', '--parallel',
        '2')
    symbols = subprocess.check_output(['docker', 'exec', 'FPAI', 'aarch64-linux-gnu-nm', '-C', arm + '/pose180_demo']).decode()
    forbidden = [name for name in ('pose::r9_startup', 'Mapping::', 'read_input_bridge', 'input_read_sdk',
        'host_cpu_adapter') if name in symbols]
    if forbidden:
        raise RuntimeError('Diagnostic mapping/legacy bridge remains: ' + str(forbidden))
    required = [name for name in ('pose::hdmi::Output::close', 'pose::hdmi::Output::verifyMemory', 'pose180_pipeline::Runtime::infer') if name in symbols]
    if len(required) != 3:
        raise RuntimeError('Functional SDK/HDMI ownership path missing')
    (OUT / 'symbol-review.json').write_text(json.dumps(dict(forbidden_present=forbidden, functional_symbols=required),
        indent=2) + '\n')
finally:
    if started_here:
        run('stop', 'stop', 'FPAI')
