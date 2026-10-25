#!/usr/bin/env python3
"""Exercise the original outgoing state routine with controlled SRAM and USART registers."""
import argparse
import hashlib
import json
from pathlib import Path

from audit_aid_tables import AidRunner, SHA


BASE = 0x2007C8


class OutgoingRunner(AidRunner):
    def __init__(self, raw):
        super().__init__(raw)
        self.allowed_ranges = ((0x71D0, 0x720C), (0x7AF8, 0x7B0A),
                               (0x7B38, 0x7B44), (0x7B4C, 0x7B58),
                               (0x7B60, 0x7EFC), (0x7F58, 0x800A),
                               (0x81A8, 0x84FE))
        self.cpu.mem_map(0xFFFC0000, 0x2000)
        self.writes = []
        self.record = False
        self.cpu.hook_add(self.uc.UC_HOOK_MEM_WRITE, self.write)

    def write(self, cpu, access, address, size, value, user):
        if self.record and (BASE <= address < BASE + 0xC8 or
                            0xFFFC0000 <= address < 0xFFFC2000):
            self.writes.append({'pc': hex(cpu.reg_read(self.arm.UC_ARM_REG_PC)),
                                'address': hex(address), 'size': size,
                                'value': hex(value & ((1 << (size * 8)) - 1))})

    def sample(self, label, flags=(), counts=(0, 0), lists=((), ()), ready=True,
               seeds=()):
        self.reset()
        self.cpu.mem_write(0xFFFC0000, bytes(0x2000))
        self.cpu.mem_write(0x20070B, bytes([int(ready)]))
        for offset, value in flags:
            self.cpu.mem_write(BASE + offset, bytes([value]))
        for offset, sequence in seeds:
            self.cpu.mem_write(BASE + offset, bytes(sequence))
        for offset, value in ((0x13, counts[0]), (0x18, counts[1])):
            self.cpu.mem_write(BASE + offset, bytes([value]))
        for offset, sequence in ((0x88, lists[0]), (0xA8, lists[1])):
            self.cpu.mem_write(BASE + offset, bytes(sequence))
        self.writes.clear()
        self.visited.clear()
        self.record = True
        result = self.call(0x81A8, [])
        self.record = False
        row = {'label': label, 'flags': [[hex(k), v] for k, v in flags],
               'ready': ready, 'source_counts': list(counts), 'result': result,
               'after_counts': [self.cpu.mem_read(BASE + o, 1)[0]
                                for o in (0x13, 0x14, 0x18, 0x19)],
               'after_flags': {hex(o): self.cpu.mem_read(BASE + o, 1)[0]
                               for o in (0, 1, 2, 3, 4, 5, 7, 8, 9, 0xB,
                                         0xC, 0xE, 0xF, 0x10, 0x11, 0x12,
                                         0x15, 0x16, 0x17, 0x1A, 0x1B, 0x1C,
                                         0x1D, 0x1E)},
               'writes': self.writes.copy(),
               'visited_outgoing': [hex(a) for a in sorted(self.visited)
                                    if 0x81A8 <= a < 0x84FE],
               'visited_helpers': [hex(a) for a in sorted(self.visited)
                                   if not 0x81A8 <= a < 0x84FE]}
        if result['status'] != 'returned':
            raise RuntimeError(row)
        return row


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('image', type=Path)
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    raw = args.image.read_bytes()
    if len(raw) != 32000 or hashlib.sha256(raw).hexdigest() != SHA:
        raise ValueError('unexpected firmware image')
    runner = OutgoingRunner(raw)
    cases = [
        ('not_ready', (), (0, 0), ((), ()), False),
        ('idle', (), (0, 0), ((), ()), True),
        ('status_9', ((9, 1),), (0, 0), ((), ()), True),
        ('status_8', ((8, 1), (6, 1)), (0, 0), ((), ()), True),
        ('status_7', ((7, 1), (6, 1)), (0, 0), ((), ()), True),
        ('status_c', ((0xC, 1), (0xA, 1)), (0, 0), ((), ()), True),
        ('status_b', ((0xB, 1), (0xA, 1)), (0, 0), ((), ()), True),
        ('status_f', ((0xF, 1), (0xD, 1)), (0, 0), ((), ()), True),
        ('status_e', ((0xE, 1), (0xD, 1)), (0, 0), ((), ()), True),
        ('list_a_bit', ((0x11, 1),), (1, 0), ((1,), ()), True),
        ('list_a_reset', ((0x10, 1),), (1, 0), ((1,), ()), True),
        ('list_b_bit', ((0x16, 1),), (0, 1), ((), (1,)), True),
        ('list_b_reset', ((0x15, 1),), (0, 1), ((), (1,)), True),
        ('list_a_deferred', ((0x11, 1),), (1, 0), ((226,), ()), True),
        ('list_a_deferred_reset', ((0x10, 1),), (1, 0), ((226,), ()), True),
        ('list_a_latch_reset', ((0x10, 1), (0x11, 1), (0x12, 1)),
         (1, 0), ((226,), ()), True),
        ('list_b_deferred', ((0x16, 1),), (0, 1), ((), (226,)), True),
        ('list_b_deferred_reset', ((0x15, 1),), (0, 1), ((), (226,)), True),
        ('list_b_latch_reset', ((0x15, 1), (0x16, 1), (0x17, 1)),
         (0, 1), ((), (226,)), True),
        ('list_a_14', ((0x11, 1),), (14, 0), (tuple(range(1, 15)), ()), True),
        ('list_b_14', ((0x16, 1),), (0, 14), ((), tuple(range(1, 15))), True),
        ('list_b_15_synthetic', ((0x16, 1),), (0, 15),
         ((), tuple(range(1, 16))), True),
        ('status_8_deferred', ((8, 1), (6, 1)), (0, 0), ((), ()),
         True, ((0x48, (226,)),)),
        ('status_7_deferred', ((7, 1), (6, 1)), (0, 0), ((), ()),
         True, ((0x48, (226,)),)),
        ('status_c_deferred', ((0xC, 1), (0xA, 1)), (0, 0), ((), ()),
         True, ((0x68, (226,)),)),
        ('status_b_deferred', ((0xB, 1), (0xA, 1)), (0, 0), ((), ()),
         True, ((0x68, (226,)),)),
        ('status_f_deferred', ((0xF, 1), (0xD, 1)), (0, 0), ((), ()),
         True, ((0x78, (226,)),)),
        ('status_e_deferred', ((0xE, 1), (0xD, 1)), (0, 0), ((), ()),
         True, ((0x78, (226,)),)),
    ]
    rows = [runner.sample(*case) for case in cases]
    starts = set()
    for row in rows:
        starts.update(int(a, 0) for a in row['visited_outgoing'])
    result = {'format': 'quadzilla-outgoing-state-emulation-v1',
              'raw_sha256': SHA, 'emulator': 'Unicorn ' + runner.uc.__version__,
              'cpu': 'ARM926 functional surrogate', 'entry': '0x81a8',
              'cases': rows, 'visited_outgoing_starts': [hex(a) for a in sorted(starts)],
              'limitations': ['controlled synthetic SRAM flags, counts and AIDs',
                              'USART register page mapped as passive memory',
                              'not device behavior, timing, interrupt or physical reachability evidence']}
    args.output.write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    print(f'{len(rows)} cases, {len(starts)} outgoing instruction starts visited')
    for row in rows:
        print(row['label'], row['result'], row['after_counts'],
              len(row['visited_outgoing']))


if __name__ == '__main__':
    main()
