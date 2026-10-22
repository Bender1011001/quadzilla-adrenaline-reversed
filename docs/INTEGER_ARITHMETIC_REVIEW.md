# Integer runtime and stretch arithmetic execution review

This pass executes the exact, source-hashed firmware bytes in an offline emulator.
It establishes six runtime roles, raising baseline coverage to **42 of 145 entries**
and reducing the baseline review queue to **103**. The six separately adjudicated
extra source starts remain supported: the known minimum is 151, not an exhaustive
count. The full firmware-analysis goal remains active.

## Emulator scope

Unicorn 2.1.4 runs an ARM926 functional surrogate. That CPU supports a superset of
ARM7TDMI's instructions; this is not exact-core, electrical, timing or exception
validation. Only read/execute image memory and read/write SRAM are mapped. The
instruction hook rejects execution outside the selected arithmetic regions;
unmapped accesses fault. No peripheral addresses, serial devices or host device
APIs are mapped or opened.

The runner checks source SHA-256 before executing, a finite instruction budget,
return to a sentinel PC and stack balance. Division runs check preservation of
R2–R11; stretch runs check R4–R11. Results are recorded in
[division evidence](../audit/data/integer_runtime_emulation.json) and
[stretch evidence](../audit/data/stretch_arithmetic_emulation.json). Independent
[explicit-mode decoding](../audit/data/integer_runtime_binaryninja.json) supplies
the instruction-level interpretation.

## Division ABI and entry roles

| Thumb entry | ARM body | Operation |
|---|---|---|
| `0x8564` | `0x8568` | Masks both inputs to 8 bits, then unsigned division |
| `0x8574` | `0x8578` | Unsigned 32-bit division |
| `0x8584` | `0x8588` | Signed 32-bit division |

Inputs are R0 numerator and R1 denominator. **Outputs are R0 remainder and R1
quotient.** For example, inputs 100 and 3 yield R0=1 and R1=33. Treating an
ordinary scalar C return as the quotient would misread these helpers. The ARM
bodies share a core loop; the separate catalog starts are entries, not six
independent algorithms. R12 and condition flags may change.

For nonzero signed divisors the tested behavior truncates the quotient toward
zero, with remainder sign following the numerator. The `INT_MIN / -1` case returns
quotient register bits `0x80000000`, remainder zero. This is an observed helper
behavior, not a claim about the defined behavior of a corresponding C expression.

Zero divisors do not trap on the checked paths. Quotient is zero. Unsigned
helpers retain the numerator as remainder; the signed helper returns its
absolute-value preprocessing result, e.g. inputs -7 and 0 yield R0=7, R1=0.
The zero-divisor branch reaches the epilogue before sign restoration. No claim
is made that any production caller can supply a zero divisor.

## Executed coverage

| Entry | Cases | Coverage |
|---|---:|---|
| `0x8564` | 65,536 | Every pair of 8-bit input values, including zero divisors |
| Five other entries | 4,321 each | Fixed boundary cross-product plus 4,096 deterministic 32-bit samples |
| **Total division calls** | **87,141** | Zero mismatches against integer arithmetic and the instruction-supported exceptional policies |
| `0x4A94` | **2,092** | Controlled SRAM cases, including signed-cell, gate, ramp and rounding boundaries |

The 32-bit domains are sampled. This is not an exhaustive proof of every input,
calling state or instruction path. Emulation reports are executed evidence; the
ordinary standard-library CI tests check their integrity/invariants and selected
examples, without requiring or redistributing the vendor image.

## Control callers use both results

[The caller inventory](../audit/data/integer_division_callers.json) contains 68
decoded direct-call contexts. It does not include every indirect call or provide
a complete dataflow proof by itself. Consequential examples checked against the
instruction export:

- `0x4AC8` and `0x4AD8` call unsigned division and move R1 into R7.
- `0x4B0E` and `0x4B18` implement successive percentage divisions; the final
  `MOV R0,R1` returns the quotient from the stretch-arithmetic function.
- `0x5226` calls signed division with divisor 250, then compares **R0** with zero
  at `0x522A`. That is a remainder test for the periodic backdown-update gate,
  not a quotient test or a measured wall-clock interval.
- `0x64A2`/`0x64B0` compute 100 divided by a power-level-related value; one path
  stores R1, another stores R0. Both quotient and remainder are used.

## Executing the stretch-arithmetic routine

The second runner executes `0x4A94` and the real division helpers. Row and column
inputs are fixed at zero to isolate arithmetic. Controlled memory fields include
the table byte at `0x200190`, word at `0x2005F0`, requested value at `0x200590`, and
the gate/ramp/minimum fields read by this routine. Their numerical roles are
modeled without assigning unproven sensor units or claiming valid vehicle states.

Two important results agree between the instruction model and actual emulated
execution:

1. **Integer divisions round at each stage.** With the recorded directed case
   using table byte 1, requested value 1019 and a 99-percent final ramp, the
   successive divisions return 9. Collapsing the arithmetic into one division
   would return 10 and would not reproduce the firmware.
2. **High-bit table bytes require a caller/writer invariant.** `0x4ABC` uses
   `LDRSB`, then an unsigned comparison is used at `0x4AC0/2`. Controlled table
   byte 140, requested value 1700 and the recorded full-gate/ramp scenario produce
   R0=42,947,700 after sign extension, wrapped multiplication and unsigned
   divisions. The analogous table byte 100 returns 1700.

The second result is **not a demonstrated vehicle vulnerability**. The writers
and reachable range of this internal table are not yet reconstructed. It must
not be equated with the profile's separately mapped 50–150 fueling-curve AIDs.
Later control gates and timer encoding also remain outside this isolated run.
The result identifies a concrete range invariant to prove during the remaining
table-writer and output-path analysis.

For this routine's reviewed unsigned branches, zero denominators are guarded:
the gate-scaling call is reached only when `gate < percent < 100`, so
`100-gate` is positive. The ramp call is reached only when the two byte thresholds
are strictly ordered, so their difference is positive. The remaining divisors
are constant 100. This local guard reasoning does not establish nonzero divisors
for all 68 other call contexts.

## Reproduce

With an independently obtained matching image and optional Unicorn dependency:

```bash
uv run --with unicorn==2.1.4 python audit/tools/emulate_integer_runtime.py fw.bin --output integer_results.json
uv run --with unicorn==2.1.4 python audit/tools/emulate_stretch_arithmetic.py fw.bin --output stretch_results.json
python audit/tools/build_integer_callers.py
python -m unittest tests.test_integer_runtime -v
```

`tools/model_stretch_arithmetic.py` is a bounded register-level model, not new
tuner firmware. No output timing or physical pulse was measured. Next work is
the internal table's writers/ranges, remaining runtime arithmetic and conversion
entries, caller preconditions, and full path constraints through timer output.
