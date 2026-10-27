# Global memory-store inventory and conditional vector/table alias

The subsequent [Thumb provenance review](THUMB_STORE_PROVENANCE_REVIEW.md)
adds conditional CFG address accounts for 1,039 of this inventory's sites,
while preserving unresolved and excluded sites. The raw inventory remains
the complete store-form baseline, not a proof of destination bounds.

This pass inventories memory-store instructions in the exact V2.8.4HF image,
SHA-256 `1ae519ba6194e8f7bdaaa94333a83a9e6fda3b0563f87f7d48383b37288c1780`.
The [raw store inventory](../audit/data/store_inventory.json) scans all 8,051
accepted instruction starts, including the known copied-helper source bodies.
It uses raw ARMv4T store encodings and checks its classification against the
accepted explicit decode. No store/non-store disagreement remains.

This is a finite instruction inventory, not proof that every possible runtime
write target has been established. It covers the accepted code map rather
than excluding undiscovered ISA/code alternatives, and does not inventory
DMA- or peripheral-initiated memory writes.

## Inventory and address evidence

| Raw addressing form | Sites |
|---|---:|
| Thumb immediate-offset stores | 911 |
| Thumb register-offset stores | 15 |
| Thumb PUSH register lists | 70 |
| Thumb SP-relative stores | 50 |
| STM register lists | 14 |
| ARM single-data stores | 3 |
| **Total** | **1,063** |

There are 134 sites with an explicit SP base, 167 with a literal load into
the base register immediately preceding the store, and 360 with IDA destination
annotations. These counts overlap. Selected execution artifacts provide
observed destinations for 98 sites; runtime helper addresses are normalized
to their copied source coordinates. Per-site records preserve the evidence
source, observed size/address, instruction form and IDA ownership.

An immediate offset is relative to a register, not an absolute address.
Likewise, a non-SP base can hold a pointer derived from SP, as the known
rejection-list writes demonstrate. SP addressing still needs frame bounds
and integrity. An adjacent literal supplies a conditional straight-line
witness: it does not exclude a branch entering at the store or a different
register value from another path. IDA annotations remain tool interpretations.
Observed destinations are examples, not exhaustive target sets.

## Indexed sites connected to existing contracts

All 15 raw register-offset stores have the following local accounts. The
table links roles, without claiming globally proven target sets:

| Site(s) | Established local context |
|---|---|
| `0x41AA` | Indexed AIC fallback-vector loop; [installation review](AIC_VECTOR_INSTALLATION_REVIEW.md). |
| `0x4208` | 32-word ADC sample filter; [ADC pipeline](ADC_PIPELINE_REVIEW.md). |
| `0x4668`, `0x468C` | Moving-average append stores through caller buffers; [helper contracts](CONTROL_HELPER_REVIEW.md). |
| `0x7400`, `0x7414` | Conditional vector scratch copy and five-word replacement, analyzed below. |
| `0x74AE`, `0x74BE`, `0x74F6` | AIC mask/enable/setup writes through initialized base pointer; [PIO/AIC review](PIO_INTERRUPT_REVIEW.md). |
| `0x77CA` | Startup's repeated AIC end-of-interrupt writes using the base stored at `0x200798`; raw store and reset-continuation context retained in the inventory. |
| `0x7E30`, `0x7E48` | Deferred-AID stack list and subsequent copy; [reader capacity review](FRAME_READER_REVIEW.md). |
| `0x7EE8` | CRC append into the caller's frame buffer; [frame builder](FRAME_READER_REVIEW.md). |
| `0x7FA0`, `0x7FC0` | Retained-AID stack list and copy-back; [queue-filter boundary](OUTGOING_QUEUE_FILTER_REVIEW.md). |

Generic pointer writes also occur in immediate-offset forms. In particular,
byte-copy site `0x853C`, byte-fill site `0x8556`, and parameter walker sites
`0x7D2A/0x7D5A` require caller ranges or resolver provenance; they cannot be
removed from the global audit merely because the raw offset is zero.

## Reproduced scalar-table writer outside the parameter handlers

The initialized scalar lookup occupies `0x200000..0x200190` (400 bytes,
exclusive end), initially all 0..100. The conditional vector-page maintenance
entry `0x73E4` uses **that same base address** as a 128-byte scratch area.
The [earlier vector account](ADC_INIT_VECTOR_REVIEW.md) described its copy;
this pass connects it to the scalar consumer and executes the original path.

The [alias artifact](../audit/data/vector_table_alias.json) starts by executing
the original descriptor initializer `0x4114`, including the copied executable
template. It then provides explicit synthetic page-zero contents and a
physical application view at `0x104000` containing the matching image.
Flash-ready status is supplied as 1 and the synthetic AIC mask as `0x15`.
No hardware implements these registers in this harness.

The helper compares word `[0x4]` with wrapped `word[0x104004]+0x1000`:

| Synthetic condition | Original instruction effects |
|---|---|
| Equal | Return `0x200000`; leave the scalar table unchanged; no staging/program request. |
| Different | Copy 32 words from page zero to `0x200000` at `0x7400`; replace words 1–5 at `0x7414` with application words plus `0x1000`; invoke the original wrapper and copied flash helper. |

The different branch makes **37 word writes** into the first 128 table bytes.
The remaining 272 table bytes stay unchanged in these cases. The copied flash
helper then stages 32 words at synthetic address zero and writes command
`0x5A000001` to synthetic `0xFFFFFF64`. The ready poll, AIC save/disable/enable
helpers and page-write helper all execute original bytes. Neither the flash
operation nor remap behavior is modeled as hardware; the staging writes are
emulator-memory effects only.

Two different-branch inputs are checked: a clearly labeled synthetic sentinel
vector page, and a synthetic page-zero alias of the supplied image's first
128 bytes. The latter does not claim to identify the missing bootloader or
the board's actual remap state.

## Later signed scalar consumption

After each vector case, a separate controlled call of `0x4D38` preserves the
table and supplies its other state explicitly. Row 0, column 3 makes the
original `LDRSB` at `0x4E82` read `0x200003`:

| Case | Table byte | Signed value | Scalar R0 return |
|---|---:|---:|---|
| Comparison equal | 10 | 10 | 208 |
| Different, sentinel page | `0xA0` | -96 | `0xFFFFFE90` |
| Different, image-prefix page | `0xEA` | -22 | `0xFFFFFE90` |

The returns agree with the existing 32-bit scalar model. This is a concrete
conditional writer/consumer connection, not a claim that the entire remaining
startup reaches this later scalar state. It also does not show a particular
timer waveform or negative final telemetry; the caller's cap/floor is a
separate operation. The [knot writer bound](KNOT_UPDATE_CONSUMER_REVIEW.md)
remains conditional on its own reviewed writers and stable cap state.

Consequently, the initial scalar-table range 0..100 cannot by itself justify
a whole-execution nonnegative-cell invariant. An existing original-code path
can write vector words over its prefix. Whether the branch executes on the
owner's board, whether later initialization restores the table, how aliases
map at that time and which other writers exist remain explicit open questions.
No live malfunction or defect severity is assigned.

The subsequent [startup lifetime review](STARTUP_TABLE_LIFETIME_REVIEW.md)
executes the later setup and selected first cycles without function-result
stubs. It finds no table restoration in those paths, while explicitly
recording that their first scalar call bypasses the lookup. Later cycles and
actual remap/configuration state remain unverified.

## Global audit priorities now made concrete

1. Trace caller/resolver ranges for generic copy/fill and parameter-pointer
   stores, including raw staging and the AID-255 boundary.
2. Reconcile all startup/restore writers of the three control lookup regions,
   starting with the demonstrated `0x200000` scratch alias.
3. Establish shared-state and indirect-count writers needed by the documented
   stack-list and repeated-load conditions.
4. Resolve remaining register destinations and distinguish runtime observations
   from globally proven bounds. No target-set closure follows from this inventory.

```sh
python audit/tools/emulate_vector_table_alias.py firmware_v2.8.4HF.bin --output audit/data/vector_table_alias.json
python audit/tools/audit_store_inventory.py firmware_v2.8.4HF.bin --output audit/data/store_inventory.json
python -m unittest discover -s tests -t .
```

The alias artifact is generated first because the inventory incorporates its
observations. No hardware, host-device access, flashing or settings change
was performed. The full firmware-analysis goal remains active.

The [generic writer footprint review](GENERIC_WRITER_FOOTPRINT_REVIEW.md) now bounds the identified direct copy/fill callers and resolved payload-data intervals. It preserves metadata/stack and other-writer limits, and connects the AID-255 response interval to complete-cycle consumers.
