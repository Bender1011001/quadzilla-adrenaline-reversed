"""Pin variable counts, caller completion and original short-value admission."""
import hashlib
import json
import unittest
from tests._paths import ROOT
from model_payload_walker import walk,width
from x2com_crc import crc8


def load(name):
    return json.loads((ROOT/'audit/data'/name).read_text(encoding='utf-8'))


class PayloadWalker(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.emu=load('payload_walker_emulation.json')
        cls.chain=load('short_value_admission.json')

    def test_source_bounds_and_complete_helper_coverage(self):
        main=load('payload_walker_binaryninja.json')
        context=load('short_value_context_binaryninja.json')
        self.assertEqual(self.emu['raw_sha256'],main['raw_sha256'])
        self.assertEqual(self.emu['raw_sha256'],self.chain['raw_sha256'])
        self.assertEqual(context['raw_sha256'],main['raw_sha256'])
        ins=[i for r in main['ranges'] for i in r['instructions']]
        self.assertEqual((len(ins),sum(i['length'] for i in ins)),(226,460))
        self.assertEqual({i['address'] for i in ins},set(self.emu['visited']))
        ida={i['start']:i for i in load('ida_image_items.json')['items']}
        for i in ins:
            self.assertEqual(int(ida[i['address']]['end'],0),int(i['address'],0)+i['length'])
        header=[i for r in context['ranges'] if r['start'] in ('0x7bcc','0x7be8','0x7bf0') for i in r['instructions']]
        self.assertEqual((len(header),sum(i['length'] for i in header)),(19,40))
        self.assertEqual({i['address'] for i in header},set(self.chain['header_helpers']['visited']))
        self.assertEqual(self.emu['reference_mismatches'],0)
        self.assertEqual(sum(self.emu['call_totals'].values()),8834)

    def test_header_boundary_corrections(self):
        doc=load('payload_header_boundaries.json')
        self.assertEqual(doc['raw_sha256'],self.emu['raw_sha256'])
        self.assertEqual(doc['ordinary_matching_starts'],17)
        self.assertEqual(doc['unexplained_boundary_mismatches'],[])
        self.assertEqual({r['entry'] for r in doc['corrections']},{'0x7be8','0x7bf0'})
        for r in doc['corrections']:
            self.assertEqual((r['prefix_halfword'],r['entry_halfword']),('0xffff','0x7800'))
            self.assertTrue(r['direct_call_sites'])

    def test_variable_count_includes_itself_and_zero_wraps(self):
        pointer=0x200AEC
        for count in range(256):
            result=walk(bytes([226,count]),{226:pointer})
            self.assertEqual(result.writes,[(pointer,count)])
            self.assertEqual(result.status,1 if count==1 else 2)
            self.assertEqual(result.remaining,(count-1)&255)
        for length in range(1,14):
            result=walk(bytes([226,length])+bytes(length-1),{226:pointer})
            self.assertEqual((result.status,len(result.writes),result.reported),(1,length,[226]))
        rows=[r for r in self.emu['examples'] if r['payload']=='e201' and r['kind_arg']==1]
        self.assertTrue(rows)
        self.assertTrue(all(r['status']==1 and r['reported']==[226] for r in rows))

    def test_local_lookahead_and_guard_fault(self):
        for aid in (9,85,154,226):
            result=walk(bytes([aid]),{aid:0x200AEC},lookahead=5)
            self.assertEqual(result.reads,[0,1])
            self.assertEqual(result.writes,[])
        guard=self.emu['lookahead_guard']
        self.assertEqual(guard['result']['status'],'emulator_fault')
        self.assertEqual(guard['result']['fault']['address'],'0x211000')
        self.assertEqual(guard['result']['fault']['pc'],'0x7d40')
        self.assertEqual(guard['writes'],[])

    def test_caller_r7_readlists_empty_and_count_truncation(self):
        for incoming in (0,1,255,256,0xFFFFFFFF):
            expected=1 if incoming&255==0 else 2
            self.assertEqual(walk(b'',{},incoming_r7=incoming).status,expected)
            for kind in (2,4):
                result=walk(b'\xff\x00\xe2',{},kind,incoming_r7=incoming)
                self.assertEqual((result.status,result.reported,result.writes),(expected,[255,0,226],[]))
        self.assertEqual(walk(bytes([9,1])*8,{9:0x200B00},count_arg=0xFFFFFFFF).reported,[9]*7)
        self.assertEqual(walk(bytes([9,1]),{9:0x200B00},count_arg=256).reported,[])
        self.assertEqual(width(220,0xFFFFFFFF),0xFFFFFFFF)
        self.assertEqual(width(219,0xFFFFFFFF),4)
        for r in self.emu['frame_cases']:
            frame=bytes.fromhex(r['frame'])
            if frame[0]&15 and crc8(frame)==0x3B and frame[0]>>4 in (2,4):
                self.assertEqual(r['status'],1 if (frame[0]&15)==1 else 2)
                self.assertFalse(any(int(w['address'],0)<0x201000 for w in r['writes']))

    def test_header_and_crc_envelope_campaign(self):
        helper=self.chain['header_helpers']
        self.assertEqual(helper['getter_cases'],512)
        digest=hashlib.sha256()
        for byte in range(256):
            digest.update(bytes([byte>>4,byte&15]))
        self.assertEqual(helper['getter_output_sha256'],digest.hexdigest())
        self.assertEqual(len(helper['envelope_cases']),96)
        for r in helper['envelope_cases']:
            self.assertEqual(r['status'],3 if crc8(bytes.fromhex(r['frame']))==0x3B else 4)
        zero=next(r for r in self.emu['frame_cases'] if r['frame']=='10')
        self.assertEqual((zero['status'],zero['type_out'],zero['reported']),(5,6,[]))

    def test_original_receive_admission_applies_failed_staging(self):
        self.assertEqual(self.chain['function_stubs'],[])
        first,second,corrupt,empty=self.chain['sequence'][:4]
        self.assertEqual([r['receive_status_at_ingest_gate'] for r in self.chain['sequence']],[2,1,4,1,1])
        self.assertEqual(first['staging226'],'0002040a00')
        self.assertEqual(second['staging226'],'0102040a00')
        self.assertEqual(first['working226'],{'mode':0,'selection':0,'coefficient_f32_bits':'0x3f000000'})
        self.assertEqual(second['working226'],{'mode':2,'selection':4,'coefficient_f32_bits':'0x3f800000'})
        self.assertNotIn('0x66ac',first['original_entry_calls'])
        self.assertIn('0x66ac',second['original_entry_calls'])
        for at in ('0x8038','0x7bcc','0x7e64','0x7cc4'):
            self.assertIn(at,second['original_entry_calls'])
        self.assertEqual(corrupt['working226'],second['working226'])
        self.assertEqual(corrupt['original_entry_calls'],['0x8038','0x7bcc'])
        self.assertEqual(empty['working226'],second['working226'])
        self.assertTrue(all(crc8(bytes.fromhex(r['frame']))==0x3B for r in (first,second,empty)))

    def test_oversized_variable_value_reaches_separately_used_status_byte(self):
        record=self.chain['sequence'][4]
        self.assertEqual(record['frame'],'1fe20d00000a00a5a5a5a5a5a5a55a68')
        self.assertEqual(record['receive_status_at_ingest_gate'],1)
        self.assertEqual(record['staging226_extended'],'0d00000a00a5a5a5a5a5a5a55a')
        self.assertEqual(record['numeric_status_byte'],0x5A)
        self.assertTrue(any(w=={'pc':'0x7d6c','address':'0x200af8','size':1,'value':0x5A}
                            for w in record['writes']))
        self.assertIn('0x66ac',record['original_entry_calls'])

    def test_model_rejects_absent_declared_bytes(self):
        with self.assertRaises(ValueError):
            walk(b'\x09',{},count_arg=2)
