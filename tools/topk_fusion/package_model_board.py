"""Package the isolated five-stage experiment from verified local inputs.

No device access. The package cannot start until a fresh boot is checked by the
board controller. Neither the delivered graph nor its parameter file is edited.
"""

import argparse
import hashlib
import json
from pathlib import Path
import shutil
import tarfile

from model_partition import MODEL, NATIVE_IDENTITIES, load_partition
from runtime import ROOT, WORK, save_json


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def prepare(directory):
    directory.mkdir(parents=True, exist_ok=False)
    package = directory / "package"
    package.mkdir()
    candidate = WORK / "native/dynamic-n180-k100-r3"
    placement = json.loads((WORK / "native/mock-npu-model-binding-r1/result.json").read_text())
    reference = WORK / "native/model-flow-r5"
    if not placement["passed"] or placement["direct_port_bindings"] != 27:
        raise ValueError("Mock placement qualification is missing")
    partition = load_partition()
    model_ops = {item["name"]: item["op_ids"] for item in partition["stages"]}
    candidate_json = candidate / "topk_native_ZG.json"
    candidate_ops = [op["op_id"] for op in json.loads(candidate_json.read_text())["ops"]
                     if op["_type_key"].endswith("::HardOp")]
    stages = []
    for stage in placement["stages"]:
        name = stage["name"]
        stages.append(dict(name=name, graph="model" if name in model_ops else name,
                           op_ids=model_ops[name] if name in model_ops else candidate_ops,
                           mapping={str(row["value_id"]): row["shared_key"] for row in stage["bindings"]}))
    plan = dict(allocations=placement["allocation_sizes"], stages=stages, cuts=partition["cuts"])
    save_json(package / "plan.json", plan)
    sources = {
        "model.json": MODEL, "model.raw": MODEL.with_suffix(".raw"),
        "candidate.json": candidate_json, "candidate.raw": candidate_json.with_suffix(".raw"),
        "input.bin": reference / "input_0.ftmp",
        "expected_3483.bin": reference / "npu_2/native/piw24_shared/ftmpHQB/3483.ftmp",
        "expected_3487.bin": reference / "npu_2/native/piw24_shared/ftmpHQB/3487.ftmp",
        "board_supervisor.py": ROOT / "tools/topk_fusion/board_supervisor.py",
        "board_model_control.py": ROOT / "tools/topk_fusion/board_model_control.py",
        "board_probe.py": ROOT / "tools/pose-v1/board_probe.py",
    }
    for name in ("CMakeLists.txt", "board_validation.cpp", "model_board_validation.cpp",
                 "shared_npu_session.hpp", "shared_npu_session.cpp", "parameter_image.hpp",
                 "test_parameter_image.cpp", "parameter_layout_probe.cpp", "shared_binding_validation.cpp"):
        sources[name] = ROOT / "FPGA/topk_gather/host/board" / name
    expected = {
        "model.json": NATIVE_IDENTITIES[".json"], "model.raw": NATIVE_IDENTITIES[".raw"],
        "candidate.json": placement["candidate_sha256"], "candidate.raw": placement["candidate_raw_sha256"],
        "expected_3483.bin": "dd1996a86ca680231f32a07ac14f99741b5704debf5184db246d9e801c781e07",
        "expected_3487.bin": "b6ab260250cbfbfb80a46b42ba9ff5e8443bfd3796759f4e59db601cbc4951c1",
    }
    for name, source in sources.items():
        if name in expected and digest(source) != expected[name]:
            raise ValueError("Qualified input identity differs: " + name)
        shutil.copyfile(source, package / name)
    manifest = dict(boot_id=None, scope="isolated old100 segmented model comparison",
                    benchmark_pairs=10, maximum_forward_calls=88, maximum_sdk_opens=1,
                    maximum_frames=22, boot_writes=0, automatic_retry=False,
                    shared_bytes=sum(plan["allocations"].values()),
                    files={path.name: digest(path) for path in sorted(package.iterdir())})
    save_json(package / "manifest.template.json", manifest)
    archive = directory / "package.tar.gz"
    with tarfile.open(archive, "w:gz") as output:
        for path in sorted(package.iterdir()):
            output.add(path, arcname=path.name, recursive=False)
    summary = dict(archive_sha256=digest(archive), archive_bytes=archive.stat().st_size,
                   files=len(manifest["files"]), shared_bytes=manifest["shared_bytes"], board_started=False)
    save_json(directory / "package-summary.json", summary)
    print(json.dumps(summary))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("directory", type=Path)
    prepare(parser.parse_args().directory.resolve())
