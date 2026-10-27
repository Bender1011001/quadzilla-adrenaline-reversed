#!/usr/bin/env python3
"""Compose original parameter handlers, control calls and AID response reads."""
import argparse
import hashlib
import json
import struct
import sys
from pathlib import Path

from emulate_control_scalar_integration import IntegrationRunner
from emulate_integer_runtime import SHA

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tools'))
from model_remaining_updates import SPECS

KNOT_AIDS = (137, 138, 139, 140, 141)
RAW = (0x2005B4, 0x2005B8, 0x2005BC, 0x2005C0, 0x200584)
ECHO = (0x200BF5, 0x200BF7, 0x200BF9, 0x200BFB, 0x200BEB)
CEILINGS = (384, 512, 640, 768, 896)


class KnotRunner(IntegrationRunner):
    def __init__(self, raw):
        self.phase = 'fixture'
        self.knot_writes = []
        super().__init__(raw)
        self.receive_boundary = []

    def write(self, cpu, access, address, size, value, user):
        super().write(cpu, access, address, size, value, user)
        addresses = set(RAW) | set(range(0x200458, 0x20046C, 4)) | {a+i for a in ECHO for i in (0, 1)} | {0x200425, 0x200426}
        if address in addresses:
            self.knot_writes.append({'phase': self.phase, 'site': hex(cpu.reg_read(self.arm.UC_ARM_REG_PC)),
                                     'address': hex(address), 'size': size, 'value': hex(value)})

    def trace(self, cpu, address, size, user):
        if address == 0x8038:
            dest, count = self.regs(2)
            cpu.mem_write(dest, bytes(self.aids))
            cpu.mem_write(count, bytes([len(self.aids)]))
            self.receive_boundary.append({'aids': self.aids[:], 'return_status': 1,
                                          'list_pointer': hex(dest), 'count_pointer': hex(count)})
            cpu.reg_write(self.arm.UC_ARM_REG_R0, 1)
            cpu.reg_write(self.arm.UC_ARM_REG_PC, cpu.reg_read(self.arm.UC_ARM_REG_LR))
            return
        super().trace(cpu, address, size, user)

    def invoke(self, entry, args):
        preserved = [(getattr(self.arm, f'UC_ARM_REG_R{i}'), self.cpu.reg_read(getattr(self.arm, f'UC_ARM_REG_R{i}')))
                     for i in range(4, 12)]
        self.cpu.reg_write(self.arm.UC_ARM_REG_LR, 0x3F00)
        result = self.call(entry, args)
        if result['status'] != 'returned':
            raise ValueError(('composed call failed', hex(entry), result))
        if any(self.cpu.reg_read(reg) != value for reg, value in preserved):
            raise ValueError(('composed callee-save mismatch', hex(entry)))
        return result['r0']

    def ingest(self, values):
        self.aids = list(values)
        if len(self.aids) > 14:
            raise ValueError('scripted receive list exceeds reviewed bound')
        for aid, value in values.items():
            stage, width = SPECS[aid][:2]
            self.cpu.mem_write(stage, value.to_bytes(width, 'little'))
        self.invoke(0x601C, [])

    def state(self):
        return {'raw_working': [self.word(a) for a in RAW],
                'scaled_knots': [self.word(0x200458+4*i) for i in range(5)],
                'echo_words': [int.from_bytes(self.cpu.mem_read(a, 2), 'little') for a in ECHO],
                'refresh': self.byte(0x200426), 'mode': self.byte(0x200425),
                'scalar_coefficient': self.byte(0x200588)}

    def sequence(self, values):
        self.receive_boundary.clear()
        self.knot_writes.clear(); self.phase = 'fixture'
        # Execute and record the same controlled fixture call as the earlier
        # integration review. Subsequent phases preserve SRAM.
        fixture = self.sample(dict(capture=2000, percent=50, clock_enabled=False))
        self.phase = 'knot_and_zero_updates'
        self.ingest(dict(zip(KNOT_AIDS, values)) | {17: 0, 59: 0, 61: 0, 62: 0})
        after_update = self.state()
        raw = [min(v, 300) for v in values]
        scaled = [128*v//10 for v in raw]
        if (after_update['raw_working'], after_update['echo_words'], after_update['scaled_knots'], after_update['refresh']) != (raw, raw, scaled, 1):
            raise ValueError(('handler knot transform mismatch', values, after_update))
        self.phase = 'nonzero_mode_control'
        self.invoke(0x50F0, [])
        after_mode1 = self.state()
        capped = [min(v, limit) for v, limit in zip(scaled, CEILINGS)]
        if after_mode1 != dict(raw_working=raw, echo_words=raw, scaled_knots=capped, refresh=0, mode=1, scalar_coefficient=0):
            raise ValueError(('mode1 mutation mismatch', values, after_mode1))
        mode1_scalar = self.scalar
        # This original handler sets its response byte and refresh flag,
        # naturally selecting zero mode on the next control call.
        self.phase = 'coefficient_update'
        self.ingest({17: 1})
        self.phase = 'zero_mode_control'
        self.invoke(0x50F0, [])
        after_mode0 = self.state()
        if after_mode0 != dict(raw_working=raw, echo_words=raw, scaled_knots=capped, refresh=0, mode=0, scalar_coefficient=1):
            raise ValueError(('mode0 retained mutation mismatch', values, after_mode0))
        mode0_scalar = self.scalar
        readers = self.read_knots(raw)
        self.phase = 'same_value_reapply'
        self.ingest(dict(zip(KNOT_AIDS, values)))
        after_reapply = self.state()
        if after_reapply != dict(raw_working=raw, echo_words=raw, scaled_knots=scaled, refresh=0, mode=0, scalar_coefficient=1):
            raise ValueError(('same-value reapply mismatch', values, after_reapply))
        self.phase = 'restored_zero_mode_control'
        self.invoke(0x50F0, [])
        after_restored_control = self.state()
        if after_restored_control != after_reapply:
            raise ValueError(('zero mode changed reapplied knots', values, after_restored_control))
        restored_scalar = self.scalar
        if any(not 1024 <= s['telemetry_store'] <= 3840 for s in (mode1_scalar, mode0_scalar, restored_scalar)):
            raise ValueError('telemetry escaped the reviewed-writer cap bound')
        restored_readers = self.read_knots(raw)
        return {'staged_knots': list(values), 'fixture_selector': fixture['return'],
                'scripted_receive': self.receive_boundary.copy(), 'after_update': after_update,
                'after_mode1_control': after_mode1, 'after_mode0_control': after_mode0,
                'mode1_scalar': mode1_scalar, 'mode0_scalar': mode0_scalar, 'readers': readers,
                'after_same_value_reapply': after_reapply, 'after_restored_control': after_restored_control,
                'restored_scalar': restored_scalar, 'restored_readers': restored_readers,
                'knot_writes': self.knot_writes.copy()}

    def read_knots(self, raw):
        readers = []
        for aid, value in zip(KNOT_AIDS, raw):
            self.cpu.mem_write(0x201000, bytes(8))
            self.cpu.mem_write(0x201040, bytes([aid]))
            self.cpu.mem_write(0x201060, b'\1')
            length = self.invoke(0x7D80, [0x201000, 5, 0x201040, 0x201060])
            actual = bytes(self.cpu.mem_read(0x201000, 3))
            if length != 3 or actual != bytes([aid])+value.to_bytes(2, 'little'):
                raise ValueError(('response reader mismatch', aid, actual.hex(), length))
            readers.append({'aid': aid, 'length': length, 'payload': actual.hex()})
        return readers


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('image', type=Path)
    p.add_argument('--output', type=Path, required=True)
    args = p.parse_args()
    raw = args.image.read_bytes()
    if hashlib.sha256(raw).hexdigest() != SHA:
        raise ValueError('source identity mismatch')
    runner = KnotRunner(raw)
    values = [(v,)*5 for v in list(range(301))+[301, 65535]]
    values += [(300, 0, 300, 0, 300), (0, 300, 0, 300, 0), (30, 40, 50, 60, 70)]
    examples = []; summaries = []; digest = hashlib.sha256()
    retain = {0, 1, 29, 30, 31, 39, 40, 41, 49, 50, 51, 59, 60, 61, 69, 70, 71, 100, 299, 300, 301, 65535}
    for n, vector in enumerate(values):
        result = runner.sequence(vector)
        digest.update(json.dumps(result, sort_keys=True, separators=(',', ':')).encode())
        summaries.append({'case': n, 'raw': result['after_update']['raw_working'],
                          'scaled_before': result['after_update']['scaled_knots'],
                          'scaled_after': result['after_mode0_control']['scaled_knots'],
                          'scaled_restored': result['after_restored_control']['scaled_knots'],
                          'telemetry_before_reapply': result['mode0_scalar']['telemetry_store'],
                          'telemetry_after_reapply': result['restored_scalar']['telemetry_store']})
        if vector[0] in retain or n >= 303:
            examples.append(result)
    doc = {'format': 'quadzilla-knot-update-consumer-v1', 'raw_sha256': SHA,
           'cpu': 'ARM926 functional surrogate', 'sequences': len(values),
           'complete_control_calls': 4*len(values), 'ingest_calls': 3*len(values), 'reader_calls': 10*len(values),
           'mismatches': 0, 'sequence_digest_sha256': digest.hexdigest(), 'summary': summaries, 'examples': examples,
           'limits': ['0x8038 is replaced by an explicit scripted receive-result boundary; transport does not execute',
                      'staging is preloaded; original dispatcher, selected handlers, controls and readers execute',
                      'fixture control call applies synthetic SRAM/MMIO overrides documented by control_scalar_integration',
                      'SRAM persists across all post-fixture phases; external return link is restored for each call',
                      'no interrupt interleaving, alternate-writer exclusion, live admission or physical-unit claim',
                      'raw working/echo settings and scaled consumer state are distinct representations; no live defect severity assigned']}
    args.output.write_text(json.dumps(doc, indent=2)+'\n')
    print(f'{len(values)} sequences; {4*len(values)} complete control calls; zero differences')


if __name__ == '__main__':
    main()
