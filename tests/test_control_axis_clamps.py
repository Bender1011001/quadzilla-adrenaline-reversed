"""Alternate-axis bound, history narrowing and directed timer-clamp evidence."""
import json
import unittest
from tests._paths import ROOT


class ControlAxisClamps(unittest.TestCase):
    def setUp(self):
        self.doc = json.loads((ROOT / 'audit/data/control_axis_clamps.json').read_text())

    def test_axis_contract_and_256_history_narrowing(self):
        self.assertEqual(len(self.doc['cases']), 265)
        for c in self.doc['cases']:
            a = c['axis']
            t, d, k = a['target'], a['denominator'], a['offset']
            expected = 19 if t > d+k else 0 if t < k or d == 0 else 19*t//d-19*k//d
            self.assertEqual(a['actual'], expected)
            self.assertTrue(0 <= a['actual'] <= 19)
            self.assertEqual(a['stored_history'], t & 255)
            self.assertEqual(c['stretch']['actual'], c['stretch']['expected'])
        self.assertEqual(self.doc['cases'][-1]['axis'],
                         {'target': 256, 'denominator': 255, 'offset': 1,
                          'expected': 19, 'actual': 19, 'stored_history': 0})

    def test_timer_clamp_boundaries_and_original_admission(self):
        directed = [c for c in self.doc['cases'] if c['entry']['kind'] == 'clamp']
        self.assertEqual(len(directed), 14)
        for c in directed:
            v = c['entry']['requested']
            expected = min(2730, max(410, v))
            events = [e for e in c['events'] if e['site'] == '0x5382']
            self.assertEqual([(e['clamp_input'], e['clamp_output']) for e in events], [(v, expected)])
            self.assertEqual(c['timer_calls'][0]['value'], hex(24*expected+3))
            self.assertEqual(len(c['timer_writes']), int(not c['entry']['clock_enabled']))

    def test_instruction_union_is_complete_without_path_claim(self):
        self.assertEqual(self.doc['combined_main_starts'], 574)
        self.assertEqual(len(self.doc['new_main_starts']), 19)
        self.assertEqual(self.doc['remaining_main_starts'], [])
        self.assertTrue(any('not exhaustive' in s for s in self.doc['limits']))


if __name__ == '__main__':
    unittest.main()
