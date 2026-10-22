import json
import unittest

from tests._paths import ROOT
from model_aid_ingest import fixed_width, value_capacity, walk_fixed


class IngestModel(unittest.TestCase):
    def test_width_boundaries_and_capacity(self):
        self.assertEqual([fixed_width(a) for a in (74, 75, 149, 150, 184, 185, 219)], [1, 2, 2, 3, 3, 4, 4])
        self.assertEqual([value_capacity(a) for a in (5, 85, 151, 185)], [7, 4, 3, 2])

    def test_complete_staging_write(self):
        result = walk_fixed(bytes([85, 0x20, 0x03]), {85: 0x200B30})
        self.assertEqual(result.memory, {0x200B30: 0x20, 0x200B31: 3})
        self.assertEqual((result.status, result.reported_aids), (1, [85]))

    def test_incomplete_value_has_already_changed_staging(self):
        result = walk_fixed(bytes([85, 0x20]), {85: 0x200B30}, {0x200B30: 1, 0x200B31: 9})
        self.assertEqual(result.memory, {0x200B30: 0x20, 0x200B31: 9})
        self.assertEqual((result.status, result.remaining), (2, 1))

    def test_unmapped_value_is_skipped_at_its_width(self):
        result = walk_fixed(bytes([85, 1, 2, 5, 9]), {5: 0x200B05})
        self.assertEqual(result.memory, {0x200B05: 9})
        self.assertEqual(result.reported_aids, [5])

    def test_unmodeled_cases_fail_explicitly(self):
        for payload in (b"", bytes([226, 1]), bytes(15)):
            with self.subTest(payload=payload), self.assertRaises(ValueError):
                walk_fixed(payload, {})

    def test_dangling_fixed_width_aid_reports_incomplete(self):
        result = walk_fixed(bytes([85]), {85: 0x200B30})
        self.assertEqual((result.memory, result.status, result.remaining), ({}, 2, 2))

    def test_model_anchors_are_in_both_tool_traces(self):
        ida = json.loads((ROOT / "audit/data/write_path_ida.json").read_text())
        bn = json.loads((ROOT / "audit/data/write_path_binaryninja.json").read_text())
        for doc in (ida, bn):
            writer = next(e for e in doc["entries"] if e["entry"] == "0x7cc4")
            instructions = {i["address"]: "".join(i["text"].lower().split()) for i in writer["instructions"]}
            self.assertEqual(instructions["0x7cd6"], "cmpr2,#0xf")
            self.assertEqual(instructions["0x7cdc"], "movsr3,#0xe")
            self.assertEqual(instructions["0x7d6c"], "strbr2,[r0]")
            self.assertEqual(instructions["0x7d70"], "addsr0,r0,#1")


if __name__ == "__main__":
    unittest.main()
