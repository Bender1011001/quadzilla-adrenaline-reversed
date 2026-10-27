"""Verify the raw/echo/scaled distinction and retained consumer mutations."""
import json
import sys
import unittest

from tests._paths import ROOT

sys.path.insert(0, str(ROOT / 'tools'))
from model_scalar_telemetry import caller_store


class KnotUpdateConsumers(unittest.TestCase):
    def setUp(self):
        self.doc = json.loads((ROOT / 'audit/data/knot_update_consumers.json').read_text())

    def test_composed_counts_and_all_sweep_transforms(self):
        d = self.doc
        self.assertEqual(d['raw_sha256'], '1ae519ba6194e8f7bdaaa94333a83a9e6fda3b0563f87f7d48383b37288c1780')
        self.assertEqual((d['sequences'], d['complete_control_calls'], d['ingest_calls'], d['reader_calls'], d['mismatches']), (306, 1224, 918, 3060, 0))
        self.assertEqual(len(d['summary']), 306)
        for c in d['summary']:
            scaled = [128*v//10 for v in c['raw']]
            self.assertTrue(all(0 <= v <= 300 for v in c['raw']))
            self.assertEqual(c['scaled_before'], scaled)
            self.assertEqual(c['scaled_after'], [min(v, cap) for v, cap in zip(scaled, (384, 512, 640, 768, 896))])
            self.assertEqual(c['scaled_restored'], scaled)
            self.assertTrue(1024 <= c['telemetry_before_reapply'] <= 3840)
            self.assertTrue(1024 <= c['telemetry_after_reapply'] <= 3840)

    def test_same_readback_and_different_consumer_result(self):
        c = next(c for c in self.doc['examples'] if c['staged_knots'] == [100]*5)
        self.assertEqual(c['after_mode0_control']['scaled_knots'], [384, 512, 640, 768, 896])
        self.assertEqual(c['after_restored_control']['scaled_knots'], [1280]*5)
        self.assertEqual((c['mode0_scalar']['telemetry_store'], c['restored_scalar']['telemetry_store']), (1024, 1268))
        self.assertEqual(c['readers'], c['restored_readers'])
        self.assertEqual(c['readers'][0]['payload'], '896400')
        self.assertEqual([len(b['aids']) for b in c['scripted_receive']], [9, 1, 5])

    def test_flag_mode_and_instruction_write_provenance(self):
        c = next(c for c in self.doc['examples'] if c['staged_knots'] == [300]*5)
        self.assertEqual((c['after_update']['refresh'], c['after_mode1_control']['mode'], c['after_mode0_control']['mode']), (1, 1, 0))
        stores = [w for w in c['knot_writes'] if w['phase'] == 'nonzero_mode_control' and 0x200458 <= int(w['address'], 0) < 0x20046C]
        self.assertEqual([w['site'] for w in stores], ['0x4db6', '0x4dc2', '0x4dce', '0x4dda', '0x4de6'])
        self.assertEqual([int(w['value'], 0) for w in stores], [384, 512, 640, 768, 896])

    def test_cap_closes_output_bound_under_reviewed_writer_range(self):
        for cap in range(3841):
            for result in (0, 1023, 1024, 3840, 0x80000000, 0xFFFFFFFF):
                self.assertTrue(1024 <= caller_store(result, cap) <= 3840)


if __name__ == '__main__':
    unittest.main()
