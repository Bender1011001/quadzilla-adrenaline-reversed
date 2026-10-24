"""Verify dispatch selection, bounded update paths and parameter ordering evidence."""
import json
import unittest

from tests._paths import ROOT
from model_selector_updates import updates


def load(name):
    return json.loads((ROOT/'audit/data'/name).read_text(encoding='utf-8'))


class SelectorUpdates(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.map=load('aid_validation_dispatch.json')
        cls.emu=load('selector_update_emulation.json')
        cls.bn=load('selector_update_binaryninja.json')

    def test_switch_table_and_all_byte_destinations(self):
        self.assertEqual(self.map['raw_sha256'],self.emu['raw_sha256'])
        self.assertEqual(self.map['raw_sha256'],load('semantic_labels.json')['raw_sha256'])
        self.assertEqual(self.map['table_range'],['0x608c','0x6240'])
        self.assertEqual((self.map['table_bytes'],self.map['slots']),(436,218))
        self.assertEqual(self.map['executed_selector_cases'],256)
        self.assertEqual(self.map['reference_mismatches'],0)
        self.assertEqual([r['aid'] for r in self.map['rows']],list(range(256)))
        for r in self.map['rows']:
            aid=r['aid']
            if 9<=aid<=226:
                self.assertEqual(int(r['table_address'],0),0x608C+2*(aid-9))
                self.assertEqual(int(r['target'],0),0x608E+r['signed_offset'])
            else:
                self.assertIsNone(r['table_address'])
                self.assertEqual(r['target'],'0x604e')
            self.assertEqual(r['pointer_slot_in_bounds'],aid<255)
        self.assertEqual(sum(not r['default_path'] for r in self.map['rows']),57)
        self.assertEqual(self.map['rows'][9]['target'],'0x6240')
        self.assertEqual(self.map['rows'][15]['target'],'0x6482')
        self.assertEqual(self.map['rows'][9]['staging_pointer'],'0x200b00')
        self.assertEqual(self.map['rows'][15]['response_pointer'],'0x200bea')

    def test_instruction_bounds_and_executed_coverage(self):
        self.assertEqual(self.emu['raw_sha256'],self.bn['raw_sha256'])
        instructions=[i for r in self.bn['ranges'] for i in r['instructions']]
        self.assertEqual((len(instructions),sum(i['length'] for i in instructions)),(99,206))
        self.assertEqual({i['address'] for i in instructions},set(self.emu['visited']))
        ida={i['start']:i for i in load('ida_image_items.json')['items']}
        for i in instructions:
            self.assertEqual(int(ida[i['address']]['end'],0),int(i['address'],0)+i['length'])
        for r in self.map['rows']:
            target=ida[r['target']]
            self.assertEqual((target['kind'],target['thumb']),('ida_code',1))
        self.assertEqual(self.emu['calls'],5391)
        self.assertEqual(self.emu['reference_mismatches'],0)

    def test_count_bounds_and_derived_mapping(self):
        for staged in range(256):
            state,post=updates([15],0,staged,13,14,7,9)
            count=min(max(staged,5),14)
            self.assertEqual(state['count'],count)
            self.assertEqual(state['count_echo'],count)
            self.assertEqual((state['step'],state['offset']),divmod(100,count-1))
            self.assertEqual(state['changed'],0)
            self.assertEqual(post['mapped'],100)
        for count in range(5,15):
            step,offset=divmod(100,count-1)
            for staged in range(256):
                state,post=updates([9],staged,11,2,count,step,offset)
                self.assertLess(state['selector'],count)
                self.assertLessEqual(post['mapped'],100)

    def test_original_ordering_and_equality_skip(self):
        examples=self.emu['examples']
        rows={tuple(c['inputs']['aids']):c for c in examples
              if c['inputs']['receive_status']==1 and c['inputs']['count']==5
              and c['inputs']['staged_selector']==10}
        self.assertEqual(rows[(9,15)]['after_ingest']['selector'],4)
        self.assertEqual(rows[(9,15)]['after_selector']['mapped'],40)
        self.assertEqual(rows[(15,9)]['after_ingest']['selector'],10)
        self.assertEqual(rows[(15,9)]['after_selector']['mapped'],100)
        retained=next(c for c in examples if c['inputs']['selector']==13
                      and c['inputs']['count']==14 and c['inputs']['aids']==[15,9])
        self.assertEqual((retained['after_ingest']['selector'],retained['after_ingest']['count']),(13,5))
        self.assertEqual((retained['after_selector']['mapped'],retained['after_selector']['response']),(100,4))
        for stage,changed in ((2,0),(130,1)):
            c=next(c for c in examples if c['inputs']['aids']==[9]
                   and c['inputs']['staged_selector']==stage and c['inputs']['selector']==2
                   and c['inputs']['count']==11 and not c['inputs']['blocked'])
            self.assertEqual(c['after_ingest']['changed'],changed)

    def test_scripted_boundary_and_recorded_reference(self):
        for c in self.emu['examples']:
            x=c['inputs']
            expected,post=updates(**{k:v for k,v in x.items()})
            self.assertEqual(c['after_ingest'],expected)
            self.assertEqual(c['after_selector'],post)
            self.assertEqual(len(c['scripted_receive']),1)
            self.assertEqual(c['scripted_receive'][0]['aids'],x['aids'])
            if x['receive_status']!=1:
                self.assertEqual(c['ingest_writes'],[])

    def test_dispatch_table_byte_classification(self):
        ledger=load('image_coverage_ledger.json')
        self.assertEqual(ledger['classification_bytes']['aid_validation_dispatch_table'],436)
        rows=[r for r in ledger['ranges'] if r['classification']=='aid_validation_dispatch_table']
        self.assertEqual(min(int(r['start'],0) for r in rows),0x608C)
        self.assertEqual(max(int(r['end'],0) for r in rows),0x6240)

    def test_model_rejects_unreviewed_domain(self):
        for aids in ([10],[226],[9]*15):
            with self.assertRaises(ValueError):
                updates(aids,0,11,2,11,10,0)
        with self.assertRaises(ValueError):
            updates([9],256,11,2,11,10,0)
