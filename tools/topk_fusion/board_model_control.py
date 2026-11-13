"""On-board controller for one bounded old-model comparison.

Stages are explicit commands; there is no restart, inference autostart, timeout
kill, or BOOT write. Original output files and native failures are retained.
"""

import argparse
import fcntl
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time


ROOT = Path(__file__).resolve().parent
BOOT_SHA = "23922f488d9d4842f217f1b318624c82607e35c6dc0c0b2ea3c803ca4023aa35"
LIBRARIES = {
    "libicraft_hostbackend.so": "d0fbf6c81e5b57b4a908f11aad27571b8f2e68a3ede7ba33c9a4f783ba266130",
    "libicraft_zg330backend.so": "592ad913737a6d661ab9d913ff16617c8fb6bf65cc0dc8929c6886303c498a57",
    "libicraft_xrt.so": "a29e4eee6106afae0b6aada4a07e85416ac6dfc3e74083033ae5d1411749dc96",
}


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def read_json(path):
    return json.loads(path.read_text())


def save_new(name, value):
    with (ROOT / name).open("x") as stream:
        json.dump(value, stream, indent=2)
        stream.write("\n")


def boot_id():
    return Path("/proc/sys/kernel/random/boot_id").read_text().strip()


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def owners():
    result = []
    for fd in Path("/proc").glob("[0-9]*/fd/*"):
        try:
            target = os.readlink(str(fd))
            if target.startswith(("/dev/axi", "/dev/udmabuf", "/dev/u-dma", "/dev/video", "/dev/mem")):
                result.append([str(fd), target])
        except FileNotFoundError:
            pass
    return result


def verify_files():
    manifest = read_json(ROOT / "manifest.template.json")
    for name, expected in manifest["files"].items():
        require(digest(ROOT / name) == expected, "Package identity differs: " + name)
    return manifest


def verify_idle():
    require(not owners(), "A device owner is still present")
    with open("/run/pose180-resident.lock", "a") as lease:
        fcntl.flock(lease, fcntl.LOCK_EX | fcntl.LOCK_NB)


def inspect():
    active = Path("/run/pose180-resident.active.json")
    return dict(boot_id=boot_id(), device_owners=owners(),
                active=read_json(active) if active.exists() else None,
                memory=Path("/proc/meminfo").read_text(),
                state=read_json(ROOT / "state.json") if (ROOT / "state.json").exists() else None,
                build=read_json(ROOT / "build-result.json") if (ROOT / "build-result.json").exists() else None,
                build_log=(ROOT / "build.log").read_text(errors="replace")[-2500:] if (ROOT / "build.log").exists() else None,
                native_log=(ROOT / "native.log").read_text(errors="replace")[-5500:] if (ROOT / "native.log").exists() else None)


def build_job():
    commands = [["cmake", "-S", str(ROOT), "-B", str(ROOT / "build"), "-DCMAKE_BUILD_TYPE=RelWithDebInfo"],
                ["cmake", "--build", str(ROOT / "build"), "--target", "topk_model_board_validation",
                 "shared_binding_validation", "parameter_layout_probe", "test_parameter_image", "--parallel", "1"],
                [str(ROOT / "build/test_parameter_image")],
                [str(ROOT / "build/parameter_layout_probe"), str(ROOT / "model.json"), str(ROOT / "model.raw")],
                [str(ROOT / "build/shared_binding_validation"), str(ROOT)]]
    results = []
    for command in commands:
        print("COMMAND", json.dumps(command), flush=True)
        code = subprocess.call(command)
        results.append(dict(command=command, native_exit=code))
        temporary = ROOT / "build-result.json.tmp"
        temporary.write_text(json.dumps(results, indent=2))
        temporary.replace(ROOT / "build-result.json")
        if code:
            break


def build():
    verify_files()
    require(not (ROOT / "build-launch.json").exists(), "Build already launched; inspect original process")
    with (ROOT / "build.log").open("xb") as stream:
        process = subprocess.Popen([sys.executable, "-u", __file__, "build-job"], cwd=str(ROOT),
                                   stdin=subprocess.DEVNULL, stdout=stream, stderr=subprocess.STDOUT,
                                   start_new_session=True)
    record = dict(pid=process.pid, boot_id=boot_id(), sdk_started=False,
                  start_ticks=Path("/proc/{}/stat".format(process.pid)).read_text().split(") ", 1)[1].split()[19])
    save_new("build-launch.json", record)
    return record


def prepare_reboot():
    verify_idle()
    active = read_json(Path("/run/pose180-resident.active.json"))
    require(active["boot_id"] == boot_id(), "Consumed startup identity differs")
    old = Path(active["run"]).resolve()
    require(old.parent == ROOT.parent and old != ROOT, "Previous run is outside this isolated experiment")
    recovered = old / "recovery-closed.json"
    outcome = read_json(recovered if recovered.exists() else old / "outcome.json")
    require(outcome["boot_id"] == boot_id() and outcome["native_shutdown_complete"] and
            outcome["allocation_count_after"] == 0, "Preceding hardware shutdown is not proven")
    if recovered.exists():
        require(outcome["original_failure_preserved"] and outcome["lease_free"] and
                not outcome["device_owners"] and (old / "failure-before-cleanup.json").is_file(),
                "Failed-batch recovery evidence is incomplete")
    else:
        require(outcome["native_exit"] == 0, "Previous normal run did not exit successfully")
    process = read_json(old / "worker-process.json")
    stat = Path("/proc/{}/stat".format(process["pid"]))
    require(not stat.exists() or stat.read_text().split(") ", 1)[1].split()[19] != process["start_ticks"],
            "Previous native worker is still alive")
    record = dict(boot_id=boot_id(), old_run=str(old), normal_reboot_prepared=True, boot_writes=0,
                  device_owners=[], native_shutdown_complete=True)
    save_new("reboot-prepared.json", record)
    return record


def preflight():
    from board_probe import audit_fat16
    verify_idle()
    manifest = verify_files()
    require(not Path("/run/pose180-resident.active.json").exists(), "This startup was already consumed")
    previous = ROOT / "reboot-prepared.json"
    if previous.exists():
        require(read_json(previous)["boot_id"] != boot_id(), "Normal reboot has not completed")
    partition = audit_fat16("/dev/mmcblk0p1")
    boot = next(item for item in partition["files"] if item["name"].upper() == "BOOT.BIN")
    require(boot["sha256"] == BOOT_SHA, "BOOT identity differs")
    actual_libraries = {name: digest(Path("/usr/lib/aarch64-linux-gnu") / name) for name in LIBRARIES}
    require(actual_libraries == LIBRARIES, "Installed SDK library identity differs")
    packages = subprocess.check_output(["dpkg-query", "-W", "-f=${Package} ${Architecture} ${Version}\n",
                                        "icraft:arm64", "customop:arm64"]).decode()
    report = dict(boot_id=boot_id(), boot_file=boot, libraries=actual_libraries, packages=packages,
                  memory=Path("/proc/meminfo").read_text(), device_owners=[], sdk_opens=0)
    save_new("preflight.json", report)
    manifest["boot_id"] = boot_id()
    save_new("manifest.json", manifest)
    return report


def launch():
    verify_idle()
    verify_files()
    manifest = read_json(ROOT / "manifest.json")
    require(manifest["boot_id"] == boot_id(), "Prepared boot differs")
    require(not Path("/run/pose180-resident.active.json").exists(), "Startup already consumed")
    require(not (ROOT / "launch.json").exists() and not (ROOT / "sdk-attempt.json").exists(), "No restart allowed")
    build_results = read_json(ROOT / "build-result.json")
    require(len(build_results) == 5 and all(item["native_exit"] == 0 for item in build_results),
            "Build/host tests/mock deployment did not pass")
    binary = ROOT / "build/topk_model_board_validation"
    loader = subprocess.run([str(binary)], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    (ROOT / "loader-check.txt").write_bytes(loader.stdout)
    require(loader.returncode == 2 and b"Usage:" in loader.stdout, "Native loader check failed")
    with (ROOT / "supervisor.log").open("xb") as log:
        process = subprocess.Popen([sys.executable, "-u", str(ROOT / "board_supervisor.py"), "model"],
                                   cwd=str(ROOT), stdin=subprocess.DEVNULL, stdout=log,
                                   stderr=subprocess.STDOUT, start_new_session=True)
    record = dict(pid=process.pid, boot_id=boot_id(), binary_sha256=digest(binary),
                  maximum_sdk_opens=1, maximum_forward_calls=88, maximum_frames=22)
    save_new("launch.json", record)
    return record


def advance():
    state = read_json(ROOT / "state.json")
    require(state["boot_id"] == boot_id() and state["release_available"], "No reviewed completed boundary")
    gates = {"ready_for_reference": ("run_reference.json", 0, 0),
             "reference_review": ("run_candidate.json", 1, 3),
             "correctness_review": ("run_benchmark.json", 2, 8),
             "release_review": ("release.json", 22, 88)}
    gate, frames, forwards = gates[state["phase"]]
    require(state["frames"] == frames and state["forward_calls"] == forwards, "Actual run budget differs")
    bindings = read_json(ROOT / "bindings.json")
    require(len(bindings) == 5 and sum(len(stage["bindings"]) for stage in bindings) == 27 and
            all(row["direct"] for stage in bindings for row in stage["bindings"]), "Direct bindings differ")
    if frames:
        results = read_json(ROOT / "results.json")
        require(len(results) == frames and all(item["simulator_bitwise_equal"] and item["board_cpu_bitwise_equal"]
                                              for item in results), "Strict model comparison did not pass")
        for item in results:
            directory = ROOT / "frames" / (str(item["frame"]) + "_" + item["mode"])
            for filename, expected in (("scores.actual.bin", "expected_3483.bin"), ("poses.actual.bin", "expected_3487.bin")):
                require((directory / filename).read_bytes() == (ROOT / expected).read_bytes(), "Preserved first output differs")
    review = dict(boot_id=boot_id(), frames=frames, forward_calls=forwards, hardware_reviewed=True,
                  native_callbacks_and_applied_sync_complete=True, public_ddr_and_idma_idle=True,
                  synchronous_io_complete=True)
    save_new(gate, review)
    return dict(gate=gate, **review)


def release_error():
    state = read_json(ROOT / "state.json")
    require(state["boot_id"] == boot_id() and state["phase"] == "retained_after_error" and
            state["release_available"], "Native completion proof does not permit error cleanup")
    require(0 <= state["forward_calls"] <= 88 and 0 <= state["frames"] <= 22, "Run budget differs")
    save_new("failure-before-cleanup.json", state)
    review = dict(boot_id=boot_id(), frames=state["frames"], hardware_reviewed=True,
                  forward_calls=state["forward_calls"], numerical_pass=False,
                  completed_native_operations=True, dma_and_npu_idle=True)
    save_new("release.json", review)
    return review


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("inspect", "build", "build-job", "prepare-reboot", "preflight", "launch", "advance", "release-error"))
    action = parser.parse_args().action.replace("-", "_")
    print(json.dumps(globals()[action](), indent=2), flush=True)
