# Response models checked inside complete original control calls

This pass extends the local [response arithmetic review](CONTROL_RESPONSE_ARITHMETIC_REVIEW.md)
to **288 complete original `0x50F0` calls**. The source is the exact 32,000-byte
V2.8.4HF image, SHA-256
`1ae519ba6194e8f7bdaaa94333a83a9e6fda3b0563f87f7d48383b37288c1780`.
The [artifact](../audit/data/full_control_responses.json) retains each entry
variation, actual response-boundary inputs, expected and actual bytes, derived
word and both filter buffers. No function result is stubbed.

## Complete caller connection

Each case starts with initialized SRAM and explicit entry overrides, then runs
the actual prologue, selector/gate/scalar/capture/timer paths, response-building
code, later scorer and epilogue. At `0x53A2`, the independent response model
receives the **actual** upstream state, R6 stretch and local clamp/write flags.
At `0x55A6`, every modeled byte store, derived word and both complete filter
buffers must agree. Earlier scalar-model, table-extent, timer, stack and
callee-saved-register checks remain active. The later scorer executes without
a new independent comparison from this suite.

The matrix varies source selector 0/1/2, filter enable 0/1/2, multiplier pairs
`(0,0)`, `(1,0)`, `(1000,0)` and `(0xFFFFFFFF,0xFFFFFFFF)`, retained response
0/255 and four finite float-source pairs. The latter are 6/2, -6/2,
maximum positive binary32/minimum positive subnormal, and 1/negative zero.
Other source/ADC words, offsets, new response 80 and filter histories are
explicitly fixed in the reproducer. These are controlled entry values, not
claimed parameter-admitted ranges or reconstructed live histories.

## Established results

- Source selector zero takes the computed analog pair; both nonzero values
  take the capture pair. Actual boundary analog raw/scalar are 4095/1024,
  while the supplied capture pair is 4095/1000, so scalar packing distinguishes
  the paths even though raw values coincide.
- The retained 0/255 response coefficient is consumed before the original
  automatic producer stores 80 later in the same call. The existing model
  reproduces new first-filter samples 0, 268 and 9999, including the ceiling.
- Ratio conversion results are 3, wrapped -3 (`0xFFFFFFFD`), signed maximum
  `0x7FFFFFFF` after positive intermediate overflow, and zero for the guarded
  negative-zero denominator. Byte packing agrees in all cases.
- Filter enable must equal one. With the supplied all-ones history and byte
  source 160, wrapped sum/shift produces response byte 4. Enable 0 or 2 returns
  direct byte 160 and retains that filter's zero history. Both full buffers
  are checked, rather than inferring filter state from a single output byte.

The ratio source words are finite, but intermediate overflow is included.
NaN/infinite source admission and numeric exception/status-byte effects remain
outside the response reference. No physical units or live impact are assigned.

## Coverage and remaining scope

The subsequent [axis/clamp review](CONTROL_AXIS_CLAMP_REVIEW.md) exercises the
19 starts listed by this suite. The six-suite union is 574/574; this suite's
own model and execution scope remain unchanged.

Twenty-nine additional main starts execute. Union with the initial scalar,
retention, idle and reinitialization suites reaches **555/574**; the 19 listed
remaining starts belong to the alternate axis calculation and optional timer
upper-clamp path. This is an instruction union over five suites, not exhaustive
branch, path, writer or firmware coverage. Previously exercised starts can
still have untested state combinations and error behavior.

Global writer constraints, asynchronous input stability, complete parameter
admission, physical timing and peripheral effects remain open. The full firmware
goal remains active.

```sh
python audit/tools/emulate_full_control_responses.py firmware_v2.8.4HF.bin --output audit/data/full_control_responses.json
python -m unittest discover -s tests -t .
```

No device traffic, flashing or engine-setting change was performed.
