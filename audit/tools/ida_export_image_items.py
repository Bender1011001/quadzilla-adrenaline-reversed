"""IDAPython: export full-image item classifications and instruction facts.

Usage: -S"SCRIPT IMAGE OUTPUT" DATABASE_COPY
Classification is IDA's interpretation, not a manual byte-coverage verdict.
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

BASE, END = 0x4000, 0xBD00


def main():
    ida_auto.auto_wait()
    raw = Path(idc.ARGV[1]).read_bytes()
    if len(raw) != END-BASE or ida_bytes.get_bytes(BASE, len(raw)) != raw:
        raise RuntimeError("database/image byte mismatch")
    rows = []
    ea = BASE
    while ea < END:
        flags = ida_bytes.get_flags(ea)
        end = min(END, max(ea+1, ida_bytes.get_item_end(ea)))
        kind = "ida_code" if ida_bytes.is_code(flags) else "ida_data" if ida_bytes.is_data(flags) else "ida_unknown"
        fn = ida_funcs.get_func(ea)
        row = {"start": hex(ea), "end": hex(end), "kind": kind,
               "thumb": idc.get_sreg(ea, "T"), "function": hex(fn.start_ea) if fn else None}
        if kind == "ida_code":
            row.update(text=idc.generate_disasm_line(ea, 0), mnemonic=idc.print_insn_mnem(ea),
                       code_refs=[hex(x) for x in idautils.CodeRefsFrom(ea, False)],
                       data_refs=[hex(x) for x in idautils.DataRefsFrom(ea)])
            if idc.get_operand_type(ea, 0) == idc.o_near:
                row["decoded_direct_target"] = hex(idc.get_operand_value(ea, 0))
        rows.append(row)
        ea = end
    result = {"format": "quadzilla-image-items-v1", "tool": "IDA Pro", "tool_version": ida_kernwin.get_kernel_version(),
              "raw_sha256": hashlib.sha256(raw).hexdigest(), "database_bytes_match": True,
              "image_range": [hex(BASE), hex(END)], "items": rows,
              "limitation": "IDA flags and mode are analysis candidates, not manually verified semantics; no vendor binary bytes included"}
    Path(idc.ARGV[2]).write_text(json.dumps(result, indent=2)+"\n", encoding="utf-8")
    print(f"exported {len(rows)} items covering {END-BASE} bytes")
    idc.qexit(0)


if __name__ == "__main__":
    main()
