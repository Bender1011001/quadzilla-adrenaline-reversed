#!/usr/bin/env python3
"""Bounded original-byte review of 0x46D0; no device or peripheral I/O."""
import argparse
import hashlib
import json
import struct
from pathlib import Path

from audit_aid_tables import AidRunner, SHA


class ScoreRunner(AidRunner):
    def __init__(self, raw):
        super().__init__(raw)
        self.allowed_ranges += ((0x46D0, 0x4790), (0x8678, 0x896C),
                                (0x8970, 0x96C4), (0x56FC, 0x5700),
                                (0x5F04, 0x5F08), (0x5F0C, 0x5F10),
                                (0x7140, 0x7144), (0x7148, 0x714C),
                                (0x7160, 0x7164))
        self.candidates = []
        self.cpu.hook_add(self.uc.UC_HOOK_CODE, self.capture)

    def capture(self, cpu, address, size, user):
        if address == 0x476C:
            raw = cpu.reg_read(self.arm.UC_ARM_REG_R0)
            value = raw if raw < 0x80000000 else raw - 0x100000000
            self.candidates.append({"index": cpu.reg_read(self.arm.UC_ARM_REG_R5),
                                    "converted_s32": value, "stored_byte": raw & 255})

    def sample(self, word_input, byte_input, transmission=0, axle=4, circumference=95.6):
        self.reset()
        self.candidates = []
        self.cpu.mem_write(0x2006E6, bytes((transmission, axle)))
        self.cpu.mem_write(0x2006E8, struct.pack("<f", circumference))
        result = self.call(0x46D0, (word_input, byte_input))
        if result["status"] != "returned":
            raise RuntimeError(result)
        return {"word_input": word_input, "byte_input": byte_input,
                "transmission": transmission, "axle": axle,
                "circumference_bits": hex(struct.unpack("<I", struct.pack("<f", circumference))[0]),
                "return_score": result["r0"],
                "selection_byte_200bd0": self.cpu.mem_read(0x200BD0, 1)[0],
                "candidates": self.candidates.copy()}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("image", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    raw = args.image.read_bytes()
    if hashlib.sha256(raw).hexdigest() != SHA:
        raise ValueError("unexpected application image")
    start = 0x9F88 - 0x4000
    rows = []
    for n in range(3):
        base = start + n*28
        count = struct.unpack_from("<I", raw, base)[0]
        rows.append({"selector": n, "count": count,
                     "ratio_bits": [hex(struct.unpack_from("<I", raw, base+4+4*i)[0]) for i in range(count)]})
    axle_bits = [hex(struct.unpack_from("<I", raw, start+0x54+4*i)[0]) for i in range(5)]
    init = 0x96E8-0x4000+0x6E6
    runner = ScoreRunner(raw)
    cases = [(1200, 0), (1200, 5), (1200, 60), (500, 1), (1000, 1),
             (500, 3), (3000, 4), (4000, 3)]
    result = {"format": "quadzilla-drivetrain-score-v1", "raw_sha256": SHA,
              "entry": "0x46d0", "cpu": "ARM926 functional surrogate",
              "source_table": "0x9f88", "transmission_rows": rows,
              "axle_ratio_bits": axle_bits,
              "startup_default": {"at": "0x2006e6", "source": hex(0x96E8+0x6E6),
                                  "bytes": raw[init:init+6].hex()},
              "cases": [runner.sample(a, b) for a, b in cases],
              "limits": ["The semantic units of the two caller inputs require upstream trace review.",
                         "AID 226 validates selector bytes in its write case; alternate RAM writers are not excluded.",
                         "No device, live input range, peripheral timing, or output consequence measured."]}
    args.output.write_text(json.dumps(result, indent=2)+"\n", encoding="utf-8")


if __name__ == "__main__":
    main()
