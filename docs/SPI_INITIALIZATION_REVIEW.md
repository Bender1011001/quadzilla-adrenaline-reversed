# SPI initialization sequence and shared timeout

This review covers entry `0x575C` in the exact 32,000-byte V2.8.4HF image,
SHA-256 `1ae519ba6194e8f7bdaaa94333a83a9e6fda3b0563f87f7d48383b37288c1780`.
The [bounded decode](../audit/data/spi_initialization_binaryninja.json) includes
its complete 622-byte instruction body and 30 bytes of the reset-only path
through `0x59E8`. All 297 instruction starts match the byte-verified IDA
boundaries and are visited across the [four execution cases](../audit/data/spi_initialization_emulation.json).
The selected decoder supports a superset of ARMv4T; source identity, explicit
Thumb bounds and visited paths are retained as evidence.

## Contract and timeout state

The board setup coordinator `0x74E8` calls `0x575C`. The initializer consumes
no explicit argument. It uses initialized SPI base pointer `0x2005E0`, SRAM
command buffers relative to `0x2005C4`, one image buffer, and a shared timeout
flag. It calls the reviewed [PIO/SPI/PDC primitives](SPI_TRANSFER_REVIEW.md),
the reset path of `0x59E8`, and the reset path of the
[SPI output state routine](SPI_STATE_MACHINE_REVIEW.md).

First, it calls `0x573C(1)` and `0x573C(2)`, writing masks `0x100` and
`0x200` to PIO_SODR. Two short local loops each increment an eight-bit value
from zero to 100; their real duration is unmeasured. Before transfers, the
routine writes `0x200AD4=1`, `0x200AD5=0`, `0x200AD3=1` once.
The [TC2 callback](TC2_CALLBACK_REVIEW.md) treats these as counter-reset,
completion and active flags for counter `0x200774`; when its prior unsigned
count reaches 3001 it sets `0x200AD5=1` and clears the active flag.

Each transfer loop repeats while the helper returns 0 and `0x200AD5` is
still zero. A nonzero helper result or nonzero timeout flag advances to the
next step. The timeout is shared across the sequence and is not restarted
at every transfer. The routine does not derive or validate a wall-clock
deadline itself. Its stores and calls establish intended setup behavior;
they do not prove successful external transactions.

## Ordered transfer requests

Every request uses SPI base `0xFFFE0000`. TX rows call `0x6B64` with the
listed pointer/count. The paired row calls `0x6B9C` with receive pointer,
transmit pointer and shared count. The artifact retains every call site,
argument and retry attempt; no PDC data movement is modeled.

| Step | Call site | Kind | Transmit pointer | Count | Receive pointer |
|---:|---|---|---|---:|---|
| 1 | `0x5790` | TX | `0x20060A` | 1 | |
| 2 | `0x57B2` | TX | `0x200623` | 3 | |
| 3 | `0x57CC` | paired | `0x200629` | 3 | `0x2006B0` |
| 4 | `0x57E2` | TX | `0x200680` | 5 | |
| 5 | `0x57F8` | TX | `0x200614` | 3 | |
| 6 | `0x580E` | TX | `0x200617` | 3 | |
| 7 | `0x5824` | TX | `0x200670` | 6 | |
| 8 | `0x583A` | TX | `0x200678` | 6 | |
| 9 | `0x5850` | TX | `0x20064C` | 4 | |
| 10 | `0x5866` | TX | `0x200650` | 4 | |
| 11 | `0x587C` | TX | `0x200658` | 6 | |
| 12 | `0x5892` | TX | `0x200660` | 6 | |
| 13 | `0x58A8` | TX | `0x200668` | 6 | |
| 14 | `0x58BE` | TX | `0x200654` | 4 | |
| 15 | `0x58D4` | TX | `0x20061A` | 3 | |
| 16 | `0x58EA` | TX | `0x20060B` | 3 | |
| 17 | `0x58FE` | TX | image `0x9FF0` | 9 | |
| 18 | `0x5914` | TX | `0x20061D` | 3 | |
| 19 | `0x592A` | TX | `0x20060E` | 3 | |
| 20 | `0x5940` | TX | `0x200611` | 3 | |
| 21 | `0x5956` | TX | `0x200620` | 3 | |
| 22 | `0x596C` | TX | `0x20068C` | 4 | |
| 23 | `0x5982` | TX | `0x200688` | 4 | |
| 24 | `0x5998` | TX | `0x200626` | 3 | |

The direct pointer/count at step 17 initially supported classifying
`0x9FF0..0x9FF8` as referenced SPI initialization data. The subsequent
[capture helper review](CAPTURE_HELPER_REVIEW.md) establishes this as record
0 of a seven-record table, extending the supported data extent to `0xA02F`
exclusive. IDA's overlapping code items remain explicit ledger conflicts;
the rest of the surrounding region is not classified by these references.

## Timeout request and normal exit

After step 24, a nonzero `0x200AD5` causes the store at `0x59B0` of
`0xA500000D` to `0xFFFFFD00`. The
[SAM7S reset-controller definition](https://ww1.microchip.com/downloads/en/DeviceDoc/doc6175.pdf)
identifies the key `0xA5` and processor/peripheral/external reset bits in
that command. The timeout case stops the emulator at this write. It does
not simulate reset acceptance or claim that the physical CPU executes
subsequent instructions after the request.

On the non-timeout path, the code clears byte `0x2005D5`, calls
`0x59E8(1,0)`, then `0x5CF0(1,0)`. The former clears reset/state byte
`0x2005DE`, calls `0x573C(2)` to set PIOA mask `0x200`, and returns via
`0x5CB2..0x5CB9`. Only that 22-byte entry prefix and eight-byte shared
epilogue are promoted to reviewed instruction ranges here; the parser
branch beginning at `0x59FE` remains separate work. The output routine
sets `0x2005DF=0` and `0x2005D4=1`. Both ready-path cases return with a
balanced stack and preserved R4–R7.

## Execution cases and limits

| Controlled case | Observed result |
|---|---|
| Ready on every transfer attempt | 24 helper calls; normal return and reset-state postconditions. |
| First attempt at each call site unready, second ready | 48 helper calls; every retry loop exercised; normal return. |
| All attempts unready; inject timeout flag at the first failed poll | 24 failed helper calls; no PDC programming writes; reaches keyed reset request. The flag remains set and causes each later loop to advance after one failed attempt. |
| All attempts unready; no timeout writer | Still executing the first transfer's polling path at the 5,000-instruction budget; no reset request or return. |

Readiness is scripted per helper entry, and the timeout case explicitly
injects the SRAM flag. TC2 interrupt timing, PDC register effects, pin
voltage and the external device are absent. This routine does not inspect
the received three-byte buffer in its own body, and its helper-success
checks are acceptance/readiness checks rather than verified command/response
semantics. Command meanings, external device identity, complete capture
parsing, live timeout duration and reset behavior remain unresolved.

```text
PYTHONPATH=<Binary Ninja Python path> python audit/tools/decode_image_ranges.py firmware_v2.8.4HF.bin --ranges 0x575c:0x59ca:thumb2,0x59e8:0x59fe:thumb2,0x5cb2:0x5cba:thumb2 --output audit/data/spi_initialization_binaryninja.json
uv run --with unicorn==2.1.4 python audit/tools/emulate_spi_initialization.py firmware_v2.8.4HF.bin --output audit/data/spi_initialization_emulation.json
python -m unittest discover -s tests -t .
```

The source image hash is checked, and no device is accessed.
