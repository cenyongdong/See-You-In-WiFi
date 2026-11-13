"""Local tool execution for the independent TopK experiment (no device access)."""

import json
import os
from pathlib import Path
import subprocess
import time


ROOT = Path(__file__).resolve().parents[2]
ICRAFT_BIN = Path("C:/Icraft/CLI v3.39.0/bin")
ICRAFT_PYTHON = Path("C:/Users/cenyongdong/miniconda3/envs/Icraft-env/python.exe")
VIVADO_BIN = Path("D:/vivado18.3/Vivado/2018.3/bin")
WORK = ROOT / ".local/topk-fusion-20261113"


def save_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, allow_nan=False) + "\n", encoding="utf-8")


def icraft_paths():
    manifest = ROOT / ".local/icraft-runtime/cuda-11.8.0/runtime-manifest.json"
    runtime = json.loads(manifest.read_text(encoding="utf-8"))
    paths = [str(ICRAFT_BIN)]
    for component in runtime["components"]:
        paths.extend(component["bin_dirs"])
    if any(not Path(path).is_dir() for path in paths):
        raise FileNotFoundError("An existing Icraft runtime directory is missing")
    return paths


def icraft_environment():
    env = dict(os.environ)
    env.update(PATH=os.pathsep.join(icraft_paths() + [env.get("PATH", "")]),
               OMP_NUM_THREADS="2", MKL_NUM_THREADS="2")
    return env


def load_xir():
    # Keep directory handles alive while SDK objects and DLLs are in use.
    handles = [os.add_dll_directory(path) for path in icraft_paths()]
    from icraft import xir
    return xir, handles


def run_native(name, argv, directory, env=None):
    """Preserve native exit codes; a tool-call timeout never kills the process."""
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    args = list(map(str, argv))
    started = time.monotonic()
    log_path = directory / (name + ".log")
    with log_path.open("xb") as log:
        child = subprocess.Popen(args, cwd=directory, env=env, stdout=log,
                                 stderr=subprocess.STDOUT,
                                 creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
        save_json(directory / (name + ".process.json"),
                  dict(pid=child.pid, argv=args, started=time.time(), automatic_kill=False))
        code = child.wait()
    result = dict(native_exit=code, seconds=time.monotonic() - started)
    save_json(directory / (name + ".exit.json"), result)
    print(json.dumps(dict(stage=name, **result)), flush=True)
    if code:
        print(log_path.read_text(errors="replace")[-6000:], flush=True)
        raise RuntimeError("{} exited with {}: {}".format(name, code, log_path))
    return result
