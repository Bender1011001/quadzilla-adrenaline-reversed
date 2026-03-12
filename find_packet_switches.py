# -*- coding: utf-8 -*-
#@title Find switch statements that dispatch on packet[AID] byte positions
#@category Analysis
#
# Heuristic:
# - Decompile all functions and find switch(...) where the switch expression contains
#   an array index like "[2]" or "[1]" (typical AID/command byte positions).
# - Report candidates ranked by case count and references.

import re
from ghidra.app.decompiler import DecompInterface, DecompileOptions
from ghidra.util.task import ConsoleTaskMonitor

INDEX_PATTERNS = [
    r"\[\s*2\s*\]",   # packet[2]
    r"\[\s*1\s*\]",   # packet[1]
    r"\[\s*3\s*\]",   # packet[3]
]

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
            cases.append(val)
        except Exception:
            pass
    return sorted(set(cases))

def find_switch_expr_lines(code):
    out = []
    for line in code.splitlines():
        lt = line.strip()
        if lt.startswith("switch"):
            out.append(lt)
    return out

def main():
    fm = currentProgram.getFunctionManager()
    functions = fm.getFunctions(True)
    di = init_decompiler(currentProgram)
    if di is None:
        exit(1)
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
            switch_lines = find_switch_expr_lines(ccode)
            if not switch_lines:
                continue
            # Heuristic: look for array index in switch expr line(s)
            hit = False
            for sl in switch_lines:
                for pat in INDEX_PATTERNS:
                    if re.search(pat, sl):
                        hit = True
                        break
                if hit:
                    break
            if not hit:
                continue
            labels = extract_case_labels(ccode)
            if not labels:
                continue
            refc = count_references_to(func)
            candidates.append({
                "name": func.getName(),
                "addr": str(func.getEntryPoint()),
                "refs": refc,
                "cases": ["0x%X" % v if v > 9 else "0x%X" % v for v in labels],
                "case_count": len(labels),
                "switch_lines": switch_lines[:3]
            })
        except Exception:
            pass

    if not candidates:
        print("No packet-style switch handlers detected by heuristic.")
        return

    candidates.sort(key=lambda r: (r["case_count"], r["refs"]), reverse=True)
    print("Packet-like switch handlers ranked by case_count then refs:")
    for c in candidates[:20]:
        print("- %s @ %s | cases=%d | refs=%d" % (c["name"], c["addr"], c["case_count"], c["refs"]))
        for sl in c["switch_lines"]:
            print("    %s" % sl)
        print("    labels: %s" % ", ".join(c["cases"]))

    # Persist full report
    out_path = "packet_switch_candidates.txt"
    try:
        with open(out_path, "w") as f:
            f.write("Packet-like switch handlers (heuristic)\n")
            f.write("=" * 80 + "\n")
            for c in candidates:
                f.write("%s @ %s | cases=%d | refs=%d\n" % (c["name"], c["addr"], c["case_count"], c["refs"]))
                for sl in c["switch_lines"]:
                    f.write("  %s\n" % sl)
                f.write("  labels: %s\n" % ", ".join(c["cases"]))
                f.write("-" * 80 + "\n")
        print("Wrote %s" % out_path)
    except Exception as e:
        print("WARN: Failed to write %s: %s" % (out_path, str(e)))

if __name__ == "__main__":
    main()