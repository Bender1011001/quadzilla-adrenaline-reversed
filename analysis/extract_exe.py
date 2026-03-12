#!/usr/bin/env python3
"""Extract embedded files from the Quadzilla ADR9802 self-extracting EXE."""
import struct
import os
import sys
import base64
import bz2
import zipfile
import io
import re
import traceback

EXE_PATH = r'ADR9802v2.8.4.exe'
SMT_PATH = r'S03V126CDR12A.Smt'
OUT_DIR = r'extracted'

def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    
    with open(EXE_PATH, 'rb') as f:
        data = f.read()
    print(f"EXE size: {len(data)} bytes")
    
    # ---- PE overlay ----
    e_lfanew = struct.unpack('<I', data[0x3C:0x40])[0]
    num_sections = struct.unpack('<H', data[e_lfanew+6:e_lfanew+8])[0]
    size_opt_hdr = struct.unpack('<H', data[e_lfanew+20:e_lfanew+22])[0]
    section_start = e_lfanew + 24 + size_opt_hdr
    
    max_end = 0
    for i in range(num_sections):
        sec = data[section_start + i*40 : section_start + (i+1)*40]
        name = sec[:8].rstrip(b'\x00').decode('ascii', 'replace')
        raw_size = struct.unpack('<I', sec[16:20])[0]
        raw_off = struct.unpack('<I', sec[20:24])[0]
        end = raw_off + raw_size
        if end > max_end:
            max_end = end
        print(f"  Section {name}: off=0x{raw_off:X} size=0x{raw_size:X} end=0x{end:X}")
    
    overlay = data[max_end:]
    overlay_path = os.path.join(OUT_DIR, 'pe_overlay_raw.bin')
    with open(overlay_path, 'wb') as f:
        f.write(overlay)
    print(f"\nPE overlay: offset=0x{max_end:X}, size={len(overlay)} bytes")
    print(f"Overlay header hex: {overlay[:64].hex()}")
    print(f"Overlay header ASCII: {repr(overlay[:80])}")
    
    # ---- Find all PK (ZIP) signatures in the whole EXE ----
    print("\n--- Searching for ZIP archives ---")
    pk_offset = 0
    zip_num = 0
    while True:
        pk_offset = data.find(b'PK\x03\x04', pk_offset)
        if pk_offset == -1:
            break
        try:
            zf = zipfile.ZipFile(io.BytesIO(data[pk_offset:]))
            names = zf.namelist()
            out_path = os.path.join(OUT_DIR, f'zip_{zip_num}')
            os.makedirs(out_path, exist_ok=True)
            zf.extractall(out_path)
            print(f"  ZIP at 0x{pk_offset:X}: {len(names)} files -> {out_path}")
            for n in names[:20]:
                info = zf.getinfo(n)
                print(f"    {n} ({info.file_size} bytes)")
            if len(names) > 20:
                print(f"    ... and {len(names)-20} more")
            zf.close()
            zip_num += 1
        except Exception:
            pass
        pk_offset += 4
    print(f"  Total ZIP archives: {zip_num}")
    
    # ---- Base64 bzip2 payloads ----
    print("\n--- Searching for base64 payloads ---")
    text = data.decode('ascii', errors='ignore')
    b64_re = re.compile(r'[A-Za-z0-9+/]{80,}={0,2}')
    b64_num = 0
    for m in b64_re.finditer(text):
        b64_str = m.group()
        offset = m.start()
        try:
            decoded = base64.b64decode(b64_str)
            if len(decoded) < 32:
                continue
            out_name = os.path.join(OUT_DIR, f'b64_{b64_num:02d}.bin')
            with open(out_name, 'wb') as f:
                f.write(decoded)
            print(f"  Base64 at 0x{offset:X}: {len(b64_str)} chars -> {len(decoded)} bytes -> {out_name}")
            print(f"    Header: {decoded[:16].hex()}")
            
            # Try bzip2
            if decoded[:3] == b'BZh':
                try:
                    decompressed = bz2.decompress(decoded)
                    dec_name = os.path.join(OUT_DIR, f'b64_{b64_num:02d}_dec.bin')
                    with open(dec_name, 'wb') as f:
                        f.write(decompressed)
                    print(f"    BZip2 decompressed: {len(decompressed)} bytes -> {dec_name}")
                    # Check if it's text
                    if all(b in (0x09, 0x0A, 0x0D) or 0x20 <= b < 0x7F for b in decompressed[:min(256, len(decompressed))]):
                        print(f"    Text content: {decompressed[:200].decode('ascii', errors='replace')}")
                except Exception as e:
                    print(f"    BZip2 failed: {e}")
            b64_num += 1
        except Exception:
            pass
    print(f"  Total base64 payloads: {b64_num}")
    
    # ---- Analyze .Smt file ----
    print("\n--- Analyzing .Smt file ---")
    with open(SMT_PATH, 'rb') as f:
        smt = f.read()
    print(f"  Size: {len(smt)} bytes")
    print(f"  Header: {repr(smt[:16])}")
    
    # After the 16-byte 'SmartyFile000001' header
    rest = smt[16:]
    print(f"  After header: {rest[:32].hex()}")
    
    # Try to find if this is a known archive format with encryption
    # Check byte frequency for randomness
    from collections import Counter
    import math
    counts = Counter(rest)
    total = len(rest)
    entropy = -sum((c/total) * math.log2(c/total) for c in counts.values())
    print(f"  Entropy after header: {entropy:.3f} bits/byte")
    
    # Try simple XOR with keys that would reveal known headers
    test_headers = [b'PK\x03\x04', b'BZh', b'\x1f\x8b', b'MZ', b':10']
    for target in test_headers:
        for key_len in [1, 2, 4]:
            if key_len == 1:
                key = bytes([rest[0] ^ target[0]])
                decrypted = bytes(b ^ key[0] for b in rest[:64])
                if decrypted[:len(target)] == target:
                    print(f"  XOR-1 key=0x{key[0]:02X} reveals {target}: {decrypted[:32].hex()}")
    
    # The .Smt likely uses a proprietary format from Smarty/Quadzilla
    # Try to extract any structure
    # Look for repeating 16-byte patterns (block cipher?)
    print(f"\n  Looking for structure in .Smt...")
    # Check if data after header has block-like alignment
    # XOR the first block with itself shifted by various amounts
    block = rest[:256]
    for shift in [16, 32, 64, 128, 256]:
        if shift < len(rest):
            block2 = rest[shift:shift+256]
            xor_result = bytes(a ^ b for a, b in zip(block[:min(32, len(block2))], block2[:32]))
            zeros = sum(1 for b in xor_result if b == 0)
            print(f"    Shift {shift}: XOR has {zeros}/32 zero bytes")
    
    # Check SmartyUSB.exe too
    print("\n--- Checking SmartyUSB.exe ---")
    if os.path.exists('SmartyUSB.exe'):
        with open('SmartyUSB.exe', 'rb') as f:
            smarty = f.read()
        print(f"  Size: {len(smarty)} bytes")
        
        # Find PE overlay in SmartyUSB
        if smarty[:2] == b'MZ':
            e_lfanew2 = struct.unpack('<I', smarty[0x3C:0x40])[0]
            ns2 = struct.unpack('<H', smarty[e_lfanew2+6:e_lfanew2+8])[0]
            soh2 = struct.unpack('<H', smarty[e_lfanew2+20:e_lfanew2+22])[0]
            ss2 = e_lfanew2 + 24 + soh2
            me2 = 0
            for i in range(ns2):
                sec = smarty[ss2 + i*40 : ss2 + (i+1)*40]
                rs = struct.unpack('<I', sec[16:20])[0]
                ro = struct.unpack('<I', sec[20:24])[0]
                end = ro + rs
                if end > me2:
                    me2 = end
            smarty_overlay = smarty[me2:]
            print(f"  Overlay: {len(smarty_overlay)} bytes at 0x{me2:X}")
            if len(smarty_overlay) > 0:
                print(f"  Overlay header: {smarty_overlay[:64].hex()}")
                
                # Look for BZh in smarty overlay
                bz_idx = smarty_overlay.find(b'BZh')
                if bz_idx >= 0:
                    print(f"  BZh found in smarty overlay at +{bz_idx}")
        
        # Interesting strings from SmartyUSB
        strings = []
        current = []
        for i, b in enumerate(smarty):
            if 32 <= b < 127:
                current.append(chr(b))
            else:
                if len(current) >= 8:
                    strings.append((i - len(current), ''.join(current)))
                current = []
        
        keywords = ['firmware', 'smt', 'smarty', 'quadzilla', 'flash', 'program',
                    'erase', 'CAN', 'USB', 'COM', 'baud', 'hex', 'update',
                    'version', 'power', 'level', 'boost', 'fuel', 'timing',
                    'calibrat', 'PIC', 'dsPIC', 'encrypt', 'decrypt', 'key',
                    'password', 'setting', 'param', 'option', 'hidden',
                    'enable', 'disable', 'mode', 'config', 'feature',
                    'tune', 'serial', 'device', 'command', 'packet']
        
        seen = set()
        for offset, s in strings:
            s_lower = s.lower()
            for kw in keywords:
                if kw.lower() in s_lower and s not in seen:
                    seen.add(s)
                    print(f"  0x{offset:06X}: {s[:120]}")
                    break
    
    print("\nDone!")

if __name__ == '__main__':
    try:
        main()
    except Exception:
        traceback.print_exc()
        sys.exit(1)
