"""Pin completed-buffer alias admission and subsequent original-cycle use."""
import json
import sys
import unittest

from tests._paths import ROOT

sys.path.insert(0, str(ROOT / 'tools'))
from x2com_crc import crc8


class Aid255ControlAdmission(unittest.TestCase):
    def setUp(self):
        self.doc = json.loads((ROOT / 'audit/data/aid255_control_admission.json').read_text())

    def test_crc_and_incomplete_width_are_distinct_boundaries(self):
        d = self.doc
        self.assertEqual(d['raw_sha256'], '1ae519ba6194e8f7bdaaa94333a83a9e6fda3b0563f87f7d48383b37288c1780')
        self.assertEqual(d['function_stubs'], [])
        self.assertEqual([c['receive_status'] for c in d['cases']], [4, 1, 2])
        for c in d['cases']:
            frame = bytes.fromhex(c['frame'])
            self.assertEqual((len(frame), frame[0]), (16, 0x1F))
            self.assertEqual(crc8(frame) == 0x3B, not c['corrupt_crc'])
            self.assertEqual(len(c['staging_stores']), 0 if c['corrupt_crc'] else 13)
            if not c['corrupt_crc']:
                self.assertEqual([int(w['address'], 0) for w in c['staging_stores']], list(range(0x200BBA, 0x200BC7)))
                self.assertTrue({'0x8038', '0x7bcc', '0x7e64', '0x7cc4'} <= set(c['original_receive_calls']))

    def test_consumer_values_and_later_automatic_overwrite(self):
        bad, good, incomplete = self.doc['cases']
        self.assertEqual([c['scalar']['inputs']['response'] for c in (bad, good, incomplete)], [7, 200, 200])
        self.assertEqual([c['response']['inputs']['previous_response'] for c in (bad, good, incomplete)], [3, 240, 240])
        self.assertEqual([c['scalar']['telemetry_store'] for c in (bad, good, incomplete)], [1041, 1280, 1280])
        self.assertEqual([c['response']['expected']['average'] for c in (bad, good, incomplete)], [313, 387, 387])
        for c in self.doc['cases']:
            self.assertEqual(c['after_control'], {'bc2': 100, 'bc3': 80})

    def test_scalar_and_response_models_agree_in_complete_cycles(self):
        for c in self.doc['cases']:
            self.assertEqual(c['scalar']['actual']['return_value'], c['scalar']['reference']['return'])
            self.assertEqual(c['scalar']['telemetry_store'], c['scalar']['reference']['caller_store'])
            self.assertEqual(c['response']['actual_bytes'], c['response']['expected']['bytes'])


if __name__ == '__main__':
    unittest.main()
