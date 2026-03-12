# -*- coding: utf-8 -*-
#@title Extract PE overlay (bytes beyond last mapped file-backed section)
#@category Analysis
#
# This script computes the end of all file-backed memory mappings in the current
# PE program and, if the on-disk file contains additional data beyond that end
# (the "overlay"), dumps it to overlay.bin. Installers often store payloads here.

from ghidra.program.model.mem import MemoryBlockSourceInfo
from java.io import FileInputStream, BufferedInputStream, File

READ_CHUNK = 1024 * 1024  # 1 MiB

def get_program_path():
    try:
        p = currentProgram.getExecutablePath()
        if p:
            return p
    except:
        pass
    try:
        url = currentProgram.getExecutableURL()
        if url:
            return url.getPath()
    except:
        pass
    return None

def max_mapped_file_end():
    mem = currentProgram.getMemory()
    max_end = 0
    for block in mem.getBlocks():
        try:
            infos = block.getSourceInfos()
        except:
            infos = None
        if not infos:
            continue
        for si in infos:
            try:
                fb = si.getFileBytes()
                if fb is None:
                    continue
                off = si.getFileBytesOffset()
                length = si.getLength()
                end = off + length
                if end > max_end:
                    max_end = end
            except:
                pass
    return max_end

def dump_overlay(path, start_off, out_name):
    f = File(path)
    fsize = f.length()
    if start_off >= fsize:
        print("No overlay detected (file size = %d, mapped end = %d)" % (fsize, start_off))
        return False
    remaining = int(fsize - start_off)
    print("Overlay detected: offset 0x%X, size %d bytes" % (start_off, remaining))
    bis = BufferedInputStream(FileInputStream(f), READ_CHUNK)
    try:
        # skip to overlay start
        skipped_total = 0
        while skipped_total < start_off:
            s = bis.skip(start_off - skipped_total)
            if s <= 0:
                print("Failed to seek to overlay start.")
                return False
            skipped_total += s
        out = open(out_name, "wb")
        try:
            left = remaining
            while left > 0:
                take = min(READ_CHUNK, left)
                buf = bytearray(take)
                n = bis.read(buf)
                if n <= 0:
                    break
                out.write(buf[:n])
                left -= n
        finally:
            out.close()
    finally:
        bis.close()
    print("Wrote %s" % out_name)
    return True

def main():
    path = get_program_path()
    if not path:
        print("ERROR: Could not resolve program executable path.")
        return
    mapped_end = max_mapped_file_end()
    if mapped_end == 0:
        print("Could not determine mapped file end; aborting.")
        return
    dump_overlay(path, mapped_end, "overlay.bin")

if __name__ == "__main__":
    main()