#!/usr/bin/env python3
"""Rank unlabeled entries by call-graph proximity for human review, not risk."""
import argparse
import hashlib
import json
from collections import deque
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ANCHORS = ("0x601c", "0x50f0", "0x6fa0", "0x8038", "0x7cc4")


def build(catalog):
    rows = {row["entry"]: row for row in catalog["entries"]}
    neighbors = {ea: set() for ea in rows}
    for ea, row in rows.items():
        for callee in row["calls"]["outgoing"]:
            if callee in rows:
                neighbors[ea].add(callee)
                neighbors[callee].add(ea)
    paths = {ea: [ea] for ea in ANCHORS}
    pending = deque(ANCHORS)
    while pending:
        current = pending.popleft()
        for ea in sorted(neighbors[current], key=lambda x: int(x, 0)):
            if ea not in paths:
                paths[ea] = paths[current] + [ea]
                pending.append(ea)
    queue = [{"entry": ea, "undirected_call_distance": len(paths[ea])-1 if ea in paths else None,
              "anchor_path": paths.get(ea), "reference_regions": row["reference_region_counts"]}
             for ea, row in rows.items() if not row["semantics"]]
    queue.sort(key=lambda row: (row["undirected_call_distance"] if row["undirected_call_distance"] is not None else 999,
                                int(row["entry"], 0)))
    return {"format": "quadzilla-offline-review-queue-v1", "raw_sha256": catalog["raw_sha256"],
            "method": "undirected call proximity; not execution reachability, semantic proof, or severity",
            "anchors": list(ANCHORS), "remaining_entries": len(queue), "queue": queue}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--catalog", type=Path, default=ROOT / "audit/data/execution_entry_catalog.json")
    parser.add_argument("--output", type=Path, default=ROOT / "audit/data/offline_review_queue.json")
    args = parser.parse_args()
    result = build(json.loads(args.catalog.read_text(encoding="utf-8")))
    # Normalize Git's platform-dependent CRLF/LF checkout representation.
    result["catalog_lf_text_sha256"] = hashlib.sha256(args.catalog.read_text(encoding="utf-8").encode("utf-8")).hexdigest()
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(f"ranked {result['remaining_entries']} unlabeled entries")


if __name__ == "__main__":
    main()
