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
        self.assertEqual(sum(b-a for a, b, *_ in ledger.validate_instruction_reviews(doc)), 14862)
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
        self.assertEqual(sum(int(r["end"], 0)-int(r["start"], 0) for r in accepted), 14862)
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

    def test_main_loop_count_writer_claim_is_bounded_to_direct_stores(self):
        audit = json.loads((ROOT / "audit/data/main_loop_count_writers.json").read_text())
        run = json.loads((ROOT / "audit/data/main_loop_dispatch_emulation.json").read_text())
        self.assertEqual((audit["bn_instruction_starts"], audit["ida_code_item_starts"]), (307, 305))
        self.assertEqual(audit["bn_only_starts"], ["0x77c0", "0x786e"])
        self.assertEqual(len(audit["main_loop_r5_direct_stores"]), 15)
        counts = set(range(0x20078A, 0x20078F))
        self.assertTrue(all(not counts.intersection(range(int(row["address"], 0),
                                                      int(row["address"], 0) + row["size"]))
                            for row in audit["main_loop_r5_direct_stores"]))
        self.assertEqual({int(row["address"], 0) for row in audit["global_direct_count_references"]}, counts)
        self.assertTrue(all(row["instruction"].startswith("LDRB")
                            for row in audit["global_direct_count_references"]))
        self.assertEqual(len(run["cases"]), 8)
        self.assertEqual(len(run["visited_starts"]), 157)
        self.assertTrue(all(int(write["address"], 0) not in counts
                            for row in run["cases"] for write in row["writes"]))

    def test_initial_state_and_aid151_mirror_have_source_bound_results(self):
        initial = json.loads((ROOT / "audit/data/initial_state_emulation.json").read_text())
        restore = json.loads((ROOT / "audit/data/config_restore_emulation.json").read_text())
        mirror = json.loads((ROOT / "audit/data/config_response_mirror_emulation.json").read_text())
        self.assertEqual(len(initial["visited_starts"]), 70)
        results = {row["label"]: row["return_r0"] for row in initial["cases"]}
        self.assertEqual((results["default_pin_low"], results["default_pin_high"]), (1, 0))
        self.assertEqual((results["mode2_disabled_below"], results["mode2_disabled_equal"]), (2, 0))
        self.assertEqual([(row["copied"], row["after_mode_byte"]) for row in restore["cases"]],
                         [(False, 4), (True, 234)])
        self.assertEqual(len(mirror["visited_starts"]), 92)
        zero = next(row for row in mirror["cases"] if row["response_fill"] == "0x0")
        self.assertEqual(zero["config_halfword_dc"], "0x7a73")
        self.assertEqual(zero["aid151_reader_payload"], "97657a00")
        stores = [(row["pc"], row["address"], row["value"]) for row in zero["writes"]
                  if row["address"] in ("0x200be8", "0x200be9")]
        self.assertEqual(stores, [("0x5f96", "0x200be8", "0x73"),
                                  ("0x5f9c", "0x200be8", "0x7a")])

    def test_adc_pipeline_tables_and_channel4_producer(self):
        layout = json.loads((ROOT / "audit/data/adc_table_layout.json").read_text())
        run = json.loads((ROOT / "audit/data/adc_pipeline_emulation.json").read_text())
        ledger_doc = json.loads((ROOT / "audit/data/image_coverage_ledger.json").read_text())
        self.assertEqual([(row["start"], row["end"], row["element_count"])
                          for row in layout["tables"]],
                         [("0xa030", "0xa0b0", 128), ("0xa0b0", "0xa320", 312),
                          ("0xa320", "0xa3a0", 128), ("0xa3a0", "0xa91c", 702)])
        self.assertEqual(sum(row["bytes"] for row in layout["tables"]), 2284)
        self.assertEqual(len(run["visited_starts"]), 166)
        cases = {row["label"]: row for row in run["cases"]}
        self.assertEqual(cases["all_zero"]["outputs"]["4"]["output"], 17)
        self.assertEqual(cases["all_max"]["outputs"]["4"]["output"], 73)
        self.assertEqual(cases["all_max"]["page_after"], 1)
        self.assertEqual(cases["channel4_only"]["status_after"], "0xe8")
        classes = ledger_doc["classification_bytes"]
        self.assertEqual(sum(classes[name] for name in (
            "adc_channel6_byte_lut", "adc_channel7_signed_halfword_lut",
            "adc_channel5_two_page_lut", "adc_channel4_signed_halfword_lut")), 2284)

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

    def test_queue_owner_counts_and_direct_state_literals(self):
        decoded = json.loads((ROOT / "audit/data/queue_state_owners_binaryninja.json").read_text())
        executed = json.loads((ROOT / "audit/data/queue_state_owners_emulation.json").read_text())
        refs = json.loads((ROOT / "audit/data/queue_state_refs.json").read_text())
        starts = {int(item["address"], 0) for block in decoded["ranges"]
                  for item in block["instructions"]}
        visited = {int(a, 0) for a in executed["visited_starts"]}
        self.assertEqual((len(starts), sum(item["length"] for block in decoded["ranges"]
                                           for item in block["instructions"])), (40, 84))
        self.assertTrue(starts <= visited)
        rows = {row["label"]: row for row in executed["cases"]}
        self.assertEqual([rows[name]["counts"]["0xd"] for name in
                          ("queue_one", "queue_fourteen", "queue_fifteen", "queue_255")],
                         [1, 14, 14, 14])
        self.assertEqual([rows[name]["result"]["r0"] for name in ("busy_e", "busy_f")], [0, 0])
        self.assertEqual([rows["reset_flags"]["counts"][name] for name in ("0x13", "0x18")],
                         [14, 13])
        self.assertEqual([(item["at"], item["value"]) for item in
                          refs["aligned_words_pointing_into_state"]],
                         [("0x8034", "0x2007c8"), ("0x81a4", "0x2007c8"),
                          ("0x8500", "0x2007c8"), ("0x9ed0", "0x2007f0")])
        self.assertEqual(set(refs["initialized_count_bytes"].values()), {0})

    def test_cycle_queue_sources_and_conditional_cross_slot_copy(self):
        decoded = json.loads((ROOT / "audit/data/cycle_queue_binaryninja.json").read_text())
        executed = json.loads((ROOT / "audit/data/cycle_queue_selection_emulation.json").read_text())
        source = json.loads((ROOT / "audit/data/cycle_queue_sources.json").read_text())
        instructions = decoded["ranges"][0]["instructions"]
        self.assertEqual((len(instructions), sum(row["length"] for row in instructions)),
                         (98, 218))
        tail = {int(row["address"], 0) for row in instructions
                if int(row["address"], 0) >= 0x76F0}
        self.assertEqual(tail, {int(a, 0) for a in executed["visited_cycle_starts"]})
        self.assertEqual([row["count_initialized"] for row in source["slots"]],
                         [6, 6, 7, 6, 5])
        self.assertEqual(source["literal_pool"]["words"],
                         ["0x200788", "0x200712", "0x200710", "0x200711"])
        rows = {row["label"]: row for row in executed["cases"]}
        for slot in range(5):
            case = rows[f"template_slot_{slot}"]
            self.assertEqual(case["queue_count"], source["slots"][slot]["count_initialized"])
            self.assertEqual(bytes.fromhex(case["queue_bytes"])[:case["queue_count"]],
                             bytes(source["slots"][slot]["aids"]))
        self.assertEqual(bytes.fromhex(rows["cross_slot_synthetic"]["queue_bytes"])[:9],
                         bytes.fromhex("101112131415161720"))
        self.assertEqual((rows["busy"]["pending_out"], rows["busy"]["selector_out"]),
                         (1, 0))

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
