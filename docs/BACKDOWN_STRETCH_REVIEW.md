# Backdown candidates and applied-stretch arithmetic

This pass reviews original V2.8.4HF application bytes, SHA-256
`1ae519ba6194e8f7bdaaa94333a83a9e6fda3b0563f87f7d48383b37288c1780`.
The [bounded Binary Ninja decode](../audit/data/backdown_stretch_binaryninja.json)
reconciles all 118 Thumb starts in `0x499C..0x4A88` and 69 in
`0x4A94..0x4B28` with the byte-verified IDA item export. The last instruction
in the latter range is an alignment NOP, outside its returning body.
The [backdown reproducer](../audit/tools/emulate_backdown.py) and its
[result](../audit/data/backdown_emulation.json) execute original bytes in
4,126 controlled SRAM states. The previously published
[stretch execution](../audit/data/stretch_arithmetic_emulation.json) covers
2,092 cases and all 68 starts in its returning body. These are bounded
instruction tests, not validated vehicle states or measured output timing.

## Two backdown candidates at `0x499C`

The routine uses two independent enable bytes and stores two clamped candidate
percentages:

| Candidate | Enable and threshold | Current and history inputs | Stored state |
|---|---|---|---|
| First | `0x2006D7` and little-endian halfword `0x2006D8` | current word `0x2008A8`; previous word `0x200454`; prior signed percentage byte `0x200427` | new percentage `0x200427`, current word to `0x200454` when enabled |
| Second | `0x2006D3` and byte `0x2006D4` | current word `0x20044C`; prior byte `0x200428`; prior signed percentage byte `0x200429` | new percentage `0x200429`, low current byte to `0x200428` when enabled |

The working fields `0x2006D7..D9` are updated from staged **AID 150 / EGT
Defuel Setting**, and `0x2006D3..D4` from **AID 81 / Boost Defuel Setting**
by the [compound AID update review](COMPOUND_AID_UPDATE_REVIEW.md). The
[ADC review](ADC_PIPELINE_REVIEW.md) traces `0x2008A8` to the channel-4
filtered/lookup path. The physical sensor connected to that channel and the
meaning of the state word `0x20044C` remain unverified by this image.

For the first enabled candidate, the original instructions can increase the
signed byte by four when the current word exceeds `threshold-25` and the
previous word is below `current+10`; otherwise they can decrease it by one
when current is below both threshold and previous. A further unsigned
comparison against `threshold-300` can force zero. For the second enabled
candidate, comparisons of the state word with `threshold-2`, the old byte,
and `threshold-4` select increments of four or decrements of two or four.
Both paths narrow the arithmetic to a signed byte before clamping to
**0..80**. A disabled path stores zero for its percentage but leaves its
history field unchanged. The first enabled path stores a full previous word;
the second stores only the low byte of its current word.

The function returns the larger of the two stored candidate bytes. All 4,126
controlled cases confirmed this relationship, the 0..80 bound, enabled
history updates, and preservation of R4–R7/SP. They visited every one of the
118 decoded instruction starts. The cases include arbitrary prior bytes and
thresholds; proving live ranges and physical cause requires tracing all
writers and hardware inputs. Unsigned subtraction around small thresholds
is retained as exact 32-bit firmware arithmetic, not interpreted as a
signed physical threshold.

The direct caller in `0x50F0` tests a remainder at `0x522A`: only on zero does
it call `0x499C` at `0x522E` and write the returned low byte to `0x200BCD`
at `0x5234`. The denominator is 250; the loop counter's real-time cadence
is not established here. The [AID table audit](../audit/data/aid_table_audit.json)
maps `0x200BCD` as the AID 13 response pointer, whose profile name is
“Backdown Percentage” with a declared 0–100 range. This **specific automatic
writer** produces at most 80 under the tested and statically clamped path.
That does not prove every possible writer or every observed response has the
same bound; it also does not establish a defect from the profile difference.

## Applied stretch at `0x4A94`

`0x4A94..0x4B26` reads the internal signed-byte table at `0x200190`, the
requested working word at `0x200590`, captured word at `0x2005F0`, and
gate/ramp fields at `0x20058A..8C` and `0x200433..434`. It calls the
integer division helper repeatedly, retaining truncation at each stage,
and returns an applied scalar in R0. The [integer/stretched arithmetic
review](INTEGER_ARITHMETIC_REVIEW.md) gives the exact directed cases and
its guarded-divisor argument. In particular, high-bit table bytes are
sign-extended by `LDRSB`; whether those values are reachable through the
table writers remains open. The 2,092-case execution visited all 68
nonalignment instruction starts. The following `0x4B26` NOP and literal
words at `0x4B28..0x4B38` are classified separately.

The backdown body ends at `0x4A88`; its three literal words at
`0x4A88..0x4A94` are `0xFFFFFED4`, `0x2006CC`, and `0x2008A8`.
The stretch literal words at `0x4B28..0x4B38` are `0x200580`, `0x200190`,
`0x200424`, and `0x2005F0`. The reproducer checks these words against the
matching raw image before executing any case.

To regenerate the new bounded result with Unicorn installed and a locally
obtained matching image:

```sh
python audit/tools/emulate_backdown.py firmware_v2.8.4HF.bin --output audit/data/backdown_emulation.json
```

No device traffic, flash operation, or output command was performed.
