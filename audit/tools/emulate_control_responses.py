#!/usr/bin/env python3
"""Run original response-building bytes with controlled caller/SRAM state."""
import argparse
import hashlib
import json
import random
import struct
import sys
from pathlib import Path

from audit_aid_tables import AidRunner
from emulate_integer_runtime import SHA
from emulate_control_scalar_integration import IntegrationRunner

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tools'))
from model_control_responses import response_values

WORDS = {'raw_capture': 0x2005E4, 'capture_scalar': 0x2005E8, 'raw_analog': 0x200600,
         'analog_scalar': 0x200604, 'adc4': 0x2008A8, 'state_total': 0x20044C,
         'multiplier0': 0x200AC8, 'multiplier1': 0x200ACC, 'capture': 0x2005EC,
         'ratio_numerator': 0x200748, 'ratio_denominator': 0x20074C, 'timer_state': 0x200738,
         'adc6': 0x2008B0, 'adc5': 0x2008AC, 'source_offset0': 0x2005F4,
         'source_clamp': 0x2005F8, 'source_offset1': 0x2005FC, 'percent_word': 0x2005F0}
BYTES = {'source_select': 0x2005D4, 'previous_response': 0x200BC3, 'filter_enable': 0x200AFE,
         'byte_source': 0x2005D8, 'new_response': 0x2005D7, 'byte_source1': 0x2005D9}


def defaults(**changes):
    c = {k: 0 for k in WORDS | BYTES}
    c.update(raw_capture=4095, capture_scalar=2000, raw_analog=2048, analog_scalar=1000,
             multiplier0=100, multiplier1=100, capture=2000, stretch=500,
             ratio_numerator=0x40C00000, ratio_denominator=0x40000000,
             previous_response=50, new_response=80, filter0=[0]*32, filter1=[0]*32,
             clamp_flag=0, write_flag=1, byte_source=160)
    c.update(changes)
    return c


class ResponseRunner(AidRunner):
    def __init__(self, raw):
        super().__init__(raw)
        ranges = json.loads((ROOT / 'audit/data/reviewed_instruction_ranges.json').read_text())
        if ranges['raw_sha256'] != SHA:
            raise ValueError('instruction evidence mismatch')
        self.allowed_ranges = tuple((int(r['start'], 0), int(r['end'], 0)) for r in ranges['ranges'])
        self.stores = []
        self.cpu.hook_add(self.uc.UC_HOOK_MEM_WRITE, self.write)

    def write(self, cpu, access, address, size, value, user):
        if 0x200BB0 <= address < 0x200BE0:
            self.stores.append({'site': hex(cpu.reg_read(self.arm.UC_ARM_REG_PC)), 'address': hex(address),
                                'size': size, 'value': hex(value & ((1 << (8*size))-1))})

    def sample(self, c):
        self.reset()
        cpu, arm = self.cpu, self.arm
        for name, address in WORDS.items():
            cpu.mem_write(address, struct.pack('<I', c[name]))
        for name, address in BYTES.items():
            cpu.mem_write(address, bytes([c[name]]))
        for start, values in ((0x200480, c['filter0']), (0x200500, c['filter1'])):
            cpu.mem_write(start, struct.pack('<32I', *values))
        cpu.mem_write(0x203000, bytes([0, 0, c['clamp_flag'], c['write_flag']]))
        cpu.reg_write(arm.UC_ARM_REG_R4, 0x200424)
        cpu.reg_write(arm.UC_ARM_REG_R6, c['stretch'])
        self.stores.clear(); self.visited.clear()
        cpu.emu_start(0x53A3, 0x55A6, count=16384)
        if cpu.reg_read(arm.UC_ARM_REG_PC) != 0x55A6 or cpu.reg_read(arm.UC_ARM_REG_SP) != 0x203000:
            raise ValueError('response slice failed to stop at the original boundary')
        expected = response_values(c)
        actual = {a: cpu.mem_read(int(a, 0), 1)[0] for a in expected['bytes']}
        filters = [list(struct.unpack('<32I', cpu.mem_read(start, 128))) for start in (0x200480, 0x200500)]
        derived = int.from_bytes(cpu.mem_read(0x200474, 4), 'little')
        if actual != expected['bytes'] or filters != [expected['filter0'], expected['filter1']] or derived != expected['derived']:
            raise ValueError(('response mismatch', c, actual, expected, filters, derived))
        if [w['address'] for w in self.stores].count('0x200bc3') != 1:
            raise ValueError('unexpected response coefficient write count')
        return {'inputs': c, 'expected': expected, 'actual_bytes': actual, 'response_stores': self.stores.copy()}


class SequenceRunner(IntegrationRunner):
    def __init__(self, raw):
        super().__init__(raw)
        self.ratio_coefficients = []

    def reset(self):
        super().reset()
        for address, value in ((0x2005E4, 4095), (0x200AC8, 1000), (0x200ACC, 0)):
            self.cpu.mem_write(address, struct.pack('<I', value))
        for address, value in ((0x2005D4, 1), (0x2005D7, 80), (0x200BC2, 7), (0x200BC3, 3), (0x200588, 20)):
            self.cpu.mem_write(address, bytes([value]))

    def trace(self, cpu, address, size, user):
        super().trace(cpu, address, size, user)
        if address == 0x549A:
            self.ratio_coefficients.append(self.byte(0x200BC3))


def sequential_calls(raw):
    runner = SequenceRunner(raw)
    first = runner.sample(dict(capture=2000, percent=50, clock_enabled=False))
    results = [{'call': 1, 'scalar_response_input': first['scalar']['inputs']['response'],
                'ratio_response_input': runner.ratio_coefficients[-1],
                'response_bc2_after': runner.byte(0x200BC2), 'response_bc3_after': runner.byte(0x200BC3)}]
    # Restore the synthetic external return link, preserving all SRAM and the
    # original first call's state updates for the next complete control call.
    runner.cpu.reg_write(runner.arm.UC_ARM_REG_LR, 0x3F00)
    result = runner.call(0x50F0, [])
    if result['status'] != 'returned':
        raise ValueError('second complete control call failed')
    results.append({'call': 2, 'scalar_response_input': runner.scalar['inputs']['response'],
                    'ratio_response_input': runner.ratio_coefficients[-1],
                    'response_bc2_after': runner.byte(0x200BC2), 'response_bc3_after': runner.byte(0x200BC3)})
    if [(c['scalar_response_input'], c['ratio_response_input'], c['response_bc2_after'], c['response_bc3_after'])
        for c in results] != [(7, 3, 100, 80), (100, 80, 100, 80)]:
        raise ValueError(('response ordering mismatch', results))
    return results


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('image', type=Path)
    p.add_argument('--output', type=Path, required=True)
    args = p.parse_args()
    raw = args.image.read_bytes()
    if hashlib.sha256(raw).hexdigest() != SHA:
        raise ValueError('source identity mismatch')
    r = ResponseRunner(raw)
    cases = [defaults(source_select=s, filter_enable=f, previous_response=v)
             for s in (0, 1, 2) for f in (0, 1, 2) for v in (0, 1, 50, 255)]
    cases += [defaults(**c) for c in
              ({'multiplier0': 0, 'multiplier1': 0},
               {'multiplier0': 1, 'multiplier1': 0, 'source_select': 1, 'capture': 1, 'previous_response': 255},
               {'filter0': [0xFFFFFFFF]*32},
               {'filter1': [0xFFFFFFFF]*32, 'filter_enable': 1},
               {'source_offset0': 0xFFFFFFFF, 'source_offset1': 0xFFFFFFFF},
               {'source_offset1': 0x80000000}, {'source_offset1': 216},
               {'source_clamp': 0xFFFFFFFF}, {'ratio_denominator': 0},
               {'ratio_denominator': 0x80000000}, {'ratio_numerator': 0xC0C00000},
               {'ratio_numerator': 0x7F7FFFFF, 'ratio_denominator': 1})]
    rng = random.Random(0x53A2)
    finite = (0, 0x80000000, 1, 0x3F800000, 0xBF800000, 0x40000000,
              0x40C00000, 0xC0C00000, 0x7F7FFFFF, 0xFF7FFFFF)
    for _ in range(1024):
        c = defaults()
        for name in WORDS:
            c[name] = rng.getrandbits(32)
        for name in BYTES:
            c[name] = rng.randrange(256)
        c.update(ratio_numerator=rng.choice(finite), ratio_denominator=rng.choice(finite),
                 filter_enable=rng.randrange(3), source_select=rng.randrange(3), stretch=rng.getrandbits(32),
                 filter0=[rng.getrandbits(32) for _ in range(32)],
                 filter1=[rng.getrandbits(32) for _ in range(32)])
        cases.append(c)
    examples = []; union = set()
    for n, c in enumerate(cases):
        result = r.sample(c)
        union.update(r.visited)
        if n < 55:
            examples.append(result)
    decode = json.loads((ROOT / 'audit/data/main_control_binaryninja.json').read_text())
    starts = {int(i['address'], 0) for block in decode['ranges'] for i in block['instructions']
              if 0x53A2 <= int(i['address'], 0) < 0x55A6}
    doc = {'format': 'quadzilla-control-response-emulation-v1', 'raw_sha256': SHA,
           'cpu': 'ARM926 functional surrogate', 'cases': len(cases), 'mismatches': 0, 'seed': '0x53a2',
           'examples': examples, 'visited': [hex(a) for a in sorted(starts & union)],
           'sequential_complete_calls': sequential_calls(raw),
           'unvisited': [hex(a) for a in sorted(starts-union)],
           'limits': ['entry inside 0x50F0 with synthetic caller registers/frame and stable SRAM',
                      'all reached conversion/filter helpers execute original bytes; no helper result stubs',
                      'ratio source float words restricted to finite inputs; arithmetic overflow infinities included',
                      'float exception/status byte is not compared by this response reference',
                      'slice stops before the separately reviewed ratio scorer 0x46D0 and threshold helper 0x4698',
                      'no live writer admission, physical-unit, interrupt or full firmware completion claim']}
    args.output.write_text(json.dumps(doc, indent=2)+'\n')
    print(f'{len(cases)} response slices, zero differences; {len(starts & union)}/{len(starts)} starts visited')


if __name__ == '__main__':
    main()
