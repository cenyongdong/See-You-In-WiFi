"""Describe isolated TopK/Gather cuts without rewriting the delivered network.

The default integration keeps dense FP32 boundaries. The explicit native mode
also removes independently tested FP16/C16 conversion paths and requires the
kernel's flush-half-zero policy. Original instructions stay read-only.
"""

from dataclasses import dataclass
from pathlib import Path
import hashlib
import json
import struct

from runtime import ROOT


MODEL = ROOT / "model/piw24_shared-20261015-r1/piw24_shared_ZG.json"


@dataclass(frozen=True)
class FusionCut:
    name: str
    topk: int
    gather: int
    scores: int
    features: int
    selected_scores: int
    indices: int
    expanded_indices: int
    output: int
    n: int
    k: int
    channels: int


CUTS = (FusionCut("A", 188, 192, 3443, 3451, 485, 486, 3455, 495, 180, 100, 42),
        FusionCut("B", 437, 442, 3467, 3471, 1136, 1137, 1137, 1148, 100, 100, 42))

# These native boundaries are specific to the independently simulated old
# instruction graph. The reusable kernel does not depend on these value IDs.
NATIVE_BOUNDARIES = {"A": (448, 478, 7470), "B": (1133, 1145, 8747)}
NATIVE_IDENTITIES = {
    ".json": "a1395205eed11112ac0e23dacf8eec4c09d7dfec120e99b060a9361cb9c812cc",
    ".raw": "d235ec300f2872f1b78ce6101bc98fd2cc13c47a53fe99f76e045587148279dd",
}


def validate_native_type(value, shape, layout):
    dtype = value["dtype"]
    element = dtype["element_dtype"]
    if (dtype["shape"] != shape or dtype["layout"] != "@layout(" + layout + ")" or
            not isinstance(element, dict) or element.get("storage_dtype") != "@fp(16)" or
            element.get("expressed_dtype") != "@fp(32)" or
            element.get("scale") != "@scales([axis=-1])" or element.get("zero_points") != []):
        raise ValueError("Native FP16 shape, layout or quantization changed")


def unary_chain(producer, value_id, stop):
    """Collect an existing unary HardOp path; do not infer its numeric meaning."""
    found, visited = set(), set()
    while value_id != stop:
        if value_id in visited:
            raise ValueError("Cycle in a proposed private HardOp path")
        visited.add(value_id)
        op = producer[value_id]
        if len(op["inputs"]) != 1 or not op["_type_key"].endswith("::HardOp"):
            raise ValueError("Boundary path is no longer a unary HardOp chain")
        found.add(op["op_id"])
        value_id = op["inputs"][0]["v_id"]
    return found


def build_partition(graph, native_layout=False):
    """Return a dependency-checked three-stage schedule and its fusion edges.

    Identity is intentionally explicit for this old-model adapter.  Reusable
    shape handling belongs to the PL planner, not to guessed graph semantics.
    """
    ops = {op["op_id"]: op for op in graph["ops"]}
    producer = {v["v_id"]: op for op in graph["ops"] for v in op["outputs"]}
    values = {v["v_id"]: v for op in graph["ops"] for v in op["outputs"]}
    users = {}
    for op in graph["ops"]:
        for value in op["inputs"]:
            users.setdefault(value["v_id"], set()).add(op["op_id"])
    input_op, = [op for op in graph["ops"] if op["_type_key"].endswith("::Input")]
    output_op, = [op for op in graph["ops"] if op["_type_key"].endswith("::Output")]
    available = {v["v_id"] for v in input_op["outputs"]}
    removed = set()
    cuts = []
    stages = []

    for cut in CUTS:
        topk, gather = ops[cut.topk], ops[cut.gather]
        if not topk["_type_key"].endswith("::TopK"):
            raise ValueError("Expected TopK at the isolated model cut")
        expected_gather = "::GatherElements" if cut.name == "A" else "::Gather"
        if not gather["_type_key"].endswith(expected_gather):
            raise ValueError("Gather kind changed at the isolated model cut")
        if (not topk["largest"] or not topk["sorted"] or
                topk["axis"] not in ((1, -1) if cut.name == "A" else (0, -1)) or
                gather["axis"] not in ((1, -2) if cut.name == "A" else (0, -2))):
            raise ValueError("Sort direction or candidate axis changed")
        if [v["v_id"] for v in topk["outputs"]] != [cut.selected_scores, cut.indices]:
            raise ValueError("TopK outputs changed")
        if topk["inputs"][0]["v_id"] != cut.scores:
            raise ValueError("TopK score input changed")
        if [v["v_id"] for v in gather["inputs"]] != [cut.features, cut.expanded_indices]:
            raise ValueError("Gather inputs changed")
        if [v["v_id"] for v in gather["outputs"]] != [cut.output]:
            raise ValueError("Gather output changed")
        path = unary_chain(producer, cut.expanded_indices, cut.indices)
        local_removed = path | {cut.topk, cut.gather}
        # Every omitted index and intermediate must be private to this fusion.
        private_values = {cut.indices}
        private_values.update(v["v_id"] for op_id in path for v in ops[op_id]["outputs"])
        for value_id in private_values:
            if users.get(value_id, set()) - local_removed:
                raise ValueError("An index intermediate escapes the proposed fusion")
        expected_shapes = {cut.scores: ([1, cut.n] if cut.name == "A" else [cut.n]),
                           cut.selected_scores: ([1, cut.k] if cut.name == "A" else [cut.k]),
                           cut.indices: ([1, cut.k] if cut.name == "A" else [cut.k]),
                           cut.features: ([1, cut.n, cut.channels] if cut.name == "A"
                                          else [cut.n, cut.channels]),
                           cut.output: ([1, cut.k, cut.channels] if cut.name == "A"
                                        else [cut.k, cut.channels])}
        for value_id, shape in expected_shapes.items():
            dtype = values[value_id]["dtype"]
            layout = "@layout(" + "*" * (len(shape) - 1) + "C)"
            if (dtype["shape"] != shape or dtype["element_dtype"] != "@fp(32)" or
                    dtype["layout"] != layout):
                raise ValueError("Dense FP32 fusion boundary changed")
        score, features, output = cut.scores, cut.features, cut.output
        format_ops = set()
        if native_layout:
            score, features, output = NATIVE_BOUNDARIES[cut.name]
            prefix = [1] if cut.name == "A" else []
            validate_native_type(values[score], [1, 1, cut.n, 1] if cut.name == "A" else [cut.n, 1],
                                 "*C*c1" if cut.name == "A" else "Cc1")
            validate_native_type(values[features], prefix + [3, cut.n, 16],
                                 "*C*c16" if cut.name == "A" else "C*c16")
            validate_native_type(values[output], [1, 3, cut.k, 16] if cut.name == "A" else [cut.k, cut.channels],
                                 "*C*c16" if cut.name == "A" else "*C")
            format_ops = (unary_chain(producer, cut.scores, score) |
                          unary_chain(producer, cut.features, features) |
                          unary_chain(producer, output, cut.output))
            local_removed.update(format_ops)
            for op_id in local_removed:
                for value in ops[op_id]["outputs"]:
                    if value["v_id"] not in (output, cut.selected_scores) and users.get(value["v_id"], set()) - local_removed:
                        raise ValueError("A removed format intermediate escapes the native fusion")
        outputs = [output]
        if users.get(cut.selected_scores):
            outputs.append(cut.selected_scores)
        removed.update(local_removed)
        cuts.append(dict(name=cut.name, n=cut.n, k=cut.k, channels=cut.channels,
                         score=score, features=features, outputs=outputs,
                         score_element_bytes=2 if native_layout else 4,
                         feature_element_bytes=2 if native_layout else 4,
                         source_layout="blocked16" if native_layout else "dense",
                         destination_layout="blocked16" if native_layout and cut.name == "A" else "dense",
                         fp16_policy="flush-half-zero" if native_layout else "preserve",
                         index_expansion_ops=sorted(path), format_conversion_ops=sorted(format_ops),
                         removed_ops=sorted(local_removed), index_conversion_needed=False,
                         selected_scores_used=bool(users.get(cut.selected_scores))))

    def schedule_stage(required):
        selected = set()
        visiting = set()

        def require(value_id):
            if value_id in available:
                return
            op = producer[value_id]
            op_id = op["op_id"]
            if op_id in removed:
                raise ValueError("Unresolved dependency on a replaced host operator")
            if op_id in visiting:
                raise ValueError("Cycle in model dependency graph")
            if op_id in selected:
                return
            if not op["_type_key"].endswith("::HardOp"):
                raise ValueError("An unsupported host operation remains in a NPU stage")
            visiting.add(op_id)
            for value in op["inputs"]:
                require(value["v_id"])
            visiting.remove(op_id)
            selected.add(op_id)

        for value_id in required:
            require(value_id)
        # Retain the original execution order within each dependency-closed stage.
        ordered = [op["op_id"] for op in graph["ops"] if op["op_id"] in selected]
        for op_id in ordered:
            op = ops[op_id]
            if any(v["v_id"] not in available for v in op["inputs"]):
                raise ValueError("Original operator order is not topological")
            available.update(v["v_id"] for v in op["outputs"])
        stages.append(dict(name="npu_{}".format(len(stages)), op_ids=ordered))

    for cut in cuts:
        schedule_stage([cut["score"], cut["features"]])
        available.update(cut["outputs"])
    schedule_stage([v["v_id"] for v in output_op["inputs"]])
    kept = set().union(*(set(stage["op_ids"]) for stage in stages))
    dead = set(ops) - kept - removed - {input_op["op_id"], output_op["op_id"]}
    if dead:
        raise ValueError("Unexpected unused operations require review: {}".format(sorted(dead)))

    return dict(model_name=graph.get("name"), board_tested=False, forward_tested=False,
                native_layout=native_layout, layout="native" if native_layout else "dense",
                element="fp16" if native_layout else "fp32", stages=stages, cuts=cuts,
                kept_hardops=len(kept), removed_ops=sorted(removed),
                original_inputs=sorted(v["v_id"] for v in input_op["outputs"]),
                original_outputs=[v["v_id"] for v in output_op["inputs"]])


def load_partition(model=MODEL, native_layout=False):
    model = Path(model)
    if native_layout:
        for suffix, identity in NATIVE_IDENTITIES.items():
            if hashlib.sha256(model.with_suffix(suffix).read_bytes()).hexdigest() != identity:
                raise ValueError("Native fusion requires the original format-chain instruction identity")
    return build_partition(json.loads(model.read_text(encoding="utf-8")), native_layout)


def validate_runtime_parameters(network, xrt):
    """Check the loaded RAW's K constants through public Host Tensor reads."""
    result = {}
    for cut in CUTS:
        parameter = network.getOpById(cut.topk).inputs[1]
        if not parameter.isParams() or parameter.storageBytes() != 4:
            raise ValueError("TopK K must be a scalar FP32 parameter")
        raw = bytearray(4)
        xrt.Tensor(parameter).read(raw, 0, 4)
        actual, = struct.unpack("<f", raw)
        if actual != cut.k:
            raise ValueError("Loaded TopK K differs from the isolated cut")
        result[cut.name] = actual
    return result
