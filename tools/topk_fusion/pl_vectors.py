"""Generate independent numeric references for the RTL stream tests."""

from pathlib import Path
import random
import struct


def bits(value):
    return struct.unpack("<I", struct.pack("<f", value))[0]


def value(word):
    return struct.unpack("<f", struct.pack("<I", word))[0]


def ordered(records):
    # Python numeric comparisons, independent of the RTL's bit ordering key.
    return sorted(records, key=lambda record: (-value(record[0]), record[1]))


def make_vectors(directory):
    directory = Path(directory)
    rng = random.Random(20261113)
    tile_cases = []
    for n, k in [(1, 1), (180, 100), (100, 50), (100, 100), (256, 256), (256, 1), (33, 17)]:
        for mode in ("ascending", "descending", "ties", "random", "edges"):
            base = (1 << 40) + len(tile_cases) * 512
            edge_bits = [0, 0x80000000, 1, 0x80000001, 0x7f7fffff, 0xff7fffff,
                         0x00800000, 0x80800000, bits(1), bits(-1)]
            scores = {"ascending": lambda i: bits(i - n / 2),
                      "descending": lambda i: bits(n / 2 - i),
                      "ties": lambda i: bits(i % 3 - 1),
                      "random": lambda i: bits(rng.uniform(-1e4, 1e4)),
                      "edges": lambda i: edge_bits[i % len(edge_bits)]}
            records = [(scores[mode](i), base + i) for i in range(n)]
            tile_cases.append((n, k, base, 0, records, ordered(records)[:k]))
    for _ in range(100):
        n = rng.randint(1, 256)
        k = rng.randint(1, n)
        base = rng.randrange(1 << 48)
        records = [(bits(rng.randint(-32, 32) / 8), base + i) for i in range(n)]
        tile_cases.append((n, k, base, 0, records, ordered(records)[:k]))
    for bad_score in (0x7fc00000, 0x7f800000, 0xff800000):
        records = [(bits(float(i)), i) for i in range(20)]
        records[7] = (bad_score, 7)
        tile_cases.append((20, 7, 0, 2, records, []))
    tile_cases.extend([(0, 0, 0, 1, [], []),
                       (1, 2, 0, 1, [(bits(1), 0)], []),
                       (2, 1, (1 << 64) - 1, 1, [(bits(1), 0), (bits(2), 1)], [])])
    with (directory / "tile_vectors.txt").open("w", encoding="ascii") as stream:
        stream.write(str(len(tile_cases)) + "\n")
        for n, k, base, error, records, expected in tile_cases:
            stream.write("{} {} {:016x} {}\n".format(n, k, base, error))
            for score, _ in records:
                stream.write("{:08x}\n".format(score))
            for score, index in expected:
                stream.write("{:08x} {:016x}\n".format(score, index))

    merge_cases = []
    for _ in range(120):
        nl, nr = rng.randint(0, 256), rng.randint(0, 256)
        if nl + nr == 0:
            nr = 1
        keep = rng.randint(1, nl + nr)
        left = ordered([(bits(rng.randint(-8, 8)), i) for i in range(nl)])
        right = ordered([(bits(rng.randint(-8, 8)), nl + i) for i in range(nr)])
        merge_cases.append((left, right, keep, ordered(left + right)[:keep], 0))
    # Nonfinite values after the retained prefix still invalidate the job.
    # Earlier output records remain unpublished until successful completion.
    for bad in (0x7fc00000, 0x7f800000, 0xff800000):
        merge_cases.append(([(bits(3), 0), (bits(2), 1), (bad, 2)],
                            [(bits(1), 3)], 1, [(bits(3), 0)], 2))
        merge_cases.append(([(bits(3), 0)],
                            [(bits(2), 1), (bits(1), 2), (bad, 3)], 1, [(bits(3), 0)], 2))
    merge_cases.extend([([], [], 0, [], 1), ([(bits(1), 0)], [], 2, [], 1),
                        ([], [(bits(1), 0)], 0, [], 1)])
    with (directory / "merge_vectors.txt").open("w", encoding="ascii") as stream:
        stream.write(str(len(merge_cases)) + "\n")
        for left, right, keep, expected, error in merge_cases:
            stream.write("{} {} {} {}\n".format(len(left), len(right), keep, error))
            for score, index in left + right + expected:
                stream.write("{:08x} {:016x}\n".format(score, index))
    return dict(tile_cases=len(tile_cases), merge_cases=len(merge_cases))


def make_gather_vectors(directory, fused=False, memory_output=False, sorted_run=False):
    """Pack logical values through independent Python lists into both layouts."""
    directory = Path(directory)
    rng = random.Random(33042)
    shapes = [(180, 100, 42), (100, 50, 42), (100, 100, 42),
              (1, 1, 1), (31, 17, 17), (33, 13, 65), (257, 11, 3)]
    rows = [(n, k, c, size, source, destination, 0)
            for n, k, c in shapes for size in (2, 4)
            for source, destination in ((0, 0), (0, 1), (1, 0), (1, 1))]
    rows += [(33, 17, 19, 4, 1, 1, fault) for fault in range(1, 8)]
    if fused:
        # The fused fast path emits its own legal indices and has capacity 256.
        rows = [row for row in rows if row[0] <= 256 and row[-1] != 1]
        rows += [(33, 17, 19, 4, 1, 1, fault) for fault in range(8, 12)]
        if memory_output:
            rows += [(33, 17, 19, 4, 1, 1, fault) for fault in range(12, 17)]
            rows.append((256, 256, 17, 2, 1, 1, 0))
            rows.append((100, 50, 42, 2, 1, 1, 17))
    if sorted_run:
        rows += [(n, k, c, size, source, destination, 0)
                 for n, k, c in ((513, 400, 42), (1025, 513, 42), (1025, 1025, 17))
                 for size in (2, 4)
                 for source, destination in ((0, 0), (0, 1), (1, 0), (1, 1))]
        rows += [(33, 17, 19, 4, 1, 1, fault) for fault in (1, 18)]
        rows.append((180, 100, 42, 2, 1, 1, 0))  # Healthy job after malformed runs.

    def pack(logical, count, channels, element_bytes, blocked, fill):
        width = (channels + 15) // 16 * 16 if blocked else channels
        storage = bytearray([fill] * ((count * width * element_bytes + 63) // 64 * 64))
        physical = []
        if blocked:
            for group in range(width // 16):
                for row in logical:
                    physical.extend(row[group * 16:group * 16 + 16] +
                                    [0] * max(0, min(16, group * 16 + 16 - channels)))
        else:
            physical = [item for row in logical for item in row]
        for index, word in enumerate(physical):
            storage[index * element_bytes:(index + 1) * element_bytes] = word.to_bytes(element_bytes, "little")
        return storage

    with (directory / "gather_vectors.txt").open("w", encoding="ascii") as stream:
        stream.write(str(len(rows)) + "\n")
        for n, k, c, size, source, destination, fault in rows:
            logical = [[rng.getrandbits(size * 8) for _ in range(c)] for _ in range(n)]
            indices = rng.sample(range(n), k)
            if fault == 16:
                indices = list(range(k))  # All scores are signed zeros; lower index wins.
            source_data = pack(logical, n, c, size, source, 0xa5)
            expected = pack([logical[i] for i in indices], k, c, size, destination, 0xa5)
            if fault == 1:
                indices[3] = n  # Invalid index must be rejected before a memory access.
            expected_error = {0: 0, 1: 3, 2: 5, 3: 6, 4: 1, 5: 4, 6: 7, 7: 0,
                              8: 5, 9: 2, 10: 1, 11: 1,
                              12: 1, 13: 1, 14: 1, 15: 1, 16: 0, 17: 5, 18: 4}[fault]
            if sorted_run and fault == 1:
                expected_error = 4  # Packed record rejected before Gather.
            stream.write("{} {} {} {} {} {} {} {} {} {}\n".format(
                n, k, c, size, source, destination, len(source_data), len(expected), fault, expected_error))
            for index in indices:
                stream.write("{:016x}\n".format(index))
            for storage in (source_data, expected):
                for offset in range(0, len(storage), 64):
                    stream.write(storage[offset:offset + 64][::-1].hex() + "\n")
    return dict(gather_cases=len(rows))


def make_score_vectors(directory, flush_half_zero=False):
    directory = Path(directory)
    rng = random.Random(33016)
    rows = [(65536, 2, 0)] + [(n, size, 0) for n in (1, 33, 100, 180, 257) for size in (2, 4)]
    rows += [(180, 2, 1), (180, 2, 2), (180, 4, 2)]
    with (directory / "score_vectors.txt").open("w", encoding="ascii") as stream:
        stream.write(str(len(rows)) + "\n")
        for n, size, fault in rows:
            words = list(range(65536)) if n == 65536 else [rng.getrandbits(size * 8) for _ in range(n)]
            data = b"".join(word.to_bytes(size, "little") for word in words)
            data += bytes((-len(data)) % 64)
            stream.write("{} {} {} {}\n".format(n, size, len(data), fault))
            for offset in range(0, len(data), 64):
                stream.write(data[offset:offset + 64][::-1].hex() + "\n")
            for word in words:
                if size == 4:
                    expected = word
                elif word & 0x7c00 == 0x7c00 and word & 0x3ff:
                    # NaN payload/sign expansion has an explicit bit contract;
                    # Python's arithmetic conversion may quiet a signaling NaN.
                    expected = (word & 0x8000) << 16 | 0x7f800000 | (word & 0x3ff) << 13
                else:
                    expected = bits(struct.unpack("<e", word.to_bytes(2, "little"))[0])
                if flush_half_zero and size == 2 and word & 0x7c00 == 0:
                    expected = 0
                stream.write("{:08x}\n".format(expected))
    return dict(score_cases=len(rows), exhaustive_half_patterns=65536)


def make_pipeline_vectors(directory, memory_output=False):
    directory = Path(directory)
    make_vectors(directory)
    tokens = iter((directory / "tile_vectors.txt").read_text().split())
    rows = []
    for _ in range(int(next(tokens))):
        n, k, base, error = int(next(tokens)), int(next(tokens)), int(next(tokens), 16), int(next(tokens))
        scores = [int(next(tokens), 16) for _ in range(n)]
        expected = [(int(next(tokens), 16), int(next(tokens), 16)) for _ in range(k)] if error == 0 else []
        rows.append((n, k, base, error, 4, scores, expected))
    for n, k in ((180, 100), (100, 50), (100, 100)):
        half = [0x8000, 0, 1, 0x8001, 0x7bff, 0xfbff, 0x3c00, 0xbc00]
        scores = [half[i % len(half)] for i in range(n)]
        expanded = [bits(struct.unpack("<e", word.to_bytes(2, "little"))[0]) for word in scores]
        rows.append((n, k, 0, 0, 2, scores, ordered([(word, i) for i, word in enumerate(expanded)])[:k]))
    for size in (2, 4):
        rows.append((180, 100, 0, 5, size, [0] * 180, []))
    faults = [0] * len(rows)
    if memory_output:
        healthy = next(row for row in rows if row[0:2] == (33, 17) and row[3] == 0)
        for fault, error in ((1, 1), (2, 1), (3, 6), (4, 7)):
            n, k, base, _, size, scores, expected = healthy
            rows.extend([(n, k, base, error, size, scores, []), healthy])
            faults.extend([fault, 0])
    with (directory / "pipeline_vectors.txt").open("w", encoding="ascii") as stream:
        stream.write(str(len(rows)) + "\n")
        for (n, k, base, error, size, scores, expected), fault in zip(rows, faults):
            data = b"".join(word.to_bytes(size, "little") for word in scores)
            data += bytes(max(64, (len(data) + 63) // 64 * 64) - len(data))
            header = "{} {} {:016x} {} {} {}".format(n, k, base, error, size, len(data))
            stream.write(header + (" " + str(fault) if memory_output else "") + "\n")
            for offset in range(0, len(data), 64):
                stream.write(data[offset:offset + 64][::-1].hex() + "\n")
            for score, index in expected:
                stream.write("{:08x} {:016x}\n".format(score, index))
    return dict(score_sort_pipeline_cases=len(rows))
