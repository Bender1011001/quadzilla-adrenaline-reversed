#!/usr/bin/env python3
"""Execute one original-byte main-loop dispatch iteration with synthetic state."""
import argparse
import hashlib
import json
from pathlib import Path

from audit_aid_tables import AidRunner, SHA


BASE = 0x200788


class MainLoopRunner(AidRunner):
    def __init__(self, raw):
        super().__init__(raw)
        self.allowed_ranges = ((0x74C4, 0x74DE), (0x74E8, 0x74EA), (0x76CC, 0x76CE),
                               (0x77B8, 0x7A3E))
        self.cpu.mem_map(0xFFFFF000, 0x1000)
        self.entry_hits = 0
        self.stop_reason = None
        self.writes = []
        self.cpu.hook_add(self.uc.UC_HOOK_CODE, self.boundary)
        self.cpu.hook_add(self.uc.UC_HOOK_MEM_WRITE, self.write)

    def boundary(self, cpu, address, size, user):
        if address == 0x78E4:
            self.entry_hits += 1
            if self.entry_hits > 1:
                self.stop_reason = 'next_dispatch_iteration'
                cpu.emu_stop()
        elif address == 0x76CC:
            self.stop_reason = 'would_call_control_cycle'
            cpu.emu_stop()
        elif address == 0x74E8:
            self.stop_reason = 'would_reinitialize_pio'
            cpu.emu_stop()

    def write(self, cpu, access, address, size, value, user):
        if 0x200788 <= address < 0x2007C8 or 0xFFFFF000 <= address < 0x100000000:
            self.writes.append({'pc': hex(cpu.reg_read(self.arm.UC_ARM_REG_PC)),
                                'address': hex(address), 'size': size,
                                'value': hex(value & ((1 << (size * 8)) - 1))})

    def sample(self, label, state, pio_pdsr=0, flags=()):
        self.reset()
        self.cpu.mem_write(0xFFFFF000, bytes(0x1000))
        self.cpu.mem_write(0xFFFFF43C, pio_pdsr.to_bytes(4, 'little'))
        self.cpu.mem_write(BASE + 8, bytes([state]))
        for address, value in flags:
            self.cpu.mem_write(address, bytes([value]))
        self.cpu.reg_write(self.arm.UC_ARM_REG_R4, 0)
        self.cpu.reg_write(self.arm.UC_ARM_REG_R5, BASE)
        self.cpu.reg_write(self.arm.UC_ARM_REG_R6, 1)
        self.cpu.reg_write(self.arm.UC_ARM_REG_R7, 0xFFFFF434)
        self.entry_hits = 0
        self.stop_reason = None
        self.writes.clear()
        self.visited.clear()
        try:
            self.cpu.emu_start(0x78E5, 0x3F00, count=2048)
        except self.uc.UcError as exc:
            raise RuntimeError((label, self.fault, str(exc))) from exc
        if self.stop_reason is None:
            raise RuntimeError((label, 'instruction budget or unexpected return',
                                hex(self.cpu.reg_read(self.arm.UC_ARM_REG_PC))))
        return {'label': label, 'state_in': state, 'pio_pdsr': hex(pio_pdsr),
                'flags_in': [[hex(a), v] for a, v in flags],
                'stop_reason': self.stop_reason,
                'state_out': self.cpu.mem_read(BASE + 8, 1)[0],
                'queue_gate': self.cpu.mem_read(BASE + 0xA, 1)[0],
                'writes': self.writes.copy(),
                'visited': [hex(a) for a in sorted(self.visited)
                            if 0x77B8 <= a < 0x7A3E]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('image', type=Path)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    raw = args.image.read_bytes()
    if len(raw) != 32000 or hashlib.sha256(raw).hexdigest() != SHA:
        raise ValueError('unexpected firmware image')
    runner = MainLoopRunner(raw)
    cases = [('default_reinit', 0, 0, ()),
             ('state1_cycle', 1, 0, ()),
             ('state1_pin_gate', 1, 1 << 28, ()),
             ('state1_to_state2', 1, 1 << 28,
              ((0x2006DF, 1), (0x2006DE, 1))),
             ('state2_cycle', 2, 0, ()),
             ('state2_hold', 2, 0, ((0x200715, 1),)),
             ('state3_cycle', 3, 0, ()),
             ('state3_pin_gate', 3, 1 << 28, ())]
    rows = [runner.sample(*case) for case in cases]
    if any(0x20078A <= int(write['address'], 0) < 0x20078F
           for row in rows for write in row['writes']):
        raise ValueError('bounded case unexpectedly wrote a telemetry count byte')
    seen = {int(a, 0) for row in rows for a in row['visited']}
    output = {'format': 'quadzilla-main-loop-dispatch-v1', 'raw_sha256': SHA,
              'cpu': 'ARM926 functional surrogate',
              'emulator': 'Unicorn ' + runner.uc.__version__,
              'entry_context': '0x78e4 with main-loop R4..R7 state supplied; stop at next iteration or before 0x76cc or 0x74e8',
              'cases': rows, 'visited_starts': [hex(a) for a in sorted(seen)],
              'limits': ['does not execute reset initialization at 0x77b8, control-cycle callee, or PIO reinitializer',
                         'synthetic PIO register memory lacks command/interrupt behavior',
                         'subordinate routines and computed-pointer aliases are outside this bounded run',
                         'bounded iterations do not prove timing or liveness']}
    args.output.write_text(json.dumps(output, indent=2) + '\n', encoding='utf-8')
    print([(row['label'], row['stop_reason'], row['state_out'], len(row['visited']))
           for row in rows])


if __name__ == '__main__':
    main()
