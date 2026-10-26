"""Check committed source-bound curve dispatch evidence."""
import json
import unittest

from tests._paths import ROOT


class CaptureScalarStructure(unittest.TestCase):
    def test_jump_tables_and_literals(self):
        doc = json.loads((ROOT / "audit/data/capture_scalar_structure.json").read_text())
        self.assertEqual(doc["raw_sha256"], "1ae519ba6194e8f7bdaaa94333a83a9e6fda3b0563f87f7d48383b37288c1780")
        self.assertEqual(doc["code_ranges"], [["0x4b38", "0x4b82"], ["0x4ba2", "0x4c32"], ["0x4c3e", "0x4d0a"]])
        self.assertEqual(doc["alignment_nops"], ["0x4b82", "0x4c32", "0x4d0a"])
        self.assertEqual(doc["decoded_instruction_starts_including_nops"], 205)
        first, second = doc["byte_jump_tables"]
        self.assertEqual((len(first["entries"]), len(second["entries"])), (29, 10))
        self.assertEqual(first["entries"][0]["target"], "0x4ba2")
        self.assertEqual(second["entries"][0]["target"], "0x4c3e")
        self.assertEqual(doc["first_table_pad_zero"], "0x4ba1")
        self.assertEqual(len(doc["literal_words"]), 11)
        self.assertEqual(len(doc["internal_direct_branches"]), 55)
        self.assertEqual(len(doc["direct_calls"]), 9)
        self.assertEqual({x["target"] for x in doc["direct_calls"]}, {"0x47b0", "0x8574"})


if __name__ == "__main__":
    unittest.main()
