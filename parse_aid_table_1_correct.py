import struct

def main():
    with open('firmware_v2.8.4HF.bin', 'rb') as f:
        # Table 1 base starts at 0xa91c (file offset 0x691c)
        # It goes up to 0xae80 (which is 0xae80 - 0xa91c = 1380 bytes = 345 entries)
        f.seek(0x691c)
        data = f.read(1380)
        
    print("Correct AID Table 1 Mapping:")
    print("=" * 40)
    for i in range(0, len(data), 4):
        ptr = struct.unpack('<I', data[i:i+4])[0]
        aid = i // 4
        if ptr != 0:
            print(f"AID {aid:3d} (offset {hex(0xa91c + i)}): RAM pointer {hex(ptr)}")

if __name__ == "__main__":
    main()
