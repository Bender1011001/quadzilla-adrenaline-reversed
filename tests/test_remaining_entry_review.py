"""Regression checks for the last baseline roles and their indirect evidence."""
import json
import unittest

from tests._paths import ROOT


DATA = ROOT / "audit/data"
SHA = "1ae519ba6194e8f7bdaaa94333a83a9e6fda3b0563f87f7d48383b37288c1780"


class RemainingEntryReview(unittest.TestCase):
    def test_indirect_callback_and_predicate(self):
        run = json.loads((DATA / "remaining_entry_emulation.json").read_text())
        ida = json.loads((DATA / "ida_image_items.json").read_text())
        self.assertEqual(run["raw_sha256"], SHA)
        self.assertEqual(run["literal_words"], {
            "0x7a48": "0x7445", "0x74e0": "0x200791", "0x74e4": "0x2005dd",
        })
        load = next(x for x in ida["items"] if x["start"] == "0x77e0")
        self.assertIn("0x7445", load["data_refs"])
        self.assertIn("0x7a48", load["data_refs"])
        self.assertTrue(run["no_op_callback"]["returned"])
        self.assertEqual(run["no_op_callback"]["r0"], "0xa5a5a5a5")
        cases = {(c["sram_0x200791"], c["sram_0x2005dd"]): int(c["r0"], 0)
                 for c in run["sram_predicate"]}
        self.assertEqual(cases, {(0, 0): 0, (1, 0): 0, (0, 1): 0,
                                 (1, 1): 1, (255, 2): 1})

    def test_copied_ready_loop_and_catalog_boundary(self):
        run = json.loads((DATA / "remaining_entry_emulation.json").read_text())
        helper = run["runtime_ready_helper"]
        self.assertEqual((helper["source"], helper["runtime"]), ("0xb114", "0x200c84"))
        self.assertTrue(helper["ready_status_1"]["returned"])
        self.assertFalse(helper["waiting_status_0"]["returned"])
        catalog = json.loads((DATA / "execution_entry_catalog.json").read_text())
        self.assertEqual((catalog["summary"]["confirmed_entries"],
                          catalog["summary"]["unlabeled_static_entries"]), (145, 0))
        ledger = json.loads((DATA / "image_coverage_ledger.json").read_text())
        self.assertEqual(ledger["classification_bytes"]["ram_executable_template"], 164)


if __name__ == "__main__":
    unittest.main()
