"""Check source-bound residual code dispositions and execution coverage."""
import json
import unittest

from tests._paths import ROOT


class ResidualCodeAdjudication(unittest.TestCase):
    def test_dispositions_preserve_code_data_and_execution_distinctions(self):
        doc=json.loads((ROOT/'audit/data/residual_code_adjudication.json').read_text())
        self.assertEqual(doc['raw_sha256'],'1ae519ba6194e8f7bdaaa94333a83a9e6fda3b0563f87f7d48383b37288c1780')
        self.assertEqual(doc['new_execution_cases'],519)
        self.assertEqual(len(doc['wrapper_reset_visited_starts']),39)
        self.assertEqual(len(doc['division_visited_starts']),69)
        self.assertEqual(len(doc['alignment_after_unconditional_transfer']),38)
        self.assertEqual(doc['interworking_nops'],['0x8566','0x8576','0x8586'])
        self.assertEqual(doc['ratio_table_range'],['0x9f88','0x9ff0'])
        reset=next(e for e in doc['examples'] if e['entry']=='0x7434')
        self.assertEqual(reset['writes'],[['0xfffffd00',4,'0xa500000d']])
        rx=next(e for e in doc['examples'] if e['entry']=='0x7b1c')
        self.assertIn(['0xfffc0104',4,'0x10'],rx['writes'])


if __name__=='__main__':unittest.main()
