#!/usr/bin/env python3
"""Compare independent IDA and Ghidra maps for the Quadzilla ARM7 image."""
from __future__ import annotations

import argparse
import hashlib
import json
import struct
from pathlib import Path
from typing import Any


FORMAT = "quadzilla-cross-disassembler-audit-v1"
DEFAULT_CRITICAL = (
    0x4818,
    0x499C,
    0x4A94,
    0x4B38,
    0x4D38,
    0x50F0,
    0x59E8,
    0x601C,
    0x6FA0,
    0x7BF8,
    0x7C1C,
    0x7C68,
    0x7D80,
)
KNOWN_DATA_RANGES = ((0xAD18, 0xB114, "aid_pointer_table_2"),)


def read_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ValueError(f"cannot read {path}: {exc}") from exc


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def address(value: Any) -> int:
    if isinstance(value, int):
        return value
    if not isinstance(value, str):
        raise ValueError(f"invalid address {value!r}")
    return int(value, 0)


def validate_map(doc: Any, path: Path) -> None:
    if not isinstance(doc, dict) or doc.get("format") != "quadzilla-disassembler-map-v1":
        raise ValueError(f"unsupported disassembler map: {path}")
    if not isinstance(doc.get("functions"), list) or not isinstance(doc.get("calls"), list):
        raise ValueError(f"map lacks functions/calls: {path}")
    starts: set[int] = set()
    for fn in doc["functions"]:
        if not isinstance(fn, dict):
            raise ValueError(f"invalid function record in {path}")
        start = address(fn.get("start"))
        if start in starts:
            raise ValueError(f"duplicate function start {start:#x} in {path}")
        starts.add(start)


def function_index(doc: dict[str, Any]) -> dict[int, dict[str, Any]]:
    return {address(fn["start"]): fn for fn in doc["functions"]}


def chunks(fn: dict[str, Any]) -> list[tuple[int, int]]:
    raw = fn.get("chunks")
    if isinstance(raw, list) and raw:
        return [(address(item[0]), address(item[1])) for item in raw]
    return [(address(fn["start"]), address(fn["end"]))]


def containing_function(start: int, functions: dict[int, dict[str, Any]]) -> int | None:
    for other_start, fn in functions.items():
        if any(lo <= start < hi for lo, hi in chunks(fn)):
            return other_start
    return None


def only_records(
    only: set[int], own: dict[int, dict[str, Any]], other: dict[int, dict[str, Any]]
) -> list[dict[str, Any]]:
    result = []
    for start in sorted(only):
        contained = containing_function(start, other)
        result.append(
            {
                "start": f"0x{start:x}",
                "name": str(own[start].get("name") or ""),
                "end": f"0x{address(own[start]['end']):x}",
                "size": int(own[start].get("size") or 0),
                "inside_other_function": f"0x{contained:x}" if contained is not None else None,
                "boundary_interpretation": "split_or_chunk_disagreement" if contained is not None else "unique_candidate",
            }
        )
    return result


def call_edges(doc: dict[str, Any]) -> set[tuple[int, int]]:
    result = set()
    for call in doc["calls"]:
        if isinstance(call, dict) and call.get("caller") is not None and call.get("callee") is not None:
            result.add((address(call["caller"]), address(call["callee"])))
    return result


def legacy_starts(doc: Any) -> set[int]:
    if not isinstance(doc, dict) or not isinstance(doc.get("functions"), list):
        raise ValueError("legacy analysis has no functions list")
    return {address(item["address"]) for item in doc["functions"] if isinstance(item, dict)}


def reference_evidence(ida: dict[str, Any], raw: bytes, target: int) -> dict[str, Any]:
    transfers = [
        item
        for item in ida.get("control_transfers", [])
        if isinstance(item, dict) and address(item.get("target")) == target
    ]
    data_refs = [
        item
        for item in ida.get("data_references", [])
        if isinstance(item, dict) and address(item.get("target")) in (target, target + 1)
    ]
    base = address(ida.get("image_range", ["0x4000"])[0])
    literal_hits = []
    for value in (target, target + 1):
        pattern = struct.pack("<I", value)
        start = 0
        while len(literal_hits) < 32:
            pos = raw.find(pattern, start)
            if pos < 0:
                break
            literal_hits.append({"at": f"0x{base + pos:x}", "value": f"0x{value:x}"})
            start = pos + 1
    return {
        "control_transfers": transfers,
        "data_references": data_refs,
        "literal_pointer_hits": literal_hits,
    }


def in_known_data_range(start: int) -> str | None:
    for lo, hi, name in KNOWN_DATA_RANGES:
        if lo <= start < hi:
            return name
    return None


def adjudicate_entries(ida: dict[str, Any], ghidra: dict[str, Any], raw: bytes) -> dict[str, Any]:
    ii, gi = function_index(ida), function_index(ghidra)
    iset, gset = set(ii), set(gi)
    ida_chunk_starts = {
        lo
        for fn in ii.values()
        for lo, _ in chunks(fn)
        if lo != address(fn["start"])
    }
    base = address(ida.get("image_range", ["0x4000"])[0])
    rows = []
    for start in sorted(iset | gset):
        tools = [name for name, values in (("IDA", iset), ("Ghidra", gset)) if start in values]
        evidence = reference_evidence(ida, raw, start)
        transfer_mnemonics = {
            str(item.get("mnemonic") or "").upper() for item in evidence["control_transfers"]
        }
        data_region = in_known_data_range(start)
        other_container = None
        status = "unresolved"
        reason = "no independent entry evidence"
        if start in iset and start in gset:
            status = "confirmed_cross_tool"
            reason = "exact function start recognized by IDA and Ghidra"
        elif start in iset:
            if data_region:
                status = "rejected_data_as_function"
                reason = f"entry lies inside known {data_region}"
            elif evidence["data_references"] or evidence["literal_pointer_hits"]:
                status = "confirmed_pointer_referenced"
                reason = "Thumb/ARM entry address is present in a literal pool or IDA data reference"
        else:
            other_container = containing_function(start, ii)
            offset = start - base
            prior = raw[offset - 4 : offset] if offset >= 4 else b""
            if start == base:
                status = "confirmed_reset_vector"
                reason = "raw image entry and external entry point"
            elif start == 0x4044:
                status = "confirmed_reset_target"
                reason = "ARM reset vector at 0x4000 branches here"
            elif other_container is not None and start in ida_chunk_starts and not ({"BL", "BLX", "BX"} & transfer_mnemonics):
                status = "rejected_separate_chunk"
                reason = f"IDA models this as a non-entry chunk of 0x{other_container:x}"
            elif {"BL", "BLX"} & transfer_mnemonics:
                status = "confirmed_direct_call_target"
                reason = "IDA decodes at least one direct call to this exact entry"
            elif "BX" in transfer_mnemonics or evidence["data_references"] or evidence["literal_pointer_hits"]:
                status = "confirmed_indirect_or_alternate_entry"
                reason = "IDA branch-exchange or literal-pointer evidence reaches this exact entry"
            elif prior == bytes.fromhex("7847c046") and (start - 4) in gset:
                status = "confirmed_interworking_body"
                reason = "immediately follows a Thumb BX-PC/NOP mode-switch thunk"
        rows.append(
            {
                "start": f"0x{start:x}",
                "tools": tools,
                "status": status,
                "reason": reason,
                "inside_ida_function": f"0x{other_container:x}" if other_container is not None else None,
                "known_data_region": data_region,
                "evidence": evidence,
            }
        )
    confirmed = [row for row in rows if row["status"].startswith("confirmed_")]
    rejected = [row for row in rows if row["status"].startswith("rejected_")]
    unresolved = [row for row in rows if row["status"] == "unresolved"]
    return {
        "unit": "execution_entries_including_vectors_thunks_and_alternate_entries",
        "confirmed": len(confirmed),
        "rejected_partitions": len(rejected),
        "unresolved": len(unresolved),
        "confirmed_starts": [row["start"] for row in confirmed],
        "rejected": rejected,
        "unresolved_entries": unresolved,
        "entries": rows,
    }


def compare(
    ida: dict[str, Any],
    ghidra: dict[str, Any],
    critical: tuple[int, ...] = DEFAULT_CRITICAL,
    legacy: dict[str, Any] | None = None,
    raw: bytes | None = None,
) -> dict[str, Any]:
    ida_hash = str(ida.get("raw_sha256") or "").lower()
    ghidra_hash = str(ghidra.get("raw_sha256") or "").lower()
    if not ida_hash or not ghidra_hash:
        raise ValueError("both maps must contain raw_sha256")
    if ida_hash != ghidra_hash:
        raise ValueError(f"image hash mismatch: IDA {ida_hash}, Ghidra {ghidra_hash}")

    ii = function_index(ida)
    gi = function_index(ghidra)
    iset, gset = set(ii), set(gi)
    shared = iset & gset
    union = iset | gset
    end_equal = []
    end_different = []
    for start in sorted(shared):
        record = {
            "start": f"0x{start:x}",
            "ida_end": f"0x{address(ii[start]['end']):x}",
            "ghidra_end": f"0x{address(gi[start]['end']):x}",
        }
        if address(ii[start]["end"]) == address(gi[start]["end"]):
            end_equal.append(record)
        else:
            end_different.append(record)

    ida_calls, ghidra_calls = call_edges(ida), call_edges(ghidra)
    shared_calls = ida_calls & ghidra_calls
    call_union = ida_calls | ghidra_calls
    critical_rows = []
    for start in critical:
        critical_rows.append(
            {
                "start": f"0x{start:x}",
                "ida": start in iset,
                "ghidra": start in gset,
                "cross_tool_confirmed": start in shared,
            }
        )

    result = {
        "format": FORMAT,
        "raw_sha256": ida_hash,
        "function_entries": {
            "ida": len(iset),
            "ghidra": len(gset),
            "shared_exact": len(shared),
            "union": len(union),
            "jaccard": round(len(shared) / len(union), 6) if union else 1.0,
            "shared": [f"0x{x:x}" for x in sorted(shared)],
            "ida_only": only_records(iset - gset, ii, gi),
            "ghidra_only": only_records(gset - iset, gi, ii),
        },
        "shared_function_boundaries": {
            "same_end": len(end_equal),
            "different_end": len(end_different),
            "different": end_different,
        },
        "direct_call_edges": {
            "ida": len(ida_calls),
            "ghidra": len(ghidra_calls),
            "shared": len(shared_calls),
            "union": len(call_union),
            "jaccard": round(len(shared_calls) / len(call_union), 6) if call_union else 1.0,
            "ida_only": [
                {"caller": f"0x{a:x}", "callee": f"0x{b:x}"}
                for a, b in sorted(ida_calls - ghidra_calls)
            ],
            "ghidra_only": [
                {"caller": f"0x{a:x}", "callee": f"0x{b:x}"}
                for a, b in sorted(ghidra_calls - ida_calls)
            ],
        },
        "critical_functions": critical_rows,
        "critical_all_cross_tool_confirmed": all(row["cross_tool_confirmed"] for row in critical_rows),
        "interpretation": (
            "Shared starts are independently recognized function entries. Tool-only starts and "
            "boundary/call disagreements remain candidates requiring instruction-level review."
        ),
    }
    if legacy is not None:
        old = legacy_starts(legacy)
        result["legacy_ida_inventory"] = {
            "entries": len(old),
            "all_in_current_ida": old <= iset,
            "missing_from_current_ida": [f"0x{x:x}" for x in sorted(old - iset)],
            "cross_tool_confirmed": len(old & shared),
            "not_cross_tool_confirmed": [f"0x{x:x}" for x in sorted(old - shared)],
        }
    if raw is not None:
        raw_hash = hashlib.sha256(raw).hexdigest()
        if raw_hash != ida_hash:
            raise ValueError(f"raw image hash mismatch: map {ida_hash}, file {raw_hash}")
        result["adjudication"] = adjudicate_entries(ida, ghidra, raw)
    return result


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ida", type=Path, required=True)
    parser.add_argument("--ghidra", type=Path, required=True)
    parser.add_argument("--legacy", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    ida = read_json(args.ida)
    ghidra = read_json(args.ghidra)
    validate_map(ida, args.ida)
    validate_map(ghidra, args.ghidra)
    legacy = read_json(args.legacy) if args.legacy else None
    raw_path_value = ida.get("raw_image")
    if not raw_path_value:
        raise ValueError("IDA map lacks raw_image path")
    raw_path = Path(str(raw_path_value))
    raw = raw_path.read_bytes()
    result = compare(ida, ghidra, legacy=legacy, raw=raw)
    result["inputs"] = {
        "ida": {"path": str(args.ida.resolve()), "sha256": file_sha256(args.ida)},
        "ghidra": {"path": str(args.ghidra.resolve()), "sha256": file_sha256(args.ghidra)},
        "legacy": (
            {"path": str(args.legacy.resolve()), "sha256": file_sha256(args.legacy)}
            if args.legacy
            else None
        ),
        "raw_image": {"path": str(raw_path.resolve()), "sha256": file_sha256(raw_path)},
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    entries = result["function_entries"]
    calls = result["direct_call_edges"]
    print(
        f"wrote {args.output}: functions IDA={entries['ida']} Ghidra={entries['ghidra']} "
        f"shared={entries['shared_exact']}; calls shared={calls['shared']}; "
        f"critical={result['critical_all_cross_tool_confirmed']}; "
        f"confirmed_entries={result['adjudication']['confirmed']} "
        f"unresolved={result['adjudication']['unresolved']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
