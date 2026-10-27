#!/usr/bin/env python3
"""Check alternate axis and applied-stretch/clamp contracts in full control calls."""
import argparse
import hashlib
import itertools
import json
from pathlib import Path

from emulate_control_retention_branches import RetentionRunner, ROOT
from emulate_integer_runtime import SHA
from model_stretch_arithmetic import applied_value


def alternate_axis(target, denominator, offset):
    if target > denominator+offset:
        return 19
    if target < offset:
        return 0
    return 19*target//denominator-19*offset//denominator if denominator else 0


class AxisClampRunner(RetentionRunner):
    def call(self, entry, args):
        self.axis = None
        self.stretch = None
        self.stretch_reads = []
        return super().call(entry, args)

    def read(self, cpu, access, address, size, value, user):
        super().read(cpu, access, address, size, value, user)
        if cpu.reg_read(self.arm.UC_ARM_REG_PC) == 0x4ABC:
            if self.stretch is None or address != self.stretch['table_address'] or size != 1:
                raise ValueError('stretch lookup differs from actual original arguments')
            self.stretch_reads.append(hex(address))

    def trace(self, cpu, address, size, user):
        super().trace(cpu, address, size, user)
        if address == 0x51CA:
            target = self.regs(3)[2]
            denominator, offset = self.byte(0x200589), self.byte(0x20058D)
            self.axis = dict(target=target, denominator=denominator, offset=offset,
                             expected=alternate_axis(target, denominator, offset))
            if target > 256 or not 0 <= self.axis['expected'] <= 19:
                raise ValueError('axis input/output bound failed')
        elif address == 0x51FE:
            actual = cpu.reg_read(self.arm.UC_ARM_REG_R6)
            if actual != self.axis['expected']:
                raise ValueError(('alternate axis mismatch', self.axis, actual))
            self.axis['actual'] = actual
        elif address == 0x5200:
            if self.byte(0x20042B) != self.axis['target'] & 255:
                raise ValueError('axis history narrowing mismatch')
            self.axis['stored_history'] = self.byte(0x20042B)
        elif address == 0x4A94:
            row, column, percent = self.regs(3)
            at = 0x200190+13*row+column
            if not 0 <= row <= 19 or not 0 <= column <= 12 or not 0x200190 <= at < 0x200294:
                raise ValueError(('stretch table index bound', row, column))
            fields = dict(step=self.byte(0x200433), residue=self.byte(0x200434),
                          captured=self.word(0x2005F0), minimum=self.byte(0x20058C),
                          low=self.byte(0x20058B), high=self.byte(0x20058A),
                          requested=self.word(0x200590), table_byte=self.byte(at), percent=percent)
            self.stretch = dict(row=row, column=column, table_address=at,
                                inputs=fields, expected=applied_value(**fields))
        elif address == 0x5328:
            actual = self.regs(1)[0]
            if actual != self.stretch['expected']:
                raise ValueError('full-caller stretch mismatch')
            self.stretch['actual'] = actual
        elif address == 0x538A:
            r6 = cpu.reg_read(self.arm.UC_ARM_REG_R6)
            if self.regs(2)[1] != (24*r6+3) & 0xFFFFFFFF:
                raise ValueError('timer argument packing mismatch')


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('image', type=Path)
    p.add_argument('--output', type=Path, required=True)
    args = p.parse_args()
    raw = args.image.read_bytes()
    if hashlib.sha256(raw).hexdigest() != SHA:
        raise ValueError('source identity mismatch')
    r = AxisClampRunner(raw)
    specs = [dict(kind='axis', denominator=d, offset=k, source=s, old_axis=old,
                  capture=2000, percent=50, clock_enabled=False)
             for d, k, s, old in itertools.product((0, 1, 10, 100, 255), (0, 1, 10, 100, 255),
                                                   (0, 1, 10, 100, 255), (0, 255))]
    specs += [dict(kind='clamp', requested=v, capture=3200, percent=100,
                   clock_enabled=clock, selector=10)
              for v, clock in itertools.product((409, 410, 411, 2729, 2730, 2731, 5000), (False, True))]
    specs.append(dict(kind='axis', denominator=255, offset=1, source=255, old_axis=255,
                      word_offset=1, capture=2000, percent=50, clock_enabled=False))
    cases = []
    union = set()
    for spec in specs:
        r.overrides = [(0x20058D, 1, spec.get('offset', 0)),
                       (0x20042B, 1, spec.get('old_axis', 0)), (0x2006EC, 1, 1),
                       (0x2008A4, 4, spec.get('word_offset', 0))]
        if spec['kind'] == 'clamp':
            r.overrides += [(0x200590, 4, spec['requested']), (0x20058C, 1, 100)]
        call_spec = {k: v for k, v in spec.items()
                     if k in ('capture', 'percent', 'clock_enabled', 'selector', 'denominator', 'source')}
        r.sample(call_spec)
        if spec['kind'] == 'clamp' and r.stretch['actual'] != spec['requested']:
            raise ValueError('directed clamp fixture did not produce requested stretch')
        union.update(r.visited)
        cases.append({'entry': spec, 'axis': r.axis, 'stretch': r.stretch,
                      'stretch_reads': r.stretch_reads, 'events': r.events,
                      'timer_calls': r.timer_calls.copy(), 'timer_writes': r.timer_writes.copy()})
    previous = json.loads((ROOT / 'audit/data/full_control_responses.json').read_text())
    remaining = {int(a, 0) for a in previous['remaining_main_starts']}
    doc = {'format': 'quadzilla-control-axis-clamps-v1', 'raw_sha256': SHA, 'cases': cases,
           'reference_mismatches': 0,
           'new_main_starts': [hex(a) for a in sorted(union & remaining)],
           'combined_main_starts': previous['combined_main_starts']+len(union & remaining),
           'remaining_main_starts': [hex(a) for a in sorted(remaining-union)],
           'limits': ['original complete control calls; no helper result stubs',
                      'actual intermediate inputs checked against alternate-axis and stretch models',
                      'bounds require stable inputs and intact frames; global writer exclusion not established',
                      'controlled entry values do not establish parameter admission or live state histories',
                      'TC0 CLKSTA is synthetic plain memory, not hardware timing or peripheral side effects',
                      'instruction coverage is not exhaustive branch/path, arithmetic-state or firmware verification']}
    args.output.write_text(json.dumps(doc, indent=2)+'\n')
    print(f'{len(cases)} complete calls; union {doc["combined_main_starts"]}/574; remaining {doc["remaining_main_starts"]}')


if __name__ == '__main__':
    main()
