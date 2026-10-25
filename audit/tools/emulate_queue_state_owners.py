#!/usr/bin/env python3
"""Execute queue setup/reset helpers and record writes to the shared state block."""
import argparse
import hashlib
import json
import struct
from pathlib import Path

from audit_aid_tables import AidRunner, SHA


BASE = 0x2007C8


class QueueOwnerRunner(AidRunner):
    def __init__(self, raw):
        super().__init__(raw)
        self.allowed_ranges = ((0x720C, 0x7256), (0x7B1C, 0x7B28),
                               (0x7EFC, 0x7F28), (0x7FD8, 0x800A),
                               (0x800C, 0x8034))
        self.cpu.mem_map(0xFFFC0000, 0x2000)
        self.writes = []
        self.record = False
        self.cpu.hook_add(self.uc.UC_HOOK_MEM_WRITE, self.write)

    def write(self, cpu, access, address, size, value, user):
        if self.record and BASE <= address < BASE + 0xC8:
            self.writes.append({'pc': hex(cpu.reg_read(self.arm.UC_ARM_REG_PC)),
                                'address': hex(address), 'size': size,
                                'value': hex(value & ((1 << (8 * size)) - 1))})

    def setup(self):
        self.reset()
        self.cpu.mem_write(0xFFFC0000, bytes(0x2000))
        self.cpu.mem_write(0x200728, struct.pack('<I', 0xFFFC0000))
        self.cpu.mem_write(0x201000, bytes(range(1, 16)))
        self.writes.clear()
        self.visited.clear()

    def sample(self, label, entry, count=0, busy_e=0, busy_f=0):
        self.setup()
        self.cpu.mem_write(BASE + 0xE, bytes([busy_e]))
        self.cpu.mem_write(BASE + 0xF, bytes([busy_f]))
        self.cpu.mem_write(BASE + 0x13, b'\x0e')
        self.cpu.mem_write(BASE + 0x18, b'\x0d')
        if entry == 0x800C:
            for offset in (7, 8, 9, 0xB, 0xC, 0x11, 0x12,
                           0x15, 0x16, 0x17):
                self.cpu.mem_write(BASE + offset, b'\x01')
        self.record = True
        result = self.call(entry, [0x201000, count] if entry == 0x7EFC else [])
        self.record = False
        if result['status'] != 'returned':
            raise RuntimeError((label, result))
        return {'label': label, 'entry': hex(entry), 'count_arg': count,
                'busy_e': busy_e, 'busy_f': busy_f, 'result': result,
                'counts': {hex(offset): self.cpu.mem_read(BASE + offset, 1)[0]
                           for offset in (0xD, 0x13, 0x14, 0x18, 0x19)},
                'flags': {hex(offset): self.cpu.mem_read(BASE + offset, 1)[0]
                          for offset in (7, 8, 9, 0xB, 0xC, 0xE, 0xF,
                                         0x11, 0x12, 0x15, 0x16, 0x17)},
                'copied': bytes(self.cpu.mem_read(BASE + 0x78, 14)).hex(),
                'writes': self.writes.copy(),
                'visited': [hex(a) for a in sorted(self.visited)]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('image', type=Path)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    raw = args.image.read_bytes()
    if len(raw) != 32000 or hashlib.sha256(raw).hexdigest() != SHA:
        raise ValueError('unexpected firmware image')
    runner = QueueOwnerRunner(raw)
    cases = [('queue_zero', 0x7EFC, 0, 0, 0),
             ('queue_one', 0x7EFC, 1, 0, 0),
             ('queue_fourteen', 0x7EFC, 14, 0, 0),
             ('queue_fifteen', 0x7EFC, 15, 0, 0),
             ('queue_255', 0x7EFC, 255, 0, 0),
             ('busy_e', 0x7EFC, 1, 1, 0),
             ('busy_f', 0x7EFC, 1, 0, 1),
             ('reset_flags', 0x800C, 0, 1, 1)]
    rows = [runner.sample(*case) for case in cases]
    visited = {int(a, 0) for row in rows for a in row['visited']}
    output = {'format': 'quadzilla-queue-state-owners-emulation-v1',
              'raw_sha256': SHA, 'cpu': 'ARM926 functional surrogate',
              'emulator': 'Unicorn ' + runner.uc.__version__,
              'cases': rows, 'visited_starts': [hex(a) for a in sorted(visited)],
              'limits': ['controlled source list and state flags',
                         'USART register page is passive memory',
                         'direct helper effects do not prove absence of indirect writers elsewhere']}
    args.output.write_text(json.dumps(output, indent=2) + '\n', encoding='utf-8')
    print(f'{len(rows)} cases; queue count outputs:',
          [(row['label'], row['counts']['0xd']) for row in rows])


if __name__ == '__main__':
    main()
