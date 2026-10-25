#!/usr/bin/env python3
"""Bound direct main-loop writes and count-byte references to source exports."""
import argparse
import hashlib
import json
import re
from pathlib import Path


SHA = "1ae519ba6194e8f7bdaaa94333a83a9e6fda3b0563f87f7d48383b37288c1780"
BASE = 0x200788
COUNT = set(range(BASE + 2, BASE + 7))
STORE = re.compile(r"^STR(B|H)?\s+\w+, \[R5(?:,#(0x[0-9A-F]+|\d+))?\]", re.I)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("image", type=Path)
    parser.add_argument("--ida", type=Path, default=Path("audit/data/ida_image_items.json"))
    parser.add_argument("--bn", type=Path, default=Path("audit/data/main_loop_binaryninja.json"))
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    raw = args.image.read_bytes()
    if len(raw) != 32000 or hashlib.sha256(raw).hexdigest() != SHA:
        raise ValueError("unexpected firmware image")
    ida = json.loads(args.ida.read_text())
    bn = json.loads(args.bn.read_text())
    if ida["raw_sha256"] != SHA or not ida["database_bytes_match"] or bn["raw_sha256"] != SHA:
        raise ValueError("disassembly source identity mismatch")
    bounds = (0x77B8, 0x7A3E)
    body = [row for row in ida["items"] if row["kind"] == "ida_code"
            and bounds[0] <= int(row["start"], 0) < bounds[1]]
    r5_def_sites = [{"site": row["start"], "instruction": row["text"]}
                    for row in body if re.match(r"^\w+\s+R5(?:,|$)", row["text"])]
    if r5_def_sites != [{"site": "0x77c6", "instruction": "LDR             R5, =0x200788"}]:
        raise ValueError("unexpected explicit R5 assignment")
    direct_stores = []
    for row in body:
        match = STORE.match(row["text"])
        if match:
            size = {None: 4, "B": 1, "H": 2}[match.group(1)]
            offset = int(match.group(2), 0) if match.group(2) else 0
            direct_stores.append({"site": row["start"], "size": size,
                                  "offset": offset, "address": hex(BASE + offset)})
    if not direct_stores or any(COUNT.intersection(range(int(row["address"], 0), int(row["address"], 0) + row["size"]))
                                for row in direct_stores):
        raise ValueError("unexpected R5 store pattern or count-byte overlap")
    count_refs = []
    base_refs = []
    for row in ida["items"]:
        if row["kind"] != "ida_code":
            continue
        refs = {int(value, 0) for value in row.get("data_refs", [])}
        for address in sorted(refs & COUNT):
            count_refs.append({"site": row["start"], "instruction": row["text"], "address": hex(address)})
        if BASE in refs:
            base_refs.append({"site": row["start"], "function": row.get("function"),
                              "instruction": row["text"]})
    if len(count_refs) != 5 or any(not row["instruction"].startswith("LDRB") for row in count_refs):
        raise ValueError("unexpected count-byte direct references")
    instructions = bn["ranges"][0]["instructions"]
    if (bn["ranges"][0]["start"], bn["ranges"][0]["end"]) != ("0x77b8", "0x7a3e"):
        raise ValueError("unexpected bounded decode")
    bn_starts = {int(row["address"], 0) for row in instructions}
    ida_starts = {int(row["start"], 0) for row in body}
    if sum(row["length"] for row in instructions) != bounds[1] - bounds[0]:
        raise ValueError("incomplete bounded decode")
    result = {
        "format": "quadzilla-main-loop-count-writer-audit-v1", "raw_sha256": SHA,
        "main_loop": [hex(x) for x in bounds], "bn_instruction_starts": len(bn_starts),
        "ida_code_item_starts": len(ida_starts),
        "bn_only_starts": [hex(x) for x in sorted(bn_starts - ida_starts)],
        "ida_only_starts": [hex(x) for x in sorted(ida_starts - bn_starts)],
        "main_loop_explicit_r5_assignments": r5_def_sites,
        "main_loop_r5_direct_stores": direct_stores,
        "global_direct_count_references": count_refs,
        "global_direct_state_base_references": base_refs,
        "limits": [
            "R5 is loaded from the 0x200788 literal at 0x77c6 and has no explicit reassignment in the bounded body; subordinate calls are separate paths",
            "IDA data references are a static xref inventory, not complete alias analysis",
            "computed pointers, interrupt effects, and downstream callees remain possible count writers",
        ],
    }
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(f"{len(direct_stores)} direct R5 stores; {len(count_refs)} count-byte xrefs")


if __name__ == "__main__":
    main()
