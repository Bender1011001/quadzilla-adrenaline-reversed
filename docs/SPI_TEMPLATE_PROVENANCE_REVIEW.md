# SPI data provenance for two code-address candidates

This review follows two of the six unresolved byte windows from the
[execution-discovery audit](EXECUTION_DISCOVERY_REVIEW.md). It uses the exact
V2.8.4HF image, SHA-256
`1ae519ba6194e8f7bdaaa94333a83a9e6fda3b0563f87f7d48383b37288c1780`.
Both windows have an established SPI-data interpretation. No additional
execution entry or control-flow use of either four-byte value is established.
The supported minimum remains 157 source entries.

The [source-bound artifact](../audit/data/spi_template_provenance.json) checks
the original initialized-data descriptor at `0x96C4`: length `0x8A0`, destination
`0x200000`, source `0x96E8`. It then executes six selected paths through the
original capture and transfer helpers using synthetic SRAM/MMIO. The existing
[parser review](CAPTURE_PARSER_REVIEW.md) supplies the wider state-machine
account; this pass specifically connects the suspicious bytes to the transfer
arguments and programmed PDC descriptors.

## Why the apparent addresses occur

| Image window | Initialized SRAM window | Little-endian value | Actual constituent bytes |
|---|---|---|---|
| `0x9D7B..0x9D7F` | `0x200693..0x200697` | `0x00009200` | Last byte `00` of the four-byte command at `0x200690`, then `92 00 00` at the start of the RXB0 template. |
| `0x9D87..0x9D8B` | `0x20069F..0x2006A3` | `0x00009400` | Last zero of the three-byte gap `0x20069D..0x2006A0`, then `94 00 00` at the start of the RXB1 template. |

All range ends in this review are exclusive. The bounded transmit extents are:

| SRAM start | Length | Initialized bytes | Established role |
|---|---:|---|---|
| `0x20068C` | 4 | `05 2C 01 00` | RXB0 interrupt-clear command. |
| `0x200690` | 4 | `05 2C 02 00` | RXB1 interrupt-clear command. |
| `0x200694` | 9 | `92`, then eight zeros | RXB0 read command and dummy clock bytes. |
| `0x2006A0` | 14 | `94`, then thirteen zeros | RXB1 read command and dummy clock bytes. |

The command interpretation is established separately in the
[MCP2515-compatible layout review](SPI_CAN_CONTROLLER_REVIEW.md). This pass
requires no additional hardware or protocol assumption to establish the
byte boundaries and original software arguments. The three zero bytes between
the two read templates lie outside these selected transmit extents; their
global use or mutability is not proven absent.

## Original-instruction consumers

The capture entry loads `A=0x2005C4` at `0x59EE`. On the RXB0 start path,
`0x5A72..0x5A7A` builds `(base, A, A+0xD0, 9)`. On the RXB1 path,
`0x5A9E..0x5AA4` builds `(base, B, A+0xDC, 14)`, where `B=0x200AB4`.
Both reach the original paired-transfer helper `0x6B9C` at `0x5A7C`.

Inside that helper, `0x6BBC` writes the transmit pointer to `0xFFFE0108`,
`0x6BBE` writes its count to `0xFFFE010C`, and `0x6BC0/0x6BC2` write the
distinct receive pointer/count at `0xFFFE0100/104`. Thus these initialized
templates supply transmit bytes; incoming data goes to other SRAM buffers.
The phase-2 paths separately request four-byte commands at `A+0xC8/CC`
through `0x6B64` at `0x5AB4/0x5AF4`.

Six original-byte cases cover both receive-start paths with ready and blocked
status, plus both phase-2 interrupt-clear paths with ready status. The four
ready cases program the expected transmit pointer/count; the two blocked
cases do not. The memory hooks observe no CPU read or write overlapping
`0x200690..0x2006AE` in those cases. That is consistent with descriptor setup:
the CPU passes addresses to PDC registers instead of loading a four-byte
callback from the windows. The emulator does not execute a DMA engine, so the
artifact reports initialized source bytes at the descriptor, not observed
SPI wire traffic.

## Scope still open

The two windows no longer lack a storage/consumer interpretation, but this is
not an exhaustive global writer or consumer proof. Other computed addresses,
runtime mutation, remap aliases, interrupt interactions and other callers
remain outside these six cases. The original discovery inventory is preserved
as the earlier scan result and linked to this subsequent disposition. The
other four compatible windows retain their existing unresolved provenance.

```sh
python audit/tools/audit_spi_template_provenance.py firmware_v2.8.4HF.bin --output audit/data/spi_template_provenance.json
python -m unittest discover -s tests -t .
```

No device traffic, settings change or hardware measurement was performed.
