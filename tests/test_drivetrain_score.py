"""Pin table layout and observed byte narrowing in original-byte evidence."""
import json
import unittest

from tests._paths import ROOT


class DrivetrainScore(unittest.TestCase):
    def test_table_and_reproduced_byte_narrowing(self):
        emu = json.loads((ROOT / "audit/data/drivetrain_score_emulation.json").read_text())
        decode = json.loads((ROOT / "audit/data/drivetrain_score_binaryninja.json").read_text())
        self.assertEqual(emu["raw_sha256"], decode["raw_sha256"])
        self.assertEqual([r["count"] for r in emu["transmission_rows"]], [4, 5, 6])
        self.assertEqual(emu["startup_default"]["bytes"], "00043333bf42")
        self.assertEqual(len(emu["axle_ratio_bits"]), 5)
        self.assertEqual(decode["ranges"][0]["start"], "0x46d0")
        self.assertEqual(decode["ranges"][0]["end"], "0x4790")
        samples = {(s["word_input"], s["byte_input"]): s for s in emu["cases"]}
        self.assertEqual((samples[1200, 0]["return_score"], samples[1200, 0]["selection_byte_200bd0"]), (100, 242))
        case = samples[1200, 5]
        self.assertEqual((case["return_score"], case["selection_byte_200bd0"]), (0, 3))
        self.assertEqual([(c["converted_s32"], c["stored_byte"]) for c in case["candidates"]],
                         [(149, 149), (322, 66), (512, 0), (787, 19)])
        self.assertEqual(sum(x["length"] for x in decode["ranges"][0]["instructions"]), 192)


if __name__ == "__main__":
    unittest.main()
