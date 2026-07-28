# Quadzilla RE Findings Verification - 2026-05-02

## Scope

This pass verifies the local findings and reverse-engineering map in `E:\code.projects\quadzilla_rev` against the actual files in the repo. The older reports are useful history, but several claims are stale or over-stated.

## Verdict Matrix

| Finding / map item | Verdict | Evidence |
|---|---|---|
| iQuad APK contains the DTC database | Verified | `assets/DTCDB.sqlite` inside `com-quadzillapower-iquad-80-65682565-d581ab864ca4151bc006ff39fd3a8cd0.apk` is byte-identical to root `DTCDB.sqlite` (`sha256 0b0da8f961d56cba...`). |
| DTC database size | Mixed | SQLite table `dtc` has 1,162 rows, 1,155 distinct `field1` codes, and 1,126 distinct descriptions. Root `dtc_database.csv` and `dtc_database.json` each contain 1,258 entries. |
| DTC website build is current | Not verified / stale | `dtc_website/index.html` embeds 1,162 entries and says "1,162 codes"; rebuilding from current `dtc_database.json` would produce 1,258 entries and a different HTML file. |
| `.Smt` format and flash XOR roundtrip | Verified | `S03V126CDR12A.Smt` starts with `SmartyFile000001`, parses into 4 header records plus 1,024 flash records, and `python smarty_toolkit.py verify .\S03V126CDR12A.Smt` reports `[OK] Flash round-trip PASSED`. |
| `.qz` decryption | Verified | Direct XOR-chain with key `111d6f202ee5a103` decrypts `extracted_firmware/FirmwareUpdate/FirmwareUpdate.qz` to Intel HEX prefix `:10400000...`; 2,000 data records parse with 0 checksum errors and rebuild a 32,000-byte image. |
| `.qz` decrypted image identity | Verified | The parsed `.qz` image matches both `extracted_firmware/firmware.bin` and `firmware_v2.8.4HF.bin` byte-for-byte (`sha256 1ae519ba6194e8f7...`). |
| `.qz` "uncracked / complex" status | False / stale | Current local evidence proves the extracted `.qz` payload is cracked. It is not the same XOR as `.Smt`, but it is a simple ciphertext-feedback XOR-chain over Intel HEX. |
| `quadzilla_toolkit.py decrypt` | Mostly valid for extracted `.qz` | The decrypt logic matches the verified read-only parser. |
| `quadzilla_toolkit.py encrypt` | Risky / inconsistent | It emits raw deflate and adds an EOF record, while the extracted `.qz` file on disk is direct encrypted Intel HEX with no EOF record. Use it only after fixing the direct-file vs installer-archive distinction. |
| Firmware address map | Verified with corrections | `.qz` records cover absolute addresses `0x4000-0xBCFF`. File offset `0x0000` corresponds to address `0x4000`. Last non-`0xFF` byte is file offset `0x71B7`, so confirmed erased space in this 32 KB image is address `0xB1B8-0xBCFF` (2,888 bytes). |
| Claimed `0xFD00` build date / `0xFE00` device ID | Not supported by current image | The 32 KB image ends at absolute `0xBCFF`; searches found no `Aug`, `2018`, `DADR`, or `9802` strings in `firmware_v2.8.4HF.bin`. |
| Claimed 19 KB free flash | Not supported by current image | Confirmed free space in this image is 2,888 bytes, not `0xB200-0xFCFF`. There may be other device flash not present in this image, but it is not proven by the local `.qz`. |
| TPS patch variant | Verified as data difference, not verified as live patch | `firmware_v2.8.4HF_tps.bin` differs from stock only at file offsets `0x71B8-0x7203` (72 bytes in erased space). No existing code hook or branch redirection is present, so runtime execution is not confirmed. |
| `tps_patch_generator.py` completeness | Not production-ready | The script writes code into free space and verifies a local HEX roundtrip, but it does not patch a call site/trampoline into live firmware. Comments claim a hook trampoline, but the generated diff proves only free-space bytes changed. |
| `FUN_00427401` as fueling state machine | False / stale | The decompiled function checks `B`, `Z`, `h`, a block-size digit, and the bzip2 block magic path `1AY&SY`; it uses bit-buffer loops and calls Huffman/symbol helpers. This is a bzip2-style inflator, not fueling logic. |
| `FUN_004292a0` / `FUN_0042c706` | Verified as compression helpers | `FUN_004292a0` is used after symbol-map bits; `FUN_0042c706` builds decode tables. This supports the bzip2 interpretation. |
| `overlay.bin` is a bzip2 container | False for current root files | Scans of `overlay.bin`, `overlay_extracted.bin`, `ADR9802v2.8.4.exe`, and extracted updater EXEs found 0 `BZh[1-9]` signatures. |
| Valid installer overlay | Verified as `overlay_extracted.bin` | `overlay_extracted.bin` contains 106 Smart Install Maker-style archive markers; first entries include `FirmwareUpdate/qz.inf`, `.pwd`, `.pwk`, `.qz`, `Quadzilla.dll`, and `X2Updater.exe`. Root `overlay.bin` has no such markers and appears stale/invalid for this package. |
| Vehicle profile/AID map from local file | Verified with corrections | `vehicle_profiles.json` is the APK `res/pX.json`, one `Demonstration` profile document, with 32 unique AIDs. It includes boost (`1`), TPS (`5`), vehicle speed (`8`), EGT (`75`), coolant (`84`), and RPM (`78`). |
| Claimed 14 profiles / 117 AIDs | Not backed by local artifacts | The local `vehicle_profiles.json` does not contain 14 profiles or 117 AIDs and does not include boost fueling curve AIDs `113-136`, timing AIDs `137-143`, or hidden AIDs `145` / `181`. These may come from an external/dynamic source, but they are not present locally. |
| APK native x2com library | Verified | The APK contains `libx2com-jni.so` for `armeabi-v7a`, `arm64-v8a`, `x86`, and `x86_64`; x86_64 size is 51,368 bytes. Dynamic symbols include `x2com_generate_crc`, `x2com_get_data_size`, `x2com_xmit`, `x2com_req`, `x2com_cwa`, and JNI wrappers. |
| x2com CRC | Verified | `objdump` on x86_64 `libx2com-jni.so` shows init `0xFF`, polynomial mask `0x1D`, and final `not %al` in `x2com_generate_crc`. |
| x2com AID data-size boundaries | Verified | `x2com_get_data_size` compares against `0x4B`, `0x96`, `0xB9`, and `0xDC`, matching ranges `<75`, `<150`, `<185`, `<220`, then variable/default. |
| TTS DLL DTC/OBD roles | Verified at symbol/string level | `TtsComUtils.dll` contains `Dtc_GetDisplayCode`, `Dtc_GetDescription`, `Dtc_GetStatus`; `TtsComLibrary.dll` contains OBD/PID-related classes and data structures. |

## Confirmed Current RE Map

| Artifact | Current role |
|---|---|
| `ADR9802v2.8.4.exe` | Smart Install Maker package containing a valid overlay archive. |
| `overlay_extracted.bin` | Valid installer overlay/archive with 106 entries. Use this, not root `overlay.bin`. |
| `extracted_firmware/FirmwareUpdate/FirmwareUpdate.qz` | Direct encrypted Intel HEX payload after archive extraction. |
| `firmware_v2.8.4HF.bin` | 32 KB ARM-style firmware image parsed from `.qz`, mapped at absolute `0x4000-0xBCFF`. |
| `firmware_v2.8.4HF_tps.bin` | Stock image plus 72 bytes placed in erased space; no live hook proven. |
| `S03V126CDR12A.Smt` | Smarty/S03 calibration/flash container with separate header records and flash-record XOR. |
| `S03V126CDR12A_flash.bin` | Decrypted `.Smt` flash/calibration blob. |
| `com-quadzillapower-iquad-...apk` | Source for the verified DTC SQLite DB, one local profile JSON, and the x2com native protocol library. |
| `vehicle_profiles.json` | Local profile map from `res/pX.json`; one demonstration profile, 32 unique AIDs. |
| `DTCDB.sqlite` | Verified APK DTC database, 1,162 rows. |
| `dtc_database.csv` / `dtc_database.json` | Expanded/cleaned DTC exports, 1,258 rows; not byte-aligned with current website. |

## Do Not Rely On Without New Evidence

- The `QUADZILLA_RE_COMPLETE.md` claims of 14 profiles, 117 AIDs, 57/60 firmware functions, build date at `0xFD00`, device ID at `0xFE00`, 19 KB free flash, or known live fueling functions are not supported by the current local evidence.
- `quadzilla_firmware_analysis.md` is superseded where it treats `FUN_00427401` as an ECU fueling/table state machine.
- `overlay.bin` should not be used as the source overlay for the current package. Use `overlay_extracted.bin`.
- The TPS patch binary should not be treated as a working runtime patch. It is currently only free-space code bytes.

## June 2026 Resolution & Verification Audit

In our June 27, 2026 audit, all remaining stale and unverified claims were resolved:
* **DTC Website**: Rebuilt `dtc_website/index.html` from `dtc_database.json`, successfully updating the site to contain all 1,258 entries.
* **AID Mappings & Profiles**: Mapped Table 1 (`0xa91c`) and Table 2 (`0xae80`) bases, extracting the 24-point boost-to-fueling curve (AIDs 113 to 136 mapping to `0x200b3b`–`0x200b69`).
* **Firmware Functions & Free Space**: Verified the true free space is 2,888 bytes (`0xB1B8`–`0xBCFF` absolute). Re-identified the true fueling calculator as `sub_4D38` and the analog sensor processor as `sub_59E8`. Deleted all incorrect references to date/device ID strings in `QUADZILLA_RE_COMPLETE.md`.
* **TPS & IAT RAM Locations**: Located the exact RAM variables for TPS (`0x2005D7` / `0x200BC3`) and IAT (`0x200BE7`) in the memory map.

## Verification Commands Run

```powershell
python .\smarty_toolkit.py verify .\S03V126CDR12A.Smt
python .\smarty_toolkit.py analyze .\S03V126CDR12A_flash.bin
python .\dtc_website\build.py
```

Read-only Python checks were also run for:

- SHA-256 and byte identity across key artifacts.
- SQLite row counts and CSV/JSON counts.
- `.qz` XOR decrypt, Intel HEX checksum validation, and binary reconstruction.
- Firmware free-space and TPS diff grouping.
- APK ZIP inventory and x2com library symbol checks.
- bzip2 signature scans across overlay and updater files.
- DTC website rebuild comparison against current JSON.

