"""Pin the composed AIC setup evidence and untouched-slot boundary."""
import json
import unittest

from tests._paths import ROOT


class AicVectorInstallation(unittest.TestCase):
    def test_programmed_vectors_and_untouched_slot31(self):
        doc=json.loads((ROOT/'audit/data/aic_vector_installation.json').read_text())
        self.assertEqual(doc['raw_sha256'],'1ae519ba6194e8f7bdaaa94333a83a9e6fda3b0563f87f7d48383b37288c1780')
        self.assertEqual((doc['case_count'],doc['segments_per_case']),(16,7))
        self.assertEqual(len(doc['literal_address_seeds']),10)
        self.assertEqual(len(doc['installed_source_entries']),9)
        self.assertEqual(len(doc['all_written_source_entries']),10)
        for case in doc['cases']:
            vectors=[int(v,0) for v in case['final_vectors']]
            self.assertEqual(len(vectors),32)
            self.assertEqual(vectors[0],0x40E0)
            self.assertEqual(vectors[31],int(case['seed'],0)+31)
            self.assertEqual([vectors[i] for i in (2,5,6,12,13,14)],[0x7449,0x6B45,0x7179,0x6C49,0x6C69,0x6C95])
            self.assertEqual(case['spurious_vector'],'0x7445')
            self.assertEqual(case['vector_write_count'],39)
            self.assertEqual([len(p['vector_writes']) for p in case['phases']],[32,0,1,1,3,1,1])
            pio=next(p for p in case['phases'] if p['phase']=='pio_prefix')
            self.assertEqual((pio['stop'],pio['stack_pointer_after_segment']),('0x757a','0x202ff4'))


if __name__=='__main__':unittest.main()
