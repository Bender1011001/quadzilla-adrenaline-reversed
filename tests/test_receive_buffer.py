import json
import unittest

from tests._paths import ROOT  # noqa: F401
from model_receive_buffer import crc_status, overwrite_prefix
from x2com_crc import add_crc


class ReceiveBuffer(unittest.TestCase):
    def setUp(self):
        # Synthetic one-pair frame: CRC occupies index 3, total length 4.
        self.frame = add_crc(bytes([0x13, 5, 10]))
        self.old_region = self.frame + bytes(16-len(self.frame))

    def test_header_low_nibble_selects_crc_index(self):
        self.assertEqual(len(self.frame), (self.frame[0] & 15)+1)
        self.assertEqual(crc_status(self.old_region), 3)

    def test_retained_suffix_can_pass_crc_after_only_header_is_overwritten(self):
        region = overwrite_prefix(self.old_region, self.frame[:1])
        self.assertEqual(region, self.old_region)
        self.assertEqual(crc_status(region), 3)

    def test_changed_value_without_matching_crc_fails(self):
        region = overwrite_prefix(self.old_region, bytes([0x13, 5, 11]))
        self.assertEqual(crc_status(region), 4)

    def test_invalid_model_regions_rejected(self):
        with self.assertRaises(ValueError):
            overwrite_prefix(self.frame, b"X")
        with self.assertRaises(ValueError):
            crc_status(self.frame)

    def test_crc_length_and_status_are_anchored_in_instruction_export(self):
        doc = json.loads((ROOT / "audit/data/uart_buffer_binaryninja.json").read_text())
        row = next(r for r in doc["ranges"] if r["start"] == "0x7bcc")
        instructions = {i["address"]: "".join(i["text"].lower().split()) for i in row["instructions"]}
        self.assertEqual(instructions["0x7bce"], "addsr1,r1,#1")
        self.assertEqual(instructions["0x7bd8"], "cmpr0,#0x3b")
        self.assertEqual(instructions["0x7be0"], "movsr0,#3")


if __name__ == "__main__":
    unittest.main()
