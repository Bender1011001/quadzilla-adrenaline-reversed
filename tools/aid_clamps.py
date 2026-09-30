#!/usr/bin/env python3
"""List the value clamps the firmware applies to each AID and compare them with the app's limits.

The audited AID ingest dispatcher (``FUN_0000601c`` in ``decompiled_firmware_full.c``) is one large
``switch`` keyed on the AID number. Each case range-checks the value it stores. This script pulls
the clamp literals out of each case and prints them next to the ``minValue``/``maxValue`` of the
vendor profile, which the iQuad app uses for its own limits.

Static analysis only: it reads decompiler output, it does not run anything.

    python tools/aid_clamps.py [decompiled_firmware_full.c] [vehicle_profile.json]

Notes:
* Stacked ``case`` labels share one body, so only the first label of a stack carries literals.
* Literals are in the firmware's raw units. The profile's ``multiplyFactor`` converts to display units.
"""
from __future__ import annotations

import importlib.util
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FUNCTION = "FUN_0000601c"
NUM = r"(0x[0-9a-fA-F]+|\d+)"


def to_int(text: str) -> int:
    return int(text, 16) if text.lower().startswith("0x") else int(text, 10)


def dispatcher_body(source: str) -> list[str]:
    match = re.search(rf"// === {FUNCTION} at .*?(?=\n// === FUN_)", source, re.S)
    if not match:
        raise SystemExit(f"{FUNCTION} not found")
    return match.group(0).split("\n")


def cases(lines: list[str]) -> dict[int, list[str]]:
    """Map AID -> body lines of its ``case`` (up to the next label)."""
    starts = [(int(m.group(1), 0), i) for i, line in enumerate(lines)
              if (m := re.match(r"\s*case\s+(0x[0-9a-fA-F]+|\d+)\s*:", line))]
    bounds = [i for _, i in starts] + [len(lines)]
    return {aid: [l.strip() for l in lines[i + 1:bounds[k + 1]] if l.strip()]
            for k, (aid, i) in enumerate(starts)}


def clamp_literals(body: list[str]) -> tuple[list[int], list[int]]:
    """(values assigned as clamp results, literals compared against)."""
    text = "\n".join(body)
    assigned = [to_int(m.group(1)) for m in re.finditer(r"^[\w\*\(\)\[\] +]*?=\s*" + NUM + r"\s*;", text, re.M)]
    compared = sorted({to_int(m) for m in re.findall(r"(?:<=?|>=?)\s*" + NUM, text)}
                      | {to_int(m) for m in re.findall(NUM + r"\s*(?:<=?|>=?)\s", text)})
    return assigned, compared


def load_profile(path: Path) -> dict:
    spec = importlib.util.spec_from_file_location("diff_profiles", ROOT / "tools" / "diff_profiles.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    with open(path, encoding="utf-8-sig") as fh:
        return module.extract_aids(json.load(fh))


def main() -> None:
    source_path = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "decompiled_firmware_full.c"
    profile_path = Path(sys.argv[2]) if len(sys.argv) > 2 else ROOT / "vehicles" / "vehicle_v2_dodge9802.json"
    by_aid = cases(dispatcher_body(source_path.read_text(encoding="utf-8", errors="replace")))
    profile = load_profile(profile_path)
    print(f"{len(by_aid)} AIDs handled by {FUNCTION}\n")
    print(f"{'AID':>3}  {'name':<32} {'app min..max (x scale)':<26} {'device: assigned | compared'}")
    for aid in sorted(by_aid):
        assigned, compared = clamp_literals(by_aid[aid])
        p = profile.get(aid, {})
        app = f"{p.get('minValue')}..{p.get('maxValue')} (x{p.get('multiplyFactor')})" if p else "(not in profile)"
        print(f"{aid:>3}  {(p.get('name') or '-')[:32]:<32} {app:<26} {assigned[:4]} | {compared[:5]}")


if __name__ == "__main__":
    main()
