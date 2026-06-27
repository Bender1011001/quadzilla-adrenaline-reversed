import struct

def main():
    with open('firmware_v2.8.4HF.bin', 'rb') as f:
        # Table 2 base starts at 0xae80 (file offset 0x6e80)
        # It goes up to 0xb1b0 (which is 0xb1b0 - 0xae80 = 808 bytes = 202 entries)
        f.seek(0x6e80)
        data = f.read(808)
        
    print("Correct AID Table 2 Mapping:")
    print("=" * 40)
    for i in range(0, len(data), 4):
        ptr = struct.unpack('<I', data[i:i+4])[0]
        aid = i // 4
        if ptr != 0:
            print(f"AID {aid:3d} (offset {hex(0xae80 + i)}): RAM pointer {hex(ptr)}")

if __name__ == "__main__":
    main()
