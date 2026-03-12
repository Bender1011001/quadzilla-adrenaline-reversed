# -*- coding: utf-8 -*-
#@title Find References to Memory Addresses
#@category Analysis

# Script to find all references to the fueling table memory locations
# Can be run in Ghidra headless mode

from ghidra.app.decompiler import DecompInterface
from ghidra.util.task import ConsoleTaskMonitor

def find_memory_references():
    print("=== Finding Fueling Table References ===")
    
    # Key memory offsets we identified
    target_offsets = [
        0x313,  # Primary data allocation pointer
        0x314,  # Secondary data allocation pointer  
        0x315,  # Tertiary data allocation pointer
        0xab60  # Fueling table base offset
    ]
    
    function_manager = currentProgram.getFunctionManager()
    address_factory = currentProgram.getAddressFactory()
    
    # Get all functions
    functions = function_manager.getFunctions(True)
    
    print("Analyzing {} functions...".format(function_manager.getFunctionCount()))
    
    # Initialize decompiler
    decompiler = DecompInterface()
    decompiler.openProgram(currentProgram)
    
    for function in functions:
        func_name = function.getName()
        func_addr = function.getEntryPoint()
        
        # Skip the table builder function - we already analyzed it
        if func_name == "FUN_00427401":
            continue
            
        # Decompile the function to analyze it
        try:
            decomp_result = decompiler.decompileFunction(function, 30, ConsoleTaskMonitor())
            if decomp_result and decomp_result.decompileCompleted():
                c_code = decomp_result.getDecompiledFunction().getC()
                
                # Check for references to our target memory offsets
                found_refs = []
                for offset in target_offsets:
                    hex_pattern = "0x{:x}".format(offset)
                    if hex_pattern in c_code:
                        found_refs.append(hex_pattern)
                
                # Check for array indexing patterns that might be table lookups
                table_patterns = [
                    "[",  # Array indexing
                    "* 0x",  # Multiplication for indexing
                    "+ 0x",  # Address offset calculations
                ]
                
                has_table_patterns = any(pattern in c_code for pattern in table_patterns)
                
                if found_refs or has_table_patterns:
                    print("\n=== Function: {} @ {} ===".format(func_name, func_addr))
                    if found_refs:
                        print("Found memory references: {}".format(", ".join(found_refs)))
                    if has_table_patterns:
                        print("Contains potential table lookup patterns")
                    
                    # Print first 20 lines of decompiled code for analysis
                    lines = c_code.split('\n')[:20]
                    for i, line in enumerate(lines):
                        print("  {:2d}: {}".format(i+1, line))
                    print("  ... (truncated)")
                    
        except Exception as e:
            print("Error decompiling {}: {}".format(func_name, str(e)))
    
    decompiler.dispose()

def find_can_functions():
    print("\n=== Finding Potential CAN/Sensor Functions ===")
    
    function_manager = currentProgram.getFunctionManager()
    functions = function_manager.getFunctions(True)
    
    # Look for functions that might handle sensor data or CAN messages
    can_indicators = [
        "FUN_0041d527",  # From our analysis - appears to parse data streams
        "FUN_004227b8",  # From our analysis - appears to parse data streams
    ]
    
    for function in functions:
        func_name = function.getName()
        func_addr = function.getEntryPoint()
        
        # Check if this is one of our identified functions
        if func_name in can_indicators:
            print("\n=== Potential Sensor Handler: {} @ {} ===".format(func_name, func_addr))
            
            # Get references TO this function (who calls it)
            references = currentProgram.getReferenceManager().getReferencesTo(func_addr)
            callers = []
            while references.hasNext():
                ref = references.next()
                from_addr = ref.getFromAddress()
                caller_func = function_manager.getFunctionContaining(from_addr)
                if caller_func:
                    callers.append("{}@{}".format(caller_func.getName(), from_addr))
            
            print("Called from: {}".format(", ".join(callers) if callers else "No callers found"))

if __name__ == "__main__":
    find_memory_references()
    find_can_functions()
    print("\n=== Analysis Complete ===")