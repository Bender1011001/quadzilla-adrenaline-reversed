"""Verify offline MCP2515-compatible layouts and source-bound firmware commands."""
import json
import random
import unittest

from tests._paths import ROOT
from mcp2515_protocol import decode_command, decode_identifier


def load():
    return json.loads((ROOT / "audit/data/spi_can_command_audit.json").read_text(encoding="utf-8"))


class SpiCanCommands(unittest.TestCase):
    def test_standard_identifier_bit_placement(self):
        for identifier in range(2048):
            header = bytes((identifier//8, (identifier % 8)*32, 0xAA, 0x55))
            self.assertEqual(decode_identifier(header), {"extended": False, "identifier": hex(identifier)})

    def test_extended_identifier_bit_placement(self):
        rng = random.Random(0x2515)
        identifiers = [0, 0x1FFFFFFF, 0x0CEA00F8] + [1 << i for i in range(29)]
        identifiers += [rng.randrange(1 << 29) for _ in range(512)]
        for identifier in identifiers:
            header = bytes(((identifier >> 21) & 255,
                            ((identifier >> 18) & 7)*32 | 8 | ((identifier >> 16) & 3),
                            (identifier >> 8) & 255, identifier & 255))
            self.assertEqual(decode_identifier(header), {"extended": True, "identifier": hex(identifier)})
        self.assertEqual(decode_identifier(bytes.fromhex("674a00f8"))["identifier"], "0xcea00f8")

    def test_command_buffer_selectors_and_malformed_probes(self):
        for selector, address in enumerate((0x31, 0x36, 0x41, 0x46, 0x51, 0x56)):
            decoded = decode_command(bytes((0x40+selector,)))
            self.assertEqual(decoded["register_start"], hex(address))
            self.assertEqual(decoded["buffer"], selector//2)
        for opcode, address in ((0x90, 0x61), (0x92, 0x66), (0x94, 0x71), (0x96, 0x76)):
            self.assertEqual(decode_command(bytes((opcode, 0)))["register_start"], hex(address))
        for malformed in (b"", b"\x02", b"\x03\x0f", b"\x05\x2c", b"\x46", b"\xc0\x00"):
            with self.subTest(malformed=malformed), self.assertRaises(ValueError):
                decode_command(malformed)
        with self.assertRaises(ValueError):
            decode_identifier(b"\x00")
        incomplete = decode_command(bytes.fromhex("40674a00f803eefe"))
        self.assertFalse(incomplete["frame"]["complete_data"])

    def test_all_initialized_commands_reproduce_the_audit(self):
        doc = load()
        source = json.loads((ROOT / "audit/data/spi_initialization_emulation.json").read_text(encoding="utf-8"))
        self.assertEqual(doc["raw_sha256"], source["raw_sha256"])
        self.assertFalse(doc["physical_part_verified"])
        self.assertEqual(len(doc["initialization"]), 24)
        for row in doc["initialization"]:
            self.assertEqual(decode_command(bytes.fromhex(row["command_hex"])), row["decoded"])
            pointer = int(row["pointer"], 0)
            expected = 0x96E8+pointer-0x200000 if pointer >= 0x200000 else pointer
            self.assertEqual(int(row["image_source"], 0), expected)

    def test_request_table_frames(self):
        records = load()["request_records"]
        self.assertEqual(len(records), 7)
        self.assertEqual([r["decoded"]["frame"]["data"] for r in records],
                         ["eefe00", "03f000", "f7fe00", "effe00", "f1fe00", "f5fe00", "f6fe00"])
        for i, row in enumerate(records):
            self.assertEqual(row["pointer"], hex(0x9FF0+9*i))
            frame = row["decoded"]["frame"]
            self.assertEqual((frame["identifier"], frame["extended"], frame["dlc"]), ("0xcea00f8", True, 3))
            self.assertTrue(frame["complete_data"])

    def test_capture_output_layout_and_explicit_tx2_configuration(self):
        doc = load()
        templates = doc["capture_output_templates"]
        self.assertEqual((templates["capture_rx0"]["decoded"]["buffer"],
                          templates["capture_rx0"]["decoded"]["start"],
                          templates["capture_rx0"]["decoded"]["response_bytes_after_opcode"]), (0, "data", 8))
        self.assertEqual((templates["capture_rx1"]["decoded"]["buffer"],
                          templates["capture_rx1"]["decoded"]["start"],
                          templates["capture_rx1"]["decoded"]["response_bytes_after_opcode"]), (1, "identifier", 13))
        self.assertEqual((templates["output_tx2"]["decoded"]["buffer"],
                          templates["output_tx2"]["decoded"]["start"]), (2, "data"))
        self.assertEqual(doc["explicit_tx2_configuration"]["identifier"], "0x100")
        self.assertFalse(doc["explicit_tx2_configuration"]["extended"])
        self.assertEqual(doc["explicit_tx2_configuration"]["dlc_register"], "0x8")


if __name__ == "__main__":
    unittest.main()
