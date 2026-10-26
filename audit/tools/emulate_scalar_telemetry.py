#!/usr/bin/env python3
"""Check original 0x4D38 bytes against the scalar contract in synthetic SRAM."""
import argparse
import hashlib
import json
import random
import struct
import sys
from pathlib import Path

from audit_aid_tables import AidRunner
from emulate_integer_runtime import SHA

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tools'))
from model_scalar_telemetry import calculate


def defaults(**changes):
    c = dict(mode=0, refresh=0, response_flags=[0, 0, 0, 0], gate_sum=[0, 0], selector=100,
             enabled=1, base=1000, capture=2000, knots=[200, 400, 600, 800, 1000],
             coefficient=20, response=50, threshold=0, working61=10, status=0,
             percent0=50, percent1=20, cell=30, row=10, column=10,
             ignored_r0=0, ignored_r2=0)
    c.update(changes)
    return c


def run(runner, c):
    runner.reset()
    cpu, arm = runner.cpu, runner.arm
    def byte(address, value):
        cpu.mem_write(address, bytes([value]))
    def word(address, value):
        cpu.mem_write(address, struct.pack('<I', value))
    cpu.mem_write(0x200424, bytes(0x50))
    for address, value in [(0x200425, c['mode']), (0x200426, c['refresh']),
                           (0x200432, c['enabled']), (0x200433, c['gate_sum'][0]),
                           (0x200434, c['gate_sum'][1]), (0x200588, c['coefficient']),
                           (0x200BC2, c['response']), (0x2005B3, c['threshold']),
                           (0x2005D7, c['status']), (0x2005B0, c['percent0']),
                           (0x2005B1, c['percent1'])]:
        byte(address, value)
    for address, value in zip((0x200BED, 0x200BF1, 0x200BF3, 0x200BF4), c['response_flags']):
        byte(address, value)
    for i, value in enumerate(c['knots']):
        word(0x200458 + 4*i, value)
    for address, value in ((0x20046C, c['working61']), (0x2005E8, c['base']), (0x2005EC, c['capture'])):
        word(address, value)
    byte(0x200000 + 20*c['row'] + c['column'], c['cell'])
    word(0x203000, c['row'])
    preserved = []
    for n in range(4, 12):
        reg = getattr(arm, f'UC_ARM_REG_R{n}')
        value = 0x12340000 + n
        cpu.reg_write(reg, value)
        preserved.append((reg, value))
    outcome = runner.call(0x4D38, [c['ignored_r0'], c['selector'], c['ignored_r2'], c['column']])
    if outcome['status'] != 'returned' or any(cpu.reg_read(r) != v for r, v in preserved):
        raise ValueError(('return or register contract failed', c, outcome))
    def readword(address):
        return int.from_bytes(cpu.mem_read(address, 4), 'little')
    actual = dict(return_value=outcome['r0'], cap=readword(0x200450),
                  mode=cpu.mem_read(0x200425, 1)[0], refresh=cpu.mem_read(0x200426, 1)[0],
                  knots=[readword(0x200458+4*i) for i in range(5)])
    expected = calculate(c)
    if actual != dict(return_value=expected['return'], **{k: expected[k] for k in ('cap', 'mode', 'refresh', 'knots')}):
        raise ValueError(('scalar mismatch', c, actual, expected))
    # Execute just the original post-call cap/floor/store slice with a synthetic
    # caller frame; this does not execute the complete 0x50F0 caller.
    cpu.reg_write(arm.UC_ARM_REG_R0, outcome['r0'])
    cpu.reg_write(arm.UC_ARM_REG_R4, 0x200424)
    cpu.reg_write(arm.UC_ARM_REG_SP, 0x202FFC)
    cpu.emu_start(0x5263, 0x527A, count=32)
    if cpu.reg_read(arm.UC_ARM_REG_PC) != 0x527A or cpu.reg_read(arm.UC_ARM_REG_SP) != 0x203000:
        raise ValueError('caller slice stop/stack mismatch')
    actual['caller_store'] = readword(0x200604)
    if actual['caller_store'] != expected['caller_store']:
        raise ValueError(('caller cap/floor mismatch', c, actual, expected))
    return {'inputs': c, 'actual': actual, 'reference': expected}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('image', type=Path)
    p.add_argument('--output', type=Path, required=True)
    args = p.parse_args()
    raw = args.image.read_bytes()
    if hashlib.sha256(raw).hexdigest() != SHA:
        raise ValueError('source identity mismatch')
    runner = AidRunner(raw)
    runner.allowed_ranges += ((0x4D38, 0x5016), (0x5262, 0x527A))
    examples, count = [], 0
    def check(c, retain=False):
        nonlocal count
        result = run(runner, c)
        count += 1
        if retain:
            examples.append(result)
    edges = (0, 999, 1000, 1004, 1005, 1199, 1200, 1499, 1500, 1999, 2000, 2499,
             2500, 2999, 3000, 3499, 3500, 0x7FFFFFFF, 0x80000000, 0xFFFFFFFF)
    for mode in (0, 1):
        for capture in range(4001):
            check(defaults(mode=mode, capture=capture), capture in edges)
    for flags in ([0, 0, 0, 0], [1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]):
        check(defaults(refresh=1, mode=1, response_flags=flags), True)
    for cell in range(256):
        check(defaults(cell=cell), cell in (0, 1, 127, 128, 255))
    for capture in edges:
        for status in (50, 51):
            check(defaults(threshold=51, status=status, capture=capture), True)
    for changes in ({'enabled': 0}, {'selector': 0}, {'gate_sum': [50, 50]},
                    {'knots': [0xFFFFFFFF]*5, 'mode': 1}, {'knots': [900, 100, 700, 0, 10]},
                    {'knots': [0xFFFFFFFF]*5, 'capture': 3500},
                    {'base': 0xFFFFFFFF}, {'cell': 128, 'percent0': 255, 'percent1': 255},
                    {'ignored_r0': 0xFFFFFFFF, 'ignored_r2': 0xDEADBEEF}):
        check(defaults(**changes), True)
    rng = random.Random(0x4D38)
    for _ in range(2000):
        check(defaults(mode=rng.randrange(3), refresh=rng.randrange(2),
                       response_flags=[rng.randrange(2) for _ in range(4)],
                       selector=rng.randrange(256), gate_sum=[rng.randrange(256) for _ in range(2)],
                       enabled=rng.randrange(2), base=rng.getrandbits(32),
                       capture=rng.choice(edges), knots=[rng.getrandbits(32) for _ in range(5)],
                       coefficient=rng.randrange(256), response=rng.randrange(256),
                       threshold=rng.randrange(256), working61=rng.getrandbits(32),
                       status=rng.randrange(256), percent0=rng.randrange(256), percent1=rng.randrange(256),
                       cell=rng.randrange(256), row=rng.randrange(20), column=rng.randrange(20)))
    decode = json.loads((ROOT / 'audit/data/scalar_telemetry_binaryninja.json').read_text())
    starts = {int(i['address'], 0) for i in decode['ranges'][0]['instructions'] if int(i['address'], 0) < 0x5016}
    visited = runner.visited & starts
    missing = starts - visited
    doc = {'format': 'quadzilla-scalar-telemetry-emulation-v1', 'raw_sha256': SHA,
           'cpu': 'ARM926 functional surrogate', 'cases': count, 'mismatches': 0,
           'examples': examples, 'visited': [hex(a) for a in sorted(visited)],
           'unvisited': [hex(a) for a in sorted(missing)], 'preservation': 'SP and R4-R11',
           'limits': ['synthetic SRAM, no hardware or interrupt execution',
                      'R1/R3 and stack inputs restricted to current caller low-byte domain; row/column sampled in 0..19',
                      'not an exhaustive 32-bit arithmetic, writer-reachability or full caller execution proof',
                      'post-call slice 0x5262..0x527A executes with a synthetic caller frame, not an executed full main loop']}
    args.output.write_text(json.dumps(doc, indent=2)+'\n')
    print(f'{count} calls, zero mismatches, {len(visited)}/{len(starts)} starts visited; missing {doc["unvisited"]}')


if __name__ == '__main__':
    main()
