"""Pin the conditional vector scratch/table alias without assuming a live boot."""
import json
import unittest

from tests._paths import ROOT


class VectorTableAlias(unittest.TestCase):
    def test_equal_branch_leaves_initialized_table_unchanged(self):
        d = json.loads((ROOT / 'audit/data/vector_table_alias.json').read_text())
        self.assertEqual(d['raw_sha256'], '1ae519ba6194e8f7bdaaa94333a83a9e6fda3b0563f87f7d48383b37288c1780')
        c = next(c for c in d['cases'] if c['mode'] == 'match')
        self.assertEqual((c['ram_word_writes'], c['synthetic_flash_staging_writes'], c['changed_offsets']), (0, 0, []))
        self.assertEqual(c['initial_table_sha256'], c['after_table_sha256'])
        self.assertEqual((c['scalar_cell_signed'], c['scalar_return']), (10, 208))

    def test_mismatch_writer_and_later_signed_consumer(self):
        d = json.loads((ROOT / 'audit/data/vector_table_alias.json').read_text())
        for c in d['cases']:
            if c['mode'] == 'match':
                continue
            self.assertEqual((c['ram_word_writes'], c['synthetic_flash_staging_writes']), (37, 32))
            self.assertTrue(c['unchanged_suffix'])
            self.assertTrue(all(0 <= i < 128 for i in c['changed_offsets']))
            self.assertLess(c['scalar_cell_signed'], 0)
            self.assertEqual(c['scalar_reads'], [{'address': '0x200003', 'size': 1}])
            self.assertEqual(c['scalar_return'], 0xFFFFFE90)
            self.assertEqual(c['scalar_return'], c['scalar_reference']['return'])
            commands = [w for w in c['vector_writes'] if w['address'] == '0xffffff64']
            self.assertEqual([w['value'] for w in commands], ['0x5a000001'])


if __name__ == '__main__':
    unittest.main()
