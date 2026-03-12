# -*- coding: utf-8 -*-
#@title Extract case->callee map from largest switch dispatcher
#@category Analysis

import re
from ghidra.app.decompiler import DecompInterface, DecompileOptions
from ghidra.util.task import ConsoleTaskMonitor

KEYWORDS = set([
    "if","for","while","switch","sizeof","return","do","case","default",
    "break","continue","else","goto","volatile","const","struct","union","enum"
])

def init_decompiler(program):
    opts = DecompileOptions()
    iface = DecompInterface()
    iface.setOptions(opts)
    iface.toggleCCode(True)
    iface.toggleSyntaxTree(True)
    iface.setSimplificationStyle("decompile")
    if not iface.openProgram(program):
        print("ERROR: Failed to open program in decompiler")
        return None
    return iface

def count_references_to(func):
    rm = currentProgram.getReferenceManager()
    it = rm.getReferencesTo(func.getEntryPoint())
    c = 0
    while it.hasNext():
        it.next()
        c += 1
    return c

def extract_case_labels(code):
    cases = []
    for m in re.finditer(r"\bcase\s+([^:]+)\s*:", code):
        raw = m.group(1).strip()
        if raw.lower() == "default":
            continue
        tok = raw.split()[0].rstrip("uUlL")
        try:
            if tok.lower().startswith("0x"):
                val = int(tok, 16)
            elif tok.startswith("'") and tok.endswith("'") and len(tok) >= 3:
                ch = tok[1:-1]
                val = ord(ch[0])
            else:
                val = int(tok, 10)
            cases.append((m.start(), val))
        except Exception:
            pass
    # Return list sorted by occurrence order
    return sorted(cases, key=lambda x: x[0])

def find_switch_span(code):
    # Return (start_index, end_index) of the first switch block using brace matching
    i = code.find("switch")
    if i < 0:
        return None
    # find first '(' after switch and then the opening '{'
    lb = code.find("{", i)
    if lb < 0:
        return None
    depth = 0
    for j in range(lb, len(code)):
        c = code[j]
        if c == "{":
            depth += 1
        elif c == "}":
            depth -= 1
            if depth == 0:
                return (lb, j)
    return None

def split_case_blocks(switch_text):
    # Yield tuples (case_value, case_block_text)
    labeled_positions = extract_case_labels(switch_text)  # list of (pos, val)
    if not labeled_positions:
        return
    # Compute block ranges between successive case labels or end brace
    positions = [pos for pos,_ in labeled_positions]
    values = [val for _,val in labeled_positions]
    ends = positions[1:] + [len(switch_text)]
    for val, start, end in zip(values, positions, ends):
        # move start to after the colon of this case
        colon = switch_text.find(":", start)
        if colon >= 0:
            block = switch_text[colon+1:end]
        else:
            block = switch_text[start:end]
        yield (val, block)

def extract_first_callee_from_block(block_text):
    # Find first function-like identifier call in this case block
    # Exclude keywords and casts; accept FUN_004xxxxx pattern or any identifier
    # Regex: identifier followed by '(' not preceded by type keywords
    for m in re.finditer(r"\b([A-Za-z_][A-Za-z0-9_@]*)\s*\(", block_text):
        name = m.group(1)
        if name in KEYWORDS:
            continue
        # filter out common C casts like 'uint8_t(' etc. Heuristic: names with '_' and hex are likely FUN_...
        if name.lower() in ["uint8_t","uint16_t","uint32_t","int","char","short","long","float","double","size_t","__int64","__int32","__int16","__int8","_BYTE","_WORD","_DWORD"]:
            continue
        return name
    return None

def hexify(v):
    return "0x%02X" % v if v <= 0xFF else "0x%X" % v

def main():
    fm = currentProgram.getFunctionManager()
    functions = fm.getFunctions(True)
    di = init_decompiler(currentProgram)
    if di is None:
        exit(1)

    print("Locating largest switch dispatcher...")
    print("=" * 80)
    mon = ConsoleTaskMonitor()
    candidates = []

    for func in functions:
        try:
            res = di.decompileFunction(func, 60, mon)
            if not res.decompileCompleted():
                continue
            cfunc = res.getDecompiledFunction()
            if cfunc is None:
                continue
            ccode = cfunc.getC()
            if "switch" not in ccode:
                continue
            span = find_switch_span(ccode)
            if not span:
                continue
            s_start, s_end = span
            s_text = ccode[s_start:s_end+1]
            cases = extract_case_labels(s_text)
            if not cases:
                continue
            refc = count_references_to(func)
            candidates.append({
                "func": func,
                "case_count": len(cases),
                "refs": refc,
                "switch_text": s_text,
                "code": ccode
            })
        except Exception:
            pass

    if not candidates:
        print("No switch dispatcher found.")
        return

    candidates.sort(key=lambda r: (r["case_count"], r["refs"]), reverse=True)
    top = candidates[0]
    func = top["func"]
    print("Top dispatcher: %s at %s | cases=%d | refs=%d" %
          (func.getName(), func.getEntryPoint(), top["case_count"], top["refs"]))

    # Extract case blocks and first callees
    dispatch = []
    for val, block in split_case_blocks(top["switch_text"]):
        callee = extract_first_callee_from_block(block)
        dispatch.append((val, callee))

    # Print summary and write to file
    out_path = "aid_dispatch_map.txt"
    print("-" * 80)
    print("AID -> Callee mapping (first call in each case block):")
    for val, callee in dispatch:
        print("  %s -> %s" % (hexify(val), callee if callee else "(no-direct-call-found)"))

    try:
        with open(out_path, "w") as f:
            f.write("Dispatcher: %s @ %s | cases=%d | refs=%d\n" %
                    (func.getName(), func.getEntryPoint(), top["case_count"], top["refs"]))
            f.write("AID -> Callee mapping\n")
            f.write("=" * 80 + "\n")
            for val, callee in dispatch:
                f.write("%s -> %s\n" % (hexify(val), callee if callee else "NONE"))
        print("Wrote %s" % out_path)
    except Exception as e:
        print("WARN: failed to write mapping file: %s" % str(e))

if __name__ == "__main__":
    main()