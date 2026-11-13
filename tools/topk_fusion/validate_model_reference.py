"""Compare the composed flow with all original NPU instructions and CPU cuts.

The SDK Host implementations of TopK/GatherElements are not used.  Independent
numeric sorting and byte-copy Gather implement their documented semantics.
All original NPU HardOps, including the removed index expansion, are executed
in a single exported reference graph.  Its boundary tensors must match those
used to construct CPU inputs, as well as its final outputs matching the flow.
"""

import argparse
import json
from pathlib import Path
import struct

from runtime import save_json
from simulate_model_stage import simulate_stage
from validate_model_flow import floats


def validate(exported, flow, directory, candidate_flow=None):
    exported, flow, directory = exported.resolve(), flow.resolve(), directory.resolve()
    directory.mkdir(parents=True, exist_ok=False)
    candidate = candidate_flow.resolve() if candidate_flow is not None else flow
    if (candidate / "input_0.ftmp").read_bytes() != (flow / "input_0.ftmp").read_bytes():
        raise ValueError("Candidate and CPU reference must use identical complete model inputs")
    manifest = json.loads((exported / "manifest.json").read_text())
    reference, = [stage for stage in manifest["stages"] if stage["name"] == "reference_all_hardops"]
    if len(reference["op_ids"]) != 1021:
        raise ValueError("The reference must contain all original NPU HardOps")
    inputs = {0: flow / "input_0.ftmp"}
    expected = {}
    for number, (scores_id, features_id, output_id) in enumerate(((3443, 3451, 495), (3467, 3471, 1148))):
        source = flow / ("npu_{}".format(number)) / "native/piw24_shared/ftmpHQB"
        score_data = (source / (str(scores_id) + ".ftmp")).read_bytes()
        feature_data = (source / (str(features_id) + ".ftmp")).read_bytes()
        scores = floats(score_data)
        floats(feature_data)
        winners = sorted(range(len(scores)), key=lambda i: (-scores[i], i))[:100]
        data = b"".join(feature_data[i*168:(i+1)*168] for i in winners)
        path = directory / (str(output_id) + ".ftmp")
        path.write_bytes(data)
        inputs[output_id] = path
        expected[scores_id], expected[features_id] = score_data, feature_data
        if number == 0:
            indices = directory / "486.ftmp"
            indices.write_bytes(struct.pack("<100f", *winners))
            inputs[486] = indices
            expected[3455] = struct.pack("<4200f", *(i for i in winners for _ in range(42)))
        else:
            selected = directory / "1136.ftmp"
            selected.write_bytes(b"".join(score_data[i*4:i*4+4] for i in winners))
            inputs[1136] = selected
    for value_id in (3483, 3487):
        expected[value_id] = (candidate / "npu_2/native/piw24_shared/ftmpHQB" / (str(value_id) + ".ftmp")).read_bytes()
    actual = simulate_stage(exported, "reference_all_hardops", inputs, directory / "original_npu")
    if set(actual) != set(expected):
        raise ValueError("Original reference graph exposes different boundaries")
    comparisons = []
    for value_id, reference_bytes in expected.items():
        (directory / (str(value_id) + ".expected.bin")).write_bytes(reference_bytes)
        actual_bytes = actual[value_id].read_bytes()
        comparisons.append(dict(value_id=value_id, bytes=len(reference_bytes),
                                bitwise_equal=actual_bytes == reference_bytes))
    report = dict(passed=all(row["bitwise_equal"] for row in comparisons), board_tested=False,
                  original_hardops=1021, original_host_backend_implementation_executed=False,
                  candidate_flow=str(candidate), cpu_reference_flow=str(flow), identical_model_inputs=True,
                  independent_cpu_topk_gather_reference=True, synthetic_inputs=1, comparisons=comparisons)
    save_json(directory / "result.json", report)
    if not report["passed"]:
        raise RuntimeError("Composed model differs from original NPU graph plus CPU cut reference")
    print("TOPK_MODEL_REFERENCE_PASS boundaries=5 final_outputs=2 original_hardops=1021", flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("exported", type=Path)
    parser.add_argument("flow", type=Path)
    parser.add_argument("directory", type=Path)
    parser.add_argument("--candidate-flow", type=Path)
    args = parser.parse_args()
    validate(args.exported, args.flow, args.directory, args.candidate_flow)
