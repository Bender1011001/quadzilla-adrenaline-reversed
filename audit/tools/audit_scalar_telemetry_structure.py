#!/usr/bin/env python3
"""Reconcile the 0x4D38 scalar helper's Thumb body and literal island."""
import argparse
import hashlib
import json
import re
import struct
from pathlib import Path

SHA = "1ae519ba6194e8f7bdaaa94333a83a9e6fda3b0563f87f7d48383b37288c1780"
CODE = (0x4D38, 0x5016)
NOP = (0x5016, 0x5018)
POOL = (0x5018, 0x506C)


def audit(raw, decode, ida):
    if any(h != SHA for h in (hashlib.sha256(raw).hexdigest(), decode["raw_sha256"], ida["raw_sha256"])):
        raise ValueError("source identity mismatch")
    ranges = decode["ranges"]
    if len(ranges) != 1 or (ranges[0]["start"], ranges[0]["end"], ranges[0]["architecture"]) != ("0x4d38", "0x5018", "thumb2"):
        raise ValueError("unexpected bounded decode range or ISA")
    row = ranges[0]
    if "decode_stopped_at" in row:
        raise ValueError("incomplete bounded decode")
    starts = set()
    cursor = CODE[0]
    for ins in row["instructions"]:
        at = int(ins["address"], 0)
        if at != cursor or ins["length"] not in (2, 4):
            raise ValueError("instruction gap, overlap, or invalid Thumb width")
        starts.add(at)
        cursor += ins["length"]
    if cursor != NOP[1] or row["instructions"][-1]["text"].strip() != "mov     r8, r8":
        raise ValueError("epilogue/alignment changed")
    if raw[NOP[0]-0x4000:NOP[1]-0x4000] != b"\xc0\x46":
        raise ValueError("NOP bytes changed")

    ida_code = [x for x in ida["items"] if x["kind"] == "ida_code" and CODE[0] <= int(x["start"], 0) < NOP[1]]
    ida_starts = {int(x["start"], 0) for x in ida_code}
    folded = sorted(starts - ida_starts)
    if len(folded) != 10 or any(not any(int(x["start"], 0) < a < int(x["end"], 0) for x in ida_code) for a in folded):
        raise ValueError("IDA pseudo-instruction boundaries changed")

    refs = {}
    branches = []
    calls = []
    for ins in row["instructions"]:
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
                if target not in starts or not CODE[0] <= target < CODE[1]:
                    raise ValueError(f"branch leaves verified code at {at:#x}")
                branches.append((at, target, op))
    if set(refs) != set(range(*POOL, 4)) or sum(map(len, refs.values())) != 30:
        raise ValueError("literal island is not fully referenced")
    if len(branches) != 51 or len(calls) != 18 or set(t for _, t in calls) != {0x8574, 0x8584}:
        raise ValueError("direct flow inventory changed")
    return {
        "format": "quadzilla-scalar-telemetry-structure-v1", "raw_sha256": SHA,
        "limitation": "Bounded instruction, literal and direct-flow reconciliation; no universal path-reachability or physical-unit claim",
        "code_range": [hex(x) for x in CODE], "alignment_nop": [hex(x) for x in NOP],
        "decoded_instruction_starts_including_nop": len(starts),
        "ida_folded_second_starts": [hex(x) for x in folded],
        "literal_words": [{"address": hex(a), "value": hex(struct.unpack_from('<I', raw, a-0x4000)[0]),
                           "load_sites": [hex(x) for x in refs[a]]} for a in range(*POOL, 4)],
        "pc_relative_loads": sum(map(len, refs.values())),
        "internal_direct_branches": [{"site": hex(a), "target": hex(b), "opcode": op} for a, b, op in branches],
        "direct_calls": [{"site": hex(a), "target": hex(b)} for a, b in calls],
    }


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("image", type=Path)
    p.add_argument("--decode", type=Path, default=Path("audit/data/scalar_telemetry_binaryninja.json"))
    p.add_argument("--ida", type=Path, default=Path("audit/data/ida_image_items.json"))
    p.add_argument("--output", type=Path, required=True)
    a = p.parse_args()
    result = audit(a.image.read_bytes(), json.loads(a.decode.read_text()), json.loads(a.ida.read_text()))
    a.output.write_text(json.dumps(result, indent=2)+"\n", encoding="utf-8")
    print(f"{result['decoded_instruction_starts_including_nop']} decoded starts; {len(result['literal_words'])} literal words")


if __name__ == "__main__":
    main()
