# Remaining local AID handlers, curves and dispatcher continuations

This review completes the bounded local accounts of all **57 non-default
handlers selected by `0x601C`**, for the exact V2.8.4HF image, SHA-256
`1ae519ba6194e8f7bdaaa94333a83a9e6fda3b0563f87f7d48383b37288c1780`.
It adds 44 handler accounts and four baseline alternate-entry roles. It
does not complete the receive protocol, all parameter writers/consumers or
the full firmware analysis.

The added instruction ranges total **1,218 bytes and 582 starts**:
`[0x6042,0x6048)`, `[0x6048,0x604C)`, `[0x604C,0x604E)`,
`[0x64B8,0x6702)` and `[0x67DC,0x6A48)`. The
[Binary Ninja decode](../audit/data/remaining_update_binaryninja.json) exposes
582 starts, all executed in the [bounded campaign](../audit/data/remaining_update_emulation.json).
The byte-verified IDA export agrees on 568 individual starts. Seven IDA macro
items combine the other fourteen starts into constant-load displays; their
source extents and constructed register values are separately adjudicated.
The intervening literal pools remain excluded. The decoder is a superset
of ARMv4T and the emulator is an ARM926 functional surrogate, not hardware.

Together with the earlier reviews, the dispatcher and its four shared
continuations account for 1,882 instruction bytes. Baseline role coverage
becomes **113 reviewed / 32 pending**, and total reviewed instruction coverage
became **10,782 bytes** at this review stage; the subsequent [payload walker review](PAYLOAD_WALKER_REVIEW.md) takes current instruction coverage to **11,282 bytes**. The historical 145-entry inventory is still not
claimed exhaustive.

## IDA constant-macro adjudication

The [source-bound macro audit](../audit/data/remaining_update_ida_macros.json)
explains all fourteen individual boundary differences, without rewriting
the original IDA export:

| IDA macro start(s) | Actual two-instruction construction | Constant |
|---|---|---:|
| `0x6534`, `0x6562`, `0x6586`, `0x65B4`, `0x65D8` | `MOVS #0xFF`, then `ADDS #0x2E` in the same register | 301 |
| `0x6686` | `MOVS #0xC8`, then `LSLS #2` | 800 |
| `0x67DC` | `MOVS #0xC8`, then `LSLS #4` | 3200 |

Each four-byte IDA item covers two two-byte Thumb instructions. The audit
decodes the original halfwords, checks register/operation consistency and
the constructed value, and verifies aggregate extent. All fourteen starts
execute in the original-byte campaign. Condition flags follow the explicit
sequence, not an imagined single constant-load instruction. There are no
unexplained boundary differences in these ranges.

## Parent-frame contract and shared continuations

The main loop calls `0x601C` at `0x76DC`. It enters validation only when
receive/type dispatcher `0x8038` returns exactly 1, then processes the reported
AID list in order. The [earlier gate/loop account](AID_DISPATCH_SELECTOR_UPDATES.md)
and [compound account](COMPOUND_AID_UPDATE_REVIEW.md) describe those paths.
All handler campaigns use an explicit scripted receive-result contract;
the `0x8038` instructions do not execute in these handler campaigns.

The catalog's entries below are non-returning continuations inside this
parent frame, not ordinary independently callable functions:

| Entry | Immediate contract | Known incoming image calls |
|---|---|---|
| `0x6042` | With curve candidate in R3 and curve base in R0, raise R3 to 50 if below 50; continue into `0x6048`. | AID 136 path at `0x6A3E`. |
| `0x6048` | Store low R3 byte to `[R0+0xF]`, load echo pointer `0x200C35` into R0, continue into `0x604C`. | AID 136 upper path at `0x6A44`, plus fall-through from `0x6042`. |
| `0x604C` | Store low R3 byte to `[R0]`, then continue into loop increment `0x604E`. | Fifteen curve paths for AIDs 121–135, plus fall-through from `0x6048`. |
| `0x604E` | Increment the parent-frame loop index modulo 256, then check count and dispatch the next AID or return through the parent epilogue. Incoming scalar registers are not arguments. | Shared `BL` at `0x684C` used by AID 116 and the AID 120 echo-store path, plus ordinary handler branches. |

These continuations require the active `0x601C` stack layout: pointer at
SP+0, loop index at SP+4, reported count at SP+8, AID list at SP+12, and the
original saved-register/return frame beyond the 28-byte locals. The loop
eventually returns through that original frame. `BL` instructions at these
sites overwrite LR, but the continuation does not return to that LR. AID
116/120 also use `BL 0x604E` as a loop continuation. Reading these as normal
C calls would incorrectly infer fall-through into the next AID case.

The `0x604E` instructions were already classified under the parent loop in
the earlier selector/count review. This pass assigns its separate catalog
role without adding those bytes again. A partition-based call graph can show
this label calling itself; the original control flow is a parent-frame loop
continuation, not evidence of recursive C calls.

Complete checked ingest calls preserve R4–R11 and SP. No scalar R0 result
is specified. The immediate continuation stores and the subsequent loop
side effects are its outputs; arbitrary standalone entry with a normal
call stack is outside the supported contract.

## Scalar clamp and echo contracts

All source values are unsigned. The following table uses source bytes
actually read by the handler; those widths can differ from transport width.
All stores listed here execute on every selected handler call, including
when the stored value is unchanged. No equality guard is present.

| AID | Source / bytes read | Working destination / bytes stored | Raw value rule | Echo destination / bytes written |
|---|---|---|---|---|
| 17 | `0x200B20` / 1 | `0x200588` / 1 | Cap at 30 | `0x200BED` / 1 |
| 18 | `0x200B21` / 1 | `0x20058A` / 1 | Cap at 100 | `0x200BEE` / 1 |
| 19 | `0x200B22` / 1 | `0x20058B` / 1 | Cap at 100 | `0x200BEF` / 1 |
| 22 | `0x200B23` / 1 | `0x200589` / 1 | Coupled rule below | `0x200BF0` / 1 |
| 59 | `0x200B24` / 1 | `0x2005B0` / 1 | Cap at 50 | `0x200BF1` / 1 |
| 60 | `0x200B25` / 1 | `0x2005B1` / 1 | Cap at 100 | `0x200BF2` / 1 |
| 61 | `0x200B26` / 1 | `0x2005B2` / 1 | Cap at 80 | `0x200BF3` / 1 |
| 62 | `0x200B27` / 1 | `0x2005B3` / 1 | Cap at 40 | `0x200BF4` / 1 |
| 85 | `0x200B30` / 2 | `0x200590` / 4 | Clamp 800..2200 | `0x200BFD` / 2 |
| 104 | `0x200B32` / 2 | `0x200594` / 4 | Clamp 3200..3700 | `0x200BFF` / 2 |
| 110 | `0x200B35` / 1 | `0x20058C` / 1 | Cap at 50 | `0x200C01` / 1 |
| 111 | `0x200B37` / 1 | `0x20058E` / 1 | Clamp 1..100 | `0x200C03` / 1 |
| 112 | `0x200B39` / 1 | `0x20058D` / 1 | Cap at 25 | `0x200C05` / 1 |
| 137 | `0x200B28` / 2 | `0x2005B4` / 4 | Cap at 300 | `0x200BF5` / 2 |
| 138 | `0x200B2A` / 2 | `0x2005B8` / 4 | Cap at 300 | `0x200BF7` / 2 |
| 139 | `0x200B2C` / 2 | `0x2005BC` / 4 | Cap at 300 | `0x200BF9` / 2 |
| 140 | `0x200B2E` / 2 | `0x2005C0` / 4 | Cap at 300 | `0x200BFB` / 2 |
| 141 | `0x200B1E` / 2 | `0x200584` / 4 | Cap at 300 | `0x200BEB` / 2 |

Two-byte sources and echoes use little-endian order. Two-byte echo updates
are two separate byte stores. AIDs 17, 59, 61 and 62 additionally set byte
`0x200426=1`; this is distinct from the compound handlers' `0x200AC4` flag.
The complete consumer of `0x200426` is outside this local account.

AID 61 stores `floor(128*value/10)` as a 32-bit value at `0x20046C`, using
the clamped byte value. AIDs 137–141 store the same scaled expression for
their clamped values at `0x200458`, `0x20045C`, `0x200460`, `0x200464` and
`0x200468`, respectively. The operands cannot overflow or become negative
within these bounds. The raw limits are not independent proof of engineering
units; profile names/scales remain separately recorded.

For AID 22, let V be the source byte and L be working byte `0x20058D`:

```text
if V >= 41:          result = 40
else if V < L + 1:   result = (L + 5) mod 256
else:               result = max(V, 20)
```

This is not a universal clamp to 20..40. With L=5, V=0 yields 10, while
V=6 yields 20. With L=25, V=25 yields 30 and V=26 yields 26. All 256 V
values were executed for each L in 0..25, the range produced by AID 112.
The field's intended control relationship and all other writers of L remain
separate questions; no defect severity follows from non-monotonicity alone.

## Twenty-four curve slots and transport-width distinction

For every AID A in 113..136, let I=A−113. The handler reads **one byte**
from `0x200B3B + 2*I`, clamps it to 50..150, stores it to working byte
`0x200598 + I`, and writes one echo byte at `0x200C07 + 2*I`. This rule,
with each individual address, is recorded in the artifact's `scalar_contracts`.

These 24 AIDs and AIDs 110–112 have **two-byte transport/read width** in
the reviewed width helper, despite reading one staged byte and writing one
echo byte in these handlers. The upper staged byte is ignored here, and
the upper echo byte is retained. The input does not undergo a 16-bit clamp.

There are 324 probes varying the upper staged byte and then calling the
original reader `0x7D80`. With an `A7` canary in the upper echo byte, the
reader returns `[AID, low_echo, A7]` and length 3. This establishes the local
write/read-width distinction under controlled SRAM. It does not establish
that live echo high bytes are nonzero, identify all echo writers, or determine
application handling of the upper byte. Treating these parameters as ordinary
16-bit clamped values would lose this distinction.

## AID 24 default-initializer trigger

The handler reads staging byte `0x200B34`. Only value **`0x55`** calls the
previously reviewed initializer `0x4384`; every other byte immediately
continues the loop. All 256 trigger bytes are executed.

The triggered 103 non-stack stores match the source-bound initializer trace
from the [control-helper review](CONTROL_HELPER_REVIEW.md). That prior
contract supplies the expected default writes; this campaign verifies the
call-site gate and propagation of those effects, rather than claiming a new
independent model of the initializer. This is an offline SRAM/default setup
path, not evidence of a hardware reset, flash operation or restored persistent
configuration on a physical unit.

## AID 226 configuration and floating coefficient

The handler reads from staging address `0x200AEC`. It does not consult the
first staging byte or a local length/count field. Offsets 1..4 are read:

* If byte 1 is below 3, copy it to `0x2006E6`; otherwise retain that field.
* If byte 2 is below 5, copy it to `0x2006E7`; otherwise retain that field.
* Assemble unsigned 16-bit W from bytes 3/4. Convert W to binary64, divide
  by binary64 10.0, round to binary32, retain that value in R5, widen it
  back to binary64, and compare it with binary64 bit pattern 1 using `0x6B10`.
  Store R5 at `0x2006E8` only when the comparison succeeds.

The comparison constant is the smallest positive binary64 subnormal, not
integer 1. W=0 retains the old coefficient; positive W gives a positive normal
result and stores the rounded binary32 representation of the staged division.
The first two selector updates are independent and can still occur for W=0.
Out-of-range staged selector values leave the corresponding working field
unchanged. No update flag is
stored by this handler in the tested finite domain.

The campaign covers selector boundaries, W edges, three different first
staging bytes, and 4,096 additional seeded W samples, totaling 4,576 AID 226
calls. The finite conversion/division path matches the exact-rational IEEE
reference at each rounding stage. This does not erase the separate
[numeric-runtime exceptional-value findings](SOFT_FLOAT_REVIEW.md).

The coefficient is consumed by the [CAN parser's F1-header scaling](CAPTURE_PARSER_REVIEW.md).
This establishes its parameter writer and software consumer. The profile
label is Drive Train Info; physical units and complete downstream meaning
remain unresolved. The variable-width payload walker and actual admission
of a short value are not executed here: varying the first staging byte does
not establish transport reachability of truncated data.

## Validation, coverage and remaining scope

The campaign executes **22,703 complete ingest calls**: 10,891 scalar cases,
6,656 coupled AID 22 cases, 324 upper-byte/readback probes, 256 reset-gate
cases, and 4,576 AID 226 cases. Ordered non-stack stores match the reference
contracts with zero differences. All new instruction starts are visited.

All 57 selected local handlers now have a substantive bounded account across
this review and the prior selector/count and compound reviews. The generated
dispatch map links each handler to its account. This closes the local handler
queue, not the full parameter/protocol goal: transport framing and variable
lengths, raw staging consumers, all global/echo writers, IRQ interactions,
persistence and downstream control effects remain required work. Full-image
literal/data classification and other execution entries also remain incomplete.

Resolve the remaining parameter-path questions by completing the variable-width
walker and receive-state accounts, enumerating writes to staging/working/echo
regions, and tracing `0x50F0`, persistence and timer consumers. Application
decoding or vendor encoding documentation is needed to establish field units
and count conventions. Passive normal-operation captures can test those
interpretations; none were performed to close this local handler queue.

```text
PYTHONPATH=<Binary Ninja Python path> python audit/tools/decode_image_ranges.py firmware_v2.8.4HF.bin --ranges 0x6042:0x6048:thumb2,0x6048:0x604c:thumb2,0x604c:0x604e:thumb2,0x64b8:0x6702:thumb2,0x67dc:0x6a48:thumb2 --output audit/data/remaining_update_binaryninja.json
uv run --with unicorn==2.1.4 python audit/tools/emulate_remaining_updates.py firmware_v2.8.4HF.bin --output audit/data/remaining_update_emulation.json
uv run --with unicorn==2.1.4 python audit/tools/audit_aid_dispatch.py firmware_v2.8.4HF.bin --output audit/data/aid_validation_dispatch.json
python audit/tools/audit_remaining_ida_macros.py firmware_v2.8.4HF.bin --output audit/data/remaining_update_ida_macros.json
python -m unittest discover -s tests -t .
```

No device traffic, programming or engine-setting changes were performed.
