# Quadzilla Firmware Reverse Engineering Analysis

## Project Overview

This document provides a comprehensive analysis of the Quadzilla firmware (`overlay.bin`) with the goal of modifying the fueling logic to support Throttle Position Sensor (TPS) based adjustments in addition to the current boost PSI-based tables.

## Executive Summary

**Target**: Quadzilla vehicle tuner firmware for PIC microcontroller  
**Primary Objective**: Enable CAN bus fueling adjustments based on TPS data  
**Key Function**: `FUN_00427401` - Main state machine for data processing  
**Architecture**: Data-driven state machine with compressed/encoded input streams  

---

## Step 1: Analysis of FUN_00427401 State Machine and Data Structures

### Function Overview

`FUN_00427401` is the core function that acts as a large, data-driven state machine. This function is responsible for processing compressed/encoded data streams and building configuration tables and fueling maps in memory.

### State Machine Structure

The function operates on a switch statement with `param_1[1]` as the state selector:

```c
switch(param_1[1]) {
    case 0x0A: // Initialize state, clear memory offsets
    case 0x0B: // Parse 'B' marker
    case 0x0C: // Parse 'Z' marker  
    case 0x0D: // Parse 'h' marker, allocate memory for data
    case 0x0E: // Parse data type indicators
    // ... continues through 0x32 (50 total states)
}
```

**Total States**: 41 cases (0x0A through 0x32)

### Memory Layout and Data Structures

#### Key Memory Offsets (in param_1 array):
- `param_1[0x3e85-0x3e9c]`: State preservation variables (18 variables)
- `param_1[0x313]`: Primary data allocation pointer (lines 200, 1095)
- `param_1[0x314]`: Secondary data allocation pointer (line 206)
- `param_1[0x315]`: Tertiary data allocation pointer (line 209)
- `param_1[0x316]`: Multi-byte value accumulator (lines 473, 495, 513, 531, 549)
- `param_1[0x317]`: Header/signature accumulator (lines 355, 1465, 1483, 1503)

#### Memory Allocation Pattern:
```c
// State 0x0D: Memory allocation based on data stream value
iVar13 = (**(code **)(iVar13 + 0x24))(*(undefined4 *)(iVar13 + 0x2c), 
                                     iVar10 * 400000, 1);  // Large allocation
param_1[0x313] = iVar13;

iVar10 = (**(code **)(iVar13 + 0x24))(*(undefined4 *)(iVar13 + 0x2c), 
                                      iVar10 * 200000);     // Medium allocation  
param_1[0x314] = iVar10;

iVar13 = (**(code **)(iVar13 + 0x24))(*(undefined4 *)(iVar13 + 0x2c), 
                                      param_1[9] * 100000 + 1 >> 1, 1); // Small allocation
param_1[0x315] = iVar13;
```

**Analysis**: The memory allocation sizes (400K, 200K, 100K) suggest these are large lookup tables, likely fueling maps with different dimensions and granularities.

### Data Structure Identification

#### 1. Multi-dimensional Lookup Tables
The function builds what appear to be 3D lookup tables:

```c
// Line 852: Table indexing pattern suggests RPM/Boost indexing
iVar13 = local_28 * 0x102 + local_8;
*(undefined1 *)(iVar13 + 0xab60 + (int)param_1) = (undefined1)local_24;
```

**Structure**: `table[boost_index][rpm_index] = fuel_value`
- `local_28`: Appears to be boost/pressure axis index
- `local_8`: Appears to be RPM axis index  
- `0x102`: Table stride (258 decimal) - suggests 256 RPM points + 2 metadata bytes
- `0xab60`: Base offset for fueling table storage

#### 2. Compression/Encoding Tables
```c
// Lines 878-885: Building Huffman-style lookup tables
FUN_0042c706(piVar17 + -0x60c, piVar17, (int)(piVar17 + 0x60c), 
             (int)local_54, (uint)param_1, (int)piVar18, local_44);
```

**Purpose**: `FUN_0042c706` builds encoding/decoding tables for compressed data streams.

#### 3. Symbol/Character Mapping Tables
```c
// Lines 1291-1299: Character frequency and mapping
pbVar22 = (byte *)(((uint)param_1 >> 0x18) + 0xd7c + (int)piVar7);
piVar7[*(byte *)(((uint)param_1 >> 0x18) + 0xd7c + (int)piVar7) + 0x10] =
     piVar7[*(byte *)(((uint)param_1 >> 0x18) + 0xd7c + (int)piVar7) + 0x10] + 1;
```

### Data Stream Processing

The state machine processes bit-level data streams:

```c
// Bit stream reading pattern (repeated throughout)
while (param_1[8] < 8) {  // Ensure 8 bits available
    param_1[7] = param_1[7] << 8 | (uint)*(byte *)*piVar12;  // Accumulate bits
    param_1[8] = param_1[8] + 8;  // Track bit count
    *piVar12 = *piVar12 + 1;      // Advance data pointer
}
```

**Analysis**: This is a sophisticated bit-stream parser, suggesting the input data is highly compressed.

### Helper Function Integration

#### FUN_004292a0 (Data Organization)
```c
// Called at line 683 after parsing table dimensions
FUN_004292a0((int)param_1);
```

From the decompiled code, this function:
- Organizes symbols into lookup tables
- Builds character-to-index mappings
- Prepares data for efficient table lookups

#### FUN_0042c706 (Table Builder)
```c
// Called at line 878-879 for each table dimension
FUN_0042c706(piVar17 + -0x60c, piVar17, (int)(piVar17 + 0x60c), 
             (int)local_54, (uint)param_1, (int)piVar18, local_44);
```

This function builds Huffman-style lookup tables for data decompression.

### Critical Observations for TPS Integration

1. **Table Structure**: The current system uses 2D tables indexed by [boost][rpm]
2. **Memory Allocation**: Large, fixed-size allocations suggest pre-determined table dimensions
3. **Data Compression**: Heavy use of compression indicates space constraints
4. **State Persistence**: State variables are preserved across calls, indicating incremental processing

### Next Steps for Analysis

The current fueling tables appear to be 2-dimensional (boost × RPM). To add TPS support, we would need to:

1. **Identify Current Table Access Patterns**: Find where these tables are read during normal operation
2. **Locate Sensor Input Processing**: Find CAN bus input handlers for current sensors
3. **Determine Table Lookup Logic**: Understand how boost and RPM values index into tables
4. **Plan 3D Table Extension**: Design how to add TPS as a third dimension

---

## Current Analysis Status

✅ **Completed**: Initial state machine structure analysis  
🔄 **In Progress**: Data structure mapping and memory layout  
⏳ **Next**: Cross-reference analysis to find table usage points
