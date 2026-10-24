"""Pin bounded original-byte PIO/AIC evidence without requiring Unicorn in CI."""
import json
import unittest

from tests._paths import ROOT


def load(name):
    return json.loads((ROOT / "audit/data" / name).read_text(encoding="utf-8"))


class PioInterrupt(unittest.TestCase):
    def test_bounded_decodes_and_source_identity(self):
        emu, bn = load("pio_interrupt_emulation.json"), load("pio_interrupt_binaryninja.json")
        self.assertEqual(emu["raw_sha256"], bn["raw_sha256"])
        self.assertEqual(emu["source_literals"],
                         {"aic_base_source": "0x9e80", "aic_base": "0xfffff000",
                          "thumb_vector_literal": "0x75dc", "thumb_vector": "0x7449"})
        self.assertEqual([(r["start"], r["end"]) for r in bn["ranges"]],
                         [("0x7448", "0x7486"), ("0x7498", "0x74b2"),
                          ("0x74b4", "0x74c2"), ("0x74e8", "0x7598")])
        self.assertEqual(sum(sum(i["length"] for i in r["instructions"]) for r in bn["ranges"]), 278)
        self.assertTrue(all("decode_stopped_at" not in r for r in bn["ranges"]))

    def test_initializer_write_order_and_pin17_sample(self):
        cases = load("pio_interrupt_emulation.json")["initialization_prefix"]
        self.assertEqual([r["ram_200791"] for r in cases], [1, 0])
        self.assertEqual(cases[0]["mmio_writes"], cases[1]["mmio_writes"])
        writes = [(w["address"], w["value"]) for w in cases[0]["mmio_writes"]]
        self.assertEqual(len(writes), 23)
        self.assertEqual(writes[:3], [("0xfffff124", "0xffffffff"),
                                      ("0xfffffc14", "0xffffffff"),
                                      ("0xfffffc10", "0x4")])
        self.assertIn(("0xfffff088", "0x7449"), writes)
        self.assertEqual(writes[-2:], [("0xfffff440", "0x40000000"),
                                       ("0xfffff120", "0x4")])
        self.assertTrue(all(int(a, 0) < 0x757a for r in cases for a in r["visited"]))

    def test_handler_branches_and_aic_mask_pair(self):
        emu = load("pio_interrupt_emulation.json")
        cases = emu["pio_handler"]
        self.assertEqual([len(r["mmio_writes"]) for r in cases], [0, 0, 3, 4])
        self.assertEqual([(w["address"], w["value"]) for w in cases[2]["mmio_writes"]],
                         [("0xfffa0000", "0x5"), ("0xfffff124", "0x4"),
                          ("0xfffff128", "0x4")])
        self.assertEqual(cases[3]["mmio_writes"][0]["address"], "0xfffa0040")
        mask = emu["aic_mask_helpers"]
        self.assertEqual(mask["saved_ram_20079c"], mask["synthetic_aic_imr"])
        self.assertEqual(mask["restore_writes"],
                         [{"site": "0x74be", "address": "0xfffff120", "size": 4,
                           "value": "0x12345678"}])


if __name__ == "__main__":
    unittest.main()
