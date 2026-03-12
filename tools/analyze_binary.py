#!/usr/bin/env python3
"""
Deep binary analysis of decrypted Quadzilla firmware.
Analyzes raw bytes to determine ARM vs Thumb instruction patterns,
find code regions, data regions, and function prologues.
"""
import struct
import sys
from pathlib import Path

def load_ihex(path):
    """Load Intel HEX file into a dict of address -> byte."""
    data = {}
    min_addr = 0xFFFFFFFF
    max_addr = 0
    base_addr = 0
    
    with open(path, 'r') as f:
        for line in f:
            line = line.strip()
            if not line.startswith(':'):
                continue
            
            byte_count = int(line[1:3], 16)
            address = int(line[3:7], 16)
            record_type = int(line[7:9], 16)
            
            if record_type == 0:  # Data record
                full_addr = base_addr + address
                for i in range(byte_count):
                    b = int(line[9 + i*2:11 + i*2], 16)
                    data[full_addr + i] = b
                    min_addr = min(min_addr, full_addr)
                    max_addr = max(max_addr, full_addr + i)
            elif record_type == 2:  # Extended Segment Address
                base_addr = int(line[9:13], 16) << 4
            elif record_type == 4:  # Extended Linear Address
                base_addr = int(line[9:13], 16) << 16
            elif record_type == 1:  # EOF
                break
    
    return data, min_addr, max_addr

def get_word(data, addr):
    """Get a 32-bit word (little-endian)."""
    try:
        return data[addr] | (data[addr+1] << 8) | (data[addr+2] << 16) | (data[addr+3] << 24)
    except KeyError:
        return None

def get_halfword(data, addr):
    """Get a 16-bit halfword (little-endian)."""
    try:
        return data[addr] | (data[addr+1] << 8)
    except KeyError:
        return None

def is_arm_instruction(word):
    """Check if a 32-bit word looks like a valid ARM instruction."""
    if word is None:
        return False
    cond = (word >> 28) & 0xF
    if cond == 0xF:  # Unconditional - valid in ARMv5+
        return True
    # Check for common ARM instruction patterns
    # Data processing: cond 00x xxxx
    if ((word >> 26) & 3) == 0:
        return True
    # Load/Store: cond 01x xxxx
    if ((word >> 26) & 3) == 1:
        return True
    # Branch: cond 101x xxxx
    if ((word >> 25) & 7) == 5:
        return True
    return False

def is_thumb_push(halfword):
    """Check for Thumb PUSH instruction (common function prologue)."""
    if halfword is None:
        return False
    # PUSH {Rn, ...} = 1011 0100 xxxx xxxx or 1011 0101 xxxx xxxx
    return (halfword & 0xFE00) == 0xB400

def is_thumb_pop(halfword):
    """Check for Thumb POP instruction."""
    if halfword is None:
        return False
    # POP {Rn, ...} = 1011 1100 xxxx xxxx or 1011 1101 xxxx xxxx
    return (halfword & 0xFE00) == 0xBC00

def is_thumb_bx(halfword):
    """Check for Thumb BX LR (return) instruction."""
    if halfword is None:
        return False
    return halfword == 0x4770  # BX LR

def is_thumb_mov_lr(halfword):
    """Check for MOV LR, PC type instructions."""
    if halfword is None:
        return False
    return (halfword & 0xFF00) == 0x4600  # MOV Rx, Rx

def analyze_instruction_density(data, start, end, window_size=64):
    """Analyze instruction density in sliding windows."""
    regions = []
    for addr in range(start, end - window_size, window_size):
        # Check ARM instruction density
        arm_valid = 0
        for i in range(0, window_size, 4):
            w = get_word(data, addr + i)
            if w is not None and is_arm_instruction(w):
                arm_valid += 1
        arm_density = arm_valid / (window_size // 4)
        
        # Check Thumb instruction patterns
        thumb_valid = 0
        for i in range(0, window_size, 2):
            hw = get_halfword(data, addr + i)
            if hw is not None and hw != 0x0000 and hw != 0xFFFF:
                # Check for recognizable Thumb patterns
                if (hw & 0xF800) in [0x4800, 0x4000, 0x2000, 0x6800, 0x6000, 
                                      0x7800, 0x7000, 0xB400, 0xBC00, 0xE000,
                                      0xD000, 0xF000, 0x0000, 0x0800, 0x1800]:
                    thumb_valid += 1
        thumb_density = thumb_valid / (window_size // 2)
        
        regions.append((addr, arm_density, thumb_density))
    
    return regions

def find_function_prologues(data, start, end):
    """Find likely function start points."""
    prologues = []
    
    for addr in range(start, end - 4, 2):
        hw = get_halfword(data, addr)
        
        # Thumb PUSH {regs, LR}
        if hw is not None and is_thumb_push(hw):
            # PUSH that includes LR (bit 8 set) = function prologue
            if hw & 0x0100:
                prologues.append(('thumb_push_lr', addr, hw))
        
        # ARM STMDB SP!, {regs, LR}
        w = get_word(data, addr)
        if w is not None:
            # E92D xxxx = STMDB SP!, {regs}
            if (w & 0xFFFF0000) == 0xE92D0000 and (w & 0x4000):  # includes LR
                prologues.append(('arm_stmdb_lr', addr, w))
    
    return prologues

def find_string_references(data, start, end):
    """Find ASCII strings in the data."""
    strings = []
    i = start
    while i < end - 4:
        # Look for runs of printable ASCII
        if data.get(i, 0) >= 0x20 and data.get(i, 0) <= 0x7E:
            s = []
            j = i
            while j < end and data.get(j, 0) >= 0x20 and data.get(j, 0) <= 0x7E:
                s.append(chr(data[j]))
                j += 1
            if len(s) >= 4:
                strings.append((i, ''.join(s)))
            i = j + 1
        else:
            i += 1
    return strings

def main():
    fw_path = r"e:\code.projects\GitHub-projects\quadzilla_rev\extracted\from_exe\ckz_75O0\FirmwareUpdate\FirmwareUpdate_decrypted.hex"
    
    print("Loading firmware...")
    data, min_addr, max_addr = load_ihex(fw_path)
    total = max_addr - min_addr + 1
    print(f"  Range: 0x{min_addr:08X} - 0x{max_addr:08X} ({total} bytes, {total/1024:.1f} KB)")
    
    # Analyze interrupt vectors
    print("\n=== INTERRUPT VECTORS ===")
    vector_names = ['Reset', 'Undef', 'SWI', 'PrefAbort', 'DataAbort', 'Rsvd', 'IRQ', 'FIQ']
    for i, name in enumerate(vector_names):
        w = get_word(data, min_addr + i * 4)
        if w is not None:
            # ARM branch: EA xxxxxx = B <offset>
            if (w >> 24) == 0xEA:
                offset = w & 0x00FFFFFF
                if offset & 0x800000:
                    offset |= 0xFF000000  # Sign extend
                target = min_addr + i * 4 + 8 + (offset << 2)
                print(f"  {name:12s}: 0x{w:08X}  -> 0x{target:08X}  (ARM branch)")
            else:
                print(f"  {name:12s}: 0x{w:08X}")
    
    # Find reset handler and startup code
    reset_vec = get_word(data, min_addr)
    if reset_vec is not None and (reset_vec >> 24) == 0xEA:
        offset = reset_vec & 0x00FFFFFF
        if offset & 0x800000:
            offset |= 0xFF000000
        reset_target = min_addr + 8 + (offset << 2)
        print(f"\n  Reset handler at: 0x{reset_target:08X}")
        
        # Check for BX instruction (ARM-to-Thumb switch)
        for scan in range(reset_target, min(reset_target + 256, max_addr), 4):
            w = get_word(data, scan)
            if w is not None:
                # BX Rn = 0x012FFF1n
                if (w & 0x0FFFFFF0) == 0x012FFF10:
                    reg = w & 0xF
                    print(f"  Found BX R{reg} at 0x{scan:08X} -> ARM-to-Thumb switch!")
                # ADD PC, Rn
                if (w & 0x0FFF0000) == 0x028F0000:
                    print(f"  Found ADD PC at 0x{scan:08X}")
    
    # Find function prologues
    print("\n=== FUNCTION PROLOGUES ===")
    prologues = find_function_prologues(data, min_addr, max_addr)
    
    thumb_funcs = [p for p in prologues if p[0] == 'thumb_push_lr']
    arm_funcs = [p for p in prologues if p[0] == 'arm_stmdb_lr']
    
    print(f"  Thumb PUSH {{..., LR}}: {len(thumb_funcs)} functions")
    for ptype, addr, val in thumb_funcs:
        regs = []
        for bit in range(8):
            if val & (1 << bit):
                regs.append(f"R{bit}")
        regs.append("LR")
        print(f"    0x{addr:08X}: PUSH {{{', '.join(regs)}}}")
    
    print(f"\n  ARM STMDB SP!, {{..., LR}}: {len(arm_funcs)} functions")
    for ptype, addr, val in arm_funcs:
        print(f"    0x{addr:08X}: 0x{val:08X}")
    
    # Find strings
    print("\n=== ASCII STRINGS ===")
    strings = find_string_references(data, min_addr, max_addr)
    for addr, s in strings:
        print(f"  0x{addr:08X}: \"{s}\"")
    
    # Analyze code/data regions
    print("\n=== REGION ANALYSIS ===")
    regions = analyze_instruction_density(data, min_addr, max_addr)
    
    # Identify code vs data blocks
    in_code = False
    code_start = 0
    for addr, arm_d, thumb_d in regions:
        is_code = arm_d > 0.6 or thumb_d > 0.3
        if is_code and not in_code:
            code_start = addr
            in_code = True
        elif not is_code and in_code:
            size = addr - code_start
            mode = "ARM" if arm_d > thumb_d else "THUMB"
            print(f"  CODE  0x{code_start:08X} - 0x{addr:08X} ({size:5d} bytes, likely {mode})")
            in_code = False
    
    if in_code:
        print(f"  CODE  0x{code_start:08X} - 0x{max_addr:08X} ({max_addr - code_start:5d} bytes)")
    
    # Data region identification
    print("\n=== BYTE PATTERN ANALYSIS ===")
    # Look for repeating patterns (calibration data)
    zero_runs = 0
    ff_runs = 0
    for addr in range(min_addr, max_addr + 1):
        b = data.get(addr, 0)
        if b == 0:
            zero_runs += 1
        if b == 0xFF:
            ff_runs += 1
    
    print(f"  Zero bytes: {zero_runs} ({zero_runs*100/total:.1f}%)")
    print(f"  0xFF bytes: {ff_runs} ({ff_runs*100/total:.1f}%)")
    
    # Entropy-based analysis of 256-byte blocks
    print("\n=== BLOCK ENTROPY ===")
    import math
    for block_start in range(min_addr, max_addr, 256):
        block_end = min(block_start + 256, max_addr + 1)
        block_data = [data.get(i, 0) for i in range(block_start, block_end)]
        
        # Calculate entropy
        freq = [0] * 256
        for b in block_data:
            freq[b] += 1
        entropy = 0.0
        for f in freq:
            if f > 0:
                p = f / len(block_data)
                entropy -= p * math.log2(p)
        
        # Classify
        if entropy < 1.0:
            block_type = "ZERO/CONST"
        elif entropy < 3.0:
            block_type = "DATA/TABLE"
        elif entropy < 5.5:
            block_type = "CODE"
        else:
            block_type = "COMPRESSED/RANDOM"
        
        # Check for ASCII
        ascii_count = sum(1 for b in block_data if 0x20 <= b <= 0x7E)
        if ascii_count > len(block_data) * 0.5:
            block_type = "ASCII"
        
        bar = '#' * int(entropy * 3)
        print(f"  0x{block_start:08X}: entropy={entropy:.2f} [{bar:24s}] {block_type}")

if __name__ == '__main__':
    main()
