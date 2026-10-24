# CAN capture state machine and fixed-offset parser

This review covers the exact V2.8.4HF image, SHA-256
`1ae519ba6194e8f7bdaaa94333a83a9e6fda3b0563f87f7d48383b37288c1780`.
Entry `0x59E8` is Thumb, with instructions through `0x5CB9` and adjacent
literals excluded. The previously reviewed reset prefix and epilogue total
30 bytes; this review adds the remaining `[0x59FE,0x5CB2)` **692 bytes**.
All 315 added instruction starts have matching boundaries in the byte-verified
IDA export and the [explicit-mode Binary Ninja decode](../audit/data/capture_parser_binaryninja.json).
Binary Ninja's Thumb2 decoder is a superset of the target ISA; the bounded
instruction trace and execution, not that decoder's name, support this account.

The [original-byte execution artifact](../audit/data/capture_parser_emulation.json)
records 303 detailed cases, including representatives from 5,120 numeric sweep calls,
with zero differences against the stated reference formulas. The combined
cases visit all 329 starts in the complete entry, including reset and epilogue.
Instruction visits are not exhaustive path, concurrency or hardware validation.

## Contract, callers and storage

R0 nonzero takes the reset-only path: clear byte `0x2005DE`, set GPIO selector
2 through `0x573C`, return. R0 zero services capture. The low byte of R1 selects
which gate bytes are consulted on the RXB0 start path. R4–R7 and the stack are
preserved; no meaningful scalar return value is established.

Known direct callers are initializer `0x575C` at `0x59B8` with `(1,0)`, and
main-loop entry `0x76CC` at `0x76D8` with `(0, byte[0x20078F])`. This is evidence
of a main-loop call, not proof of an interrupt-free or race-free environment.

Let `A=0x2005C4`, `B=0x200AB4`. The SPI base is word `A+0x1C`.

| Storage | Role in this entry |
|---|---|
| `A+0..8` | Nine-byte receive buffer: opcode response plus RXB0 D0–D7. |
| `B+0..13` | Fourteen-byte receive buffer: opcode response, four identifier bytes, DLC, D0–D7. |
| `A+0xF` | Persistent RXB0 capture-request flag, conditionally set then cleared on capture start. |
| `A+0x10` | Additional capture-request input byte. |
| `A+0x11` | Output-pending flag set after RXB0 completion/pin release. |
| `A+0x12` | Selected receive kind: 1 for RXB0, 2 for RXB1. |
| `A+0x1A` | Phase byte: 2 parse/queue-clear, 1 completion/retry; all other values enter selection. |
| `A+0xC8`, `A+0xCC` | Four-byte transmit command buffers used after RXB0/RXB1 capture. |
| `A+0xD0`, `A+0xDC` | Initialized receive-command templates, `92` and `94`. |
| `0x200AFE` | Byte controlling one output adjustment; only exact value 1 enables it. |
| `0x2006E8` | Binary32 coefficient read by the floating scaling path. |

The buffer meanings follow the separately reviewed
[MCP2515 command layouts](SPI_CAN_CONTROLLER_REVIEW.md). Connector wiring and
the physical meaning of the raw PIO bits remain untraced.

## State transitions

For phases other than 1 or 2, read PIO_PDSR `0xFFFFF43C`. Bit 3 low selects
kind 1 first, even when bit 4 is also low. Define the gate as the OR of bytes
`0x20042D/0x20042E` when the low byte of R1 is zero; otherwise use byte
`0x20042A`. If that gate is zero or `A+0x10` is nonzero, set `A+0xF=1`.
An existing flag is retained when neither condition sets it.

If PIO bit 2 is high and `A+0xF` is zero, call the reviewed rotation helper
`0x5EBC` and return without starting capture. Otherwise clear `A+0xF`, set
GPIO selector 2, call `0x5EBC`, and request a nine-byte paired transfer
`0x6B9C(base,A,A+0xD0,9)`. Move to phase 2 only if that helper returns true.
The rotation helper can invoke its own blocking request/timeout sequence;
its behavior is documented in the [helper review](CAPTURE_HELPER_REVIEW.md).

When bit 3 is high, bit 4 low selects kind 2 and requests a fourteen-byte
paired transfer `0x6B9C(base,B,A+0xDC,14)`, again entering phase 2 only on
acceptance. Both bits high clears the selected-kind byte and returns.

| Current phase/kind | Condition and action |
|---|---|
| Phase 2, kind 1 | Try four-byte transmit from `A+0xC8` using `0x6B64`. Failure retains phase 2 and old outputs. Acceptance sets phase 1 and unpacks RXB0 immediately. |
| Phase 2, kind 2 | Same behavior using `A+0xCC`, then match and parse RXB1. An unmatched header still leaves phase 1. |
| Phase 2, other kind | Clear phase to zero. |
| Phase 1, kind 1 | Test ENDRX through `0x6B8C`; false retains phase. If true and PIO bit 3 remains low, try the four-byte transmit again and retain phase regardless of its result. If the pin is high, set `A+0x11=1` and clear phase. |
| Phase 1, kind 2 | Same ENDRX gate and retry using bit 4 / `A+0xCC`; pin high clears phase without setting `A+0x11`. |
| Phase 1, other kind | Clear phase. |

The transfer primitives are executed rather than replaced by successful
stubs. Their registers are synthetic plain memory: no DMA engine changes
status or fills buffers. The phase-2 parse is gated by successful TX setup
(ENDTX and PIO bit 11 in `0x6B64`), not an explicit ENDRX test. ENDRX is tested
in phase 1. A controlled `SPI_SR=0x20` case therefore parses while ENDRX is
clear. Whether real hardware ordering prevents an incomplete receive at that
point requires a PDC/SPI timing analysis and passive capture; no live race is
claimed from the synthetic case.

## RXB0 fields

Treat data bytes as unsigned. Write 32-bit values to:

| Destination | Computation |
|---|---|
| `A+0x20` (`0x2005E4`) | Little-endian word D0/D1. |
| `A+0x24` (`0x2005E8`) | Little-endian word D4/D5. |
| `A+0x28` (`0x2005EC`) | Floor of little-endian word D6/D7 divided by 4. |

The last expression uses signed-looking shift/bias instructions, but its
assembled input is unsigned 0..65535, so the bias is zero. D2/D3 are unused
by this entry. This receive template contains no identifier or DLC field.

## RXB1 header matches and outputs

Comparisons run in the following order. Four-byte rows compare all four raw
identifier registers, including their flag bits. The two-byte row compares
only SIDH/SIDL. Let `D0=B[6]`, ..., `D7=B[13]`, and `W=D6 | (D7 << 8)`.
Integer divisions below truncate nonnegative values. Byte destinations retain
only the low eight bits; word destinations retain low 32 bits.

| Raw matched prefix | Compared bytes | Destination and computation |
|---|---:|---|
| `67 88 03 00` | 4 | Word `A+0x2C=min(floor(4*D1/10),100)`; byte `A+0x16=D2`. |
| `C7 EA F1 00` | 4 | Byte `A+0x13`: staged floating conversion described below. |
| `C7 EA EE 00` | 4 | Word `A+0x30=floor(9*D0/5)-40`, wrapping for negative results. |
| `C7 EA F7 00` | 4 | Word `A+0x34=floor(5*W/10)`. |
| `C7 EA EF 00` | 4 | Byte `A+0x14=floor(58*D3/100)`. |
| `22 40` | 2 | Word `A+0x38=floor(1125*W/10000)-460`, wrapping for negative results. B[3:5] do not participate in matching. |
| `C7 EA F5 00` | 4 | Byte `A+0x18=B[1]>>1`, therefore **99 for this exact initialized header**, not a payload extraction. |
| `C7 EA F6 00` | 4 | Byte `A+0x17=floor(((2*D1) mod 256)/7)`; if byte `0x200AFE==1`, replace it with `max(value,13)-13`. Byte `A+0x15=floor(9*D2/5) mod 256`. |
| `D2 CA A5 A5` | 4 | Set byte `A+0x19=1` only if D0 is `BB`; otherwise retain it. |

No match retains every output field. Successful matches modify only their
listed fields. The `A+0x19` action is a set-only latch within this entry;
clearing it elsewhere is a separate writer analysis. Application signal names,
PGN labels and engineering units are not established by these formulas alone.

For the floating row, first compute `q=floor(62*D2/100)` as an integer. Convert
q to binary32, multiply by the binary32 coefficient at `0x2006E8`, round at
binary32 precision, widen to binary64, divide by binary64
`0x4057ECCCCCCCCCCD` (the stored approximation to 95.7), then convert to signed
integer and store its low byte. The initialized coefficient bits are
`0x42BF3333`; the reference uses exact rational arithmetic and IEEE rounding
at each stage. It does not replace that sequence with a single real-number
formula. Tests here use the initialized coefficient and finite byte inputs;
changed coefficients and exceptional float paths remain covered only by the
separate [numeric-runtime review](SOFT_FLOAT_REVIEW.md), not exhaustively by
this caller's cases.

## Consequential observations and limits

* **DLC is not consulted by the RXB1 parser.** No executed parser read accesses
  `B[5]`. Matching buffers with DLC 0 and DLC 8 produce the same updates in all
  5,120 numeric sweep calls. The parser reads offsets through B[13] on selected
  paths. This proves an absent local length guard; it does not prove malformed
  traffic reaches the installed device or determine controller contents beyond
  a short frame's valid data. A stale-buffer/short-frame consequence requires
  controller behavior and caller sequencing evidence.
* **Eight-bit narrowing precedes one division.** At D1=127 the F6-header path
  produces 36 before the optional adjustment; D1=128 produces zero. The
  `0x8564` unsigned-byte divider masks the doubled input. The second output
  also wraps: D2=255 produces `459 mod 256 = 203`. Expected input ranges and
  downstream consequences are not yet established.
* **A header byte is used as data in one branch.** The F5 match writes 99 from
  the matched `C7` header. This is the instruction behavior, whether deliberate
  or erroneous; no intended signal specification is available to adjudicate it.
* **Old values persist.** Unknown headers, failed phase-2 setup and unmatched
  set-only conditions retain destination values. No timestamp/freshness reset
  occurs in this entry. Consumers must be traced before assigning impact.

The scalar formulas, local guards and state transitions are reviewed. Physical
PIO wiring, live CAN acceptance, interrupt/DMA interleaving, coefficient
writers, downstream field consumers and meaningful sensor units remain explicit
follow-up work. This is a completed bounded entry account, not full firmware
or hardware acceptance.

## Reproduction

```text
PYTHONPATH=<Binary Ninja Python path> python audit/tools/decode_image_ranges.py firmware_v2.8.4HF.bin --ranges 0x59fe:0x5cb2:thumb2 --output audit/data/capture_parser_binaryninja.json
uv run --with unicorn==2.1.4 python audit/tools/emulate_capture_parser.py firmware_v2.8.4HF.bin --output audit/data/capture_parser_emulation.json
python -m unittest discover -s tests -t .
```
