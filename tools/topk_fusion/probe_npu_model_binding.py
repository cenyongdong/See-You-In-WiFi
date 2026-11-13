"""Validate the five-stage NPU composition's shared allocations on a mock device.

The original B boundary has 100 rows; its allocation is extended to capacity 180
without changing its tensor type. Runtime masks exclude the extra rows. All
three model stages and both rank instances bind directly to these same chunks.
No hardware device, register access or forward call is reachable here.
"""

import argparse
import hashlib
import json
from pathlib import Path
import shutil

from model_partition import MODEL, load_partition, validate_runtime_parameters
from probe_sdk_binding import inspect_binding
from runtime import ROOT, ICRAFT_PYTHON, icraft_environment, load_xir, run_native, save_json


def probe(candidate, directory):
    xir, dll_handles = load_xir()
    from icraft import xrt, zg330backend

    partition = load_partition()
    graph = xir.Network.CreateFromJsonFile(str(MODEL))
    graph.loadParamsFromFile(str(MODEL.with_suffix(".raw")))
    validate_runtime_parameters(graph, xrt)
    candidate_path = candidate / "topk_native_ZG.json"
    candidate_raw = candidate / "topk_native_ZG.raw"
    candidate_graph = json.loads(candidate_path.read_text())
    candidate_ops = [op["op_id"] for op in candidate_graph["ops"] if op["_type_key"].endswith("::HardOp")]
    contract = json.loads((candidate / "contract.json").read_text())
    if tuple(contract[key] for key in ("algorithm", "n", "k", "channels")) != ("rank_dynamic", 180, 100, 42):
        raise ValueError("Expected the validated runtime-mask candidate")
    sessions, backends, tensors, chunks, stages, networks = [], [], [], {}, [], [graph]
    required = {}
    for stage in partition["stages"]:
        view = graph.view(stage["op_ids"])
        mapping = {v.v_id: "model:{}".format(v.v_id) for v in view.inputs() + view.outputs()}
        stages.append(dict(name=stage["name"], view=view, mapping=mapping, hardops=len(stage["op_ids"])))
    for cut in partition["cuts"]:
        network = xir.Network.CreateFromJsonFile(str(candidate_path))
        network.loadParamsFromFile(str(candidate_raw))
        networks.append(network)
        ops = candidate_ops
        if len(ops) != 54:
            raise ValueError("Candidate HardOp count differs")
        view = network.view(ops)
        name = "rank_" + cut["name"]
        mapping = {0: "model:{}".format(cut["score"]),
                   1: "model:{}".format(cut["features"]),
                   2: name + ":input_mask", 3: name + ":output_mask",
                   167: name + ":indices", 171: "model:{}".format(cut["outputs"][0]),
                   169: "model:{}".format(cut["outputs"][1]) if cut["selected_scores_used"] else name + ":scores"}
        stages.append(dict(name=name, view=view, mapping=mapping, hardops=54))
    by_name = {stage["name"]: stage for stage in stages}
    stages = [by_name[name] for name in ("npu_0", "rank_A", "npu_1", "rank_B", "npu_2")]
    for stage in stages:
        for value in stage["view"].inputs() + stage["view"].outputs():
            key = stage["mapping"][value.v_id]
            required[key] = max(required.get(key, 0), (value.storageBytes() + 63) // 64 * 64)
    report = dict(board_tested=False, forward_calls=0, hardware_device_opens=0,
                  shared_allocation_bytes=sum(required.values()), allocation_sizes=required,
                  model_sha256=hashlib.sha256(MODEL.read_bytes()).hexdigest(),
                  raw_sha256=hashlib.sha256(MODEL.with_suffix(".raw").read_bytes()).hexdigest(),
                  candidate_sha256=hashlib.sha256(candidate_path.read_bytes()).hexdigest(),
                  candidate_raw_sha256=hashlib.sha256(candidate_raw.read_bytes()).hexdigest(), stages=[])
    device = xrt.Device.Open("mock://zg330")
    try:
        if str(device.typeKey()).split("::")[-1] != "MockZG330DeviceNode":
            raise RuntimeError("Only the literal offline mock is permitted")
        region = device.defaultMemRegion()
        for key, size in sorted(required.items()):
            chunks[key] = region.malloc(size, False, 4096)
        for stage in stages:
            view = stage["view"]
            backend = xrt.Backend.Create(zg330backend.ZG330Backend, view, device)
            backends.append(backend)
            zg = zg330backend.ZG330Backend(backend)
            for value_id, key in stage["mapping"].items():
                zg.userConnectNetwork(chunks[key], value_id)
            session = xrt.Session.CreateWithBackends(view, [backend])
            sessions.append(session)
            session.apply()
            rows = []
            for value in view.inputs() + view.outputs():
                key = stage["mapping"][value.v_id]
                tensor = xrt.Tensor(value.tensorType(), chunks[key], 0)
                tensors.append(tensor)
                row = inspect_binding(zg, value.v_id, chunks[key])
                row.update(shared_key=key, tensor_bytes=value.storageBytes(),
                           tensor_address=tensor.data().addr())
                if not row["direct"] or row["tensor_address"] != row["requested_address"]:
                    raise RuntimeError("Shared port was staged or relocated")
                rows.append(row)
            groups = [dict(op_id=op_id, sync=list(info.sync_idx), members=list(info.merge_from) or [op_id])
                      for op_id, info in zg.forward_info.hardop_map.items() if op_id in session.backendBindings()]
            members = [item for group in groups for item in group["members"]]
            if len(members) != stage["hardops"] or len(set(members)) != len(members):
                raise RuntimeError("Applied HardOp coverage differs")
            report["stages"].append(dict(name=stage["name"], hardops=stage["hardops"], bindings=rows, groups=groups))
            save_json(directory / "placement.json", report)
        report["peak_managed_bytes"] = sum(chunk.byte_size for chunk in region.memManager().getAllMemChunk())
    finally:
        tensor = session = None
        tensors.clear()
        sessions.clear()
        for backend in reversed(backends):
            backend.deinit()
        for chunk in reversed(list(chunks.values())):
            chunk.free()
        report["allocation_count_after"] = len(device.defaultMemRegion().memManager().getAllMemChunk())
        xrt.Device.Close(device)
        save_json(directory / "result.json", report)
    if report["allocation_count_after"] != 0:
        raise RuntimeError("Mock resources remain after cleanup")
    report.update(passed=True, direct_port_bindings=sum(len(stage["bindings"]) for stage in report["stages"]))
    save_json(directory / "result.json", report)
    print("NPU_MODEL_BINDING_PASS stages=5 direct_ports={} bytes={}".format(
        report["direct_port_bindings"], report["shared_allocation_bytes"]), flush=True)
    assert dll_handles and networks


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("candidate", type=Path)
    parser.add_argument("directory", type=Path)
    parser.add_argument("--child", action="store_true", help=argparse.SUPPRESS)
    args = parser.parse_args()
    args.candidate, args.directory = args.candidate.resolve(), args.directory.resolve()
    if args.child:
        probe(args.candidate, args.directory)
    else:
        args.directory.mkdir(parents=True, exist_ok=False)
        shutil.copyfile(Path(__file__), args.directory / Path(__file__).name)
        run_native("probe", [ICRAFT_PYTHON, "-B", Path(__file__).resolve(), args.candidate, args.directory, "--child"],
                   args.directory, icraft_environment())
