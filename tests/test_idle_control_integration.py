"""Pin gate ordering, fresh consumption and caller saturation evidence."""
import json
import unittest
from tests._paths import ROOT


class IdleControlIntegration(unittest.TestCase):
    def setUp(self):
        self.doc = json.loads((ROOT / 'audit/data/idle_control_integration.json').read_text())

    def test_original_gate_overwrites_entry_active_flag(self):
        self.assertEqual(len(self.doc['cases']), 144)
        self.assertEqual(sum(c['active_after'] for c in self.doc['cases']), 24)
        for c in self.doc['cases']:
            self.assertEqual(c['gate']['actual'], c['gate']['expected'])
            self.assertEqual(c['accumulator'] is not None, c['active_after'] == 1)
            if c['entry']['selector'] == 5:
                self.assertEqual(c['active_after'], 0)

    def test_transition_defers_consumption_until_next_control_call(self):
        seqs = self.doc['persistent_two_call_sequences']
        self.assertEqual(len(seqs), 3)
        self.assertEqual(self.doc['full_control_calls'], 150)
        for s in seqs:
            self.assertIsNone(s['first']['accumulator'])
            self.assertEqual(s['first']['gate']['actual']['0x20042c'], 3)
            self.assertEqual(s['first']['gate']['actual']['0x20042d'], 0)
            self.assertEqual(s['first']['gate']['actual']['0x20071e'], 1)
            acc = s['second']['accumulator']
            self.assertEqual(acc['actual'], acc['expected'])
            self.assertEqual(acc['actual'][3], [1, 1, 0])
        self.assertEqual([s['second']['accumulator']['caller_store'] for s in seqs], [206, 650, 205])

    def test_stale_accumulator_and_caller_have_different_bounds(self):
        stale = [c['accumulator'] for c in self.doc['cases']
                 if c['accumulator'] and c['accumulator']['inputs'][0] == 0xFFFFFFFF
                 and c['accumulator']['inputs'][3] == 0]
        self.assertTrue(stale)
        for a in stale:
            self.assertEqual(a['actual'][0], 0xFFFFFFFF)
            self.assertEqual(a['caller_store'], 4095)
        self.assertEqual(self.doc['combined_main_starts'], 520)
        self.assertEqual(len(self.doc['new_main_starts']), 13)
        self.assertIn('0x55e4', self.doc['remaining_main_starts'])


if __name__ == '__main__':
    unittest.main()
