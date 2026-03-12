# -*- coding: utf-8 -*-
# Nuclear option: clear EVERYTHING, set Thumb, disassemble from known entry points
# @category Quadzilla
# @runtime Jython

from ghidra.app.decompiler import DecompInterface
from ghidra.util.task import ConsoleTaskMonitor
from ghidra.app.cmd.function import CreateFunctionCmd
from ghidra.program.model.lang import RegisterValue
from ghidra.program.disassemble import Disassembler
from java.math import BigInteger

THUMB_ADDRS = [
    0x4114, 0x4214, 0x4384, 0x46D0, 0x48E8, 0x495C, 0x497C, 0x4A94,
    0x4B38, 0x4D38, 0x506C, 0x50F0, 0x571C, 0x575C, 0x59E8,
    0x5CF0, 0x5E04, 0x5EBC, 0x5F14, 0x601C,
    0x6B20, 0x6B48, 0x6B64, 0x6B8C, 0x6B9C, 0x6C94,
    0x73E4, 0x74E8, 0x76CC, 0x77B8,
    0x7AF8, 0x7B1C, 0x7BCC, 0x7BF8, 0x7C1C, 0x7C68, 0x7CC4, 0x7D80,
    0x7E64, 0x7EB4, 0x7EFC, 0x800C, 0x8038, 0x81A8,
    0x8530, 0x854C, 0x8908, 0x8970, 0xB18C,
]

ARM_ADDRS = [0x4000, 0x4028, 0x4044, 0x4090, 0x4094, 0x409C, 0x40B4, 0x40EC, 0x893C, 0x89B0, 0x8A50]

def get_addr(offset):
    return currentProgram.getAddressFactory().getDefaultAddressSpace().getAddress(offset)

listing = currentProgram.getListing()
tmode = currentProgram.getRegister("TMode")
base = currentProgram.getMinAddress()
end = currentProgram.getMaxAddress()

# Step 1: Clear EVERYTHING
println("=== STEP 1: CLEAR ALL CODE UNITS ===")
listing.clearCodeUnits(base, end, False)
println("  Cleared all code units from %s to %s" % (str(base), str(end)))

# Step 2: Set Thumb mode for the Thumb code region
println("\n=== STEP 2: SET THUMB MODE ===")
if tmode is not None:
    thumb_start = get_addr(0x4100)  # After ARM startup code
    try:
        tmode_val = RegisterValue(tmode, BigInteger.valueOf(1))
        currentProgram.getProgramContext().setRegisterValue(thumb_start, end, tmode_val)
        println("  Set TMode=1 for 0x4100-0x%X" % end.getOffset())
    except Exception as e:
        println("  Warning: %s" % str(e))

# Step 3: Disassemble ARM startup code (vectors + reset handler)
println("\n=== STEP 3: DISASSEMBLE ARM STARTUP ===")
disassembler = Disassembler.getDisassembler(currentProgram, ConsoleTaskMonitor(), None)
for addr_val in ARM_ADDRS:
    addr = get_addr(addr_val)
    result = disassembler.disassemble(addr, currentProgram.getAddressFactory().getAddressSet(addr, addr.add(255)), True)
    if result:
        println("  ARM 0x%08X: %d instructions" % (addr_val, result.getNumAddresses()))

# Step 4: Disassemble from each known Thumb function entry
println("\n=== STEP 4: DISASSEMBLE THUMB FUNCTIONS ===")
total_thumb_insts = 0
for addr_val in sorted(THUMB_ADDRS):
    addr = get_addr(addr_val)
    result = disassembler.disassemble(addr, currentProgram.getAddressFactory().getAddressSet(addr, end), True)
    n = result.getNumAddresses() if result else 0
    total_thumb_insts += n
    if n > 10:
        println("  Thumb 0x%08X: %d instructions" % (addr_val, n))

println("  Total Thumb instructions: %d" % total_thumb_insts)

# Step 5: Create functions at all entry points
println("\n=== STEP 5: CREATE FUNCTIONS ===")
created = 0
for addr_val in sorted(THUMB_ADDRS + ARM_ADDRS):
    addr = get_addr(addr_val)
    func = listing.getFunctionContaining(addr)
    if func is not None and func.getEntryPoint().equals(addr):
        continue
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

# Step 7: Decompile everything
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
println("\n=== COMPLETE ===")
