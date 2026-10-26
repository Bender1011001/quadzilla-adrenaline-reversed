#!/usr/bin/env python3
"""Bounded original-byte startup checks with synthetic SRAM and MMIO.

Requires unicorn. ARM926 is an instruction surrogate, not timing or board behavior.
"""
import argparse
import hashlib
import json
from pathlib import Path

SHA = "1ae519ba6194e8f7bdaaa94333a83a9e6fda3b0563f87f7d48383b37288c1780"


def make_cpu(raw, ranges):
    import unicorn as uc
    import unicorn.arm_const as arm

    cpu = uc.Uc(uc.UC_ARCH_ARM, uc.UC_MODE_ARM)
    cpu.ctl_set_cpu_model(arm.UC_CPU_ARM_926)
    cpu.mem_map(0x4000, 0x8000)
    cpu.mem_write(0x4000, raw)
    cpu.mem_protect(0x4000, 0x8000, uc.UC_PROT_READ | uc.UC_PROT_EXEC)
    cpu.mem_map(0x200000, 0x4000)
    cpu.mem_map(0xFFFF0000, 0x10000)
    visited = set()
    writes = []

    def code_hook(_, address, size, __):
        if not any(start <= address < end for start, end in ranges):
            raise RuntimeError(f"execution left reviewed ranges at {address:#x}")
        visited.add(address)

    def write_hook(_, access, address, size, value, __):
        if address >= 0xFFFF0000:
            writes.append((address, size, value))

    cpu.hook_add(uc.UC_HOOK_CODE, code_hook)
    cpu.hook_add(uc.UC_HOOK_MEM_WRITE, write_hook)
    return cpu, arm, visited, writes


def execute(cpu, arm, entry, limit=50000):
    cpu.reg_write(arm.UC_ARM_REG_CPSR, 0x13)
    cpu.reg_write(arm.UC_ARM_REG_SP, 0x203000)
    cpu.reg_write(arm.UC_ARM_REG_LR, 0x3F00)
    cpu.emu_start(entry | 1, 0x3F00, count=limit)
    if cpu.reg_read(arm.UC_ARM_REG_PC) != 0x3F00:
        raise RuntimeError(f"instruction limit reached before return: PC={cpu.reg_read(arm.UC_ARM_REG_PC):#x}")
    if cpu.reg_read(arm.UC_ARM_REG_SP) != 0x203000:
        raise RuntimeError("unbalanced startup stack")


def run(raw):
    pools = {
        "arm_startup": (0x40F8, (0x204000, 0x414D, 0xFFFFF000, 0x4115, 0x408C, 0x77B9, 0x7435)),
        "descriptor_loop": (0x4144, (0x96C4, 0x96E8)),
        "clock_setup": (0x41C0, (0xFFFFFD44, 0xFFFFFC20, 0x601, 0xFFFFFC68,
                                 0xFFFFFC2C, 0x481C0E, 0xFFFFFC30, 0xFFFFF080,
                                 0x40E0, 0x40E4, 0xFFFFF134, 0x40E8)),
    }
    for name, (start, words) in pools.items():
        actual = tuple(int.from_bytes(raw[a-0x4000:a-0x4000+4], "little")
                       for a in range(start, start+4*len(words), 4))
        if actual != words:
            raise RuntimeError(f"{name} literal pool differs")
    cpu, arm, copied_visited, _ = make_cpu(raw, ((0x4114, 0x4144), (0x8530, 0x854A), (0x854C, 0x8562)))
    execute(cpu, arm, 0x4114)
    if cpu.mem_read(0x200000, 0x8A0) != raw[0x96E8-0x4000:0x9F88-0x4000]:
        raise RuntimeError("initialized RAM copy differs from source")
    if cpu.mem_read(0x2008A0, 0x3E2) != bytes(0x3E2):
        raise RuntimeError("zero-fill descriptor did not clear RAM")
    if cpu.mem_read(0x200C84, 0xA4) != raw[0xB114-0x4000:0xB1B8-0x4000]:
        raise RuntimeError("executable template copy differs from source")

    clock, arm, clock_visited, writes = make_cpu(raw, ((0x414C, 0x41BE),))
    clock.mem_write(0xFFFFFC68, (0xD).to_bytes(4, "little"))
    execute(clock, arm, 0x414C)
    values = {(address, value) for address, size, value in writes if size == 4}
    required = {
        (0xFFFFFF60, 0x100), (0xFFFFFD44, 0x8000),
        (0xFFFFFC20, 0x601), (0xFFFFFC2C, 0x481C0E),
        (0xFFFFFC30, 0x4), (0xFFFFFC30, 0x7),
        (0xFFFFF080, 0x40E0), (0xFFFFF134, 0x40E8),
    }
    if not required <= values:
        raise RuntimeError(f"missing expected MMIO writes: {sorted(required-values)}")
    vectors = [int.from_bytes(clock.mem_read(0xFFFFF080+i*4, 4), "little") for i in range(31)]
    if vectors != [0x40E0] + [0x40E4]*30:
        raise RuntimeError("fallback AIC vectors differ")
    return {
        "format": "quadzilla-startup-init-emulation-v1",
        "raw_sha256": SHA,
        "limitation": "ARM926 instruction surrogate; synthetic ready flags and MMIO memory, no oscillator, flash, watchdog or interrupt hardware model",
        "literal_pools": {name: {"start": hex(start), "words": [hex(word) for word in words]}
                          for name, (start, words) in pools.items()},
        "descriptor_copy": {
            "initialized_bytes": 0x8A0,
            "zeroed_bytes": 0x3E2,
            "executable_template_bytes": 0xA4,
            "visited_instruction_starts": len(copied_visited),
        },
        "clock_setup": {
            "synthetic_pmc_sr": "0xd",
            "visited_instruction_starts": len(clock_visited),
            "mmio_writes": [{"address": hex(a), "size": size, "value": hex(v)} for a, size, v in writes],
            "aic_fallback_vector_words": len(vectors),
        },
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("image", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    raw = args.image.read_bytes()
    if hashlib.sha256(raw).hexdigest() != SHA:
        raise ValueError("unexpected firmware image")
    result = run(raw)
    args.output.write_text(json.dumps(result, indent=2)+"\n", encoding="utf-8")
    print(f"copied and cleared three descriptors; {result['clock_setup']['visited_instruction_starts']} clock-setup starts visited")


if __name__ == "__main__":
    main()
