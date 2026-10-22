"""IDAPython: verify database bytes and export critical instruction traces.

Usage: idat -A -S'ida_verify_image.py IMAGE OUTPUT' DATABASE_COPY
"""
import hashlib
import json
from pathlib import Path

import ida_auto
import ida_bytes
import ida_funcs
import ida_kernwin
import idautils
import idc


def main():
    ida_auto.auto_wait()
    raw = Path(idc.ARGV[1]).read_bytes()
    mapped = ida_bytes.get_bytes(0x4000, len(raw))
    if mapped != raw:
        raise RuntimeError("database bytes differ from supplied firmware")
    rows = []
    for start in (0x4818, 0x499C, 0x4A94, 0x4B38, 0x4D38, 0x50F0, 0x59E8,
                  0x601C, 0x6FA0, 0x7BF8, 0x7C1C, 0x7C68, 0x7CC4, 0x7D80):
        fn = ida_funcs.get_func(start)
        if fn is None or fn.start_ea != start:
            raise RuntimeError(f"missing entry {start:#x}")
        instructions = [{"address": hex(ea), "text": idc.generate_disasm_line(ea, 0),
                         "bytes": ida_bytes.get_bytes(ea, idc.get_item_size(ea)).hex()}
                        for ea in idautils.FuncItems(start)
                        if ida_bytes.is_code(ida_bytes.get_flags(ea))]
        rows.append({"entry": hex(start), "thumb": idc.get_sreg(start, "T"),
                     "instructions": instructions})
    constants = {hex(ea): ida_bytes.get_dword(ea) for ea in (0x67C0, 0x67D8)}
    result = {"format": "quadzilla-ida-byte-verified-trace-v1", "tool_version": ida_kernwin.get_kernel_version(),
              "raw_sha256": hashlib.sha256(raw).hexdigest(), "database_bytes_match": True,
              "literal_words": constants, "entries": rows}
    Path(idc.ARGV[2]).write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(f"verified database image; exported {len(rows)} critical traces")
    idc.qexit(0)


if __name__ == "__main__":
    main()
