# IDAPython 9.x: export reproducible function and control-flow facts from the
# existing Quadzilla ARM7 database. This script performs no device I/O.
import hashlib
import json
from pathlib import Path

import ida_auto
import ida_bytes
import ida_funcs
import ida_ida
import ida_kernwin
import ida_nalt
import ida_ua
import idautils
import idc


IMAGE_START = 0x4000
IMAGE_END = 0xBD00
OUT = Path(r"E:\code.projects\dodge\quadzilla_rev\captures\quadzilla_re\ida_function_map.json")
RAW = Path(r"E:\code.projects\dodge\quadzilla_rev\firmware_v2.8.4HF.bin")


def hex_ea(value):
    return f"0x{int(value):x}"


def main():
    ida_auto.auto_wait()
    functions = []
    calls = set()
    transfers = set()
    data_refs = set()
    for start in idautils.Functions(IMAGE_START, IMAGE_END):
        fn = ida_funcs.get_func(start)
        if fn is None:
            continue
        chunks = [(int(a), int(b)) for a, b in idautils.Chunks(start)]
        instruction_count = 0
        for chunk_start, chunk_end in chunks:
            for ea in idautils.Heads(chunk_start, chunk_end):
                if not ida_bytes.is_code(ida_bytes.get_flags(ea)):
                    continue
                instruction_count += 1
                mnemonic = ida_ua.print_insn_mnem(ea).upper()
                for target in idautils.CodeRefsFrom(ea, False):
                    if IMAGE_START <= target < IMAGE_END:
                        transfers.add((int(start), int(ea), int(target), mnemonic))
                        target_fn = ida_funcs.get_func(target)
                        if mnemonic in ("BL", "BLX") and target_fn is not None:
                            calls.add((int(start), int(ea), int(target_fn.start_ea), mnemonic))
                for target in idautils.DataRefsFrom(ea):
                    data_refs.add((int(start), int(ea), int(target)))
        functions.append(
            {
                "start": hex_ea(start),
                "end": hex_ea(fn.end_ea),
                "size": int(sum(b - a for a, b in chunks)),
                "name": ida_funcs.get_func_name(start),
                "instruction_count": instruction_count,
                "chunks": [[hex_ea(a), hex_ea(b)] for a, b in chunks],
            }
        )
    functions.sort(key=lambda item: int(item["start"], 16))
    result = {
        "format": "quadzilla-disassembler-map-v1",
        "tool": "IDA Pro",
        "tool_version": ida_kernwin.get_kernel_version(),
        "processor": ida_ida.inf_get_procname(),
        "database_input": ida_nalt.get_input_file_path(),
        "raw_image": str(RAW),
        "raw_sha256": hashlib.sha256(RAW.read_bytes()).hexdigest(),
        "image_range": [hex_ea(IMAGE_START), hex_ea(IMAGE_END)],
        "functions": functions,
        "calls": [
            {"caller": hex_ea(a), "site": hex_ea(site), "callee": hex_ea(b), "mnemonic": mnemonic}
            for a, site, b, mnemonic in sorted(calls)
        ],
        "control_transfers": [
            {"function": hex_ea(a), "site": hex_ea(site), "target": hex_ea(b), "mnemonic": mnemonic}
            for a, site, b, mnemonic in sorted(transfers)
        ],
        "data_references": [
            {"function": hex_ea(a), "site": hex_ea(site), "target": hex_ea(b)}
            for a, site, b in sorted(data_refs)
        ],
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(f"WROTE {OUT} functions={len(functions)} calls={len(calls)}")
    idc.qexit(0)


if __name__ == "__main__":
    main()
