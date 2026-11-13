"""One finite, supervised NPU experiment on the owner's ZG330 board.

Public SDK allocations and completion callbacks are used unchanged. First
outputs and hardware status are preserved before numerical review. The worker
retains its device, allocations and global lease between cases; the controller
must review each result before allowing the next case or final cleanup.
Exceptions never trigger another forward, reset, forced release or retry.
"""

from datetime import timedelta
import fcntl
import hashlib
import json
import os
from pathlib import Path
import signal
import sys
import time
import traceback


def save(path, data):
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(data, indent=2, allow_nan=False) + "\n")
    temporary.replace(path)


def boot_id():
    return Path("/proc/sys/kernel/random/boot_id").read_text().strip()


def owners():
    found = []
    for fd in Path("/proc").glob("[0-9]*/fd/*"):
        try:
            target = os.readlink(str(fd))
            if target.startswith(("/dev/axi", "/dev/udmabuf", "/dev/u-dma", "/dev/video", "/dev/mem")):
                found.append([str(fd), target])
        except OSError:
            pass
    return found


class Experiment:
    def __init__(self, root, manifest):
        self.root, self.manifest = root, manifest
        self.device = self.region = self.backend = self.zg = self.session = self.network = None
        self.chunks = {}
        self.inputs, self.outputs = [], []
        self.completed = 0
        self.forward_calls = 0
        self.stop_requested = False
        self.release_review_available = False
        self.stage = "before_sdk"

    def report(self, phase, **fields):
        self.stage = phase
        record = dict(phase=phase, pid=os.getpid(), boot_id=boot_id(), completed=self.completed,
                      forward_calls=self.forward_calls, **fields)
        save(self.root / "state.json", record)
        print(json.dumps(record), flush=True)

    def status(self, label):
        print("HARDWARE_STATUS_BEGIN " + label, flush=True)
        for level in (1, 2, 3, 4, 5):
            print("STATUS_LEVEL " + str(level), flush=True)
            self.device.showStatus(level)
        print("HARDWARE_STATUS_END " + label, flush=True)

    def gate(self, name):
        path = self.root / name
        while not path.exists():
            time.sleep(0.2)
        request = json.loads(path.read_text())
        if (request.get("boot_id") != self.manifest["boot_id"] or
                request.get("completed") != self.completed or not request.get("hardware_reviewed")):
            raise ValueError("Controller gate identity or completion differs")
        if self.stop_requested and name != "release.json":
            raise RuntimeError("Stop requested; no new SDK work")

    def initialize(self):
        from icraft import xir, xrt, zg330backend
        self.xrt = xrt
        graph_path = self.root / "candidate.json"
        graph = json.loads(graph_path.read_text())
        hardops = [op["op_id"] for op in graph["ops"] if op["_type_key"].endswith("::HardOp")]
        if len(hardops) != 54 or len(graph["ops"]) != 56:
            raise ValueError("Only the validated rank candidate is accepted")
        self.network = xir.Network.CreateFromJsonFile(str(graph_path))
        self.network.loadParamsFromFile(str(self.root / "candidate.raw"))
        self.view = self.network.view(hardops)
        self.report("opening_sdk")
        self.device = xrt.Device.Open("axi://zg330aiu?npu=0x40000000&dma=0x80000000")
        self.device.setWaitTime(10000)
        self.zdevice = xrt.ZG330Device(self.device)
        version = dict(self.device.version())
        if version.get("device") != "25122301" or version.get("icore") != "FMSHZGV3TECH-AID - 24160628":
            raise ValueError("Actual device/icore identity differs")
        self.region = self.device.defaultMemRegion()
        self.report("sdk_opened", version=version, region=str(self.region.typeKey()))
        self.status("before_dma")
        # Explicit ownership of complete allocations, including the guard lines.
        self.scratch = self.region.malloc(30400, False, 4096)
        dma = []
        for size in (64, 768, 30272):
            original = bytearray([0xa5]) * 30400
            pattern = bytearray((i*73 + size//64) & 255 for i in range(size))
            expected = original[:]
            expected[64:64+size] = pattern
            self.scratch.write(0, original, len(original))
            self.scratch.write(64, pattern, size)
            actual = bytearray(30400)
            self.scratch.read(actual, 0, len(actual))
            (self.root / ("dma_{}.actual.bin".format(size))).write_bytes(actual)
            (self.root / ("dma_{}.expected.bin".format(size))).write_bytes(expected)
            equal = actual == expected
            dma.append(dict(bytes=size, first_read_equal=equal, guard_lines_equal=actual[:64] == expected[:64] and actual[64+size:] == expected[64+size:]))
            save(self.root / "dma.json", dma)
            if not equal:
                raise RuntimeError("First DMA read differs; preserve allocations, no retry")
        self.status("after_dma")
        self.release_review_available = True
        self.report("dma_review", dma=dma)
        self.gate("deploy.json")
        self.report("deploying")
        self.release_review_available = False
        self.backend = xrt.Backend.Create(zg330backend.ZG330Backend, self.view, self.device)
        self.zg = zg330backend.ZG330Backend(self.backend)
        for value in self.view.inputs() + self.view.outputs():
            size = (value.storageBytes()+63)//64*64
            self.chunks[value.v_id] = self.region.malloc(size, False, 4096)
            self.zg.userConnectNetwork(self.chunks[value.v_id], value.v_id)
        self.session = xrt.Session.CreateWithBackends(self.view, [self.backend])
        self.session.apply()
        if not self.zg.precheck():
            raise RuntimeError("SDK instruction/parameter upload precheck failed")
        bindings = []
        for value_id, chunk in self.chunks.items():
            info = self.zg.forward_info.memchunk_map[value_id]
            value = self.zg.value_info[value_id]
            direct = (info.user_used and not info.staged_chunk and not value.is_host and not value.is_ocm
                      and info.memChunk.begin.addr() == chunk.begin.addr() == value.phy_addr)
            bindings.append(dict(value_id=value_id, address=chunk.begin.addr(), bytes=chunk.byte_size, direct=direct))
        if not all(row["direct"] for row in bindings):
            raise RuntimeError("A candidate port did not bind directly to owned PL DDR")
        self.inputs = [xrt.Tensor(value.tensorType(), self.chunks[value.v_id], 0) for value in self.view.inputs()]
        self.input_ids = [value.v_id for value in self.view.inputs()]
        self.output_ids = [value.v_id for value in self.view.outputs()]
        if self.input_ids != [0, 1, 2, 3] or self.output_ids != [167, 169, 171]:
            raise ValueError("Candidate port order differs")
        groups = []
        members = []
        for op_id in self.session.backendBindings():
            info = self.zg.forward_info.hardop_map[op_id]
            covered = list(info.merge_from) or [op_id]
            members.extend(covered)
            groups.append(dict(op_id=op_id, sync=list(info.sync_idx), members=covered))
        if len(members) != len(set(members)) or set(members) != set(hardops):
            raise ValueError("Applied HardOp coverage differs")
        self.final_count = 0
        for row in sorted(groups, key=lambda row: row["sync"][0]):
            start, count = row["sync"]
            if start != self.final_count or count <= 0:
                raise ValueError("Applied synchronization intervals differ")
            self.final_count += count
        save(self.root / "binding.json", dict(bindings=bindings, groups=groups, final_count=self.final_count))
        self.release_review_available = True
        self.report("ready_for_case", next_case=0)

    def execute(self, case):
        index = self.completed
        self.gate("continue_{}.json".format(index))
        self.report("case_running", case=case["name"])
        self.release_review_available = False
        folder = self.root / case["name"]
        for tensor, value_id in zip(self.inputs, self.input_ids):
            data = bytearray((folder / ("input_{}.bin".format(value_id))).read_bytes())
            if len(data) != self.network.getValueById(value_id).storageBytes():
                raise ValueError("Input physical extent differs")
            tensor.write(0, data, len(data))
        # This clears prior software-visible FPGA status, not in-flight work.
        # Each continuation requires review of the preceding completed job.
        self.device.reset(1)
        if self.zdevice.layerCount() != 0:
            raise RuntimeError("Initial layer count did not clear")
        begin = time.monotonic()
        self.forward_calls += 1
        self.outputs = self.session.forward(self.inputs)
        for tensor in self.outputs:
            if not tensor.waitForReady(timedelta(seconds=10)):
                raise RuntimeError("Native output completion callback timed out")
        compute_ms = (time.monotonic()-begin)*1000
        count = self.zdevice.layerCount()
        if count != self.final_count or len(self.outputs) != 3:
            raise RuntimeError("Applied final synchronization count or output extent differs")
        comparisons = []
        begin = time.monotonic()
        for value_id, tensor in zip(self.output_ids, self.outputs):
            size = self.network.getValueById(value_id).storageBytes()
            actual = bytearray(size)
            tensor.read(actual, 0, size)
            (folder / ("actual_{}.bin".format(value_id))).write_bytes(actual)
            expected = (folder / ("expected_{}.bin".format(value_id))).read_bytes()
            comparisons.append(dict(value_id=value_id, bytes=size, bitwise_equal=actual == expected,
                                    direct_address=tensor.data().addr() == self.chunks[value_id].begin.addr()))
        result = dict(case=case["name"], comparisons=comparisons, forward_and_wait_ms=compute_ms,
                      readback_ms=(time.monotonic()-begin)*1000, layer_count=count,
                      passed=all(row["bitwise_equal"] and row["direct_address"] for row in comparisons))
        save(folder / "result.json", result)
        self.completed += 1
        self.status("after_" + case["name"])
        self.release_review_available = True
        self.report("case_review", result=result)
        if not result["passed"]:
            raise RuntimeError("First outputs differ; no next case or retry")

    def finish(self):
        self.report("release_review")
        self.gate("release.json")
        self.report("releasing")
        self.outputs.clear()
        self.inputs.clear()
        self.session = None
        if self.backend is not None:
            self.backend.deinit()
        self.zg = self.backend = None
        for chunk in self.chunks.values():
            chunk.free()
        self.chunks.clear()
        if hasattr(self, "scratch"):
            self.scratch.free()
        count = len(self.region.memManager().getAllMemChunk())
        if count:
            raise RuntimeError("SDK allocations remain after explicit cleanup")
        self.xrt.Device.Close(self.device)
        self.report("complete", allocation_count_after=count, sdk_opens=1, boot_writes=0, reboots=0)


def main():
    root = Path(__file__).resolve().parent
    manifest = json.loads((root / "manifest.json").read_text())
    for name, digest in manifest["files"].items():
        if hashlib.sha256((root / name).read_bytes()).hexdigest() != digest:
            raise ValueError("Experiment package identity differs: " + name)
    if boot_id() != manifest["boot_id"] or owners():
        raise ValueError("Boot identity or existing device ownership differs")
    experiment = Experiment(root, manifest)
    for sig in (signal.SIGINT, signal.SIGTERM, signal.SIGHUP):
        signal.signal(sig, lambda *_: setattr(experiment, "stop_requested", True))
    with open("/run/pose180-resident.lock", "a") as lease:
        fcntl.flock(lease, fcntl.LOCK_EX | fcntl.LOCK_NB)
        if owners():
            raise ValueError("Device owner appeared before the lease")
        if Path("/run/pose180-resident.active.json").exists():
            raise ValueError("An existing global startup reservation must be reviewed")
        save(Path("/run/pose180-resident.active.json"), dict(boot_id=boot_id(), run=str(root)))
        with (root / "sdk-attempt.json").open("x") as stream:
            json.dump(dict(boot_id=boot_id(), opens=1, maximum_forward_calls=len(manifest["cases"]), automatic_retry=False), stream)
        try:
            experiment.initialize()
            for case in manifest["cases"]:
                experiment.execute(case)
            experiment.finish()
        except BaseException as error:
            traceback.print_exc()
            if experiment.stage == "before_sdk":
                experiment.report("failed_before_sdk", error=str(error), sdk_opens=0)
                reservation = Path("/run/pose180-resident.active.json")
                if json.loads(reservation.read_text()).get("run") == str(root):
                    reservation.unlink()
                return 1
            experiment.report("retained_after_error", error=str(error), prior_stage=experiment.stage)
            # Keep all application-owned SDK handles and the lease. The controller
            # must establish a safe platform recovery; a deadline cannot free them.
            while True:
                if experiment.release_review_available and (root / "release.json").exists():
                    experiment.finish()
                    return 1
                time.sleep(1)


if __name__ == "__main__":
    sys.exit(main())
