# ADC initialization, startup constants, and vector-page maintenance

This review is tied to the V2.8.4HF 32,000-byte application image, SHA-256
`1ae519ba6194e8f7bdaaa94333a83a9e6fda3b0563f87f7d48383b37288c1780`.
The [bounded Binary Ninja decode](../audit/data/adc_init_vector_binaryninja.json)
uses explicit Thumb mode for six ranges; the byte-verified IDA export supplies
literal values and call sites. These are static observations, not a claim that
the corresponding branch ran on a connected board.

IDA presents `0x73E6..0x73EA` and `0x740C..0x7410` as single four-byte
constant-load pseudo-instructions. Binary Ninja exposes each as a two-byte
`MOVS` followed by a two-byte `LSLS` at `0x73E8` and `0x740E`. The spans and
resulting constants agree; the decoder outputs should not be counted as
different instruction starts at those two addresses.

## ADC initializer at `0x4330..0x435E`

The call from the peripheral setup routine at `0x74E8` executes these writes:

| Instruction | Destination | Value | Register-level reading |
|---|---|---:|---|
| `0x4334` | `0xFFFFFC10` | `0x10` | PMC PCER, enable peripheral ID 4 (ADC) |
| `0x433A` | `0xFFFD8014` | `0xFF` | ADC CHDR, disable channels 0–7 |
| `0x4340` | `0xFFFD8004` | `0x02010A00` | ADC MR, configuration word |
| `0x4346` | `0xFFFD8010` | `0xF8` | ADC CHER, enable channels 3–7 |
| `0x434C` | `0xFFFD8000` | `2` | ADC CR, start conversion |

The register names and offsets follow the [AT91SAM7S datasheet](https://ww1.microchip.com/downloads/en/DeviceDoc/doc6175.pdf).
`0x02010A00` has LOWRES clear, so the configured resolution is 10 bits; this
agrees with the separately reviewed ADC polling and lookup path. The initializer
also stores `0xF8` at SRAM `0x2008A0` and `1` at `0x200720` and `0x20071F`.
The relationship of those three bytes to later state needs a caller/data-flow
review; their names and physical sensor assignments are not established here.

The `0xF8` channel mask is an exact match to the channel sequence in
[the polling review](ADC_PIPELINE_REVIEW.md). The user's V2.2 board has a
provisionally identified 16 MHz crystal beside the MCP2515. That oscillator is
separate from this MCU ADC setup and does not establish an ADC clock or a CAN
bit rate from these instructions.

## Three literal-return helpers

`0x73CC`, `0x73D4`, and `0x73DC` are each a PC-relative literal load into R0
followed by `BX LR`. Their respective literal words at `0x73D0`, `0x73D8`,
and `0x73E0` are `0x0010FD00`, `0x0133EF42`, and `0x0010FE00`.
The baseline call graph associates each with the reset continuation at `0x77B8`.
At the directly inspected start of that routine, calls to `0x73CC` and
`0x73DC` have no intervening use of R0. These are constant-return routines;
no device interaction or timing role is inferred from the values alone.

## Conditional vector-page path and write wrapper

`0x73E4..0x742E` loads the current word at address `0x4` and compares it with
the word at `0x104004` plus `0x1000`. On equality it returns `0x200000`.
On inequality it copies 32 words (128 bytes) from address zero to SRAM
`0x200000`, replaces words 1–5 with words from `0x104004..0x104014` plus
`0x1000`, and calls `0x6B20` with destination zero, length `0x80`, and source
`0x200000`. It then returns `0x200000`. The call appears in startup near
the constant helpers. The comparison depends on memory alias/remap state,
which this image alone does not establish.

The subsequent [store/alias review](GLOBAL_STORE_INVENTORY_REVIEW.md)
executes both comparison outcomes with explicit synthetic alias/status inputs
and the original copied flash helpers. It connects scratch `0x200000` to the
scalar lookup table, recording 37 prefix word writes on the different branch
and later signed-byte consumption. It does not establish live remap state or
exclude subsequent table restoration.

`0x6B20..0x6B44` saves the three arguments, calls SRAM helper `0x200C84`,
calls interrupt-state helper `0x7498`, then calls SRAM page writer `0x200C94`
with the original arguments and restores interrupt state via `0x74B4`.
The [persistence review](STARTUP_PERSISTENCE_REVIEW.md) traces the SRAM writer
and its command construction. The wrapper does not preserve the writer's R0
result; the restore helper changes R0. A successful physical write, a required
bootloader layout, and the branch's live frequency remain unverified.

The explicit ranges classify 168 instruction bytes: 46 ADC initializer,
12 literal helpers, 74 vector path, and 36 write wrapper. Literal pools adjacent
to these ranges remain data candidates in the byte ledger. No flash operation,
peripheral access, or board setting was performed for this review.
