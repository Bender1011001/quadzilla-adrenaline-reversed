"""Check raw store decoding and keep address evidence distinct from guarantees."""
import importlib.util
import json
import sys
import unittest

from tests._paths import ROOT

sys.path.insert(0, str(ROOT / 'audit/tools'))
spec = importlib.util.spec_from_file_location('store_inventory_audit', ROOT / 'audit/tools/audit_store_inventory.py')
audit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit)


class StoreInventory(unittest.TestCase):
    def test_thumb_store_widths_offsets_and_lists(self):
        for op, width, offset in ((0x6008, 4, 0), (0x7048, 1, 1), (0x8048, 2, 2)):
            row = audit.store_form('thumb', op)
            self.assertEqual((row['base'], row['source'], row['width'], row['offset']), (1, 0, width, offset))
        indexed = audit.store_form('thumb', 0x5088)
        self.assertEqual((indexed['base'], indexed['source'], indexed['offset_register'], indexed['width']), (1, 0, 2, 4))
        push = audit.store_form('thumb', 0xB510)
        self.assertEqual((push['base'], push['registers'], push['offset']), (13, [4, 14], -8))
        for load in (0x6808, 0x8808, 0x9800, 0xBD10):
            self.assertIsNone(audit.store_form('thumb', load))

    def test_arm_pre_post_and_block_stores(self):
        pre = audit.store_form('arm', 0xE5810004)
        post = audit.store_form('arm', 0xE4810004)
        self.assertEqual((pre['base'], pre['width'], pre['offset'], pre['writeback']), (1, 4, 4, False))
        self.assertEqual((post['offset'], post['index_adjustment'], post['writeback']), (0, 4, True))
        half = audit.store_form('arm', 0xE1C100B2)
        self.assertEqual((half['width'], half['offset']), (2, 2))
        push = audit.store_form('arm', 0xE92D4010)
        self.assertEqual((push['base'], push['registers'], push['offset']), (13, [4, 14], -8))
        for load in (0xE5910004, 0xE8BD4010):
            self.assertIsNone(audit.store_form('arm', load))

    def test_complete_accepted_store_inventory(self):
        d = json.loads((ROOT / 'audit/data/store_inventory.json').read_text())
        self.assertEqual(d['raw_sha256'], '1ae519ba6194e8f7bdaaa94333a83a9e6fda3b0563f87f7d48383b37288c1780')
        self.assertEqual((d['accepted_instruction_starts'], d['store_sites']), (8051, 1063))
        self.assertEqual(sum(d['counts'].values()), 1063)
        self.assertEqual(d['raw_text_disagreements'], [])
        self.assertEqual((d['explicit_sp_base_sites'], d['adjacent_literal_witnesses'], d['ida_annotated_sites'], d['observed_sites']), (134, 167, 360, 98))
        self.assertEqual(len({s['site'] for s in d['stores']}), 1063)
        table_writers = {s['site'] for s in d['stores'] if any(0x200000 <= int(o['address'], 0) < 0x200190 for o in s['observations'])}
        self.assertTrue({'0x7400', '0x7414'} <= table_writers)


if __name__ == '__main__':
    unittest.main()
