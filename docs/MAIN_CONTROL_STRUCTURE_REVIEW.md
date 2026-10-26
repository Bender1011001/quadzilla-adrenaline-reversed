# Main control-loop structure and conditional TC0 write

This review uses the exact V2.8.4HF 32,000-byte application image, SHA-256
`1ae519ba6194e8f7bdaaa94333a83a9e6fda3b0563f87f7d48383b37288c1780`.
The [explicit Thumb decode](../audit/data/main_control_binaryninja.json),
[byte-verified IDA items](../audit/data/ida_image_items.json), and
[structure audit](../audit/data/main_control_structure.json) establish the
source layout. The [targeted execution](../audit/data/control_timer_tail_emulation.json)
starts inside the routine at `0x5324` with synthetic registers, stack, SRAM,
and TC0 status. It tests that path and the real `0x4A94`, division, and
`0x6FA0` helper bytes; it does not execute the entire control loop.

The subsequent [complete-control integration review](CONTROL_SCALAR_INTEGRATION_REVIEW.md)
executes 325 original calls from prologue to return, checking scalar/table
provenance, caller stores, periodic dispatch and timer admission. Its 79
unvisited main starts and remaining semantic/concurrency limits are explicit.

## Source layout and direct flow

The catalog entry `0x50F0` is a Thumb routine whose returning body reaches
`0x5612`. It is called from the cycle path at `0x76E0`. Its code is split by
an 80-byte literal pool:

| Image range | Role | Evidence |
|---|---|---|
| `0x50F0..0x53C4` | 724 Thumb instruction bytes | 344 explicit decoded starts |
| `0x53C4..0x5414` | 20 literal words | every word is a PC-relative load target |
| `0x5414..0x5612` | 510 Thumb instruction bytes | 230 explicit decoded starts |
| `0x5612..0x5614` | Thumb NOP alignment | raw `C0 46` |
| `0x5614..0x56FC` | 58 literal words | every word is a PC-relative load target |

There are 94 PC-relative loads into exactly those 78 literal words. All 56
non-call direct branches target decoded starts in the two code spans; 43
direct calls reach 26 distinct targets. `BX R1` at `0x5610` is the function
return. Binary Ninja exposes eight second halfwords of constant-building
`MOVS`/`LSLS` pairs that IDA folds into four-byte pseudo-instructions. The
structure artifact records those addresses; the two views agree on byte spans.
This is an instruction and literal-pool classification. It does not make all
branch states, caller invariants, or downstream helper semantics complete.

The bounded phase map from original instructions is:

| Span | Established role and effects |
|---|---|
| `0x50F0..0x522E` | Advance a counter at `0x200470`, normalize input indices, update state word `0x20044C`, and test counter remainder modulo 250. |
| `0x522E..0x52D2` | Conditionally call the two-candidate backdown updater and store AID 13 response byte `0x200BCD`; run selector/input helpers and form a clamped telemetry word at `0x200604`. |
| `0x52D2..0x53A2` | Derate a scalar with AID 13, compute applied stretch, test gates, and conditionally request TC0 RC write through `0x6FA0`. |
| `0x53A2..0x5474` | Store two attempted-output flags at `0x200789/788`, select telemetry inputs, and write several response bytes. |
| `0x5474..0x55BA` | Convert/filter numeric state through integer and software-float helpers; populate response bytes in `0x200BB6..0x200BD8`. Individual response scales need continued review. |
| `0x55BA..0x5612` | Compare prior/current words, count consecutive matching states, conditionally call peripheral initializer `0x74E8` after the count reaches `0x7D1`, save current words, and return the low byte of a local selector. The count is iterations, not a measured time. |

This phase map captures the branch/call structure and direct stores. It is not
a full consumer/writer account for every state value or a proof that every
branch executes in service.

## Derate, clamp and timer-write slice

At `0x5324`, `0x4A94` returns an applied scalar. The caller reads AID 13
response byte `0x200BCD`, computes `floor(applied × backdown / 100)` with
the real integer helper, and subtracts it to form R6. The subsequent direct
gates require a local selector to exceed a step/residue expression, R6 to be
nonzero, and word `0x200594` to be at least the word held in R5. The optional
R6 clamp runs only when R5 is at least 3200 **and** byte `0x2006EC` is nonzero;
then it bounds R6 to 410..2730. Otherwise that clamp is bypassed.

At `0x5382..0x538A`, the routine forms `R1 = (24 × R6 + 3) mod 2^32` and
calls `0x6FA0` with TC0 base `0xFFFA0000`. The helper reads TC0 status at
offset `0x20`; if bit 16 is clear, it writes R1 to RC at offset `0x1C` and
returns 1. If bit 16 is set, it does not write RC and returns 0. The
[SAM7S datasheet](https://ww1.microchip.com/downloads/en/DeviceDoc/doc6175.pdf)
identifies bit 16 as `CLKSTA` and defines the RC field in bits 0–15. The
emulator records the 32-bit bus value; it is not a timer waveform model.

| Synthetic case | R6 after backdown/clamp | 32-bit value presented to RC | Observed write |
|---|---:|---:|---|
| Table byte 100, backdown 0, TC clock disabled | 1,700 | `0x00009F63` | yes |
| Table byte 100, backdown 80, TC clock disabled | 340 | `0x00001FE3` | yes |
| Table byte 100, TC clock enabled | 1,700 | `0x00009F63` | no |
| Table byte 100, local selector gate zero | 1,700 | `0x00009F63` | no |
| Table byte 140, R5=100, clamp disabled | 42,947,700 | `0x3D6FEAE3` | yes |
| Table byte 140, R5=100, clamp flag enabled | 42,947,700 | `0x3D6FEAE3` | yes; R5 bypasses clamp |
| Table byte 140, R5=3,200, clamp flag enabled | 2,730 | `0x0000FFF3` | yes |

The high-bit byte is sign-extended by `LDRSB` in `0x4A94`, as the
[stretch review](INTEGER_ARITHMETIC_REVIEW.md) established. The path test
shows how such a synthetic value can reach the RC write, and that the clamp
requires both conditions. It **does not prove that a table writer can produce
byte 140 in service**, that the chosen stack/gate state occurs in a vehicle,
or that a large 32-bit write produces a particular pulse. Those are the
discriminating next checks. The physical pump topology remains outside this
image's direct evidence.

Regenerate the structural and path artifacts with a matching local image,
Binary Ninja evidence already exported, and Unicorn installed:

```sh
python audit/tools/audit_main_control_structure.py firmware_v2.8.4HF.bin --output audit/data/main_control_structure.json
python audit/tools/emulate_control_timer_tail.py firmware_v2.8.4HF.bin --output audit/data/control_timer_tail_emulation.json
```

No device traffic or settings change was performed.
