#!/usr/bin/env python3
"""
Extract strings and class/method names from the iQuad APK's DEX file.
APK is just a ZIP - extract classes.dex and scan for parameter names.
"""
import zipfile
import os
import re
import struct

APK_PATH = r'E:\code.projects\quadzilla_rev\iquad.apk'
OUT_DIR = r'extracted/iquad'

def extract_dex_strings(dex_data):
    """Extract all string constants from a DEX file."""
    # DEX header
    magic = dex_data[:8]
    if magic[:4] != b'dex\n':
        print(f"Not a valid DEX file (magic: {magic[:8]})")
        return []
    
    # String IDs start at offset 0x3C in the header
    string_ids_size = struct.unpack_from('<I', dex_data, 0x38)[0]
    string_ids_off = struct.unpack_from('<I', dex_data, 0x3C)[0]
    
    strings = []
    for i in range(string_ids_size):
        str_data_off = struct.unpack_from('<I', dex_data, string_ids_off + i * 4)[0]
        
        # Read ULEB128 length
        pos = str_data_off
        length = 0
        shift = 0
        while True:
            b = dex_data[pos]
            length |= (b & 0x7F) << shift
            pos += 1
            if (b & 0x80) == 0:
                break
            shift += 7
        
        # Read MUTF-8 string
        s = []
        end = pos + length
        while pos < end and pos < len(dex_data):
            b = dex_data[pos]
            if b == 0:
                break
            if b < 0x80:
                s.append(chr(b))
            elif b < 0xE0:
                if pos + 1 < len(dex_data):
                    s.append(chr(((b & 0x1F) << 6) | (dex_data[pos+1] & 0x3F)))
                    pos += 1
            else:
                if pos + 2 < len(dex_data):
                    s.append(chr(((b & 0x0F) << 12) | ((dex_data[pos+1] & 0x3F) << 6) | (dex_data[pos+2] & 0x3F)))
                    pos += 2
            pos += 1
        
        strings.append(''.join(s))
    
    return strings

def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    
    print(f"APK: {APK_PATH}")
    print(f"Size: {os.path.getsize(APK_PATH)} bytes")
    
    # Extract DEX files from APK
    with zipfile.ZipFile(APK_PATH, 'r') as zf:
        print(f"\nAPK contents ({len(zf.namelist())} files):")
        for name in sorted(zf.namelist()):
            info = zf.getinfo(name)
            if name.endswith('.dex') or 'quadzilla' in name.lower() or name.endswith('.xml'):
                print(f"  * {name} ({info.file_size} bytes)")
        
        # Extract all DEX files
        dex_files = [n for n in zf.namelist() if n.endswith('.dex')]
        print(f"\nDEX files: {dex_files}")
        
        all_strings = []
        for dex_name in dex_files:
            print(f"\n=== Processing {dex_name} ===")
            dex_data = zf.read(dex_name)
            print(f"  Size: {len(dex_data)} bytes")
            
            # Save DEX
            dex_out = os.path.join(OUT_DIR, dex_name)
            os.makedirs(os.path.dirname(dex_out) if os.path.dirname(dex_out) else OUT_DIR, exist_ok=True)
            with open(dex_out, 'wb') as f:
                f.write(dex_data)
            
            strings = extract_dex_strings(dex_data)
            print(f"  Strings: {len(strings)} total")
            all_strings.extend(strings)
    
    # Filter interesting strings
    keywords = [
        'quadzilla', 'adrenaline', 'iquad', 'parameter', 'gauge',
        'boost', 'rpm', 'speed', 'torque', 'fuel', 'injection',
        'timing', 'pressure', 'rail', 'turbo', 'egt', 'exhaust',
        'intake', 'throttle', 'idle', 'cruise', 'tow', 'economy',
        'performance', 'stage', 'power', 'level', 'setting',
        'calibrat', 'tune', 'defuel', 'smoke', 'limiter',
        'transmission', 'trans', 'slip', 'temp', 'oil', 'coolant',
        'pid', 'can', 'j1939', 'obd', 'dtc', 'fault', 'error',
        'bluetooth', 'serial', 'command', 'feature', 'hidden',
        'unlock', 'code', 'enable', 'disable', 'mode', 'config',
        'map', 'table', 'offset', 'gain', 'factor', 'scale',
        'sensor', 'voltage', 'current', 'resistance', 'frequency',
        'duty', 'pwm', 'analog', 'digital', 'adc', 'dac',
        'monitor', 'display', 'screen', 'layout',
        'cummins', 'dodge', 'ram', 'diesel', 'common rail',
    ]
    
    print(f"\n\n=== INTERESTING STRINGS ({len(all_strings)} total scanned) ===")
    interesting = []
    for s in all_strings:
        s_lower = s.lower()
        if any(kw in s_lower for kw in keywords):
            interesting.append(s)
    
    # Deduplicate and sort
    interesting = sorted(set(interesting))
    print(f"Found {len(interesting)} matching strings:")
    for s in interesting:
        if len(s) > 3:
            print(f"  {s[:200]}")
    
    # Also find all class names that look like Quadzilla's
    print(f"\n\n=== QUADZILLA CLASS/METHOD NAMES ===")
    class_names = [s for s in all_strings if 'quadzilla' in s.lower() or 'iquad' in s.lower() or 'X2' in s]
    for cn in sorted(set(class_names)):
        print(f"  {cn[:200]}")
    
    # Parameter-like strings (look like parameter definitions)
    print(f"\n\n=== PARAMETER-LIKE STRINGS ===")
    param_patterns = [s for s in all_strings 
                      if re.match(r'^[A-Z][a-z]+[A-Z]', s)  # CamelCase
                      or re.match(r'^[A-Z_]{4,}$', s)  # ALL_CAPS
                      or 'Param' in s or 'param' in s
                      or 'Gauge' in s or 'gauge' in s]
    param_patterns = sorted(set(param_patterns))
    for p in param_patterns:
        if len(p) > 3 and len(p) < 80:
            print(f"  {p}")
    
    print("\nDone!")

if __name__ == '__main__':
    main()
