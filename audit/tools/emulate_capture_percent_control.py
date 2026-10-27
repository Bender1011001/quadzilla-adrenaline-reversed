#!/usr/bin/env python3
"""Follow an original RXB1 percent producer through the original full cycle."""
import argparse
import hashlib
import json
from pathlib import Path

from emulate_aid255_control_admission import AdmissionControlRunner
from emulate_control_scalar_integration import ROOT
from emulate_integer_runtime import SHA


class PercentRunner(AdmissionControlRunner):
    def __init__(self, raw):
        super().__init__(raw)
        self.percent_reads = []
        self.percent_events = []
        self.cpu.hook_add(self.uc.UC_HOOK_MEM_READ, self.watch_read)

    def watch_read(self, cpu, access, address, size, value, user):
        if address == 0x2005F0:
            self.percent_reads.append({'site': hex(cpu.reg_read(self.arm.UC_ARM_REG_PC)),
                                       'value': self.word(address), 'size': size})
            self.percent_events.append({'kind': 'read', **self.percent_reads[-1]})

    def write(self, cpu, access, address, size, value, user):
        super().write(cpu, access, address, size, value, user)
        if address <= 0x2005F0 < address+size:
            self.percent_events.append({'kind': 'write', 'site': hex(cpu.reg_read(self.arm.UC_ARM_REG_PC)),
                                        'value': value, 'size': size})

    def run_case(self, value, dlc=8, status=0x30, match=True, retained=0):
        self.sample(dict(capture=2000, percent=50, clock_enabled=False))
        for address in (0xFFFC0000, 0xFFFE0000, 0xFFFFF000, 0xFFFD8000):
            self.cpu.mem_write(address, bytes(0x1000))
        for address, v in ((0x2005E0, 0xFFFE0000), (0xFFFE0010, status),
                           (0xFFFFF43C, 0x818), (0x200728, 0xFFFC0000),
                           (0x2007E8, 0x2007F0), (0x2005F0, retained)):
            self.cpu.mem_write(address, v.to_bytes(4, 'little'))
        frame = bytearray(14)
        frame[1:5] = bytes.fromhex('67880300') if match else bytes(4)
        frame[5], frame[7], frame[8] = dlc, value, 0xA5
        self.cpu.mem_write(0x200AB4, bytes(frame))
        self.cpu.mem_write(0x2005DE, b'\2')
        self.cpu.mem_write(0x2005D6, b'\2')
        self.cpu.mem_write(0x200AFD, b'\0')
        self.cpu.mem_write(0x200792, b'\0')
        self.global_writes.clear()
        self.percent_reads.clear()
        self.percent_events.clear()
        self.calls.clear()
        self.visited.clear()
        self.invoke(0x76CC)
        expected = min(4*value//10, 100) if match and status & 0x20 else retained
        stores = [w for w in self.global_writes
                  if int(w['address'], 0) <= 0x2005F0 < int(w['address'], 0)+w['size']]
        expected_stores = int(match and bool(status & 0x20))
        if self.word(0x2005F0) != expected or len(stores) != expected_stores:
            raise ValueError(('percent producer mismatch', value, dlc, status, match, stores))
        if stores and (stores[0]['site'] != '0x5b22' or int(stores[0]['value'], 0) != expected):
            raise ValueError('unexpected percent writer')
        if stores and self.percent_events[0]['kind'] != 'write':
            raise ValueError('consumer read preceded this cycle producer')
        if not self.percent_reads or any(r['value'] != expected or r['size'] != 4 for r in self.percent_reads):
            raise ValueError('cycle percent read differs from producer/retained value')
        expected_column = 19 if expected >= 101 else 19*expected//100
        if self.scalar['column'] != expected_column:
            raise ValueError('producer did not reach scalar column calculation')
        return {'input': dict(value=value, dlc=dlc, status=hex(status), match=match, retained=retained),
                'frame': frame.hex(), 'percent_after': expected, 'stores': stores,
                'reads': self.percent_reads.copy(), 'scalar_column': self.scalar['column'],
                'ordered_events': self.percent_events.copy(),
                'response_percent_byte': self.response['actual_bytes']['0x200bc0'],
                'capture_table_calls': self.calls.copy()}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('image', type=Path)
    p.add_argument('--output', type=Path, required=True)
    args = p.parse_args()
    raw = args.image.read_bytes()
    if hashlib.sha256(raw).hexdigest() != SHA:
        raise ValueError('source identity mismatch')
    runner = PercentRunner(raw)
    cases = [runner.run_case(value, dlc) for value in range(256) for dlc in (0, 8)]
    cases += [runner.run_case(255, match=match, status=status, retained=old)
              for match, status in ((False, 0x30), (True, 0x10)) for old in (0, 100, 0xFFFFFFFF)]
    doc = {'format': 'quadzilla-capture-percent-control-v1', 'raw_sha256': SHA,
           'cases': cases, 'producer_cases': 512, 'retention_cases': 6,
           'limits': ['completed RXB1 buffer and phase/kind supplied; no physical CAN or DMA delivery',
                      'preparatory original control call followed by original 0x76CC cycle, no function stubs',
                      'original ADC, capture, receive, scalar, response and scheduling instructions execute',
                      'all watched percent reads stable within these uninterrupted cycles',
                      'local producer bound and retained-value cases do not exclude alternate global writers or IRQ interleavings',
                      'no hardware traffic, timing, flashing, engine-setting or physical-output claim']}
    args.output.write_text(json.dumps(doc, indent=2)+'\n')
    print('512 original producer/control cycles; 6 original retained-value cycles')


if __name__ == '__main__':
    main()
