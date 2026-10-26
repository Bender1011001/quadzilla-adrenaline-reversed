#!/usr/bin/env python3
"""Trace response-buffer writes from the original 0x5f34 config mirror."""
import argparse
import hashlib
import json
from pathlib import Path

from audit_aid_tables import AidRunner, SHA


class MirrorRunner(AidRunner):
    def __init__(self, raw):
        super().__init__(raw)
        self.allowed_ranges = ((0x5F34, 0x5FEC), (0x7B60, 0x7EFC))
        self.writes = []
        self.cpu.hook_add(self.uc.UC_HOOK_MEM_WRITE, self.record_write)

    def record_write(self, cpu, access, address, size, value, user):
        if 0x200B00 <= address < 0x200C00:
            self.writes.append({"pc": hex(cpu.reg_read(self.arm.UC_ARM_REG_PC)),
                                "address": hex(address), "size": size,
                                "value": hex(value & ((1 << (size * 8)) - 1))})

    def sample(self, flag_de, flag_df, response_fill=0xEE):
        self.reset()
        source = bytearray((i * 7 + 3) & 0xFF for i in range(44))
        source[0x12], source[0x13] = flag_de, flag_df
        self.cpu.mem_write(0x2006CC, bytes(source))
        self.cpu.mem_write(0x200B00, bytes([response_fill]) * 0x100)
        self.writes.clear()
        self.visited.clear()
        try:
            self.cpu.emu_start(0x5F35, 0x3F00, count=512)
        except self.uc.UcError as exc:
            raise RuntimeError((flag_de, flag_df, self.fault, str(exc))) from exc
        if self.cpu.reg_read(self.arm.UC_ARM_REG_PC) != 0x3F00:
            raise ValueError("mirror did not return")
        mirror_visited = [hex(address) for address in sorted(self.visited)]
        self.cpu.mem_write(0x200E00, bytes([151]))
        self.cpu.mem_write(0x200E40, bytes([1]))
        self.visited.clear()
        reader = self.call(0x7D80, [0x200E80, 5, 0x200E00, 0x200E40])
        if reader.get("status") != "returned":
            raise ValueError("AID 151 table-2 reader failed")
        return {"flag_de": flag_de, "flag_df": flag_df,
                "response_fill": hex(response_fill),
                "config_halfword_dc": hex(int.from_bytes(source[0x10:0x12], "little")),
                "writes": self.writes.copy(),
                "response_be7_be9": bytes(self.cpu.mem_read(0x200BE7, 3)).hex(),
                "aid151_reader_length": reader["r0"],
                "aid151_reader_payload": bytes(self.cpu.mem_read(0x200E80, reader["r0"])).hex(),
                "visited_mirror": mirror_visited,
                "visited_reader": [hex(address) for address in sorted(self.visited)]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("image", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    raw = args.image.read_bytes()
    if len(raw) != 32000 or hashlib.sha256(raw).hexdigest() != SHA:
        raise ValueError("unexpected firmware image")
    runner = MirrorRunner(raw)
    rows = [runner.sample(de, df) for de in (0, 1) for df in (0, 1)]
    rows.append(runner.sample(0, 0, 0))
    seen = {int(address, 0) for row in rows for address in row["visited_mirror"]}
    result = {"format": "quadzilla-config-response-mirror-emulation-v1", "raw_sha256": SHA,
              "entry": "0x5f34", "bounds": ["0x5f34", "0x5fec"],
              "cpu": "ARM926 functional surrogate", "emulator": "Unicorn " + runner.uc.__version__,
              "cases": rows, "visited_starts": [hex(a) for a in sorted(seen)],
              "limits": ["synthetic configuration and response SRAM; no live app or board traffic",
                         "response transport and interpretation are separate paths"]}
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print([(row["flag_de"], row["flag_df"], row["response_be7_be9"],
            row["aid151_reader_payload"], len(row["visited_mirror"]))
           for row in rows])


if __name__ == "__main__":
    main()
