#!/usr/bin/env python3
"""Annotate Quadzilla peripheral references with SAM7S address blocks."""
from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any


FORMAT = "quadzilla-peripheral-reference-audit-v1"


def load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ValueError(f"cannot read {path}: {exc}") from exc


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def address(value: Any) -> int:
    if isinstance(value, int):
        return value
    if isinstance(value, str):
        return int(value, 0)
    raise ValueError(f"invalid address {value!r}")


def validate_map(document: Any) -> list[dict[str, Any]]:
    if not isinstance(document, dict) or document.get("format") != "sam7s-peripheral-map-v1":
        raise ValueError("unsupported peripheral map")
    ranges = document.get("ranges")
    if not isinstance(ranges, list) or not ranges:
        raise ValueError("peripheral map has no ranges")
    normalized = []
    for item in ranges:
        start, end = address(item.get("start")), address(item.get("end"))
        if end <= start:
            raise ValueError(f"invalid peripheral range {item!r}")
        normalized.append({**item, "start_int": start, "end_int": end})
    for left, right in zip(sorted(normalized, key=lambda item: item["start_int"]), sorted(normalized, key=lambda item: item["start_int"])[1:]):
        if left["end_int"] > right["start_int"]:
            raise ValueError(f"overlapping peripheral ranges: {left['name']} and {right['name']}")
    return normalized


def resolve_block(target: int, ranges: list[dict[str, Any]]) -> dict[str, Any] | None:
    for item in ranges:
        if item["start_int"] <= target < item["end_int"]:
            return item
    return None


def annotate(catalog: dict[str, Any], peripheral_map: dict[str, Any]) -> dict[str, Any]:
    if catalog.get("format") != "quadzilla-execution-entry-catalog-v1":
        raise ValueError("unsupported execution-entry catalog")
    ranges = validate_map(peripheral_map)
    rows = []
    total_refs = 0
    block_counts: Counter[str] = Counter()
    unmapped = []
    for entry in catalog.get("entries", []):
        references = []
        entry_blocks: Counter[str] = Counter()
        for reference in entry.get("ida_data_references", []):
            if reference.get("region") != "peripheral":
                continue
            target = address(reference["target"])
            block = resolve_block(target, ranges)
            total_refs += 1
            if block is None:
                unmapped.append({"entry": entry["entry"], **reference})
                record = {**reference, "block": None, "block_offset": None}
            else:
                name = str(block["name"])
                block_counts[name] += 1
                entry_blocks[name] += 1
                record = {
                    **reference,
                    "block": name,
                    "block_offset": f"0x{target - block['start_int']:x}",
                }
            references.append(record)
        if references:
            rows.append(
                {
                    "entry": entry["entry"],
                    "semantic_status": entry.get("semantic_status"),
                    "semantics": entry.get("semantics", []),
                    "blocks": dict(sorted(entry_blocks.items())),
                    "references": references,
                }
            )
    return {
        "format": FORMAT,
        "raw_sha256": catalog.get("raw_sha256"),
        "map_source": peripheral_map.get("source"),
        "summary": {
            "entries_with_peripheral_references": len(rows),
            "peripheral_references": total_refs,
            "mapped_references": total_refs - len(unmapped),
            "unmapped_references": len(unmapped),
            "block_reference_counts": dict(sorted(block_counts.items())),
        },
        "entries": rows,
        "unmapped": unmapped,
        "interpretation": (
            "A mapped address proves that an instruction references a peripheral register block. "
            "It does not by itself distinguish initialization, status, data transfer or interrupt handling."
        ),
    }


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description=__doc__)
    result.add_argument("--catalog", type=Path, required=True)
    result.add_argument("--peripheral-map", type=Path, required=True)
    result.add_argument("--output", type=Path, required=True)
    return result


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    result = annotate(load_json(args.catalog), load_json(args.peripheral_map))
    result["inputs"] = {
        "catalog": {"path": str(args.catalog.resolve()), "sha256": sha256_file(args.catalog)},
        "peripheral_map": {
            "path": str(args.peripheral_map.resolve()),
            "sha256": sha256_file(args.peripheral_map),
        },
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    summary = result["summary"]
    print(
        f"wrote {args.output}: entries={summary['entries_with_peripheral_references']} "
        f"refs={summary['peripheral_references']} mapped={summary['mapped_references']} "
        f"unmapped={summary['unmapped_references']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
