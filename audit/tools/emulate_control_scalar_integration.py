#!/usr/bin/env python3
"""Execute full 0x50F0 calls and check scalar/table/timer integration offline."""
import argparse
from collections import Counter
import hashlib
import json
import struct
import sys
from pathlib import Path

from audit_aid_tables import AidRunner
from emulate_integer_runtime import SHA

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tools'))
from model_scalar_telemetry import calculate


def axes(total, denominator, percent):
    """Stable-state direct-caller indices, including the runtime's zero quotient."""
    row = 19 if denominator < total else total*19//denominator if denominator else 0
    column = 19 if percent >= 101 else percent*19//100
    return row, column


class IntegrationRunner(AidRunner):
    def __init__(self, raw):
        super().__init__(raw)
        manifest = json.loads((ROOT / 'audit/data/reviewed_instruction_ranges.json').read_text())
        if manifest['raw_sha256'] != SHA:
            raise ValueError('instruction evidence identity changed')
        self.allowed_ranges = tuple((int(r['start'], 0), int(r['end'], 0)) for r in manifest['ranges'])
        self.cpu.mem_map(0xFFFA0000, 0x1000)
        self.calls = []
        self.global_writes = []
        self.scalar = None
        self.timer_calls = []
        self.timer_writes = []
        self.table_reads = []
        self.backdown_calls = 0
        self.cpu.hook_add(self.uc.UC_HOOK_MEM_WRITE, self.write)
        self.cpu.hook_add(self.uc.UC_HOOK_MEM_READ, self.read)

    def byte(self, a):
        return self.cpu.mem_read(a, 1)[0]

    def word(self, a):
        return int.from_bytes(self.cpu.mem_read(a, 4), 'little')

    def regs(self, n=4):
        return [self.cpu.reg_read(getattr(self.arm, f'UC_ARM_REG_R{i}')) for i in range(n)]

    def write(self, cpu, access, address, size, value, user):
        site = cpu.reg_read(self.arm.UC_ARM_REG_PC)
        row = {'site': hex(site), 'address': hex(address), 'size': size,
               'value': hex(value & ((1 << (size*8))-1))}
        if 0x200000 <= address < 0x202000:
            self.global_writes.append(row)
        if address == 0xFFFA001C:
            self.timer_writes.append(row)

    def read(self, cpu, access, address, size, value, user):
        site = cpu.reg_read(self.arm.UC_ARM_REG_PC)
        if site in (0x4E82, 0x4CEC):
            expected = self.scalar['table_address'] if site == 0x4E82 else self.calls[-1]['table_address']
            if hex(address) != expected:
                raise ValueError(('lookup differs from original caller axes', hex(site), hex(address), expected))
            self.table_reads.append({'site': hex(site), 'address': hex(address), 'size': size})

    def trace(self, cpu, address, size, user):
        super().trace(cpu, address, size, user)
        if address == 0x74E8:
            raise ValueError('reinitialization branch is outside this integration suite')
        if address == 0x4D38:
            args = self.regs()
            row = self.byte(cpu.reg_read(self.arm.UC_ARM_REG_SP))
            column = args[3]
            expected_axes = axes(self.word(0x20044C), self.byte(0x200589), self.word(0x2005F0))
            if (row, column) != expected_axes or not 0 <= row <= 19 or not 0 <= column <= 19:
                raise ValueError(('scalar indices', row, column, expected_axes))
            c = dict(mode=self.byte(0x200425), refresh=self.byte(0x200426),
                     response_flags=[self.byte(a) for a in (0x200BED, 0x200BF1, 0x200BF3, 0x200BF4)],
                     gate_sum=[self.byte(0x200433), self.byte(0x200434)], selector=args[1],
                     enabled=self.byte(0x200432), base=self.word(0x2005E8), capture=self.word(0x2005EC),
                     knots=[self.word(0x200458+4*i) for i in range(5)], coefficient=self.byte(0x200588),
                     response=self.byte(0x200BC2), threshold=self.byte(0x2005B3), working61=self.word(0x20046C),
                     status=self.byte(0x2005D7), percent0=self.byte(0x2005B0), percent1=self.byte(0x2005B1),
                     cell=self.byte(0x200000+20*row+column))
            self.scalar = {'row': row, 'column': column, 'table_address': hex(0x200000+20*row+column),
                           'inputs': c, 'reference': calculate(c)}
        elif address == 0x5262:
            expected = self.scalar['reference']
            actual = dict(return_value=self.regs(1)[0], cap=self.word(0x200450), mode=self.byte(0x200425),
                          refresh=self.byte(0x200426), knots=[self.word(0x200458+4*i) for i in range(5)])
            if actual != dict(return_value=expected['return'], **{k: expected[k] for k in ('cap', 'mode', 'refresh', 'knots')}):
                raise ValueError(('integrated scalar mismatch', actual, expected))
            self.scalar['actual'] = actual
        elif address == 0x527A:
            if self.word(0x200604) != self.scalar['reference']['caller_store']:
                raise ValueError('integrated caller store mismatch')
            self.scalar['telemetry_store'] = self.word(0x200604)
        elif address == 0x4B38:
            stack = cpu.reg_read(self.arm.UC_ARM_REG_SP)
            row, column = self.word(stack+4), self.word(stack+8)
            if not 0 <= row <= 19 or not 0 <= column <= 19:
                raise ValueError('capture table bounds mismatch')
            self.calls.append({'entry': hex(address), 'row': row, 'column': column,
                               'table_address': hex(0x200294+20*row+column)})
        elif address == 0x6FA0:
            base, value = self.regs(2)
            if base != 0xFFFA0000:
                raise ValueError('unexpected timer base')
            self.timer_calls.append({'base': hex(base), 'value': hex(value),
                                     'clock_enabled': bool(self.word(base+0x20) & 0x10000)})
        elif address == 0x499C:
            self.backdown_calls += 1

    def sample(self, spec):
        self.reset()
        self.cpu.mem_write(0xFFFA0000, bytes(0x1000))
        def word(a, value):
            self.cpu.mem_write(a, struct.pack('<I', value))
        def byte(a, value):
            self.cpu.mem_write(a, bytes([value]))
        # These are controlled overrides after the exact initialized-data copy.
        for a, value in ((0x2005EC, spec['capture']), (0x2005F0, spec['percent']),
                         (0x2008A4, spec.get('offset', 0)), (0x200470, spec.get('counter', 0)),
                         (0x2005E8, spec.get('base', 1000)), (0x200448, 0),
                         (0x200590, 1700), (0x200594, 10000),
                         (0xFFFA0020, 0x10000 if spec['clock_enabled'] else 0)):
            word(a, value)
        for a, value in ((0x200589, spec.get('denominator', 100)), (0x2005DB, spec.get('source', 50)),
                         (0x200432, spec.get('enabled', 1)), (0x200425, spec.get('mode', 0)),
                         (0x200426, 0), (0x20042B, 0), (0x2006E2, 0)):
            byte(a, value)
        for a, value in ((0x2006CD, spec.get('selector', 5)), (0x200580, 11),
                         (0x200433, 10), (0x200434, 0), (0x200431, 1),
                         (0x2006CF, 0), (0x20058A, 10), (0x20058B, 0), (0x20058C, 50)):
            byte(a, value)
        preserved = []
        for n in range(4, 12):
            reg = getattr(self.arm, f'UC_ARM_REG_R{n}')
            self.cpu.reg_write(reg, 0x12340000+n)
            preserved.append((reg, 0x12340000+n))
        self.calls.clear(); self.global_writes.clear(); self.table_reads.clear(); self.backdown_calls = 0
        self.timer_calls.clear(); self.timer_writes.clear(); self.visited.clear(); self.scalar = None
        result = self.call(0x50F0, [])
        if result['status'] != 'returned' or any(self.cpu.reg_read(r) != v for r, v in preserved):
            raise ValueError(('full control return/preservation', result))
        if self.scalar is None or 'actual' not in self.scalar:
            raise ValueError('missing scalar execution')
        if result['r0'] != self.scalar['inputs']['selector']:
            raise ValueError('outer return differs from retained selector')
        old_counter = spec.get('counter', 0)
        signed_counter = old_counter if old_counter < 0x80000000 else old_counter-0x100000000
        new_counter = 1 if signed_counter >= 1000001 else (old_counter+1) & 0xFFFFFFFF
        signed_new = new_counter if new_counter < 0x80000000 else new_counter-0x100000000
        if self.word(0x200470) != new_counter or self.backdown_calls != int(signed_new % 250 == 0):
            raise ValueError('counter/backdown dispatch mismatch')
        expected_writes = [c['value'] for c in self.timer_calls if not c['clock_enabled']]
        if [w['value'] for w in self.timer_writes] != expected_writes:
            raise ValueError('timer write admission mismatch')
        for read in self.table_reads:
            lo = 0x200000 if read['site'] == '0x4e82' else 0x200294
            if read['size'] != 1 or not lo <= int(read['address'], 0) < lo+400:
                raise ValueError('lookup escaped expected 20x20 extent')
        return {'inputs': spec, 'return': result['r0'], 'scalar': self.scalar,
                'counter_after': new_counter, 'backdown_calls': self.backdown_calls,
                'capture_table_calls': self.calls.copy(), 'table_reads': self.table_reads.copy(),
                'timer_calls': self.timer_calls.copy(), 'timer_writes': self.timer_writes.copy(),
                'global_writes': self.global_writes.copy()}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('image', type=Path)
    p.add_argument('--output', type=Path, required=True)
    args = p.parse_args()
    raw = args.image.read_bytes()
    if hashlib.sha256(raw).hexdigest() != SHA:
        raise ValueError('source identity mismatch')
    runner = IntegrationRunner(raw)
    captures = (0, 899, 900, 999, 1000, 1004, 1199, 1200, 1400, 1401, 1499, 1500,
                1999, 2000, 2499, 2500, 2999, 3000, 3199, 3200, 3499, 3500, 4000,
                0x7FFFFFFF, 0x80000000, 0xFFFFFFFF)
    specs = [dict(capture=c, percent=pct, clock_enabled=clk)
             for c in captures for pct in (0, 1, 50, 100, 101, 0xFFFFFFFF) for clk in (False, True)]
    specs += [dict(capture=2000, percent=50, clock_enabled=False, **extra) for extra in
              ({'denominator': 0, 'source': 0}, {'denominator': 0, 'source': 1},
               {'denominator': 255, 'source': 255}, {'source': 1, 'offset': 0xFFFFFFFF},
               {'offset': 0xFFFFFFFF}, {'counter': 249}, {'counter': 999999},
               {'counter': 1000001}, {'counter': 0xFFFFFFFF}, {'counter': 0x80000000},
               {'mode': 1}, {'enabled': 0}, {'base': 0xFFFFFFFF})]
    union = set(); examples = []; summary = []; timers = Counter()
    for n, spec in enumerate(specs):
        case = runner.sample(spec)
        union.update(runner.visited)
        scalar = case['scalar']
        summary.append({'case': n, 'scalar_axes': [scalar['row'], scalar['column']],
                        'scalar_return': scalar['actual']['return_value'], 'telemetry': scalar['telemetry_store'],
                        'return': case['return'], 'timer_calls': len(case['timer_calls']), 'timer_writes': len(case['timer_writes'])})
        summary[-1].update(counter_after=case['counter_after'], backdown_calls=case['backdown_calls'])
        timers['calls'] += len(case['timer_calls']); timers['writes'] += len(case['timer_writes'])
        if n in (0, 2, 4, 6, 8, 10, 72, 144, 156, 240, 264, 300, 311) or n >= 312:
            case['case'] = n
            examples.append(case)
    decode = json.loads((ROOT / 'audit/data/main_control_binaryninja.json').read_text())
    starts = {int(i['address'], 0) for r in decode['ranges'] for i in r['instructions']
              if 0x50F0 <= int(i['address'], 0) < 0x5612}
    source = raw[0x96E8-0x4000:0x96E8-0x4000+400]
    doc = {'format': 'quadzilla-control-scalar-integration-v1', 'raw_sha256': SHA,
           'cpu': 'ARM926 functional surrogate', 'cases': len(specs), 'reference_mismatches': 0,
           'source_cases': specs, 'summary': summary, 'examples': examples,
           'timer_counts': dict(timers), 'main_starts_visited': [hex(a) for a in sorted(starts & union)],
           'main_starts_unvisited': [hex(a) for a in sorted(starts-union)],
           'initial_scalar_table': {'start': '0x200000', 'end_exclusive': '0x200190',
                                    'source': '0x96e8', 'sha256': hashlib.sha256(source).hexdigest(),
                                    'minimum': min(source), 'maximum': max(source), 'high_bit_count': sum(b >= 128 for b in source)},
           'limits': ['all 0x50F0 calls execute original helpers; no helper result stubs',
                      'exact initialized-data copy plus recorded synthetic overrides, not an entire startup sequence',
                      'TC0 status is plain memory; no timers, interrupts, DMA or hardware timing execute',
                      'input words remain stable across repeated loads; asynchronous writers not modeled',
                      'reinitialization call 0x74E8 is rejected if reached, not replaced with a successful stub',
                      'scalar contract, table bounds and timer admission are checked; other telemetry stores are observed without a complete independent model',
                      'not exhaustive branches, writer bounds, physical semantics or a full firmware completion claim']}
    args.output.write_text(json.dumps(doc, indent=2)+'\n')
    print(f'{len(specs)} full control calls; {len(starts & union)}/{len(starts)} main starts; timer {dict(timers)}')


if __name__ == '__main__':
    main()
