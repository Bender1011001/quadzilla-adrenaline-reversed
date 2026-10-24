"""Check source-bound response assembly and the conditional list overflow."""
import json
import unittest

from tests._paths import ROOT
from model_frame_reader import build_frame,read_values
from x2com_crc import crc8


def load(name):
    return json.loads((ROOT/'audit/data'/name).read_text(encoding='utf-8'))


class FrameReader(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.decode=load('frame_reader_binaryninja.json')
        cls.emu=load('frame_reader_emulation.json')

    def test_bounds_source_identity_and_instruction_coverage(self):
        self.assertEqual(self.decode['raw_sha256'],self.emu['raw_sha256'])
        self.assertEqual([(r['start'],r['end']) for r in self.decode['ranges']],
            [('0x7c68','0x7c9e'),('0x7d80','0x7e64'),('0x7eb4','0x7efc'),('0x7fd8','0x800a')])
        starts={i['address'] for r in self.decode['ranges'] for i in r['instructions']}
        self.assertEqual((len(starts),sum(i['length'] for r in self.decode['ranges'] for i in r['instructions'])),
                         (198,404))
        self.assertEqual(starts-set(self.emu['visited']),{'0x7fee'})
        ida={i['start']:i for i in load('ida_image_items.json')['items']}
        for r in self.decode['ranges']:
            for i in r['instructions']:
                if i['address']=='0x7fd8':
                    continue
                self.assertEqual(int(ida[i['address']]['end'],0),int(i['address'],0)+i['length'])
        correction=load('frame_reader_boundary.json')
        self.assertEqual(correction['ordinary_matching_starts'],197)
        self.assertEqual((correction['correction']['prefix_halfword'],
                          correction['correction']['entry_halfword']),('0xffff','0xb430'))
        self.assertEqual(len(correction['correction']['decoded_direct_call_sites']),7)
        self.assertEqual((self.emu['bounded_cases'],self.emu['queue_copy_cases'],
                          self.emu['reference_mismatches']),(4328,257,0))

    def test_reader_deferral_and_builder_crc(self):
        sources={9:b'\x76\x00\x00\x00',226:None}
        self.assertEqual(read_values([9,226],1,sources),(b'\x09\x76',b'\xe2'))
        self.assertEqual(read_values([9,226],4,sources),(b'\x09\xe2',b''))
        frame,deferred,status=build_frame([9,226],1,sources)
        self.assertEqual((frame[0],frame[1:3],deferred,status),(0x13,b'\x09\x76',b'\xe2',2))
        self.assertEqual(crc8(frame),0x3B)
        sample=next(r for r in self.emu['examples'] if r['aids']=='09' and r['kind']==1 and 'frame' in r)
        self.assertEqual((sample['frame'],sample['return']),('13097664',1))

    def test_copy_cap_and_direct_oversized_rejection(self):
        copies={r['count_arg']:r for r in self.emu['queue_copy_examples']}
        self.assertEqual([(n,copies[n]['count_out']) for n in (1,13,14,15,16,255)],
                         [(1,1),(13,13),(14,14),(15,14),(16,14),(255,14)])
        self.assertEqual(copies[0]['count_out'],0xAA)
        self.assertEqual(self.emu['null_destination']['count_out'],0xAA)
        over={r['count']:r for r in self.emu['oversized_synthetic_caller']}
        self.assertFalse(over[16]['writes_saved_register_region'])
        self.assertEqual(over[17]['last_deferred_stack_store']['address'],'0x202fe0')
        self.assertTrue(over[17]['writes_saved_register_region'])
        self.assertEqual(over[22]['result']['fault']['pc'],'0x7e48')
        self.assertEqual(over[22]['result']['fault']['address'],'0x209a9a')
        self.assertEqual(self.emu['aid255_alias']['fault']['pc'],'0x7de8')

    def test_shared_literal_pool(self):
        pool=load('frame_reader_literals.json')
        self.assertEqual(pool['raw_sha256'],self.emu['raw_sha256'])
        self.assertEqual(pool['range'],['0x7ca0','0x7cc4'])
        self.assertEqual([int(r['word'],0) for r in pool['words']],
            [0xAD18,0xAE44,0xAF70,0xAFFC,0xB088,0xFFFFFED4,0xFFFFFDA8,0xFFFFFD1C,0xFFFFFC90])
        self.assertTrue(all(any(0x7C68<=int(site,0)<0x7C9E for site in r['reader_sites'])
                            for r in pool['words']))
        ledger=load('image_coverage_ledger.json')
        self.assertEqual(ledger['classification_bytes']['aid_resolver_literal_pool'],36)
