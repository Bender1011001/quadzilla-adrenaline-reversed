# Control selector mapping and AID 9 response encoding

Entry `0x506C` maps a working selector to a byte used by later control
arithmetic and separately writes the byte returned for AID 9. This review
applies to the exact 32,000-byte V2.8.4HF image, SHA-256
`1ae519ba6194e8f7bdaaa94333a83a9e6fda3b0563f87f7d48383b37288c1780`.
It adds one baseline role (109 reviewed, 36 pending) and 112 classified
Thumb instruction bytes `[0x506C,0x50DC)`. The following five literal words
are excluded from the instruction range.

The [Binary Ninja decode](../audit/data/control_selector_binaryninja.json)
contains 54 instruction starts; all boundaries match the byte-verified IDA
item export. [Original-byte execution](../audit/data/control_selector_emulation.json)
visits 52 starts. The remaining two have a specific unreachable-path proof
below. A superset Thumb decoder and an ARM926 functional emulator are used;
neither establishes ARM7TDMI hardware timing or all live states.

## Inputs, outputs and caller connection

The entry ignores incoming scalar arguments, calls `0x47B0(0)` to update
the reviewed persistent threshold/latch state, and uses its return as a
readiness gate. That helper consumes the captured signed source at
`0x2005F4`, along with its enable/threshold/counter and prior latch bytes.
Its complete contract is in the [control-helper review](CONTROL_HELPER_REVIEW.md).

| Byte address | Local role |
|---|---|
| `0x2006CD` | Working selector S. |
| `0x200580` | Count/cap byte C. |
| `0x200433` | Step byte T. |
| `0x200434` | Offset byte O. |
| `0x200BCD` | Marker input M; threshold is 13. |
| `0x200BC4` | Stored response byte E. |

R0 returns the mapped byte V as an unsigned 32-bit value. The response byte
E is a different result. The only non-stack writes are the latch helper's
state updates and the store to `0x200BC4`. No peripheral access occurs.
R4–R11 and the stack are preserved in the checked calls; flags and
caller-saved registers are not specified as outputs.

The known direct caller is `0x50F0` at `0x5236`. It stores R0 in its local
stack slot at `0x523A`, later reloads that slot into R1 at `0x52C6`, narrows
it to a byte, and passes it to arithmetic entry `0x4B38` at `0x52D2`.
This establishes a consumer of V, not a complete reconstruction of that
large caller or the physical effect of the arithmetic result.

Separately, response pointer table 2 at `0xAD18` has AID 9's word at
`0xAD3C` equal to `0x200BC4`. AID 9 has one-byte width, and the profiles
name it **Power Level**. Sixteen boundary probes execute the real reader
`0x7D80` after the selector call: it returns two output bytes `09 E` and
does not remove E's high bit or replace its special values. This is a
sequential helper-to-reader path, without packet framing or transport.
Table 1's AID 9 pointer is the distinct staging byte `0x200B00`; this review
does not assert that all staged values reach S unchanged.

## Exact local arithmetic

All S, C, T, O and M inputs are unsigned bytes. Let R be the latch helper's
return; any nonzero R is treated as ready.

1. If R is zero, set E=`E4`, return V=0, and skip selector arithmetic.
2. If S is zero, set E=0, return V=0, and skip the marker threshold.
3. Otherwise, if S is at least C, replace S with `(C-1) mod 256`.
4. Compute `V=(S*T+O) mod 256`. Keep this value as the eventual return.
5. If V is below 128, set a temporary reported value Q=S. If V is at least
   128, set `Q=truncate_toward_zero((V-O)/T)` using the signed runtime
   divider. Its established zero-denominator policy yields quotient zero.
6. If M is at least 13, OR Q with `0x80`. Store `E=Q mod 256` and return V.

The sign test is implemented by narrowing the computed sum to signed eight
bits and comparing it with its zero-extended representation. This is not
saturation at 127, and the optional division is performed on the already
wrapped byte. E must not be assumed to equal either V or the original S.

| Controlled inputs `(S,C,T,O,M)` | V returned | E stored | Significance |
|---|---:|---:|---|
| `(2,10,100,100,0)` | 44 | 2 | Sum 300 wraps to 44. |
| `(1,10,0,128,0)` | 128 | 0 | High-bit branch invokes the divider with zero denominator. |
| `(255,0,1,0,0)` | 255 | 255 | C=0 underflows the replacement selector to 255. |
| `(1,10,1,0,12)` | 1 | 1 | Marker below threshold. |
| `(1,10,1,0,13)` | 1 | 129 | Marker threshold sets bit 7 in E, leaving V unchanged. |
| `(129,255,1,255,0)` | 128 | 129 | Signed quotient is -127; its stored low byte has bit 7 even without the marker threshold. |

For the initialized shape C=11, T=10, O=0, ready nonzero, S=1..255
maps to `V=10*min(S,10)`, with Q=`min(S,10)`. S=0 remains zero. Marker
values at least 13 set bit 7 for nonzero original S. Initialization bytes
and the reviewed default initializer support this shape; later writers can
change the configuration. None of the synthetic C=0/large-step probes alone
establishes a reachable parameter-validation defect.

## Unreachable instruction disposition

At `0x509E..0x50A4`, R2 is the zero-extended mapped byte and R5 is its
signed-eight-bit extension. Falling through the equality branch therefore
requires V>=128. `MOVS R0,R2` at `0x50A6` sets Z=0 because R2 is then nonzero.
The `BNE` at `0x50A8` always branches to `0x50AE`. Consequently the `MOVS`
at `0x50AA` and branch at `0x50AC` are unreachable from normal entry under
the instruction semantics. They remain classified as instruction bytes,
with an explicit dead-path disposition rather than fabricated execution.
No direct branch into either start appears in the full IDA item export;
arbitrary PC corruption or unknown external execution is outside this proof.

## Validation, unresolved work and reproduction

The original helper and latch bytes were executed for 65,536 selector/step
pairs with fixed C=255, O=17, M=0; 4,096 seeded cases varying all byte
configuration and latch inputs; 1,024 initialized-shape cases; and 16
discriminating boundary/readback calls: **70,672 selector calls**, with zero
reference differences. Sixteen random and twenty initialized-shape examples
are preserved alongside all boundary cases. The sweep digest covers the
pair sweep followed by seeded cases; it does not include the initialized-shape
or boundary calls. The reference preserves byte wrap and signed truncation.

The captured source can affect readiness through the persistent latch helper.
This establishes one connection from the CAN parser to selection, but does
not establish freshness checks, complete global writer sets or IRQ ordering.
M is written by the preceding `0x499C` path under caller conditions that still
require a full account. Its application meaning and the app's interpretation
of E's special/high-bit values remain unresolved. The subsequent [AID 9/15 update review](AID_DISPATCH_SELECTOR_UPDATES.md)
establishes their count bounds, mapping derivation and sequential behavior.
Other `0x601C` handlers and the full `0x50F0` consumer account remain required
before assigning physical output or severity.
Passive hardware observations can test reported AID 9 values during ordinary
operation; no traffic injection or engine setting changes were performed.

```text
PYTHONPATH=<Binary Ninja Python path> python audit/tools/decode_image_ranges.py firmware_v2.8.4HF.bin --ranges 0x506c:0x50dc:thumb2 --output audit/data/control_selector_binaryninja.json
uv run --with unicorn==2.1.4 python audit/tools/emulate_control_selector.py firmware_v2.8.4HF.bin --output audit/data/control_selector_emulation.json
python -m unittest discover -s tests -t .
```
