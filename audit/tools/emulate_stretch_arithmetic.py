#!/usr/bin/env python3
"""Run 0x4A94 and its real division helpers against controlled SRAM scenarios."""
import argparse
import hashlib
import json
import random
import struct
import sys
from pathlib import Path

from emulate_integer_runtime import Runner, SHA

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
from model_stretch_arithmetic import applied_value


def execute(runner, fields):
    arm, cpu = runner.arm, runner.cpu
    cpu.reg_write(arm.UC_ARM_REG_CPSR, 0x13)
    cpu.reg_write(arm.UC_ARM_REG_SP, 0x203000)
    cpu.reg_write(arm.UC_ARM_REG_LR, 0x3F00)
    for i in range(13):
        cpu.reg_write(getattr(arm, f"UC_ARM_REG_R{i}"), 0x12340000+i)
    for reg, value in ((arm.UC_ARM_REG_R0, 0), (arm.UC_ARM_REG_R1, 0), (arm.UC_ARM_REG_R2, fields["percent"])):
        cpu.reg_write(reg, value)
    for address, key in ((0x200433, "step"), (0x200434, "residue"), (0x20058C, "minimum"),
                         (0x20058B, "low"), (0x20058A, "high"), (0x200190, "table_byte")):
        cpu.mem_write(address, bytes([fields[key]]))
    for address, key in ((0x2005F0, "captured"), (0x200590, "requested")):
        cpu.mem_write(address, struct.pack("<I", fields[key]))
    cpu.emu_start(0x4A95, 0x3F00, count=8192)
    if cpu.reg_read(arm.UC_ARM_REG_PC) != 0x3F00 or cpu.reg_read(arm.UC_ARM_REG_SP) != 0x203000:
        raise RuntimeError("control routine did not return with balanced stack")
    for i in range(4, 12):
        if cpu.reg_read(getattr(arm, f"UC_ARM_REG_R{i}")) != 0x12340000+i:
            raise RuntimeError("callee-preserved register changed")
    return cpu.reg_read(arm.UC_ARM_REG_R0)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("image", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    raw = args.image.read_bytes()
    if hashlib.sha256(raw).hexdigest() != SHA:
        raise ValueError("unexpected image")
    runner = Runner(raw, extra_ranges=((0x4A94, 0x4B26),))
    base = dict(step=0, residue=0, captured=10, minimum=50, low=0, high=10,
                requested=1700, table_byte=100, percent=100)
    cases = [dict(base, table_byte=n, percent=p) for n in (0, 50, 100, 127, 128, 140, 150, 255) for p in (0, 1, 50, 99, 100)]
    cases += [dict(base, low=20), dict(base, low=10, high=10), dict(base, step=30, residue=10)]
    cases += [dict(base, minimum=0, captured=99, high=100, requested=1019, table_byte=1)]
    directed_count = len(cases)
    rng = random.Random(0x4A94)
    for _ in range(2048):
        cases.append(dict(step=rng.randrange(31), residue=rng.randrange(6), captured=rng.randrange(1025),
                          minimum=rng.randrange(101), low=rng.randrange(101), high=rng.randrange(101),
                          requested=rng.randrange(800, 2201), table_byte=rng.randrange(256), percent=rng.randrange(101)))
    failures, examples = [], []
    for n, fields in enumerate(cases):
        actual, expected = execute(runner, fields), applied_value(**fields)
        if actual != expected:
            failures.append({"fields": fields, "actual": actual, "expected": expected})
        if n < directed_count:
            examples.append({"fields": fields, "actual_r0": actual})
    result = {"format": "quadzilla-stretch-arithmetic-emulation-v1", "raw_sha256": SHA,
              "emulator": "Unicorn " + runner.uc.__version__, "cpu": "ARM926 functional surrogate",
              "cases": len(cases), "mismatches": failures, "examples": examples,
              "visited_addresses": [hex(x) for x in sorted(runner.visited)],
              "limits": ["controlled SRAM, not validated vehicle states", "row/column fixed at zero to isolate arithmetic",
                         "not exhaustive input or control-flow proof", "no peripherals mapped, no hardware output",
                         "R4..R11 and SP preservation checked; instruction budget 8192 per call"]}
    args.output.write_text(json.dumps(result, indent=2)+"\n", encoding="utf-8")
    print(f"0x4A94: {len(cases)} cases, {len(failures)} mismatches")
    if failures:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
