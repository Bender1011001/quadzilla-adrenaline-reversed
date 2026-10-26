#!/usr/bin/env python3
"""Bind four contiguous ADC lookup tables to exact image bytes and readers."""
import argparse
import hashlib
import json
import struct
from pathlib import Path


SHA = "1ae519ba6194e8f7bdaaa94333a83a9e6fda3b0563f87f7d48383b37288c1780"
BASE = 0x4000
TABLES = (
    ("channel6_byte_lut", 0xA030, 0xA0B0, "B", 0x73C0, 0x73C2),
    ("channel7_signed_halfword_lut", 0xA0B0, 0xA320, "h", 0x7374, 0x7376),
    ("channel5_two_64_byte_pages", 0xA320, 0xA3A0, "b", 0x7388, 0x738C),
    ("channel4_signed_halfword_lut", 0xA3A0, 0xA91C, "h", 0x73A2, 0x73A4),
)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("image", type=Path)
    parser.add_argument("--ida", type=Path, default=Path("audit/data/ida_image_items.json"))
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    raw = args.image.read_bytes()
    if len(raw) != 32000 or hashlib.sha256(raw).hexdigest() != SHA:
        raise ValueError("unexpected firmware image")
    ida = json.loads(args.ida.read_text(encoding="utf-8"))
    if ida["raw_sha256"] != SHA or not ida["database_bytes_match"]:
        raise ValueError("IDA export does not match image")
    items = {int(item["start"], 0): item for item in ida["items"]}
    rows = []
    for name, start, end, fmt, literal_site, read_site in TABLES:
        data = raw[start - BASE:end - BASE]
        width = struct.calcsize("<" + fmt)
        values = [item[0] for item in struct.iter_unpack("<" + fmt, data)]
        literal_refs = {int(value, 0) for value in items[literal_site].get("data_refs", [])}
        if not literal_refs or not any(BASE <= address <= BASE + len(raw) - 4 and
                                       struct.unpack_from("<I", raw, address - BASE)[0] == start
                                       for address in literal_refs):
            raise ValueError(f"{name}: missing reader literal reference")
        if not items[read_site]["mnemonic"].startswith("LDR"):
            raise ValueError(f"{name}: unexpected indexed read")
        rows.append({"name": name, "start": hex(start), "end": hex(end),
                     "bytes": len(data), "element_width": width,
                     "element_count": len(values), "signed": fmt.islower(),
                     "min": min(values), "max": max(values),
                     "first_values": values[:8], "last_values": values[-8:],
                     "sha256": hashlib.sha256(data).hexdigest(),
                     "reader_literal_site": hex(literal_site),
                     "reader_load_site": hex(read_site)})
    if sum(row["bytes"] for row in rows) != 0xA91C - 0xA030:
        raise ValueError("table extent mismatch")
    result = {"format": "quadzilla-adc-table-layout-v1", "raw_sha256": SHA,
              "region": ["0xa030", "0xa91c"], "tables": rows,
              "limits": ["table extents follow the bounded indexes in the original helpers under a 10-bit ADC result",
                         "physical signals, units, calibration intent, and actual analog voltages remain unverified",
                         "IDA instruction items inside this region are conflicting candidate interpretations"]}
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print([(row["name"], row["element_count"], row["min"], row["max"]) for row in rows])


if __name__ == "__main__":
    main()
