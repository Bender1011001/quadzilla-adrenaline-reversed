"""Check published source table and caller-bound evidence integrity."""
import hashlib
import json
import unittest

from tests._paths import ROOT


class CaptureTableBounds(unittest.TestCase):
    def test_source_table_and_axes(self):
        doc = json.loads((ROOT / "audit/data/capture_table_bounds.json").read_text())
        self.assertEqual(doc["raw_sha256"], "1ae519ba6194e8f7bdaaa94333a83a9e6fda3b0563f87f7d48383b37288c1780")
        self.assertEqual(doc["table_source"], ["0x997c", "0x9b0c"])
        self.assertEqual(doc["table_runtime"], ["0x200294", "0x200424"])
        self.assertEqual(doc["shape"], [20, 20])
        self.assertEqual(len(doc["rows"]), 20)
        self.assertTrue(all(len(row) == 20 for row in doc["rows"]))
        table = bytes(value for row in doc["rows"] for value in row)
        self.assertEqual(hashlib.sha256(table).hexdigest(), doc["table_sha256"])
        self.assertEqual((min(table), max(table)), (0, 100))
        self.assertEqual(doc["initial_negative_signed_cells"], 0)
        self.assertEqual(sum(row["count"] for row in doc["value_counts"]), 400)
        self.assertEqual((doc["max_offset"], doc["last_address"]), (399, "0x200423"))
        self.assertEqual(doc["capture_axis"]["range"], [0, 19])
        self.assertEqual(doc["input_axis"]["range"], [0, 19])
        for key in ("capture_axis", "input_axis"):
            self.assertTrue(all(0 <= p["index"] <= 19 for p in doc[key]["probes"]))


if __name__ == "__main__":
    unittest.main()
