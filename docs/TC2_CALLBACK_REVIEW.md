# TC2 callback: counter, flag and numeric state review

This review is bound to the exact 32,000-byte V2.8.4HF application image,
SHA-256 `1ae519ba6194e8f7bdaaa94333a83a9e6fda3b0563f87f7d48383b37288c1780`.
The [Binary Ninja decode](../audit/data/tc2_callback_binaryninja.json) covers
`0x6C94..0x6F55`, 706 Thumb instruction bytes and 333 instruction starts.
The [original-byte execution artifact](../audit/data/tc2_callback_emulation.json)
uses 50 controlled SRAM/MMIO cases plus 24 numeric reference cases. The
50 control cases' union visits all 333 decoded starts.
These are instruction paths, not real-time measurements. Binary Ninja's
Thumb decoder supports a superset of ARMv4T; explicit bounds and original-byte
execution provide additional evidence for this selected instruction stream.

## Entry contract and provenance

The [timer setup](TIMER_SETUP_REVIEW.md) installs odd Thumb pointer `0x6C95`
in AIC_SVR14. The baseline call graph has no ordinary `BL` incoming edge to
`0x6C94`; the vector write is its supported entry evidence. The callback
preserves R4–R7 and the stack in all controlled executions, returns through
its saved link address, and makes no direct timer-counter writes. It first
reads TC2_SR at `0xFFFA00A0` through initialized pointer `0x200728`.
The [SAM7S datasheet](https://ww1.microchip.com/downloads/en/DeviceDoc/doc6175.pdf)
identifies the TC and AIC registers; no peripheral side effects are modeled.

The callback uses SRAM base `A=0x200708` from image literal `0x6F58` and
`B=0x200AD0` from `0x6F60`. It reads/writes byte flags and 32-bit counters in
those structures, may write `4` to AIC_IECR at `0xFFFFF120`, and conditionally
updates six numeric state words. It calls [two reviewed flag helpers](TC2_FLAG_HELPER_REVIEW.md)
(`0x7F28`, `0x7F40`) and the already reviewed software numeric wrappers
`0x7120`, `0x7128`, `0x7138`, `0x7140`, `0x7148`, `0x7150`, `0x7158`,
`0x7160`, `0x7168`. Numeric callees can also update status byte `0x200AF8`;
the harness records it. Their exceptional-value limits remain those in the
[soft-float review](SOFT_FLOAT_REVIEW.md).

## Counter and flag transitions

In this table a nonzero **reset flag** first zeros the counter and clears
itself. A nonzero **active flag** increments the counter modulo `2^32`.
Thresholds compare the counter's value **before** that increment using
unsigned branches. Each row was exercised with an active flag and a counter
just below or at its threshold, in addition to an all-zero baseline. On
threshold, the active flag is cleared unless the row says otherwise.

| Reset flag | Active flag | Counter | Threshold on prior count | Threshold action |
|---|---|---|---:|---|
| `0x20070A` | `0x200709` | `0x200750` | 101 | Set `0x20070B=1`. |
| `0x20070D` | `0x20070C` | `0x200754` | 1001 | Call `0x7F40`. |
| `0x20070F` | `0x20070E` | `0x200758` | 1001 | Call `0x7F28`. |
| `0x200711` | `0x200710` | `0x20075C` | 1001 | Set `0x200712=1`. |
| `0x200717` | `0x200716` | `0x200760` | 501 | Set `0x200718=1`. |
| `0x20071D` | `0x20071C` | `0x200764` | 151 | Set `0x20071E=1`. |
| `0x200720` | `0x20071F` | `0x200768` | 32 | Set bytes `0x200721..0x200724` to 1. **Active flag is not cleared here.** |
| `0x200AD1` | `0x200AD0` | `0x20076C` | 401 | Set `0x200AD2=1`. |
| `0x200726` | `0x200725` | `0x200770` | 6 | Wait for AIC_IMR bit 2, then set `0x200727=1`, clear active flag, set `0x200ADC=1`, clear `0x200ADD`. |
| `0x200AD4` | `0x200AD3` | `0x200774` | 3001 | Set `0x200AD5=1`. |
| `0x200AD7` | `0x200AD6` | `0x200778` | 20001 | Set `0x200AD8=1`. |
| `0x200ADA` | `0x200AD9` | `0x20077C` | 4001 | Set `0x200ADB=1`. |
| `0x200ADF` | `0x200ADE` | `0x200AE4` | 50001 | Set `0x200AE0=1`. |

The AIC wait at `0x6DC8..0x6DCE` reads AIC_IMR `0xFFFFF110` and tests mask
`4` (source 2). While clear, `0x6DC4..0x6DC6` writes `4` to AIC_IECR and
retries. One case begins with bit 2 set. Another begins clear and explicitly
models an IECR write setting IMR bit 2; it observes one retry. Plain synthetic
memory alone would not implement that command's hardware effect, so these
cases cannot establish physical wait duration or liveness on a controller.

Three further counters have different rules:

| Reset/active condition | Counter | Condition and effect |
|---|---|---|
| `0x200ADC` resets it, then it increments **unconditionally** | `0x200780` | When the prior count is at least 1001, set `0x200ADD=1`; no active flag is required. |
| `0x200714` resets; `0x200713` enables | `0x200734` | After increment, if prior count is **greater than** variable threshold `0x20072C`, set `0x200715=1` and clear active flag. |
| `0x20071A` resets; `0x200719` enables | `0x200784` | After increment, if prior count is **greater than** variable threshold `0x200730`, set `0x20071B=1` and clear active flag. |

These counters and flags are software state. The vector association suggests
a TC2-driven service path, but no timer frequency, scheduling interval, or
physical output timing follows from the static thresholds alone.

## Conditional numeric update

Byte `0x200708` resets word `0x200AE8` when nonzero; the word then increments
unconditionally. The numeric tail runs only if the **prior** count is at least
10001 and byte `0x200792` is nonzero. Its direct source words and wrapper
sequence support this data flow, with each conversion/operation rounded or
saturated by the specific firmware helper rather than ideal real arithmetic:

1. Convert unsigned word `0x200474` to binary64; divide by binary64 `60.0`;
   convert to binary32. Store result `x` at `0x200740`.
2. Convert the old unsigned accumulator `0x20073C` to binary32, add `x`,
   saturating-convert back to unsigned word `0x20073C`.
3. Convert that new unsigned word to binary64, divide by binary64 `37854.1`,
   saturating-convert to unsigned word `0x200738`.
4. Convert `x` to binary64, divide by binary64 `3785410.0`, add the binary64
   conversion of old binary32 word `0x20074C`, convert back to binary32, and
   store at `0x20074C`.
5. Convert byte `0x200BC3` to binary64, divide by binary64 `36.0`, convert
   to binary32, and store `y` at `0x200744`. Add `y` to old binary32 word
   `0x200748` and store there. Set byte `0x200708=1`, causing the next
   invocation to reset `0x200AE8`.

For one finite controlled case (`0x200474=600`, `0x200BC3=72`, prior
`0x20073C=5`, binary32 `0x20074C=1.0`, binary32 `0x200748=0.5`), the
original bytes stored `0x41200000` (10.0) at `0x200740`, `15` at
`0x20073C`, `0` at `0x200738`, `0x3F800016` at `0x20074C`,
`0x40000000` (2.0) at `0x200744`, and `0x40200000` (2.5) at
`0x200748`. The gate-off case with the same count made none of those numeric
writes. A further 24 cases cover unsigned input values from 0 through
`0xFFFFFFFF`, bytes 0/1/255, integer accumulators 0/5/`0xFFFFFFFE`, and
selected positive, negative, zero and subnormal binary32 accumulator states.
All six output words matched an independent exact-rational model of the
stated operation sequence in those cases; all sampled status bytes remained
zero. This finite sample does not assert universally correct floating arithmetic.

## Coverage and limits

The 50 synthetic cases cover all 333 decoded instruction starts, both sides
of each fixed-threshold condition, all reset blocks, a 32-bit counter wrap,
the AIC retry branch, and both numeric gate outcomes. They are not exhaustive
combinations of the SRAM state. The callback's instruction body is accounted
for through its return; the adjacent `0x6F56` NOP and `0x6F58..0x6F9F`
literal words are excluded from reviewed instructions. The literals include
the bases, thresholds, AIC addresses, gate pointers and binary64 constants.

The existing byte-verified [IDA image export](../audit/data/ida_image_items.json)
contains 331 code items over the same 706 bytes. At `0x6D34..0x6D37`, IDA
displays a four-byte `MOVS R0,#0x1F5` item where Binary Ninja and execution
show `MOVS R0,#0xFF` followed by `ADDS R0,#0xF6`. At `0x6D98..0x6D9B`,
IDA similarly folds `MOVS #0xFF` and `ADDS #0x92` into `MOVS #0x191`.
Those display macros explain the two-item count difference; all other item
boundaries match the bounded decoder, and no byte gap occurs. The emulator
visits both second-halfword starts (`0x6D36`, `0x6D9A`).

This analysis establishes inputs, branch conditions, writes and calls for
this entry. It does not establish the names or units of the upstream values
at `0x200474` and `0x200BC3`, the ownership of every flag, live interrupt
cadence, electrical behavior, or exceptional numeric behavior for arbitrary
state. Those questions require upstream writer review and, for timing and
pins, hardware observation. The callback is a counter/flag and numeric
state updater; an earlier first-pass “CAN handler” label is unsupported.

## Reproduction

```text
PYTHONPATH=<Binary Ninja Python path> python audit/tools/decode_image_ranges.py firmware_v2.8.4HF.bin --ranges 0x6c94:0x6f56:thumb2 --output audit/data/tc2_callback_binaryninja.json
uv run --with unicorn==2.1.4 python audit/tools/emulate_tc2_callback.py firmware_v2.8.4HF.bin --output audit/data/tc2_callback_emulation.json
python -m unittest discover -s tests -t .
```

The harness checks the exact image hash and never accesses a device.
