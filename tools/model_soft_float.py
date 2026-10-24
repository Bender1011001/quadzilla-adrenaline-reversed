"""Exact rational references for bounded soft-float execution comparisons.

This defines mathematical comparison behavior, not a claim that every firmware
NaN payload, exception flag or rounding path implements IEEE 754 completely.
"""
from fractions import Fraction


def fields(bits, width):
    fraction_bits, exponent_bits = (23, 8) if width == 32 else (52, 11)
    sign = bits >> (width-1)
    exponent = (bits >> fraction_bits) & ((1 << exponent_bits)-1)
    fraction = bits & ((1 << fraction_bits)-1)
    return sign, exponent, fraction, fraction_bits, exponent_bits


def category(bits, width):
    _, exponent, fraction, _, eb = fields(bits, width)
    if exponent == (1 << eb)-1:
        return "nan" if fraction else "infinity"
    return "finite"


def rational(bits, width):
    sign, exponent, fraction, fb, eb = fields(bits, width)
    if category(bits, width) != "finite":
        raise ValueError("nonfinite input")
    bias = (1 << (eb-1))-1
    mantissa = fraction | ((1 << fb) if exponent else 0)
    shift = (exponent or 1)-bias-fb
    value = Fraction(mantissa << shift, 1) if shift >= 0 else Fraction(mantissa, 1 << -shift)
    return -value if sign else value


def round_even(numerator, denominator):
    q, r = divmod(numerator, denominator)
    return q+int(2*r > denominator or (2*r == denominator and q % 2 == 1))


def infinity(sign, width):
    fb, eb = (23, 8) if width == 32 else (52, 11)
    return (sign << (width-1)) | (((1 << eb)-1) << fb)


def encode(value, width, zero_sign=0):
    fb, eb = (23, 8) if width == 32 else (52, 11)
    if not value:
        return zero_sign << (width-1)
    sign = int(value < 0)
    value = abs(value)
    n, d = value.numerator, value.denominator
    exponent = n.bit_length()-d.bit_length()
    below_power = (n < d << exponent) if exponent >= 0 else (n << -exponent < d)
    if below_power:
        exponent -= 1
    bias = (1 << (eb-1))-1
    scale = max(exponent, 1-bias)-fb
    mantissa = round_even(n, d << scale) if scale >= 0 else round_even(n << -scale, d)
    if mantissa >= 1 << (fb+1):
        mantissa >>= 1
        exponent += 1
    if exponent > bias:
        return infinity(sign, width)
    encoded_exponent = max(exponent+bias, 1) if mantissa >= 1 << fb else 0
    return (sign << (width-1)) | (encoded_exponent << fb) | (mantissa & ((1 << fb)-1))


def binary(operation, a, b, width):
    """Return expected bits, or None when only NaN classification is compared."""
    if operation == "sub":
        return binary("add", a, b ^ (1 << (width-1)), width)
    ca, cb = category(a, width), category(b, width)
    sa, sb = a >> (width-1), b >> (width-1)
    if "nan" in (ca, cb):
        return None
    sign = sa ^ sb
    if operation == "add":
        if ca == cb == "infinity" and sign:
            return None
        if ca == "infinity":
            return infinity(sa, width)
        if cb == "infinity":
            return infinity(sb, width)
        return encode(rational(a, width)+rational(b, width), width, sa & sb)
    va = rational(a, width) if ca == "finite" else None
    vb = rational(b, width) if cb == "finite" else None
    if operation == "mul":
        if (ca == "infinity" and vb == 0) or (cb == "infinity" and va == 0):
            return None
        if "infinity" in (ca, cb):
            return infinity(sign, width)
        return encode(va*vb, width, sign)
    if operation == "div":
        if ca == cb == "infinity" or va == vb == 0:
            return None
        if ca == "infinity" or vb == 0:
            return infinity(sign, width)
        if cb == "infinity":
            return sign << (width-1)
        return encode(va/vb, width, sign)
    raise ValueError("unknown operation")


def convert(bits, source_width, target_width):
    kind = category(bits, source_width)
    sign = bits >> (source_width-1)
    if kind == "nan":
        return None
    if kind == "infinity":
        return infinity(sign, target_width)
    return encode(rational(bits, source_width), target_width, sign)


def to_integer(bits, width, signed):
    sign = bits >> (width-1)
    kind = category(bits, width)
    if kind == "finite":
        value = int(rational(bits, width))
    else:
        # Documented runtime saturation policy; not a mathematical NaN value.
        value = -(1 << 64) if sign else 1 << 64
    if signed:
        return min(max(value, -(1 << 31)), (1 << 31)-1) & 0xFFFFFFFF
    return min(max(value, 0), 0xFFFFFFFF)
