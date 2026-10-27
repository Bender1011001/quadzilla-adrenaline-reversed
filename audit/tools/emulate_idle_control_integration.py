#!/usr/bin/env python3
"""Compose original selector, idle gate, fresh accumulator and caller saturation."""
import argparse
import hashlib
import itertools
import json
from pathlib import Path

from emulate_control_retention_branches import RetentionRunner, ROOT
from emulate_input_gate import model as gate_model, STATE, ACTIVE, FLAGS, TIMER
from emulate_integer_runtime import SHA
from model_control_helpers import ramp_state


class IdleRunner(RetentionRunner):
    def call(self, entry, args):
        self.gate = None
        self.accumulator = None
        self.sum_expected = None
        return super().call(entry, args)

    def trace(self, cpu, address, size, user):
        super().trace(cpu, address, size, user)
        if address == 0x4818:
            values = [self.byte(STATE), self.byte(0x2006E2), self.regs(1)[0],
                      self.word(0x2005EC), self.word(0x2005F0), self.byte(0x2005D7),
                      self.byte(0x20071B), int.from_bytes(cpu.mem_read(0x2006E4, 2), 'little')]
            expected = gate_model(*values)
            if expected[0x20071E] == 0x7C:
                expected[0x20071E] = self.byte(0x20071E)
            self.gate = {'inputs': values, 'expected': {hex(a): v for a, v in expected.items()}}
        elif address == 0x5240:
            actual = {a: self.word(int(a, 0)) if int(a, 0) == TIMER else self.byte(int(a, 0))
                      for a in self.gate['expected']}
            if actual != self.gate['expected'] or self.regs(1)[0] != actual[hex(ACTIVE)]:
                raise ValueError(('integrated idle gate mismatch', actual, self.gate))
            self.gate['actual'] = actual
        elif address == 0x48E8:
            inputs = [self.word(0x200478), self.word(0x20047C), self.word(0x2005EC),
                      self.byte(0x20071E), self.byte(ACTIVE), self.regs(2)[1],
                      self.byte(0x20071C), self.byte(0x20071D)]
            self.accumulator = {'inputs': inputs, 'expected': ramp_state(*inputs)}
        elif address == 0x5306:
            observed = (self.regs(1)[0], self.word(0x200478), self.word(0x20047C),
                        list(cpu.mem_read(0x20071C, 3)))
            if observed != self.accumulator['expected']:
                raise ValueError('integrated fresh accumulator mismatch')
            self.accumulator['actual'] = observed
        elif address == 0x5308:
            r0, r1 = self.regs(2)
            self.sum_expected = (r0+r1) & 0xFFFFFFFF
            self.accumulator['caller_base'] = r1
        elif address == 0x530A and self.sum_expected is not None:
            if self.regs(1)[0] != self.sum_expected:
                raise ValueError('idle caller addition mismatch')
        elif address == 0x5316 and self.sum_expected is not None:
            expected = min(self.sum_expected, 4095)
            if self.word(0x200600) != expected:
                raise ValueError('idle caller saturation mismatch')
            self.accumulator['caller_sum'] = self.sum_expected
            self.accumulator['caller_store'] = expected


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('image', type=Path)
    p.add_argument('--output', type=Path, required=True)
    args = p.parse_args()
    raw = args.image.read_bytes()
    if hashlib.sha256(raw).hexdigest() != SHA:
        raise ValueError('source identity mismatch')
    runner = IdleRunner(raw)
    cases = []
    union = set()
    for state, selector, capture, event, fresh, old in itertools.product(
            (0, 1, 3), (0, 5), (999, 1200), (0, 1), (0, 1), (0, 649, 0xFFFFFFFF)):
        runner.overrides = [(0x2006E2, 1, 1), (STATE, 1, state), (ACTIVE, 1, 0xA5),
                            (0x2005D7, 1, 0), (0x2006E4, 2, 2),
                            (FLAGS[0], 1, 0x5A), (FLAGS[1], 1, 0x6B),
                            (FLAGS[2], 1, event), (FLAGS[3], 1, fresh),
                            (TIMER, 4, 0x12345678), (0x200478, 4, old),
                            (0x20047C, 4, 0), (0x20071C, 1, 0x55), (0x20071D, 1, 0x66)]
        runner.sample(dict(capture=capture, percent=0, clock_enabled=False, selector=selector))
        union.update(runner.visited)
        cases.append({'entry': dict(state=state, selector=selector, capture=capture,
                                   event=event, fresh=fresh, old=old),
                      'gate': runner.gate, 'accumulator': runner.accumulator,
                      'active_after': runner.byte(ACTIVE), 'state_after': runner.byte(STATE)})
    base = json.loads((ROOT / 'audit/data/control_scalar_integration.json').read_text())
    sequences = []
    for old in (0, 649, 0xFFFFFFFF):
        runner.overrides = [(0x2006E2, 1, 1), (STATE, 1, 1), (ACTIVE, 1, 0xA5),
                            (0x2005D7, 1, 0), (0x2006E4, 2, 2),
                            (FLAGS[0], 1, 0x5A), (FLAGS[1], 1, 0x6B),
                            (FLAGS[2], 1, 1), (FLAGS[3], 1, 0),
                            (TIMER, 4, 0x12345678), (0x200478, 4, old),
                            (0x20047C, 4, 0), (0x20071C, 1, 0x55), (0x20071D, 1, 0x66)]
        runner.sample(dict(capture=999, percent=0, clock_enabled=False, selector=0))
        first = {'gate': runner.gate, 'accumulator': runner.accumulator}
        if runner.accumulator is not None or runner.byte(STATE) != 3 or runner.byte(0x20071E) != 1:
            raise ValueError('transition call did not defer fresh accumulator')
        union.update(runner.visited)
        runner.overrides = []
        runner.cpu.reg_write(runner.arm.UC_ARM_REG_SP, 0x203000)
        runner.cpu.reg_write(runner.arm.UC_ARM_REG_LR, 0x3F00)
        result = runner.call(0x50F0, [])
        if result != {'status': 'returned', 'r0': 0} or runner.accumulator is None:
            raise ValueError('persistent second call failed')
        if runner.byte(0x20071E) != 0 or runner.byte(ACTIVE) != 1:
            raise ValueError('persistent fresh consumption failed')
        if any(runner.cpu.reg_read(getattr(runner.arm, f'UC_ARM_REG_R{n}')) != 0x12340000+n
               for n in range(4, 12)):
            raise ValueError('persistent call register preservation failed')
        union.update(runner.visited)
        sequences.append({'old': old, 'first': first,
                          'second': {'gate': runner.gate, 'accumulator': runner.accumulator}})
    extension = json.loads((ROOT / 'audit/data/control_retention_branches.json').read_text())
    remaining = {int(a, 0) for a in extension['remaining_main_starts']}
    previous = {int(a, 0) for a in base['main_starts_visited']+extension['new_main_starts']}
    doc = {'format': 'quadzilla-idle-control-integration-v1', 'raw_sha256': SHA,
           'cases': cases, 'persistent_two_call_sequences': sequences, 'full_control_calls': len(cases)+6,
           'reference_mismatches': 0,
           'new_main_starts': [hex(a) for a in sorted(union & remaining)],
           'combined_main_starts': len(previous | (union & remaining)),
           'remaining_main_starts': [hex(a) for a in sorted(remaining-union)],
           'limits': ['controlled initialized SRAM and entry overrides; no normal-service reachability proof',
                      'original complete control calls and inherited scalar/table/timer checks; no function stubs',
                      'gate and fresh accumulator independently modeled; response arithmetic not checked here',
                      'fresh/event states are supplied, not generated by live TC2 interrupt delivery',
                      'no hardware traffic, timing, DMA, flashing or engine-output claim']}
    args.output.write_text(json.dumps(doc, indent=2)+'\n')
    print(f'{doc["full_control_calls"]} calls; new starts {doc["new_main_starts"]}; combined {doc["combined_main_starts"]}/574')


if __name__ == '__main__':
    main()
