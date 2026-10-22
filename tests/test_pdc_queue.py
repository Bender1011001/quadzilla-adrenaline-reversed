import json
import unittest

from tests._paths import ROOT
from model_pdc_queue import QueueState, stage


class PdcQueue(unittest.TestCase):
    def test_idle_current_replaces_current_and_clears_next_pair(self):
        result, outcome = stage(QueueState(1, 0, 2, 8), 0x200800, 16)
        self.assertEqual(result, QueueState(0x200800, 16, 0, 0, 0))
        self.assertEqual(outcome, "current")

    def test_busy_current_uses_next_slot(self):
        result, outcome = stage(QueueState(1, 3), 2, 16)
        self.assertEqual(result, QueueState(1, 3, 2, 16, 0))
        self.assertEqual(outcome, "next")

    def test_full_slots_preserve_both_transfers_but_clear_software_flag(self):
        result, outcome = stage(QueueState(1, 3, 2, 16), 99, 7)
        self.assertEqual(result, QueueState(1, 3, 2, 16, 0))
        self.assertEqual(outcome, "not_staged")

    def test_zero_count_is_not_rejected_by_staging_logic(self):
        result, outcome = stage(QueueState(), 0x200800, 0)
        self.assertEqual((result.current_pointer, result.current_count, outcome), (0x200800, 0, "current"))

    def test_instruction_anchors_cover_both_slot_paths(self):
        doc = json.loads((ROOT / "audit/data/uart_buffer_binaryninja.json").read_text())
        rows = {r["start"]: r for r in doc["ranges"]}
        for start, zero_test, current_store, next_store in (
            ("0x71d0", "0x71e0", "0x71e6", "0x71f6"),
            ("0x720c", "0x721c", "0x7222", "0x7232")):
            instructions = {i["address"]: i["text"] for i in rows[start]["instructions"]}
            self.assertEqual(instructions[zero_test].split()[0], "cmp")
            self.assertEqual(instructions[current_store].split()[0], "str")
            self.assertEqual(instructions[next_store].split()[0], "str")

    def test_all_new_roles_have_inputs_outputs_and_limits(self):
        doc = json.loads((ROOT / "audit/data/uart_function_reviews.json").read_text())
        self.assertEqual(len(doc["entries"]), 15)
        for row in doc["entries"]:
            for field in ("role", "inputs", "outputs", "side_effects", "evidence", "confidence", "limits"):
                self.assertTrue(row[field], (row["entry"], field))


if __name__ == "__main__":
    unittest.main()
