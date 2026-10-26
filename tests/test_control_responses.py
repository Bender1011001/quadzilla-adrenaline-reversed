"""Response arithmetic ordering, finite rounding and byte-store regressions."""
import importlib.util
import json
import sys
import unittest

from tests._paths import ROOT

sys.path.insert(0, str(ROOT / 'audit/tools'))
spec = importlib.util.spec_from_file_location('control_response_audit', ROOT / 'audit/tools/emulate_control_responses.py')
audit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit)


class ControlResponses(unittest.TestCase):
    def test_retained_coefficient_and_current_byte_store(self):
        old_zero = audit.response_values(audit.defaults(previous_response=0, new_response=80))
        old_fifty = audit.response_values(audit.defaults(previous_response=50, new_response=80))
        self.assertEqual((old_zero['sample'], old_fifty['sample']), (0, 730))
        self.assertEqual((old_zero['bytes']['0x200bc3'], old_fifty['bytes']['0x200bc3']), (80, 80))
        self.assertEqual(old_fifty['derived'], 432000)
        self.assertEqual(old_fifty['average'], 22)

    def test_zero_denominator_fallback_and_upper_cap(self):
        fallback = audit.response_values(audit.defaults(multiplier0=0, multiplier1=0))
        capped = audit.response_values(audit.defaults(multiplier0=1, multiplier1=0, source_select=1, capture=1, previous_response=255))
        self.assertEqual((fallback['sample'], capped['sample']), (9999, 9999))
        self.assertEqual(fallback['ratio_bits'], '0x42c7fae1')
        self.assertEqual(audit.response_values(audit.defaults(ratio_denominator=0))['ratio_integer'], 0)
        self.assertEqual(audit.response_values(audit.defaults(ratio_denominator=0x80000000))['ratio_integer'], 0)

    def test_filter_wrap_and_exact_enable(self):
        enabled = audit.response_values(audit.defaults(filter_enable=1))
        disabled = audit.response_values(audit.defaults(filter_enable=2))
        wrapped = audit.response_values(audit.defaults(filter_enable=1, filter1=[0xFFFFFFFF]*32))
        self.assertEqual([c['bytes']['0x200bc1'] for c in (enabled, disabled, wrapped)], [5, 160, 4])
        self.assertEqual(enabled['filter1'], [0]*31+[160])
        self.assertEqual(disabled['filter1'], [0]*32)

    def test_signed_ratio_and_distinct_integer_narrowing(self):
        c = audit.response_values(audit.defaults(ratio_numerator=0xC0C00000, source_offset1=216, source_clamp=0xFFFFFFFF))
        self.assertEqual([c['bytes'][hex(a)] for a in range(0x200BD6, 0x200BD9)], [253, 255, 255])
        self.assertEqual(c['bytes']['0x200bbe'], 0)
        self.assertEqual(c['bytes']['0x200bca'], 255)
        self.assertEqual(audit.response_values(audit.defaults(source_offset1=0x80000000))['bytes']['0x200bbe'], 0)
        self.assertEqual(audit.response_values(audit.defaults(source_offset1=0xFFFFFFFF))['bytes']['0x200bbe'], 39)
        with self.assertRaises(ValueError):
            audit.response_values(audit.defaults(ratio_numerator=0x7FC00000))

    def test_original_execution_and_formula_artifact(self):
        d = json.loads((ROOT / 'audit/data/control_response_emulation.json').read_text())
        self.assertEqual(d['raw_sha256'], '1ae519ba6194e8f7bdaaa94333a83a9e6fda3b0563f87f7d48383b37288c1780')
        self.assertEqual((d['cases'], d['mismatches'], len(d['visited']), d['unvisited']), (1072, 0, 196, []))
        self.assertEqual([(c['scalar_response_input'], c['ratio_response_input'], c['response_bc2_after'], c['response_bc3_after'])
                          for c in d['sequential_complete_calls']], [(7, 3, 100, 80), (100, 80, 100, 80)])
        for c in d['examples']:
            self.assertEqual(audit.response_values(c['inputs']), c['expected'])
            self.assertEqual(c['actual_bytes'], c['expected']['bytes'])


if __name__ == '__main__':
    unittest.main()
