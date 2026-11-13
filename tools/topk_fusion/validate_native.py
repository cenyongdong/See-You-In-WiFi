"""Differential validation of generated ZG330 instructions, including edge cases."""

import argparse
import json
from pathlib import Path
import random
import struct

from native_pipeline import simulate
from runtime import save_json


def fp16(value):
    return struct.unpack("<e", struct.pack("<e", value))[0]


def packed(values):
    return struct.pack("<{}f".format(len(values)), *values)


def cases(n, channels):
    rng = random.Random(330)
    ordinary = [fp16(rng.uniform(-8, 8)) for _ in range(n * channels)]
    yield "all_equal", [1.0] * n, ordinary
    yield "ascending", [fp16(i - n / 2) for i in range(n)], ordinary
    yield "descending", [fp16(n / 2 - i) for i in range(n)], ordinary
    yield "negative_ties", [-float(i % 7 + 1) for i in range(n)], ordinary
    yield "random", [fp16(rng.uniform(-100, 100)) for _ in range(n)], ordinary
    extremes = [65504.0, -65504.0, 2**-24, -(2**-24), 0.0, -0.0, 1.0, -1.0]
    yield "fp16_extremes", [extremes[i % 8] for i in range(n)], ordinary
    yield "payload_edges", [float(n - i) for i in range(n)], [extremes[i % 8] for i in range(n * channels)]


def validate(directory):
    directory = directory.resolve()
    contract = json.loads((directory / "contract.json").read_text())
    graph = json.loads((directory / "topk_native_ZG.json").read_text())
    ports = next(op["inputs"] for op in graph["ops"] if op["_type_key"] == "icraft::xir::Output")
    n, k, channels = (contract[x] for x in ("n", "k", "channels"))
    records = []
    for name, scores, payload in cases(n, channels):
        simulate(directory, graph, scores, payload, name)
        winners = sorted(range(n), key=lambda i: (-scores[i], i))[:k]
        expected = [[float(i) for i in winners]]
        if contract["algorithm"] != "argmax":
            expected.extend([[scores[i] for i in winners],
                             [payload[i * channels + c] for i in winners for c in range(channels)]])
        else:
            expected = [expected[0][:1]]
        output_results = []
        for port, reference in zip(ports, expected):
            data = (directory / name / "native/topk_native/ftmpSFB" /
                    (str(port["v_id"]) + ".ftmp")).read_bytes()
            expected_data = packed(reference)
            if len(data) != len(expected_data):
                raise RuntimeError("Unexpected output byte count")
            actual = list(struct.unpack("<{}f".format(len(data) // 4), data))
            differences = [i for i, (x, y) in enumerate(zip(actual, reference)) if x != y]
            bit_differences = [i for i in range(len(reference))
                               if data[4*i:4*i+4] != expected_data[4*i:4*i+4]]
            (directory / name / (str(port["v_id"]) + ".expected.f32")).write_bytes(expected_data)
            output_results.append(dict(value_id=port["v_id"], numeric_equal=not differences,
                                       bitwise_equal=not bit_differences,
                                       numeric_mismatch_indices=differences,
                                       bitwise_mismatch_indices=bit_differences))
        record = dict(case=name, outputs=output_results)
        save_json(directory / name / "comparison.json", record)
        records.append(record)
        print(json.dumps(dict(case=name, outputs=[dict(value_id=o["value_id"],
              numeric_mismatches=len(o["numeric_mismatch_indices"]),
              bitwise_mismatches=len(o["bitwise_mismatch_indices"])) for o in output_results])), flush=True)
    result = dict(board_tested=False, generated_instruction_simulation=True, cases=records,
                  numeric_equal=all(o["numeric_equal"] for r in records for o in r["outputs"]),
                  bitwise_equal=all(o["bitwise_equal"] for r in records for o in r["outputs"]))
    save_json(directory / "validation.json", result)
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("directory", type=Path)
    args = parser.parse_args()
    result = validate(args.directory)
    if not result["bitwise_equal"]:
        raise SystemExit("Strict bitwise validation failed; original outputs retained")
