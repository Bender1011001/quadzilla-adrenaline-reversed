"""Machine-check the headline numbers of docs/FIRMWARE_AUDIT.md against audit/data/."""
import json
import unittest

from tests._paths import ROOT

DATA = ROOT / "audit" / "data"
IMAGE_SHA256 = "1ae519ba6194e8f7bdaaa94333a83a9e6fda3b0563f87f7d48383b37288c1780"


def load(name):
    return json.loads((DATA / name).read_text(encoding="utf-8"))


class FirmwareAudit(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.audit = load("cross_disassembler_audit.json")
        cls.catalog = load("execution_entry_catalog.json")
        cls.periph = load("peripheral_reference_audit.json")

    def test_all_artifacts_bind_to_one_image(self):
        for name in ("cross_disassembler_audit.json", "execution_entry_catalog.json",
                     "peripheral_reference_audit.json", "semantic_labels.json",
                     "ida_function_map.json", "ghidra_function_map.json"):
            self.assertEqual(load(name)["raw_sha256"], IMAGE_SHA256, name)

    def test_tool_function_counts(self):
        fe = self.audit["function_entries"]
        self.assertEqual((fe["ida"], fe["ghidra"], fe["shared_exact"], fe["union"]), (122, 133, 109, 146))

    def test_boundaries_and_call_edges(self):
        self.assertEqual(self.audit["shared_function_boundaries"]["same_end"], 88)
        self.assertEqual(self.audit["shared_function_boundaries"]["different_end"], 21)
        edges = self.audit["direct_call_edges"]
        self.assertEqual((edges["ida"], edges["ghidra"], edges["shared"], edges["union"]), (136, 159, 115, 180))

    def test_critical_functions_confirmed_by_both_tools(self):
        self.assertEqual(len(self.audit["critical_functions"]), 13)
        self.assertTrue(self.audit["critical_all_cross_tool_confirmed"])

    def test_entry_catalog(self):
        s = self.catalog["summary"]
        self.assertEqual((s["confirmed_entries"], s["documented_static_roles"], s["unlabeled_static_entries"]), (145, 14, 131))
        entries = {e["entry"] for e in self.catalog["entries"]}
        self.assertEqual(len(entries), 145)
        # IDA proposed a function at 0xAE82 inside the AID pointer table (0xAD18-0xB113): rejected as data.
        self.assertNotIn("0xae82", entries)

    def test_peripheral_references_all_mapped(self):
        s = self.periph["summary"]
        self.assertEqual((s["peripheral_references"], s["mapped_references"], s["unmapped_references"]), (136, 136, 0))
        self.assertEqual(s["entries_with_peripheral_references"], 21)
        self.assertEqual(sum(s["block_reference_counts"].values()), 136)


if __name__ == "__main__":
    unittest.main()
