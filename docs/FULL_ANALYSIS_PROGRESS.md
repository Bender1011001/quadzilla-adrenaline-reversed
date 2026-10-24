# Full firmware analysis: live coverage and unresolved work

The full offline-analysis goal is **active and incomplete**. This ledger extends
the bounded reviews; it must not be read as a completed firmware reconstruction.
The existing 145-entry catalog is a supported starting inventory, not an
exhaustive count of execution entries or runtime addresses.

Update: the [startup/persistence review](STARTUP_PERSISTENCE_REVIEW.md) and
[soft float review](SOFT_FLOAT_REVIEW.md) adjudicate twelve additional source
entries, for at least 157 supported starts. Three callable numeric routines
have no identified incoming image call and are not claimed reachable in service.
The original 145-start catalog is retained as the baseline; its semantic coverage
now stands at 116 roles with 29 entries left after the
[outgoing state review](OUTGOING_STATE_REVIEW.md). The
new entries and aliases are recorded separately in
`audit/data/entry_adjudications.json`. Neither inventory is claimed exhaustive.

## Full-image baseline

The byte-verified IDA export now records 13,201 items over the entire 32,000-byte
image. It includes decoded direct branch operands, because IDA's reference graph
omits some targets in unmapped SRAM. Exported item kinds and Thumb state are tool
interpretations and still require correction.

[The byte ledger](../audit/data/image_coverage_ledger.json) accounts for every
address without hiding pending review:

| Classification | Bytes |
|---|---:|
| IDA code candidates awaiting review | 8,787 |
| Explicitly reviewed Thumb instruction ranges | 8,498 |
| Explicitly reviewed ARM instruction ranges | 4,168 |
| IDA data candidates awaiting review | 2,672 |
| Shared AID resolver literal pool | 36 |
| Soft float status pointer literal | 4 |
| Startup descriptors | 36 |
| Initialized RAM data source | 2,208 |
| Indexed SPI request transmit table | 63 |
| Two AID pointer tables | 2,040 |
| AID validation switch offsets | 436 |
| RAM executable source template | 164 |
| Erased trailing `FF` | 2,888 |

Coverage of an address is not proof that its meaning or ISA has been reviewed.
The explicit instruction-range manifest now accepts 12,666 bytes through the
[outgoing state review](OUTGOING_STATE_REVIEW.md). It excludes adjacent literal
pools and alignment. Earlier semantic labels are not automatically promoted to
byte-level classification; their exact ranges still need to be adjudicated.
The ledger explicitly preserves 2,144 item/layout conflicts. These are tool item
spans, not 2,144 bugs or distinct functions. Many arise because initialized data
or erased space was interpreted as instructions.

## New finding: startup relocates executable helpers into SRAM

The startup loop at `0x4114` walks three 12-byte records from `0x96C4` to
`0x96E8`. Each contains `(length, destination, source)`. It uses the byte-copy
helper at `0x8530` for unequal source/destination and a zero-fill helper at
`0x854C` for equal addresses.

| Record | Length | Destination | Source | Operation |
|---|---:|---|---|---|
| `0x96C4` | `0x8A0` | `0x200000` | `0x96E8` | initialized RAM data copy |
| `0x96D0` | `0x3E2` | `0x2008A0` | same address | zero fill |
| `0x96DC` | `0xA4` | `0x200C84` | `0xB114` | executable template copy |

The template's runtime aliases explain direct calls that were absent from the
earlier exported call graph:

| Caller | Decoded runtime target | Source in the image | Supported behavior |
|---|---|---|---|
| `0x6B28` | `0x200C84` | `0xB114` | polls bit 0 of `0xFFFFFF68` until set |
| `0x6B36` | `0x200C94` | `0xB124` | copies words to a supplied address and issues a keyed controller command |
| `0x77E4` | `0x200CFC` | `0xB18C` | issues command `0x5A00000F`, waits through the first helper, returns masked status |

The routines use addresses `0xFFFFFF60`, `0xFFFFFF64`, and `0xFFFFFF68`.
Register writes and instruction arithmetic are directly supported; exact
controller-bit semantics and device effects require the appropriate datasheet
and further caller review. These are in-image helpers, not evidence that the
missing updater bootloader or recovery protocol has been recovered.

The startup source-to-runtime mapping is an important distinction: literal pools
and relative branches are copied with the code. Merely creating ROM functions
cannot recover all runtime call edges.

## ISA and entry-boundary corrections under investigation

IDA currently decodes several `FFFF` alignment halfwords together with subsequent
valid Thumb instructions as NEON opcodes (for example `VSRI.32` at `0xB122`
swallows the `PUSH` at `0xB124`). ARM7TDMI cannot execute NEON instructions.
Bounded Binary Ninja decoding beginning at `0xB124` recovers an ordinary Thumb
routine; the same pass decodes `0xB18C` and the startup/copy helpers.

The [SPI/PDC review](SPI_TRANSFER_REVIEW.md) adjudicates `0x6B48` as a
Thumb predicate; IDA's NEON item at `0x6B46` overlaps its first instruction.
The preceding halfword remains outside the reviewed instruction body.
Other invalid-ISA candidates occur around
entry starts such as `0x7B04`, `0x7BE8`, `0x7BF0`, and `0x8530`.
The known catalog already contains some of these exact starts while the IDA item
spans overlap them. Shared entry recognition does not prove correct surrounding
decoding. Those spans remain pending, and the current 145-entry inventory will
be revised only with explicit entry and runtime-alias adjudication.

## Artifacts and reproduction

- [Full IDA item export](../audit/data/ida_image_items.json): no vendor image bytes;
  instructions, references, item boundaries and mode candidates only.
- [Bounded Binary Ninja decode](../audit/data/startup_relocation_binaryninja.json).
- `audit/tools/ida_export_image_items.py`: `IMAGE OUTPUT` IDAPython arguments;
  use a database copy and the headless procedure from the earlier verification.
- `audit/tools/build_image_ledger.py IMAGE`: regenerate address accounting.
- `audit/tools/decode_image_ranges.py IMAGE --ranges START:END:ISA,... --output OUTPUT`:
  explicit-mode bounded decoder; available ISA decoders are a superset of ARMv4T.

## Selector and response connection

The [control selector review](CONTROL_SELECTOR_REVIEW.md) traces the captured
signed source through the readiness latch into the `0x506C` mapping helper,
then separates its returned control byte from its stored AID 9 response.
It adds one role and 112 instruction bytes, including a supported disposition
for two unreachable instruction starts. 70,672 original-byte calls agree with
the bounded model. Parameter validation, later writers, application decoding
and the full downstream control calculation remain incomplete.

## Validation dispatch and selector updates

The [dispatch audit](AID_DISPATCH_SELECTOR_UPDATES.md) establishes all 256
AID destinations using both signed source offsets and original selector
instructions. It classifies 436 table bytes and 206 instruction bytes for
the gate/loop and AID 9/15 handlers. 5,391 ingest cases, each followed by the
original selector helper, reproduce count bounds, sequential update ordering
and retained working selectors. The receive boundary is scripted, not a
transport execution claim. The other 55 non-default handler accounts remain
pending this review; role counts stay at 109/36.

## Compound updates and cross-AID staging

The [compound-handler review](COMPOUND_AID_UPDATE_REVIEW.md) adds eleven
handler accounts and 458 instruction bytes. Thirteen of the 57 non-default
handlers now have bounded update accounts; 44 remain pending. The original
walker plus two scripted receive results reproduce partial AID 146 staging
later reaching working state through AID 154 fall-through. A separate repeated
16-bit-compare/eight-bit-store case sets the update flag without changing
the final byte. Full transport reachability, intended ranges and downstream
impact remain unresolved. Entry-role counts stay at 109/36.

## Complete bounded local handler accounts

The [remaining-handler review](REMAINING_AID_UPDATE_REVIEW.md) closes the
57-handler local queue and classifies all 1,882 instruction bytes of the
dispatcher and its four parent-frame continuations. It adds 1,218 reviewed
bytes and four baseline roles. 22,703 ingest calls check clamp/curve paths,
coupled limits, width distinctions, the default-initializer trigger and
AID 226 floating configuration. A two-byte reader can return a retained upper
echo byte after a one-byte handler store. Complete variable-width admission,
all staging/echo writers, persistence and downstream control remain open;
closing this local queue is not completion of the full parameter goal.

## Outstanding requirements

The [SPI/CAN command audit](SPI_CAN_CONTROLLER_REVIEW.md) establishes an
MCP2515-compatible interpretation of the initialized SPI buffers and register
sequence. It clarifies the two receive layouts and TXB2 data-only output.
It does not itself increase instruction coverage. The subsequent
[capture parser review](CAPTURE_PARSER_REVIEW.md) adds 692 instruction bytes
for the complete normal-service body, while retaining 108 labeled baseline
roles and 37 pending entries. It documents nine header matches, scalar
formulas, retained outputs, an absent local DLC guard and a byte-narrowing
discontinuity. Coefficient writers, downstream consumers, DMA/IRQ ordering,
hardware topology and live acceptance remain follow-up work. The owner's
[V2.2 board report](BOARD_V2_2_COMPONENTS.md) is separate hardware context,
including the provisional 16 MHz crystal and conditional 250 kbit/s calculation.

The [AID table boundary review](AID_TABLE_BOUNDARY_REVIEW.md) now covers 512
resolver calls and 256 controlled single-AID reader calls. AID 255 crosses both
table boundaries, with a reproduced SRAM write alias and an unmapped response
read in emulation. The complete pointer map is available; individual parameter
semantics, all writer constraints and hardware consequences remain open.

The [SPI output state review](SPI_STATE_MACHINE_REVIEW.md) establishes
state progress that discards transfer-helper results and signed remainder/quotient
byte packing for controlled negative inputs. Outstanding questions include whether
the scripted readiness change is possible on hardware, who owns the ENDRX
status used by state 5, and whether negative `0x200604` values reach packing.
These remain specific caller/scheduling follow-ups rather than asserted live defects.

1. Correct mode/item boundaries, map relocated executable aliases, and adjudicate
   every additional entry candidate (including interrupt/vector alternate entries).
2. Give every cataloged and newly accepted entry a reviewed account of inputs,
   outputs, side effects, references, confidence and unresolved questions.
3. Complete startup/clock/interrupt, persistence, receive/transmit-state,
   variable-width-AID, control arithmetic and sensor/capture analyses.
4. Trace alternate raw-staging consumers and interrupt interactions; validate
   potential defects with bounded models and instruction evidence.
5. Replace remaining candidate classifications with supported byte-range roles,
   publish the resulting architecture/reference, and complete the offline audit.

No hardware traffic, flash operation or engine-setting change was performed.
