# Initial state, configuration restore, and AID 151 response mirror

This review binds to the exact 32,000-byte V2.8.4HF application image,
SHA-256 `1ae519ba6194e8f7bdaaa94333a83a9e6fda3b0563f87f7d48383b37288c1780`.
The [bounded decode for `0x760C`](../audit/data/initial_state_binaryninja.json)
has 70 Thumb starts across 140 bytes; all are visited in the
[original-byte campaign](../audit/data/initial_state_emulation.json).
The [configuration decode](../audit/data/config_restore_binaryninja.json)
covers `0x5F14..5F2E` (26 bytes), `0x5F34..5FEC` (184 bytes), and
`0x8530..854A` (26 bytes). The mirror's 92 starts and copy helper's 13
starts are all visited by bounded execution. The `0x5F14` campaign stops
before its distinct `0x5F34` callee; its final two epilogue starts are
statically reviewed. IDA and Ghidra agree on `0x760C`, `0x5F14` and
`0x5F34` bounds. IDA folds the first Thumb halfword at `0x8530` into an
invalid `VSRI.32` item beginning at `0x852E`; Binary Ninja and original-byte
execution support the Thumb entry at `0x8530`.

## Initial state selector `0x760C`

The main-loop setup calls `0x760C` once after waiting for byte `0x200718`
to become nonzero, then stores the returned byte at `0x200790`. The helper
takes no caller-supplied arguments and preserves R4–R7 and SP. It reads
PIOA status `0xFFFFF43C` bit 28 and configuration byte `0x2006ED` (offset
`0x21` in the `0x2006CC` block). A low pin reads as boolean 1; a high pin
as 0. The image initializes the mode byte to 4. These are instruction and
source-image facts; the physical signal on the pin has not been identified.

| Mode byte | Result with pin 28 low | Result with pin 28 high | Additional path |
|---:|---:|---:|---|
| 1 | 1 | 1 | No nonstack store. |
| 2 | 2 or 0 | 2 or 0 | Independent of pin. See below. |
| 3 | 3 | 0 | On result 3, stores `1,0,1` to `0x200717,718,716`. |
| Every other value tested, including initialized 4 | 1 | 0 | No nonstack store. |

For mode 2, a nonzero byte at `0x2006DE` causes result 2. It copies
`word[0x2006F0]` to `0x200734`, stores
`(uint16[0x2006E0] * 10000) mod 2^32` at `0x20072C`, clears
`0x200715`, and sets `0x200713`. When `0x2006DE` is zero, it first stores
the configured halfword at `0x200794`. If that halfword is greater than or
equal to `word[0x2008A8]`, it returns 0 without the later stores. If less,
it returns 2, copies the word to `0x200734`, stores `0x5B8D80` at
`0x20072C`, clears `0x200715`, and sets `0x200713`. The emulation includes
below, equal, and above comparisons. The
[ADC pipeline review](ADC_PIPELINE_REVIEW.md) identifies `0x2008A8` as
the gated 32-sample average of a channel-4 table value. The names of the two time-like words
and exact elapsed-time semantics remain unresolved; `0x5B8D80` is the
literal six million, not a measured duration.

## Configuration source at `0x10FF00`

At startup, `0x5F14` reads byte `0x10FF00`. If it equals `0xA5`, it calls
forward byte-copy helper `0x8530` with destination `0x2006CC`, source
`0x10FF00` and count `0x2C` (44). It then calls response mirror `0x5F34`
regardless of the magic byte. The [bounded restore runs](../audit/data/config_restore_emulation.json)
show the initialized mode 4 retained when synthetic source byte 0 is zero
and replaced when it is `0xA5`; the test pattern changes offset `0x21`
from 4 to 234. Thus the image default does **not** establish the mode of a
unit with accepted contents at `0x10FF00`. That address is outside the
supplied application image. The firmware checks one magic byte here; this
review does not establish the contents, validity, or provenance of a board's
non-image storage.

The copy helper returns immediately for count zero and otherwise copies
forward one byte at a time. The restored 44-byte block includes the
selector mode and fields used by the mode-2 branches. This startup copy
does not touch the five telemetry-list count bytes. The generic copy helper
can write a destination supplied by another caller, so its other call paths
and the larger alias search remain open.

## Confirmed local AID 151 response mismatch

The `0x5F34` mirror reads the configuration block and writes several SRAM
response locations. The [five-case execution artifact](../audit/data/config_response_mirror_emulation.json)
visits all 92 of its instruction starts, records ordered writes, and then
calls the already reviewed AID reader `0x7D80` with AID 151. The AID 151
update handler stores a first byte at `0x2006DA` and a little-endian
halfword at `0x2006DC`; its table-2 response pointer is `0x200BE7`.

| Configuration source | Response destination | Observed transform |
|---|---|---|
| `0x2006CD`, `0x2006CE` | `0x200BC4`, `0x200BC5` | First byte masked to seven low bits; second copied. |
| `0x2006CF..D6` | `0x200BDC..E3` | Eight bytes copied in order. |
| `0x2006D7..D9` | `0x200BE4..E6` | Byte and little-endian halfword copied. |
| `0x2006DA` | `0x200BE7` | Byte copied. |
| `0x2006DC..DD` | `0x200BE8` twice | Low byte then high byte; `0x200BE9` not written. |
| `0x2006DF`, `0x2006DE` | `0x200BD9` bits 0, 1 | Each source's nonzero status sets its bit; zero clears it; other bits retained. |
| `0x2006E0..E1` | `0x200BDA..DB` | Little-endian halfword copied. |
| `0x2006F4..F5`, `0x2006F6` | `0x200B19..1A`, `0x200B1C` | Three bytes copied. |

At `0x5F8C`, the mirror writes the first byte to `0x200BE7`. It writes
the low byte of the halfword to `0x200BE8` at `0x5F96`, then writes the
high byte **to the same `0x200BE8`** at `0x5F9C`. It makes no store to
`0x200BE9`. With a synthetic working halfword `0x7A73`, first byte
`0x65`, and response SRAM initialized to zero, the final three response
bytes are `65 7A 00`; the original AID reader returns payload
`97 65 7A 00` (AID `0x97` plus those bytes). With a sentinel `0xEE` in
response SRAM, it returns `97 65 7A EE`, proving that the third response
byte was retained rather than written by this function.

This is a **confirmed local mirror mismatch** for the implemented AID 151
response path. The intended external interpretation of unprofiled AID 151,
later computed-pointer writers, and whether a live request can observe the
same state without another update still need investigation. The supplied
image's zero-fill descriptor covers the response SRAM at startup, but the
sentinel case isolates the lack of a `0x200BE9` store. No hardware traffic
was sent.

```text
PYTHONPATH=<Binary Ninja Python path> python audit/tools/decode_image_ranges.py firmware_v2.8.4HF.bin --ranges 0x760c:0x7698:thumb2 --output audit/data/initial_state_binaryninja.json
PYTHONPATH=<Binary Ninja Python path> python audit/tools/decode_image_ranges.py firmware_v2.8.4HF.bin --ranges 0x5f14:0x5f2e:thumb2,0x5f34:0x5fec:thumb2,0x8530:0x854a:thumb2 --output audit/data/config_restore_binaryninja.json
uv run --with unicorn==2.1.4 python audit/tools/emulate_initial_state.py firmware_v2.8.4HF.bin --output audit/data/initial_state_emulation.json
uv run --with unicorn==2.1.4 python audit/tools/emulate_config_restore.py firmware_v2.8.4HF.bin --output audit/data/config_restore_emulation.json
uv run --with unicorn==2.1.4 python audit/tools/emulate_config_response_mirror.py firmware_v2.8.4HF.bin --output audit/data/config_response_mirror_emulation.json
python audit/tools/build_image_ledger.py firmware_v2.8.4HF.bin
python -m unittest discover -s tests -t .
```
