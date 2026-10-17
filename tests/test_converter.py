"""Dependency-free tests for the native-coordinate compiler."""

import copy
import importlib.util
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("moss_bbox_core", ROOT / "core.py")
core = importlib.util.module_from_spec(spec)
spec.loader.exec_module(core)


class LayoutConversionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.layout = json.loads((ROOT / "examples" / "layout_1000.json").read_text(encoding="utf-8"))

    def test_full_canvas_multiple_aspect_ratios(self):
        for w, h in ((1248, 1680), (1024, 1024), (1920, 1088), (896, 1152), (16, 16)):
            with self.subTest(size=(w, h)):
                converted = core.convert_layout(self.layout, w, h)
                self.assertEqual(converted["bbox_coord_space"], "abs_centralized")
                self.assertEqual(converted["bbox_format"], "yxyx")
                self.assertEqual(converted["items"][0]["bbox"], [-h // 2, -w // 2, h // 2, w // 2])

    def test_sample_panel_coordinates(self):
        converted = core.convert_layout(self.layout, 1248, 1680)
        self.assertEqual(converted["items"][1]["bbox"], [-773, -580, -580, -231])

    def test_center_scaling_and_text_preservation(self):
        converted = core.convert_layout(self.layout, 1248, 1680)
        text_item = converted["items"][-1]
        self.assertEqual(text_item["text"], "CENTER")
        self.assertEqual(text_item["bbox"], [-59, -137, 59, 137])
        self.assertNotIn("text", converted["items"][0])

    def test_no_mutation(self):
        inp = copy.deepcopy(self.layout)
        core.convert_layout(inp, 1024, 1024)
        self.assertEqual(inp, self.layout)

    def test_extracts_json_from_markdown(self):
        output = "# Heading\n```json\n" + json.dumps(self.layout) + "\n```\nExtra paragraph."
        self.assertEqual(core.extract_layout(output), self.layout)

    def test_rejects_native_input(self):
        native = core.convert_layout(self.layout, 1024, 1024)
        with self.assertRaisesRegex(ValueError, "already native"):
            core.convert_layout(native, 1024, 1024)

    def test_inverted_box_rejected(self):
        invalid = copy.deepcopy(self.layout)
        invalid["items"][0]["bbox"] = [200, 100, 100, 500]
        with self.assertRaisesRegex(ValueError, "top < bottom"):
            core.convert_layout(invalid, 1024, 1024)

    def test_out_of_grid_rejected(self):
        invalid = copy.deepcopy(self.layout)
        invalid["items"][0]["bbox"] = [0, -5, 1000, 1000]
        with self.assertRaisesRegex(ValueError, "outside"):
            core.convert_layout(invalid, 1024, 1024)

    def test_boolean_coordinate_rejected(self):
        invalid = copy.deepcopy(self.layout)
        invalid["items"][0]["bbox"][0] = True
        with self.assertRaisesRegex(ValueError, "integer"):
            core.convert_layout(invalid, 1024, 1024)

    def test_dimensions_must_be_multiples_of_sixteen(self):
        with self.assertRaisesRegex(ValueError, "multiples of 16"):
            core.convert_layout(self.layout, 1000, 1024)

    def test_native_box_cannot_collapse(self):
        invalid = copy.deepcopy(self.layout)
        invalid["items"][0]["bbox"] = [2, 2, 3, 3]
        with self.assertRaisesRegex(ValueError, "zero-area"):
            core.convert_layout(invalid, 16, 16)

    def test_text_item_requires_literal_text(self):
        invalid = copy.deepcopy(self.layout)
        del invalid["items"][2]["text"]
        with self.assertRaisesRegex(ValueError, "requires"):
            core.convert_layout(invalid, 1024, 1024)

    def test_marker_and_field_format(self):
        invalid = copy.deepcopy(self.layout)
        invalid["bbox_coord_space"] = "relative"
        with self.assertRaisesRegex(ValueError, "Unsupported"):
            core.convert_layout(invalid, 1024, 1024)
        invalid = copy.deepcopy(self.layout)
        invalid["bbox_format"] = "xyxy"
        with self.assertRaisesRegex(ValueError, "bbox_format"):
            core.convert_layout(invalid, 1024, 1024)

    def test_node_mapping_imports(self):
        spec = importlib.util.spec_from_file_location("moss_bbox_nodes", ROOT / "__init__.py", submodule_search_locations=[str(ROOT)])
        module = importlib.util.module_from_spec(spec)
        sys_modules_name = spec.name
        import sys
        sys.modules[sys_modules_name] = module
        try:
            spec.loader.exec_module(module)
            cls = module.NODE_CLASS_MAPPINGS["MossBBox1000ToNative"]
            self.assertEqual(json.loads(cls().compile_layout(json.dumps(self.layout), 1248, 1680)[0])["bbox_coord_space"], "abs_centralized")
        finally:
            del sys.modules[sys_modules_name]


if __name__ == "__main__":
    unittest.main()
