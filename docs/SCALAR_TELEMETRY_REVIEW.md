# Scalar helper at `0x4D38`: working knots and telemetry caller

This account is for the exact 32,000-byte V2.8.4HF image, SHA-256
`1ae519ba6194e8f7bdaaa94333a83a9e6fda3b0563f87f7d48383b37288c1780`.
The [bounded Binary Ninja decode](../audit/data/scalar_telemetry_binaryninja.json),
[byte-verified IDA export](../audit/data/ida_image_items.json), and
[reproducible structure audit](../audit/data/scalar_telemetry_structure.json)
support the code and literal boundaries below. This is a static account of the
original bytes; the helper has not yet been exercised across a modeled set of
caller states.

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
and one low byte on the stack. The origin and live range of the passed bytes
still require upstream tracing. The helper also reads words
`0x2005E8` and `0x2005EC`, bytes in the `0x200424` state structure, AID-related
response bytes, a signed cell in the initialized-RAM table at `0x200000`, and
the five working knots `0x200458..0x200468`. The knot words are written from
AIDs 137–141 and have reviewed initializer defaults; the separate working
word `0x20046C` is written from AID 61. See the
[handler review](REMAINING_AID_UPDATE_REVIEW.md) and
[initializer review](CONTROL_HELPER_REVIEW.md).

The caller at `0x5262..0x5278` caps the return value with word `0x200450`,
then applies a lower floor of 1,024 and stores the result at telemetry word
`0x200604`. The order matters: if the upper cap is below 1,024, the final
stored word is 1,024. This supports the telemetry relationship; it does not
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
pool also contains the exact state/table addresses used above. This phase map
does not establish all cross-path invariants, overflow bounds for every
caller state, or the reachable signed-table cells. Those are the next checks
before assigning a complete mathematical contract or defect classification.

Reproduce the source-bound layout with an independently obtained matching
image and Binary Ninja Python path:

```sh
PYTHONPATH=<Binary Ninja Python path> python audit/tools/decode_image_ranges.py firmware_v2.8.4HF.bin --ranges 0x4d38:0x5018:thumb2 --output audit/data/scalar_telemetry_binaryninja.json
python audit/tools/audit_scalar_telemetry_structure.py firmware_v2.8.4HF.bin --output audit/data/scalar_telemetry_structure.json
python audit/tools/build_image_ledger.py firmware_v2.8.4HF.bin
```

No connected hardware, device traffic, flashing or setting changes were used.
