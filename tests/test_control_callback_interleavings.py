"""Selected original callback effects persist through resumed control."""
import json
import unittest
from tests._paths import ROOT


class ControlCallbackInterleavings(unittest.TestCase):
    def setUp(self):
        self.doc = json.loads((ROOT / 'audit/data/control_callback_interleavings.json').read_text())

    def test_repeated_load_source_is_stable_in_selected_cases(self):
        self.assertEqual(len(self.doc['cases']), 33)
        for c in self.doc['cases']:
            p = c['percent']['before']
            self.assertEqual(c['pause_pc'], '0x5210')
            self.assertNotEqual(c['interrupted_sp'], c['callback_sp'])
            self.assertEqual(c['percent']['after'], p)
            self.assertEqual(c['scalar_column'], 19*p//100)
            self.assertEqual(c['response_actual_bytes'], c['response_expected']['bytes'])
            self.assertFalse(any(int(w['address'], 0) < 0x2005F4 and
                                 int(w['address'], 0)+w['size'] > 0x2005F0
                                 for w in c['callback_writes']))

    def test_numeric_callback_changes_reach_response_consumer(self):
        numeric = [c for c in self.doc['cases'] if c['scenario']['name'] == 'tc2_numeric']
        self.assertEqual(len(numeric), 3)
        for c in numeric:
            writes = {w['address']: w['value'] for w in c['callback_writes']}
            self.assertEqual(writes['0x20074c'], '0x4001b0d2')
            self.assertEqual(c['response_inputs']['ratio_denominator'], 0x4001B0D2)
            self.assertEqual(c['response_inputs']['timer_state'], 2)

    def test_selected_peripheral_branch_effects_are_preserved(self):
        selected = {c['scenario']['name']: c for c in self.doc['cases'] if c['percent']['before'] == 50}
        self.assertEqual(selected['pio_high']['callback_writes'], [])
        self.assertEqual(selected['spi_stub']['callback_writes'], [])
        self.assertEqual(len(selected['tc1_clear']['callback_writes']), 2)
        self.assertEqual(len(selected['tc1_set']['callback_writes']), 1)
        uart = {w['address']: w['value'] for w in selected['usart_both']['callback_writes']}
        self.assertEqual(uart['0x200afd'], '0x1')
        self.assertEqual(uart['0xfffc0104'], '0x0')


if __name__ == '__main__':
    unittest.main()
