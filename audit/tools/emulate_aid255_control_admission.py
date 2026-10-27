#!/usr/bin/env python3
"""Follow a completed AID255 frame through original admission and control code."""
import argparse
import hashlib
import json
import struct
from pathlib import Path

from emulate_control_scalar_integration import IntegrationRunner
from emulate_control_responses import WORDS, BYTES, response_values
from emulate_integer_runtime import SHA
from x2com_crc import add_crc


class AdmissionControlRunner(IntegrationRunner):
    def __init__(self, raw):
        super().__init__(raw)
        self.cpu.mem_map(0xFFFC0000, 0x1000)
        for address in (0xFFFFF000, 0xFFFE0000, 0xFFFD8000):
            self.cpu.mem_map(address, 0x1000)
        self.receive_returns = []
        self.receive_calls = []
        self.response = None
        self.admission_snapshot = None

    def trace(self, cpu, address, size, user):
        super().trace(cpu, address, size, user)
        if address in (0x8038, 0x7BCC, 0x7E64, 0x7CC4):
            self.receive_calls.append(hex(address))
        if address == 0x6028:
            self.receive_returns.append(self.regs(1)[0])
            self.admission_snapshot = dict(bytes=bytes(cpu.mem_read(0x200BBA, 13)),
                                           stores=[w for w in self.global_writes if 0x200BBA <= int(w['address'], 0) < 0x200BC7])
        if address == 0x53A2:
            c = {name: self.word(a) for name, a in WORDS.items()} | {name: self.byte(a) for name, a in BYTES.items()}
            sp = cpu.reg_read(self.arm.UC_ARM_REG_SP)
            c.update(stretch=cpu.reg_read(self.arm.UC_ARM_REG_R6), clamp_flag=self.byte(sp+2), write_flag=self.byte(sp+3),
                     filter0=list(struct.unpack('<32I', cpu.mem_read(0x200480, 128))),
                     filter1=list(struct.unpack('<32I', cpu.mem_read(0x200500, 128))))
            self.response = dict(inputs=c, expected=response_values(c))
        if address == 0x55A6:
            expected = self.response['expected']
            actual = {a: self.byte(int(a, 0)) for a in expected['bytes']}
            filters = [list(struct.unpack('<32I', cpu.mem_read(a, 128))) for a in (0x200480, 0x200500)]
            if (actual != expected['bytes'] or self.word(0x200474) != expected['derived']
                    or filters != [expected['filter0'], expected['filter1']]):
                raise ValueError('integrated response arithmetic mismatch')
            self.response['actual_bytes'] = actual

    def invoke(self, entry):
        sp = self.cpu.reg_read(self.arm.UC_ARM_REG_SP)
        saved = [(getattr(self.arm, f'UC_ARM_REG_R{i}'), self.cpu.reg_read(getattr(self.arm, f'UC_ARM_REG_R{i}')))
                 for i in range(4, 12)]
        self.cpu.reg_write(self.arm.UC_ARM_REG_LR, 0x3F00)
        self.cpu.emu_start(entry | 1, 0x3F00, count=100000)
        if self.cpu.reg_read(self.arm.UC_ARM_REG_PC) != 0x3F00 or self.cpu.reg_read(self.arm.UC_ARM_REG_SP) != sp:
            raise ValueError(('composed call return/stack failure', hex(entry)))
        if any(self.cpu.reg_read(reg) != value for reg, value in saved):
            raise ValueError('composed callee-save mismatch')

    def case(self, corrupt, declared_count=13):
        self.sample(dict(capture=2000, percent=50, clock_enabled=False))
        for address in (0xFFFC0000, 0xFFFE0000, 0xFFFFF000, 0xFFFD8000):
            self.cpu.mem_write(address, bytes(0x1000))
        # Scalar settings use reviewed handler ranges. Other globals are
        # controlled inputs without an entire live-history claim.
        for address, value in ((0x2005E4, 4095), (0x200AC8, 100), (0x200ACC, 100),
                               (0x2007E8, 0x2007F0), (0x200728, 0xFFFC0000),
                               (0x2005E0, 0xFFFE0000), (0xFFFE0010, 0x30), (0xFFFFF43C, 0x800),
                               *((0x200458+4*i, 1280) for i in range(5))):
            self.cpu.mem_write(address, struct.pack('<I', value))
        for address, value in ((0x200588, 20), (0x2005B0, 0), (0x2005B1, 100),
                               (0x2005D4, 1), (0x2005D7, 80), (0x200BC2, 7), (0x200BC3, 3),
                               (0x200425, 0), (0x200426, 0)):
            self.cpu.mem_write(address, bytes([value]))
        data = bytearray([declared_count]+[0xA0+i for i in range(12)])
        data[8], data[9] = 200, 240
        payload = bytes([255])+bytes(data)
        frame = add_crc(bytes([0x1F])+payload)
        if corrupt:
            frame = frame[:-1]+bytes([frame[-1]^1])
        self.cpu.mem_write(0x2007F0, frame)
        self.cpu.mem_write(0x200AFD, b'\1')
        self.cpu.mem_write(0xFFFC0104, bytes(4))
        self.global_writes.clear(); self.receive_returns.clear(); self.receive_calls.clear()
        self.cpu.mem_write(0x200792, b'\1')
        self.invoke(0x76CC)
        after_admission = self.admission_snapshot['bytes']
        stores = self.admission_snapshot['stores']
        if self.receive_returns != ([4] if corrupt else [1 if declared_count == 13 else 2]):
            raise ValueError('receive CRC/admission status differs')
        if corrupt:
            if stores or (after_admission[8], after_admission[9]) != (7, 3):
                raise ValueError('bad CRC frame changed aliased bytes')
        elif after_admission != bytes(data) or len(stores) != 13:
            raise ValueError('maximum AID255 value did not reach expected response extent')
        admission_calls = self.receive_calls.copy(); admission_status = self.receive_returns[:]
        expected_inputs = (7, 3) if corrupt else (200, 240)
        if (self.scalar['inputs']['response'], self.response['inputs']['previous_response']) != expected_inputs:
            raise ValueError('aliased coefficients did not reach the original control consumers')
        if (self.byte(0x200BC2), self.byte(0x200BC3)) != (100, 80):
            raise ValueError('automatic producers did not overwrite the consumed bytes later')
        return dict(corrupt_crc=corrupt, declared_count=declared_count, payload=payload.hex(), frame=frame.hex(),
                    receive_status=admission_status[0], original_receive_calls=admission_calls,
                    after_admission=after_admission.hex(), staging_stores=stores,
                    scalar=self.scalar, response=self.response,
                    after_control=dict(bc2=self.byte(0x200BC2), bc3=self.byte(0x200BC3)))


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('image', type=Path); p.add_argument('--output', type=Path, required=True)
    args = p.parse_args(); raw = args.image.read_bytes()
    if hashlib.sha256(raw).hexdigest() != SHA:
        raise ValueError('source identity mismatch')
    r = AdmissionControlRunner(raw)
    cases = [r.case(True), r.case(False), r.case(False, declared_count=14)]
    doc = dict(format='quadzilla-aid255-control-admission-v1', raw_sha256=SHA, function_stubs=[], cases=cases,
               limits=['completed receive buffer, pending flag and zero UART receive count are explicitly supplied',
                    'original complete 0x76CC cycle executes receive/CRC/walker/validation, control and outgoing scheduler',
                       'scalar settings use reviewed handler ranges; remaining fixture globals are controlled, not a live configuration history',
                       'USART/PDC/timer registers are plain memory without DMA, interrupts or physical transport',
                       'no authentication bypass, pairing, real delivery, waveform or physical engine effect is established',
                       'a fixed aliased response interval is modified, not an arbitrary-address write primitive'])
    args.output.write_text(json.dumps(doc, indent=2)+'\n')
    print([(c['receive_status'], c['scalar']['inputs']['response'], c['scalar']['telemetry_store']) for c in cases])


if __name__ == '__main__':
    main()
