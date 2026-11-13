"""Connect actual tiled-sort RTL results to the independent Gather RTL test.

The expected result is recomputed from the C++ plan's original scores. Actual
indices come only from tb_plan; no reference index is substituted into the DUT.
This is a file-connected RTL test, not a board or bus integration test.
"""

import argparse
from pathlib import Path
import random
import struct

from runtime import save_json


def read_reference(path):
    tokens = iter(path.read_text().split())
    reference = {}
    for case in range(int(next(tokens))):
        batches, n, k, jobs = [int(next(tokens)) for _ in range(4)]
        scores = [[struct.unpack("<f", int(next(tokens), 16).to_bytes(4, "little"))[0]
                   for _ in range(n)] for _ in range(batches)]
        for _ in range(jobs * 8):
            next(tokens)
        for batch in range(batches):
            recorded = [(int(next(tokens), 16), int(next(tokens), 16)) for _ in range(k)]
            winners = sorted(range(n), key=lambda i: (-scores[batch][i], i))[:k]
            if winners != [index for _, index in recorded]:
                raise ValueError("Plan reference does not match independent numeric sort")
            reference[case, batch] = n, k, winners
    if next(tokens, None) is not None:
        raise ValueError("Trailing plan tokens")
    return reference


def pack_rows(logical, channels, size, blocked):
    rows = len(logical)
    physical_channels = (channels + 15) // 16 * 16 if blocked else channels
    used = rows * physical_channels * size
    data = bytearray([0xa5] * ((used + 63) // 64 * 64))
    # Explicit coordinate mapping is independent of the RTL's incremental
    # address generation and of pl_vectors.py's sequential packing algorithm.
    for row in range(rows):
        for channel in range(physical_channels):
            offset = (((channel // 16) * rows + row) * 16 + channel % 16
                      if blocked else row * channels + channel) * size
            word = logical[row][channel] if channel < channels else 0
            data[offset:offset + size] = word.to_bytes(size, "little")
    return data


def generate(plan, selected, output, actual_runs=None):
    reference = read_reference(plan)
    records = {}
    if actual_runs is not None:
        tokens = iter(actual_runs.read_text().split())
        while True:
            case_token = next(tokens, None)
            if case_token is None:
                break
            case, batch, n, k = int(case_token), int(next(tokens)), int(next(tokens)), int(next(tokens))
            key = case, batch
            if key in records or key not in reference or (n, k) != reference[key][:2]:
                raise ValueError("Invalid actual record batch")
            rows = [(int(next(tokens), 16), int(next(tokens), 16)) for _ in range(k)]
            if [index for _, index in rows] != reference[key][2]:
                raise ValueError("Actual record indices differ from independent reference")
            records[key] = rows
        if set(records) != set(reference):
            raise ValueError("Missing actual record batch")
    lines = iter(selected.read_text().splitlines())
    cases, selected_records, seen = [], [], set()
    rng = random.Random(3301311)
    for header in lines:
        case, batch, n, k = map(int, header.split())
        key = case, batch
        if key in seen or key not in reference:
            raise ValueError("Duplicate or unknown RTL batch")
        seen.add(key)
        indices = [int(next(lines), 16) for _ in range(k)]
        ref_n, ref_k, winners = reference[key]
        if (n, k) != (ref_n, ref_k) or indices != winners:
            raise ValueError("Actual sort RTL indices differ from independent reference")
        channels = 42
        for size in (2, 4):
            logical = [[rng.getrandbits(size * 8) for _ in range(channels)] for _ in range(n)]
            for src_blocked, dst_blocked in ((0, 0), (0, 1), (1, 0), (1, 1)):
                source = pack_rows(logical, channels, size, src_blocked)
                expected = pack_rows([logical[i] for i in winners], channels, size, dst_blocked)
                cases.append((n, k, channels, size, src_blocked, dst_blocked, indices, source, expected))
                if records:
                    selected_records.append(records[key])
    if seen != set(reference):
        raise ValueError("Missing actual RTL batch")
    with output.open("x", encoding="ascii") as stream:
        stream.write(str(len(cases)) + "\n")
        for n, k, c, size, src, dst, indices, source, expected in cases:
            stream.write("{} {} {} {} {} {} {} {} 0 0\n".format(n, k, c, size, src, dst,
                         len(source), len(expected)))
            for index in indices:
                stream.write("{:016x}\n".format(index))
            for data in (source, expected):
                for offset in range(0, len(data), 64):
                    stream.write(data[offset:offset + 64][::-1].hex() + "\n")
    if selected_records:
        with Path(str(output) + ".records").open("x", encoding="ascii") as stream:
            for rows in selected_records:
                for score, index in rows:
                    stream.write("{:08x} {:016x}\n".format(score, index))
    save_json(output.with_suffix(".json"), dict(cases=len(cases), actual_rtl_batches=len(seen),
              plan=str(plan.resolve()), selected_indices=str(selected.resolve()), board_tested=False))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("plan", type=Path)
    parser.add_argument("selected", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--actual-runs", type=Path, help="Use actual packed-run scores and indices for the final memory kernel")
    args = parser.parse_args()
    generate(args.plan, args.selected, args.output, args.actual_runs)
