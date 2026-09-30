#!/usr/bin/env python3
"""X2com frame checksum: CRC-8/SAE-J1850.

Recovered from ``x2com_generate_crc`` in the iQuad app's native library
(``libx2com-jni.so``): initial value 0xFF, polynomial 0x1D, MSB first, final XOR 0xFF.
Those parameters match the catalogued CRC-8/SAE-J1850 (check value 0x4B for
``b"123456789"``), the checksum used on J1850 vehicle buses.

Frame layout (``x2com_build_msg`` / ``x2com_parse_msg``)::

    byte 0      [ message type : 4 | index of last data byte : 4 ]
    bytes 1..N  AID list and values
    byte N+1    CRC-8 over bytes 0..N

``x2com_check_crc`` accepts a frame when the CRC computed over the whole frame,
including its own CRC byte, equals 0x3B (the inverted J1850 residue 0xC4).

A CRC detects corruption only; it is not a MAC. The protocol has no authentication
field (see docs/SECURITY_ASSESSMENT.md, F4).
"""
from __future__ import annotations

POLY = 0x1D
INIT = 0xFF
XOROUT = 0xFF
CHECK_VALUE = 0x3B  # crc8(frame_with_crc) for any valid frame

MSG_TYPES = {0: "CWA", 1: "CMD", 2: "ACK", 3: "NOTIFY", 4: "REQ", 5: "RESP"}
MAX_AIDS_PER_FRAME = 14


def crc8(data: bytes) -> int:
    crc = INIT
    for byte in data:
        crc ^= byte
        for _ in range(8):
            crc = ((crc << 1) ^ POLY) & 0xFF if crc & 0x80 else (crc << 1) & 0xFF
    return crc ^ XOROUT


def add_crc(frame_without_crc: bytes) -> bytes:
    return frame_without_crc + bytes([crc8(frame_without_crc)])


def check_frame(frame: bytes) -> bool:
    return len(frame) >= 2 and crc8(frame) == CHECK_VALUE


def parse_header(byte0: int) -> tuple[str, int]:
    """Return ``(message type name, index of last data byte)``."""
    return MSG_TYPES.get(byte0 >> 4, f"UNKNOWN({byte0 >> 4})"), byte0 & 0x0F


if __name__ == "__main__":
    import sys

    raw = bytes.fromhex(sys.argv[1]) if len(sys.argv) > 1 else b"123456789"
    print(f"crc8({raw.hex()}) = 0x{crc8(raw):02X}")
    if len(sys.argv) > 1:
        kind, last = parse_header(raw[0])
        print(f"as a complete frame: valid={check_frame(raw)} type={kind} last_pos={last}")
