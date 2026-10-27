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
now stands at 145 roles with no unlabeled baseline entries after the
[final baseline-entry review](FINAL_BASELINE_ENTRIES_REVIEW.md). The
new entries and aliases are recorded separately in
`audit/data/entry_adjudications.json`. Neither inventory is claimed exhaustive.
The empty baseline semantic queue does not close the full analysis. The
[residual code audit](RESIDUAL_CODE_ADJUDICATION.md) and
[PC-literal audit](PC_LITERAL_POOL_REVIEW.md) give every image byte a supported
classification. Additional entry discovery, complete semantic contracts,
global writer/consumer paths and subsystem integration remain open.

The [execution-discovery review](EXECUTION_DISCOVERY_REVIEW.md) reconciles
354 raw direct-call sites, 1,114 direct branches and 48 code-address data
windows, including relocated source aliases. It establishes no new independent
entry; 157 remains a supported minimum. The subsequent
[indirect-transfer audit](INDIRECT_TRANSFER_PROVENANCE.md) classifies the local
register sources of all 203 `BX` sites and six other computed PC writes.
Programmable AIC values, frame integrity, synthesized/mutated pointers and
the retained data windows remain part of the entry-discovery work.

The [AIC installation review](AIC_VECTOR_INSTALLATION_REVIEW.md) composes seven
selected setup pieces across 16 synthetic cases. It establishes their vector
write set and the untouched slot-31 boundary, with a complete-startup and
exhaustive-writer claim explicitly excluded.

The [SPI-template provenance review](SPI_TEMPLATE_PROVENANCE_REVIEW.md) gives
two retained code-address byte windows an established overlapping SPI-data
interpretation. Six original-byte cases verify selected transmit descriptor
boundaries and blocked admission. It adds no source entries or instruction
bytes and does not close exhaustive writer/consumer provenance.

The [scalar telemetry arithmetic review](SCALAR_TELEMETRY_REVIEW.md) now adds
a complete local 32-bit calculation account and 10,312 original helper calls,
each followed by the original caller cap/floor/store slice. All 349 helper
starts are visited with zero model differences. It corrects the incoming
R0/R2 interpretation and signed lower-floor account; upstream writer bounds,
complete caller execution and physical meaning remain open.

The [complete-control integration review](CONTROL_SCALAR_INTEGRATION_REVIEW.md)
executes 325 original `0x50F0` calls, checking scalar inputs/results, both
table extents, the actual caller store, timer admission and periodic backdown
dispatch. It visits 495/574 main starts and explicitly retains 79 unvisited
starts. Scalar axes are bounded to 0..19 under intact-frame/stable-input
assumptions; a duplicated source-word load leaves an asynchronous-writer
condition open. Full response contracts and remaining branch states are pending.

The [control-response arithmetic review](CONTROL_RESPONSE_ARITHMETIC_REVIEW.md)
adds exact integer/float/filter accounts for `0x53A2..0x55A6`, with 1,072
matching slice executions and all 196 starts visited. Two consecutive complete
control calls demonstrate retained `0x200BC2/BC3` dependencies. NaN source
paths, numeric status effects, physical units and global writer bounds remain
open, along with the other unexercised main-control branches.

The [knot writer/consumer review](KNOT_UPDATE_CONSUMER_REVIEW.md) composes
306 update/control/readback sequences, including 1,224 whole control calls.
It establishes the normal knot-handler bound, in-place scaled-word reductions,
retention after a handler-driven mode change, and restoration by same-value
updates while raw readbacks remain unchanged. A scripted receive boundary and
stable state remain explicit; global writer exclusion is not claimed.

The [global store inventory](GLOBAL_STORE_INVENTORY_REVIEW.md) inventories
1,063 raw store sites over all 8,051 accepted starts and links the 15 indexed
forms to local contracts. Original-byte vector-path execution demonstrates
a conditional scratch alias into the scalar table's first 128 bytes, followed
by a controlled signed-cell read. Actual remap state, later restoration and
global target-set closure remain open; the initial 0..100 table contents are
not a whole-execution invariant by themselves.

The [startup table-lifetime review](STARTUP_TABLE_LIFETIME_REVIEW.md) follows
the original post-descriptor setup and first cycle in 16 ready-state cases,
plus two bounded waits. No sampled later setup or first-cycle path restores
the overwritten prefix. The first scalar call bypasses lookup in those
initial states; no first-cycle harmful consumption is inferred. Remap state,
later cycles and asynchronous writers remain open.

The [generic writer/alias admission review](GENERIC_WRITER_FOOTPRINT_REVIEW.md)
bounds the three identified direct copy/fill callers and all byte-AID resolved
staging extents, with 768 original walker calls. Three complete original
cycles establish AID-255 response-coefficient writes through valid CRC and
incomplete-width paths, plus a damaged-CRC negative control. Scalar and response
models confirm the controlled computational effects; physical delivery,
authentication and global writer exclusion remain unproven.

## Full-image baseline

The [reviewed Thumb store-provenance pass](THUMB_STORE_PROVENANCE_REVIEW.md)
represents all 1,039 selected stores over 6,813 starts and 118 normal-entry roots,
including four previously bounded dispatches. It derives 791 conditional fixed
addresses and 137 SP-relative stores, retaining 111 unresolved sites and 24
excluded ARM/template stores. These are address obligations, not new defects;
entry, frame, pointer and callee conditions prevent global exclusion claims.

The [callback transitive store-address review](CALLBACK_TRANSITIVE_STORE_REVIEW.md)
accounts for nine fixed numeric wrappers and two flag helpers. The whole ARM
numeric-region superset has seven SP-relative stores and one fixed status-byte
store; its ordinary transfer graph stays inside reviewed code. Composed address
nonoverlap with P is conditional on pointer, register, frame and normal-entry
contracts. Numeric defects, DMA and unrelated global writers remain open.

The [local callback store-contract review](CALLBACK_STORE_CONTRACT_REVIEW.md)
accounts for all 114 stores across seven returning callback bodies, with 110
fixed destinations and four entry-SP-relative stores under explicit pointer,
callee-preservation and stack assumptions. All fixed sites agree with existing
observations. Twenty calls to eleven entries remain transitive obligations;
local nonoverlap with P does not close the asynchronous/global writer proof.

The [selected callback interleaving review](CONTROL_CALLBACK_INTERLEAVING_REVIEW.md)
pauses original control between repeated percent loads, executes original
callback bodies with a saved CPU context/separate synthetic stack, and resumes
with memory effects retained. All 33 cases preserve P and match scalar/response
models; TC2 numeric state changes demonstrably reach the response consumer.
ARM exception entry, all callback states and global writer exclusion remain open.

The [peripheral-pointer fixture review](PERIPHERAL_POINTER_FIXTURE_REVIEW.md)
corrects four transport harnesses to retain TC2's initialized `0x200728` base.
Original callback reads distinguish that slot from USART's direct status
address. All four prior artifacts reproduce unchanged after correction. This
removes an unused artificial pointer assumption before interrupt composition;
it does not close global pointer-writer or asynchronous-stability requirements.

The [capture-percent producer/control review](CAPTURE_PERCENT_CONTROL_REVIEW.md)
connects the known `0x2005F0` writer to 512 original cycles across all payload
byte values and two DLCs, plus six retained-value cycles. It establishes local
producer range and observed same-cycle ordering; retention and asynchronous
global writer exclusion remain separate. No entry/coverage completion follows.

The [alternate-axis and clamp review](CONTROL_AXIS_CLAMP_REVIEW.md) adds 265
complete calls, an instruction-level conditional 0..19 alternate-axis bound,
original stretch-model comparisons and directed lower/in-range/upper timer
clamp cases with both clock-status admissions. All remaining main starts
execute: the six-suite union is 574/574. This is instruction coverage only;
global writers, parameter admission, asynchronous paths, numerical status and
the wider subsystem/documentation requirements remain incomplete.

The [full-control response review](FULL_CONTROL_RESPONSE_REVIEW.md) adds 288
complete original calls with actual-boundary scalar/response inputs and exact
byte, derived-word and full-filter comparisons. Twenty-nine additional main
starts bring the five-suite union to 555/574. Finite-source intermediate
overflow is checked, but source NaNs, numeric status effects, alternate axis
and upper-clamp starts, global writers and asynchronous ordering remain open.

The [control reinitialization review](CONTROL_REINITIALIZATION_REVIEW.md)
adds 32 complete returns and one readiness-budget wait. Sixteen triggered calls
execute original peripheral setup and all six initializers, retaining its 221
non-stack writes and checking lookup retention and caller byte/count updates.
The four-suite main-start union reaches 526/574. No asynchronous timeout or
physical peripheral behavior is inferred from the blocked synthetic case.

The [idle-control integration review](IDLE_CONTROL_INTEGRATION_REVIEW.md)
adds 150 complete calls, including three persistent two-call sequences. It
establishes original gate overwriting of the earlier entry-active override,
state-transition delay before fresh consumption, accumulator model agreement
and actual caller saturation. The three-suite union reaches 520/574 main
starts. Supplied events do not establish interrupt timing or live admission;
setup, other branches and global writer bounds remain open.

The [retained-sample and timer-branch review](CONTROL_RETENTION_BRANCH_REVIEW.md)
adds 120 complete original control calls, checking both sample-equality gates,
the 601 capture threshold, wrapping counter increment, retained-source refresh
and 24 optional timer-floor cases. Twelve additional main starts bring the
union with the initial integration suite to 507/574; 67 remain listed. Setup
at count 2001, the idle branch, upper timer clamp and global writers remain open.

The byte-verified IDA export now records 13,201 items over the entire 32,000-byte
image. It includes decoded direct branch operands, because IDA's reference graph
omits some targets in unmapped SRAM. Exported item kinds and Thumb state remain
tool interpretations retained for provenance; the ledger records their accepted
source-bound dispositions.

[The byte ledger](../audit/data/image_coverage_ledger.json) accounts for every
address without equating classification with complete semantic review:

| Classification | Bytes |
|---|---:|
| IDA code candidates awaiting review | 0 |
| Explicitly reviewed Thumb instruction ranges | 14,320 |
| Explicitly reviewed ARM instruction ranges | 4,680 |
| IDA data candidates awaiting review | 0 |
| Remaining PC-relative literal words | 1,788 |
| Remaining literal-pool FF alignment | 14 |
| Residual function NOP/FF alignment | 76 |
| Integer interworking NOPs | 6 |
| Reset-request literal words | 8 |
| USART wrapper/flag literal words | 20 |
| Ratio scorer rows and coefficients | 104 |
| SPI/ADC zero alignment | 1 |
| Startup literal pools and alignment | 86 |
| Callback and predicate alignment/literals | 12 |
| Input gate literals/alignment | 38 |
| Backdown and stretch literals/alignment | 30 |
| Capture scalar jump tables/literals/alignment | 90 |
| Scalar helper literals/alignment | 86 |
| Main-control literals/alignment | 314 |
| TC0 helper alignment | 2 |
| USART literal pools/alignment | 126 |
| Cycle queue alignment and literal pool | 18 |
| Queue helper alignment and state-base literals | 10 |
| Receive type jump table | 6 |
| Receive alignment and state-base literal | 6 |
| Shared AID resolver literal pool | 36 |
| Soft float status pointer literal | 4 |
| Startup descriptors | 36 |
| Initialized RAM data source outside the capture table | 1,808 |
| Capture scalar 20×20 initialized table | 400 |
| Indexed SPI request transmit table | 63 |
| Four ADC lookup tables | 2,284 |
| Two AID pointer tables | 2,040 |
| AID validation switch offsets | 436 |
| RAM executable source template | 164 |
| Erased trailing `FF` | 2,888 |

Coverage of an address is not proof that its meaning or ISA has been reviewed.
The explicit instruction-range manifest now accepts 19,000 bytes through the
[residual code audit](RESIDUAL_CODE_ADJUDICATION.md). It excludes adjacent literal
pools and alignment. These byte roles do not prove complete branch states,
caller invariants, writer coverage, or downstream subsystem semantics.
The ledger explicitly preserves 3,376 item/layout conflicts. These are tool item
spans, not 3,376 bugs or distinct functions. Many arise because initialized data
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
5. Consolidate the global architecture/reference and discriminating hardware
   checklist, then audit every original completion requirement against its
   authoritative evidence. Complete byte classification alone does not satisfy
   the remaining semantic, entry-discovery and integration requirements.

No hardware traffic, flash operation or engine-setting change was performed.
