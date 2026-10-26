"""Keep code-like byte windows distinct from actual SPI descriptor boundaries."""
import json
import unittest

from tests._paths import ROOT


class SpiTemplateProvenance(unittest.TestCase):
    def setUp(self):
        self.doc = json.loads((ROOT / 'audit/data/spi_template_provenance.json').read_text())

    def test_cross_boundary_windows(self):
        self.assertEqual(self.doc['raw_sha256'], '1ae519ba6194e8f7bdaaa94333a83a9e6fda3b0563f87f7d48383b37288c1780')
        self.assertEqual(self.doc['data_descriptor_words'], ['0x8a0', '0x200000', '0x96e8'])
        for window, runtime, value in zip(self.doc['windows'], (0x200693, 0x20069F), (0x9200, 0x9400)):
            self.assertEqual(int(window['runtime'], 0), runtime)
            self.assertEqual(int(window['image_source'], 0), 0x96E8 + runtime - 0x200000)
            self.assertEqual(int.from_bytes(bytes.fromhex(window['bytes']), 'little'), value)
            parts = window['parts']
            self.assertEqual(len(parts), 2)
            self.assertEqual(parts[0]['end_exclusive'], parts[1]['start'])
            self.assertEqual(bytes.fromhex(parts[0]['bytes'] + parts[1]['bytes']), bytes.fromhex(window['bytes']))
            self.assertEqual(int(parts[0]['end_exclusive'], 0), runtime + 1)

    def test_original_transfer_extents_and_blocked_admission(self):
        expected = {'rx0_start': (0x200694, 9), 'rx1_start': (0x2006A0, 14),
                    'rx0_clear': (0x20068C, 4), 'rx1_clear': (0x200690, 4)}
        self.assertEqual(self.doc['case_count'], 6)
        for case in self.doc['cases']:
            name, admission = case['name'].rsplit('_', 1)
            pointer, count = expected[name]
            extent = case['transmit_extent']
            self.assertEqual((int(extent['start'], 0), int(extent['end_exclusive'], 0)), (pointer, pointer + count))
            self.assertEqual(len(bytes.fromhex(extent['initialized_bytes'])), count)
            self.assertEqual(case['cpu_window_accesses'], [])
            self.assertEqual(case['tx_descriptor_programmed'], admission == 'ready')
            tx = [w for w in case['mmio_writes'] if w['address'] == '0xfffe0108']
            if admission == 'ready':
                self.assertEqual([int(w['value'], 0) for w in tx], [pointer])
            else:
                self.assertEqual(tx, [])


if __name__ == '__main__':
    unittest.main()
