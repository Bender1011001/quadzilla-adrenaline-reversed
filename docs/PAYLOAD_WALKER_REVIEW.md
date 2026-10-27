# Payload widths, completion and short-value admission

This review applies to the exact 32,000-byte V2.8.4HF application image,
SHA-256 `1ae519ba6194e8f7bdaaa94333a83a9e6fda3b0563f87f7d48383b37288c1780`.
It reconstructs the complete local walker and frame-helper contracts, then
executes a short-value sequence through the original receive dispatcher and
parameter ingest. The latter replaces no firmware functions.

The accepted ranges add **500 instruction bytes** and **245 starts**. The
[main decode](../audit/data/payload_walker_binaryninja.json) covers 460 bytes;
three complete header helpers in the [context decode](../audit/data/short_value_context_binaryninja.json)
add 40. All starts execute. IDA agrees on 243 individual boundaries; two
overlapping invalid-ISA items are adjudicated below. Total reviewed instruction
coverage becomes **11,282 bytes**. Baseline roles remain 113 reviewed / 32
pending: these eight entries already had semantic labels.

The explicit Thumb decoder supports a superset of ARMv4T; the original-byte
emulator is an ARM926 functional surrogate. Source identities, controlled
register/memory inputs and execution results support the stated contracts,
not target timing or universal hardware correctness.

## Entry contracts

| Entry / instruction range | Inputs and result | Effects and known context |
|---|---|---|
| `0x7B60..0x7BC9` | R0 byte pointer, low byte of R1 count; CRC-8 result in R0. | Initial FF, polynomial 1D, MSB-first, final XOR FF. No non-stack writes or capacity argument. Count 256 processes zero bytes. Called by both CRC wrappers and frame construction. |
| `0x7BCC..0x7BE5` | R0 pointer, R1 final-byte index; CRC over `(R1+1) mod 256` bytes. Return 3 for residue 3B, otherwise 4. | No type, allocation-length or independent schema check. Original receive dispatcher obtains the index from the header getter. |
| `0x7BE8..0x7BED` | R0 pointer; return high nibble of its first byte. | One byte read, no non-stack writes. |
| `0x7BF0..0x7BF7` | R0 pointer; return low nibble of its first byte. | One byte read, no non-stack writes. |
| `0x7BF8..0x7C19` | R1 AID, R0 lookahead value. Return 1/2/3/4 for AID ranges 0–74/75–149/150–184/185–219; retain incoming R0 for AID>=220. | No independent validation of the variable count. Callers here supply an AID byte and one lookahead byte; direct tests also check full-width retained R0. |
| `0x7C1C..0x7C51` | Byte AID in R0; return table-1 staging pointer. | For 0..255, the address calculation is equivalent to table at A91C plus 4*AID. AID 255 crosses the 255-slot boundary, as separately reviewed. No destination capacity is supplied. |
| `0x7CC4..0x7D7D` | R0 payload pointer, low R1 byte count capped to 14, low R2 byte type, R3 reported-AID pointer, fifth stack argument count-output pointer. R0 returns 1 or 2. | Byte stores to staging occur before completion is known. Reported AIDs are emitted when nonzero pointers resolve, before value completion. R7 is an implicit incoming completion input on empty/read-list paths. |
| `0x7E64..0x7EB3` | R0 frame pointer, R1 type-output pointer, R2 AID-list pointer, R3 count-output pointer. | Initialize type=6/count=0. Header low nibble zero returns 5; bad CRC returns 4. Valid CRC extracts type and invokes the walker on `low_nibble−1` payload bytes, propagating its 1/2 result. |

All checked ordinary calls preserve R4–R11 and SP. Caller-saved registers
and condition flags are not additional output contracts. Adjacent pools,
alignment and other function bodies are excluded from these byte ranges.
The [table-boundary account](AID_TABLE_BOUNDARY_REVIEW.md) covers the AID 255
alias and response-read behavior separately.

## Byte-walker state and variable counts

The walker starts in "expect AID" mode. In that mode it reads the AID,
advances its payload pointer, and **unconditionally reads one lookahead byte**
before calling the width helper. Fixed-width AIDs ignore that byte in width
selection. Variable AIDs use it as the count. It then resolves the staging
pointer, emits the AID if nonzero, and enters store or discard mode.

For each subsequent value byte, decrement the remaining count modulo 256.
Store the byte only when the pointer is nonzero; discard otherwise. On count
zero, return to expecting an AID. When the declared payload budget ends,
return 1 if the low remaining byte is zero, else 2. There is no rollback.
Unmapped AIDs still consume their selected widths, but are not reported.

For variable AIDs, the first count byte is itself stored and consumes one
of the selected value bytes. Thus count 5 consumes `[5, a, b, c, d]` after
the AID; count 1 consumes just `[1]` and can return success. Count zero is
not rejected before stores: the first value byte decrements zero to 255,
and the bounded frame ends incomplete. All 256 count bytes were executed
at declared payload lengths 2..14.

Types 2 and 4 take a separate AID-only path: copy every payload byte to the
reported list without resolving pointers or writing staging. Other low-byte
type values use the value-bearing state machine. The frame helper itself
does not reject unknown high-nibble types; the outer receive dispatcher has
its own 0..5 type selection. These are distinct contracts.

## Lookahead and caller-defined completion

A final AID byte causes a read at payload offset equal to the declared
payload length. A direct guard-page test places AID 226 at the last mapped
byte and records an unmapped read at `0x211000`, PC `0x7D40`. This proves
the local read beyond the declared payload, not a physical memory fault.
In the normal frame-helper layout that next byte is the frame's CRC byte,
inside the allocated frame; those two bounds must not be conflated.

The walker does not locally assign R7 on empty or AID-only paths. Its final
test depends on the low incoming R7 byte, while its epilogue restores the
caller's full R7. Direct tests vary that incoming state explicitly.

The only identified direct image caller is `0x7E64` at `0x7EA2`. It sets R7
to the payload-byte count immediately before calling. Therefore:

* A CRC-valid empty frame reaches the walker with R7=0 and returns 1.
* A nonempty type-2/4 list reaches it with R7=payload length and returns 2,
  despite copying its complete AID list.

These are reproduced caller-defined results, not unspecified behavior in
that known call path. The receive dispatcher's type-4 path at `0x80BE..0x80CE`
checks reported count and queues a response independently of status 1.
A result of 2 must not universally be interpreted as a malformed read list.
The entire type-2/4 response/acknowledgment state machine remains separate
review work; the complete no-stub admission example below exercises type 1.

## Short value applies fields retained from an earlier failed value

The [admission artifact](../audit/data/short_value_admission.json) executes:

```text
0x601C -> 0x8038 -> header getters / 0x7BCC CRC check
                    -> 0x7E64 -> 0x7CC4
         -> successful reported-AID validation -> AID 226 numeric path
```

There are **no function stubs** in this sequence. The environment supplies
a completed frame in the current 16-byte buffer, sets pending flag
`0x200AFD=1`, and supplies zero current receive count at `0xFFFC0104`, matching
the earlier reviewed completion boundary. USART/PDC registers are plain
synthetic memory. The original code switches buffers, rearms reception,
checks CRC, walks the payload and decides whether to run validation.

Initial working configuration is mode=0, selection=0, coefficient binary32
`0x3F000000` (0.5). The sequence is:

| Step | Frame in hex | Original receive status at ingest gate | Observed effect |
|---|---|---:|---|
| Variable count zero with fields | `17 E2 00 02 04 0A 00 8A` | 2 | CRC-valid; staging becomes `00 02 04 0A 00`; working values remain unchanged. |
| Count-only value | `13 E2 01 B6` | 1 | CRC-valid; only staging count becomes 01. AID 226 applies retained mode 2, selection 4, and word 10, producing coefficient 1.0 (`3F800000`). |
| Damaged-CRC control | `17 E2 05 00 00 14 00 2E` | 4 | Rejected by the original preliminary CRC check; staging and working configuration retained. |
| Empty valid frame | `11 EB` | 1 | Original caller supplies the empty-walker state; no configuration change. |
| Oversized AID 226 value | `1F E2 0D 00 00 0A 00 A5 A5 A5 A5 A5 A5 A5 5A 68` | 1 | Thirteen value bytes are staged, including `5A` at `0x200AF8`; the working mode and selection become zero. |

The first failed value supplied the four data fields later applied by the
successful count-only value. The latter supplies none of those fields.
The source handler reads staging offsets 1..4 without checking how many
were refreshed, as established in the [local AID 226 account](REMAINING_AID_UPDATE_REVIEW.md).

This is a confirmed software-path acceptance and retained-field application
under the stated completed-buffer preconditions. Intended partial-update
semantics, physical delivery, pairing, all upstream receive states and
downstream consequences remain unresolved. It does not establish engine
effects or an independent severity rating. No frame was sent to a device.

## Bounded cross-global write from a variable value

The 14-byte payload cap still permits AID 226 followed by 13 value bytes.
The original walker accepts count `0D`, stores all 13 bytes beginning at
`0x200AEC`, and returns success. Its last store at PC `0x7D6C` writes `5A`
to `0x200AF8`. The original receive path then invokes the AID 226 handler,
which consumes staging offsets 0..4. The separately reviewed soft-float
path at `0x8958` loads a pointer to `0x200AF8` from literal `0x896C` and
uses that byte as numeric status; see [soft-float review](SOFT_FLOAT_REVIEW.md).
The witness reads back `5A` there after ingest.

This establishes a software write across the five fields used by this
handler into a separately used byte. It does not establish the formal
allocation size of the staging object or a physical effect. Within one
frame the farthest reached byte is `0x200AF8`; this evidence does not
support arbitrary writes or a write to the pending flag at `0x200AFD`.
It also does not prove which later numeric operation, if any, observes
the retained status byte.

## Header getter boundary correction

The [boundary audit](../audit/data/payload_header_boundaries.json) records
IDA items at `0x7BE6` and `0x7BEE` that display NEON `VTBL.8` and swallow
the first halfword of getters at `0x7BE8` and `0x7BF0`. ARM7TDMI has no NEON.
The original entry halfword is `7800` (`LDRB R0,[R0]`); explicit Thumb decode,
decoded direct calls and all 256 header-byte probes support the real getters.
The preceding `FFFF` halfwords remain outside this instruction review and
are not silently promoted to verified padding. Seventeen other header-helper
starts and all 226 main-helper starts match ordinary IDA boundaries.

The context decode also contains the admission path and previously reviewed
RX staging helper. Those extra context spans are not counted as complete
`0x8038` or USART instruction coverage merely because the witness visits them.

## Validation and remaining work

The main campaign checks **8,834 calls**: 7,608 direct payload cases, 193
frame-helper cases, 1,024 width-helper cases and nine CRC-length cases,
plus the guard-page probe. It includes all byte AIDs, all variable count
bytes across lengths 2..14, types 0..15, explicit incoming R7 values,
two-byte count-argument truncation/capping and seeded mixed payloads.
The header campaign adds 512 getter calls and 96 CRC-envelope calls.
All match the stated reference contracts. Five complete ingest calls
exercise the no-stub admission sequence.

Complete receive-state dispatch, outgoing queues/readback assembly, other
raw-staging consumers, persistent state and control/timer consequences
remain required. The original fixed-width model remains a documented
subset; the new byte-state model adds variable widths and caller state
without implying live protocol acceptance beyond the tested software path.
Full firmware analysis remains active and incomplete.

```text
uv run --with unicorn==2.1.4 python audit/tools/emulate_payload_walker.py firmware_v2.8.4HF.bin --output audit/data/payload_walker_emulation.json
uv run --with unicorn==2.1.4 python audit/tools/emulate_short_value_admission.py firmware_v2.8.4HF.bin --output audit/data/short_value_admission.json
python audit/tools/audit_payload_header_boundaries.py firmware_v2.8.4HF.bin --output audit/data/payload_header_boundaries.json
python -m unittest discover -s tests -t .
```

The [generic writer/admission review](GENERIC_WRITER_FOOTPRINT_REVIEW.md) adds the complete resolved staging footprint and follows AID 255 through complete original cycles, including an incomplete value whose response-byte stores are consumed by control.
