#!/usr/bin/env jython
# Ghidra headless/Jython script: scan currentProgram for 256-byte CRC-8 lookup tables.
# - Works on any binary (e.g., overlay.bin) loaded into the current Ghidra project.
# - Matches several common CRC-8 polynomials in both normal and reflected forms.
# - Writes results to "crc_table_hits_overlay.txt" in the current working directory.
#
# Usage (headless):
#   analyzeHeadless.bat . <projectName> -process "overlay.bin" -scriptPath . -postScript find_crc_tables.py
#
# Notes:
# - This script assumes the table is stored as 256 consecutive bytes (uint8).
# - It attempts normal and reflected algorithms; tables are independent of init/xorout so those are not needed.

from __future__ import print_function

# Ghidra imports
from ghidra.util import Msg

# Jython/Java interop
from jarray import zeros

# ----------------------------------------------------------------------
# Utilities
# ----------------------------------------------------------------------

def u8(x):
    return x & 0xFF

def gen_crc8_table(poly, reflected=False):
    # Generate a 256-element CRC-8 table
    t = [0] * 256
    if not reflected:
        for i in range(256):
            crc = i
            for _ in range(8):
                if (crc & 0x80) != 0:
                    crc = ((crc << 1) & 0xFF) ^ poly
                else:
                    crc = (crc << 1) & 0xFF
            t[i] = u8(crc)
    else:
        # Reflected bit ordering (LSB-first)
        for i in range(256):
            crc = i
            for _ in range(8):
                if (crc & 0x01) != 0:
                    crc = (crc >> 1) ^ poly
                else:
                    crc = crc >> 1
            t[i] = u8(crc)
    return t

def to_py_list(java_byte_array):
    # Convert signed Java bytes to Python ints 0..255
    return [u8(b) for b in java_byte_array]

def compare_slice(buf, off, table):
    # Fast compare of 256 bytes at buf[off:off+256] to table (list of ints)
    # Early-out macro checks
    if buf_len - off < 256:
        return False
    if buf[off] != table[0]:
        return False
    # Last-byte quick-check too
    if buf[off + 255] != table[255]:
        return False
    for i in range(256):
        if buf[off + i] != table[i]:
            return False
    return True

def scan_block(memory, block, tables, hits, println):
    size = int(block.getSize())
    if size < 256:
        return
    start = block.getStart()
    # Read block bytes into a Java byte[] then to Python list
    ba = zeros(size, 'b')
    memory.getBytes(start, ba, 0, size)
    buf = to_py_list(ba)

    global buf_len
    buf_len = size

    # Build quick candidate dictionary keyed by first byte for speed
    first_map = {}
    for name, variant, table in tables:
        first_map.setdefault(table[0], []).append((name, variant, table))

    for off in range(0, size - 256 + 1):
        fb = buf[off]
        cand = first_map.get(fb)
        if not cand:
            continue
        for (name, variant, table) in cand:
            if compare_slice(buf, off, table):
                addr = start.add(off)
                hits.append((addr, name, variant))
                println("CRC8 table hit at %s: %s [%s]" % (addr, name, variant))

# ----------------------------------------------------------------------
# Main
# ----------------------------------------------------------------------

def main():
    try:
        # currentProgram is provided by GhidraScript environment
        prog = currentProgram
    except NameError:
        prog = None

    if prog is None:
        # If script is not running inside a program context
        try:
            println("No current program context; aborting.")
        except:
            pass
        return

    mem = prog.getMemory()

    # Common CRC-8 polynomials (normal/reflected)
    # Note: Reflected forms use the reflected polynomial value for the LSB-first algorithm.
    POLYS = [
        ("CRC-8",               0x07, False, "normal"),
        ("CRC-8 (reflected)",   0x07, True,  "reflected"),         # many use refin=true with same poly
        ("CRC-8/MAXIM",         0x8C, True,  "reflected"),         # 0x31 reflected -> 0x8C
        ("CRC-8/SAE-J1850",     0x1D, False, "normal"),
        ("CRC-8/SAE-J1850 (R)", 0x1D, True,  "reflected"),
        ("CRC-8/AUTOSAR",       0x2F, False, "normal"),
        ("CRC-8/AUTOSAR (R)",   0x2F, True,  "reflected"),
        ("CRC-8/DVB-S2",        0xD5, False, "normal"),
        ("CRC-8/DVB-S2 (R)",    0xD5, True,  "reflected"),
        ("CRC-8/CDMA2000",      0x9B, False, "normal"),
        ("CRC-8/CDMA2000 (R)",  0x9B, True,  "reflected"),
        ("CRC-8/ROHC",          0x07, True,  "reflected"),         # ROHC uses refin/refout true
    ]

    # Precompute tables (and also reversed-order tables to catch reversed storage)
    tables = []
    for (name, poly, is_reflected, variant) in POLYS:
        t = gen_crc8_table(poly, reflected=is_reflected)
        tables.append(("%s" % name, "%s" % variant, t))

    # Also add reversed-order versions to match if table stored backwards
    rev_tables = []
    for (name, variant, t) in tables:
        rev_tables.append(("%s" % name, "%s-reversed" % variant, list(reversed(t))))

    all_tables = []
    for (name, variant, t) in tables + rev_tables:
        all_tables.append((name, variant, t))

    hits = []
    # Iterate initialized memory blocks
    blocks = mem.getBlocks()
    for blk in blocks:
        try:
            if not blk.isInitialized():
                continue
            scan_block(mem, blk, all_tables, hits, println)
        except Exception as e:
            Msg.warn(self, "Error scanning block %s: %s" % (blk, str(e)))

    # Write out results
    out_name = "crc_table_hits_overlay.txt"
    try:
        with open(out_name, "w") as f:
            f.write("Program: %s\n" % prog.getName())
            f.write("CRC-8 lookup table candidates (256 bytes) found: %d\n" % len(hits))
            for (addr, name, variant) in hits:
                f.write("%s | %s | %s\n" % (addr, name, variant))
        println("Wrote %d hits to %s" % (len(hits), out_name))
    except Exception as e:
        println("Failed writing results: %s" % str(e))

if __name__ == "__main__":
    main()