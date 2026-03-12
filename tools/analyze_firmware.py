#!/usr/bin/env python3
"""
Deep analysis of the decrypted ARM firmware binary.
Look for: tuning tables, parameter data, CAN bus IDs, J1939 PIDs, calibration data,
register addresses (for MCU identification).
"""
import struct
import os
import hashlib
from collections import Counter

FW_PATH = r'extracted/from_exe/ckz_75O0/FirmwareUpdate/firmware_arm.bin'

def main():
    with open(FW_PATH, 'rb') as f:
        data = f.read()
    
    base = 0x4000
    print(f"Firmware: {len(data)} bytes ({len(data)/1024:.1f} KB)")
    print(f"Base address: 0x{base:08X}")
    print(f"MD5: {hashlib.md5(data).hexdigest()}")
    
    # ============================================
    # 1. MCU Identification from register addresses
    # ============================================
    print("\n=== MCU REGISTER ADDRESS SCAN ===")
    # Common ARM MCU memory-mapped register ranges
    # LPC2000: Peripherals at 0xE000xxxx and 0xFFxxxxxx
    # STM32: Peripherals at 0x4000xxxx
    # NXP LPC: 0xE01FC000 (system control), 0xE002C000 (pinsel)
    
    reg_hits = Counter()
    for i in range(0, len(data)-3, 4):
        word = struct.unpack_from('<I', data, i)[0]
        # Check for typical ARM peripheral register addresses
        prefix = (word >> 16) & 0xFFFF
        if prefix in [0xE000, 0xE001, 0xE002, 0xE003, 0xE004, 0xE01F, 0xE005, 0xE006, 0xE007, 0xE008]:
            reg_hits[f"0x{word:08X}"] += 1
        elif prefix == 0xFFFF:
            reg_hits[f"0x{word:08X}"] += 1
        elif prefix == 0xFFFE:
            reg_hits[f"0x{word:08X}"] += 1
        elif prefix in [0x4001, 0x4002, 0x4003, 0x4004]:  # STM32-like
            reg_hits[f"0x{word:08X}"] += 1
    
    if reg_hits:
        print(f"Found {len(reg_hits)} potential register addresses:")
        for addr, count in sorted(reg_hits.items(), key=lambda x: -x[1])[:30]:
            # Identify known registers
            val = int(addr, 16)
            name = ""
            # LPC2000 registers
            if val == 0xE01FC000: name = "LPC2xxx MAMCR (Memory Accelerator)"
            elif val == 0xE01FC004: name = "LPC2xxx MAMTIM"
            elif val == 0xE01FC080: name = "LPC2xxx MEMMAP"
            elif val == 0xE01FC0C0: name = "LPC2xxx PLL0CON"
            elif val == 0xE01FC0C4: name = "LPC2xxx PLL0CFG"
            elif val == 0xE01FC0C8: name = "LPC2xxx PLL0STAT"
            elif val == 0xE01FC0CC: name = "LPC2xxx PLL0FEED"
            elif val == 0xE01FC100: name = "LPC2xxx APBDIV"
            elif val == 0xE01FC10C: name = "LPC2xxx CCLKCFG"
            elif val == 0xE002C000: name = "LPC2xxx PINSEL0"
            elif val == 0xE002C004: name = "LPC2xxx PINSEL1"
            elif val == 0xE002C008: name = "LPC2xxx PINSEL2"
            elif val == 0xE002C014: name = "LPC2xxx PINSEL5"
            elif val == 0xE0028000: name = "LPC2xxx IO0DIR (GPIO0)"
            elif val == 0xE0028004: name = "LPC2xxx IO0MASK"
            elif val == 0xE0028008: name = "LPC2xxx IO0PIN"
            elif val == 0xE002800C: name = "LPC2xxx IO0SET"
            elif val == 0xE0028010: name = "LPC2xxx IO0CLR"
            elif val == 0xE0044000: name = "LPC2xxx CAN1 (CAN Bus 1)"
            elif val == 0xE0048000: name = "LPC2xxx CAN2 (CAN Bus 2)"
            elif val == 0xE003C000: name = "LPC2xxx CAN AF"
            elif val == 0xE0040000: name = "LPC2xxx CAN Central"
            elif val == 0xE000C000: name = "LPC2xxx UART0"
            elif val == 0xE0010000: name = "LPC2xxx UART1"
            elif val == 0xE0020000: name = "LPC2xxx SPI (SSP)"
            elif val == 0xE0058000: name = "LPC2xxx I2C0"
            elif val == 0xE0004000: name = "LPC2xxx TIMER0"
            elif val == 0xE0008000: name = "LPC2xxx TIMER1"
            elif val == 0xE0034000: name = "LPC2xxx ADC"
            elif val == 0xE0060000: name = "LPC2xxx USB"
            elif val == 0xE01FC1A0: name = "LPC2xxx SCS (fast GPIO)"
            elif 0xE0044000 <= val <= 0xE004FFFF: name = "LPC2xxx CAN1 range"
            elif 0xE0048000 <= val <= 0xE004FFFF: name = "LPC2xxx CAN2 range"
            elif 0xE003C000 <= val <= 0xE003FFFF: name = "LPC2xxx CAN AF range"
            elif 0xE0060000 <= val <= 0xE0064000: name = "LPC2xxx USB range"
            elif 0xE000C000 <= val <= 0xE000FFFF: name = "LPC2xxx UART0 range"
            elif 0xE0010000 <= val <= 0xE0013FFF: name = "LPC2xxx UART1 range"
            elif 0xE0028000 <= val <= 0xE002BFFF: name = "LPC2xxx GPIO range"
            elif 0xE002C000 <= val <= 0xE002FFFF: name = "LPC2xxx PINSEL range"
            elif 0xE0034000 <= val <= 0xE0037FFF: name = "LPC2xxx ADC range"
            elif 0xE01FC000 <= val <= 0xE01FFFFF: name = "LPC2xxx System Control range"
            
            label = f"  {name}" if name else ""
            print(f"  {addr} (×{count}){label}")
    
    # ============================================
    # 2. CAN Bus Message IDs (J1939/OBD2)
    # ============================================
    print("\n=== CAN BUS / J1939 SCAN ===")
    # J1939 PGNs are typically 0x00xx00 - 0xFFFF00 (18-bit)
    # Common OBD2 CAN IDs: 0x7DF, 0x7E0-0x7E7
    # Common J1939: 0x18FEEE (engine temp), 0x18FEF1 (cruise), etc.
    
    can_ids = set()
    for i in range(0, len(data)-3, 4):
        word = struct.unpack_from('<I', data, i)[0]
        # Check for standard J1939 29-bit CAN IDs
        if 0x18000000 <= word <= 0x1CFFFFFF:
            pgn = (word >> 8) & 0xFFFF
            can_ids.add((word, pgn, i + base))
        # Standard 11-bit CAN IDs
        elif 0x700 <= word <= 0x7FF:
            can_ids.add((word, word, i + base))
    
    if can_ids:
        print(f"Found {len(can_ids)} potential CAN IDs:")
        for cid, pgn, addr in sorted(can_ids)[:40]:
            # Identify known J1939 PGNs
            pgn_name = ""
            if pgn == 0xFEEE: pgn_name = "Engine Coolant Temperature"
            elif pgn == 0xFEEF: pgn_name = "Engine Fuel Rate"
            elif pgn == 0xFEF1: pgn_name = "Cruise Control / Vehicle Speed"
            elif pgn == 0xFEF2: pgn_name = "Fuel Economy"
            elif pgn == 0xFEF5: pgn_name = "Ambient Conditions"
            elif pgn == 0xFEF6: pgn_name = "Inlet/Exhaust Conditions"
            elif pgn == 0xFEF7: pgn_name = "Vehicle Position"
            elif pgn == 0xF003: pgn_name = "Electronic Engine Controller #1 (EEC1)"
            elif pgn == 0xF004: pgn_name = "Electronic Engine Controller #2 (EEC2)"
            elif pgn == 0xF005: pgn_name = "Electronic Transmission Controller #2"
            elif pgn == 0xF009: pgn_name = "Fuel Economy (Liquid)"
            elif pgn == 0xFF00: pgn_name = "Manufacturer Specific"
            elif pgn == 0xFE4A: pgn_name = "Exhaust Gas Temperature"
            elif pgn == 0xFD7D: pgn_name = "High Resolution Vehicle Distance"
            elif pgn == 0xFEFC: pgn_name = "Dash Display"
            elif pgn == 0xFE56: pgn_name = "Aftertreatment Control"
            elif pgn == 0xFDB8: pgn_name = "Turbocharger"
            elif 0xFF00 <= pgn <= 0xFFFF: pgn_name = "Manufacturer Specific"
            elif 0xFE00 <= pgn <= 0xFEFF: pgn_name = "J1939 Range"
            elif 0xF000 <= pgn <= 0xF0FF: pgn_name = "J1939 Range"
            
            label = f"  PGN={pgn:04X} {pgn_name}" if pgn_name else f"  PGN={pgn:04X}"
            print(f"  0x{cid:08X} at 0x{addr:06X}{label}")

    # ============================================
    # 3. Lookup tables / calibration data
    # ============================================
    print("\n=== DATA TABLES SCAN ===")
    # Look for regions with sequential/monotonic 16-bit values (calibration tables)
    table_regions = []
    for i in range(0, len(data) - 32, 2):
        # Check for a run of 16+ monotonically increasing 16-bit values
        vals = [struct.unpack_from('<H', data, i + j*2)[0] for j in range(16)]
        if all(vals[j] <= vals[j+1] for j in range(15)) and vals[-1] > vals[0] + 100:
            table_regions.append((i + base, vals[0], vals[-1], 'increasing'))
        elif all(vals[j] >= vals[j+1] for j in range(15)) and vals[0] > vals[-1] + 100:
            table_regions.append((i + base, vals[0], vals[-1], 'decreasing'))
    
    # Deduplicate (keep first in each run)
    seen = set()
    unique_tables = []
    for addr, vmin, vmax, direction in table_regions:
        key = addr // 64
        if key not in seen:
            seen.add(key)
            unique_tables.append((addr, vmin, vmax, direction))
    
    print(f"Found {len(unique_tables)} potential calibration tables:")
    for addr, vmin, vmax, direction in unique_tables[:20]:
        print(f"  0x{addr:06X}: {direction} {vmin} -> {vmax}")
    
    # ============================================
    # 4. String extraction (all printable sequences)
    # ============================================
    print("\n=== ALL STRINGS >=6 CHARS ===")
    strings = []
    current = []
    for i, b in enumerate(data):
        if 32 <= b < 127:
            current.append(chr(b))
        else:
            if len(current) >= 6:
                strings.append((i + base - len(current), ''.join(current)))
            current = []
    if len(current) >= 6:
        strings.append((len(data) + base - len(current), ''.join(current)))
    
    print(f"Found {len(strings)} strings:")
    for addr, s in strings:
        print(f"  0x{addr:06X}: \"{s}\"")
    
    # ============================================
    # 5. Function call pattern analysis
    # ============================================
    print("\n=== BRANCH/CALL TARGETS ===")
    # ARM BL instruction: 0xEB... (bits 27:24 = 1011)
    call_targets = Counter()
    for i in range(0, len(data) - 3, 4):
        word = struct.unpack_from('<I', data, i)[0]
        cond = (word >> 24) & 0xFF
        if (cond & 0x0F) == 0x0B:  # BL instruction
            offset = word & 0x00FFFFFF
            if offset & 0x00800000:  # Sign extend
                offset = offset - 0x01000000
            target = (i + base) + 8 + offset * 4
            call_targets[target] += 1
    
    print(f"Found {len(call_targets)} unique BL targets:")
    for target, count in sorted(call_targets.items(), key=lambda x: -x[1])[:20]:
        print(f"  0x{target:06X} (called {count} times)")

    print("\nDone!")

if __name__ == '__main__':
    main()
