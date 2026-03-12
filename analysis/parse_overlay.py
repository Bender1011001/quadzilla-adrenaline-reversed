#!/usr/bin/env python3
"""
Parse the custom self-extractor overlay format from ADR9802v2.8.4.exe.

The overlay starts at 0x58000 and has a structure like:
  [8 bytes header] [key-value pairs] [file data]

The header starts with: 48 12 90 bf 49 ff 91 aa 01 00 00 00 00 02
Then we see key-value pairs:
  0d 00 "setupFilename" 1c 00 "FirmwareUpdate\X2Updater.exe"
  0b 00 "noInterface" 04 00 "true"

This looks like a length-prefixed key-value store followed by compressed/encoded file data.
"""
import struct
import os

EXE_PATH = r'ADR9802v2.8.4.exe'
OUT_DIR = r'extracted'

def parse_overlay():
    with open(EXE_PATH, 'rb') as f:
        data = f.read()
    
    overlay_start = 0x58000
    overlay = data[overlay_start:]
    print(f"Overlay size: {len(overlay)} bytes")
    
    # Hex dump first 512 bytes to understand the format
    print("\n--- Overlay hex dump (first 512 bytes) ---")
    for i in range(0, min(512, len(overlay)), 16):
        h = ' '.join(f'{overlay[i+j]:02x}' if i+j < len(overlay) else '  ' for j in range(16))
        a = ''.join(chr(overlay[i+j]) if 32 <= overlay[i+j] < 127 else '.' for j in range(16) if i+j < len(overlay))
        print(f"  {i:08x}: {h}  {a}")
    
    # Try to parse the key-value structure
    print("\n--- Parsing key-value pairs ---")
    pos = 8  # Skip 8-byte header
    # Read 4 bytes at pos 8: 01 00 00 00 = 1 (little-endian) - maybe count or version
    val32 = struct.unpack('<I', overlay[pos:pos+4])[0]
    print(f"  Offset 8, uint32: {val32}")
    pos += 4
    
    # Next 2 bytes: 00 02 = 512 or 0x0200
    val16 = struct.unpack('<H', overlay[pos:pos+2])[0]
    print(f"  Offset 12, uint16: {val16}")
    pos += 2
    
    # Now parse length-prefixed strings
    kv_pairs = {}
    max_pos = min(4096, len(overlay))
    try:
        while pos < max_pos:
            # Read key length (1 byte or 2 bytes?)
            key_len = overlay[pos]
            pos += 1
            if key_len == 0:
                # Check if next byte is also 0 - might be end marker
                if pos < len(overlay) and overlay[pos] == 0:
                    print(f"  End marker at offset {pos-1}")
                    break
                continue
            
            # Skip one byte (seems to be 0x00 separator)
            if pos < len(overlay) and overlay[pos] == 0:
                pos += 1
            
            # Read key string
            key = overlay[pos:pos+key_len].decode('ascii', errors='replace')
            pos += key_len
            
            # Read value length
            val_len = overlay[pos]
            pos += 1
            if pos < len(overlay) and overlay[pos] == 0:
                pos += 1
            
            # Read value string  
            value = overlay[pos:pos+val_len].decode('ascii', errors='replace')
            pos += val_len
            
            kv_pairs[key] = value
            print(f"  Key: '{key}' = '{value}'")
            
            if len(kv_pairs) > 50:
                break
    except Exception as e:
        print(f"  Parse error at offset {pos}: {e}")
    
    print(f"\n  Total KV pairs: {len(kv_pairs)}")
    print(f"  Parse ended at offset: {pos}")
    
    # Dump a larger hex range around where the file data likely starts
    print(f"\n--- Hex at offset {pos} (after KV pairs) ---")
    for i in range(pos, min(pos + 256, len(overlay)), 16):
        h = ' '.join(f'{overlay[i+j]:02x}' if i+j < len(overlay) else '  ' for j in range(16))
        a = ''.join(chr(overlay[i+j]) if 32 <= overlay[i+j] < 127 else '.' for j in range(16) if i+j < len(overlay))
        print(f"  {i:08x}: {h}  {a}")
    
    # Search for MZ (PE) signatures in overlay  
    print("\n--- Searching for embedded PE files ---")
    idx = 0
    pe_files = []
    while True:
        idx = overlay.find(b'MZ', idx)
        if idx == -1:
            break
        # Verify it looks like a real PE
        if idx + 0x40 < len(overlay):
            try:
                e_lfanew = struct.unpack('<I', overlay[idx+0x3C:idx+0x40])[0]
                if e_lfanew < 0x1000 and idx + e_lfanew + 4 < len(overlay):
                    pe_sig = overlay[idx+e_lfanew:idx+e_lfanew+4]
                    if pe_sig == b'PE\x00\x00':
                        # Get PE size
                        num_sec = struct.unpack('<H', overlay[idx+e_lfanew+6:idx+e_lfanew+8])[0]
                        soh = struct.unpack('<H', overlay[idx+e_lfanew+20:idx+e_lfanew+22])[0]
                        ss = e_lfanew + 24 + soh
                        max_end = 0
                        for si in range(num_sec):
                            sec = overlay[idx+ss+si*40:idx+ss+(si+1)*40]
                            if len(sec) < 40:
                                break
                            rs = struct.unpack('<I', sec[16:20])[0]
                            ro = struct.unpack('<I', sec[20:24])[0]
                            end = ro + rs
                            if end > max_end:
                                max_end = end
                        
                        pe_files.append((idx, max_end))
                        print(f"  PE at overlay+0x{idx:X} (EXE offset 0x{overlay_start+idx:X}), size ~{max_end} bytes, sections={num_sec}")
            except:
                pass
        idx += 2
    
    # Extract PE files
    if pe_files:
        pe_dir = os.path.join(OUT_DIR, 'pe_files')
        os.makedirs(pe_dir, exist_ok=True)
        for i, (off, size) in enumerate(pe_files):
            pe_data = overlay[off:off+size]
            pe_path = os.path.join(pe_dir, f'pe_{i:02d}_{off:06X}.exe')
            with open(pe_path, 'wb') as f:
                f.write(pe_data)
            print(f"  Extracted: {pe_path} ({len(pe_data)} bytes)")
            
            # Extract strings from this PE
            strings = []
            current = []
            for j, b in enumerate(pe_data):
                if 32 <= b < 127:
                    current.append(chr(b))
                else:
                    if len(current) >= 8:
                        strings.append((j - len(current), ''.join(current)))
                    current = []
            
            keywords = ['firmware', 'flash', 'CAN', 'USB', 'version', 'quadzilla',
                        'smarty', 'power', 'boost', 'fuel', 'timing', 'rpm', 'tps',
                        'tune', 'calibrat', 'hex', 'erase', 'program', 'serial',
                        'command', 'response', 'packet', 'PIC', 'dsPIC', 'setting',
                        'param', 'option', 'hidden', 'enable', 'mode', 'sensor',
                        'gauge', 'torque', 'injection', 'rail', 'EGT', 'trans',
                        'speed', 'turbo', 'pressure', 'adrenaline', 'config']
            
            print(f"    Key strings:")
            seen = set()
            for off_s, s in strings:
                s_lower = s.lower()
                for kw in keywords:
                    if kw.lower() in s_lower and s not in seen:
                        seen.add(s)
                        print(f"      0x{off_s:06X}: {s[:120]}")
                        break
    
    # Also search for BZip2 in overlay
    print("\n--- BZip2 search in overlay ---")
    idx = 0
    while True:
        idx = overlay.find(b'BZh', idx)
        if idx == -1:
            break
        print(f"  BZh at overlay+0x{idx:X}")
        idx += 1
    
    # Search for Intel HEX start markers
    print("\n--- Intel HEX search in overlay ---")
    ihex_count = overlay.count(b':10')
    print(f"  ':10' occurrences (Intel HEX data records): {ihex_count}")
    
    # Search for any file-like markers
    print("\n--- File signature search ---")
    sigs = {
        b'\x89PNG': 'PNG', b'BM': 'BMP', b'GIF8': 'GIF',
        b'\xff\xd8\xff': 'JPEG', b'Rar!': 'RAR', b'7z\xbc\xaf': '7z'
    }
    for sig, name in sigs.items():
        idx = 0
        hits = []
        while True:
            idx = overlay.find(sig, idx)
            if idx == -1:
                break
            hits.append(idx)
            idx += 1
        if hits:
            print(f"  {name}: {len(hits)} hits at offsets {hits[:5]}")

if __name__ == '__main__':
    os.makedirs(OUT_DIR, exist_ok=True)
    parse_overlay()
