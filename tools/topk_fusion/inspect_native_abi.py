"""Read-only DLL export/disassembly evidence; never calls inferred SDK ABIs."""

import argparse
import hashlib
from pathlib import Path
import struct
import subprocess

from runtime import save_json


def exports(path):
    data = path.read_bytes()
    pe = struct.unpack_from("<I", data, 0x3c)[0]
    if data[pe:pe + 4] != b"PE\0\0":
        raise ValueError("Not a PE image")
    sections, optional_size = struct.unpack_from("<H12xH", data, pe + 6)
    optional = pe + 24
    if struct.unpack_from("<H", data, optional)[0] != 0x20b:
        raise ValueError("Only PE32+ is supported")
    image_base = struct.unpack_from("<Q", data, optional + 24)[0]
    export_rva = struct.unpack_from("<I", data, optional + 112)[0]
    table = []
    for i in range(sections):
        entry = optional + optional_size + i * 40
        virtual_size, rva, raw_size, offset = struct.unpack_from("<IIII", data, entry + 8)
        table.append((rva, max(virtual_size, raw_size), offset))

    def offset(rva):
        for start, size, physical in table:
            if start <= rva < start + size:
                return physical + rva - start
        raise ValueError("RVA outside image")

    directory = offset(export_rva)
    count = struct.unpack_from("<I", data, directory + 24)[0]
    functions, names, ordinals = struct.unpack_from("<III", data, directory + 28)
    result = {}
    for i in range(count):
        name_start = offset(struct.unpack_from("<I", data, offset(names) + 4*i)[0])
        name = data[name_start:data.index(b"\0", name_start)].decode("ascii")
        ordinal = struct.unpack_from("<H", data, offset(ordinals) + 2*i)[0]
        function_rva = struct.unpack_from("<I", data, offset(functions) + 4*ordinal)[0]
        result[name] = image_base + function_rva
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("directory", type=Path)
    args = parser.parse_args()
    args.directory.mkdir(parents=True, exist_ok=False)
    records = []
    targets = {"byzg-task.dll": ("?tileTypeCheck@D2aTask", "?taskSim@D2aTask", "?d2aInstGen@D2aTask"),
               "byzg-tile.dll": ("?AssignByD2a@DataTile", "?assignToStreamD2aIS@DataTile")}
    for filename, prefixes in targets.items():
        path = Path("C:/Icraft/CLI v3.39.0/bin") / filename
        symbols = exports(path)
        addresses = sorted(set(symbols.values()))
        for prefix in prefixes:
            name, address = next((n, a) for n, a in symbols.items() if n.startswith(prefix))
            # The next exported entry bounds evidence, not necessarily function size.
            stop = min(next((a for a in addresses if a > address), address + 8192), address + 8192)
            argv = ["objdump", "-d", "-Mintel", "--start-address=" + hex(address),
                    "--stop-address=" + hex(stop), str(path)]
            result = subprocess.run(argv, capture_output=True)
            output = args.directory / (filename + "-" + prefix.split("@")[0][1:] + ".asm")
            output.write_bytes(result.stdout + result.stderr)
            records.append(dict(dll=str(path), sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
                                symbol=name, address=hex(address), stop=hex(stop),
                                native_exit=result.returncode, disassembly=str(output)))
            if result.returncode:
                raise RuntimeError("Native disassembly failed")
    save_json(args.directory / "evidence.json", records)
    for record in records:
        print(record["symbol"], record["address"], record["disassembly"])


if __name__ == "__main__":
    main()
