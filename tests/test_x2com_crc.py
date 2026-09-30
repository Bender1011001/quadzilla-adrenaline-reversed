import unittest

from tests._paths import ROOT  # noqa: F401
import x2com_crc as x


class Crc8J1850(unittest.TestCase):
    def test_catalogue_check_value(self):
        # CRC-8/SAE-J1850 check value for the ASCII string "123456789".
        self.assertEqual(x.crc8(b"123456789"), 0x4B)

    def test_valid_frame_residue(self):
        for frame in (b"\x41\x05\x10\x22", b"\x00", b"\x5E" + bytes(range(13))):
            self.assertTrue(x.check_frame(x.add_crc(frame)), frame.hex())

    def test_single_bit_errors_detected(self):
        good = x.add_crc(b"\x41\x05\x10\x22\x07")
        for i in range(len(good)):
            for bit in range(8):
                bad = bytearray(good)
                bad[i] ^= 1 << bit
                self.assertFalse(x.check_frame(bytes(bad)))

    def test_header_nibbles(self):
        self.assertEqual(x.parse_header(0x4A), ("REQ", 10))
        self.assertEqual(x.parse_header(0x00), ("CWA", 0))


if __name__ == "__main__":
    unittest.main()
