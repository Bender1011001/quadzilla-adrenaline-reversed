#!/usr/bin/env python3
"""Execute the original control-cycle queue-selection continuation with explicit context."""
import argparse
import hashlib
import json
import struct
from pathlib import Path

from audit_aid_tables import SHA
from emulate_queue_state_owners import QueueOwnerRunner


BASE = 0x200788
STATE = 0x2007C8
SOURCES = [BASE + 0x18 + 8 * index for index in range(5)]


class CycleQueueRunner(QueueOwnerRunner):
    def __init__(self, raw):
        super().__init__(raw)
        self.allowed_ranges += ((0x76F0, 0x77A6), (0x7B04, 0x7B0A),
                                (0x81A8, 0x81B8), (0x84F4, 0x84FE))

    def sample(self, label, selector, count, pending=True, busy=False,
               outgoing=False, template_lists=False):
        self.setup()
        if not template_lists:
            for index, source in enumerate(SOURCES):
                self.cpu.mem_write(source, bytes([0x10 * (index + 1) + j
                                                  for j in range(8)]))
        self.cpu.mem_write(BASE + 0xB, bytes([selector]))
        self.cpu.mem_write(BASE + 0xA, bytes([int(outgoing)]))
        if not template_lists:
            self.cpu.mem_write(BASE + 2 + min(selector, 4), bytes([count]))
        effective_slot = min(selector, 4)
        source_count = self.cpu.mem_read(BASE + 2 + effective_slot, 1)[0]
        source_block = bytes(self.cpu.mem_read(SOURCES[effective_slot], 8))
        self.cpu.mem_write(0x200712, bytes([int(pending)]))
        self.cpu.mem_write(STATE + 0xE, bytes([int(busy)]))
        self.cpu.reg_write(self.arm.UC_ARM_REG_R4, BASE)
        self.cpu.reg_write(self.arm.UC_ARM_REG_R5, 0x200712)
        self.cpu.reg_write(self.arm.UC_ARM_REG_R6, 0x200710)
        self.cpu.reg_write(self.arm.UC_ARM_REG_R7, 0x200711)
        self.cpu.reg_write(self.arm.UC_ARM_REG_SP, 0x202FEC)
        self.cpu.mem_write(0x202FEC, struct.pack('<IIIII',
                                                 0x12340004, 0x12340005,
                                                 0x12340006, 0x12340007,
                                                 0x3F00))
        self.writes.clear()
        self.visited.clear()
        self.record = True
        try:
            self.cpu.emu_start(0x76F1, 0x3F00, count=8192)
        except self.uc.UcError as exc:
            raise RuntimeError((label, self.fault, str(exc))) from exc
        finally:
            self.record = False
        if (self.cpu.reg_read(self.arm.UC_ARM_REG_PC) != 0x3F00 or
                self.cpu.reg_read(self.arm.UC_ARM_REG_SP) != 0x203000):
            raise RuntimeError((label, 'continuation did not return cleanly'))
        return {'label': label, 'selector_in': selector, 'count_in': source_count,
                'pending_in': pending, 'busy_in': busy, 'outgoing_in': outgoing,
                'template_lists': template_lists,
                'source_address': hex(SOURCES[effective_slot]),
                'source_block': source_block.hex(),
                'selector_out': self.cpu.mem_read(BASE + 0xB, 1)[0],
                'pending_out': self.cpu.mem_read(0x200712, 1)[0],
                'cycle_flags': [self.cpu.mem_read(a, 1)[0]
                                for a in (0x200710, 0x200711)],
                'queue_count': self.cpu.mem_read(STATE + 0xD, 1)[0],
                'queue_busy': self.cpu.mem_read(STATE + 0xE, 1)[0],
                'queue_bytes': bytes(self.cpu.mem_read(STATE + 0x78, 14)).hex(),
                'writes': self.writes.copy(),
                'visited_cycle': [hex(a) for a in sorted(self.visited)
                                  if 0x76F0 <= a < 0x77A6],
                'visited_helpers': [hex(a) for a in sorted(self.visited)
                                    if not 0x76F0 <= a < 0x77A6]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('image', type=Path)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    raw = args.image.read_bytes()
    if len(raw) != 32000 or hashlib.sha256(raw).hexdigest() != SHA:
        raise ValueError('unexpected firmware image')
    runner = CycleQueueRunner(raw)
    cases = [('no_pending', 0, 8, False, False),
             ('busy', 0, 8, True, True),
             ('slot_0', 0, 8, True, False),
             ('slot_1', 1, 8, True, False),
             ('slot_2', 2, 8, True, False),
             ('slot_3', 3, 8, True, False),
             ('slot_4', 4, 8, True, False),
             ('out_of_range_selector', 255, 8, True, False),
             ('zero_count', 0, 0, True, False),
             ('cross_slot_synthetic', 0, 9, True, False),
             ('outgoing_gate_not_ready', 0, 8, False, False, True)]
    cases.extend((f'template_slot_{index}', index, 0, True, False, False, True)
                 for index in range(5))
    rows = [runner.sample(*case) for case in cases]
    starts = {int(a, 0) for row in rows for a in row['visited_cycle']}
    output = {'format': 'quadzilla-cycle-queue-selection-v1',
              'raw_sha256': SHA, 'cpu': 'ARM926 functional surrogate',
              'emulator': 'Unicorn ' + runner.uc.__version__,
              'entry_context': '0x76f0 continuation after upstream cycle calls; R4..R7 and saved frame explicitly supplied',
              'cases': rows, 'visited_cycle_starts': [hex(a) for a in sorted(starts)],
              'limits': ['does not execute or validate the earlier 0x76cc..0x76ef calls',
                         'synthetic count 9 is not established reachable from a producer',
                         'no physical cycle, interrupt or USART effects modeled']}
    args.output.write_text(json.dumps(output, indent=2) + '\n', encoding='utf-8')
    print(f'{len(rows)} cases, {len(starts)} continuation starts visited')
    for row in rows:
        print(row['label'], row['selector_out'], row['pending_out'],
              row['queue_count'], row['queue_bytes'])


if __name__ == '__main__':
    main()
