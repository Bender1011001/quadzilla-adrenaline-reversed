"""Bounded models of reviewed control helpers; no hardware or physical units.

These preserve the firmware's 32-bit wrap, truncation, and persistent byte
state. They model helper calls, not all reachable main-loop or vehicle states.
"""
MASK = 0xFFFFFFFF


def signed(value):
    value &= MASK
    return value if value < 0x80000000 else value-0x100000000


def normalize(value):
    return min(value & MASK, 4095)*100//4095


def index19(value):
    return min(normalize(value)*19//100, 19)


def mean32(samples, value):
    if len(samples) != 32:
        raise ValueError("32 samples required")
    shifted = [x & MASK for x in samples[1:]]+[value & MASK]
    return shifted, (sum(shifted) & MASK) >> 5


def threshold6(value, byte_ad7, byte_ad8):
    value &= MASK
    if value >= 6:
        return 0, [0, 1, 0]
    return (1 if byte_ad8 else value), [1, byte_ad7, byte_ad8]


def latch_state(mode, source, enabled, selector, limit, counter, state):
    """Return R0 and [threshold, latched, ready, edge] at 0x20042F..432."""
    threshold, latched, ready, edge = state
    if mode & MASK:
        return 0, [limit if enabled else 120, 0, 0, 0]
    source = signed(source)
    if not enabled or selector == 1 or (max(source, 0) >= limit and counter < 15):
        ready = 1
    if threshold < source and not latched:
        latched, edge = 1, 1
    return ready, [threshold, latched, ready, edge]


def ramp_state(old, previous, sample, fresh, gate, inhibit, flag_c, flag_d):
    """Return R0, accumulator, previous delta, and bytes 0x20071C..71E."""
    if not fresh:
        return old, old, previous, [flag_c, flag_d, fresh]
    delta = (1200-sample) & MASK
    result = 0
    if gate and not inhibit:
        numerator = signed(delta)
        quotient = abs(numerator)//40
        if numerator < 0:
            quotient = -quotient
        candidate = (old+quotient+delta-previous) & MASK
        if not candidate & 0x80000000:
            result = min(candidate, 650)
    return result, result, delta, [1, 1, 0]
