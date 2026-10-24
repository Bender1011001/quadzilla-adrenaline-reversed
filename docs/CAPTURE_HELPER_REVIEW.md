# Capture request selection, rotation and byte comparison

This review covers three Thumb entries in the exact 32,000-byte V2.8.4HF
image, SHA-256 `1ae519ba6194e8f7bdaaa94333a83a9e6fda3b0563f87f7d48383b37288c1780`.
The [bounded decode](../audit/data/capture_helper_binaryninja.json) accounts
for 252 bytes and 123 instruction starts. The
[original-byte evidence](../audit/data/capture_helper_emulation.json) includes
172 request/rotation cases and 65,605 comparator calls. Their union visits
all 123 starts; the existing byte-verified IDA export matches those boundaries.
Explicit-mode decoding and execution support the selected
stream; Binary Ninja's decoder supports a superset of ARMv4T.

## `0x5E04`: request-table selector and optional secondary command

This 156-byte routine is called by `0x5EBC`. R2 is an unsigned table index;
values at least 7 return before global flag writes or transfers. For valid
indices, it writes timeout-control bytes `0x200AD4=1`, `0x200AD5=0`,
`0x200AD3=1`, and calls `0x6B64` with SPI base from `0x2005E0`, pointer
`0x9FF0+9*R2`, and count 9. It retries while the helper returns zero and
`0x200AD5` remains zero, using the same shared timeout mechanism documented
in the [initializer](SPI_INITIALIZATION_REVIEW.md).

After that first transfer loop, R1 is clamped to 3 when its unsigned value
is at least 4. R0 chooses the following behavior:

| R0 mode | Byte `0x2005D1` | Secondary transfer |
|---:|---:|---|
| 0 | `0x30` | Write `0x2005D2 = 8 OR clamped_R1`; transmit three counts from `0x2005D0`. |
| 1 | `0x40` | Same secondary pointer/count and option-byte rule. |
| 2 | `0x50` | Same secondary pointer/count and option-byte rule. |
| unsigned value at least 3 | unchanged | Skip the secondary command; the first nine-count request has still been attempted. |

The byte at `0x2005D0` is preserved. Each secondary attempt repeats until
accepted or timed out. A nonzero timeout at the final check requests
`0xA500000D` at reset-controller address `0xFFFFFD00`; the harness stops at
that store. No physical reset or transfer is simulated. The subsequent
[command audit](SPI_CAN_CONTROLLER_REVIEW.md) interprets these bytes as
MCP2515-compatible TX-buffer selection, TXREQ and priority controls; the
installed component and application message meanings remain unresolved.

The table base comes from image literal `0x5EAC`. The seven supported record
starts are `0x9FF0`, `0x9FF9`, `0xA002`, `0xA00B`, `0xA014`, `0xA01D`,
`0xA026`, giving an exact referenced extent `[0x9FF0,0xA02F)` of 63 bytes.
The initializer's nine-byte request is record 0. This extends its earlier
nine-byte classification to the whole seven-record table; the byte at
`0xA02F` and the surrounding area are not classified by this evidence.
IDA's overlapping code items are retained as layout conflicts in the ledger.

## `0x5EBC`: flag-driven request rotation

This 54-byte helper is called by capture entry `0x59E8`. If byte
`0x200AD2` is zero, it returns without global writes or transfers. Otherwise
it clears that flag, sets `0x200AD1=1` and `0x200AD0=1`, and updates index
byte `0x200AFC`: increment modulo 256, then replace values at least 7 with
zero. It calls `0x5E04(0,0,new_index)`.

The [TC2 review](TC2_CALLBACK_REVIEW.md) shows that `0x200AD1` resets
counter `0x20076C`, `0x200AD0` enables it, and a prior count of at least 401
sets `0x200AD2` and clears `0x200AD0`. The request sender separately arms
the 3001-threshold timeout group at `0x200AD3..0x200AD5`. These are two
different software counter groups; no real duration is established here.
The rotation index changes before the transfer helper is accepted, and no
response validation or retry-index rollback occurs in this helper.

## `0x8504`: unsigned bytewise comparison

This 42-byte helper takes pointers in R0/R1 and an unsigned byte count in R2.
It returns `0xFFFFFFFF` when the first differing left byte is lower, 1 when
it is higher, and 0 when all requested bytes compare equal. A zero count
performs no input read. Embedded zero bytes do not terminate comparison.
It advances the pointers and decrements the count while matching, preserves
R4, and makes no non-stack writes. Capture entry `0x59E8` is the known caller.

Every pair of possible one-byte inputs was executed: 32,640 returned -1,
256 returned 0, and 32,640 returned 1, with zero reference differences.
A further 68 cases cover equal and differing prefixes of lengths 0, 1, 2,
4, 8 and 16, including embedded zeros and mismatches at each position.
The extra zero-length call with unmapped pointers returned 0 without a fault.
The output digest and per-prefix outcomes are recorded in the artifact.
This proves those bounded comparisons, not arbitrary pointer/count safety;
the helper has no independent buffer-bound checks.

## Request execution cases and scope

The 172 helper cases include the product of indices 0–7, modes 0–3 and
options 0–4; unsigned extreme probes; one-failure-per-transfer retries;
an explicitly injected timeout; a bounded unready/no-timeout probe; and
rotation trigger/index combinations. Cases returning normally preserve
R4–R7 and the stack. The retry case visits both loops; the timeout case
stops at its keyed reset request; the unready case remains active at the
instruction budget. Table pointers, secondary command bytes, flag writes
and caller-selected arguments are preserved in the evidence.

SPI/PDC/PIO/RSTC are plain synthetic memory, readiness is scripted, and the
timeout flag is injected explicitly. There is no PDC data movement, IRQ
cadence or external command/response model. The full parser state machine,
format matching, field scaling and malformed/stale response behavior at
`0x59E8` remain separate review work. These helpers establish its lower-level
contracts without assigning external meanings to unreviewed data.

```text
PYTHONPATH=<Binary Ninja Python path> python audit/tools/decode_image_ranges.py firmware_v2.8.4HF.bin --ranges 0x5e04:0x5ea0:thumb2,0x5ebc:0x5ef2:thumb2,0x8504:0x852e:thumb2 --output audit/data/capture_helper_binaryninja.json
uv run --with unicorn==2.1.4 python audit/tools/emulate_capture_helpers.py firmware_v2.8.4HF.bin --output audit/data/capture_helper_emulation.json
python -m unittest discover -s tests -t .
```

The tools check the exact image hash and never access a device.
