# High-idle delay and input-gated state at `0x4818`

This review executes the original V2.8.4HF application bytes, SHA-256
`1ae519ba6194e8f7bdaaa94333a83a9e6fda3b0563f87f7d48383b37288c1780`.
The [execution report](../audit/data/input_gate_emulation.json) contains 16,390
matching synthetic calls and visits every one of the 85 decoded instruction
starts in `0x4818..0x48C2`. The [bounded Thumb decode](../audit/data/input_gate_binaryninja.json)
includes the following `C0 46` NOP at `0x48C2`; it is classified separately.
The nine literal words at `0x48C4..0x48E8` are all referenced. Three further
loads reuse words at `0x4950`, `0x4954`, and `0x4958`; that shared pool is
outside this new instruction range.

## Inputs, outputs, and state

The only decoded direct caller is `0x523C` in `0x50F0`. R0 retains the return
from the preceding selector call `0x506C` and serves as a mode/inhibit value.
The helper always returns 0 or 1 and writes that same result to byte
`0x20042D`. Its state byte is `0x20042C`.

| Input | Role in these instructions |
|---|---|
| Byte `0x2006E2` | Enable; any nonzero value enables the state logic |
| R0 | Nonzero inhibits this call's state progression and returns zero |
| Word `0x2005EC` | Capture-derived word, compared unsigned with 1,000 |
| Word `0x2005F0` | Must equal zero for the idle-entry condition |
| Byte `0x2005D7` | Must equal zero for entry and active-state retention |
| Halfword `0x2006E4` | Multiplied by 10,000 to set word `0x200730` |
| Byte `0x20071B` | Completion event read while state equals 1 |

Define `idle = capture < 1000 and word[0x2005F0] == 0 and byte[0x2005D7] == 0`.
With enable nonzero and R0 zero, the instruction contract is:

| Initial state | Condition | Resulting writes and return |
|---|---|---|
| Any state other than 1 or 3 | `idle` | Store `duration*10000` to `0x200730`; set `0x20071A=1`, `0x200719=1`, clear `0x20071B`, set state to 1; return 0 |
| Any state other than 1 or 3 | Not `idle` | Retain state and timer/flags; return 0 |
| 1 | Not `idle` | Clear `0x200719` and state; return 0 |
| 1 | `idle`, event zero | Retain state and timer/flags; return 0 |
| 1 | `idle`, event nonzero | Set state to 3 and fresh flag `0x20071E=1`; return 0 |
| 3 | Both source word and input byte zero | Retain state; return 1, regardless of capture word |
| 3 | Either source word or input byte nonzero | Clear state; return 0 |

Disable clears the state and returns zero but retains the timer/flags. A
nonzero mode argument retains the state and timer/flags and returns zero.
Every path stores the returned active byte at `0x20042D`. In particular,
capture crossing 1,000 cancels state 1, while state 3 does not recheck that
threshold. These are verified state rules, not inferred engineering units.
The maximum halfword product is `65535*10000 = 655350000`, so that particular
multiply fits in 32 bits.

## Connection to reviewed parameter, callback, and accumulator paths

The [compound AID review](COMPOUND_AID_UPDATE_REVIEW.md) identifies AID 153,
named High Idle Delay Setting by the profiles, as the writer of enable byte
`0x2006E2` and duration halfword `0x2006E4`. The helper starts the counter
protocol by setting reset byte `0x20071A` and active byte `0x200719`.
The [TC2 callback review](TC2_CALLBACK_REVIEW.md) independently establishes
that it resets counter `0x200784`, increments it while active, and when the
prior count is greater than threshold `0x200730`, sets `0x20071B=1` and clears
the active flag. This explains the completion event consumed in state 1.

The state-1 to state-3 transition sets `0x20071E=1`. The
[fresh accumulator review](CONTROL_HELPER_REVIEW.md) shows `0x48E8` consumes
that flag and uses active byte `0x20042D` as one of its update gates. This
connects the AID working values, delayed completion, state transition, and
fresh accumulator input. It does not establish all competing flag writers,
interrupt interleavings, physical delay units, or live output behavior.

## Verification and reproduction

The main sweep covers all 256 initial state bytes with both enable/mode
conditions, capture values 999/1000, zero/nonzero source and input, and both
completion-event conditions: 16,384 calls. Six additional cases cover
non-Boolean enable/event bytes, maximum duration, high-bit capture/source
words, and a wide nonzero mode. The harness checks the exact state, active
byte, four flags, timer, R4–R11, stack balance, return address, allowed code
range and every non-stack write. ROM is read/execute and SRAM read/write;
no peripherals are mapped. Unicorn ARM926 is a functional surrogate, not
ARM7TDMI timing or interrupt simulation.

```sh
PYTHONPATH=<Binary Ninja Python path> python audit/tools/decode_image_ranges.py firmware_v2.8.4HF.bin --ranges 0x4818:0x48c4:thumb2 --output audit/data/input_gate_binaryninja.json
python audit/tools/emulate_input_gate.py firmware_v2.8.4HF.bin --output audit/data/input_gate_emulation.json
python audit/tools/build_image_ledger.py firmware_v2.8.4HF.bin
```

No connected device, flashing, or setting changes were used.
