"""Original percent producer, retention and same-cycle index evidence."""
import json
import unittest
from tests._paths import ROOT


class CapturePercentControl(unittest.TestCase):
    def setUp(self):
        self.doc = json.loads((ROOT / 'audit/data/capture_percent_control.json').read_text())

    def test_every_payload_byte_reaches_original_control(self):
        cases = self.doc['cases'][:512]
        self.assertEqual({(c['input']['value'], c['input']['dlc']) for c in cases},
                         {(v, d) for v in range(256) for d in (0, 8)})
        for c in cases:
            expected = min(4*c['input']['value']//10, 100)
            self.assertEqual(c['percent_after'], expected)
            self.assertEqual(c['stores'][0]['site'], '0x5b22')
            self.assertEqual(c['ordered_events'][0]['kind'], 'write')
            self.assertEqual(c['scalar_column'], 19*expected//100)
            self.assertEqual(c['response_percent_byte'], expected)
            self.assertTrue({'0x5202', '0x5210'} <= {r['site'] for r in c['reads']})

    def test_dlc_zero_does_not_prevent_completed_buffer_parse(self):
        for zero, eight in zip(self.doc['cases'][:512:2], self.doc['cases'][1:512:2]):
            self.assertEqual(zero['percent_after'], eight['percent_after'])
            self.assertEqual(zero['scalar_column'], eight['scalar_column'])
            self.assertEqual(zero['response_percent_byte'], eight['response_percent_byte'])

    def test_retention_does_not_inherit_successful_writer_bound(self):
        retained = self.doc['cases'][512:]
        self.assertEqual(len(retained), 6)
        for c in retained:
            old = c['input']['retained']
            self.assertEqual(c['stores'], [])
            self.assertEqual(c['percent_after'], old)
            self.assertTrue(all(r['value'] == old for r in c['reads']))
            self.assertEqual(c['scalar_column'], 19 if old > 100 else 19*old//100)
            self.assertEqual(c['response_percent_byte'], old & 255)


if __name__ == '__main__':
    unittest.main()
