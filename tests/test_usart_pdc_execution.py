"""Check committed original-byte USART/PDC evidence and explicit MMIO limits."""
import json
import unittest

from tests._paths import ROOT


class UsartPdcExecution(unittest.TestCase):
    def test_execution_coverage_and_control_read_variants(self):
        doc = json.loads((ROOT / 'audit/data/usart_pdc_emulation.json').read_text())
        decode = json.loads((ROOT / 'audit/data/uart_buffer_binaryninja.json').read_text())
        self.assertEqual(doc['raw_sha256'], decode['raw_sha256'])
        self.assertEqual(doc['mismatches'], [])
        self.assertEqual((len(doc['queue_cases']), len(doc['interrupt_cases']), len(doc['initializer_cases'])), (48, 8, 3))
        ranges = [(int(a, 0), int(b, 0)) for a, b in doc['code_ranges']]
        starts = {i['address'] for r in decode['ranges'] for i in r['instructions']
                  if any(a <= int(i['address'], 0) < b for a, b in ranges)}
        self.assertEqual(set(doc['visited_addresses']), starts)
        self.assertEqual(len(starts), 183)
        self.assertEqual(len(doc['literal_words']), 30)
        self.assertEqual({c['outcome'] for c in doc['queue_cases']}, {'current', 'next', 'not_staged'})
        for c in doc['initializer_cases']:
            control = [int(v, 0) for a, n, v in c['writes'] if a == '0xfffc0000']
            self.assertEqual(control, [0xAC, int(c['us_cr_read'], 0)|0x800, 0x40, 0x10])


if __name__ == '__main__':
    unittest.main()
