#!/usr/bin/env python3
"""Extract direct-call contexts for the eight reviewed control helpers."""
import argparse
import json
from pathlib import Path

from build_integer_callers import extract_calls

ROOT = Path(__file__).resolve().parents[2]
TARGETS = {"0x4384", "0x4650", "0x4674", "0x4698", "0x47b0", "0x48e8", "0x495c", "0x497c"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--items", type=Path, default=ROOT / "audit/data/ida_image_items.json")
    parser.add_argument("--output", type=Path, default=ROOT / "audit/data/control_helper_callers.json")
    args = parser.parse_args()
    doc = json.loads(args.items.read_text(encoding="utf-8"))
    result = {"format": "quadzilla-control-caller-sites-v1", "raw_sha256": doc["raw_sha256"],
              "interpretation": "decoded direct calls only; IDA owner partitions and nearby context are not complete dataflow proof",
              "calls": extract_calls(doc, TARGETS)}
    args.output.write_text(json.dumps(result, indent=2)+"\n", encoding="utf-8")
    print(f"recorded {len(result['calls'])} direct-call contexts")


if __name__ == "__main__":
    main()
