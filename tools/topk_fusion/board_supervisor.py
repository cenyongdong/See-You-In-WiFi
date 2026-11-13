"""Preserve a finite board worker's native exit without imposing a kill timeout."""

import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time


def write_exclusive(path, value):
    with path.open("x") as stream:
        json.dump(value, stream, indent=2)
        stream.write("\n")


def main():
    root = Path(__file__).resolve().parent
    boot = Path("/proc/sys/kernel/random/boot_id").read_text().strip()
    mode = sys.argv[1] if len(sys.argv) == 2 else "python"
    executables = {"native": "build/topk_board_validation", "model": "build/topk_model_board_validation"}
    if mode not in ("python", *executables):
        raise ValueError("Unknown finite worker mode")
    native = mode in executables
    worker_file = root / executables[mode] if native else root / "board_worker.py"
    command = [str(worker_file), str(root)] if native else [sys.executable, "-u", str(worker_file)]
    with (root / "dmesg.before.txt").open("xb") as stream:
        subprocess.run(["dmesg"], stdout=stream, stderr=subprocess.STDOUT, check=True)
    with (root / "native.log").open("xb") as log:
        worker = subprocess.Popen(command,
                                  cwd=str(root), stdin=subprocess.DEVNULL,
                                  stdout=log, stderr=subprocess.STDOUT)
        start_ticks = Path("/proc/{}/stat".format(worker.pid)).read_text().split(") ", 1)[1].split()[19]
        write_exclusive(root / "worker-process.json", dict(
            boot_id=boot, pid=worker.pid, start_ticks=start_ticks,
            supervisor_pid=os.getpid(), started_unix=time.time(),
            command=command, worker_sha256=hashlib.sha256(worker_file.read_bytes()).hexdigest()))
        native_exit = worker.wait()
    write_exclusive(root / "native-exit.json", dict(
        boot_id=boot, pid=worker.pid, start_ticks=start_ticks,
        native_exit=native_exit, ended_unix=time.time(), automatic_retry=False))
    return native_exit


if __name__ == "__main__":
    sys.exit(main())
