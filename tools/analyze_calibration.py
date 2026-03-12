#!/usr/bin/env python3
"""
Analyze the calibration/lookup table region of the Quadzilla firmware (0x9700-0xB200).
Reads the decrypted Intel HEX firmware and dumps the data structures.
"""
import struct
import sys
import os

def read_ihex(filename):
    """Read Intel HEX file into a flat byte array with base address tracking."""
    data = {}
    min_addr = float('inf')
    max_addr = 0
    base_addr = 0
    
    with open(filename, 'r') as f:
        for line in f:
            line = line.strip()
            if not line.startswith(':'):
                continue
            
            byte_count = int(line[1:3], 16)
            address = int(line[3:7], 16)
            record_type = int(line[7:9], 16)
            
            if record_type == 0x00:  # Data record
                full_addr = base_addr + address
                for i in range(byte_count):
                    b = int(line[9 + i*2:11 + i*2], 16)
                    data[full_addr + i] = b
                min_addr = min(min_addr, full_addr)
                max_addr = max(max_addr, full_addr + byte_count - 1)
            elif record_type == 0x02:  # Extended segment address
                base_addr = int(line[9:13], 16) << 4
            elif record_type == 0x04:  # Extended linear address
                base_addr = int(line[9:13], 16) << 16
            elif record_type == 0x01:  # EOF
                break
    
    # Convert to contiguous array
    size = max_addr - min_addr + 1
    result = bytearray(size)
    for addr, byte in data.items():
        result[addr - min_addr] = byte
    
    return result, min_addr

def analyze_region(data, base, start, end, label):
    """Analyze a memory region for data patterns."""
    offset_start = start - base
    offset_end = end - base
    region = data[offset_start:offset_end]
    
    print(f"\n{'='*70}")
    print(f"  {label}: 0x{start:04X} - 0x{end:04X} ({end-start} bytes)")
    print(f"{'='*70}")
    
    # Check for zero-fill
    zero_count = sum(1 for b in region if b == 0)
    if zero_count > len(region) * 0.9:
        print(f"  → Mostly zeros ({zero_count}/{len(region)} = {zero_count*100//len(region)}%)")
        return
    
    # Look for table-like patterns (monotonic sequences)
    # Try as 8-bit values
    print(f"\n  As 8-bit values (first 64):")
    vals8 = list(region[:min(64, len(region))])
    print(f"  {vals8}")
    
    # Check monotonicity
    increasing = sum(1 for i in range(1, len(vals8)) if vals8[i] >= vals8[i-1])
    if increasing > len(vals8) * 0.8:
        print(f"  → MONOTONIC INCREASING (potential axis table)")
    
    # Try as 16-bit LE values
    vals16 = []
    for i in range(0, min(64, len(region)), 2):
        if i+1 < len(region):
            vals16.append(struct.unpack_from('<H', region, i)[0])
    print(f"\n  As 16-bit LE (first 32):")
    print(f"  {vals16}")
    
    # Try as 32-bit LE values
    vals32 = []
    for i in range(0, min(64, len(region)), 4):
        if i+3 < len(region):
            vals32.append(struct.unpack_from('<I', region, i)[0])
    print(f"\n  As 32-bit LE (first 16):")
    print(f"  {vals32}")
    
    # Entropy
    byte_counts = [0] * 256
    for b in region:
        byte_counts[b] += 1
    unique = sum(1 for c in byte_counts if c > 0)
    print(f"\n  Unique bytes: {unique}/256, Non-zero: {len(region)-zero_count}/{len(region)}")
    
    # Pattern detection: look for repeated structures
    for stride in [4, 8, 16, 20, 32]:
        if len(region) >= stride * 3:
            chunks = [region[i:i+stride] for i in range(0, min(stride*8, len(region)), stride)]
            # Check if structure repeats (similar first bytes)
            first_bytes = [c[0] if len(c) > 0 else -1 for c in chunks]
            if len(set(first_bytes)) <= 3:
                print(f"  → Possible {stride}-byte record structure (first bytes: {first_bytes})")


def main():
    # Find the decrypted firmware
    base_dir = os.path.dirname(os.path.abspath(__file__))
    hex_file = os.path.join(base_dir, "FirmwareUpdate_decrypted.hex")
    
    if not os.path.exists(hex_file):
        print(f"[-] Not found: {hex_file}")
        sys.exit(1)
    
    data, base = read_ihex(hex_file)
    print(f"[+] Loaded {len(data)} bytes from {hex_file}")
    print(f"[+] Base address: 0x{base:04X}")
    print(f"[+] Address range: 0x{base:04X} - 0x{base + len(data) - 1:04X}")
    
    # Analyze the calibration region in chunks
    # Based on decompiled code, key tables are referenced via DAT_00005018 + offsets 0x34-0x44
    # and via DAT_0000504c as a parameter table indexed by [power_level * 0x14 + param_id]
    
    regions = [
        (0x9700, 0x9800, "Region A — Start of calibration data"),
        (0x9800, 0x9900, "Region B"),
        (0x9900, 0x9A00, "Region C"),
        (0x9A00, 0x9B00, "Region D"),
        (0x9B00, 0x9C00, "Region E"),
        (0x9C00, 0x9D00, "Region F"),
        (0x9D00, 0x9E00, "Region G"),
        (0x9E00, 0x9F00, "Region H"),
        (0x9F00, 0xA000, "Region I"),
        (0xA000, 0xA100, "Region J"),
        (0xA100, 0xA200, "Region K"),
        (0xA200, 0xA400, "Region L (512 bytes)"),
        (0xA400, 0xA800, "Region M (1024 bytes)"),
        (0xA800, 0xAC00, "Region N (1024 bytes)"),
        (0xAC00, 0xB000, "Region O (1024 bytes)"),
        (0xB000, 0xB200, "Region P — End of calibration data"),
    ]
    
    for start, end, label in regions:
        if end - base <= len(data):
            analyze_region(data, base, start, end, label)
        else:
            print(f"\n  {label}: OUT OF RANGE")
    
    # Also map the DAT_ references from the main loop to identify pointers into this region
    print(f"\n{'='*70}")
    print(f"  DATA POINTER ANALYSIS")
    print(f"{'='*70}")
    
    # The main loop (FUN_50F0) references DAT_000053c4 through DAT_000056f8
    # These are in the literal pool region, containing pointers to RAM and calibration
    # Let's dump the literal pool near the main function
    lit_start = 0x53C4
    lit_end = 0x5700
    if lit_end - base <= len(data):
        offset_start = lit_start - base
        offset_end = lit_end - base
        region = data[offset_start:offset_end]
        
        print(f"\n  Literal pool 0x{lit_start:04X}-0x{lit_end:04X} (main loop data refs):")
        for i in range(0, len(region), 4):
            if i + 3 < len(region):
                val = struct.unpack_from('<I', region, i)[0]
                addr = lit_start + i
                # Flag values that point into calibration region
                marker = ""
                if 0x9700 <= val <= 0xB200:
                    marker = " ← CALIBRATION TABLE PTR"
                elif 0x4000 <= val <= 0x9700:
                    marker = " ← CODE/ROM"
                elif val < 0x4000:
                    marker = " ← RAM"
                print(f"    DAT_{addr:08X} = 0x{val:08X}{marker}")

if __name__ == '__main__':
    main()
