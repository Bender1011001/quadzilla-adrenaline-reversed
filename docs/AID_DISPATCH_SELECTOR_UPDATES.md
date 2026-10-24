# AID validation dispatch and selector/count updates

This review applies to the exact V2.8.4HF application image, SHA-256
`1ae519ba6194e8f7bdaaa94333a83a9e6fda3b0563f87f7d48383b37288c1780`.
It establishes the complete byte-AID destination map for the validation
dispatcher, then reviews its loop and AID 9/15 update paths. It does not
claim complete semantics for every handler or for the receive transport.

## Source-bound switch map

The instructions at `0x607E..0x608A` subtract 9 from the AID byte and use an
unsigned comparison against 217. Out-of-range values branch to `0x604E`.
For AIDs 9..226 inclusive, load a signed little-endian halfword from
`0x608C + 2*(AID-9)`, then branch to `0x608E + offset`.

The [complete dispatch audit](../audit/data/aid_validation_dispatch.json)
records all 256 AIDs, their destinations, source-table locations, staging
and response pointers and profile names. The table occupies exactly
**436 data bytes `[0x608C,0x6240)`**, with 218 slots. Independent execution
of the original dispatch instructions for all 256 AID bytes agrees with
the signed-offset calculation. Execution stops before the target instruction;
these 256 cases verify selection, not handler behavior.

There are **57 non-default handler targets**. The other 199 byte values
take the default loop path, including 161 in-range slots and 38 out-of-range
values. A default path here does not establish absence of a staging pointer,
response pointer, other writer or supported read operation. AID 255 still
has the separately documented [pointer-table boundary issue](AID_TABLE_BOUNDARY_REVIEW.md).
Profile names are labels from vendor files, not proof of implemented behavior.

At this review stage, the other 55 non-default handler accounts remained
pending. The subsequent [compound review](COMPOUND_AID_UPDATE_REVIEW.md) adds
eleven accounts, and the machine-readable rows now identify 13 reviewed
handlers and 44 pending. Earlier lexical clamp listings are useful
research aids but do not replace their complete instruction-level accounts.

## Loop and receive boundary

Entry `0x601C` calls receive/type dispatcher `0x8038`, supplying stack
pointers for an AID list and one-byte count. Only return value exactly 1
enters validation; zero and 2 skip it. A zero count returns immediately.
The loop processes the list in order, reinitializing working-base pointers
on each iteration, increments an eight-bit index and stops at the count.
This review caps its synthetic list to 14 entries, matching the previously
reviewed receive contract. It does not establish safety for arbitrary
corrupted counts or an unbounded external list.

The [original-byte update harness](../audit/tools/emulate_selector_updates.py)
replaces **only `0x8038`** with an explicit scripted result: AID list, count
and return status. It preloads staging SRAM. All reviewed ingest instructions,
the latch helper, integer divider and subsequent `0x506C` selector helper
execute from the original image. There is no packet decoder, DMA, IRQ or bus
model in this harness. The earlier [write-path review](OFFLINE_WRITE_PATH_REVIEW.md)
documents the receive/walker connection separately.

The accepted instruction ranges are `[0x601C,0x6042)`, `[0x604E,0x608C)`,
`[0x6240,0x6274)` and `[0x6482,0x64B8)`: **206 bytes and 99 starts**.
All starts match the byte-verified IDA export and the explicit-mode
[Binary Ninja decode](../audit/data/selector_update_binaryninja.json), and
all are visited by the controlled execution cases. Unreviewed handlers,
alternate entries at `0x6042/0x6048/0x604C`, and adjacent literal pools are
excluded. The baseline role count remains 109/36: `0x601C` already had a
broader semantic label, whose unreviewed portions are not promoted here.

## AID 9: staged selector to working selector

Table 1 points to staging byte `0x200B00`. The handler starts at `0x6240`:

1. Call the reviewed readiness/latch helper `0x47B0(0)`. If it returns zero,
   leave the working selector unchanged.
2. Compare the **raw staged byte** with working byte `0x2006CD`. If equal,
   skip normalization, capping and the update-flag store.
3. Otherwise mask the staged byte with `0x7F`, store it to `0x2006CD`, and
   compare it to count byte `0x200580`. If it is at least the count, replace
   it with `(count-1) mod 256`.
4. Set byte `0x200AC4=1`, then continue the loop.

The comparison happens before masking: staged `82` hex with working value 2
sets the update flag even though the normalized working value remains 2.
Staged 2 with working 2 skips that store. The name "update flag" is local
description; its complete scheduling/persistence role is not established here.

AID 9 does not directly store its outgoing response. The subsequent
[selector helper](CONTROL_SELECTOR_REVIEW.md) maps the working selector,
caps its local copy again, and writes the separate AID 9 response at
`0x200BC4`. The harness executes that original helper after each ingest case
and checks both its arithmetic return and response byte.

## AID 15: count, echo and derived mapping

Table 1 points to staging byte `0x200B1D`. The handler at `0x6482` always:

* Clamps the unsigned staged byte to **5..14**.
* Writes the result C to working byte `0x200580` and response byte `0x200BEA`.
* Divides 100 by `C-1`, storing the quotient at `0x200433` and remainder at
  `0x200434`. The runtime returns these in R1 and R0 respectively.

This branch has no readiness gate and does not itself set `0x200AC4`.
It also does not rewrite the existing working selector. In this path the
denominator is 4..13, so it cannot be zero. The earlier selector review's
C=0 and arbitrary-step probes remain synthetic configurations; they are
not values produced by this AID 15 handler.

For these derived T and O, and a ready nonzero selector locally capped to
`C-1`, `V=S*T+O` is at most 100 and needs no byte wrap or signed reversal.
The maximum is exactly 100 because `100=(C-1)*T+O`. The original helper's
special zero-selector branch still returns zero. These bounds cover this
configuration path, not all possible writers of C/T/O.

## Processing order and retained selector evidence

The loop has observable sequential semantics. With initial C=5, S=2,
T=25, O=0, staged selector 10 and staged count 11, readiness available:

| Scripted AID order | Final working S/C | Subsequent mapped return / AID 9 response |
|---|---|---|
| `[9,15]` | 4 / 11 | 40 / 4 |
| `[15,9]` | 10 / 11 | 100 / 10 |

The first order caps S using the old count before the count update. This is
reproduced instruction behavior under the stated receive-result contract;
it is not by itself an atomic-update defect or a measured packet outcome.
Both parameter pairs fit the reviewed fixed-width payload budget, but actual
transport execution is outside this harness.

A further case starts with valid C=14/S=13/T=7/O=9 and processes `[15,9]`
with staged C=5 and staged S=13. AID 15 reduces C without changing S;
AID 9's raw equality check then skips capping. Working S remains 13 with
C=5. The selector helper nevertheless caps its local copy to 4, returns 100
and reports 4. This distinguishes stored working state from the downstream
effective selector. Later writers, persistence and user-visible behavior
require their own complete accounts.

## Evidence and remaining work

The [execution artifact](../audit/data/selector_update_emulation.json)
records **5,391 ingest cases**, each followed by an original selector-helper
call, with zero reference differences. These include all 256 staged selector
bytes for every count 5..14 with ready/blocked latch contexts, all 256 staged
count bytes, ordering, repeated/default AIDs, a fourteen-entry list, failed
receive statuses, pre-mask comparison and invalid-existing-count probes.
Representative write traces and exact receive-boundary injections are saved.

The default initializer separately establishes count 11, step 10 and offset
zero. These two handlers and that initializer explain supported sources for
the selector mapping, but do not exhaust raw writers, interrupts or malformed
transport paths. Complete accounts for all other handlers, variable-width
payload handling, alternate entries and downstream control remain required.
No device traffic, flash operation or engine-setting change was performed.

```text
uv run --with unicorn==2.1.4 python audit/tools/audit_aid_dispatch.py firmware_v2.8.4HF.bin --output audit/data/aid_validation_dispatch.json
PYTHONPATH=<Binary Ninja Python path> python audit/tools/decode_image_ranges.py firmware_v2.8.4HF.bin --ranges 0x601c:0x6042:thumb2,0x604e:0x608c:thumb2,0x6240:0x6274:thumb2,0x6482:0x64b8:thumb2 --output audit/data/selector_update_binaryninja.json
uv run --with unicorn==2.1.4 python audit/tools/emulate_selector_updates.py firmware_v2.8.4HF.bin --output audit/data/selector_update_emulation.json
python -m unittest discover -s tests -t .
```
