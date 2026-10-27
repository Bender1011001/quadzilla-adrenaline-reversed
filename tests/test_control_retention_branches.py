"""Retained-sample threshold, wrap and optional-floor evidence checks."""
import json
import unittest
from tests._paths import ROOT


class ControlRetentionBranches(unittest.TestCase):
    def setUp(self):
        self.doc = json.loads((ROOT / 'audit/data/control_retention_branches.json').read_text())

    def test_counter_predicates_and_wrap(self):
        cases = self.doc['cases']
        self.assertEqual(len(cases), 120)
        for c in cases:
            expected = ((c['old_count']+1) & 0xFFFFFFFF
                        if c['match'] == 'both' and c['capture'] >= 601 else 0)
            self.assertEqual(c['count_after'], expected)
        self.assertTrue(any(c['old_count'] == 0xFFFFFFFF and c['capture'] >= 601
                            and c['match'] == 'both' for c in cases))

    def test_optional_floor_and_timer_admission(self):
        clamps = [e for c in self.doc['cases'] for e in c['events'] if e['site'] == '0x5382']
        self.assertEqual(len(clamps), 24)
        for e in clamps:
            self.assertLess(e['clamp_input'], 410)
            self.assertEqual(e['clamp_output'], 410)
        for c in self.doc['cases']:
            self.assertEqual([t['value'] for t in c['timer_calls']],
                             [t['value'] for t in c['timer_writes']])

    def test_coverage_does_not_claim_reinitialization(self):
        self.assertEqual(self.doc['combined_main_starts'], 507)
        self.assertEqual(len(self.doc['new_main_starts']), 12)
        self.assertIn('0x55e4', self.doc['remaining_main_starts'])
        self.assertIn('0x52f0', self.doc['remaining_main_starts'])


if __name__ == '__main__':
    unittest.main()
