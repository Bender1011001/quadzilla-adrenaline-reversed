# -*- coding: utf-8 -*-
#@title List All Functions
#@category Analysis

# Get the function manager
function_manager = currentProgram.getFunctionManager()

# Get all functions
functions = function_manager.getFunctions(True)

print("Listing all functions in the binary:")
print("=" * 50)

count = 0
for function in functions:
    count += 1
    function_name = function.getName()
    entry_point = function.getEntryPoint()
    
    # Check if function name contains CRC-related keywords
    crc_related = False
    if "crc" in function_name.lower():
        crc_related = True
    elif "checksum" in function_name.lower():
        crc_related = True
    elif "packet" in function_name.lower():
        crc_related = True
    elif "process" in function_name.lower():
        crc_related = True
    
    if crc_related:
        print("[CRC/PACKET RELATED] {} at {}".format(function_name, entry_point))
    elif count <= 20:  # Print first 20 functions regardless
        print("{} at {}".format(function_name, entry_point))

print("=" * 50)
print("Total functions: {}".format(count))

# Now let's look for functions that might be called frequently
print("\nLooking for functions with many references...")
print("=" * 50)

# Reset count and look for functions with many references
count = 0
for function in functions:
    count += 1
    function_name = function.getName()
    entry_point = function.getEntryPoint()
    
    # Get references to this function
    references = currentProgram.getReferenceManager().getReferencesTo(entry_point)
    
    # Count references
    ref_count = 0
    while references.hasNext():
        references.next()
        ref_count += 1
    
    if ref_count > 5:  # Functions called more than 5 times
        print("[FREQUENTLY CALLED] {} at {} (called {} times)".format(function_name, entry_point, ref_count))
    elif count <= 10:  # Print first 10 functions regardless
        print("{} at {} (called {} times)".format(function_name, entry_point, ref_count))