#!/usr/bin/env python3
"""Exercise the original-byte 0x760c initial state selector offline."""
import argparse
import hashlib
import json
import struct
from pathlib import Path

from audit_aid_tables import AidRunner, SHA


class InitialStateRunner(AidRunner):
    def __init__(self, raw):
        super().__init__(raw)
        self.allowed_ranges = ((0x760C, 0x7698),)
        self.cpu.mem_map(0xFFFFF000, 0x1000)
        self.writes = []
        self.cpu.hook_add(self.uc.UC_HOOK_MEM_WRITE, self.record_write)

    def record_write(self, cpu, access, address, size, value, user):
        if 0x200000 <= address < 0x201000:
            self.writes.append({"pc": hex(cpu.reg_read(self.arm.UC_ARM_REG_PC)),
                                "address": hex(address), "size": size,
                                "value": hex(value & ((1 << (size * 8)) - 1))})

    def sample(self, label, mode, pin28, enabled=0, duration=180, comparison=0,
               saved_word=0x12345678):
        self.reset()
        self.cpu.mem_write(0xFFFFF000, bytes(0x1000))
        self.cpu.mem_write(0xFFFFF43C, (pin28 << 28).to_bytes(4, "little"))
        self.cpu.mem_write(0x2006ED, bytes([mode]))
        self.cpu.mem_write(0x2006DE, bytes([enabled]))
        self.cpu.mem_write(0x2006E0, struct.pack("<H", duration))
        self.cpu.mem_write(0x2008A8, struct.pack("<I", comparison))
        self.cpu.mem_write(0x2006F0, struct.pack("<I", saved_word))
        self.writes.clear()
        self.visited.clear()
        preserved = {name: self.cpu.reg_read(getattr(self.arm, "UC_ARM_REG_" + name))
                     for name in ("R4", "R5", "R6", "R7")}
        try:
            self.cpu.emu_start(0x760D, 0x3F00, count=256)
        except self.uc.UcError as exc:
            raise RuntimeError((label, self.fault, str(exc))) from exc
        if self.cpu.reg_read(self.arm.UC_ARM_REG_PC) != 0x3F00:
            raise ValueError(f"{label}: did not return")
        if self.cpu.reg_read(self.arm.UC_ARM_REG_SP) != 0x203000:
            raise ValueError(f"{label}: unbalanced stack")
        if any(self.cpu.reg_read(getattr(self.arm, "UC_ARM_REG_" + name)) != value
               for name, value in preserved.items()):
            raise ValueError(f"{label}: R4-R7 not preserved")
        return {"label": label, "mode": mode, "pin28": pin28,
                "enabled": enabled, "duration": duration, "comparison": comparison,
                "saved_word": hex(saved_word),
                "return_r0": self.cpu.reg_read(self.arm.UC_ARM_REG_R0),
                "writes": self.writes.copy(),
                "visited": [hex(address) for address in sorted(self.visited)]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("image", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    raw = args.image.read_bytes()
    if len(raw) != 32000 or hashlib.sha256(raw).hexdigest() != SHA:
        raise ValueError("unexpected firmware image")
    runner = InitialStateRunner(raw)
    cases = [
        ("default_pin_low", 4, 0),
        ("default_pin_high", 4, 1),
        ("mode1_pin_low", 1, 0),
        ("mode1_pin_high", 1, 1),
        ("mode2_enabled", 2, 0, 1, 180, 200),
        ("mode2_disabled_below", 2, 0, 0, 180, 200),
        ("mode2_disabled_equal", 2, 0, 0, 180, 180),
        ("mode2_disabled_above", 2, 1, 0, 180, 100),
        ("mode3_pin_low", 3, 0),
        ("mode3_pin_high", 3, 1),
        ("mode0_pin_low", 0, 0),
        ("mode255_pin_high", 255, 1),
    ]
    rows = [runner.sample(*case) for case in cases]
    seen = {int(address, 0) for row in rows for address in row["visited"]}
    result = {"format": "quadzilla-initial-state-emulation-v1", "raw_sha256": SHA,
              "entry": "0x760c", "bounds": ["0x760c", "0x7698"],
              "cpu": "ARM926 functional surrogate", "emulator": "Unicorn " + runner.uc.__version__,
              "cases": rows, "visited_starts": [hex(x) for x in sorted(seen)],
              "limits": ["PIOA status is synthetic memory; command-register and interrupt effects are not simulated",
                         "state inputs are supplied RAM values, not measured board observations",
                         "single helper calls do not establish later main-loop timing"]}
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print([(row["label"], row["return_r0"], len(row["writes"])) for row in rows])


if __name__ == "__main__":
    main()
