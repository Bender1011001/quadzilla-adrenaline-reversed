"""Pin selector/response separation, byte arithmetic and dead-path evidence."""
import hashlib
import json
import random
import unittest

from tests._paths import ROOT
from model_control_helpers import latch_state, selector_state


def load(name):
    return json.loads((ROOT/'audit/data'/name).read_text(encoding='utf-8'))


class ControlSelector(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.emu=load('control_selector_emulation.json')
        cls.bn=load('control_selector_binaryninja.json')

    def test_source_boundaries_and_dead_path(self):
        self.assertEqual(self.emu['raw_sha256'], self.bn['raw_sha256'])
        self.assertEqual(self.emu['raw_sha256'], load('semantic_labels.json')['raw_sha256'])
        ins=self.bn['ranges'][0]['instructions']
        self.assertEqual((len(ins),sum(i['length'] for i in ins)),(54,112))
        ida={i['start']:i for i in load('ida_image_items.json')['items']}
        for i in ins:
            self.assertEqual(int(ida[i['address']]['end'],0),int(i['address'],0)+i['length'])
        self.assertEqual(set(self.emu['visited'])|set(self.emu['unreachable_starts']),
                         {i['address'] for i in ins})
        self.assertEqual(set(self.emu['unreachable_starts']),{'0x50aa','0x50ac'})
        self.assertTrue(set(self.emu['visited']).isdisjoint(self.emu['unreachable_starts']))
        for i in ida.values():
            self.assertNotIn(i.get('decoded_direct_target'),self.emu['unreachable_starts'])
        self.assertEqual(self.emu['reference_mismatches'],0)

    def test_response_table_and_original_reader(self):
        self.assertEqual(self.emu['aid9_response_pointer']['pointer'],'0x200bc4')
        row=load('aid_table_audit.json')['rows'][9]
        self.assertEqual(row['table2']['pointer'],'0x200bc4')
        self.assertIn('Power Level',row['profile_names'])
        rows=[r for r in self.emu['examples'] if 'aid9_read' in r]
        self.assertEqual(len(rows),16)
        for r in rows:
            self.assertEqual(r['aid9_read']['result'],{'status':'returned','r0':2})
            self.assertEqual(bytes.fromhex(r['aid9_read']['buffer'])[:2],bytes([9,r['response_byte']]))

    def test_boundary_contracts(self):
        vectors=[((2,10,100,100,0,1),(44,2)),
                 ((1,10,0,128,0,1),(128,0)),
                 ((255,0,1,0,0,1),(255,255)),
                 ((1,10,1,0,12,1),(1,1)),
                 ((1,10,1,0,13,1),(1,129)),
                 ((129,255,1,255,0,1),(128,129)),
                 ((2,10,10,0,13,0),(0,228)),
                 ((0,0,255,255,255,1),(0,0))]
        for args,expected in vectors:
            self.assertEqual(selector_state(*args),expected)
        observed={tuple(r['inputs'][k] for k in ('selector','count','step','offset','marker')):
                  (r['mapped_return'],r['response_byte']) for r in self.emu['examples']
                  if 'aid9_read' in r and r['inputs']['enabled']==0}
        for args,expected in vectors:
            if args[-1] and tuple(args[:5]) in observed:
                self.assertEqual(observed[tuple(args[:5])],expected)

    def test_initialized_configuration_range(self):
        for selector in range(256):
            for marker in (0,12,13,255):
                v,e=selector_state(selector,11,10,0,marker,1)
                capped=min(selector,10)
                self.assertEqual(v,capped*10)
                self.assertEqual(e,capped|(128 if marker>=13 and selector else 0))
        self.assertEqual(self.emu['initialized_shape_cases']['cases'],1024)

    def test_pair_sweep_digest_and_examples(self):
        self.assertEqual(self.emu['pair_sweep']['cases'],65536)
        self.assertEqual(self.emu['random_cases'],4096)
        self.assertEqual(len(self.emu['sweep_output_pairs_sha256']),64)
        self.assertEqual(len(self.emu['examples']),52)
        digest=hashlib.sha256()
        for selector in range(256):
            for step in range(256):
                digest.update(bytes(selector_state(selector,255,step,17,0,1)))
        rng=random.Random(0x506C)
        for _ in range(4096):
            selector,count,step,offset,marker,enabled,limit=(rng.randrange(256) for _ in range(7))
            counter=rng.choice((0,14,15,0xFFFFFFFF))
            source=rng.getrandbits(32)
            state=[rng.randrange(256) for _ in range(4)]
            ready,_=latch_state(0,source,enabled,selector,limit,counter,state)
            digest.update(bytes(selector_state(selector,count,step,offset,marker,ready)))
        self.assertEqual(digest.hexdigest(),self.emu['sweep_output_pairs_sha256'])
        for r in self.emu['examples']:
            x=r['inputs']
            ready=r['latch_out'][2]
            self.assertEqual(selector_state(*(x[k] for k in
                ('selector','count','step','offset','marker')),ready),
                (r['mapped_return'],r['response_byte']))
