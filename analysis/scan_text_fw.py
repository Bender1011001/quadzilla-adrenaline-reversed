#!/usr/bin/env python3
import sys
import os
import re
from typing import List, Tuple, Dict

IHEX_LINE_RE = re.compile(r"^:([0-9A-Fa-f]{2})([0-9A-Fa-f]{4})([0-9A-Fa-f]{2})([0-9A-Fa-f]*)([0-9A-Fa-f]{2})$")
SREC_LINE_RE = re.compile(r"^(S[0-9A-Fa-f])([0-9A-Fa-f]{2})([0-9A-Fa-f]+)$")

def checksum_ihex(byte_vals: List[int]) -> int:
    return ((-sum(byte_vals)) & 0xFF)

def hexstr_to_bytes(s: str) -> List[int]:
    if len(s) % 2 != 0:
        raise ValueError("Odd hex length")
    return [int(s[i:i+2], 16) for i in range(0, len(s), 2)]

def parse_ihex(lines: List[str]) -> Tuple[Dict[int, int], int, int]:
    mem: Dict[int, int] = {}
    base = 0
    min_addr = None
    max_addr = None
    for ln in lines:
        m = IHEX_LINE_RE.match(ln.strip())
        if not m:
            continue
        reclen = int(m.group(1), 16)
        addr = int(m.group(2), 16)
        rectyp = int(m.group(3), 16)
        data_hex = m.group(4)
        csum = int(m.group(5), 16)
        data_bytes = hexstr_to_bytes(data_hex)
        # Verify length and checksum
        chkl = [reclen, (addr >> 8) & 0xFF, addr & 0xFF, rectyp] + data_bytes
        if (len(data_bytes) != reclen) or (checksum_ihex(chkl) != csum):
            # Fail softly: skip bad lines
            continue
        if rectyp == 0x00:
            full_addr = base + addr
            for i, b in enumerate(data_bytes):
                mem[full_addr + i] = b
            if data_bytes:
                cur_min = full_addr
                cur_max = full_addr + len(data_bytes) - 1
                min_addr = cur_min if min_addr is None else min(min_addr, cur_min)
                max_addr = cur_max if max_addr is None else max(max_addr, cur_max)
        elif rectyp == 0x01:
            # EOF
            pass
        elif rectyp == 0x04:
            # Extended Linear Address
            if len(data_bytes) == 2:
                base = ((data_bytes[0] << 8) | data_bytes[1]) << 16
        # 0x02/0x03/0x05 ignored
    if min_addr is None or max_addr is None:
        return {}, 0, -1
    return mem, min_addr, max_addr

def parse_srec(lines: List[str]) -> Tuple[Dict[int, int], int, int]:
    mem: Dict[int, int] = {}
    min_addr = None
    max_addr = None
    for ln in lines:
        ln = ln.strip()
        if not ln or ln[0] != 'S':
            continue
        m = SREC_LINE_RE.match(ln)
        if not m:
            continue
        rectyp = m.group(1)  # S0,S1,S2,S3,S5,S7,S8,S9
        count = int(m.group(2), 16)
        rest = m.group(3)
        # Determine address length by record type
        if rectyp in ('S1', 'S9'):
            addr_len = 2
        elif rectyp in ('S2', 'S8'):
            addr_len = 3
        elif rectyp in ('S3', 'S7'):
            addr_len = 4
        else:
            # S0,S5 etc not data
            continue
        # count includes address + data + checksum (in bytes)
        # Extract address
        addr_hex = rest[:addr_len*2]
        addr = int(addr_hex, 16)
        data_hex = rest[addr_len*2:-2]  # exclude checksum
        data_bytes = hexstr_to_bytes(data_hex)
        # Best-effort checksum check
        # Compute checksum across count + address bytes + data bytes + checksum == 0xFF
        chk = int(rest[-2:], 16)
        accum = count
        for i in range(0, addr_len*2, 2):
            accum += int(addr_hex[i:i+2], 16)
        for i in range(0, len(data_hex), 2):
            accum += int(data_hex[i:i+2], 16)
        if ((accum + chk) & 0xFF) != 0xFF:
            continue
        # Map data
        for i, b in enumerate(data_bytes):
            mem[addr + i] = b
        if data_bytes:
            cur_min = addr
            cur_max = addr + len(data_bytes) - 1
            min_addr = cur_min if min_addr is None else min(min_addr, cur_min)
            max_addr = cur_max if max_addr is None else max(max_addr, cur_max)
    if min_addr is None or max_addr is None:
        return {}, 0, -1
    return mem, min_addr, max_addr

def find_text_records(buf: bytes) -> Tuple[List[str], List[str]]:
    text = buf.decode('ascii', errors='ignore')
    lines = text.splitlines()
    ihex_chunks: List[str] = []
    srec_chunks: List[str] = []
    # Collect consecutive IHEX lines
    i = 0
    while i < len(lines):
        if lines[i].startswith(':') and IHEX_LINE_RE.match(lines[i].strip()):
            start = i
            # Require at least 5 lines to be considered a blob
            while i < len(lines) and lines[i].startswith(':') and IHEX_LINE_RE.match(lines[i].strip()):
                i += 1
            if i - start >= 5:
                ihex_chunks.extend(lines[start:i])
            continue
        i += 1
    # Collect consecutive SREC lines
    i = 0
    while i < len(lines):
        if lines[i].startswith('S') and SREC_LINE_RE.match(lines[i].strip()):
            start = i
            while i < len(lines) and lines[i].startswith('S') and SREC_LINE_RE.match(lines[i].strip()):
                i += 1
            if i - start >= 5:
                srec_chunks.extend(lines[start:i])
            continue
        i += 1
    return ihex_chunks, srec_chunks

def write_bin(mem: Dict[int, int], start: int, end: int, out_path: str) -> None:
    size = end - start + 1
    out = bytearray([0xFF]) * size
    for a, b in mem.items():
        if start <= a <= end:
            out[a - start] = b
    with open(out_path, 'wb') as f:
        f.write(out)

def main():
    if len(sys.argv) < 2:
        print("Usage: python scan_text_fw.py <file1> [file2 ...]")
        sys.exit(1)
    for p in sys.argv[1:]:
        if not os.path.isfile(p):
            print(f"[{p}] not found")
            continue
        buf = open(p, 'rb').read()
        print("="*72)
        print(f"FILE: {p}  size={len(buf)}")
        ihex_lines, srec_lines = find_text_records(buf)
        print(f"  IHEX lines found: {len(ihex_lines)}")
        print(f"  SREC lines found: {len(srec_lines)}")
        base = os.path.splitext(os.path.basename(p))[0]
        any_out = False
        if ihex_lines:
            ihex_txt = base + ".ihex.txt"
            with open(ihex_txt, 'w') as fw:
                fw.write("\n".join(ihex_lines) + "\n")
            mem, start, end = parse_ihex(ihex_lines)
            if end >= start and mem:
                out_bin = base + ".ihex.bin"
                write_bin(mem, start, end, out_bin)
                print(f"  Wrote IHEX text: {ihex_txt}")
                print(f"  Wrote IHEX BIN : {out_bin}  range=0x{start:08X}-0x{end:08X} size={end-start+1}")
                any_out = True
            else:
                print("  IHEX parse yielded no data (checksum/format mismatch).")
        if srec_lines:
            srec_txt = base + ".srec.txt"
            with open(srec_txt, 'w') as fw:
                fw.write("\n".join(srec_lines) + "\n")
            mem, start, end = parse_srec(srec_lines)
            if end >= start and mem:
                out_bin = base + ".srec.bin"
                write_bin(mem, start, end, out_bin)
                print(f"  Wrote SREC text: {srec_txt}")
                print(f"  Wrote SREC BIN : {out_bin}  range=0x{start:08X}-0x{end:08X} size={end-start+1}")
                any_out = True
            else:
                print("  SREC parse yielded no data (checksum/format mismatch).")
        if not any_out:
            print("  No usable textual firmware records discovered.")
    print("="*72)

if __name__ == "__main__":
    main()