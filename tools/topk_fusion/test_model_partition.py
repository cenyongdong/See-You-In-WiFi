"""Reject graph changes that would silently invalidate the isolated fusion."""

import copy
import json
import unittest

from model_partition import MODEL, build_partition


class PartitionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.original = json.loads(MODEL.read_text())

    def setUp(self):
        self.graph = copy.deepcopy(self.original)
        self.ops = {op["op_id"]: op for op in self.graph["ops"]}

    def test_real_dependency_partition(self):
        result = build_partition(self.graph)
        self.assertEqual([len(s["op_ids"]) for s in result["stages"]], [370, 417, 220])
        self.assertEqual(result["kept_hardops"], 1007)
        self.assertEqual([c["outputs"] for c in result["cuts"]], [[495], [1148, 1136]])

    def test_equivalent_negative_axes(self):
        for op_id, axis in ((188, -1), (192, -2), (437, 0), (442, -2)):
            self.ops[op_id]["axis"] = axis
        self.assertEqual(build_partition(self.graph)["kept_hardops"], 1007)

    def test_native_partition(self):
        result = build_partition(self.graph, native_layout=True)
        self.assertEqual([len(s["op_ids"]) for s in result["stages"]], [358, 401, 212])
        self.assertEqual(result["kept_hardops"], 971)
        self.assertEqual([c["outputs"] for c in result["cuts"]], [[7470], [8747, 1136]])
        self.assertEqual(sum(len(c["format_conversion_ops"]) for c in result["cuts"]), 36)
        self.assertEqual(sum(len(c["index_expansion_ops"]) for c in result["cuts"]), 14)
        self.assertTrue(all(c["fp16_policy"] == "flush-half-zero" for c in result["cuts"]))

    def test_reject_native_scale_or_shape_change(self):
        values = {v["v_id"]: v for op in self.graph["ops"] for v in op["outputs"]}
        for value_id in (448, 478, 7470, 1133, 1145, 8747):
            value = values[value_id]
            original = copy.deepcopy(value["dtype"])
            with self.subTest(value=value_id, field="scale"):
                value["dtype"]["element_dtype"]["scale"] = "@scales([axis=-1, scales=[2]])"
                with self.assertRaises(ValueError):
                    build_partition(self.graph, native_layout=True)
            value["dtype"] = copy.deepcopy(original)
            with self.subTest(value=value_id, field="shape"):
                value["dtype"]["shape"][-1] += 1
                with self.assertRaises(ValueError):
                    build_partition(self.graph, native_layout=True)
            value["dtype"] = original

    def test_reject_escaping_native_conversion(self):
        self.ops[7645]["inputs"].append(self.ops[7634]["outputs"][0])
        with self.assertRaisesRegex(ValueError, "format intermediate escapes"):
            build_partition(self.graph, native_layout=True)

    def test_reject_changed_semantics(self):
        for op_id, field, value in ((188, "largest", False), (437, "sorted", False),
                                    (188, "axis", 0), (192, "axis", 2),
                                    (442, "axis", 1), (442, "_type_key", "icraft::xir::GatherElements")):
            with self.subTest(op=op_id, field=field):
                changed = copy.deepcopy(self.original)
                next(op for op in changed["ops"] if op["op_id"] == op_id)[field] = value
                with self.assertRaises(ValueError):
                    build_partition(changed)

    def test_reject_escaping_indices(self):
        # A retained model consumer would invalidate removing the index chain.
        self.ops[7645]["inputs"].append(self.ops[188]["outputs"][1])
        with self.assertRaises(ValueError):
            build_partition(self.graph)

    def test_reject_escaping_expansion(self):
        self.ops[7645]["inputs"].append(self.ops[7636]["outputs"][0])
        with self.assertRaises(ValueError):
            build_partition(self.graph)

    def test_reject_changed_storage(self):
        self.ops[7634]["outputs"][0]["dtype"]["element_dtype"] = "@fp(16)"
        with self.assertRaises(ValueError):
            build_partition(self.graph)

    def test_reject_changed_shape(self):
        self.ops[437]["outputs"][0]["dtype"]["shape"] = [50]
        with self.assertRaises(ValueError):
            build_partition(self.graph)

    def test_reject_changed_layout(self):
        self.ops[7634]["outputs"][0]["dtype"]["layout"] = "@layout(C**)"
        with self.assertRaises(ValueError):
            build_partition(self.graph)

    def test_reject_changed_gather_output(self):
        self.ops[192]["outputs"][0]["v_id"] = 999999
        with self.assertRaises(ValueError):
            build_partition(self.graph)

    def test_reject_unresolved_host_dependency(self):
        self.ops[7650]["_type_key"] = "icraft::xir::Add"
        with self.assertRaises(ValueError):
            build_partition(self.graph)

    def test_reject_non_topological_order(self):
        first = self.graph["ops"].index(self.ops[7650])
        second = self.graph["ops"].index(self.ops[7630])
        self.graph["ops"][first], self.graph["ops"][second] = self.graph["ops"][second], self.graph["ops"][first]
        with self.assertRaises(ValueError):
            build_partition(self.graph)


if __name__ == "__main__":
    unittest.main()
