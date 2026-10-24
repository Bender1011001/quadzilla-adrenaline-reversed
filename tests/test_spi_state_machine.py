"""Pin the reviewed SPI state and payload behavior from original-byte evidence."""
import json
import unittest

from tests._paths import ROOT


def load(name):
    return json.loads((ROOT / "audit/data" / name).read_text(encoding="utf-8"))


class SpiStateMachine(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.emu = load("spi_state_machine_emulation.json")
        cls.bn = load("spi_state_machine_binaryninja.json")
        cls.named = {c["name"]: c for c in cls.emu["cases"] if c["name"] != "matrix"}

    def test_source_bounds_and_instruction_coverage(self):
        self.assertEqual(self.emu["raw_sha256"], self.bn["raw_sha256"])
        self.assertEqual(self.emu["raw_sha256"], load("semantic_labels.json")["raw_sha256"])
        self.assertEqual([(r["start"], r["end"]) for r in self.bn["ranges"]], [("0x5cf0", "0x5dea")])
        instructions = [i for r in self.bn["ranges"] for i in r["instructions"]]
        self.assertEqual(sum(i["length"] for i in instructions), 250)
        self.assertEqual(len(instructions), 118)
        self.assertEqual({i["address"] for i in instructions},
                         {a for c in self.emu["cases"] for a in c["routine_visited"]})
        self.assertEqual(len(self.emu["cases"]), 76)
        self.assertTrue(all(c["callee_saved_r4_r7_preserved"] for c in self.emu["cases"]))
        self.assertEqual(self.emu["initialized_spi_pointer"],
                         {"ram": "0x2005e0", "source": "0x9cc8", "value": "0xfffe0000"})
        ida = load("ida_image_items.json")
        items = [i for i in ida["items"] if 0x5CF0 <= int(i["start"], 0) < 0x5DEA]
        self.assertEqual({(i["start"], int(i["end"], 0)-int(i["start"], 0)) for i in items},
                         {(i["address"], i["length"]) for i in instructions})

    def test_reset_and_gate_families(self):
        explicit = self.named["explicit_reset"]
        self.assertEqual((explicit["state_out"], explicit["request_out"], explicit["pending_out"]), (0, 1, 1))
        for name in ("ordinary_gates_off", "alternate_gate_off"):
            case = self.named[name]
            self.assertEqual((case["state_out"], case["request_out"], case["pending_out"]), (0, 1, 0))
        for name in ("ordinary_second_gate", "alternate_gate_on"):
            case = self.named[name]
            self.assertEqual((case["state_out"], case["pending_out"], case["request_out"]), (2, 0, 9))

    def test_stable_status_transition_matrix(self):
        cases = [c for c in self.emu["cases"] if c["name"] == "matrix"]
        self.assertEqual(len(cases), 60)
        for case in cases:
            state, pending = case["state_in"], case["pending_in"]
            status, pins = int(case["synthetic_spi_sr"], 0), int(case["synthetic_pio_pdsr"], 0)
            ready = bool(status & 0x20 and pins & 0x800)
            expected_state, expected_pending, request = state, pending, 9
            if state == 0:
                if not pending:
                    request = 1
                elif ready:
                    expected_state, expected_pending, request = 2, 0, 0
            elif state == 1 and pending:
                expected_state, expected_pending = 2, 0
            elif state == 2 and ready and pins & 4:
                expected_state = 5
            elif state == 5 and status & 0x10:
                expected_state = 1
            self.assertEqual((case["state_out"], case["pending_out"], case["request_out"]),
                             (expected_state, expected_pending, request), case)

    def test_readiness_change_advances_without_pdc_writes(self):
        case = self.named["readiness_changes"]
        self.assertEqual(case["scripted_status_reads"], ["0x20", "0x0"])
        self.assertEqual(case["state_out"], 5)
        self.assertEqual(case["writes"], [])
        self.assertIsNotNone(case["packet_reference"])

    def test_signed_payload_packing(self):
        cases = [c for c in self.emu["cases"] if c["name"] == "payload_signed"]
        self.assertEqual(len(cases), 10)
        for case in cases:
            self.assertEqual(case["packet"], case["packet_reference"])
            self.assertEqual(case["state_out"], 5)
        by_input = {c["signed_word"]: bytes.fromhex(c["packet"]) for c in cases}
        self.assertEqual(by_input["0xffffffff"][5:7], b"\xff\x00")
        self.assertEqual(by_input["0xfffffeff"][5:7], b"\xff\xff")
        self.assertEqual(by_input["0xffffff00"][5:7], b"\x00\xff")


if __name__ == "__main__":
    unittest.main()
