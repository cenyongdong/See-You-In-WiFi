"""Compile isolated XIR graphs to ZG330 and retain instruction simulator output."""

import argparse
import collections
import json
from pathlib import Path
import struct

from runtime import (ROOT, ICRAFT_BIN, ICRAFT_PYTHON, icraft_environment,
                     run_native, save_json)


def compile_graph(directory, n, k, channels, algorithm):
    directory = directory.resolve()
    directory.mkdir(parents=True, exist_ok=False)
    environment = icraft_environment()
    # Icraft adaptation otherwise shares %TEMP%/icraftAdapterMergeFile/<name>.
    # Concurrent models with the same network name can destroy each other's files.
    temporary = directory / "tmp"
    temporary.mkdir()
    environment.update(TEMP=str(temporary), TMP=str(temporary))
    run_native("build", [ICRAFT_PYTHON, "-B", ROOT / "tools/topk_fusion/build_native.py",
               directory, "--n", n, "--k", k, "--channels", channels,
               "--algorithm", algorithm], directory, environment)
    stages = [("optimize", "parsed"), ("quantize", "optimized"),
              ("adapt", "quantized"), ("generate", "adapted")]
    sections = []
    for stage, source in stages:
        section = ['[{}]'.format(stage), 'json = "./topk_native_{}.json"'.format(source),
                   'raw = "./topk_native_{}.raw"'.format(source), 'jr_path = "./"',
                   'log_path = "./logs/{}"'.format(stage)]
        if stage != "generate":
            section.append('target = "zhuge"')
        if stage == "quantize":
            section.append('qdtype = "tf32"')
        if stage == "generate":
            section.extend(["rows = 4", "cols = 4", "cores = 1", "dump_instlogs = true"])
        sections.append("\n".join(section))
    config = directory / "compile.toml"
    config.write_text("\n\n".join(sections) + "\n", encoding="utf-8")
    for stage, _ in stages:
        run_native(stage, [ICRAFT_BIN / "icraft.exe", stage, config], directory, environment)
    graph = json.loads((directory / "topk_native_ZG.json").read_text(encoding="utf-8"))
    host = [op for op in graph["ops"] if op["compile_target"] == "@hostt"
            and op["_type_key"] not in ("icraft::xir::Input", "icraft::xir::Output")]
    if host:
        raise RuntimeError("The candidate retained Host computation: " + repr(host))
    report = dict(target=graph["ai_target"], board_tested=False,
                  operators=dict(collections.Counter(op["_type_key"] for op in graph["ops"])),
                  instruction_bytes=sum(p["dtype"]["shape"][0] * 8 for op in graph["ops"]
                                        for p in op.get("instr", [])),
                  raw_bytes=(directory / "topk_native_ZG.raw").stat().st_size)
    save_json(directory / "compilation.json", report)
    return graph


def simulate(directory, graph, scores, payload, name, runtime_counts=None, use_fireby=False, dump_format="SFB"):
    """Pack each port's FP16/FP32 storage and retain complete simulator outputs."""
    environment = icraft_environment()
    if dump_format not in ("SFB", "HQB"):
        raise ValueError("Unsupported simulator output representation")
    folder = directory / name
    folder.mkdir(exist_ok=False)
    temporary = folder / "tmp"
    temporary.mkdir()
    environment.update(TEMP=str(temporary), TMP=str(temporary))
    inputs = next(op["outputs"] for op in graph["ops"] if op["_type_key"] == "icraft::xir::Input")
    fixtures = [scores, payload]
    if runtime_counts is not None:
        n, k = runtime_counts
        max_n = inputs[0]["dtype"]["shape"][-1]
        max_k = inputs[3]["dtype"]["shape"][0]
        if not (1 <= k <= n <= max_n and k <= max_k):
            raise ValueError("Runtime counts exceed the compiled capacity")
        fixtures.extend([[float(i < n) for i in range(max_n)],
                         [float(i < k) for i in range(max_k)]])
    if len(inputs) != len(fixtures):
        raise ValueError("Input count does not match the compiled graph")
    paths = []
    for index, port in enumerate(inputs):
        data = fixtures[index]
        path = folder / ("input_{}.ftmp".format(index))
        element = port["dtype"]["element_dtype"]
        if isinstance(element, dict):
            element = element["storage_dtype"]
        if element not in ("@fp(16)", "@fp(32)", "@tf(32)"):
            raise ValueError("Fixture writer requires explicit FP16 or FP32 input storage")
        format_code = "e" if element == "@fp(16)" else "f"
        path.write_bytes(struct.pack("<{}{}".format(len(data), format_code), *data))
        paths.append(path.as_posix())
    outputs = next(op["inputs"] for op in graph["ops"] if op["_type_key"] == "icraft::xir::Output")
    config = folder / "run.toml"
    config.write_text('[run]\njson = "' + (directory / "topk_native_ZG.json").as_posix() + '"\n'
                      'raw = "' + (directory / "topk_native_ZG.raw").as_posix() + '"\n'
                      'input = "' + ";".join(paths) + '"\nbackends = "Host"\n'
                      'use_fireby = ' + str(use_fireby).lower() + '\n'
                      'dump_format = "' + dump_format + '"\ndump_ftmp = "' +
                      ",".join(str(port["v_id"]) for port in outputs) + '"\n'
                      'log_path = "' + (folder / "native").as_posix() + '"\n', encoding="utf-8")
    run_native("simulate", [ICRAFT_BIN / "icraft.exe", "run", config], folder, environment)
    save_json(folder / "expected.json", dict(scores=scores, payload=payload,
              sorted_indices=sorted(range(len(scores)), key=lambda i: (-scores[i], i)),
              outputs=outputs))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("directory", type=Path)
    parser.add_argument("--n", type=int, default=8)
    parser.add_argument("--k", type=int, default=3)
    parser.add_argument("--channels", type=int, default=3)
    parser.add_argument("--algorithm", choices=("argmax", "selection", "rank", "rank_dynamic"), default="argmax")
    args = parser.parse_args()
    directory = args.directory.resolve()
    graph = compile_graph(directory, args.n, args.k, args.channels, args.algorithm)
    scores = [float(i % 5 - 2) for i in range(args.n)]
    payload = [float(i) / 16 for i in range(args.n * args.channels)]
    simulate(directory, graph, scores, payload, "ties",
             (args.n, args.k) if args.algorithm == "rank_dynamic" else None)
