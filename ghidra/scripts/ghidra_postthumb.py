# -*- coding: utf-8 -*-
# Post-analysis: Export all functions and decompile them
# @category Quadzilla
# @runtime Jython

from ghidra.app.decompiler import DecompInterface
from ghidra.util.task import ConsoleTaskMonitor

def main():
    listing = currentProgram.getListing()
    base = currentProgram.getMinAddress()
    end = currentProgram.getMaxAddress()
    
    # Count instructions vs data
    inst_count = 0
    data_count = 0
    addr = base
    while addr is not None and addr.compareTo(end) <= 0:
        cu = listing.getCodeUnitAt(addr)
        if cu is None:
            try:
                addr = addr.add(1)
            except:
                break
            continue
        inst = listing.getInstructionAt(addr)
        if inst is not None:
            inst_count += 1
        else:
            data_count += 1
        try:
            addr = addr.add(cu.getLength())
        except:
            break
    
    println("=== ANALYSIS STATS ===")
    println("  Instructions: %d" % inst_count)
    println("  Data items: %d" % data_count)
    
    # List all functions
    funcs = []
    func_iter = listing.getFunctions(True)
    while func_iter.hasNext():
        func = func_iter.next()
        size = func.getBody().getNumAddresses()
        name = func.getName()
        entry = str(func.getEntryPoint())
        called = 0
        calling = 0
        try:
            called = len(list(func.getCalledFunctions(ConsoleTaskMonitor())))
            calling = len(list(func.getCallingFunctions(ConsoleTaskMonitor())))
        except:
            pass
        funcs.append((size, name, entry, called, calling))
    
    funcs.sort(key=lambda x: x[0], reverse=True)
    
    println("\n=== ALL FUNCTIONS (%d total) ===" % len(funcs))
    println("  %-12s %-40s %6s %6s %6s" % ("Address", "Name", "Size", "Calls", "CalledBy"))
    println("  " + "-" * 110)
    for size, name, entry, called, calling in funcs:
        println("  %-12s %-40s %6d %6d %6d" % (entry, name, size, called, calling))
    
    # Decompile all functions >= 16 bytes
    to_decompile = [(s,n,e,c,cb) for s,n,e,c,cb in funcs if s >= 16]
    println("\n=== DECOMPILING %d FUNCTIONS ===" % len(to_decompile))
    
    decomp = DecompInterface()
    decomp.openProgram(currentProgram)
    
    all_code = []
    for i, (size, name, entry, called, calling) in enumerate(to_decompile):
        try:
            addr_val = int(entry, 16)
            addr = currentProgram.getAddressFactory().getDefaultAddressSpace().getAddress(addr_val)
            func = getFunctionAt(addr)
        except:
            continue
        
        if func is None:
            continue
        
        result = decomp.decompileFunction(func, 60, ConsoleTaskMonitor())
        if result and result.decompileCompleted():
            c_code = result.getDecompiledFunction().getC()
            header = "// === %s at %s (%d bytes, calls=%d, called_by=%d) ===" % (
                name, entry, size, called, calling)
            all_code.append(header + "\n" + c_code)
            
            lines = c_code.split('\n')
            tags = []
            if 'param_1 * 4' in c_code or 'param_1 * 2' in c_code or '* 4' in c_code:
                tags.append("TABLE")
            if 'while' in c_code or 'for (' in c_code:
                tags.append("LOOP")
            if c_code.count('if ') > 5:
                tags.append("COMPLEX")
            if '>> ' in c_code or '<< ' in c_code:
                tags.append("BITOPS")
            
            println("  [%d/%d] %-35s %5d bytes %4d lines [%s]" % (
                i+1, len(to_decompile), name, size, len(lines), ' '.join(tags)))
    
    decomp.dispose()
    
    import os
    out_path = os.path.join("e:\\code.projects\\GitHub-projects\\quadzilla_rev", "decompiled_firmware_full.c")
    f = open(out_path, 'w')
    f.write('\n\n'.join(all_code))
    f.close()
    println("\n  Wrote %d functions (%d bytes) to: %s" % (len(all_code), len('\n\n'.join(all_code)), out_path))

main()
