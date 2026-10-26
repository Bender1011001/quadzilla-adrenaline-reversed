"""Check PC-write recognition and the committed indirect-target source audit."""
import importlib.util
import json
import sys
import unittest

from tests._paths import ROOT

sys.path.insert(0,str(ROOT/'audit/tools'))
spec=importlib.util.spec_from_file_location('indirect',ROOT/'audit/tools/audit_indirect_transfers.py')
indirect=importlib.util.module_from_spec(spec)
spec.loader.exec_module(indirect)


class IndirectTransfers(unittest.TestCase):
    def test_pc_write_forms_exclude_status_and_bx(self):
        self.assertEqual(indirect.pc_write_kind('thumb',0x448F),'high-register ADD/MOV PC')
        self.assertEqual(indirect.pc_write_kind('thumb',0x46F7),'high-register ADD/MOV PC')
        self.assertEqual(indirect.pc_write_kind('thumb',0xBD00),'POP PC')
        self.assertIsNone(indirect.pc_write_kind('thumb',0xB500))
        self.assertEqual(indirect.pc_write_kind('arm',0xE25EF004),'data-processing PC destination')
        self.assertEqual(indirect.pc_write_kind('arm',0xE8FD8000),'LDM including PC')
        self.assertEqual(indirect.pc_write_kind('arm',0xE59FF000),'LDR PC')
        self.assertIsNone(indirect.pc_write_kind('arm',0xE129F000))
        self.assertIsNone(indirect.pc_write_kind('arm',0xE12FFF10))

    def test_every_bx_has_local_source_disposition(self):
        doc=json.loads((ROOT/'audit/data/indirect_transfer_provenance.json').read_text())
        prior=json.loads((ROOT/'audit/data/execution_discovery_audit.json').read_text())
        self.assertEqual(doc['raw_sha256'],prior['raw_sha256'])
        self.assertEqual(doc['bx_count'],203)
        self.assertEqual({r['site'] for r in doc['bx_dispositions']},{r['site'] for r in prior['bx_sites']})
        self.assertEqual(doc['bx_kind_counts'],{'LR return-form':140,'stack-restored return-form':38,'fixed numeric veneer':16,
                                             'fixed startup/reset transfer':4,'ISA interworking veneer':3,'AIC-selected callback':2})
        tables=[r for r in doc['other_pc_writes'] if 'table_cases' in r]
        self.assertEqual([r['table_cases'] for r in tables],[29,10,218,6])
        self.assertEqual(len(doc['other_pc_writes']),6)
        self.assertEqual(doc['software_interrupt_sites'],[])


if __name__=='__main__':unittest.main()
