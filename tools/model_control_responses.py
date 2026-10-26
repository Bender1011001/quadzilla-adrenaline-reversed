"""Arithmetic reference for the original 0x53A2..0x55A6 response slice."""
from fractions import Fraction

from model_soft_float import binary, category, convert, encode, to_integer

MASK = 0xFFFFFFFF


def response_values(c):
    """Return expected byte stores, filter buffers and the derived state word.

    Float source words must be finite. Intermediate operations use the existing
    exact-rational float model, preserving binary32/binary64 rounding points.
    Exception/status-byte updates are outside this reference.
    """
    if any(category(c[name], 32) != 'finite' for name in ('ratio_numerator', 'ratio_denominator')):
        raise ValueError('response reference requires finite ratio source words')
    out = {}
    def put(address, value, width=1):
        for i in range(width):
            out[address+i] = (value >> (8*i)) & 255
    raw, scalar = (c['raw_capture'], c['capture_scalar']) if c['source_select'] else (c['raw_analog'], c['analog_scalar'])
    pct = 100*min(raw, 4095)//4095
    put(0x200789, c['clamp_flag']); put(0x200788, c['write_flag'])
    put(0x200BB8, raw, 2); put(0x200BC2, pct)
    put(0x200BB6, ((100*scalar) & MASK) >> 7, 2)
    put(0x200BC6, c['adc4'], 2); put(0x200BBB, c['state_total'])
    first = ((c['multiplier0']*pct) & MASK)//100
    second = ((c['multiplier1']*c['stretch']) & MASK)//2200
    derived = ((first+second)*c['capture']*3) & MASK
    denominator = convert(binary('div', encode(Fraction(derived), 64), 0x414CE16100000000, 64), 64, 32)
    if denominator & 0x7FFFFFFF:
        numerator = convert(binary('div', encode(Fraction(c['previous_response']), 64), 0x404E000000000000, 64), 64, 32)
        ratio = binary('div', numerator, denominator, 32)
    else:
        ratio = 0x42C7FAE1
    scaled = binary('mul', 0x42C80000, ratio, 32)
    sample = min(to_integer(scaled, 32, False), 9999)
    filter0 = c['filter0'][1:] + [sample]
    average = (sum(filter0) & MASK) >> 5
    ratio1 = binary('div', c['ratio_numerator'], c['ratio_denominator'], 32) if c['ratio_denominator'] & 0x7FFFFFFF else 0
    converted = to_integer(ratio1, 32, True)
    put(0x200BD6, converted, 3)
    put(0x200BD4, c['timer_state'], 2); put(0x200BD2, average, 2)
    put(0x200BBA, c['adc6']); put(0x200BC8, c['adc5'], 2)
    put(0x200BBC, (c['source_offset0']+40) & MASK, 2)
    put(0x200BCB, c['capture'], 2)
    put(0x200BCA, min(c['source_clamp'], 255))
    filter1 = c['filter1'][1:]+[c['byte_source']] if c['filter_enable'] == 1 else c['filter1'][:]
    value = ((sum(filter1) & MASK) >> 5) if c['filter_enable'] == 1 else c['byte_source']
    put(0x200BC1, value)
    offset = (c['source_offset1']+40) & MASK
    put(0x200BBE, 0 if offset & 0x80000000 else offset)
    put(0x200BC3, c['new_response'])
    put(0x200BC0, c['percent_word']); put(0x200BBF, c['byte_source1'])
    return {'bytes': {hex(a): v for a, v in sorted(out.items())},
            'derived': derived, 'filter0': filter0, 'filter1': filter1,
            'sample': sample, 'average': average, 'ratio_integer': converted,
            'ratio_denominator_bits': hex(denominator), 'ratio_bits': hex(ratio), 'scaled_bits': hex(scaled)}
