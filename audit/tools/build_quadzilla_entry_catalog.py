#!/usr/bin/env python3
"""Build a review catalog for every confirmed Quadzilla execution entry."""
from __future__ import annotations

import argparse
import hashlib
import json
from collections import defaultdict
from pathlib import Path
from typing import Any


FORMAT = "quadzilla-execution-entry-catalog-v1"


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
    raise ValueError(f"invalid address: {value!r}")


def index_functions(document: dict[str, Any]) -> dict[int, dict[str, Any]]:
    return {address(item["start"]): item for item in document.get("functions", [])}


def call_edges(*documents: dict[str, Any]) -> set[tuple[int, int]]:
    edges = set()
    for document in documents:
        for item in document.get("calls", []):
            if item.get("caller") is not None and item.get("callee") is not None:
                edges.add((address(item["caller"]), address(item["callee"])))
    return edges


def memory_region(target: int, image_start: int, image_end: int) -> str:
    if image_start <= target < image_end:
        return "image"
    if 0x00200000 <= target < 0x00300000:
        return "sram"
    if target >= 0xFFF00000:
        return "peripheral"
    return "external_or_literal"


def parse_labels(document: Any) -> dict[int, list[dict[str, Any]]]:
    if not isinstance(document, dict) or document.get("format") != "quadzilla-semantic-labels-v1":
        raise ValueError("unsupported semantic-label document")
    grouped: dict[int, list[dict[str, Any]]] = defaultdict(list)
    for item in document.get("labels", []):
        if not isinstance(item, dict) or not str(item.get("label") or "").strip():
            raise ValueError("semantic label lacks entry or label text")
        grouped[address(item.get("entry"))].append(item)
    return grouped


def build_catalog(
    audit: dict[str, Any],
    ida: dict[str, Any],
    ghidra: dict[str, Any],
    labels_document: dict[str, Any],
) -> dict[str, Any]:
    if audit.get("format") != "quadzilla-cross-disassembler-audit-v1":
        raise ValueError("unsupported cross-disassembler audit")
    hashes = {str(item.get("raw_sha256") or "").lower() for item in (audit, ida, ghidra)}
    if len(hashes) != 1 or "" in hashes:
        raise ValueError("input image hashes do not match")
    labels_hash = str(labels_document.get("raw_sha256") or "").lower()
    if labels_hash != next(iter(hashes)):
        raise ValueError("semantic-label image hash does not match disassembler maps")
    adjudication = audit.get("adjudication")
    if not isinstance(adjudication, dict) or adjudication.get("unresolved") != 0:
        raise ValueError("audit adjudication is absent or unresolved")

    confirmed = {address(value) for value in adjudication.get("confirmed_starts", [])}
    ida_functions, ghidra_functions = index_functions(ida), index_functions(ghidra)
    labels = parse_labels(labels_document)
    unknown_labels = sorted(set(labels) - confirmed)
    if unknown_labels:
        raise ValueError(f"semantic labels target unconfirmed entries: {[hex(value) for value in unknown_labels]}")

    adjudication_rows = {
        address(item["start"]): item
        for item in adjudication.get("entries", [])
        if address(item["start"]) in confirmed
    }
    edges = call_edges(ida, ghidra)
    outgoing: dict[int, set[int]] = defaultdict(set)
    incoming: dict[int, set[int]] = defaultdict(set)
    for caller, callee in edges:
        outgoing[caller].add(callee)
        incoming[callee].add(caller)

    image_start, image_end = [address(value) for value in ida["image_range"]]
    refs_by_function: dict[int, list[dict[str, Any]]] = defaultdict(list)
    for reference in ida.get("data_references", []):
        if reference.get("function") is None or reference.get("target") is None:
            continue
        owner = address(reference["function"])
        target = address(reference["target"])
        refs_by_function[owner].append(
            {
                "site": reference.get("site"),
                "target": f"0x{target:x}",
                "region": memory_region(target, image_start, image_end),
            }
        )

    entries = []
    for start in sorted(confirmed):
        ida_fn, ghidra_fn = ida_functions.get(start), ghidra_functions.get(start)
        refs = sorted(
            refs_by_function.get(start, []),
            key=lambda item: (address(item["site"]), address(item["target"])),
        )
        regions: dict[str, int] = defaultdict(int)
        for item in refs:
            regions[item["region"]] += 1
        semantics = labels.get(start, [])
        entries.append(
            {
                "entry": f"0x{start:x}",
                "adjudication": adjudication_rows.get(start, {}).get("status"),
                "tool_models": {
                    "ida": (
                        {
                            "name": ida_fn.get("name"),
                            "end": ida_fn.get("end"),
                            "size": ida_fn.get("size"),
                            "chunks": ida_fn.get("chunks", []),
                        }
                        if ida_fn
                        else None
                    ),
                    "ghidra": (
                        {
                            "name": ghidra_fn.get("name"),
                            "end": ghidra_fn.get("end"),
                            "size": ghidra_fn.get("size"),
                            "chunks": ghidra_fn.get("chunks", []),
                        }
                        if ghidra_fn
                        else None
                    ),
                },
                "semantics": semantics,
                "semantic_status": "documented_static_role" if semantics else "unlabeled_static_entry",
                "calls": {
                    "outgoing": [f"0x{value:x}" for value in sorted(outgoing.get(start, set()))],
                    "incoming": [f"0x{value:x}" for value in sorted(incoming.get(start, set()))],
                },
                "ida_data_references": refs,
                "reference_region_counts": dict(sorted(regions.items())),
            }
        )

    labeled = sum(item["semantic_status"] == "documented_static_role" for item in entries)
    entries_with_sram = sum(bool(item["reference_region_counts"].get("sram")) for item in entries)
    entries_with_peripherals = sum(bool(item["reference_region_counts"].get("peripheral")) for item in entries)
    return {
        "format": FORMAT,
        "raw_sha256": next(iter(hashes)),
        "unit": adjudication.get("unit"),
        "summary": {
            "confirmed_entries": len(entries),
            "documented_static_roles": labeled,
            "unlabeled_static_entries": len(entries) - labeled,
            "entries_with_ida_sram_references": entries_with_sram,
            "entries_with_ida_peripheral_references": entries_with_peripherals,
            "union_direct_call_edges": len(edges),
        },
        "entries": entries,
        "interpretation": (
            "Documented roles are evidence-backed static labels. Unlabeled entries are an explicit review queue; "
            "they are not claimed to be functionally unknown to the original firmware."
        ),
    }


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description=__doc__)
    result.add_argument("--audit", type=Path, required=True)
    result.add_argument("--ida", type=Path, required=True)
    result.add_argument("--ghidra", type=Path, required=True)
    result.add_argument("--labels", type=Path, required=True)
    result.add_argument("--output", type=Path, required=True)
    return result


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    inputs = {name: path for name, path in vars(args).items() if name != "output"}
    catalog = build_catalog(
        load_json(args.audit),
        load_json(args.ida),
        load_json(args.ghidra),
        load_json(args.labels),
    )
    catalog["inputs"] = {
        name: {"path": str(path.resolve()), "sha256": sha256_file(path)}
        for name, path in inputs.items()
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(catalog, indent=2) + "\n", encoding="utf-8")
    summary = catalog["summary"]
    print(
        f"wrote {args.output}: entries={summary['confirmed_entries']} "
        f"labeled={summary['documented_static_roles']} "
        f"unlabeled={summary['unlabeled_static_entries']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
