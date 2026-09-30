# Reverse engineering report: Quadzilla Adrenaline

How the update package, firmware, protocol and parameter system were analysed, what worked, what did not, and what is still
open. Findings and severity are in [SECURITY_ASSESSMENT.md](SECURITY_ASSESSMENT.md); reference tables are in
[TECHNICAL_REFERENCE.md](TECHNICAL_REFERENCE.md).

## 1. Scope and approach

Four independent surfaces were attacked, each giving a cross-check on the others:

| Surface | Artifact | Yield |
|---|---|---|
| Windows updater | `ADR9802v2.8.4.exe` (self-extracting installer), `X2Updater`, `Quadzilla.dll` | container format, cipher, USB opcodes |
| Firmware package | `FirmwareUpdate.qz`, `.pwd`, `.pwk` | the 32 KB application image |
| Android app | iQuad (`com.quadzillapower.iquad`), 689 files | transport, parameter schema, vendor update URLs |
| Native library | `libx2com-jni.so` (4 ABIs) | frame format, CRC, state machine |

Method: extract, decode, then **verify with a second tool or a test before writing a claim down**. Where an earlier claim failed
verification it was corrected in place; the list is the errata table in the security assessment.

## 2. The update container

The installer is a self-extractor whose archive holds 106 entries, including `FirmwareUpdate.qz`, `.pwd`, `.pwk` and `Quadzilla.dll`.
The `.qz` is an Intel HEX file under a ciphertext-feedback XOR chain with an 8-byte key. The key is derived from the `.pwd` password by
`GeneratePasswordKey`, which uses a 256-entry table that proved to be the standard AES `Te0` table. Decrypted: 2,000 data records, 0 checksum
errors, image `0x4000`-`0xBCFF`. `tools/firmware_crypto.py` reproduces this end to end and recovers the key from ciphertext alone.

## 3. The firmware image

Hardware: ARM7TDMI, SAM7S-class. The image is ARM for the first 256 bytes (vectors, reset, mode switch) and Thumb thereafter, with literal pools
interleaved.

**The disassembly problem.** Ghidra's auto-analysis classified about 96 % of the image as data because it read literal pools as data and then refused to
disassemble around them. Approaches that failed, in order: setting Thumb mode before analysis (ignored by the analyzer); forcing Thumb on undefined
regions (there were none left); clearing and re-disassembling in place (Thumb/ARM context conflicts). What worked: clear everything, set Thumb mode on the clean
slate, then disassemble from each known entry with an address range capped at the next entry so one entry cannot absorb its neighbours
(`ghidra/scripts/ghidra_nuclear.py`). Entry points came from a prologue scan (`tools/analyze_binary.py`, looking for `PUSH {..., LR}`).

That produced the first-pass 57 decompiled functions. A later two-tool audit (IDA Pro 9.3 and Ghidra 11.3.2, independently) reconciled the union to
**145 execution entries** ([FIRMWARE_AUDIT.md](FIRMWARE_AUDIT.md)), so 57 was a hand-seeded subset.

**What the image contains** (audited roles only): the fueling calculation at `0x4D38`, the analog sensor processor at `0x59E8`, the AID table lookup and
multi-AID read/write routines around `0x7BF8`-`0x7D80`, and CAN handling. 2,888 bytes at `0xB1B8`-`0xBCFF` are erased.

## 4. X2com and the parameter system

`libx2com-jni.so` (x86_64 build, 51 KB) decompiles cleanly with symbols. It yields the frame format, six message types, the 14-AID frame limit, ACK/RESP
retransmit timers and the CRC. The CRC is CRC-8/SAE-J1850 (init `0xFF`, poly `0x1D`, final XOR `0xFF`), confirmed against the catalogue check value
`0x4B` and the repo's documented valid-frame residue `0x3B`.

Parameters ("AIDs") are addressed by number; width is fixed by range (1, 2, 3, 4 bytes, then variable). Across the 14 vendor profiles there are 117 unique
AIDs, including a 24-point fueling-versus-boost curve (113-136) and RPM timing entries (137-143). Two AIDs (145, 181) appear only in the vendor's internal
QZTEST profile. Whether each AID is honoured by the device, and whether the device clamps values itself, is **not established**.

## 5. The iQuad app

The APK's dex shows `BluetoothChatService` (from Google's sample) using secure RFCOMM sockets; there are no BLE/GATT API references. Class names
`QuadAttribute`, `VehicleDataSource`, `DashboardLayout` and `GaugeView` are present. `VehicleDataSource` fetches per-vehicle JSON from
`https://www.quadzillatech.com/iquadv2/update.json`; the profile fields (`minValue`, `maxValue`, `multiplyFactor`, `offset`, `warningValue`, ...) define the
UI's limits and scaling.

An earlier revision analysed the wrong file: a 20 MB `iquad.apk` that is the Aptoide store client. This was caught by comparing dex contents (8,419
Aptoide mentions and zero x2com mentions, against 1 x2com and 0 Aptoide in the real 2.9 MB APK).

## 6. What could be built on this (not implemented)

Nothing below has been built, flashed or tested on a device.

| Idea | Needs |
|---|---|
| Edit AID values over the phone link | a Bluetooth client speaking X2com; pairing behaviour unknown |
| Edit calibration tables in the image | a known-good update path; bootloader acceptance rules unknown |
| Add a small routine in the 2,888 free bytes | confirmed hook points; the audit labels only 14 of 145 entries |

Ideas from earlier notes that do not fit (a data logger, adaptive fuel learning, an OBD-II emulator) were based on a mistaken 19 KB free-flash figure.

## 7. Open questions

1. Does the on-device bootloader verify anything beyond the Intel HEX line checksums?
2. What pairing mode and PIN does the Bluetooth module use?
3. Does the firmware clamp AID writes independently of the app's limits?
4. Roles of the 131 unlabelled execution entries.
5. The X2com-over-USB framing needed to probe AIDs (`quadzilla_tool.py scan` is deliberately unimplemented).

## 8. Reproducing

```bash
python -m unittest discover -s tests -t . -v        # 24 tests, no vendor files needed
python tools/diff_profiles.py                        # 14 profiles, 117 unique AIDs, QZTEST-only {145, 181}
python tools/x2com_crc.py 41051022                   # frame CRC helper
# with your own copy of the vendor package:
python tools/firmware_crypto.py recover-key FirmwareUpdate.qz
python tools/firmware_crypto.py decrypt FirmwareUpdate.qz fw.hex --pwd-file FirmwareUpdate.pwd --bin fw.bin
```

The Ghidra scripts in `ghidra/scripts/` (`ghidra_decompile_all.py`, `ghidra_nuclear.py`, `ghidra_x2com.py`; the others are kept as the record of
earlier attempts) need Ghidra 11.3.2 and Java 17.

## 9. Lessons

- Do not iterate on a slow analysis tool (3-5 minutes per Ghidra run). Understand the binary with a fast script first, then write one tool run.
- For mixed-ISA firmware, feed entry points to the disassembler; do not trust auto-detection.
- A recognised constant is faster than tracing code: `0x1D` with init `0xFF` is a well-known CRC-8, and a check value settles it in one line.
- Reconcile counts across tools before stating them, and check which file an analysis actually ran on.
