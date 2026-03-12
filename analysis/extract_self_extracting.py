#!/usr/bin/env python3
"""
Extract embedded files from the Quadzilla ADR9802 self-extracting EXE.

The EXE contains a FirmwareUpdate/ directory with the actual firmware updater,
firmware payload, DLLs, and other assets. This script extracts everything
by finding the embedded archive within the PE.

Strategy:
1. Look for PK (ZIP) or other archive signatures after the PE sections
2. Try standard extraction (7z, ZIP) 
3. Also decode the base64 bzip2 payloads found in the binary
4. Extract and analyze the .Smt file format
"""
import os
import sys
import struct
import base64
import bz2
import re
import zipfile
import io

EXE_PATH = r'ADR9802v2.8.4.exe'
SMT_PATH = r'S03V126CDR12A.Smt'
OUT_DIR = r'extracted'

def find_pe_overlay_offset(data):
    """Find where the PE file-mapped sections end (overlay starts)."""
    if data[:2] != b'MZ':
        return None
    e_lfanew = struct.unpack('<I', data[0x3C:0x40])[0]
    if data[e_lfanew:e_lfanew+4] != b'PE\x00\x00':
        return None
    
    # COFF header
    num_sections = struct.unpack('<H', data[e_lfanew+6:e_lfanew+8])[0]
    size_opt_hdr = struct.unpack('<H', data[e_lfanew+20:e_lfanew+22])[0]
    
    # Section headers start after optional header
    section_start = e_lfanew + 24 + size_opt_hdr
    
    max_file_end = 0
    for i in range(num_sections):
        sec_off = section_start + i * 40
        sec_data = data[sec_off:sec_off+40]
        if len(sec_data) < 40:
            break
        name = sec_data[:8].rstrip(b'\x00').decode('ascii', errors='replace')
        raw_size = struct.unpack('<I', sec_data[16:20])[0]
        raw_offset = struct.unpack('<I', sec_data[20:24])[0]
        end = raw_offset + raw_size
        print(f"  Section '{name}': offset=0x{raw_offset:X}, size=0x{raw_size:X}, end=0x{end:X}")
        if end > max_file_end:
            max_file_end = end
    
    return max_file_end

def extract_zip_archives(data, out_dir):
    """Find and extract ZIP archives embedded in the binary."""
    idx = 0
    zip_count = 0
    while True:
        idx = data.find(b'PK\x03\x04', idx)
        if idx == -1:
            break
        print(f"  ZIP local header at offset 0x{idx:X}")
        # Try to open as zip from this offset
        try:
            zf = zipfile.ZipFile(io.BytesIO(data[idx:]))
            names = zf.namelist()
            print(f"    Contains {len(names)} files:")
            for n in names[:30]:
                info = zf.getinfo(n)
                print(f"      {n} ({info.file_size} bytes)")
            
            zip_out = os.path.join(out_dir, f'zip_archive_{zip_count}')
            os.makedirs(zip_out, exist_ok=True)
            zf.extractall(zip_out)
            print(f"    Extracted to: {zip_out}")
            zip_count += 1
            zf.close()
        except Exception as e:
            print(f"    Not a valid ZIP from this offset: {e}")
        idx += 4
    return zip_count

def decode_base64_payloads(data, out_dir):
    """Find and decode base64-encoded bzip2 streams."""
    # Look for the c4aeUs pattern (base64 bzip2)
    text = data.decode('ascii', errors='ignore')
    # Pattern: long base64 strings
    b64_pattern = re.compile(r'[A-Za-z0-9+/]{100,}={0,2}')
    
    count = 0
    for match in b64_pattern.finditer(text):
        b64_str = match.group()
        offset = match.start()
        try:
            decoded = base64.b64decode(b64_str)
            out_name = os.path.join(out_dir, f'b64_payload_{count:02d}.bin')
            with open(out_name, 'wb') as f:
                f.write(decoded)
            print(f"  Base64 at 0x{offset:X}: {len(b64_str)} chars -> {len(decoded)} bytes decoded -> {out_name}")
            
            # Try bzip2 decompress
            if decoded[:3] == b'BZh':
                try:
                    decompressed = bz2.decompress(decoded)
                    out_dec = os.path.join(out_dir, f'b64_payload_{count:02d}_decompressed.bin')
                    with open(out_dec, 'wb') as f:
                        f.write(decompressed)
                    print(f"    BZip2 decompressed: {len(decompressed)} bytes -> {out_dec}")
                except Exception as e:
                    print(f"    BZip2 decompress failed: {e}")
            
            count += 1
        except Exception as e:
            pass
    return count

def extract_named_files(data, out_dir):
    """
    Extract files referenced by their FirmwareUpdate/ path names.
    The EXE likely uses a proprietary self-extractor format.
    We look for file headers that include the path strings.
    """
    # Find all FirmwareUpdate/ path references
    paths = []
    idx = 0
    while True:
        idx = data.find(b'FirmwareUpdate/', idx)
        if idx == -1:
            break
        # Read the path string
        end = data.find(b'\x00', idx)
        if end == -1:
            end = idx + 200
        path_str = data[idx:end].decode('ascii', errors='replace')
        paths.append((idx, path_str))
        idx += 1
    
    print(f"\n  Found {len(paths)} FirmwareUpdate/ path references:")
    for offset, p in paths:
        # Show hex context around the path
        ctx_start = max(0, offset - 32)
        ctx = data[ctx_start:offset]
        print(f"    0x{offset:06X}: {p}")
        print(f"      Context before: {ctx.hex()}")

def analyze_smt_file(path, out_dir):
    """Analyze the SmartyFile format."""
    print(f"\n{'='*72}")
    print(f"ANALYZING .Smt FILE: {path}")
    with open(path, 'rb') as f:
        data = f.read()
    
    print(f"Size: {len(data)} bytes")
    print(f"Header: {data[:16]}")
    
    # The header is 'SmartyFile000001' (16 bytes)
    header = data[:16].decode('ascii', errors='replace')
    print(f"Header text: '{header}'")
    
    # Show next few hundred bytes in hex
    print("After header (offset 0x10):")
    for i in range(16, min(512, len(data)), 16):
        h = ' '.join(f'{b:02x}' for b in data[i:i+16])
        a = ''.join(chr(b) if 32 <= b < 127 else '.' for b in data[i:i+16])
        print(f"  {i:08x}: {h:<48s} {a}")
    
    # Try to find gzip streams
    print(f"\nGzip signatures in .Smt:")
    idx = 0
    gz_count = 0
    while True:
        idx = data.find(b'\x1f\x8b\x08', idx)
        if idx == -1:
            break
        print(f"  offset 0x{idx:X}")
        gz_count += 1
        # Try to decompress
        import gzip
        try:
            decompressed = gzip.decompress(data[idx:idx+1024*1024])
            out_name = os.path.join(out_dir, f'smt_gz_{gz_count:02d}.bin')
            with open(out_name, 'wb') as f:
                f.write(decompressed)
            print(f"    Decompressed: {len(decompressed)} bytes -> {out_name}")
        except Exception as e:
            pass  # expected - most hits are false positives in compressed data
        idx += 1
        if gz_count >= 20:
            break
    print(f"  Total gzip signatures: {gz_count}")
    
    # Check if after the 16-byte header, the rest is a known archive format
    rest = data[16:]
    if rest[:2] == b'PK':
        print("  After header: ZIP archive!")
    elif rest[:3] == b'BZh':
        print("  After header: BZip2 stream!")
    elif rest[:2] == b'\x1f\x8b':
        print("  After header: Gzip stream!")
    else:
        print(f"  After header, first bytes: {rest[:16].hex()}")
        # Maybe XOR encrypted? Try XOR with common keys
        for key in range(1, 256):
            decrypted = bytes(b ^ key for b in rest[:16])
            if decrypted[:2] == b'PK' or decrypted[:3] == b'BZh' or decrypted[:2] == b'\x1f\x8b':
                print(f"  XOR key 0x{key:02X} reveals: {decrypted[:16].hex()} ({decrypted[:8]})")
        
        # Try byte-pair XOR
        print("  Trying pattern-based decryption...")
        # If it's Intel HEX, first char should be ':' (0x3A)
        # If rest[0] XOR key = 0x3A...
        key_candidate = rest[0] ^ 0x3A
        decrypted_sample = bytes(b ^ key_candidate for b in rest[:64])
        sample_text = decrypted_sample.decode('ascii', errors='replace')
        if ':' in sample_text[:5]:
            print(f"  XOR key 0x{key_candidate:02X} might reveal Intel HEX: {sample_text[:60]}")

def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    
    # Read EXE
    with open(EXE_PATH, 'rb') as f:
        exe_data = f.read()
    
    print("=" * 72)
    print(f"EXTRACTING FROM: {EXE_PATH} ({len(exe_data)} bytes)")
    
    # Step 1: Find PE overlay
    print("\n--- PE Section Map ---")
    overlay_offset = find_pe_overlay_offset(exe_data)
    if overlay_offset:
        overlay_size = len(exe_data) - overlay_offset
        print(f"PE overlay starts at: 0x{overlay_offset:X} ({overlay_size} bytes)")
        
        # Save the actual overlay
        overlay_data = exe_data[overlay_offset:]
        with open(os.path.join(OUT_DIR, 'pe_overlay.bin'), 'wb') as f:
            f.write(overlay_data)
        print(f"Saved overlay to: {os.path.join(OUT_DIR, 'pe_overlay.bin')}")
        
        # Check overlay header
        print(f"Overlay starts with: {overlay_data[:32].hex()}")
        print(f"Overlay ASCII: {overlay_data[:64].decode('ascii', errors='replace')}")
    
    # Step 2: Try ZIP extraction
    print("\n--- ZIP Archive Search ---")
    zip_count = extract_zip_archives(exe_data, OUT_DIR)
    print(f"ZIP archives extracted: {zip_count}")
    
    # Step 3: Base64 payloads
    print("\n--- Base64 Payload Search ---")
    b64_count = decode_base64_payloads(exe_data, OUT_DIR)
    print(f"Base64 payloads decoded: {b64_count}")
    
    # Step 4: Named file extraction
    print("\n--- Named File References ---")
    extract_named_files(exe_data, OUT_DIR)
    
    # Step 5: Analyze .Smt file
    analyze_smt_file(SMT_PATH, OUT_DIR)
    
    print("\n" + "=" * 72)
    print("EXTRACTION COMPLETE")
    print(f"Output directory: {os.path.abspath(OUT_DIR)}")

if __name__ == '__main__':
    main()
