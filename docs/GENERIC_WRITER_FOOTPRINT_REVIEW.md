# Generic writer extents and AID-255 coefficient admission

This pass bounds copy/fill callers and resolved staging writes of `0x7CC4`,
then follows the AID-255 alias through complete original control cycles.
Evidence binds to V2.8.4HF, 32,000 bytes, SHA-256
`1ae519ba6194e8f7bdaaa94333a83a9e6fda3b0563f87f7d48383b37288c1780`.
The [footprint artifact](../audit/data/generic_writer_footprints.json) records
768 original walker calls and the entire byte-AID destination map. The
[admission artifact](../audit/data/aid255_control_admission.json) executes
three complete original `0x76CC` cycles without function stubs.

## Copy/fill callers

The direct-transfer audit identifies `0x4128 → 0x8530`, `0x413E → 0x854C`,
and `0x5F22 → 0x8530`. With original descriptors and ordinary caller state:

| Operation | Source | Destination | Bytes | End exclusive |
|---|---|---|---:|---|
| Initialized-data copy | `0x96E8` | `0x200000` | 2208 | `0x2008A0` |
| Zero fill | fill byte 0 | `0x2008A0` | 994 | `0x200C82` |
| Executable-template copy | `0xB114` | `0x200C84` | 164 | `0x200D28` |
| Accepted configuration copy | `0x10FF00` | `0x2006CC` | 44 | `0x2006F8` |

Descriptor bounds and all three records are reread from the source. The
configuration copy requires source byte `A5`; accepted contents do not change
its fixed destination/length. The gap `0x200C82..0x200C84` is outside those
operations. These are caller-specific bounds, not intrinsic helper capacity
checks or exclusion of indirect/corrupted calls. The later configuration copy
does not overlap lookup tables. The separate
[vector scratch writer](GLOBAL_STORE_INVENTORY_REVIEW.md) retains its
conditional overlap; it is not one of these generic helper calls.

## Resolved payload-data footprint

Table 1 at `0xA91C` has 82 nonzero pointers in its 255 in-bound slots.
AID 255 aliases the next word, producing `0x200BBA`. Fixed-width AIDs select
1/2/3/4 bytes by the reviewed ranges. Variable AIDs use a lookahead byte as
count. With a 14-byte payload budget and one byte needed for the AID, a
single value run can store at most 13 bytes. Each store advances the pointer;
resolving another AID resets it. With the original table and byte AIDs, every
resolved staging-data store lies in this union:

| Interval, end exclusive | AIDs 0..254 | Including AID 255 |
|---|---|---|
| `0x200AEC..0x200AF9` | yes; variable AID 226 | yes |
| `0x200B00..0x200B19` | yes | yes |
| `0x200B1B..0x200B1C` | yes | yes |
| `0x200B1D..0x200BB6` | yes | yes |
| `0x200BBA..0x200BC7` | no | yes; out-of-table alias |

All 256 AIDs have original single-value executions. All 256 count bytes are
also executed for each mapped variable AID, 226 and 255, at the maximum
payload length. Count zero still writes: decrement wraps to 255 and the
budget ends incomplete after 13 stores. Count 13 completes one 13-byte value;
count 14 writes 13 bytes and returns incomplete. The smaller-count sweep
uses unmapped-AID padding after the first value ends, so its whole-payload
status must not be mistaken for that first value's completion.

These bounds concern **resolved staging-data stores**, not report/count
outputs, stack stores, subsequent handlers or the entire receive path. They
assume the unmodified pointer table and budget. They preserve AID 226's
previously established reach to numeric status byte `0x200AF8`; they do not
establish a global exclusion of all lookup-table writers.

## Original receive-to-control path

AID 255's interval includes `0x200BC2` at offset 8 and `0x200BC3` at offset 9.
The scalar helper consumes BC2 before its automatic 0..100 normalization
producer runs. A later ratio consumes BC3 before it is refreshed from the
current source byte. The [response review](CONTROL_RESPONSE_ARITHMETIC_REVIEW.md)
establishes those arithmetic and ordering contracts. This pass reaches the
bytes through original receive code rather than directly preloading them.

The harness supplies a completed 16-byte buffer, pending flag `0x200AFD=1`
and zero UART receive count, then calls actual cycle `0x76CC` with the outgoing
gate enabled. Original ADC, capture, CRC/receive, walker, validation, control,
response and outgoing scheduling instructions execute. Registers are plain
synthetic memory; no DMA, IRQ or physical transmission occurs.

Scalar settings use reviewed handler ranges: coefficient 20, subtraction
percentage 0 and knots 1280 (scaled raw settings 100). Other source/calibration
globals are controlled, not a reconstructed live history. BC2/BC3 initially
contain 7/3; selected raw capture is 4095 and the current source byte is 80.
The aliased value sets its offsets 8/9 to 200/240.

Each case first executes the prior integration runner's controlled fixture
call, then applies these overrides. Its retained first-filter history contains
one 9999 sample. The tested cycle appends 30 in the CRC-negative case or
2403 in the aliased cases, giving `(9999+30)>>5 = 313` and
`(9999+2403)>>5 = 387`. That history is part of the explicit fixture, not an
assumed live vehicle state.

| Case | CRC | Declared count | Receive status at validation gate | Alias stores | BC2 consumed | BC3 consumed | Stored telemetry | Filtered response average |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| Negative control | bad | 13 | 4 | 0 | 7 | 3 | 1041 | 313 |
| Complete value | valid | 13 | 1 | 13 | 200 | 240 | 1280 | 387 |
| Short value | valid | 14 | 2 | 13 | 200 | 240 | 1280 | 387 |

Incomplete status does not roll back already stored data. The original cycle
calls control after ingest regardless of that status. AID 255 has no selected
validation handler to repair the alias; the status-1 case reaches the default
continuation. This does not bypass CRC: the damaged frame has no alias stores.

At cycle return, automatic producers have restored BC2/BC3 to 100/80 in all
three cases. Those later writes do not undo the scalar result or changed
filter history. Scalar return/cap/knot/flag state, telemetry, response bytes,
derived word and both filter buffers agree with the existing independent
models. Exact frame bytes and alias stores are recorded in the artifact.

The result is a completed-buffer, in-image computational input alias, including
an incomplete-value path. It is confined to a fixed interval, not an arbitrary
address primitive. Physical delivery, pairing/authentication, live source
ranges, UART/DMA ordering, waveforms and engine effects remain unproven.

## Scope and corrective direction

The AID-255 boundary finding now has this concrete original-cycle consumer
account. Copy/fill bounds remain tied to identified direct callers; payload
bounds assume the original table and 14-byte budget. Other writers, indirect
calls, corruption and asynchronous state still require their own accounts.
The full firmware goal remains active.

A correction should reject out-of-table IDs before either lookup, allow only
writable parameters, validate width/capacity before stores, and define staging
isolation or rollback for incomplete values. CRC validity does not supply
those checks. No firmware patch or device operation accompanies this report.

```sh
python audit/tools/audit_generic_writer_footprints.py firmware_v2.8.4HF.bin --output audit/data/generic_writer_footprints.json
python audit/tools/emulate_aid255_control_admission.py firmware_v2.8.4HF.bin --output audit/data/aid255_control_admission.json
python -m unittest discover -s tests -t .
```

No device traffic, host flash operation, firmware-file modification or engine
setting change was performed.
