"""Compose the unchanged rank candidate with all three original NPU stages.

This validates instruction-level numerical composition with retained physical
outputs. File marshalling, capacity padding and runtime masks are explicit;
this is not an integrated zero-copy backend or a board performance measurement.
The arithmetic Gather keeps its restricted contract and is not labelled D2a.
"""

import argparse
import hashlib
import json
from pathlib import Path
import shutil
import struct

from native_pipeline import simulate
from runtime import save_json
from simulate_model_stage import simulate_stage
from validate_model_flow import floats


def validate(native, exported, baseline, directory):
    native, exported = native.resolve(), exported.resolve()
    baseline, directory = baseline.resolve(), directory.resolve()
    directory.mkdir(parents=True, exist_ok=False)
    manifest = json.loads((exported / "manifest.json").read_text())
    contract = json.loads((native / "contract.json").read_text())
    if manifest.get("native_layout") or any(cut.get("score_element_bytes", 4) != 4 for cut in manifest["cuts"]):
        raise ValueError("This composition requires the validated dense FP32 model cuts")
    if (contract["algorithm"], contract["n"], contract["k"], contract["channels"]) != ("rank_dynamic", 180, 100, 42):
        raise ValueError("Expected the validated 180/100/42 capacity candidate")
    identities = []
    candidate = directory / "candidate"
    candidate.mkdir()
    for name in ("topk_native_ZG.json", "topk_native_ZG.raw", "contract.json"):
        shutil.copyfile(native / name, candidate / name)
        identities.append(dict(name=name, sha256=hashlib.sha256((candidate / name).read_bytes()).hexdigest()))
    save_json(directory / "candidate-identity.json", identities)
    graph = json.loads((candidate / "topk_native_ZG.json").read_text())
    ports = next(op["inputs"] for op in graph["ops"] if op["_type_key"].endswith("::Output"))
    if [v["dtype"]["shape"] for v in ports] != [[1, 100], [100, 1], [100, 42]] or any(
            v["dtype"]["element_dtype"] != "@fp(32)" or v["dtype"]["layout"] != "@layout(*C)" for v in ports):
        raise ValueError("Candidate physical output format changed")
    input_path = directory / "input_0.ftmp"
    shutil.copyfile(baseline / "input_0.ftmp", input_path)
    tensors = {0: input_path}
    tensors.update(simulate_stage(exported, "npu_0", tensors, directory / "npu_0"))
    records = []
    for index, cut in enumerate(manifest["cuts"]):
        n, k, channels = cut["n"], cut["k"], cut["channels"]
        score_data = tensors[cut["score"]].read_bytes()
        feature_data = tensors[cut["features"]].read_bytes()
        scores, features = floats(score_data), floats(feature_data)
        if len(scores) != n or len(features) != n*channels or k != 100:
            raise ValueError("Unexpected original model boundary extent")
        if any(struct.unpack("<e", struct.pack("<e", v))[0] != v for v in scores + features):
            raise ValueError("Candidate exact numeric domain requires FP16-representable inputs")
        winners = sorted(range(n), key=lambda i: (-scores[i], i))[:k]
        expected = [struct.pack("<100f", *winners),
                    b"".join(score_data[i*4:(i+1)*4] for i in winners),
                    b"".join(feature_data[i*168:(i+1)*168] for i in winners)]
        name = "cut_" + cut["name"]
        simulate(candidate, graph, list(scores)+[65504.0]*(180-n),
                 list(features)+[123.0]*((180-n)*42), name, (n,k), dump_format="HQB")
        folder = candidate / name
        actual = [(folder / "native/topk_native/ftmpHQB" / (str(port["v_id"])+".ftmp")).read_bytes() for port in ports]
        comparisons = []
        for port, data, reference in zip(ports, actual, expected):
            (folder / (str(port["v_id"])+".expected.bin")).write_bytes(reference)
            comparisons.append(dict(value_id=port["v_id"], bitwise_equal=data == reference))
        record = dict(name=name, passed=all(row["bitwise_equal"] for row in comparisons), comparisons=comparisons)
        save_json(folder / "comparison.json", record)
        if not record["passed"]:
            raise RuntimeError("Arithmetic candidate differs at this model boundary; complete outputs retained")
        records.append(record)
        for value_id, data in [(cut["outputs"][0], actual[2])] + (
                [(cut["outputs"][1], actual[1])] if cut["selected_scores_used"] else []):
            path = folder / (str(value_id)+".ftmp")
            path.write_bytes(data)  # Actual instruction output, never CPU reference bytes.
            tensors[value_id] = path
        tensors.update(simulate_stage(exported, "npu_{}".format(index+1), tensors,
                                      directory / "npu_{}".format(index+1)))
    final = []
    for value_id in (3483, 3487):
        data = tensors[value_id].read_bytes()
        numeric = floats(data)
        reference = (baseline / "npu_2/native/piw24_shared/ftmpHQB" / (str(value_id)+".ftmp")).read_bytes()
        final.append(dict(value_id=value_id, elements=len(numeric), bitwise_equal=data == reference,
                          sha256=hashlib.sha256(data).hexdigest()))
    result = dict(passed=all(row["bitwise_equal"] for row in final), board_tested=False,
                  unchanged_candidate=True, composed_instruction_simulation=True, synthetic_inputs=1,
                  arithmetic_gather=True, d2a_generated_binary_tested=False,
                  integrated_backend=False, hardware_completion_verified=False, performance_measured=False,
                  capacity_padding_via_files=True, original_hardops=1007, candidate_hardops_per_cut=54,
                  cuts=records, final_outputs=final)
    save_json(directory / "result.json", result)
    if not result["passed"]:
        raise RuntimeError("Composed NPU candidate changes final model results")
    print("TOPK_NPU_MODEL_FLOW_PASS original_stages=3 candidate_calls=2 final_outputs=2", flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("native", "exported", "baseline", "directory"):
        parser.add_argument(name, type=Path)
    args = parser.parse_args()
    validate(args.native, args.exported, args.baseline, args.directory)
