#!/usr/bin/env python3
"""Verify main-control code/pool boundaries and enumerate direct flow."""
import argparse
import hashlib
import json
import re
import struct
from collections import Counter
from pathlib import Path

SHA = "1ae519ba6194e8f7bdaaa94333a83a9e6fda3b0563f87f7d48383b37288c1780"
CODE = ((0x50F0, 0x53C4), (0x5414, 0x5612))
POOLS = ((0x53C4, 0x5414), (0x5614, 0x56FC))
EXPECTED_FOLDED = (0x511E, 0x512C, 0x5170, 0x526E, 0x528C, 0x52A4, 0x535C, 0x5370)


def audit(raw, decode, ida):
    if hashlib.sha256(raw).hexdigest() != SHA or decode["raw_sha256"] != SHA or ida["raw_sha256"] != SHA:
        raise ValueError("source identity mismatch")
    ranges = decode["ranges"]
    if [(int(r["start"], 0), int(r["end"], 0)) for r in ranges] != [(0x50F0, 0x53C4), (0x5414, 0x5614)]:
        raise ValueError("unexpected bounded decode ranges")
    instructions = [i for r in ranges for i in r["instructions"]]
    starts = {int(i["address"], 0) for i in instructions}
    for r in ranges:
        if r["architecture"] != "thumb2" or "decode_stopped_at" in r:
            raise ValueError("incomplete or non-Thumb decode")
        cursor = int(r["start"], 0)
        for i in r["instructions"]:
            if int(i["address"], 0) != cursor:
                raise ValueError("decode gap or overlap")
            cursor += i["length"]
        if cursor != int(r["end"], 0):
            raise ValueError("bounded decode did not reach end")
    ida_code = [x for x in ida["items"] if x["kind"] == "ida_code"]
    ida_starts = {int(x["start"], 0) for x in ida_code}
    folded = sorted(a for a in starts if a not in ida_starts)
    if folded != list(EXPECTED_FOLDED):
        raise ValueError(f"unexpected IDA pseudo-instruction boundaries: {folded}")
    for a in folded:
        if not any(int(x["start"], 0) < a < int(x["end"], 0) for x in ida_code):
            raise ValueError("IDA folded start is not inside a code item")
    if raw[0x5612-0x4000:0x5614-0x4000] != b"\xc0\x46":
        raise ValueError("return alignment NOP differs")
    refs = {}
    calls = Counter()
    branches = []
    for i in instructions:
        at, text = int(i["address"], 0), i["text"].strip()
        m = re.fullmatch(r"ldr\s+r\d+, \[pc, #0x([0-9a-f]+)\]", text)
        if m:
            target = ((at+4) & ~3) + int(m.group(1), 16)
            refs.setdefault(target, []).append(at)
        m = re.fullmatch(r"(b[a-z]*)\s+#(0x[0-9a-f]+)", text)
        if m:
            op, target = m.group(1), int(m.group(2), 0)
            if op == "bl":
                calls[target] += 1
            else:
                if target not in starts or not any(a <= target < b for a, b in CODE):
                    raise ValueError(f"branch leaves known code or targets a nonstart at {at:#x}")
                branches.append((at, target, op))
    expected_literals = {a for lo, hi in POOLS for a in range(lo, hi, 4)}
    if set(refs) != expected_literals:
        raise ValueError("PC-relative loads do not account for every pool word")
    if sum(calls.values()) != 43 or len(calls) != 26 or len(branches) != 56:
        raise ValueError("direct-control edge inventory changed")
    return {
        "format": "quadzilla-main-control-structure-v1", "raw_sha256": SHA,
        "limitation": "Instruction and literal/branch target reconciliation only; path reachability, complete dataflow and hardware effects remain open",
        "code_ranges": [{"start": hex(a), "end": hex(b), "bytes": b-a} for a, b in CODE],
        "return_alignment_nop": "0x5612..0x5614",
        "decoded_instruction_starts": len(instructions),
        "ida_folded_second_starts": [hex(a) for a in folded],
        "literal_pools": [{"start": hex(lo), "end": hex(hi),
                           "words": [{"address": hex(a), "value": hex(struct.unpack_from('<I', raw, a-0x4000)[0]),
                                      "load_sites": [hex(x) for x in refs[a]]}
                                     for a in range(lo, hi, 4)]}
                          for lo, hi in POOLS],
        "pc_relative_loads": sum(len(v) for v in refs.values()),
        "internal_direct_branches": [{"site": hex(a), "target": hex(b), "opcode": op}
                                     for a, b, op in branches],
        "direct_calls": [{"target": hex(a), "sites": n} for a, n in sorted(calls.items())],
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("image", type=Path)
    parser.add_argument("--decode", type=Path, default=Path("audit/data/main_control_binaryninja.json"))
    parser.add_argument("--ida", type=Path, default=Path("audit/data/ida_image_items.json"))
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = audit(args.image.read_bytes(), json.loads(args.decode.read_text(encoding="utf-8")),
                   json.loads(args.ida.read_text(encoding="utf-8")))
    args.output.write_text(json.dumps(result, indent=2)+"\n", encoding="utf-8")
    print(f"{result['decoded_instruction_starts']} decoded starts; "
          f"{sum(len(p['words']) for p in result['literal_pools'])} referenced literal words")


if __name__ == "__main__":
    main()
