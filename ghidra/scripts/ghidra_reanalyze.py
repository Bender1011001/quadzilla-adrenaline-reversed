# -*- coding: utf-8 -*-
# Clear all code/data and re-disassemble everything as Thumb
# @category Quadzilla
# @runtime Jython

from ghidra.program.model.listing import CodeUnit
from ghidra.app.decompiler import DecompInterface
from ghidra.util.task import ConsoleTaskMonitor
from ghidra.program.disassemble import Disassembler
from ghidra.program.model.lang import RegisterValue
from ghidra.app.cmd.function import CreateFunctionCmd
from java.math import BigInteger

def clear_and_redisassemble():
    """Clear existing analysis and force Thumb mode on everything."""
    listing = currentProgram.getListing()
    mem = currentProgram.getMemory()
    base = currentProgram.getMinAddress()
    end = currentProgram.getMaxAddress()
    total = end.getOffset() - base.getOffset()
    
    println("=== FIRMWARE LAYOUT ===")
    println("  Range: %s - %s (%d bytes)" % (str(base), str(end), total))
    
    # The interrupt vectors at 0x4000-0x403F are ARM mode (32-bit branch instructions)
    # Everything after that is likely Thumb
    # Skip the first 0x40 bytes (vectors) and the known ARM functions
    
    thumb_start = base.add(0x40)  # After vectors
    
    # Known ARM functions that should NOT be converted to Thumb
    arm_ranges = [
        # These were already correctly identified as ARM
    ]
    
    # Get TMode register
    tmode = currentProgram.getRegister("TMode")
    if tmode is None:
        println("ERROR: TMode register not found")
        return
    
    # First, clear all existing code units in the regions we want to re-analyze
    # We'll clear everything except the interrupt vector area and already-good functions
    println("\n=== CLEARING EXISTING ANALYSIS ===")
    
    # Count what exists now
    inst_count = 0
    data_count = 0
    undef_count = 0
    addr = base
    while addr is not None and addr.compareTo(end) <= 0:
        cu = listing.getCodeUnitAt(addr)
        if cu is None:
            undef_count += 1
            try:
                addr = addr.add(1)
            except:
                break
        else:
            inst = listing.getInstructionAt(addr)
            if inst is not None:
                inst_count += 1
            else:
                data_count += 1
            try:
                addr = addr.add(cu.getLength())
            except:
                break
    
    println("  Before: %d instructions, %d data, %d undefined" % (inst_count, data_count, undef_count))
    
    # Clear everything that's classified as data (not instructions)
    # This preserves good ARM code but clears misclassified data
    println("  Clearing data classifications...")
    addr = thumb_start
    cleared = 0
    while addr is not None and addr.compareTo(end) <= 0:
        cu = listing.getCodeUnitAt(addr)
        if cu is None:
            try:
                addr = addr.add(1)
            except:
                break
            continue
        
        inst = listing.getInstructionAt(addr)
        func = listing.getFunctionContaining(addr)
        
        if inst is None and func is None:
            # This is data, not in a function - clear it
            try:
                length = cu.getLength()
                listing.clearCodeUnits(addr, addr.add(length - 1), False)
                cleared += length
            except:
                pass
            try:
                addr = addr.add(length)
            except:
                break
        else:
            try:
                addr = addr.add(cu.getLength())
            except:
                break
    
    println("  Cleared %d bytes of data" % cleared)
    
    # Now set TMode=1 (Thumb) for the entire range after vectors
    println("\n=== SETTING THUMB MODE ===")
    try:
        tmode_val = RegisterValue(tmode, BigInteger.valueOf(1))
        currentProgram.getProgramContext().setRegisterValue(thumb_start, end, tmode_val)
        println("  Set TMode=1 for %s-%s" % (str(thumb_start), str(end)))
    except Exception as e:
        println("  Error setting TMode: %s" % str(e))
    
    # Disassemble all undefined regions as Thumb
    println("\n=== DISASSEMBLING AS THUMB ===")
    disassembler = Disassembler.getDisassembler(currentProgram, ConsoleTaskMonitor(), None)
    
    new_instructions = 0
    addr = thumb_start
    while addr is not None and addr.compareTo(end) <= 0:
        cu = listing.getCodeUnitAt(addr)
        if cu is None:
            # Try to disassemble here
            result = disassembler.disassemble(addr, currentProgram.getAddressFactory().getAddressSet(addr, end), True)
            if result is not None:
                n = result.getNumAddresses()
                new_instructions += n
                if n > 0:
                    # Skip past what was disassembled
                    try:
                        last = result.getMaxAddress()
                        addr = last.add(1)
                    except:
                        addr = addr.add(2)
                else:
                    try:
                        addr = addr.add(2)
                    except:
                        break
            else:
                try:
                    addr = addr.add(2)
                except:
                    break
        else:
            try:
                addr = addr.add(max(cu.getLength(), 1))
            except:
                break
    
    println("  Disassembled %d new Thumb instructions" % new_instructions)
    
    # Create functions from Thumb prologues
    println("\n=== CREATING FUNCTIONS ===")
    new_funcs = 0
    addr = thumb_start
    while addr is not None and addr.compareTo(end) <= 0:
        cu = listing.getCodeUnitAt(addr)
        if cu is None:
            try:
                addr = addr.add(1)
            except:
                break
            continue
        
        inst = listing.getInstructionAt(addr)
        func = listing.getFunctionContaining(addr)
        
        if inst is not None and func is None:
            mnemonic = inst.getMnemonicString()
            # Common Thumb function prologues
            if mnemonic in ['push', 'stmdb', 'stm', 'str', 'mov']:
                cmd = CreateFunctionCmd(addr)
                if cmd.applyTo(currentProgram):
                    new_funcs += 1
        
        try:
            length = cu.getLength()
            if length > 0:
                addr = addr.add(length)
            else:
                addr = addr.add(1)
        except:
            break
    
    println("  Created %d new functions" % new_funcs)


def export_and_decompile():
    """Export all functions and decompile them."""
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
    
    println("\n=== ALL FUNCTIONS (%d total) ===" % len(funcs))
    println("  %-12s %-40s %6s %6s %6s" % ("Address", "Name", "Size", "Calls", "CalledBy"))
    println("  " + "-" * 110)
    for size, name, entry, called, calling in funcs:
        println("  %-12s %-40s %6d %6d %6d" % (entry, name, size, called, calling))
    
    # Decompile everything >= 16 bytes
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
            if 'param_1 * 4' in c_code or 'param_1 * 2' in c_code:
                tags.append("TABLE")
            if 'while' in c_code or 'for' in c_code:
                tags.append("LOOP")
            if c_code.count('if ') > 5:
                tags.append("COMPLEX")
            
            println("  [%d/%d] %-30s %4d bytes %3d lines [%s]" % (
                i+1, len(to_decompile), name, size, len(lines), ' '.join(tags)))
    
    decomp.dispose()
    
    import os
    out_path = os.path.join("e:\\code.projects\\GitHub-projects\\quadzilla_rev", "decompiled_firmware_full.c")
    f = open(out_path, 'w')
    f.write('\n\n'.join(all_code))
    f.close()
    println("\n  Wrote %d functions to: %s (%d bytes)" % (len(all_code), out_path, len('\n\n'.join(all_code))))


# Main
println("=" * 60)
println("  QUADZILLA FULL RE-ANALYSIS (Clear + Thumb)")
println("=" * 60)

clear_and_redisassemble()
export_and_decompile()

println("\n=== FULL RE-ANALYSIS COMPLETE ===")
