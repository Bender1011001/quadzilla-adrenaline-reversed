#!/usr/bin/env python3
"""Verify 0x4B38 code islands, byte jump tables, and literal pool."""
import argparse
import hashlib
import json
import re
import struct
from pathlib import Path

SHA = "1ae519ba6194e8f7bdaaa94333a83a9e6fda3b0563f87f7d48383b37288c1780"
RANGES = ((0x4B38, 0x4B84), (0x4BA2, 0x4C34), (0x4C3E, 0x4D0C))
CODE = ((0x4B38, 0x4B82), (0x4BA2, 0x4C32), (0x4C3E, 0x4D0A))
NOP = (0x4B82, 0x4C32, 0x4D0A)
TABLES = ((0x4B84, 0x4BA1, 0x4B84), (0x4C34, 0x4C3E, 0x4C34))
LITERALS = (0x4D0C, 0x4D38)


def audit(raw, decode, ida):
    if any(x != SHA for x in (hashlib.sha256(raw).hexdigest(), decode["raw_sha256"], ida["raw_sha256"])):
        raise ValueError("source identity mismatch")
    ranges = decode["ranges"]
    if [(int(r["start"], 0), int(r["end"], 0), r["architecture"]) for r in ranges] != [(*r, "thumb2") for r in RANGES]:
        raise ValueError("bounded decode ranges differ")
    instructions = []
    for row in ranges:
        if "decode_stopped_at" in row:
            raise ValueError("bounded decode stopped early")
        cursor = int(row["start"], 0)
        for ins in row["instructions"]:
            if int(ins["address"], 0) != cursor or ins["length"] not in (2, 4):
                raise ValueError("instruction gap, overlap, or invalid width")
            cursor += ins["length"]
            instructions.append(ins)
        if cursor != int(row["end"], 0):
            raise ValueError("bounded decode did not reach end")
    starts = {int(i["address"], 0) for i in instructions}
    for a in NOP:
        if raw[a-0x4000:a-0x4000+2] != b"\xc0\x46":
            raise ValueError("alignment NOP changed")
        if next(i for i in instructions if int(i["address"], 0) == a)["text"].strip() != "mov     r8, r8":
            raise ValueError("alignment decode changed")
    ida_code = [i for i in ida["items"] if i["kind"] == "ida_code" and RANGES[0][0] <= int(i["start"], 0) < RANGES[-1][1]]
    ida_starts = {int(i["start"], 0) for i in ida_code}
    folded = sorted(starts - ida_starts)
    if folded != [0x4CFA] or not any(int(i["start"], 0) < 0x4CFA < int(i["end"], 0) for i in ida_code):
        raise ValueError("IDA pseudo-instruction boundary changed")

    table_rows = []
    for lo, hi, pc_base in TABLES:
        entries = []
        for index, a in enumerate(range(lo, hi)):
            offset = raw[a-0x4000]
            target = pc_base + offset
            if target not in starts or not any(ca <= target < cb for ca, cb in CODE):
                raise ValueError(f"jump-table target is not a code start: {a:#x}")
            entries.append({"index": index, "offset": offset, "target": hex(target)})
        table_rows.append({"start": hex(lo), "end": hex(hi), "pc_base": hex(pc_base), "entries": entries})
    if raw[0x4BA1-0x4000] != 0:
        raise ValueError("first table padding changed")

    refs, branches, calls = {}, [], []
    for ins in instructions:
        at, text = int(ins["address"], 0), ins["text"].strip()
        m = re.fullmatch(r"ldr\s+r\d+, \[pc, #0x([0-9a-f]+)\]", text)
        if m:
            target = ((at+4) & ~3) + int(m.group(1), 16)
            refs.setdefault(target, []).append(at)
        m = re.fullmatch(r"(b[a-z]*)\s+#(0x[0-9a-f]+)", text)
        if m:
            op, target = m.group(1), int(m.group(2), 0)
            if op == "bl":
                calls.append((at, target))
            else:
                if target not in starts or not any(ca <= target < cb for ca, cb in CODE):
                    raise ValueError(f"direct branch target is not a code start: {at:#x}")
                branches.append((at, target, op))
    if set(refs) != set(range(*LITERALS, 4)) or any(len(x) != 1 for x in refs.values()):
        raise ValueError("literal pool is not exactly accounted for")
    if len(branches) != 55 or len(calls) != 9 or {b for _, b in calls} != {0x47B0, 0x8574}:
        raise ValueError("direct flow inventory changed")
    return {
        "format": "quadzilla-capture-scalar-structure-v1", "raw_sha256": SHA,
        "limitation": "Source-bound code/data and direct target reconciliation, not proof of runtime input ranges or hardware effects",
        "code_ranges": [[hex(a), hex(b)] for a, b in CODE],
        "alignment_nops": [hex(a) for a in NOP],
        "decoded_instruction_starts_including_nops": len(starts),
        "ida_folded_second_starts": [hex(a) for a in folded],
        "byte_jump_tables": table_rows, "first_table_pad_zero": "0x4ba1",
        "literal_words": [{"address": hex(a), "value": hex(struct.unpack_from('<I', raw, a-0x4000)[0]),
                           "load_site": hex(refs[a][0])} for a in range(*LITERALS, 4)],
        "internal_direct_branches": [{"site": hex(a), "target": hex(b), "opcode": op} for a, b, op in branches],
        "direct_calls": [{"site": hex(a), "target": hex(b)} for a, b in calls],
    }


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("image", type=Path)
    p.add_argument("--decode", type=Path, default=Path("audit/data/capture_scalar_binaryninja.json"))
    p.add_argument("--ida", type=Path, default=Path("audit/data/ida_image_items.json"))
    p.add_argument("--output", type=Path, required=True)
    args = p.parse_args()
    result = audit(args.image.read_bytes(), json.loads(args.decode.read_text()), json.loads(args.ida.read_text()))
    args.output.write_text(json.dumps(result, indent=2)+"\n", encoding="utf-8")
    print(f"{result['decoded_instruction_starts_including_nops']} decoded starts; "
          f"{sum(len(t['entries']) for t in result['byte_jump_tables'])} indexed table bytes; "
          f"{len(result['literal_words'])} literals")


if __name__ == "__main__":
    main()
