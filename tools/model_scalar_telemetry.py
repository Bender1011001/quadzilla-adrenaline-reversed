"""32-bit mathematical model of the reviewed 0x4D38 scalar path; no device I/O."""
MASK = 0xFFFFFFFF


def signed(value):
    value &= MASK
    return value if value < 0x80000000 else value - 0x100000000


def sdiv(value, divisor):
    value = signed(value)
    return ((abs(value) // divisor) * (-1 if value < 0 else 1)) & MASK


def caller_store(result, cap):
    """0x5266 unsigned upper comparison, then 0x5272 signed lower comparison."""
    result = min(result & MASK, cap & MASK)
    return 1024 if signed(result) < 1024 else result


def calculate(c):
    """Input fields describe controlled SRAM and the low-byte caller domain.

    Products and additions wrap to 32 bits before the next division. The return
    includes the externally visible flag, knot and cap writes as final state.
    No monotonic-knot, live-writer or physical-unit invariant is assumed.
    """
    knots = [v & MASK for v in c['knots']]
    mode = c['mode']
    if c['refresh']:
        mode = int(not any(c['response_flags']))
    active = c['gate_sum'][0] + c['gate_sum'][1] < c['selector'] and c['enabled'] != 0
    base, x = c['base'] & MASK, c['capture'] & MASK
    cell, a, b, special, fraction, slope = 0, 0, 0, False, 0, 0
    cap = 0xF00
    if active:
        if mode:
            knots = [min(v, ceiling) for v, ceiling in zip(knots, (384, 512, 640, 768, 896))]
        else:
            cap = knots[4]
            cell = c['cell'] if c['cell'] < 128 else c['cell'] - 256
            a = sdiv(c['coefficient'] * c['response'] * 128, 1000)
            b = sdiv(c['coefficient'] * 128, 10)
            special = c['response'] < c['threshold'] and c['working61'] != 0
        if x < 1000:
            a, b, special = 0, 0, False
        elif x >= 3500:
            if mode:
                fraction, slope = 100, knots[4]
            else:
                base, a = knots[4], b
        else:
            segment = (x - 1000) // 500
            fraction = (x - (999 + 500 * segment)) // 5
            if segment == 0:
                slope = knots[0] if mode else (knots[0] - base) & MASK
                if not mode:
                    a, b = 0, 0
                    if x < 1200:
                        special = False
            else:
                slope = (knots[segment] - knots[segment - 1]) & MASK
                base = (base + knots[segment - 1]) & MASK if mode else knots[segment - 1]
    interpolated = sdiv((slope * fraction) & MASK, 100)
    if special:
        adjustment = ((c['working61'] * c['response']) & MASK) // 100
        bonus = 128 if c['status'] >= 51 else 0
        scalar = (base + interpolated + c['working61'] + bonus - adjustment) & MASK
        cell = 0
    else:
        scalar = (base + interpolated - b + a) & MASK
    table_term = sdiv((sdiv(cell * 1280, 100) * c['percent0']) & MASK, 100)
    ceiling_term = ((sdiv(c['percent1'] * c['percent0'], 100) * 1280) & MASK) // 100
    subtraction = min(table_term, ceiling_term)  # unsigned CMP/BCS at 0x5006
    result = (scalar - subtraction) & MASK
    return {'return': result, 'cap': cap, 'mode': mode, 'refresh': 0,
            'knots': knots, 'active': bool(active), 'special': bool(special),
            'interpolated': interpolated, 'pre_subtraction': scalar,
            'table_term': table_term, 'ceiling_term': ceiling_term,
            'subtraction': subtraction, 'caller_store': caller_store(result, cap)}
