"""Pin exact-image flag helper effects without local Binary Ninja or Unicorn."""
import json
import unittest

from tests._paths import ROOT


def load(name):
    return json.loads((ROOT / "audit/data" / name).read_text(encoding="utf-8"))


class Tc2FlagHelpers(unittest.TestCase):
    def test_decode_and_pointers(self):
        emu, bn = load("tc2_flag_helper_emulation.json"), load("tc2_flag_helper_binaryninja.json")
        self.assertEqual(emu["raw_sha256"], bn["raw_sha256"])
        self.assertEqual([(r["start"], r["end"]) for r in bn["ranges"]],
                         [("0x7f28", "0x7f40"), ("0x7f40", "0x7f58")])
        self.assertEqual(sum(sum(i["length"] for i in r["instructions"]) for r in bn["ranges"]), 48)
        self.assertTrue(all("decode_stopped_at" not in r for r in bn["ranges"]))
        self.assertEqual(emu["literal_pointers"], {"0x81a4": "0x2007c8", "0x8034": "0x2007c8"})

    def test_both_gate_outcomes(self):
        cases = load("tc2_flag_helper_emulation.json")["cases"]
        self.assertEqual([(c["entry"], c["gate"]) for c in cases],
                         [("0x7f28", 0), ("0x7f28", 1),
                          ("0x7f40", 0), ("0x7f40", 1)])
        actual = [[(w["address"], w["value"]) for w in c["writes"]] for c in cases]
        self.assertEqual(actual, [
            [("0x2007ca", "0x1"), ("0x2007df", "0x0")],
            [("0x2007ca", "0x1"), ("0x2007df", "0x0"),
             ("0x2007c8", "0x1"), ("0x2007de", "0x0")],
            [("0x2007cb", "0x1"), ("0x2007da", "0x0")],
            [("0x2007cb", "0x1"), ("0x2007da", "0x0"),
             ("0x2007c9", "0x1"), ("0x2007d9", "0x0")]])


if __name__ == "__main__":
    unittest.main()
