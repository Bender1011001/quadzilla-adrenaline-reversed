# -*- coding: utf-8 -*-
#@title Extract all callees per dispatcher case
#@category Analysis
#
# This script locates the largest switch-based dispatcher (by number of cases),
# then enumerates ALL function calls within each case block and writes the result
# to 'aid_dispatch_map_all_calls.txt' in the current working directory.
#
# It complements extract_dispatch_map.py (which only grabbed the first call).

import re
from ghidra.app.decompiler import DecompInterface, DecompileOptions
from ghidra.util.task import ConsoleTaskMonitor

KEYWORDS = set([
    "if","for","while","switch","sizeof","return","do","case","default",
    "break","continue","else","goto","volatile","const","struct","union","enum"
])

TYPE_CAST_NAMES = set([
    "uint8_t","uint16_t","uint32_t","int","char","short","long","float","double",
    "size_t","__int64","__int32","__int16","__int8","_BYTE","_WORD","_DWORD"
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
    # Return list of (pos, value) for each case label in code segment
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
    return sorted(cases, key=lambda x: x[0])

def find_switch_span(code):
    # Return (start_index, end_index) of first balanced switch {...}
    i = code.find("switch")
    if i < 0:
        return None
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
    # Yield (case_value, case_block_C_text)
    labeled_positions = extract_case_labels(switch_text)
    if not labeled_positions:
        return
    positions = [pos for pos,_ in labeled_positions]
    values = [val for _,val in labeled_positions]
    ends = positions[1:] + [len(switch_text)]
    for val, start, end in zip(values, positions, ends):
        colon = switch_text.find(":", start)
        if colon >= 0:
            block = switch_text[colon+1:end]
        else:
            block = switch_text[start:end]
        yield (val, block)

def hexify(v):
    return "0x%02X" % v if v <= 0xFF else "0x%X" % v

def build_funcname_to_addr_map():
    fm = currentProgram.getFunctionManager()
    it = fm.getFunctions(True)
    m = {}
    for f in it:
        try:
            m[str(f.getName())] = str(f.getEntryPoint())
        except Exception:
            pass
    return m

def extract_all_callees_from_block(block_text, funcname_to_addr):
    callees = []
    # Find occurrences of identifier '(' with simple heuristics
    for m in re.finditer(r"\b([A-Za-z_][A-Za-z0-9_@]*)\s*\(", block_text):
        name = m.group(1)
        lname = name.lower()
        if name in KEYWORDS:
            continue
        if lname in TYPE_CAST_NAMES:
            continue
        # Deduplicate preserving order
        if name not in [c[0] for c in callees]:
            addr = funcname_to_addr.get(name)
            callees.append((name, addr))
    return callees

def main():
    fm = currentProgram.getFunctionManager()
    functions = fm.getFunctions(True)
    di = init_decompiler(currentProgram)
    if di is None:
        exit(1)

    print("Enumerating dispatcher with the largest switch...")
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
                "switch_text": s_text
            })
        except Exception:
            pass

    if not candidates:
        print("No switch-based dispatcher found.")
        return

    candidates.sort(key=lambda r: (r["case_count"], r["refs"]), reverse=True)
    top = candidates[0]
    func = top["func"]

    print("Top dispatcher: %s at %s | cases=%d | refs=%d" %
          (func.getName(), func.getEntryPoint(), top["case_count"], top["refs"]))

    funcname_to_addr = build_funcname_to_addr_map()

    # Build mapping of case -> list of callees
    mapping = []
    for val, block in split_case_blocks(top["switch_text"]):
        callees = extract_all_callees_from_block(block, funcname_to_addr)
        mapping.append((val, callees))

    # Output summary
    print("-" * 80)
    print("AID -> Callee list (all calls observed in case block, order preserved):")
    for val, callees in mapping:
        if not callees:
            print("  %s -> (no calls)" % hexify(val))
        else:
            items = ["%s%s" % (n, ("@" + a) if a else "") for (n,a) in callees]
            print("  %s -> %s" % (hexify(val), ", ".join(items)))

    # Write to file
    out_path = "aid_dispatch_map_all_calls.txt"
    try:
        with open(out_path, "w") as f:
            f.write("Dispatcher: %s @ %s | cases=%d | refs=%d\n" %
                    (func.getName(), func.getEntryPoint(), top["case_count"], top["refs"]))
            f.write("AID -> Callees (all calls found per case block)\n")
            f.write("=" * 80 + "\n")
            for val, callees in mapping:
                if not callees:
                    f.write("%s -> (no calls)\n" % hexify(val))
                else:
                    pairs = ["%s%s" % (n, ("@" + a) if a else "") for (n,a) in callees]
                    f.write("%s -> %s\n" % (hexify(val), ", ".join(pairs)))
        print("Wrote %s" % out_path)
    except Exception as e:
        print("WARN: failed to write mapping file: %s" % str(e))

if __name__ == "__main__":
    main()