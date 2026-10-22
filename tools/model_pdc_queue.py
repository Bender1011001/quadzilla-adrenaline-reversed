"""Snapshot model of the USART0 current/next staging decision, with no hardware I/O.

The outcome field is analysis metadata, not a status returned by the firmware.
Hardware DMA promotion, interrupts, and memory-transfer timing are not simulated.
"""
from dataclasses import dataclass, replace


@dataclass(frozen=True)
class QueueState:
    current_pointer: int = 0
    current_count: int = 0
    next_pointer: int = 0
    next_count: int = 0
    software_flag: int = 1


def stage(state: QueueState, pointer: int, count: int):
    if not 0 <= pointer <= 0xFFFFFFFF or not 0 <= count <= 0xFFFF:
        raise ValueError("model expects a 32-bit pointer and 16-bit counter")
    state = replace(state, software_flag=0)
    if state.current_count == 0:
        return replace(state, current_pointer=pointer, current_count=count, next_pointer=0, next_count=0), "current"
    if state.next_count == 0:
        return replace(state, next_pointer=pointer, next_count=count), "next"
    return state, "not_staged"
