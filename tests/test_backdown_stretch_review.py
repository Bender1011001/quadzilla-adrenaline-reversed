"""Check source-bound backdown and stretch coverage claims."""
import json
import unittest

from tests._paths import ROOT


DATA = ROOT / "audit/data"
SHA = "1ae519ba6194e8f7bdaaa94333a83a9e6fda3b0563f87f7d48383b37288c1780"


class BackdownStretchReview(unittest.TestCase):
    def test_original_byte_case_and_instruction_coverage(self):
        decode = json.loads((DATA / "backdown_stretch_binaryninja.json").read_text())
        backdown = json.loads((DATA / "backdown_emulation.json").read_text())
        stretch = json.loads((DATA / "stretch_arithmetic_emulation.json").read_text())
        self.assertEqual((decode["raw_sha256"], backdown["raw_sha256"], stretch["raw_sha256"]),
                         (SHA, SHA, SHA))
        blocks = {r["start"]: r for r in decode["ranges"]}
        self.assertEqual(set(blocks), {"0x499c", "0x4a94"})
        self.assertEqual(backdown["case_count"], 4126)
        self.assertEqual(backdown["directed_cases"], 30)
        self.assertEqual({i["address"] for i in blocks["0x499c"]["instructions"]},
                         set(backdown["visited_addresses"]))
        stretch_body = {i["address"] for i in blocks["0x4a94"]["instructions"]
                        if int(i["address"], 0) < 0x4B26}
        self.assertTrue(stretch_body <= set(stretch["visited_addresses"]))
        self.assertEqual((stretch["cases"], stretch["mismatches"]), (2092, []))

    def test_literal_and_aid_response_identity(self):
        backdown = json.loads((DATA / "backdown_emulation.json").read_text())
        self.assertEqual(backdown["literal_pools"], {
            "backdown": {"start": "0x4a88", "words": ["0xfffffed4", "0x2006cc", "0x2008a8"]},
            "stretch": {"start": "0x4b28", "words": ["0x200580", "0x200190", "0x200424", "0x2005f0"]},
        })
        table = json.loads((DATA / "aid_table_audit.json").read_text())
        aid13 = next(r for r in table["rows"] if r["aid"] == 13)
        self.assertEqual(aid13["table2"]["pointer"], "0x200bcd")


if __name__ == "__main__":
    unittest.main()
