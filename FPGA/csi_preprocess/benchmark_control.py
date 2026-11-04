"""Finite GP-only benchmark, exclusive, matching candidate boot, no SDK."""
import fcntl, json, subprocess, sys, time
from pathlib import Path
ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / 'board'))
import startup
with Path('/run/pose180-resident.lock').open('a') as lock:
    fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    # Same public deployment checks used by the SDK launcher. No functional
    # startup consumer or NPU call is executed by this preflight/benchmark.
    identity = json.loads((ROOT / 'board/identity.json').read_text())
    current = startup.preflight(ROOT / 'board', identity)
    out = ROOT / 'benchmark'
    out.mkdir(exist_ok=False)
    frequency = {}
    for name in ('scaling_governor', 'scaling_cur_freq', 'cpuinfo_max_freq'):
        path = Path('/sys/devices/system/cpu/cpu0/cpufreq') / name
        if path.exists():
            frequency[name] = path.read_text().strip()
    (out / 'started.json').write_text(json.dumps(dict(boot_id=current, started=time.time(), SDK_initialized=False,
        CPU_frequency=frequency, kernel=subprocess.check_output(['uname', '-a'], universal_newlines=True).strip(),
        order='alternating PS-first / PL-first; same input each pair'), indent=2))
    argv = [str(ROOT / 'board/board_benchmark'), str(ROOT / 'board/dataset.piwcsi2'), identity['hardware_profile'],
        str(out / 'result.json')]
    with (out / 'native.log').open('w') as f:
        p = subprocess.Popen(argv, stdout=f, stderr=subprocess.STDOUT)
        (out / 'process.json').write_text(json.dumps(dict(pid=p.pid, argv=argv, automatic_kill=False)))
        rc = p.wait()
    (out / 'exit.json').write_text(json.dumps(dict(native_exit=rc, finished=time.time())))
    print((out / 'native.log').read_text())
    if (out / 'result.json').exists():
        print((out / 'result.json').read_text())
    sys.exit(rc)
