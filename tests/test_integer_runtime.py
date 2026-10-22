"""Check committed execution evidence and exceptional arithmetic contracts.

The standard suite does not redistribute or re-execute vendor firmware. See the
audit emulation scripts to reproduce the original-image execution separately.
"""
import importlib.util
import json
import unittest

from tests._paths import ROOT
from model_stretch_arithmetic import applied_value

spec = importlib.util.spec_from_file_location("integer_emulation", ROOT / "audit/tools/emulate_integer_runtime.py")
integer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(integer)


def load(name):
    return json.loads((ROOT / "audit/data" / name).read_text(encoding="utf-8"))


class IntegerRuntime(unittest.TestCase):
    def test_execution_report_covers_byte_domain_and_six_entries(self):
        doc = load("integer_runtime_emulation.json")
        self.assertEqual(doc["raw_sha256"], integer.SHA)
        suites = {s["entry"]: s for s in doc["suites"]}
        self.assertEqual(set(suites), {"0x8564", "0x8568", "0x8574", "0x8578", "0x8584", "0x8588"})
        self.assertEqual(suites["0x8564"]["cases"], 65536)
        self.assertEqual(sum(s["cases"] for s in suites.values()), 87141)
        for suite in suites.values():
            self.assertEqual(suite["mismatches"], [])
            self.assertTrue(all(0x8564 <= int(ea, 0) < 0x8678 for ea in suite["visited_addresses"]))

    def test_return_registers_are_anchored_in_executed_example(self):
        suite = next(s for s in load("integer_runtime_emulation.json")["suites"] if s["entry"] == "0x8574")
        example = next(e for e in suite["examples"] if e["inputs"] == [100, 3])
        self.assertEqual((example["r0_remainder"], example["r1_quotient"]), (1, 33))

    def test_signed_zero_and_overflow_contract(self):
        self.assertEqual(integer.reference("s32", 0xFFFFFFF9, 3), (0xFFFFFFFF, 0xFFFFFFFE))
        self.assertEqual(integer.reference("s32", 0xFFFFFFF9, 0), (7, 0))
        self.assertEqual(integer.reference("s32", 0x80000000, 0xFFFFFFFF), (0, 0x80000000))
        suite = next(s for s in load("integer_runtime_emulation.json")["suites"] if s["entry"] == "0x8584")
        example = next(e for e in suite["examples"] if e["inputs"] == [0xFFFFFFF9, 0])
        self.assertEqual((example["r0_remainder"], example["r1_quotient"]), (7, 0))

    def test_stretch_execution_evidence_is_bounded(self):
        doc = load("stretch_arithmetic_emulation.json")
        self.assertEqual(doc["raw_sha256"], integer.SHA)
        self.assertEqual((doc["cases"], doc["mismatches"]), (2092, []))
        normal = next(e for e in doc["examples"] if e["fields"]["table_byte"] == 100 and e["fields"]["percent"] == 100)
        high_bit = next(e for e in doc["examples"] if e["fields"]["table_byte"] == 140 and e["fields"]["percent"] == 100)
        self.assertEqual(normal["actual_r0"], 1700)
        self.assertEqual(high_bit["actual_r0"], 42947700)

    def test_two_percentage_stages_round_separately(self):
        fields = dict(step=0, residue=0, captured=99, minimum=0, low=0, high=100,
                      requested=1019, table_byte=1, percent=100)
        self.assertEqual(applied_value(**fields), 9)
        example = next(e for e in load("stretch_arithmetic_emulation.json")["examples"] if e["fields"] == fields)
        self.assertEqual(example["actual_r0"], 9)
        self.assertEqual((1*1019*99)//10000, 10)  # collapsing stages would change behavior

    def test_control_caller_uses_remainder_for_periodic_gate(self):
        calls = load("integer_division_callers.json")["calls"]
        site = next(c for c in calls if c["site"] == "0x5226")
        context = {i["address"]: i["text"] for i in site["context"]}
        self.assertIn("R0, #0", context["0x522a"])
        self.assertEqual(site["target"], "0x8584")


if __name__ == "__main__":
    unittest.main()
