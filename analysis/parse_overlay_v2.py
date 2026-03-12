#!/usr/bin/env python3
"""
Parse the custom self-extractor overlay format.

Format analysis:
  Offset 0-7: Magic/header (48 12 90 bf 49 ff 91 aa)
  Offset 8-11: Version? (01 00 00 00)
  Offset 12-13: Flags? (00 02)
  Offset 14+: Length-prefixed KV pairs ending with 00 00
  
After KV pairs, file entries begin:
  Each entry appears to be:
    [?? bytes meta] [len_byte 00] [path string] [00] [compressed data until next entry]
    
Let's try to figure out the file entry structure by looking for all path strings.
"""
import struct
import os
import zlib

EXE_PATH = r'ADR9802v2.8.4.exe'
OUT_DIR = r'extracted/firmware_update'

def main():
    with open(EXE_PATH, 'rb') as f:
        data = f.read()
    
    overlay_start = 0x58000
    ovl = data[overlay_start:]
    print(f"Overlay: {len(ovl)} bytes\n")
    
    # Find all FirmwareUpdate/ path strings in the overlay
    paths_found = []
    idx = 0
    while True:
        idx = ovl.find(b'FirmwareUpdate/', idx)
        if idx == -1:
            break
        # Find the null terminator
        null_pos = ovl.find(b'\x00', idx)
        if null_pos == -1:
            null_pos = idx + 100
        path = ovl[idx:null_pos].decode('ascii', errors='replace')
        
        # Look backwards from the path to find the length prefix
        # The byte before should be 00, and before that the length
        # Actually looking at hex: 15 00 "FirmwareUpdate/qz.inf" 00
        # 0x15 = 21, len("FirmwareUpdate/qz.inf") = 21. So format is: [len_le16] [path] [null]
        
        # Check 2 bytes before the path for length
        if idx >= 2:
            len_val = struct.unpack('<H', ovl[idx-2:idx])[0]
            if len_val == len(path):
                # Now look further back for metadata before the length
                meta_region = ovl[max(0, idx-20):idx-2]
                paths_found.append({
                    'path': path,
                    'path_offset': idx,
                    'len_prefix': len_val,
                    'data_start': null_pos + 1,
                    'meta_before': meta_region.hex()
                })
        idx += 1
    
    print(f"Found {len(paths_found)} file entries:\n")
    
    # For adjacent entries, the data of entry N ends where entry N+1's metadata starts
    for i, entry in enumerate(paths_found):
        if i + 1 < len(paths_found):
            # Next entry's metadata starts some bytes before its length prefix
            # We need to figure out the metadata size. Let's look at each entry's meta_before
            next_meta_offset = paths_found[i+1]['path_offset'] - 20  # rough estimate
            
            # Actually let's compute: data between end of this path and start of next length-prefix
            this_data_start = entry['data_start']
            next_path_off = paths_found[i+1]['path_offset']
            next_len_prefix_off = next_path_off - 2
            
            # Before the length prefix of next entry, there should be some header bytes
            # Let's look at what's right before each entry's length prefix
            entry['data_end_guess'] = next_len_prefix_off
            entry['data_size_guess'] = next_len_prefix_off - this_data_start
        else:
            entry['data_end_guess'] = len(ovl)
            entry['data_size_guess'] = len(ovl) - entry['data_start']
        
        print(f"  [{i:2d}] {entry['path']}")
        print(f"       meta_before: {entry['meta_before']}")
        print(f"       data: offset {entry['data_start']}, ~{entry['data_size_guess']} bytes")
    
    # Now let's look at the meta_before patterns more carefully
    # For the first entry at offset 0x67:
    # "00 9b e5 27 6d 02 15 00" -> then "FirmwareUpdate/qz.inf"
    # 9b e5 27 6d could be CRC32 or timestamp
    # 02 could be compression method
    # 15 00 = length 21
    
    # Let's check: offset 98 (0x62) is after KV pairs
    # 00 (separator) | 9b e5 27 6d (4 bytes - CRC/hash) | 02 (method?) | 15 00 (name len) | path | 00 | data
    
    print("\n\n--- Detailed entry header analysis ---")
    for i, entry in enumerate(paths_found):
        # Get 20 bytes before the path
        start = max(0, entry['path_offset'] - 10)
        header = ovl[start:entry['path_offset']]
        print(f"\n  Entry {i}: {entry['path']}")
        print(f"    Header bytes (10 before path): {header.hex()}")
        
        # Pattern guess: 
        # [00 terminator of prev entry or separator]
        # [4 bytes: CRC/checksum/hash]  
        # [1 byte: compression type or flags]
        # [2 bytes LE: filename length]
        # [filename]
        # [00 null terminator]
        # [compressed data]
        
        # Check if data is zlib compressed
        data_region = ovl[entry['data_start']:entry['data_start'] + min(entry['data_size_guess'], 65536)]
        
        # Check for sizes embedded in header
        # Maybe the header also contains the compressed size and/or uncompressed size
        if entry['path_offset'] >= 14:
            potential_header = ovl[entry['path_offset']-14:entry['path_offset']-2]
            print(f"    Extended header (14 before len_prefix): {potential_header.hex()}")
            
            # Try to parse: [prev_null] [4 CRC] [4 comp_size] [4 uncomp_size] [1 method] [2 name_len]
            # That's 16 bytes which is a bit much. Let's try other layouts.
            
            # Maybe: ... [compressed_size: 4 bytes] [...] [name_len: 2 bytes]
            # Or maybe the overlay is just zlib-compressed as one stream
        
        # Try various decompression approaches on the data
        if len(data_region) > 4:
            print(f"    Data first 32 bytes: {data_region[:32].hex()}")
            
            # Try raw deflate
            for wbits in [-15, -8, 15, 31, 47]:  # raw, zlib, gzip, auto
                try:
                    dec = zlib.decompress(data_region, wbits)
                    print(f"    DECOMPRESSED with wbits={wbits}: {len(dec)} bytes!")
                    # Show first bytes
                    if all(32 <= b < 127 or b in (9,10,13) for b in dec[:min(50, len(dec))]):
                        print(f"    Text: {dec[:200].decode('ascii', errors='replace')}")
                    else:
                        print(f"    Binary: {dec[:64].hex()}")
                    break
                except Exception:
                    pass
            else:
                # Try with larger windows
                for offset_adj in range(0, 10):
                    adj_data = data_region[offset_adj:]
                    for wbits in [-15, 15, 31, 47]:
                        try:
                            dec = zlib.decompress(adj_data, wbits)
                            print(f"    DECOMPRESSED at +{offset_adj} wbits={wbits}: {len(dec)} bytes!")
                            if all(32 <= b < 127 or b in (9,10,13) for b in dec[:min(50, len(dec))]):
                                print(f"    Text: {dec[:200].decode('ascii', errors='replace')}")
                            else:
                                print(f"    Binary: {dec[:64].hex()}")
                            break
                        except:
                            pass
                    else:
                        continue
                    break
    
    # Also try treating the entire data section after KV pairs as zlib
    print("\n\n--- Trying whole-overlay decompression ---")
    data_section = ovl[98:]  # After KV pairs
    for wbits in [-15, 15, 31, 47]:
        try:
            dec = zlib.decompress(data_section, wbits)
            print(f"  Whole decompression wbits={wbits}: {len(dec)} bytes")
            break
        except:
            pass
    
    # Let's try searching for zlib headers (78 01, 78 5E, 78 9C, 78 DA)
    print("\n--- Searching for zlib headers in overlay ---")
    zlib_markers = [b'\x78\x01', b'\x78\x5E', b'\x78\x9C', b'\x78\xDA']
    for marker in zlib_markers:
        idx = 0
        hits = []
        while True:
            idx = ovl.find(marker, idx)
            if idx == -1:
                break
            hits.append(idx)
            idx += 1
        if hits:
            print(f"  {marker.hex()} found at: {hits[:20]}")
    
    # The entries might use a size field we haven't found yet
    # Let's look right after each null terminator of the filename
    print("\n--- Looking for size fields after filename null terminators ---")
    for i, entry in enumerate(paths_found[:5]):
        # After null terminator of the path, check if there are 4-byte size fields
        pos = entry['data_start']
        if pos + 8 < len(ovl):
            # Read potential sizes
            val1 = struct.unpack('<I', ovl[pos:pos+4])[0]
            val2 = struct.unpack('<I', ovl[pos+4:pos+8])[0]
            val3 = struct.unpack('<H', ovl[pos:pos+2])[0]
            print(f"  Entry {i} ({entry['path']}): next 8 bytes = {ovl[pos:pos+8].hex()}")
            print(f"    As uint32 LE: {val1}, {val2}")
            print(f"    As uint16 LE: {val3}")
            
            # Also check bytes before the 'meta_before' for more context
            # The previous entry's data might have a stored size somewhere
            
    print("\nDone!")

if __name__ == '__main__':
    os.makedirs(OUT_DIR, exist_ok=True)
    main()
