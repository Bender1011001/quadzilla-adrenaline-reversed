#!/usr/bin/env python3
"""Exercise the original 0x499C backdown helper with controlled SRAM states."""
import argparse
import hashlib
import json
import random
import struct
from pathlib import Path

from emulate_integer_runtime import Runner, SHA


def execute(runner, case):
    arm, cpu = runner.arm, runner.cpu
    cpu.mem_write(0x200424, bytes(0x40))
    cpu.mem_write(0x2006CC, bytes(0x10))
    for address, value in ((0x200427, case["first"]), (0x200428, case["second_prior"]),
                           (0x200429, case["second"]), (0x2006D3, case["second_enabled"]),
                           (0x2006D4, case["second_threshold"]), (0x2006D7, case["first_enabled"])):
        cpu.mem_write(address, bytes((value & 255,)))
    cpu.mem_write(0x2006D8, struct.pack("<H", case["first_threshold"]))
    for address, value in ((0x200454, case["first_previous"]),
                           (0x20044C, case["second_sample"]),
                           (0x2008A8, case["first_sample"])):
        cpu.mem_write(address, struct.pack("<I", value))
    cpu.reg_write(arm.UC_ARM_REG_CPSR, 0x13)
    cpu.reg_write(arm.UC_ARM_REG_SP, 0x203000)
    cpu.reg_write(arm.UC_ARM_REG_LR, 0x3F00)
    for n in range(13):
        cpu.reg_write(getattr(arm, f"UC_ARM_REG_R{n}"), 0x12340000+n)
    cpu.emu_start(0x499D, 0x3F00, count=512)
    if cpu.reg_read(arm.UC_ARM_REG_PC) != 0x3F00 or cpu.reg_read(arm.UC_ARM_REG_SP) != 0x203000:
        raise RuntimeError("backdown helper did not return with balanced stack")
    if any(cpu.reg_read(getattr(arm, f"UC_ARM_REG_R{n}")) != 0x12340000+n for n in range(4, 8)):
        raise RuntimeError("backdown helper changed preserved registers")
    result = cpu.reg_read(arm.UC_ARM_REG_R0)
    first, second = (cpu.mem_read(a, 1)[0] for a in (0x200427, 0x200429))
    first_previous = struct.unpack("<I", cpu.mem_read(0x200454, 4))[0]
    second_prior_stored = cpu.mem_read(0x200428, 1)[0]
    if not (0 <= result <= 80 and 0 <= first <= 80 and 0 <= second <= 80):
        raise RuntimeError("backdown percentage left observed 0..80 bound")
    if result != max(first, second):
        raise RuntimeError("returned percentage differs from max of stored candidates")
    if case["first_enabled"] and first_previous != case["first_sample"]:
        raise RuntimeError("first previous-sample word was not updated")
    if not case["first_enabled"] and first_previous != case["first_previous"]:
        raise RuntimeError("disabled first path changed its history word")
    if case["second_enabled"] and second_prior_stored != (case["second_sample"] & 255):
        raise RuntimeError("second prior-sample byte was not updated")
    if not case["second_enabled"] and second_prior_stored != case["second_prior"]:
        raise RuntimeError("disabled second path changed its history byte")
    return {"result": result, "first": first, "second": second,
            "first_previous": first_previous, "second_prior_stored": second_prior_stored}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("image", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    raw = args.image.read_bytes()
    if hashlib.sha256(raw).hexdigest() != SHA:
        raise ValueError("unexpected image")
    pools = {
        "backdown": (0x4A88, (0xFFFFFED4, 0x2006CC, 0x2008A8)),
        "stretch": (0x4B28, (0x200580, 0x200190, 0x200424, 0x2005F0)),
    }
    for name, (start, words) in pools.items():
        actual = tuple(struct.unpack_from("<I", raw, a-0x4000)[0]
                       for a in range(start, start+4*len(words), 4))
        if actual != words:
            raise RuntimeError(f"{name} literal pool differs")
    if raw[0x4B26-0x4000:0x4B28-0x4000] != b"\xc0\x46":
        raise RuntimeError("stretch alignment NOP differs")
    runner = Runner(raw, extra_ranges=((0x499C, 0x4A88),))
    rng = random.Random(0x499C)
    cases = []
    for fe in (0, 1):
        for se in (0, 1):
            for first_sample in (0, 25, 100, 300, 650, 1023):
                cases.append(dict(first=20, second=30, second_prior=5, first_enabled=fe,
                                  second_enabled=se, first_threshold=400, first_previous=100,
                                  first_sample=first_sample, second_threshold=80, second_sample=45))
    for first_threshold, second_sample in ((0, 0x1234), (24, 0x100), (25, 255),
                                           (299, 256), (300, 45), (400, 0)):
        cases.append(dict(first=20, second=30, second_prior=5, first_enabled=1,
                          second_enabled=1, first_threshold=first_threshold,
                          first_previous=100, first_sample=25,
                          second_threshold=80, second_sample=second_sample))
    directed_count = len(cases)
    for _ in range(4096):
        cases.append(dict(first=rng.randrange(256), second=rng.randrange(256),
                          second_prior=rng.randrange(256), first_enabled=rng.randrange(2),
                          second_enabled=rng.randrange(2), first_threshold=rng.randrange(1024),
                          first_previous=rng.randrange(1024), first_sample=rng.randrange(1024),
                          second_threshold=rng.randrange(256), second_sample=rng.randrange(256)))
    examples = []
    for n, case in enumerate(cases):
        result = execute(runner, case)
        if n < directed_count:
            examples.append({"input": case, "output": result})
    result = {"format": "quadzilla-backdown-emulation-v1", "raw_sha256": SHA,
              "emulator": "Unicorn " + runner.uc.__version__,
              "limitation": "Synthetic SRAM states; many random values may be unreachable in service; no board or output timing model",
              "case_count": len(cases), "directed_cases": directed_count,
              "literal_pools": {name: {"start": hex(start), "words": [hex(w) for w in words]}
                                for name, (start, words) in pools.items()},
              "visited_addresses": [hex(a) for a in sorted(runner.visited)],
              "examples": examples,
              "invariants_checked": ["return equals max of stored candidate bytes", "both candidate bytes and return in 0..80",
                                     "enabled sample histories update", "R4..R7 and SP preserved"]}
    args.output.write_text(json.dumps(result, indent=2)+"\n", encoding="utf-8")
    print(f"{len(cases)} cases; {len(runner.visited)} instruction starts visited")


if __name__ == "__main__":
    main()
