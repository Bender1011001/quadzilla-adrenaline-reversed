# -*- coding: utf-8 -*-
#@title Scan original on-disk EXE for embedded payload signatures and dump chunks
#@category Analysis
#
# This script reads the original program file from disk (not the mapped memory)
# and scans for common container/firmware signatures that may be appended or
# stored in non-mapped overlays. It dumps chunks starting at each signature hit.
#
# Signatures scanned:
#   - ZIP      "PK\x03\x04"
#   - CAB      "MSCF"
#   - 7z       "7z\xBC\xAF'\x1C"
#   - RAR      "Rar!"
#   - XZ       "\xFD7zXZ\x00"
#   - BZIP2    "BZh"
#   - GZIP     "\x1F\x8B"
#   - Intel HEX lines (start with ':')
#   - S-Record lines ('S0'...'S9')
#
# Output files: disk_hit_<label>_<index>.bin (binary) and disk_text_fw_<index>.hex for textual blobs.
#
# Notes:
#   - Written for Ghidra Jython (2.7). Avoids 'nonlocal' and Python 3-only syntax.

import os, re
from java.io import FileInputStream, BufferedInputStream, File
from java.lang import Math

MAX_DUMP = 128 * 1024 * 1024  # dump up to 128 MiB per hit
READ_CHUNK = 1024 * 1024      # 1 MiB streaming buffer
OVERLAP = 64                  # overlap bytes to catch boundary signatures

SIGS = [
    ("zip",  bytearray(b"PK\x03\x04")),
    ("cab",  bytearray(b"MSCF")),
    ("7z",   bytearray(b"7z\xBC\xAF\x27\x1C")),
    ("rar",  bytearray(b"Rar!")),
    ("xz",   bytearray(b"\xFD7zXZ\x00")),
    ("bz2",  bytearray(b"BZh")),
    ("gz",   bytearray(b"\x1F\x8B")),
]

def get_program_path():
    try:
        p = currentProgram.getExecutablePath()
        if p:
            return p
    except Exception:
        pass
    try:
        url = currentProgram.getExecutableURL()
        if url:
            return url.getPath()
    except Exception:
        pass
    return None

def scan_binary_hits(path, label, sig):
    hits = []
    f = File(path)
    size = f.length()
    bis = BufferedInputStream(FileInputStream(f), READ_CHUNK)
    try:
        offset = 0  # use int; Jython will widen to Java long as needed
        prev_tail = bytearray()
        while offset < size:
            to_read = int(min(READ_CHUNK, size - offset))
            buf = bytearray(to_read)
            n = bis.read(buf)
            if n <= 0:
                break
            window = prev_tail + buf[:n]
            # scan window for signature
            i = 0
            last = len(window) - len(sig)
            while i <= last:
                if window[i:i+len(sig)] == sig:
                    hit_off = offset - len(prev_tail) + i
                    if hit_off >= 0:
                        hits.append(hit_off)
                    i += len(sig)
                else:
                    i += 1
            # keep overlap tail
            prev_tail = window[-OVERLAP:] if len(window) >= OVERLAP else window
            offset += n
    finally:
        bis.close()
    if hits:
        print("Found %d %s hits in disk file." % (len(hits), label))
    return hits

def dump_from_offset(path, start_off, max_len, out_name):
    f = File(path)
    size = f.length()
    end_off = min(size, start_off + max_len)
    remaining = int(end_off - start_off)
    if remaining <= 0:
        return False
    bis = BufferedInputStream(FileInputStream(f), READ_CHUNK)
    try:
        # skip to start_off
        skipped_total = 0
        while skipped_total < start_off:
            s = bis.skip(start_off - skipped_total)
            if s <= 0:
                return False
            skipped_total += s
        out = open(out_name, "wb")
        try:
            left = remaining
            while left > 0:
                take = min(READ_CHUNK, left)
                tmp = bytearray(take)
                n = bis.read(tmp)
                if n <= 0:
                    break
                out.write(tmp[:n])
                left -= n
        finally:
            out.close()
    finally:
        bis.close()
    return True

def scan_textual_hex(path):
    # Extract substantial Intel HEX or S-Record runs from disk file
    f = File(path)
    size = f.length()
    bis = BufferedInputStream(FileInputStream(f), READ_CHUNK)
    data = bytearray()
    try:
        while True:
            buf = bytearray(READ_CHUNK)
            n = bis.read(buf)
            if n <= 0:
                break
            data.extend(buf[:n])
    finally:
        bis.close()
    try:
        text = bytes(data).decode("ascii", errors="ignore")
    except:
        print("ASCII decode failed; skipping textual scan.")
        return 0
    lines = text.splitlines()

    out_count = 0
    cur = []
    cur_chars = 0

    def is_hex_record(ln):
        if ln.startswith(":") and re.match(r"^:[0-9A-Fa-f]{4,}", ln):
            return True
        if re.match(r"^S[0-9A-Fa-f]", ln):
            return True
        return False

    for ln in lines:
        if is_hex_record(ln):
            cur.append(ln.strip())
            cur_chars += len(ln) + 1
        else:
            if cur and cur_chars > 4096:
                fname = "disk_text_fw_%02d.hex" % out_count
                with open(fname, "w") as f:
                    f.write("\n".join(cur))
                print("  Wrote %s (len=%d lines)" % (fname, len(cur)))
                out_count += 1
            cur = []
            cur_chars = 0
    if cur and cur_chars > 4096:
        fname = "disk_text_fw_%02d.hex" % out_count
        with open(fname, "w") as f:
            f.write("\n".join(cur))
        print("  Wrote %s (len=%d lines)" % (fname, len(cur)))
        out_count += 1
    return out_count

def main():
    path = get_program_path()
    if not path:
        print("ERROR: Could not resolve program executable path.")
        return
    print("Disk scan of: %s" % path)

    total_hits = 0
    for label, sig in SIGS:
        hits = scan_binary_hits(path, label, sig)
        for idx, off in enumerate(hits):
            out_name = "disk_hit_%s_%04d.bin" % (label, idx)
            ok = dump_from_offset(path, off, MAX_DUMP, out_name)
            if ok:
                print("  Dumped %s from offset 0x%X" % (out_name, off))
                total_hits += 1

    tcount = scan_textual_hex(path)
    if total_hits == 0 and tcount == 0:
        print("No embedded payload signatures found in disk file (common types).")
    else:
        print("Disk extraction complete: %d binary hit(s), %d textual blob(s)." % (total_hits, tcount))

if __name__ == "__main__":
    main()