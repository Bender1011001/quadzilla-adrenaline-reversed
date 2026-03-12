# -*- coding: utf-8 -*-
# Force Thumb mode analysis on remaining firmware code
# @category Quadzilla
# @runtime Jython

from ghidra.program.model.listing import CodeUnit
from ghidra.app.decompiler import DecompInterface
from ghidra.util.task import ConsoleTaskMonitor
from ghidra.program.disassemble import Disassembler
from ghidra.program.model.lang import RegisterValue
from java.math import BigInteger

def force_thumb_analysis():
    """Force Thumb mode disassembly on all unanalyzed code regions."""
    listing = currentProgram.getListing()
    mem = currentProgram.getMemory()
    base = currentProgram.getMinAddress()
    end = currentProgram.getMaxAddress()
    
    # Get the TMode register for ARM Thumb switching
    tmode = currentProgram.getRegister("TMode")
    if tmode is None:
        println("ERROR: TMode register not found")
        return
    
    println("=== FORCING THUMB DISASSEMBLY ===")
    
    # Find undefined (unanalyzed) regions
    undefined_ranges = []
    addr = base
    space = currentProgram.getAddressFactory().getDefaultAddressSpace()
    
    in_undefined = False
    range_start = None
    total_undefined = 0
    
    while addr is not None and addr.compareTo(end) <= 0:
        cu = listing.getCodeUnitAt(addr)
        if cu is None:
            # This address has no code unit - it's undefined
            if not in_undefined:
                range_start = addr
                in_undefined = True
            total_undefined += 1
            try:
                addr = addr.add(1)
            except:
                break
        else:
            if in_undefined:
                undefined_ranges.append((range_start, addr))
                in_undefined = False
            try:
                addr = addr.add(cu.getLength())
            except:
                break
    
    if in_undefined:
        undefined_ranges.append((range_start, end))
    
    println("  Found %d undefined regions (%d bytes total)" % (len(undefined_ranges), total_undefined))
    
    # Force Thumb mode on undefined regions and disassemble
    disassembler = Disassembler.getDisassembler(currentProgram, ConsoleTaskMonitor(), None)
    addr_set = currentProgram.getAddressFactory().getAddressSet()
    
    count = 0
    for range_start, range_end in undefined_ranges:
        size = range_end.getOffset() - range_start.getOffset()
        if size < 2:
            continue
        
        # Set TMode=1 (Thumb) for this range
        try:
            tmode_val = RegisterValue(tmode, BigInteger.valueOf(1))
            currentProgram.getProgramContext().setRegisterValue(range_start, range_end.subtract(1), tmode_val)
        except Exception as e:
            println("  Warning: Could not set TMode for %s-%s: %s" % (str(range_start), str(range_end), str(e)))
            continue
        
        # Disassemble
        result = disassembler.disassemble(range_start, currentProgram.getAddressFactory().getAddressSet(range_start, range_end.subtract(1)), True)
        
        if result is not None and result.getNumAddresses() > 0:
            count += result.getNumAddresses()
            if size > 100:
                println("  Disassembled %s-%s (%d bytes, %d instructions)" % (
                    str(range_start), str(range_end), size, result.getNumAddresses()))
    
    println("  Total: %d new instructions disassembled in Thumb mode" % count)
    
    # Now run function analysis on the newly disassembled code
    println("\n=== CREATING FUNCTIONS FROM NEW CODE ===")
    from ghidra.app.cmd.function import CreateFunctionCmd
    
    new_funcs = 0
    addr = base
    while addr is not None and addr.compareTo(end) <= 0:
        cu = listing.getCodeUnitAt(addr)
        if cu is None:
            try:
                addr = addr.add(1)
            except:
                break
            continue
        
        # Check if this is an instruction at a function entry pattern
        func = listing.getFunctionContaining(addr)
        if func is None and listing.getInstructionAt(addr) is not None:
            inst = listing.getInstructionAt(addr)
            mnemonic = inst.getMnemonicString()
            # Common Thumb function prologues
            if mnemonic in ['push', 'stmdb', 'str', 'sub']:
                cmd = CreateFunctionCmd(addr)
                if cmd.applyTo(currentProgram):
                    new_funcs += 1
        
        try:
            if cu.getLength() > 0:
                addr = addr.add(cu.getLength())
            else:
                addr = addr.add(1)
        except:
            break
    
    println("  Created %d new functions" % new_funcs)


def export_all_functions():
    """Export complete function list after Thumb analysis."""
    listing = currentProgram.getListing()
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
    
    println("\n=== ALL FUNCTIONS AFTER THUMB ANALYSIS (%d total) ===" % len(funcs))
    println("  %-12s %-40s %6s %6s %6s" % ("Address", "Name", "Size", "Calls", "CalledBy"))
    println("  " + "-" * 110)
    
    for size, name, entry, called, calling in funcs:
        println("  %-12s %-40s %6d %6d %6d" % (entry, name, size, called, calling))
    
    return funcs


def decompile_all(funcs, min_size=20):
    """Decompile all functions above minimum size."""
    to_decompile = [(s,n,e,c,cb) for s,n,e,c,cb in funcs if s >= min_size]
    
    println("\n=== DECOMPILING %d FUNCTIONS (>=%d bytes) ===" % (len(to_decompile), min_size))
    
    decomp = DecompInterface()
    decomp.openProgram(currentProgram)
    
    all_code = []
    
    for i, (size, name, entry, called, calling) in enumerate(to_decompile):
        println("  [%d/%d] %s at %s (%d bytes, calls=%d, called_by=%d)" % (
            i+1, len(to_decompile), name, entry, size, called, calling))
        
        # Parse the address
        try:
            addr_val = int(entry, 16) if entry.startswith('0') else int(entry)
            addr = currentProgram.getAddressFactory().getDefaultAddressSpace().getAddress(addr_val)
            func = getFunctionAt(addr)
        except:
            println("    (could not parse address)")
            continue
        
        if func is None:
            println("    (no function at address)")
            continue
        
        result = decomp.decompileFunction(func, 60, ConsoleTaskMonitor())
        if result and result.decompileCompleted():
            c_code = result.getDecompiledFunction().getC()
            header = "// === %s at %s (%d bytes, calls=%d, called_by=%d) ===" % (
                name, entry, size, called, calling)
            all_code.append(header + "\n" + c_code)
            
            # Print summary
            lines = c_code.split('\n')
            # Look for interesting patterns
            has_table_lookup = 'param_1 * 4' in c_code or 'param_1 * 2' in c_code
            has_conditional = c_code.count('if ') > 3
            has_loop = 'while' in c_code or 'for' in c_code or 'do {' in c_code
            has_multiply = '*' in c_code and '0x' in c_code
            
            tags = []
            if has_table_lookup:
                tags.append("TABLE_LOOKUP")
            if has_loop:
                tags.append("LOOP")
            if has_multiply:
                tags.append("MATH")
            if has_conditional:
                tags.append("BRANCHY")
            
            println("    %d lines [%s]" % (len(lines), ' '.join(tags)))
            
            # Print first few lines for context
            for line in lines[1:6]:
                println("    %s" % line)
        else:
            err_msg = ""
            if result:
                err_msg = str(result.getErrorMessage()) if result.getErrorMessage() else ""
            println("    (decompilation failed: %s)" % err_msg)
    
    decomp.dispose()
    
    # Write all decompiled code
    import os
    out_path = os.path.join("e:\\code.projects\\GitHub-projects\\quadzilla_rev", "decompiled_firmware_full.c")
    f = open(out_path, 'w')
    f.write('\n\n'.join(all_code))
    f.close()
    println("\n  Wrote %d decompiled functions to: %s" % (len(all_code), out_path))
    
    return all_code


# Main
println("=" * 60)
println("  QUADZILLA THUMB MODE DEEP ANALYSIS")
println("=" * 60)

force_thumb_analysis()
funcs = export_all_functions()
decompile_all(funcs, min_size=16)

println("\n=== DEEP ANALYSIS COMPLETE ===")
