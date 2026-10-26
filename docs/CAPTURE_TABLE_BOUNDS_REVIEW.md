# Direct caller bounds for the `0x4B38` signed-table lookup

The previous [capture scalar review](CAPTURE_SCALAR_REVIEW.md) identified a
signed-byte load at `0x4CEC` without a bounds check inside `0x4B38`. This pass
traces the two supplied indices backward through its only decoded direct
caller, `0x50F0` at `0x52D2`. The
[reproducible bound artifact](../audit/data/capture_table_bounds.json) is tied
to the exact 32,000-byte V2.8.4HF image, SHA-256
`1ae519ba6194e8f7bdaaa94333a83a9e6fda3b0563f87f7d48383b37288c1780`.

## Stack transfer and index formulas

The main routine reserves local stack space at `0x50F2`. Its byte at local
`SP+1` is assigned along every decoded branch before `0x52AE` reads it. The
source is unsigned word `W = word[0x2005EC]`. Thresholds and division constants
are actual literal and instruction values; unsigned division at `0x8574`
returns the quotient in R1:

```text
column(W) = 0                                  if W < 900
          = floor(19 × (W − 900) / 500)        if 900 ≤ W ≤ 1400
          = 19                                 if W ≥ 1401
```

In the middle interval, `W−900` is at most 500, so multiplication cannot
overflow 32 bits and the quotient is 0..19. The high branch assigns 19
directly, including for words with the high bit set. The code also forms a
different local byte at `SP+0` with a 0..12 range; that byte is not the column
passed to this table lookup.

The word `P = word[0x2005F0]` supplies local `SP+0xC` at `0x5200..0x5220`:

```text
row(P) = floor(19 × P / 100)    if 0 ≤ P ≤ 100
       = 19                     if P ≥ 101
```

The multiply is performed only for P at most 100, so it cannot overflow.
Both local values are narrowed to bytes at `0x52AE` and `0x52B0`, then
`PUSH {R0,R1,R2}` at `0x52B8` passes them as the fifth and sixth arguments.
After `0x4B38` saves R4–R7/LR, its `SP+0x18` is the row and `SP+0x1C` is the
column. The instructions at `0x4CDC..0x4CEC` form:

```text
0x200294 + 20 × row(P) + column(W)
```

Since each axis is 0..19, the offset is 0..399. The final byte is at
`0x200423`, immediately before the state structure starting at `0x200424`.
The [audit script](../audit/tools/audit_capture_table_bounds.py) pins the
branch/stack instruction skeleton and literal values, checks the finite
middle intervals exhaustively, and records boundary/high-word probes. This is
an instruction-supported bound for this direct call, not a measured sensor
range.

## Initialized table source

Startup copies 2,208 image bytes from `0x96E8` to SRAM `0x200000`. The
400-byte source slice `0x997C..0x9B0C` lands at `0x200294..0x200424` and is
now classified separately in the [image ledger](../audit/data/image_coverage_ledger.json).
It is a 20×20 byte table. The source slice SHA-256 is
`267d0c881003f8fc49f2e0d5071cac6a684df46f69edc0b74c3904b4927597e5`;
all 400 initial values are 0..100. No byte has its high bit set, so the
`LDRSB` yields nonnegative values immediately after initialization.

This closes the out-of-table concern **for the reviewed direct caller with
intact stack and the established code path**. The table resides in writable
RAM. A complete writer audit, indirect or alternate entry analysis, and fault
or stack-corruption behavior remain open. Those limits prevent claiming the
table can never change, or that every possible execution is bounded.

Reproduce with a matching independently obtained image:

```sh
python audit/tools/audit_capture_table_bounds.py firmware_v2.8.4HF.bin --output audit/data/capture_table_bounds.json
python audit/tools/build_image_ledger.py firmware_v2.8.4HF.bin
```

No connected hardware or settings were used.
