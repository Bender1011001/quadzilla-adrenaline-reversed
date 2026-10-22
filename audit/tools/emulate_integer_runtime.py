#!/usr/bin/env python3
"""Execute exact division-helper bytes in Unicorn, without device I/O.

Requires an independently obtained image and optional `unicorn==2.1.4` package.
ARM926 is a functional surrogate, not ARM7TDMI hardware or cycle simulation.
"""
import argparse
import hashlib
import json
import random
from pathlib import Path

SHA = "1ae519ba6194e8f7bdaaa94333a83a9e6fda3b0563f87f7d48383b37288c1780"
MASK = 0xFFFFFFFF


def signed(x):
    return x if x < 0x80000000 else x-0x100000000


def reference(kind, numerator, denominator):
    if kind == "u8":
        numerator &= 255
        denominator &= 255
    elif kind == "s32":
        numerator, denominator = signed(numerator), signed(denominator)
    if denominator == 0:
        # The signed routine branches to its epilogue after absolute-value
        # preprocessing, before sign restoration. This is an observed runtime
        # policy, not a mathematical definition of division by zero.
        return abs(numerator) & MASK, 0
    quotient = abs(numerator)//abs(denominator)
    if (numerator < 0) != (denominator < 0):
        quotient = -quotient
    remainder = numerator-quotient*denominator
    return remainder & MASK, quotient & MASK


class Runner:
    def __init__(self, raw, extra_ranges=()):
        import unicorn as uc
        import unicorn.arm_const as arm
        self.uc, self.arm = uc, arm
        self.allowed_ranges = ((0x8564, 0x8678),) + tuple(extra_ranges)
        self.cpu = uc.Uc(uc.UC_ARCH_ARM, uc.UC_MODE_ARM)
        self.cpu.ctl_set_cpu_model(arm.UC_CPU_ARM_926)
        self.cpu.mem_map(0x4000, 0x8000)
        self.cpu.mem_write(0x4000, raw)
        self.cpu.mem_protect(0x4000, 0x8000, uc.UC_PROT_READ | uc.UC_PROT_EXEC)
        self.cpu.mem_map(0x200000, 0x4000, uc.UC_PROT_READ | uc.UC_PROT_WRITE)
        self.visited = set()
        self.cpu.hook_add(uc.UC_HOOK_CODE, self.trace)
        self.preserved = [(getattr(arm, f"UC_ARM_REG_R{i}"), 0x12340000+i) for i in range(2, 12)]

    def trace(self, cpu, address, size, user):
        if not any(lo <= address < hi for lo, hi in self.allowed_ranges):
            raise RuntimeError(f"execution left division region: {address:#x}")
        self.visited.add(address)

    def run(self, entry, thumb, numerator, denominator):
        arm, cpu = self.arm, self.cpu
        cpu.reg_write(arm.UC_ARM_REG_CPSR, 0x13)
        cpu.reg_write(arm.UC_ARM_REG_SP, 0x203000)
        cpu.reg_write(arm.UC_ARM_REG_LR, 0x3F00)
        cpu.reg_write(arm.UC_ARM_REG_R0, numerator)
        cpu.reg_write(arm.UC_ARM_REG_R1, denominator)
        cpu.reg_write(arm.UC_ARM_REG_R12, 0xDEADBEEF)
        for reg, value in self.preserved:
            cpu.reg_write(reg, value)
        cpu.emu_start(entry | int(thumb), 0x3F00, count=2048)
        if cpu.reg_read(arm.UC_ARM_REG_PC) != 0x3F00:
            raise RuntimeError("instruction limit reached without returning")
        if cpu.reg_read(arm.UC_ARM_REG_SP) != 0x203000:
            raise RuntimeError("unbalanced stack")
        if any(cpu.reg_read(reg) != value for reg, value in self.preserved):
            raise RuntimeError("R2..R11 preservation mismatch")
        return cpu.reg_read(arm.UC_ARM_REG_R0), cpu.reg_read(arm.UC_ARM_REG_R1)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("image", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    raw = args.image.read_bytes()
    if hashlib.sha256(raw).hexdigest() != SHA:
        raise ValueError("unexpected firmware image")
    runner = Runner(raw)
    edges = [0, 1, 2, 3, 7, 100, 127, 128, 255, 256, 0x7FFFFFFF, 0x80000000, 0xFFFFFFF9, MASK-1, MASK]
    rng = random.Random(0x284)
    samples = [(a, b) for a in edges for b in edges] + [(rng.getrandbits(32), rng.getrandbits(32)) for _ in range(4096)]
    suites = []
    for kind, entry, thumb, vectors in (
        ("u8", 0x8564, True, ((a, b) for a in range(256) for b in range(256))),
        ("u32", 0x8574, True, samples), ("s32", 0x8584, True, samples),
        ("u8", 0x8568, False, samples), ("u32", 0x8578, False, samples),
        ("s32", 0x8588, False, samples)):
        count, mismatches, examples = 0, [], []
        runner.visited.clear()
        for a, b in vectors:
            result = runner.run(entry, thumb, a, b)
            expected = reference(kind, a, b)
            count += 1
            if result != expected:
                if len(mismatches) < 20:
                    mismatches.append({"inputs": [a, b], "actual_r0_r1": result, "expected": expected})
                else:
                    raise RuntimeError("more than 20 arithmetic mismatches")
            if len(examples) < 8 or (a, b) in [(100, 3), (7, 0), (0xFFFFFFF9, 0), (0xFFFFFFF9, 3), (0x80000000, MASK)]:
                examples.append({"inputs": [a, b], "r0_remainder": result[0], "r1_quotient": result[1]})
        suites.append({"entry": hex(entry), "isa": "thumb" if thumb else "arm", "kind": kind,
                       "cases": count, "mismatches": mismatches,
                       "visited_addresses": [hex(x) for x in sorted(runner.visited)], "examples": examples})
        print(f"{entry:#x} {kind}: {count} cases, {len(mismatches)} mismatches", flush=True)
    result = {"format": "quadzilla-integer-emulation-v1", "raw_sha256": SHA,
              "emulator": "Unicorn", "version": runner.uc.__version__, "cpu": "ARM926 functional surrogate",
              "limits": ["not hardware or cycle validation", "not an exhaustive 32-bit proof",
                         "instruction budget 2048 per call", "only ROM read/execute and SRAM read/write mapped; no peripherals"],
              "preservation_checked": "R2..R11 and SP", "return_convention": "R0 remainder; R1 quotient",
              "suites": suites}
    args.output.write_text(json.dumps(result, indent=2)+"\n", encoding="utf-8")
    if any(s["mismatches"] for s in suites):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
