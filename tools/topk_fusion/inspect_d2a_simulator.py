"""Read-only evidence for the installed SDK 3.39 default simulator's D2a path.

This is a version-specific disassembly audit, not a hardware instruction decoder
or a patched simulator. Known bytes are checked before drawing any conclusion.
No DLL is loaded/called or modified; generated instruction files are read only.
"""

import argparse
import hashlib
from pathlib import Path
import re
import struct

from runtime import ICRAFT_BIN, run_native, save_json


def image_reader(path):
    data = path.read_bytes()
    pe = struct.unpack_from("<I", data, 0x3c)[0]
    if data[pe:pe + 4] != b"PE\0\0":
        raise ValueError("Not PE")
    sections, optional_size = struct.unpack_from("<H12xH", data, pe + 6)
    optional = pe + 24
    if struct.unpack_from("<H", data, optional)[0] != 0x20b:
        raise ValueError("Not PE32+")
    base = struct.unpack_from("<Q", data, optional + 24)[0]
    table = []
    for index in range(sections):
        entry = optional + optional_size + index * 40
        _, rva, size, offset = struct.unpack_from("<IIII", data, entry + 8)
        table.append((rva, size, offset))

    def read(address, count):
        rva = address - base
        for start, size, offset in table:
            if start <= rva and rva + count <= start + size:
                return data[offset + rva - start:offset + rva - start + count]
        raise ValueError("Requested evidence crosses an image section")

    return read


def classify(path):
    records = []
    for line in path.read_text().splitlines():
        match = re.search(r"RETM.*-> \[([0-9A-F]{8})\]", line)
        if not match:
            continue
        control = int(match[1], 16)
        records.append(dict(control=hex(control), status_mode=bool(control & 0xf00),
                            d2a_mask=hex(control & 0x600000),
                            direct_return_without_read=not (control & 0xf00) and bool(control & 0x600000),
                            decoded_line=line))
    if not records:
        raise ValueError("No decoded RETM controls")
    return records


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("directory", type=Path)
    parser.add_argument("--d2a-log", type=Path, required=True)
    parser.add_argument("--copy-log", type=Path, required=True)
    args = parser.parse_args()
    directory = args.directory.resolve()
    directory.mkdir(parents=True, exist_ok=False)
    dll = ICRAFT_BIN / "icraft-fireby.dll"
    read = image_reader(dll)
    checks = {
        # Vpe::parseCodes RETM case calls the inspected constructor.
        0x180026ea7: bytes.fromhex("e8 34 06 01 00"),
        # Constructor installs vtable 0x18004e9c0.
        0x18003752f: bytes.fromhex("48 8d 05 8a 74 01 00 48 89 01"),
        # Third vtable slot is the executing method.
        0x18004e9d0: struct.pack("<Q", 0x18003fbe0),
        # Load decoded IEM control word 6, distinguish status operations.
        0x18003fbf5: bytes.fromhex("4c 8b 43 28 41 8b 50 18 8b ca 81 e1 00 0f 00 00 75 1d"),
        # For ordinary RETM, either D2a flag branches directly to the return.
        0x18003fc07: bytes.fromhex("f7 c2 00 00 60 00 0f 85 1a 01 00 00"),
        # Only the unflagged path tail-calls Vpe::readEtm.
        0x18003fc1f: bytes.fromhex("e9 9c 7f fe ff"),
        0x18003fd2d: bytes.fromhex("48 83 c4 50 5b c3"),
    }
    for address, expected in checks.items():
        if read(address, len(expected)) != expected:
            raise RuntimeError("SDK differs from audited code at " + hex(address))
    for name, start, stop in (("retm_constructor", 0x1800374e0, 0x1800376b0),
                              ("retm_execute", 0x18003fbe0, 0x18003fd40),
                              ("parse_codes", 0x180026e20, 0x180026eb2)):
        run_native(name, ["objdump", "-d", "-Mintel", "--start-address=" + hex(start),
                         "--stop-address=" + hex(stop), dll], directory)
    d2a, copy = classify(args.d2a_log), classify(args.copy_log)
    if len(d2a) != 2 or not all(item["direct_return_without_read"] for item in d2a):
        raise RuntimeError("D2a fixture does not exercise the audited branch")
    if len(copy) != 1 or copy[0]["direct_return_without_read"] or copy[0]["status_mode"]:
        raise RuntimeError("Copy control does not exercise normal RETM")
    evidence = dict(dll=str(dll), sha256=hashlib.sha256(dll.read_bytes()).hexdigest(),
                    version_scope="installed Windows SDK 3.39.0 only",
                    checked_addresses=[hex(address) for address in checks],
                    d2a_retms=d2a, copy_retms=copy,
                    conclusion="Both generated D2a RETMs take a direct return in this simulator's execution method; normal copy takes readEtm.",
                    hardware_support_proven=False, board_tested=False, sdk_modified=False)
    save_json(directory / "evidence.json", evidence)
    print(evidence["conclusion"])


if __name__ == "__main__":
    main()
