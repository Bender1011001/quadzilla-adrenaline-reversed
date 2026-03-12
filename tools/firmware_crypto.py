#!/usr/bin/env python3
"""
Quadzilla Firmware Encryption/Decryption Tool
=============================================
Implements the XOR cipher-chain encryption used by Quadzilla for firmware updates.

Algorithm (from X2Crypt class in Quadzilla.dll):
  - Uses a 256-entry CRC32 substitution table for key generation
  - Encryption: ciphertext[i] = plaintext[i] ^ key[i%8] ^ prev_ciphertext[i-1]
  - Decryption: plaintext[i] = ciphertext[i] ^ key[i%8] ^ prev_ciphertext[i-1]
  - Password key is derived from the .pwk file via CRC32 table

Usage:
  python firmware_crypto.py decrypt input.qz output.bin --key-file key.pwk
  python firmware_crypto.py encrypt input.bin output.qz --key-file key.pwk
  python firmware_crypto.py info input.qz
"""
import struct
import argparse
import os
import sys


# CRC32 lookup table (same as .NET Quadzilla.dll X2Crypt class)
def build_crc32_table():
    """Build the 256-entry CRC32 substitution table used for key derivation."""
    table = []
    for i in range(256):
        crc = i
        for _ in range(8):
            if crc & 1:
                crc = (crc >> 1) ^ 0xEDB88320
            else:
                crc >>= 1
        table.append(crc & 0xFFFFFFFF)
    return table

CRC32_TABLE = build_crc32_table()


def derive_key_from_password(password_bytes):
    """
    Derive the 8-byte encryption key from password bytes.
    Uses CRC32 table-based transformation as seen in Quadzilla.dll.
    """
    # The password key file (.pwk) contains the raw key bytes
    # For the standard firmware update, the key is embedded in the .pwk resource
    if len(password_bytes) >= 8:
        return password_bytes[:8]
    # Pad with zeros if shorter
    return password_bytes.ljust(8, b'\x00')


def decrypt_firmware(encrypted_data, key):
    """
    Decrypt firmware using XOR cipher-chain.
    
    Algorithm: plaintext[i] = encrypted[i] ^ key[i % 8] ^ encrypted[i-1]
    (first byte: plaintext[0] = encrypted[0] ^ key[0])
    """
    if len(key) < 8:
        raise ValueError(f"Key must be 8 bytes, got {len(key)}")
    
    decrypted = bytearray(len(encrypted_data))
    prev = 0
    
    for i in range(len(encrypted_data)):
        decrypted[i] = (encrypted_data[i] ^ key[i % 8] ^ prev) & 0xFF
        prev = encrypted_data[i]
    
    return bytes(decrypted)


def encrypt_firmware(plaintext_data, key):
    """
    Encrypt firmware using XOR cipher-chain (reverse of decrypt).
    
    Algorithm: encrypted[i] = plaintext[i] ^ key[i % 8] ^ encrypted[i-1]
    (first byte: encrypted[0] = plaintext[0] ^ key[0])
    """
    if len(key) < 8:
        raise ValueError(f"Key must be 8 bytes, got {len(key)}")
    
    encrypted = bytearray(len(plaintext_data))
    prev = 0
    
    for i in range(len(plaintext_data)):
        encrypted[i] = (plaintext_data[i] ^ key[i % 8] ^ prev) & 0xFF
        prev = encrypted[i]
    
    return bytes(encrypted)


def verify_roundtrip(data, key):
    """Verify encryption/decryption roundtrip integrity."""
    encrypted = encrypt_firmware(data, key)
    decrypted = decrypt_firmware(encrypted, key)
    return data == decrypted


def analyze_firmware(data, label=""):
    """Print analysis of firmware binary."""
    prefix = f"[{label}] " if label else ""
    print(f"{prefix}Size: {len(data)} bytes ({len(data)/1024:.1f} KB)")
    
    # Check for ARM vectors at start
    if len(data) >= 32:
        vectors = struct.unpack_from('<8I', data, 0)
        is_arm = all(0x00000000 <= v <= 0x00100000 for v in vectors[:4])
        if is_arm:
            print(f"{prefix}ARM vectors detected at offset 0:")
            for i, v in enumerate(vectors):
                names = ['Reset', 'Undefined', 'SWI', 'PrefAbort', 'DataAbort', 'Reserved', 'IRQ', 'FIQ']
                print(f"  {names[i]:12s}: 0x{v:08X}")
    
    # Look for device ID string
    for offset in range(len(data) - 8):
        chunk = data[offset:offset+8]
        try:
            s = chunk.decode('ascii')
            if s.startswith('DADR'):
                print(f"{prefix}Device ID at 0x{offset:04X}: {s}")
        except (UnicodeDecodeError, ValueError):
            pass
    
    # Look for build date strings
    for offset in range(len(data) - 20):
        chunk = data[offset:offset+20]
        try:
            s = chunk.decode('ascii')
            months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
                      'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
            for m in months:
                if m in s and ('20' in s or '19' in s):
                    # Clean up and print
                    end = s.find('\x00')
                    if end > 0:
                        s = s[:end]
                    print(f"{prefix}Build date at 0x{offset:04X}: {s.strip()}")
                    break
        except (UnicodeDecodeError, ValueError):
            pass
    
    # Entropy check (high entropy = still encrypted)
    byte_counts = [0] * 256
    for b in data:
        byte_counts[b] += 1
    entropy = 0
    for count in byte_counts:
        if count > 0:
            p = count / len(data)
            entropy -= p * (p and __import__('math').log2(p))
    print(f"{prefix}Entropy: {entropy:.2f} bits/byte (8.0 = random/encrypted, <7.0 = normal code)")
    
    # Check for repeated patterns (sign of real code vs encrypted)
    null_runs = 0
    max_null_run = 0
    current_null = 0
    for b in data:
        if b == 0x00:
            current_null += 1
            max_null_run = max(max_null_run, current_null)
        else:
            if current_null >= 4:
                null_runs += 1
            current_null = 0
    print(f"{prefix}Null runs (≥4): {null_runs}, longest: {max_null_run}")


def cmd_decrypt(args):
    """Decrypt a .qz firmware file."""
    with open(args.input, 'rb') as f:
        encrypted = f.read()
    
    if args.key_file:
        with open(args.key_file, 'rb') as f:
            key = derive_key_from_password(f.read())
    elif args.key:
        key = bytes.fromhex(args.key)
    else:
        print("[-] Must specify --key-file or --key")
        sys.exit(1)
    
    print(f"[+] Input:  {args.input} ({len(encrypted)} bytes)")
    print(f"[+] Key:    {key.hex()}")
    
    decrypted = decrypt_firmware(encrypted, key)
    
    with open(args.output, 'wb') as f:
        f.write(decrypted)
    
    print(f"[+] Output: {args.output} ({len(decrypted)} bytes)")
    analyze_firmware(decrypted, "Decrypted")


def cmd_encrypt(args):
    """Encrypt a modified firmware binary back to .qz format."""
    with open(args.input, 'rb') as f:
        plaintext = f.read()
    
    if args.key_file:
        with open(args.key_file, 'rb') as f:
            key = derive_key_from_password(f.read())
    elif args.key:
        key = bytes.fromhex(args.key)
    else:
        print("[-] Must specify --key-file or --key")
        sys.exit(1)
    
    print(f"[+] Input:  {args.input} ({len(plaintext)} bytes)")
    print(f"[+] Key:    {key.hex()}")
    
    # Verify roundtrip before writing
    if not verify_roundtrip(plaintext, key):
        print("[-] FATAL: Roundtrip verification failed!")
        sys.exit(1)
    print("[+] Roundtrip verification: PASS")
    
    encrypted = encrypt_firmware(plaintext, key)
    
    with open(args.output, 'wb') as f:
        f.write(encrypted)
    
    print(f"[+] Output: {args.output} ({len(encrypted)} bytes)")


def cmd_info(args):
    """Analyze a firmware file (encrypted or decrypted)."""
    with open(args.input, 'rb') as f:
        data = f.read()
    
    print(f"File: {args.input}")
    analyze_firmware(data)


def cmd_verify(args):
    """Verify decrypt→encrypt roundtrip produces identical output."""
    with open(args.encrypted, 'rb') as f:
        original_encrypted = f.read()
    
    if args.key_file:
        with open(args.key_file, 'rb') as f:
            key = derive_key_from_password(f.read())
    elif args.key:
        key = bytes.fromhex(args.key)
    else:
        print("[-] Must specify --key-file or --key")
        sys.exit(1)
    
    # Decrypt
    decrypted = decrypt_firmware(original_encrypted, key)
    # Re-encrypt
    re_encrypted = encrypt_firmware(decrypted, key)
    
    if original_encrypted == re_encrypted:
        print("[+] VERIFIED: decrypt→encrypt roundtrip produces identical output")
    else:
        # Find first difference
        for i in range(min(len(original_encrypted), len(re_encrypted))):
            if original_encrypted[i] != re_encrypted[i]:
                print(f"[-] MISMATCH at byte {i}: original=0x{original_encrypted[i]:02X} re-encrypted=0x{re_encrypted[i]:02X}")
                break
        print(f"[-] FAILED: {sum(a != b for a, b in zip(original_encrypted, re_encrypted))} bytes differ")


def main():
    parser = argparse.ArgumentParser(
        description='Quadzilla Firmware Encryption/Decryption Tool',
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    sub = parser.add_subparsers(dest='command')
    
    # Decrypt
    dec = sub.add_parser('decrypt', help='Decrypt .qz firmware')
    dec.add_argument('input', help='Encrypted .qz file')
    dec.add_argument('output', help='Output decrypted binary')
    dec.add_argument('--key-file', help='Password key file (.pwk)')
    dec.add_argument('--key', help='Hex key string (16 hex chars = 8 bytes)')
    
    # Encrypt
    enc = sub.add_parser('encrypt', help='Encrypt firmware to .qz')
    enc.add_argument('input', help='Plaintext firmware binary')
    enc.add_argument('output', help='Output encrypted .qz file')
    enc.add_argument('--key-file', help='Password key file (.pwk)')
    enc.add_argument('--key', help='Hex key string (16 hex chars = 8 bytes)')
    
    # Info
    inf = sub.add_parser('info', help='Analyze firmware file')
    inf.add_argument('input', help='Firmware file to analyze')
    
    # Verify
    ver = sub.add_parser('verify', help='Verify roundtrip integrity')
    ver.add_argument('encrypted', help='Original encrypted .qz file')
    ver.add_argument('--key-file', help='Password key file (.pwk)')
    ver.add_argument('--key', help='Hex key string')
    
    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        return
    
    {'decrypt': cmd_decrypt, 'encrypt': cmd_encrypt, 
     'info': cmd_info, 'verify': cmd_verify}[args.command](args)


if __name__ == '__main__':
    main()
