# TC2 pointer ownership and transport-fixture correction

This review corrects an analysis-fixture assumption before interrupt-composition
work. It is bound to the exact V2.8.4HF 32,000-byte image, SHA-256
`1ae519ba6194e8f7bdaaa94333a83a9e6fda3b0563f87f7d48383b37288c1780`.
The [new execution artifact](../audit/data/peripheral_pointer_ownership.json)
records original TC2 and USART callback reads under initialized and deliberately
altered pointer cases. This is a harness correction, not a firmware defect.

## Image and original callback evidence

The initialization copy maps image word `0x9E10` to SRAM `0x200728`; its bits
are `0xFFFA0080`, the TC2 block base. The existing
[timer setup artifact](../audit/data/timer_setup_emulation.json) already records
that source mapping. TC2 callback `0x6C94` loads structure base `0x200708` from
literal `0x6F58`, reads its word at offset `0x20`, then reads the pointed block
at offset `0x20`. With the initialized pointer, actual instruction `0x6C9A`
reads `0xFFFA00A0`.

USART callback `0x7178` instead loads direct status address `0xFFFC0014` from
literal `0x71C0`, then reads it at `0x717C`. It does not need SRAM slot
`0x200728` to select that register. The two original callback bodies execute
to their returns under controlled flag/status inputs; no helper return is stubbed.

The deliberately altered case supplies `0xFFFC0000` at `0x200728`. TC2's read
then moves to `0xFFFC0020`, while the USART status read remains `0xFFFC0014`.
Both callbacks retain the supplied pointer. This demonstrates why that artificial
override would be unsuitable for later TC2/transport interrupt composition.
It does not establish a production path that corrupts the pointer.

## Corrected fixtures and prior results

Four harnesses had explicitly supplied `0xFFFC0000` at the TC2 slot as part
of transport preparation. They now supply the image's `0xFFFA0080`:

| Harness | Reproduced prior artifact |
|---|---|
| `emulate_aid255_control_admission.py` | `aid255_control_admission.json` |
| `emulate_queue_state_owners.py` | `queue_state_owners_emulation.json` |
| `emulate_short_value_admission.py` | `short_value_admission.json` |
| `emulate_capture_percent_control.py` | `capture_percent_control.json` |

Each prior artifact is regenerated after the correction and compared byte for
byte. Those transport/control runs do not execute TC2, so their recorded results
remain unchanged. Their earlier synthetic states must not be retrospectively
described as faithful full startup or interrupt conditions. The correction
preserves the established bounded results while removing the unused wrong
pointer from future reproductions.

## Remaining ownership and interrupt work

The image establishes the initialized pointer; this pass does not exclude
later computed/alias writers. Calling callback bodies with ordinary host return
links is not ARM exception entry, banked-register, nesting or interrupt timing
simulation. Full asynchronous source stability still requires transitive writer
contracts and the relevant pointer/frame assumptions. The full goal remains active.

```sh
python audit/tools/emulate_peripheral_pointer_ownership.py firmware_v2.8.4HF.bin --output audit/data/peripheral_pointer_ownership.json
python -m unittest discover -s tests -t .
```

No device traffic, flashing, engine-setting change or hardware measurement occurred.
