# -*- coding: utf-8 -*-
# Create functions at all known Thumb entry points and decompile
# @category Quadzilla
# @runtime Jython

from ghidra.app.decompiler import DecompInterface
from ghidra.util.task import ConsoleTaskMonitor
from ghidra.app.cmd.function import CreateFunctionCmd
from ghidra.program.model.lang import RegisterValue
from java.math import BigInteger

# All 39 Thumb function entry points found by binary analysis
THUMB_FUNCTIONS = [
    0x4114, 0x4214, 0x4384, 0x46D0, 0x48E8, 0x495C, 0x497C, 0x4A94,
    0x4B38, 0x4D38, 0x506C, 0x50F0, 0x575C, 0x59E8, 0x5CF0, 0x5E04,
    0x5EBC, 0x5F14, 0x601C, 0x6B20, 0x6B64, 0x6B9C, 0x6C94, 0x73E4,
    0x74E8, 0x76CC, 0x77B8, 0x7AF8, 0x7B1C, 0x7BCC, 0x7CC4, 0x7D80,
    0x7E64, 0x7EB4, 0x7EFC, 0x800C, 0x8038, 0x81A8, 0xB18C,
]

# ARM functions (startup/interrupt handlers)
ARM_FUNCTIONS = [
    0x4028, 0x4094, 0x409C, 0x40B4, 0x893C, 0x89B0, 0x8A50,
]

# Additional functions that don't start with PUSH LR
# (found by analyzing call targets and BX destinations)
EXTRA_THUMB = [
    0x4040,  # After vector table
    0x571C,  # FUN_0000571c (known from first analysis)
    0x6B48,  # FUN_00006b48 (CAN ready check)
    0x6B8C,  # FUN_00006b8c
    0x7BF8,  # FUN_00007bf8 (AID segment selector)
    0x7C1C,  # FUN_00007c1c (AID read)
    0x7C68,  # FUN_00007c68 (AID size)
    0x8530,  # FUN_00008530 (memcpy)
    0x854C,  # FUN_0000854c (memset)
    0x8908,  # FUN_00008908
    0x8970,  # FUN_00008970
]

def get_addr(offset):
    return currentProgram.getAddressFactory().getDefaultAddressSpace().getAddress(offset)

def main():
    listing = currentProgram.getListing()
    tmode = currentProgram.getRegister("TMode")
    
    println("=== CREATING FUNCTIONS AT KNOWN ENTRY POINTS ===")
    
    created = 0
    already = 0
    failed = 0
    
    all_thumb = sorted(set(THUMB_FUNCTIONS + EXTRA_THUMB))
    
    for addr_val in all_thumb:
        addr = get_addr(addr_val)
        
        # Ensure Thumb mode is set
        if tmode is not None:
            try:
                tmode_val = RegisterValue(tmode, BigInteger.valueOf(1))
                currentProgram.getProgramContext().setRegisterValue(addr, addr.add(1), tmode_val)
            except:
                pass
        
        # Check if function already exists
        func = listing.getFunctionContaining(addr)
        if func is not None and func.getEntryPoint().equals(addr):
            already += 1
            continue
        
        # Clear any existing code/data at this location
        try:
            cu = listing.getCodeUnitAt(addr)
            if cu is not None:
                listing.clearCodeUnits(addr, addr.add(1), False)
        except:
            pass
        
        # Create function
        cmd = CreateFunctionCmd(addr)
        if cmd.applyTo(currentProgram):
            created += 1
        else:
            failed += 1
            println("  Failed: 0x%08X" % addr_val)
    
    # ARM functions
    for addr_val in ARM_FUNCTIONS:
        addr = get_addr(addr_val)
        func = listing.getFunctionContaining(addr)
        if func is not None and func.getEntryPoint().equals(addr):
            already += 1
            continue
        cmd = CreateFunctionCmd(addr)
        if cmd.applyTo(currentProgram):
            created += 1
        else:
            failed += 1
    
    println("  Created: %d, Already existed: %d, Failed: %d" % (created, already, failed))
    
    # Now list all functions
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
    println("  " + "-" * 80)
    for size, name, entry, called, calling in funcs:
        println("  %-12s %-40s %6d %6d %6d" % (entry, name, size, called, calling))
    
    # Decompile all functions >= 8 bytes
    to_decompile = [(s,n,e,c,cb) for s,n,e,c,cb in funcs if s >= 8]
    println("\n=== DECOMPILING %d FUNCTIONS ===" % len(to_decompile))
    
    decomp = DecompInterface()
    decomp.openProgram(currentProgram)
    
    all_code = []
    for i, (size, name, entry, called, calling) in enumerate(to_decompile):
        try:
            addr_val = int(entry, 16)
            addr = get_addr(addr_val)
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
            println("  [%d/%d] %-30s %5d bytes %4d lines" % (
                i+1, len(to_decompile), name, size, len(lines)))
        else:
            println("  [%d/%d] %-30s FAILED" % (i+1, len(to_decompile), name))
    
    decomp.dispose()
    
    import os
    out_path = os.path.join("e:\\code.projects\\GitHub-projects\\quadzilla_rev", "decompiled_firmware_full.c")
    f = open(out_path, 'w')
    f.write('\n\n'.join(all_code))
    f.close()
    println("\n  Wrote %d functions (%d bytes) to: %s" % (len(all_code), len('\n\n'.join(all_code)), out_path))

main()
println("\n=== COMPLETE ===")
