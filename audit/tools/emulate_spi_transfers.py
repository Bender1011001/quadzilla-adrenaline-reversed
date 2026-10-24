#!/usr/bin/env python3
"""Run exact SPI/PDC transfer primitives against synthetic MMIO, without devices."""
import argparse
import hashlib
import json
import struct
from pathlib import Path

from audit_aid_tables import AidRunner, SHA


SPI = 0xFFFE0000
PIO_PDSR = 0xFFFFF43C


class TransferRunner(AidRunner):
    def __init__(self, raw):
        super().__init__(raw)
        self.allowed_ranges = ((0x571C, 0x5736), (0x573C, 0x5756),
                               (0x6B48, 0x6B60), (0x6B64, 0x6B8C),
                               (0x6B8C, 0x6B9C), (0x6B9C, 0x6BD2))
        self.cpu.mem_map(SPI, 0x1000)
        self.cpu.mem_map(0xFFFFF000, 0x1000)
        self.writes = []
        self.reads = []
        self.cpu.hook_add(self.uc.UC_HOOK_MEM_WRITE, self.record_write)
        self.cpu.hook_add(self.uc.UC_HOOK_MEM_READ, self.record_read)

    def record_write(self, cpu, access, address, size, value, user):
        if address >= SPI:
            self.writes.append({"site": hex(cpu.reg_read(self.arm.UC_ARM_REG_PC)),
                                "address": hex(address), "size": size, "value": hex(value)})

    def record_read(self, cpu, access, address, size, value, user):
        if address >= SPI:
            self.reads.append({"site": hex(cpu.reg_read(self.arm.UC_ARM_REG_PC)),
                               "address": hex(address), "size": size})

    def sample(self, entry, args, status=0, pin_status=0):
        self.reset()
        self.cpu.mem_write(SPI, bytes(0x1000))
        self.cpu.mem_write(0xFFFFF000, bytes(0x1000))
        self.cpu.mem_write(SPI+0x10, struct.pack("<I", status))
        self.cpu.mem_write(SPI+8, struct.pack("<I", 0xA5))
        self.cpu.mem_write(PIO_PDSR, struct.pack("<I", pin_status))
        self.writes.clear()
        self.reads.clear()
        self.visited.clear()
        preserved = []
        for n in range(4, 8):
            reg = getattr(self.arm, f"UC_ARM_REG_R{n}")
            value = 0x12340000+n
            self.cpu.reg_write(reg, value)
            preserved.append((reg, value))
        outcome = self.call(entry, args)
        if outcome["status"] != "returned":
            raise RuntimeError(outcome)
        if any(self.cpu.reg_read(reg) != value for reg, value in preserved):
            raise RuntimeError("R4-R7 preservation mismatch")
        return {"entry": hex(entry), "args": [hex(a) for a in args],
                "synthetic_spi_sr": hex(status), "synthetic_pio_pdsr": hex(pin_status),
                "return_r0": hex(outcome["r0"]), "writes": self.writes.copy(),
                "reads": self.reads.copy(), "visited": [hex(a) for a in sorted(self.visited)],
                "callee_saved_r4_r7_preserved": True}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("image", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    raw = args.image.read_bytes()
    if hashlib.sha256(raw).hexdigest() != SHA:
        raise ValueError("unexpected application image")
    literals = {hex(a): hex(struct.unpack_from("<I", raw, a-0x4000)[0])
                for a in (0x5738, 0x5758, 0x6B60, 0x6BD4)}
    runner = TransferRunner(raw)
    cases = [runner.sample(entry, [selector]) for entry in (0x571C, 0x573C)
             for selector in (0, 1, 2, 3)]
    for entry, registers in ((0x6B48, [SPI]), (0x6B64, [SPI, 0x200600, 3]),
                             (0x6B9C, [SPI, 0x200620, 0x200600, 3])):
        for status in (0, 0x20):
            for pins in (0, 0x800):
                cases.append(runner.sample(entry, registers, status, pins))
    cases.extend(runner.sample(0x6B8C, [SPI], status) for status in (0, 0x10, 0xFFFFFFFF))
    for count in (0, 0xFFFFFFFF):
        cases.append(runner.sample(0x6B64, [SPI, 0, count], 0x20, 0x800))
        cases.append(runner.sample(0x6B9C, [SPI, 0, 0xFFFFFFFF, count], 0x20, 0x800))
    result = {"format": "quadzilla-spi-transfer-emulation-v1", "raw_sha256": SHA,
              "cpu": "ARM926 functional surrogate", "literal_words": literals,
              "cases": cases,
              "limits": ["SPI/PDC/PIO registers are plain memory without side effects",
                         "no PDC transfer, buffer dereference, pin voltage or timing modeled",
                         "raw 32-bit writes do not prove hardware-effective pointer/count widths",
                         "direct helper edge cases do not establish live caller reachability"]}
    args.output.write_text(json.dumps(result, indent=2)+"\n", encoding="utf-8")


if __name__ == "__main__":
    main()
