"""Test the unchanged rank candidate on actual old-model simulated tensors."""

import argparse
import hashlib
import json
from pathlib import Path
import shutil
import struct

from native_pipeline import simulate
from runtime import save_json
from validate_d2a_chain import gather_objects
from validate_model_flow import floats


def validate(native, flow, directory):
    native, flow, directory = native.resolve(), flow.resolve(), directory.resolve()
    directory.mkdir(parents=True, exist_ok=False)
    contract = json.loads((native / "contract.json").read_text())
    if (contract["algorithm"], contract["n"], contract["k"], contract["channels"]) != ("rank_dynamic", 180, 100, 42):
        raise ValueError("Expected the validated 180/100/42 runtime-mask candidate")
    identity = []
    for name in ("topk_native_ZG.json", "topk_native_ZG.raw", "contract.json"):
        shutil.copyfile(native / name, directory / name)
        identity.append(dict(name=name, sha256=hashlib.sha256((directory / name).read_bytes()).hexdigest()))
    save_json(directory / "candidate-identity.json", identity)
    graph = json.loads((directory / "topk_native_ZG.json").read_text())
    ports = next(op["inputs"] for op in graph["ops"] if op["_type_key"].endswith("::Output"))
    records = []
    for name, stage, score_id, feature_id, n, k in (("A", 0, 3443, 3451, 180, 100),
                                                  ("B", 1, 3467, 3471, 100, 100),
                                                  ("B_reuse50", 1, 3467, 3471, 100, 50)):
        source = flow / ("npu_{}".format(stage)) / "native/piw24_shared/ftmpHQB"
        score_data = (source / (str(score_id) + ".ftmp")).read_bytes()
        payload_data = (source / (str(feature_id) + ".ftmp")).read_bytes()
        scores, payload = list(floats(score_data)), list(floats(payload_data))
        if len(scores) != n or len(payload) != n*42:
            raise ValueError("Actual model tensor shape differs")
        if any(struct.unpack("<e", struct.pack("<e", value))[0] != value for value in scores + payload):
            raise ValueError("Actual tensors exceed this candidate's exact FP16 domain")
        winners = sorted(range(n), key=lambda i: (-scores[i], i))[:k]
        simulate(directory, graph, scores + [65504.0]*(180-n), payload + [123.0]*((180-n)*42), name, (n,k))
        folder = directory / name
        references = [struct.pack("<100f", *(list(map(float, winners)) + [-1.0]*(100-k))),
                      b"".join(score_data[i*4:i*4+4] for i in winners) + bytes((100-k)*4),
                      b"".join(payload_data[i*168:(i+1)*168] for i in winners) + bytes((100-k)*168)]
        comparisons = []
        actual_indices = None
        for index, (port, reference) in enumerate(zip(ports, references)):
            actual = (folder / "native/topk_native/ftmpSFB" / (str(port["v_id"]) + ".ftmp")).read_bytes()
            (folder / (str(port["v_id"]) + ".expected.bin")).write_bytes(reference)
            equal = actual == reference
            comparisons.append(dict(value_id=port["v_id"], bitwise_equal=equal))
            if index == 0 and equal:
                actual_indices = list(map(int, struct.unpack("<100f", actual)[:k]))
        record = dict(case=name, n=n, k=k, outputs=comparisons,
                      generated_binary_bitwise_equal=all(item["bitwise_equal"] for item in comparisons))
        save_json(folder / "comparison.json", record)
        if not record["generated_binary_bitwise_equal"]:
            raise RuntimeError("Model boundary rank candidate mismatch; outputs retained")
        objects = folder / "d2a_objects"
        objects.mkdir()
        gathered = gather_objects(actual_indices, payload, n, k, 42, objects)
        (objects / "actual.f32").write_bytes(gathered)
        (objects / "expected.f32").write_bytes(references[2][:k*168])
        record["d2a_object_bitwise_equal"] = gathered == references[2][:k*168]
        if not record["d2a_object_bitwise_equal"]:
            raise RuntimeError("D2a object Gather mismatch; outputs retained")
        records.append(record)
    save_json(directory / "result.json", dict(passed=True, board_tested=False,
              actual_model_simulator_tensors=True, candidate_recompiled=False, cases=records,
              rank_generated_binary_simulation=True, gather_instruction_object_simulation=True,
              d2a_fused_generated_binary_simulation=False))
    print("TOPK_NATIVE_MODEL_CUTS_PASS cases=3 d2a_objects=9", flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("native", type=Path)
    parser.add_argument("flow", type=Path)
    parser.add_argument("directory", type=Path)
    args = parser.parse_args()
    validate(args.native, args.flow, args.directory)
