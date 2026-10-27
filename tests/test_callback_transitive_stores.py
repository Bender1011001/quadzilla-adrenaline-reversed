"""Numeric closure and explicit return/stack limits of callback store accounts."""
import json
import sys
import unittest
from tests._paths import ROOT

sys.path.insert(0, str(ROOT / 'audit/tools'))
from audit_callback_transitive_stores import arm_edges


class CallbackTransitiveStores(unittest.TestCase):
    def test_conservative_arm_edges_and_opaque_transfer_rejection(self):
        self.assertEqual(arm_edges(0x4000, 0xEA000000)[0], [0x4008])
        self.assertEqual(arm_edges(0x4000, 0x0A000000)[0], [0x4008, 0x4004])
        self.assertEqual(arm_edges(0x4000, 0xEB000000)[0], [0x4008, 0x4004])
        self.assertEqual(arm_edges(0x4000, 0xE12FFF1E)[0], [])
        self.assertEqual(arm_edges(0x4000, 0x112FFF1E)[0], [0x4004])
        for op in (0xE12FFF10, 0xE1A0F000, 0xEF000000):
            with self.assertRaises(ValueError):
                arm_edges(0x4000, op)

    def test_all_eleven_direct_targets_have_address_accounts(self):
        d = json.loads((ROOT / 'audit/data/callback_transitive_stores.json').read_text())
        self.assertEqual(d['call_sites_accounted'], 20)
        self.assertEqual(len(d['numeric_wrappers']), 9)
        self.assertEqual(len(d['flag_helpers']), 2)
        self.assertEqual(sum(w['stack_push_bytes'] != 0 for w in d['numeric_wrappers']), 2)
        stores = [s for f in d['flag_helpers'] for s in f['stores']]
        self.assertEqual(len(stores), 8)
        self.assertTrue(all(s['status'] == 'fixed' for s in stores))

    def test_numeric_region_has_only_status_and_stack_stores(self):
        d = json.loads((ROOT / 'audit/data/callback_transitive_stores.json').read_text())
        self.assertEqual(d['runtime_instruction_superset'], 1042)
        stores = d['runtime_stores_superset']
        self.assertEqual(len(stores), 8)
        fixed = [s for s in stores if 'address' in s]
        self.assertEqual([(s['site'], s['address']) for s in fixed], [('0x8964', '0x200af8')])
        self.assertTrue(all(s['form']['base'] == 13 for s in stores if s not in fixed))
        self.assertEqual(d['status_store_predecessor_chain'], ['0x8958', '0x895c', '0x8960', '0x8964'])
        self.assertTrue(any('numeric correctness' in s for s in d['limits']))


if __name__ == '__main__':
    unittest.main()
