# Verification review — October 22, 2026

This review checks the published research and tooling against the owner's local
V2.8.4HF application image. It does not establish complete reverse engineering,
live device behavior, or correctness of every decompiler inference.

## Reproduced evidence

| Check | Result |
|---|---|
| Image identity | 32,000 bytes; SHA-256 `1ae519ba6194e8f7bdaaa94333a83a9e6fda3b0563f87f7d48383b37288c1780` |
| Actual vendor `.qz` | 2,000 valid HEX records; zero checksum errors; re-encryption identical |
| Existing IDA/Ghidra reconciliation regenerated | 145 supported execution entries, one rejected data partition, zero unresolved starts in the proposed-start union |
| Semantic catalog regenerated | 14 labeled roles, 131 unlabeled entries |
| Fresh IDA Pro 9.3 pass | Database bytes exactly match the image; 14 critical Thumb traces exported |
| Binary Ninja 5.2.8722 Personal | Now operational; the same 14 entries decoded at the explicit `0x4000` image base |

Binary Ninja was seeded with existing entry addresses and uses its ARMv7/Thumb2
decoder. Recognition of an entry is not independent discovery, validation of
every ARMv4T opcode, or proof that it executes. IDA macro instructions and tool
partition boundaries can differ. Earlier notes about Binary Ninja's invalid
license describe an earlier session, not this review.

The new exports are [IDA traces](../audit/data/ida_verified_traces.json) and
[Binary Ninja traces](../audit/data/binaryninja_seeded_check.json). The exporters
are in `audit/tools/`; neither opens a device. The existing full Hex-Rays export
in the owner's working archive failed to decompile the ARM image and is not
treated as verified C source.

## Corrections and additional findings

- **AID 104 upper clamp resolved:** the word at `0x67D8` is 3701; the upper branch
  subtracts one. Together with the lower clamp at 3200, this matches the profile's
  3200–3700 RPM range statically. AID 85's corresponding upper literal at `0x67C0`
  is 2201, yielding 2200. Hardware behavior remains untested.
- **Timer path rechecked:** both tools decode `STR R1,[R0,#0x1C]` at `0x6FA6`.
  IDA traces show the caller loading `0xFFFA0000` at `0x5388` and calling the helper
  at `0x538A`, after `R6*24+3`. The write is conditional on the status bit tested
  in the helper. This supports the TC0_RC chain, not a measured pulse duration.
- **Firmware map corrected:** there are seven initial branch words, followed by
  `MOV R9,R0` at `0x401C`. Executable helpers resume at `0xB114` after the second
  pointer table. ARM interworking code also prevents a simple global
  "first 256 bytes ARM, everything else Thumb" interpretation.
- **Clamp extractor bounded:** it reports literals within lexical case bodies.
  Cases 123–136 jump into shared code, so absent local literals cannot establish
  absent validation. It does not evaluate the dispatcher's full control flow.
- **Security wording tightened:** valid checksums do not prove that the updater
  accepts an altered package; lack of a nonce in a frame does not demonstrate
  device replay acceptance. Both remain hardware questions.

## Tool defects fixed

The HEX parser previously accepted a truncated record such as `:10400000B0`
(its checksum sums to zero despite its missing payload), included bad-checksum
data in the decoded image, ignored arbitrary non-record text, and did not honor
EOF or extended segment addresses. Decryption wrote output before validating it.

The parser now checks exact lengths, record types, control-record fields,
overlaps and address boundaries. Invalid checksums are reported and excluded
from memory. Encrypt/decrypt validate before writing output; key arguments are
mutually exclusive. Flat sparse images larger than 16 MiB are rejected rather
than expanded into potentially gigabytes of memory. The vendor's valid no-EOF
format remains supported.

The entry reconciliation now rejects known pointer-table data even if both
disassemblers propose a function there. Export/reconciliation paths are
configurable instead of depending on the author's old drive path.

The optional USB reader now rejects incomplete feature responses, restores its
timeout after read errors, and returns module-info bytes without assigning
unverified version/serial/hardware field layouts. Its transport is still
untested on a device.

## Reproduce

The standard-library suite runs without vendor images or licensed tools:

```bash
python -m unittest discover -s tests -t . -v
python tools/diff_profiles.py
python tools/aid_clamps.py
python tools/x2com_crc.py
```

With the independently obtained vendor package:

```bash
python tools/firmware_crypto.py verify FirmwareUpdate.qz --key 111d6f202ee5a103
python tools/firmware_crypto.py decrypt FirmwareUpdate.qz fw.hex --key 111d6f202ee5a103 --bin fw.bin
python audit/tools/compare_quadzilla_disassemblers.py --ida audit/data/ida_function_map.json --ghidra audit/data/ghidra_function_map.json --image fw.bin --output reconciliation.json
```

Licensed tools, configured with their own Python modules:

```text
idat -A -S"audit/tools/ida_verify_image.py fw.bin ida_traces.json" DATABASE_COPY.i64
python audit/tools/binaryninja_check.py fw.bin --catalog audit/data/execution_entry_catalog.json --output bn_traces.json
```

## Remaining work

131 execution entries still lack reviewed semantic labels. Bootloader acceptance,
pairing behavior, all incoming-write paths, live timing, firmware hooks, and
recovery are unresolved. Smarty S03 and CM551 files in the owner's broader local
workspace are separate targets; this public repository does not claim to verify
them. The defensible outcome is a reproducible, bounded static analysis, not a
claim that the whole device is understood or engine-tested.
