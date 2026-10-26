"""Validate committed original-byte gate execution and source coverage."""
import json
import unittest

from tests._paths import ROOT


class InputGateState(unittest.TestCase):
    def test_report_covers_body_and_boundary_behavior(self):
        report = json.loads((ROOT / 'audit/data/input_gate_emulation.json').read_text())
        decode = json.loads((ROOT / 'audit/data/input_gate_binaryninja.json').read_text())
        self.assertEqual(report['raw_sha256'], decode['raw_sha256'])
        self.assertEqual(report['cases'], 16390)
        self.assertEqual(report['mismatches'], [])
        starts = {i['address'] for i in decode['ranges'][0]['instructions'] if int(i['address'], 0) < 0x48C2}
        self.assertEqual(set(report['visited_addresses']), starts)
        self.assertEqual(len(starts), 85)
        self.assertEqual(len(report['literal_words']), 12)
        high_capture = next(x for x in report['examples'] if x['inputs'][:6] == [3, 1, 0, 0xFFFFFFFF, 0, 0])
        self.assertEqual(high_capture['result']['0x20042d'], 1)
        maximum_duration = next(x for x in report['examples'] if x['inputs'][-1] == 65535)
        self.assertEqual(maximum_duration['result']['0x200730'], 655350000)


if __name__ == '__main__':
    unittest.main()
