"""Pin the queue filter's byte contract, callers, and conditional stack write."""
import json
import unittest

from tests._paths import ROOT
from model_queue_filter import filter_aids


def load(name):
    return json.loads((ROOT/'audit/data'/name).read_text(encoding='utf-8'))


class QueueFilter(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.decode=load('queue_filter_binaryninja.json')
        cls.emu=load('queue_filter_emulation.json')
        cls.callers=load('queue_filter_callers.json')

    def test_image_bounds_and_executed_starts(self):
        self.assertEqual(self.decode['raw_sha256'],self.emu['raw_sha256'])
        self.assertEqual(self.callers['raw_sha256'],self.emu['raw_sha256'])
        block=self.decode['ranges'][0]
        self.assertEqual((block['start'],block['end']),('0x7f58','0x7fd6'))
        self.assertEqual((len(block['instructions']),sum(i['length'] for i in block['instructions'])),(63,126))
        self.assertEqual({i['address'] for i in block['instructions']},set(self.emu['visited']))
        ida={i['start']:i for i in load('ida_image_items.json')['items']}
        for i in block['instructions']:
            self.assertEqual(int(ida[i['address']]['end'],0),int(i['address'],0)+i['length'])
        self.assertEqual((self.emu['bounded_cases'],self.emu['reference_mismatches']),(4549,0))

    def test_list_subtraction_and_zero_comparison(self):
        self.assertEqual(filter_aids([1,2,3,2],[2]),b'\x01\x03')
        self.assertEqual(filter_aids([1,2,3],[]),b'')
        self.assertEqual(filter_aids([1,2,3],[2],destination_valid=False),b'')
        examples=self.emu['examples']
        selected=[r for r in examples if r['current']=='010203' and r['remove']=='02'
                  and r['count_arg']==1 and r['destination_valid']]
        self.assertEqual([(r['return'],r['output']) for r in selected],[(2,'0103')])
        zero=[r for r in examples if r['current']=='010203' and r['count_arg']==0
              and r['destination_valid']]
        self.assertTrue(zero and all(r['return']==0 and r['output']=='' for r in zero))

    def test_direct_stack_boundary(self):
        rows={r['initial_count']:r for r in self.emu['oversized_synthetic_caller']}
        self.assertFalse(rows[16]['writes_saved_register_region'])
        self.assertEqual(rows[17]['last_scratch_store']['address'],'0x202fe8')
        self.assertTrue(rows[17]['writes_saved_register_region'])
        self.assertEqual(rows[18]['result']['status'],'emulator_fault')
        self.assertEqual(rows[18]['result']['fault']['pc'],'0x7fc0')

    def test_caller_sites_and_initial_fields(self):
        self.assertEqual([r['call'] for r in self.callers['calls']],
                         ['0x8126','0x8172','0x83c4','0x84ec'])
        self.assertEqual([r['address'] for r in self.callers['initialized_count_fields']],
                         ['0x2007db','0x2007dc','0x2007e0','0x2007e1'])
        self.assertTrue(all(r['byte']==0 for r in self.callers['initialized_count_fields']))
        for row in self.callers['calls']:
            self.assertTrue(any(i['address']==row['call'] and
                                i['decoded_direct_target']=='0x7f58' for i in row['items']))
