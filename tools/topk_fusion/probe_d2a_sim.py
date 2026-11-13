"""Exercise the vendor's host-only DataTile D2a simulation with owned buffers.

No device is opened and no instruction is submitted. The Windows x64 object
layout is transcribed from public ZgTile fields and checked against constructor
disassembly (vptr at 0, integer fields at 8..72, data pointer at 80). This binding
is deliberately isolated from deployment code and specific to SDK 3.39.0.
"""

import argparse
import ctypes as ct
import hashlib
import os
from pathlib import Path
import random
import struct
import sys

from runtime import ICRAFT_BIN, save_json


class DataTile(ct.Structure):
    _fields_ = [("vptr", ct.c_void_p)] + [(name, ct.c_int32) for name in (
        "kind", "unit", "base", "width", "height", "width_stride", "height_stride",
        "column", "row", "sub_id", "dtype", "int8_half", "sub_count", "sub_stride",
        "group", "core", "external_control")] + [("data", ct.c_void_p)]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("directory", type=Path)
    args = parser.parse_args()
    if sys.platform != "win32" or ct.sizeof(ct.c_void_p) != 8:
        raise RuntimeError("This inspected ABI is Windows x64 only")
    if ct.sizeof(DataTile) != 88 or DataTile.data.offset != 80 or DataTile.width.offset != 20:
        raise RuntimeError("DataTile layout differs from inspected SDK")
    args.directory.mkdir(parents=True, exist_ok=False)
    dll_handle = os.add_dll_directory(str(ICRAFT_BIN))
    library_path = ICRAFT_BIN / "byzg-tile.dll"
    library = ct.CDLL(str(library_path))
    constructor = getattr(library, "??0DataTile@zgt@@QEAA@XZ")
    constructor.argtypes = [ct.POINTER(DataTile)]
    constructor.restype = ct.c_void_p
    gather = getattr(library, "?AssignByD2a@DataTile@zgt@@QEAAXAEAV12@0HHH@Z")
    gather.argtypes = [ct.POINTER(DataTile)] * 3 + [ct.c_int32] * 3
    gather.restype = None

    def tile(buffer, count, unit):
        result = DataTile()
        constructor(ct.byref(result))
        if result.kind != 11 or result.unit != 16 or result.dtype != 1 or result.data:
            raise RuntimeError("Vendor constructor disagrees with expected public layout")
        result.kind = 5  # TileType::ETM, from the public enumeration.
        result.dtype = 5  # TF32 simulator storage is an array of native float words.
        result.unit = unit
        result.width = count
        result.height = 1
        result.width_stride = 1
        result.height_stride = count
        result.data = ct.addressof(buffer)
        return result

    rng = random.Random(330)
    cases = []
    for n, k, c in [(3, 2, 1), (180, 100, 42), (100, 50, 42), (100, 100, 42), (257, 127, 16)]:
        selected = rng.sample(range(n), k)
        words = [rng.getrandbits(32) for _ in range(n * c)]
        words[:min(8, len(words))] = [0, 0x80000000, 1, 0x80000001, 0x7fc00001,
                                    0x7f7fffff, 0xff7fffff, 0x00800000][:min(8, len(words))]
        payload = (ct.c_uint32 * (n*c + 16))(*words, *([0xcafebeef] * 16))
        coordinates = (ct.c_float * (k*2 + 16))()
        for row, index in enumerate(selected):
            coordinates[2*row] = 0.0
            coordinates[2*row+1] = float(index)
        destination = (ct.c_uint32 * (k*c + 16))(*([0xa5a5a5a5] * (k*c + 16)))
        coordinate_tile = tile(coordinates, k, 2)
        payload_tile = tile(payload, n, c)
        output_tile = tile(destination, k, c)
        # Inferred equation in mode 0:
        # address = (coord[0] * height + coord[1] * width) * channels + lane.
        # w=1,h=0 therefore selects an entire row, without arithmetic on payload.
        reference = [words[index*c + lane] for index in selected for lane in range(c)]
        prefix = args.directory / "n{}_k{}_c{}".format(n, k, c)
        prefix.with_suffix(".expected.u32").write_bytes(struct.pack("<{}I".format(len(reference)), *reference))
        gather(ct.byref(output_tile), ct.byref(coordinate_tile), ct.byref(payload_tile), 1, 0, 0)
        actual = list(destination[:k*c])
        prefix.with_suffix(".actual.u32").write_bytes(struct.pack("<{}I".format(len(actual)), *actual))
        passed = actual == reference and list(destination[k*c:]) == [0xa5a5a5a5] * 16
        passed = passed and list(payload[n*c:]) == [0xcafebeef] * 16 and list(payload[:n*c]) == words
        cases.append(dict(n=n, k=k, channels=c, bitwise_equal=passed))
        print(cases[-1], flush=True)
        if not passed:
            raise RuntimeError("D2a simulation disagrees with inferred mode 0 semantics")
    save_json(args.directory / "result.json", dict(host_datatile_simulation=True,
              generated_instruction_simulation=False, board_tested=False,
              dll_sha256=hashlib.sha256(library_path.read_bytes()).hexdigest(), cases=cases))
    dll_handle.close()


if __name__ == "__main__":
    main()
