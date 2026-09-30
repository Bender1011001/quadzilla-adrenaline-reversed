import importlib.util
import unittest

from tests._paths import ROOT  # noqa: F401  (sets sys.path)
import firmware_crypto as fc

# Password/key pair recovered from the vendor installer (see analysis/decrypt_results.txt).
PASSWORD = bytes.fromhex("3d211c362a1e514e")
DERIVED_KEY = bytes.fromhex("111d6f202ee5a103")


def _synthetic_hex(n_records: int = 64) -> bytes:
    lines = []
    for i in range(n_records):
        body = bytes([0x10, (0x4000 + i * 16) >> 8 & 0xFF, (0x4000 + i * 16) & 0xFF, 0x00]) + bytes((i * 7 + j) & 0xFF for j in range(16))
        lines.append(":" + (body + bytes([(-sum(body)) & 0xFF])).hex().upper())
    return ("\r\n".join(lines) + "\r\n").encode("ascii")


class KeyDerivation(unittest.TestCase):
    def test_published_vector(self):
        self.assertEqual(fc.generate_password_key(PASSWORD), DERIVED_KEY)

    def test_table_matches_vendor_table(self):
        spec = importlib.util.spec_from_file_location("df", ROOT / "analysis" / "decrypt_firmware.py")
        vendor = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(vendor)
        self.assertEqual(fc.E_TABLE, vendor.E_TABLE)

    def test_table_is_aes_te0(self):
        self.assertEqual(len(fc.E_TABLE), 256)
        self.assertEqual(fc.E_TABLE[0], 0xC66363A5)
        self.assertEqual(fc.E_TABLE[1], 0xF87C7C84)

    def test_wrong_length_rejected(self):
        with self.assertRaises(ValueError):
            fc.generate_password_key(PASSWORD[:4])


class Cipher(unittest.TestCase):
    def test_roundtrip(self):
        plain = _synthetic_hex()
        self.assertEqual(fc.decrypt_chain(fc.encrypt_chain(plain, DERIVED_KEY), DERIVED_KEY), plain)

    def test_chain_propagates_errors(self):
        # Ciphertext feedback: flipping one ciphertext byte garbles exactly two plaintext bytes.
        plain = _synthetic_hex()
        ct = bytearray(fc.encrypt_chain(plain, DERIVED_KEY))
        ct[100] ^= 0x01
        damaged = fc.decrypt_chain(bytes(ct), DERIVED_KEY)
        self.assertEqual([i for i in range(len(plain)) if plain[i] != damaged[i]], [100, 101])

    def test_short_key_rejected_not_padded(self):
        with self.assertRaises(ValueError):
            fc.decrypt_chain(b"abc", DERIVED_KEY[:4])

    def test_known_plaintext_key_recovery(self):
        ct = fc.encrypt_chain(_synthetic_hex(), DERIVED_KEY)
        self.assertEqual(fc.recover_key_known_plaintext(ct), DERIVED_KEY)


class IntelHex(unittest.TestCase):
    def test_parse_and_image(self):
        memory, records, bad = fc.parse_ihex(_synthetic_hex(4).decode())
        self.assertEqual((records, bad), (4, 0))
        base, image = fc.ihex_to_image(memory)
        self.assertEqual((base, len(image)), (0x4000, 64))

    def test_checksum_error_detected(self):
        text = _synthetic_hex(2).decode().replace(":10400000", ":10400001", 1)
        _, records, bad = fc.parse_ihex(text)
        self.assertEqual((records, bad), (2, 1))


if __name__ == "__main__":
    unittest.main()
