#!/usr/bin/env python3
"""Filter and present the interesting findings from Ghidra analysis."""
import json

with open('SmartyUSB_analysis.json') as f:
    data = json.load(f)

print("=== STATS ===")
print(f"Total strings: {len(data.get('strings', []))}")
print(f"Total functions: {len(data.get('functions', []))}")
print(f"Total imports: {len(data.get('imports', []))}")
print(f"Interesting strings: {len(data.get('interesting_strings', []))}")

print("\n=== INTERESTING STRINGS ===")
for s in data.get('interesting_strings', []):
    val = s['value']
    if len(val) > 3:  # Skip very short strings
        print(f"  {s['address']}: {val[:150]}")

print("\n=== ALL STRINGS WITH 'smarty' (case insensitive) ===")
for s in data.get('strings', []):
    if 'smarty' in s['value'].lower() or 'smt' in s['value'].lower():
        print(f"  {s['address']}: {s['value'][:150]}")

print("\n=== ALL STRINGS WITH 'FT_' (FTDI functions) ===")
for s in data.get('strings', []):
    if 'FT_' in s['value'] or 'ftdi' in s['value'].lower():
        print(f"  {s['address']}: {s['value'][:150]}")

print("\n=== STRINGS WITH setting/param/config/feature/option/mode/level/power ===")
for s in data.get('strings', []):
    val_lower = s['value'].lower()
    for kw in ['setting', 'param', 'config', 'feature', 'option', 'mode', 'level', 'power', 'stage', 'tune', 'calibrat']:
        if kw in val_lower:
            print(f"  {s['address']}: {s['value'][:150]}")
            break

print("\n=== STRINGS WITH USB/serial/baud/COM ===")
for s in data.get('strings', []):
    val_lower = s['value'].lower()
    for kw in ['usb', 'serial', 'baud', 'comm', 'com port', 'device']:
        if kw in val_lower:
            print(f"  {s['address']}: {s['value'][:150]}")
            break

print("\n=== STRINGS WITH flash/erase/program/verify/write/read/send ===")
for s in data.get('strings', []):
    val_lower = s['value'].lower()
    for kw in ['flash', 'erase', 'program', 'verify', 'firmware', 'update', 'download', 'upload', 'send', 'receive', 'transmit']:
        if kw in val_lower:
            print(f"  {s['address']}: {s['value'][:150]}")
            break

print("\n=== STRINGS WITH error/fault/code/DTC ===")
for s in data.get('strings', []):
    val_lower = s['value'].lower()
    for kw in ['error', 'fault', 'code', 'dtc', 'diagnostic', 'trouble', 'warning', 'alert']:
        if kw in val_lower and len(s['value']) > 6:
            print(f"  {s['address']}: {s['value'][:150]}")
            break

print("\n=== STRINGS WITH engine/fuel/boost/timing/RPM/injection ===")
for s in data.get('strings', []):
    val_lower = s['value'].lower()
    for kw in ['engine', 'fuel', 'boost', 'timing', 'rpm', 'injection', 'rail', 'pressure', 'turbo', 'egt', 'exhaust', 'intake', 'throttle', 'tps', 'torque', 'trans']:
        if kw in val_lower:
            print(f"  {s['address']}: {s['value'][:150]}")
            break

print("\n=== STRINGS WITH encrypt/decrypt/key/password/checksum/CRC ===")
for s in data.get('strings', []):
    val_lower = s['value'].lower()
    for kw in ['encrypt', 'decrypt', 'cipher', 'key', 'password', 'hash', 'checksum', 'crc', 'signature']:
        if kw in val_lower:
            print(f"  {s['address']}: {s['value'][:150]}")
            break

print("\n=== NAMED FUNCTIONS (non-FUN_, non-thunk) ===")
named = [f for f in data.get('functions', []) if not f['name'].startswith('FUN_')]
for f in sorted(named, key=lambda x: x['name']):
    print(f"  {f['name']} @ {f['address']} (size={f['size']})")
