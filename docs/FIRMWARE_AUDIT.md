# Firmware audit: two-disassembler cross-check

Scope: the 32,000-byte application image `firmware_v2.8.4HF.bin`, loaded at `0x4000`-`0xBCFF`
(SAM7S-class ARM7TDMI, mixed ARM/Thumb). SHA-256
`1ae519ba6194e8f7bdaaa94333a83a9e6fda3b0563f87f7d48383b37288c1780`. The image is the output of
`python tools/firmware_crypto.py decrypt ... --bin`, so every artifact below can be tied back to the
vendor's `.qz` update file. The image itself is not redistributed here.

The [capture parser review](CAPTURE_PARSER_REVIEW.md) completes entry `0x59E8`: all 315 added instruction boundaries match the IDA item export and explicit-mode Binary Ninja decode, and all are visited in original-byte controlled execution. At that stage, reviewed instruction bytes totaled 8,788 and baseline role coverage remained 108 with 37 pending. The subsequent [control selector review](CONTROL_SELECTOR_REVIEW.md) raises these to 8,900 bytes and 109 roles, with 36 pending; it accounts for two unreachable instruction starts explicitly.

The [validation dispatch review](AID_DISPATCH_SELECTOR_UPDATES.md) adds 206 reviewed instruction bytes and classifies the 436-byte signed-offset table, bringing instruction coverage to 9,106 bytes. All 256 selection destinations are checked; only the gate/loop and AID 9/15 handlers receive their update account here. Baseline role counts remain 109/36.

The [compound update review](COMPOUND_AID_UPDATE_REVIEW.md) adds 458 instruction bytes with all 227 starts matched and visited, bringing instruction coverage to 9,564 bytes. It reviews eleven more handlers and records specific cross-AID staging and width-loss paths. Baseline entry-role counts remain 109/36; 44 of 57 non-default handler accounts remain incomplete.

The [remaining-handler review](REMAINING_AID_UPDATE_REVIEW.md) adds 1,218 instruction bytes and four parent-frame continuation roles, bringing coverage at that stage to 10,782 instruction bytes and 113/32 baseline roles. The [payload walker review](PAYLOAD_WALKER_REVIEW.md) adds 500 reviewed bytes and confirms short-value admission and a bounded write to the numeric status byte. The [frame reader review](FRAME_READER_REVIEW.md) adds 404 instruction bytes, 36 literal-pool bytes, and one role. The [outgoing queue filter review](OUTGOING_QUEUE_FILTER_REVIEW.md) adds 126 instruction bytes and one role. The [outgoing state review](OUTGOING_STATE_REVIEW.md) adds 854 instruction bytes and one role; current coverage is 12,666 instruction bytes and 116/29 baseline roles. All 57 selected local update handlers now have bounded accounts; the dispatcher plus continuations total 1,882 reviewed instruction bytes. Full protocol and downstream behavior remain incomplete.

## Why

A single disassembler is not evidence. Ghidra's auto-analysis classified about 96 % of this firmware as data (Thumb
literal pools), and the first-pass function count of 57 (from a hand-seeded Ghidra run) turned out to be incomplete.
This audit asks two independent tools for their function starts and reconciles the disagreement byte by byte.

## Results

All numbers are asserted by `tests/test_firmware_audit.py` from `audit/data/`.

| Measure | Value |
|---|---|
| IDA Pro 9.3 function partitions | 122 |
| Ghidra 11.3.2 function partitions (`ARM:LE:32:v4t`, base `0x4000`) | 133 |
| Identical start addresses in both | 109 |
| Union of proposed starts | 146 |
| **Confirmed execution entries** | **145** |
| Rejected | 1 |
| Direct-call edges (IDA / Ghidra / both / union) | 136 / 159 / 115 / 180 |
| Shared starts with the same end / a different end | 88 / 21 |
| Critical VP44-chain functions recognised by both tools | 13 of 13 |

**Rejected:** IDA proposed a function at `0xAE82`. That address lies inside the second AID pointer table
(`0xAD18`-`0xB113`) and has no transfer, reference or literal-pointer evidence, so it is data.

**Confirmation** uses tool agreement, direct calls, control transfers, data references, literal pointers,
reset-vector reachability and ARM/Thumb interworking layout.

**Unit of count:** an *execution entry* includes reset vectors, thunks, alternate entries and interworking bodies.
It is not a count of original C functions, and the two tools still disagree on where 21 shared functions end.

### Semantic coverage, stated plainly

| | |
|---|---|
| Entries with an evidence-backed static role | 113 |
| Entries still unlabelled | 32 |

The 32 unlabelled entries are a work queue, not findings. Labels from the first-pass notes are treated as hypotheses
unless they appear in `audit/data/semantic_labels.json`.

The initial audit assigned 14 roles; the [offline write-path review](OFFLINE_WRITE_PATH_REVIEW.md)
adds seven from fresh IDA/Binary Ninja traces. The 145-entry inventory itself is unchanged.

The [USART0 buffer review](USART0_BUFFER_REVIEW.md) adds fifteen more roles,
bringing the baseline semantic total to 36. Six separately adjudicated source
starts are listed in the [startup review](STARTUP_PERSISTENCE_REVIEW.md); 145 is
the historical baseline count, not the complete supported minimum of 157.

Six division-runtime entry/body roles from the
[integer execution review](INTEGER_ARITHMETIC_REVIEW.md) brought the baseline total to 42 roles. Eight more entries from the
[control helper review](CONTROL_HELPER_REVIEW.md) bring that total to 50.
The [software floating point review](SOFT_FLOAT_REVIEW.md) adds 34 baseline
roles, yielding 84 with 61 pending.
The [configured ratio scorer review](DRIVETRAIN_SCORE_REVIEW.md) adds one
baseline role, yielding 85 with 60 pending.
The [PIOA and interrupt setup review](PIO_INTERRUPT_REVIEW.md) adds four
baseline roles, yielding 89 with 56 pending.
The [three-channel timer setup review](TIMER_SETUP_REVIEW.md) adds three
baseline roles, yielding 92 with 53 pending.
The [SPI setup review](SPI_SETUP_REVIEW.md) adds two baseline roles,
yielding 94 with 51 pending.
The [TC2 flag helper review](TC2_FLAG_HELPER_REVIEW.md) adds two baseline
roles, yielding 96 with 49 pending.
The [TC2 callback review](TC2_CALLBACK_REVIEW.md) adds the vector entry,
yielding 97 with 48 pending.
The [SPI/PDC primitive review](SPI_TRANSFER_REVIEW.md) adds six roles,
yielding 103 with 42 pending.
The [SPI output state review](SPI_STATE_MACHINE_REVIEW.md) adds one role,
yielding 104 with 41 pending.
The [SPI initialization review](SPI_INITIALIZATION_REVIEW.md) adds one role,
yielding 105 with 40 pending; it does not claim the complete capture parser is reviewed.
The [capture helper review](CAPTURE_HELPER_REVIEW.md) adds three roles,
yielding 108 with 37 pending.

### Peripheral map

All 136 peripheral references across 21 entries map to blocks of the official SAM7S address layout: USART0 35,
PIOA 40, AIC 29, ADC 11, SPI 6, timer/counter 6, PMC 6, reset controller 3. No reference is unmapped. Mapping a register
block does not by itself establish a function's purpose or direction.

The [SPI/CAN command audit](SPI_CAN_CONTROLLER_REVIEW.md) interprets initialized
SPI buffers using an MCP2515-compatible register layout. Those external
controller commands use the SPI block already counted above; physical part
identification and live CAN acceptance remain unverified.

## What this does not show

No live VP44 output, no working custom patch, no flash protocol and no bootloader behaviour. It is static evidence about
one application image.

## Reproduce

Regenerating the exports needs IDA Pro 9.3 and Ghidra 11.3.2; the reconciliation itself needs only Python.

```bash
# exports (licensed tools) -> audit/data/ida_function_map.json, ghidra_function_map.json
idat -A -S"audit/tools/ida_export_quadzilla.py" firmware_v2.8.4HF.bin.i64
# Ghidra: audit/tools/ghidra_scripts/SeedQuadzilla.java, then ExportQuadzilla.java

# reconcile and catalogue (Python only)
python audit/tools/compare_quadzilla_disassemblers.py --ida audit/data/ida_function_map.json \
  --ghidra audit/data/ghidra_function_map.json --image fw.bin --output /tmp/cross_disassembler_audit.json
python audit/tools/build_quadzilla_entry_catalog.py --audit audit/data/cross_disassembler_audit.json \
  --ida audit/data/ida_function_map.json --ghidra audit/data/ghidra_function_map.json \
  --labels audit/data/semantic_labels.json --output /tmp/execution_entry_catalog.json

# verify the committed numbers
python -m unittest tests.test_firmware_audit -v
```

The `--image` argument supplies the locally obtained image instead of relying on
the historical absolute path in an export. The IDA exporter also accepts explicit
`IMAGE OUTPUT` script arguments and checks database bytes against that image.

An additional [October 22 review](VERIFICATION_2026-10-22.md) records fresh IDA
traces and a catalog-seeded Binary Ninja check of 14 Thumb entries. That check
supports specific instruction traces; it does not replace this two-tool entry
inventory or constitute independent entry discovery.
