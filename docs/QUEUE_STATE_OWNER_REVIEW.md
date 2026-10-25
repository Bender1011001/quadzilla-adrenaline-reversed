# Queue setup, reset and source-count provenance

This account uses the exact 32,000-byte V2.8.4HF application image,
SHA-256 `1ae519ba6194e8f7bdaaa94333a83a9e6fda3b0563f87f7d48383b37288c1780`.
The [explicit Thumb decode](../audit/data/queue_state_owners_binaryninja.json)
and [original-byte cases](../audit/data/queue_state_owners_emulation.json)
cover `0x7EFC..0x7F27` and `0x800C..0x8033`: **84 instruction bytes,
40 starts**. Every start matches an ordinary byte-verified IDA boundary and
executes in the eight controlled cases. The `FFFF` at `0x800A..0x800B`
separates functions; the words at `0x8034` and `0x8500` are both the
`0x2007C8` state-base literal. These ten bytes are classified as layout
data in the ledger.

## Guarded queue setup `0x7EFC`

R0 supplies a source list pointer; R1 supplies its requested byte count.
The helper checks state bytes `+0xE` and `+0xF`. If either is nonzero, it
returns zero without changing the queue. Otherwise it sets `+0xE=1`, calls
the previously reviewed `0x7FD8` with destination `+0x78` (`0x200840`) and
count pointer `+0xD` (`0x2007D5`), then returns one. `0x7FD8` caps a
nonzero requested count at 14. A zero count leaves `+0xD` unchanged even
though the busy flag is set.

Original-byte calls with requests 1, 14, 15 and 255 wrote counts 1, 14,
14 and 14 respectively. Busy `+0xE` or `+0xF` rejected a one-byte request
without a state write. Five direct image call sites are at `0x7706`,
`0x7724`, `0x7744`, `0x7764` and `0x7780`. This helper writes the
type-3/other-data queue count at `+0xD`; it does not fill either AID-list
source count `+0x13/+0x18`.

## Flag reset and receive rearm `0x800C`

The single direct call at `0x758E` enters `0x800C`. It clears state flags
`+7`, `+8`, `+9`, `+0xB`, `+0xC`, `+0xE`, `+0xF`, `+0x11`, `+0x12`,
`+0x15`, `+0x16`, and `+0x17`, then passes the saved receive-buffer
pointer at `+0x20` to `0x7B1C` to rearm the USART0 receive path. It does
not clear list counts `+0x13/+0x14/+0x18/+0x19`. The controlled case
deliberately preloads source counts 14 and 13 to check that they survive
the helper. Those synthetic values are **not** claimed as an initialized
or reachable board state. The helper has no meaningful R0 return contract:
its epilogue uses a popped return address through R0.

## What the reference inventory establishes

The [source-bound reference inventory](../audit/data/queue_state_refs.json)
finds only four aligned image words pointing into the `0x2007C8..0x20088F`
state block: three `0x2007C8` base literals at `0x8034`, `0x81A4` and
`0x8500`, and the initialized receive-buffer pointer `0x2007F0` at
`0x9ED0`. IDA reports six instructions loading the shared base from those
literals, at `0x7F00`, `0x7F28`, `0x7F42`, `0x800E`, `0x804C` and
`0x81BC`. The four list counts `0x2007DB/DC/E0/E1` initialize to zero.
No exact literal points directly to either source count or source list.

Together with the [receive dispatcher](RECEIVE_STATE_REVIEW.md) and
[outgoing scheduler](OUTGOING_STATE_REVIEW.md), this narrows the direct
owners of the queue state. It does **not** prove that source counts can
never grow: unreviewed entries could compute a pointer, receive an alias,
or write through a broader copy. A whole-image writer and pointer-flow
audit, including interrupt and main-loop paths, is still needed before
classifying the two direct-call stack-boundary findings as ordinarily
reachable or unreachable. The emulator maps USART registers as passive
memory and did not send hardware traffic.

```text
PYTHONPATH=<Binary Ninja Python path> python audit/tools/decode_image_ranges.py firmware_v2.8.4HF.bin --ranges 0x7efc:0x7f28:thumb2,0x800c:0x8034:thumb2 --output audit/data/queue_state_owners_binaryninja.json
uv run --with unicorn==2.1.4 python audit/tools/emulate_queue_state_owners.py firmware_v2.8.4HF.bin --output audit/data/queue_state_owners_emulation.json
python audit/tools/audit_queue_state_refs.py firmware_v2.8.4HF.bin --output audit/data/queue_state_refs.json
python audit/tools/build_image_ledger.py firmware_v2.8.4HF.bin
python -m unittest discover -s tests -t .
```
