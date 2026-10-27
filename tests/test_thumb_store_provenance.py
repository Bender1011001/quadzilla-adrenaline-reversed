"""All selected stores remain represented, including unresolved obligations."""
import json
import unittest
from tests._paths import ROOT


class ThumbStoreProvenance(unittest.TestCase):
    def setUp(self):
        self.doc = json.loads((ROOT / 'audit/data/thumb_store_provenance.json').read_text())

    def test_selected_domain_and_all_store_statuses(self):
        d = self.doc
        self.assertEqual(d['selected_instruction_starts'], 6813)
        self.assertEqual(d['reachable_starts'], 6813)
        self.assertEqual(len(d['entry_roots']), 118)
        self.assertEqual(len(d['stores']), 1039)
        self.assertEqual(d['status_counts'], {'stack-relative': 137, 'fixed': 805, 'unresolved': 97})
        self.assertEqual(len(d['excluded_store_sites']), 24)
        self.assertEqual(d['unsupported_starts'], [])

    def test_percent_overlap_does_not_exclude_unknown_writers(self):
        d = self.doc
        self.assertEqual(d['conditional_fixed_percent_overlaps'], ['0x5b22'])
        unresolved = [s for s in d['stores'] if s['status'] == 'unresolved']
        self.assertEqual(len(unresolved), 97)
        self.assertTrue(any(s['site'] == '0x853c' for s in unresolved))
        self.assertTrue(any('no whole-image writer exclusion' in s for s in d['limits']))

    def test_dispatch_and_observation_evidence_stays_explicit(self):
        self.assertEqual({r['site'] for r in self.doc['bounded_dispatch_assumptions']},
                         {'0x4b80', '0x4c30', '0x608a', '0x809a'})
        self.assertTrue(self.doc['matched_observed_fixed_sites'])
        self.assertTrue(self.doc['callee_obligations'])
        self.assertTrue(self.doc['exit_obligations'])
        self.assertEqual(len(self.doc['frame_transfer_edges']), 18)


if __name__ == '__main__':
    unittest.main()
