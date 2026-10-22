#!/usr/bin/env python3
"""Bounded explicit-ISA Binary Ninja disassembly, including uncataloged entries."""
import argparse
import hashlib
import json
from pathlib import Path


def main():
    import binaryninja as bn
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("image", type=Path)
    parser.add_argument("--ranges", required=True, help="start:end:armv7 or start:end:thumb2, comma separated")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    raw = args.image.read_bytes()
    result = {"format": "quadzilla-bounded-decode-v1", "raw_sha256": hashlib.sha256(raw).hexdigest(),
              "tool_version": bn.core_version(), "limitation": "decoder supports a superset of ARMv4T; explicit mode and bounds are supplied hypotheses", "ranges": []}
    for value in args.ranges.split(","):
        start, end, arch = value.split(":")
        start, end = int(start, 0), int(end, 0)
        if arch not in ("thumb2", "armv7") or not 0x4000 <= start < end <= 0x4000+len(raw):
            raise ValueError("invalid range")
        architecture = bn.Architecture[arch]
        row = {"start": hex(start), "end": hex(end), "architecture": arch, "instructions": []}
        cursor = start
        while cursor < end:
            tokens, length = architecture.get_instruction_text(raw[cursor-0x4000:min(cursor-0x4000+architecture.max_instr_length, end-0x4000)], cursor)
            if not tokens or not length or cursor+length > end:
                row["decode_stopped_at"] = hex(cursor)
                break
            row["instructions"].append({"address": hex(cursor), "length": length, "text": "".join(str(t) for t in tokens)})
            cursor += length
        result["ranges"].append(row)
    args.output.write_text(json.dumps(result, indent=2)+"\n", encoding="utf-8")
    print(f"decoded {len(result['ranges'])} bounded ranges")


if __name__ == "__main__":
    main()
