"""Check the committed source-bound scalar helper structure evidence."""
import json
import unittest

from tests._paths import ROOT


class ScalarTelemetryStructure(unittest.TestCase):
    def test_body_pool_and_direct_flow(self):
        data = json.loads((ROOT / "audit/data/scalar_telemetry_structure.json").read_text())
        self.assertEqual(data["raw_sha256"], "1ae519ba6194e8f7bdaaa94333a83a9e6fda3b0563f87f7d48383b37288c1780")
        self.assertEqual(data["code_range"], ["0x4d38", "0x5016"])
        self.assertEqual(data["alignment_nop"], ["0x5016", "0x5018"])
        self.assertEqual(data["decoded_instruction_starts_including_nop"], 350)
        self.assertEqual(len(data["literal_words"]), 21)
        self.assertEqual(data["pc_relative_loads"], 30)
        self.assertTrue(all(word["load_sites"] for word in data["literal_words"]))
        self.assertEqual(len(data["internal_direct_branches"]), 51)
        self.assertEqual(len(data["direct_calls"]), 18)
        self.assertEqual({x["target"] for x in data["direct_calls"]}, {"0x8574", "0x8584"})


if __name__ == "__main__":
    unittest.main()
