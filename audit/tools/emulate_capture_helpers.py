#!/usr/bin/env python3
"""Exercise capture request selection/rotation and byte comparison offline."""
import argparse
import hashlib
import itertools
import json
import struct
from pathlib import Path

from audit_aid_tables import SHA
from emulate_spi_transfers import TransferRunner, SPI, PIO_PDSR


class HelperRunner(TransferRunner):
    def __init__(self, raw):
        super().__init__(raw)
        self.allowed_ranges += ((0x5E04, 0x5EA0), (0x5EBC, 0x5EF2), (0x8504, 0x852E))
        self.mode = "ready"
        self.calls = []
        self.attempts = {}
        self.state_writes = []
        self.injected = []
        self.reset_requested = False

    def trace(self, cpu, address, size, user):
        super().trace(cpu, address, size, user)
        if address == 0x6B64:
            site = (cpu.reg_read(self.arm.UC_ARM_REG_LR) & ~1)-4
            number = self.attempts.get(site, 0)+1
            self.attempts[site] = number
            ready = self.mode == "ready" or (self.mode == "retry" and number > 1)
            cpu.mem_write(SPI+0x10, struct.pack("<I", 0x20 if ready else 0))
            self.calls.append({"site": hex(site), "attempt": number, "scripted_ready": ready,
                               "args": [hex(cpu.reg_read(getattr(self.arm, f"UC_ARM_REG_R{i}")))
                                        for i in range(3)]})
        if self.mode == "timeout" and address == 0x5E40 and not self.injected:
            cpu.mem_write(0x200AD5, b"\x01")
            self.injected.append({"site": hex(address), "address": "0x200ad5", "value": 1})

    def record_write(self, cpu, access, address, size, value, user):
        super().record_write(cpu, access, address, size, value, user)
        if address in (0x2005D1, 0x2005D2, 0x200AD0, 0x200AD1, 0x200AD2,
                       0x200AD3, 0x200AD4, 0x200AD5, 0x200AFC):
            self.state_writes.append({"site": hex(cpu.reg_read(self.arm.UC_ARM_REG_PC)),
                                      "address": hex(address), "size": size, "value": hex(value)})
        if address == 0xFFFFFD00:
            self.reset_requested = True
            cpu.emu_stop()

    def helper_case(self, entry, args=(), mode="ready", trigger=0, index=0):
        self.reset()
        self.cpu.mem_write(SPI, bytes(0x1000))
        self.cpu.mem_write(0xFFFFF000, bytes(0x1000))
        self.cpu.mem_write(PIO_PDSR, struct.pack("<I", 0x800))
        self.cpu.mem_write(0x200AD2, bytes([trigger]))
        self.cpu.mem_write(0x200AFC, bytes([index]))
        self.mode = mode
        self.calls.clear()
        self.attempts.clear()
        self.state_writes.clear()
        self.injected.clear()
        self.writes.clear()
        self.reads.clear()
        self.visited.clear()
        self.reset_requested = False
        preserved = []
        for n in range(4, 8):
            reg = getattr(self.arm, f"UC_ARM_REG_R{n}")
            value = 0x12340000+n
            self.cpu.reg_write(reg, value)
            preserved.append((reg, value))
        for n, value in enumerate(args):
            self.cpu.reg_write(getattr(self.arm, f"UC_ARM_REG_R{n}"), value)
        self.cpu.emu_start(entry | 1, 0x3F00, count=5000 if mode == "stall" else 20000)
        returned = self.cpu.reg_read(self.arm.UC_ARM_REG_PC) == 0x3F00
        if mode in ("ready", "retry"):
            if not returned or self.cpu.reg_read(self.arm.UC_ARM_REG_SP) != 0x203000:
                raise RuntimeError("helper failed to return with balanced stack")
            if any(self.cpu.reg_read(reg) != value for reg, value in preserved):
                raise RuntimeError("R4-R7 not preserved")
        if mode == "timeout" and not self.reset_requested:
            raise RuntimeError("timeout did not request reset")
        if mode == "stall" and (returned or self.reset_requested):
            raise RuntimeError("unready/no-timeout case unexpectedly terminated")
        return {"entry": hex(entry), "args": [hex(a) for a in args], "mode": mode,
                "trigger": trigger, "index_in": index,
                "index_out": self.cpu.mem_read(0x200AFC, 1)[0],
                "outcome": "reset_request_stop" if self.reset_requested else
                           "returned" if returned else "instruction_budget",
                "transfer_calls": self.calls.copy(), "external_flag_injections": self.injected.copy(),
                "state_writes": self.state_writes.copy(), "writes": self.writes.copy(),
                "visited": [hex(a) for a in sorted(self.visited)
                            if 0x5E04 <= a < 0x5EA0 or 0x5EBC <= a < 0x5EF2]}

    def comparison_suite(self):
        self.reset()
        self.visited.clear()
        mismatches = 0
        counts = {"-1": 0, "0": 0, "1": 0}
        digest = hashlib.sha256()
        for a, b in itertools.product(range(256), repeat=2):
            self.cpu.mem_write(0x201000, bytes([a]))
            self.cpu.mem_write(0x201040, bytes([b]))
            actual = self.call(0x8504, [0x201000, 0x201040, 1])["r0"]
            expected = (int(a > b)-int(a < b)) & 0xFFFFFFFF
            mismatches += actual != expected
            counts[str(-1 if actual == 0xFFFFFFFF else actual)] += 1
            digest.update(struct.pack("<I", actual))
        prefix_cases = []
        for length in (0, 1, 2, 4, 8, 16):
            a = bytes(range(length))
            variants = [(a, a)]
            for at in range(length):
                b = bytearray(a)
                b[at] ^= 1
                variants += [(a, bytes(b)), (bytes(b), a)]
            for left, right in variants:
                self.cpu.mem_write(0x201000, left or b"\x00")
                self.cpu.mem_write(0x201040, right or b"\x00")
                actual = self.call(0x8504, [0x201000, 0x201040, length])["r0"]
                expected = (int(left > right)-int(left < right)) & 0xFFFFFFFF
                mismatches += actual != expected
                prefix_cases.append({"left": left.hex(), "right": right.hex(), "length": length,
                                     "actual": hex(actual), "expected": hex(expected)})
        empty = self.call(0x8504, [0x300000, 0x400000, 0])
        if empty != {"status": "returned", "r0": 0}:
            raise RuntimeError("zero-length comparison dereferenced an input")
        return {"single_byte_cases": 65536, "result_counts": counts,
                "output_u32le_sha256": digest.hexdigest(), "prefix_cases": prefix_cases,
                "zero_length_unmapped_inputs": empty, "reference_mismatches": mismatches,
                "visited": [hex(a) for a in sorted(self.visited)]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("image", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    raw = args.image.read_bytes()
    if hashlib.sha256(raw).hexdigest() != SHA:
        raise ValueError("unexpected application image")
    runner = HelperRunner(raw)
    cases = [runner.helper_case(0x5E04, (mode, option, index))
             for index, mode, option in itertools.product(range(8), range(4), range(5))]
    cases += [runner.helper_case(0x5E04, (0, 0, 0xFFFFFFFF)),
              runner.helper_case(0x5E04, (0xFFFFFFFF, 0, 0)),
              runner.helper_case(0x5E04, (2, 0xFFFFFFFF, 0))]
    cases += [runner.helper_case(0x5E04, (0, 0, 0), mode=mode) for mode in ("retry", "timeout", "stall")]
    cases += [runner.helper_case(0x5EBC, trigger=trigger, index=index)
              for trigger, index in itertools.product((0, 1), (0, 6, 255))]
    result = {"format": "quadzilla-capture-helper-emulation-v1", "raw_sha256": SHA,
              "cpu": "ARM926 functional surrogate", "cases": cases,
              "literal_words": {hex(a): hex(struct.unpack_from("<I", raw, a-0x4000)[0])
                                for a in (*range(0x5EA0, 0x5EBC, 4), *range(0x5EF4, 0x5F04, 4))},
              "comparison": runner.comparison_suite(),
              "limits": ["SPI/PDC/PIO/RSTC are synthetic; no physical transfer or reset occurs",
                         "retry readiness and timeout flag are explicit scripted inputs",
                         "comparison coverage is exhaustive for one-byte values, not arbitrary address/count safety",
                         "no real interrupt timing or request/response semantics established"]}
    args.output.write_text(json.dumps(result, indent=2)+"\n", encoding="utf-8")


if __name__ == "__main__":
    main()
