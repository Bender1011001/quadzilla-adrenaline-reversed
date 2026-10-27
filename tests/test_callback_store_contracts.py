"""CFG joins must not turn differing branch destinations into a fixed target."""
import json
import sys
import unittest
from tests._paths import ROOT

sys.path.insert(0, str(ROOT / 'audit/tools'))
from audit_callback_store_contracts import analyze


class CallbackStoreContracts(unittest.TestCase):
    def test_distinct_branch_addresses_remain_unresolved(self):
        raw = bytearray(0x8000)
        ops = [0x4804, 0x2900, 0xD001, 0x3004, 0xE7FF, 0x6002, 0x4770]
        for n, op in enumerate(ops):
            raw[2*n:2*n+2] = op.to_bytes(2, 'little')
        raw[0x14:0x18] = (0x200000).to_bytes(4, 'little')
        rows = {0x4000+2*n: {'length': 2, 'text': hex(op)} for n, op in enumerate(ops)}
        result = analyze(raw, rows, 0x4000, {})
        self.assertEqual(result['unsupported_starts'], [])
        self.assertEqual(result['stores'][0]['status'], 'unresolved')
        raw[6:8] = (0x2207).to_bytes(2, 'little')
        same = analyze(raw, rows, 0x4000, {})
        self.assertEqual(same['stores'][0]['address'], '0x200000')

    def test_complete_selected_body_store_inventory(self):
        d = json.loads((ROOT / 'audit/data/callback_store_contracts.json').read_text())
        stores = [s for b in d['bodies'] for s in b['stores']]
        self.assertEqual(len(d['bodies']), 7)
        self.assertEqual(len(stores), 114)
        self.assertEqual(sum(s['status'] == 'fixed' for s in stores), 110)
        self.assertEqual(sum(s['status'] == 'stack-relative' for s in stores), 4)
        self.assertFalse(any(b['unsupported_starts'] for b in d['bodies']))
        for s in stores:
            if s['address']:
                start = int(s['address'], 0)
                self.assertFalse(start < 0x2005F4 and start+s['byte_count'] > 0x2005F0)

    def test_stack_saved_pointer_join_remains_conservative(self):
        raw = bytearray(0x8000)
        ops = [0xB081, 0x4805, 0x9000, 0x2900, 0xD002, 0x3004,
               0x9000, 0xE7FF, 0x9800, 0x6002, 0xB001, 0x4770]
        for n, op in enumerate(ops):
            raw[2*n:2*n+2] = op.to_bytes(2, 'little')
        raw[0x18:0x1C] = (0x200000).to_bytes(4, 'little')
        rows = {0x4000+2*n: {'length': 2, 'text': hex(op)} for n, op in enumerate(ops)}
        result = analyze(raw, rows, 0x4000, {})
        final = next(s for s in result['stores'] if s['site'] == '0x4012')
        self.assertEqual(final['status'], 'unresolved')
        raw[10:12] = (0x2207).to_bytes(2, 'little')
        same = analyze(raw, rows, 0x4000, {})
        self.assertEqual(next(s for s in same['stores'] if s['site'] == '0x4012')['address'], '0x200000')

    def test_callee_and_pointer_obligations_are_not_hidden(self):
        d = json.loads((ROOT / 'audit/data/callback_store_contracts.json').read_text())
        calls = [c for b in d['bodies'] for c in b['callee_obligations']]
        self.assertEqual(len(calls), 20)
        self.assertEqual(len({c['target'] for c in calls}), 11)
        self.assertEqual(d['pointer_assumptions']['0x200728'], '0xfffa0080')
        self.assertTrue(d['runtime_observed_fixed_sites'])
        self.assertTrue(any('transitive' in s for s in d['limits']))


if __name__ == '__main__':
    unittest.main()
