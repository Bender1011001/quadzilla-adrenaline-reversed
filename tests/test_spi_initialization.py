"""Check initialization order, retry behavior and bounded timeout evidence."""
import json
import unittest

from tests._paths import ROOT


def load(name):
    return json.loads((ROOT / "audit/data" / name).read_text(encoding="utf-8"))


class SpiInitialization(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.emu = load("spi_initialization_emulation.json")
        cls.bn = load("spi_initialization_binaryninja.json")
        cls.cases = {c["mode"]: c for c in cls.emu["cases"]}

    def test_source_bounds_and_partial_capture_path(self):
        self.assertEqual(self.emu["raw_sha256"], self.bn["raw_sha256"])
        self.assertEqual(self.emu["raw_sha256"], load("semantic_labels.json")["raw_sha256"])
        instructions = [i for r in self.bn["ranges"] for i in r["instructions"]]
        self.assertEqual(sum(i["length"] for i in instructions), 652)
        self.assertEqual(len(instructions), 297)
        self.assertEqual({i["address"] for i in instructions},
                         {a for c in self.cases.values() for key in
                          ("initializer_visited", "capture_reset_path_visited") for a in c[key]})
        manifest = load("reviewed_instruction_ranges.json")
        capture = [(r["start"], r["end"]) for r in manifest["ranges"] if r["entry"] == "0x59e8"]
        self.assertIn(("0x59e8", "0x59fe"), capture)
        self.assertIn(("0x5cb2", "0x5cba"), capture)

    def test_ready_order_and_retry_per_site(self):
        ready, retry = self.cases["ready"], self.cases["retry_once_each"]
        self.assertEqual((ready["outcome"], retry["outcome"]), ("returned", "returned"))
        self.assertEqual(len(ready["transfer_calls"]), 24)
        self.assertEqual(len(retry["transfer_calls"]), 48)
        self.assertEqual(len({x["site"] for x in ready["transfer_calls"]}), 24)
        self.assertEqual([x["site"] for x in ready["transfer_calls"]],
                         [x["site"] for x in retry["transfer_calls"][::2]])
        for first, second in zip(retry["transfer_calls"][::2], retry["transfer_calls"][1::2]):
            self.assertEqual(first["site"], second["site"])
            self.assertFalse(first["scripted_ready"])
            self.assertTrue(second["scripted_ready"])
        self.assertEqual(sum(x["helper"] == "0x6b9c" for x in ready["transfer_calls"]), 1)
        self.assertEqual(ready["transfer_calls"][2]["args"],
                         ["0xfffe0000", "0x2006b0", "0x200629", "0x3"])
        self.assertEqual((ready["reset_state_2005de"], ready["output_state_2005df"],
                          ready["request_2005d4"], ready["pending_2005d5"]), (0, 0, 1, 0))

    def test_timeout_stops_at_reset_and_unready_probe_remains_bounded(self):
        timeout = self.cases["timeout"]
        self.assertEqual(timeout["outcome"], "reset_request_stop")
        self.assertEqual(timeout["external_flag_injections"],
                         [{"site": "0x5798", "address": "0x200ad5", "value": 1}])
        self.assertEqual(len(timeout["transfer_calls"]), 24)
        self.assertTrue(all(not c["scripted_ready"] for c in timeout["transfer_calls"]))
        self.assertEqual(timeout["writes"][-1],
                         {"site": "0x59b0", "address": "0xfffffd00", "size": 4, "value": "0xa500000d"})
        self.assertFalse(any(0xFFFE0100 <= int(w["address"], 0) < 0xFFFE0124 for w in timeout["writes"]))
        stalled = self.cases["not_ready"]
        self.assertEqual(stalled["outcome"], "instruction_budget")
        self.assertEqual({c["site"] for c in stalled["transfer_calls"]}, {"0x5790"})
        self.assertEqual(stalled["timeout_flag"], 0)

    def test_initial_transmit_is_first_record_of_supported_table(self):
        call = next(c for c in self.cases["ready"]["transfer_calls"] if c["site"] == "0x58fe")
        self.assertEqual(call["args"], ["0xfffe0000", "0x9ff0", "0x9"])
        ledger = load("image_coverage_ledger.json")
        rows = [r for r in ledger["ranges"] if r["classification"] == "spi_request_tx_table"]
        self.assertEqual(min(int(r["start"], 0) for r in rows), 0x9FF0)
        self.assertTrue(any(int(r["start"], 0) < 0x9FF9 <= int(r["end"], 0) for r in rows))
        self.assertEqual(ledger["classification_bytes"]["spi_request_tx_table"], 63)


if __name__ == "__main__":
    unittest.main()
