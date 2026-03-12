#!/usr/bin/env python3
"""Probe the extracted firmware files for structure and content."""
import os
import struct
import hashlib
import math
from collections import Counter

BASE = r'extracted/from_exe/ckz_75O0/FirmwareUpdate'

def entropy(data):
    if not data:
        return 0.0
    counts = Counter(data)
    total = len(data)
    return -sum((c/total) * math.log2(c/total) for c in counts.values())

def probe_file(path):
    with open(path, 'rb') as f:
        data = f.read()
    
    name = os.path.basename(path)
    print(f"\n{'='*60}")
    print(f"FILE: {name}")
    print(f"  Size: {len(data)} bytes ({len(data)/1024:.1f} KB)")
    print(f"  MD5:  {hashlib.md5(data).hexdigest()}")
    print(f"  SHA1: {hashlib.sha1(data).hexdigest()}")
    
    # Entropy
    ent = entropy(data)
    print(f"  Entropy: {ent:.3f} bits/byte")
    
    # First 128 bytes hex dump
    print(f"  Header (first 128 bytes):")
    for i in range(0, min(128, len(data)), 16):
        h = ' '.join(f'{data[i+j]:02x}' if i+j < len(data) else '  ' for j in range(16))
        a = ''.join(chr(data[i+j]) if 32 <= data[i+j] < 127 else '.' for j in range(16) if i+j < len(data))
        print(f"    {i:04x}: {h}  {a}")
    
    # Last 64 bytes
    if len(data) > 128:
        print(f"  Footer (last 64 bytes):")
        start = max(128, len(data) - 64)
        for i in range(start, len(data), 16):
            h = ' '.join(f'{data[i+j]:02x}' if i+j < len(data) else '  ' for j in range(16))
            a = ''.join(chr(data[i+j]) if 32 <= data[i+j] < 127 else '.' for j in range(16) if i+j < len(data))
            print(f"    {i:04x}: {h}  {a}")
    
    # Check if PE
    if data[:2] == b'MZ':
        print(f"  FORMAT: PE (Windows executable)")
        e_lfanew = struct.unpack('<I', data[0x3C:0x40])[0]
        if data[e_lfanew:e_lfanew+4] == b'PE\x00\x00':
            machine = struct.unpack('<H', data[e_lfanew+4:e_lfanew+6])[0]
            machines = {0x14c: 'x86', 0x8664: 'x86-64', 0x1c0: 'ARM', 0x1c4: 'ARM Thumb-2'}
            print(f"  Machine: {machines.get(machine, f'0x{machine:X}')}")
            
            # Sections
            num_sections = struct.unpack('<H', data[e_lfanew+6:e_lfanew+8])[0]
            size_opt = struct.unpack('<H', data[e_lfanew+20:e_lfanew+22])[0]
            ss = e_lfanew + 24 + size_opt
            for si in range(num_sections):
                sec = data[ss+si*40:ss+(si+1)*40]
                sname = sec[:8].rstrip(b'\x00').decode('ascii', 'replace')
                vsize = struct.unpack('<I', sec[8:12])[0]
                rsize = struct.unpack('<I', sec[16:20])[0]
                print(f"    Section: {sname:8s} vsize=0x{vsize:X} rsize=0x{rsize:X}")
    
    # Check for Intel HEX
    if data[:1] == b':':
        print(f"  FORMAT: Intel HEX")
        lines = data.decode('ascii', errors='replace').split('\n')
        print(f"  Lines: {len(lines)}")
        for line in lines[:5]:
            print(f"    {line.rstrip()}")
    
    # Check for S-Record
    if data[:2] in (b'S0', b'S1', b'S2', b'S3'):
        print(f"  FORMAT: Motorola S-Record")
    
    # String extraction (8+ chars)
    strings = []
    current = []
    for i, b in enumerate(data):
        if 32 <= b < 127:
            current.append(chr(b))
        else:
            if len(current) >= 8:
                strings.append((i - len(current), ''.join(current)))
            current = []
    if len(current) >= 8:
        strings.append((len(data) - len(current), ''.join(current)))
    
    if strings:
        print(f"  Strings ({len(strings)} found with len >= 8):")
        fw_kw = ['firmware', 'quadzilla', 'adrenaline', 'power', 'level', 'boost',
                 'fuel', 'timing', 'rpm', 'tps', 'torque', 'injection', 'rail',
                 'pressure', 'turbo', 'egt', 'exhaust', 'intake', 'throttle', 'idle',
                 'cruise', 'tow', 'economy', 'performance', 'stage', 'calibrat',
                 'setting', 'param', 'option', 'config', 'CAN', 'J1939', 'PID',
                 'version', 'ADR', 'serial', 'dsPIC', 'PIC', 'microchip',
                 'flash', 'erase', 'program', 'verify', 'command', 'packet',
                 'gauge', 'sensor', 'speed', 'trans', 'temp', 'oil', 'coolant',
                 'DTC', 'error', 'fault', 'USB', 'update']
        
        for off, s in strings:
            s_lower = s.lower()
            is_interesting = any(kw.lower() in s_lower for kw in fw_kw) or len(s) > 20
            marker = "***" if is_interesting else "   "
            if is_interesting or len(strings) < 50:
                print(f"    {marker} 0x{off:06X}: {s[:120]}")
    
    return data

def main():
    # Probe key files
    for fname in ['FirmwareUpdate.qz', 'FirmwareUpdate.opt', 'FirmwareUpdate.pwd',
                   'FirmwareUpdate.pwk', 'Quadzilla.dll', 'X2Updater.exe']:
        path = os.path.join(BASE, fname)
        if os.path.exists(path):
            probe_file(path)
    
    print("\n\nDone!")

if __name__ == '__main__':
    main()
