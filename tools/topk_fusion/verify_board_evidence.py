"""Recompute TopK/Gather references from saved board inputs without using the SDK.

This verifies the first returned bytes, package identities and shutdown evidence.
It does not connect to a board or reinterpret the SDK's diagnostic registers.
"""

import argparse
import hashlib
import json
import math
from pathlib import Path
import struct

from runtime import save_json


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def floats(data):
    if len(data) % 4:
        raise ValueError("FP32 extent is not a multiple of four bytes")
    return struct.unpack("<{}f".format(len(data) // 4), data)


def active_prefix(data):
    mask = floats(data)
    count = sum(value == 1.0 for value in mask)
    if not count or mask != (1.0,) * count + (0.0,) * (len(mask) - count):
        raise ValueError("Expected a nonempty contiguous runtime mask")
    return count


def verify(directory):
    manifest = read_json(directory / "manifest.json")
    for name, digest in manifest["files"].items():
        if hashlib.sha256((directory / name).read_bytes()).hexdigest() != digest:
            raise ValueError("Package identity differs: " + name)
    state = read_json(directory / "state.json")
    outcome = read_json(directory / "outcome.json")
    native_exit = read_json(directory / "native-exit.json")
    for item in (state, outcome, native_exit):
        if item["boot_id"] != manifest["boot_id"]:
            raise ValueError("Evidence boot identities differ")
    if (state["phase"] != "complete" or state["allocation_count_after"] != 0 or
            native_exit["native_exit"] != 0 or not outcome["native_shutdown_complete"] or
            outcome["device_owners"] or not outcome["global_lease_available"]):
        raise ValueError("Native shutdown evidence is incomplete")
    dma = read_json(directory / "dma.json")
    for row in dma:
        stem = "dma_{}".format(row["bytes"])
        actual = (directory / (stem + ".actual.bin")).read_bytes()
        expected = bytearray([0xa5]) * 30400
        size = row["bytes"]
        expected[64:64 + size] = bytes((i * 73 + size // 64) & 255 for i in range(size))
        if actual != expected or not row["first_read_equal"] or not row["guard_lines_equal"]:
            raise ValueError("Saved first DMA bytes or guards differ")

    results = []
    for case in manifest["cases"]:
        folder = directory / case["name"]
        inputs = [(folder / "input_{}.bin".format(i)).read_bytes() for i in range(4)]
        n, k = active_prefix(inputs[2]), active_prefix(inputs[3])
        scores = floats(inputs[0])
        if not 1 <= k <= n <= 180 or k > 100 or len(scores) != 180 or len(inputs[1]) != 180 * 42 * 4:
            raise ValueError("Candidate capacity/extent differs")
        if not all(math.isfinite(value) for value in scores + floats(inputs[1])):
            raise ValueError("Nonfinite fixture values")
        winners = sorted(range(n), key=lambda index: (-scores[index], index))[:k]
        references = {
            167: struct.pack("<100f", *(winners + [-1] * (100 - k))),
            169: b"".join(inputs[0][i * 4:(i + 1) * 4] for i in winners) + bytes((100 - k) * 4),
            171: b"".join(inputs[1][i * 168:(i + 1) * 168] for i in winners) + bytes((100 - k) * 168),
        }
        outputs = []
        for value_id, reference in references.items():
            actual = (folder / "actual_{}.bin".format(value_id)).read_bytes()
            stored = (folder / "expected_{}.bin".format(value_id)).read_bytes()
            equal = actual == reference == stored
            outputs.append(dict(value_id=value_id, bytes=len(actual), bitwise_equal=equal,
                                sha256=hashlib.sha256(actual).hexdigest()))
            if not equal:
                raise ValueError("Independent CPU reference differs: {}/{}".format(case["name"], value_id))
        native = read_json(folder / "result.json")
        if not native["passed"] or native["layer_count"] != 41:
            raise ValueError("Native case result differs")
        results.append(dict(case=case["name"], n=n, k=k, channels=42, outputs=outputs,
                            forward_and_wait_ms=native["forward_and_wait_ms"],
                            readback_and_preserve_ms=native["readback_ms"]))
    if len(results) != 7 or state["forward_calls"] != 7 or outcome["sdk_opens"] != 1:
        raise ValueError("Actual finite execution scope differs")
    return dict(passed=True, board_tested=True, independent_cpu_reference=True,
                first_read_only=True, boot_id=manifest["boot_id"], cases=results, dma=dma,
                outcome=outcome, full_model_board_tested=False, pl_kernel_board_tested=False,
                d2a_binary_board_tested=False, negative_zero_universal_gather_proven=False,
                end_to_end_speedup_proven=False, detailed_sdk_diagnostics_qualified=False)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("directory", type=Path)
    parser.add_argument("report", type=Path)
    args = parser.parse_args()
    if args.report.exists():
        parser.error("Preserve the previous verification report")
    report = verify(args.directory)
    save_json(args.report, report)
    print("BOARD_EVIDENCE_PASS cases=7 outputs=21 dma=3 allocations_after=0")
