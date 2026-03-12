# -*- coding: utf-8 -*-
#@title Find References to Function
#@category Analysis

import sys

function_name = "calculate_crc8"

if len(sys.argv) > 1:
    function_name = sys.argv[1]

print("Searching for references to function: {}".format(function_name))

# Get the symbol table
symbol_table = currentProgram.getSymbolTable()

# Find all symbols with the given name
# Use getSymbols instead of getAllSymbols
symbols = symbol_table.getSymbols(function_name)

if not symbols:
    print("No symbols found with name: {}".format(function_name))
    sys.exit(0)

for symbol in symbols:
    if symbol.getSymbolType().toString() == "Function":
        function = symbol.getObject()
        print("Found function: {} at {}".format(function.getName(), function.getEntryPoint()))
        
        # Find references to this function
        references = currentProgram.getReferenceManager().getReferencesTo(function.getEntryPoint())
        
        print("References to {}:".format(function_name))
        found_references = False
        
        while references.hasNext():
            ref = references.next()
            from_addr = ref.getFromAddress()
            print("  - Referenced from: {}".format(from_addr))
            
            # Try to find the function containing this reference
            from_func = currentProgram.getFunctionManager().getFunctionContaining(from_addr)
            if from_func is not None:
                print("    In function: {}".format(from_func.getName()))
            
            found_references = True
        
        if not found_references:
            print("  No references found.")