"""Check guarded scalar axes and original whole-control integration evidence."""
import importlib.util
import json
import sys
import unittest

from tests._paths import ROOT

sys.path.insert(0, str(ROOT / 'audit/tools'))
spec = importlib.util.spec_from_file_location('control_scalar_integration', ROOT / 'audit/tools/emulate_control_scalar_integration.py')
integration = importlib.util.module_from_spec(spec)
spec.loader.exec_module(integration)


class ControlScalarIntegration(unittest.TestCase):
    def test_finite_division_branch_bound(self):
        for denominator in range(256):
            for value in range(denominator+1):
                row, column = integration.axes(value, denominator, 100)
                self.assertTrue(0 <= row <= 19)
                self.assertEqual(column, 19)
            self.assertEqual(integration.axes(denominator+1, denominator, 101), (19, 19))

    def test_zero_and_high_word_axes(self):
        self.assertEqual(integration.axes(0, 0, 0), (0, 0))
        self.assertEqual(integration.axes(1, 0, 50), (19, 9))
        self.assertEqual(integration.axes(0xFFFFFFFF, 255, 0xFFFFFFFF), (19, 19))
        self.assertEqual(integration.axes(255, 255, 1), (19, 0))

    def test_complete_calls_and_explicit_coverage_limits(self):
        d = json.loads((ROOT / 'audit/data/control_scalar_integration.json').read_text())
        self.assertEqual(d['raw_sha256'], '1ae519ba6194e8f7bdaaa94333a83a9e6fda3b0563f87f7d48383b37288c1780')
        self.assertEqual((d['cases'], d['reference_mismatches']), (325, 0))
        self.assertEqual((len(d['main_starts_visited']), len(d['main_starts_unvisited'])), (495, 79))
        self.assertEqual(d['timer_counts'], {'calls': 197, 'writes': 105})
        self.assertEqual(len(d['summary']), 325)
        for row in d['summary']:
            self.assertTrue(all(0 <= a <= 19 for a in row['scalar_axes']))
        self.assertEqual((d['initial_scalar_table']['high_bit_count'], d['initial_scalar_table']['maximum']), (0, 100))

    def test_integrated_scalar_and_counter_examples(self):
        d = json.loads((ROOT / 'audit/data/control_scalar_integration.json').read_text())
        counters = {249: (250, 1), 999999: (1000000, 1), 1000001: (1, 0),
                    0xFFFFFFFF: (0, 1), 0x80000000: (0x80000001, 0)}
        for c in d['examples']:
            s = c['scalar']
            self.assertEqual(s['actual']['return_value'], s['reference']['return'])
            self.assertEqual(s['telemetry_store'], s['reference']['caller_store'])
            self.assertEqual(c['return'], s['inputs']['selector'])
            if 'counter' in c['inputs']:
                self.assertEqual((c['counter_after'], c['backdown_calls']), counters[c['inputs']['counter']])
            self.assertEqual([w['value'] for w in c['timer_writes']],
                             [t['value'] for t in c['timer_calls'] if not t['clock_enabled']])


if __name__ == '__main__':
    unittest.main()
