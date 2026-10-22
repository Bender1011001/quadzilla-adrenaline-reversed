"""Reject damaged firmware before any output is created."""
import argparse
import importlib.util
import tempfile
import unittest
from pathlib import Path

from tests._paths import ROOT
import firmware_crypto as fc


def record(address, kind, data=b""):
    body = bytes([len(data), address >> 8, address & 255, kind]) + data
    return ":" + (body + bytes([-sum(body) & 255])).hex().upper() + "\n"


class FirmwareValidation(unittest.TestCase):
    def test_truncated_record_with_balanced_checksum_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "length"):
            fc.parse_ihex(":10400000B0\n")

    def test_nonrecord_text_is_rejected(self):
        with self.assertRaises(ValueError):
            fc.parse_ihex("garbage\n" + record(0x4000, 0, b"A"))

    def test_checksum_failure_does_not_contribute_bytes(self):
        valid = record(0x4000, 0, b"A")
        broken = valid[:-3] + "00\n"
        memory, count, bad = fc.parse_ihex(broken)
        self.assertEqual((memory, count, bad), ({}, 1, 1))

    def test_eof_is_optional_but_must_be_last(self):
        text = record(0x4000, 0, b"A")
        self.assertEqual(fc.parse_ihex(text)[0], {0x4000: 65})
        with self.assertRaisesRegex(ValueError, "after EOF"):
            fc.parse_ihex(text + record(0, 1) + text)

    def test_segment_and_linear_address_records(self):
        for kind, data, expected in [(2, b"\x12\x34", 0x12341), (4, b"\x00\x02", 0x20001)]:
            self.assertEqual(fc.parse_ihex(record(0, kind, data) + record(1, 0, b"X"))[0], {expected: 88})

    def test_invalid_type_or_control_length_rejected(self):
        for text in [record(0, 6), record(0, 4, b"X"), record(1, 1)]:
            with self.subTest(text=text), self.assertRaises(ValueError):
                fc.parse_ihex(text)

    def test_overlapping_records_rejected(self):
        with self.assertRaisesRegex(ValueError, "overlapping"):
            fc.parse_ihex(record(0x4000, 0, b"A") * 2)

    def test_address_boundary_rejected(self):
        with self.assertRaisesRegex(ValueError, "boundary"):
            fc.parse_ihex(record(0xFFFF, 0, b"AB"))

    def test_sparse_image_cannot_allocate_gigabytes(self):
        with self.assertRaisesRegex(ValueError, "16 MiB"):
            fc.ihex_to_image({0: 1, 0xFFFFFFFF: 2})

    def test_damaged_decrypt_creates_neither_output(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            source, output, binary = root / "bad.qz", root / "out.hex", root / "out.bin"
            key = bytes(8)
            source.write_bytes(fc.encrypt_chain(b":10400000B0\n", key))
            args = argparse.Namespace(input=str(source), output=str(output), bin=str(binary),
                                      key=key.hex(), pwk_file=None, pwd_file=None)
            with self.assertRaises(ValueError):
                fc.cmd_decrypt(args)
            self.assertFalse(output.exists())
            self.assertFalse(binary.exists())

    def test_encrypt_rejects_bad_checksum_before_output(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            source, output = root / "bad.hex", root / "out.qz"
            source.write_bytes(b":014000004100\n")
            args = argparse.Namespace(input=str(source), output=str(output), key=bytes(8).hex(),
                                      pwk_file=None, pwd_file=None)
            with self.assertRaises(ValueError):
                fc.cmd_encrypt(args)
            self.assertFalse(output.exists())

    def test_two_tools_cannot_override_known_table_data(self):
        spec = importlib.util.spec_from_file_location("reconcile", ROOT / "audit/tools/compare_quadzilla_disassemblers.py")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        doc = {"image_range": ["0x4000", "0xbd00"], "functions": [
            {"start": "0xae82", "end": "0xae88"}], "calls": []}
        result = module.adjudicate_entries(doc, doc, bytes(32000))
        self.assertEqual(result["confirmed"], 0)
        self.assertEqual(result["rejected_partitions"], 1)


if __name__ == "__main__":
    unittest.main()
