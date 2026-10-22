#!/usr/bin/env python3
"""Check catalog entries in an explicitly mapped raw image using Binary Ninja.

Entry starts are seeded from the existing catalog; this is an instruction check,
not an independent discovery count. Binary Ninja's ARMv7/Thumb2 decoders are used
for this ARMv4T image, so results require ARM7 instruction-level review.
"""
import argparse
import hashlib
import json
from pathlib import Path


def main():
    import binaryninja as bn

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("image", type=Path)
    parser.add_argument("--catalog", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--entries", help="comma-separated known Thumb entry addresses")
    args = parser.parse_args()
    data = args.image.read_bytes()
    catalog = json.loads(args.catalog.read_text(encoding="utf-8"))
    digest = hashlib.sha256(data).hexdigest()
    if digest != catalog["raw_sha256"] or len(data) != 32000:
        raise ValueError("image does not match catalog")
    raw = bn.BinaryView.new(data)
    view = bn.BinaryViewType["Mapped"].create(raw)
    view.remove_auto_segment(0)
    flags = bn.SegmentFlag.SegmentReadable | bn.SegmentFlag.SegmentExecutable
    view.add_auto_segment(0x4000, len(data), 0, len(data), flags)
    view.platform = bn.Architecture["armv7"].standalone_platform
    # Exact address mapping is checked before trusting decoded instructions.
    assert view.read(0x4000, len(data)) == data
    entries = []
    critical = {0x4818, 0x499C, 0x4A94, 0x4B38, 0x4D38, 0x50F0, 0x59E8,
                0x601C, 0x6FA0, 0x7BF8, 0x7C1C, 0x7C68, 0x7CC4, 0x7D80}
    if args.entries:
        critical = {int(value, 0) for value in args.entries.split(",")}
    if not critical <= {int(row["entry"], 0) for row in catalog["entries"]}:
        raise ValueError("requested entry is absent from the catalog")
    for row in catalog["entries"]:
        start = int(row["entry"], 0)
        # Limit this pass to entries whose Thumb state is checked by IDA traces.
        if start not in critical:
            continue
        view.add_function(start, bn.Architecture["thumb2"].standalone_platform)
    view.update_analysis_and_wait()
    for row in catalog["entries"]:
        start = int(row["entry"], 0)
        if start not in critical:
            continue
        fn = view.get_function_at(start, bn.Architecture["thumb2"].standalone_platform)
        instructions = []
        if fn:
            for tokens, address in fn.instructions:
                instructions.append({"address": hex(address), "text": "".join(str(t) for t in tokens)})
        entries.append({"entry": hex(start), "recognized": fn is not None,
                        "instructions": instructions})
    result = {"format": "quadzilla-binaryninja-seeded-check-v1", "tool_version": bn.core_version(),
              "raw_sha256": digest, "image_base": "0x4000",
              "method": "catalog-seeded Thumb2 decode; not independent entry discovery or ARMv4T validation",
              "entries": entries}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(f"checked {len(entries)} seeded entries; recognized {sum(e['recognized'] for e in entries)}")


if __name__ == "__main__":
    main()
