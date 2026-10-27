# Conditional address provenance across reviewed Thumb code

This pass extends the callback address engine to the reviewed Thumb domain of
exact V2.8.4HF: 32,000 bytes, SHA-256
`1ae519ba6194e8f7bdaaa94333a83a9e6fda3b0563f87f7d48383b37288c1780`.
The [artifact](../audit/data/thumb_store_provenance.json) represents every one
of **1,039 selected store sites**, including unresolved destinations. It is a
conditional normal-entry CFG account, not a whole-image writer-exclusion proof.

## Selected domain and graph conditions

All **6,813 reviewed Thumb starts** are loaded from the instruction manifest.
The tool seeds 118 roots from the baseline catalog, additional adjudications
and declared review entries, with unknown incoming registers and abstract
entry SP. Both conditional successors are propagated. Differing register or
saved-stack values join to unknown. Calls retain the explicit SP/R4–R11
preservation condition rather than proving each callee's ABI here.

Four dispatches use target sets from the source-bound
[indirect-transfer audit](INDIRECT_TRANSFER_PROVENANCE.md). Raw opcodes and
accepted destination starts are checked here; original table derivations and
bounds remain conditions from that audit:

| Dispatch | Table cases | Distinct supplied targets |
|---|---:|---:|
| `0x4B80` | 29 | 23 |
| `0x4C30` | 10 | 10 |
| `0x608A` | 218 | 58 |
| `0x809A` | 6 | 5 |

With those edges, propagation reaches all selected starts. This is graph reach,
not proof that every start is live-reachable or every path executes. The artifact
records 347 call sites and 114 exit sites. Many exits are normal returns or
interworking forms, not newly discovered defects; prior transfer classifications
and their conditions are retained.

## Address propagation and results

Raw address-producing forms include MOVS register aliases, constant shifts and
logical operations, immutable image reads and bounded stack-value facts.
LSR/ASR immediate-zero encodings mean shifts by 32, rather than pointer copies.
Carry-dependent arithmetic remains unknown. Mutable SRAM is not treated as
initialized constant memory, except for the three explicitly assumed stable
TC pointer slots from the callback account. Their initializer words are checked
against this exact image.

| Classification | Sites | Meaning |
|---|---:|---|
| Conditional fixed address | 791 | Same address over modeled paths, under the recorded conditions. |
| Entry-SP relative | 137 | Derived offsets; actual frame validity, bounds and nonaliasing still required. |
| Unresolved | 111 | Destination depends on information this abstraction does not establish. |
| **Selected total** | **1,039** | Every selected raw store is represented. |

All 83 fixed sites with observations in the prior store inventory agree in
address and width. Stack-relative offsets range from −64 to −4 here. Neither
an SP-derived address nor a fixed address alone proves safety. No unsupported
instruction remains in this selected propagation pass.

The full inventory has 1,063 stores. Its other **24 sites** are explicitly
listed outside this domain: 17 ARM sites and seven copied-template Thumb source
sites. They require separate ISA/relocation contracts. The earlier callback and
transitive artifacts still regenerate byte for byte after the engine extensions.

## Remaining obligations

The 111 unresolved sites are not 111 new vulnerabilities or unreviewed functions.
They include generic fill/copy, indexed filter/output buffers, mutable peripheral
bases and handlers requiring their parent's register/frame context. IDA owner
labels/grouped counts are navigation only; shared continuations can make them
misleading as function boundaries. Existing caller-specific accounts remain
evidence to reconcile against these obligations.

Among conditional fixed rows, only `0x5B22` overlaps percent word
`0x2005F0..0x2005F4`, agreeing with the
[producer/control review](CAPTURE_PERCENT_CONTROL_REVIEW.md). This does **not**
establish sole ownership: unresolved writers, excluded ARM/template sites,
missing/alternate entries, mutable vectors and DMA have not been excluded.

Fixed results depend on the selected entry/dispatch model, immutable image,
callee-preservation contracts and stable pointer assumptions. Missing entry or
dispatch evidence can invalidate global exclusion inferred from them. The full
goal remains active; no new entry or instruction-byte classification is claimed.

```sh
python audit/tools/audit_thumb_store_provenance.py firmware_v2.8.4HF.bin --output audit/data/thumb_store_provenance.json
python -m unittest discover -s tests -t .
```

No device traffic, flashing, engine-setting change or hardware measurement occurred.
