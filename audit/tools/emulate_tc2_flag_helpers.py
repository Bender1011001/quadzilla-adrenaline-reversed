#!/usr/bin/env python3
"""Execute two exact TC2-triggered SRAM flag helpers without device I/O."""
import argparse
import hashlib
import json
import struct
from pathlib import Path

from audit_aid_tables import AidRunner, SHA


BASE = 0x2007C8


class FlagRunner(AidRunner):
    def __init__(self, raw):
        super().__init__(raw)
        self.writes = []
        self.cpu.hook_add(self.uc.UC_HOOK_MEM_WRITE, self.record)

    def record(self, cpu, access, address, size, value, user):
        if BASE <= address < BASE+0x18:
            self.writes.append({"site": hex(cpu.reg_read(self.arm.UC_ARM_REG_PC)),
                                "address": hex(address), "size": size, "value": hex(value)})

    def sample(self, entry, gate):
        self.reset()
        self.allowed_ranges = ((entry, {0x7F28: 0x7F40, 0x7F40: 0x7F58}[entry]),)
        self.cpu.mem_write(BASE, bytes(0x18))
        self.cpu.mem_write(BASE + {0x7F28: 5, 0x7F40: 4}[entry], bytes([gate]))
        self.writes.clear()
        self.visited.clear()
        result = self.call(entry, [])
        if result["status"] != "returned":
            raise RuntimeError(result)
        return {"entry": hex(entry), "gate": gate, "writes": self.writes.copy(),
                "after": bytes(self.cpu.mem_read(BASE, 0x18)).hex(),
                "visited": [hex(x) for x in sorted(self.visited)]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("image", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    raw = args.image.read_bytes()
    if hashlib.sha256(raw).hexdigest() != SHA:
        raise ValueError("unexpected application image")
    pointers = {hex(a): hex(struct.unpack_from("<I", raw, a-0x4000)[0])
                for a in (0x81A4, 0x8034)}
    if set(pointers.values()) != {hex(BASE)}:
        raise ValueError("flag helper pointer changed")
    runner = FlagRunner(raw)
    result = {"format": "quadzilla-tc2-flag-helper-emulation-v1", "raw_sha256": SHA,
              "cpu": "ARM926 functional surrogate", "literal_pointers": pointers,
              "cases": [runner.sample(entry, gate) for entry in (0x7F28, 0x7F40)
                        for gate in (0, 1)],
              "limits": ["controlled SRAM flags, not observed timer or interrupt state",
                         "helper calls are standalone Thumb routines, without caller timing"]}
    args.output.write_text(json.dumps(result, indent=2)+"\n", encoding="utf-8")


if __name__ == "__main__":
    main()
