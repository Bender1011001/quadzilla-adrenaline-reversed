"""Review direct copy/fill extents and resolved AID data-store bounds."""
import json
import unittest

from tests._paths import ROOT


class GenericWriterFootprints(unittest.TestCase):
    def setUp(self):
        self.doc = json.loads((ROOT / 'audit/data/generic_writer_footprints.json').read_text())

    def test_descriptor_and_direct_call_ranges(self):
        d = self.doc
        self.assertEqual(d['raw_sha256'], '1ae519ba6194e8f7bdaaa94333a83a9e6fda3b0563f87f7d48383b37288c1780')
        self.assertEqual([(r['destination'], r['byte_count'], r['end_exclusive']) for r in d['descriptor_operations']],
                         [('0x200000', 2208, '0x2008a0'), ('0x2008a0', 994, '0x200c82'), ('0x200c84', 164, '0x200d28')])
        self.assertEqual({r['site'] for r in d['direct_copy_fill_calls']}, {'0x4128', '0x413e', '0x5f22'})
        self.assertEqual((d['config_copy']['destination'], d['config_copy']['end_exclusive']), ('0x2006cc', '0x2006f8'))

    def test_all_byte_aid_resolved_ranges(self):
        d = self.doc
        self.assertEqual((d['walker_cases'], d['mapped_in_bounds_aids'], len(d['rows'])), (768, 82, 256))
        for row in d['rows']:
            self.assertEqual(row['table1_slot_in_bounds'], row['aid'] < 255)
            self.assertEqual(row['observed_store_count'], row['maximum_single_value_bytes'])
            if int(row['pointer'], 0):
                self.assertTrue(0x200AEC <= int(row['pointer'], 0) < int(row['end_exclusive'], 0) <= 0x200BC7)
        self.assertEqual(d['rows'][255]['pointer'], '0x200bba')
        self.assertEqual(d['rows'][255]['end_exclusive'], '0x200bc7')
        self.assertEqual(d['rows'][226]['end_exclusive'], '0x200af9')

    def test_zero_variable_count_still_writes_and_budget_bounds_it(self):
        for aid in (226, 255):
            cases = [r for r in self.doc['variable_count_examples'] if r['aid'] == aid]
            for c in cases:
                self.assertEqual(len(c['writes']), min(c['count'], 13) if c['count'] else 13)
            self.assertEqual(next(c for c in cases if c['count'] == 0)['status'], 2)
            self.assertEqual(next(c for c in cases if c['count'] == 13)['status'], 1)
            self.assertEqual(next(c for c in cases if c['count'] == 14)['status'], 2)


if __name__ == '__main__':
    unittest.main()
