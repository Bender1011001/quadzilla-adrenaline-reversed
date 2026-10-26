#!/usr/bin/env python3
"""Bounded synthetic calls for the last three baseline entry roles."""
import argparse
import hashlib
import json
from pathlib import Path

SHA = "1ae519ba6194e8f7bdaaa94333a83a9e6fda3b0563f87f7d48383b37288c1780"


def call(raw, entry, allowed, sram=(), status=None, limit=100):
    import unicorn as uc
    import unicorn.arm_const as arm

    cpu = uc.Uc(uc.UC_ARCH_ARM, uc.UC_MODE_ARM)
    cpu.ctl_set_cpu_model(arm.UC_CPU_ARM_926)
    cpu.mem_map(0x4000, 0x8000)
    cpu.mem_write(0x4000, raw)
    cpu.mem_protect(0x4000, 0x8000, uc.UC_PROT_READ | uc.UC_PROT_EXEC)
    cpu.mem_map(0x200000, 0x4000)
    cpu.mem_map(0xFFFF0000, 0x10000)
    cpu.mem_write(0x200C84, raw[0xB114-0x4000:0xB1B8-0x4000])
    for address, value in sram:
        cpu.mem_write(address, bytes((value,)))
    if status is not None:
        cpu.mem_write(0xFFFFFF68, status.to_bytes(4, "little"))
    visited = set()

    def trace(_, address, size, __):
        if not allowed[0] <= address < allowed[1]:
            raise RuntimeError(f"execution left helper at {address:#x}")
        visited.add(address)

    cpu.hook_add(uc.UC_HOOK_CODE, trace)
    cpu.reg_write(arm.UC_ARM_REG_CPSR, 0x13)
    cpu.reg_write(arm.UC_ARM_REG_SP, 0x203000)
    cpu.reg_write(arm.UC_ARM_REG_LR, 0x3F00)
    cpu.reg_write(arm.UC_ARM_REG_R0, 0xA5A5A5A5)
    cpu.emu_start(entry | 1, 0x3F00, count=limit)
    return {"returned": cpu.reg_read(arm.UC_ARM_REG_PC) == 0x3F00,
            "r0": hex(cpu.reg_read(arm.UC_ARM_REG_R0)),
            "stack_preserved": cpu.reg_read(arm.UC_ARM_REG_SP) == 0x203000,
            "visited": [hex(ea) for ea in sorted(visited)]}


def run(raw):
    literals = {0x7A48: 0x7445, 0x74E0: 0x200791, 0x74E4: 0x2005DD}
    for address, expected in literals.items():
        actual = int.from_bytes(raw[address-0x4000:address-0x4000+4], "little")
        if actual != expected:
            raise RuntimeError(f"unexpected literal at {address:#x}")
    if raw[0x7446-0x4000:0x7448-0x4000] != b"\xff\xff":
        raise RuntimeError("callback alignment differs")
    noop = call(raw, 0x7444, (0x7444, 0x7446))
    if not noop["returned"] or noop["r0"] != "0xa5a5a5a5" or not noop["stack_preserved"]:
        raise RuntimeError("no-op callback changed state")
    predicate = []
    for first, second in ((0, 0), (1, 0), (0, 1), (1, 1), (255, 2)):
        result = call(raw, 0x74C4, (0x74C4, 0x74DE),
                      ((0x200791, first), (0x2005DD, second)))
        if not result["returned"] or int(result["r0"], 0) != int(bool(first and second)):
            raise RuntimeError("predicate truth table differs")
        predicate.append({"sram_0x200791": first, "sram_0x2005dd": second, **result})
    ready = call(raw, 0x200C84, (0x200C84, 0x200C92), status=1)
    waiting = call(raw, 0x200C84, (0x200C84, 0x200C92), status=0, limit=50)
    if not ready["returned"] or waiting["returned"] or len(waiting["visited"]) != 5:
        raise RuntimeError("flash-ready loop differs")
    return {"format": "quadzilla-remaining-entry-emulation-v1", "raw_sha256": SHA,
            "limitation": "Synthetic SRAM and status register; ARM926 instruction surrogate, no flash hardware or reachability proof",
            "literal_words": {hex(a): hex(v) for a, v in literals.items()},
            "no_op_callback": noop, "sram_predicate": predicate,
            "runtime_ready_helper": {"source": "0xb114", "runtime": "0x200c84",
                                     "ready_status_1": ready, "waiting_status_0": waiting}}


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
    print("verified no-op callback, SRAM predicate, and copied flash-ready loop")


if __name__ == "__main__":
    main()
