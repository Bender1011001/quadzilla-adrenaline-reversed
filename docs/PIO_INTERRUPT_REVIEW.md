# PIOA and AIC setup: bounded firmware review

This review is tied to the exact 32,000-byte V2.8.4HF application image,
SHA-256 `1ae519ba6194e8f7bdaaa94333a83a9e6fda3b0563f87f7d48383b37288c1780`.
The [bounded decoder artifact](../audit/data/pio_interrupt_binaryninja.json)
covers four Thumb entries; the [original-byte execution artifact](../audit/data/pio_interrupt_emulation.json)
records writes against **synthetic** register memory. The register names and
write-one semantics come from the [Microchip SAM7S datasheet](https://ww1.microchip.com/downloads/en/DeviceDoc/doc6175.pdf),
particularly the PMC, AIC, PIO and timer/counter register tables. The exact
installed chip suffix, board pin wiring and device effects have not been
measured.

## Entries and call boundaries

| Entry | Supported contract | Callers and limits |
|---|---|---|
| `0x74E8` | Configures PIOA, PMC and AIC, samples PIOA bit 17 into SRAM `0x200791`, then calls `0x6FB4`, `0x6BD8`, `0x575C`, `0x4330`, `0x725C`, `0x800C` in that order. Restores R4/R5 and stack on return. | Called from `0x77B8` at `0x77E8` and `0x78C0`, and from `0x50F0` at `0x55E4`. The emulator stops immediately before the first subordinate call; those six routines and complete device initialization remain separate review work. |
| `0x7448` | Callback address installed in AIC source vector 2 as Thumb pointer `0x7449`; reads PIOA pin 30 and two SRAM flags, conditionally writes timer/counter control commands, masks and clears source 2, and reads PIOA interrupt status. | Invoked in the harness as a Thumb routine. Actual IRQ entry/return context and timing are not simulated. |
| `0x7498` | Reads AIC interrupt mask at `0xFFFFF110` into SRAM `0x20079C`, then writes all ones to AIC interrupt disable command at `0xFFFFF124`. | Called by `0x6B20` around its SRAM flash helper. No hardware mask state is emulated. |
| `0x74B4` | Writes the saved `0x20079C` mask to AIC interrupt enable command at `0xFFFFF120`. | Also called by `0x6B20` after the flash helper. This re-enables saved sources; it is not a proof that the mask is restored exactly if another path enabled sources in between. |

`0x200798` is initialized from image source `0x9E80` to `0xFFFFF000`, the
AIC base, explaining the indirect AIC writes in `0x74E8`. The bounded decode
ends at each returning instruction and excludes adjacent literal pools.

## Direct setup sequence at `0x74E8`

The table lists the **ordered bus writes** in the original-byte prefix. A
write to a command register is not equivalent to storing a new readable
register value. The artifact retains the instruction site for each write.

| Register | Address | Value written | Datasheet-level meaning |
|---|---|---:|---|
| AIC_IDCR | `0xFFFFF124` | `0xFFFFFFFF` | Disable AIC sources. |
| PMC_PCDR | `0xFFFFFC14` | `0xFFFFFFFF` | Disable peripheral clocks. |
| PMC_PCER | `0xFFFFFC10` | `0x00000004` | Enable PID 2, PIOA. |
| PIO_PER, PIO_OER | `0xFFFFF400`, `0xFFFFF410` | `0x03208383` | Select PIO control and output direction for mask bits. |
| PIO_ODR, PIO_PER | `0xFFFFF414`, `0xFFFFF400` | `0xFCDF7C7C` | Complementary input-direction mask; together the PER writes cover all 32 bit positions. |
| PIO_CODR | `0xFFFFF434` | `0x03208383` | Clear output data for mask bits. |
| PIO_OWDR, PIO_OWER | `0xFFFFF4A4`, `0xFFFFF4A0` | `0xFCDF7C7C`, `0x03208383` | Set direct output-write mask. |
| PIO_MDDR, PIO_MDER | `0xFFFFF454`, `0xFFFFF450` | `0xFDFF97FF`, `0x02006800` | Disable/enable multi-driver by mask. |
| PIO_PUDR, PIO_PUER | `0xFFFFF460`, `0xFFFFF464` | `0xFFFDFFFF`, `0x00020000` | Disable/enable pull-ups by mask. |
| PIO_ASR, PIO_BSR, PIO_PDR | `0xFFFFF470`, `0xFFFFF474`, `0xFFFFF404` | `0x7860`, `0x88001`, `0x8F861` | Select peripheral A/B for some lines and hand selected lines to peripherals. |
| AIC_IDCR | `0xFFFFF124` | `0x00000004` | Disable source 2 during setup. |
| AIC_SVR2 | `0xFFFFF088` | `0x00007449` | Set Thumb callback address `0x7448`. |
| AIC_SMR2 | `0xFFFFF008` | `0x00000047` | Priority 7; SRCTYPE bits `10` (high-level-sensitive internal source). |
| AIC_ICCR | `0xFFFFF128` | `0x00000004` | Clear pending source 2. |
| PIO_IER | `0xFFFFF440` | `0x40000000` | Enable input-change interrupt bit 30. |
| AIC_IECR | `0xFFFFF120` | `0x00000004` | Enable AIC source 2. |

The source reads PIO_PDSR at `0xFFFFF43C`. If bit 17 is clear, it stores 1
at `0x200791`; if set, it stores 0. Both synthetic pin states produced the
same 23 MMIO writes and their expected opposite SRAM bytes. These are
software-observed branches. Register side effects, actual pin voltage, and
which external signal occupies that pin are unverified.

## Source 2 callback and mask helpers

The callback at `0x7448` tests PIO_PDSR bit 30. When that bit is low and
`0x200788` is nonzero, it writes `5` (CLKEN + SWTRG) to TC0_CCR at
`0xFFFA0000`. If `0x200789` is also nonzero it writes `5` to TC1_CCR at
`0xFFFA0040` first. It then writes bit 2 to AIC_IDCR and AIC_ICCR, and reads
PIO_ISR at `0xFFFFF44C`. Synthetic cases with pin 30 high or `0x200788=0`
made no MMIO writes; the two enabled cases produced the exact branches and
writes in the artifact. No timer clock rate or pulse duration is inferred.

The mask helpers were exercised with synthetic AIC_IMR=`0x12345678`:
`0x7498` saved that value at `0x20079C` and wrote `0xFFFFFFFF` to AIC_IDCR;
`0x74B4` wrote `0x12345678` to AIC_IECR. Their static caller `0x6B20`
places them around the copied-to-SRAM flash command helper. This relates
interrupt masking to that critical section but does not validate flash
controller behavior.

## Remaining work

The six subordinate setup calls from `0x74E8` need instruction-level
contracts. The callback's IRQ wrapper, priority interactions and actual
pin wiring need separate review. The SAM7S family includes variants with
different exposed pins, so writing a bit mask does not prove a particular
board pin exists. The existing main-loop path can call `0x74E8` again;
this review does not establish a live reinitialization frequency.

## Reproduction

```text
PYTHONPATH=<Binary Ninja Python path> python audit/tools/decode_image_ranges.py firmware_v2.8.4HF.bin --ranges 0x7448:0x7486:thumb2,0x7498:0x74b2:thumb2,0x74b4:0x74c2:thumb2,0x74e8:0x7598:thumb2 --output audit/data/pio_interrupt_binaryninja.json
uv run --with unicorn==2.1.4 python audit/tools/emulate_pio_interrupt.py firmware_v2.8.4HF.bin --output audit/data/pio_interrupt_emulation.json
python -m unittest discover -s tests -t .
```

The harness checks the image hash, maps fake MMIO memory and stops the
coordinator before any subordinate call. Binary Ninja's Thumb decoder is a
superset of the target ARMv4T ISA; mode, bounds and visited paths are explicit
in the evidence. Neither command sends device traffic.
