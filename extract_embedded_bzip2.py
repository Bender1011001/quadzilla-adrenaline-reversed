#!/usr/bin/env python3
import sys
import os
import bz2

def main():
    if len(sys.argv) < 2:
        print("Usage: python extract_embedded_bzip2.py <input_file> [output_prefix]")
        sys.exit(1)
    in_path = sys.argv[1]
    prefix = sys.argv[2] if len(sys.argv) > 2 else os.path.splitext(os.path.basename(in_path))[0]

    with open(in_path, 'rb') as f:
        data = f.read()

    hits = []
    for i in range(len(data) - 3):
        if data[i:i+3] == b'BZh':
            hits.append(i)

    if not hits:
        print("No BZh signatures found in input.")
        print(f"Input size: {len(data)} bytes")
        return

    total_ok = 0
    for idx, off in enumerate(hits):
        d = bz2.BZ2Decompressor()
        try:
            out = d.decompress(data[off:])
            if len(out) < 16:
                print(f"Stream at 0x{off:08X} too small ({len(out)} bytes) - skipping")
                continue
            out_name = f"{prefix}.dec" if total_ok == 0 else f"{prefix}.dec.{idx:02d}_0x{off:08X}"
            with open(out_name, 'wb') as out_f:
                out_f.write(out)
            unused = d.unused_data
            print(f"OK: offset 0x{off:08X} -> {out_name} ({len(out)} bytes). Unused after stream: {len(unused)} bytes")
            total_ok += 1
        except OSError as e:
            print(f"FAIL: offset 0x{off:08X} not a complete bzip2 stream: {e}")
            continue

    if total_ok == 0:
        print("No valid bzip2 streams decompressed.")
        sys.exit(2)
    else:
        print(f"Completed: {total_ok} stream(s) extracted.")

if __name__ == "__main__":
    main()