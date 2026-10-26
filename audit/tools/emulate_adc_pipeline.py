#!/usr/bin/env python3
"""Exercise the exact-image ADC poll, lookup tables, and 32-word averages."""
import argparse
import hashlib
import json
import struct
from pathlib import Path

from audit_aid_tables import AidRunner, SHA


RINGS = ((4, 0x200934, 0x2008A8), (5, 0x2008B4, 0x2008A4),
         (6, 0x200A34, 0x2008B0), (7, 0x2009B4, 0x2008AC))


def table_value(raw, channel, sample, page, offset):
    def at(address, fmt):
        return struct.unpack_from("<" + fmt, raw, address - 0x4000)[0]
    if channel == 4:
        return at(0xA3A0 + 2 * min(sample, 701), "h") + offset
    if channel == 5:
        return at(0xA320 + 64 * page + (sample >> 4), "b")
    if channel == 6:
        return at(0xA030 + (sample >> 3), "B")
    if channel == 7:
        index = sample >> 1
        return 100 if index >= 312 else at(0xA0B0 + 2 * index, "h")
    raise ValueError(channel)


class AdcRunner(AidRunner):
    def __init__(self, raw):
        super().__init__(raw)
        self.allowed_ranges = ((0x41F0, 0x4302), (0x7364, 0x737C),
                               (0x7380, 0x7390), (0x7398, 0x73B0),
                               (0x73BC, 0x73C6))
        self.cpu.mem_map(0xFFFD8000, 0x1000)
        self.writes = []
        self.cpu.hook_add(self.uc.UC_HOOK_MEM_WRITE, self.record_write)

    def record_write(self, cpu, access, address, size, value, user):
        if (0x2008A0 <= address <= 0x2008B0 or 0x200721 <= address <= 0x200724 or
                address in (0x200AFE, 0xFFFD8000)):
            self.writes.append({"pc": hex(cpu.reg_read(self.arm.UC_ARM_REG_PC)),
                                "address": hex(address), "size": size,
                                "value": hex(value & ((1 << (size * 8)) - 1))})

    def sample(self, label, ready_mask, samples, average_mask, initial_status=0xF8,
               initial_page=0, offset=7):
        self.reset()
        self.cpu.mem_write(0xFFFD8000, bytes(0x1000))
        self.cpu.mem_write(0xFFFD801C, struct.pack("<I", ready_mask))
        for channel, value in samples.items():
            if not 0 <= value <= 1023:
                raise ValueError("sample must be a 10-bit ADC result")
            self.cpu.mem_write(0xFFFD8030 + 4 * channel, struct.pack("<I", value))
        self.cpu.mem_write(0x2008A0, bytes([initial_status]))
        self.cpu.mem_write(0x200AFE, bytes([initial_page]))
        self.cpu.mem_write(0x200AFF, bytes([offset]))
        for channel in range(4, 8):
            self.cpu.mem_write(0x200721 + channel - 4,
                               bytes([int(bool(average_mask & (1 << channel)))]))
        for _, start, _ in RINGS:
            self.cpu.mem_write(start, struct.pack("<32I", *range(1, 33)))
        self.writes.clear()
        self.visited.clear()
        try:
            self.cpu.emu_start(0x4215, 0x3F00, count=4096)
        except self.uc.UcError as exc:
            raise RuntimeError((label, self.fault, str(exc))) from exc
        if self.cpu.reg_read(self.arm.UC_ARM_REG_PC) != 0x3F00 or self.cpu.reg_read(self.arm.UC_ARM_REG_SP) != 0x203000:
            raise ValueError(f"{label}: incomplete call or unbalanced stack")
        page = self.cpu.mem_read(0x200AFE, 1)[0]
        expected_page = (int(samples.get(3, 0) >= 676) if ready_mask & (1 << 3) else initial_page)
        if page != expected_page:
            raise ValueError(f"{label}: page mismatch")
        outputs = {}
        for channel, start, output in RINGS:
            ring = struct.unpack("<32I", bytes(self.cpu.mem_read(start, 128)))
            value = struct.unpack("<I", bytes(self.cpu.mem_read(output, 4)))[0]
            ready = bool(ready_mask & (1 << channel))
            averaged = ready and bool(average_mask & (1 << channel))
            if averaged:
                transformed = table_value(self.raw, channel, samples[channel], page, offset)
                expected = ((sum(range(2, 33)) + transformed) & 0xFFFFFFFF) >> 5
                if ring != tuple(range(2, 33)) + (transformed,) or value != expected:
                    raise ValueError(f"{label}: channel {channel} average mismatch")
            elif ring != tuple(range(1, 33)) or value != 0:
                raise ValueError(f"{label}: channel {channel} changed without averaging")
            outputs[str(channel)] = {"averaged": averaged, "output": value,
                                     "ring_first": ring[0], "ring_last": ring[-1]}
        status = self.cpu.mem_read(0x2008A0, 1)[0]
        expected_status = initial_status & ~(ready_mask & 0xF8)
        if not expected_status:
            expected_status = 0xF8
        if status != expected_status:
            raise ValueError(f"{label}: status mismatch")
        return {"label": label, "ready_mask": hex(ready_mask),
                "samples": {str(key): value for key, value in samples.items()},
                "average_mask": hex(average_mask), "initial_status": hex(initial_status),
                "page_after": page, "status_after": hex(status), "outputs": outputs,
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
    runner = AdcRunner(raw)
    all_ready = 0xF8
    cases = [
        ("none_ready", 0, {}, 0xF0),
        ("all_zero", all_ready, {3: 0, 4: 0, 5: 0, 6: 0, 7: 0}, 0xF0),
        ("all_max", all_ready, {3: 1023, 4: 1023, 5: 1023, 6: 1023, 7: 1023}, 0xF0),
        ("all_no_averages", all_ready, {3: 675, 4: 701, 5: 512, 6: 512, 7: 622}, 0),
        ("channel4_only", 1 << 4, {4: 700}, 1 << 4),
    ]
    rows = [runner.sample(*case) for case in cases]
    seen = {int(address, 0) for row in rows for address in row["visited"]}
    result = {"format": "quadzilla-adc-pipeline-emulation-v1", "raw_sha256": SHA,
              "cpu": "ARM926 functional surrogate", "emulator": "Unicorn " + runner.uc.__version__,
              "entry": "0x4214", "cases": rows,
              "visited_starts": [hex(a) for a in sorted(seen)],
              "limits": ["ADC status and channel results are synthetic memory, not board voltages",
                         "synthetic registers do not clear EOC bits on reads",
                         "physical channel wiring, update cadence, and output units remain unverified"]}
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print([(row["label"], row["page_after"], row["status_after"], len(row["visited"]))
           for row in rows])


if __name__ == "__main__":
    main()
