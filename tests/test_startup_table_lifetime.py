"""Check original setup continuity and make the first-cycle bypass explicit."""
import json
import unittest

from tests._paths import ROOT


class StartupTableLifetime(unittest.TestCase):
    def setUp(self):
        self.doc = json.loads((ROOT / 'audit/data/startup_table_lifetime.json').read_text())

    def test_complete_setup_matrix_and_no_sampled_restoration(self):
        d = self.doc
        self.assertEqual(d['raw_sha256'], '1ae519ba6194e8f7bdaaa94333a83a9e6fda3b0563f87f7d48383b37288c1780')
        self.assertEqual((d['ready_cases'], d['blocked_cases'], len(d['cases'])), (16, 2, 18))
        ready = d['cases'][:16]
        self.assertEqual(len({tuple(c['inputs'][k] for k in ('vector_match', 'config_accepted', 'pin17', 'uscr_read')) for c in ready}), 16)
        for c in ready:
            self.assertEqual((c['outcome'], c['stop_pc'], c['stop_sp']), ('second_dispatcher_after_first_cycle', '0x78e4', '0x202fec'))
            self.assertEqual((c['first_control_calls'], c['scalar_calls']), (1, 1))
            self.assertEqual(c['table_write_count'], 0 if c['inputs']['vector_match'] else 37)
            self.assertEqual({w['site'] for w in c['table_writes']}, set() if c['inputs']['vector_match'] else {'0x7400', '0x7414'})
            hashes = [m['tables_sha256']['scalar'] for m in c['milestones']]
            self.assertEqual(len(set(hashes)), 1)
            self.assertEqual(c['initial_tables_sha256']['scalar'] == c['final_tables_sha256']['scalar'], c['inputs']['vector_match'])
            for name in ('stretch', 'capture'):
                self.assertEqual(c['initial_tables_sha256'][name], c['final_tables_sha256'][name])

    def test_no_first_cycle_lookup_or_unmodeled_hardware_claim(self):
        for c in self.doc['cases'][:16]:
            self.assertEqual((c['scalar_entry']['selector_r1'], c['scalar_entry']['enable']), (0, 0))
            self.assertEqual(c['scalar_bypass_visits'], 1)
            self.assertEqual(c['lookup_reads'], [])
            self.assertEqual(c['final_config_mode'], 1 if c['inputs']['config_accepted'] else 4)
            self.assertEqual(len(c['software_event_injections']), 1)
            self.assertEqual({r['supplied'] for r in c['uscr_reads']}, {hex(c['inputs']['uscr_read'])})
            commands = [r['value'] for r in c['flash_command_requests']]
            self.assertEqual(commands, ['0x5a00000f'] if c['inputs']['vector_match'] else ['0x5a000001', '0x5a00000f'])

    def test_missing_inputs_remain_bounded_waits(self):
        spi, event = self.doc['cases'][-2:]
        self.assertFalse(spi['inputs']['spi_ready'])
        self.assertFalse(event['inputs']['wait_event'])
        self.assertEqual((spi['outcome'], spi['stop_pc']), ('instruction_budget', '0x6b6a'))
        self.assertEqual((event['outcome'], event['stop_pc']), ('instruction_budget', '0x7832'))
        for c in (spi, event):
            self.assertEqual(c['table_write_count'], 37)
            self.assertEqual(c['first_control_calls'], 0)
            self.assertEqual(c['software_event_injections'], [])


if __name__ == '__main__':
    unittest.main()
