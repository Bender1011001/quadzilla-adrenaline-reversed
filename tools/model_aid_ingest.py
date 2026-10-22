#!/usr/bin/env python3
"""Bounded offline model of the fixed-width byte walker at 0x7CC4.

This is a reviewed algorithm model, not a CPU emulator or a device client.
Variable-width AIDs, frame reception and downstream validation are excluded.
The trace and model limits are documented in docs/OFFLINE_WRITE_PATH_REVIEW.md.
"""
from dataclasses import dataclass

MAX_PAYLOAD_BYTES = 14


def fixed_width(aid: int) -> int:
    if not 0 <= aid < 220:
        raise ValueError("model supports fixed-width AIDs 0..219 only")
    return 1 if aid < 75 else 2 if aid < 150 else 3 if aid < 185 else 4


def value_capacity(aid: int) -> int:
    return MAX_PAYLOAD_BYTES // (1 + fixed_width(aid))


@dataclass
class WalkResult:
    memory: dict[int, int]
    reported_aids: list[int]
    remaining: int

    @property
    def status(self) -> int:
        return 1 if self.remaining == 0 else 2


def walk_fixed(payload: bytes, pointers: dict[int, int], initial=None) -> WalkResult:
    """Model nonempty type 0/1/3/5 payload walking, including partial stores.

    `pointers` represents the table-1 resolver result; zero/missing means unmapped.
    Empty payloads are excluded: the machine's final R7 is not initialized along
    that path. Variable-width lookahead is excluded. No bytes are sent anywhere.
    """
    if not 1 <= len(payload) <= MAX_PAYLOAD_BYTES:
        raise ValueError("model requires 1..14 payload bytes")
    memory = dict(initial or {})
    reported = []
    remaining = 0
    destination = 0
    for byte in payload:
        if remaining == 0:
            remaining = fixed_width(byte)
            destination = pointers.get(byte, 0)
            if destination:
                reported.append(byte)
        else:
            if destination:
                memory[destination] = byte
                destination += 1
            remaining -= 1
    return WalkResult(memory, reported, remaining)
