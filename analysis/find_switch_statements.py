# -*- coding: utf-8 -*-
#@title Find Switch Statements
#@category Analysis

# Get the function manager
function_manager = currentProgram.getFunctionManager()

# Get all functions
functions = function_manager.getFunctions(True)

print("Looking for functions with switch statements...")
print("=" * 50)

switch_functions = []

for function in functions:
    function_name = function.getName()
    entry_point = function.getEntryPoint()
    
    try:
        # Try to decompile the function
        decompile = currentProgram.getDecompiler()
        decompile_results = decompile.decompile(function, 30)
        
        if decompile_results and decompile_results.decompileCompleted():
            decompiled_code = decompile_results.getDecompiledFunction().getC()
            
            # Check if the decompiled code contains a switch statement
            if "switch" in decompiled_code:
                switch_functions.append((function_name, entry_point))
                print("[SWITCH STATEMENT] {} at {}".format(function_name, entry_point))
                
                # Print a snippet of the decompiled code
                lines = decompiled_code.split('\n')
                for i, line in enumerate(lines):
                    if "switch" in line:
                        # Print a few lines around the switch statement
                        start = max(0, i-2)
                        end = min(len(lines), i+10)
                        for j in range(start, end):
                            print("  {}".format(lines[j]))
                        print("  ...")
                        break
    except:
        # If decompilation fails, just continue
        pass

print("=" * 50)
print("Found {} functions with switch statements".format(len(switch_functions)))

# Now let's look for functions that might be CRC-related by examining their code
print("\nLooking for potential CRC functions...")
print("=" * 50)

crc_functions = []

for function in functions:
    function_name = function.getName()
    entry_point = function.getEntryPoint()
    
    try:
        # Try to decompile the function
        decompile = currentProgram.getDecompiler()
        decompile_results = decompile.decompile(function, 30)
        
        if decompile_results and decompile_results.decompileCompleted():
            decompiled_code = decompile_results.getDecompiledFunction().getC()
            
            # Check if the decompiled code contains CRC-like patterns
            crc_patterns = [
                "0xFF",  # Common CRC mask
                "0x8",   # Common CRC polynomial
                "0x18",  # Another common CRC polynomial
                "0x1021", # CRC-16 polynomial
                "xor",   # XOR operation common in CRC
                "shift",  # Shift operation common in CRC
                "0x10000", # Common CRC-16 mask
                "0x1000000" # Common CRC-32 mask
            ]
            
            found_patterns = []
            for pattern in crc_patterns:
                if pattern in decompiled_code:
                    found_patterns.append(pattern)
            
            if len(found_patterns) >= 2:  # If multiple CRC patterns are found
                crc_functions.append((function_name, entry_point, found_patterns))
                print("[POTENTIAL CRC] {} at {} (patterns: {})".format(function_name, entry_point, found_patterns))
                
                # Print a snippet of the decompiled code
                lines = decompiled_code.split('\n')
                for i, line in enumerate(lines):
                    if any(pattern in line for pattern in found_patterns):
                        # Print a few lines around the pattern
                        start = max(0, i-1)
                        end = min(len(lines), i+3)
                        for j in range(start, end):
                            print("  {}".format(lines[j]))
                        print("  ...")
                        break
    except:
        # If decompilation fails, just continue
        pass

print("=" * 50)
print("Found {} potential CRC functions".format(len(crc_functions)))