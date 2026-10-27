#!/usr/bin/env python3
"""Check retained-sample counter and optional control branches in original calls."""
import argparse
import hashlib
import json
import struct
from pathlib import Path

from emulate_control_scalar_integration import IntegrationRunner, ROOT
from emulate_integer_runtime import SHA


def retained_count(old, saved_capture, capture, saved_source, source):
    return ((old + 1) & 0xFFFFFFFF
            if saved_capture == capture and saved_source == source and capture >= 601 else 0)


class RetentionRunner(IntegrationRunner):
    def call(self, entry, args):
        self.events = []
        self.clamp_input = None
        for address, size, value in self.overrides:
            self.cpu.mem_write(address, value.to_bytes(size, 'little'))
        return super().call(entry, args)

    def trace(self, cpu, address, size, user):
        super().trace(cpu, address, size, user)
        if address == 0x55BA:
            self.expected_count = retained_count(self.word(0x200448), self.word(0x20043C),
                                                self.word(0x2005EC), self.word(0x200440),
                                                self.word(0x200600))
            self.events.append({'site': hex(address), 'old_count': self.word(0x200448),
                                'saved_capture': self.word(0x20043C), 'capture': self.word(0x2005EC),
                                'saved_source': self.word(0x200440), 'source': self.word(0x200600),
                                'expected_count': self.expected_count})
        elif address == 0x55DE:
            if self.word(0x200448) != self.expected_count:
                raise ValueError('retained-sample counter mismatch')
        elif address == 0x5382 and self.clamp_input is not None:
            expected = min(2730, max(410, self.clamp_input))
            if cpu.reg_read(self.arm.UC_ARM_REG_R6) != expected:
                raise ValueError('optional timer clamp mismatch')
            self.events.append({'site': hex(address), 'clamp_input': self.clamp_input,
                                'clamp_output': expected})
        elif address in (0x52F0, 0x530A, 0x536A, 0x5376, 0x5380, 0x539E):
            self.events.append({'site': hex(address), 'r0': self.regs(1)[0],
                                'r6': cpu.reg_read(self.arm.UC_ARM_REG_R6)})
            if address == 0x536A:
                self.clamp_input = cpu.reg_read(self.arm.UC_ARM_REG_R6)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('image', type=Path)
    p.add_argument('--output', type=Path, required=True)
    args = p.parse_args()
    raw = args.image.read_bytes()
    if hashlib.sha256(raw).hexdigest() != SHA:
        raise ValueError('source identity mismatch')
    # Literal operands independently bind the counter account to this image.
    literals = {0x53C4: 0x200424, 0x5664: 0x2005EC, 0x56E0: 0x200600,
                0x56E4: 601, 0x56E8: 2001, 0x5618: 0x2006EC, 0x561C: 2731}
    for address, value in literals.items():
        if struct.unpack_from('<I', raw, address-0x4000)[0] != value:
            raise ValueError('literal contract changed')
    runner = RetentionRunner(raw)
    cases = []
    union = set()
    for capture in (600, 601, 2000, 3200, 4000):
        for old in (0, 1, 1999, 0xFFFFFFFF):
            for match in ('both', 'capture_mismatch', 'source_mismatch'):
                for optional in (False, True):
                    runner.overrides = [(0x200448, 4, old),
                                        (0x20043C, 4, capture + (match == 'capture_mismatch')),
                                        (0x200440, 4, 1 if match == 'source_mismatch' else 0),
                                        (0x20042D, 1, int(optional)), (0x2006EC, 1, int(optional)),
                                        (0x200ADD, 1, int(optional))]
                    spec = dict(capture=capture, percent=50, clock_enabled=False)
                    result = runner.sample(spec)
                    union.update(runner.visited)
                    if runner.word(0x20043C) != capture or runner.word(0x200440) != runner.word(0x200600):
                        raise ValueError('retained source refresh mismatch')
                    cases.append({'capture': capture, 'old_count': old, 'match': match,
                                  'optional': optional, 'overrides': runner.overrides,
                                  'events': runner.events, 'count_after': runner.word(0x200448),
                                  'timer_calls': result['timer_calls'], 'timer_writes': result['timer_writes']})
    baseline = json.loads((ROOT / 'audit/data/control_scalar_integration.json').read_text())
    previous = {int(a, 0) for a in baseline['main_starts_visited']}
    remaining = {int(a, 0) for a in baseline['main_starts_unvisited']}
    doc = {'format': 'quadzilla-control-retention-branches-v1', 'raw_sha256': SHA,
           'cases': cases, 'reference_mismatches': 0,
           'new_main_starts': [hex(a) for a in sorted(union & remaining)],
           'combined_main_starts': len(previous | (union & remaining)),
           'remaining_main_starts': [hex(a) for a in sorted(remaining-union)],
           'limits': ['controlled entry-state overrides after initialized SRAM; not live admission',
                      'complete original control calls with existing scalar/table/timer checks',
                      'optional branch events are observations, not complete arithmetic models',
                      '2001-count reinitialization remains rejected by the inherited runner',
                      'no interrupts, DMA, hardware timing or physical output claim']}
    args.output.write_text(json.dumps(doc, indent=2)+'\n')
    print(f'{len(cases)} calls; new starts {doc["new_main_starts"]}; combined {doc["combined_main_starts"]}/574')


if __name__ == '__main__':
    main()
