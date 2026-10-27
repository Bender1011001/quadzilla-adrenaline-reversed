# Conditional local callback store contracts

This pass replaces sampled destination inference with conservative local CFG
propagation for seven selected returning callback bodies. It binds to exact
V2.8.4HF, 32,000 bytes, SHA-256
`1ae519ba6194e8f7bdaaa94333a83a9e6fda3b0563f87f7d48383b37288c1780`.
The [artifact](../audit/data/callback_store_contracts.json) records every local
store, its raw encoding form, resolved address or stack offset, calls and exit
obligations. It is **an intrabody conditional account**, not a transitive ISR
or global-writer proof.

## Method and conditions

The tool reads the reviewed explicit-mode decoder ranges, checks source
identity and contiguous instruction extents, and propagates abstract register
values across both successors of every conditional branch. It does not prune
paths using flags. Equal constants survive joins; differing values become
unknown. Raw Thumb encodings supply transfers, loads and stores; the recorded
instruction text is descriptive. Each store form must also match the full
1,063-site raw store inventory.

PC-relative image loads provide constants. Three pointer loads use explicit
stable initialized-value assumptions, checked against the image data copy:

| SRAM slot | Assumed word throughout the callback |
|---|---|
| `0x200700` | `0xFFFA0000` (TC0 base) |
| `0x200704` | `0xFFFA0040` (TC1 base) |
| `0x200728` | `0xFFFA0080` (TC2 base) |

SP is relative to entry SP. Known word stores/loads in a bounded local stack
window preserve pointer provenance. Unknown stores invalidate the stack-value
facts; call summaries invalidate them too. This resolves PIO's saved/reloaded
TC0/TC1 pointers without treating arbitrary stack data as constants. Tests
explicitly check that distinct branch addresses join to unknown rather than
one misleading fixed destination.

Calls are summarized as preserving SP/R4–R11 and forgetting caller-saved
registers. This is an explicit callee-contract condition; the tool does not
prove that condition or inspect transitive stores. Stack-relative destinations
require a valid intact callback frame disjoint from the globals under review.
Return/computed-exit integrity is separately retained as an obligation. Stable
image bytes, supplied pointer values and ordinary reviewed body entry are also
conditions. Unsupported instructions or unknown destinations would prevent
the corresponding local exclusion claim.

## Local results

All 425 starts in the selected bodies are reached by the conservative local
CFG. No unsupported opcode or unresolved local destination remains.

| Body entry | Local stores | Fixed destinations | Entry-SP-relative stores | Direct call sites |
|---|---:|---:|---:|---:|
| TC0 `0x6C48` | 4 | 4 | 0 | 0 |
| TC1 `0x6C68` | 2 | 2 | 0 | 0 |
| TC2 `0x6C94` | 93 | 92 | 1 | 20 |
| PIO `0x7448` | 6 | 4 | 2 | 0 |
| USART `0x7178` | 9 | 8 | 1 | 0 |
| SPI stub `0x6B44` | 0 | 0 | 0 | 0 |
| Spurious stub `0x7444` | 0 | 0 | 0 | 0 |
| **Total** | **114** | **110** | **4** | **20** |

The stack stores are TC2's 20-byte push at entry SP−20, USART's 12-byte push
at entry SP−12, and PIO word stores at entry SP−4 and entry SP−8. Fixed store
addresses and widths agree with observations for **all 110 fixed sites** in
the TC2 execution and selected interleaving artifacts. Observations corroborate
the conditional result; they do not substitute for its CFG and assumptions.

No fixed local destination overlaps `0x2005F0..0x2005F4`. Under the stated
nonaliasing stack condition, these body-local stores also cannot hit that word.
This improves the [selected interleaving account](CONTROL_CALLBACK_INTERLEAVING_REVIEW.md)
but does **not** close asynchronous percent stability: the twenty calls, mutable
vectors, other entries, external engines and global aliases are not excluded.

## Explicit transitive obligations

All twenty call sites are in TC2 and target eleven entries:
`0x7120`, `0x7128`, `0x7138`, `0x7140`, `0x7148`, `0x7150`, `0x7158`,
`0x7160`, `0x7168`, `0x7F28` and `0x7F40`. Numeric wrappers and their lower
helpers can update numeric status, and flag helpers can change queue state.
Their existing semantic reviews do not automatically become exhaustive store
contracts. Those transitive writes and the caller-preservation summaries must
be reconciled separately before claiming a complete callback footprint.

The programmed ARM fallback self-loops and the ARM exception wrappers are not
these seven returning Thumb bodies. Their prior reviews and remaining frame/
dispatch conditions remain separate. No entry count or byte classification
changes. The full firmware-analysis goal remains active.

```sh
python audit/tools/audit_callback_store_contracts.py firmware_v2.8.4HF.bin --output audit/data/callback_store_contracts.json
python -m unittest discover -s tests -t .
```

No device traffic, flashing, engine-setting change or hardware measurement occurred.
