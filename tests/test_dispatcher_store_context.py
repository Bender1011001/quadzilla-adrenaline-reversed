"""Parent-frame continuation and finite destination-set contracts."""
import json
import unittest
from tests._paths import ROOT


class DispatcherStoreContext(unittest.TestCase):
    def setUp(self):
        self.doc = json.loads((ROOT / 'audit/data/dispatcher_store_context.json').read_text())

    def test_normal_entry_accounts_for_every_local_store(self):
        d = self.doc
        self.assertEqual(d['entry'], '0x601c')
        self.assertEqual(d['selected_starts'], 908)
        self.assertEqual(d['reachable_starts'], 908)
        self.assertEqual(d['status_counts'], {'stack-relative': 4, 'fixed': 104, 'finite-address-set': 10})
        self.assertEqual(len(d['stores']), 118)
        self.assertEqual(len(d['previous_unresolved_now_classified']), 41)
        self.assertEqual(len(d['runtime_observations']), 114)

    def test_curve_echo_continuation_has_multiple_destinations(self):
        row = next(s for s in self.doc['stores'] if s['site'] == '0x604c')
        self.assertEqual(row['status'], 'finite-address-set')
        self.assertEqual(row['addresses'], [hex(a) for a in range(0x200C17, 0x200C36, 2)])
        self.assertEqual(len(self.doc['frame_transfer_edges']), 18)
        for s in self.doc['stores']:
            for a in s.get('addresses', [s['address']] if s['address'] else []):
                start = int(a, 0)
                self.assertFalse(start < 0x2005F4 and start+s['byte_count'] > 0x2005F0)

    def test_special_register_contracts_are_explicit_and_limited(self):
        contracts = self.doc['callee_contract_assumptions']
        self.assertEqual(contracts['0x8574']['preserved_caller_registers'], [2, 3])
        self.assertEqual(contracts['0x8584']['preserved_caller_registers'], [2, 3])
        self.assertEqual(contracts['0x7128']['preserved_caller_registers'], [])
        self.assertNotIn('0x8038', contracts)
        self.assertEqual(self.doc['unsupported_starts'], [])


if __name__ == '__main__':
    unittest.main()
