# Quadzilla Adrenaline Tuner - Reverse Engineering Findings

## Status Summary
**Current Stage**: Static analysis complete. Firmware extraction pending (requires EXE execution or live USB capture).

---

## Architecture Overview

### Communication Stack
```
[PC Software] <-- FTDI D2XX USB (FTD2XX.DLL) --> [Quadzilla Module MCU]
```
- **USB Interface**: FTDI chip providing virtual serial port via D2XX driver
- **14 FTDI API functions** used: CreateFile, CloseHandle, SetCommState, WriteFile, ReadFile, WaitCommEvent, SetupComm, ListDevices, GetCommState, SetCommMask, GetLastError, GetOverlappedResult, SetCommTimeouts, PurgeComm

### Software Components
| Component | Type | Size | Purpose |
|-----------|------|------|---------|
| `SmartyUSB.exe` | Delphi/C++ (CodeGear 2007) | 730KB | Smarty firmware flasher (reads .Smt files, writes to device) |
| `ADR9802v2.8.4.exe` | MSVC self-extractor | 1.6MB | Adrenaline firmware update package (encrypted) |
| `S03V126CDR12A.Smt` | Encrypted firmware | 4.3MB | Smarty firmware file (SmartyFile000001 format, 7.999 entropy) |

### Inside ADR9802v2.8.4.exe (Self-Extractor)
The EXE contains a proprietary self-extractor engine with **AES encryption support** (WinZip AES). The overlay at offset `0x58000` (1.27MB) contains **106 encrypted file entries**:

| # | File | Size (compressed) | Purpose |
|---|------|-------------------|---------|
| 0 | `FirmwareUpdate/qz.inf` | ~575 bytes | Configuration/manifest |
| 1 | `FirmwareUpdate/FirmwareUpdate.pwd` | ~32 bytes | Password file |
| 2 | `FirmwareUpdate/FirmwareUpdate.pwk` | ~32 bytes | Password key file |
| 3 | **`FirmwareUpdate/FirmwareUpdate.qz`** | **~70KB** | **MCU firmware payload** |
| 4 | `FirmwareUpdate/Quadzilla.dll` | ~13KB | DLL with tuning parameters |
| 5 | `FirmwareUpdate/X2Updater.exe` | ~82KB | Firmware updater application |
| 6 | `FirmwareUpdate/Working.exe` | ~13KB | Progress display |
| 7-88 | `quadzillaWorking0-81.bmp` | ~8KB each | Animation frames |
| 89-101 | `images/usb0-12.png` | ~29KB each | USB connection status images |
| 102 | `blank.bmp` | ~1KB | UI asset |
| 103 | `generic_pane.bmp` | ~12KB | UI asset |
| 104 | `FirmwareUpdate/setupWizard.exe` | ~50KB | Setup wizard |
| 105 | **`FirmwareUpdate/FirmwareUpdate.opt`** | **~53 bytes** | **Options/settings file** |

### Self-Extractor KV Config
```
setupFilename = FirmwareUpdate\X2Updater.exe
noInterface   = true
unzipToTemp   = true
```

---

## SmartyFile Format
The `.Smt` firmware file format supports multiple versions for different hardware:

| Header | Vehicle/Hardware |
|--------|-----------------|
| `SmartyFile000001` | Base format (our S03V126CDR12A.Smt uses this) |
| `SmartyFile000002` | Version 2 |
| `SmartyFile000003` | Version 3 |
| `SmartyFile000004` | Version 4 |
| `SmartyFile000005` | Version 5 |
| `SmartyFile000006` | Version 6 |
| `SmartyFile000007` | Version 7 |
| `SmartyFile000008` | Version 8 |
| `SmartyFile00POD4` | POD variant 4 |
| `SmartyFile0PODF4` | POD variant F4 |
| `SmartyFile00POD5` | POD variant 5 |
| `SmartyFile0S67US` | S67 US variant |
| `SmartyFile000J67` | J67 variant |
| `SmartyFile0J67US` | J67 US variant |

The S03V126CDR12A.Smt file has entropy of 7.999 bits/byte (maximum 8.0), indicating strong encryption or compression after the 16-byte header.

---

## Encrypted Data Analysis
- **45 base64-encoded blocks** in the EXE's `.rdata` section, all with header `73 86 9e 52`
- These appear to be **encrypted calibration/configuration data** (not bzip2 despite Ghidra showing bz2-like base64 text)
- Consistent sub-header pattern: `010969a0ccc50564` appears in all blocks
- Varying bytes at positions 4-7 may indicate parameter IDs or addresses

---

## Flash Process (from SmartyUSB.exe strings)
1. "Sending data, please wait"
2. "Verifying memory, please wait"
3. "%d minutes to complete upgrade" / "%d seconds to complete upgrade"
4. Success: "Transmission correctly performed to Smarty" / "OK on Smarty - "
5. Errors: "Flash verify error", "Error erasing memory", "Error sending data", "Error closing USB"

---

## Next Steps (Priority Order)

### 1. Run ADR9802v2.8.4.exe to Capture Decrypted Files
The self-extractor extracts to `%TEMP%` (`unzipToTemp=true`). Use `run_and_capture.py`:
```bash
python run_and_capture.py
```
This will launch the EXE and monitor temp for new files. Close the updater window when it appears. Captures go to `extracted/from_exe/`.

**High-value targets**: `FirmwareUpdate.qz`, `Quadzilla.dll`, `FirmwareUpdate.opt`, `X2Updater.exe`

### 2. USBPcap Live Capture
With the device connected, capture USB traffic during a firmware update:
```powershell
# List USB devices
& "C:\Program Files\USBPcap\USBPcapCMD.exe" --list-devices

# Capture on the relevant USB root hub
& "C:\Program Files\USBPcap\USBPcapCMD.exe" -d "\\.\USBPcap1" -o quadzilla_capture.pcap
```

### 3. Ghidra Analysis of Extracted Binaries
Once `Quadzilla.dll` and `X2Updater.exe` are extracted:
```powershell
# Analyze Quadzilla.dll (contains parameter definitions)
& "E:\tools\ghidra_11.3.2_PUBLIC\support\analyzeHeadless.bat" gh_tmp quadzilla_dll -import extracted/from_exe/FirmwareUpdate/Quadzilla.dll -overwrite -postScript ghidra_extract_info.py

# Analyze X2Updater.exe (contains USB protocol handlers)
& "E:\tools\ghidra_11.3.2_PUBLIC\support\analyzeHeadless.bat" gh_tmp x2updater -import extracted/from_exe/FirmwareUpdate/X2Updater.exe -overwrite -postScript ghidra_extract_info.py
```

---

## Tools Installed
- **Ghidra 11.3.2**: `E:\tools\ghidra_11.3.2_PUBLIC\`
- **USBPcap**: `C:\Program Files\USBPcap\USBPcapCMD.exe`
- **Java 17** (OpenJDK 17.0.16): Required for Ghidra
