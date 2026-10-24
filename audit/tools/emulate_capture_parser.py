#!/usr/bin/env python3
"""Execute the original capture/parser with synthetic SRAM/MMIO; no device I/O."""
import argparse
import hashlib
import itertools
import json
import struct
import sys
from fractions import Fraction
from pathlib import Path

from audit_aid_tables import SHA
from emulate_capture_helpers import HelperRunner

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "tools"))
from model_soft_float import binary, convert, encode, to_integer

A, B = 0x2005C4, 0x200AB4
PATTERNS = (0x6C, 0x78, 0x68, 0x70, 0x74, 0x44, 0x80, 0x7C, 0x84)
BYTE_FIELDS = tuple(range(0x13, 0x1A))
WORD_FIELDS = tuple(range(0x20, 0x3C, 4))


class ParserRunner(HelperRunner):
    def __init__(self, raw):
        super().__init__(raw)
        self.allowed_ranges += ((0x59E8, 0x5CBA), (0x8564, 0x8678),
                                (0x5F04, 0x5F08), (0x5F0C, 0x5F10),
                                (0x7128, 0x7132), (0x7140, 0x7144),
                                (0x7160, 0x7164), (0x8678, 0x96C4))
        self.buffer_reads = set()
        self.capture_writes = []
        self.transfers = []
        self.spi_status = 0x30
        self.mode = "parser"

    def trace(self, cpu, address, size, user):
        # Avoid HelperRunner's scripted transfer-status changes. Execute each
        # helper against the same explicitly supplied plain-memory status.
        from emulate_spi_transfers import TransferRunner
        TransferRunner.trace(self, cpu, address, size, user)
        if address in (0x6B64, 0x6B8C, 0x6B9C, 0x5EBC):
            self.transfers.append({"entry": hex(address), "args": [
                hex(cpu.reg_read(getattr(self.arm, f"UC_ARM_REG_R{i}"))) for i in range(4)]})

    def record_read(self, cpu, access, address, size, value, user):
        super().record_read(cpu, access, address, size, value, user)
        if B <= address < B+14:
            self.buffer_reads.add(address-B)

    def record_write(self, cpu, access, address, size, value, user):
        super().record_write(cpu, access, address, size, value, user)
        if A <= address < A+0x3C:
            self.capture_writes.append({"site": hex(cpu.reg_read(self.arm.UC_ARM_REG_PC)),
                                        "offset": hex(address-A), "size": size,
                                        "value": hex(value & ((1 << (8*size))-1))})

    def sample(self, name, state=2, kind=2, frame=None, pins=0x818, status=0x30,
               mode=0, reset=0, changes=()):
        self.reset()
        self.cpu.mem_write(0xFFFE0000, bytes(0x1000))
        self.cpu.mem_write(0xFFFFF000, bytes(0x1000))
        self.cpu.mem_write(0xFFFE0010, struct.pack("<I", status))
        self.cpu.mem_write(0xFFFFF43C, struct.pack("<I", pins))
        self.cpu.mem_write(A+0x1C, struct.pack("<I", 0xFFFE0000))
        for at in BYTE_FIELDS:
            self.cpu.mem_write(A+at, b"\xa7")
        for at in WORD_FIELDS:
            self.cpu.mem_write(A+at, struct.pack("<I", 0xA7A7A7A7))
        self.cpu.mem_write(A+0x1A, bytes([state]))
        self.cpu.mem_write(A+0x12, bytes([kind]))
        self.cpu.mem_write(0x200AD2, b"\0")  # rotation helper's documented no-op path
        if frame is not None:
            self.cpu.mem_write(B if kind == 2 else A, frame)
        for at, value in changes:
            self.cpu.mem_write(at, bytes([value]))
        self.buffer_reads.clear()
        self.capture_writes.clear()
        self.transfers.clear()
        self.reads.clear()
        self.writes.clear()
        self.visited.clear()
        preserved = []
        for n in range(4, 8):
            reg = getattr(self.arm, f"UC_ARM_REG_R{n}")
            value = 0x12340000+n
            self.cpu.reg_write(reg, value)
            preserved.append((reg, value))
        outcome = self.call(0x59E8, [reset, mode])
        if outcome["status"] != "returned":
            raise RuntimeError(f"{name}: {outcome}")
        if any(self.cpu.reg_read(r) != v for r, v in preserved):
            raise RuntimeError("R4-R7 preservation failure")
        outputs = {hex(at): self.cpu.mem_read(A+at, 1)[0] for at in BYTE_FIELDS}
        outputs.update({hex(at): struct.unpack("<I", self.cpu.mem_read(A+at, 4))[0]
                        for at in WORD_FIELDS})
        return {"name": name, "inputs": {"state": state, "kind": kind, "pins": hex(pins),
                "status": hex(status), "mode": mode, "reset": reset,
                "frame": None if frame is None else frame.hex(),
                "changes": [[hex(a), v] for a, v in changes]},
                "state_out": self.cpu.mem_read(A+0x1A, 1)[0],
                "kind_out": self.cpu.mem_read(A+0x12, 1)[0],
                "pending_out": self.cpu.mem_read(A+0x11, 1)[0], "outputs": outputs,
                "writes": self.capture_writes.copy(), "mmio_writes": self.writes.copy(),
                "calls": self.transfers.copy(), "rx1_offsets_read": sorted(self.buffer_reads),
                "visited": [hex(a) for a in sorted(self.visited) if 0x59E8 <= a < 0x5CBA]}


def expected(pattern, frame, adjustment, coefficient):
    d = frame
    word = d[12] | d[13] << 8
    if pattern == 0x6C:
        return {"0x2c": min(d[7]*4//10, 100), "0x16": d[8]}
    if pattern == 0x78:
        q = d[8]*62//100
        f = binary("mul", encode(Fraction(q), 32), coefficient, 32)
        ratio = binary("div", convert(f, 32, 64), 0x4057ECCCCCCCCCCD, 64)
        return {"0x13": to_integer(ratio, 64, True) & 255}
    if pattern == 0x68:
        return {"0x30": (d[6]*9//5-40) & 0xFFFFFFFF}
    if pattern == 0x70:
        return {"0x34": word*5//10}
    if pattern == 0x74:
        return {"0x14": d[9]*58//100}
    if pattern == 0x44:
        return {"0x38": (word*1125//10000-460) & 0xFFFFFFFF}
    if pattern == 0x80:
        return {"0x18": d[1] >> 1}
    if pattern == 0x7C:
        q = ((d[7]*2) & 255)//7
        if adjustment == 1:
            q = max(q, 13)-13
        return {"0x17": q, "0x15": (d[8]*9//5) & 255}
    return {"0x19": 1} if d[6] == 0xBB else {}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("image", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    raw = args.image.read_bytes()
    if hashlib.sha256(raw).hexdigest() != SHA:
        raise ValueError("unexpected image")
    r = ParserRunner(raw)
    init = raw[0x96E8-0x4000:0x9F88-0x4000]
    coefficient = struct.unpack_from("<I", init, 0x6E8)[0]
    patterns = {p: init[A-0x200000+p:A-0x200000+p+(2 if p == 0x44 else 4)] for p in PATTERNS}
    detailed, seen, mismatches = [], set(), []
    def collect(case, keep=True):
        seen.update(case["visited"])
        if keep:
            detailed.append(case)
        return case
    for state, kind, status, pins in itertools.product((0, 1, 2, 3), (0, 1, 2, 3),
                                                      (0, 0x10, 0x20, 0x30), (0x800, 0x818)):
        collect(r.sample("control", state=state, kind=kind, status=status, pins=pins))
    for mode, gate1, gate2, request, bit2 in itertools.product((0, 1), (0, 1), (0, 1), (0, 1), (0, 4)):
        collect(r.sample("rx0_gate", state=0, mode=mode, pins=0x800 | bit2,
                         changes=((0x20042D, gate1), (0x20042E, gate2),
                                  (0x20042A, gate1), (A+0x10, request), (A+0xF, 0))))
    collect(r.sample("rx1_start", state=0, pins=0x808))
    collect(r.sample("reset", state=2, reset=1))
    for word in (0, 1, 3, 4, 255, 256, 32767, 32768, 65535):
        frame = bytes([0xA5])+struct.pack("<H", word)+bytes([0xCC, 0xDD])+struct.pack("<HH", word, word)
        case = collect(r.sample("rx0_words", kind=1, frame=frame))
        exp = {"0x20": word, "0x24": word, "0x28": word//4}
        if any(case["outputs"][k] != v for k, v in exp.items()):
            mismatches.append({"case": case, "expected": exp})
    # Unknown headers retain every destination; the two-byte comparison
    # intentionally ignores the other two identifier-register bytes.
    collect(r.sample("unknown_header", frame=bytes(14)))
    frame = bytearray(14)
    frame[1:3] = patterns[0x44]
    frame[3:5] = b"\xff\xff"
    collect(r.sample("two_byte_header_match", frame=bytes(frame)))
    summaries = []
    for p in PATTERNS:
        digest = hashlib.sha256()
        count = 0
        for value, adjustment, dlc in itertools.product(range(256), (0, 1) if p == 0x7C else (0,), (0, 8)):
            frame = bytearray([0xA5]+[value]*13)
            frame[1:1+len(patterns[p])] = patterns[p]
            frame[5] = dlc
            case = collect(r.sample(f"pattern_{p:x}", frame=bytes(frame),
                                    changes=((0x200AFE, adjustment),)),
                           keep=value in (0, 1, 127, 128, 187, 255))
            exp = expected(p, frame, adjustment, coefficient)
            expected_outputs = {hex(at): 0xA7 for at in BYTE_FIELDS}
            expected_outputs.update({hex(at): 0xA7A7A7A7 for at in WORD_FIELDS})
            expected_outputs.update(exp)
            if case["outputs"] != expected_outputs:
                mismatches.append({"pattern": hex(p), "value": value, "adjustment": adjustment,
                                   "dlc": dlc, "actual": case["outputs"], "expected": expected_outputs})
            digest.update(bytes([value, adjustment, dlc]))
            digest.update(b"".join(struct.pack("<I", case["outputs"][hex(at)])
                                   for at in BYTE_FIELDS+WORD_FIELDS))
            count += 1
        summaries.append({"pattern_offset": hex(p), "header": patterns[p].hex(),
                          "cases": count, "output_sha256": digest.hexdigest()})
    # Explicit low/high word independence, unlike the repeated-byte sweeps.
    for p, word in itertools.product((0x70, 0x44), (0, 1, 4090, 4091, 65535)):
        frame = bytearray(14)
        frame[1:1+len(patterns[p])] = patterns[p]
        frame[5] = 8
        frame[12:14] = struct.pack("<H", word)
        case = collect(r.sample("word_edge", frame=bytes(frame)))
        exp = expected(p, frame, 0, coefficient)
        if any(case["outputs"][k] != v for k, v in exp.items()):
            mismatches.append({"case": case, "expected": exp})
    result = {"format": "quadzilla-capture-parser-emulation-v1", "raw_sha256": SHA,
              "entry": "0x59e8", "cpu": "ARM926 functional surrogate",
              "coefficient_f32_bits": hex(coefficient), "cases": detailed,
              "sweeps": summaries, "reference_mismatches": mismatches,
              "visited": sorted(seen, key=lambda x: int(x, 0)),
              "limits": ["plain-memory synthetic SPI/PIO status, no DMA engine or bus",
                         "receive buffers supplied directly, not live frames",
                         "rotation trigger held off; helper reviewed separately",
                         "no IRQ interleaving, timing, oscillator or vehicle-unit model",
                         "DLC-zero probes establish parser behavior, not live frame acceptance"]}
    args.output.write_text(json.dumps(result, indent=2)+"\n", encoding="utf-8")
    print(f"{len(detailed)} detailed cases; {sum(s['cases'] for s in summaries)} sweep calls; "
          f"{len(seen)} visited parser starts; {len(mismatches)} reference differences")


if __name__ == "__main__":
    main()
