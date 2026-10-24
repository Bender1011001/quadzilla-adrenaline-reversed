#!/usr/bin/env python3
"""Execute selector encoding and AID9 reads from exact bytes, without hardware."""
import argparse
import hashlib
import itertools
import json
import random
import struct
from pathlib import Path

from audit_aid_tables import SHA
from emulate_control_helpers import ControlRunner
from model_control_helpers import latch_state, selector_state


class SelectorRunner(ControlRunner):
    def __init__(self, raw):
        super().__init__(raw)
        self.allowed_ranges += ((0x506C, 0x50DC), (0x7B60, 0x7EFC))

    def sample(self, values, read_aid=False):
        selector, count, step, offset, marker, enabled, limit, counter, source, state = values
        self.prepare(((0x20042F, 0x200433), (0x200BC4, 0x200BC5),
                      (0x201000, 0x201100)))
        for at, value in ((0x2006CD, selector), (0x200580, count), (0x200433, step),
                          (0x200434, offset), (0x200BCD, marker), (0x2006CF, enabled),
                          (0x2006D0, limit)):
            self.cpu.mem_write(at, bytes([value]))
        self.cpu.mem_write(0x20042F, bytes(state))
        self.word(0x20044C, counter)
        self.word(0x2005F4, source)
        result = self.checked_call(0x506C, [])
        status = self.cpu.mem_read(0x200BC4, 1)[0]
        ready, expected_latch = latch_state(0, source, enabled, selector, limit, counter, state)
        actual_latch = list(self.cpu.mem_read(0x20042F, 4))
        expected = selector_state(selector, count, step, offset, marker, ready)
        if (result, status) != expected or actual_latch != expected_latch:
            raise RuntimeError((values, result, status, expected, actual_latch, expected_latch))
        seen = self.visited.copy()
        record = {"inputs": {"selector": selector, "count": count, "step": step,
                  "offset": offset, "marker": marker, "enabled": enabled,
                  "threshold_limit": limit, "counter": counter, "source_u32": hex(source),
                  "latch_in": state}, "mapped_return": result, "response_byte": status,
                  "latch_out": actual_latch, "writes": self.writes.copy()}
        if read_aid:
            self.cpu.mem_write(0x201040, b"\x09")
            self.cpu.mem_write(0x201060, b"\x01")
            self.cpu.reg_write(self.arm.UC_ARM_REG_LR, 0x3F00)
            result = self.call(0x7D80, [0x201000, 5, 0x201040, 0x201060])
            record["aid9_read"] = {"result": result,
                                   "buffer": bytes(self.cpu.mem_read(0x201000, 4)).hex()}
        return record, {a for a in seen if 0x506C <= a < 0x50DC}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("image", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    raw = args.image.read_bytes()
    if hashlib.sha256(raw).hexdigest() != SHA:
        raise ValueError("unexpected image")
    r = SelectorRunner(raw)
    literals = {hex(at): hex(struct.unpack_from("<I", raw, at-0x4000)[0])
                for at in range(0x50DC, 0x50F0, 4)}
    aid9_read_pointer = struct.unpack_from("<I", raw, 0xAD18+9*4-0x4000)[0]
    if aid9_read_pointer != 0x200BC4:
        raise ValueError("AID9 response pointer changed")
    cases, seen, digest = [], set(), hashlib.sha256()
    # All selector/step pairs at an explicitly fixed count, offset and marker.
    for selector, step in itertools.product(range(256), repeat=2):
        values = (selector, 255, step, 17, 0, 0, 120, 0, 0, [120, 0, 0, 0])
        case, visited = r.sample(values)
        seen.update(visited)
        digest.update(bytes([case["mapped_return"], case["response_byte"]]))
    rng = random.Random(0x506C)
    for index in range(4096):
        values = tuple(rng.randrange(256) for _ in range(7)) + (
            rng.choice((0, 14, 15, 0xFFFFFFFF)), rng.getrandbits(32),
            [rng.randrange(256) for _ in range(4)])
        case, visited = r.sample(values)
        seen.update(visited)
        digest.update(bytes([case["mapped_return"], case["response_byte"]]))
        if index < 16:
            cases.append(case)
    for selector, marker in itertools.product(range(256), (0, 12, 13, 255)):
        case, visited = r.sample((selector, 11, 10, 0, marker, 0, 120, 0, 0,
                                 [120, 0, 0, 0]))
        seen.update(visited)
        if selector in (0, 1, 10, 11, 255):
            cases.append(case)
    # Discriminating boundaries, including signed-eight-bit reversal, zero
    # count, zero denominator and marker gating. Each includes the real reader.
    vectors = [(1, 10, 127, 0, 0), (1, 10, 128, 0, 0), (2, 10, 100, 100, 0),
               (1, 10, 0, 128, 0), (255, 0, 1, 0, 0), (0, 0, 255, 255, 255),
               (1, 10, 1, 0, 12), (1, 10, 1, 0, 13), (2, 10, 255, 255, 13),
               (1, 1, 1, 0, 0), (2, 10, 0, 0, 0), (255, 255, 255, 17, 0),
               (129, 255, 1, 255, 0)]
    for vector in vectors:
        case, visited = r.sample((*vector, 0, 120, 0, 0, [120, 0, 0, 0]), read_aid=True)
        cases.append(case)
        seen.update(visited)
    # A non-ready path and retained-ready path with the same threshold inputs.
    for ready in (0, 1, 255):
        case, visited = r.sample((2, 10, 10, 0, 13, 1, 100, 15, 0,
                                 [120, 0, ready, 0]), read_aid=True)
        cases.append(case)
        seen.update(visited)
    result = {"format": "quadzilla-control-selector-emulation-v1", "raw_sha256": SHA,
              "entry": "0x506c", "cpu": "ARM926 functional surrogate",
              "literal_words": literals,
              "aid9_response_pointer": {"table_address": "0xad3c", "pointer": hex(aid9_read_pointer),
                                        "profile_name": "Power Level", "width": 1},
              "pair_sweep": {"cases": 65536, "selector": "0..255", "step": "0..255",
                             "count": 255, "offset": 17, "marker": 0},
              "random_cases": 4096, "seed": "0x506c",
              "initialized_shape_cases": {"cases": 1024, "count": 11, "step": 10,
                                          "offset": 0, "markers": [0, 12, 13, 255]},
              "sweep_output_pairs_sha256": digest.hexdigest(),
              "reference_mismatches": 0, "examples": cases,
              "visited": [hex(a) for a in sorted(seen)],
              "unreachable_starts": {"0x50aa": "mapped byte >=128 on this path, so MOVS R0,R2 sets Z=0 and BNE always branches",
                                     "0x50ac": "only reached through unreachable 0x50aa"},
              "limits": ["direct helper inputs, not all validated or reachable parameter states",
                         "no main-loop/interrupt interleaving, hardware, bus or device I/O",
                         "AID9 reader called sequentially without packet-transport framing",
                         "profile names do not establish physical output or application decoding"]}
    args.output.write_text(json.dumps(result, indent=2)+"\n", encoding="utf-8")
    print(f"65536 pair sweep + 4096 seeded + 1024 initialized-shape + 16 boundary calls; {len(seen)} starts visited; zero model differences")


if __name__ == "__main__":
    main()
