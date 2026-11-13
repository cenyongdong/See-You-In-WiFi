"""Verify several runtime N/K pairs using one compiled ZG330 capacity graph."""

import argparse
import json
from pathlib import Path
import struct

from native_pipeline import simulate
from runtime import save_json
from validate_native import cases, packed


def validate(directory, reuse=False):
    directory = directory.resolve()
    contract = json.loads((directory / "contract.json").read_text())
    if contract["algorithm"] != "rank_dynamic":
        raise ValueError("Requires a compiled runtime-mask graph")
    graph = json.loads((directory / "topk_native_ZG.json").read_text())
    ports = next(op["inputs"] for op in graph["ops"] if op["_type_key"] == "icraft::xir::Output")
    max_n, max_k, channels = (contract[x] for x in ("n", "k", "channels"))
    shapes = [(max_n, max_k), (100, 50), (100, 100), (1, 1), (33, 17)]
    records = []
    for n, k in dict.fromkeys(shapes):
        if not 1 <= k <= n <= max_n or k > max_k:
            continue
        for name, scores, payload in cases(n, channels):
            name = "n{}_k{}_{}".format(n, k, name)
            if not reuse:
                simulate(directory, graph, scores + [65504.0] * (max_n - n),
                         payload + [123.0] * ((max_n - n) * channels), name, (n, k))
            winners = sorted(range(n), key=lambda i: (-scores[i], i))[:k]
            expected = [[float(i) for i in winners] + [-1.0] * (max_k - k),
                        [scores[i] for i in winners] + [0.0] * (max_k - k),
                        [payload[i * channels + c] for i in winners for c in range(channels)] +
                        [0.0] * ((max_k - k) * channels)]
            results = []
            for port, values in zip(ports, expected):
                path = directory / name / "native/topk_native/ftmpSFB" / (str(port["v_id"]) + ".ftmp")
                actual_data, expected_data = path.read_bytes(), packed(values)
                if len(actual_data) != len(expected_data):
                    raise RuntimeError("Unexpected output extent")
                actual = struct.unpack("<{}f".format(len(values)), actual_data)
                results.append(dict(value_id=port["v_id"],
                    numeric_equal=all(a == b for a, b in zip(actual, values)),
                    bitwise_equal=actual_data == expected_data))
                (directory / name / (str(port["v_id"]) + ".expected.f32")).write_bytes(expected_data)
            record = dict(case=name, outputs=results)
            records.append(record)
            print(json.dumps(record), flush=True)
    report = dict(board_tested=False, generated_instruction_simulation=True,
                  index_bitwise_equal=all(row["outputs"][0]["bitwise_equal"] for row in records),
                  numeric_equal=all(o["numeric_equal"] for row in records for o in row["outputs"]),
                  gather_bitwise_equal=all(row["outputs"][2]["bitwise_equal"] for row in records),
                  cases=records)
    save_json(directory / "dynamic-validation-reproducible.json", report)
    # Numeric and index correctness are distinct from the bit-preserving Gather
    # contract. A numeric pass must never be labelled a strict Gather pass.
    if not report["index_bitwise_equal"] or not report["numeric_equal"]:
        raise SystemExit("Runtime reuse failed; full outputs retained")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("directory", type=Path)
    parser.add_argument("--reuse", action="store_true", help="Recheck preserved native outputs")
    args = parser.parse_args()
    validate(args.directory, args.reuse)
