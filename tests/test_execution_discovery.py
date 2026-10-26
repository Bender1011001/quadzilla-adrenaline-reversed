"""Verify raw branch decoding and the bounded entry-discovery inventory."""
import importlib.util
import json
import sys
import unittest

from tests._paths import ROOT

sys.path.insert(0,str(ROOT/'audit/tools'))
spec=importlib.util.spec_from_file_location('entry_discovery',ROOT/'audit/tools/audit_execution_discovery.py')
discovery=importlib.util.module_from_spec(spec)
spec.loader.exec_module(discovery)


class ExecutionDiscovery(unittest.TestCase):
    def test_raw_branch_kind_sign_and_state(self):
        self.assertEqual(discovery.direct_transfer(0x1000,'thumb',bytes.fromhex('00f000f8')),('BL',0x1004,14))
        self.assertEqual(discovery.direct_transfer(0x1000,'thumb',bytes.fromhex('fff7feff')),('BL',0x1000,14))
        self.assertEqual(discovery.direct_transfer(0x1000,'arm',bytes.fromhex('000000eb')),('BL',0x1008,14))
        self.assertEqual(discovery.direct_transfer(0x1000,'arm',bytes.fromhex('feffffea')),('B',0x1000,14))
        self.assertEqual(discovery.direct_transfer(0x1000,'arm',bytes.fromhex('0000009a')),('B',0x1008,9))
        self.assertIsNone(discovery.direct_transfer(0x1000,'thumb',bytes.fromhex('7047')))
        self.assertEqual(discovery.canonical(0x200C94),0xB124)

    def test_recorded_edges_aliases_and_scalar_dispositions(self):
        doc=json.loads((ROOT/'audit/data/execution_discovery_audit.json').read_text())
        self.assertEqual(doc['raw_sha256'],'1ae519ba6194e8f7bdaaa94333a83a9e6fda3b0563f87f7d48383b37288c1780')
        self.assertEqual((doc['known_source_entries'],doc['decoded_instruction_starts']),(157,8051))
        self.assertEqual((doc['direct_calls'],doc['direct_branches']),(354,1114))
        self.assertEqual(doc['raw_ida_target_disagreements'],[])
        self.assertTrue(all(e['documented_entry'] for e in doc['direct_transfers'] if e['kind']=='BL'))
        self.assertEqual(len(doc['resolved_runtime_calls']),3)
        self.assertEqual(len(doc['cross_ida_owner_dispositions']),4)
        self.assertTrue(all(e['target_visited_from_entries'] for e in doc['cross_ida_owner_dispositions']))
        self.assertEqual(len(doc['code_address_data_windows']),48)
        scalar=next(e for e in doc['code_address_data_windows'] if e['source']=='0x6f6c')
        self.assertIn('counter threshold',scalar['disposition'])
        self.assertEqual(len(doc['bx_sites']),203)
        self.assertEqual(sum(e['status'].startswith('requires') for e in doc['bx_sites']),60)


if __name__=='__main__':unittest.main()
