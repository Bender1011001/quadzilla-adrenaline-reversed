# Technical reference

Facts about the Adrenaline update package, firmware image, USB/X2com protocol and parameter system. Each section
says where the fact comes from. For conclusions see [SECURITY_ASSESSMENT.md](SECURITY_ASSESSMENT.md).

## Hardware

| | |
|---|---|
| Model | Adrenaline `DADR9802`, firmware V2.8.4HF (`FirmwareUpdate.opt`) |
| MCU | ARM7TDMI, SAM7S-class (every peripheral reference in the image maps to the SAM7S address layout, see [FIRMWARE_AUDIT.md](FIRMWARE_AUDIT.md)) |
| Image | 32,000 bytes at `0x4000`-`0xBCFF`, SHA-256 `1ae519ba6194e8f7bdaaa94333a83a9e6fda3b0563f87f7d48383b37288c1780` |
| USB | CDC ACM, VID `0x1A18` PID `0x0002`, 921600 baud 8N1 |
| Phone link | Bluetooth Classic RFCOMM (not BLE), carrying X2com frames |
| Bus | CAN to the ECM/VP44 |

## Update package (`.qz`)

Keyed XOR chain over an Intel HEX file: `E[i] = P[i] ^ K[i % 8] ^ E[i-1]`. The key derives from an 8-byte password via a
256-entry table (AES `Te0`). The plaintext is 2,000 type-`00` records, 0 checksum errors, no EOF record, no signature.
Details and reproduction: [SECURITY_ASSESSMENT.md F1/F2](SECURITY_ASSESSMENT.md), `tools/firmware_crypto.py`.

## Memory map (application image)

```
0x4000-0x403F  ARM exception vectors (8 x branch)
0x4040-0x40FF  ARM startup: reset handler, stacks, switch to Thumb
0x4100-0x96FF  Thumb application code and literal pools
0x9700-0xB1B7  tables: AID pointer/size tables (0xA91C, 0xAE80), calibration data
0xB1B8-0xBCFF  erased (0xFF), 2,888 bytes
```

Source: IDA Pro audit of the decrypted image (June 2026). Earlier notes claimed a 48 KB part with ~19 KB free and
build-date/device-ID strings at `0xFD00`/`0xFE00`; none of that exists in the image.

## Functions

The authoritative inventory is the two-tool audit: 145 confirmed execution entries, 14 with an evidence-backed role
(`audit/data/semantic_labels.json`). The table lists entries of interest from the first-pass decompile
(`decompiled_firmware_full.c`); treat a role as a hypothesis unless the last column says audited.

| Address | Size | Role | Basis |
|---|---|---|---|
| `0x4D38` | 734 B | fueling calculation; writes final pump fueling value to RAM `0x200604` | audited (June 2026) |
| `0x59E8` | 722 B | analog sensor processing; TPS voltage to RAM `0x2005D7` | audited (June 2026) |
| `0x50F0` | 1,234 B | largest function, main control loop | first-pass label |
| `0x6C94` | 706 B | CAN message handler | first-pass label |
| `0x77B8` | 646 B | 2-D table interpolation | first-pass label |
| `0x601C` | 100 B (785 decompiled lines) | communication protocol switch | first-pass label |
| `0x5CF0` | 250 B | protocol state machine (5 states) | first-pass label |
| `0x7BF8` / `0x7C1C` / `0x7C68` | 34 / 54 / 54 B | AID to segment / RAM pointer / size | first-pass label |
| `0x7CC4` / `0x7D80` | 186 / 228 B | write / read multiple AIDs | first-pass label |
| `0x6B20`-`0x6B9C` | small | CAN controller init, ready check, transmit | first-pass label |

Known RAM locations: TPS `0x2005D7` (internal) and `0x200BC3` (AID 263), intake air temperature `0x200BE7` (AID 61), boost-fueling
curve AIDs 113-136 at `0x200B3B`-`0x200B69`.

### Disassembly caveat

The firmware mixes ARM (first 256 bytes) and Thumb (the rest) with literal pools between instructions. Ghidra's
auto-analysis marked about 96 % of it as data. The working approach: clear all code units, set Thumb mode, then disassemble each
known entry with an address range capped at the next entry to stop cascading (`ghidra/scripts/ghidra_nuclear.py`).
The two-tool audit then replaced hand-seeded entry lists with reconciled ones.

## X2com protocol

Frames on the phone link (and the same framing family over USB): `[type:4 | last_pos:4] + AID list/values + CRC-8`.
Source: decompile of `libx2com-jni.so` (x86_64, 62 functions). CRC-8/SAE-J1850, implemented in `tools/x2com_crc.py`.

| Type | Name | Direction | Meaning |
|---|---|---|---|
| 0 | CWA | app to tuner | write AIDs, wait for ACK |
| 1 | CMD | app to tuner | write AIDs, no ACK |
| 2 | ACK | tuner to app | acknowledgement |
| 3 | NOTIFY | tuner to app | unsolicited data (live gauges) |
| 4 | REQ | app to tuner | read AIDs, triggers RESP |
| 5 | RESP | tuner to app | values |

Up to 14 AIDs per frame; CWA/REQ split across frames above that; ACK and RESP timers retransmit. Value width is fixed by
AID range:

| AID range | Width |
|---|---|
| 0-74 | 1 byte |
| 75-149 | 2 bytes |
| 150-184 | 3 bytes |
| 185-219 | 4 bytes |
| 220+ | variable |

## USB update protocol

Recovered from the updater (`Quadzilla.dll`, `X2Updater.exe`); 11 opcodes. The lab copy of the DLL used for the original
decompile is damaged, so the table was not re-verified in the latest revision.

| Opcode | Name | Data |
|---|---|---|
| `0x00` | LINK_CHECK | reply `0x01` |
| `0x02` | DISCONNECT | |
| `0x03` | BOOTLOAD_MODE | mode |
| `0x04` | MODULE_INFO | reply 25 bytes |
| `0x06` | KEY_TRANSFER | 8-byte key |
| `0x07` | DATA_TRANSFER | length + 61 bytes |
| `0x0B` | XFER_COMPLETE | |
| `0x0D` | SN_PROGRAM | 8-byte serial |
| `0x0E` | FEATURE_CODE | op + 8-byte code |
| `0x10` | ABORT | |
| `0x11` | FEATURE_READ | reply count + data |

Flash sequence: LINK_CHECK, MODULE_INFO, BOOTLOAD_MODE, KEY_TRANSFER, DATA_TRANSFER (repeated), XFER_COMPLETE, DISCONNECT.
`tools/quadzilla_tool.py` implements only LINK_CHECK, MODULE_INFO, FEATURE_READ and DISCONNECT.

## AIDs

117 unique AIDs are declared across the 14 vendor profiles in `vehicles/` (`python tools/diff_profiles.py`). AIDs 145 and 181
(AVG MPG reset / Average MPG) appear only in the vendor's internal "Quadzilla Only" (QZTEST) profile. 110 AID numbers in 0-226
appear in no profile. Catalogue: [AID_REFERENCE.md](AID_REFERENCE.md).
