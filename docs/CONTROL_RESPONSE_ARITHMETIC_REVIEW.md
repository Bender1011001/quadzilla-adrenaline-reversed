# Control response arithmetic, filters and retained-state ordering

This review covers the response-building slice `0x53A2..0x55A6` of `0x50F0`
in the exact V2.8.4HF image, SHA-256
`1ae519ba6194e8f7bdaaa94333a83a9e6fda3b0563f87f7d48383b37288c1780`.
Range ends are exclusive. A literal island separates its instruction spans;
the reviewed slice has **196 instruction starts**. The
[execution artifact](../audit/data/control_response_emulation.json) records
**1,072 original-byte slice executions**, visiting every start with zero
differences against the [arithmetic model](../tools/model_control_responses.py).
It also records two consecutive complete original control calls that check
the retained response dependencies described below.

The slice starts with synthetic caller registers/frame: R4 points to
`0x200424`, R6 is the previously computed applied-stretch value, and local
stack bytes 2/3 hold clamp/write flags. It stops before the separately
reviewed [ratio scorer](DRIVETRAIN_SCORE_REVIEW.md) and
[threshold helper](CONTROL_HELPER_REVIEW.md). Helpers reached within the
slice execute original bytes. The test does not replace floating conversions
or moving averages with stubs.

## Source selection and integer derived state

If byte `0x2005D4` is zero, select raw word `0x200600` and scalar word
`0x200604`; otherwise select raw word `0x2005E4` and scalar word `0x2005E8`.
Any nonzero selector takes the second path. Define:

```text
pct = floor(100*min_unsigned(raw,4095)/4095)
a   = floor(((word[0x200AC8]*pct) mod 2^32)/100)
b   = floor(((word[0x200ACC]*R6) mod 2^32)/2200)
T   = ((a+b)*word[0x2005EC]*3) mod 2^32
```

The routine stores T at `0x200474` before converting it as an unsigned
integer to floating point. Products wrap before each subsequent division;
neither a wide host-integer formula nor a physical-unit interpretation can
be substituted. The selected raw word is stored as low 16 bits, whereas
`pct` uses the separately reviewed saturated normalization helper.

## First floating calculation and 32-sample filter

Let `f32` and `f64` denote rounding to those binary formats after the stated
operation. Constants are source-bound bit patterns, not inferred units:
`0x414CE16100000000` is binary64 3,785,410; `0x404E000000000000` is
binary64 60; `0x42C7FAE1` is a binary32 value near 99.99.

```text
d = f32(f64(unsigned(T))/3785410.0)
n = f32(f64(previous_byte[0x200BC3])/60.0)
r = f32(n/d)                   when d != 0
  = bits32(0x42C7FAE1)          when d == 0
q = min_unsigned(u32_saturating(f32(100.0*r)),9999)
```

The numerator operations execute only when d is nonzero. The source includes
a binary32-to-binary64-to-binary32 round trip of r; it preserves these
tested non-NaN values. The model retains the earlier rounding points rather
than collapsing the expression into one rational or host double operation.
`q` is appended to the 32-word buffer at `0x200480`: drop its oldest word,
shift the retained 31 words, append q, sum modulo 2^32, and logically shift
right by five. The response at `0x200BD2` receives only the average's low
16 bits. Arbitrary old buffer words can wrap the sum; the new-sample cap
alone does not bound all historical contents.

## Second floating ratio and byte-filter branch

Words `0x200748` and `0x20074C` are interpreted as binary32 bits. With
denominator nonzero, divide in binary32; with denominator positive or
negative zero, use zero. Convert the result with the reviewed signed
32-bit saturating helper, then store **only its low 24 bits** at
`0x200BD6..0x200BD9`. For example, synthetic numerator -6 and denominator 2
convert to -3 and store `FD FF FF`. Arithmetic overflow to infinity is
included in the suite; NaN source words are outside this reference's domain.

Byte `0x2005D8` is averaged through the other 32-word buffer at `0x200500`
only when byte `0x200AFE` equals **exactly 1**. That path uses the same
wrapped-sum/right-shift filter; the response stores the average's low byte.
Every other enable value directly copies the source byte to `0x200BC1`
and leaves this filter buffer unchanged.

## Response stores

Multi-byte rows store consecutive little-endian bytes. Truncation is distinct
from saturation; no unproven field names or physical units are assigned.

| Destination | Implemented value |
|---|---|
| `0x200789`, `0x200788` | Local stack clamp/write flag bytes. |
| `0x200BB8` (2 bytes) | Selected raw word, low 16 bits. |
| `0x200BC2` | Normalized pct from the selected raw word. |
| `0x200BB6` (2 bytes) | Low 16 bits of `((100*selected_scalar) mod 2^32) >> 7`. |
| `0x200BC6` (2 bytes) | Word `0x2008A8`, low 16 bits. |
| `0x200BBB` | Word `0x20044C`, low byte. |
| `0x200BD2` (2 bytes) | First filter average, low 16 bits. |
| `0x200BD6` (3 bytes) | Second floating ratio's converted integer, low 24 bits. |
| `0x200BD4` (2 bytes) | Word `0x200738`, low 16 bits. |
| `0x200BBA` | Word `0x2008B0`, low byte. |
| `0x200BC8` (2 bytes) | Word `0x2008AC`, low 16 bits. |
| `0x200BBC` (2 bytes) | Wrapped `word[0x2005F4]+40`, low 16 bits. |
| `0x200BCB` (2 bytes) | Word `0x2005EC`, low 16 bits. |
| `0x200BCA` | Unsigned `min(word[0x2005F8],255)`. |
| `0x200BC1` | Optional byte-source filter result described above. |
| `0x200BBE` | Add 40 to word `0x2005FC` with 32-bit wrap; if the result's N bit is set, store zero, otherwise its low byte. There is no upper saturation. |
| `0x200BC3` | Current byte `0x2005D7`. |
| `0x200BC0` | Word `0x2005F0`, low byte. |
| `0x200BBF` | Byte `0x2005D9`. |

For the `0x200BBE` path, source 216 yields wrapped sum 256 and stored zero;
source `0xFFFFFFFF` yields sum 39 and stored 39. This is different from the
unsigned cap at `0x200BCA`. Floating runtime status byte `0x200AF8` can also
change through numeric helpers; this response model does not compare its
exception/status effects. Filter buffers and derived word T are compared in
addition to every response byte in the table.

## Retained response dependencies across control calls

The scalar call at `0x525E` reads `0x200BC2` before this slice replaces it at
`0x5428`. The floating numerator reads `0x200BC3` at `0x549C`, before the
current source byte is copied there at `0x5594`. These are retained-state
dependencies, rather than both calculations automatically receiving the
newly reported inputs from the same call.

Two complete control calls preserve SRAM between invocations. The first
starts with `BC2/BC3=7/3`, raw capture 4095 and current source byte 80. It
consumes 7/3 and finishes with `BC2/BC3=100/80`; the second consumes 100/80.
Only the synthetic external return link is restored before the second call.
No other helper result or SRAM state is reset. This demonstrates the ordering
under those stable inputs; alternate writers or interrupt interleavings can
change which retained values a later call observes.

## Validation and remaining scope

The cases include both source paths, enable values 0/1/2, byte coefficient
boundaries, zero-denominator fallback, an explicit upper-cap case, wrapped
filter history, negative offset results, signed ratio conversion, floating
overflow and 1,024 deterministic mixed cases. All 196 starts are visited,
without claiming exhaustive arithmetic combinations or normal-state
reachability. The source float words are finite in this suite. The internal
entry/frame, R6 value and old filter contents are controlled inputs; the
earlier complete-control review supplies wider caller context.

Global writer bounds, NaN source paths, floating status-byte effects, all
parameter-to-field mappings, physical units and asynchronous behavior remain
separate work. No instruction-byte or entry count changes follow from this
semantic pass. The full offline analysis remains incomplete.

```sh
python audit/tools/emulate_control_responses.py firmware_v2.8.4HF.bin --output audit/data/control_response_emulation.json
python -m unittest discover -s tests -t .
```

No hardware, device traffic, flashing or settings change was used.
