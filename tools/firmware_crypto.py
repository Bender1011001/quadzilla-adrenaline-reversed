#!/usr/bin/env python3
"""Quadzilla Adrenaline ``.qz`` firmware-update container: decrypt, encrypt, verify.

The vendor updater (X2Updater / ``Quadzilla.dll``, class ``X2Crypt``) protects the
Intel HEX firmware file with an 8-byte key using a ciphertext-feedback XOR chain::

    E[i] = P[i] ^ K[i % 8] ^ E[i-1]        (E[-1] = 0)
    P[i] = E[i] ^ K[i % 8] ^ E[i-1]

The 8-byte key (``.pwk``) is derived from an 8-byte password (``.pwd``) by
``generate_password_key`` below. Both files, the algorithm and the ciphertext ship in
the same installer package, so this is obfuscation rather than confidentiality; see
docs/SECURITY_ASSESSMENT.md (findings F1 and F2).

The key-derivation table is the standard AES ``Te0`` round table. It is computed here
from the Rijndael S-box and checked against the vendor's table by the test-suite.
The cipher itself uses no AES rounds.

Only static analysis of the update package was performed. Nothing in this module
has been tested against a device, and the device-side acceptance rules are unknown.

Usage::

    python firmware_crypto.py decrypt  FirmwareUpdate.qz out.hex  --pwd-file FirmwareUpdate.pwd
    python firmware_crypto.py decrypt  FirmwareUpdate.qz out.hex  --pwk-file FirmwareUpdate.pwk
    python firmware_crypto.py decrypt  FirmwareUpdate.qz out.hex  --key 111d6f202ee5a103 --bin out.bin
    python firmware_crypto.py encrypt  image.hex out.qz --key <16 hex chars>
    python firmware_crypto.py verify   FirmwareUpdate.qz --pwd-file FirmwareUpdate.pwd
    python firmware_crypto.py recover-key FirmwareUpdate.qz
    python firmware_crypto.py info     out.hex
"""
from __future__ import annotations

import argparse
import math
import sys

KEY_LEN = 8


# --- key derivation -------------------------------------------------------

def _aes_sbox() -> list[int]:
    """Rijndael S-box, generated (multiplicative inverse + affine transform)."""
    sbox = [0] * 256
    p = q = 1
    while True:
        p = p ^ ((p << 1) & 0xFF) ^ (0x1B if p & 0x80 else 0)  # p *= 3 in GF(2^8)
        q ^= (q << 1) & 0xFF
        q ^= (q << 2) & 0xFF
        q ^= (q << 4) & 0xFF
        if q & 0x80:
            q ^= 0x09                                          # q /= 3 in GF(2^8)
        rot = lambda v, n: ((v << n) | (v >> (8 - n))) & 0xFF
        sbox[p] = (q ^ rot(q, 1) ^ rot(q, 2) ^ rot(q, 3) ^ rot(q, 4) ^ 0x63) & 0xFF
        if p == 1:
            break
    sbox[0] = 0x63
    return sbox


def _build_te0() -> list[int]:
    sbox = _aes_sbox()

    def xtime(a: int) -> int:
        return ((a << 1) ^ 0x1B) & 0xFF if a & 0x80 else (a << 1) & 0xFF

    return [
        (xtime(s) << 24) | (s << 16) | (s << 8) | (xtime(s) ^ s)
        for s in sbox
    ]


#: X2Crypt's ``e_table`` (identical to the AES ``Te0`` table).
E_TABLE = _build_te0()


def generate_password_key(password: bytes) -> bytes:
    """Derive the 8-byte key (``.pwk``) from the 8-byte password (``.pwd``).

    Port of ``X2Crypt.GeneratePasswordKey``. Byte ``password[row*4 + col]`` indexes
    ``E_TABLE``; entries are rotated left by ``8*col`` bits and XOR-folded per row.
    """
    if len(password) != KEY_LEN:
        raise ValueError(f"password must be {KEY_LEN} bytes, got {len(password)}")
    acc = [0, 0]
    for col in range(4):
        for row in range(2):
            value = E_TABLE[password[row * 4 + col]]
            if col:
                shift = col * 8
                value = ((value << shift) | (value >> (32 - shift))) & 0xFFFFFFFF
            acc[row] = value if col == 0 else acc[row] ^ value
    key = bytearray(KEY_LEN)
    for col in range(4):
        for row in range(2):
            key[row * 4 + col] = (acc[row] >> (8 * col)) & 0xFF
    return bytes(key)


# --- cipher ---------------------------------------------------------------

def _check_key(key: bytes) -> None:
    if len(key) != KEY_LEN:
        raise ValueError(
            f"key must be exactly {KEY_LEN} bytes, got {len(key)} "
            "(truncated .pwk/.pwd files from a damaged extraction are a common cause)"
        )


def decrypt_chain(ciphertext: bytes, key: bytes) -> bytes:
    _check_key(key)
    out = bytearray(len(ciphertext))
    prev = 0
    for i, c in enumerate(ciphertext):
        out[i] = c ^ key[i % KEY_LEN] ^ prev
        prev = c
    return bytes(out)


def encrypt_chain(plaintext: bytes, key: bytes) -> bytes:
    _check_key(key)
    out = bytearray(len(plaintext))
    prev = 0
    for i, p in enumerate(plaintext):
        prev = out[i] = p ^ key[i % KEY_LEN] ^ prev
    return bytes(out)


def recover_key_known_plaintext(ciphertext: bytes, known: bytes = b":1040000") -> bytes:
    """Recover the key from ciphertext alone using the predictable Intel HEX header.

    Every Intel HEX record starts with ``:``; the image is loaded at 0x4000 with
    16-byte records, so the first 8 plaintext bytes are ``:1040000``. Since
    ``K[i] = P[i] ^ E[i] ^ E[i-1]``, eight known bytes give the whole key, which shows
    that secrecy of the key files adds nothing.
    """
    if len(known) < KEY_LEN or len(ciphertext) < KEY_LEN:
        raise ValueError("need at least 8 bytes of ciphertext and known plaintext")
    key = bytearray(KEY_LEN)
    prev = 0
    for i in range(KEY_LEN):
        key[i] = known[i] ^ ciphertext[i] ^ prev
        prev = ciphertext[i]
    return bytes(key)


# --- Intel HEX ------------------------------------------------------------

def parse_ihex(text: str) -> tuple[dict[int, int], int, int]:
    """Parse Intel HEX. Returns ``(address -> byte, record_count, checksum_errors)``."""
    memory: dict[int, int] = {}
    records = bad = 0
    base = 0
    for line in text.replace("\r", "").split("\n"):
        line = line.strip()
        if not line.startswith(":"):
            continue
        raw = bytes.fromhex(line[1:])
        records += 1
        if sum(raw) & 0xFF:
            bad += 1
        count, addr, rtype = raw[0], (raw[1] << 8) | raw[2], raw[3]
        data = raw[4:4 + count]
        if rtype == 0x00:
            for offset, byte in enumerate(data):
                memory[base + addr + offset] = byte
        elif rtype == 0x04:
            base = ((data[0] << 8) | data[1]) << 16
    return memory, records, bad


def ihex_to_image(memory: dict[int, int], fill: int = 0xFF) -> tuple[int, bytes]:
    if not memory:
        raise ValueError("no data records")
    lo, hi = min(memory), max(memory)
    return lo, bytes(memory.get(a, fill) for a in range(lo, hi + 1))


# --- reporting ------------------------------------------------------------

def describe(data: bytes, label: str = "") -> None:
    prefix = f"[{label}] " if label else ""
    print(f"{prefix}size: {len(data)} bytes")
    counts = [0] * 256
    for b in data:
        counts[b] += 1
    entropy = -sum((c / len(data)) * math.log2(c / len(data)) for c in counts if c) if data else 0.0
    print(f"{prefix}entropy: {entropy:.2f} bits/byte")
    if data[:1] == b":":
        memory, records, bad = parse_ihex(data.decode("ascii", "replace"))
        if memory:
            lo, image = ihex_to_image(memory)
            print(f"{prefix}Intel HEX: {records} records, {bad} checksum errors, "
                  f"image 0x{lo:X}-0x{lo + len(image) - 1:X} ({len(image)} bytes)")


# --- CLI ------------------------------------------------------------------

def _read(path: str) -> bytes:
    with open(path, "rb") as fh:
        return fh.read()


def _key_from_args(args: argparse.Namespace) -> bytes:
    if args.key:
        return bytes.fromhex(args.key)
    if args.pwk_file:
        return _read(args.pwk_file)
    if args.pwd_file:
        return generate_password_key(_read(args.pwd_file))
    sys.exit("specify one of --key, --pwk-file, --pwd-file")


def cmd_decrypt(args: argparse.Namespace) -> None:
    data = _read(args.input)
    key = _key_from_args(args)
    plain = decrypt_chain(data, key)
    with open(args.output, "wb") as fh:
        fh.write(plain)
    print(f"[+] {args.input} ({len(data)} bytes) -> {args.output}")
    describe(plain, "plaintext")
    if args.bin:
        memory, _, _ = parse_ihex(plain.decode("ascii", "replace"))
        base, image = ihex_to_image(memory)
        with open(args.bin, "wb") as fh:
            fh.write(image)
        print(f"[+] binary image: {args.bin} (load address 0x{base:X}, {len(image)} bytes)")


def cmd_encrypt(args: argparse.Namespace) -> None:
    plain = _read(args.input)
    key = _key_from_args(args)
    encrypted = encrypt_chain(plain, key)
    if decrypt_chain(encrypted, key) != plain:
        sys.exit("roundtrip check failed")
    with open(args.output, "wb") as fh:
        fh.write(encrypted)
    print(f"[+] {args.input} ({len(plain)} bytes) -> {args.output} (roundtrip verified)")


def cmd_verify(args: argparse.Namespace) -> None:
    data = _read(args.input)
    key = _key_from_args(args)
    plain = decrypt_chain(data, key)
    ok = encrypt_chain(plain, key) == data
    print("[+] re-encrypting the decrypted file reproduces the original" if ok
          else "[-] roundtrip mismatch")
    memory, records, bad = parse_ihex(plain.decode("ascii", "replace"))
    print(f"[{'+' if memory and not bad else '-'}] Intel HEX: {records} records, {bad} checksum errors")
    sys.exit(0 if ok and memory and not bad else 1)


def cmd_recover_key(args: argparse.Namespace) -> None:
    key = recover_key_known_plaintext(_read(args.input))
    plain = decrypt_chain(_read(args.input), key)
    _, records, bad = parse_ihex(plain.decode("ascii", "replace"))
    print(f"key (from known plaintext): {key.hex()}")
    print(f"validation: {records} Intel HEX records, {bad} checksum errors")


def cmd_info(args: argparse.Namespace) -> None:
    describe(_read(args.input))


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    sub = parser.add_subparsers(dest="command", required=True)

    def add_key_args(p: argparse.ArgumentParser) -> None:
        p.add_argument("--key", help="8-byte key as 16 hex characters")
        p.add_argument("--pwk-file", help="8-byte derived key file (.pwk)")
        p.add_argument("--pwd-file", help="8-byte password file (.pwd); key is derived")

    p = sub.add_parser("decrypt", help="decrypt a .qz file to Intel HEX")
    p.add_argument("input"); p.add_argument("output")
    p.add_argument("--bin", help="also write the flat binary image")
    add_key_args(p); p.set_defaults(func=cmd_decrypt)

    p = sub.add_parser("encrypt", help="encrypt an Intel HEX file into .qz form")
    p.add_argument("input"); p.add_argument("output")
    add_key_args(p); p.set_defaults(func=cmd_encrypt)

    p = sub.add_parser("verify", help="check decrypt/encrypt roundtrip and HEX checksums")
    p.add_argument("input"); add_key_args(p); p.set_defaults(func=cmd_verify)

    p = sub.add_parser("recover-key", help="recover the key from ciphertext alone")
    p.add_argument("input"); p.set_defaults(func=cmd_recover_key)

    p = sub.add_parser("info", help="describe a file")
    p.add_argument("input"); p.set_defaults(func=cmd_info)

    args = parser.parse_args(argv)
    try:
        args.func(args)
    except (ValueError, OSError) as exc:
        sys.exit(f"error: {exc}")


if __name__ == "__main__":
    main()
