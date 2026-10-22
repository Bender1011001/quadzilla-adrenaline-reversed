"""Register-level arithmetic model of 0x4A94; field names do not imply sensor units."""
MASK = 0xFFFFFFFF


def applied_value(*, step, residue, captured, minimum, low, high, requested, table_byte, percent):
    gate = 3*step+residue
    if gate >= percent:
        table = 0
    else:
        # LDRSB followed by unsigned CMP is significant for high-bit cells.
        table = (table_byte if table_byte < 128 else table_byte-256) & MASK
        if table < minimum:
            table = ((minimum*captured) & MASK)//100
        if percent < 100:
            table = (((percent-gate)*table) & MASK)//((100-gate) & MASK)
    if captured < low:
        ramp = 0
    elif low >= high:
        ramp = 100
    else:
        ramp = min(100, (((captured-low)*100) & MASK)//(high-low))
    first = ((table*requested) & MASK)//100
    return ((first*ramp) & MASK)//100
