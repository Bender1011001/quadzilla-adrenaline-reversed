# Capture scalar and curve dispatch at `0x4B38`

This review uses the exact 32,000-byte V2.8.4HF application image, SHA-256
`1ae519ba6194e8f7bdaaa94333a83a9e6fda3b0563f87f7d48383b37288c1780`.
The [bounded Thumb decode](../audit/data/capture_scalar_binaryninja.json),
[byte-verified IDA items](../audit/data/ida_image_items.json), and
[structure audit](../audit/data/capture_scalar_structure.json) establish three
code islands separated by two byte jump tables. This is a static original-byte
review; it is not a full runtime or hardware simulation.

| Image range | Supported classification |
|---|---|
| `0x4B38..0x4B82` | 74 Thumb instruction bytes |
| `0x4B82..0x4B84` | `C0 46` NOP alignment |
| `0x4B84..0x4BA1` | 29 byte offsets for the first jump table |
| `0x4BA1` | zero pad byte, unreachable through the guarded index |
| `0x4BA2..0x4C32` | 144 Thumb instruction bytes |
| `0x4C32..0x4C34` | `C0 46` NOP alignment |
| `0x4C34..0x4C3E` | 10 byte offsets for the second jump table |
| `0x4C3E..0x4D0A` | 204 Thumb instruction bytes, ending in `BX R1` |
| `0x4D0A..0x4D0C` | `C0 46` NOP alignment |
| `0x4D0C..0x4D38` | 11 PC-relative literal words |

The decode has 205 instruction starts including the three NOPs. All 11
literal words have one PC-relative load site. All 55 non-call direct branches
target decoded code starts. Nine direct calls go only to the unsigned division
entry `0x8574` and the persistent-latch helper `0x47B0`. The byte tables are
used by `LDRB` then `ADD PC,R1`; the audit computes each target from the
actual offset byte and checks it against a decoded Thumb start. The only IDA
four-byte constant-building item folded across a Binary Ninja start is at
`0x4CFA`. Decoder agreement and target reconciliation classify these bytes;
they do not establish all feasible caller states.

## Caller and curve inputs

The only decoded direct call is `0x52D2` inside the main control loop. Its R1
argument is the low byte returned by the [selector helper](CONTROL_SELECTOR_REVIEW.md).
The caller supplies a word read from `0x2005E4` in R2, a low-byte value in R3,
and three stack arguments. The complete provenance and production ranges of
the remaining arguments still need tracing. The helper uses R2 as its primary
scalar, reads word `0x200594` as an upper threshold, and uses bytes
`0x200598..0x2005AF` as a 24-slot curve. AIDs 113–136 write those working
bytes after clamping each to 50..150; AID 104 writes the threshold word.
Those writer rules and initializer defaults are documented in the
[AID handler review](REMAINING_AID_UPDATE_REVIEW.md) and
[control helper review](CONTROL_HELPER_REVIEW.md). This establishes dataflow,
not the curve's physical units.

## Indexed selection and arithmetic

The first gate compares `2 × byte[0x200433] + byte[0x200434]` with the
selector. If the sum is lower, `0x4B4E..0x4B74` optionally computes a
percentage term when its stack word is at least 3,101 and below working word
`0x200594`. It then reads counter word `0x20044C`. Indices 0..28 use the first
29-byte table to choose among curve slots 0..22, with some later indices
mapping to the same slot. Indices above 28 explicitly read slot 23. It forms
`floor(R2 × selected_byte / 100)` using unsigned division. If that exceeds R2,
an additional percentage term is added; otherwise the initial result is kept.

When the first gate fails, the second gate compares
`byte[0x200433] + byte[0x200434]` with the selector. If lower, counter indices
0..9 choose curve slots 0..9 through the second 10-byte table. Higher indices
read slot 10. The selected byte scales R2 by an unsigned divide by 100, with
the result capped at R2. If the second gate also fails and the selector is
nonzero, byte `0x20058E` supplies another percentage of R2. If the selector
is zero, the helper retains R2. The branch conditions and integer truncation
are explicit in the instruction evidence; none of these percentages should
be read as floating-point interpolation.

The helper then calls `0x47B0` with zero mode. If the latch reports ready, it
clears byte `0x20042E`. Otherwise a guarded branch can scale R2 using curve
slot 0 when that slot is below 100 and byte `0x20042A` is nonzero. That branch
sets `0x20042E` and copies capture word `0x2005E8` to telemetry word
`0x200604`. The subsequent main-loop scalar helper can overwrite the same
telemetry word; this copy is not proof of the value ultimately transmitted.

Finally, if word `0x2005EC` is in the unsigned interval 701..1499 and the
current scalar is below R2, the helper accesses a signed byte at
`0x200294 + 20 × row + column` and adds a percentage of the difference.
**There is no local bounds check inside this helper.** The
[direct-caller bound audit](../audit/data/capture_table_bounds.json) now traces
both indices through `0x50F0`: row is 0..19 from word `0x2005F0`, and column
is 0..19 from capture word `0x2005EC`. Their maximum offset is 399, the last
byte of the 20×20 initialized table. Thus this direct call does not support
an out-of-table claim for intact caller state. Alternate or indirect callers,
stack corruption, and later table writers remain separate questions.
The table's 400 initial bytes are all 0..100, so the signed load is initially
nonnegative; later RAM mutation has not been excluded.
The terminal comparison caps values at 4,095 when they are not less than
4,096 under a signed comparison; its return is R0. Full overflow and live
range analysis remains open.

Reproduce the structural artifact with a matching independently obtained
image and the Binary Ninja Python package path:

```sh
PYTHONPATH=<Binary Ninja Python path> python audit/tools/decode_image_ranges.py firmware_v2.8.4HF.bin --ranges 0x4b38:0x4b84:thumb2,0x4ba2:0x4c34:thumb2,0x4c3e:0x4d0c:thumb2 --output audit/data/capture_scalar_binaryninja.json
python audit/tools/audit_capture_scalar_structure.py firmware_v2.8.4HF.bin --output audit/data/capture_scalar_structure.json
python audit/tools/build_image_ledger.py firmware_v2.8.4HF.bin
```

No device traffic, flashing, setting changes or physical measurements were
performed.
