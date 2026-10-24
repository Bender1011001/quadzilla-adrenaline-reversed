"""IDAPython: bounded ARM decode on a disposable database copy.

Usage: -S"SCRIPT IMAGE OUTPUT" DATABASE_COPY. Existing items in the two reviewed
code ranges are removed before decoding; the literal at 0x896C is excluded. Never use the
researcher's original database for this verification pass.
"""
import hashlib
import json
import struct
from pathlib import Path

import ida_auto
import ida_bytes
import ida_kernwin
import ida_ida
import ida_segment
import ida_ua
import idc


def main():
    ida_auto.auto_wait()
    raw = Path(idc.ARGV[1]).read_bytes()
    sha = hashlib.sha256(raw).hexdigest()
    if sha != "1ae519ba6194e8f7bdaaa94333a83a9e6fda3b0563f87f7d48383b37288c1780":
        raise ValueError("unexpected image or database bytes")
    if ida_bytes.get_bytes(0x4000, len(raw)) != raw:
        loaded_at = ida_ida.inf_get_min_ea()
        if ida_bytes.get_bytes(loaded_at, len(raw)) != raw:
            raise ValueError("database bytes do not match source at loaded base")
        ida_segment.rebase_program(0x4000-loaded_at, ida_segment.MSF_FIXONCE)
        if ida_bytes.get_bytes(0x4000, len(raw)) != raw:
            raise RuntimeError("cannot rebase the disposable image database")
    ida_auto.enable_auto(False)
    ida_ida.inf_set_be(False)
    ida_ida.inf_set_macros_enabled(False)
    ranges = []
    for start, end in ((0x8678, 0x896C), (0x8970, 0x96C4)):
        ida_bytes.del_items(start, ida_bytes.DELIT_SIMPLE, end-start)
        if not idc.split_sreg_range(start, "T", 0):
            raise RuntimeError("cannot set ARM mode")
        instructions = []
        for address in range(start, end, 4):
            # Explicitly override old per-address mode changes from the original
            # auto-analysis; no analysis or function discovery is requested.
            idc.split_sreg_range(address, "T", 0)
            insn = ida_ua.insn_t()
            decoded_size = ida_ua.decode_insn(insn, address)
            if decoded_size != 4:
                word = struct.unpack_from("<I", raw, address-0x4000)[0]
                instructions.append({"address": hex(address), "length": 4, "decode_status": "unrecognized_by_ida",
                                     "condition": word >> 28})
                continue
            row = {"address": hex(address), "length": 4, "mnemonic": insn.get_canon_mnem(),
                   "condition": struct.unpack_from("<I", raw, address-0x4000)[0] >> 28,
                   "operand_types": [op.type for op in insn.ops if op.type != ida_ua.o_void]}
            if insn.ops[0].type == ida_ua.o_near:
                row["direct_target"] = hex(insn.ops[0].addr)
            instructions.append(row)
        ranges.append({"start": hex(start), "end": hex(end), "isa": "arm", "instructions": instructions})
    result = {"format": "quadzilla-soft-float-ida-v1", "raw_sha256": sha,
              "database_bytes_match": True, "tool": "IDA Pro "+ida_kernwin.get_kernel_version(),
              "decode_gaps": [i["address"] for r in ranges for i in r["instructions"] if "decode_status" in i],
              "ranges": ranges, "excluded_literal": {"start": "0x896c", "end": "0x8970", "value": "0x200af8"},
              "limits": "Partial explicit-mode decode: unrecognized word slots are retained as gaps, not accepted IDA instructions. Not independent function discovery or complete behavioral verification."}
    Path(idc.ARGV[2]).write_text(json.dumps(result, indent=2)+"\n", encoding="utf-8")
    idc.qexit(0)


if __name__ == "__main__":
    main()
