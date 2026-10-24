#!/usr/bin/env python3
"""Trace exact SPI initialization and its timeout path using synthetic MMIO."""
import argparse
import hashlib
import json
import struct
from pathlib import Path

from audit_aid_tables import SHA
from emulate_spi_transfers import TransferRunner, SPI, PIO_PDSR


class InitializationRunner(TransferRunner):
    def __init__(self, raw):
        super().__init__(raw)
        self.allowed_ranges += ((0x575C, 0x59CA), (0x59E8, 0x59FE),
                                (0x5CB2, 0x5CBA), (0x5CF0, 0x5D04), (0x5DE2, 0x5DEA))
        self.mode = "ready"
        self.calls = []
        self.attempts = {}
        self.state_writes = []
        self.injected = []
        self.reset_requested = False

    def trace(self, cpu, address, size, user):
        super().trace(cpu, address, size, user)
        if address in (0x6B64, 0x6B9C):
            site = (cpu.reg_read(self.arm.UC_ARM_REG_LR) & ~1)-4
            number = self.attempts.get(site, 0)+1
            self.attempts[site] = number
            ready = self.mode == "ready" or (self.mode == "retry_once_each" and number > 1)
            cpu.mem_write(SPI+0x10, struct.pack("<I", 0x30 if ready else 0))
            self.calls.append({"site": hex(site), "helper": hex(address), "attempt": number,
                               "scripted_ready": ready,
                               "args": [hex(cpu.reg_read(getattr(self.arm, f"UC_ARM_REG_R{i}")))
                                        for i in range(3 if address == 0x6B64 else 4)]})
        if self.mode == "timeout" and address == 0x5798 and not self.injected:
            cpu.mem_write(0x200AD5, b"\x01")
            self.injected.append({"site": hex(address), "address": "0x200ad5", "value": 1})

    def record_write(self, cpu, access, address, size, value, user):
        super().record_write(cpu, access, address, size, value, user)
        if 0x200000 <= address < 0x200C00:
            self.state_writes.append({"site": hex(cpu.reg_read(self.arm.UC_ARM_REG_PC)),
                                      "address": hex(address), "size": size, "value": hex(value)})
        if address == 0xFFFFFD00:
            self.reset_requested = True
            cpu.emu_stop()

    def sample_initialization(self, mode):
        self.reset()
        self.cpu.mem_write(SPI, bytes(0x1000))
        self.cpu.mem_write(0xFFFFF000, bytes(0x1000))
        self.cpu.mem_write(PIO_PDSR, struct.pack("<I", 0x800))
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
        self.cpu.emu_start(0x575D, 0x3F00, count=5000 if mode == "not_ready" else 20000)
        pc = self.cpu.reg_read(self.arm.UC_ARM_REG_PC)
        returned = pc == 0x3F00
        if mode in ("ready", "retry_once_each"):
            if not returned or self.cpu.reg_read(self.arm.UC_ARM_REG_SP) != 0x203000:
                raise RuntimeError("normal initialization did not return with balanced stack")
            if any(self.cpu.reg_read(reg) != value for reg, value in preserved):
                raise RuntimeError("R4-R7 not preserved")
        if mode == "timeout" and not self.reset_requested:
            raise RuntimeError("timeout did not reach reset request")
        if mode == "not_ready" and (returned or self.reset_requested):
            raise RuntimeError("unready/no-timeout probe unexpectedly terminated")
        return {"mode": mode, "outcome": "reset_request_stop" if self.reset_requested else
                "returned" if returned else "instruction_budget", "stop_pc": hex(pc),
                "transfer_calls": self.calls.copy(), "external_flag_injections": self.injected.copy(),
                "writes": self.writes.copy(), "state_writes": self.state_writes.copy(),
                "timeout_flag": self.cpu.mem_read(0x200AD5, 1)[0],
                "reset_state_2005de": self.cpu.mem_read(0x2005DE, 1)[0],
                "output_state_2005df": self.cpu.mem_read(0x2005DF, 1)[0],
                "request_2005d4": self.cpu.mem_read(0x2005D4, 1)[0],
                "pending_2005d5": self.cpu.mem_read(0x2005D5, 1)[0],
                "initializer_visited": [hex(a) for a in sorted(self.visited) if 0x575C <= a < 0x59CA],
                "capture_reset_path_visited": [hex(a) for a in sorted(self.visited)
                                               if 0x59E8 <= a < 0x59FE or 0x5CB2 <= a < 0x5CBA]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("image", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    raw = args.image.read_bytes()
    if hashlib.sha256(raw).hexdigest() != SHA:
        raise ValueError("unexpected application image")
    runner = InitializationRunner(raw)
    result = {"format": "quadzilla-spi-initialization-emulation-v1", "raw_sha256": SHA,
              "cpu": "ARM926 functional surrogate", "entry": "0x575c",
              "literal_words": {hex(a): hex(struct.unpack_from("<I", raw, a-0x4000)[0])
                                for a in range(0x59CC, 0x59E8, 4)},
              "cases": [runner.sample_initialization(mode) for mode in
                        ("ready", "retry_once_each", "timeout", "not_ready")],
              "limits": ["SPI/PDC/PIO/RSTC are synthetic memory; no physical transfer or reset occurs",
                         "readiness is scripted per transfer attempt, not produced by a PDC model",
                         "timeout is an explicitly injected SRAM flag, without simulated IRQ timing",
                         "execution stops at the reset request; physical reset acceptance is unverified",
                         "only the R0-nonzero reset path of 0x59e8 is included"]}
    args.output.write_text(json.dumps(result, indent=2)+"\n", encoding="utf-8")


if __name__ == "__main__":
    main()
