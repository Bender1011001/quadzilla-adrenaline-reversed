# Firmware audit: two-disassembler cross-check

Scope: the 32,000-byte application image `firmware_v2.8.4HF.bin`, loaded at `0x4000`-`0xBCFF`
(SAM7S-class ARM7TDMI, mixed ARM/Thumb). SHA-256
`1ae519ba6194e8f7bdaaa94333a83a9e6fda3b0563f87f7d48383b37288c1780`. The image is the output of
`python tools/firmware_crypto.py decrypt ... --bin`, so every artifact below can be tied back to the
vendor's `.qz` update file. The image itself is not redistributed here.

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
| Entries with an evidence-backed static role | 50 |
| Entries still unlabelled | 95 |

The 95 unlabelled entries are a work queue, not findings. Labels from the first-pass notes are treated as hypotheses
unless they appear in `audit/data/semantic_labels.json`.

The initial audit assigned 14 roles; the [offline write-path review](OFFLINE_WRITE_PATH_REVIEW.md)
adds seven from fresh IDA/Binary Ninja traces. The 145-entry inventory itself is unchanged.

The [USART0 buffer review](USART0_BUFFER_REVIEW.md) adds fifteen more roles,
bringing the baseline semantic total to 36. Six separately adjudicated source
starts are listed in the [startup review](STARTUP_PERSISTENCE_REVIEW.md); 145 is
the historical baseline count, not the complete supported minimum of 151.

Six division-runtime entry/body roles from the
[integer execution review](INTEGER_ARITHMETIC_REVIEW.md) brought the baseline total to 42 roles. Eight more entries from the
[control helper review](CONTROL_HELPER_REVIEW.md) bring the current total to 50,
with 95 entries pending semantic review.

### Peripheral map

All 136 peripheral references across 21 entries map to blocks of the official SAM7S address layout: USART0 35,
PIOA 40, AIC 29, ADC 11, SPI 6, timer/counter 6, PMC 6, reset controller 3. No reference is unmapped. Mapping a register
block does not by itself establish a function's purpose or direction.

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
