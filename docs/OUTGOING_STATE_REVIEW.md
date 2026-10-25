# Outgoing frame scheduler and AID queue state

This account uses the exact 32,000-byte V2.8.4HF application image,
SHA-256 `1ae519ba6194e8f7bdaaa94333a83a9e6fda3b0563f87f7d48383b37288c1780`.
The [bounded Binary Ninja decode](../audit/data/outgoing_state_binaryninja.json)
covers the full Thumb body `0x81A8..0x84FD`: **854 instruction bytes and 383
starts**. All 383 starts agree with ordinary boundaries in the byte-verified
IDA export. The [original-byte campaign](../audit/data/outgoing_state_emulation.json)
returns in 28 controlled cases and visits 378 starts. The five unvisited
starts are `0x847C`, `0x847E`, `0x8480`, `0x848A`, and `0x84DC`, all in the
type-4 list branch after it asks the frame builder to consume the source
list. They are statically decoded and accounted for below; the campaign does
not establish whether normal state can enter them.

## Call boundary and priority

The scheduler first reads the USART-ready byte at `0x20070B` through
`0x7B04`. When it is zero, it returns code 7 without selecting a frame.
Otherwise it selects the first pending category in this order and uses the
frame buffer at `0x200890`:

| Priority | State at base `0x2007C8` | Frame type | Returned code and transition |
|---|---|---:|---|
| 1 | flag `+9` | 2 | Clear flag; return 8. |
| 2 | flag `+8`, then `+7` | 5 | Build/send. Depending on deferred count and prior count, clear or rearm flags; return 9 or 10. |
| 3 | flag `+C`, then `+B` | 1 | Same pattern with flags `+C/+B`; return 11 or 12. |
| 4 | flag `+F`, then `+E` | 3 | Same pattern with flags `+F/+E`; return 13 or 14. |
| 5 | list A bit `+11 & 1` while latch `+12` is clear, else flag `+10` | 0 | Copy, build, send, filter, update flags; return 15 or 16. |
| 6 | list B bit `+16 & 1` while latch `+17` is clear, else flag `+15` | 4 | Copy, build, send, filter, update flags; return 17 or 18. |

With no selected category, it returns zero. Each selected branch sends one
frame and exits; it does not drain every queue in a single call. The frame
length comes from `0x7BF0` plus one byte and is narrowed to eight bits before
`0x7AF8` submits the buffer to the USART0/PDC setup helper at `0x71D0`.
The original helper writes the mapped `0xFFFC0108/010C/0118/011C/0120`
registers. The emulator treats that register page as passive memory; it
does not model DMA completion, interrupts, timing, or line traffic.

## List A and B count transitions

The two list paths are structurally parallel but differ in frame type and
source data. Source list A is `0x200850`, its count is `0x2007DB`, copied
list A is `0x200860`, and copied count is `0x2007DC`. List B uses
`0x200870/0x2007E0` and `0x200880/0x2007E1` respectively. All four counts
are zero in the image's initialized RAM data.

On either the bit path or the reset path, `0x7FD8` copies at most 14 source
AIDs into the associated working list and writes its count. Then `0x7EB4`
builds type 0 or 4, calling `0x7D80` with the original mutable list and count
pointer. The reader overwrites the **source** count with the number it could
not include. After USART submission and flag updates, `0x7F58` removes the
remaining source AIDs from the copied working list and writes the working
count. The saved `+1D/+1E` byte records the post-builder source count.

The campaign records actual writes at `0x8002`, `0x7E56`, and `0x7FCC`.
For list A with 14 source AIDs `1..14`, the copier writes 14 to `0x2007DC`,
the reader writes one deferred AID to `0x2007DB`, and the filter leaves 13
in `0x2007DC`. With one mapped AID, both counts end at zero. A synthetic
unmapped AID 226 in type 0 leaves source count one and produces return 16;
the filter then clears the working count. For type 4, the inspected 1-,
14-, and synthetic 15-AID cases all end with source count zero. The type-4
nonzero-count branches are present in the code but not covered by those cases.

The previous [queue-filter review](OUTGOING_QUEUE_FILTER_REVIEW.md) showed a
direct-call stack overwrite at a *working* count of 17, and the
[frame-reader review](FRAME_READER_REVIEW.md) showed one at 17 rejected
AIDs. This scheduler's two `0x7FD8` copies cap the working counts at 14
before its own filter calls. Its frame-builder input counts, however, come
from the **source** fields `0x2007DB/0x2007E0`; the scheduler does not cap
these before the builder. The complete producer and indirect-writer audit
for those fields is therefore still required before assigning ordinary-path
reachability to the frame-reader defect. No physical exploitability or
absence of risk is inferred from the synthetic cases.

## Reproduction and limits

```text
PYTHONPATH=<Binary Ninja Python path> python audit/tools/decode_image_ranges.py firmware_v2.8.4HF.bin --ranges 0x81a8:0x84fe:thumb2 --output audit/data/outgoing_state_binaryninja.json
uv run --with unicorn==2.1.4 python audit/tools/emulate_outgoing_state.py firmware_v2.8.4HF.bin --output audit/data/outgoing_state_emulation.json
python audit/tools/build_image_ledger.py firmware_v2.8.4HF.bin
python -m unittest discover -s tests -t .
```

The emulator uses controlled SRAM flags, counts and lists, executes exact
firmware instructions in an ARM926 functional surrogate, and maps USART0
registers as ordinary memory. It proves instruction and local state behavior
for those inputs. Receive dispatch, all indirect producers of the two source
counts, completion-driven USART state and board V2.2 behavior remain separate
work. No device traffic was sent.
