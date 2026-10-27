"""Counter-triggered original setup, caller epilogue and blocked path evidence."""
import json
import unittest
from tests._paths import ROOT


class ControlReinitialization(unittest.TestCase):
    def setUp(self):
        self.doc = json.loads((ROOT / 'audit/data/control_reinitialization.json').read_text())

    def test_threshold_and_caller_epilogue(self):
        self.assertEqual(self.doc['returned_cases'], 32)
        for c in self.doc['cases'][:-1]:
            s = c['inputs']
            triggered = s['old_count'] in (2000, 2001)
            self.assertEqual(c['outcome'], 'returned')
            self.assertEqual(c['stop_pc'], '0x3f00')
            self.assertEqual(c['recovery_byte_after'], (s['recovery_byte']+triggered) & 255)
            self.assertEqual(c['counter_after'], 2000 if s['old_count'] == 1999 else 0)
            self.assertEqual(c['setup_calls'],
                             ['0x74e8', '0x6fb4', '0x6bd8', '0x575c', '0x4330', '0x725c', '0x800c']
                             if triggered else [])

    def test_setup_writes_and_lookup_retention(self):
        for c in self.doc['cases'][:-1]:
            if c['setup_calls']:
                self.assertEqual(len(c['setup_writes']), 221)
                self.assertEqual(c['milestones'][0]['pin_sample'], 1-c['inputs']['pin17'])
                rc = [w for w in c['setup_writes'] if w['address'] == '0xfffa001c']
                self.assertEqual(rc, [{'site': '0x7018', 'address': '0xfffa001c', 'size': 4, 'value': '0x1b'}])
            else:
                self.assertEqual(c['setup_writes'], [])

    def test_no_ready_status_does_not_fake_setup_return(self):
        c = self.doc['cases'][-1]
        self.assertEqual(c['outcome'], 'instruction_budget')
        self.assertEqual(c['setup_calls'], ['0x74e8', '0x6fb4', '0x6bd8', '0x575c'])
        self.assertGreater(c['repeated_sites']['0x6b48'], 100)
        self.assertEqual(c['counter_after'], 2001)
        self.assertEqual(c['recovery_byte_after'], 0)
        self.assertEqual(c['milestones'], [])
        self.assertEqual(self.doc['combined_main_starts'], 526)


if __name__ == '__main__':
    unittest.main()
