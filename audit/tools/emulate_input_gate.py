#!/usr/bin/env python3
"""Execute the input-gated state helper against its instruction-derived contract."""
import argparse
import hashlib
import itertools
import json
import re
import struct
from pathlib import Path

from emulate_integer_runtime import Runner, SHA

STATE, ACTIVE = 0x20042C, 0x20042D
FLAGS = (0x200719, 0x20071A, 0x20071B, 0x20071E)
TIMER = 0x200730


def model(state, enabled, mode, capture, source, tps, event, duration):
    out = {STATE: state, ACTIVE: 0, FLAGS[0]: 0x5A, FLAGS[1]: 0x6B,
           FLAGS[2]: event, FLAGS[3]: 0x7C, TIMER: 0x12345678}
    if not enabled:
        out[STATE] = 0
    elif mode == 0:
        idle = capture < 1000 and source == 0 and tps == 0
        if state == 1:
            if not idle:
                out[FLAGS[0]], out[STATE] = 0, 0
            elif event:
                out[STATE], out[FLAGS[3]] = 3, 1
        elif state == 3:
            if source == 0 and tps == 0:
                out[ACTIVE] = 1
            else:
                out[STATE] = 0
        elif idle:
            out[TIMER] = duration * 10000
            out[FLAGS[1]], out[FLAGS[2]], out[FLAGS[0]], out[STATE] = 1, 0, 1, 1
    return out


def execute(runner, values):
    state, enabled, mode, capture, source, tps, event, duration = values
    cpu, arm = runner.cpu, runner.arm
    for a, v in ((STATE, state), (ACTIVE, 0xA5), (0x2006E2, enabled),
                 (0x2005D7, tps), (FLAGS[0], 0x5A), (FLAGS[1], 0x6B),
                 (FLAGS[2], event), (FLAGS[3], 0x7C)):
        cpu.mem_write(a, bytes((v,)))
    for a, v in ((0x2005EC, capture), (0x2005F0, source), (TIMER, 0x12345678)):
        cpu.mem_write(a, struct.pack('<I', v))
    cpu.mem_write(0x2006E4, struct.pack('<H', duration))
    cpu.reg_write(arm.UC_ARM_REG_CPSR, 0x13)
    cpu.reg_write(arm.UC_ARM_REG_SP, 0x203000)
    cpu.reg_write(arm.UC_ARM_REG_LR, 0x3F00)
    cpu.reg_write(arm.UC_ARM_REG_R0, mode)
    for n in range(4, 12):
        cpu.reg_write(getattr(arm, f'UC_ARM_REG_R{n}'), 0x12340000+n)
    runner.visited.clear()
    cpu.emu_start(0x4819, 0x3F00, count=256)
    if cpu.reg_read(arm.UC_ARM_REG_PC) != 0x3F00 or cpu.reg_read(arm.UC_ARM_REG_SP) != 0x203000:
        raise RuntimeError('helper failed to return with balanced stack')
    if any(cpu.reg_read(getattr(arm, f'UC_ARM_REG_R{n}')) != 0x12340000+n for n in range(4, 12)):
        raise RuntimeError('callee-saved register changed')
    actual = {a: int.from_bytes(cpu.mem_read(a, 4 if a == TIMER else 1), 'little')
              for a in (STATE, ACTIVE, *FLAGS, TIMER)}
    expected = model(*values)
    if actual != expected or cpu.reg_read(arm.UC_ARM_REG_R0) != expected[ACTIVE]:
        raise RuntimeError((values, actual, expected))
    return actual


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('image', type=Path)
    p.add_argument('--decode', type=Path, default=Path('audit/data/input_gate_binaryninja.json'))
    p.add_argument('--output', type=Path, required=True)
    args = p.parse_args()
    raw = args.image.read_bytes()
    decode = json.loads(args.decode.read_text())
    if hashlib.sha256(raw).hexdigest() != SHA or decode['raw_sha256'] != SHA:
        raise ValueError('unexpected image or decode')
    row, = decode['ranges']
    if (row['start'], row['end'], row['architecture']) != ('0x4818', '0x48c4', 'thumb2') or 'decode_stopped_at' in row:
        raise ValueError('unexpected decode bounds')
    cursor, refs = 0x4818, {}
    for ins in row['instructions']:
        at = int(ins['address'], 0)
        if at != cursor:
            raise ValueError('instruction decode gap')
        cursor += ins['length']
        m = re.fullmatch(r'ldr\s+r\d+, \[pc, #0x([0-9a-f]+)\]', ins['text'].strip())
        if m:
            a = ((at+4)&~3)+int(m.group(1), 16)
            refs.setdefault(a, []).append(at)
    expected_refs = set(range(0x48C4, 0x48E8, 4)) | {0x4950, 0x4954, 0x4958}
    if cursor != 0x48C4 or set(refs) != expected_refs or raw[0x48C2-0x4000:0x48C4-0x4000] != b'\xc0\x46':
        raise ValueError('literal pool or alignment differs')
    runner = Runner(raw)
    runner.allowed_ranges = ((0x4818, 0x48C2),)
    allowed = {STATE, ACTIVE, *FLAGS}

    def write_guard(cpu, access, address, size, value, _):
        if 0x202FE8 <= address and address+size <= 0x203000:
            return
        if not ((size == 1 and address in allowed) or (size == 4 and address == TIMER)):
            raise RuntimeError(f'unexpected data write {address:#x}/{size}')

    runner.cpu.hook_add(runner.uc.UC_HOOK_MEM_WRITE, write_guard)
    visited, examples, count = set(), [], 0
    for state, enabled, mode, capture, source, tps, event in itertools.product(
            range(256), (0, 1), (0, 1), (999, 1000), (0, 1), (0, 1), (0, 1)):
        values = (state, enabled, mode, capture, source, tps, event, 123)
        actual = execute(runner, values)
        count += 1
        visited.update(runner.visited)
        if state in (0, 1, 3, 255) and enabled == 1 and mode == 0 and capture == 999 and source == 0 and tps == 0:
            examples.append({'inputs': list(values), 'result': {hex(a): v for a, v in actual.items()}})
    for values in ((0, 255, 0, 0, 0, 0, 255, 0), (0, 1, 0, 0, 0, 0, 1, 65535),
                   (3, 1, 0, 0xFFFFFFFF, 0, 0, 0, 1), (1, 1, 0, 0xFFFFFFFF, 0, 0, 0, 1),
                   (3, 1, 0xFFFFFFFF, 0, 0, 0, 1, 1), (3, 1, 0, 0, 0xFFFFFFFF, 255, 1, 1)):
        actual = execute(runner, values)
        count += 1
        visited.update(runner.visited)
        examples.append({'inputs': list(values), 'result': {hex(a): v for a, v in actual.items()}})
    expected_starts = {int(i['address'], 0) for i in row['instructions'] if int(i['address'], 0) < 0x48C2}
    if visited != expected_starts:
        raise RuntimeError(f'unvisited or unexpected starts: {visited ^ expected_starts}')
    result = {'format': 'quadzilla-input-gate-emulation-v1', 'raw_sha256': SHA,
              'emulator': 'Unicorn '+runner.uc.__version__, 'cases': count, 'mismatches': [],
              'input_order': ['state', 'enabled', 'mode_r0', 'capture_word', 'source_word', 'input_byte', 'event_byte', 'duration_halfword'],
              'limitations': ['Synthetic state; no complete writer or interrupt audit', 'ARM926 functional surrogate; no physical timing or hardware I/O'],
              'instruction_range': ['0x4818', '0x48c2'], 'alignment_nop': ['0x48c2', '0x48c4'],
              'literal_words': [{'address': hex(a), 'value': hex(struct.unpack_from('<I', raw, a-0x4000)[0]),
                                 'load_sites': [hex(x) for x in refs[a]]} for a in sorted(refs)],
              'visited_addresses': [hex(a) for a in sorted(visited)], 'examples': examples}
    args.output.write_text(json.dumps(result, indent=2)+'\n', encoding='utf-8')
    print(f'{count} matching calls; {len(visited)} body starts visited; {len(refs)} literals')


if __name__ == '__main__':
    main()
