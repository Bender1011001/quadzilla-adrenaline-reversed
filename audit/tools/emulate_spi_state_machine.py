#!/usr/bin/env python3
"""Execute the exact SPI state routine with controlled flags and register reads."""
import argparse
import hashlib
import json
import struct
from pathlib import Path

from audit_aid_tables import SHA
from emulate_spi_transfers import TransferRunner, SPI, PIO_PDSR


A = 0x2005C4
PACKET = 0x2006C0


def packet_reference(signed_word):
    value = signed_word if signed_word < 0x80000000 else signed_word-0x100000000
    quotient = abs(value)//256 * (-1 if value < 0 else 1)
    remainder = value-256*quotient
    return bytes((0xA7, 0x78, 0x56, 0x11, 0x22, remainder & 255,
                  quotient & 255, 0x33, 0x44)).hex()


class StateRunner(TransferRunner):
    def __init__(self, raw):
        super().__init__(raw)
        self.allowed_ranges += ((0x5CF0, 0x5DEA),)
        self.state_writes = []
        self.status_sequence = []
        self.status_reads = 0

    def record_write(self, cpu, access, address, size, value, user):
        super().record_write(cpu, access, address, size, value, user)
        if A <= address < A+0x110:
            self.state_writes.append({"site": hex(cpu.reg_read(self.arm.UC_ARM_REG_PC)),
                                      "address": hex(address), "size": size, "value": hex(value)})

    def record_read(self, cpu, access, address, size, value, user):
        if address == SPI+0x10:
            if self.status_reads < len(self.status_sequence):
                cpu.mem_write(address, struct.pack("<I", self.status_sequence[self.status_reads]))
            self.status_reads += 1
        super().record_read(cpu, access, address, size, value, user)

    def state_case(self, name, state=0, pending=0, status=0, pins=0,
                   reset_arg=0, mode_arg=0, gates=(1, 0, 0), signed_word=0,
                   status_sequence=()):
        self.reset()
        self.cpu.mem_write(SPI, bytes(0x1000))
        self.cpu.mem_write(0xFFFFF000, bytes(0x1000))
        self.cpu.mem_write(SPI+0x10, struct.pack("<I", status))
        self.cpu.mem_write(PIO_PDSR, struct.pack("<I", pins))
        self.cpu.mem_write(A, bytes(0x110))
        self.cpu.mem_write(A+0x1C, struct.pack("<I", SPI))
        self.cpu.mem_write(A+0x1B, bytes([state]))
        self.cpu.mem_write(A+0x10, b"\x09")
        self.cpu.mem_write(A+0x11, bytes([pending]))
        for address, value in zip((0x20042D, 0x20042E, 0x20042A), gates):
            self.cpu.mem_write(address, bytes([value]))
        for offset, value in ((3, 0x11), (4, 0x22), (7, 0x33), (8, 0x44)):
            self.cpu.mem_write(A+offset, bytes([value]))
        self.cpu.mem_write(A+0x3C, struct.pack("<I", 0x12345678))
        self.cpu.mem_write(A+0x40, struct.pack("<I", signed_word))
        self.cpu.mem_write(PACKET, b"\xA7"+b"\xCC"*8)
        self.cpu.mem_write(A+0xC4, b"\x01\x02\x03\x04")
        self.status_sequence = list(status_sequence)
        self.status_reads = 0
        self.state_writes.clear()
        self.writes.clear()
        self.reads.clear()
        self.visited.clear()
        preserved = []
        for n in range(4, 8):
            reg = getattr(self.arm, f"UC_ARM_REG_R{n}")
            value = 0x12340000+n
            self.cpu.reg_write(reg, value)
            preserved.append((reg, value))
        result = self.call(0x5CF0, [reset_arg, mode_arg])
        if result["status"] != "returned":
            raise RuntimeError(result)
        if any(self.cpu.reg_read(reg) != value for reg, value in preserved):
            raise RuntimeError("R4-R7 not preserved")
        packet = bytes(self.cpu.mem_read(PACKET, 9)).hex()
        built = any(w["address"] == hex(PACKET+1) for w in self.state_writes)
        expected = packet_reference(signed_word) if built else None
        if expected is not None and packet != expected:
            raise RuntimeError("packet reference mismatch")
        return {"name": name, "state_in": state, "pending_in": pending,
                "reset_arg": reset_arg, "mode_arg": mode_arg, "gates": list(gates),
                "synthetic_spi_sr": hex(status), "synthetic_pio_pdsr": hex(pins),
                "scripted_status_reads": [hex(x) for x in status_sequence],
                "signed_word": hex(signed_word),
                "state_out": self.cpu.mem_read(A+0x1B, 1)[0],
                "request_out": self.cpu.mem_read(A+0x10, 1)[0],
                "pending_out": self.cpu.mem_read(A+0x11, 1)[0],
                "packet": packet, "packet_reference": expected,
                "writes": self.writes.copy(), "state_writes": self.state_writes.copy(),
                "reads": self.reads.copy(),
                "routine_visited": [hex(a) for a in sorted(self.visited) if 0x5CF0 <= a < 0x5DEA],
                "callee_saved_r4_r7_preserved": True}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("image", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    raw = args.image.read_bytes()
    if hashlib.sha256(raw).hexdigest() != SHA:
        raise ValueError("unexpected application image")
    spi_pointer = struct.unpack_from("<I", raw, 0x9CC8-0x4000)[0]
    if spi_pointer != SPI:
        raise ValueError("initialized SPI pointer changed")
    runner = StateRunner(raw)
    cases = []
    for state in (0, 1, 2, 5, 3):
        for pending in (0, 1):
            for status in (0, 0x30):
                for pins in (0, 0x800, 0x804):
                    cases.append(runner.state_case("matrix", state, pending, status, pins))
    cases += [runner.state_case("explicit_reset", state=5, pending=1, reset_arg=1),
              runner.state_case("ordinary_gates_off", state=5, pending=1, gates=(0, 0, 0)),
              runner.state_case("ordinary_second_gate", state=1, pending=1, pins=4, gates=(0, 1, 0)),
              runner.state_case("alternate_gate_off", state=5, pending=1, mode_arg=1),
              runner.state_case("alternate_gate_on", state=1, pending=1, pins=4, mode_arg=1, gates=(0, 0, 1)),
              runner.state_case("readiness_changes", state=2, status=0x20, pins=0x804,
                                status_sequence=(0x20, 0))]
    for value in (0, 1, 255, 256, 0xFFFFFFFF, 0xFFFFFF01, 0xFFFFFF00,
                  0xFFFFFEFF, 0x7FFFFFFF, 0x80000000):
        cases.append(runner.state_case("payload_signed", state=2, status=0x30,
                                       pins=0x804, signed_word=value))
    literals = {hex(a): hex(struct.unpack_from("<I", raw, a-0x4000)[0])
                for a in range(0x5DEC, 0x5E04, 4)}
    result = {"format": "quadzilla-spi-state-machine-emulation-v1", "raw_sha256": SHA,
              "cpu": "ARM926 functional surrogate", "entry": "0x5cf0",
              "initialized_spi_pointer": {"ram": "0x2005e0", "source": "0x9cc8",
                                          "value": hex(spi_pointer)},
              "literal_words": literals, "cases": cases,
              "limits": ["SPI/PDC/PIO registers are synthetic and transfers do not occur",
                         "readiness_changes explicitly supplies different status values on successive reads",
                         "single-call state matrix does not model real interrupt/main-loop scheduling",
                         "negative payload inputs are controlled probes without proven live reachability"]}
    args.output.write_text(json.dumps(result, indent=2)+"\n", encoding="utf-8")


if __name__ == "__main__":
    main()
