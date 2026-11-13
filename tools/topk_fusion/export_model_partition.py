"""Export dependency-closed old-model stages for Host instruction simulation."""

import argparse
from pathlib import Path

from model_partition import MODEL, load_partition, validate_runtime_parameters
from runtime import (ICRAFT_PYTHON, icraft_environment, load_xir,
                     run_native, save_json)


def export(directory, native_layout=False):
    xir, dll_handles = load_xir()
    from icraft import xrt
    partition = load_partition(native_layout=native_layout)
    network = xir.Network.CreateFromJsonFile(str(MODEL))
    network.loadParamsFromFile(str(MODEL.with_suffix(".raw")))
    parameters = validate_runtime_parameters(network, xrt)
    entries = list(partition["stages"])
    entries.append(dict(name="index_expansion_a", op_ids=partition["cuts"][0]["index_expansion_ops"]))
    # The set above is serialized in original graph order, not numeric ID order.
    selected = set(entries[-1]["op_ids"])
    entries[-1]["op_ids"] = [op.op_id for op in network.ops if op.op_id in selected]
    entries.append(dict(name="reference_all_hardops", op_ids=[op.op_id for op in network.ops
                        if str(op.typeKey()).split("::")[-1] == "HardOpNode"]))
    for entry in entries:
        stage = network.view(entry["op_ids"]).toNetwork()
        stage.dumpJsonAndParams(str(directory / (entry["name"] + ".json")),
                                str(directory / (entry["name"] + ".raw")))
        entry["inputs"] = [dict(value_id=v.v_id, bytes=v.storageBytes()) for v in stage.inputs()]
        entry["outputs"] = [dict(value_id=v.v_id, bytes=v.storageBytes()) for v in stage.outputs()]
        print(entry["name"], "inputs", entry["inputs"], "outputs", entry["outputs"], flush=True)
    save_json(directory / "manifest.json", dict(board_tested=False, forward_tested=False,
              stages=entries, cuts=partition["cuts"], checked_topk_k=parameters,
              native_layout=native_layout, kept_hardops=partition["kept_hardops"]))
    assert dll_handles


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("directory", type=Path)
    parser.add_argument("--child", action="store_true", help=argparse.SUPPRESS)
    parser.add_argument("--native-layout", action="store_true")
    args = parser.parse_args()
    directory = args.directory.resolve()
    if args.child:
        export(directory, args.native_layout)
    else:
        directory.mkdir(parents=True, exist_ok=False)
        run_native("export", [ICRAFT_PYTHON, "-B", Path(__file__).resolve(), directory, "--child"] +
                   (["--native-layout"] if args.native_layout else []),
                   directory, icraft_environment())


if __name__ == "__main__":
    main()
