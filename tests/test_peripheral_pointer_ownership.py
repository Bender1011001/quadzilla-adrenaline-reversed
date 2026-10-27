"""Separate initialized TC2 pointer ownership from direct USART addresses."""
import json
import unittest
from tests._paths import ROOT


class PeripheralPointerOwnership(unittest.TestCase):
    def setUp(self):
        self.doc = json.loads((ROOT / 'audit/data/peripheral_pointer_ownership.json').read_text())

    def test_image_pointer_and_literal_sources(self):
        self.assertEqual(self.doc['initialized_sram_slot'], '0x200728')
        self.assertEqual(self.doc['image_words'], {'0x9e10': '0xfffa0080',
                                                  '0x6f58': '0x200708', '0x71c0': '0xfffc0014'})

    def test_original_tc2_callback_follows_supplied_pointer(self):
        self.assertEqual(len(self.doc['cases']), 2)
        addresses = []
        for c in self.doc['cases']:
            reads = [r for r in c['peripheral_reads'] if r['site'] == '0x6c9a']
            self.assertEqual(len(reads), 1)
            addresses.append(reads[0]['address'])
            self.assertEqual(c['pointer_after'], c['supplied_pointer'])
        self.assertEqual(addresses, ['0xfffa00a0', '0xfffc0020'])

    def test_usart_status_read_is_independent_of_tc2_slot(self):
        for c in self.doc['cases']:
            reads = [r for r in c['peripheral_reads'] if r['site'] == '0x717c']
            self.assertEqual(reads, [{'callback': 'usart', 'site': '0x717c',
                                      'address': '0xfffc0014', 'size': 4}])


if __name__ == '__main__':
    unittest.main()
