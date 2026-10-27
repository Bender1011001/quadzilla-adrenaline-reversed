#!/usr/bin/env python3
"""Execute counter-triggered original peripheral setup inside full control."""
import argparse
from collections import Counter
import hashlib
import itertools
import json
from pathlib import Path

from emulate_control_retention_branches import RetentionRunner, ROOT
from emulate_integer_runtime import SHA


class BudgetStop(RuntimeError):
    pass


class ReinitRunner(RetentionRunner):
    def __init__(self, raw):
        super().__init__(raw)
        self.allow_reinitialization = True
        for address in (0xFFFF0000, 0xFFFC0000, 0xFFFE0000, 0xFFFD8000):
            self.cpu.mem_map(address, 0x10000 if address == 0xFFFF0000 else 0x1000)
        self.cpu.hook_add(self.uc.UC_HOOK_MEM_READ, self.peripheral_read)
        self.cpu.hook_add(self.uc.UC_HOOK_MEM_WRITE, self.setup_write)

    def peripheral_read(self, cpu, access, address, size, value, user):
        if address == 0xFFFC0000:
            cpu.mem_write(address, self.spec['uscr_read'].to_bytes(4, 'little'))

    def setup_write(self, cpu, access, address, size, value, user):
        if self.in_setup and not 0x202000 <= address < 0x204000:
            self.setup_writes.append({'site': hex(cpu.reg_read(self.arm.UC_ARM_REG_PC)),
                                      'address': hex(address), 'size': size, 'value': hex(value)})

    def write(self, cpu, access, address, size, value, user):
        super().write(cpu, access, address, size, value, user)
        # The inherited admission check concerns 0x6FA0's RC store. Setup has
        # its own RC initializer; preserve that store in setup_writes instead.
        if self.in_setup and address == 0xFFFA001C and cpu.reg_read(self.arm.UC_ARM_REG_PC) != 0x6FA6:
            self.timer_writes.pop()

    def call(self, entry, args):
        self.events = []
        self.clamp_input = None
        self.in_setup = False
        self.setup_writes = []
        self.setup_calls = []
        self.milestones = []
        self.site_counts = Counter()
        for address in (0xFFFF0000, 0xFFFC0000, 0xFFFE0000, 0xFFFD8000):
            self.cpu.mem_write(address, bytes(0x10000 if address == 0xFFFF0000 else 0x1000))
        for address, value in ((0xFFFFF43C, 0x800 | (self.spec['pin17'] << 17)),
                               (0xFFFE0010, 0x30 if self.spec['spi_ready'] else 0)):
            self.cpu.mem_write(address, value.to_bytes(4, 'little'))
        for address, size, value in self.overrides:
            self.cpu.mem_write(address, value.to_bytes(size, 'little'))
        self.cpu.emu_start(entry | 1, 0x3F00, count=100000)
        pc = self.cpu.reg_read(self.arm.UC_ARM_REG_PC)
        if pc != 0x3F00:
            raise BudgetStop(hex(pc))
        if self.cpu.reg_read(self.arm.UC_ARM_REG_SP) != 0x203000:
            raise ValueError('unbalanced control/setup stack')
        return {'status': 'returned', 'r0': self.regs(1)[0]}

    def trace(self, cpu, address, size, user):
        self.site_counts[address] += 1
        if address == 0x74E8:
            self.in_setup = True
            self.before_tables = hashlib.sha256(cpu.mem_read(0x200000, 0x424)).hexdigest()
        if self.in_setup and address in (0x74E8, 0x6FB4, 0x6BD8, 0x575C, 0x4330, 0x725C, 0x800C):
            self.setup_calls.append(hex(address))
        if address == 0x55E8:
            self.in_setup = False
            after = hashlib.sha256(cpu.mem_read(0x200000, 0x424)).hexdigest()
            if after != self.before_tables:
                raise ValueError('setup changed lookup-region bytes')
            self.milestones.append({'site': hex(address), 'lookup_sha256': after,
                                    'pin_sample': self.byte(0x200791)})
        super().trace(cpu, address, size, user)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('image', type=Path)
    p.add_argument('--output', type=Path, required=True)
    args = p.parse_args()
    raw = args.image.read_bytes()
    if hashlib.sha256(raw).hexdigest() != SHA:
        raise ValueError('source identity mismatch')
    runner = ReinitRunner(raw)
    cases = []
    union = set()
    specs = [dict(old_count=old, pin17=pin, uscr_read=u, recovery_byte=b, spi_ready=True)
             for old, pin, u, b in itertools.product((1999, 2000, 2001, 0xFFFFFFFF), (0, 1),
                                                     (0, 0xFFFFFFFF), (0, 255))]
    specs += [dict(old_count=2000, pin17=0, uscr_read=0, recovery_byte=0, spi_ready=False)]
    for spec in specs:
        runner.spec = spec
        runner.overrides = [(0x200448, 4, spec['old_count']), (0x20043C, 4, 2000),
                            (0x200440, 4, 0), (0x200424, 1, spec['recovery_byte'])]
        outcome = 'returned'
        try:
            runner.sample(dict(capture=2000, percent=50, clock_enabled=False))
        except BudgetStop as exc:
            outcome = 'instruction_budget'
            if spec['spi_ready'] or not 0x6B48 <= int(str(exc), 0) < 0x6B98:
                raise
        triggered = spec['old_count'] in (2000, 2001)
        if spec['spi_ready']:
            expected_calls = ['0x74e8', '0x6fb4', '0x6bd8', '0x575c', '0x4330', '0x725c', '0x800c'] if triggered else []
            if runner.setup_calls != expected_calls:
                raise ValueError('setup call sequence mismatch')
            expected_count = 0 if triggered or spec['old_count'] == 0xFFFFFFFF else 2000
            expected_byte = (spec['recovery_byte']+int(triggered)) & 255
            if runner.word(0x200448) != expected_count or runner.byte(0x200424) != expected_byte:
                raise ValueError('setup caller epilogue mismatch')
            if triggered and runner.byte(0x200791) != 1-spec['pin17']:
                raise ValueError('setup pin sample mismatch')
            if runner.word(0x20043C) != runner.word(0x2005EC) or runner.word(0x200440) != runner.word(0x200600):
                raise ValueError('setup caller retained-source refresh mismatch')
        elif (runner.setup_calls != ['0x74e8', '0x6fb4', '0x6bd8', '0x575c']
              or runner.milestones or runner.site_counts[0x6B48] < 100):
            raise ValueError('blocked case did not repeat original readiness path')
        union.update(runner.visited)
        cases.append({'inputs': spec, 'outcome': outcome,
                      'stop_pc': hex(runner.cpu.reg_read(runner.arm.UC_ARM_REG_PC)),
                      'setup_calls': runner.setup_calls, 'setup_writes': runner.setup_writes,
                      'milestones': runner.milestones, 'counter_after': runner.word(0x200448),
                      'repeated_sites': {hex(a): n for a, n in sorted(runner.site_counts.items()) if n > 100},
                      'recovery_byte_after': runner.byte(0x200424)})
    previous = json.loads((ROOT / 'audit/data/idle_control_integration.json').read_text())
    remaining = {int(a, 0) for a in previous['remaining_main_starts']}
    doc = {'format': 'quadzilla-control-reinitialization-v1', 'raw_sha256': SHA,
           'cases': cases, 'returned_cases': 32, 'blocked_cases': 1,
           'new_main_starts': [hex(a) for a in sorted(union & remaining)],
           'combined_main_starts': previous['combined_main_starts']+len(union & remaining),
           'remaining_main_starts': [hex(a) for a in sorted(remaining-union)],
           'limits': ['plain-memory peripheral registers, explicit SPI readiness and USART command read values',
                      'no helper result stubs; original setup and all six subordinate calls execute when ready',
                      'controlled counter/sample history; no normal-service or time-duration proof',
                      'blocked case has no interrupt-driven timeout progression',
                      'no hardware I/O, flashing, physical pulses, DMA or interrupt delivery']}
    args.output.write_text(json.dumps(doc, indent=2)+'\n')
    print(f'32 returns and 1 blocked setup; new starts {doc["new_main_starts"]}; union {doc["combined_main_starts"]}/574')


if __name__ == '__main__':
    main()
