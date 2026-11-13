"""Validate public ZG330 memory binding on a literal offline mock device.

This probe never calls forward, icoreCalc, register I/O or a hardware protocol.
Mock allocation proves SDK placement/ownership only, not bus visibility or NPU
completion.  Backend resources are destroyed before user allocations are freed.
"""

import argparse
import hashlib
from pathlib import Path
import shutil

from model_partition import MODEL, load_partition, validate_runtime_parameters
from runtime import (ROOT, ICRAFT_PYTHON, icraft_environment, load_xir,
                     run_native, save_json)


def inspect_binding(backend, value_id, requested):
    value = backend.value_info[value_id]
    memory = backend.forward_info.memchunk_map[value_id]
    address = requested.begin.addr()
    staged = {str(k): dict(address=v.begin.addr(), bytes=v.byte_size)
              for k, v in memory.staged_chunk.items()}
    return dict(value_id=value_id, requested_address=address,
                requested_bytes=requested.byte_size, value_bytes=value.byte_size,
                value_address=value.phy_addr, real=value.real,
                is_host=value.is_host, is_ocm=value.is_ocm,
                segment=str(value.segment), user_owned=memory.user_used,
                actual_address=memory.memChunk.begin.addr(),
                actual_bytes=memory.memChunk.byte_size, staged=staged,
                direct=(memory.user_used and not staged and not value.is_host
                        and not value.is_ocm and value.phy_addr == address
                        and memory.memChunk.begin.addr() == address))


def probe(directory, native_layout=False):
    xir, dll_handles = load_xir()
    from icraft import xrt, zg330backend

    partition = load_partition(native_layout=native_layout)
    save_json(directory / "partition.json", partition)
    network = xir.Network.CreateFromJsonFile(str(MODEL))
    network.loadParamsFromFile(str(MODEL.with_suffix(".raw")))
    parameters = validate_runtime_parameters(network, xrt)
    views = [network.view(stage["op_ids"]) for stage in partition["stages"]]
    boundaries = {}
    report = dict(board_tested=False, forward_calls=0, hardware_device_opens=0, native_layout=native_layout,
                  model_sha256=hashlib.sha256(MODEL.read_bytes()).hexdigest(),
                  raw_sha256=hashlib.sha256(MODEL.with_suffix(".raw").read_bytes()).hexdigest(),
                  mock_device_opens=0, stages=[], cleanup_complete=False, checked_topk_k=parameters)
    for stage, view in zip(partition["stages"], views):
        ports = dict(inputs=[v.v_id for v in view.inputs()],
                     outputs=[v.v_id for v in view.outputs()])
        report["stages"].append(dict(name=stage["name"], hardops=len(stage["op_ids"]),
                                     **ports, bindings=[]))
        for value in view.inputs() + view.outputs():
            boundaries[value.v_id] = value
    allocation_bytes = sum((v.storageBytes() + 63) // 64 * 64 for v in boundaries.values())
    if allocation_bytes > 64 * 1024 * 1024:
        raise ValueError("Mock boundary allocation exceeds the experiment budget")
    report["boundary_bytes"] = allocation_bytes
    save_json(directory / "before-apply.json", report)

    # No caller-supplied protocol can reach Device.Open through this program.
    device = xrt.Device.Open("mock://zg330")
    report["mock_device_opens"] = 1
    backends = []
    sessions = []
    port_tensors = []
    chunks = {}
    private_chunks = []
    try:
        if str(device.typeKey()).split("::")[-1] != "MockZG330DeviceNode":
            raise RuntimeError("Expected the SDK's offline mock device")
        region = device.defaultMemRegion()
        if str(region.typeKey()).split("::")[-1] != "MockZG330PLDDRMemRegionNode":
            raise RuntimeError("Expected offline mock PL DDR")
        report["device_type"] = str(device.typeKey())
        report["region_type"] = str(region.typeKey())
        report["allocation_count_before"] = len(region.memManager().getAllMemChunk())
        for value_id, value in sorted(boundaries.items()):
            size = (value.storageBytes() + 63) // 64 * 64
            chunk = region.malloc(size, False, 4096)
            chunks[value_id] = chunk
            if chunk.begin.addr() % 4096 or chunk.byte_size < size:
                raise RuntimeError("SDK allocation does not satisfy the requested extent")
        report["fusion_memory"] = []
        for cut in partition["cuts"]:
            def private_output(size):
                chunk = region.malloc((size + 63) // 64 * 64, False, 4096)
                private_chunks.append(chunk)
                return chunk

            selected_scores = (chunks[cut["outputs"][1]] if cut["selected_scores_used"]
                               else private_output(cut["k"] * 4))
            selected_indices = private_output(cut["k"] * 8)
            memory = [chunks[cut["score"]], chunks[cut["features"]], selected_scores,
                      selected_indices, chunks[cut["outputs"][0]]]
            specification = [dict(base=chunk.begin.addr(), bytes=chunk.byte_size) for chunk in memory]
            if any(row["base"] % 64 or row["bytes"] % 64 or row["base"] + row["bytes"] > 2**32
                   for row in specification):
                raise ValueError("Mock allocation cannot be described by the 32-bit PL interface")
            report["fusion_memory"].append(dict(name=cut["name"], entries=specification))
            (directory / ("cut_" + cut["name"] + ".memory")).write_text(
                "".join("{} {}\n".format(row["base"], row["bytes"]) for row in specification), encoding="ascii")
        report["private_pl_bytes"] = sum(chunk.byte_size for chunk in private_chunks)
        for view, stage in zip(views, report["stages"]):
            print("Creating", stage["name"], stage["hardops"], "HardOps", flush=True)
            backend = xrt.Backend.Create(zg330backend.ZG330Backend, view, device)
            backends.append(backend)
            zg = zg330backend.ZG330Backend(backend)
            for value_id in set(stage["inputs"] + stage["outputs"]):
                zg.userConnectNetwork(chunks[value_id], value_id)
            session = xrt.Session.CreateWithBackends(view, [backend])
            sessions.append(session)
            if set(session.backendBindings()) != {op.op_id for op in view.ops}:
                raise RuntimeError("Session does not bind every retained HardOp")
            stage["session_bindings_before_apply"] = len(session.backendBindings())
            session.apply()
            stage["session_bindings_after_apply"] = len(session.backendBindings())
            stage["merged_hardops"] = {str(op_id): list(info.merge_from)
                                      for op_id, info in zg.forward_info.hardop_map.items()}
            for value_id in stage["inputs"] + stage["outputs"]:
                tensor = xrt.Tensor(network.getValueById(value_id).tensorType(), chunks[value_id], 0)
                if tensor.data().addr() != chunks[value_id].begin.addr() or not tensor.hasData():
                    raise RuntimeError("Public Tensor construction lost the bound PL allocation")
                port_tensors.append(tensor)
            for value_id in sorted(set(stage["inputs"] + stage["outputs"])):
                stage["bindings"].append(inspect_binding(zg, value_id, chunks[value_id]))
            stage["direct"] = all(row["direct"] for row in stage["bindings"])
            print(stage["name"], "direct", stage["direct"], "ports", len(stage["bindings"]), flush=True)
            save_json(directory / "placement.json", report)
        report["peak_managed_bytes"] = sum(chunk.byte_size for chunk in region.memManager().getAllMemChunk())
    finally:
        # Only a mock device is reachable and no work has ever been submitted.
        # This cleanup order must not be generalized to an in-flight real device.
        session = None
        tensor = None
        port_tensors.clear()
        sessions.clear()
        for backend in reversed(backends):
            backend.deinit()
        for chunk in reversed(private_chunks):
            chunk.free()
        for chunk in reversed(list(chunks.values())):
            chunk.free()
        report["allocation_count_after"] = len(device.defaultMemRegion().memManager().getAllMemChunk())
        xrt.Device.Close(device)
        report["cleanup_complete"] = True
        save_json(directory / "result.json", report)
    report["direct_all_ports"] = all(stage["direct"] for stage in report["stages"])
    save_json(directory / "result.json", report)
    if not report["direct_all_ports"]:
        raise RuntimeError("One or more SDK ports did not bind directly")
    if report["allocation_count_before"] != report["allocation_count_after"]:
        raise RuntimeError("Mock allocations remain after explicit cleanup")
    print("MOCK_BINDING_PROBE_FINISHED direct_all_ports={}".format(report["direct_all_ports"]), flush=True)
    # Keep DLL directory handles alive through destruction of all SDK objects.
    assert dll_handles


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("directory", type=Path)
    parser.add_argument("--child", action="store_true", help=argparse.SUPPRESS)
    parser.add_argument("--native-layout", action="store_true")
    args = parser.parse_args()
    directory = args.directory.resolve()
    if args.child:
        probe(directory, args.native_layout)
        return
    directory.mkdir(parents=True, exist_ok=False)
    for name in ("probe_sdk_binding.py", "model_partition.py"):
        shutil.copyfile(ROOT / "tools/topk_fusion" / name, directory / name)
    run_native("probe", [ICRAFT_PYTHON, "-B", Path(__file__).resolve(), directory, "--child"] +
               (["--native-layout"] if args.native_layout else []),
               directory, icraft_environment())


if __name__ == "__main__":
    main()
