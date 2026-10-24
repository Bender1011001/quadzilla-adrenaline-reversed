"""Pin exact-image timer evidence without needing Binary Ninja or Unicorn in CI."""
import json
import unittest

from tests._paths import ROOT


def load(name):
    return json.loads((ROOT / "audit/data" / name).read_text(encoding="utf-8"))


class TimerSetup(unittest.TestCase):
    def test_decoder_bounds_and_source_pointers(self):
        emu, bn = load("timer_setup_emulation.json"), load("timer_setup_binaryninja.json")
        self.assertEqual(emu["raw_sha256"], bn["raw_sha256"])
        self.assertEqual([(r["start"], r["end"]) for r in bn["ranges"]],
                         [("0x6c48", "0x6c5e"), ("0x6c68", "0x6c82"),
                          ("0x6fb4", "0x70ca")])
        self.assertEqual(sum(sum(i["length"] for i in r["instructions"]) for r in bn["ranges"]), 326)
        self.assertTrue(all("decode_stopped_at" not in r for r in bn["ranges"]))
        self.assertEqual([int(x["value"], 0) for x in emu["source_pointers"].values()],
                         [0xFFFA00C0, 0xFFFA00C4, 0xFFFA0000, 0xFFFA0040, 0xFFFA0080])

    def test_setup_conditional_compare_and_vectors(self):
        cases = load("timer_setup_emulation.json")["cases"]
        self.assertEqual([len(c["writes"]) for c in cases], [41, 36])
        active = [(w["address"], w["value"]) for w in cases[0]["writes"]]
        running = [(w["address"], w["value"]) for w in cases[1]["writes"]]
        self.assertEqual([w for w in active if w not in running],
                         [("0xfffa0014", "0x3"), ("0xfffa001c", "0x1b"),
                          ("0xfffa0054", "0x3"), ("0xfffa005c", "0x1b"),
                          ("0xfffa009c", "0x963")])
        self.assertIn(("0xfffff0b0", "0x6c49"), active)
        self.assertIn(("0xfffff0b4", "0x6c69"), active)
        self.assertIn(("0xfffff0b8", "0x6c95"), active)
        self.assertEqual(active[-3:], [("0x200748", "0x0"), ("0x20074c", "0x0"),
                                       ("0x20073c", "0x0")])

    def test_short_callback_branches(self):
        callbacks = load("timer_setup_emulation.json")["callbacks"]
        self.assertEqual([c["entry"] for c in callbacks], ["0x6c48", "0x6c68", "0x6c68"])
        self.assertEqual([(w["address"], w["value"]) for w in callbacks[0]["writes"]],
                         [("0xfffa0000", "0x2"), ("0x200726", "0x1"),
                          ("0x200727", "0x0"), ("0x200725", "0x1")])
        self.assertEqual([(w["address"], w["value"]) for w in callbacks[1]["writes"]],
                         [("0xfffa0040", "0x2"), ("0xfffa005c", "0x2583")])
        self.assertEqual([(w["address"], w["value"]) for w in callbacks[2]["writes"]],
                         [("0xfffa0040", "0x2")])


if __name__ == "__main__":
    unittest.main()
