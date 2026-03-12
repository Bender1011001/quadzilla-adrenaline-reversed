# Quadzilla Adrenaline Firmware Reverse Engineering

## Status
- **Working**: Decrypted Android APK extraction, Ghidra headless decompilation scripts, USB/BLE protocol mapping (AIDs mapped), CRC table identification.
- **Broken**: Remaining Phase 3 tasks blocked by lack of decrypted base firmware file and access to live hardware for dynamic analysis.

## Tech Stack
- Python 3.x (Ghidra headless scripts, protocol extractors)
- Ghidra (Reverse engineering and decompilation engine)
- Android APK decompilation tools

## Key Files
- `SmartyUSB.exe` / `ADR9802v2.8.4.exe` — The original manufacturer flashing and update tools.
- `quadzilla_custom_firmware_findings.md` — The comprehensive encyclopedia of parameters, BLE/USB communication signatures, and function mappings.
- `find_switch_statements.py` & `extract_dispatch_map.py` — Core Ghidra scripts for mapping the AID (Parameter) dispatch tables.
- `S03V126CDR12A.Smt` — Core payload file for parameter mapping.

## Architecture Quirks
- Ghidra Python scripts (`.py`) inside this repo are written specifically to be executed via Ghidra's **Headless Analyzer** or Script Manager, not standard Python interpreters.
- The firmware relies on obscure CRC matching and heavy switch-case statements for routing USB/BLE payloads (AIDs). 

## Trap Diary
- **Bzip2 Payloads**: Original firmware binaries are heavily obfuscated and packed with Bzip2 payloads internally. Standard hex extraction fails without aligning to the exact Bzip2 headers.
- **Missing decrypted overlay**: The final target firmware file remains encrypted/locked inside `overlay.bin` logic.

## Anti-Patterns (DO NOT)
- Do not attempt to run Ghidra scripts via `python script.py`. They must be executed within Ghidra's JRE context.
- Do not delete `quadzilla_custom_firmware_findings.md`, it contains all raw, unrecoverable hex address offsets found during static analysis.

## Build / Verify
No direct build available. Execution relies on Ghidra's headless mode (`analyzeHeadless.bat`) paired with the local `.gpr` files.
