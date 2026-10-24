"""Check source-bound capture paths, ignored DLC and numeric boundary evidence."""
import json
import unittest

from tests._paths import ROOT


def load(name):
    return json.loads((ROOT / "audit/data" / name).read_text(encoding="utf-8"))


class CaptureParser(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.emu = load("capture_parser_emulation.json")
        cls.bn = load("capture_parser_binaryninja.json")
        cls.cases = cls.emu["cases"]

    def test_source_and_boundaries(self):
        self.assertEqual(self.emu["raw_sha256"], self.bn["raw_sha256"])
        self.assertEqual(self.emu["raw_sha256"], load("semantic_labels.json")["raw_sha256"])
        ins = [i for r in self.bn["ranges"] for i in r["instructions"]]
        self.assertEqual((len(ins), sum(i["length"] for i in ins)), (315, 692))
        ida = {i["start"]: i for i in load("ida_image_items.json")["items"]}
        for i in ins:
            self.assertEqual(int(ida[i["address"]]["end"], 0), int(i["address"], 0)+i["length"])
        self.assertLessEqual({i["address"] for i in ins}, set(self.emu["visited"]))
        self.assertEqual(len(self.emu["visited"]), 329)
        self.assertEqual(len(self.cases), 303)
        self.assertEqual(sum(s["cases"] for s in self.emu["sweeps"]), 5120)
        self.assertEqual(self.emu["reference_mismatches"], [])

    def test_dlc_is_unread_and_does_not_gate_outputs(self):
        rows = [c for c in self.cases if c["name"].startswith("pattern_")]
        self.assertEqual(len(rows), 120)
        paired = {}
        for c in rows:
            frame = bytearray.fromhex(c["inputs"]["frame"])
            dlc = frame[5]
            frame[5] = 0
            key = (c["name"], bytes(frame), str(c["inputs"]["changes"]))
            paired.setdefault(key, {})[dlc] = c
            self.assertNotIn(5, c["rx1_offsets_read"])
            self.assertEqual(c["state_out"], 1)
        self.assertEqual(len(paired), 60)
        for pair in paired.values():
            self.assertEqual(set(pair), {0, 8})
            self.assertEqual(pair[0]["outputs"], pair[8]["outputs"])

    def test_narrowing_and_header_derived_output(self):
        rows = [c for c in self.cases if c["name"] == "pattern_7c"
                and c["inputs"]["changes"] == [["0x200afe", 0]]]
        outputs = {bytes.fromhex(c["inputs"]["frame"])[7]: c["outputs"] for c in rows}
        self.assertEqual(outputs[127]["0x17"], 36)
        self.assertEqual(outputs[128]["0x17"], 0)
        self.assertEqual(outputs[255]["0x15"], 203)
        rows = [c for c in self.cases if c["name"] == "pattern_80"]
        self.assertTrue(rows)
        self.assertTrue(all(c["outputs"]["0x18"] == 99 for c in rows))

    def test_phase_two_uses_tx_gate_before_rx_completion_test(self):
        rows = [c for c in self.cases if c["name"] == "control"
                and c["inputs"]["state"] == 2 and c["inputs"]["kind"] in (1, 2)]
        for c in rows:
            ready = bool(int(c["inputs"]["status"], 0) & 0x20)
            self.assertEqual(c["state_out"], 1 if ready else 2)
            self.assertNotIn("0x6b8c", [call["entry"] for call in c["calls"]])
            if not ready:
                self.assertEqual(c["writes"], [])

    def test_rx0_words_and_retained_outputs(self):
        for c in self.cases:
            if c["name"] == "rx0_words":
                frame = bytes.fromhex(c["inputs"]["frame"])
                self.assertEqual(c["outputs"]["0x20"], int.from_bytes(frame[1:3], "little"))
                self.assertEqual(c["outputs"]["0x24"], int.from_bytes(frame[5:7], "little"))
                self.assertEqual(c["outputs"]["0x28"], int.from_bytes(frame[7:9], "little")//4)
            if c["name"] == "unknown_header":
                self.assertEqual({w["offset"] for w in c["writes"]}, {"0x1a"})
            if c["name"] == "two_byte_header_match":
                self.assertEqual(c["outputs"]["0x38"], (-460) & 0xFFFFFFFF)
        for c in (c for c in self.cases if c["name"] == "pattern_84"):
            frame = bytes.fromhex(c["inputs"]["frame"])
            self.assertEqual(c["outputs"]["0x19"], 1 if frame[6] == 0xBB else 0xA7)

    def test_phase_one_pin_release_and_retry(self):
        for c in self.cases:
            x = c["inputs"]
            if c["name"] != "control" or x["state"] != 1 or x["kind"] not in (1, 2):
                continue
            completed = bool(int(x["status"], 0) & 0x10)
            released = bool(int(x["pins"], 0) & (8 if x["kind"] == 1 else 16))
            self.assertEqual(c["state_out"], 0 if completed and released else 1)
            calls = [call["entry"] for call in c["calls"]]
            self.assertEqual("0x6b64" in calls, completed and not released)
