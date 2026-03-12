# -*- coding: utf-8 -*-
# Ghidra headless analysis script for Quadzilla Adrenaline firmware
# Runs in Jython 2.7 inside Ghidra headless analyzer
#
# @category Quadzilla
# @runtime Jython

from ghidra.program.model.listing import CodeUnit
from ghidra.app.decompiler import DecompInterface
from ghidra.util.task import ConsoleTaskMonitor
from ghidra.program.model.mem import MemoryAccessException

import java.lang.Exception as JavaException


def get_addr(offset):
    return currentProgram.getAddressFactory().getDefaultAddressSpace().getAddress(offset)


def analyze_vectors():
    """Parse ARM interrupt vectors at firmware base."""
    mem = currentProgram.getMemory()
    base = currentProgram.getMinAddress()
    names = ['Reset', 'Undef', 'SWI', 'PrefAbort', 'DataAbort', 'Rsvd', 'IRQ', 'FIQ']
    
    println("=== ARM INTERRUPT VECTORS ===")
    for i in range(8):
        addr = base.add(i * 4)
        try:
            val = mem.getInt(addr)
            println("  %s: %s -> 0x%08X" % (names[i], str(addr), val & 0xFFFFFFFF))
        except:
            println("  %s: %s -> (unreadable)" % (names[i], str(addr)))


def find_strings_in_memory():
    """Find ASCII strings embedded in firmware."""
    mem = currentProgram.getMemory()
    base = currentProgram.getMinAddress()
    end = currentProgram.getMaxAddress()
    
    println("\n=== KEY STRINGS IN FIRMWARE ===")
    
    targets = ['DADR', 'Aug', 'Sep', 'Oct', 'CAN', 'SPI', 'UART', 'PWM', 'ADC', 'I2C',
               'ERR', 'BOOT', 'FLASH', 'TIMER', 'ISR', 'FUEL', 'BOOST', 'EGT', 'TPS',
               'RPM', 'IDLE', 'INJ', 'PUMP', 'TIMING']
    
    for target in targets:
        target_bytes = bytearray(target.encode('ascii'))
        addr = mem.findBytes(base, target_bytes, None, True, ConsoleTaskMonitor())
        while addr is not None and addr.compareTo(end) < 0:
            # Read surrounding bytes for context
            try:
                context = []
                for j in range(-4, 20):
                    b = mem.getByte(addr.add(j))
                    if 0x20 <= (b & 0xFF) <= 0x7E:
                        context.append(chr(b & 0xFF))
                    else:
                        context.append('.')
                context_str = ''.join(context)
                println("  '%s' at %s  context: [%s]" % (target, str(addr), context_str))
            except:
                println("  '%s' at %s" % (target, str(addr)))
            
            # Search for next occurrence
            next_addr = addr.add(len(target))
            if next_addr.compareTo(end) >= 0:
                break
            addr = mem.findBytes(next_addr, target_bytes, None, True, ConsoleTaskMonitor())
            if addr is None:
                break


def list_functions():
    """List all auto-detected functions sorted by size."""
    listing = currentProgram.getListing()
    funcs = []
    func_iter = listing.getFunctions(True)
    
    while func_iter.hasNext():
        func = func_iter.next()
        size = func.getBody().getNumAddresses()
        name = func.getName()
        entry = str(func.getEntryPoint())
        
        # Count calls made and received
        called = 0
        calling = 0
        try:
            called = len(list(func.getCalledFunctions(ConsoleTaskMonitor())))
            calling = len(list(func.getCallingFunctions(ConsoleTaskMonitor())))
        except:
            pass
        
        funcs.append((size, name, entry, called, calling))
    
    funcs.sort(key=lambda x: x[0], reverse=True)
    
    println("\n=== ALL FUNCTIONS (by size, %d total) ===" % len(funcs))
    println("  %-12s %-40s %6s %6s %6s" % ("Address", "Name", "Size", "Calls", "CalledBy"))
    println("  " + "-" * 110)
    
    for size, name, entry, called, calling in funcs:
        println("  %-12s %-40s %6d %6d %6d" % (entry, name, size, called, calling))
    
    return funcs


def find_peripheral_refs():
    """Find references to AT91SAM7 peripheral addresses."""
    println("\n=== PERIPHERAL REFERENCES ===")
    
    # AT91SAM7S256 / LPC2xxx peripheral map
    peripherals = [
        (0xFFFD0000, 0xFFFD03FF, "CAN Controller"),
        (0xFFFC0000, 0xFFFC03FF, "USART0"),
        (0xFFFC4000, 0xFFFC43FF, "USART1"),
        (0xFFFFF200, 0xFFFFF3FF, "DBGU (Debug UART)"),
        (0xFFFFF400, 0xFFFFF5FF, "PIO-A"),
        (0xFFFFF600, 0xFFFFF7FF, "PIO-B"),
        (0xFFFFFC00, 0xFFFFFDFF, "PMC (Clocks)"),
        (0xFFFE0000, 0xFFFE00BF, "Timer/Counter"),
        (0xFFFB0000, 0xFFFB01FF, "TWI (I2C)"),
        (0xFFFB8000, 0xFFFB81FF, "ADC"),
        (0xFFFA0000, 0xFFFA01FF, "SPI"),
        (0xFFFFF000, 0xFFFFF1FF, "AIC (Interrupts)"),
        (0xFFFFFF00, 0xFFFFFFFF, "System Controller"),
        # LPC2xxx CAN
        (0xE0044000, 0xE00440FF, "LPC CAN1"),
        (0xE0048000, 0xE00480FF, "LPC CAN2"),
        (0xE003C000, 0xE003C0FF, "LPC CAN Accept Filter"),
        (0xE0040000, 0xE00400FF, "LPC CAN Central"),
    ]
    
    listing = currentProgram.getListing()
    ref_mgr = currentProgram.getReferenceManager()
    
    for start, end, name in peripherals:
        # Search for any references to this address range
        refs_found = []
        func_iter = listing.getFunctions(True)
        while func_iter.hasNext():
            func = func_iter.next()
            inst_iter = listing.getInstructions(func.getBody(), True)
            while inst_iter.hasNext():
                inst = inst_iter.next()
                mnemonic = inst.getMnemonicString()
                inst_str = str(inst)
                # Check if any operand reference falls in peripheral range
                for op_idx in range(inst.getNumOperands()):
                    refs = inst.getOperandReferences(op_idx)
                    for ref in refs:
                        ref_addr = ref.getToAddress().getOffset() & 0xFFFFFFFF
                        if start <= ref_addr <= end:
                            refs_found.append((str(inst.getAddress()), func.getName(), 
                                             "0x%08X" % ref_addr, mnemonic))
        
        if refs_found:
            println("  %s (%d refs):" % (name, len(refs_found)))
            for addr, fn, target, mnem in refs_found[:10]:
                println("    %s  in %-30s -> %s  (%s)" % (addr, fn, target, mnem))
            if len(refs_found) > 10:
                println("    ... and %d more" % (len(refs_found) - 10))


def decompile_top_functions(funcs, count=15):
    """Decompile the largest functions and save to file."""
    println("\n=== DECOMPILING TOP %d FUNCTIONS ===" % count)
    
    decomp = DecompInterface()
    decomp.openProgram(currentProgram)
    
    all_code = []
    
    for i, (size, name, entry, called, calling) in enumerate(funcs[:count]):
        println("  [%d/%d] Decompiling %s (%d bytes)..." % (i+1, count, name, size))
        
        # Parse address
        addr = get_addr(int(entry.replace("0000",""), 16)) if "0000" in entry else get_addr(int(entry, 16))
        try:
            func = getFunctionAt(addr)
            if func is None:
                # Try parsing as hex
                func = getFunctionAt(get_addr(long(entry, 16)))
        except:
            pass
        
        if func is None:
            println("    (could not find function at %s)" % entry)
            continue
        
        result = decomp.decompileFunction(func, 60, ConsoleTaskMonitor())
        if result and result.decompileCompleted():
            c_code = result.getDecompiledFunction().getC()
            all_code.append("// === %s at %s (%d bytes) ===\n%s" % (name, entry, size, c_code))
            
            # Print first 30 lines
            lines = c_code.split('\n')
            for line in lines[:30]:
                println("    %s" % line)
            if len(lines) > 30:
                println("    ... (%d more lines)" % (len(lines) - 30))
        else:
            println("    (decompilation failed)")
    
    decomp.dispose()
    
    # Write all decompiled code to file
    import os
    out_path = os.path.join("e:\\code.projects\\GitHub-projects\\quadzilla_rev", "decompiled_firmware.c")
    f = open(out_path, 'w')
    f.write('\n\n'.join(all_code))
    f.close()
    println("\n  Wrote decompiled code to: %s" % out_path)


def find_data_tables():
    """Find potential calibration/lookup tables in data sections."""
    println("\n=== POTENTIAL CALIBRATION TABLES ===")
    mem = currentProgram.getMemory()
    base = currentProgram.getMinAddress()
    end = currentProgram.getMaxAddress()
    total = end.getOffset() - base.getOffset()
    
    tables = []
    i = 0
    while i < total - 32:
        addr = base.add(i)
        try:
            # Look for sequences of monotonically increasing/decreasing 16-bit values
            vals = []
            for j in range(16):
                v = mem.getShort(addr.add(j * 2)) & 0xFFFF
                vals.append(v)
            
            # Check for monotonic increase (common in lookup tables)
            increasing = all(vals[j] <= vals[j+1] for j in range(len(vals)-1))
            decreasing = all(vals[j] >= vals[j+1] for j in range(len(vals)-1))
            
            if (increasing or decreasing) and vals[0] != vals[-1] and max(vals) < 65000:
                tables.append((str(addr), "inc" if increasing else "dec", vals[:8]))
                i += 32  # Skip past this table
                continue
        except:
            pass
        i += 2
    
    println("  Found %d potential tables" % len(tables))
    for addr, direction, vals in tables[:20]:
        vals_str = ', '.join([str(v) for v in vals])
        println("  %s [%s]: %s ..." % (addr, direction, vals_str))


# Main execution
println("=" * 60)
println("  QUADZILLA ADRENALINE FIRMWARE ANALYSIS")
println("  Firmware: %s" % str(currentProgram.getName()))
println("  Base: %s  End: %s" % (str(currentProgram.getMinAddress()), str(currentProgram.getMaxAddress())))
total_size = currentProgram.getMaxAddress().getOffset() - currentProgram.getMinAddress().getOffset()
println("  Size: %d bytes (%.1f KB)" % (total_size, total_size / 1024.0))
println("=" * 60)

analyze_vectors()
find_strings_in_memory()
funcs = list_functions()
find_data_tables()
find_peripheral_refs()
decompile_top_functions(funcs, 15)

println("\n=== ANALYSIS COMPLETE ===")
