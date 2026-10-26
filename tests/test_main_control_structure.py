"""Pin main-control byte boundaries, literals and conditional timer evidence."""
import json
import unittest

from tests._paths import ROOT


DATA = ROOT / "audit/data"
SHA = "1ae519ba6194e8f7bdaaa94333a83a9e6fda3b0563f87f7d48383b37288c1780"


class MainControlStructure(unittest.TestCase):
    def test_code_and_literal_islands_are_source_bound(self):
        report = json.loads((DATA / "main_control_structure.json").read_text())
        self.assertEqual(report["raw_sha256"], SHA)
        self.assertEqual(report["code_ranges"], [
            {"start": "0x50f0", "end": "0x53c4", "bytes": 724},
            {"start": "0x5414", "end": "0x5612", "bytes": 510},
        ])
        self.assertEqual(report["return_alignment_nop"], "0x5612..0x5614")
        self.assertEqual(report["decoded_instruction_starts"], 575)
        self.assertEqual(report["pc_relative_loads"], 94)
        self.assertEqual([len(p["words"]) for p in report["literal_pools"]], [20, 58])
        self.assertEqual(len(report["internal_direct_branches"]), 56)
        self.assertEqual(sum(x["sites"] for x in report["direct_calls"]), 43)
        self.assertEqual(len(report["direct_calls"]), 26)
        self.assertEqual(len(report["ida_folded_second_starts"]), 8)

    def test_timer_tail_cases_are_conditional(self):
        run = json.loads((DATA / "control_timer_tail_emulation.json").read_text())
        decode = json.loads((DATA / "tc0_rc_helper_binaryninja.json").read_text())
        self.assertEqual((run["raw_sha256"], decode["raw_sha256"]), (SHA, SHA))
        self.assertEqual(len(run["cases"]), 7)
        values = [c["tc0_rc_writes"] for c in run["cases"]]
        self.assertEqual(values, [["0x9f63"], ["0x1fe3"], [], [],
                                  ["0x3d6feae3"], ["0x3d6feae3"], ["0xfff3"]])
        self.assertEqual([c["effective_stretch_r6"] for c in run["cases"]],
                         [1700, 340, 1700, 1700, 42947700, 42947700, 2730])
        visited = {a for c in run["cases"] for a in c["visited"]}
        self.assertTrue({i["address"] for i in decode["ranges"][0]["instructions"]} <= visited)


if __name__ == "__main__":
    unittest.main()
