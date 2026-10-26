# Scalar helper at `0x4D38`: working knots and telemetry caller

This account is for the exact 32,000-byte V2.8.4HF image, SHA-256
`1ae519ba6194e8f7bdaaa94333a83a9e6fda3b0563f87f7d48383b37288c1780`.
The [bounded Binary Ninja decode](../audit/data/scalar_telemetry_binaryninja.json),
[byte-verified IDA export](../audit/data/ida_image_items.json), and
[reproducible structure audit](../audit/data/scalar_telemetry_structure.json)
support the code and literal boundaries below. The subsequent
[original-byte execution artifact](../audit/data/scalar_telemetry_emulation.json)
checks 10,312 helper calls and the original post-call cap/floor/store slice
against the [32-bit arithmetic model](../tools/model_scalar_telemetry.py).
There are zero mismatches in return values, final cap/flag/knot state and
stored telemetry. All 349 helper instruction starts are visited; this is
instruction coverage, not exhaustive path or live-state validation.

| Image range | Supported classification |
|---|---|
| `0x4D38..0x5016` | 734 Thumb instruction bytes, ending in `BX R1` return |
| `0x5016..0x5018` | `C0 46` Thumb NOP alignment |
| `0x5018..0x506C` | 21 literal words, all 21 targeted by PC-relative loads |

The explicit decode has 350 instruction starts including the NOP. Thirty
PC-relative loads use the 21 literal words. All 51 non-call direct branches
target decoded starts within the body. Eighteen direct calls target only the
unsigned division entry `0x8574` and signed division entry `0x8584`. Those
helpers return the remainder in R0 and quotient in R1, as established in the
[integer-runtime review](INTEGER_ARITHMETIC_REVIEW.md). Ten second halfwords of
constant-building pairs are folded into four-byte IDA items; the structure
artifact lists their addresses.

## Input and caller boundary

The only decoded direct caller is `0x525E` in the main control loop. It passes
low-byte values in R0, R1 and R3, the word read from `0x2005E4` in R2,
and one low byte on the stack. **The incoming R0 and R2 are overwritten before
being read by this helper**: `0x4D3C` replaces R0 with R3, and `0x4D3E` replaces
R2 with the stack-argument address. They are not scalar inputs here. The
execution suite varies those ignored values as a check. R1 is the selector,
R3 the column, and the low stack byte the row for the table path. The origin
and live range of those passed bytes still require upstream tracing. The helper reads words
`0x2005E8` and `0x2005EC`, bytes in the `0x200424` state structure, AID-related
response bytes, a signed cell in the initialized-RAM table at `0x200000`, and
the five working knots `0x200458..0x200468`. The knot words are written from
AIDs 137–141 and have reviewed initializer defaults; the separate working
word `0x20046C` is written from AID 61. See the
[handler review](REMAINING_AID_UPDATE_REVIEW.md) and
[initializer review](CONTROL_HELPER_REVIEW.md).

The caller at `0x5262..0x5278` caps the return value with word `0x200450`
using an **unsigned** comparison, then compares that result to 1,024 using
**signed** `CMP/BGE` at `0x5270/0x5272`. It stores the result at telemetry word
`0x200604`. Precisely, let `z=min_unsigned(return,cap)`; store 1,024 when
`signed32(z)<1024`, otherwise store `z`. Thus both a cap below 1,024 and a
retained value with bit 31 set cause the floor store. Each helper case is
followed by execution of this original slice with a synthetic caller frame.
For example, a controlled zero-mode case with all knots `0xFFFFFFFF` and
`X=3500` returns `0xFFFFFF7F` under the suite's other default inputs. The cap
is `0xFFFFFFFF`; the original caller slice stores 1,024 because its second
comparison is signed. This is a synthetic arithmetic demonstration, not a
claim that those knot values are admitted by the normal parameter writers.
This supports the telemetry relationship; it does not
identify the result as a direct pump command or establish physical units.

## Branch and state map

At entry, the helper checks byte `0x200426`. If set, it tests four response
bytes at `0x200BED`, `0x200BF1`, `0x200BF3`, and `0x200BF4`. When all are zero,
it sets byte `0x200425` to 1; otherwise it clears that byte. Either way it
clears `0x200426`. The update is skipped when the flag is already zero.

The next gate compares the sum of bytes `0x200433` and `0x200434` against the
caller-supplied R1 byte and tests byte `0x200432`. The bypass path zeros local
terms and writes `0xF00` to word `0x200450`. It still continues through the
common arithmetic and return. The active path reads capture-derived word
`0x2005EC` and uses one of two scalar paths selected by byte `0x200425`:

| Path | Established instruction behavior |
|---|---|
| `0x200425` nonzero, `0x4D9C..0x4E78` | Sets `0x200450` to `0xF00`, caps each of five knot words in place against increasing constants, then selects a segment by unsigned comparisons with 1,000, 1,500, 2,000, 2,500 and 3,000. A subrange numerator uses `0x2005EC` plus a negative literal, followed by unsigned division by 5; below 1,000 it selects zero terms. |
| `0x200425` zero, `0x4E7A..0x4F94` | Indexes a signed byte at `0x200000 + 20 × stack_byte + R3_byte`, combines it with `0x200BC2` and the AID-61 working word `0x20046C`, checks byte `0x2005D7`, and selects the same capture-word segments. Signed and unsigned division results, integer truncation, and the sign of the table cell matter. |
| `0x4F96..0x5016` | Combines selected terms with capture word `0x2005E8`, applies two percentage terms from the structure at `0x2005B0`, subtracts the smaller derived amount, and returns R0. The divisions and arithmetic are 32-bit instruction operations, not floating-point math. |

The negative literals in the pool are arithmetic offsets, not pointers. The
pool also contains the exact state/table addresses used above. The following
contract adds the arithmetic and mutation account under the current caller's
byte-input domain; reachable state and writer constraints remain separate.

## Arithmetic contract

All intermediate additions, subtractions and products wrap to 32 bits before
the next operation. `S(v,d)` means reinterpret the wrapped numerator as signed
32-bit, divide by positive `d` with truncation toward zero, then retain the
32-bit result. `U(v,d)` divides the wrapped numerator as unsigned. These are
the original division helpers, returning the quotient in R1.

| Symbol | Source |
|---|---|
| `B`, `X` | Words `0x2005E8`, `0x2005EC` |
| `K1..K5` | Words `0x200458..0x200468` |
| `W` | AID-61 working word `0x20046C` |
| `p`, `t` | Bytes `0x200588`, `0x200BC2` |
| `u`, `v`, `h` | Bytes `0x2005B0`, `0x2005B1`, `0x2005B3` |
| `s` | Status byte `0x2005D7` |
| `C` | Sign-extended byte at `0x200000 + 20*row + column` |

The entry's refresh gate updates the mode byte exactly as described above,
then clears the refresh flag. The active arithmetic path requires
`byte[0x200433]+byte[0x200434] < R1` and `byte[0x200432] != 0`. The sum
comparison is signed, but both the sum 0..510 and this caller's selector
0..255 are nonnegative. This contract does not extend that simplification to
arbitrary direct-call R1 values.

On bypass, set cap `0x200450=3840`, leave knots unchanged, and return `B`.
In active nonzero mode, set that same cap and replace each knot in place with
`min_unsigned(Ki, ceiling_i)`, where the ceilings are
`384,512,640,768,896`. There is no lower or monotonicity check in this entry.
In active zero mode, leave the knots unchanged and set the cap to `K5`.

For `1000<=X<3500`, let `j=floor((X-1000)/500)` in 0..4 and
`f=floor((X-(999+500*j))/5)`. This is deliberately the source's offset of
**999**, not 1000. The first four positions in each interval give `f=0`;
the last position gives `f=100`. The common interpolation term is
`I=S(slope*f,100)`:

| Mode and interval | Base used below | Slope |
|---|---|---|
| Nonzero mode, `j=0` | `B` | `K1` |
| Nonzero mode, `j=1..4` | `B+Kj` | `K(j+1)-Kj` |
| Zero mode, `j=0` | `B` | `K1-B` |
| Zero mode, `j=1..4` | `Kj` | `K(j+1)-Kj` |

Below 1000, use base `B`, `I=0`, and no coefficient or special adjustment.
At or above 3500, nonzero mode uses `B+K5`; zero mode uses `K5`, with
coefficient terms cancelling and no interpolation. `X` segment comparisons
are unsigned. Decreasing knots therefore produce wrapped differences that
are interpreted as signed only at the subsequent signed division.

Zero mode normally computes `a=S(p*t*128,1000)` and `b=S(p*128,10)`.
Both are zeroed below 1500; at or above 3500 it makes `a=b`. Define a special
adjustment when `t<h` and `W!=0`, except it is disabled below 1200. When
enabled, the pre-subtraction scalar is
`base+I+W+(128 if s>=51 else 0)-U(W*t,100)` and the table term is disabled
by setting `C=0`. Otherwise it is `base+I-b+a`. Nonzero mode uses `a=b=C=0`
and has no special adjustment. The `W*t` product can wrap before unsigned
division; the entry does not enforce a bound on `W`.

Finally compute:

```text
table_term   = S(S(C*1280,100)*u,100)
ceiling_term = U(S(v*u,100)*1280,100)
return       = pre_subtraction - min_unsigned(table_term,ceiling_term)
```

The unsigned minimum at `0x5006` matters for negative signed table cells.
A negative `table_term`, represented with bit 31 set, ordinarily selects the
nonnegative ceiling term rather than adding the magnitude of the negative
term. Truncation can also produce zero. No defect classification or intended
signed behavior is inferred without the writer/consumer requirements.

The visible helper writes are the refresh/mode bytes, cap word, conditional
knot clamps, and its own stack frame. It preserves SP and R4–R11 in the
execution suite. Its scalar return is R0; R1 is also used by the epilogue to
hold the return address and is not an independent numeric result.

## Execution scope and remaining work

The suite sweeps every integer `X=0..4000` in both modes, all 256 table-cell
byte values, every refresh-response early-exit position, special adjustment
boundaries at 1200 and status 50/51, bypass gates, oversized and decreasing
knots, ignored argument changes, and 2,000 deterministic mixed cases. Mixed
cases include arbitrary 32-bit knot/capture/base/working values and byte
coefficients. It compares final side effects as well as return values.

The controlled row/column domain is 0..19. The later
[complete-control integration review](CONTROL_SCALAR_INTEGRATION_REVIEW.md)
traces these axes through the only decoded direct caller and executes 325
complete caller invocations. It establishes the bounds under intact-frame
and stable-input assumptions, retaining the repeated-load concurrency
condition. Neither suite proves all 32-bit combinations, physical units, intended
calibration, runtime mutability, interrupt ordering or live hardware effects.
Those require upstream writer and integration evidence. No new execution
entry or reviewed-byte count is added by this arithmetic pass.

Reproduce the source-bound layout with an independently obtained matching
image and Binary Ninja Python path:

```sh
PYTHONPATH=<Binary Ninja Python path> python audit/tools/decode_image_ranges.py firmware_v2.8.4HF.bin --ranges 0x4d38:0x5018:thumb2 --output audit/data/scalar_telemetry_binaryninja.json
python audit/tools/audit_scalar_telemetry_structure.py firmware_v2.8.4HF.bin --output audit/data/scalar_telemetry_structure.json
python audit/tools/emulate_scalar_telemetry.py firmware_v2.8.4HF.bin --output audit/data/scalar_telemetry_emulation.json
python audit/tools/build_image_ledger.py firmware_v2.8.4HF.bin
```

No connected hardware, device traffic, flashing or setting changes were used.
