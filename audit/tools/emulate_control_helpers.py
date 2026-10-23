#!/usr/bin/env python3
"""Execute eight control helpers from the exact image, entirely offline."""
import argparse
import hashlib
import itertools
import json
import random
import struct
import sys
from pathlib import Path

from audit_aid_tables import AidRunner, SHA

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
from model_control_helpers import index19, latch_state, mean32, normalize, ramp_state, threshold6


class ControlRunner(AidRunner):
    def __init__(self, raw):
        super().__init__(raw)
        self.allowed_ranges = ((0x4384, 0x4596), (0x4650, 0x46C2),
                               (0x47B0, 0x4810), (0x48E8, 0x4942),
                               (0x495C, 0x499A), (0x8564, 0x8678))
        self.writes = []
        self.data_ranges = ()
        self.cpu.hook_add(self.uc.UC_HOOK_MEM_WRITE, self.write)

    def write(self, cpu, access, address, size, value, user):
        if 0x202E00 <= address and address+size <= 0x203004:
            return
        if not any(lo <= address and address+size <= hi for lo, hi in self.data_ranges):
            raise RuntimeError(f"unexpected write at {address:#x}")
        self.writes.append({"pc": hex(cpu.reg_read(self.arm.UC_ARM_REG_PC)),
                            "address": hex(address), "size": size, "value": value})

    def prepare(self, ranges=()):
        self.reset()
        self.data_ranges = ranges
        self.writes = []
        self.visited.clear()
        for i in range(4, 12):
            self.cpu.reg_write(getattr(self.arm, f"UC_ARM_REG_R{i}"), 0x12340000+i)

    def checked_call(self, entry, args):
        result = self.call(entry, args)
        if result["status"] != "returned":
            raise RuntimeError(result)
        for i in range(4, 12):
            if self.cpu.reg_read(getattr(self.arm, f"UC_ARM_REG_R{i}")) != 0x12340000+i:
                raise RuntimeError(f"callee-saved R{i} changed")
        return result["r0"]

    def word(self, address, value):
        self.cpu.mem_write(address, struct.pack("<I", value))

    def read_word(self, address):
        return struct.unpack("<I", self.cpu.mem_read(address, 4))[0]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("image", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    raw = args.image.read_bytes()
    if hashlib.sha256(raw).hexdigest() != SHA:
        raise ValueError("unexpected source image")
    runner = ControlRunner(raw)
    rng = random.Random(0x4650)
    suites = []

    def record(entry, cases, examples, visited):
        suites.append({"entry": hex(entry), "cases": cases, "mismatches": [],
                       "examples": examples, "visited_addresses": [hex(x) for x in sorted(visited)]})
        print(f"{entry:#x}: {cases} matching calls", flush=True)

    for entry, model in ((0x495C, normalize), (0x497C, index19)):
        inputs = list(range(4097))+[65535, 0x7FFFFFFF, 0x80000000, 0xFFFFFFFF]
        inputs += [rng.getrandbits(32) for _ in range(1024)]
        examples, visited = [], set()
        for value in inputs:
            runner.prepare()
            actual = runner.checked_call(entry, [value])
            if actual != model(value):
                raise RuntimeError((hex(entry), value, actual, model(value)))
            visited.update(runner.visited)
            if value in (0, 40, 41, 215, 216, 4094, 4095, 4096, 0xFFFFFFFF):
                examples.append({"input": value, "r0": actual})
        record(entry, len(inputs), examples, visited)

    for entry in (0x4650, 0x4674):
        vectors = [([0]*32, 32), ([7]*32, 7), ([0xFFFFFFFF]*32, 0xFFFFFFFF),
                   (list(range(32)), 32)]
        vectors += [([rng.getrandbits(32) for _ in range(32)], rng.getrandbits(32)) for _ in range(256)]
        examples, visited = [], set()
        for samples, value in vectors:
            runner.prepare(((0x200E00, 0x200E80),))
            runner.cpu.mem_write(0x200E00, struct.pack("<32I", *samples))
            actual = runner.checked_call(entry, [0x200E00, value])
            observed = list(struct.unpack("<32I", runner.cpu.mem_read(0x200E00, 128)))
            expected, mean = mean32(samples, value)
            if (observed, actual) != (expected, mean):
                raise RuntimeError((hex(entry), samples, value, actual))
            visited.update(runner.visited)
            if len(examples) < 4:
                examples.append({"samples": samples, "new": value, "shifted": observed, "r0": actual})
        record(entry, len(vectors), examples, visited)

    vectors = list(itertools.product(list(range(256))+[0x80000000, 0xFFFFFFFF], (0, 1, 255)))
    examples, visited = [], set()
    for value, ad8 in vectors:
        runner.prepare(((0x200AD6, 0x200AD9),))
        runner.cpu.mem_write(0x200AD6, bytes([0x55, 0x66, ad8]))
        actual = runner.checked_call(0x4698, [value])
        state = list(runner.cpu.mem_read(0x200AD6, 3))
        if (actual, state) != threshold6(value, 0x66, ad8):
            raise RuntimeError((value, ad8, actual, state))
        visited.update(runner.visited)
        if value in (0, 5, 6, 255):
            examples.append({"input": value, "initial_ad7_ad8": [0x66, ad8], "r0": actual, "state_ad6_ad8": state})
    record(0x4698, len(vectors), examples, visited)

    vectors = list(itertools.product((0, 1), (0, 119, 120, 121, 0xFFFFFFFF),
                                    (0, 1), (0, 1), (0, 120), (0, 14, 15),
                                    ([120, 0, 0, 0], [120, 1, 1, 1])))
    examples, visited = [], set()
    for mode, source, enabled, selector, limit, counter, state in vectors:
        runner.prepare(((0x20042F, 0x200433),))
        runner.word(0x2005F4, source)
        runner.word(0x20044C, counter)
        runner.cpu.mem_write(0x2006CD, bytes([selector, 0, enabled, limit]))
        runner.cpu.mem_write(0x20042F, bytes(state))
        actual = runner.checked_call(0x47B0, [mode])
        observed = list(runner.cpu.mem_read(0x20042F, 4))
        expected = latch_state(mode, source, enabled, selector, limit, counter, state)
        if (actual, observed) != expected:
            raise RuntimeError((mode, source, enabled, selector, limit, counter, state, actual, observed, expected))
        visited.update(runner.visited)
        if len(examples) < 8 or (mode == 0 and source == 121 and enabled == 1 and selector == 0 and limit == 120 and counter == 15):
            examples.append({"inputs": [mode, source, enabled, selector, limit, counter, state], "r0": actual, "state": observed})
    record(0x47B0, len(vectors), examples, visited)

    vectors = list(itertools.product((0, 649, 650, 0x7FFFFFFF), (0, 1200),
                                    (0, 1199, 1200, 1201, 0x80000000, 0xFFFFFFFF),
                                    (0, 1), (0, 1), (0, 1)))
    vectors += [(rng.getrandbits(32), rng.getrandbits(32), rng.getrandbits(32), 1, 1, 0) for _ in range(512)]
    examples, visited = [], set()
    for old, previous, sample, fresh, gate, inhibit in vectors:
        runner.prepare(((0x200478, 0x200480), (0x20071C, 0x20071F)))
        runner.word(0x200478, old)
        runner.word(0x20047C, previous)
        runner.word(0x2005EC, sample)
        runner.cpu.mem_write(0x20071C, bytes([0x55, 0x66, fresh]))
        runner.cpu.mem_write(0x20042D, bytes([gate]))
        actual = runner.checked_call(0x48E8, [0, inhibit])
        observed = (actual, runner.read_word(0x200478), runner.read_word(0x20047C),
                    list(runner.cpu.mem_read(0x20071C, 3)))
        expected = ramp_state(old, previous, sample, fresh, gate, inhibit, 0x55, 0x66)
        if observed != expected:
            raise RuntimeError((old, previous, sample, fresh, gate, inhibit, observed, expected))
        visited.update(runner.visited)
        if len(examples) < 8 or (old == 649 and previous == 0 and fresh and gate and not inhibit):
            examples.append({"inputs": [old, previous, sample, fresh, gate, inhibit], "result": observed})
    record(0x48E8, len(vectors), examples, visited)

    runner.prepare(((0x200424, 0x200470), (0x200580, 0x2005C4), (0x200BEA, 0x200C36)))
    runner.checked_call(0x4384, [])
    defaults = runner.writes
    expected_words = {0x200584: 250, 0x200590: 1800, 0x200594: 3400,
                      0x200458: 1920, 0x20045C: 2304, 0x200460: 2688,
                      0x200464: 2944, 0x200468: 3200, 0x20046C: 256}
    if any(runner.read_word(address) != value for address, value in expected_words.items()):
        raise RuntimeError("default scalar/Q7 initialization mismatch")
    if list(runner.cpu.mem_read(0x200433, 2)) != [10, 0]:
        raise RuntimeError("default ramp-step/remainder mismatch")
    record(0x4384, 1, [{"writes": defaults}], runner.visited)
    result = {"format": "quadzilla-control-helper-emulation-v1", "raw_sha256": SHA,
              "emulator": "Unicorn "+runner.uc.__version__, "cpu": "ARM926 functional surrogate",
              "seed": "0x4650", "suites": suites, "total_calls": sum(s["cases"] for s in suites),
              "checks": ["R4..R11 preserved", "SP balanced", "writes limited to described data and stack",
                         "execution limited to reviewed helper ranges and integer division"],
              "limits": ["synthetic helper inputs; not proof of main-loop reachability", "no peripheral or device I/O",
                         "32-bit arithmetic samples are not exhaustive", "not hardware or timing validation"]}
    args.output.write_text(json.dumps(result, indent=2)+"\n", encoding="utf-8")


if __name__ == "__main__":
    main()
