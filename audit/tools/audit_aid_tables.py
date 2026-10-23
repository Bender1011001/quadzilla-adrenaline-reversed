#!/usr/bin/env python3
"""Source-bound pointer-table and offline helper audit. No device interfaces."""
import argparse
import hashlib
import json
import struct
import sys
from pathlib import Path

from emulate_integer_runtime import Runner, SHA

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
from diff_profiles import extract_aids


class AidRunner(Runner):
    def __init__(self, raw):
        super().__init__(raw, extra_ranges=((0x7B60, 0x7EFC),))
        self.raw = raw
        self.fault = None
        self.cpu.hook_add(self.uc.UC_HOOK_MEM_INVALID, self.invalid)

    def invalid(self, cpu, access, address, size, value, user):
        self.fault = {"address": hex(address), "size": size, "access": access,
                      "pc": hex(cpu.reg_read(self.arm.UC_ARM_REG_PC))}
        return False

    def reset(self):
        self.cpu.mem_write(0x200000, bytes(0x4000))
        self.cpu.mem_write(0x200000, self.raw[0x96E8-0x4000:0x9F88-0x4000])
        self.cpu.reg_write(self.arm.UC_ARM_REG_CPSR, 0x13)
        self.cpu.reg_write(self.arm.UC_ARM_REG_SP, 0x203000)
        self.cpu.reg_write(self.arm.UC_ARM_REG_LR, 0x3F00)
        for i in range(13):
            self.cpu.reg_write(getattr(self.arm, f"UC_ARM_REG_R{i}"), 0)
        self.fault = None

    def call(self, entry, args):
        for i, value in enumerate(args):
            self.cpu.reg_write(getattr(self.arm, f"UC_ARM_REG_R{i}"), value)
        try:
            self.cpu.emu_start(entry | 1, 0x3F00, count=8192)
        except self.uc.UcError as exc:
            return {"status": "emulator_fault", "error": str(exc), "fault": self.fault}
        if self.cpu.reg_read(self.arm.UC_ARM_REG_PC) != 0x3F00:
            raise RuntimeError("helper did not return within instruction budget")
        if self.cpu.reg_read(self.arm.UC_ARM_REG_SP) != 0x203000:
            raise RuntimeError("unbalanced stack")
        return {"status": "returned", "r0": self.cpu.reg_read(self.arm.UC_ARM_REG_R0)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("image", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    raw = args.image.read_bytes()
    if hashlib.sha256(raw).hexdigest() != SHA:
        raise ValueError("unexpected source image")
    names = {}
    profile_files = sorted((ROOT / "vehicles").glob("vehicle_*.json"))
    for path in profile_files:
        for aid, record in extract_aids(json.loads(path.read_text(encoding="utf-8-sig"))).items():
            names.setdefault(aid, set()).add(record["name"])
    runner = AidRunner(raw)
    rows = []
    for aid in range(256):
        table_words = []
        for base, helper in ((0xA91C, 0x7C1C), (0xAD18, 0x7C68)):
            at = base+4*aid
            expected = struct.unpack_from("<I", raw, at-0x4000)[0]
            runner.reset()
            actual = runner.call(helper, [aid])
            if actual != {"status": "returned", "r0": expected}:
                raise RuntimeError(f"resolver mismatch at AID {aid}: {actual}")
            table_words.append({"lookup_address": hex(at), "pointer": hex(expected)})
        runner.reset()
        runner.cpu.mem_write(0x200E00, bytes([aid]))
        runner.cpu.mem_write(0x200E40, b"\x01")
        reader = runner.call(0x7D80, [0x200E80, 5, 0x200E00, 0x200E40])
        rows.append({"aid": aid, "inside_255_slot_tables": aid < 255,
                     "table1": table_words[0], "table2": table_words[1],
                     "profile_names": sorted(names.get(aid, set())), "reader": reader})
    builds = []
    for aid in (85, 255):
        runner.reset()
        runner.cpu.mem_write(0x200E00, bytes([aid]))
        runner.cpu.mem_write(0x200E40, b"\x01")
        outcome = runner.call(0x7EB4, [0x200E80, 5, 0x200E00, 0x200E40])
        builds.append({"aid": aid, "result": outcome,
                       "buffer_prefix": bytes(runner.cpu.mem_read(0x200E80, 6)).hex()})
    runner.reset()
    # The fifth C argument is a pointer at the original stack address.
    runner.cpu.mem_write(0x203000, struct.pack("<I", 0x200E70))
    runner.cpu.mem_write(0x200E00, bytes([255, 1]))
    before = bytes(runner.cpu.mem_read(0x200BBA, 1)).hex()
    writer = runner.call(0x7CC4, [0x200E00, 2, 1, 0x200E60])
    alias = {"result": writer, "destination": "0x200bba", "before": before,
             "after": bytes(runner.cpu.mem_read(0x200BBA, 1)).hex(),
             "reported_aid": bytes(runner.cpu.mem_read(0x200E60, 1)).hex(),
             "reported_count": bytes(runner.cpu.mem_read(0x200E70, 1)).hex()}
    initialized_window = raw[0x96E8-0x4000+0x190:0x96E8-0x4000+0x190+650]
    result = {"format": "quadzilla-aid-table-audit-v1", "raw_sha256": SHA,
              "emulator": "Unicorn "+runner.uc.__version__, "cpu": "ARM926 functional surrogate",
              "profile_files": len(profile_files), "profile_aid_union": len(names),
              "resolver_cases": 512, "reader_cases": 256, "rows": rows,
              "frame_builder_cases": builds, "aid255_writer_alias": alias,
              "initial_window": {"start": "0x200190", "end_exclusive": "0x20041a",
                                 "length": len(initialized_window), "min": min(initialized_window),
                                 "max": max(initialized_window), "high_bit_bytes": sum(b >= 128 for b in initialized_window)},
              "limits": ["controlled initialized SRAM, not live vehicle state", "no peripherals or device interfaces mapped",
                         "unmapped emulation read is not a demonstrated hardware reset", "initial-window values do not prove absence of later writers"]}
    args.output.write_text(json.dumps(result, indent=2)+"\n", encoding="utf-8")
    print(f"512 resolver and 256 reader cases; reader faults: {[r['aid'] for r in rows if r['reader']['status'] != 'returned']}")
    print(json.dumps({"builder": builds, "writer_alias": alias}))


if __name__ == "__main__":
    main()
