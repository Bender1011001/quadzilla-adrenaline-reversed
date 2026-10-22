# USART0 receive/transmit and buffer review

V2.8.4HF, source hash
`1ae519ba6194e8f7bdaaa94333a83a9e6fda3b0563f87f7d48383b37288c1780`.
This pass assigns fifteen additional baseline roles. There are now **36 reviewed
roles among the original 145 starts**, leaving **109 baseline entries** unlabeled.
The separately adjudicated six extra starts bring the supported minimum to 151;
the inventories still do not claim exhaustiveness or complete semantic coverage.

Each new role has inputs, outputs, side effects, evidence and limits in
[the function reviews](../audit/data/uart_function_reviews.json). Fresh bounded
[Binary Ninja decoding](../audit/data/uart_buffer_binaryninja.json) is checked
against the full byte-verified IDA export. The model and test results below are
offline evidence only.

## Register interpretation and initialization

The [Microchip SAM7S datasheet](https://ww1.microchip.com/downloads/en/DeviceDoc/doc6175.pdf),
chapters 22 and 31 (printed pages 154–158 and 388–403), identifies USART/PDC
registers and status bits. The observed `0xFFFC0000` block is USART0. Current
receive/transmit pointer/count pairs occupy offsets `0x100/104` and `0x108/10C`;
next pairs use `0x110/114` and `0x118/11C`. Status bit 8 is receive timeout; bit 4
marks end of a transmit DMA transfer, not physical transmitter drain.

Initializer `0x725C` enables the USART0 peripheral clock, resets/disables relevant
state, zeros all four PDC pointer/count pairs, and installs Thumb handler pointer
`0x7179` in AIC slot address `0xFFFFF098`. It writes baud divider `0x34`, mode
`0x8C0`, and timeout `0x79`. From the programmed divider, the nominal normal-mode
baud expression is `MCK / (16*52)`. Neither MCK nor actual baud has been measured;
the updater's separately documented 921600 baud must not be substituted here.
Physical wiring to Bluetooth, USB or any external bridge remains unverified.

## Interrupt behavior

`0x7178` takes no explicit arguments and reads USART0 status once:

- If status bit `0x100` is set, it sets SRAM `0x200AFD` to 1, disables that
  interrupt, zeros the current receive count and disables receive DMA.
- If status bit `0x10` is set **and** PDC status indicates transmit enabled,
  it disables that interrupt and transmit DMA, then sets `0x200709` and
  `0x20070A` to 1.

The handler does not preserve an actual received-byte count in this path before
zeroing RCR. It preserves R4–R6; low registers and flags are changed. It returns
through LR to the enclosing interrupt wrapper. The two branches can both run
for a single sampled status word. Other status/error bits are not handled in
these reviewed branches; consequences depend on configuration and callers.

## DMA staging helpers and their limits

| Entry | Arguments | Static staging behavior |
|---|---|---|
| `0x71D0` | R0 source pointer, R1 count | Clears `0x20070B`; writes current TX pair when idle, else next TX pair when free; enables TX DMA and its completion interrupt |
| `0x720C` | R0 destination pointer, R1 count | Clears `0x200AFD`; analogous RX pair staging; restarts timeout and enables receive DMA/timeout interrupt |
| `0x7AF8` | Same as `0x71D0` | Call wrapper; no explicit acceptance status |
| `0x7B1C` | R0 destination | Forces R1=16 and calls `0x720C` |

Both staging helpers preserve R4–R6, change R0–R3 and flags, and take no explicit
buffer-capacity or pointer-validity argument. A caller must supply suitable RAM.
If the current count is zero, they replace its pair and clear **both** next
pointer and next count. If both counts are nonzero, they stage no new pair, but
still perform flag/control writes. They return without an explicit success or
failure result. This identifies a queue-full case to trace; it does not prove
that a normal caller can lose a frame or that DMA promotion cannot free a slot.

`tools/model_pdc_queue.py` models those decisions against a frozen register
snapshot. Its outcome string is analysis metadata, not a firmware return value.
It deliberately excludes asynchronous hardware promotion, memory transfers,
interrupt timing and the effects of USART control-register writes.

## Receive path closed to frame parsing

The previously reviewed `0x8038` uses getter `0x7B10` to check `0x200AFD`.
On its receive path it captures the completed buffer pointer, changes the active
pointer between the two 16-byte regions at context offsets `0x28` and `0x38`,
and calls `0x7B1C` to arm the alternate buffer. It then validates/parses the old
buffer through `0x7BCC` and `0x7E64`, eventually reaching the staging-byte walker
and the `0x601C` clamp dispatcher.

Thus the two 16-byte receive regions and the 14-byte payload budget fit the
header/payload/CRC layout. This is static dataflow; it is not a measured serial
transaction or a complete proof of race freedom.

`0x7BE8` reads the message type (header >> 4); `0x7BF0` reads the low nibble.
The latter is the **CRC-byte index**, not the index of the last payload byte:
`0x7BCC` increments it before computing CRC across that many bytes. The frame
builder at `0x7EB4` places CRC at that index. Maximum index 15 means a maximum
16-byte frame with 14 payload bytes. Earlier wording in the CRC utility has been
corrected without changing its CRC algorithm.

Because the parser uses that encoded index while the reviewed timeout path does
not retain the actual count, short reception and stale buffer suffixes need
additional analysis. The bounded model in `tools/model_receive_buffer.py` shows
that a previously valid frame remains CRC-valid if a reused region receives only
the same header byte and retains its old suffix. That result depends on the
specified buffer-reuse state; it is not a physical reproduction or a demonstrated
new actuator command. Changed bytes without a matching CRC fail the same model.
No fabricated input was sent to a tuner. Full message-type acceptance, actual
serial timeout behavior, and resulting engine effects remain unverified.

## Other reviewed flag helpers

| Entry | Effect |
|---|---|
| `0x7B04` | Returns unsigned SRAM byte `0x20070B` in R0 |
| `0x7B10` | Returns unsigned receive-timeout flag `0x200AFD` in R0 |
| `0x7B28` | Stores 0 at `0x20070E` |
| `0x7B30` | Stores 0 at `0x20070C` |
| `0x7B38` | Stores 1 at both `0x20070F` and `0x20070E` |
| `0x7B4C` | Stores 1 at both `0x20070D` and `0x20070C` |

These byte effects are established. Assigning complete protocol/timer meanings to
the `0x20070C..F` pairs requires tracing their remaining readers/writers. `0x7B04`
is recovered by decoding at the accepted entry itself; the earlier IDA item before
it incorrectly overlaps the start with a NEON interpretation.

## What remains

Trace the transmit callers' queue-occupancy assumptions and buffer lifetime,
actual short-frame handling, all receive errors, and the retransmission scheduler.
Then connect these states to the remaining main-loop/interrupt writers and finish
the variable-width AID and control-path reviews. The full-analysis goal is active.
