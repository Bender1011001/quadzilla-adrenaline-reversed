#!/usr/bin/env python3
"""Distinguish initialized TC2 pointer from direct USART callback registers."""
import argparse
import hashlib
import json
from pathlib import Path

from emulate_aid255_control_admission import AdmissionControlRunner
from emulate_integer_runtime import SHA


class PointerRunner(AdmissionControlRunner):
    def __init__(self, raw):
        super().__init__(raw)
        self.phase = None
        self.reads = []
        self.cpu.hook_add(self.uc.UC_HOOK_MEM_READ, self.observe_read)

    def observe_read(self, cpu, access, address, size, value, user):
        if self.phase and address >= 0xFFFA0000:
            self.reads.append({'callback': self.phase, 'site': hex(cpu.reg_read(self.arm.UC_ARM_REG_PC)),
                               'address': hex(address), 'size': size})

    def run_case(self, pointer):
        self.phase = None
        self.sample(dict(capture=2000, percent=50, clock_enabled=False))
        self.cpu.mem_write(0x200728, pointer.to_bytes(4, 'little'))
        self.cpu.mem_write(0xFFFFF110, (4).to_bytes(4, 'little'))
        self.reads.clear()
        self.phase = 'tc2'
        self.invoke(0x6C94)
        self.phase = 'usart'
        self.invoke(0x7178)
        self.phase = None
        tc2 = [r for r in self.reads if r['site'] == '0x6c9a']
        usart = [r for r in self.reads if r['site'] == '0x717c']
        if tc2 != [{'callback': 'tc2', 'site': '0x6c9a', 'address': hex(pointer+0x20), 'size': 4}]:
            raise ValueError('TC2 pointer read mismatch')
        if usart != [{'callback': 'usart', 'site': '0x717c', 'address': '0xfffc0014', 'size': 4}]:
            raise ValueError('USART direct status read mismatch')
        if self.word(0x200728) != pointer:
            raise ValueError('callback unexpectedly mutated TC2 pointer')
        return {'supplied_pointer': hex(pointer), 'pointer_after': hex(self.word(0x200728)),
                'peripheral_reads': self.reads.copy()}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('image', type=Path)
    p.add_argument('--output', type=Path, required=True)
    args = p.parse_args()
    raw = args.image.read_bytes()
    if hashlib.sha256(raw).hexdigest() != SHA:
        raise ValueError('source identity mismatch')
    def word(at):
        return int.from_bytes(raw[at-0x4000:at-0x4000+4], 'little')
    literals = {0x9E10: 0xFFFA0080, 0x6F58: 0x200708, 0x71C0: 0xFFFC0014}
    if any(word(at) != value for at, value in literals.items()):
        raise ValueError('pointer source/literal contract changed')
    runner = PointerRunner(raw)
    doc = {'format': 'quadzilla-peripheral-pointer-ownership-v1', 'raw_sha256': SHA,
           'image_words': {hex(at): hex(v) for at, v in literals.items()},
           'initialized_sram_slot': '0x200728',
           'cases': [runner.run_case(0xFFFA0080), runner.run_case(0xFFFC0000)],
           'limits': ['original complete TC2 and USART callback bodies execute with controlled flags/status',
                      'second case deliberately reproduces the historical artificial fixture override',
                      'callback body calls are not ARM IRQ entry, banked state or interrupt interleaving simulation',
                      'initial pointer ownership does not exclude later alias/pointer writers',
                      'no device traffic, hardware timing, DMA, flashing or physical-output claim']}
    args.output.write_text(json.dumps(doc, indent=2)+'\n')
    print('Initialized TC2 pointer and artificial override distinguished; USART direct read unchanged')


if __name__ == '__main__':
    main()
