# Configured ratio scorer at `0x46D0`

This bounded review uses only the 32,000-byte V2.8.4HF image with SHA-256
`1ae519ba6194e8f7bdaaa94333a83a9e6fda3b0563f87f7d48383b37288c1780`.
The [bounded Thumb decode](../audit/data/drivetrain_score_binaryninja.json)
covers `0x46D0` through its return at `0x478E`; literal words begin at `0x4790`.
The [original-byte execution artifact](../audit/data/drivetrain_score_emulation.json)
records the table values, initialization bytes, inputs, every candidate's full
converted integer, the stored byte, selected code and returned score. No
controller, peripheral, live input range or engine effect was measured.

## Data and call path

`0x50F0` calls the routine at `0x55AC` with R0 loaded from word `0x2005EC`
and R1 retaining byte `0x2005D7`. The caller stores its R0 return byte at
`0x200BCE`. The routine also writes its chosen code to `0x200BD0`; R4–R7 and
SP are restored. If the R1 byte is zero, it writes `0xF2` to `0x200BD0` and
returns 100 without visiting a candidate.

The firmware table at `0x9F88` has three 28-byte rows. Their candidate counts
are 4, 5 and 6, followed by binary32 ratios:

| Selector `0x2006E6` | Candidate ratios (approximate decimal display) |
|---:|---|
| 0 | 2.45, 1.45, 1.00, 0.69 |
| 1 | 5.61, 3.04, 1.67, 1.00, 0.75 |
| 2 | 5.63, 3.38, 2.04, 1.39, 1.00, 0.73 |

Five more binary32 coefficients at `0x9FDC`, selected by byte `0x2006E7`,
are approximately 3.73, 4.10, 1.00, 3.54 and 3.55. The exact bit patterns
are in the artifact. Startup's initialized-RAM template sets the two selector
bytes to 0 and 4, followed by binary32 `95.6` at `0x2006E8`. The AID 226
write case at `0x66AC` accepts a new first selector only below 3, a second
only below 5, and a word-derived binary32 circumference only when its
comparison against 1 passes. This establishes bounds on that write path;
other possible RAM writers are not excluded.
The [profile reference](AID_REFERENCE.md) lists 95.7–120.9 inches for AID
226, whereas the image's initialized value is 95.6. The inspected firmware
case checks the derived value against 1 and shows no corresponding 120.9
upper bound. This is a profile/firmware discrepancy, not a device measurement.

The executed instruction sequence multiplies a row ratio, selected coefficient,
R1's low byte and binary32 `1056.0`. It divides the product of R0 and the
word at `0x2006E8` by that value, subtracts 1.0, multiplies by 100.0, clears
the sign bit, and converts binary64 to signed 32-bit integer. In compact form,
ignoring intermediate binary32 rounding:

```text
candidate = int(abs(100 * ((R0 * circumference)
              / (R1_low_byte * row_ratio * selected_coefficient * 1056) - 1)))
```

The coefficients resemble transmission and axle ratios, while 1056 is the
inches-per-minute conversion for one mile per hour. That suggests a gear ratio
fit calculation, but the present evidence does **not** establish the physical
unit or source of `0x2005D7`. Earlier repository notes call it a TPS input.
Tracing its upstream producer is required before calling this a vehicle-speed
or throttle-dependent output. The case label “Drive Train Info” for AID 226
also does not itself establish the byte semantics.

## Confirmed byte truncation in the offline path

At `0x476C`, each converted signed score is stored to an 8-bit stack cell.
At `0x4770`–`0x4776`, that **byte** is compared with R7, initially 100, and
the minimum byte becomes the return score. The selection code is candidate
index plus one for indexes 0–3 and plus two for indexes 4–5.

With startup selectors (0, 4), binary32 circumference 95.6, R0=1200 and
R1=5, the original-byte emulator records full candidate integers
149, 322, **512**, and 787. Their stored bytes are 149, 66, **0**, and 19.
The routine therefore returns **0** and selects code 3, even though none of
the full scores is zero. A second sample, R0=500 and R1=1, records full
scores 420, 779, 1175 and 1747; the 779 score becomes byte 11 and wins.
These demonstrate an actual truncation in the callable firmware routine.
Whether these inputs arise on a vehicle, or whether the returned score affects
an output, remains unverified.

The arithmetic inherits the [software floating point review's](SOFT_FLOAT_REVIEW.md)
exceptional-value limitations. This review probes a small set of finite inputs
and does not prove all possible selectors, RAM mutation paths or caller states.

## Reproduction

```text
PYTHONPATH=<Binary Ninja Python path> python audit/tools/decode_image_ranges.py firmware_v2.8.4HF.bin --ranges 0x46d0:0x4790:thumb2 --output audit/data/drivetrain_score_binaryninja.json
uv run --with unicorn==2.1.4 python audit/tools/audit_drivetrain_score.py firmware_v2.8.4HF.bin --output audit/data/drivetrain_score_emulation.json
python -m unittest discover -s tests -t .
```

The script rejects a different image hash and maps no peripherals. Binary
Ninja's selected Thumb decoder accepts a superset of ARMv4T; the decoded
instruction mode and bounds are explicit hypotheses corroborated on these
visited paths by original-byte execution.
