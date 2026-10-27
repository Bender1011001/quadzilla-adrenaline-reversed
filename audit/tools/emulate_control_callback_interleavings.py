#!/usr/bin/env python3
"""Suspend original control between repeated loads and run original callbacks."""
import argparse
import hashlib
import itertools
import json
from pathlib import Path

from emulate_aid255_control_admission import AdmissionControlRunner
from emulate_control_scalar_integration import ROOT
from emulate_integer_runtime import SHA


class InterleaveRunner(AdmissionControlRunner):
    def __init__(self, raw):
        super().__init__(raw)
        self.callback_phase = False

    def write(self, cpu, access, address, size, value, user):
        super().write(cpu, access, address, size, value, user)
        if self.callback_phase and not 0x202600 <= address < 0x202800:
            self.callback_writes.append({'site': hex(cpu.reg_read(self.arm.UC_ARM_REG_PC)),
                                         'address': hex(address), 'size': size, 'value': hex(value)})

    def trace(self, cpu, address, size, user):
        super().trace(cpu, address, size, user)
        if address == 0x5210 and not self.paused:
            self.paused = True
            cpu.emu_stop()

    def call(self, entry, args):
        self.paused = False
        self.callback_writes = []
        for address in (0xFFFC0000, 0xFFFFF000):
            self.cpu.mem_write(address, bytes(0x1000))
        for address, value in ((0xFFFFF110, 4), (0xFFFFF43C, self.scenario.get('pins', 0)),
                               (0xFFFA0060, self.scenario.get('clock', 0)),
                               (0xFFFC0014, self.scenario.get('uart', 0)), (0xFFFC0124, 0x100),
                               (0x200728, 0xFFFA0080), (0x200AE8, 10001 if self.scenario.get('numeric') else 0),
                               (0x200474, 6000000), (0x200748, 0x40C00000), (0x20074C, 0x40000000)):
            self.cpu.mem_write(address, value.to_bytes(4, 'little'))
        for address, value in ((0x200792, 1), (0x200788, 1), (0x200789, 1)):
            self.cpu.mem_write(address, bytes([value]))
        self.cpu.emu_start(entry | 1, 0x3F00, count=100000)
        if not self.paused or self.cpu.reg_read(self.arm.UC_ARM_REG_PC) != 0x5210:
            raise ValueError('control did not stop before its second percent load')
        context = self.cpu.context_save()
        self.interrupted_sp = self.cpu.reg_read(self.arm.UC_ARM_REG_SP)
        before = self.word(0x2005F0)
        self.callback_phase = True
        self.cpu.reg_write(self.arm.UC_ARM_REG_SP, 0x202800)
        self.invoke(self.scenario['entry'])
        self.callback_phase = False
        after = self.word(0x2005F0)
        if before != after or any(int(w['address'], 0) < 0x2005F4 and
                                  int(w['address'], 0)+w['size'] > 0x2005F0 for w in self.callback_writes):
            raise ValueError('selected callback changed percent word')
        self.percent_snapshot = {'before': before, 'after': after}
        self.cpu.context_restore(context)
        self.cpu.emu_start(0x5211, 0x3F00, count=100000)
        if self.cpu.reg_read(self.arm.UC_ARM_REG_PC) != 0x3F00 or self.cpu.reg_read(self.arm.UC_ARM_REG_SP) != 0x203000:
            raise ValueError('resumed control return/stack mismatch')
        return {'status': 'returned', 'r0': self.regs(1)[0]}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('image', type=Path)
    p.add_argument('--output', type=Path, required=True)
    args = p.parse_args()
    raw = args.image.read_bytes()
    if hashlib.sha256(raw).hexdigest() != SHA:
        raise ValueError('source identity mismatch')
    scenarios = [dict(name='pio_low', entry=0x7448), dict(name='pio_high', entry=0x7448, pins=1 << 30),
                 dict(name='spi_stub', entry=0x6B44), dict(name='tc0', entry=0x6C48),
                 dict(name='tc1_clear', entry=0x6C68), dict(name='tc1_set', entry=0x6C68, clock=0x10000),
                 dict(name='tc2_counters', entry=0x6C94), dict(name='tc2_numeric', entry=0x6C94, numeric=True),
                 dict(name='usart_none', entry=0x7178), dict(name='usart_both', entry=0x7178, uart=0x110),
                 dict(name='spurious_stub', entry=0x7444)]
    r = InterleaveRunner(raw)
    cases = []
    for scenario, percent in itertools.product(scenarios, (0, 50, 100)):
        r.scenario = scenario
        result = r.sample(dict(capture=2000, percent=percent, clock_enabled=False))
        cases.append({'scenario': scenario, 'percent': r.percent_snapshot,
                      'pause_pc': '0x5210', 'interrupted_sp': hex(r.interrupted_sp),
                      'callback_sp': '0x202800', 'callback_writes': r.callback_writes,
                      'scalar_column': result['scalar']['column'],
                      'response_inputs': r.response['inputs'],
                      'response_expected': r.response['expected'], 'response_actual_bytes': r.response['actual_bytes']})
    doc = {'format': 'quadzilla-control-callback-interleavings-v1', 'raw_sha256': SHA,
           'cases': cases, 'checked_model_mismatches': 0,
           'limits': ['host saves/restores full CPU context; original callback bodies execute on separate synthetic stack',
                      'SRAM/MMIO changes persist into original resumed control; no function result stubs',
                      'not ARM IRQ/FIQ wrappers, banked mode entry, interrupt nesting, AIC routing or timing simulation',
                      'selected initialized pointers and explicit flag/status/numeric states only; no exhaustive callback writer exclusion',
                      'no DMA, device traffic, flashing, measured units or physical-output claim']}
    args.output.write_text(json.dumps(doc, indent=2)+'\n')
    print(f'{len(cases)} original callback/control interleavings; percent unchanged; scalar/response checks pass')


if __name__ == '__main__':
    main()
