# Three-channel timer setup: bounded firmware review

This review covers three Thumb entries in the exact 32,000-byte V2.8.4HF
application image, SHA-256
`1ae519ba6194e8f7bdaaa94333a83a9e6fda3b0563f87f7d48383b37288c1780`.
The [bounded Binary Ninja decode](../audit/data/timer_setup_binaryninja.json)
accounts for 326 instruction bytes. The [execution artifact](../audit/data/timer_setup_emulation.json)
records original-byte writes to synthetic SRAM and register memory. Register
names and command bit meanings are from the [Microchip SAM7S datasheet](https://ww1.microchip.com/downloads/en/DeviceDoc/doc6175.pdf).
The installed chip suffix and board wiring have not been verified.

## Entries and boundaries

| Entry | Reviewed instructions | Supported contract |
|---|---:|---|
| `0x6FB4` | `0x6FB4..0x70C9` (278 bytes) | Set up TC channels 0, 1 and 2, enable their PMC clocks and AIC sources, initialize three SRAM words, then return. Called by the PIOA setup coordinator `0x74E8`. No subordinate call occurs inside this range. |
| `0x6C48` | `0x6C48..0x6C5D` (22 bytes) | TC0 vector callback: write `2` to TC0_CCR (CLKDIS), then store bytes `1`, `0`, `1` at `0x200726`, `0x200727`, `0x200725`. |
| `0x6C68` | `0x6C68..0x6C81` (26 bytes) | TC1 vector callback: write `2` to TC1_CCR, read TC1_SR, and write `0x2583` to TC1_RC only when CLKSTA bit 16 reads clear. |

The setup installs odd Thumb pointers `0x6C49`, `0x6C69` and `0x6C95` in
AIC_SVR12/13/14. The third target begins at `0x6C94` and **is not reviewed in
this pass**. Calling the first two callbacks as ordinary Thumb subroutines
proves their instruction paths under the supplied memory state, but does not
reproduce IRQ entry, acknowledgement or return behavior.

## Pointer origin and setup sequence

The startup copy initializes SRAM pointers from these exact image locations:

| SRAM pointer | Image source | Value |
|---|---|---|
| `0x2006F8` | `0x9DE0` | `0xFFFA00C0` (TC_BCR) |
| `0x2006FC` | `0x9DE4` | `0xFFFA00C4` (TC_BMR) |
| `0x200700` | `0x9DE8` | `0xFFFA0000` (TC0 base) |
| `0x200704` | `0x9DEC` | `0xFFFA0040` (TC1 base) |
| `0x200728` | `0x9E10` | `0xFFFA0080` (TC2 base) |

The initializer writes TC_BCR=`0` and TC_BMR=`0x15`. For each channel it writes
the PMC_PCER mask, a TC_CCR disable command (`2`), mode, an AIC disable command,
the vector, source mode, pending clear and enable commands, and TC_IDR=`0x10`.
The ordered instruction sites and values are retained in the execution artifact.

| Channel | PMC_PCER / AIC mask | TC_CMR | AIC vector / source mode | Conditional compare writes | Final TC_CCR commands |
|---|---:|---:|---|---|---|
| TC0 | `0x1000` | `0x980C0` | SVR12=`0x6C49`, SMR12=`0x26` | RA=`3`, RC=`0x1B` | `5` (CLKEN + SWTRG) |
| TC1 | `0x2000` | `0x980C0` | SVR13=`0x6C69`, SMR13=`0x26` | RA=`3`, RC=`0x1B` | `5` (CLKEN + SWTRG) |
| TC2 | `0x4000` | `0xC000` | SVR14=`0x6C95`, SMR14=`0x25` | RC=`0x963` | `1` (CLKEN), then `4` (SWTRG) |

Each compare write in the table occurs **only if that channel's TC_SR.CLKSTA
bit 16 reads clear** in the bounded execution. With all three synthetic status
bits clear, the routine made 41 recorded writes; with all three set, 36. The
five-write difference is the two RA, two RC and one RC values above. Other
writes are common to both cases. Finally, the routine zeros SRAM words
`0x200748`, `0x20074C` and `0x20073C`. The independent TC0/TC1/TC2 status
branches have not been exhaustively exercised in all eight combinations.

The two callback cases show `0x6C68` always writes TC1_CCR=`2`, then writes
TC1_RC=`0x2583` only when its synthetic TC1_SR.CLKSTA is clear. The synthetic
register model does not update TC1_SR in response to the preceding CCR
command. Consequently, this is an instruction-level condition, not a prediction
of the value a real counter returns after a disable command.

## Scope of inference

These are exact source-byte pointer values, instruction paths and bus-write
values. PMC, AIC and TC registers in the harness are plain memory: command
registers have no device side effects, status bits are supplied, and no timer
ticks. AIC source enable state, output pins, pulse width, clock rate, interrupt
timing and engine behavior remain unverified. The mode register words are
reported without claiming a board-level waveform. The current review also
does not determine the role of the longer `0x6C94` callback.

## Reproduction

```text
PYTHONPATH=<Binary Ninja Python path> python audit/tools/decode_image_ranges.py firmware_v2.8.4HF.bin --ranges 0x6c48:0x6c5e:thumb2,0x6c68:0x6c82:thumb2,0x6fb4:0x70ca:thumb2 --output audit/data/timer_setup_binaryninja.json
uv run --with unicorn==2.1.4 python audit/tools/emulate_timer_setup.py firmware_v2.8.4HF.bin --output audit/data/timer_setup_emulation.json
python -m unittest discover -s tests -t .
```

Both source-consuming tools require the exact image hash. The image is not
redistributed in this repository. These commands do not access a controller.
