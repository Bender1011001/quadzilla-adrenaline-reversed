# AIC vector installation across selected initialization paths

This pass connects the [AIC-selected callbacks](INDIRECT_TRANSFER_PROVENANCE.md)
to the image's reviewed initialization writes. The exact V2.8.4HF source is
32,000 bytes with SHA-256
`1ae519ba6194e8f7bdaaa94333a83a9e6fda3b0563f87f7d48383b37288c1780`.
The [execution artifact](../audit/data/aic_vector_installation.json) records
16 composed cases and every vector write, including its instruction address.

Each case executes seven selected pieces: returning clock setup `0x414C`,
returning memory-descriptor setup `0x4114` and its original copy/fill helpers,
main's spurious-vector slice `0x77DE..0x77E4`, the PIO coordinator prefix
`0x74E8..0x757A`, and returning TC, SPI and USART setup routines `0x6FB4`,
`0x6BD8`, and `0x725C`. The PIO prefix stops before its first subordinate call.
The main slice stops before the security-helper call. Register/stack calling
state is constructed separately for each piece while SRAM/MMIO state persists.
This is a composition of reviewed segments, **not a full startup execution**.
Vector-page, security and other omitted setup paths have not been folded into
a claim of live startup completion.

## Observed vector transitions

Clock setup writes vector slot 0 to `0x40E0`, slots 1..30 to `0x40E4`, and
the spurious vector to `0x40E8`. The loop starts at 1, increments after its
indexed store, and repeats while the index is less than 31. It therefore
does not write slot 31 at `0xFFFFF0FC`. The harness seeds all 32 slots with
distinct values from two different sentinel bases and confirms that slot 31
is unchanged after every selected segment. The sentinel is an experimental
initial condition, not a device reading or a valid-handler claim.

Later selected paths produce the following state:

| Vector slot/address | Pointer bits after selected setup | Source entry and role | Writer |
|---|---|---|---|
| 0 / `0xFFFFF080` | `0x40E0` | ARM fallback self-loop | Clock setup `0x41A0` |
| 2 / `0xFFFFF088` | `0x7449` | Thumb `0x7448`, PIO callback | PIO prefix `0x7564` |
| 5 / `0xFFFFF094` | `0x6B45` | Thumb `0x6B44`, SPI callback stub | SPI setup `0x6BF8` |
| 6 / `0xFFFFF098` | `0x7179` | Thumb `0x7178`, USART callback | USART setup `0x72D6` |
| 12 / `0xFFFFF0B0` | `0x6C49` | Thumb `0x6C48`, TC0 callback | TC setup `0x6FE2` |
| 13 / `0xFFFFF0B4` | `0x6C69` | Thumb `0x6C68`, TC1 callback | TC setup `0x703A` |
| 14 / `0xFFFFF0B8` | `0x6C95` | Thumb `0x6C94`, TC2 callback | TC setup `0x708E` |
| Other slots 1..30 | `0x40E4` | ARM fallback self-loop | Clock setup `0x41AA` |
| 31 / `0xFFFFF0FC` | Initial sentinel retained | No write in these segments | None observed |
| Spurious / `0xFFFFF134` | `0x7445` | Thumb `0x7444`, returning stub | Main slice `0x77E2`, replacing the clock fallback `0x40E8` |

Each case has 39 vector writes: 32 during clock setup (31 source slots plus
the spurious vector), one main spurious replacement, one PIO replacement,
three timer replacements, one SPI replacement, and one USART replacement.
All ten distinct source entries written over these phases are already
documented and match their reviewed ARM/Thumb state. The final programmed
values cover nine source entries; the earlier spurious fallback `0x40E8`
has been replaced. This pass establishes no new independent entry.

## Evidence and limits of the installed set

The original-byte runs vary two initial vector seeds, both PIO pin-17 values,
both synthetic TC clock-status values, and read values zero/all-ones supplied
for write-only USART `US_CR`. Clock-ready bits are supplied so clock setup can
return. These variations leave the programmed vector set unchanged in this
memory model. Returning pieces check SP and R4–R11; prefix/slice stops retain
their actual SP in the artifact rather than claiming a completed frame.

The audit also compares raw PC-relative address-load encodings with the
byte-verified IDA references. Both identify ten literal sites supplying the
source-vector block or spurious-vector address, all inside the selected
initialization pieces. This is a bounded address-seed inventory. It does not
exclude an address synthesized through other arithmetic, a generic pointer
writer, DMA, corruption or later mutation.

The two exception wrappers still read hardware-selected vector values at
`0xFFFFF104` and `0xFFFFF100`. The table above identifies programmed values
under the stated setup assumptions; it does not simulate AIC priority,
pending/enabled state, fast routing, interrupt nesting or exact dispatch
ordering. No live malfunction follows from the untouched slot-31 finding.
An exhaustive writer/alias account and runtime invariants are still required
before claiming a complete finite set of all possible callback values.

The linked [startup](STARTUP_VECTOR_CLOCK_REVIEW.md),
[PIO](PIO_INTERRUPT_REVIEW.md), [timer](TIMER_SETUP_REVIEW.md),
[SPI](SPI_SETUP_REVIEW.md), and [USART](USART0_BUFFER_REVIEW.md) reviews retain
their per-register and per-handler contracts and hardware limitations.

```sh
python audit/tools/emulate_aic_vector_installation.py firmware_v2.8.4HF.bin --output audit/data/aic_vector_installation.json
```

No device traffic, flashing, settings or hardware measurements were used.
