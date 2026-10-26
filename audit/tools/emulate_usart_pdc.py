#!/usr/bin/env python3
"""Execute USART/PDC helpers with frozen status and explicit US_CR read values."""
import argparse
import hashlib
import itertools
import json
import re
import struct
import sys
from pathlib import Path

from emulate_integer_runtime import Runner, SHA

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'tools'))
from model_pdc_queue import QueueState, stage

U = 0xFFFC0000
CODE = ((0x7178, 0x71BE), (0x71D0, 0x720C), (0x720C, 0x7256), (0x725C, 0x72FE))


class Harness(Runner):
    def __init__(self, raw):
        super().__init__(raw)
        self.allowed_ranges = CODE
        self.cpu.mem_map(U, 0x1000)
        self.cpu.mem_map(0xFFFFF000, 0x1000)
        self.writes = []
        self.cr_read = 0
        self.cpu.hook_add(self.uc.UC_HOOK_MEM_WRITE, self.write)
        self.cpu.hook_add(self.uc.UC_HOOK_MEM_READ, self.read)

    def read(self, cpu, access, address, size, value, _):
        if address == U:
            self.word(U, self.cr_read)

    def write(self, cpu, access, address, size, value, _):
        if 0x202FE0 <= address and address+size <= 0x203000:
            return
        if not (U <= address < U+0x128 or 0xFFFFF000 <= address < 0xFFFFFD00 or
                (address in (0x200AFD, 0x200709, 0x20070A, 0x20070B) and size == 1)):
            raise RuntimeError(f'unexpected write {address:#x}/{size}')
        self.writes.append((address, size, value))

    def word(self, address, value):
        self.cpu.mem_write(address, struct.pack('<I', value))

    def get(self, address):
        return int.from_bytes(self.cpu.mem_read(address, 4), 'little')

    def prepare(self, cr_read=0):
        self.cpu.mem_write(U, bytes(0x1000))
        self.cpu.mem_write(0xFFFFF000, bytes(0x1000))
        for address in (0x200AFD, 0x200709, 0x20070A, 0x20070B):
            self.cpu.mem_write(address, b'\xa5')
        self.writes = []
        self.cr_read = cr_read
        self.visited.clear()

    def call(self, entry, pointer=0, count=0):
        a, c = self.arm, self.cpu
        c.reg_write(a.UC_ARM_REG_CPSR, 0x13)
        c.reg_write(a.UC_ARM_REG_SP, 0x203000)
        c.reg_write(a.UC_ARM_REG_LR, 0x3F00)
        c.reg_write(a.UC_ARM_REG_R0, pointer)
        c.reg_write(a.UC_ARM_REG_R1, count)
        for n in range(4, 12):
            c.reg_write(getattr(a, f'UC_ARM_REG_R{n}'), 0x12340000+n)
        c.emu_start(entry|1, 0x3F00, count=512)
        if c.reg_read(a.UC_ARM_REG_PC) != 0x3F00 or c.reg_read(a.UC_ARM_REG_SP) != 0x203000:
            raise RuntimeError('return or stack mismatch')
        if any(c.reg_read(getattr(a, f'UC_ARM_REG_R{n}')) != 0x12340000+n for n in range(4, 12)):
            raise RuntimeError('preserved register mismatch')


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('image', type=Path)
    p.add_argument('--output', type=Path, required=True)
    args = p.parse_args()
    raw = args.image.read_bytes()
    if hashlib.sha256(raw).hexdigest() != SHA:
        raise ValueError('unexpected source image')
    h = Harness(raw)
    visited, queues, interrupts, inits = set(), [], [], []
    for rx in (False, True):
        cp, cc, np, nc = (0x100, 0x104, 0x110, 0x114) if rx else (0x108, 0x10C, 0x118, 0x11C)
        flag, entry = (0x200AFD, 0x720C) if rx else (0x20070B, 0x71D0)
        for current, nxt, count, cr in itertools.product((0, 3), (0, 5), (0, 16, 65535), (0, 0xAC, 0xFFFFFFFF) if rx else (0,)):
            h.prepare(cr)
            initial = QueueState(0x200800, current, 0x200820, nxt, 0xA5)
            for offset, value in ((cp, initial.current_pointer), (cc, current), (np, initial.next_pointer), (nc, nxt)):
                h.word(U+offset, value)
            expected, outcome = stage(initial, 0x200840, count)
            h.call(entry, 0x200840, count)
            actual = QueueState(h.get(U+cp), h.get(U+cc), h.get(U+np), h.get(U+nc), h.cpu.mem_read(flag, 1)[0])
            if actual != expected:
                raise RuntimeError((rx, current, nxt, count, actual, expected))
            expected_writes = [(flag, 1, 0)]
            if outcome == 'current':
                expected_writes += [(U+cp, 4, 0x200840), (U+cc, 4, count), (U+np, 4, 0), (U+nc, 4, 0)]
            elif outcome == 'next':
                expected_writes += [(U+np, 4, 0x200840), (U+nc, 4, count)]
            expected_writes += ([(U, 4, cr|0x800), (U+8, 4, 0x100), (U+0x120, 4, 1)] if rx else
                                [(U+8, 4, 0x10), (U+0x120, 4, 0x100)])
            if h.writes != expected_writes:
                raise RuntimeError(('queue write trace', h.writes, expected_writes))
            visited.update(h.visited)
            queues.append({'entry': hex(entry), 'current_count': current, 'next_count': nxt,
                           'requested_count': count, 'us_cr_read': hex(cr), 'outcome': outcome,
                           'writes': [[hex(a), n, hex(v)] for a, n, v in h.writes]})
    for timeout, tx, enabled in itertools.product((0, 1), repeat=3):
        h.prepare()
        h.word(U+0x14, timeout*0x100+tx*0x10)
        h.word(U+0x124, enabled*0x100)
        h.word(U+0x104, 16)
        h.call(0x7178)
        expected = []
        if timeout:
            expected += [(0x200AFD, 1, 1), (U+0xC, 4, 0x100), (U+0x104, 4, 0), (U+0x120, 4, 2)]
        if tx and enabled:
            expected += [(U+0xC, 4, 0x10), (U+0x120, 4, 0x200), (0x20070A, 1, 1), (0x200709, 1, 1)]
        if h.writes != expected:
            raise RuntimeError(('interrupt write trace', h.writes, expected))
        visited.update(h.visited)
        interrupts.append({'timeout': timeout, 'tx_end': tx, 'tx_enabled': enabled,
                           'writes': [[hex(a), n, hex(v)] for a, n, v in h.writes]})
    for cr in (0, 0xAC, 0xFFFFFFFF):
        h.prepare(cr)
        h.call(0x725C)
        if any(h.get(U+o) != 0 for o in range(0x100, 0x120, 4)):
            raise RuntimeError('initializer left nonzero DMA pair')
        for address, value in ((U+0x20, 0x34), (U+4, 0x8C0), (U+0x24, 0x79), (0xFFFFF098, 0x7179), (0xFFFFF018, 0x21)):
            if h.get(address) != value:
                raise RuntimeError(('initializer register', hex(address)))
        control_writes = [v for a, n, v in h.writes if a == U]
        if control_writes != [0xAC, cr|0x800, 0x40, 0x10]:
            raise RuntimeError(('initializer control writes', control_writes))
        if h.cpu.mem_read(0x20070B, 1)[0] != 1:
            raise RuntimeError('initializer software flag')
        visited.update(h.visited)
        inits.append({'us_cr_read': hex(cr), 'writes': [[hex(a), n, hex(v)] for a, n, v in h.writes]})
    decode = json.loads(Path('audit/data/uart_buffer_binaryninja.json').read_text())
    if decode['raw_sha256'] != SHA:
        raise ValueError('decode source identity mismatch')
    expected_starts = {int(i['address'], 0) for r in decode['ranges'] for i in r['instructions']
                       if any(lo <= int(i['address'], 0) < hi for lo, hi in CODE)}
    if visited != expected_starts:
        raise RuntimeError(('instruction coverage', visited ^ expected_starts))
    pools = ((0x71C0, 0x71D0), (0x7258, 0x725C), (0x7300, 0x7364))
    refs = {}
    for r in decode['ranges']:
        for ins in r['instructions']:
            at = int(ins['address'], 0)
            if at not in expected_starts:
                continue
            m = re.fullmatch(r'ldr\s+r\d+, \[pc, #0x([0-9a-f]+)\]', ins['text'].strip())
            if m:
                target = ((at+4)&~3)+int(m.group(1), 16)
                refs.setdefault(target, []).append(at)
            m = re.fullmatch(r'b[a-z]*\s+#(0x[0-9a-f]+)', ins['text'].strip())
            if m and int(m.group(1), 0) not in expected_starts:
                raise RuntimeError('direct branch leaves body starts')
    if set(refs) != {a for lo, hi in pools for a in range(lo, hi, 4)}:
        raise RuntimeError(('literal island references', sorted(refs)))
    for at, value in ((0x71BE, b'\xc0\x46'), (0x7256, b'\xff\xff'), (0x72FE, b'\xc0\x46')):
        if raw[at-0x4000:at-0x4000+2] != value:
            raise RuntimeError('alignment bytes differ')
    result = {'format': 'quadzilla-usart-pdc-emulation-v1', 'raw_sha256': SHA,
              'emulator': 'Unicorn '+h.uc.__version__, 'code_ranges': [[hex(a), hex(b)] for a, b in CODE],
              'mismatches': [], 'queue_cases': queues, 'interrupt_cases': interrupts, 'initializer_cases': inits,
              'visited_addresses': [hex(a) for a in sorted(visited)],
              'literal_words': [{'address': hex(a), 'value': hex(struct.unpack_from('<I', raw, a-0x4000)[0]),
                                 'load_sites': [hex(x) for x in refs[a]]} for a in sorted(refs)],
              'limitations': ['Frozen DMA/status snapshot; no transfer or promotion timing',
                              'US_CR is write-only: each read is explicitly supplied synthetic data, not register readback',
                              'ARM926 functional surrogate; no controller or serial traffic']}
    args.output.write_text(json.dumps(result, indent=2)+'\n', encoding='utf-8')
    print(f'{len(queues)} queue cases, {len(interrupts)} IRQ cases, {len(inits)} initializers; {len(visited)} starts')


if __name__ == '__main__':
    main()
