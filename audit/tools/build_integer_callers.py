#!/usr/bin/env python3
"""Extract decoded direct-call context for the six integer division entries."""
import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--items", type=Path, default=ROOT / "audit/data/ida_image_items.json")
    parser.add_argument("--output", type=Path, default=ROOT / "audit/data/integer_division_callers.json")
    args = parser.parse_args()
    doc = json.loads(args.items.read_text(encoding="utf-8"))
    rows = doc["items"]
    calls = []
    for n, row in enumerate(rows):
        if row.get("decoded_direct_target") in {"0x8564", "0x8568", "0x8574", "0x8578", "0x8584", "0x8588"}:
            calls.append({"caller_partition": row["function"], "site": row["start"], "target": row["decoded_direct_target"],
                          "context": [{"address": i["start"], "text": i.get("text", i["kind"])} for i in rows[max(0,n-3):n+5]]})
    result = {"format": "quadzilla-integer-caller-sites-v1", "raw_sha256": doc["raw_sha256"],
              "interpretation": "decoded direct-call sites only; IDA owner partitions and nearby context are not a complete dataflow proof", "calls": calls}
    args.output.write_text(json.dumps(result, indent=2)+"\n", encoding="utf-8")
    print(f"recorded {len(calls)} direct-call contexts")


if __name__ == "__main__":
    main()
