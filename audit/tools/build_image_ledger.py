#!/usr/bin/env python3
"""Build an exhaustive byte ledger while preserving unresolved classifications.

IDA item types are candidates. Only explicit source-bound layout facts override
them; a covered byte is not automatically a manually reviewed byte.
"""
import argparse
import hashlib
import json
import struct
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SHA = "1ae519ba6194e8f7bdaaa94333a83a9e6fda3b0563f87f7d48383b37288c1780"
BASE, END = 0x4000, 0xBD00
LAYOUT = (
    (0x608C, 0x6240, "aid_validation_dispatch_table"),
    (0x7CA0, 0x7CC4, "aid_resolver_literal_pool"),
    (0x896C, 0x8970, "soft_float_status_pointer"),
    (0x96C4, 0x96E8, "startup_region_descriptors"),
    (0x96E8, 0x9F88, "initialized_ram_data_source"),
    (0x9FF0, 0xA02F, "spi_request_tx_table"),
    (0xA91C, 0xAD18, "aid_pointer_table_1"),
    (0xAD18, 0xB114, "aid_pointer_table_2"),
    (0xB114, 0xB1B8, "ram_executable_template"),
    (0xB1B8, END, "erased_tail_ff"),
)


def validate_item_coverage(rows, base=BASE, end=END):
    cursor = base
    for row in rows:
        lo, hi = int(row["start"], 0), int(row["end"], 0)
        if lo != cursor or not lo < hi <= end:
            raise ValueError("IDA item coverage has a gap, overlap, or invalid range")
        cursor = hi
    if cursor != end:
        raise ValueError("incomplete image item coverage")


def validate_instruction_reviews(document):
    if document.get("format") != "quadzilla-instruction-range-reviews-v1" or document.get("raw_sha256") != SHA:
        raise ValueError("instruction-review identity mismatch")
    reviewed = []
    for row in document["ranges"]:
        lo, hi = int(row["start"], 0), int(row["end"], 0)
        alignment = {"thumb": 2, "arm": 4}.get(row.get("isa"))
        if not alignment or not BASE <= lo < hi <= END or lo % alignment or hi % alignment:
            raise ValueError("invalid reviewed instruction range or ISA alignment")
        if not row.get("evidence") or not row.get("account"):
            raise ValueError("reviewed range lacks supporting account")
        if any(lo < b and hi > a for a, b, _ in LAYOUT):
            raise ValueError("instruction review overlaps a supported layout region")
        reviewed.append((lo, hi, row["entry"], row["isa"]))
    reviewed.sort()
    if any(a[1] > b[0] for a, b in zip(reviewed, reviewed[1:])):
        raise ValueError("overlapping instruction reviews")
    return reviewed


def build(raw, export, reviews=None):
    digest = hashlib.sha256(raw).hexdigest()
    if digest != SHA or export.get("raw_sha256") != digest or not export.get("database_bytes_match"):
        raise ValueError("source identity mismatch")
    rows = export["items"]
    validate_item_coverage(rows)
    reviewed = validate_instruction_reviews(reviews) if reviews is not None else []
    if raw[0xB1B8-BASE:] != bytes([255]) * (END-0xB1B8):
        raise ValueError("tail is not erased")
    descriptors = []
    for ea in range(0x96C4, 0x96E8, 12):
        length, dest, source = struct.unpack_from("<III", raw, ea-BASE)
        descriptors.append({"at": hex(ea), "length": length, "destination": hex(dest),
                            "source": hex(source), "operation": "zero_fill" if source == dest else "copy"})
    ranges = []
    conflicts = []
    for row in rows:
        lo, hi = int(row["start"], 0), int(row["end"], 0)
        cuts = sorted({lo, hi} | {v for a, b, *_ in (*LAYOUT, *reviewed) for v in (a, b) if lo < v < hi})
        for a, b in zip(cuts, cuts[1:]):
            purpose = next((name for x, y, name in LAYOUT if x <= a and b <= y), None)
            review = next(((entry, isa) for x, y, entry, isa in reviewed if x <= a and b <= y), None)
            classification = purpose or ("reviewed_"+review[1]+"_instructions" if review else row["kind"] + "_pending_review")
            if purpose and row["kind"] == "ida_code" and purpose != "ram_executable_template":
                conflicts.append({"start": hex(a), "end": hex(b), "ida_text": row.get("text"),
                                  "layout": purpose})
            record = {"start": hex(a), "end": hex(b), "classification": classification,
                      "review_state": "layout_role_supported" if purpose else
                                      "instruction_range_supported" if review else "needs_instruction_or_data_review"}
            if review:
                record["review_entry"] = review[0]
            ranges.append(record)
    counts = Counter()
    for row in ranges:
        counts[row["classification"]] += int(row["end"], 0)-int(row["start"], 0)
    return {"format": "quadzilla-image-ledger-v1", "raw_sha256": digest,
            "image_range": [hex(BASE), hex(END)], "covered_bytes": END-BASE,
            "completion": "incomplete; item coverage is not proof of manual classification",
            "startup_descriptors": descriptors, "classification_bytes": dict(counts),
            "ida_layout_conflicts": conflicts, "ranges": ranges}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("image", type=Path)
    parser.add_argument("--items", type=Path, default=ROOT / "audit/data/ida_image_items.json")
    parser.add_argument("--reviews", type=Path, default=ROOT / "audit/data/reviewed_instruction_ranges.json")
    parser.add_argument("--output", type=Path, default=ROOT / "audit/data/image_coverage_ledger.json")
    args = parser.parse_args()
    result = build(args.image.read_bytes(), json.loads(args.items.read_text(encoding="utf-8")),
                   json.loads(args.reviews.read_text(encoding="utf-8")))
    args.output.write_text(json.dumps(result, indent=2)+"\n", encoding="utf-8")
    print(json.dumps({"bytes": result["covered_bytes"], "classifications": result["classification_bytes"],
                      "conflicts": len(result["ida_layout_conflicts"])}))


if __name__ == "__main__":
    main()
