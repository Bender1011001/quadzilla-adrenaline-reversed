"""Check source-bound AID mapping and the limits of committed emulator evidence."""
import json
import unittest

from tests._paths import ROOT
from diff_profiles import extract_aids
from x2com_crc import check_frame


class AidTableBoundary(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.doc = json.loads((ROOT / "audit/data/aid_table_audit.json").read_text(encoding="utf-8"))
        cls.rows = cls.doc["rows"]

    def test_mapping_covers_byte_domain_and_actual_profiles(self):
        self.assertEqual([r["aid"] for r in self.rows], list(range(256)))
        names = {}
        for path in (ROOT / "vehicles").glob("vehicle_*.json"):
            for aid, record in extract_aids(json.loads(path.read_text(encoding="utf-8-sig"))).items():
                names.setdefault(aid, set()).add(record["name"])
        self.assertEqual(self.doc["profile_aid_union"], len(names))
        for row in self.rows:
            self.assertEqual(row["profile_names"], sorted(names.get(row["aid"], set())))
            for table, base in (("table1", 0xA91C), ("table2", 0xAD18)):
                self.assertEqual(int(row[table]["lookup_address"], 0), base+4*row["aid"])
            self.assertEqual(row["inside_255_slot_tables"], row["aid"] < 255)

    def test_last_byte_indexes_the_next_region(self):
        row = self.rows[255]
        self.assertEqual(row["table1"], {"lookup_address": "0xad18", "pointer": "0x200bba"})
        self.assertEqual(row["table2"], {"lookup_address": "0xb114", "pointer": "0x43c02097"})
        self.assertEqual(row["table1"]["pointer"], self.rows[0]["table2"]["pointer"])
        self.assertEqual(self.doc["resolver_cases"], 512)

    def test_only_last_byte_faults_in_controlled_single_aid_reader(self):
        self.assertEqual(self.doc["reader_cases"], 256)
        faults = [r for r in self.rows if r["reader"]["status"] != "returned"]
        self.assertEqual([r["aid"] for r in faults], [255])
        self.assertEqual(faults[0]["reader"]["fault"]["address"], "0x43c02097")
        self.assertEqual(faults[0]["reader"]["fault"]["pc"], "0x7de8")

    def test_builder_has_valid_comparison_and_faulting_case(self):
        cases = {c["aid"]: c for c in self.doc["frame_builder_cases"]}
        frame = bytes.fromhex(cases[85]["buffer_prefix"])
        frame = frame[:(frame[0] & 15)+1]
        self.assertTrue(check_frame(frame))
        self.assertEqual(frame[1], 85)
        self.assertEqual(cases[85]["result"], {"status": "returned", "r0": 1})
        self.assertEqual(cases[255]["result"]["fault"]["address"], "0x43c02097")

    def test_writer_alias_is_an_observed_byte_write(self):
        alias = self.doc["aid255_writer_alias"]
        self.assertEqual(alias["result"], {"status": "returned", "r0": 1})
        self.assertEqual((alias["destination"], alias["before"], alias["after"]), ("0x200bba", "00", "01"))
        self.assertEqual((alias["reported_aid"], alias["reported_count"]), ("ff", "01"))

    def test_provenance_and_hardware_limit_are_explicit(self):
        source = json.loads((ROOT / "audit/data/aid_table_binaryninja.json").read_text(encoding="utf-8"))
        self.assertEqual(self.doc["raw_sha256"], source["raw_sha256"])
        self.assertIn("unmapped emulation read is not a demonstrated hardware reset", self.doc["limits"])
        instructions = {i["address"]: i["text"] for r in source["ranges"] for i in r["instructions"]}
        self.assertEqual(instructions["0x7de8"], "ldrb    r0, [r0]")
        self.assertEqual(instructions["0x7d6c"], "strb    r2, [r0]")


if __name__ == "__main__":
    unittest.main()
