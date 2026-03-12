#!/usr/bin/env python3
"""Filter ADR9802 analysis results for firmware/settings-related info."""
import json

with open('ADR9802v2.8.4_analysis.json') as f:
    data = json.load(f)

print("=== STATS ===")
print(f"Total strings: {len(data.get('strings', []))}")
print(f"Total functions: {len(data.get('functions', []))}")
print(f"Total imports: {len(data.get('imports', []))}")
print(f"Interesting strings: {len(data.get('interesting_strings', []))}")

# Focus on firmware/settings strings
fw_keywords = ['firmware', 'quadzilla', 'adrenaline', 'update', 'flash',
               'power', 'level', 'stage', 'tune', 'boost', 'fuel', 'timing',
               'rpm', 'tps', 'torque', 'injection', 'rail', 'pressure',
               'turbo', 'egt', 'exhaust', 'intake', 'throttle', 'idle',
               'cruise', 'tow', 'economy', 'performance', 'aggressive',
               'stock', 'calibrat', 'setting', 'param', 'option', 'config',
               'feature', 'hidden', 'enable', 'disable', 'mode', 'sensor',
               'gauge', 'trans', 'speed', 'serial', 'command', 'packet',
               'register', 'address', 'offset', 'CAN', 'J1939', 'OBD',
               'PID', 'SPN', 'FMI', 'encrypt', 'decrypt', 'key', 'password',
               'checksum', 'CRC', 'verify', 'write', 'read', 'send',
               'upload', 'download', 'FirmwareUpdate', '.qz', '.pwd',
               '.pwk', '.opt', 'X2Updater', 'setupWizard', 'Quadzilla.dll',
               'Working', 'noInterface', 'unzipToTemp', 'setupFilename']

print("\n=== FIRMWARE/SETTINGS STRINGS ===")
seen = set()
for s in data.get('strings', []):
    val = s['value']
    val_lower = val.lower()
    for kw in fw_keywords:
        if kw.lower() in val_lower and val not in seen and len(val) > 3:
            seen.add(val)
            print(f"  {s['address']}: {val[:200]}")
            break

# Also show strings near the overlay start (these are likely the self-extractor engine)
print("\n=== STRINGS IN 0x00040000-0x00058000 RANGE (self-extractor code) ===")
for s in data.get('strings', []):
    try:
        addr = int(s['address'], 16)
        if 0x00040000 <= addr <= 0x00058000:
            val = s['value']
            if len(val) > 5:
                print(f"  {s['address']}: {val[:200]}")
    except:
        pass

# Non-FUN named functions
print("\n=== NAMED FUNCTIONS (non-FUN_, non-thunk, non-single letter) ===")
named = [f for f in data.get('functions', []) if 
         not f['name'].startswith('FUN_') and 
         len(f['name']) > 3 and
         f['size'] > 10]
for f in sorted(named, key=lambda x: x['name']):
    print(f"  {f['name']} @ {f['address']} (size={f['size']})")

# Imports
print("\n=== NON-STANDARD IMPORTS ===")
std_libs = {'KERNEL32.DLL', 'USER32.DLL', 'GDI32.DLL', 'ADVAPI32.DLL',
            'COMCTL32.DLL', 'COMDLG32.DLL', 'SHELL32.DLL', 'msvcrt.dll',
            'MSVCRT.DLL', 'ole32.dll', 'OLE32.DLL', 'oleaut32.dll',
            'OLEAUT32.DLL', 'VERSION.DLL'}
for i in data.get('imports', []):
    if i['library'] not in std_libs:
        print(f"  {i['library']}: {i['name']}")
