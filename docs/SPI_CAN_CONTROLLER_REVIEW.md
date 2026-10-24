# SPI command evidence for an MCP2515-compatible CAN controller

The exact V2.8.4HF image, SHA-256
`1ae519ba6194e8f7bdaaa94333a83a9e6fda3b0563f87f7d48383b37288c1780`,
contains a consistent MCP2515-compatible SPI command/register path. This is
a firmware protocol interpretation. The owner's subsequent
[V2.2 board inventory](BOARD_V2_2_COMPONENTS.md) reports U2 marked MCP2515,
corroborating the interpretation. Board wiring, CAN traffic and successful
command execution have not been measured; the marking has not been
independently inspected by this project.

The [command audit](../audit/data/spi_can_command_audit.json) binds each
initialized SRAM buffer to its source-image address and decodes all 24
requests recorded by the [initializer review](SPI_INITIALIZATION_REVIEW.md).
It also decodes the seven request records and three receive/output templates.
The layout source is Microchip's [MCP2515 family datasheet DS20001801K](https://ww1.microchip.com/downloads/en/DeviceDoc/MCP2515-Family-Data-Sheet-DS20001801K.pdf),
sections 3, 4, 11 and 12. The pure decoder has no device I/O.

## Independent command/register correspondences

These matches occur in the original initialized buffers, rather than names
in a decompiler. The byte values and call order come from this firmware.

| Firmware command | Datasheet-compatible interpretation |
|---|---|
| `C0` | Controller reset command. |
| `02 0F 80`, later `02 0F 00` | CANCTRL configuration-mode request, then normal-mode request. |
| `03 0F 00` | Read CANCTRL with one response clock byte. |
| `02 28 05 F1 01` | Write CNF3/CNF2/CNF1. |
| Writes at `00/04/08/10/14/18` and `20/24` | Acceptance filter and mask register groups. |
| `02 60 00`, `02 70 00` | RXB0CTRL and RXB1CTRL writes. |
| `02 0C 0F`, `02 0D 06` | BFPCTRL and TXRTSCTRL writes. |
| `44 20 00`, `02 55 08` | Set TXB2 identifier prefix and its DLC. |
| `05 2C 01 00`, `05 2C 10 00` | Clear selected CANINTF bits. |

The breadth of matching opcodes, addresses and buffer formats supports the
compatible-controller interpretation. The reported U2 marking supplies
corroborating component identification; an independent marking inspection and
board traces remain useful verification. CNF bytes are recorded without
claiming a measured oscillator or bus rate.

## Conditional CAN bit timing

The owner reports the crystal immediately beside U2 marked `EC 16.0` and
`AEN F`, distinct from the MCU-side `18.4` marking. This supports a
**provisional 16 MHz MCP2515 oscillator**, not a measured frequency or traced
oscillator connection. See the [board record](BOARD_V2_2_COMPONENTS.md).

The source-bound initialization command `02 28 05 F1 01` writes
CNF3=`05`, CNF2=`F1`, CNF1=`01`. Applying the datasheet's section 5 and
registers 5-1 through 5-3 yields:

| Field | Decoded value |
|---|---|
| BRP field | 1, giving a time quantum of `2 * (1 + 1) / Fosc` |
| Synchronization segment | 1 TQ |
| Propagation segment | 2 TQ |
| Phase segment 1 | 7 TQ |
| Phase segment 2 | 6 TQ, selected by BTLMODE=1 |
| Total nominal bit | 16 TQ |
| Synchronization jump width | 1 TQ |
| Sampling | Three samples (SAM=1) |

Thus `bitrate = Fosc / (2 * 2 * 16) = Fosc / 64`.
At the provisional 16 MHz frequency, TQ is 250 ns, a nominal bit is 4 us,
and the **configured nominal rate is 250,000 bit/s**. The nominal sample
point is `(1 + 2 + 7) / 16 = 62.5%` of the bit time.

This is a conditional calculation from this image's initialization bytes
and the reported crystal marking. It does not establish the installed
firmware version, successful register programming, measured bus rate,
network identity or absence of later timing changes. A passive capture of
normal operation can test the predicted rate.

## Seven request records

Each nine-byte table record starts with `40`, a TXB0 identifier-start load,
and decodes as extended identifier `0x0CEA00F8`, DLC 3, followed by three
data bytes. The audit checks that all seven records contain their complete
three-byte data field. No application/PGN names are assigned here.

| Index | Image address | Data bytes |
|---:|---|---|
| 0 | `0x9FF0` | `EE FE 00` |
| 1 | `0x9FF9` | `03 F0 00` |
| 2 | `0xA002` | `F7 FE 00` |
| 3 | `0xA00B` | `EF FE 00` |
| 4 | `0xA014` | `F1 FE 00` |
| 5 | `0xA01D` | `F5 FE 00` |
| 6 | `0xA026` | `F6 FE 00` |

The [request selector](CAPTURE_HELPER_REVIEW.md) follows the table load with
`02 (30/40/50) (08 OR priority)`. Under this register map, its mode selects
TXB0/TXB1/TXB2 control, bit 3 requests transmission, and the clamped low two
bits select priority. This establishes software intent without proving a
message was accepted onto a live bus.

## Receive and output layouts

| Initialized buffer | Prefix / length | Compatible register layout after the opcode clock |
|---|---|---|
| `0x200694` | `92`, 9 bytes | RXB0 data bytes D0–D7. |
| `0x2006A0` | `94`, 14 bytes | RXB1 identifier registers, DLC, then D0–D7. |
| `0x2006C0` | `45`, 9 bytes | TXB2 data bytes D0–D7. |

The opcode-clock response occupies byte 0 of a receive buffer. This makes
the capture routine's nine-byte and fourteen-byte paths structurally
different. The subsequent [complete parser entry review](CAPTURE_PARSER_REVIEW.md)
documents its matching and scaling, absent local DLC guard and retained
outputs. Live short-frame behavior remains unverified.

The initializer explicitly writes TXB2 SIDH=`20`, SIDL=`00` and DLC=`08`,
which decode as standard identifier `0x100` and eight data bytes. EID fields
are unnecessary for that standard-ID interpretation. With its initialized
`45` prefix, the [output state routine](SPI_STATE_MACHINE_REVIEW.md) writes
eight data bytes into TXB2. In its payload table, offsets 5/6 are therefore
data bytes D4/D5; its signed quotient/remainder arithmetic is not operating
on the CAN DLC field. Later writers or changed command prefixes remain a
separate reachability question.

## Validation and hardware evidence still needed

The source-bound audit checks the exact image hash, initialized-data mapping,
original call arguments, table stride and explicit TXB2 writes. Decoder tests
cover standard and extended identifier bit placement and command selectors.
This evidence adds protocol context without retiring unreviewed parser code
or increasing instruction coverage by itself.

Useful discriminating hardware checks are component identification, continuity
from MCU SPI/PIO lines to the controller, and passive capture of the setup
commands and bus frames. Oscillator/bus timing, chip-select behavior, GPIO
request/receive wiring, physical topology and actual CAN acceptance remain
unverified. No such hardware actions are performed by these tools.

```text
python audit/tools/audit_spi_can_commands.py firmware_v2.8.4HF.bin --output audit/data/spi_can_command_audit.json
python -m unittest discover -s tests -t .
```
