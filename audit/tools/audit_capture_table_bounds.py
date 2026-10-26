#!/usr/bin/env python3
"""Verify the caller-derived 20x20 signed-table lookup bounds in 0x4B38."""
import argparse
import hashlib
import json
import struct
from collections import Counter
from pathlib import Path

SHA = "1ae519ba6194e8f7bdaaa94333a83a9e6fda3b0563f87f7d48383b37288c1780"
BASE = 0x4000
TABLE_FILE = (0x997C, 0x9B0C)
TABLE_RAM = (0x200294, 0x200424)

# These original-byte decode sites are the complete arithmetic and stack-transfer
# skeleton for the two lookup indices. The branch graph is documented separately.
MAIN = {
    0x5118: "ldr     r0, [pc, #0x2b4]", 0x5120: "cmp     r5, r0",
    0x512A: "movs    r0, #0xe1", 0x512C: "lsls    r0, r0, #2",
    0x5134: "strb    r1, [r0, #1]", 0x5138: "ldr     r0, [pc, #0x298]",
    0x5150: "ldr     r1, [pc, #0x288]", 0x5156: "strb    r1, [r2]",
    0x5158: "ldr     r0, [pc, #0x284]", 0x515E: "mov     r0, sp",
    0x5160: "movs    r1, #0x13", 0x5162: "b       #0x5134",
    0x5166: "ldr     r0, [pc, #0x27c]", 0x516A: "movs    r1, #0x13",
    0x516E: "movs    r1, #0xfa", 0x5170: "lsls    r1, r1, #1",
    0x5172: "bl      #0x8574", 0x5176: "strb    r1, [r2, #1]",
    0x5200: "ldr     r0, [pc, #0x1f0]", 0x5204: "cmp     r0, #0x65",
    0x5208: "movs    r0, #0x13", 0x520A: "str     r0, [sp, #0xc]",
    0x520E: "ldr     r0, [pc, #0x1e4]", 0x5212: "movs    r1, #0x13",
    0x5216: "movs    r1, #0x64", 0x5218: "bl      #0x8574",
    0x5220: "str     r1, [sp, #0xc]",
    0x52AC: "mov     r0, sp", 0x52AE: "ldrb    r2, [r0, #1]",
    0x52B0: "ldr     r1, [sp, #0xc]", 0x52B8: "push    {r0, r1, r2}",
    0x52D2: "bl      #0x4b38",
}
HELPER = {
    0x4CDC: "mov     r1, sp", 0x4CDE: "ldrb    r1, [r1, #0x1c]",
    0x4CE0: "mov     r2, sp", 0x4CE2: "ldrb    r2, [r2, #0x18]",
    0x4CE4: "movs    r3, #0x14", 0x4CE6: "muls    r2, r3, r2",
    0x4CE8: "ldr     r3, [pc, #0x30]", 0x4CEA: "adds    r2, r3, r2",
    0x4CEC: "ldrsb   r1, [r2, r1]",
}
LITERALS = {
    0x53D0: 0x2005EC, 0x53D4: 4001, 0x53D8: 0xFFFFFC18,
    0x53DC: 3000, 0x53E0: 1401, 0x53E4: 0xFFFFFC7C,
    0x53F4: 0x2005F0, 0x4D1C: TABLE_RAM[0],
}


def capture_axis(word):
    """Low byte of main-loop SP+1 at 0x52AE for an unsigned capture word."""
    if not 0 <= word <= 0xFFFFFFFF:
        raise ValueError("capture word outside u32")
    if word < 900:
        return 0
    if word < 1401:
        return 19 * (word - 900) // 500
    return 19


def input_axis(word):
    """Low byte of main-loop SP+0xC at 0x52B0 for an unsigned input word."""
    if not 0 <= word <= 0xFFFFFFFF:
        raise ValueError("input word outside u32")
    return 19 if word >= 101 else 19 * word // 100


def audit(raw, main, helper):
    if any(x != SHA for x in (hashlib.sha256(raw).hexdigest(), main["raw_sha256"], helper["raw_sha256"])):
        raise ValueError("source identity mismatch")
    mi = {int(i["address"], 0): i["text"] for r in main["ranges"] for i in r["instructions"]}
    hi = {int(i["address"], 0): i["text"] for r in helper["ranges"] for i in r["instructions"]}
    if any(mi.get(a) != t for a, t in MAIN.items()) or any(hi.get(a) != t for a, t in HELPER.items()):
        raise ValueError("index construction or stack transfer instructions changed")
    if any(struct.unpack_from("<I", raw, a-BASE)[0] != value for a, value in LITERALS.items()):
        raise ValueError("caller or table-base literal changed")
    table = raw[TABLE_FILE[0]-BASE:TABLE_FILE[1]-BASE]
    if len(table) != 400 or TABLE_RAM[1]-TABLE_RAM[0] != len(table):
        raise ValueError("20x20 table source mapping changed")
    if any(not 0 <= capture_axis(w) <= 19 for w in range(4002)):
        raise ValueError("capture index exceeds table axis on finite branch domain")
    if any(not 0 <= input_axis(w) <= 19 for w in range(102)):
        raise ValueError("input index exceeds table axis on finite branch domain")
    probes = [0, 899, 900, 999, 1000, 1400, 1401, 4000, 4001, 0xFFFFFFFF]
    input_probes = [0, 1, 99, 100, 101, 0xFFFFFFFF]
    if max(capture_axis(w) for w in probes) != 19 or max(input_axis(w) for w in input_probes) != 19:
        raise ValueError("saturation-bound probes changed")
    counts = Counter(table)
    return {
        "format": "quadzilla-capture-table-bounds-v1", "raw_sha256": SHA,
        "evidence_scope": "Direct 0x50F0 caller and original initialized table; later RAM writers and alternate entries remain open",
        "table_source": [hex(x) for x in TABLE_FILE], "table_runtime": [hex(x) for x in TABLE_RAM],
        "table_sha256": hashlib.sha256(table).hexdigest(),
        "shape": [20, 20], "initial_value_min": min(table), "initial_value_max": max(table),
        "initial_negative_signed_cells": sum(x >= 128 for x in table),
        "value_counts": [{"value": k, "count": v} for k, v in sorted(counts.items())],
        "rows": [list(table[i*20:(i+1)*20]) for i in range(20)],
        "capture_axis": {"source": "u32[0x2005ec]", "formula": "0 below 900; floor(19*(W-900)/500) for 900..1400; 19 at or above 1401", "range": [0, 19],
                         "probes": [{"word": hex(w), "index": capture_axis(w)} for w in probes]},
        "input_axis": {"source": "u32[0x2005f0]", "formula": "floor(19*W/100) for 0..100; 19 at or above 101", "range": [0, 19],
                       "probes": [{"word": hex(w), "index": input_axis(w)} for w in input_probes]},
        "lookup": "0x200294 + 20*input_axis + capture_axis",
        "max_offset": 399, "last_address": "0x200423",
        "limitations": ["No proof that RAM table remains unmodified", "No audit of indirect or alternate callers",
                        "No live sensor-range or hardware-output measurement"],
    }


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("image", type=Path)
    p.add_argument("--main-decode", type=Path, default=Path("audit/data/main_control_binaryninja.json"))
    p.add_argument("--helper-decode", type=Path, default=Path("audit/data/capture_scalar_binaryninja.json"))
    p.add_argument("--output", type=Path, required=True)
    args = p.parse_args()
    result = audit(args.image.read_bytes(), json.loads(args.main_decode.read_text()), json.loads(args.helper_decode.read_text()))
    args.output.write_text(json.dumps(result, indent=2)+"\n", encoding="utf-8")
    print(f"20x20 table {result['table_sha256']}; caller maximum offset {result['max_offset']}")


if __name__ == "__main__":
    main()
