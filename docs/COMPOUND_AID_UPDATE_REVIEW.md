# Compound AID updates and cross-AID staging consumption

This review covers eleven additional handlers in the exact V2.8.4HF image,
SHA-256 `1ae519ba6194e8f7bdaaa94333a83a9e6fda3b0563f87f7d48383b37288c1780`.
It adds **458 instruction bytes** in `[0x6274,0x63AC)` and
`[0x63F0,0x6482)`, excluding the intervening literal pool. All 227 starts
match the byte-verified IDA export and [Binary Ninja decode](../audit/data/compound_update_binaryninja.json),
and all are visited in original-byte execution. Superset decoding and an
ARM926 functional surrogate do not establish target timing or live behavior.

The [execution artifact](../audit/data/compound_update_emulation.json) records
5,632 sweep ingests and 39 asymmetric-word/sequence ingests, with zero model
differences. State snapshots and ordered non-stack writes are compared with
the byte-memory reference, including writes that retain the same final byte.
The receive-result boundary at `0x8038` is explicitly scripted. The cross-AID
example additionally executes the original payload walker `0x7CC4`; packet
framing, CRC, physical interfaces and IRQ interleaving remain outside it.

## Handler contracts and storage

Each handler runs within the `0x601C` frame and returns to the shared loop
at `0x604E`; these are not independent ordinary callable functions. No
peripheral accesses occur. R4–R11 and the original stack are preserved in
the checked complete ingest calls; scalar R0 is not a semantic result.

Unless noted otherwise, each field is copied only if its current working
value differs, and each changed field sets byte `0x200AC4=1`. This is called
the update flag locally; its complete scheduling/persistence role remains
unreviewed. Multiple changed fields may store the flag repeatedly. No local
range clamp is present in these eleven handlers beyond AID 152's two bit
extractions. Profile names below are descriptive labels, not inferred units.

| AID / profile label | Staging source | Working update |
|---|---|---|
| 10 / absent from the 14 profiles | Byte `0x200B01` | Byte `0x200AFF`. |
| 64 / absent from profiles | Byte `0x200B1B` | Byte `0x2006F6`; when changed, also zero 32-bit locations `0x200748` and `0x20074C`. |
| 80 / absent from profiles | Bytes `0x200B08..09` | Separately compare/copy to bytes `0x2006D1..D2`. |
| 81 / Boost Defuel Setting | Bytes `0x200B0A..0B` | Separately compare/copy to bytes `0x2006D3..D4`. |
| 82 / absent from profiles | Bytes `0x200B0C..0D` | Separately compare/copy to bytes `0x2006D5..D6`. |
| 150 / EGT Defuel Setting | Three bytes at `0x200B0E` | First byte to `0x2006D7`; little-endian trailing 16-bit value to `0x2006D8`. |
| 151 / absent from profiles | Three bytes at `0x200B11` | First byte to `0x2006DA`; trailing 16-bit value to `0x2006DC`. |
| 152 / Turbo Timer Setting | Three bytes at `0x200B02` | First byte bit 0 to `0x2006DF`, bit 1 to `0x2006DE`, each normalized to 0/1; trailing 16-bit value to `0x2006E0`. Other first-byte bits are ignored here. |
| 153 / High Idle Delay Setting | Three bytes at `0x200B14` | First byte to `0x2006E2`; trailing 16-bit value to `0x2006E4`. |
| 154 / Warmup Mode Setting | Three bytes at `0x200B05` | First byte to `0x2006CF`; trailing 16-bit value is compared against byte `0x2006D0`, then stored with an eight-bit store if unequal. Always continues into AID 146 processing. |
| 146 / MPG Offset | Bytes `0x200B17..18` | Low byte to `0x2006F4`, high byte to `0x2006F5`, with the additional effects below. |

The [source-bound dispatch map](../audit/data/aid_validation_dispatch.json)
binds these AIDs to their source targets and staging/response pointer slots.
These handlers do not themselves write their response-pointer destinations;
read support and later response-population paths remain distinct questions.
The [configuration mirror review](INITIAL_STATE_CONFIG_REVIEW.md) now traces
the startup response-population path for AID 151 and records its local
halfword-byte overwrite.
The five unprofiled AIDs demonstrate implemented update paths beyond profile
declarations, without establishing their application meaning.

## AID 146 side effects and retained values

If the low staged byte differs from `0x2006F4`, copy it, zero the 32-bit
location `0x20073C`, and set the update flag. If the high staged byte differs
from `0x2006F5`, copy it, then compute:

```text
word[0x200AC8] = floor(125 * high_byte / 100)
word[0x200ACC] = floor(25 * word[0x200AC8] / 100)
```

The first division uses the reviewed signed runtime and the second uses the
unsigned runtime; the byte-derived operands are nonnegative and cannot
overflow. At input 255, the two outputs are 318 and 79. Each quotient is
stored as a 32-bit value. No physical units are assigned here.

If the high byte is unchanged, both derived locations are retained, even
when the low-byte path ran. If the low byte is unchanged, `0x20073C` is
retained. AID 64 similarly retains its two accumulator locations when its
staged byte is unchanged. These are local update policies, not proof of
incorrect retained state; complete initialization and consumer analysis are
still required.

## Confirmed AID 154 fall-through

Both outcomes of the comparison at `0x62AA` reach `0x62B6`, AID 146's
handler start. If unequal, the intervening byte store and update-flag store
execute before falling through. If equal, the conditional branch reaches
the same target directly. There is no check that AID 146 appears in the
current receive-result list.

Consequently, processing AID 154 also consumes the existing AID 146 staging
bytes, independently of whether the warmup fields changed. This is a confirmed
control/data-flow relationship, not a conjecture from decompiler case layout.
Its intended behavior is not documented by a firmware specification.

The first warmup byte and narrowed second field are the enable/limit inputs
used by the separately reviewed [readiness latch](CONTROL_HELPER_REVIEW.md).
That establishes another parameter-to-selector connection; all readiness-state
writers, ordering and physical interpretations remain outside this handler
account.

## Partial staging write reaches working state through another AID

The bounded sequence begins with AID 146 staging and working bytes both
`0A 14` and nonzero canaries in the affected accumulator/derived locations.

1. Execute the original type-1 payload walker with bytes `92 4D` in hex:
   AID 146 and only its first value byte. It writes `4D` to `0x200B17`,
   retains the old high byte `14`, reports AID 146 and returns status 2.
2. Supply that failed result to the original ingest entry. Its existing
   success gate skips validation, retaining working byte `0x2006F4=0A`.
3. Execute the original walker with `9A 00 00 00`: a complete AID 154
   value. It reports only AID 154 and returns status 1.
4. Supply that successful result to ingest. The AID 154 path falls through
   into AID 146, copies the retained staged `4D` to `0x2006F4`, zeros
   `0x20073C` and sets the update flag. The high byte and its derived
   locations remain unchanged.

The artifact retains both walker results, reported lists, receive-boundary
injections and ingest write traces. This establishes a specific path by
which a failed partial staging update can later be applied through another
AID. Actual acceptance of corresponding frames, application behavior,
downstream physical effects and defect severity are not established by this
scripted receive contract. The earlier [partial-write review](OFFLINE_WRITE_PATH_REVIEW.md)
documents the broader staging-before-validation behavior.

## Repeated 16-bit comparison / eight-bit store

AID 154 assembles both trailing bytes, compares that 16-bit value with a
single working byte, and stores only the low byte. For a staged value
`0x1234` with working byte already `0x34`, it nevertheless stores `0x34`
and sets the update flag. Repeating the same ingest after clearing the flag
repeats both stores. Both calls are executed and recorded.

Any staged value above 255 cannot equal that byte-sized working field.
This establishes width loss and a repeatedly taken update path. It does not
establish an intended 16-bit working limit, a valid application range, or a
measured malfunction. The direct source and byte comparison/store widths
are retained rather than silently interpreting the field as a 16-bit value.

## Coverage, queue and reproduction

The sweeps vary each staged byte value 0..255 for each handler in changed
and post-application working contexts. Thirty-five additional cases distinguish
low/high byte order with values 0, 1, 255, 256, `0x1234`, `0x8000`, `0xFFFF`.
Four sequence ingests cover failed-partial/successful-cross-AID application
and repeated narrowing. Ordered stores as well as final fields match the model.

At this review stage, thirteen of the 57 non-default handlers had bounded update accounts:
these eleven plus AIDs 9 and 15. The subsequent [remaining-handler account](REMAINING_AID_UPDATE_REVIEW.md)
closes the local handler queue at 57; full transport, writer and consumer analysis remains incomplete.
Baseline entry-role counts remain 109 reviewed / 36 pending because these
handlers belong to the already labeled dispatcher. Total reviewed instruction
bytes are 9,564. Other handlers, alternate entries, transport state machines,
coefficient writers and downstream control still require their full accounts.

```text
PYTHONPATH=<Binary Ninja Python path> python audit/tools/decode_image_ranges.py firmware_v2.8.4HF.bin --ranges 0x6274:0x63ac:thumb2,0x63f0:0x6482:thumb2 --output audit/data/compound_update_binaryninja.json
uv run --with unicorn==2.1.4 python audit/tools/emulate_compound_updates.py firmware_v2.8.4HF.bin --output audit/data/compound_update_emulation.json
uv run --with unicorn==2.1.4 python audit/tools/audit_aid_dispatch.py firmware_v2.8.4HF.bin --output audit/data/aid_validation_dispatch.json
python -m unittest discover -s tests -t .
```

No device traffic, programming, flash operation or engine setting was used.
