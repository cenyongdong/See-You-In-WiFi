"""Owned-board SSH using existing host identity and memory-only authentication.

Every operation keeps its command, native status and full stdout/stderr. A local
SSH timeout never proves that remote hardware work has stopped. No retry, forced
kill, BOOT write or SDK initialization is performed by this transport.
"""

import argparse
import importlib.util
import json
from pathlib import Path
import shlex
import sys

from runtime import ROOT, save_json

sys.path.insert(0, str(ROOT / "tools"))
from device_credentials import credentials

HOST = "192.168.126.49"
REMOTE_ROOT = "/root/topk-fusion-20261113-r1"
KNOWN_KEY = "AAAAC3NzaC1lZDI1NTE5AAAAIJEJjNFzYnjluPa+kwz4imgxJHRfVt462buoRP0JRtu6"


def run(directory, label, command, data=None, timeout=60):
    directory = Path(directory).resolve()
    directory.mkdir(parents=True, exist_ok=True)
    receipt = directory / (label + ".ssh.json")
    if receipt.exists() or Path(label).name != label:
        raise ValueError("Use a new operation label")
    known = Path("C:/Users/cenyongdong/.ssh/known_hosts")
    expected = [HOST, "ssh-ed25519", KNOWN_KEY]
    if not any(line.split()[:3] == expected for line in known.read_text().splitlines()):
        raise ValueError("Existing board host identity is unavailable")
    (directory / "known_hosts").write_text(" ".join(expected) + "\n", encoding="ascii")
    source = ROOT / "tools/nexmon/host/router_transport.py"
    spec = importlib.util.spec_from_file_location("topk_ssh_transport", source)
    transport = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(transport)
    (directory / "askpass.sh").write_text(
        '#!/bin/sh\nexec "' + Path(sys.executable).as_posix() + '" "' + source.as_posix() + '" askpass "$@"\n',
        encoding="utf-8", newline="\n")
    user, password = credentials(HOST, "root")
    if user != "root":
        raise ValueError("Board administrator identity differs")
    save_json(receipt, dict(command=command, input_bytes=len(data) if data else 0,
                           timeout_seconds=timeout, state="started", automatic_retry=False))
    try:
        code, stdout, stderr = transport.ssh_run(directory, user, password.encode("utf-8"),
                                                command, data, timeout, host=HOST, connect_timeout=min(timeout, 15))
    finally:
        password = ""
    (directory / (label + ".stdout")).write_bytes(stdout)
    (directory / (label + ".stderr")).write_bytes(stderr)
    save_json(receipt, dict(command=command, input_bytes=len(data) if data else 0,
                           timeout_seconds=timeout, native_exit=code, automatic_retry=False,
                           remote_command_returned=code == 0,
                           hardware_completion_proven=False))
    if code:
        print(stderr.decode(errors="replace")[-2000:], flush=True)
        raise RuntimeError("SSH operation failed; inspect retained output before any retry")
    return stdout


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("directory", type=Path)
    parser.add_argument("label")
    parser.add_argument("mode", choices=("python", "shell", "put", "get"))
    parser.add_argument("local", type=Path)
    parser.add_argument("--remote")
    parser.add_argument("--timeout", type=int, default=60)
    args = parser.parse_args()
    if not 1 <= args.timeout <= 600:
        parser.error("SSH observation budget must be in [1,600] seconds")
    if args.mode in ("python", "shell"):
        command = "python3 -" if args.mode == "python" else "sh -s"
        output = run(args.directory, args.label, command, args.local.read_bytes(), args.timeout)
        print(output.decode(errors="replace")[-7000:])
    else:
        if not args.remote or not args.remote.startswith(REMOTE_ROOT + "/") or ".." in args.remote.split("/"):
            parser.error("Transfers must remain in the new TopK board directory")
        path = shlex.quote(args.remote)
        if args.mode == "put":
            run(args.directory, args.label, "umask 077; test ! -e " + path + " && cat > " + path,
                args.local.read_bytes(), args.timeout)
        else:
            if args.local.exists():
                parser.error("Preserve prior returned data")
            output = run(args.directory, args.label, "cat " + path, timeout=args.timeout)
            args.local.write_bytes(output)
        print(json.dumps(dict(operation=args.mode, completed=True)))


if __name__ == "__main__":
    main()
