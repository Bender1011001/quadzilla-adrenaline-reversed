# SPI and source-5 interrupt setup: bounded firmware review

This review covers Thumb entries `0x6BD8` and `0x6B44` in the exact 32,000-byte
V2.8.4HF application image, SHA-256
`1ae519ba6194e8f7bdaaa94333a83a9e6fda3b0563f87f7d48383b37288c1780`.
The [bounded decode](../audit/data/spi_setup_binaryninja.json) accounts for
62 instruction bytes. The [original-byte execution artifact](../audit/data/spi_setup_emulation.json)
records the ordered accesses to synthetic MMIO. Register names and access
types follow the [Microchip SAM7S datasheet](https://ww1.microchip.com/downloads/en/DeviceDoc/doc6175.pdf),
particularly its SPI register map. The exact installed part suffix and external
SPI wiring have not been verified.

## Call and vector relationship

`0x74E8` calls `0x6BD8` during board setup, after the timer setup call.
The 60-byte `0x6BD8..0x6C13` body has no subordinate call and returns with
`BX LR`. It installs odd Thumb address `0x6B45` into AIC_SVR5. Source
`0x6B44..0x6B45` consists solely of `BX LR`; bounded execution makes no
register writes. It is a no-op callback body, not a reconstruction of IRQ
entry or exit. The generic interrupt wrapper and any effect of returning
without a source-specific action remain to be reviewed.

## Ordered setup writes

The image literal pool at `0x6C14..0x6C47` contains the target addresses and
constants; its words are recorded in the execution artifact and excluded from
the instruction range. The exact original-byte bus writes are:

| Instruction | Register / address | Value | Datasheet-level meaning |
|---|---|---:|---|
| `0x6BDC` | PMC_PCER `0xFFFFFC10` | `0x20` | Enable peripheral clock ID 5. |
| `0x6BE2` | SPI_MR `0xFFFE0004` | `1` | Master mode. |
| `0x6BE8` | SPI_CSR0 `0xFFFE0030` | `0x3002` | Chip-select register 0 configuration; no clock frequency inferred. |
| `0x6BEC` | SPI_CR `0xFFFE0000` | `1` | SPIEN command. |
| `0x6BF4` | AIC_IDCR `0xFFFFF124` | `0x20` | Disable source 5 while configuring it. |
| `0x6BF8` | AIC_SVR5 `0xFFFFF094` | `0x6B45` | Install Thumb callback at `0x6B44`. |
| `0x6BFE` | AIC_SMR5 `0xFFFFF014` | `0x21` | Raw source mode/priority word. |
| `0x6C02` | AIC_ICCR `0xFFFFF128` | `0x20` | Clear pending source 5. |
| `0x6C08` | SPI_IDR `0xFFFE0018` | `0xFFF` | Disable the low 12 SPI interrupt sources. |
| `0x6C0C` | AIC_IECR `0xFFFFF120` | `0x20` | Enable AIC source 5. |
| `0x6C10` | SPI_IER `0xFFFE0014` | `1` | Enable SPI receive-data-full interrupt. |

Before AIC_IDCR, `0x6BF0` reads the previous AIC_SVR5 word, then the code
overwrites that register value with the literal AIC_IDCR address. The read
has no observed effect on subsequent writes: synthetic previous-vector
values `0` and `0xDEADBEEF` yielded the same 11 writes. The SPI_IDR value
is obtained by shifting its **address** (`0xFFFE0018`) right by 20, yielding
`0xFFF`. It is not a read of SPI status. The register at offset `0x18` is
SPI_IDR according to the datasheet.

## Limits and next work

The harness has plain memory at PMC, SPI and AIC addresses. It does not model
clock gating, SPI command semantics, peripheral status, IRQ entry/exit, or an
external transfer. Thus the writes establish firmware intent and arithmetic,
not a functioning live SPI bus or actual interrupt rate. The receive interrupt
path through the IRQ wrapper and any related transport use remain open.
The larger timer callback at `0x6C94` is also pending a separate review.

## Reproduction

```text
PYTHONPATH=<Binary Ninja Python path> python audit/tools/decode_image_ranges.py firmware_v2.8.4HF.bin --ranges 0x6b44:0x6b46:thumb2,0x6bd8:0x6c14:thumb2 --output audit/data/spi_setup_binaryninja.json
uv run --with unicorn==2.1.4 python audit/tools/emulate_spi_setup.py firmware_v2.8.4HF.bin --output audit/data/spi_setup_emulation.json
python -m unittest discover -s tests -t .
```

The tools check the exact image hash. The firmware image is not distributed in
the repo, and the commands do not access a device.
