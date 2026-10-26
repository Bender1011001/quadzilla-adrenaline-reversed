# Direct-transfer and code-address discovery audit

This pass audits execution-entry evidence in the exact V2.8.4HF image,
SHA-256 `1ae519ba6194e8f7bdaaa94333a83a9e6fda3b0563f87f7d48383b37288c1780`.
It covers the 19,000 accepted ARM/Thumb instruction bytes and the 138 source
instruction bytes of the three relocated Thumb helpers. The latter remain
inside the separate 164-byte executable-template ledger category, which also
includes their literals and alignment.

The [source audit](../audit/data/execution_discovery_audit.json) decodes raw
ARMv4T branch encodings at 8,051 accepted instruction starts. All 354 direct
calls and 1,114 direct branches resolve to accepted instruction starts with
the expected ISA. Every direct-call destination is a documented source entry
or a documented runtime alias. Raw targets agree with the byte-verified IDA
export wherever it provides a decoded direct target. The 354 count is call
**sites**, not distinct functions or call-graph edges.

This pass establishes no additional independent source entry. The supported
minimum stays at 157 (145 baseline plus 12 supplemental starts). This is a
bounded discovery result; indirect/computed targets, synthesized addresses,
and complete runtime provenance remain open. Canonical addresses in this
audit cover image coordinates and the known SRAM copy; other physical/remap
aliases are not normalized by the pointer-window scan.

## Relocated call targets

The source template `0xB114..0xB1B8` is copied to `0x200C84..0x200D28`.
The three calls outside image-address code resolve through that mapping:

| Call site | Runtime target | Canonical source | Documented role |
|---|---|---|---|
| `0x6B28` | `0x200C84` | `0xB114` | Flash-ready poll |
| `0x6B36` | `0x200C94` | `0xB124` | Page-write helper |
| `0x77E4` | `0x200CFC` | `0xB18C` | Set-security-bit request |

The scan includes the source bodies' own relative branches and call. Aliases
are not counted as new source functions. Copy and command behavior remain
bounded by the [startup/persistence review](STARTUP_PERSISTENCE_REVIEW.md).

## Shared continuations across IDA ownership boundaries

Four direct branches cross IDA's function ownership without targeting a
documented independent entry. Their targets already have primary instruction
accounts and visited-address evidence in the [numeric runtime review](SOFT_FLOAT_REVIEW.md):

| Branch | Supported disposition |
|---|---|
| `0x86EC → 0x870C` | Unsigned integer-to-binary64 entry joins the conversion body also used by the signed entry. |
| `0x8808 → 0x883C` | Internal continuation of binary64-to-binary32 conversion. |
| `0x9160 → 0x91BC` | Special-value/sign handling inside binary32 multiplication's primary `0x913C..0x92CC` span. |
| `0x927C → 0x929C` | Sign-zero tail inside that multiplication span. |

The artifact retains IDA's source/target ownership and the entry suites that
visited each target. These are supported shared/internal continuations, with
no newly established independent calling contract. IDA ownership is not used
to truncate their executable flow.

## Data windows that resemble code pointers

The audit examines every four-byte window, including unaligned windows, whose
bytes are outside accepted code. It records 48 values whose normalized target
falls inside accepted code bytes. Thirty-one match documented entry addresses
and the reviewed ISA. Their use still depends on the consumer; a matching
number alone does not establish a callback or call.

Two tempting new-entry candidates have explicit numeric uses:

- Word `0x6F6C = 0x4E21` is loaded at `0x6E0E` and compared with a counter
  at `0x6E10`: it is threshold 20,001, despite resembling a Thumb pointer.
- Word `0x75CC = 0x7860` is loaded at `0x754A` and stored to PIO configuration
  address `0xFFFFF470` at `0x754C`. Its consumer is a mask write.

The executable-copy descriptor's destination/source words at `0x96E0` and
`0x96E4` are address metadata, not evidence of function-pointer calls. Seven
other windows conflict with the reviewed target ISA or instruction alignment.
That conflict is evidence against the proposed pointer in the current map;
it does not prove every alternate ISA interpretation impossible.

Six byte windows are compatible with the current target ISA but have no
identified code-pointer consumer. They are retained explicitly:

| Window source | Apparent value | Established storage context and remaining question |
|---|---|---|
| `0x5676` | `0x42C7` | Unaligned overlap of accepted main-control literal words; no load of a pointer from this window identified. |
| `0x96FA` | `0x645F` | Initialized-RAM bytes copied to `0x200012`; located in the byte-coefficient region used by scalar arithmetic. A pointer consumer is not established. |
| `0x9D7B` | `0x9200` | Initialized bytes copied to `0x200693`; complete consumer/provenance account remains open. |
| `0x9D87` | `0x9400` | Initialized bytes copied to `0x20069F`; complete consumer/provenance account remains open. |
| `0x9DB7` | `0x8C00` | Initialized bytes copied to `0x2006CF`, overlapping the reviewed warmup enable/threshold fields. A control-flow use of the composite window is not established. |
| `0xB185` | `0x4901` | Unaligned overlap of the page-write helper's literal constants, including word `0x00490100`; no pointer consumer from the overlapping window identified. |

These windows are not promoted to entries without control-flow evidence.
Their uncertainty belongs in the ongoing global writer/consumer audit, rather
than being hidden by the completed byte classification pass.

## Remaining entry-discovery work

The scan inventories 203 `BX` sites: 140 use LR, three are Thumb `BX PC`
interworking veneers, and 60 use other registers. Those 60 require return-
address, loaded-target or callback provenance; the inventory does not claim
they are all new indirect calls. Other computed PC writes and jump-table
targets also require their specific accounts.

Seven known starts lack an incoming edge or compatible data-pointer window
in this bounded scan. `0x4000` and `0x401C` are architectural vector roots;
`0x8568` and `0x8588` are reached by the recorded Thumb `BX PC` veneers.
The independently callable numeric entries `0x8CFC`, `0x9048`, and `0x94B4`
retain the earlier finding of no established in-image incoming reference.
Absence from this scan does not prove runtime unreachability.

Next work is to resolve the non-LR `BX` provenance and other computed PC
writes, trace the data windows above, and continue the global parameter,
interrupt, and subsystem accounts. No exhaustive-entry or full-analysis
completion claim follows from this pass.

```sh
python audit/tools/audit_execution_discovery.py firmware_v2.8.4HF.bin --output audit/data/execution_discovery_audit.json
```

No connected hardware, settings or device traffic were used.
