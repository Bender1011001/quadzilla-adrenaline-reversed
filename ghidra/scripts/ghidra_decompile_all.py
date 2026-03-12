# -*- coding: utf-8 -*-
# Fixed approach: disassemble per-function with restricted address ranges,
# then create functions, then decompile everything
# @category Quadzilla
# @runtime Jython

from ghidra.app.decompiler import DecompInterface
from ghidra.util.task import ConsoleTaskMonitor
from ghidra.app.cmd.function import CreateFunctionCmd
from ghidra.program.model.lang import RegisterValue
from ghidra.program.disassemble import Disassembler
from java.math import BigInteger

# Known function entry points sorted by address, with estimated end addresses
# End addresses are set to just before the next function entry
THUMB_ENTRIES = [
    0x4114, 0x4214, 0x4384, 0x46D0, 0x48E8, 0x495C, 0x497C, 0x4A94,
    0x4B38, 0x4D38, 0x506C, 0x50F0, 0x571C, 0x575C, 0x59E8,
    0x5CF0, 0x5E04, 0x5EBC, 0x5F14, 0x601C,
    0x6B20, 0x6B48, 0x6B64, 0x6B8C, 0x6B9C, 0x6C94,
    0x73E4, 0x74E8, 0x76CC, 0x77B8,
    0x7AF8, 0x7B1C, 0x7BCC, 0x7BF8, 0x7C1C, 0x7C68, 0x7CC4, 0x7D80,
    0x7E64, 0x7EB4, 0x7EFC, 0x800C, 0x8038, 0x81A8,
    0x8530, 0x854C, 0x8908, 0x8970, 0xB18C,
]

ARM_ENTRIES = [0x4000, 0x4028, 0x4044, 0x4090, 0x4094, 0x409C, 0x40B4, 0x40EC]
ARM_FUNCS_LATE = [0x893C, 0x89B0, 0x8A50]

def get_addr(offset):
    return currentProgram.getAddressFactory().getDefaultAddressSpace().getAddress(offset)

def make_addr_set(start, end):
    return currentProgram.getAddressFactory().getAddressSet(get_addr(start), get_addr(end))

listing = currentProgram.getListing()
tmode = currentProgram.getRegister("TMode")
monitor = ConsoleTaskMonitor()

# Step 1: Clear EVERYTHING
println("=== STEP 1: CLEAR ALL ===")
base = currentProgram.getMinAddress()
end = currentProgram.getMaxAddress()

# Remove all existing functions first
func_iter = listing.getFunctions(True)
func_list = []
while func_iter.hasNext():
    func_list.append(func_iter.next())
for func in func_list:
    currentProgram.getFunctionManager().removeFunction(func.getEntryPoint())
println("  Removed %d existing functions" % len(func_list))

# Clear all code units
listing.clearCodeUnits(base, end, False)
println("  Cleared all code units")

# Step 2: Set TMode
println("\n=== STEP 2: SET TMODE ===")
if tmode is not None:
    thumb_start = get_addr(0x4100)
    tmode_val = RegisterValue(tmode, BigInteger.valueOf(1))
    currentProgram.getProgramContext().setRegisterValue(thumb_start, end, tmode_val)
    println("  TMode=1 from 0x4100 to end")

# Step 3: Disassemble ARM startup (small, won't cascade far)
println("\n=== STEP 3: ARM STARTUP ===")
disassembler = Disassembler.getDisassembler(currentProgram, monitor, None)
for addr_val in ARM_ENTRIES:
    addr = get_addr(addr_val)
    # Disassemble with restricted range (just this vector entry area)
    end_val = min(addr_val + 0x100, 0x4100)
    result = disassembler.disassemble(addr, make_addr_set(addr_val, end_val), True)

for addr_val in ARM_FUNCS_LATE:
    addr = get_addr(addr_val)
    # Set ARM mode for these
    if tmode is not None:
        arm_val = RegisterValue(tmode, BigInteger.valueOf(0))
        currentProgram.getProgramContext().setRegisterValue(addr, addr.add(0x80), arm_val)
    result = disassembler.disassemble(addr, make_addr_set(addr_val, addr_val + 0x80), True)

# Step 4: Disassemble each Thumb function INDIVIDUALLY with restricted range
println("\n=== STEP 4: THUMB FUNCTIONS (restricted ranges) ===")
all_entries = sorted(THUMB_ENTRIES)

for i, addr_val in enumerate(all_entries):
    # Estimate end: midpoint to next function or +2KB max
    if i + 1 < len(all_entries):
        next_entry = all_entries[i + 1]
        max_size = next_entry - addr_val
    else:
        max_size = 0x800
    
    # Cap at 4KB to be safe, minimum 32 bytes
    max_size = min(max(max_size, 32), 0x1000)
    end_val = addr_val + max_size - 1
    
    addr = get_addr(addr_val)
    addr_set = make_addr_set(addr_val, end_val)
    result = disassembler.disassemble(addr, addr_set, True)
    n = result.getNumAddresses() if result else 0
    if n > 10:
        println("  0x%08X: %4d instructions (range %d bytes)" % (addr_val, n, max_size))

# Step 5: Create functions at ALL entry points
println("\n=== STEP 5: CREATE FUNCTIONS ===")
created = 0
for addr_val in sorted(ARM_ENTRIES + ARM_FUNCS_LATE + THUMB_ENTRIES):
    addr = get_addr(addr_val)
    # Check if already inside another function
    existing = listing.getFunctionContaining(addr)
    if existing is not None:
        if existing.getEntryPoint().equals(addr):
            continue
        # This address is inside another function - need to split
        # Remove the encompassing function, then create both
        old_entry = existing.getEntryPoint()
        currentProgram.getFunctionManager().removeFunction(old_entry)
        # Re-create the old function
        cmd = CreateFunctionCmd(old_entry)
        cmd.applyTo(currentProgram)
    
    cmd = CreateFunctionCmd(addr)
    if cmd.applyTo(currentProgram):
        created += 1

println("  Created %d functions" % created)

# Step 6: List all functions
funcs = []
func_iter = listing.getFunctions(True)
while func_iter.hasNext():
    func = func_iter.next()
    size = func.getBody().getNumAddresses()
    name = func.getName()
    entry = str(func.getEntryPoint())
    funcs.append((size, name, entry))

funcs.sort(key=lambda x: x[0], reverse=True)

println("\n=== ALL FUNCTIONS (%d total) ===" % len(funcs))
println("  %-12s %-40s %6s" % ("Address", "Name", "Size"))
println("  " + "-" * 60)
for size, name, entry in funcs:
    println("  %-12s %-40s %6d" % (entry, name, size))

# Step 7: Decompile ALL functions >= 8 bytes
to_decompile = [(s,n,e) for s,n,e in funcs if s >= 8]
println("\n=== DECOMPILING %d FUNCTIONS ===" % len(to_decompile))

decomp = DecompInterface()
decomp.openProgram(currentProgram)

all_code = []
for i, (size, name, entry) in enumerate(to_decompile):
    try:
        addr_val = int(entry, 16)
        addr = get_addr(addr_val)
        func = getFunctionAt(addr)
    except:
        continue
    
    if func is None:
        continue
    
    result = decomp.decompileFunction(func, 120, monitor)
    if result and result.decompileCompleted():
        c_code = result.getDecompiledFunction().getC()
        header = "// === %s at %s (%d bytes) ===" % (name, entry, size)
        all_code.append(header + "\n" + c_code)
        
        lines = c_code.split('\n')
        println("  [%d/%d] %-30s %5d bytes %4d lines" % (
            i+1, len(to_decompile), name, size, len(lines)))
    else:
        msg = ""
        if result:
            msg = str(result.getErrorMessage()) if result.getErrorMessage() else ""
        println("  [%d/%d] %-30s FAILED %s" % (i+1, len(to_decompile), name, msg[:80]))

decomp.dispose()

import os
out_path = os.path.join("e:\\code.projects\\GitHub-projects\\quadzilla_rev", "decompiled_firmware_full.c")
f = open(out_path, 'w')
f.write('\n\n'.join(all_code))
f.close()
println("\n  Wrote %d functions (%d bytes) to: %s" % (len(all_code), len('\n\n'.join(all_code)), out_path))
println("\n=== COMPLETE ===")
