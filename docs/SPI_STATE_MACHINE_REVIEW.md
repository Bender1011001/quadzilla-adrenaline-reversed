# SPI output state routine and nine-byte payload packing

This review covers Thumb entry `0x5CF0..0x5DE9` in the exact 32,000-byte
V2.8.4HF application image, SHA-256
`1ae519ba6194e8f7bdaaa94333a83a9e6fda3b0563f87f7d48383b37288c1780`.
The [bounded decode](../audit/data/spi_state_machine_binaryninja.json) contains
250 bytes and 118 instruction starts. The byte-verified IDA item export
matches all 118 boundaries in this range. The [original-byte execution artifact](../audit/data/spi_state_machine_emulation.json)
contains 76 controlled cases whose union visits all 118 starts. It calls the
real [SPI/PDC primitives](SPI_TRANSFER_REVIEW.md), using synthetic register
memory without physical transfers or timing.

## Entry, inputs and storage

R0 is a reset request; nonzero takes the immediate reset path. R1 selects
between two gate families when R0 is zero. SRAM base `A=0x2005C4` comes from
literal `0x5DF0`. Its word at `A+0x1C` (`0x2005E0`) is initialized from image
source `0x9CC8` to SPI base `0xFFFE0000`.

| Address | Established use in this routine |
|---|---|
| `0x2005DF` (`A+0x1B`) | State byte: dispatches 0, 1, 2 and 5; other values fall through without state work. |
| `0x2005D4` (`A+0x10`) | Request/flag byte written as 1 on reset or idle state-0 paths. External meaning remains open. |
| `0x2005D5` (`A+0x11`) | Pending/flag byte that gates state 0/1 actions and is cleared by several transitions. |
| `0x20042D`, `0x20042E` | When R1=0, either nonzero permits state dispatch. |
| `0x20042A` | When R1 is nonzero, this gate alone permits dispatch. |
| `0x200688` (`A+0xC4`) | Pointer passed to the four-count transmit helper; this routine does not modify those bytes. |
| `0x2006C0` | Nine-byte payload buffer; byte 0 is preserved and bytes 1–8 are assembled in state 2. |

If the selected gates are false, the routine sets state=0, pending=0 and
request=1. A nonzero R0 instead sets state=0 and request=1 while preserving
the pending byte. The supplied byte values are flags, not verified names for
external signals or settings.

Known callers are `0x575C` and `0x76CC`. The setup path calls with R0=1 at
`0x59C0`. The `0x76CC` path calls with R0=0 and R1 from the preceding
`0x50F0` return at `0x76EA`. Both callers ignore this routine's immediate R0
value; it has no uniform success/failure return contract. All controlled
calls preserve R4–R7 and return with balanced stack.

## State transitions under an enabled gate

The readiness predicate requires SPI_SR.ENDTX and PIOA pin-status bit 11.
PIOA pin-status bit 2 is a separate branch input. Register meanings are
from the [SAM7S datasheet](https://ww1.microchip.com/downloads/en/DeviceDoc/doc6175.pdf);
external wiring and electrical levels have not been measured.

| State | Condition | Writes and next state |
|---|---|---|
| 0 | Pending=0 | Set request=1; remain 0. |
| 0 | Pending nonzero | Try a four-count transmit from `0x200688`. On helper success, state=2 and a halfword store clears both request and pending. On failure, remain 0 without those stores. |
| 1 | Pending=0 | No state action. |
| 1 | Pending nonzero, PIOA bit 2 low | Try the four-count transmit, then set state=2 and pending=0 **regardless of helper return**. |
| 1 | Pending nonzero, PIOA bit 2 high | Skip the transmit; set state=2 and pending=0. |
| 2 | Readiness false | No state action. |
| 2 | Readiness true, PIOA bit 2 low | Try the four-count transmit and remain 2. |
| 2 | Readiness true, PIOA bit 2 high | Build the payload, try a nine-count transmit from `0x2006C0`, then set state=5 **regardless of helper return**. |
| 5 | SPI_SR.ENDRX clear | Remain 5. |
| 5 | SPI_SR.ENDRX set | Call selector `0x571C(2)`, writing `0x200` to PIO_CODR, then set state=1. |

The state-5 path tests ENDRX even though the state-2 action programs the
transmit helper. This is the observed predicate, without an assumption about
how receive status is maintained elsewhere. Higher-level caller and
peripheral interaction review must explain that relationship.

## Exact payload bytes and signed arithmetic

State 2 preserves byte 0 at `0x2006C0` and writes:

| Payload offset | Source / operation |
|---:|---|
| 1, 2 | Low two bytes of word `0x200600` (`A+0x3C`), low byte first. |
| 3, 4 | Bytes `0x2005C7`, `0x2005C8`. |
| 5 | Low byte of remainder `r=n-256*q`, where `n` is signed word `0x200604`. |
| 6 | Low byte of `q=trunc(n/256)` toward zero. |
| 7, 8 | Bytes `0x2005CB`, `0x2005CC`. |

Instructions `0x5DAE..0x5DB8` implement the signed quotient with a 255 bias
for negative input before the arithmetic right shift. The stores truncate
both remainder and quotient to bytes. This differs from simply taking the
low two bytes of a negative two's-complement word: for `n=-1`, offsets 5/6
are `FF 00`; for `n=-257`, they are `FF FF`. Ten controlled signed-word
probes, including both signed extremes, match an independent integer model
of that sequence. The artifact uses a controlled byte-0 canary `A7`; that
value is not claimed to be the live SPI opcode.

The initialized prefix at `0x2006C0` is `45`. Under the subsequently
established [MCP2515-compatible layout](SPI_CAN_CONTROLLER_REVIEW.md), it
loads TXB2 data D0–D7. Thus offsets 5/6 above are CAN data bytes D4/D5;
the identifier and DLC are configured separately. This interpretation
assumes that the initialized opcode remains unchanged along the path.

The word at `0x200604` is part of the previously identified capture/telemetry
path. Its valid range and whether negative values reach this packing code
remain unresolved. The observed encoding difference is established for
controlled inputs; a protocol violation or live data-corruption finding
requires that range and the receiving format to be established.

## Conditional progress despite a failed transfer helper

The state-1 and state-2 paths described above discard a helper result. A
controlled `readiness_changes` case supplies SPI_SR=`0x20` for the initial
readiness read, then `0` for the helper's second read, with PIOA bits 11 and
2 set. The original routine builds the payload and advances from state 2 to
5 while making **no PDC programming writes**, because the helper rejects
the second status sample. A stable-ready case programs the expected three
transmit registers. This reproduces the instruction-level progress rule.

The scripted status change is explicit in the artifact. It is not a measured
race, and the analysis does not establish that the hardware can change in
that way during these instructions. Determining whether the transition can
lose a transfer requires interrupt/PDC status ownership and caller scheduling
evidence. The state-1 false-ready matrix cases also advance to 2 and clear
pending without transfer writes, as specified by the code.

## Scope and reproduction

The matrix covers states 0/1/2/5 and an unsupported value, pending flags,
gate families, ready/not-ready status, both PIO branches, reset, and the
payload probes. Single-call state combinations do not model complete live
handshakes or concurrent code. Buffer contents, gate flags and status reads
are controlled; no PDC transfer or external transaction occurs. Literal
words `0x5DEC..0x5E03` and adjacent alignment remain excluded from the
reviewed instruction range. Binary Ninja's decoder supports a superset of
ARMv4T; explicit bounds, IDA boundaries and visited paths are preserved.

```text
PYTHONPATH=<Binary Ninja Python path> python audit/tools/decode_image_ranges.py firmware_v2.8.4HF.bin --ranges 0x5cf0:0x5dea:thumb2 --output audit/data/spi_state_machine_binaryninja.json
uv run --with unicorn==2.1.4 python audit/tools/emulate_spi_state_machine.py firmware_v2.8.4HF.bin --output audit/data/spi_state_machine_emulation.json
python -m unittest discover -s tests -t .
```

The tools require the exact image hash and never access a device.
