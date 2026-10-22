"""Check headline conclusions against the fresh, byte-verified tool exports."""
import json
import unittest

from tests._paths import ROOT

SHA = "1ae519ba6194e8f7bdaaa94333a83a9e6fda3b0563f87f7d48383b37288c1780"


class FreshTraces(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ida = json.loads((ROOT / "audit/data/ida_verified_traces.json").read_text())
        cls.bn = json.loads((ROOT / "audit/data/binaryninja_seeded_check.json").read_text())

    def test_tool_exports_are_bound_to_same_firmware(self):
        self.assertTrue(self.ida["database_bytes_match"])
        for doc in (self.ida, self.bn):
            self.assertEqual(doc["raw_sha256"], SHA)
            self.assertEqual(len(doc["entries"]), 14)
        self.assertTrue(all(row["thumb"] == 1 for row in self.ida["entries"]))
        self.assertTrue(all(row["recognized"] for row in self.bn["entries"]))

    def test_timer_rc_store_agrees_at_exact_address(self):
        for doc in (self.ida, self.bn):
            row = next(row for row in doc["entries"] if row["entry"] == "0x6fa0")
            store = next(i for i in row["instructions"] if i["address"] == "0x6fa6")
            self.assertEqual("".join(store["text"].lower().split()), "strr1,[r0,#0x1c]")

    def test_rpm_and_stretch_upper_clamp_literals(self):
        self.assertEqual(self.ida["literal_words"], {"0x67c0": 2201, "0x67d8": 3701})


if __name__ == "__main__":
    unittest.main()
