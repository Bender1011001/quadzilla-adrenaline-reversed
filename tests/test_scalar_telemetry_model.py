"""Exercise arithmetic distinctions that a generic linear interpolation misses."""
import json
import sys
import unittest

from tests._paths import ROOT

sys.path.insert(0, str(ROOT / 'tools'))
from model_scalar_telemetry import calculate, caller_store, sdiv


def inputs(**changes):
    c = dict(mode=0, refresh=0, response_flags=[0]*4, gate_sum=[0, 0], selector=100,
             enabled=1, base=1000, capture=2000, knots=[200, 400, 600, 800, 1000],
             coefficient=20, response=50, threshold=0, working61=10, status=0,
             percent0=50, percent1=20, cell=30)
    c.update(changes)
    return c


class ScalarTelemetryContract(unittest.TestCase):
    def test_unsigned_cap_then_signed_floor(self):
        self.assertEqual(caller_store(0xFFFFFFFF, 0xFFFFFFFF), 1024)
        self.assertEqual(caller_store(0xFFFFFFFF, 3840), 3840)
        self.assertEqual(caller_store(2000, 500), 1024)
        self.assertEqual(caller_store(1500, 2000), 1500)
        self.assertEqual(sdiv(0xFFFFFFF9, 3), 0xFFFFFFFE)

    def test_bypass_and_knot_mutation(self):
        bypass = calculate(inputs(enabled=0))
        self.assertEqual((bypass['return'], bypass['cap'], bypass['knots']), (1000, 3840, [200, 400, 600, 800, 1000]))
        for x, result in ((999, 1000), (1000, 1000), (1004, 1002), (1499, 1200),
                          (1500, 1200), (2000, 1400), (3500, 1896)):
            case = calculate(inputs(mode=1, capture=x))
            self.assertEqual(case['return'], result)
            self.assertEqual(case['knots'], [200, 400, 600, 768, 896])

    def test_table_special_and_unsigned_subtraction(self):
        ordinary = calculate(inputs())
        self.assertEqual((ordinary['pre_subtraction'], ordinary['subtraction'], ordinary['return']), (272, 128, 144))
        self.assertEqual(calculate(inputs(cell=1))['return'], 266)
        negative = calculate(inputs(cell=128))
        self.assertGreater(negative['table_term'], 0x80000000)
        self.assertEqual((negative['subtraction'], negative['return']), (128, 144))
        special = calculate(inputs(threshold=51, status=51))
        self.assertEqual((special['special'], special['return'], special['subtraction']), (True, 533, 0))
        self.assertEqual(calculate(inputs(threshold=51, status=50))['return'], 405)

    def test_refresh_selects_mode_and_clears_flag(self):
        clean = calculate(inputs(refresh=1))
        self.assertEqual((clean['mode'], clean['refresh']), (1, 0))
        for i in range(4):
            flags = [0]*4
            flags[i] = 1
            dirty = calculate(inputs(refresh=1, mode=1, response_flags=flags))
            self.assertEqual((dirty['mode'], dirty['refresh']), (0, 0))

    def test_source_execution_evidence(self):
        d = json.loads((ROOT / 'audit/data/scalar_telemetry_emulation.json').read_text())
        self.assertEqual(d['raw_sha256'], '1ae519ba6194e8f7bdaaa94333a83a9e6fda3b0563f87f7d48383b37288c1780')
        self.assertEqual((d['cases'], d['mismatches'], len(d['visited']), d['unvisited']), (10312, 0, 349, []))
        for case in d['examples']:
            self.assertEqual(calculate(case['inputs']), case['reference'])
            self.assertEqual(case['actual']['return_value'], case['reference']['return'])
            for field in ('mode', 'refresh', 'knots', 'cap', 'caller_store'):
                self.assertEqual(case['actual'][field], case['reference'][field])


if __name__ == '__main__':
    unittest.main()
