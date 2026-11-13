"""Feed actual generated-rank indices into D2a instruction-object simulation.

This explicitly mixes two evidence levels. The rank bytes are executable ZG
instructions; the D2a objects have not passed binary round-trip simulation.
Consequently this test cannot authorize deployment of a fused binary kernel.
"""

import argparse
import json
from pathlib import Path
import struct
import sys

from runtime import ROOT, run_native, save_json
from validate_native import cases, packed


def gather_objects(indices, payload, n, k, channels, folder):
    """Gather actual rank indices using three independent C16 object probes."""
    actual = bytearray(k * channels * 4)
    for block in range((channels + 15) // 16):
        fixture = folder / ("block_{}.json".format(block))
        block_payload = [payload[row * channels + lane] if lane < channels else 0.0
                         for row in range(n) for lane in range(block * 16, block * 16 + 16)]
        save_json(fixture, dict(indices=indices, payload=block_payload))
        destination = folder / ("block_{}".format(block))
        run_native("block_{}".format(block), [sys.executable, "-B",
                   ROOT / "tools/topk_fusion/probe_d2a_instructions.py", destination,
                   "--n", n, "--k", k, "--channels", 16,
                   "--object-simulation", "--fixture", fixture], folder)
        data = (destination / "actual.f32").read_bytes()
        if len(data) != k * 64:
            raise RuntimeError("D2a object output byte count differs")
        for row in range(k):
            width = min(16, channels - block * 16) * 4
            begin = (row * channels + block * 16) * 4
            actual[begin:begin + width] = data[row * 64:row * 64 + width]
    return bytes(actual)


def validate(native, output):
    native, output = native.resolve(), output.resolve()
    output.mkdir(parents=True, exist_ok=False)
    contract = json.loads((native / "contract.json").read_text())
    max_k, channels = contract["k"], contract["channels"]
    graph = json.loads((native / "topk_native_ZG.json").read_text())
    ports = next(op["inputs"] for op in graph["ops"] if op["_type_key"] == "icraft::xir::Output")
    records = []
    for n, k in ((180, 100), (100, 50), (100, 100), (1, 1), (33, 17)):
        for name, scores, payload in cases(n, channels):
            name = "n{}_k{}_{}".format(n, k, name)
            folder = output / name
            folder.mkdir()
            raw = (native / name / "native/topk_native/ftmpSFB" /
                   (str(ports[0]["v_id"]) + ".ftmp")).read_bytes()
            floats = struct.unpack("<{}f".format(max_k), raw)[:k]
            if any(value != int(value) or not 0 <= value < n for value in floats):
                raise RuntimeError("Invalid actual rank index")
            indices = list(map(int, floats))
            winners = sorted(range(n), key=lambda i: (-scores[i], i))[:k]
            if indices != winners:
                raise RuntimeError("Actual native rank output differs")
            actual = gather_objects(indices, payload, n, k, channels, folder)
            expected = packed([payload[i * channels + c] for i in winners for c in range(channels)])
            (folder / "actual.f32").write_bytes(actual)
            (folder / "expected.f32").write_bytes(expected)
            record = dict(case=name, bitwise_equal=actual == expected)
            records.append(record)
            if actual != expected:
                raise RuntimeError("D2a chain mismatch; full output retained")
    save_json(output / "result.json", dict(rank_generated_binary_simulation=True,
              gather_instruction_object_simulation=True, fused_generated_binary_simulation=False,
              board_tested=False, cases=records))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("native", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    validate(args.native, args.output)
