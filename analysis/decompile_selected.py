# -*- coding: utf-8 -*-
#@title Decompile selected functions and write C output
#@category Analysis
#
# Usage (headless):
#   -postScript decompile_selected.py FUN_004292a0 FUN_0042c706 FUN_00427401
#
# Writes files:
#   decomp_FUN_004292a0.c, etc.

import sys
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

def find_functions_by_names(names):
    fm = currentProgram.getFunctionManager()
    it = fm.getFunctions(True)
    targets = {}
    names_set = set(names)
    for f in it:
        try:
            nm = str(f.getName())
            if nm in names_set:
                targets[nm] = f
                if len(targets) == len(names_set):
                    break
        except Exception:
            pass
    return targets

def get_args():
    try:
        # Prefer Ghidra's API for headless arguments
        arr = getScriptArgs()
        if arr and len(arr) > 0:
            return list(arr)
    except NameError:
        pass
    # Fallback to sys.argv (may be empty in headless)
    if len(sys.argv) > 1:
        return sys.argv[1:]
    return []

def main():
    names = get_args()
    if not names:
        print("No function names provided. Example usage: -postScript decompile_selected.py FUN_004292a0 FUN_0042c706 FUN_00427401")
        return

    print("Requested decompilation for: %s" % ", ".join(names))

    di = init_decompiler(currentProgram)
    if di is None:
        return
    mon = ConsoleTaskMonitor()

    targets = find_functions_by_names(names)
    missing = [n for n in names if n not in targets]
    if missing:
        print("WARN: Not found: %s" % ", ".join(missing))

    for nm, func in targets.items():
        print("Decompiling %s at %s ..." % (nm, func.getEntryPoint()))
        res = di.decompileFunction(func, 120, mon)
        if not res.decompileCompleted() or res.getDecompiledFunction() is None:
            print("ERROR: Decompilation failed for %s" % nm)
            continue
        ccode = res.getDecompiledFunction().getC()

        # Print a short header and first 120 lines to console
        print("----- BEGIN %s (%s) -----" % (nm, func.getEntryPoint()))
        lines = ccode.splitlines()
        for i, line in enumerate(lines[:160]):
            print("%4d: %s" % (i+1, line))
        if len(lines) > 160:
            print("... (%d more lines omitted)" % (len(lines) - 160))
        print("----- END %s -----" % nm)

        # Write full decompilation to file
        out_name = "decomp_%s.c" % nm
        try:
            with open(out_name, "w") as f:
                f.write("// %s @ %s\n\n" % (nm, func.getEntryPoint()))
                f.write(ccode)
            print("Wrote %s" % out_name)
        except Exception as e:
            print("WARN: Failed writing %s: %s" % (out_name, str(e)))

if __name__ == "__main__":
    main()