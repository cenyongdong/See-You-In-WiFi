"""Compose old-model instruction simulation and actual PL peripheral simulation.

Data crosses simulators through preserved files, never through a board.  Each
PL result is checked against a numeric full-sort reference before being supplied
to the next NPU stage.  The original index expansion is independently simulated
once to verify that the removed chain only broadcasts the selected indices.
"""

import argparse
import hashlib
import json
import math
from pathlib import Path
import shutil
import struct
import sys

from runtime import ROOT, run_native, save_json
from simulate_model_stage import simulate_stage


def floats(data):
    values = struct.unpack("<{}f".format(len(data) // 4), data)
    if not all(math.isfinite(value) for value in values):
        raise ValueError("Nonfinite model data cannot continue to the next stage")
    return values


def build_generator(directory):
    directory.mkdir()
    sources = ROOT / "FPGA/topk_gather/host"
    identities = []
    for name in ("topk_plan.hpp", "topk_plan.cpp", "topk_registers.hpp", "generate_model_vectors.cpp"):
        target = directory / name
        shutil.copyfile(sources / name, target)
        identities.append(dict(path=str(sources / name), sha256=hashlib.sha256(target.read_bytes()).hexdigest()))
    save_json(directory / "sources.json", identities)
    binary = directory / "generate_model_vectors.exe"
    run_native("compile", ["g++", "-std=c++17", "-O2", "-Wall", "-Wextra", "-Wpedantic", "-Werror",
               directory / "topk_plan.cpp", directory / "generate_model_vectors.cpp", "-o", binary], directory)
    return binary


def run_cut(cut, inputs, directory, generator, memory_path=None):
    directory.mkdir()
    n, k, channels = cut["n"], cut["k"], cut["channels"]
    score_data = inputs[cut["score"]].read_bytes()
    feature_data = inputs[cut["features"]].read_bytes()
    native = cut.get("score_element_bytes", 4) == 2
    if native:
        if (cut["fp16_policy"] != "flush-half-zero" or cut["source_layout"] != "blocked16" or
                cut["feature_element_bytes"] != 2 or cut["destination_layout"] not in ("dense", "blocked16")):
            raise ValueError("Unsupported native boundary contract")
        padded = (channels+15)//16*16
        if len(score_data) != n*2 or len(feature_data) != n*padded*2:
            raise ValueError("Native FP16 cut shape mismatch")

        def normalize(word):
            return 0 if word & 0x7c00 == 0 else word

        def number(word):
            return struct.unpack("<e", struct.pack("<H", normalize(word)))[0]

        score_words = struct.unpack("<{}H".format(n), score_data)
        source_words = struct.unpack("<{}H".format(n*padded), feature_data)
        rows = [[normalize(source_words[(c//16)*n*16+i*16+c%16]) for c in range(channels)] for i in range(n)]
        scores = tuple(number(word) for word in score_words)
        features = tuple(number(word) for row in rows for word in row)
        if not all(math.isfinite(value) for value in scores + features):
            raise ValueError("Nonfinite native logical tensor cannot continue")
        score_data = struct.pack("<{}f".format(n), *scores)
    else:
        if len(score_data) != n*4 or len(feature_data) != n*channels*4:
            raise ValueError("Dense FP32 cut shape mismatch")
        scores, features = floats(score_data), floats(feature_data)
    winners = sorted(range(n), key=lambda i: (-scores[i], i))[:k]
    expected = dict(scores=b"".join(score_data[i*4:i*4+4] for i in winners),
                    indices=struct.pack("<{}Q".format(k), *winners))
    if native:
        if cut["destination_layout"] == "blocked16":
            payload = [rows[i][block*16+lane] if block*16+lane < channels else 0
                       for block in range(padded//16) for i in winners for lane in range(16)]
        else:
            payload = [word for i in winners for word in rows[i]]
        expected["primary"] = struct.pack("<{}H".format(len(payload)), *payload)
    else:
        expected["primary"] = b"".join(feature_data[i*channels*4:(i+1)*channels*4] for i in winners)
    for name, data in expected.items():
        (directory / (name + ".expected.bin")).write_bytes(data)
    vectors = directory / "device_vectors.txt"
    command = [generator, n, k, channels, inputs[cut["score"]], inputs[cut["features"]], vectors]
    if memory_path is not None or native:
        command.append(memory_path if memory_path is not None else "-")
    if memory_path is not None:
        shutil.copyfile(memory_path, directory / "sdk-memory.txt")
    if native:
        command.append("native-f16-c16" if cut["destination_layout"] == "blocked16" else "native-f16-dense")
    run_native("vectors", command, directory)
    rtl = directory / "rtl"
    run_native("rtl", [sys.executable, "-B", ROOT / "tools/topk_fusion/run_rtl.py", rtl,
                         "--suite", "device", "--vectors", vectors] +
                         (["--flush-half-zero"] if native else []), directory)
    result = dict(name=cut["name"], n=n, k=k, channels=channels, board_tested=False,
                  actual_model_inputs=True, comparisons={}, indices=winners, native_layout=native,
                  fp16_policy=cut.get("fp16_policy", "preserve"),
                  sdk_mock_memory=memory_path is not None, finite=True, exact_fp16_inputs=all(
                      struct.unpack("<e", struct.pack("<e", value))[0] == value for value in scores + features))
    # Actual full allocations are saved by the testbench before any comparison.
    for name, reference in expected.items():
        actual = (rtl / ("actual_0_" + name + ".bin")).read_bytes()
        allocation_bytes = (len(reference) + 63) // 64 * 64
        equal = len(actual) == allocation_bytes and actual[:len(reference)] == reference
        tail = actual[len(reference):] == bytes([0xa5]) * (allocation_bytes-len(reference))
        result["comparisons"][name] = dict(bitwise_equal=equal, tail_unchanged=tail)
    result["passed"] = all(r["bitwise_equal"] and r["tail_unchanged"] for r in result["comparisons"].values())
    save_json(directory / "result.json", result)
    if not result["passed"]:
        raise RuntimeError("Actual PL output failed independent comparison")
    outputs = {}
    for value_id, name in [(cut["outputs"][0], "primary")] + (
            [(cut["outputs"][1], "scores")] if cut["selected_scores_used"] else []):
        path = directory / (str(value_id) + ".ftmp")
        # Strip only the allocation tail; copy actual DUT data, never the oracle.
        path.write_bytes((rtl / ("actual_0_" + name + ".bin")).read_bytes()[:len(expected[name])])
        outputs[value_id] = path
    return outputs, result


def validate(exported, directory, binding=None):
    exported, directory = exported.resolve(), directory.resolve()
    directory.mkdir(parents=True, exist_ok=False)
    manifest = json.loads((exported / "manifest.json").read_text())
    if binding is not None:
        binding = binding.resolve()
        placement = json.loads((binding / "result.json").read_text())
        if (not placement["direct_all_ports"] or not placement["cleanup_complete"] or
                placement["device_type"] != "MockZG330DeviceNode" or placement["forward_calls"] != 0):
            raise ValueError("Expected completed offline mock binding evidence")
        if bool(placement.get("native_layout")) != bool(manifest.get("native_layout")):
            raise ValueError("SDK binding and model partition use different boundary formats")
        shutil.copyfile(binding / "result.json", directory / "sdk-binding.json")
    shutil.copyfile(Path(__file__), directory / "validate_model_flow.py")
    exported_files = [exported / "manifest.json"] + [exported / (stage["name"] + suffix)
                     for stage in manifest["stages"] for suffix in (".json", ".raw")]
    save_json(directory / "export-identity.json", [dict(name=path.name,
              sha256=hashlib.sha256(path.read_bytes()).hexdigest()) for path in exported_files])
    generator = build_generator(directory / "generator")
    input_path = directory / "input_0.ftmp"
    signal = [math.sin(i*0.019)*0.5 + math.cos(i*0.007)*0.25 for i in range(180*60)]
    input_path.write_bytes(struct.pack("<10800f", *signal))
    tensors = {0: input_path}
    tensors.update(simulate_stage(exported, "npu_0", tensors, directory / "npu_0"))
    cut_results = []
    for index, cut in enumerate(manifest["cuts"]):
        memory = binding / ("cut_" + cut["name"] + ".memory") if binding is not None else None
        outputs, result = run_cut(cut, tensors, directory / ("cut_" + cut["name"]), generator, memory)
        cut_results.append(result)
        tensors.update(outputs)
        if index == 0:
            index_path = directory / "indices_486.ftmp"
            index_path.write_bytes(struct.pack("<100f", *result["indices"]))
            expanded = simulate_stage(exported, "index_expansion_a", {486: index_path}, directory / "index_expansion_a")
            expected = struct.pack("<4200f", *(i for i in result["indices"] for _ in range(42)))
            (directory / "expanded_indices.expected.bin").write_bytes(expected)
            expansion_equal = expanded[3455].read_bytes() == expected
            save_json(directory / "index-expansion-comparison.json", dict(bitwise_equal=expansion_equal))
            if not expansion_equal:
                raise RuntimeError("Original index expansion differs from row-index broadcast")
        tensors.update(simulate_stage(exported, "npu_{}".format(index+1), tensors,
                                      directory / ("npu_{}".format(index+1))))
    final = {}
    for value_id in (3483, 3487):
        data = tensors[value_id].read_bytes()
        numeric = floats(data)
        final[str(value_id)] = dict(bytes=len(data), elements=len(numeric), finite=True,
                                   minimum=min(numeric), maximum=max(numeric),
                                   sha256=hashlib.sha256(data).hexdigest(), path=str(tensors[value_id]))
    report = dict(passed=True, board_tested=False, composed_instruction_rtl_simulation=True,
                  synthetic_inputs=1, npu_hardops=manifest.get("kept_hardops", 1007), original_index_hardops=14,
                  native_layout=bool(manifest.get("native_layout")),
                  cuts=cut_results, final_outputs=final, index_expansion_equal=expansion_equal,
                  independent_full_model_baseline_compared=False,
                  hardware_completion_verified=False, performance_measured=False)
    report["sdk_mock_allocations_used"] = binding is not None
    save_json(directory / "result.json", report)
    print("TOPK_MODEL_FLOW_PASS npu_stages=3 rtl_cuts=2 original_index_expansion=PASS", flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("exported", type=Path)
    parser.add_argument("directory", type=Path)
    parser.add_argument("--binding", type=Path, help="Use retained mock SDK allocations as RTL descriptor addresses")
    arguments = parser.parse_args()
    validate(arguments.exported, arguments.directory, arguments.binding)
