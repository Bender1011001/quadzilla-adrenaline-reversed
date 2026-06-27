# Quadzilla / Smarty S03 Reverse Engineering

## Status
- **Verified 2026-06-27**: Live MCU fueling function map, including Table 1 (`0xa91c`) and Table 2 (`0xae80`), core fueling calculation (`sub_50F0` calling `sub_4D38`), and parameter validation/clamping (`sub_601C`).
- **Verified 2026-06-27**: Custom boost-to-fueling curve contains 24 points (AIDs 113 to 136) mapped to RAM variables `0x200b3b` to `0x200b69`.
- **Disproven/Corrected**: The build date `"Aug  2 2018"` and device ID `"DADR9802"` strings do NOT exist in `firmware_v2.8.4HF.bin`. The erased space is `0xB1B8-0xBCFF` (2,888 bytes).
- **Working**: DTC database extracted from the iQuad APK. SQLite has 1,162 rows; CSV/JSON exports have 1,258 rows.
- **Working**: dtc_website/index.html embeds all 1,258 entries and matches the JSON database exactly.
- **Working**: `.Smt` file structure mapped and flash XOR roundtrip verified.
- **Working**: `FirmwareUpdate.qz` from `extracted_firmware/FirmwareUpdate/` is cracked as direct encrypted Intel HEX using XOR-chain key `111d6f202ee5a103`; it rebuilds `firmware_v2.8.4HF.bin` exactly.
- **Working**: x2com native library symbols and core CRC/data-size boundaries verified from APK x86_64 `.so`.
- **Not Verified**: Working TPS runtime hook (no live hook proven).

## Key Files

### Extracted Data
- `DTCDB.sqlite` - SQLite DTC database (1,162 codes), extracted from iQuad APK
- `dtc_database.csv` - Clean/exported CSV (1,258 rows; not the same count as SQLite)
- `dtc_database.json` - JSON export for web use (1,258 rows)
- `vehicle_profiles.json` - Local APK `res/pX.json`: one Demonstration profile, 32 unique AIDs
- `dtc_website/index.html` - Searchable DTC lookup website, but currently stale vs JSON

### Firmware Files
- `S03V126CDR12A.Smt` - Smarty/S03 calibration/flash container; magic `SmartyFile000001`
- `S03V126CDR12A_flash.bin` - Decrypted `.Smt` flash/calibration blob
- `firmware_v2.8.4HF.bin` - ARM7TDMI firmware (32KB)
- `firmware_v2.8.4HF_tps.bin` - TPS patch variant (72 bytes different in erased space only; no live hook proven)
- `extracted_firmware/FirmwareUpdate/FirmwareUpdate.qz` - Encrypted Intel HEX payload (90KB), cracked and verified

### Software
- `SmartyUSB.exe` / `ADR9802v2.8.4.exe` - PC updater tools
- `DataMaster-BT.exe` - 11MB data display/monitoring tool
- `TtsComUtils.dll` - .NET DTC handling (Dtc_GetDisplayCode, Dtc_GetDescription)
- `TtsComLibrary.dll` - .NET OBD-II PID definitions
- `com-quadzillapower-iquad-*.apk` - Android app (contains DTCDB.sqlite)
- `overlay_extracted.bin` - Valid Smart Install Maker-style overlay archive with 106 entries
- `overlay.bin` - Stale/invalid for current package; no archive markers or bzip signatures found

## Architecture Quirks
- .Smt XOR key is 254 bytes, position-dependent (wraps per record)
- ARM firmware uses classic exception vector table at 0x00000000
- `.qz` firmware records are absolute `0x4000-0xBCFF`; file offset `0x0000` maps to address `0x4000`
- TPS patch occupies previously erased flash at file offsets `0x71B8-0x7203` / absolute `0xB1B8-0xB203`
- DTC descriptions are NOT in the firmware binary - they're in the app/DLL layer
- The `.qz` file encryption is NOT the same as the `.Smt` XOR; it is a separate 8-byte ciphertext-feedback XOR-chain
- `FUN_00427401` is a bzip2-style inflator in PC-side/updater code, not a proven ECU fueling state machine

## Trap Diary
| Issue | Cause | Fix |
|-------|-------|-----|
| DTCs not in .Smt file | .Smt contains ECM calibration data, not device firmware | Found in iQuad APK instead |
| DTCs not in firmware.bin | 32KB ARM firmware has LCD menu code, not DTC database | Database lives in app layer |
| `.qz` marked uncracked | Older context was stale | Use key `111d6f202ee5a103`; read-only verification rebuilt the 32KB image with 0 HEX checksum errors |
| `FUN_00427401` misread as fueling logic | It is a bzip2-style parser/decompressor | Do not use it as a fueling patch target |
| 14-profile / 117-AID claim | Not present in local `vehicle_profiles.json` | Treat as external/unverified until the source profiles are recovered |
| TPS patch assumed live | Only free-space bytes differ; no branch hook was patched | Treat `firmware_v2.8.4HF_tps.bin` as non-executing code unless a hook is added and verified |
| `quadzilla_toolkit.py encrypt` mismatch | It emits raw deflate plus EOF, while extracted `.qz` is direct encrypted HEX with no EOF | Fix before using for flashing/repacking |

## Anti-Patterns (DO NOT)
- Don't try to find DTC descriptions in the .Smt file - it only has ECM calibration data
- Don't assume the ARM firmware contains user-facing strings (it's too small at 32KB)
- Don't use the same XOR key from .Smt to decrypt the .qz file - different encryption
- Don't rely on `QUADZILLA_RE_COMPLETE.md` as current truth for profile count, AID count, firmware date/device strings, free-space size, or live fueling functions
- Don't treat `overlay.bin` as the valid current overlay; use `overlay_extracted.bin`
- Don't flash the TPS variant as a working feature without adding and verifying a real runtime hook
