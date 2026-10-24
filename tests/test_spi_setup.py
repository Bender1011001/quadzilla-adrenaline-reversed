"""Pin bounded SPI setup evidence without requiring vendor bytes or Unicorn in CI."""
import json
import unittest

from tests._paths import ROOT


def load(name):
    return json.loads((ROOT / "audit/data" / name).read_text(encoding="utf-8"))


class SpiSetup(unittest.TestCase):
    def test_decode_and_literal_sources(self):
        emu, bn = load("spi_setup_emulation.json"), load("spi_setup_binaryninja.json")
        self.assertEqual(emu["raw_sha256"], bn["raw_sha256"])
        self.assertEqual([(r["start"], r["end"]) for r in bn["ranges"]],
                         [("0x6b44", "0x6b46"), ("0x6bd8", "0x6c14")])
        self.assertEqual(sum(sum(i["length"] for i in r["instructions"]) for r in bn["ranges"]), 62)
        self.assertTrue(all("decode_stopped_at" not in r for r in bn["ranges"]))
        self.assertEqual(emu["literal_words"]["0x6c30"], "0x6b45")
        self.assertEqual(emu["literal_words"]["0x6c3c"], "0xfffe0018")

    def test_ordered_writes_and_noop_vector(self):
        cases = load("spi_setup_emulation.json")["cases"]
        self.assertEqual(cases[0]["writes"], cases[1]["writes"])
        self.assertEqual(cases[0]["reads"], cases[1]["reads"])
        self.assertEqual(cases[0]["reads"],
                         [{"site": "0x6bf0", "address": "0xfffff094", "size": 4}])
        self.assertEqual([(w["address"], w["value"]) for w in cases[0]["writes"]], [
            ("0xfffffc10", "0x20"), ("0xfffe0004", "0x1"),
            ("0xfffe0030", "0x3002"), ("0xfffe0000", "0x1"),
            ("0xfffff124", "0x20"), ("0xfffff094", "0x6b45"),
            ("0xfffff014", "0x21"), ("0xfffff128", "0x20"),
            ("0xfffe0018", "0xfff"), ("0xfffff120", "0x20"),
            ("0xfffe0014", "0x1")])
        self.assertEqual(cases[2]["visited"], ["0x6b44"])
        self.assertEqual(cases[2]["writes"], [])


if __name__ == "__main__":
    unittest.main()
