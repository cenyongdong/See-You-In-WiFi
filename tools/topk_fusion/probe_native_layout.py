"""Compare original model format chains with direct FP16/C16 byte semantics.

All work uses Host instruction simulation.  An exported unary chain is not
assumed to be an identity: complete actual outputs are retained and compared.
Sixteen fixtures cover every finite FP16 feature pattern, including signed
zero and subnormals; score paths additionally exercise the same edge patterns.
"""

import argparse
import json
from pathlib import Path
import struct

from model_partition import MODEL, unary_chain
from runtime import (ICRAFT_PYTHON, icraft_environment, load_xir,
                     run_native, save_json)
from simulate_model_stage import simulate_stage


FORMATS = {
    "A_pre": ((3443, 448), (3451, 478)),
    "A_post": ((7470, 495),),
    "B_pre": ((3467, 1133), (3471, 1145)),
    "B_post": ((8747, 1148),),
}


def export(directory):
    xir, dll_handles = load_xir()
    graph = json.loads(MODEL.read_text())
    producer = {v["v_id"]: op for op in graph["ops"] for v in op["outputs"]}
    network = xir.Network.CreateFromJsonFile(str(MODEL))
    network.loadParamsFromFile(str(MODEL.with_suffix(".raw")))
    entries = []
    for name, boundaries in FORMATS.items():
        selected = set().union(*(unary_chain(producer, end, start) for end, start in boundaries))
        op_ids = [op["op_id"] for op in graph["ops"] if op["op_id"] in selected]
        view = network.view(op_ids).toNetwork()
        view.dumpJsonAndParams(str(directory / (name + ".json")), str(directory / (name + ".raw")))
        entries.append(dict(name=name, op_ids=op_ids,
                            inputs=[dict(value_id=v.v_id, bytes=v.storageBytes()) for v in view.inputs()],
                            outputs=[dict(value_id=v.v_id, bytes=v.storageBytes()) for v in view.outputs()]))
    save_json(directory / "manifest.json", dict(board_tested=False, stages=entries))
    assert dll_handles


def half_to_float(word):
    return struct.unpack("<e", struct.pack("<H", word))[0]


def normalized_half(word, policy):
    return 0 if policy == "flush-half-zero" and word & 0x7c00 == 0 else word


def dense_float(words, policy="none"):
    return struct.pack("<{}f".format(len(words)), *(half_to_float(normalized_half(word, policy)) for word in words))


def blocked_half(words, rows, channels=42, padding=0):
    data = []
    for block in range((channels + 15) // 16):
        for row in range(rows):
            for lane in range(16):
                c = block*16 + lane
                data.append(words[row*channels+c] if c < channels else padding)
    return struct.pack("<{}H".format(len(data)), *data)


def probe(directory, cases, policy):
    directory.mkdir(parents=True, exist_ok=False)
    exported = directory / "graphs"
    exported.mkdir()
    run_native("export", [ICRAFT_PYTHON, "-B", Path(__file__).resolve(), exported, "--export-only"],
               directory, icraft_environment())
    edges = [0, 0x8000, 1, 0x8001, 0x3c00, 0xbc00, 0x7bff, 0xfbff, 0x03ff, 0x83ff, 0x0400, 0x8400]
    finite = edges + [word for word in range(65536) if word & 0x7c00 != 0x7c00 and word not in edges]
    covered = set()
    results = []
    for case in range(cases):
        for name, n, score_id, feature_id, old_score, old_features, gather_input, native_output in (
                ("A", 180, 448, 478, 3443, 3451, 495, 7470),
                ("B", 100, 1133, 1145, 3467, 3471, 1148, 8747)):
            folder = directory / ("case_{}_{}".format(case, name))
            folder.mkdir()
            words = [finite[(case*4200+i) % len(finite)] for i in range(n*42)]
            score_words = [edges[i % len(edges)] if i < len(edges) else finite[(case*n+i) % len(finite)]
                           for i in range(n)]
            scores = folder / "scores.ftmp"
            scores.write_bytes(struct.pack("<{}H".format(n), *score_words))
            features = folder / "features.ftmp"
            # Padding is not a logical channel; a NaN there must not leak.
            features.write_bytes(blocked_half(words, n, padding=0x7e01))
            pre = simulate_stage(exported, name+"_pre", {score_id: scores, feature_id: features}, folder / "pre")
            expected = {old_score: dense_float(score_words, policy), old_features: dense_float(words, policy)}
            comparisons = []
            for value_id, data in expected.items():
                (folder / (str(value_id) + ".expected.bin")).write_bytes(data)
                comparisons.append(dict(value_id=value_id, bitwise_equal=pre[value_id].read_bytes() == data))
            # The post chain is a format test, so select the first 100 rows.
            # Complete TopK selection is separately verified by the RTL flow.
            selected = words[:4200]
            host = folder / "gather.ftmp"
            host.write_bytes(pre[old_features].read_bytes()[:16800])
            post = simulate_stage(exported, name+"_post", {gather_input: host}, folder / "post")
            normalized = [normalized_half(word, policy) for word in selected]
            output = (blocked_half(normalized, 100) if name == "A"
                      else struct.pack("<4200H", *normalized))
            (folder / (str(native_output) + ".expected.bin")).write_bytes(output)
            comparisons.append(dict(value_id=native_output, bitwise_equal=post[native_output].read_bytes() == output))
            row = dict(case=case, cut=name, expected_policy=policy, comparisons=comparisons,
                       passed=all(item["bitwise_equal"] for item in comparisons))
            save_json(folder / "comparison.json", row)
            results.append(row)
            covered.update(selected)
            save_json(directory / "progress.json", dict(cases=results, distinct_finite_patterns=len(covered)))
            if not row["passed"]:
                raise RuntimeError("Original format chain differs from the requested compatibility policy")
    save_json(directory / "result.json", dict(passed=True, board_tested=False,
              native_layout_optimization_implemented=False, cases=results, expected_policy=policy,
              distinct_finite_feature_patterns=len(covered),
              all_finite_fp16_feature_patterns=(len(covered) == 63488),
              padding_nan_excluded=True))
    print("TOPK_NATIVE_FORMATS_PASS fixtures={} finite_feature_patterns={}".format(cases*2, len(covered)), flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("directory", type=Path)
    parser.add_argument("--cases", type=int, default=16, choices=range(1,17))
    parser.add_argument("--expected-policy", choices=("none", "flush-half-zero"), default="none")
    parser.add_argument("--export-only", action="store_true", help=argparse.SUPPRESS)
    args = parser.parse_args()
    if args.export_only:
        export(args.directory.resolve())
    else:
        probe(args.directory.resolve(), args.cases, args.expected_policy)
