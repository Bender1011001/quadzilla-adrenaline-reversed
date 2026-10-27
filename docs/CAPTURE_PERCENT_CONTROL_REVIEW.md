# Capture-derived percent: producer, retention and control consumers

This pass follows the known producer of `word[0x2005F0]` through complete
original `0x76CC` cycles. Source is V2.8.4HF, 32,000 bytes, SHA-256
`1ae519ba6194e8f7bdaaa94333a83a9e6fda3b0563f87f7d48383b37288c1780`.
The [artifact](../audit/data/capture_percent_control.json) records **512 successful
producer cycles and six retained-value cycles**, with ordered writes/reads,
actual scalar column, capture-table arguments and response byte.

## Known producer and caller ordering

The [capture parser review](CAPTURE_PARSER_REVIEW.md) identifies raw RXB1 header
`67 88 03 00`. In phase 2/kind 2, original transfer admission and header comparison
lead to `0x5B12..0x5B22`. D1 is multiplied by four, divided by ten through the
signed runtime helper and capped at 100. Its nonnegative 0..1020 numerator
makes the final word `min(floor(4*D1/10),100)`, in 0..100.

Each test first executes the existing controlled integration fixture call,
then supplies a completed 14-byte RXB1 buffer, phase/kind 2/2, SPI base/status,
PIO status `0x818`, USART context and no pending application message. Outgoing
gate is zero. The original cycle executes ADC and capture before receive,
validation, control and scheduling, with no substituted helper results.
Preparatory state, buffer and peripheral status are synthetic; no DMA engine
or physical CAN delivery runs.

All 256 D1 values are tested at DLC 0 and 8. Exactly one overlapping percent
word store occurs in each successful cycle, at `0x5B22`, before every watched
word read. Each read at address `0x2005F0` sees that produced value. Both index
reads (`0x5202`, `0x5210`) execute. Scalar column is `floor(19*P/100)`, and the
original response builder stores P at byte `0x200BC0`. Other scalar/response
results pass the inherited independent model comparisons.

DLC zero does not prevent this completed-buffer parser path or its consumers.
This extends the absent-DLC-guard account through the full cycle, without
establishing physical delivery under the same timing/status conditions.

## Retained values and writer limits

Six cases supply old P in 0/100/`0xFFFFFFFF` with either an unknown header and
ready status `0x30`, or recognized header and status `0x10` (ENDTX clear).
No percent store occurs. All watched reads retain the old word through the
cycle. For `0xFFFFFFFF`, scalar column is the direct capped value 19 and
response byte is 255. The successful producer's range is therefore not itself
a universal invariant of the stored word.

The [store inventory](GLOBAL_STORE_INVENTORY_REVIEW.md) has an IDA destination
annotation for this producer. That is navigation evidence, not exclusion of
aliases, computed pointers, startup, corruption or DMA. This pass does not
establish that `0x5B22` is the only writer.

The repeated-load condition in the [scalar review](CONTROL_SCALAR_INTEGRATION_REVIEW.md)
remains conditional. These uninterrupted cycles establish producer-to-consumer
ordering and stable observed values. They do not simulate an interrupt between
reads or prove that installed callbacks, mutable vectors, generic writers and
memory engines cannot alter P. Callback transitive writer sets and global alias
exclusion remain required before strengthening asynchronous stability claims.

No entry or instruction-coverage counts change. The full goal remains active;
the separate 574/574 main-start milestone does not close writer/ordering work.

```sh
python audit/tools/emulate_capture_percent_control.py firmware_v2.8.4HF.bin --output audit/data/capture_percent_control.json
python -m unittest discover -s tests -t .
```

No device traffic, flashing, engine-setting changes or physical measurements
were performed.
