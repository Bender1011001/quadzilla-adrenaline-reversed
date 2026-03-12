#!/usr/bin/env python2
#@category Quadzilla
# Headless-friendly: If no args are provided, defaults to reading "overlay.bin"
# Scans the specified file for common container/compression/firmware signatures and carves each hit to disk.
# This does not require a Ghidra program context and can run as -postScript without -process.
#
# Usage:
#   -postScript overlay_probe.py [overlay_file]
#
# Output:
#   - Writes found signature hits to stdout with offsets
#   - Carves each hit to carved_<name>_0x<offset>.<ext> in current working dir

import os
import sys
from ghidra.app.script import GhidraScript

class OverlayProbe(GhidraScript):
    def run(self):
        try:
            args = self.getScriptArgs()
        except:
            args = []
        # Default to overlay.bin in CWD if not provided
        target = args[0] if (args and len(args) >= 1) else "overlay.bin"

        if not os.path.isabs(target):
            # Headless CWD is typically the working dir we launched from
            target_path = os.path.join(os.getcwd(), target)
        else:
            target_path = target

        if not os.path.isfile(target_path):
            self.println("ERROR: File not found: %s" % target_path)
            self.println("Usage: -postScript overlay_probe.py overlay.bin")
            return

        self.println("Scanning file: %s" % target_path)
        data = None
        with open(target_path, "rb") as f:
            data = f.read()

        hits = []

        def add_hit(name, off, ext, desc=""):
            hits.append((name, off, ext, desc))

        def find_all(needle):
            off = 0
            while True:
                idx = data.find(needle, off)
                if idx == -1:
                    break
                yield idx
                off = idx + 1

        # Signatures dictionary: name -> (magic bytes, ext, description)
        sigs = [
            ("ZIP", b"PK\x03\x04", "zip", "ZIP local file header"),
            ("GZIP", b"\x1f\x8b\x08", "gz", "GZIP (deflate)"),
            ("BZIP2", b"BZh", "bz2", "BZip2"),
            ("XZ", b"\xfd7zXZ\x00", "xz", "XZ (LZMA2)"),
            ("LZMA_Raw?", b"\x5d\x00\x00\x80\x00", "lzma", "Potential raw LZMA header"),
            ("RAR4", b"Rar!\x1a\x07\x00", "rar", "RAR v4"),
            ("RAR5", b"Rar!\x1a\x07\x01\x00", "rar", "RAR v5"),
            ("7Z", b"7z\xbc\xaf\x27\x1c", "7z", "7-Zip"),
            ("ELF", b"\x7fELF", "elf", "ELF executable"),
            ("MZ", b"MZ", "exe", "DOS/PE MZ header"),
            ("Ustar", b"ustar", "tar", "TAR (ustar) marker"),
            # Some common firmware container markers (heuristic)
            ("CRAMFS", b"\x28\xcd\x3d\x45\x00\x00\x00\x00", "cramfs", "CRAMFS magic"),
            ("SQUASHFS", b"hsqs", "squashfs", "SquashFS (little-endian)"),
            ("SQUASHFS_BE", b"sqsh", "squashfs", "SquashFS (big-endian)"),
        ]

        # Scan magic hits
        for name, magic, ext, desc in sigs:
            for off in find_all(magic):
                add_hit(name, off, ext, desc)

        # Attempt to detect Intel HEX text blocks inside binary
        # Strategy: look for a ":" followed by a plausible record, and consecutive lines
        def detect_intel_hex(buf):
            results = []
            off = 0
            end = len(buf)
            while True:
                pos = buf.find(":", off)
                if pos == -1:
                    break
                # Scan next few hundred bytes for newlines and ':' occurrences
                window = buf[pos:pos+4096]
                lines = window.splitlines()
                valid = 0
                total = 0
                for ln in lines[:200]:
                    total += 1
                    if total < 3 and not ln.startswith(":"):
                        break
                    if len(ln) > 1 and ln.startswith(":"):
                        valid += 1
                    else:
                        break
                if valid >= 5:
                    results.append(pos)
                off = pos + 1
            return results

        try:
            intel_hex_hits = detect_intel_hex(data.decode('latin-1'))
            for pos in intel_hex_hits:
                add_hit("IHEX_text", pos, "hex", "Intel HEX textual records (heuristic)")
        except Exception as e:
            # If decode fails, skip textual scan
            pass

        # Sort hits by offset
        hits.sort(key=lambda x: x[1])

        if not hits:
            self.println("No known signatures found.")
            return

        self.println("Found %d signature hits:" % len(hits))
        for name, off, ext, desc in hits:
            self.println("  - %-10s @ 0x%08X [%s]" % (name, off, desc))

        # Carving approach:
        # - For container/compression formats, carve from hit offset to either:
        #   (a) next hit offset (acts as boundary guess), or
        #   (b) EOF if no later hit
        # This is a heuristic but often works to extract usable objects.
        # We avoid carving very tiny slices (< 1KB) to reduce noise.
        carve_min = 1024  # bytes
        out_count = 0
        for idx, (name, off, ext, desc) in enumerate(hits):
            end = len(data)
            if idx + 1 < len(hits):
                # If the next hit is too close (< 512 bytes), we still carve to next hit to avoid overlap.
                end = hits[idx + 1][1]
                if end <= off:
                    end = len(data)
            size = end - off
            if size < carve_min:
                continue
            out_name = "carved_%s_0x%X.%s" % (name.lower(), off, ext)
            try:
                with open(out_name, "wb") as wf:
                    wf.write(data[off:end])
                out_count += 1
                self.println("Carved %s (%d bytes)" % (out_name, size))
            except Exception as e:
                self.println("Failed to write %s: %s" % (out_name, str(e)))

        self.println("Carving complete. Wrote %d files." % out_count)

if __name__ == "__main__":
    # In Ghidra headless, this module will be loaded and OverlayProbe.run() invoked automatically.
    # This block allows running under Jython standalone, but we do nothing here.
    pass