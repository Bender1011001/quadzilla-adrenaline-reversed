#!/usr/bin/env python3
"""Bound the startup persisted-configuration copy before its response mirror."""
import argparse
import hashlib
import json
from pathlib import Path

from audit_aid_tables import AidRunner, SHA


class RestoreRunner(AidRunner):
    def __init__(self, raw):
        super().__init__(raw)
        self.allowed_ranges = ((0x5F14, 0x5F2E), (0x8530, 0x854A))
        self.cpu.mem_map(0x10F000, 0x1000)
        self.stop_reason = None
        self.writes = []
        self.cpu.hook_add(self.uc.UC_HOOK_CODE, self.boundary)
        self.cpu.hook_add(self.uc.UC_HOOK_MEM_WRITE, self.record_write)

    def boundary(self, cpu, address, size, user):
        if address == 0x5F26:
            self.stop_reason = "before_response_mirror_0x5f34"
            cpu.emu_stop()

    def record_write(self, cpu, access, address, size, value, user):
        if 0x2006CC <= address < 0x2006F8:
            self.writes.append({"pc": hex(cpu.reg_read(self.arm.UC_ARM_REG_PC)),
                                "address": hex(address), "size": size,
                                "value": hex(value & ((1 << (size * 8)) - 1))})

    def sample(self, label, flash_magic):
        self.reset()
        source = bytes([flash_magic]) + bytes((i * 7 + 3) & 0xFF for i in range(1, 44))
        self.cpu.mem_write(0x10F000, bytes(0x1000))
        self.cpu.mem_write(0x10FF00, source)
        before = bytes(self.cpu.mem_read(0x2006CC, 44))
        self.stop_reason = None
        self.visited.clear()
        self.writes.clear()
        try:
            self.cpu.emu_start(0x5F15, 0x3F00, count=512)
        except self.uc.UcError as exc:
            raise RuntimeError((label, self.fault, str(exc))) from exc
        if self.stop_reason != "before_response_mirror_0x5f34":
            raise ValueError(f"{label}: unexpected stop {self.stop_reason}, "
                             f"pc={self.cpu.reg_read(self.arm.UC_ARM_REG_PC):#x}, "
                             f"last={sorted(self.visited)[-8:]}")
        after = bytes(self.cpu.mem_read(0x2006CC, 44))
        if after != (source if flash_magic == 0xA5 else before):
            raise ValueError(f"{label}: copied data mismatch")
        return {"label": label, "flash_magic": hex(flash_magic),
                "copied": flash_magic == 0xA5,
                "source_sha256": hashlib.sha256(source).hexdigest(),
                "before_mode_byte": before[0x21], "source_mode_byte": source[0x21],
                "after_mode_byte": after[0x21], "config_writes": self.writes.copy(),
                "visited": [hex(address) for address in sorted(self.visited)]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("image", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    raw = args.image.read_bytes()
    if len(raw) != 32000 or hashlib.sha256(raw).hexdigest() != SHA:
        raise ValueError("unexpected firmware image")
    runner = RestoreRunner(raw)
    rows = [runner.sample("magic_absent", 0x00), runner.sample("magic_present", 0xA5)]
    result = {"format": "quadzilla-config-restore-emulation-v1", "raw_sha256": SHA,
              "cpu": "ARM926 functional surrogate", "emulator": "Unicorn " + runner.uc.__version__,
              "entry": "0x5f14", "copy_helper": "0x8530", "source": "0x10ff00",
              "destination": "0x2006cc", "length": 44,
              "cases": rows,
              "visited_starts": [hex(a) for a in sorted({int(a, 0) for row in rows for a in row["visited"]})],
              "limits": ["0x10ff00 is synthetic mapped memory, not device flash",
                         "stops before the distinct response mirror at 0x5f34",
                         "magic-byte acceptance does not prove configuration authenticity or integrity"]}
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print([(row["label"], row["copied"], row["before_mode_byte"],
            row["after_mode_byte"], len(row["visited"])) for row in rows])


if __name__ == "__main__":
    main()
