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
| F5 | Selected device-side limits differ from the app's (AID 85 floor 800 vs 1200 us; timing 137-138 up to 30 deg vs 20/26) | Low | verified statically |

Full write-up with CWE mappings, reproduction commands, recommendations and what was *not* tested: **[docs/SECURITY_ASSESSMENT.md](docs/SECURITY_ASSESSMENT.md)**.

Supporting analysis:

- **Two-tool firmware audit:** IDA Pro 9.3 and Ghidra 11.3.2 independently reconciled to 145 execution entries in a 32,000-byte image, asserted by tests
  ([docs/FIRMWARE_AUDIT.md](docs/FIRMWARE_AUDIT.md)).
- **Reverse engineering report:** method, dead ends and open questions ([docs/REVERSE_ENGINEERING_REPORT.md](docs/REVERSE_ENGINEERING_REPORT.md)).
- **Technical reference:** memory map, X2com frames, USB opcodes, AIDs ([docs/TECHNICAL_REFERENCE.md](docs/TECHNICAL_REFERENCE.md)).

The [capture parser review](docs/CAPTURE_PARSER_REVIEW.md) completes the instruction account of `0x59E8`, adding 692 reviewed bytes without changing the 108/37 role count. Original-byte execution documents the receive state machine, nine header matches, exact scalar formulas, ignored DLC and an eight-bit narrowing discontinuity. DMA ordering, signal units and downstream consequences remain open.

The [control selector review](docs/CONTROL_SELECTOR_REVIEW.md) raises baseline coverage to 109 roles with 36 pending. It separates the mapped arithmetic byte from the AID 9 response and checks 70,672 original-byte calls, including wrap, zero-count and marker cases. Total classified instruction coverage is 8,900 bytes; the full analysis remains incomplete.

The [AID dispatch and selector-update review](docs/AID_DISPATCH_SELECTOR_UPDATES.md) maps all 256 validation destinations and checks AID 9/15 updates. It establishes count bounds of 5–14, derived mapping values and order-dependent results under a scripted receive contract. Reviewed instructions total 9,106 bytes, plus 436 explicitly classified switch-table bytes. The other 55 non-default handler accounts remain pending this review.

The [compound AID review](docs/COMPOUND_AID_UPDATE_REVIEW.md) adds eleven handler accounts, including five AIDs absent from the profiles. Original-byte evidence reproduces AID 154 consuming AID 146 staging after an earlier partial write, and a repeated 16-bit comparison/eight-bit store. Thirteen of 57 non-default handlers are reviewed, 44 remain pending, and instruction coverage is 9,564 bytes. Receive results are scripted; live transport and downstream effects remain unverified.

The [remaining local handler review](docs/REMAINING_AID_UPDATE_REVIEW.md) gives all 57 selected handlers bounded accounts and identifies four shared parent-frame entries. The [payload walker review](docs/PAYLOAD_WALKER_REVIEW.md) verifies variable counts and original receive admission, including a bounded AID 226 write to the separately used numeric status byte. The [frame reader review](docs/FRAME_READER_REVIEW.md) reconstructs table-2 response assembly and its conditional rejection-list stack write. The [outgoing queue filter review](docs/OUTGOING_QUEUE_FILTER_REVIEW.md) establishes its list subtraction and count behavior, including another conditional stack write for oversized direct calls. The [outgoing state review](docs/OUTGOING_STATE_REVIEW.md) traces priority, AID queue transitions, and USART submission. The [receive state review](docs/RECEIVE_STATE_REVIEW.md) traces all six incoming type branches and the byte-indexed jump table. The [queue state owner review](docs/QUEUE_STATE_OWNER_REVIEW.md) bounds a third queue and audits direct state-base references. The [cycle queue selection review](docs/CYCLE_QUEUE_SELECTION_REVIEW.md) identifies five initialized AID lists and traces their rotating submission. The [main-loop review](docs/MAIN_LOOP_STATE_REVIEW.md) traces the nonreturning reset continuation and its state dispatcher, narrowing the count-byte writer search. The [initial-state and configuration review](docs/INITIAL_STATE_CONFIG_REVIEW.md) traces persisted mode selection and a confirmed local AID 151 response-byte overwrite. The [ADC pipeline review](docs/ADC_PIPELINE_REVIEW.md) traces the source of the state-comparison word and classifies four contiguous lookup tables. The [ADC initializer and vector review](docs/ADC_INIT_VECTOR_REVIEW.md) traces the ADC channel setup, three startup literals, and a conditional vector-page write path. The [startup vector and clock review](docs/STARTUP_VECTOR_CLOCK_REVIEW.md) reconciles reset and exception paths, descriptor copies, oscillator and PLL setup, and fallback handlers. The [final baseline-entry review](docs/FINAL_BASELINE_ENTRIES_REVIEW.md) accounts for the installed spurious callback, a fixed-SRAM predicate, and the copied flash-ready helper. The [backdown and stretch review](docs/BACKDOWN_STRETCH_REVIEW.md) traces both candidate percentages, their AID 81/150 working inputs, the periodic AID 13 response writer, and signed-byte stretch arithmetic. The [main control structure review](docs/MAIN_CONTROL_STRUCTURE_REVIEW.md) reconciles its split code spans, 78 literal words, direct flow, and a conditional TC0 RC path under synthetic state. The [scalar telemetry review](docs/SCALAR_TELEMETRY_REVIEW.md) traces the five working knots and signed table path through `0x4D38`, including the main-loop telemetry cap and floor. The [capture scalar review](docs/CAPTURE_SCALAR_REVIEW.md) resolves two bounded byte jump tables, 24 AID-written curve slots, and a conditional telemetry copy in `0x4B38`. The [direct-caller table-bound review](docs/CAPTURE_TABLE_BOUNDS_REVIEW.md) proves both lookup indices stay in 0..19 and identifies the 20×20 initialized table. The [input gate state review](docs/INPUT_GATE_STATE_REVIEW.md) executes the AID-153 delay state machine and connects its completion event to the fresh accumulator path. The [USART/PDC execution review](docs/USART0_BUFFER_REVIEW.md) checks original staging, interrupt and initializer bytes under explicit register assumptions. The [residual code audit](docs/RESIDUAL_CODE_ADJUDICATION.md) reconciles division interworking, small wrappers, reset-request bytes, ratio tables and alignment. The [PC-literal audit](docs/PC_LITERAL_POOL_REVIEW.md) accounts for the last data candidates using raw load encodings and records a supported role for every image byte. All 145 original catalog entries now have evidence-backed roles; 19,000 instruction bytes are reviewed. The baseline catalog is not an exhaustive execution-entry inventory. Full protocol, all writer/consumer paths and hardware acceptance remain incomplete.

## Try it

Python 3.10+, standard library only (`pyserial` for the USB tool).

```bash
python -m unittest discover -s tests -t . -v     # offline tests, no vendor files needed
python tools/diff_profiles.py                     # 14 vendor profiles, 117 unique AIDs, QZTEST-only {145, 181}
python tools/x2com_crc.py                         # CRC-8/SAE-J1850 check value: 0x4B
python tools/aid_clamps.py                        # lexical clamp listing; use the linked handler reviews for exact behavior
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

The [capture helper review](docs/CAPTURE_HELPER_REVIEW.md) adds request selection, seven-slot rotation and unsigned byte comparison, bringing baseline coverage to 108 roles with 37 pending. Indexed request evidence extends the shared transmit-data table to 63 bytes; full capture parsing is covered by the subsequent parser review.

The [SPI/CAN command audit](docs/SPI_CAN_CONTROLLER_REVIEW.md) identifies an MCP2515-compatible controller protocol in the initialized commands, including receive-buffer layouts, seven extended request frames and TXB2 configuration. The owner's [V2.2 board component inventory](docs/BOARD_V2_2_COMPONENTS.md) reports U2 marked MCP2515 and records the MCU, analog components and unresolved markings. These reported observations corroborate the software interpretation; wiring, live CAN behavior and the installed firmware version remain unverified.

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
