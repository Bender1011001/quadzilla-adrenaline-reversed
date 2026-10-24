#!/usr/bin/env python3
"""Execute exact timer-setup bytes with synthetic MMIO, never a controller."""
import argparse
import hashlib
import json
import struct
from pathlib import Path

from audit_aid_tables import AidRunner, SHA


class TimerRunner(AidRunner):
    def __init__(self, raw):
        super().__init__(raw)
        self.allowed_ranges = ((0x6FB4, 0x70CA),)
        self.cpu.mem_map(0xFFFA0000, 0x4000)
        self.cpu.mem_map(0xFFFFF000, 0x1000)
        self.writes = []
        self.cpu.hook_add(self.uc.UC_HOOK_MEM_WRITE, self.record)

    def record(self, cpu, access, address, size, value, user):
        if address >= 0xFFFA0000 or 0x2006F8 <= address < 0x200750:
            self.writes.append({"site": hex(cpu.reg_read(self.arm.UC_ARM_REG_PC)),
                                "address": hex(address), "size": size,
                                "value": hex(value & ((1 << (size*8)) - 1))})

    def sample(self, clock_status):
        self.reset()
        self.cpu.mem_write(0xFFFA0000, bytes(0x4000))
        self.cpu.mem_write(0xFFFFF000, bytes(0x1000))
        self.writes.clear()
        self.visited.clear()
        for n in range(3):
            self.cpu.mem_write(0xFFFA0020 + 0x40*n, struct.pack("<I", clock_status))
        before = []
        for n in range(4, 8):
            reg = getattr(self.arm, f"UC_ARM_REG_R{n}")
            value = 0x12340000+n
            self.cpu.reg_write(reg, value)
            before.append(value)
        result = self.call(0x6FB4, [])
        if result["status"] != "returned":
            raise RuntimeError(result)
        after = [self.cpu.reg_read(getattr(self.arm, f"UC_ARM_REG_R{n}")) for n in range(4, 8)]
        if after != before:
            raise RuntimeError("callee-saved register mismatch")
        return {"synthetic_tc_sr_each": hex(clock_status), "return_r0": result["r0"],
                "writes": self.writes.copy(), "visited": [hex(x) for x in sorted(self.visited)]}

    def callback(self, entry, clock_status=0):
        self.reset()
        self.cpu.mem_write(0xFFFA0000, bytes(0x4000))
        self.cpu.mem_write(0xFFFFF000, bytes(0x1000))
        self.cpu.mem_write(0xFFFA0060, struct.pack("<I", clock_status))
        self.allowed_ranges = ((entry, {0x6C48: 0x6C5E, 0x6C68: 0x6C82}[entry]),)
        self.writes.clear()
        self.visited.clear()
        result = self.call(entry, [])
        if result["status"] != "returned":
            raise RuntimeError(result)
        return {"entry": hex(entry), "synthetic_tc1_sr": hex(clock_status),
                "writes": self.writes.copy(), "visited": [hex(x) for x in sorted(self.visited)]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("image", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    raw = args.image.read_bytes()
    if hashlib.sha256(raw).hexdigest() != SHA:
        raise ValueError("unexpected application image")
    pointers = {}
    for address in (0x2006F8, 0x2006FC, 0x200700, 0x200704, 0x200728):
        source = 0x96E8 + (address - 0x200000)
        pointers[hex(address)] = {"image_source": hex(source),
                                  "value": hex(struct.unpack_from("<I", raw, source-0x4000)[0])}
    expected = [0xFFFA00C0, 0xFFFA00C4, 0xFFFA0000, 0xFFFA0040, 0xFFFA0080]
    if [int(row["value"], 0) for row in pointers.values()] != expected:
        raise ValueError("timer pointer template changed")
    runner = TimerRunner(raw)
    result = {"format": "quadzilla-timer-setup-emulation-v1", "raw_sha256": SHA,
              "entry": "0x6fb4", "cpu": "ARM926 functional surrogate",
              "peripherals": "synthetic read/write memory with no device side effects",
              "source_pointers": pointers,
              "cases": [runner.sample(0), runner.sample(0x10000)],
              "callbacks": [runner.callback(0x6C48), runner.callback(0x6C68, 0),
                            runner.callback(0x6C68, 0x10000)],
              "limits": ["TC_SR, AIC and PMC are plain synthetic memory, not peripheral models",
                         "only uniform CLKSTA=0 and CLKSTA=1 channel states sampled",
                         "callbacks are called as Thumb routines without IRQ entry simulation",
                         "counter timing, pin wiring and physical outputs not simulated"]}
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
