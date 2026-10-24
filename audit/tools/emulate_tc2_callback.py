#!/usr/bin/env python3
"""Exercise exact TC2 callback bytes with controlled SRAM and synthetic MMIO."""
import argparse
import hashlib
import json
import struct
import sys
from fractions import Fraction
from pathlib import Path

from audit_aid_tables import AidRunner, SHA

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "tools"))
from model_soft_float import binary, convert, encode, to_integer


A = 0x200708
B = 0x200AD0


class CallbackRunner(AidRunner):
    def __init__(self, raw):
        super().__init__(raw)
        self.allowed_ranges = ((0x6C94, 0x6F56), (0x7F28, 0x7F58),
                               (0x7120, 0x7172), (0x8678, 0x96C4))
        self.cpu.mem_map(0xFFFA0000, 0x4000)
        self.cpu.mem_map(0xFFFFF000, 0x1000)
        self.writes = []
        self.reads = []
        self.model_aic_enable = False
        self.cpu.hook_add(self.uc.UC_HOOK_MEM_WRITE, self.record_write)
        self.cpu.hook_add(self.uc.UC_HOOK_MEM_READ, self.record_read)

    def record_write(self, cpu, access, address, size, value, user):
        if (A <= address < A+0x80 or 0x2007C8 <= address < 0x2007E0 or
                B <= address < B+0x1C or
                address in (0x200474, 0x200792, 0x200AF8, 0x200BC3) or address >= 0xFFFA0000):
            self.writes.append({"site": hex(cpu.reg_read(self.arm.UC_ARM_REG_PC)),
                                "address": hex(address), "size": size,
                                "value": hex(value & ((1 << (8*size))-1))})
            if self.model_aic_enable and address == 0xFFFFF120 and value == 4:
                cpu.mem_write(0xFFFFF110, struct.pack("<I", 4))

    def record_read(self, cpu, access, address, size, value, user):
        if address >= 0xFFFA0000:
            self.reads.append({"site": hex(cpu.reg_read(self.arm.UC_ARM_REG_PC)),
                               "address": hex(address), "size": size})

    def sample(self, name, bytes_at=(), words_at=(), aic_initial_mask=4,
               model_aic_enable=False):
        self.reset()
        self.cpu.mem_write(0xFFFA0000, bytes(0x4000))
        self.cpu.mem_write(0xFFFFF000, bytes(0x1000))
        self.cpu.mem_write(0xFFFFF110, struct.pack("<I", aic_initial_mask))
        self.model_aic_enable = model_aic_enable
        self.cpu.mem_write(A, bytes(0x80))
        self.cpu.mem_write(B, bytes(0x1C))
        self.cpu.mem_write(0x2007C8, bytes(0x18))
        self.cpu.mem_write(0x200474, bytes(4))
        self.cpu.mem_write(0x200792, bytes(1))
        self.cpu.mem_write(0x200BC3, bytes(1))
        self.cpu.mem_write(A+0x20, struct.pack("<I", 0xFFFA0080))
        for address, value in bytes_at:
            self.cpu.mem_write(address, bytes([value]))
        for address, value in words_at:
            self.cpu.mem_write(address, struct.pack("<I", value))
        self.writes.clear()
        self.reads.clear()
        self.visited.clear()
        preserved = []
        for n in range(4, 8):
            reg = getattr(self.arm, f"UC_ARM_REG_R{n}")
            value = 0x12340000+n
            self.cpu.reg_write(reg, value)
            preserved.append((reg, value))
        try:
            self.cpu.emu_start(0x6C95, 0x3F00, count=100000)
        except self.uc.UcError as exc:
            raise RuntimeError(f"{name}: {exc}; invalid={self.fault}") from exc
        if self.cpu.reg_read(self.arm.UC_ARM_REG_PC) != 0x3F00:
            raise RuntimeError(f"{name}: callback did not return")
        if self.cpu.reg_read(self.arm.UC_ARM_REG_SP) != 0x203000:
            raise RuntimeError(f"{name}: unbalanced stack")
        if any(self.cpu.reg_read(reg) != value for reg, value in preserved):
            raise RuntimeError(f"{name}: R4-R7 not preserved")
        return {"name": name, "bytes_at": [[hex(a), hex(v)] for a, v in bytes_at],
                "words_at": [[hex(a), hex(v)] for a, v in words_at],
                "aic_initial_mask": hex(aic_initial_mask),
                "modeled_aic_enable_command": model_aic_enable,
                "callee_saved_r4_r7_preserved": True,
                "status_byte_af8": hex(self.cpu.mem_read(0x200AF8, 1)[0]),
                "writes": self.writes.copy(), "peripheral_reads": self.reads.copy(),
                "callback_visited": [hex(a) for a in sorted(self.visited)
                                     if 0x6C94 <= a < 0x6F56],
                "helpers_visited": [hex(a) for a in sorted(self.visited)
                                    if 0x7F28 <= a < 0x7F58],
                "numeric_wrapper_entries_visited": [hex(a) for a in
                    (0x7120, 0x7128, 0x7138, 0x7140, 0x7148,
                     0x7150, 0x7158, 0x7160, 0x7168) if a in self.visited]}


def numeric_reference(value, byte, old_integer, old_float, old_sum):
    """Independent exact-rational arithmetic following the reviewed call sequence."""
    x = convert(binary("div", encode(Fraction(value), 64), 0x404E000000000000, 64), 64, 32)
    total = to_integer(binary("add", encode(Fraction(old_integer), 32), x, 32), 32, False)
    scaled = to_integer(binary("div", encode(Fraction(total), 64), 0x40E27BC333333333, 64), 64, False)
    increment = binary("div", convert(x, 32, 64), 0x414CE16100000000, 64)
    accumulated = convert(binary("add", convert(old_float, 32, 64), increment, 64), 64, 32)
    y = convert(binary("div", encode(Fraction(byte), 64), 0x4042000000000000, 64), 64, 32)
    return {"0x200740": hex(x), "0x20073c": hex(total), "0x200738": hex(scaled),
            "0x20074c": hex(accumulated), "0x200744": hex(y),
            "0x200748": hex(binary("add", old_sum, y, 32))}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("image", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    raw = args.image.read_bytes()
    if hashlib.sha256(raw).hexdigest() != SHA:
        raise ValueError("unexpected application image")
    literals = {hex(a): hex(struct.unpack_from("<I", raw, a-0x4000)[0])
                for a in range(0x6F58, 0x6FA0, 4)}
    runner = CallbackRunner(raw)
    cases = [runner.sample("baseline")]
    transitions = [
        ("a1", A+1, A+0x48, 101),
        ("a4", A+4, A+0x4C, 1001),
        ("a6", A+6, A+0x50, 1001),
        ("a8", A+8, A+0x54, 1001),
        ("ae", A+0xE, A+0x58, 501),
        ("a14", A+0x14, A+0x5C, 151),
        ("a17", A+0x17, A+0x60, 32),
        ("b0", B, A+0x64, 401),
        ("a1d", A+0x1D, A+0x68, 6),
        ("b3", B+3, A+0x6C, 3001),
        ("b6", B+6, A+0x70, 20001),
        ("b9", B+9, A+0x74, 4001),
        ("b0e", B+0xE, B+0x14, 50001),
    ]
    for name, flag, counter, threshold in transitions:
        cases.append(runner.sample(name, bytes_at=((flag, 1),),
                                   words_at=((counter, threshold),)))
        cases.append(runner.sample(name+"_below", bytes_at=((flag, 1),),
                                   words_at=((counter, threshold-1),)))
    cases.append(runner.sample("a1_wrap", bytes_at=((A+1, 1),),
                               words_at=((A+0x48, 0xFFFFFFFF),)))
    cases.append(runner.sample("a1d_enable_retry", bytes_at=((A+0x1D, 1),),
                               words_at=((A+0x68, 6),), aic_initial_mask=0,
                               model_aic_enable=True))
    reset_flags = [("a2", A+2), ("a5", A+5), ("a7", A+7),
                   ("a9", A+9), ("af", A+0xF), ("a15", A+0x15),
                   ("a18", A+0x18), ("b1", B+1), ("a1e", A+0x1E),
                   ("b4", B+4), ("b7", B+7), ("ba", B+0xA),
                   ("ac", A+0xC), ("a12", A+0x12), ("bf", B+0xF),
                   ("a0", A)]
    for name, flag in reset_flags:
        cases.append(runner.sample(name+"_reset", bytes_at=((flag, 1),)))
    cases.append(runner.sample("unconditional_b_d", words_at=((A+0x78, 1001),)))
    for name, flag, counter, threshold in (("a_b", A+0xB, A+0x2C, A+0x24),
                                           ("a_11", A+0x11, A+0x7C, A+0x28)):
        cases.append(runner.sample(name, bytes_at=((flag, 1),),
                                   words_at=((threshold, 4), (counter, 5))))
    cases.append(runner.sample("numeric_gate_off", words_at=((B+0x18, 10001),)))
    cases.append(runner.sample("numeric_gate_on", bytes_at=((0x200792, 1),
                                                            (0x200BC3, 72)),
                               words_at=((B+0x18, 10001), (0x200474, 600),
                                         (A+0x34, 5), (A+0x40, 0x3F000000),
                                         (A+0x44, 0x3F800000))))
    numeric_cases = []
    for i, value in enumerate((0, 1, 59, 60, 600, 0xFFFFFF, 0x1000001, 0xFFFFFFFF)):
        for j, byte in enumerate((0, 1, 255)):
            old_integer = (0, 5, 0xFFFFFFFE)[j]
            old_float = (0, 1, 0x3F800000, 0xBF800000)[(i+j) % 4]
            old_sum = (0, 0x3F000000, 0xBF800000)[j]
            case = runner.sample("numeric_reference", bytes_at=((0x200792, 1), (0x200BC3, byte)),
                                 words_at=((B+0x18, 10001), (0x200474, value),
                                           (A+0x34, old_integer), (A+0x44, old_float),
                                           (A+0x40, old_sum)))
            expected = numeric_reference(value, byte, old_integer, old_float, old_sum)
            written = {w["address"]: w["value"] for w in case["writes"]}
            actual = {a: written[a] for a in expected}
            numeric_cases.append({"inputs": [hex(x) for x in
                                  (value, byte, old_integer, old_float, old_sum)],
                                  "actual": actual, "expected": expected,
                                  "matches": actual == expected,
                                  "status_byte_af8": case["status_byte_af8"]})
    result = {"format": "quadzilla-tc2-callback-emulation-v1", "raw_sha256": SHA,
              "cpu": "ARM926 functional surrogate", "entry": "0x6c94",
              "source_literals": literals, "cases": cases,
              "numeric_reference_cases": numeric_cases,
              "numeric_reference_mismatches": sum(not c["matches"] for c in numeric_cases),
              "limits": ["TC registers are plain memory; AIC IECR-to-IMR update is modeled only in the explicitly marked retry case",
                         "single callback invocation per case, no IRQ wrapper or timing",
                         "controlled trigger and threshold states, not exhaustive state combinations",
                         "numeric reference suite is a finite sample, not universal soft-float correctness"]}
    args.output.write_text(json.dumps(result, indent=2)+"\n", encoding="utf-8")


if __name__ == "__main__":
    main()
