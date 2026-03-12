# -*- coding: utf-8 -*-
#@title Extract embedded BZip2 payloads from current program
#@category Analysis
#
# This script scans the loaded program image for BZip2 ('BZh') signatures and attempts to
# decompress each stream using Apache Commons Compress, writing results to payload_XX.bin.
#
# Steps:
#  1) Linear scan of initialized readable memory for 'BZh'
#  2) For each hit, build a contiguous byte window (up to 32 MiB) across memory
#  3) Feed the window to BZip2CompressorInputStream and extract until EOF
#  4) Write decompressed blob to payload_N.bin
#
# Notes:
#  - This is heuristic; some streams may be false positives or truncated.
#  - If the EXE is an installer, these payloads may include the actual ECU firmware.

from ghidra.util.task import ConsoleTaskMonitor
from ghidra.program.model.address import Address
from ghidra.program.flatapi import FlatProgramAPI
from java.io import ByteArrayInputStream, BufferedInputStream, ByteArrayOutputStream
from java.lang import Math
import os

# Try to import Apache Commons Compress BZip2
try:
    from org.apache.commons.compress.compressors.bzip2 import BZip2CompressorInputStream
    HAVE_BZ2 = True
except:
    HAVE_BZ2 = False

SIG = [0x42, 0x5A, 0x68]  # 'B''Z''h'
MAX_WINDOW = 32 * 1024 * 1024  # 32 MiB

def read_linear_bytes(mem, start_addr, max_len):
    """
    Read up to max_len bytes from memory starting at start_addr, walking linearly
    across blocks until reaching max_len or no more initialized readable blocks.
    Returns a Python bytearray with the data actually read.
    """
    out = bytearray()
    cur = start_addr
    remaining = max_len
    while remaining > 0 and cur is not None:
        block = mem.getBlock(cur)
        if block is None or not block.isInitialized() or not block.isRead():
            break
        # Compute how many bytes we can read within this block from cur
        block_end = block.getEnd()
        avail_in_block = int(block_end.subtract(cur)) + 1
        to_read = int(Math.min(avail_in_block, remaining))
        # Read chunk
        buf = bytearray(to_read)
        n = mem.getBytes(cur, buf)
        if n <= 0:
            break
        out.extend(buf[:n])
        remaining -= n
        # Advance to next address
        try:
            cur = cur.add(n)
        except:
            break
    return out

def find_bzh_hits(mem):
    """
    Return a list of Address objects where 'BZh' occurs in initialized readable memory.
    """
    hits = []
    for block in mem.getBlocks():
        if not block.isInitialized() or not block.isRead():
            continue
        # Read this block into a buffer
        size = int(block.getSize())
        if size < 3:
            continue
        buf = bytearray(size)
        mem.getBytes(block.getStart(), buf)
        # Scan for signature
        for i in range(0, size - 2):
            if buf[i] == SIG[0] and buf[i+1] == SIG[1] and buf[i+2] == SIG[2]:
                try:
                    hits.append(block.getStart().add(i))
                except:
                    pass
    return hits

def decompress_bzip2(blob):
    """
    Attempt to decompress a BZip2 stream from the provided bytearray blob.
    Returns (success, decompressed_bytes, used_bytes_or_-1).
    """
    if not HAVE_BZ2:
        return (False, None, -1)
    try:
        bais = ByteArrayInputStream(bytes(blob))
        bis = BufferedInputStream(bais)
        bzis = BZip2CompressorInputStream(bis)  # auto-detect BZ header
        baos = ByteArrayOutputStream()
        # Read until EOF
        buf = bytearray(8192)
        while True:
            # In Jython, we can read into a Java byte[] by creating it from Python bytes
            jbuf = bytes(buf)
            n = bzis.read(jbuf, 0, len(jbuf))
            if n == -1:
                break
            baos.write(jbuf, 0, n)
        # We cannot easily get 'used bytes' from the stream; return -1
        return (True, baos.toByteArray(), -1)
    except Exception as e:
        return (False, None, -1)

def main():
    mem = currentProgram.getMemory()
    fpa = FlatProgramAPI(currentProgram)
    print("Scanning for BZh signatures in initialized memory...")
    hits = find_bzh_hits(mem)
    if not hits:
        print("No BZh signatures found.")
        return
    print("Found %d candidate BZip2 streams." % len(hits))
    out_dir = os.getcwd()
    extracted = 0
    for idx, addr in enumerate(hits):
        print("Processing hit #%d at %s ..." % (idx+1, addr))
        # Read a window of bytes starting at this address
        blob = read_linear_bytes(mem, addr, MAX_WINDOW)
        if not blob or len(blob) < 10:
            print("  Skipping (too short).")
            continue
        ok, decomp, used = decompress_bzip2(blob)
        if not ok or decomp is None or len(decomp) == 0:
            print("  Decompression failed.")
            continue
        # Heuristic sanity check: require at least 4KB output
        if len(decomp) < 4096:
            print("  Output too small (%d bytes) - likely false positive." % len(decomp))
            continue
        out_name = "payload_%02d.bin" % (extracted+1)
        try:
            with open(out_name, "wb") as f:
                f.write(decomp.tostring() if hasattr(decomp, "tostring") else bytearray(decomp))
            print("  Wrote %s (%d bytes)" % (out_name, len(decomp)))
            extracted += 1
        except Exception as e:
            print("  Failed writing output: %s" % str(e))
    if extracted == 0:
        print("No payloads successfully extracted.")
    else:
        print("Extraction complete. %d payload(s) written in %s" % (extracted, out_dir))

if __name__ == "__main__":
    main()