# -*- coding: utf-8 -*-
#@title Map switch AIDs and candidate dispatchers
#@category Analysis

import re
from ghidra.app.decompiler import DecompInterface, DecompileOptions
from ghidra.util.task import ConsoleTaskMonitor

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

def extract_switch_expression(code):
    # Return first switch(...) expression text for context
    for line in code.splitlines():
        lt = line.strip()
        if lt.startswith("switch"):
            m = re.search(r"switch\s*\((.*)\)", lt)
            if m:
                return m.group(1)
    return None

def extract_case_labels(code):
    # Find all case labels, normalize to integers, return as sorted unique list
    cases = []
    # Match 'case X:' allowing multiple on a line; avoid 'default:'
    for m in re.finditer(r"\bcase\s+([^:]+)\s*:", code):
        raw = m.group(1).strip()
        if raw.lower() == "default":
            continue
        # Sometimes multiple case labels collapse like 'case 1:' followed by 'case 2:' on same line,
        # regex will catch each occurrence.
        # Normalize constants like 0xNN, decimal, with optional suffixes (u, U, l, L)
        tok = raw.split()[0].rstrip("uUlL")
        try:
            if tok.lower().startswith("0x"):
                val = int(tok, 16)
            else:
                # handle char literals like '\'A\''
                if tok.startswith("'") and tok.endswith("'") and len(tok) >= 3:
                    ch = tok[1:-1]
                    val = ord(ch[0])
                else:
                    val = int(tok, 10)
            cases.append(val)
        except Exception:
            # ignore unparsed tokens
            pass
    # Unique, sorted
    uniq = sorted(set(cases))
    return ["0x%02X" % v if v <= 0xFF else "0x%X" % v for v in uniq]

def main():
    fm = currentProgram.getFunctionManager()
    functions = fm.getFunctions(True)
    di = init_decompiler(currentProgram)
    if di is None:
        exit(1)

    print("Scanning for switch statements across functions...")
    print("=" * 80)
    results = []

    mon = ConsoleTaskMonitor()

    # Iterate all functions and decompile
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

            # Extract metadata
            switch_expr = extract_switch_expression(ccode)
            labels = extract_case_labels(ccode)
            case_count = len(labels)
            if case_count == 0:
                continue

            ref_count = count_references_to(func)
            results.append({
                "name": func.getName(),
                "addr": str(func.getEntryPoint()),
                "cases": labels,
                "case_count": case_count,
                "switch_expr": switch_expr,
                "refs": ref_count
            })
        except Exception as e:
            # Continue on decompilation errors
            pass

    # Rank by case_count desc, then refs desc
    results.sort(key=lambda r: (r["case_count"], r["refs"]), reverse=True)

    if not results:
        print("No switch statements found.")
        return

    # Print top candidates
    print("Top candidate dispatcher functions (by number of case labels, then references):")
    for idx, r in enumerate(results[:20], 1):
        print("Candidate #%d: %s at %s | cases=%d | refs=%d" %
              (idx, r["name"], r["addr"], r["case_count"], r["refs"]))
        if r["switch_expr"]:
            print("  switch(%s)" % r["switch_expr"])
        # Print case list, wrap at reasonable width
        print("  Case labels (%d):" % r["case_count"])
        line = "    "
        for i, lab in enumerate(r["cases"]):
            nxt = (lab + ("," if i < len(r["cases"]) - 1 else ""))
            if len(line) + 1 + len(nxt) > 100:
                print(line.rstrip())
                line = "    " + nxt + " "
            else:
                line += nxt + " "
        if line.strip():
            print(line.rstrip())
        print("-" * 80)

    # Persist full results to a file in the project workspace for later reporting
    out_path = "aid_switch_candidates.txt"
    try:
        f = open(out_path, "w")
        f.write("AID/Command dispatcher switch candidates\n")
        f.write("=" * 80 + "\n")
        for r in results:
            f.write("%s @ %s | cases=%d | refs=%d\n" %
                    (r["name"], r["addr"], r["case_count"], r["refs"]))
            if r["switch_expr"]:
                f.write("  switch(%s)\n" % r["switch_expr"])
            f.write("  " + ", ".join(r["cases"]) + "\n")
            f.write("-" * 80 + "\n")
        f.close()
        print("Wrote detailed results to %s" % out_path)
    except Exception as e:
        print("WARN: Failed to write output file: %s" % str(e))

if __name__ == "__main__":
    main()