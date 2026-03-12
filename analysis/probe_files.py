#!/usr/bin/env python3
"""Probe the key files to understand their structure."""
import struct
import os

def probe_smt(path):
    """Probe the .Smt firmware file."""
    print("=" * 72)
    print(f"FILE: {path}")
    with open(path, 'rb') as f:
        data = f.read()
    print(f"Size: {len(data)} bytes ({len(data)/1024:.1f} KB)")
    
    # Check if it's text-based
    is_text = True
    for b in data[:1024]:
        if b not in (0x09, 0x0A, 0x0D) and not (0x20 <= b <= 0x7E):
            is_text = False
            break
    
    print(f"Appears text-based: {is_text}")
    
    if is_text:
        text = data.decode('ascii', errors='replace')
        lines = text.split('\n')
        print(f"Total lines: {len(lines)}")
        print(f"First 20 lines:")
        for i, line in enumerate(lines[:20]):
            print(f"  {i:5d}: {line.rstrip()[:120]}")
        print(f"Last 10 lines:")
        for i, line in enumerate(lines[-10:]):
            print(f"  {len(lines)-10+i:5d}: {line.rstrip()[:120]}")
        
        # Check for Intel HEX
        ihex_count = sum(1 for l in lines if l.strip().startswith(':'))
        # Check for SREC
        srec_count = sum(1 for l in lines if l.strip().startswith('S'))
        print(f"Lines starting with ':' (IHEX): {ihex_count}")
        print(f"Lines starting with 'S' (SREC): {srec_count}")
    else:
        print(f"First 128 bytes hex:")
        for i in range(0, min(128, len(data)), 16):
            hex_part = ' '.join(f'{b:02x}' for b in data[i:i+16])
            ascii_part = ''.join(chr(b) if 32 <= b < 127 else '.' for b in data[i:i+16])
            print(f"  {i:08x}: {hex_part:<48s} {ascii_part}")
        
        # Scan for known signatures
        sigs = {
            b'BZh': 'bzip2',
            b'\x1f\x8b': 'gzip',
            b'PK': 'ZIP/PK',
            b'\x89PNG': 'PNG',
            b'MZ': 'DOS/PE EXE',
            b'\x7fELF': 'ELF',
            b'Smarty': 'Smarty header',
            b'MCHP': 'Microchip',
        }
        for sig, name in sigs.items():
            idx = 0
            hits = []
            while True:
                idx = data.find(sig, idx)
                if idx == -1:
                    break
                hits.append(idx)
                if len(hits) >= 20:
                    break
                idx += 1
            if hits:
                print(f"  Signature '{name}': found at offsets {hits[:10]}{'...' if len(hits) > 10 else ''}")


def probe_overlay(path):
    """Probe overlay.bin."""
    print("=" * 72)
    print(f"FILE: {path}")
    with open(path, 'rb') as f:
        data = f.read()
    print(f"Size: {len(data)} bytes ({len(data)/1024:.1f} KB)")
    
    # Find first non-zero
    first_nonzero = None
    for i, b in enumerate(data):
        if b != 0:
            first_nonzero = i
            break
    
    print(f"First non-zero byte at offset: {first_nonzero}")
    if first_nonzero is not None:
        # Show hex around first non-zero
        start = max(0, first_nonzero - 16)
        end = min(len(data), first_nonzero + 128)
        print(f"Hex around first non-zero ({start}-{end}):")
        for i in range(start, end, 16):
            chunk = data[i:i+16]
            hex_part = ' '.join(f'{b:02x}' for b in chunk)
            ascii_part = ''.join(chr(b) if 32 <= b < 127 else '.' for b in chunk)
            print(f"  {i:08x}: {hex_part:<48s} {ascii_part}")
    
    # Count zero bytes
    zero_count = data.count(0)
    print(f"Zero bytes: {zero_count} ({zero_count*100/len(data):.1f}%)")
    
    # Entropy analysis (rough)
    from collections import Counter
    counts = Counter(data)
    total = len(data)
    import math
    entropy = -sum((c/total) * math.log2(c/total) for c in counts.values() if c > 0)
    print(f"Shannon entropy: {entropy:.3f} bits/byte (max 8.0)")
    
    # Byte frequency distribution
    print(f"Unique byte values: {len(counts)}")
    most_common = counts.most_common(10)
    print(f"Most common bytes: {[(f'0x{b:02X}', c) for b, c in most_common]}")
    
    # Scan for signatures
    sigs = {
        b'BZh': 'bzip2',
        b'\x1f\x8b': 'gzip',  
        b'PK': 'ZIP/PK',
        b'MZ': 'DOS/PE',
        b'\x7fELF': 'ELF',
        b'MCHP': 'Microchip',
        b'\xfe\xed\xfa\xce': 'Mach-O',
        b'\x42\x4d': 'BMP',
    }
    for sig, name in sigs.items():
        idx = data.find(sig)
        if idx != -1:
            print(f"  Signature '{name}': found at offset {idx}")
    
    # Check if it might be a raw firmware image - look for ARM/MIPS/PIC patterns
    # ARM cortex: first 4 bytes are usually stack pointer, next 4 are reset vector
    if len(data) >= 8:
        sp = struct.unpack('<I', data[0:4])[0]
        rv = struct.unpack('<I', data[4:8])[0]
        print(f"  If ARM LE: SP=0x{sp:08X}, Reset=0x{rv:08X}")
        sp_be = struct.unpack('>I', data[0:4])[0]
        rv_be = struct.unpack('>I', data[4:8])[0]
        print(f"  If ARM BE: SP=0x{sp_be:08X}, Reset=0x{rv_be:08X}")
    
    # Look for repeating patterns / table structures 
    # Check for 0xFF-filled regions (common in firmware images)
    ff_runs = []
    run_start = None
    for i, b in enumerate(data):
        if b == 0xFF:
            if run_start is None:
                run_start = i
        else:
            if run_start is not None and i - run_start >= 64:
                ff_runs.append((run_start, i - run_start))
            run_start = None
    if run_start is not None and len(data) - run_start >= 64:
        ff_runs.append((run_start, len(data) - run_start))
    print(f"FF-filled regions (>=64 bytes): {len(ff_runs)}")
    for start, length in ff_runs[:5]:
        print(f"    offset {start:08X}, length {length}")

    # Scan for text strings
    print(f"\nASCII strings >= 8 chars:")
    strings = []
    current = []
    for i, b in enumerate(data):
        if 32 <= b < 127:
            current.append(chr(b))
        else:
            if len(current) >= 8:
                strings.append((i - len(current), ''.join(current)))
            current = []
    if current and len(current) >= 8:
        strings.append((len(data) - len(current), ''.join(current)))
    
    for offset, s in strings[:50]:
        print(f"  {offset:08X}: {s[:100]}")
    print(f"Total strings found: {len(strings)}")


def probe_exe_overlay(exe_path):
    """Probe the ADR9802 exe for its overlay/embedded data."""
    print("=" * 72)
    print(f"PROBING EXE: {exe_path}")
    with open(exe_path, 'rb') as f:
        data = f.read()
    print(f"Size: {len(data)} bytes ({len(data)/1024:.1f} KB)")
    
    # Scan for interesting strings related to firmware, USB, COM port, etc.
    print(f"\nInteresting strings in EXE:")
    strings = []
    current = []
    for i, b in enumerate(data):
        if 32 <= b < 127:
            current.append(chr(b))
        else:
            if len(current) >= 6:
                strings.append((i - len(current), ''.join(current)))
            current = []
    
    keywords = ['firmware', 'flash', 'program', 'erase', 'CAN', 'USB', 
                'COM', 'serial', 'baud', 'hex', 'update', 'version',
                'adrenaline', 'quadzilla', 'smarty', 'power', 'level',
                'boost', 'fuel', 'timing', 'rpm', 'tps', 'map',
                'tune', 'calibrat', 'table', 'offset', '.bin', '.hex',
                'PIC', 'micro', 'chip', 'dsPIC', 'payload', 'MCU',
                'device', 'protocol', 'command', 'response', 'packet']
    
    seen = set()
    for offset, s in strings:
        s_lower = s.lower()
        for kw in keywords:
            if kw.lower() in s_lower and s not in seen:
                seen.add(s)
                print(f"  {offset:08X}: {s[:120]}")
                break

    # Scan for bzip2 headers
    print(f"\nBZh signatures in EXE:")
    idx = 0
    while True:
        idx = data.find(b'BZh', idx)
        if idx == -1:
            break
        # Show context
        ctx = data[idx:idx+20]
        print(f"  offset 0x{idx:08X}: {ctx.hex()} ({ctx[:10]})")
        idx += 1


if __name__ == '__main__':
    base = r'e:\code.projects\GitHub-projects\quadzilla_rev'
    probe_smt(os.path.join(base, 'S03V126CDR12A.Smt'))
    probe_overlay(os.path.join(base, 'overlay.bin'))
    probe_exe_overlay(os.path.join(base, 'ADR9802v2.8.4.exe'))
