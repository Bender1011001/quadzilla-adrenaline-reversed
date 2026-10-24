"""Pin scalar widths, shared-frame entries and completed local handler accounts."""
import json
import unittest

from tests._paths import ROOT
from model_remaining_updates import HANDLERS,SPECS,coefficient,writes_for


def load(name):
    return json.loads((ROOT/'audit/data'/name).read_text(encoding='utf-8'))


class RemainingUpdates(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.emu=load('remaining_update_emulation.json')
        cls.bn=load('remaining_update_binaryninja.json')

    def test_source_bounds_and_all_local_handler_dispositions(self):
        self.assertEqual(self.emu['raw_sha256'],self.bn['raw_sha256'])
        self.assertEqual(self.emu['raw_sha256'],load('semantic_labels.json')['raw_sha256'])
        ins=[i for r in self.bn['ranges'] for i in r['instructions']]
        self.assertEqual((len(ins),sum(i['length'] for i in ins)),(582,1218))
        self.assertEqual({i['address'] for i in ins},set(self.emu['visited']))
        ida={r['start']:r for r in load('ida_image_items.json')['items']}
        macro=load('remaining_update_ida_macros.json')
        explained=set(macro['explained_explicit_starts'])
        differences=set()
        for i in ins:
            if i['address'] not in ida or int(ida[i['address']]['end'],0)!=int(i['address'],0)+i['length']:
                differences.add(i['address'])
        self.assertEqual(differences,explained)
        self.assertEqual((len(macro['macro_items']),len(explained),macro['ordinary_matching_starts']),(7,14,568))
        self.assertEqual(macro['unexplained_boundary_mismatches'],[])
        self.assertEqual(macro['raw_sha256'],self.emu['raw_sha256'])
        self.assertEqual({r['start'] for r in macro['macro_items']},
                         {'0x6534','0x6562','0x6586','0x65b4','0x65d8','0x6686','0x67dc'})
        for r in macro['macro_items']:
            self.assertEqual(sum(i['length'] for i in r['explicit_instructions']),4)
            self.assertEqual(ida[r['start']]['end'],r['end'])
        dispatch=load('aid_validation_dispatch.json')
        self.assertEqual((dispatch['reviewed_nondefault_handlers'],dispatch['pending_nondefault_handlers']),(57,0))
        self.assertEqual({r['aid'] for r in dispatch['rows'] if
            r['handler_review']=='docs/REMAINING_AID_UPDATE_REVIEW.md'},set(HANDLERS))
        self.assertEqual(len(HANDLERS),44)
        self.assertEqual(self.emu['reference_mismatches'],0)
        self.assertEqual(sum(self.emu['call_totals'].values()),22703)

    def test_full_parent_body_and_four_continuation_roles(self):
        rows=[r for r in load('reviewed_instruction_ranges.json')['ranges']
              if r['entry'] in ('0x601c','0x6042','0x6048','0x604c','0x604e')]
        ranges=sorted((int(r['start'],0),int(r['end'],0)) for r in rows)
        self.assertEqual(sum(b-a for a,b in ranges),1882)
        merged=[]
        for a,b in ranges:
            if merged and merged[-1][1]==a:
                merged[-1]=(merged[-1][0],b)
            else:
                merged.append((a,b))
        self.assertEqual(merged,[(0x601C,0x608C),(0x6240,0x63AC),(0x63F0,0x6702),(0x67DC,0x6A48)])
        labels={r['entry']:r for r in load('semantic_labels.json')['labels']}
        for at in ('0x6042','0x6048','0x604c','0x604e'):
            self.assertIn('docs/REMAINING_AID_UPDATE_REVIEW.md',labels[at]['evidence'])

    def test_scalar_source_and_echo_bindings(self):
        rows=load('aid_validation_dispatch.json')['rows']
        self.assertEqual(len(self.emu['scalar_contracts']),42)
        for r in self.emu['scalar_contracts']:
            self.assertEqual(r['staging'],rows[r['aid']]['staging_pointer'])
            self.assertEqual(r['echo'],rows[r['aid']]['response_pointer'])
            self.assertEqual(r['transport_bytes'],1 if r['aid']<75 else 2)
        for aid in range(113,137):
            s=SPECS[aid]
            i=aid-113
            self.assertEqual((s[0],s[1],s[2],s[4],s[5]),(0x200B3B+2*i,1,0x200598+i,0x200C07+2*i,1))

    def test_original_upper_byte_retention_and_reader(self):
        rows=[r for r in self.emu['examples'] if 'reader' in r]
        self.assertEqual(len(rows),324)
        self.assertEqual({r['aid'] for r in rows},set(range(110,137)))
        for r in rows:
            expected=writes_for(r['aid'],r['value'],r['low_setting'])[0][2]
            self.assertEqual(r['reader']['result'],{'status':'returned','r0':3})
            self.assertEqual(bytes.fromhex(r['reader']['buffer'])[:3],bytes([r['aid'],expected,0xA7]))

    def test_coupled_rule_and_wide_clamp_boundaries(self):
        for value,low,expected in ((0,5,10),(6,5,20),(25,25,30),(26,25,26),(41,25,40)):
            self.assertEqual(writes_for(22,value,low)[0][2],expected)
            case=next(r for r in self.emu['examples'] if r['aid']==22 and r['value']==value and r['low_setting']==low)
            self.assertEqual(case['writes'][0]['value'],expected)
        for aid,minimum,maximum in ((85,800,2200),(104,3200,3700)):
            for value in (0,minimum-1,minimum,maximum,maximum+1,65535):
                self.assertEqual(writes_for(aid,value)[0][2],min(max(value,minimum),maximum))

    def test_reset_gate_reuses_verified_initializer(self):
        rows=[r for r in self.emu['examples'] if r['aid']==24]
        reference=next(r for r in load('control_helper_emulation.json')['suites'] if r['entry']=='0x4384')['examples'][0]['writes']
        for r in rows:
            self.assertEqual(r['writes'],reference if r['value']==85 else [])
        self.assertEqual(self.emu['call_totals']['reset_gate'],256)

    def test_configuration_guards_coefficient_and_ignored_first_byte(self):
        self.assertEqual(self.emu['call_totals']['configuration226'],4576)
        rows=[r for r in self.emu['examples'] if r['aid']==226]
        grouped={}
        for r in rows:
            writes={w['address']:w['value'] for w in r['writes']}
            self.assertEqual('0x2006e6' in writes,r['mode']<3)
            self.assertEqual('0x2006e7' in writes,r['selection']<5)
            self.assertEqual('0x2006e8' in writes,r['value']!=0)
            if r['value']:
                self.assertEqual(writes['0x2006e8'],coefficient(r['value']))
            key=(r['mode'],r['selection'],r['value'])
            grouped.setdefault(key,{})[r['prefix']]=r['writes']
        for group in grouped.values():
            if set(group)=={0,4,255}:
                self.assertEqual(group[0],group[4])
                self.assertEqual(group[4],group[255])

    def test_model_rejects_unreviewed_domain(self):
        with self.assertRaises(ValueError):
            writes_for(154,0)
        with self.assertRaises(ValueError):
            coefficient(65536)
