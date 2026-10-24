"""Pure MCP2515 command/header decoding for offline firmware evidence.

Layout source: Microchip DS20001801K sections 3, 4, 11 and 12.
This module has no device I/O and does not model controller side effects.
"""


def decode_identifier(header):
    if len(header) != 4:
        raise ValueError("identifier header must contain four register bytes")
    sidh, sidl, eid8, eid0 = header
    standard = (sidh << 3) | (sidl >> 5)
    extended = bool(sidl & 8)
    identifier = ((standard << 18) | ((sidl & 3) << 16) | (eid8 << 8) | eid0
                  if extended else standard)
    return {"extended": extended, "identifier": hex(identifier)}


def decode_command(command):
    if not command:
        raise ValueError("empty command")
    opcode = command[0]
    result = {"opcode": hex(opcode), "length": len(command)}
    if opcode == 0xC0:
        if len(command) != 1:
            raise ValueError("RESET probe has trailing bytes")
        return result | {"operation": "RESET"}
    if opcode in (2, 3):
        if len(command) < 3:
            raise ValueError("register operation lacks address/data clocks")
        start = command[1]
        if start+len(command)-2 > 256:
            raise ValueError("register span wraps")
        return result | {"operation": "WRITE" if opcode == 2 else "READ",
                         "register_start": hex(start), "register_count": len(command)-2,
                         "write_data": command[2:].hex() if opcode == 2 else None}
    if opcode == 5:
        if len(command) != 4:
            raise ValueError("BIT MODIFY requires four bytes")
        return result | {"operation": "BIT_MODIFY", "register": hex(command[1]),
                         "mask": hex(command[2]), "data": hex(command[3])}
    if 0x40 <= opcode <= 0x45:
        selector = opcode-0x40
        buffer = selector//2
        data_only = bool(selector & 1)
        result |= {"operation": "LOAD_TX_BUFFER", "buffer": buffer,
                   "start": "data" if data_only else "identifier",
                   "register_start": hex((0x36 if data_only else 0x31)+16*buffer),
                   "payload": command[1:].hex()}
        if not data_only and len(command) >= 6:
            dlc = command[5] & 15
            result["frame"] = decode_identifier(command[1:5]) | {
                "dlc": dlc, "remote_request": bool(command[5] & 0x40),
                "data": command[6:6+dlc].hex(),
                "complete_data": dlc <= 8 and len(command) >= 6+dlc}
        return result
    if opcode in (0x90, 0x92, 0x94, 0x96):
        buffer = (opcode >> 2) & 1
        data_only = bool(opcode & 2)
        return result | {"operation": "READ_RX_BUFFER", "buffer": buffer,
                         "start": "data" if data_only else "identifier",
                         "register_start": hex((0x66 if data_only else 0x61)+16*buffer),
                         "response_bytes_after_opcode": len(command)-1}
    raise ValueError(f"unsupported opcode {opcode:#x}")
