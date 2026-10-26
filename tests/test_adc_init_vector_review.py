"""Keep the committed cross-decoder review tied to the audited image."""
import json
import unittest

from tests._paths import ROOT


DATA = ROOT / "audit/data"
SHA = "1ae519ba6194e8f7bdaaa94333a83a9e6fda3b0563f87f7d48383b37288c1780"


class ADCInitVectorReview(unittest.TestCase):
    def test_explicit_thumb_ranges_reconcile_ida_pseudo_instructions(self):
        decoded = json.loads((DATA / "adc_init_vector_binaryninja.json").read_text())
        ida = json.loads((DATA / "ida_image_items.json").read_text())
        self.assertEqual(decoded["raw_sha256"], SHA)
        starts = {int(row["start"], 0) for row in ida["items"] if row["kind"] == "ida_code"}
        ranges = {row["start"]: row for row in decoded["ranges"]}
        self.assertEqual(set(ranges), {"0x4330", "0x73cc", "0x73d4", "0x73dc", "0x73e4", "0x6b20"})
        self.assertEqual(sum(int(row["end"], 0) - int(row["start"], 0)
                             for row in ranges.values()), 168)
        folded = {0x73e8, 0x740e}
        observed_folded = set()
        for row in ranges.values():
            with self.subTest(entry=row["start"]):
                self.assertEqual(row["architecture"], "thumb2")
                self.assertNotIn("decode_stopped_at", row)
                self.assertEqual(sum(ins["length"] for ins in row["instructions"]),
                                 int(row["end"], 0) - int(row["start"], 0))
                for ins in row["instructions"]:
                    address = int(ins["address"], 0)
                    if address not in starts:
                        observed_folded.add(address)
                        self.assertIn(address, folded)
        self.assertEqual(observed_folded, folded)

    def test_key_paths_stay_in_reviewed_trace(self):
        decoded = json.loads((DATA / "adc_init_vector_binaryninja.json").read_text())
        rows = {row["start"]: {ins["address"]: ins["text"] for ins in row["instructions"]}
                for row in decoded["ranges"]}
        self.assertIn("str", rows["0x4330"]["0x4346"])
        self.assertIn("beq", rows["0x73e4"]["0x73f8"])
        self.assertIn("#0x6b20", rows["0x73e4"]["0x7422"])
        self.assertIn("#0x200c94", rows["0x6b20"]["0x6b36"])


if __name__ == "__main__":
    unittest.main()
