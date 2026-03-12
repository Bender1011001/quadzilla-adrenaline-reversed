# -*- coding: utf-8 -*-
# Decompile libx2com-jni.so — x86_64 with full symbols will decompile cleanly
# @category Quadzilla
# @runtime Jython

from ghidra.app.decompiler import DecompInterface
from ghidra.util.task import ConsoleTaskMonitor

def main():
    listing = currentProgram.getListing()
    
    # List all functions
    funcs = []
    func_iter = listing.getFunctions(True)
    while func_iter.hasNext():
        func = func_iter.next()
        size = func.getBody().getNumAddresses()
        name = func.getName()
        entry = str(func.getEntryPoint())
        if name.startswith("_") and not name.startswith("_Z"):
            continue  # Skip internal libc functions
        funcs.append((size, name, entry))
    
    funcs.sort(key=lambda x: x[0], reverse=True)
    
    println("=== ALL FUNCTIONS (%d total) ===" % len(funcs))
    for size, name, entry in funcs:
        println("  %-12s %-50s %6d" % (entry, name, size))
    
    # Filter for x2com_ and Java_ functions
    interesting = [(s,n,e) for s,n,e in funcs if 'x2com' in n or 'Java_' in n or n in ['getAID', 'setAID']]
    
    println("\n=== X2COM / JNI FUNCTIONS (%d) ===" % len(interesting))
    for size, name, entry in interesting:
        println("  %-12s %-50s %6d" % (entry, name, size))
    
    # Decompile all x2com/JNI functions
    println("\n=== DECOMPILING ===" )
    decomp = DecompInterface()
    decomp.openProgram(currentProgram)
    
    all_code = []
    for size, name, entry in interesting:
        try:
            addr = currentProgram.getAddressFactory().getDefaultAddressSpace().getAddress(int(entry, 16))
            func = getFunctionAt(addr)
        except:
            continue
        
        if func is None:
            continue
        
        result = decomp.decompileFunction(func, 60, ConsoleTaskMonitor())
        if result and result.decompileCompleted():
            c_code = result.getDecompiledFunction().getC()
            header = "// === %s at %s (%d bytes) ===" % (name, entry, size)
            all_code.append(header + "\n" + c_code)
            println("  %-50s %d lines" % (name, len(c_code.split('\n'))))
        else:
            println("  %-50s FAILED" % name)
    
    decomp.dispose()
    
    import os
    out_path = os.path.join("e:\\code.projects\\GitHub-projects\\quadzilla_rev", "decompiled_x2com.c")
    f = open(out_path, 'w')
    f.write('\n\n'.join(all_code))
    f.close()
    println("\n  Wrote %d functions (%d bytes) to: %s" % (len(all_code), len('\n\n'.join(all_code)), out_path))

main()
