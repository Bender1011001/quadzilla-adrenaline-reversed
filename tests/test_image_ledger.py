"""Test byte-accounting invariants and pin the discovered relocation evidence."""
import importlib.util
import json
import unittest

from tests._paths import ROOT

spec = importlib.util.spec_from_file_location("ledger", ROOT / "audit/tools/build_image_ledger.py")
ledger = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ledger)


class ImageLedger(unittest.TestCase):
    def test_coverage_rejects_gaps_overlaps_and_truncation(self):
        def row(a, b):
            return {"start": hex(a), "end": hex(b)}
        ledger.validate_item_coverage([row(0, 2), row(2, 4)], 0, 4)
        for rows in ([row(0, 1), row(2, 4)], [row(0, 3), row(2, 4)], [row(0, 3)], [row(0, 5)], [row(0, 0)]):
            with self.subTest(rows=rows), self.assertRaises(ValueError):
                ledger.validate_item_coverage(rows, 0, 4)

    def test_real_ledger_accounts_for_image_without_claiming_completion(self):
        doc = json.loads((ROOT / "audit/data/image_coverage_ledger.json").read_text())
        ledger.validate_item_coverage(doc["ranges"])
        self.assertEqual(sum(doc["classification_bytes"].values()), 32000)
        self.assertIn("incomplete", doc["completion"])
        self.assertGreater(doc["classification_bytes"]["ida_code_pending_review"], 0)
        self.assertGreater(len(doc["ida_layout_conflicts"]), 0)

    def test_ram_template_descriptor_and_call_targets(self):
        doc = json.loads((ROOT / "audit/data/image_coverage_ledger.json").read_text())
        descriptor = next(r for r in doc["startup_descriptors"] if r["at"] == "0x96dc")
        self.assertEqual(descriptor, {"at": "0x96dc", "length": 164, "destination": "0x200c84", "source": "0xb114", "operation": "copy"})
        items = json.loads((ROOT / "audit/data/ida_image_items.json").read_text())["items"]
        refs = {r["start"]: r.get("decoded_direct_target") for r in items}
        self.assertEqual([refs[a] for a in ("0x6b28", "0x6b36", "0x77e4")], ["0x200c84", "0x200c94", "0x200cfc"])

    def test_bounded_decode_recovers_entry_after_ff_alignment(self):
        doc = json.loads((ROOT / "audit/data/startup_relocation_binaryninja.json").read_text())
        rows = {r["start"]: r for r in doc["ranges"]}
        self.assertEqual(rows["0xb124"]["instructions"][0]["text"].split()[0], "push")
        self.assertEqual(rows["0xb18c"]["instructions"][0]["text"].split()[0], "push")
        self.assertNotIn("decode_stopped_at", rows["0xb124"])


if __name__ == "__main__":
    unittest.main()
