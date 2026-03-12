# -*- coding: utf-8 -*-
#@title Extract common embedded payload signatures (.rsrc and whole memory)
#@category Analysis
#
# Finds and dumps candidate embedded firmware/container blobs by scanning:
# - The .rsrc section (dump to rsrc_dump.bin)
# - All initialized, readable memory for signature hits:
#     * "PK\x03\x04" (ZIP)
#     * "MSCF" (CAB)
#     * "7z\xBC\xAF\x27\x1C" (7z)
#     * "Rar!" (RAR)
#     * "\xFD7zXZ\x00" (XZ)
#     * "BZh" (BZip2)
#     * "\x1F\x8B" (GZIP)
#     * Intel HEX (lines starting with ':' and hex) and Motorola S-Record ('S0'...'S9')
#
# For each signature hit, dumps up to MAX_SPAN bytes to a file named hit_XXXX.bin starting at the hit.
#
# Note: Jython 2.7 (Ghidra) does not support 'nonlocal'. Avoid nested closures that mutate outer vars.

import os, re
from ghidra.program.flatapi import FlatProgramAPI
from ghidra.util.task import ConsoleTaskMonitor
from java.lang import Math

MAX_SPAN = 64 * 1024 * 1024  # 64 MiB

SIGS = [
    ("zip", bytearray(b"PK\x03\x04")),
    ("cab", bytearray(b"MSCF")),
    ("7z",  bytearray(b"7z\xBC\xAF\x27\x1C")),
    ("rar", bytearray(b"Rar!")),
    ("xz",  bytearray(b"\xFD7zXZ\x00")),
    ("bz2", bytearray(b"BZh")),
    ("gz",  bytearray(b"\x1F\x8B")),
]

def read_linear(mem, start_addr, max_len):
    out = bytearray()
    cur = start_addr
    remaining = max_len
    while remaining > 0 and cur is not None:
        block = mem.getBlock(cur)
        if block is None or not block.isInitialized() or not block.isRead():
            break
        block_end = block.getEnd()
        avail = int(block_end.subtract(cur)) + 1
        take = int(min(avail, remaining))
        buf = bytearray(take)
        n = mem.getBytes(cur, buf)
        if n <= 0:
            break
        out.extend(buf[:n])
        remaining -= n
        try:
            cur = cur.add(n)
        except:
            break
    return out

def dump_rsrc(mem):
    for block in mem.getBlocks():
        nm = block.getName() or ""
        if ".rsrc" in nm or "rsrc" in nm.lower():
            data = read_linear(mem, block.getStart(), int(block.getSize()))
            if data:
                fname = "rsrc_dump.bin"
                with open(fname, "wb") as f:
                    f.write(data)
                print("Dumped .rsrc to %s (%d bytes)" % (fname, len(data)))
            break

def find_sig_hits(mem, label, sig):
    hits = []
    for block in mem.getBlocks():
        if not block.isInitialized() or not block.isRead():
            continue
        size = int(block.getSize())
        if size < len(sig):
            continue
        buf = bytearray(size)
        mem.getBytes(block.getStart(), buf)
        i = 0
        last = size - len(sig)
        while i <= last:
            if buf[i:i+len(sig)] == sig:
                try:
                    hits.append(block.getStart().add(i))
                except:
                    pass
                i += len(sig)
            else:
                i += 1
    if hits:
        print("Found %d %s signature hits." % (len(hits), label))
    return hits

def dump_hits(mem, label, sig):
    hits = find_sig_hits(mem, label, sig)
    idx = 0
    for a in hits:
        blob = read_linear(mem, a, MAX_SPAN)
        if not blob:
            continue
        fname = "hit_%s_%04d.bin" % (label, idx)
        with open(fname, "wb") as f:
            f.write(blob)
        print("  Wrote %s starting at %s (%d bytes cap)" % (fname, a, len(blob)))
        idx += 1

def scan_textual_records(mem):
    # Intel HEX (start with ':') and S-Record ('S0'...'S9') in .rsrc and .rdata/.data
    emitted = 0
    for block in mem.getBlocks():
        if not block.isInitialized() or not block.isRead():
            continue
        nm = (block.getName() or "").lower()
        if not any(s in nm for s in [".rsrc", ".rdata", ".data", "data", "rsrc"]):
            continue
        data = read_linear(mem, block.getStart(), int(block.getSize()))
        if not data:
            continue
        try:
            text = bytes(data).decode("ascii", errors="ignore")
        except:
            continue
        lines = text.splitlines()

        current_run = []
        current_chars = 0

        def is_hex_record(ln):
            if ln.startswith(":") and re.match(r"^:[0-9A-Fa-f]{4,}", ln):
                return True
            if re.match(r"^S[0-9A-Fa-f]", ln):
                return True
            return False

        for ln in lines:
            if is_hex_record(ln):
                current_run.append(ln.strip())
                current_chars += len(ln) + 1
            else:
                if current_run and current_chars > 4096:
                    fname = "text_fw_%02d.hex" % emitted
                    with open(fname, "w") as f:
                        f.write("\n".join(current_run))
                    print("  Wrote %s (len=%d lines)" % (fname, len(current_run)))
                    emitted += 1
                current_run = []
                current_chars = 0

        # flush tail
        if current_run and current_chars > 4096:
            fname = "text_fw_%02d.hex" % emitted
            with open(fname, "w") as f:
                f.write("\n".join(current_run))
            print("  Wrote %s (len=%d lines)" % (fname, len(current_run)))
            emitted += 1

    if emitted == 0:
        print("No Intel HEX / S-Record textual payloads detected.")
    else:
        print("Extracted %d textual record blob(s)." % emitted)

def main():
    mem = currentProgram.getMemory()
    print("Dumping .rsrc section if present...")
    dump_rsrc(mem)
    print("Scanning for container signatures...")
    for label, sig in SIGS:
        dump_hits(mem, label, sig)
    print("Scanning for textual firmware records (Intel HEX / S-Record)...")
    scan_textual_records(mem)
    print("Signature extraction complete.")

if __name__ == "__main__":
    main()