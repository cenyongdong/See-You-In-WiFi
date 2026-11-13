"""Isolated SDK 3.39.0 D2a instruction experiment; never opens a device.

The incomplete vendor headers prevent normal C++ compilation. These Windows
x64 bindings use the inspected public ZgTile layout and MSVC release ABI.
Native tasks, vectors and simulator state live only in this child process;
the process boundary reclaims them, including on a vendor exception. This
experimental binding must not be imported into a deployed service.
"""

import argparse
import ctypes as ct
import hashlib
import json
import os
from pathlib import Path
import random
import struct

from inspect_native_abi import exports
from probe_d2a_sim import DataTile
from runtime import ICRAFT_BIN, save_json


class ZgTile(ct.Structure):
    _fields_ = DataTile._fields_[:-1]


class Vector(ct.Structure):
    _fields_ = [(name, ct.c_void_p) for name in ("begin", "end", "capacity")]

    @classmethod
    def view(cls, buffer):
        start = ct.addressof(buffer)
        return cls(start, start + ct.sizeof(buffer), start + ct.sizeof(buffer))

    def count(self, item_bytes):
        length = (self.end or 0) - (self.begin or 0)
        if length < 0 or length % item_bytes or length > 64 * 1024 * 1024:
            raise RuntimeError("Unexpected native vector extent")
        return length // item_bytes


class ShortString(ct.Structure):
    _fields_ = [("text", ct.c_char * 16), ("length", ct.c_size_t), ("capacity", ct.c_size_t)]

    @classmethod
    def make(cls, text):
        data = text.encode("ascii")
        if len(data) > 15:
            raise ValueError("Only SSO strings are allowed in this probe")
        return cls(data, len(data), 15)


class EtmInfo(ct.Structure):
    # Opaque storage: use the public constructor, setters and getters only.
    # 72-byte size verified from the native constructor/copy implementation.
    _fields_ = [("storage", ct.c_uint64 * 9)]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("directory", type=Path)
    parser.add_argument("--n", type=int, default=8)
    parser.add_argument("--k", type=int, default=3)
    parser.add_argument("--channels", type=int, default=16)
    parser.add_argument("--object-simulation", action="store_true")
    parser.add_argument("--restore-logical-dma", action="store_true",
                        help="Host-only diagnosis: restore logical DMA units after decoding; not binary validation")
    parser.add_argument("--relative-etm-base", action="store_true",
                        help="Use zero ETM base placeholders, as in compiler-generated relocatable HardOps")
    parser.add_argument("--emit-only", action="store_true", help="Preserve generated code without executing a simulator")
    parser.add_argument("--copy-control", action="store_true",
                        help="Generate a contiguous AssignTask as a control for the same XIR wrapper")
    parser.add_argument("--fixture", type=Path, help="Owned host payload and actual index fixture")
    parser.add_argument("--etm-unit", choices=("zero", "channels", "bytes"), default="zero",
                        help="Differential check of conflicting vendor unit comments")
    args = parser.parse_args()
    fixture = json.loads(args.fixture.read_text()) if args.fixture else None
    directory = args.directory.resolve()
    directory.mkdir(parents=True, exist_ok=False)
    os.chdir(directory)
    if ct.sizeof(ZgTile) != 80 or ct.sizeof(Vector) != 24 or ct.sizeof(ShortString) != 32:
        raise RuntimeError("Not the inspected Windows x64 release ABI")
    dll_handle = os.add_dll_directory(str(ICRAFT_BIN))
    libraries = {}
    evidence = []

    def bind(dll, prefix, parameters, result=None):
        if dll not in libraries:
            path = ICRAFT_BIN / dll
            libraries[dll] = ct.CDLL(str(path)), exports(path)
            evidence.append(dict(dll=dll, sha256=hashlib.sha256(path.read_bytes()).hexdigest()))
        library, names = libraries[dll]
        matched = [name for name in names if name.startswith(prefix)]
        if len(matched) != 1:
            raise RuntimeError("Ambiguous ABI symbol: " + prefix)
        function = getattr(library, matched[0])
        function.argtypes = parameters
        function.restype = result
        return function

    ptr, integer, uint, ulong = ct.c_void_p, ct.c_int, ct.c_uint, ct.c_uint64
    construct_tile = bind("byzg-tile.dll", "??0ZgTile@zgt@@QEAA@XZ", [ptr], ptr)
    construct_etm = bind("byzg-code.dll", "??0EtmInfo@zgc@@QEAA@XZ", [ptr], ptr)
    set_etm = bind("byzg-code.dll", "?setEtmInfo@EtmInfo", [ptr, ulong, uint, uint, uint, uint, integer, ptr, uint])
    get_sim = bind("byzg-code.dll", "?getSim@EtmInfo", [ptr], ptr)
    show_etm = bind("byzg-code.dll", "?printShow@EtmInfo", [ptr])
    parse_etm = bind("byzg-code.dll", "?parseEtmInfo@ZgCodeGen", [ptr, ct.c_size_t, ptr])
    add_task = bind("byzg-task.dll", "?addTask@D2aTask", [ptr, ptr, ptr, integer, integer, integer], ptr)
    get_tasks = bind("byzg-task.dll", "?getTasks@ZgTask", [ptr], ptr)
    configure = bind("zg_codegen.dll", "?setFirebyCodeGenOption@", [integer] * 7)
    initialize_codes = bind("byzg-code.dll", "?initial@ZgCodeGen", [])
    make_control = bind("zg_codegen.dll", "?addInstCtrl@Zg_CodeGen", [ptr] + [uint] * 8, ptr)
    to_codes = bind("zg_codegen.dll", "?tasks2Codes@Zg_CodeGen",
                    [ptr, integer, ptr, ptr, integer, ptr, ptr, ptr, ptr, ptr, ct.c_bool, integer], ptr)
    simulate = bind("zg_codegen.dll", "?instsSim@Zg_CodeGen", [ptr, integer, ptr, ptr, ptr, integer, integer], ptr)
    decode = bind("zg_codegen.dll", "?logFromCodes@Zg_CodeGen", [integer, ptr, ptr, ptr])
    to_insts = bind("zg_codegen.dll", "?tasks2Insts@Zg_CodeGen",
                   [ptr, integer, ptr, ptr, integer, ptr, ptr, ptr, ptr, ct.c_bool], ptr)
    simulate_objects = bind("byzg-inst.dll", "?instsSim@ZgInst@zgi@@SAX", [ptr, ptr, integer])

    n, k, c = args.n, args.k, args.channels
    if not 1 <= k <= n <= 2048 or c not in (1, 2, 4, 8, 16):
        raise ValueError("Probe requires 1 <= K <= N <= 2048, Cu in {1,2,4,8,16}")
    rng = random.Random(330)
    selected = rng.sample(range(n), k)
    if args.copy_control:
        selected = list(range(k))
    edges = [0.0, -0.0, 2**-24, -(2**-24), 65504.0, -65504.0, 1.0, -1.0]
    # Every row must differ: a repeating C=16 pattern would hide a wrong index.
    words = [float(rng.randrange(-32768, 32768)) / 8 for _ in range(n * c)]
    for i in range(0, len(words), 29):
        words[i] = edges[(i // 29) % len(edges)]
    if fixture is not None:
        selected, words = fixture["indices"], fixture["payload"]
        if len(selected) != k or len(words) != n * c or any(
                not isinstance(index, int) or not 0 <= index < n for index in selected):
            raise ValueError("Invalid fixture shape or index")
    coordinates = (ct.c_float * (k * 2))(*[value for i in selected for value in (0, i)])
    payload = (ct.c_float * (n * c))(*words)
    output = (ct.c_float * (k * c))(*([-999.0] * (k * c)))
    buffers = [coordinates, payload, output]
    counts, units = [k, n, k], [2, c, c]
    infos = (EtmInfo * 3)()
    tiles = []
    for i, (buffer, count, unit) in enumerate(zip(buffers, counts, units)):
        construct_etm(ct.byref(infos[i]))
        # D2a's coordinate RETM is fixed at four bytes per pair, so the
        # coordinate pair uses FP16 while TF32 payload uses four bytes/lane.
        dtype_id = 4 if i == 0 else 5
        physical_bytes = ct.sizeof(buffer) // 2 if i == 0 else ct.sizeof(buffer)
        # Zero is the inspected constructor/default path. DWDC packing remains
        # undocumented; do not infer its encoding from unrelated dtype fields.
        etm_unit = {"zero": 0, "channels": unit, "bytes": unit * (2 if i == 0 else 4)}[args.etm_unit]
        base = 0 if args.relative_etm_base else 0x100000 * (i + 1)
        set_etm(ct.byref(infos[i]), base, physical_bytes, etm_unit, 0, dtype_id,
                2 if i == 2 else 0, ct.addressof(buffer), i)
        tile = ZgTile()
        construct_tile(ct.byref(tile))
        if tile.kind != 11 or tile.unit != 16 or tile.dtype != 0 or tile.sub_count != 1:
            raise RuntimeError("Constructor layout mismatch")
        tile.kind, tile.unit, tile.dtype = 5, unit, dtype_id
        tile.width, tile.height = count, 1
        tile.width_stride, tile.height_stride = 1, count
        # ETM floating point IEM columns are numbered 1 and 2, not 0 and 1.
        # D2a uses the adjacent column for its coordinate stream/output.
        tile.column = 1
        tile.sub_id = i
        tiles.append(tile)
    etm_vector = Vector.view(infos)
    configure(1, 1, 4, 4, 2, 15, 0)
    initialize_codes()
    print("Creating D2a task with ETM coordinates/payload/output", flush=True)
    # Despite the header's generic src/idx names, native addTask maps its first
    # argument to d2a_src_ (coordinates), its second to AssignTask::src_ (data).
    if args.copy_control:
        add_copy = bind("byzg-task.dll", "?addTask@AssignTask", [ptr, ptr, integer, integer, integer, integer], ptr)
        copy_source = ZgTile.from_buffer_copy(tiles[1])
        copy_source.width = k
        add_copy(ct.byref(copy_source), ct.byref(tiles[2]), 0, 1, 0, 0)
    else:
        add_task(*[ct.byref(tile) for tile in tiles], 0, 1, n)
    tasks = Vector()
    get_tasks(ct.byref(tasks))
    if tasks.count(8) != 1:
        raise RuntimeError("Unexpected task count")
    codes, read_controls, write_controls = Vector(), Vector(), Vector()
    # By-value MSVC vectors transfer their temporary storage to the callee's
    # destructor. Allocate this 8-byte temporary with the same UCRT allocator;
    # a ctypes/Python-owned array must never be passed as an owning vector.
    control = ct.c_uint64()
    make_control(ct.byref(control), 0, 0, 2, 2, 0, 0, 0, 1)
    crt = ct.CDLL("ucrtbase.dll")
    crt.malloc.argtypes, crt.malloc.restype = [ct.c_size_t], ptr
    control_storage = crt.malloc(8)
    if not control_storage:
        raise MemoryError("Native control allocation failed")
    ct.memmove(control_storage, ct.byref(control), 8)
    write_controls = Vector(control_storage, control_storage + 8, control_storage + 8)
    name, log_root, mode = ShortString.make("D2aProbe"), ShortString.make("probe"), ShortString.make("w")
    if args.object_simulation:
        instructions = Vector()
        print("Generating instruction objects for differential diagnosis", flush=True)
        to_insts(ct.byref(instructions), 0, ct.byref(name), ct.byref(tasks), 1,
                 ct.byref(read_controls), ct.byref(write_controls), ct.byref(log_root), ct.byref(mode), True)
        print("Simulating {} instruction objects".format(instructions.count(8)), flush=True)
        simulate_objects(ct.byref(instructions), ct.byref(etm_vector), 1)
        actual = ct.string_at(get_sim(ct.byref(infos[2])), k*c*4)
        expected = struct.pack("<{}f".format(k*c), *[words[i*c+j] for i in selected for j in range(c)])
        (directory / "actual.f32").write_bytes(actual)
        (directory / "expected.f32").write_bytes(expected)
        save_json(directory / "result.json", dict(n=n, k=k, channels=c, bitwise_equal=actual == expected,
                  instruction_object_simulation=True, generated_binary_simulation=False, board_tested=False))
        if actual != expected:
            raise RuntimeError("Instruction object simulation differs")
        return
    print("Generating ZG330 binary instructions", flush=True)
    to_codes(ct.byref(codes), 0, ct.byref(name), ct.byref(tasks), 1,
             ct.byref(read_controls), ct.byref(write_controls), ct.byref(etm_vector),
             ct.byref(log_root), ct.byref(mode), True, 1)
    count = codes.count(8)
    if not count:
        raise RuntimeError("No instructions generated")
    (directory / "instructions.bin").write_bytes(ct.string_at(codes.begin, count * 8))
    decoded_name, decoded_root = ShortString.make("D2aDecoded"), ShortString.make("decoded")
    decode(0, ct.byref(decoded_name), ct.byref(codes), ct.byref(decoded_root))
    parsed_etm = Vector()
    parse_etm(codes.begin, count, ct.byref(parsed_etm))
    for i in range(parsed_etm.count(ct.sizeof(EtmInfo))):
        show_etm(parsed_etm.begin + i * ct.sizeof(EtmInfo))
    if args.emit_only:
        save_json(directory / "result.json", dict(n=n, k=k, channels=c, instruction_bytes=count*8,
                  relative_etm_base=args.relative_etm_base, generated_binary_simulation=False,
                  simulation_status="not_run", copy_control=args.copy_control, board_tested=False, dlls=evidence))
        return
    if args.restore_logical_dma:
        # fromIem uses byte-normalized DMA widths and ArSize=1. The object
        # simulator consumed logical widths before serialization. Restore only
        # that representation to test this hypothesis; never alter the binary.
        from_codes = bind("byzg-inst.dll", "?instsFromCode@ZgInst@zgi@@SA?AV?$vector@PEAVZgInst@zgi@@V?$allocator@PEAVZgInst@zgi@@@std@@@std@@PEB_K_K@Z",
                          [ptr, ptr, ct.c_size_t], ptr)
        type_name = bind("byzg-inst.dll", "?typeName@ZgInst", [ptr, ptr], ptr)
        construct_dma = bind("byzg-inst.dll", "??0DmaParam@zgi@@QEAA@AEAVZgTile", [ptr, ptr], ptr)
        set_ar_size = bind("byzg-inst.dll", "?setArSize@VpeRetmInst", [ptr, uint])
        set_aw_size = bind("byzg-inst.dll", "?setAwSize@VpeWetmInst", [ptr, uint])
        get_aw_mode = bind("byzg-inst.dll", "?getAwmode@VpeWetmInst", [ptr], uint)
        set_const_a = bind("byzg-inst.dll", "?setD2aConstA@VpeRetmInst", [ptr, uint])
        set_const_b = bind("byzg-inst.dll", "?setD2aConstB@VpeRetmInst", [ptr, uint])
        decoded_objects = Vector()
        from_codes(ct.byref(decoded_objects), codes.begin, count)
        restored = []
        read_number = 0
        for offset in range(decoded_objects.count(8)):
            instruction_ptr = ct.c_void_p.from_address(decoded_objects.begin + offset * 8).value
            label = ShortString()
            type_name(instruction_ptr, ct.byref(label))
            if label.length > 128:
                raise RuntimeError("Unexpected native instruction label")
            label_address = ct.addressof(label) if label.capacity < 16 else ct.c_void_p.from_address(ct.addressof(label)).value
            label_text = ct.string_at(label_address, label.length).decode("ascii")
            print("Decoded instruction", offset, label_text, flush=True)
            if label_text == "VpeRetm":
                if read_number > 1:
                    raise RuntimeError("Unexpected extra RETM")
                tile = ZgTile.from_buffer_copy(tiles[read_number])
                tile.width = k
                # Embedded DmaParam offset 0x20 is verified in fromIem and
                # simRun; its constructor provides all field assignments.
                construct_dma(instruction_ptr + 0x20, ct.byref(tile))
                set_ar_size(instruction_ptr, 4 if read_number == 0 else c * 4)
                if read_number == 1:
                    set_const_a(instruction_ptr, 1)
                    set_const_b(instruction_ptr, 1)
                restored.append(dict(instruction=offset, kind=label_text, logical_width=k))
                read_number += 1
            elif label_text == "VpeWetm" and get_aw_mode(instruction_ptr) == 0:
                construct_dma(instruction_ptr + 0x20, ct.byref(tiles[2]))
                set_aw_size(instruction_ptr, c * 4)
                restored.append(dict(instruction=offset, kind=label_text, logical_width=k))
        save_json(directory / "restored-representation.json", restored)
        if read_number != 2 or len(restored) != 3:
            raise RuntimeError("Unexpected decoded D2a instruction shape")
        simulate_objects(ct.byref(decoded_objects), ct.byref(etm_vector), 1)
        actual = ct.string_at(get_sim(ct.byref(infos[2])), k*c*4)
        expected = struct.pack("<{}f".format(k*c), *[words[i*c+j] for i in selected for j in range(c)])
        (directory / "actual.f32").write_bytes(actual)
        (directory / "expected.f32").write_bytes(expected)
        save_json(directory / "result.json", dict(n=n, k=k, channels=c,
                  bitwise_equal=actual == expected, host_dma_representation_restored=True,
                  generated_binary_simulation=False, board_tested=False, dlls=evidence))
        if actual != expected:
            raise RuntimeError("Restored logical DMA simulation differs")
        return
    print("Simulating {} instruction bytes".format(count * 8), flush=True)
    results = Vector()
    name = ShortString.make("D2aProbe")
    simulate(ct.byref(results), 0, ct.byref(name), ct.byref(codes), ct.byref(etm_vector), 1, 0)
    if results.count(ct.sizeof(EtmInfo)) != 3:
        raise RuntimeError("Unexpected simulated ETM count")
    result_info = results.begin + 2 * ct.sizeof(EtmInfo)
    actual = ct.string_at(get_sim(result_info), k * c * 4)
    expected = struct.pack("<{}f".format(k * c), *[words[i*c+j] for i in selected for j in range(c)])
    (directory / "actual.f32").write_bytes(actual)
    (directory / "expected.f32").write_bytes(expected)
    record = dict(n=n, k=k, channels=c, instruction_bytes=count*8,
                  bitwise_equal=actual == expected, generated_instruction_simulation=True,
                  board_tested=False, dlls=evidence)
    save_json(directory / "result.json", record)
    print(record, flush=True)
    if actual != expected:
        raise RuntimeError("D2a instruction simulation differs; complete output retained")
    dll_handle.close()


if __name__ == "__main__":
    main()
