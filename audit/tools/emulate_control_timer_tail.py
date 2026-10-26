#!/usr/bin/env python3
"""Execute original bytes from stretch call through conditional TC0_RC write.

Starts inside 0x50F0 with synthetic caller state. This is a path test, not an
assertion that the chosen RAM values can arise on a connected vehicle.
"""
import argparse
import hashlib
import json
import struct
from pathlib import Path

from emulate_integer_runtime import Runner, SHA


def run_case(runner, *, table_byte, backdown, tc_clock_enabled, clamp_enabled, telemetry,
             selector_limit=100):
    uc, arm, cpu = runner.uc, runner.arm, runner.cpu
    cpu.mem_write(0x200424, bytes(0x40))
    cpu.mem_write(0x200580, bytes(0x20))
    cpu.mem_write(0x2006EC, bytes((clamp_enabled,)))
    cpu.mem_write(0x200ADD, b"\0")
    cpu.mem_write(0x200BCD, bytes((backdown,)))
    for address, value in ((0x200433, 0), (0x200434, 0), (0x20058A, 10),
                           (0x20058B, 0), (0x20058C, 50), (0x200190, table_byte)):
        cpu.mem_write(address, bytes((value,)))
    for address, value in ((0x2005F0, 10), (0x200590, 1700), (0x200594, 10000)):
        cpu.mem_write(address, struct.pack("<I", value))
    cpu.mem_write(0xFFFA001C, struct.pack("<I", 0xA5A5A5A5))
    cpu.mem_write(0xFFFA0020, struct.pack("<I", 0x10000 if tc_clock_enabled else 0))
    cpu.mem_write(0x203000, bytes(0x20))
    cpu.mem_write(0x203004, struct.pack("<I", selector_limit))
    for n in range(13):
        cpu.reg_write(getattr(arm, f"UC_ARM_REG_R{n}"), 0x12340000+n)
    cpu.reg_write(arm.UC_ARM_REG_CPSR, 0x13)
    cpu.reg_write(arm.UC_ARM_REG_SP, 0x203000)
    cpu.reg_write(arm.UC_ARM_REG_LR, 0x3F00)
    for reg, value in ((arm.UC_ARM_REG_R0, 0), (arm.UC_ARM_REG_R1, 0),
                       (arm.UC_ARM_REG_R2, 100), (arm.UC_ARM_REG_R4, 0x200424),
                       (arm.UC_ARM_REG_R5, telemetry), (arm.UC_ARM_REG_R7, 1)):
        cpu.reg_write(reg, value)
    visited = set()
    mmio_writes = []

    def stop_at_boundary(_, address, size, __):
        visited.add(address)
        if address == 0x53A2:
            cpu.emu_stop()

    def record_mmio(_, access, address, size, value, __):
        if address == 0xFFFA001C:
            mmio_writes.append(value)

    h_code = cpu.hook_add(uc.UC_HOOK_CODE, stop_at_boundary)
    h_mem = cpu.hook_add(uc.UC_HOOK_MEM_WRITE, record_mmio)
    try:
        cpu.emu_start(0x5325, 0x3F00, count=8192)
    finally:
        cpu.hook_del(h_code)
        cpu.hook_del(h_mem)
    if cpu.reg_read(arm.UC_ARM_REG_PC) != 0x53A2 or cpu.reg_read(arm.UC_ARM_REG_SP) != 0x203000:
        raise RuntimeError("tail did not stop at boundary with balanced stack")
    effective = cpu.reg_read(arm.UC_ARM_REG_R6)
    expected_rc = (effective*24+3) & 0xFFFFFFFF
    if (tc_clock_enabled or selector_limit == 0) and mmio_writes:
        raise RuntimeError("RC write occurred despite clock-status or selector gate")
    if not tc_clock_enabled and selector_limit != 0 and mmio_writes != [expected_rc]:
        raise RuntimeError("RC write value differs from computed stretch")
    return {"input": {"table_byte": table_byte, "backdown": backdown,
                      "tc_clock_enabled": tc_clock_enabled, "clamp_enabled": clamp_enabled,
                      "telemetry": telemetry, "selector_limit": selector_limit},
            "effective_stretch_r6": effective, "computed_rc": expected_rc,
            "tc0_rc_writes": [hex(x) for x in mmio_writes],
            "visited": [hex(x) for x in sorted(visited)]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("image", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    raw = args.image.read_bytes()
    if hashlib.sha256(raw).hexdigest() != SHA:
        raise ValueError("unexpected image")
    runner = Runner(raw, extra_ranges=((0x5324, 0x53A4), (0x4A94, 0x4B26), (0x6FA0, 0x6FB2)))
    runner.cpu.mem_map(0xFFFA0000, 0x1000)
    cases = [run_case(runner, table_byte=t, backdown=b, tc_clock_enabled=c,
                      clamp_enabled=k, telemetry=y, selector_limit=s)
             for t,b,c,k,y,s in ((100,0,0,0,100,100), (100,80,0,0,100,100),
                                 (100,0,1,0,100,100), (100,0,0,0,100,0),
                                 (140,0,0,0,100,100), (140,0,0,1,100,100),
                                 (140,0,0,1,3200,100))]
    result = {"format": "quadzilla-control-timer-tail-emulation-v1", "raw_sha256": SHA,
              "emulator": "Unicorn " + runner.uc.__version__,
              "limitation": "Entry at 0x5324 with synthetic stack/SRAM and TC0 status; no proof of live reachability, timer waveform, or physical output",
              "cases": cases}
    args.output.write_text(json.dumps(result, indent=2)+"\n", encoding="utf-8")
    print([(c["input"]["table_byte"], c["input"]["tc_clock_enabled"], c["tc0_rc_writes"])
           for c in cases])


if __name__ == "__main__":
    main()
