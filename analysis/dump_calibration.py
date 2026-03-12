#!/usr/bin/env python3
"""Quick calibration region dump from decrypted firmware."""
import struct

def read_ihex(filename):
    data = {}
    base_addr = 0
    with open(filename, 'r') as f:
        for line in f:
            line = line.strip()
            if not line.startswith(':'): continue
            byte_count = int(line[1:3], 16)
            address = int(line[3:7], 16)
            record_type = int(line[7:9], 16)
            if record_type == 0x00:
                full_addr = base_addr + address
                for i in range(byte_count):
                    b = int(line[9 + i*2:11 + i*2], 16)
                    data[full_addr + i] = b
            elif record_type == 0x02:
                base_addr = int(line[9:13], 16) << 4
            elif record_type == 0x04:
                base_addr = int(line[9:13], 16) << 16
            elif record_type == 0x01:
                break
    min_a = min(data.keys())
    max_a = max(data.keys())
    result = bytearray(max_a - min_a + 1)
    for addr, byte in data.items():
        result[addr - min_a] = byte
    return result, min_a

data, base = read_ihex('FirmwareUpdate_decrypted.hex')
print(f'Loaded {len(data)} bytes, base=0x{base:04X}')

# Calibration region
cal_start = 0x9700 - base
cal_end = 0xB200 - base
cal = data[cal_start:cal_end]
print(f'Calibration region: 0x9700-0xB200 = {len(cal)} bytes')

zeros = sum(1 for b in cal if b == 0)
print(f'Zeros: {zeros}/{len(cal)} ({zeros*100//len(cal)}%)')

# Hex dump of entire calibration region in 256-byte blocks
for block in range(0, len(cal), 256):
    block_data = cal[block:block+256]
    nonzero = sum(1 for b in block_data if b != 0)
    if nonzero == 0:
        print(f'\n=== 0x{0x9700+block:04X}-0x{0x9700+block+256:04X}: ALL ZEROS ===')
        continue
    print(f'\n=== 0x{0x9700+block:04X}-0x{0x9700+block+min(256,len(block_data)):04X} ({nonzero} non-zero bytes) ===')
    for row in range(min(16, (len(block_data)+15)//16)):
        offset = row * 16
        hex_vals = ' '.join(f'{block_data[offset+c]:02X}' for c in range(min(16, len(block_data)-offset)))
        ascii_chars = ''.join(chr(block_data[offset+c]) if 32 <= block_data[offset+c] <= 126 else '.' for c in range(min(16, len(block_data)-offset)))
        print(f'  {0x9700+block+offset:04X}: {hex_vals:<48s} {ascii_chars}')

# Also dump the literal pool (data references from main loop)
print(f'\n=== LITERAL POOL ANALYSIS (main loop data refs) ===')
for addr in range(0x53C4, 0x5700, 4):
    off = addr - base
    if off+3 < len(data):
        val = struct.unpack_from('<I', data, off)[0]
        marker = ""
        if 0x9700 <= val <= 0xB200:
            marker = " << CALIBRATION TABLE"
        elif 0x4000 <= val <= 0x9700:
            marker = " (code/rom)"
        elif val < 0x4000:
            marker = " (ram)"
        elif val > 0xFFFF:
            marker = " (peripheral/large)"
        if marker:
            print(f'  DAT_{addr:08X} = 0x{val:08X}{marker}')
