"""Bounded reused-buffer/CRC model, not a serial receiver or MCU emulator."""
from x2com_crc import CHECK_VALUE, crc8


def overwrite_prefix(old: bytes, received: bytes) -> bytes:
    if len(old) != 16 or not 0 < len(received) <= 16:
        raise ValueError("expected a 16-byte region and nonempty received prefix")
    return received + old[len(received):]


def crc_status(buffer: bytes) -> int:
    """0x7BCC's check, with R1 supplied by header-low-nibble getter 0x7BF0.

    Firmware increments R1 before CRC; hence the low nibble is the CRC index.
    No actual received-count parameter is available on this reviewed call path.
    Return 3/4 models the CRC helper only, not full message-type acceptance.
    """
    if len(buffer) != 16:
        raise ValueError("model requires the whole 16-byte region")
    crc_index = buffer[0] & 15
    return 3 if crc8(buffer[:crc_index+1]) == CHECK_VALUE else 4
