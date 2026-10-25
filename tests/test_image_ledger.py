"""Test byte-accounting invariants and pin the discovered relocation evidence."""
import importlib.util
import copy
import json
import unittest

from tests._paths import ROOT

spec = importlib.util.spec_from_file_location("ledger", ROOT / "audit/tools/build_image_ledger.py")
ledger = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ledger)


class ImageLedger(unittest.TestCase):
    def test_review_manifest_rejects_false_coverage(self):
        doc = json.loads((ROOT / "audit/data/reviewed_instruction_ranges.json").read_text())
        self.assertEqual(sum(b-a for a, b, *_ in ledger.validate_instruction_reviews(doc)), 13022)
        for change in ("hash", "overlap", "layout", "odd", "account"):
            malformed = copy.deepcopy(doc)
            if change == "hash":
                malformed["raw_sha256"] = "0"*64
            elif change == "overlap":
                malformed["ranges"].append(malformed["ranges"][0].copy())
            elif change == "layout":
                malformed["ranges"][0].update(start="0xa91c", end="0xa920")
            elif change == "odd":
                malformed["ranges"][0]["end"] = "0x4595"
            else:
                malformed["ranges"][0]["account"] = ""
            with self.subTest(change=change), self.assertRaises(ValueError):
                ledger.validate_instruction_reviews(malformed)

    def test_accepted_instruction_bytes_have_exact_manifest_and_decoder_bounds(self):
        manifest = json.loads((ROOT / "audit/data/reviewed_instruction_ranges.json").read_text())
        doc = json.loads((ROOT / "audit/data/image_coverage_ledger.json").read_text())
        ranges = []
        for row in manifest["ranges"]:
            start, end = int(row["start"], 0), int(row["end"], 0)
            ranges.append((row["entry"], start, end))
            decode = json.loads((ROOT / row["decoder_artifact"]).read_text())
            block = next(r for r in decode["ranges"] if r["start"] == row["start"])
            self.assertEqual(block["architecture"], "armv7" if row["isa"] == "arm" else "thumb2")
            self.assertNotIn("decode_stopped_at", block)
            cursor = start
            for instruction in block["instructions"]:
                self.assertEqual(int(instruction["address"], 0), cursor)
                self.assertNotIn("undefined", instruction["text"])
                cursor += instruction["length"]
            self.assertEqual(cursor, end)
        accepted = [r for r in doc["ranges"] if r["classification"] in ("reviewed_thumb_instructions", "reviewed_arm_instructions")]
        self.assertEqual(sum(int(r["end"], 0)-int(r["start"], 0) for r in accepted), 13022)
        for r in accepted:
            self.assertTrue(any(entry == r["review_entry"] and
                                start <= int(r["start"], 0) < int(r["end"], 0) <= end
                                for entry, start, end in ranges))

    def test_coverage_rejects_gaps_overlaps_and_truncation(self):
        def row(a, b):
            return {"start": hex(a), "end": hex(b)}
        ledger.validate_item_coverage([row(0, 2), row(2, 4)], 0, 4)
        for rows in ([row(0, 1), row(2, 4)], [row(0, 3), row(2, 4)], [row(0, 3)], [row(0, 5)], [row(0, 0)]):
            with self.subTest(rows=rows), self.assertRaises(ValueError):
                ledger.validate_item_coverage(rows, 0, 4)

    def test_real_ledger_accounts_for_image_without_claiming_completion(self):
        doc = json.loads((ROOT / "audit/data/image_coverage_ledger.json").read_text())
        ledger.validate_item_coverage(doc["ranges"])
        self.assertEqual(sum(doc["classification_bytes"].values()), 32000)
        self.assertIn("incomplete", doc["completion"])
        self.assertGreater(doc["classification_bytes"]["ida_code_pending_review"], 0)
        self.assertGreater(len(doc["ida_layout_conflicts"]), 0)

    def test_outgoing_state_evidence_and_count_write_order(self):
        decoded = json.loads((ROOT / "audit/data/outgoing_state_binaryninja.json").read_text())
        executed = json.loads((ROOT / "audit/data/outgoing_state_emulation.json").read_text())
        instructions = decoded["ranges"][0]["instructions"]
        starts = {int(row["address"], 0) for row in instructions}
        visited = {int(address, 0) for address in executed["visited_outgoing_starts"]}
        self.assertEqual((len(starts), sum(row["length"] for row in instructions)), (383, 854))
        self.assertEqual(starts - visited, {0x847C, 0x847E, 0x8480, 0x848A, 0x84DC})
        self.assertEqual(len(executed["cases"]), 28)
        self.assertTrue(all(row["result"]["status"] == "returned" for row in executed["cases"]))
        case = next(row for row in executed["cases"] if row["label"] == "list_a_14")
        count_writes = [(row["pc"], row["address"], row["value"]) for row in case["writes"]
                        if row["address"] in ("0x2007db", "0x2007dc")]
        self.assertEqual(count_writes, [("0x8002", "0x2007dc", "0xe"),
                                        ("0x7e56", "0x2007db", "0x1"),
                                        ("0x7fcc", "0x2007dc", "0xd")])

    def test_receive_type_switch_is_data_and_all_code_starts_execute(self):
        decoded = json.loads((ROOT / "audit/data/receive_state_binaryninja.json").read_text())
        executed = json.loads((ROOT / "audit/data/receive_state_emulation.json").read_text())
        layout = json.loads((ROOT / "audit/data/receive_state_layout.json").read_text())
        starts = {int(item["address"], 0) for block in decoded["ranges"]
                  for item in block["instructions"]}
        self.assertEqual(sum(item["length"] for block in decoded["ranges"]
                             for item in block["instructions"]), 356)
        self.assertEqual(len(starts), 162)
        self.assertEqual(starts, {int(a, 0) for a in executed["visited_receive_starts"]})
        self.assertEqual(layout["switch"]["bytes"], "1d0231020a57")
        self.assertEqual(layout["switch"]["targets"],
                         ["0x80d8", "0x80a2", "0x8100", "0x80a2", "0x80b2", "0x814c"])
        self.assertEqual(layout["state_base_literal"]["value"], "0x2007c8")
        results = {row["label"]: row["status"] for row in executed["cases"]}
        self.assertEqual((results["no_pending"], results["bad_crc"], results["type5_finish"]),
                         (0, 4, 6))

    def test_ram_template_descriptor_and_call_targets(self):
        doc = json.loads((ROOT / "audit/data/image_coverage_ledger.json").read_text())
        descriptor = next(r for r in doc["startup_descriptors"] if r["at"] == "0x96dc")
        self.assertEqual(descriptor, {"at": "0x96dc", "length": 164, "destination": "0x200c84", "source": "0xb114", "operation": "copy"})
        items = json.loads((ROOT / "audit/data/ida_image_items.json").read_text())["items"]
        refs = {r["start"]: r.get("decoded_direct_target") for r in items}
        self.assertEqual([refs[a] for a in ("0x6b28", "0x6b36", "0x77e4")], ["0x200c84", "0x200c94", "0x200cfc"])

    def test_bounded_decode_recovers_entry_after_ff_alignment(self):
        doc = json.loads((ROOT / "audit/data/startup_relocation_binaryninja.json").read_text())
        rows = {r["start"]: r for r in doc["ranges"]}
        self.assertEqual(rows["0xb124"]["instructions"][0]["text"].split()[0], "push")
        self.assertEqual(rows["0xb18c"]["instructions"][0]["text"].split()[0], "push")
        self.assertNotIn("decode_stopped_at", rows["0xb124"])


if __name__ == "__main__":
    unittest.main()
