# Extract strings, function names, and references from the binary
# @category Analysis
# @runtime Jython

from ghidra.program.model.listing import CodeUnit
from ghidra.program.model.symbol import SourceType
from ghidra.program.model.data import StringDataType
import os
import json

def extract_all_strings(program):
    """Extract all defined strings from the program."""
    listing = program.getListing()
    mem = program.getMemory()
    strings = []
    
    # Get all defined strings
    data_iter = listing.getDefinedData(True)
    while data_iter.hasNext():
        data = data_iter.next()
        dt = data.getDataType()
        if 'string' in dt.getName().lower() or 'unicode' in dt.getName().lower():
            try:
                val = data.getValue()
                if val and len(str(val)) >= 4:
                    strings.append({
                        'address': str(data.getAddress()),
                        'value': str(val),
                        'type': dt.getName()
                    })
            except:
                pass
    
    return strings

def extract_functions(program):
    """Extract all function names and addresses."""
    fm = program.getFunctionManager()
    functions = []
    func_iter = fm.getFunctions(True)
    while func_iter.hasNext():
        func = func_iter.next()
        functions.append({
            'name': func.getName(),
            'address': str(func.getEntryPoint()),
            'signature': str(func.getSignature()) if func.getSignature() else '',
            'size': func.getBody().getNumAddresses(),
            'callers': [str(ref.getFromAddress()) for ref in func.getSymbol().getReferences()[:20]],
            'is_thunk': func.isThunk()
        })
    return functions

def extract_imports(program):
    """Extract imported functions."""
    sm = program.getSymbolTable()
    imports = []
    ext_syms = sm.getExternalSymbols()
    while ext_syms.hasNext():
        sym = ext_syms.next()
        imports.append({
            'name': sym.getName(),
            'library': str(sym.getParentNamespace()),
            'address': str(sym.getAddress())
        })
    return imports

def find_interesting_patterns(strings):
    """Find strings related to firmware, settings, protocols."""
    keywords = [
        'firmware', 'flash', 'program', 'erase', 'CAN', 'USB', 'COM',
        'serial', 'baud', 'update', 'version', 'adrenaline', 'quadzilla',
        'smarty', 'power', 'level', 'boost', 'fuel', 'timing', 'rpm',
        'tps', 'map', 'tune', 'calibrat', 'table', 'PIC', 'dsPIC',
        'setting', 'param', 'option', 'config', 'feature', 'hidden',
        'enable', 'disable', 'mode', 'speed', 'torque', 'injection',
        'rail', 'pressure', 'turbo', 'EGT', 'trans', 'gauge', 'sensor',
        'temperature', 'coolant', 'oil', 'exhaust', 'intake', 'throttle',
        'idle', 'cruise', 'tow', 'economy', 'performance', 'aggressive',
        'stock', 'level', 'stage', 'error', 'fault', 'code', 'DTC',
        'CAN', 'J1939', 'OBD', 'PID', 'SPN', 'FMI', 'command',
        'response', 'packet', 'register', 'address', 'offset',
        'SmartyFile', 'smt', 'SmtE', 'encrypt', 'decrypt', 'key',
        'password', 'checksum', 'CRC', 'verify', 'write', 'read',
        'FT_', 'FTDI', 'D2XX'
    ]
    
    interesting = []
    for s in strings:
        val_lower = s['value'].lower()
        for kw in keywords:
            if kw.lower() in val_lower:
                interesting.append(s)
                break
    return interesting

def main():
    program = currentProgram
    print("Program: %s" % program.getName())
    print("Architecture: %s" % program.getLanguage().getProcessor())
    print("Endian: %s" % program.getLanguage().isBigEndian())
    
    # Extract strings
    print("\nExtracting strings...")
    strings = extract_all_strings(program)
    print("  Found %d strings" % len(strings))
    
    # Find interesting ones
    interesting = find_interesting_patterns(strings)
    print("  %d interesting strings:" % len(interesting))
    for s in sorted(interesting, key=lambda x: x['address']):
        print("    %s: %s" % (s['address'], s['value'][:120]))
    
    # Extract functions
    print("\nExtracting functions...")
    functions = extract_functions(program)
    print("  Found %d functions" % len(functions))
    
    # Filter for non-library functions
    user_funcs = [f for f in functions if not f['is_thunk'] and not f['name'].startswith('FUN_')]
    named_funcs = [f for f in functions if not f['name'].startswith('FUN_') and not f['is_thunk']]
    print("  Named user functions:")
    for f in sorted(named_funcs, key=lambda x: x['name']):
        print("    %s @ %s (size=%d)" % (f['name'], f['address'], f['size']))
    
    # Extract imports
    print("\nExtracting imports...")
    imports = extract_imports(program)
    print("  Found %d imports" % len(imports))
    
    # Focus on FTDI and interesting imports
    ftdi_imports = [i for i in imports if 'FT_' in i['name'] or 'FTDI' in i['name'].upper()]
    print("  FTDI imports:")
    for i in ftdi_imports:
        print("    %s from %s" % (i['name'], i['library']))
    
    # Save full results to JSON
    output = {
        'program': program.getName(),
        'strings': strings,
        'interesting_strings': interesting,
        'functions': [{'name': f['name'], 'address': f['address'], 'size': f['size']} for f in functions],
        'imports': imports
    }
    
    # Write to file
    out_path = os.path.join(os.getcwd(), program.getName().replace('.exe', '') + '_analysis.json')
    with open(out_path, 'w') as f:
        json.dump(output, f, indent=2)
    print("\nFull results saved to: %s" % out_path)

main()
