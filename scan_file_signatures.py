# -*- coding: utf-8 -*-
#@title Scan an arbitrary on-disk file for embedded payload signatures and dump chunks
#@category Analysis
#
# Usage in headless:
#   -postScript scan_file_signatures.py <path-to-file>
#
# Scans the specified file (not currentProgram) for:
#   - ZIP   "PK\x03\x04"
#   - CAB   "MSCF"
#   - 7z    "7z\xBC\xAF'\x1C"
#   - RAR   "Rar!"
#   - XZ    "\xFD7zXZ\x00"
#   - BZIP2 "BZh"
#   - GZIP  "\x1F\x8B"
#   - Intel HEX records (text lines starting with ':')
#   - Motorola S-Records (text lines starting with 'S')
#
# Outputs:
#   - bin chunks: file_hit_<label>_<idx>.bin (up to MAX_DUMP bytes from each hit)
#   - textual:    file_text_fw_<idx>.hex (joined lines of substantial record runs)

import os, re
from java.io import FileInputStream, BufferedInputStream, File
from ghidra.app.script import GhidraScript

MAX_DUMP   = 128 * 1024 * 1024  # 128 MiB per hit
READ_CHUNK = 1024 * 1024        # 1 MiB buffer
OVERLAP    = 64                 # bytes overlap between reads

SIGS = [
    ("zip",  bytearray(b"PK\x03\x04")),
    ("cab",  bytearray(b"MSCF")),
    ("7z",   bytearray(b"7z\xBC\xAF\x27\x1C")),
    ("rar",  bytearray(b"Rar!")),
    ("xz",   bytearray(b"\xFD7zXZ\x00")),
    ("bz2",  bytearray(b"BZh")),
    ("gz",   bytearray(b"\x1F\x8B")),
]

class ScanFileSignatures(GhidraScript):
    def run(self):
        args = self.getScriptArgs()
        if not args or len(args) < 1:
            self.println("ERROR: provide a file path argument. Example:")
            self.println("  -postScript scan_file_signatures.py C:/path/to/overlay.bin")
            return
        path = args[0]
        f = File(path)
        if not f.exists():
            self.println("ERROR: file does not exist: %s" % path)
            return
        self.println("Scanning file: %s" % path)
        total_hits = 0
        for label, sig in SIGS:
            hits = self._scan_binary_hits(path, label, sig)
            for idx, off in enumerate(hits):
                out_name = "file_hit_%s_%04d.bin" % (label, idx)
                if self._dump_from_offset(path, off, MAX_DUMP, out_name):
                    self.println("  Dumped %s from offset 0x%X" % (out_name, off))
                    total_hits += 1
        tcount = self._scan_textual_hex(path)
        if total_hits == 0 and tcount == 0:
            self.println("No embedded payload signatures found (common types).")
        else:
            self.println("Extraction complete: %d binary hit(s), %d textual blob(s)." % (total_hits, tcount))

    def _scan_binary_hits(self, path, label, sig):
        hits = []
        f = File(path)
        size = f.length()
        bis = BufferedInputStream(FileInputStream(f), READ_CHUNK)
        try:
            offset = 0
            prev_tail = bytearray()
            while offset < size:
                to_read = int(min(READ_CHUNK, size - offset))
                buf = bytearray(to_read)
                n = bis.read(buf)
                if n <= 0:
                    break
                window = prev_tail + buf[:n]
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
                prev_tail = window[-OVERLAP:] if len(window) >= OVERLAP else window
                offset += n
        finally:
            bis.close()
        if hits:
            self.println("Found %d %s hits." % (len(hits), label))
        return hits

    def _dump_from_offset(self, path, start_off, max_len, out_name):
        f = File(path)
        size = f.length()
        end_off = min(size, start_off + max_len)
        remaining = int(end_off - start_off)
        if remaining <= 0:
            return False
        bis = BufferedInputStream(FileInputStream(f), READ_CHUNK)
        try:
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

    def _scan_textual_hex(self, path):
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
            self.println("ASCII decode failed; skipping textual scan.")
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
                    fname = "file_text_fw_%02d.hex" % out_count
                    with open(fname, "w") as fw:
                        fw.write("\n".join(cur))
                    self.println("  Wrote %s (len=%d lines)" % (fname, len(cur)))
                    out_count += 1
                cur = []
                cur_chars = 0
        if cur and cur_chars > 4096:
            fname = "file_text_fw_%02d.hex" % out_count
            with open(fname, "w") as fw:
                fw.write("\n".join(cur))
            self.println("  Wrote %s (len=%d lines)" % (fname, len(cur)))
            out_count += 1
        return out_count