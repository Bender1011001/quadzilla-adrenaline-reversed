"""Response-source, ratio and filter evidence inside original complete calls."""
import json
import unittest
from tests._paths import ROOT


class FullControlResponses(unittest.TestCase):
    def setUp(self):
        self.doc = json.loads((ROOT / 'audit/data/full_control_responses.json').read_text())

    def test_complete_response_snapshot_agrees_with_model(self):
        self.assertEqual(len(self.doc['cases']), 288)
        self.assertEqual(self.doc['function_stubs'], [])
        for c in self.doc['cases']:
            r = c['response']
            self.assertEqual(r['actual_bytes'], r['expected']['bytes'])
            self.assertEqual(r['actual_derived'], r['expected']['derived'])
            self.assertEqual(r['actual_filters'], [r['expected']['filter0'], r['expected']['filter1']])

    def test_finite_sources_include_overflow_negative_and_signed_zero(self):
        self.assertEqual({c['response']['expected']['ratio_integer'] for c in self.doc['cases']},
                         {3, 0xFFFFFFFD, 0x7FFFFFFF, 0})
        self.assertEqual({c['response']['expected']['sample'] for c in self.doc['cases']}, {0, 268, 9999})
        for c in self.doc['cases']:
            r = c['response']
            self.assertEqual(r['inputs']['previous_response'], c['entry']['previous_response'])
            self.assertEqual(r['actual_bytes']['0x200bc3'], 80)

    def test_filter_enable_is_exactly_one_and_coverage_is_bounded(self):
        for c in self.doc['cases']:
            expected = 4 if c['entry']['filter_enable'] == 1 else 160
            self.assertEqual(c['response']['actual_bytes']['0x200bc1'], expected)
        self.assertEqual(self.doc['combined_main_starts'], 555)
        self.assertEqual(len(self.doc['new_main_starts']), 29)
        self.assertEqual(len(self.doc['remaining_main_starts']), 19)


if __name__ == '__main__':
    unittest.main()
