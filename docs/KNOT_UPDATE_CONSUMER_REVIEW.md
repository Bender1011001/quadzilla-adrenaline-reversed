# Knot update, consumer mutation and same-value reapplication

This review composes the original `0x601C` parameter handlers, complete
`0x50F0` control calls and `0x7D80` response reads in the exact V2.8.4HF image,
SHA-256 `1ae519ba6194e8f7bdaaa94333a83a9e6fda3b0563f87f7d48383b37288c1780`.
The [execution artifact](../audit/data/knot_update_consumers.json) records
306 sequences: 1,224 complete control calls, 918 ingest calls and 3,060
single-AID response-reader calls. All checked state transforms and reader
payloads agree with the stated contracts. Detailed examples retain ordered
knot/raw/echo/flag writes and their instruction addresses.

**Boundary:** `0x8038` is replaced with an explicit receive-result contract
that supplies an AID list and success status. Staging is preloaded. The
original dispatcher, selected handlers, control calculations and readers
execute; packet framing, transport admission and interrupts do not. This
establishes a composed local update/consumer path, not a live-device finding.

## Three distinct representations

The [handler review](REMAINING_AID_UPDATE_REVIEW.md) establishes that each
knot handler reads an unsigned staged halfword, caps it at 300, stores that
raw value as a working word and echo halfword, then computes a second
working word `floor(128*raw/10)` for the scalar consumer:

| AID | Staged halfword | Raw working word | Scaled knot word | Echo halfword |
|---:|---|---|---|---|
| 137 | `0x200B28` | `0x2005B4` | `0x200458` | `0x200BF5` |
| 138 | `0x200B2A` | `0x2005B8` | `0x20045C` | `0x200BF7` |
| 139 | `0x200B2C` | `0x2005BC` | `0x200460` | `0x200BF9` |
| 140 | `0x200B2E` | `0x2005C0` | `0x200464` | `0x200BFB` |
| 141 | `0x200B1E` | `0x200584` | `0x200468` | `0x200BEB` |

Consequently these handlers produce scaled knots in 0..3840. Values such as
`0xFFFFFFFF` used in earlier arithmetic probes are not produced by this
handler transform. That is a writer-specific bound, not an exclusion of all
other writers or corruption. The five handlers do not enforce monotonicity
between knots, and do not themselves set refresh byte `0x200426`.

The [scalar calculation](SCALAR_TELEMETRY_REVIEW.md) has another writer:
on the active nonzero-mode path, it clamps these **scaled words in place**
to `384,512,640,768,896`. The stores are at
`0x4DB6/0x4DC2/0x4DCE/0x4DDA/0x4DE6`, respectively. It does not revise the
raw working words or echoes there. For a freshly handled integer setting,
the first raw values that exceed those scaled ceilings are
`31,41,51,61,71`, respectively.

## Composed sequence and retained state

Each sequence runs one controlled fixture control call using the setup from
the [control integration review](CONTROL_SCALAR_INTEGRATION_REVIEW.md).
The following phases preserve SRAM and restore only the external return link:

1. Update all five knot AIDs plus AIDs 17/59/61/62 with zero values for those
   four scalar settings. The latter handlers store zero response bytes and
   set refresh `0x200426=1`.
2. Execute the complete control routine. The scalar refresh check finds all
   four response bytes zero, selects mode 1, clears refresh, and clamps the
   five scaled knots on its active path.
3. Update AID 17 to 1 through its original handler. It sets its response
   byte and refresh flag. The next complete control call selects mode 0;
   it **retains** the scaled knots reduced by the preceding call.
4. Read all five AIDs with the original response reader. They report the
   capped raw settings, without reconstructing the current scaled words.
5. Reapply exactly the same five staged knot settings. Their unconditional
   handler stores restore the scaled words from the raw settings. A complete
   mode-0 control call retains the restored words; repeated original reader
   calls still report the same raw settings.

The common-value sweep covers every staged integer 0..300, plus 301 and
65535 to exercise the handler cap. Three additional vectors are alternating
0/300, alternating 300/0, and the five exact ceiling-equivalent values
`30/40/50/60/70`. This is not an exhaustive Cartesian product of five
halfword inputs. Each control call also executes the earlier scalar-model,
caller-store and table-index checks through the shared integration runner.

## Concrete history-dependent result

With all five staged settings equal to 100, capture word 2000 and the
documented fixture state:

| Phase | Raw working / echo values | Scaled knots | Stored telemetry `0x200604` |
|---|---|---|---:|
| After handler updates | all 100 | all 1280 | not sampled as a new control result |
| After mode 1, then mode 0 | all 100 | 384 / 512 / 640 / 768 / 896 | 1024 after the mode-0 call |
| After same-value reapply and mode 0 | all 100 | all 1280 | 1268 |

The AID 137 reader payload is `89 64 00` before and after reapplication.
For all settings equal to 300, the corresponding scaled values start at
3840, reduce to the same five ceilings, and restore to 3840. The tested
mode-0 telemetry changes from 1024 to 3828 while reader payload remains
`89 2C 01` for AID 137. Every knot's own reader is checked, not just AID 137.

This is a **confirmed local history dependency in scaled consumer state**.
Raw echoes remain consistent with the handler's raw-setting representation;
they do not expose the intervening scaled-word mutation. Intended mode
semantics, application behavior, transport reachability and physical impact
are not established by this sequence, so no live defect severity is assigned.

## Conditional arithmetic bounds and remaining writer work

For knots just produced by these handlers, or subsequently reduced by the
nonzero-mode consumer, every scaled knot remains at most 3840. The scalar
helper sets its cap to 3840 on bypass/nonzero mode, or to K5 on active zero
mode. Thus, with these writers and stable cap state, the original unsigned
cap followed by the signed floor stores telemetry in **1024..3840**, even
if intermediate arithmetic wrapped. This bounds this composed path; it does
not prove the global `0x200604` writer set or exclude asynchronous changes.

Other reviewed scalar handlers provide separate local bounds: AID 17 caps
its coefficient at 30, AID 59 at 50, AID 60 at 100, and AID 61's raw cap of
80 gives derived word at most 1024. These bounds must be attached to their
writers rather than assumed for every SRAM state. Persistence/default paths,
alternate raw-staging consumers, complete table writers and interrupt ordering
remain part of the global provenance work. The full analysis stays active.

```sh
python audit/tools/emulate_knot_update_consumers.py firmware_v2.8.4HF.bin --output audit/data/knot_update_consumers.json
python -m unittest discover -s tests -t .
```

No hardware, device traffic, flash or engine-setting change was used.
