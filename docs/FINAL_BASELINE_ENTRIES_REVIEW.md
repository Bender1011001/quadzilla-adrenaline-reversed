# Final three entries in the original 145-entry catalog

This review binds to the V2.8.4HF application image, SHA-256
`1ae519ba6194e8f7bdaaa94333a83a9e6fda3b0563f87f7d48383b37288c1780`.
The [bounded Thumb decode](../audit/data/remaining_entry_binaryninja.json)
and [synthetic execution](../audit/data/remaining_entry_emulation.json) support
the instruction accounts below. The [reproducer](../audit/tools/emulate_remaining_entries.py)
uses an ARM926 instruction surrogate and synthetic SRAM/MMIO; it does not prove
physical outcomes or live reachability.

With a locally obtained image of the stated hash and Unicorn installed, regenerate
the bounded cases with:

```sh
python audit/tools/emulate_remaining_entries.py firmware_v2.8.4HF.bin --output audit/data/remaining_entry_emulation.json
```

## `0x7444`: no-op callback

The entire body is `BX LR`; it makes no store and has no register side effect
apart from the control transfer. In a bounded call, R0 and SP were unchanged.
The next halfword at `0x7446` is `FFFF` alignment, not part of the body.

The original direct-call graph shows no incoming call. A raw pointer word
`0x00007445` at `0x7A48` is loaded at `0x77E0` and written to AIC address
`0xFFFFF134` at `0x77E2`, after the conditional vector-page helper. Thus the
firmware **installs this Thumb no-op as its spurious-interrupt callback** on
that startup path. The absence of an ordinary `BL` edge did not mean it was
unused. Whether that callback ever fires on the board is unmeasured.

## `0x74C4`: two-byte SRAM predicate

The 13-instruction Thumb body at `0x74C4..0x74DE` loads fixed SRAM addresses
`0x200791` and `0x2005DD` from literal words at `0x74E0` and `0x74E4`.
It returns R0=1 exactly when both bytes are nonzero; otherwise R0=0. It takes
no argument from its caller in this body and performs no stores. Five bounded
cases include each false branch, the true branch, and noncanonical nonzero
bytes. The halfword at `0x74DE` is a Thumb NOP before the two literal words.

IDA misdecodes the `FFFF` halfword at `0x74C2` together with the first Thumb
instruction at `0x74C4` as a NEON opcode; this ARM7TDMI image cannot execute
that interpretation. IDA also decodes the first literal word as two apparent
instructions. The explicit Thumb decode and the literal-address arithmetic
resolve those boundaries. No direct caller or literal function pointer to
`0x74C5` was identified in this image, so service reachability and the
physical meaning of these two bytes remain open.

## `0xB114`: source of the SRAM flash-ready helper

`0xB114..0xB122` is the first routine in the 164-byte template copied by the
startup descriptor to runtime `0x200C84..0x200D28`. It reads flash-controller
status at `0xFFFFFF68` and loops until bit 0 is set; then it returns. The
bounded runtime-alias call returned for synthetic status 1 and continued
looping through an instruction limit for status 0. No timeout exists in this
body. The source remains classified in the byte ledger as part of a copied
executable template, rather than counted twice as both data and in-place
instructions.

There is no direct call to source `0xB114`, but `0x6B20` calls runtime alias
`0x200C84`, and the page-write template also reaches this ready check.
The [startup/persistence review](STARTUP_PERSISTENCE_REVIEW.md) accounts for
the template and flash-controller command path. Status bit semantics come
from the [SAM7S datasheet](https://ww1.microchip.com/downloads/en/DeviceDoc/doc6175.pdf).
No flash write or board traffic was performed for this review.

These accounts close the **original catalog's** semantic queue. That catalog
is not an exhaustive execution-entry inventory. The separate supplemental
entries, remaining code/data candidates, indirect calls, and full subsystem
paths still require review under the active full-image goal.
