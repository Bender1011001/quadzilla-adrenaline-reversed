# Selected original callbacks between repeated control loads

This pass pauses original control `0x50F0` at `0x5210`, after the percent-word
comparison load and before the second load. It executes an original callback
body, restores the interrupted CPU context and resumes control. Source is
V2.8.4HF, 32,000 bytes, SHA-256
`1ae519ba6194e8f7bdaaa94333a83a9e6fda3b0563f87f7d48383b37288c1780`.
The [artifact](../audit/data/control_callback_interleavings.json) records
**33 callback/control compositions**, their non-stack callback writes, scalar
column and response inputs/results. No function result is stubbed.

## Host composition and its boundaries

The first original control segment stops before instruction `0x5210` executes.
The host saves Unicorn's full CPU context, supplies a separate callback stack
at `0x202800` and an external return link, then invokes the original callback
through its actual return. Its SP and R4–R11 preservation are checked. The
interrupted CPU context is restored, including flags and registers, while all
SRAM/MMIO changes persist. Control resumes at `0x5210` and returns through its
original epilogue with the inherited scalar/table/timer/stack/register checks.
Its actual response inputs and full response/filter calculations are compared
with the existing independent model.

This host operation **is not ARM IRQ/FIQ entry or wrapper execution**. It does
not model banked modes, AIC routing/priorities, nesting, exact interrupt timing,
hardware register side effects or DMA. Separate callback stack placement is an
explicit fixture choice. It does not prove the board uses that exact context.

## Cases and actual effects

Each row runs with `word[0x2005F0]` equal to 0, 50 and 100. Initialized TC2
pointer ownership is preserved using the preceding
[fixture correction](PERIPHERAL_POINTER_FIXTURE_REVIEW.md). AIC mask bit 2,
PIO, timer and USART statuses are supplied as plain-memory inputs.

| Callback | Selected conditions | Observed callback effects |
|---|---|---|
| PIO `0x7448` | Pin 30 low/high; both timer-enable flags set | Low writes both timer CCR commands and AIC disable/clear; high has no writes. |
| SPI stub `0x6B44` | Ordinary entry | Returns with no writes. |
| TC0 `0x6C48` | Initialized timer pointer | Writes timer disable command and three scheduling flag bytes. |
| TC1 `0x6C68` | Clock status clear/set | Both disable channel; only clear case writes RC `0x2583`. |
| TC2 `0x6C94` | Numeric tail disabled/enabled by old counter | Counter-only case writes two counters; numeric case additionally updates accumulated/ratio state. |
| USART `0x7178` | Status zero / timeout and TX-end bits set | Combined status sets receive pending, clears RCR, changes DMA/interrupt commands and sets TX timer flags. |
| Spurious stub `0x7444` | Ordinary entry | Returns with no writes. |

Every selected callback leaves the percent word unchanged and has no observed
store overlapping it. The resumed scalar column equals `floor(19*P/100)`.
That is bounded executed evidence, not exhaustive transitive writer exclusion.
Other callback states, mutable pointers/vectors, indirect entries and external
memory engines remain outside the claim.

## Shared effects are retained, not discarded

The numeric TC2 fixture supplies prior update count 10001, derived state
6000000, old ratio numerator binary32 6 and denominator binary32 2. The original
callback writes denominator bits `0x4001B0D2` at `0x20074C` and timer state 2
at `0x200738`. The later original response calculation consumes those changed
values; its bytes and full filters agree with the model using the actual state.
This verifies that composition preserves shared-memory effects even though the
host restores the interrupted CPU registers. It does not newly prove the full
numeric callback contract or physical meaning of those state words.

The uninterrupted-cycle [percent producer review](CAPTURE_PERCENT_CONTROL_REVIEW.md)
and these selected interruptions together strengthen the source-word account,
but they do not remove the stable-input condition from the global table-index
proof. Full callback writer contracts and global alias constraints remain open.
No instruction-coverage or entry count changes; the full goal remains active.

```sh
python audit/tools/emulate_control_callback_interleavings.py firmware_v2.8.4HF.bin --output audit/data/control_callback_interleavings.json
python -m unittest discover -s tests -t .
```

No device traffic, flashing, engine-setting change or measured output occurred.
