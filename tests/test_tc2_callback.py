"""Check the exact-image TC2 state evidence without requiring local vendor bytes."""
import json
import unittest

from tests._paths import ROOT


def load(name):
    return json.loads((ROOT / "audit/data" / name).read_text(encoding="utf-8"))


def writes(case):
    return {w["address"]: w["value"] for w in case["writes"]}


class Tc2Callback(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.emu = load("tc2_callback_emulation.json")
        cls.bn = load("tc2_callback_binaryninja.json")
        cls.cases = {c["name"]: c for c in cls.emu["cases"]}

    def test_source_bounds_and_executed_instruction_coverage(self):
        self.assertEqual(self.emu["raw_sha256"], self.bn["raw_sha256"])
        self.assertEqual(self.emu["raw_sha256"], load("semantic_labels.json")["raw_sha256"])
        self.assertEqual([(r["start"], r["end"]) for r in self.bn["ranges"]],
                         [("0x6c94", "0x6f56")])
        instructions = [i for r in self.bn["ranges"] for i in r["instructions"]]
        self.assertEqual(sum(i["length"] for i in instructions), 706)
        self.assertEqual(len(instructions), 333)
        self.assertTrue(all("decode_stopped_at" not in r for r in self.bn["ranges"]))
        seen = {a for c in self.cases.values() for a in c["callback_visited"]}
        self.assertEqual(seen, {i["address"] for i in instructions})
        self.assertEqual(len(self.cases), 50)
        self.assertTrue(all(c["callee_saved_r4_r7_preserved"] for c in self.cases.values()))
        self.assertEqual(self.emu["source_literals"]["0x6f58"], "0x200708")
        self.assertEqual(self.emu["source_literals"]["0x6f60"], "0x200ad0")

    def test_threshold_actions_and_below_threshold_cases(self):
        events = {"a1": "0x20070b", "a4": "0x2007cb", "a6": "0x2007ca",
                  "a8": "0x200712", "ae": "0x200718", "a14": "0x20071e",
                  "a17": "0x200721", "b0": "0x200ad2", "a1d": "0x200727",
                  "b3": "0x200ad5", "b6": "0x200ad8", "b9": "0x200adb",
                  "b0e": "0x200ae0"}
        for name, event in events.items():
            self.assertEqual(writes(self.cases[name])[event], "0x1", name)
            self.assertNotIn(event, writes(self.cases[name+"_below"]), name)
        self.assertEqual(writes(self.cases["a1_wrap"])["0x200750"], "0x0")
        self.assertEqual(writes(self.cases["a1_wrap"])["0x20070b"], "0x1")
        self.assertNotIn("0x20071f", writes(self.cases["a17"]))
        self.assertEqual(writes(self.cases["a_b"])["0x200715"], "0x1")
        self.assertEqual(writes(self.cases["a_11"])["0x20071b"], "0x1")
        self.assertEqual(writes(self.cases["unconditional_b_d"])["0x200add"], "0x1")

    def test_ida_display_macros_account_for_item_difference(self):
        ida = load("ida_image_items.json")
        self.assertEqual(ida["raw_sha256"], self.emu["raw_sha256"])
        self.assertTrue(ida["database_bytes_match"])
        items = [i for i in ida["items"] if 0x6C94 <= int(i["start"], 0) < 0x6F56]
        self.assertEqual(len(items), 331)
        self.assertTrue(all(i["kind"] == "ida_code" and i["thumb"] == 1 for i in items))
        ida_slots = {(int(i["start"], 0), int(i["end"], 0)-int(i["start"], 0)) for i in items}
        bn_slots = {(int(i["address"], 0), i["length"]) for r in self.bn["ranges"]
                    for i in r["instructions"]}
        self.assertEqual(ida_slots-bn_slots, {(0x6D34, 4), (0x6D98, 4)})
        self.assertEqual(bn_slots-ida_slots,
                         {(0x6D34, 2), (0x6D36, 2), (0x6D98, 2), (0x6D9A, 2)})

    def test_aic_retry_model_is_explicit(self):
        retry = self.cases["a1d_enable_retry"]
        self.assertEqual(retry["aic_initial_mask"], "0x0")
        self.assertTrue(retry["modeled_aic_enable_command"])
        self.assertEqual([w for w in retry["writes"] if w["address"] == "0xfffff120"],
                         [{"site": "0x6dc6", "address": "0xfffff120", "size": 4, "value": "0x4"}])
        self.assertFalse(self.cases["a1d"]["modeled_aic_enable_command"])
        self.assertNotIn("0xfffff120", writes(self.cases["a1d"]))

    def test_numeric_gate_and_finite_sample(self):
        on = writes(self.cases["numeric_gate_on"])
        expected = {"0x200740": "0x41200000", "0x20073c": "0xf",
                    "0x200738": "0x0", "0x20074c": "0x3f800016",
                    "0x200744": "0x40000000", "0x200748": "0x40200000"}
        for address, value in expected.items():
            self.assertEqual(on[address], value)
            self.assertNotIn(address, writes(self.cases["numeric_gate_off"]))
        self.assertEqual(on["0x200708"], "0x1")
        self.assertEqual(self.cases["numeric_gate_on"]["numeric_wrapper_entries_visited"],
                         ["0x7120", "0x7128", "0x7138", "0x7140", "0x7148",
                          "0x7150", "0x7158", "0x7160", "0x7168"])

    def test_numeric_reference_comparisons_are_complete(self):
        cases = self.emu["numeric_reference_cases"]
        self.assertEqual(len(cases), 24)
        self.assertEqual(len({tuple(c["inputs"]) for c in cases}), 24)
        self.assertEqual(self.emu["numeric_reference_mismatches"], 0)
        for case in cases:
            self.assertEqual(case["actual"], case["expected"], case["inputs"])
            self.assertTrue(case["matches"])
            self.assertEqual(case["status_byte_af8"], "0x0")


if __name__ == "__main__":
    unittest.main()
