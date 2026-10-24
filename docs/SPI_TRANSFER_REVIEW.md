# SPI/PDC transfer primitives and PIO selectors

This review covers six Thumb entries in the exact 32,000-byte V2.8.4HF
application image, SHA-256
`1ae519ba6194e8f7bdaaa94333a83a9e6fda3b0563f87f7d48383b37288c1780`.
The [bounded decode](../audit/data/spi_transfer_binaryninja.json) accounts for
186 bytes and 91 instruction starts. The [original-byte execution artifact](../audit/data/spi_transfer_emulation.json)
contains 27 controlled cases whose union visits all 91 starts. SPI, PDC and
PIO register names follow the [Microchip SAM7S datasheet](https://ww1.microchip.com/downloads/en/DeviceDoc/doc6175.pdf),
sections 22, 27 and 28. The emulator uses synthetic register memory without
PDC transfers, device effects or timing.

## Entry contracts

| Entry and instruction bounds | Inputs | Supported output and effects | Known callers |
|---|---|---|---|
| `0x571C..0x5735` | R0 selector | Selector 1 writes `0x100` to PIO_CODR `0xFFFFF434`; selector 2 writes `0x200`. Other values make no register write. R0 holds the mask on selected paths. | `0x5CF0` |
| `0x573C..0x5755` | R0 selector | Selector 1 writes `0x100` to PIO_SODR `0xFFFFF430`; selector 2 writes `0x200`. Other values make no register write. R0 holds the mask on selected paths. | `0x575C`, `0x59E8` |
| `0x6B48..0x6B5F` | R0 peripheral base | Return 1 only when base+`0x10` bit 5 and PIO_PDSR bit 11 are both set; otherwise return 0. The PIO register is read only if the first condition passes. No writes. | `0x5CF0`, `0x6B64`, `0x6B9C` |
| `0x6B64..0x6B8B` | R0 base, R1 transmit pointer, R2 count | Call `0x6B48`; if false, return 0 without MMIO writes. Otherwise write PTCR=`0x100`, TPR=R1, TCR=R2 in that order and return 1. | `0x575C`, `0x59E8`, `0x5CF0`, `0x5E04` |
| `0x6B8C..0x6B9B` | R0 peripheral base | Return base+`0x10` bit 4 as 0 or 1. No writes. | `0x5CF0` |
| `0x6B9C..0x6BD1` | R0 base, R1 receive pointer, R2 transmit pointer, R3 shared count | Call `0x6B48`; if false, return 0 without MMIO writes. Otherwise read SPI_RDR, program the six writes below, and return 1. | `0x575C`, `0x59E8` |

The selector literals at `0x5738` and `0x5758` contain `0xFFFFF434` and
`0xFFFFF430`. The readiness literal at `0x6B60` contains PIO_PDSR
`0xFFFFF43C`; the read literal at `0x6BD4` contains SPI_RDR `0xFFFE0008`.
These literal words are excluded from the instruction ranges. Selector masks
address PIOA bits 8 and 9; the image alone does not establish their external
signal names. No direction or peripheral selection is configured by these
two helpers.

At the known SPI base `0xFFFE0000`, status bits 5 and 4 are ENDTX and ENDRX.
The predicates report the sampled status and pin condition. ENDTX indicates
a PDC transmit-buffer condition; it does not by itself prove a complete
electrical transaction or a particular slave's response. A true predicate
is distinct from completion of a newly requested transfer.

## Exact PDC write order

PDC registers are relative to the supplied peripheral base. In the paired
helper, the fixed SPI_RDR read is performed even though the base argument is
otherwise used for PDC addressing; the loaded value is discarded. A real
SPI_RDR read can affect peripheral status, which synthetic memory does not
model.

| Helper | Ordered writes relative to base |
|---|---|
| `0x6B64` | `+0x120=0x100` (PTCR TXTEN), `+0x108=R1` (TPR), `+0x10C=R2` (TCR) |
| `0x6B9C` | `+0x120=0`, `+0x108=R2` (TPR), `+0x10C=R3` (TCR), `+0x100=R1` (RPR), `+0x104=R3` (RCR), `+0x120=0x101` (PTCR RXTEN + TXTEN) |

PTCR command bits written as zero have no enabling/disabling effect in the
datasheet model. In particular, the paired helper's initial zero write is
not a channel-disable command. The transmit helper writes TXTEN **before**
updating its pointer/count. These are observed instruction orders, with no
claim that asynchronous peripheral behavior has been tested.

Neither helper checks pointer range, alignment, buffer size or count before
writing registers. Controlled direct calls with count 0 and `0xFFFFFFFF`
and unusual pointer values reproduce unchanged 32-bit bus writes when the
gate is true. The helpers themselves do not dereference those buffers in
software. Hardware counter width and asynchronous memory access require the
PDC/device model; this evidence does not demonstrate an unsafe value reaching
the helpers through a live caller.

## Decoder adjudication and verification

The baseline catalog already contains `0x6B48` from Ghidra evidence. IDA's
full-image export instead has a `VTBL.8` item beginning at `0x6B46` that
swallows the actual `LDR` at `0x6B48`. That NEON interpretation is not an
ARM7TDMI instruction stream. Explicit Thumb decoding from `0x6B48` and
bounded original-byte execution recover the predicate above. This review
does not count the preceding halfword or neighboring literals as code.
Binary Ninja's selected Thumb decoder is a superset of ARMv4T; its explicit
bounds and the executed paths are retained in the evidence.

Selector cases 0/1/2/3 cover both output masks and no-write paths. All four
ENDTX/pin-11 combinations exercise the readiness gate and both transfer
helpers. ENDRX cases include clear, set and all-ones status. Every case
returns with balanced stack and preserved R4–R7. Caller `0x5CF0` is documented
in the [SPI output state review](SPI_STATE_MACHINE_REVIEW.md). Higher-level
setup `0x575C`, timeout interactions and complete capture parsing remain
separate review work.

## Reproduction

```text
PYTHONPATH=<Binary Ninja Python path> python audit/tools/decode_image_ranges.py firmware_v2.8.4HF.bin --ranges 0x571c:0x5736:thumb2,0x573c:0x5756:thumb2,0x6b48:0x6b60:thumb2,0x6b64:0x6b8c:thumb2,0x6b8c:0x6b9c:thumb2,0x6b9c:0x6bd2:thumb2 --output audit/data/spi_transfer_binaryninja.json
uv run --with unicorn==2.1.4 python audit/tools/emulate_spi_transfers.py firmware_v2.8.4HF.bin --output audit/data/spi_transfer_emulation.json
python -m unittest discover -s tests -t .
```

Source-consuming commands require the exact image hash and access no device.
