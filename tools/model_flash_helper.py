"""Arithmetic model of the relocated helper; never opens hardware or programs flash."""


def staged_word_count(length: int) -> int:
    """0xB136 uses signed CMP/BLT and stops after 128 four-byte writes."""
    if not 0 <= length <= 0xFFFFFFFF:
        raise ValueError("length must be a 32-bit register value")
    signed = length if length < 0x80000000 else length-0x100000000
    return min(128, (signed+3)//4) if signed > 0 else 0


def page_command(address: int) -> int:
    """Literal arithmetic only: subtract flash base, shift seven, mask selector."""
    if not 0 <= address <= 0xFFFFFFFF:
        raise ValueError("address must be a 32-bit register value")
    selector = ((address-0x100000) & 0xFFFFFFFF) >> 7
    return 0x5A000001 | ((selector << 8) & 0x3FF00)
