#!/usr/bin/env python3
"""Bounded execution of ARM soft-float routines and their Thumb wrappers.

Reference differences are research output, not hidden or converted into passing
conformance claims. Exit success means the execution harness completed.
"""
import argparse
import hashlib
import itertools
import json
import random
import struct
import sys
from pathlib import Path

from audit_aid_tables import AidRunner, SHA
from build_integer_callers import extract_calls

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
from model_soft_float import binary, category, convert, encode, rational, to_integer
from fractions import Fraction

# wrapper: (ARM target, pointer literal, end of Thumb instructions)
THUNKS = {0x56FC: (0x92CC, 0x5700, 0x5700), 0x5704: (0x893C, 0x5710, 0x570E),
          0x5714: (0x90E4, 0x5718, 0x5718), 0x5F04: (0x913C, 0x5F08, 0x5F08),
          0x5F0C: (0x8788, 0x5F10, 0x5F10), 0x6B08: (0x86F0, 0x6B0C, 0x6B0C),
          0x6B10: (0x89B0, 0x6B1C, 0x6B1A), 0x7120: (0x86D8, 0x7124, 0x7124),
          0x7128: (0x89C8, 0x7134, 0x7132), 0x7138: (0x87E8, 0x713C, 0x713C),
          0x7140: (0x9038, 0x7144, 0x7144), 0x7148: (0x95F4, 0x714C, 0x714C),
          0x7150: (0x90B0, 0x7154, 0x7154), 0x7158: (0x874C, 0x715C, 0x715C),
          0x7160: (0x88A4, 0x7164, 0x7164), 0x7168: (0x8EF4, 0x7174, 0x7172)}


class FloatRunner(AidRunner):
    def __init__(self, raw):
        super().__init__(raw)
        self.allowed_ranges = ((0x8678, 0x896C), (0x8970, 0x96C4)) + tuple(
            (entry, end) for entry, (_, _, end) in THUNKS.items())
        self.cpu.hook_add(self.uc.UC_HOOK_MEM_WRITE, self.write)

    def write(self, cpu, access, address, size, value, user):
        if not (0x202E00 <= address and address+size <= 0x203000) and (address, size) != (0x200AF8, 1):
            raise RuntimeError(f"unexpected write at {address:#x}")

    def run(self, entry, registers, thumb=False, internal=False):
        self.reset()
        self.visited.clear()
        for i in range(4, 12):
            self.cpu.reg_write(getattr(self.arm, f"UC_ARM_REG_R{i}"), 0x12340000+i)
        for i, value in registers.items():
            self.cpu.reg_write(getattr(self.arm, f"UC_ARM_REG_R{i}"), value)
        self.cpu.emu_start(entry | int(thumb), 0x3F00, count=16384)
        if self.cpu.reg_read(self.arm.UC_ARM_REG_PC) != 0x3F00 or self.cpu.reg_read(self.arm.UC_ARM_REG_SP) != 0x203000:
            raise RuntimeError("helper failed to return with balanced stack")
        if not internal:
            for i in range(4, 12):
                if self.cpu.reg_read(getattr(self.arm, f"UC_ARM_REG_R{i}")) != registers.get(i, 0x12340000+i):
                    raise RuntimeError(f"R{i} not preserved")
        return {"registers": [self.cpu.reg_read(getattr(self.arm, f"UC_ARM_REG_R{i}")) for i in range(13)],
                "nzcv": self.cpu.reg_read(self.arm.UC_ARM_REG_CPSR) >> 28,
                "status_byte_af8": self.cpu.mem_read(0x200AF8, 1)[0]}


def words(bits, width, offset=0):
    result = {offset: bits & 0xFFFFFFFF}
    if width == 64:
        result[offset+1] = bits >> 32
    return result


def bits_from_result(result, width):
    regs = result["registers"]
    return regs[0] | ((regs[1] << 32) if width == 64 else 0)


def edges(width):
    fb, eb = (23, 8) if width == 32 else (52, 11)
    bias = (1 << (eb-1))-1
    positive = [0, 1, (1 << fb)-1, 1 << fb, (1 << fb)+1,
                (bias-1) << fb, bias << fb, (bias << fb)+1, (bias+1) << fb,
                (((1 << eb)-1) << fb)-1, ((1 << eb)-1) << fb,
                (((1 << eb)-1) << fb)+(1 << (fb-1)), (((1 << eb)-1) << fb)+1]
    return positive+[value | (1 << (width-1)) for value in positive]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("image", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    raw = args.image.read_bytes()
    if hashlib.sha256(raw).hexdigest() != SHA:
        raise ValueError("unexpected source image")
    runner = FloatRunner(raw)
    for target, literal, _ in THUNKS.values():
        if struct.unpack_from("<I", raw, literal-0x4000)[0] != target:
            raise ValueError("wrapper literal does not match ARM target")
    rng = random.Random(0x8678)
    suites = []
    by_target = {target: entry for entry, (target, _, _) in THUNKS.items()}

    def suite(entry, contract, cases, reference, output_width, examples_limit=18):
        variants = [(entry, False)] + ([(by_target[entry], True)] if entry in by_target else [])
        for start, thumb in variants:
            mismatches, examples, visited = [], [], set()
            mismatch_count = 0
            for number, (inputs, registers) in enumerate(cases):
                actual = runner.run(start, registers, thumb)
                expected = reference(inputs)
                bits = bits_from_result(actual, output_width)
                okay = category(bits, output_width) == "nan" if expected is None else bits == expected
                if not okay:
                    mismatch_count += 1
                    if len(mismatches) < 128:
                        mismatches.append({"inputs": inputs, "actual": hex(bits), "expected": None if expected is None else hex(expected)})
                visited.update(runner.visited)
                if number < examples_limit or (actual["status_byte_af8"] and len(examples) < examples_limit+8):
                    examples.append({"inputs": [hex(v) for v in inputs], "output_bits": hex(bits),
                                     "nzcv": actual["nzcv"], "status_byte_af8": actual["status_byte_af8"]})
            suites.append({"entry": hex(start), "isa": "thumb" if thumb else "arm", "arm_target": hex(entry),
                           "contract": contract, "cases": len(cases), "mismatch_count": mismatch_count,
                           "mismatches": mismatches, "examples": examples,
                           "visited_addresses": [hex(v) for v in sorted(visited)]})
            print(f"{start:#x} {contract}: {len(cases)} cases, {mismatch_count} reference differences", flush=True)

    for entry, operation, width in ((0x913C, "mul", 32), (0x92CC, "div", 32),
                                    (0x95F4, "add", 32), (0x94B4, "sub", 32),
                                    (0x89C8, "div", 64), (0x8EF4, "add", 64), (0x8CFC, "sub", 64)):
        pairs = list(itertools.product(edges(width), repeat=2))
        pairs += [(rng.getrandbits(width), rng.getrandbits(width)) for _ in range(512)]
        cases = [([a, b], words(a, width) | words(b, width, 2 if width == 64 else 1)) for a, b in pairs]
        suite(entry, f"f{width}_{operation}", cases, lambda v, op=operation, w=width: binary(op, *v, w), width)

    integer_inputs = [0, 1, 2, 0xFFFFFF, 0x1000000, 0x1000001, 0x1000003, 0x7FFFFFFF, 0x80000000, 0xFFFFFFFF]
    integer_inputs += [rng.getrandbits(32) for _ in range(512)]
    for entry, signed, width in ((0x86D8, False, 64), (0x86F0, True, 64),
                                  (0x9038, False, 32), (0x9048, True, 32)):
        def expected(v, signed=signed, width=width):
            value = v[0]-(1 << 32) if signed and v[0] >= 0x80000000 else v[0]
            return encode(Fraction(value), width)
        suite(entry, f"{'s' if signed else 'u'}32_to_f{width}", [([v], {0: v}) for v in integer_inputs], expected, width)

    for entry, source, target in ((0x87E8, 64, 32), (0x88A4, 32, 64)):
        values = edges(source)+[rng.getrandbits(source) for _ in range(512)]
        suite(entry, f"f{source}_to_f{target}", [([v], words(v, source)) for v in values],
              lambda v, s=source, t=target: convert(v[0], s, t), target)

    for entry, width, signed in ((0x874C, 64, False), (0x8788, 64, True),
                                  (0x90B0, 32, False), (0x90E4, 32, True)):
        values = edges(width)+[rng.getrandbits(width) for _ in range(512)]
        values += [encode(Fraction(v), width) for v in (-0x100000001, -0x80000001, -0x80000000, -1, 0x7FFFFFFF, 0x80000000, 0xFFFFFFFF, 0x100000000)]
        suite(entry, f"f{width}_to_{'s' if signed else 'u'}32_saturating", [([v], words(v, width)) for v in values],
              lambda v, w=width, s=signed: to_integer(v[0], w, s), 32)

    def compare(v, operation):
        a, b = v
        if "nan" in (category(a, 64), category(b, 64)):
            return int(operation == "ne")
        def value(bits):
            if category(bits, 64) == "infinity":
                return float("-inf") if bits >> 63 else float("inf")
            return rational(bits, 64)
        return int(value(a) != value(b)) if operation == "ne" else int(value(a) >= value(b))
    pairs = list(itertools.product(edges(64), repeat=2))
    pairs += [(rng.getrandbits(64), rng.getrandbits(64)) for _ in range(512)]
    for entry, operation in ((0x893C, "ne"), (0x89B0, "ge")):
        suite(entry, "f64_compare_"+operation, [([a, b], words(a, 64) | words(b, 64, 2)) for a, b in pairs],
              lambda v, op=operation: compare(v, op), 32, 32)

    normalization = []
    for entry, offset, count_register in ((0x8678, 0, 12), (0x86A8, 2, 5)):
        count, visited, examples = 0, set(), []
        for mantissa in [1 << n for n in range(52)]+[rng.randrange(1, 1 << 52) for _ in range(128)]:
            for r7 in (0, 1, 0x80000000, 0xFFFFFFFF):
                registers = words(mantissa, 64, offset) | {7: r7}
                actual = runner.run(entry, registers, internal=True)
                shift = 53-mantissa.bit_length()
                regs = actual["registers"]
                observed = regs[offset] | (regs[offset+1] << 32)
                if observed != mantissa << shift or regs[count_register] != (1-shift) & 0xFFFFFFFF or regs[7] != (2*r7) & 0xFFFFFFFF:
                    raise RuntimeError("internal normalization contract mismatch")
                visited.update(runner.visited)
                count += 1
                if len(examples) < 8:
                    examples.append({"mantissa": hex(mantissa), "r7_input": hex(r7), "shift": shift,
                                     "normalized": hex(observed), "exponent_adjustment": hex(regs[count_register]), "r7_output": hex(regs[7])})
        normalization.append({"entry": hex(entry), "cases": count, "mismatches": [], "examples": examples,
                              "visited_addresses": [hex(v) for v in sorted(visited)]})

    influences = []
    for r4 in (0, 0x80000000, 0x12340004, 0x200424, 0xFFFFFFFF):
        a, b = 1, 0x10000000000000
        actual = runner.run(0x8EF4, words(a, 64) | words(b, 64, 2) | {4: r4})
        influences.append({"entry": "0x8ef4", "a": hex(a), "b": hex(b), "initial_r4": hex(r4),
                           "output_bits": hex(bits_from_result(actual, 64)), "reference_bits": hex(binary("add", a, b, 64))})

    branches = []
    for start, end in ((0x8678, 0x896C), (0x8970, 0x96C4)):
        for address in range(start, end, 4):
            word = struct.unpack_from("<I", raw, address-0x4000)[0]
            if (word >> 25) & 7 == 5:
                offset = (word & 0xFFFFFF) << 2
                if offset & 0x2000000:
                    offset -= 0x4000000
                branches.append({"site": hex(address), "target": hex(address+8+offset),
                                 "link": bool(word & 0x1000000), "condition": word >> 28})
    item_export = json.loads((ROOT / "audit/data/ida_image_items.json").read_text(encoding="utf-8"))
    if item_export["raw_sha256"] != SHA:
        raise ValueError("caller export source mismatch")

    result = {"format": "quadzilla-soft-float-emulation-v1", "raw_sha256": SHA,
              "emulator": "Unicorn "+runner.uc.__version__, "cpu": "ARM926 functional surrogate", "seed": "0x8678",
              "reference": "exact Fraction arithmetic rounded nearest, ties to even; NaN arithmetic compared by category only; integer conversions use documented saturation policy",
              "thunks": [{"entry": hex(e), "target": hex(t), "literal": hex(p), "instruction_end": hex(end)} for e, (t, p, end) in THUNKS.items()],
              "total_calls": sum(s["cases"] for s in suites)+sum(s["cases"] for s in normalization)+len(influences),
              "suites": suites, "internal_normalization": normalization, "caller_r4_influence": influences,
              "arm_branch_edges": branches, "thumb_direct_callers": extract_calls(item_export, {hex(e) for e in THUNKS}),
              "all_reference_comparisons_match": not any(s["mismatch_count"] for s in suites),
              "checks": ["R4..R11 and SP preserved for public calls", "execution bounded to ARM region and Thumb wrapper instructions", "writes limited to stack and status byte 0x200AF8"],
              "limits": ["bounded operand samples, not complete IEEE 754 conformance", "NaN payload/quieting policy is not equated by category checks", "no device, peripheral, timing or live reachability validation"]}
    args.output.write_text(json.dumps(result, indent=2)+"\n", encoding="utf-8")


if __name__ == "__main__":
    main()
