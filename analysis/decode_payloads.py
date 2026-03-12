#!/usr/bin/env python3
"""
Decode firmware payloads from ADR9802v2.8.4.exe.
Find bzip2 streams directly in the binary and decode them.
Also extract the AES-encrypted ZIP overlay.
"""
import base64
import bz2
import os
import struct
import re
import hashlib
import zipfile
import io

EXE_PATH = r'ADR9802v2.8.4.exe'
OUT_DIR = r'extracted/firmware_payloads'

def pad_b64(s):
    """Add proper padding to base64 string."""
    return s + '=' * (-len(s) % 4)

def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    
    with open(EXE_PATH, 'rb') as f:
        data = f.read()
    
    print(f"EXE size: {len(data)} bytes")
    
    # ============================================
    # Approach 1: Find bzip2 streams directly in binary
    # ============================================
    print("\n=== SEARCHING FOR BZh (BZIP2) STREAMS ===")
    idx = 0
    bz_streams = []
    while True:
        idx = data.find(b'BZh', idx)
        if idx == -1:
            break
        # BZh is followed by a digit (block size: 1-9)
        if idx + 3 < len(data) and chr(data[idx+3]).isdigit():
            bz_streams.append(idx)
        idx += 1
    
    print(f"Found {len(bz_streams)} BZh streams")
    for i, off in enumerate(bz_streams):
        block_size = chr(data[off + 3])
        context_before = data[max(0, off-4):off].hex()
        context_after = data[off:off+10].hex()
        print(f"  [{i}] Offset 0x{off:06X}: BZh{block_size} | before: {context_before} | after: {context_after}")
        
        # Try to decompress
        try:
            decompressed = bz2.decompress(data[off:off+1024*1024])  # Max 1MB
            dec_path = os.path.join(OUT_DIR, f'bz2_{i:02d}_0x{off:06X}.bin')
            with open(dec_path, 'wb') as f:
                f.write(decompressed)
            
            md5 = hashlib.md5(decompressed).hexdigest()
            print(f"       DECOMPRESSED: {len(decompressed)} bytes, MD5: {md5}")
            
            # Check content type
            is_text = all(b in (0x09, 0x0A, 0x0D) or 0x20 <= b < 0x7F for b in decompressed[:min(256, len(decompressed))])
            if is_text:
                text_content = decompressed.decode('ascii', errors='replace')
                lines = text_content.split('\n')
                print(f"       TEXT ({len(lines)} lines):")
                for line in lines[:20]:
                    print(f"         {line.rstrip()}")
                if len(lines) > 20:
                    print(f"         ... ({len(lines)} total lines)")
            else:
                print(f"       Binary: {decompressed[:32].hex()}")
                # Check signatures
                if decompressed[:2] == b'MZ':
                    print(f"       -> PE executable!")
                elif decompressed[:1] == b':':
                    print(f"       -> Intel HEX format!")
                elif decompressed[:2] in (b'S0', b'S1', b'S2', b'S3'):
                    print(f"       -> Motorola S-Record!")
                elif decompressed[:4] == b'PK\x03\x04':
                    print(f"       -> ZIP archive!")
                    zpath = os.path.join(OUT_DIR, f'bz2_{i:02d}_0x{off:06X}.zip')
                    with open(zpath, 'wb') as f:
                        f.write(decompressed)
                    try:
                        zf = zipfile.ZipFile(io.BytesIO(decompressed))
                        print(f"       -> ZIP contains: {zf.namelist()}")
                    except:
                        pass
        except Exception as e:
            # Try incremental decompression
            try:
                dobj = bz2.BZ2Decompressor()
                result = dobj.decompress(data[off:off+1024*1024])
                if len(result) > 0:
                    dec_path = os.path.join(OUT_DIR, f'bz2_{i:02d}_0x{off:06X}_partial.bin')
                    with open(dec_path, 'wb') as f:
                        f.write(result)
                    print(f"       Partial: {len(result)} bytes")
                else:
                    print(f"       Empty decompression")
            except Exception as e2:
                print(f"       Decompress failed: {str(e)[:80]}")
    
    # ============================================
    # Approach 2: Extract base64+bzip2 from text regions
    # ============================================
    print("\n\n=== DECODING BASE64 PAYLOADS ===")
    text = data.decode('ascii', errors='ignore')
    
    # Find the c4aeUs blocks (these are at known offsets from Ghidra)
    pattern = re.compile(r'c4aeUs[A-Za-z0-9+/]{20,}={0,2}')
    matches = list(pattern.finditer(text))
    print(f"Found {len(matches)} 'c4aeUs' blocks")
    
    for i, m in enumerate(matches):
        b64_str = m.group()
        offset = m.start()
        
        try:
            padded = pad_b64(b64_str)
            raw = base64.b64decode(padded)
        except Exception as e:
            print(f"  [{i}] 0x{offset:06X}: decode error: {e}")
            continue
        
        print(f"  [{i}] 0x{offset:06X}: b64={len(b64_str)} -> raw={len(raw)} bytes")
        print(f"       Header: {raw[:16].hex()}")
        
        # Look for BZh within
        bz_idx = raw.find(b'BZh')
        if bz_idx >= 0:
            pre_header = raw[:bz_idx]
            print(f"       BZh at +{bz_idx}, pre-header: {pre_header.hex()}")
            
            try:
                dec = bz2.decompress(raw[bz_idx:])
                dec_path = os.path.join(OUT_DIR, f'c4ae_{i:02d}_dec.bin')
                with open(dec_path, 'wb') as f:
                    f.write(dec)
                
                is_text = all(b in (0x09, 0x0A, 0x0D) or 0x20 <= b < 0x7F for b in dec[:min(100, len(dec))])
                if is_text:
                    print(f"       DECODED TEXT ({len(dec)} bytes): {dec[:200].decode('ascii', errors='replace')}")
                else:
                    print(f"       DECODED BIN ({len(dec)} bytes): {dec[:32].hex()}")
            except Exception as e:
                print(f"       BZip2 failed: {str(e)[:60]}")
        else:
            # Save raw
            raw_path = os.path.join(OUT_DIR, f'c4ae_{i:02d}_raw.bin')
            with open(raw_path, 'wb') as f:
                f.write(raw)

    # ============================================
    # Approach 3: Try the overlay as AES-encrypted ZIP
    # ============================================
    print("\n\n=== TRYING OVERLAY AS ENCRYPTED ZIP ===")
    overlay_start = 0x58000
    overlay = data[overlay_start:]
    
    # The overlay has a custom header but might contain a ZIP further in
    # Search for PK\x03\x04 and PK\x01\x02 (central directory)
    pk34 = overlay.find(b'PK\x03\x04')
    pk12 = overlay.find(b'PK\x01\x02')
    pk56 = overlay.find(b'PK\x05\x06')  # End of central directory
    
    print(f"  PK\\x03\\x04 (local file header): {pk34 if pk34 >= 0 else 'NOT FOUND'}")
    print(f"  PK\\x01\\x02 (central directory): {pk12 if pk12 >= 0 else 'NOT FOUND'}")
    print(f"  PK\\x05\\x06 (end of central dir): {pk56 if pk56 >= 0 else 'NOT FOUND'}")
    
    if pk34 >= 0:
        try:
            zf = zipfile.ZipFile(io.BytesIO(overlay[pk34:]))
            print(f"  ZIP opened: {zf.namelist()}")
        except Exception as e:
            print(f"  ZIP open failed: {e}")
    
    # Also search for 7z signature
    sig_7z = overlay.find(b'7z\xBC\xAF\x27\x1C')
    print(f"  7z signature: {sig_7z if sig_7z >= 0 else 'NOT FOUND'}")

    # CAB signature
    sig_cab = overlay.find(b'MSCF')
    print(f"  CAB signature: {sig_cab if sig_cab >= 0 else 'NOT FOUND'}")
    
    print("\nDone!")

if __name__ == '__main__':
    main()
