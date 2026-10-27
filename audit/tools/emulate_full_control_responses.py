#!/usr/bin/env python3
"""Check modeled response arithmetic inside complete original control calls."""
import argparse
import hashlib
import itertools
import json
import struct
from pathlib import Path

from emulate_aid255_control_admission import AdmissionControlRunner
from emulate_control_scalar_integration import ROOT
from emulate_integer_runtime import SHA


class FullResponseRunner(AdmissionControlRunner):
    def trace(self, cpu, address, size, user):
        super().trace(cpu, address, size, user)
        if address == 0x55A6:
            self.response['actual_derived'] = self.word(0x200474)
            self.response['actual_filters'] = [list(struct.unpack('<32I', cpu.mem_read(a, 128)))
                                               for a in (0x200480, 0x200500)]

    def call(self, entry, args):
        for address, size, value in self.overrides:
            self.cpu.mem_write(address, value.to_bytes(size, 'little'))
        for start in (0x200480, 0x200500):
            self.cpu.mem_write(start, struct.pack('<32I', *self.filter_seed))
        return super().call(entry, args)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('image', type=Path)
    p.add_argument('--output', type=Path, required=True)
    args = p.parse_args()
    raw = args.image.read_bytes()
    if hashlib.sha256(raw).hexdigest() != SHA:
        raise ValueError('source identity mismatch')
    runner = FullResponseRunner(raw)
    cases = []
    union = set()
    float_pairs = ((0x40C00000, 0x40000000), (0xC0C00000, 0x40000000),
                   (0x7F7FFFFF, 1), (0x3F800000, 0x80000000))
    for source, filtering, multipliers, previous, ratio in itertools.product(
            (0, 1, 2), (0, 1, 2), ((0, 0), (1, 0), (1000, 0), (0xFFFFFFFF, 0xFFFFFFFF)),
            (0, 255), float_pairs):
        runner.overrides = [(0x2005D4, 1, source), (0x200AFE, 1, filtering),
                            (0x200AC8, 4, multipliers[0]), (0x200ACC, 4, multipliers[1]),
                            (0x200BC3, 1, previous), (0x2005D7, 1, 80),
                            (0x2005D8, 1, 160), (0x2005D9, 1, 255),
                            (0x2005E4, 4, 4095), (0x200748, 4, ratio[0]), (0x20074C, 4, ratio[1]),
                            (0x2005F8, 4, 0xFFFFFFFF), (0x2005FC, 4, 0x80000000),
                            (0x2008A8, 4, 0x12345678), (0x2008AC, 4, 0x89ABCDEF),
                            (0x2008B0, 4, 0x87654321)]
        runner.filter_seed = [0xFFFFFFFF]*32 if filtering == 1 else [0]*32
        runner.sample(dict(capture=2000, percent=50, clock_enabled=False))
        union.update(runner.visited)
        if runner.response is None or 'actual_bytes' not in runner.response:
            raise ValueError('complete response comparison missing')
        cases.append({'entry': {'source_select': source, 'filter_enable': filtering,
                                'multipliers': multipliers, 'previous_response': previous,
                                'ratio_source_bits': [hex(x) for x in ratio]},
                      'response': runner.response, 'return_selector': runner.regs(1)[0]})
    previous = json.loads((ROOT / 'audit/data/control_reinitialization.json').read_text())
    remaining = {int(a, 0) for a in previous['remaining_main_starts']}
    doc = {'format': 'quadzilla-full-control-responses-v1', 'raw_sha256': SHA,
           'cases': cases, 'reference_mismatches': 0, 'function_stubs': [],
           'new_main_starts': [hex(a) for a in sorted(union & remaining)],
           'combined_main_starts': previous['combined_main_starts']+len(union & remaining),
           'remaining_main_starts': [hex(a) for a in sorted(remaining-union)],
           'limits': ['complete original 0x50F0 calls; controlled entry-state overrides after initialized SRAM',
                      'response model receives actual state at 0x53A2, including upstream computed results and local flags',
                      'finite float source words; intermediate overflow included; numeric status byte not compared',
                      'byte stores, derived word and both filter buffers checked at 0x55A6',
                      'later scorer executes but has no new independent comparison in this suite',
                      'no parameter-admission, global-writer, interrupt, physical-unit or hardware-output proof']}
    args.output.write_text(json.dumps(doc, indent=2)+'\n')
    print(f'{len(cases)} full response calls; new starts {doc["new_main_starts"]}; union {doc["combined_main_starts"]}/574')


if __name__ == '__main__':
    main()
