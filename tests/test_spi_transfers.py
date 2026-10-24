"""Check source-bound SPI/PDC primitive evidence without requiring a device."""
import json
import unittest

from tests._paths import ROOT


def load(name):
    return json.loads((ROOT / "audit/data" / name).read_text(encoding="utf-8"))


def pairs(rows):
    return [(w["address"], w["value"]) for w in rows]


class SpiTransfers(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.emu = load("spi_transfer_emulation.json")
        cls.bn = load("spi_transfer_binaryninja.json")

    def test_source_and_bounded_execution_coverage(self):
        self.assertEqual(self.emu["raw_sha256"], self.bn["raw_sha256"])
        self.assertEqual(self.emu["raw_sha256"], load("semantic_labels.json")["raw_sha256"])
        instructions = [i for r in self.bn["ranges"] for i in r["instructions"]]
        self.assertEqual(sum(i["length"] for i in instructions), 186)
        self.assertEqual(len(instructions), 91)
        self.assertEqual(len(self.emu["cases"]), 27)
        self.assertEqual({i["address"] for i in instructions},
                         {a for c in self.emu["cases"] for a in c["visited"]})
        self.assertTrue(all(c["callee_saved_r4_r7_preserved"] for c in self.emu["cases"]))
        self.assertEqual(self.emu["literal_words"],
                         {"0x5738": "0xfffff434", "0x5758": "0xfffff430",
                          "0x6b60": "0xfffff43c", "0x6bd4": "0xfffe0008"})

    def test_selector_masks_and_unsupported_values(self):
        for entry, target in (("0x571c", "0xfffff434"), ("0x573c", "0xfffff430")):
            cases = [c for c in self.emu["cases"] if c["entry"] == entry]
            self.assertEqual([pairs(c["writes"]) for c in cases],
                             [[], [(target, "0x100")], [(target, "0x200")], []])

    def test_readiness_and_pdc_write_order(self):
        for case in self.emu["cases"]:
            if case["entry"] not in ("0x6b48", "0x6b64", "0x6b9c"):
                continue
            ready = bool(int(case["synthetic_spi_sr"], 0) & 0x20 and
                         int(case["synthetic_pio_pdsr"], 0) & 0x800)
            self.assertEqual(case["return_r0"], hex(int(ready)))
            if not ready or case["entry"] == "0x6b48":
                self.assertEqual(case["writes"], [])
                continue
            args = case["args"]
            expected = [("0xfffe0120", "0x100"), ("0xfffe0108", args[1]),
                        ("0xfffe010c", args[2])] if case["entry"] == "0x6b64" else [
                            ("0xfffe0120", "0x0"), ("0xfffe0108", args[2]),
                            ("0xfffe010c", args[3]), ("0xfffe0100", args[1]),
                            ("0xfffe0104", args[3]), ("0xfffe0120", "0x101")]
            self.assertEqual(pairs(case["writes"]), expected)
            if case["entry"] == "0x6b9c":
                self.assertIn("0xfffe0008", [r["address"] for r in case["reads"]])

    def test_endrx_predicate_and_raw_count_edges(self):
        for case in self.emu["cases"]:
            if case["entry"] == "0x6b8c":
                self.assertEqual(case["return_r0"], hex(int(bool(int(case["synthetic_spi_sr"], 0) & 0x10))))
        edges = [c for c in self.emu["cases"] if c["entry"] in ("0x6b64", "0x6b9c")
                 and c["args"][-1] in ("0x0", "0xffffffff")]
        self.assertEqual(len(edges), 4)
        self.assertTrue(all(c["return_r0"] == "0x1" for c in edges))

    def test_ida_overlap_is_explicitly_adjudicated(self):
        ida = load("ida_image_items.json")
        overlap = next(i for i in ida["items"] if i["start"] == "0x6b46")
        self.assertEqual(overlap["end"], "0x6b4a")
        self.assertEqual(overlap["mnemonic"], "VTBL.8")
        first = next(r for r in self.bn["ranges"] if r["start"] == "0x6b48")["instructions"][0]
        self.assertEqual((first["address"], first["length"]), ("0x6b48", 2))
        self.assertTrue(first["text"].startswith("ldr"))


if __name__ == "__main__":
    unittest.main()
