# Lookup-table lifetime through selected startup and first-cycle paths

The [store/alias review](GLOBAL_STORE_INVENTORY_REVIEW.md) established a
conditional vector-scratch writer into the scalar lookup prefix. This pass
asks whether the later startup code restores that region. It executes the
original descriptor initializer, then the actual `0x77B8` reset continuation
through setup and selected first main cycles. All evidence binds to the exact
V2.8.4HF image, SHA-256
`1ae519ba6194e8f7bdaaa94333a83a9e6fda3b0563f87f7d48383b37288c1780`.

The [execution artifact](../audit/data/startup_table_lifetime.json) has 16
ready-state cases and two deliberately blocked cases. **No restoration of
the overwritten prefix occurs in the completed sampled paths**, including
after the first complete control cycle. The equal-vector comparison cases
retain the original initialized table instead. This is an execution result
under the stated synthetic inputs, not a universal remap/startup invariant.

## Executed sequence and watched regions

Descriptor initializer `0x4114` performs its original data copy, zero fill and
executable-template copy. The harness then enters `0x77B8`, with a synthetic
supervisor frame at SP=`0x203000`. It does not execute the ARM reset/clock
prefix or simulate banked exception state.

The main continuation executes its original calls and instructions:

| Milestone | Original code completed before the snapshot |
|---|---|
| `0x77DE` | Vector maintenance `0x73E4`, including its copied page helper on the different branch. |
| `0x77E8` | Copied security-request helper `0x200CFC`. |
| `0x77EC` | Entire peripheral coordinator `0x74E8`, including TC, SPI/CAN, ADC, USART and communications initializers. |
| `0x77F0` | Configuration restore `0x5F14`, its conditional copy and response mirror. |
| `0x77FA` | Default initializer `0x4384`. |
| `0x7836` | Setup reaches the software-event wait. |
| First `0x78E4` | Wait release and initial-state selection `0x760C` complete. |
| `0x50F0`, `0x4D38` | First normal cycle reaches the original control routine and scalar entry. |
| Second `0x78E4` | First normal cycle has returned; execution stops before the next dispatcher iteration. |

Snapshots hash all three contiguous lookup regions: scalar
`0x200000..0x200190` (400 bytes), stretch region `0x200190..0x200294`
(260 bytes), and capture `0x200294..0x200424` (400 bytes). Every CPU store
overlapping those regions is recorded. Ends are exclusive. The copied
helpers execute at their actual initialized SRAM aliases; no initializer or
transfer result is replaced with a successful return stub.

## Explicit synthetic inputs

The 16-case matrix crosses these independent choices:

- Vector comparison equal or different. Page zero initially contains the
  image's first 128 bytes; the equal case replaces its second word with
  wrapped `word[0x104004]+0x1000` to satisfy the comparison explicitly.
- Persisted-configuration magic absent or accepted. Synthetic `0x10FF00`
  contains the initialized 44-byte configuration, with magic `00/A5` and
  its mode byte set to 1. Without acceptance the SRAM default mode 4 remains;
  with acceptance it becomes 1. No real non-image storage is read.
- PIO bit 17 clear or set. Bit 11 is supplied high for SPI readiness; bit 28
  is clear in this matrix, allowing the selected state-1 normal cycle.
- USART write-only command-register reads supplied as `0` or `0xFFFFFFFF`.
  Each read and supplied value is recorded; hardware register behavior is
  not inferred from ordinary emulator memory.

Flash-ready status is supplied as 1 and SPI status as `0x30`. Other MMIO
locations are plain synthetic memory. Commands do not produce oscillator,
timer, DMA, CAN, serial or interrupt effects. In particular, DMA does not
populate receive buffers in these runs.

At the first wait read at `0x7836`, the ready cases explicitly set software
byte `0x200718=1`. This is an external event injection, **not simulated IRQ
delivery**. The original wait and subsequent selection instructions execute.
Only this memory event and the declared command-register read values are
supplied during execution; helper return values are not stubbed.

## Observed table lifetime and first control call

Each different-vector case makes the same 37 word writes from the vector
maintenance loops. No further store overlaps any of the three lookup
regions through the second dispatcher stop. The scalar prefix's resulting
hash remains the same at every later milestone: peripheral initialization,
configuration restore, defaults, wait, dispatcher, control entry and scalar
entry. The stretch and capture region hashes remain their initialized values.

The equal-vector cases make no lookup-region store and retain all three
initialized hashes. In every completed case, one complete `0x50F0` call and
one scalar call execute, and the main frame remains at SP=`0x202FEC` after
the first cycle returns.

**The first scalar call does not read the table in these sampled initial
states.** It enters with selector R1=0 and enable byte `0x200432=0`, then
visits bypass `0x4F96`. The three signed lookup sites monitored by the harness
are not reached during these first cycles. Thus this pass establishes table
retention into ordinary control execution, but does not demonstrate a harmful
first-cycle table read or output difference. The earlier alias review's
later signed-byte consumption used separately controlled scalar inputs.

The different-vector path issues synthetic flash command requests
`0x5A000001` and then `0x5A00000F`; the equal path issues only the latter.
These are original bus stores in emulator memory, not successful physical
programming or security-state measurements.

## Blocked negative controls

Two additional different-vector cases retain the table overwrite but do not
reach control execution within the 30,000-instruction budget:

| Missing input | Observed stop | Interpretation |
|---|---|---|
| SPI ready status (`SPI_SR=0`) | Budget stop at `0x6B6A`, before peripheral setup returns | Original transfer setup continues waiting; no timeout/IRQ flag is injected. |
| Software wait event | Budget stop at `0x7832` | Setup reaches the original `0x200718` wait and remains there without the event. |

These are bounded execution stops, not a measured startup duration, simulated
hardware timeout, or proof that a physical device is stuck.

## Remaining scope

This closes the restoration question **for the executed post-descriptor setup
and first-cycle cases**. It does not exclude later restoration, alternate
configurations, other remap states, interrupt/peripheral writers or future
control states that consume the table. The actual page-zero mapping and
persisted configuration are outside the supplied image's direct evidence.
The full global writer and firmware completion claims remain open.

```sh
python audit/tools/emulate_startup_table_lifetime.py firmware_v2.8.4HF.bin --output audit/data/startup_table_lifetime.json
python -m unittest discover -s tests -t .
```

No connected hardware, device traffic, host flash operation or firmware-file
modification was used.
