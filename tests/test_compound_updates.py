"""Pin cross-AID staging, width-loss and compound handler evidence."""
import json
import unittest

from tests._paths import ROOT
from model_compound_updates import HANDLERS,apply


def load(name):
    return json.loads((ROOT/'audit/data'/name).read_text(encoding='utf-8'))


class CompoundUpdates(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.emu=load('compound_update_emulation.json')
        cls.bn=load('compound_update_binaryninja.json')

    def test_source_bounds_coverage_and_pending_handlers(self):
        self.assertEqual(self.emu['raw_sha256'],self.bn['raw_sha256'])
        self.assertEqual(self.emu['raw_sha256'],load('semantic_labels.json')['raw_sha256'])
        ins=[i for r in self.bn['ranges'] for i in r['instructions']]
        self.assertEqual((len(ins),sum(i['length'] for i in ins)),(227,458))
        self.assertEqual({i['address'] for i in ins},set(self.emu['visited']))
        ida={r['start']:r for r in load('ida_image_items.json')['items']}
        for i in ins:
            self.assertEqual(int(ida[i['address']]['end'],0),int(i['address'],0)+i['length'])
        self.assertEqual(self.emu['sweep_calls'],5632)
        self.assertEqual(self.emu['extra_ingest_calls'],39)
        self.assertEqual(self.emu['reference_mismatches'],0)
        dispatch=load('aid_validation_dispatch.json')
        self.assertEqual((dispatch['reviewed_nondefault_handlers'],dispatch['pending_nondefault_handlers']),(13,44))
        self.assertEqual({r['aid'] for r in dispatch['rows'] if
            r['handler_review']=='docs/COMPOUND_AID_UPDATE_REVIEW.md'},set(HANDLERS))

    def test_failed_partial_staging_applied_by_different_aid(self):
        seq=self.emu['cross_aid_sequence']
        first=seq['partial_walker']
        self.assertEqual((first['payload'],first['status'],first['reported_aids']),('924d',2,[146]))
        self.assertEqual(seq['failed_ingest']['writes'],[])
        self.assertEqual(seq['failed_ingest']['after']['0x2006f4'],10)
        second=seq['complete_walker']
        self.assertEqual((second['payload'],second['status'],second['reported_aids']),('9a000000',1,[154]))
        later=seq['later_ingest']
        self.assertEqual(later['aids'],[154])
        self.assertEqual(later['after']['0x2006f4'],77)
        self.assertEqual(later['after']['0x20073c'],0)
        self.assertEqual(later['after']['0x2006f5'],20)
        self.assertEqual(later['after']['0x200ac8'],later['before']['0x200ac8'])
        self.assertEqual(later['after']['0x200acc'],later['before']['0x200acc'])
        stores={w['address'] for w in later['writes']}
        self.assertEqual(stores,{'0x2006f4','0x20073c','0x200ac4'})

    def test_repeated_narrow_store_and_flag(self):
        cases=self.emu['repeated_narrow_store']
        self.assertEqual(len(cases),2)
        for c in cases:
            self.assertEqual(c['before']['0x2006d0'],52)
            self.assertEqual(c['after']['0x2006d0'],52)
            self.assertEqual(c['after']['0x200ac4'],1)
            self.assertEqual([(w['address'],w['size'],w['value']) for w in c['writes']],
                             [('0x2006d0',1,52),('0x200ac4',1,1)])

    def test_asymmetric_words_and_flag_bits(self):
        word_dest={150:'0x2006d8',151:'0x2006dc',152:'0x2006e0',153:'0x2006e4',154:'0x2006d0'}
        rows=self.emu['asymmetric_word_cases']
        self.assertEqual(len(rows),35)
        for c in rows:
            aid=c['aids'][0]
            expected=c['word_input'] & (255 if aid==154 else 65535)
            self.assertEqual(c['after'][word_dest[aid]],expected)
        for c in self.emu['examples']:
            if c['aids']==[152]:
                value=c['sweep_value']
                self.assertEqual(c['after']['0x2006df'],value&1)
                self.assertEqual(c['after']['0x2006de'],(value>>1)&1)

    def test_retained_accumulators_and_derived_values(self):
        for c in self.emu['examples']:
            aid=c['aids'][0]
            if aid==64:
                changed=c['before']['0x2006f6']!=c['after']['0x2006f6']
                for addr in ('0x200748','0x20074c'):
                    self.assertEqual(c['after'][addr],0 if changed else c['before'][addr])
            if aid in (146,154):
                changed=c['before']['0x2006f5']!=c['after']['0x2006f5']
                if changed:
                    q=c['after']['0x2006f5']*125//100
                    self.assertEqual(c['after']['0x200ac8'],q)
                    self.assertEqual(c['after']['0x200acc'],q*25//100)
                else:
                    self.assertEqual(c['after']['0x200ac8'],c['before']['0x200ac8'])

    def test_model_rejects_unreviewed_handlers(self):
        with self.assertRaises(ValueError):
            apply([226],{})
        with self.assertRaises(ValueError):
            apply([154]*15,{})
