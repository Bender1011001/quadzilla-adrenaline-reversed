"""Arithmetic/state regressions anchored to the original-byte execution report."""
import json
import unittest

from tests._paths import ROOT
from model_control_helpers import index19, latch_state, mean32, normalize, ramp_state, threshold6


class ControlHelpers(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.doc = json.loads((ROOT / "audit/data/control_helper_emulation.json").read_text(encoding="utf-8"))
        cls.suites = {s["entry"]: s for s in cls.doc["suites"]}

    def test_evidence_covers_eight_contracts(self):
        counts = {"0x4384": 1, "0x4650": 260, "0x4674": 260, "0x4698": 774,
                  "0x47b0": 480, "0x48e8": 896, "0x495c": 5125, "0x497c": 5125}
        self.assertEqual({ea: s["cases"] for ea, s in self.suites.items()}, counts)
        self.assertEqual(self.doc["total_calls"], 12921)
        self.assertTrue(all(s["mismatches"] == [] for s in self.suites.values()))

    def test_staged_normalization_changes_boundary(self):
        self.assertEqual(normalize(216), 5)
        self.assertEqual(index19(216), 0)
        self.assertEqual(19*216//4095, 1)
        observed = next(e for e in self.suites["0x497c"]["examples"] if e["input"] == 216)
        self.assertEqual(observed["r0"], 0)
        self.assertEqual((index19(4094), index19(4095), normalize(0xFFFFFFFF)), (18, 19, 100))

    def test_filter_drops_oldest_and_wraps_sum(self):
        shifted, average = mean32(list(range(32)), 32)
        self.assertEqual(shifted, list(range(1, 33)))
        self.assertEqual(average, 16)
        for entry in ("0x4650", "0x4674"):
            wide = next(e for e in self.suites[entry]["examples"] if e["new"] == 0xFFFFFFFF)
            self.assertEqual(wide["r0"], 0x07FFFFFF)
            self.assertEqual(mean32(wide["samples"], wide["new"]), (wide["shifted"], wide["r0"]))

    def test_threshold_result_is_not_boolean(self):
        self.assertEqual(threshold6(5, 0x66, 0), (5, [1, 0x66, 0]))
        self.assertEqual(threshold6(5, 0x66, 1), (1, [1, 0x66, 1]))
        self.assertEqual(threshold6(6, 0x66, 1), (0, [0, 1, 0]))
        observed = next(e for e in self.suites["0x4698"]["examples"] if e["input"] == 5 and e["initial_ad7_ad8"][1] == 0)
        self.assertEqual(observed["r0"], 5)

    def test_latch_persists_until_reset(self):
        first = latch_state(0, 121, 1, 0, 120, 15, [120, 0, 0, 0])
        self.assertEqual(first, (0, [120, 1, 0, 1]))
        self.assertEqual(latch_state(0, 0, 1, 0, 120, 15, first[1]), first)
        self.assertEqual(latch_state(1, 0, 1, 0, 80, 15, first[1]), (0, [80, 0, 0, 0]))
        observed = next(e for e in self.suites["0x47b0"]["examples"] if e["inputs"] == [0, 121, 1, 0, 120, 15, [120, 0, 0, 0]])
        self.assertEqual((observed["r0"], observed["state"]), first)

    def test_stale_ramp_does_not_clamp_and_fresh_gate_updates_previous(self):
        self.assertEqual(ramp_state(900, 7, 0, 0, 1, 0, 4, 5), (900, 900, 7, [4, 5, 0]))
        self.assertEqual(ramp_state(649, 0, 1199, 1, 1, 0, 4, 5), (650, 650, 1, [1, 1, 0]))
        self.assertEqual(ramp_state(649, 0, 1201, 1, 1, 0, 4, 5), (648, 648, 0xFFFFFFFF, [1, 1, 0]))
        self.assertEqual(ramp_state(649, 0, 1199, 1, 0, 0, 4, 5), (0, 0, 1, [1, 1, 0]))
        for e in self.suites["0x48e8"]["examples"]:
            actual = e["result"]
            expected = ramp_state(*e["inputs"], 0x55, 0x66)
            self.assertEqual(actual[:3], list(expected[:3]))
            self.assertEqual(actual[3], expected[3])

    def test_initializer_records_derived_words_and_no_stretch_table_write(self):
        writes = self.suites["0x4384"]["examples"][0]["writes"]
        self.assertEqual(len(writes), 103)
        by_address = {int(w["address"], 0): w["value"] for w in writes}
        self.assertEqual(by_address[0x200590], 1800)
        self.assertEqual([by_address[a] for a in range(0x200458, 0x200470, 4)], [1920, 2304, 2688, 2944, 3200, 256])
        self.assertFalse(any(int(w["address"], 0) < 0x20041A and int(w["address"], 0)+w["size"] > 0x200190 for w in writes))

    def test_roles_and_caller_evidence_are_complete_for_this_pass(self):
        reviews = json.loads((ROOT / "audit/data/control_function_reviews.json").read_text(encoding="utf-8"))
        self.assertEqual({e["entry"] for e in reviews["entries"]}, set(self.suites))
        for e in reviews["entries"]:
            for field in ("inputs", "outputs", "side_effects", "callers", "callees", "confidence", "limits"):
                self.assertIn(field, e)
        callers = json.loads((ROOT / "audit/data/control_helper_callers.json").read_text(encoding="utf-8"))
        self.assertEqual(len(callers["calls"]), 14)
        self.assertEqual(callers["raw_sha256"], self.doc["raw_sha256"])


if __name__ == "__main__":
    unittest.main()
