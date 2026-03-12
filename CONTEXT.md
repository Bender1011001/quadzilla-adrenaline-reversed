# Quadzilla Adrenaline Firmware Reverse Engineering

## Status
- **Working**: Firmware decryption/encryption, basic USB comms, AID database (117 mapped), binary analysis
- **In Progress**: Full decompilation of all 50+ functions (need Ghidra GUI for remaining 30)
- **Broken**: Nothing critical

## Tech Stack
- MCU: ARM7TDMI (AT91SAM7S or similar), 48KB flash  
- ISA: Mixed ARM (startup) + Thumb (application code)
- Firmware: Intel HEX, XOR cipher-chain encrypted
- Build: Aug 2 2018, Device ID: DADR9802
- Tools: Python 3.x, Ghidra 11.3.2 (Java 17), Jython 2.7

## Memory Map
```
0x4000-0x403F  ARM interrupt vectors (8 vectors, ARM branch instructions)
0x4040-0x40FF  ARM startup code (reset handler, IRQ, mode switching)
0x4100-0x96FF  Thumb application code + literal pools (~22KB)
0x9700-0xB200  Calibration tables / lookup data (~7KB)  
0xB200-0xFCFF  Zero-fill padding (~19KB unused flash)
0xFD00-0xFD0A  Build date string "Aug  2 2018"
0xFE00-0xFE07  Device ID string "DADR9802"
0xFF00         End of firmware
```

## Key Files
- `tools/firmware_crypto.py`     — Decrypt/encrypt firmware (XOR cipher-chain)
- `tools/quadzilla_tool.py`      — USB serial comms, AID probing
- `tools/diff_profiles.py`       — Profile comparison, 117 AIDs mapped
- `docs/QUADZILLA_RE_COMPLETE.md` — Full RE writeup from AI perspective
- `docs/AID_REFERENCE.md`        — Complete parameter database (117 AIDs)
- `ghidra/scripts/ghidra_decompile_all.py` — The Ghidra script that works
- `analyze_binary.py`      — Raw binary analysis (entropy, prologues, strings)
- `decompiled_firmware_full.c` — 19 decompiled C functions (~17KB)
- `ghidra_nuclear.py`      — Best Ghidra script (clear+thumb+disassemble+decompile)

## Function Map (60 total, 57 decompiled to C — 125KB)

### Top Functions by Size (all decompiled)
| Address | Size | Lines | Name/Purpose |
|---------|------|-------|-------------|
| 0x50F0 | 1234 | 320 | **MAIN CONTROL LOOP** — largest function |
| 0x81A8 | 854 | 204 | Large processing / computation |
| 0x4D38 | 734 | 230 | Parameter/table processing |
| 0x59E8 | 722 | 206 | **FUEL/TIMING CALCULATION** |
| 0x6C94 | 706 | 265 | **CAN MESSAGE PROCESSING** |
| 0x77B8 | 646 | 187 | Data/map interpolation |
| 0x575C | 622 | 136 | Vehicle profile handler |
| 0x4384 | 530 | 176 | Init/config |
| 0x4B38 | 290 | 206 | Calibration table processing |
| 0x5CF0 | 250 | 96 | Protocol state machine (5 states) |
| 0x4214 | 238 | 69 | Peripheral initialization |
| 0x7D80 | 228 | 74 | AID_ReadMulti (pack response) |
| 0x76CC | 218 | 81 | Timer/PWM output control |
| 0x46D0 | 192 | 67 | ADC/sensor data acquisition |
| 0x7CC4 | 186 | 69 | AID_WriteMulti |
| 0x74E8 | 176 | 56 | CAN RX processing |
| 0x5E04 | 156 | 59 | Frame encode (opcodes 0x30/40/50) |
| 0x4A94 | 146 | 54 | Math/interpolation |
| 0x506C | 112 | 54 | Sensor processing |
| 0x8038 | 110 | 90 | Timing calculation |
| 0x8A50 | 108 | 50 | Interrupt handler |
| 0x601C | 100 | 785 | Comm protocol (large switch) |

### Utility Functions (all decompiled)
| Address | Size | Purpose |
|---------|------|---------|
| 0x7C1C | 54 | AID → RAM pointer (4-segment table) |
| 0x7C68 | 54 | AID → data size pointer |
| 0x7BF8 | 34 | AID → segment # (1-4) |
| 0x6B9C | 54 | CAN TX with ID setup |
| 0x6B64 | 40 | CAN TX data only |
| 0x6B48 | 24 | CAN controller ready check |
| 0x6B8C | 16 | CAN TX complete check |
| 0x8530 | 26 | memcpy |
| 0x854C | 22 | memset |
| 0x5EBC | 54 | Power level cycle (0-6) |
| 0x571C | 26 | PIO output set |
| 0x4114 | 48 | ROM→RAM init tables |

## AID Subsystem Architecture
```
AID 0-74   → Segment 1 (base at DAT_00007c54, 75 × 4 = 300 bytes)
AID 75-149 → Segment 2 (base at DAT_00007c58 + offset DAT_00007cb4)
AID 150-184 → Segment 3 (base at DAT_00007c60 + offset DAT_00007cbc)
AID 185-219 → Segment 4 (base at DAT_00007c64 + offset DAT_00007cc0)
```

## Architecture Quirks
- Firmware is Thumb mode but Ghidra auto-analysis classifies 96% as data (literal pools confuse it)
- Need to clear all code units, set TMode=1, then disassemble from each known entry point
- Functions end with jump tables (POP PC from variable register set) — Ghidra shows as UNRECOVERED_JUMPTABLE
- ARM startup code at 0x4000-0x40FF transitions to Thumb via BX R0

## Trap Diary
| Issue | Cause | Fix |
|-------|-------|-----|
| Ghidra finds only 20 functions | Literal pools between Thumb inst classified as data | Use ghidra_nuclear.py: clear all → set TMode → disassemble from known entry points |
| Pre-script TMode ignored | Auto-analyzer doesn't respect manually set TMode | Use pre-import script (-preScript flag) |
| ContextChangeException | Can't change TMode on addresses with existing instructions | Clear all code units first with listing.clearCodeUnits() |
| Jython encoding error | Non-ASCII in .py file | Add # -*- coding: utf-8 -*- header |
| CreateFunctionCmd size=1 | Cascading disassembly from one entry covers multiple functions | Need CreateFunctionCmd AFTER disassembly runs separately for each entry |

## Anti-Patterns (DO NOT)
- Do NOT run Ghidra auto-analysis on this firmware without pre-setting TMode=1
- Do NOT use ARM mode for anything after address 0x4100 — it's all Thumb
- Do NOT expect function boundaries from auto-detection — must use known prologue addresses
- Do NOT delete the `ghidra_project/` directory without re-creating via fresh import

## Build / Verify
```bash
# Decrypt firmware
python firmware_crypto.py decrypt input.hex output_decrypted.hex

# Analyze binary
python analyze_binary.py

# Run Ghidra analysis
E:\tools\ghidra_11.3.2_PUBLIC\support\analyzeHeadless.bat ghidra_project QuadzillaFW -process "FirmwareUpdate_decrypted.hex" -noanalysis -postScript ghidra_nuclear.py -scriptPath .
```

## X2com BLE Protocol Specification (Reverse-Engineered)

### Source
Decompiled from `libx2com-jni.so` (x86_64, 51KB) → 62 functions, 224KB C code

### Frame Format
```
Byte 0: [msg_type:4 | last_pos:4]
  - Upper nibble: message type (0-5)
  - Lower nibble: index of last data byte (max 14)
Bytes 1..N: AID list + data payload
Byte N+1:   CRC-8 checksum
```

### Message Types
| Type | Name   | Description |
|------|--------|-------------|
| 0    | CWA    | Command With Acknowledgment (write AIDs + wait for ACK) |
| 1    | CMD    | Command (write AIDs, no ACK) |
| 2    | ACK    | Acknowledgment response |
| 3    | NOTIFY | Notification (unsolicited data push) |
| 4    | REQ    | Request (read AIDs → triggers RESP) |
| 5    | RESP   | Response to REQ |

### CRC-8 Algorithm
- Polynomial: 0x1D (x^8 + x^4 + x^3 + x^2 + 1)
- Init: 0xFF
- Processing: bit-by-bit MSB→LSB, Galois LFSR
- Final: bitwise invert (~crc)
- Check value: 0x3B (valid CRC over msg+crc == ';')

### AID Data Sizes (fixed by range)
| AID Range | Size | Storage |
|-----------|------|---------|
| 0 - 74    | 1 byte | one_byte_rx_p / one_byte_tx_p |
| 75 - 149  | 2 bytes | two_byte_rx_p / two_byte_tx_p |
| 150 - 184 | 3 bytes | three_byte_rx_p / three_byte_tx_p |
| 185 - 219 | 4 bytes | four_byte_rx_p / four_byte_tx_p |
| 220+      | variable | var_byte_rx_p / var_byte_tx_p |

### JNI API (BluetoothChatService native methods)
```
X2comInit()               → void     // Initialize protocol state
X2comCmd(byte[] aids, byte count) → boolean  // Send CMD (type=1)
X2comCwa(byte[] aids, byte count) → boolean  // Send CWA (type=0)
X2comReq(byte[] aids, byte count) → boolean  // Send REQ (type=4)
X2comRcv(byte[] buf, byte[] out)  → int      // Process received frame
X2comHandleAck()          → void     // ACK timeout handler
X2comHandleResp()         → void     // RESP timeout handler
X2comHandleXmit()         → int      // Process TX queue
getAID(int aid)           → byte[]   // Read single AID value
setAID(int aid, byte[] data) → boolean // Write single AID value
```

### Protocol State Machine
- Max 14 AIDs per frame
- CWA/REQ support multi-part: splits >14 AIDs across multiple frames
- ACK timer: started after CWA TX, retransmit if timeout
- RESP timer: started after REQ TX, retransmit if timeout  
- Double-buffered RX (rx_buffer0/rx_buffer1, active_buffer flag)

### Key Internal Functions
| Function | Purpose |
|----------|---------|
| x2com_build_msg(buf, type, data, count) | Build frame: set header, pack data, append CRC |
| x2com_parse_msg(buf, type_out, data, count) | Parse frame: extract type, unpack AID data |
| x2com_generate_crc(buf, len) | Compute CRC-8 over buffer |
| x2com_check_crc(buf, last_pos) | Verify CRC (returns 3 if valid) |
| x2com_get_data_size(default, aid) | Get byte width for AID by range |
| x2com_find_rx_storage / x2com_find_tx_storage | Look up storage buffer for AID |
| x2com_set_msg_data / x2com_get_msg_data | Pack/unpack AIDs+values into frame |
