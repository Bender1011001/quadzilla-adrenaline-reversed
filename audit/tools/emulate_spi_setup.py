#!/usr/bin/env python3
"""Execute exact SPI setup bytes against synthetic register memory only."""
import argparse
import hashlib
import json
import struct
from pathlib import Path

from audit_aid_tables import AidRunner, SHA


class SpiRunner(AidRunner):
    def __init__(self, raw):
        super().__init__(raw)
        self.cpu.mem_map(0xFFFE0000, 0x1000)
        self.cpu.mem_map(0xFFFFF000, 0x1000)
        self.writes = []
        self.reads = []
        self.cpu.hook_add(self.uc.UC_HOOK_MEM_WRITE, self.record_write)
        self.cpu.hook_add(self.uc.UC_HOOK_MEM_READ, self.record_read)

    def record_write(self, cpu, access, address, size, value, user):
        if address >= 0xFFFE0000:
            self.writes.append({"site": hex(cpu.reg_read(self.arm.UC_ARM_REG_PC)),
                                "address": hex(address), "size": size, "value": hex(value)})

    def record_read(self, cpu, access, address, size, value, user):
        if address >= 0xFFFE0000:
            self.reads.append({"site": hex(cpu.reg_read(self.arm.UC_ARM_REG_PC)),
                               "address": hex(address), "size": size})

    def sample(self, entry, aic_vector=0):
        self.reset()
        self.cpu.mem_write(0xFFFE0000, bytes(0x1000))
        self.cpu.mem_write(0xFFFFF000, bytes(0x1000))
        self.cpu.mem_write(0xFFFFF094, struct.pack("<I", aic_vector))
        self.allowed_ranges = ((entry, {0x6B44: 0x6B46, 0x6BD8: 0x6C14}[entry]),)
        self.writes.clear()
        self.reads.clear()
        self.visited.clear()
        result = self.call(entry, [])
        if result["status"] != "returned":
            raise RuntimeError(result)
        return {"entry": hex(entry), "initial_aic_svr5": hex(aic_vector),
                "writes": self.writes.copy(), "reads": self.reads.copy(),
                "visited": [hex(x) for x in sorted(self.visited)]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("image", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    raw = args.image.read_bytes()
    if hashlib.sha256(raw).hexdigest() != SHA:
        raise ValueError("unexpected application image")
    source = {hex(address): hex(struct.unpack_from("<I", raw, address-0x4000)[0])
              for address in (0x6C14, 0x6C18, 0x6C1C, 0x6C20, 0x6C24, 0x6C28,
                              0x6C2C, 0x6C30, 0x6C34, 0x6C38, 0x6C3C, 0x6C40, 0x6C44)}
    runner = SpiRunner(raw)
    result = {"format": "quadzilla-spi-setup-emulation-v1", "raw_sha256": SHA,
              "cpu": "ARM926 functional surrogate", "peripherals": "synthetic read/write memory",
              "literal_words": source,
              "cases": [runner.sample(0x6BD8, 0), runner.sample(0x6BD8, 0xDEADBEEF),
                        runner.sample(0x6B44)],
              "limits": ["SPI, PMC and AIC register command side effects are absent",
                         "no physical SPI transaction or interrupt context simulated",
                         "only AIC vector prestate varies between setup cases"]}
    args.output.write_text(json.dumps(result, indent=2)+"\n", encoding="utf-8")


if __name__ == "__main__":
    main()
