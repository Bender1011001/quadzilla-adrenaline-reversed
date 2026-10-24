# Software floating point runtime: bounded offline review

This review applies only to the exact 32,000-byte V2.8.4HF application image
with SHA-256 `1ae519ba6194e8f7bdaaa94333a83a9e6fda3b0563f87f7d48383b37288c1780`.
It uses original image bytes in an ARM926 emulator, an exact-rational Python
reference, explicit-mode Binary Ninja decoding, and a disposable IDA database.
There was no connected controller or peripheral simulation. The results do not
establish live engine behavior or universal IEEE 754 compliance.

## Scope and entry contracts

The [per-entry review](../audit/data/soft_float_function_reviews.json) gives
register inputs, outputs, callers, shared bodies and bounds for 40 entries:
18 baseline ARM entries, 16 baseline Thumb wrappers, and six additional ARM
starts. The six include a status helper and five numeric starts. The binary64
subtraction at `0x8CFC`, signed integer to binary32 conversion at `0x9048`,
and binary32 subtraction at `0x94B4` are independently callable in the offline
harness, but no incoming image call has been established for them. The source
entry minimum is now 157; the 145-entry baseline has 84 semantic labels and
61 pending. Source entries are not a count of reachable live functions.

The wrapper targets are checked against their image literals in the
[execution artifact](../audit/data/soft_float_emulation.json). Public suites
cover binary32 add, subtract, multiply, divide and conversions; binary64 add,
subtract, divide, comparisons and conversions; and wrappers. Internal
normalizers `0x8678` and `0x86A8` were separately exercised on nonzero
52-bit mantissas. The [Binary Ninja range export](../audit/data/soft_float_binaryninja.json)
contains two ARM instruction spans and 16 Thumb wrapper spans. The word at
`0x896C` is a pointer to status byte `0x200AF8`, excluded from instructions.
Wrapper literals and alignment bytes are excluded as well.

The emulator completed 30,627 bounded original-byte calls across 35 public
entry suites, two internal normalizer suites and five caller-state probes.
Its ARM926 model is a functional surrogate. ROM and SRAM are mapped; no
peripherals are mapped. The harness checks return bounds, callee-saved
registers, stack preservation and writes limited to stack or `0x200AF8`.
The exact-rational reference rounds finite arithmetic to nearest, ties to
even. Arithmetic NaNs are compared by category; NaN payloads and quiet bits
are not asserted. The committed suite has mismatches and is deliberately
marked `all_reference_comparisons_match: false`; a successful harness exit
means the checks completed, not that every result agreed.

## Reproducible exceptional results

| Original-byte call | Inputs | Observed output | Exact reference | Bound |
|---|---|---|---|---|
| Binary32 division `0x92CC` | `0x00800000 / 0x00000001` | `0x35000000` | `0x4B000000` | Subnormal denominator normalization; suite has 32 mismatches in 1,188 calls. |
| Binary64 addition `0x8EF4` | `0x1 + 0x0010000000000000`, incoming R4=`0x0` | `0x0010000000000001` | same | One tested caller state. |
| Binary64 addition `0x8EF4` | same operands, incoming R4=`0x12340004` | `0x00148D0000000001` | `0x0010000000000001` | Caller-state dependence, without a live caller assertion. |

On the subnormal path, the branch at `0x8F64` reaches `0x8F90` without
executing the `MOV R4,#0x80000000` initialization at `0x8F8C`; the latter
path ORs incoming R4 into the result. The harness tried five incoming R4
values and recorded five outputs. R4 is preserved on return, so preservation
alone would not detect this. Binary64 subtraction shares the add body.
This is an offline numeric defect in the callable routine. Its impact at
an actual call site requires caller-state and hardware review.

Other bounded differences appear in binary64 divide (49/1,188), addition
(37/1,188), subtraction (36/1,188), binary64 to binary32 (2/538), and two
binary64 comparison suites (2 and 47 differences in 1,188 each). The latter
cases include NaNs whose payload exists only in the low word: some are treated
as infinity or compare equal to themselves. The suite records each input,
actual output and reference output. The tested integer conversions and
binary32 add/multiply/subtract suites had zero reference mismatches; that
is evidence for those tested inputs only.

## Decoder limits and byte accounting

The [IDA decode artifact](../audit/data/soft_float_ida.json) accepts 761
ARM word slots and records 281 slots it did not recognize in explicit mode.
They remain decode gaps, not proof of invalid instructions or agreement
between tools. The Binary Ninja range decoder accepts the bounded spans,
but its selected decoder is a superset of ARMv4T. The original-byte emulator
provides independent execution evidence for visited paths. Unvisited paths
and the IDA gaps still need manual instruction-level reconciliation.

The [full-image ledger](../audit/data/image_coverage_ledger.json) now marks
4,168 ARM instruction bytes and 976 Thumb instruction bytes reviewed,
separately from 16,372 IDA code candidates and 3,144 IDA data candidates
awaiting review. It continues to retain 2,119 IDA layout conflicts.

## Reproduction

From the repository root, with the exact image at `firmware_v2.8.4HF.bin`:

```text
uv run --with unicorn==2.1.4 python audit/tools/emulate_soft_float.py firmware_v2.8.4HF.bin --output audit/data/soft_float_emulation.json
python audit/tools/build_image_ledger.py firmware_v2.8.4HF.bin
python -m unittest discover -s tests -t .
```

The IDA script is `audit/tools/ida_decode_soft_float.py`; run it with a
disposable database and headless IDA 9.3, passing `IMAGE OUTPUT` after the
script path. The Binary Ninja range export is committed as evidence, including
its tool version and bounds. These commands require licensed local tools
where applicable. Neither executes code on the physical controller.
