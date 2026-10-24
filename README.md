# Quadzilla Adrenaline: firmware and protocol security analysis

[![tests](https://github.com/Bender1011001/quadzilla-adrenaline-reversed/actions/workflows/ci.yml/badge.svg)](https://github.com/Bender1011001/quadzilla-adrenaline-reversed/actions/workflows/ci.yml)
[![license: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

Static security analysis of the **Quadzilla Adrenaline** (DADR9802), an aftermarket inline tuner for 1998.5-2002 Dodge Ram 5.9 Cummins trucks. It sits between the
ECM and the VP44 injection pump and changes fuel quantity and timing in real time, so an unauthorised write to it can damage an engine.

The work covers the firmware update package, the ARM7 firmware image, the iQuad Android app and its native protocol library, and the vendor's parameter profiles.
The repository includes reproduction scripts and offline tests; some claims still depend on separately obtained vendor artifacts and licensed analysis tools. Claims that could not be verified are labelled, and corrections to earlier versions of this
repository are listed in the [errata](docs/SECURITY_ASSESSMENT.md#errata-corrections-made-to-earlier-claims-in-this-repository).

## Results

| # | Finding | Severity | Evidence |
|---|---|---|---|
| F1 | "Encrypted" firmware is a keyed XOR chain; password, key and algorithm ship in the installer; key recoverable from 8 bytes of known plaintext | Low | verified |
| F2 | Update package has no signature, MAC or hash, only Intel HEX line checksums | Medium (potential) | verified for package; device check untested |
| F3 | Phone link is Bluetooth **Classic** RFCOMM with no app-level pairing or crypto | Info | verified; pairing strength untested |
| F4 | X2com control protocol has no authentication, nonce or encryption; CRC-8/SAE-J1850 only | Medium | verified statically |
| F5 | The device clamps most values, but its limits differ from the app's (AID 85 floor 800 vs 1200 us; timing 137-138 up to 30 deg vs 20/26) | Low | verified statically |

Full write-up with CWE mappings, reproduction commands, recommendations and what was *not* tested: **[docs/SECURITY_ASSESSMENT.md](docs/SECURITY_ASSESSMENT.md)**.

Supporting analysis:

- **Two-tool firmware audit:** IDA Pro 9.3 and Ghidra 11.3.2 independently reconciled to 145 execution entries in a 32,000-byte image, asserted by tests
  ([docs/FIRMWARE_AUDIT.md](docs/FIRMWARE_AUDIT.md)).
- **Reverse engineering report:** method, dead ends and open questions ([docs/REVERSE_ENGINEERING_REPORT.md](docs/REVERSE_ENGINEERING_REPORT.md)).
- **Technical reference:** memory map, X2com frames, USB opcodes, AIDs ([docs/TECHNICAL_REFERENCE.md](docs/TECHNICAL_REFERENCE.md)).

## Try it

Python 3.10+, standard library only (`pyserial` for the USB tool).

```bash
python -m unittest discover -s tests -t . -v     # offline tests, no vendor files needed
python tools/diff_profiles.py                     # 14 vendor profiles, 117 unique AIDs, QZTEST-only {145, 181}
python tools/x2com_crc.py                         # CRC-8/SAE-J1850 check value: 0x4B
python tools/aid_clamps.py                        # device-side value clamps for 57 AIDs vs the app's limits
```

With your own copy of the vendor update package (not included):

```bash
python tools/firmware_crypto.py recover-key FirmwareUpdate.qz          # key from ciphertext alone
python tools/firmware_crypto.py decrypt FirmwareUpdate.qz fw.hex --pwd-file FirmwareUpdate.pwd --bin fw.bin
# expected image SHA-256: 1ae519ba6194e8f7bdaaa94333a83a9e6fda3b0563f87f7d48383b37288c1780
python -m unittest tests.test_firmware_audit -v                        # audit numbers vs the committed data
```

Latest review: [October 22 verification](docs/VERIFICATION_2026-10-22.md) covers strict firmware parsing, fresh IDA/Binary Ninja checks and remaining limits.

The subsequent [offline write-path review](docs/OFFLINE_WRITE_PATH_REVIEW.md) traces receive → staging → validation → control, corrects the 14-byte frame budget, and expands semantic coverage to 21 of 145 entries. It includes a bounded ingest model and the complete remaining review queue.

**Full firmware analysis is ongoing.** The [coverage ledger and progress report](docs/FULL_ANALYSIS_PROGRESS.md) identify relocated SRAM code and additional entry candidates beyond the original catalog. The 145-entry figure is a starting inventory, not an exhaustive count of execution entries or runtime addresses.

The [startup and persistence review](docs/STARTUP_PERSISTENCE_REVIEW.md) supports six additional source entries (at least 151 total), reconstructs exception dispatch and SRAM helpers, and identifies the startup attempt to set the MCU security bit. Installed hardware state remains unmeasured.

The [USART0 buffer review](docs/USART0_BUFFER_REVIEW.md) expands the baseline to 36 semantic roles, leaving 109 baseline entries unlabeled. It traces DMA and frame parsing, identifies queue-full behavior, and models the conditions under which a reused short-receive buffer can retain a CRC-valid suffix.

The [integer execution review](docs/INTEGER_ARITHMETIC_REVIEW.md) brings baseline coverage to 42 roles, with 103 pending. It executes the real division and stretch-arithmetic bytes in an offline ARM emulator, establishes remainder/quotient register conventions, and checks exceptional values, staged rounding and signed-cell assumptions.

The [AID table boundary review](docs/AID_TABLE_BOUNDARY_REVIEW.md) maps both resolvers over all 256 AID bytes. AID 255 indexes past each 255-slot table: original-helper execution reproduces a write alias and an invalid response read. Hardware effects and complete transport reachability remain untested.

The [control helper review](docs/CONTROL_HELPER_REVIEW.md) expands baseline coverage to 50 roles, leaving 95 pending. It checks filtering, normalization, defaults, persistent latches and a fresh-sample accumulator with 12,921 offline calls of the original helpers.

The [software floating point review](docs/SOFT_FLOAT_REVIEW.md) expands the baseline to 84 labeled roles with 61 pending and supports at least 157 source starts. It records 30,627 original-byte offline calls, including reproducible subnormal division errors and a binary64 addition path that depends on incoming R4. Decoder gaps and unverified live reachability remain explicit.

The [configured ratio scorer review](docs/DRIVETRAIN_SCORE_REVIEW.md) raises baseline coverage to 85 roles with 60 pending. An original-byte trace shows that candidate scores are narrowed to one byte before comparison: a computed score of 512 becomes zero. The caller's input units and any live effect remain unresolved.

The [PIOA and interrupt setup review](docs/PIO_INTERRUPT_REVIEW.md) documents four more entries, bringing baseline coverage to 89 roles with 56 pending. It records the exact PMC/PIO/AIC write sequence and bounded source-2 callback behavior using synthetic registers; subordinate setup routines and physical pin behavior remain open.

The [three-channel timer setup review](docs/TIMER_SETUP_REVIEW.md) documents the timer coordinator and two short callbacks, bringing baseline coverage to 92 roles with 53 pending at that stage. It records conditional compare values, clock and interrupt setup writes, and the limits of synthetic register execution. The third callback is reviewed below; live timing remains open.

The [SPI setup review](docs/SPI_SETUP_REVIEW.md) documents the following setup call and its no-op source-5 callback, bringing baseline coverage to 94 roles with 51 pending. It records the eleven ordered register writes and literal-pool provenance; live SPI transfers and IRQ handling remain open.

The [TC2 flag helper review](docs/TC2_FLAG_HELPER_REVIEW.md) documents two small callbacks invoked from the larger TC2 routine, bringing baseline coverage to 96 roles with 49 pending at that stage. Their exact SRAM flag writes and trigger sites support the full callback review below.

The [TC2 callback review](docs/TC2_CALLBACK_REVIEW.md) now covers that larger vector routine itself, bringing baseline coverage to 97 roles with 48 pending. Fifty controlled cases visit all 333 decoded instruction starts and document its counter transitions and gated numeric updates; live timing and upstream value units remain unresolved.

The [SPI/PDC primitive review](docs/SPI_TRANSFER_REVIEW.md) adds six GPIO, readiness and buffer-programming roles, bringing baseline coverage to 103 roles with 42 pending. It records exact register-write order, gate outcomes and an IDA boundary correction; higher-level transfer/timeout flows remain under review.

The [SPI output state review](docs/SPI_STATE_MACHINE_REVIEW.md) adds the four-state caller and payload packing, bringing baseline coverage to 104 roles with 41 pending. It records progress after ignored helper results and signed packing behavior as controlled findings requiring caller and hardware context.

The [SPI initialization review](docs/SPI_INITIALIZATION_REVIEW.md) adds the 24-step setup sequence and its shared timeout/reset path, bringing baseline coverage to 105 roles with 40 pending. It also records the reset-only capture-entry path and identifies nine directly referenced image bytes as transmit data.

## Layout

```
docs/    SECURITY_ASSESSMENT.md  findings, errata        FIRMWARE_AUDIT.md   two-tool cross-check
         REVERSE_ENGINEERING_REPORT.md                   TECHNICAL_REFERENCE.md   AID_REFERENCE.md
         RE_VERIFICATION_2026-05-02.md  earlier audit    archive/   superseded notes, kept as a record
tools/   firmware_crypto.py  x2com_crc.py  diff_profiles.py  quadzilla_tool.py (read-only USB subset)  analyze_*.py
audit/   data/ (IDA + Ghidra exports, reconciliation)   tools/ (export and reconcile scripts)
ghidra/  scripts used for the first-pass decompile
tests/   unit tests (crypto, CRC, profiles, audit numbers)
vehicles/  14 vendor profile JSONs     decompiled_*.c  decompiler output (see NOTICE.md)     analysis/  working notes and scratch scripts
```

## Methodology and AI assistance

The analysis was done with AI coding assistants (Claude and Codex) working under the repository owner's direction on hardware and files the owner supplied.
Nothing is accepted on an assistant's say-so: a result stays only if a script, a test, or a second independent tool reproduces it, and several earlier
claims did not survive that check (see the errata). The two-disassembler audit and the test suite exist for that reason.

## Scope and responsible use

Independent research on a product the author owns. No vendor binaries, installers, firmware images or APKs are included (`.gitignore` blocks them); see
[NOTICE.md](NOTICE.md) for what is and is not in the tree. No modified firmware has been flashed and no radio traffic was captured. No vendor contact is
recorded here. Changing fuel or timing on a diesel can destroy an engine and may be illegal for road use; nothing here is a tuning guide.

## License

MIT for original work ([LICENSE](LICENSE)). Decompiler output, vendor profile JSON and derived analysis artifacts remain the property of their owners and are
included for analysis and interoperability documentation only.
