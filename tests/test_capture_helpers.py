"""Pin capture helper bounds, request records and comparison evidence."""
import json
import unittest

from tests._paths import ROOT


def load(name):
    return json.loads((ROOT / "audit/data" / name).read_text(encoding="utf-8"))


class CaptureHelpers(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.emu = load("capture_helper_emulation.json")
        cls.bn = load("capture_helper_binaryninja.json")

    def test_source_and_instruction_coverage(self):
        self.assertEqual(self.emu["raw_sha256"], self.bn["raw_sha256"])
        self.assertEqual(self.emu["raw_sha256"], load("semantic_labels.json")["raw_sha256"])
        instructions = [i for r in self.bn["ranges"] for i in r["instructions"]]
        self.assertEqual(sum(i["length"] for i in instructions), 252)
        self.assertEqual(len(instructions), 123)
        seen = {a for c in self.emu["cases"] for a in c["visited"]} | set(self.emu["comparison"]["visited"])
        self.assertEqual(seen, {i["address"] for i in instructions})
        self.assertEqual(len(self.emu["cases"]), 172)

    def test_selector_index_option_and_table_extent(self):
        starts = set()
        for case in self.emu["cases"]:
            if case["entry"] != "0x5e04" or case["mode"] != "ready":
                continue
            mode, option, index = [int(a, 0) for a in case["args"]]
            if index >= 7:
                self.assertEqual(case["transfer_calls"], [])
                self.assertEqual(case["state_writes"], [])
                self.assertEqual(case["writes"], [])
                continue
            calls = case["transfer_calls"]
            starts.add(int(calls[0]["args"][1], 0))
            self.assertEqual(calls[0]["args"], ["0xfffe0000", hex(0x9FF0+9*index), "0x9"])
            self.assertEqual(len(calls), 2 if mode < 3 else 1)
            state = {w["address"]: w["value"] for w in case["state_writes"]}
            if mode < 3:
                self.assertEqual(calls[1]["args"], ["0xfffe0000", "0x2005d0", "0x3"])
                self.assertEqual(state["0x2005d1"], hex((0x30, 0x40, 0x50)[mode]))
                self.assertEqual(state["0x2005d2"], hex(8 | min(option, 3)))
            else:
                self.assertNotIn("0x2005d1", state)
        self.assertEqual(starts, {0x9FF0+9*i for i in range(7)})
        ledger = load("image_coverage_ledger.json")
        rows = [r for r in ledger["ranges"] if r["classification"] == "spi_request_tx_table"]
        self.assertEqual((min(int(r["start"], 0) for r in rows), max(int(r["end"], 0) for r in rows)),
                         (0x9FF0, 0xA02F))
        self.assertEqual(sum(int(r["end"], 0)-int(r["start"], 0) for r in rows), 63)

    def test_rotation_trigger_and_wrap(self):
        cases = [c for c in self.emu["cases"] if c["entry"] == "0x5ebc"]
        self.assertEqual(len(cases), 6)
        for case in cases:
            if not case["trigger"]:
                self.assertEqual(case["index_out"], case["index_in"])
                self.assertEqual(case["state_writes"], [])
                self.assertEqual(case["transfer_calls"], [])
            else:
                next_index = (case["index_in"]+1) & 255
                if next_index >= 7:
                    next_index = 0
                self.assertEqual(case["index_out"], next_index)
                self.assertEqual(case["transfer_calls"][0]["args"][1], hex(0x9FF0+9*next_index))

    def test_retry_timeout_and_bounded_stall(self):
        cases = {c["mode"]: c for c in self.emu["cases"] if c["mode"] != "ready"}
        self.assertEqual(cases["retry"]["outcome"], "returned")
        self.assertEqual([c["scripted_ready"] for c in cases["retry"]["transfer_calls"]],
                         [False, True, False, True])
        self.assertEqual(cases["timeout"]["outcome"], "reset_request_stop")
        self.assertEqual(cases["timeout"]["writes"][-1],
                         {"site": "0x5e96", "address": "0xfffffd00", "size": 4, "value": "0xa500000d"})
        self.assertEqual(cases["stall"]["outcome"], "instruction_budget")
        self.assertEqual({c["site"] for c in cases["stall"]["transfer_calls"]}, {"0x5e38"})

    def test_unsigned_comparison_reference(self):
        compare = self.emu["comparison"]
        self.assertEqual(compare["single_byte_cases"], 65536)
        self.assertEqual(compare["result_counts"], {"-1": 32640, "0": 256, "1": 32640})
        self.assertEqual(compare["reference_mismatches"], 0)
        self.assertEqual(len(compare["prefix_cases"]), 68)
        self.assertTrue(all(c["actual"] == c["expected"] for c in compare["prefix_cases"]))
        self.assertEqual(compare["zero_length_unmapped_inputs"], {"status": "returned", "r0": 0})


if __name__ == "__main__":
    unittest.main()
