import hashlib
import json
import unittest

from tests._paths import ROOT
from model_flash_helper import page_command, staged_word_count


def load(name):
    return json.loads((ROOT / "audit/data" / name).read_text(encoding="utf-8"))


class StartupPersistence(unittest.TestCase):
    def test_supplement_adds_distinct_source_entries_not_runtime_aliases(self):
        base = load("execution_entry_catalog.json")
        supplement = load("entry_adjudications.json")
        starts = {e["entry"] for e in base["entries"]}
        extra = {e["start"] for e in supplement["entries"]}
        self.assertFalse(starts & extra)
        self.assertEqual(len(starts | extra), supplement["combined_supported_starts"])
        self.assertEqual(len(extra), 6)
        self.assertEqual(supplement["baseline_lf_text_sha256"], hashlib.sha256(
            (ROOT / "audit/data/execution_entry_catalog.json").read_text(encoding="utf-8").encode()).hexdigest())
        for e in supplement["entries"]:
            if e["runtime_alias"]:
                self.assertEqual(int(e["runtime_alias"], 0)-0x200C84, int(e["start"], 0)-0xB114)

    def test_irq_and_exception_direct_targets_in_full_export(self):
        items = {i["start"]: i for i in load("ida_image_items.json")["items"]}
        self.assertEqual(items["0x4018"]["decoded_direct_target"], "0x4090")
        self.assertEqual(items["0x4004"]["decoded_direct_target"], "0x40ec")
        self.assertIn("0x5A00000F", items["0xb19a"]["text"])
        self.assertEqual(items["0x77e4"]["decoded_direct_target"], "0x200cfc")

    def test_interworking_thunk_and_arm_body_are_decoded_separately(self):
        ranges = {r["start"]: r for r in load("startup_persistence_binaryninja.json")["ranges"]}
        self.assertEqual(ranges["0x8574"]["instructions"][0]["text"].split(), ["bx", "pc"])
        self.assertEqual(ranges["0x8578"]["architecture"], "armv7")
        self.assertEqual(ranges["0x8578"]["instructions"][0]["length"], 4)
        self.assertTrue(ranges["0x8578"]["instructions"][0]["text"].startswith("push"))

    def test_signed_length_and_nonword_lengths(self):
        self.assertEqual([staged_word_count(n) for n in (0, 1, 3, 4, 5, 128, 512, 513, 0x7FFFFFFF, 0x80000000, 0xFFFFFFFF)],
                         [0, 1, 1, 1, 2, 32, 128, 128, 128, 0, 0])

    def test_page_selector_alias_and_boundaries(self):
        self.assertEqual(page_command(0), page_command(0x100000))
        self.assertEqual(page_command(0x10007F), 0x5A000001)
        self.assertEqual(page_command(0x100080), 0x5A000101)
        self.assertEqual(page_command(0x100000+1024*128), 0x5A000001)


if __name__ == "__main__":
    unittest.main()
