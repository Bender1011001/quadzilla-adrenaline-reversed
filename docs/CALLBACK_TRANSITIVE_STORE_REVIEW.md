# Callback callees: conditional transitive store-address account

This pass follows the twenty direct call sites left open by the
[local callback review](CALLBACK_STORE_CONTRACT_REVIEW.md). It binds to exact
V2.8.4HF, 32,000 bytes, SHA-256
`1ae519ba6194e8f7bdaaa94333a83a9e6fda3b0563f87f7d48383b37288c1780`.
The [artifact](../audit/data/callback_transitive_stores.json) records fixed
wrapper targets, both flag-helper store accounts, the ARM runtime store superset
and the status-address predecessor chain. It addresses **write destinations**;
it does not establish numeric correctness or unconditional ISR safety.

## Eleven direct targets

Nine numeric wrappers at `0x7120`, `0x7128`, `0x7138`, `0x7140`, `0x7148`,
`0x7150`, `0x7158`, `0x7160` and `0x7168` are checked against their exact raw
instruction sequences and literal target words. Seven load R3 and tail-transfer
to a fixed ARM address. The other two push R3, load/copy a target to R12, restore
R3 and transfer through R12. Their only stores are those two stack pushes.
The resolved targets are recorded individually; arbitrary/mutated targets are
outside this normal-entry, immutable-image account.

The remaining helpers, `0x7F28` and `0x7F40`, have eight fixed byte-store sites
in total, all inside `0x2007C8..0x2007E0`. Conservative local propagation includes
both gate outcomes and finds no additional call. Their earlier
[semantic account](TC2_FLAG_HELPER_REVIEW.md) remains applicable.

## ARM numeric closure and status byte

The tool examines all **1,042 accepted ARM starts** across the two numeric
instruction spans, excluding the literal word at `0x896C`. This whole-region
account deliberately includes code not established reachable from these nine
wrappers. Raw direct branches/calls remain inside the accepted region. The tool
includes conditional fallthrough and possible call return fallthrough; every
indirect transfer is an LR return form. Other computed PC writes and software
interrupts would reject this closure check. LR return integrity remains a condition.

There are exactly **eight store sites** in this superset:

| Store class | Count | Destination contract |
|---|---:|---|
| ARM stack register-list stores | 7 | Current SP with recorded offsets/register lists; valid nonaliasing runtime frames required. |
| Byte store at `0x8964` | 1 | `0x200AF8`, the numeric status byte. |

The only nonstack store follows this exact chain:

```text
0x8958: load R2 from image literal 0x896C = 0x200AF8
0x895C: load byte through R2 into R12
0x8960: OR bit 0 into R12
0x8964: store byte R12 through R2
```

The tool checks those instruction words, the literal, and the unique immediate
predecessors of the last three instructions across the ARM-region CFG. None of
the nine wrapper roots enters mid-chain, and the full-image direct-transfer
inventory has no entry bypassing the literal into those three instructions.
The two intermediate instructions retain R2. Under ordinary fixed entry/return
and immutable-code assumptions, the byte-store destination is therefore fixed.
This does not admit arbitrary entry through a corrupted return/vector.

## What the composed result establishes

The local callback account's 110 fixed stores are extended by eight flag-helper
sites and one numeric status site. Including every store in the whole ARM
superset gives **119 fixed nonstack sites and 13 stack sites**, or 132 sites in
the conservative composition. These are source store sites, not counts per
execution, and not a claim that every superset site is reachable from TC2.

No fixed destination in this composition overlaps `0x2005F0..0x2005F4`.
With valid stack placement disjoint from that word, the normal callee-address
obligations introduce no additional write to it. Caller register-preservation,
stable initialized peripheral pointers, stack/return integrity and fixed entry
conditions remain explicit. This pass does not independently prove every callee
preservation path, all mutable-vector targets, DMA exclusion or other global writers.

The [soft-float review](SOFT_FLOAT_REVIEW.md) records numeric mismatches and
caller-state dependence. A restricted store footprint does not repair those
arithmetic defects or strengthen their live-impact claims. Nonfinite/status
semantics and wider parameter-to-output integration remain separate work.
The full firmware-analysis goal remains active.

```sh
python audit/tools/audit_callback_transitive_stores.py firmware_v2.8.4HF.bin --output audit/data/callback_transitive_stores.json
python -m unittest discover -s tests -t .
```

No device traffic, flashing, engine-setting change or hardware measurement occurred.
