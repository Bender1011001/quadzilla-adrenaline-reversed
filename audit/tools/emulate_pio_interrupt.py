#!/usr/bin/env python3
"""Execute bounded PIO/AIC paths against synthetic registers, never hardware."""
import argparse
import hashlib
import json
import struct
from pathlib import Path

from audit_aid_tables import AidRunner, SHA


class PeripheralRunner(AidRunner):
    def __init__(self, raw):
        super().__init__(raw)
        self.cpu.mem_map(0xFFFA0000, 0x4000)
        self.cpu.mem_map(0xFFFFF000, 0x1000)
        self.writes = []
        self.cpu.hook_add(self.uc.UC_HOOK_MEM_WRITE, self.record)

    def record(self, cpu, access, address, size, value, user):
        if address >= 0xFFFA0000 or address in (0x200791, 0x20079C):
            self.writes.append({"site": hex(cpu.reg_read(self.arm.UC_ARM_REG_PC)),
                                "address": hex(address), "size": size,
                                "value": hex(value & ((1 << (size*8))-1))})

    def prepare(self, lo, hi):
        self.reset()
        self.allowed_ranges = ((lo, hi),)
        self.visited.clear()
        self.writes.clear()
        self.cpu.mem_write(0xFFFFF000, bytes(0x1000))
        self.cpu.mem_write(0xFFFA0000, bytes(0x4000))


def prefix(runner, pdsr):
    runner.prepare(0x74E8, 0x757A)
    runner.cpu.mem_write(0xFFFFF43C, struct.pack("<I", pdsr))
    runner.cpu.emu_start(0x74E9, 0x757A, count=1000)
    if runner.cpu.reg_read(runner.arm.UC_ARM_REG_PC) != 0x757A:
        raise RuntimeError("initialization prefix did not stop before callees")
    return {"synthetic_pio_pdsr": hex(pdsr), "ram_200791": runner.cpu.mem_read(0x200791, 1)[0],
            "mmio_writes": [w for w in runner.writes if int(w["address"], 0) >= 0xFFFA0000],
            "visited": [hex(a) for a in sorted(runner.visited)]}


def handler(runner, pin30, first_flag, second_flag):
    runner.prepare(0x7448, 0x7486)
    runner.cpu.mem_write(0xFFFFF43C, struct.pack("<I", pin30 << 30))
    runner.cpu.mem_write(0x200788, bytes((first_flag, second_flag)))
    outcome = runner.call(0x7448, [])
    if outcome["status"] != "returned":
        raise RuntimeError(outcome)
    return {"pin30_high": bool(pin30), "ram_200788": first_flag, "ram_200789": second_flag,
            "mmio_writes": runner.writes.copy(), "visited": [hex(a) for a in sorted(runner.visited)]}


def mask_helpers(runner):
    runner.prepare(0x7498, 0x74B2)
    runner.cpu.mem_write(0xFFFFF110, struct.pack("<I", 0x12345678))
    first = runner.call(0x7498, [])
    if first["status"] != "returned":
        raise RuntimeError(first)
    saved = struct.unpack("<I", runner.cpu.mem_read(0x20079C, 4))[0]
    disable_writes = runner.writes.copy()
    runner.allowed_ranges = ((0x74B4, 0x74C2),)
    runner.visited.clear()
    runner.writes.clear()
    second = runner.call(0x74B4, [])
    if second["status"] != "returned":
        raise RuntimeError(second)
    return {"synthetic_aic_imr": "0x12345678", "saved_ram_20079c": hex(saved),
            "save_and_disable_writes": disable_writes,
            "restore_writes": runner.writes.copy()}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("image", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    raw = args.image.read_bytes()
    if hashlib.sha256(raw).hexdigest() != SHA:
        raise ValueError("unexpected application image")
    aic_base = struct.unpack_from("<I", raw, 0x9E80 - 0x4000)[0]
    vector = struct.unpack_from("<I", raw, 0x75DC - 0x4000)[0]
    if aic_base != 0xFFFFF000 or vector != 0x7449:
        raise ValueError("AIC base or Thumb vector literal changed")
    runner = PeripheralRunner(raw)
    result = {"format": "quadzilla-pio-interrupt-emulation-v1", "raw_sha256": SHA,
              "emulator": "Unicorn " + runner.uc.__version__,
              "cpu": "ARM926 functional surrogate", "registers": "synthetic read/write memory, no peripheral model",
              "source_literals": {"aic_base_source": "0x9e80", "aic_base": hex(aic_base),
                                  "thumb_vector_literal": "0x75dc", "thumb_vector": hex(vector)},
              "initialization_prefix": [prefix(runner, 0), prefix(runner, 1 << 17)],
              "pio_handler": [handler(runner, p, a, b) for p, a, b in
                              ((1, 1, 1), (0, 0, 1), (0, 1, 0), (0, 1, 1))],
              "aic_mask_helpers": mask_helpers(runner),
              "limits": ["0x74E8 is stopped before its first BL; six subordinate routines need separate review",
                         "synthetic MMIO has no register side effects or timing",
                         "handler is called as a bounded Thumb routine, not through a simulated IRQ controller",
                         "installed device part suffix and pin wiring are unmeasured"]}
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
