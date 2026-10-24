"""Pin source-bound numeric findings without requiring licensed tools in CI."""
import json
import unittest
from fractions import Fraction

from tests._paths import ROOT
from model_soft_float import binary, encode


def load(name):
    return json.loads((ROOT / "audit/data" / name).read_text(encoding="utf-8"))


class SoftFloatReview(unittest.TestCase):
    def test_exact_reference_rounding_and_division_case(self):
        self.assertEqual(encode(Fraction(1, 1 << 149), 32), 1)
        self.assertEqual(encode(Fraction(1, 1 << 126), 32), 0x800000)
        self.assertEqual(binary("div", 0x800000, 1, 32), 0x4b000000)

    def test_original_byte_execution_records_exceptional_results(self):
        doc = load("soft_float_emulation.json")
        self.assertEqual(doc["total_calls"], 30627)
        self.assertEqual(len(doc["suites"]), 35)
        self.assertFalse(doc["all_reference_comparisons_match"])
        suite = next(s for s in doc["suites"] if s["entry"] == "0x92cc")
        self.assertEqual(suite["mismatch_count"], 32)
        self.assertIn({"inputs": [0x800000, 1], "actual": "0x35000000", "expected": "0x4b000000"}, suite["mismatches"])
        probes = doc["caller_r4_influence"]
        self.assertEqual(len(probes), 5)
        self.assertEqual(len({p["output_bits"] for p in probes}), 5)
        self.assertEqual({p["reference_bits"] for p in probes}, {"0x10000000000001"})

    def test_decoder_gaps_and_review_boundary_remain_visible(self):
        ida = load("soft_float_ida.json")
        bn = load("soft_float_binaryninja.json")
        reviews = load("soft_float_function_reviews.json")
        sha = load("soft_float_emulation.json")["raw_sha256"]
        self.assertTrue(ida["database_bytes_match"])
        self.assertEqual(len(ida["decode_gaps"]), 281)
        self.assertEqual({ida["raw_sha256"], bn["raw_sha256"], reviews["raw_sha256"]}, {sha})
        self.assertEqual(len(reviews["entries"]), 40)
        self.assertEqual(sum(int(r["end"], 0)-int(r["start"], 0) for r in bn["ranges"]), 4256)
        self.assertTrue(all(r["contract"] and r["evidence"] and r["limits"] for r in reviews["entries"]))


if __name__ == "__main__":
    unittest.main()
