# Control-cycle telemetry queue selection

This review applies to the exact 32,000-byte V2.8.4HF application image,
SHA-256 `1ae519ba6194e8f7bdaaa94333a83a9e6fda3b0563f87f7d48383b37288c1780`.
The [bounded Binary Ninja decode](../audit/data/cycle_queue_binaryninja.json)
covers the complete Thumb function `0x76CC..0x77A5`: **218 instruction
bytes and 98 starts**. Every start matches an ordinary item boundary in
the byte-verified IDA export. The [original-byte campaign](../audit/data/cycle_queue_selection_emulation.json)
executes all 85 starts from the `0x76F0` continuation through return.
It explicitly supplies the R4–R7 registers and saved call frame left by
the prologue. The first 13 starts (`0x76CC..0x76EF`) are reviewed
statically; that campaign does not execute their upstream callees.

## Cycle structure

The function first calls `0x4214`, reads byte `0x20078F`, calls the
capture parser `0x59E8` with `(0, byte[0x20078F])`, calls receive ingest
`0x601C`, obtains a control byte from `0x50F0`, stores it back at
`0x20078F`, and calls `0x5CF0` with `(0, control_byte)`. These are direct
instruction facts; each callee's full downstream behavior has its own
review status. The queue-selection tail tests pending byte `0x200712`.
If zero, it skips submission. It later checks `0x200792` and calls the
outgoing scheduler `0x81A8` when nonzero, even if no third-queue item was
accepted.

When pending is nonzero, selector `0x200793` chooses one of five lists.
For 0–3, the matching branch passes a list pointer and its one-byte count
to guarded helper `0x7EFC`. Every other selector value uses slot 4. If the
helper reports busy, the tail returns with pending and selector intact.
On success it clears pending, sets bytes `0x200710/0x200711` to one, and
advances selector 0→1→2→3→4→0; an out-of-range selector also resets to
zero after submitting slot 4. A zero count still counts as accepted by
`0x7EFC`, sets its busy flag, and advances the selector; `0x7FD8` leaves
the destination count unchanged on that zero-copy path.

## Five lists in initialized RAM

The [source-bound artifact](../audit/data/cycle_queue_sources.json) ties
the five direct calls `0x7706/7724/7744/7764/7780` to these initialized
one-byte counts and eight-byte AID blocks. AID numbers come from the
firmware image; profile names and physical signal meanings need separate
evidence.

| Slot | Count byte | List block | Initialized count | AIDs in counted prefix |
|---:|---|---|---:|---|
| 0 | `0x20078A` | `0x2007A0` | 6 | `0, 32, 76, 6, 9, 188` |
| 1 | `0x20078B` | `0x2007A8` | 6 | `84, 75, 4, 40, 39, 16` |
| 2 | `0x20078C` | `0x2007B0` | 7 | `148, 149, 1, 5, 78, 147, 181` |
| 3 | `0x20078D` | `0x2007B8` | 6 | `13, 12, 7, 3, 8, 9` |
| 4 | `0x20078E` | `0x2007C0` | 5 | `105, 148, 149, 78, 16` |

Every unused byte within these initialized blocks is zero. Five
continuation cases use the image's actual source blocks and counts; each
copies its counted prefix into the third queue at `0x200840` and advances
the selector as the instruction trace predicts. Separate synthetic cases
cover each slot with eight entries, no pending work, busy rejection,
out-of-range selector, zero count, and the conditional outgoing call while
USART-ready is clear.
The artifact also inventories every aligned image word pointing into
`0x200788..0x2007C7`: none names the five count bytes or list starts
directly. Computed pointers and existing aliases remain possible.

The helper caps copies at 14, while each source block occupies eight bytes.
A **synthetically preloaded** count of nine for slot 0 copied eight bytes
from `0x2007A0..A7` plus the first byte of slot 1 at `0x2007A8`. This
proves a local cross-slot read if the slot count is corrupted or raised
beyond eight. It does not show that ordinary firmware can create such a
count. Initialized counts are 5–7, and the remaining writers of
`0x20078A..8E` must be traced before assigning normal-path reachability.

The `FFFF` at `0x77A6..A7` is alignment. The four following words at
`0x77A8..B7` are literals `0x200788`, `0x200712`, `0x200710`, and
`0x200711`; they are data, not Thumb instructions. Together with the
[queue owner review](QUEUE_STATE_OWNER_REVIEW.md), this establishes the
direct caller inputs to the third queue while leaving computed-pointer
and interrupt/main-loop writer questions open. No hardware traffic was
sent.

```text
PYTHONPATH=<Binary Ninja Python path> python audit/tools/decode_image_ranges.py firmware_v2.8.4HF.bin --ranges 0x76cc:0x77a6:thumb2 --output audit/data/cycle_queue_binaryninja.json
uv run --with unicorn==2.1.4 python audit/tools/emulate_cycle_queue_selection.py firmware_v2.8.4HF.bin --output audit/data/cycle_queue_selection_emulation.json
python audit/tools/audit_cycle_queue_sources.py firmware_v2.8.4HF.bin --output audit/data/cycle_queue_sources.json
python audit/tools/build_image_ledger.py firmware_v2.8.4HF.bin
python -m unittest discover -s tests -t .
```
