"""Exercise all finite FP16 payload words through the complete compatibility DUT.

One peripheral instance executes sixteen jobs without reset. Source C16 padding
contains NaNs, logical payloads cover every finite word, and destinations alternate
between dense and C16. C++ and Python form independent expected output files.
"""

import argparse
from pathlib import Path
import struct
import sys

from runtime import ROOT, run_native, save_json
from validate_model_flow import build_generator


def pack_half(words):
    return struct.pack("<{}H".format(len(words)), *words)


def blocked(rows, padding):
    return [rows[i][block*16+lane] if block*16+lane < 42 else padding
            for block in range(3) for i in range(len(rows)) for lane in range(16)]


def normalize(word):
    return 0 if word & 0x7c00 == 0 else word


def validate(directory):
    directory.mkdir(parents=True, exist_ok=False)
    generator = build_generator(directory / "generator")
    finite = [word for word in range(65536) if word & 0x7c00 != 0x7c00]
    edges = (0, 0x8000, 1, 0x8001, 0x3ff, 0x83ff, 0x400, 0x8400, 0x3c00, 0xbc00, 0x7bff, 0xfbff)
    commands = ["16"]
    coverage = set()
    references = []
    for case in range(16):
        folder = directory / ("case_{}".format(case))
        folder.mkdir()
        words = [finite[(case*4200+i) % len(finite)] for i in range(4200)]
        coverage.update(words)
        rows = [words[i*42:(i+1)*42] for i in range(100)]
        scores = [edges[(i+case) % len(edges)] for i in range(100)]
        (folder / "scores.ftmp").write_bytes(pack_half(scores))
        (folder / "features.ftmp").write_bytes(pack_half(blocked(rows, 0x7e01)))
        numeric = struct.unpack("<100e", pack_half([normalize(word) for word in scores]))
        indices = sorted(range(100), key=lambda i: (-numeric[i], i))
        selected = [[normalize(word) for word in rows[i]] for i in indices]
        payload = blocked(selected, 0) if case % 2 == 0 else [word for row in selected for word in row]
        expected = dict(primary=pack_half(payload), scores=struct.pack("<100f", *(numeric[i] for i in indices)),
                        indices=struct.pack("<100Q", *indices))
        for name, data in expected.items():
            (folder / (name + ".expected.bin")).write_bytes(data)
        references.append(expected)
        vectors = folder / "vectors.txt"
        run_native("vectors", [generator, 100, 100, 42, folder / "scores.ftmp", folder / "features.ftmp",
                   vectors, "-", "native-f16-c16" if case % 2 == 0 else "native-f16-dense"], folder)
        lines = vectors.read_text().splitlines()
        if lines[0] != "1":
            raise ValueError("Expected one generated device command")
        lines[2] = format(case+1, "x")  # Unique low job word; high word remains unchanged.
        commands.extend(lines[1:])
    vectors = directory / "device_vectors.txt"
    vectors.write_text("\n".join(commands) + "\n", encoding="ascii")
    run_native("rtl", [sys.executable, "-B", ROOT / "tools/topk_fusion/run_rtl.py", directory / "rtl",
               "--suite", "device", "--vectors", vectors, "--flush-half-zero"], directory)
    comparisons = []
    for case, expected in enumerate(references):
        for name, reference in expected.items():
            actual = (directory / "rtl" / ("actual_{}_{}.bin".format(case, name))).read_bytes()
            padded = reference + bytes([0xa5]) * (-len(reference) % 64)
            comparisons.append(dict(case=case, output=name, bitwise_equal=actual == padded))
    result = dict(passed=all(row["bitwise_equal"] for row in comparisons), board_tested=False,
                  cases=16, distinct_finite_payload_words=len(coverage), padding_nan_excluded=True,
                  full_peripheral=True, fp16_policy="flush-half-zero", comparisons=comparisons)
    save_json(directory / "result.json", result)
    if not result["passed"] or len(coverage) != 63488:
        raise RuntimeError("Finite FP16 compatibility payload coverage failed")
    print("TOPK_NATIVE_PAYLOAD_PASS cases=16 finite_patterns=63488", flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("directory", type=Path)
    validate(parser.parse_args().directory.resolve())
