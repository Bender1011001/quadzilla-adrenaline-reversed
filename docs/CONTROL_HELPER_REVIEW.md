# Control helper contracts and state transitions

Eight additional baseline entries now have instruction-level contracts backed
by original-byte execution. Semantic coverage is 50 of the historical 145
entries, with 95 pending. The separately adjudicated six additional source
starts remain outside that baseline. Full analysis is incomplete.

The [instruction-range manifest](../audit/data/reviewed_instruction_ranges.json)
accepts 888 bytes through the eight returning epilogues. Literal pools and
alignment following those helpers are excluded. The full-image ledger consumes
this manifest and retains all other instruction ranges as pending until they
receive their own supported byte-level disposition.

The exact source image is V2.8.4HF, 32,000 bytes, SHA-256
`1ae519ba6194e8f7bdaaa94333a83a9e6fda3b0563f87f7d48383b37288c1780`.
[Per-entry records](../audit/data/control_function_reviews.json) document inputs,
outputs, side effects, callers/callees, confidence and limitations. They describe
storage and arithmetic without assigning unmeasured physical units.

## Arithmetic and filtering

| Entry | Contract | Checked calls |
|---|---|---:|
| `0x495C` | `floor(100*min(u32(R0),4095)/4095)` | 5,125 |
| `0x497C` | `floor(19*normalize(R0)/100)`, capped at 19 | 5,125 |
| `0x4650` | shift 32 words left, append R1, return wrapped unsigned sum shifted right 5 | 260 |
| `0x4674` | same 32-word filter contract | 260 |

Normalization is unsigned: values with the high bit set are capped to 4095,
rather than treated as negative. Every integer input 0..4096 was executed for
each normalization entry, together with boundary values and 1,024 seeded
32-bit samples. At `0x497C`, the percentage truncates before the second multiply.
For input 216, the actual result is 0; a collapsed `floor(19*216/4095)` gives 1.
Input 4094 yields index 18, while 4095 yields 19.

Both filters drop the oldest word, retain the next 31 and append the new sample.
They sum in 32 bits and apply a logical right shift, without saturation. An
all-`0xFFFFFFFF` retained/input set returns `0x07FFFFFF`, not `0xFFFFFFFF`.
This establishes an arithmetic contract, not a reachable overflow defect.
In the reviewed caller, `0x4674` uses the buffer at `0x200480` and its new input
is capped to 9,999; `0x4650` uses `0x200500` with a byte input. Those new-input
bounds alone do not establish the initial contents or all possible buffer writers.

`0x50F0` calls `0x497C` at `0x5112` for an index and `0x495C` at `0x5422`
for a percentage stored at `0x200BC2`. Fourteen decoded direct-call contexts
for all eight helpers are recorded in
[the caller artifact](../audit/data/control_helper_callers.json). This is a
direct-call inventory, not a proof of all indirect entry paths or runtime order.

## Three-byte threshold state at `0x4698`

For unsigned input R0 below 6, the helper writes 1 to `0x200AD6` and leaves
`0x200AD7`/`0x200AD8` unchanged. Its result is the original input if `AD8` is
zero, or 1 if `AD8` is nonzero. For input at least 6, it clears `AD6` and `AD8`,
sets `AD7` to 1, and returns 0. Thus the result is not simply a Boolean
`input < 6`. The 774 executions cover all byte inputs and two high-bit 32-bit
inputs with three initial `AD8` values.

The main loop passes the result of `0x46D0` to this helper at `0x55B2` and
stores its result at `0x200BCF`. The physical meaning of those flags remains
pending review of the preceding floating-point calculation and other flag users.

## Persistent latch at `0x47B0`

The state bytes at `0x20042F..0x200432` are described here as
`[threshold, latched, ready, edge]`; these are local descriptive names.

For a nonzero mode argument, the helper clears the last three bytes and sets
the threshold to 120, or to `0x2006D0` if `0x2006CF` is nonzero. It returns 0.
For mode zero, it reads the signed word at `0x2005F4`, the selector at
`0x2006CD`, the enable byte at `0x2006CF`, the limit at `0x2006D0` and the
counter at `0x20044C`:

- It sets `ready` if disabled, if selector equals 1, or if
  `max(source,0) >= limit` and the counter is below 15.
- If the signed source exceeds the stored threshold and `latched` is zero,
  it sets both `latched` and `edge` to 1.
- Otherwise it retains those state bytes. It returns `ready`.

Neither test clearing can be inferred from a later source falling below its
threshold; the mode reset or another writer is needed. The 480 checked calls
include negative sources, threshold crossings, counter 14/15, reset calls and
both initially clear and already-latched states. Several callers pass reset mode;
their scheduling and any interrupt interactions still require a full account.

## Fresh-sample accumulator at `0x48E8`

The accumulator is word `0x200478`; its previous delta is word `0x20047C`.
With fresh flag `0x20071E` zero, the helper returns the old accumulator without
clamping it or changing the previous delta and three flag bytes. It still writes
the unchanged accumulator back to storage.

With a fresh flag, it clears that flag and sets `0x20071C`/`0x20071D` to 1.
It computes `delta = u32(1200 - word[0x2005EC])`. If byte `0x20042D` is nonzero
and argument R1 is zero, it computes:

```text
candidate = u32(old + trunc_signed(delta / 40) + delta - previous)
result = 0 if candidate's high bit is set, otherwise min(candidate, 650)
```

If that gate fails, the result is zero. Every fresh call stores the new delta
as `previous`, including gated-off calls. The signed division and each wrap are
preserved in the model. The 896 executions include fresh/stale cases, both gate
values, inhibit values, clamp boundaries and seeded wide-word samples. The
0..650 bound applies to the fresh result, not arbitrary stale storage.

## Default initializer at `0x4384`

This helper writes fixed working values, curve bytes, echo storage and derived
scalars. The recorded call captures all 103 non-stack writes with their PCs,
sizes and values. Selected verified defaults include word `0x200590 = 1800`,
word `0x200594 = 3400`, bytes `0x200433/434 = [10,0]`, and the six words at
`0x200458..0x20046C = [1920,2304,2688,2944,3200,256]`. These last words are
derived by multiplying defaults by 128 and dividing by 10.

It is called during startup and from the AID-24 dispatch case when staging byte
`0x200B34` equals `0x55`. The latter association is supported by the dispatch
instruction trace; a live command was not sent. The helper does not write the
internal stretch window at `0x200190`, so its curve bytes up to 150 must not be
used as proof that high-bit stretch cells are reachable.

No semantic return value is assigned: its epilogue pops the return address into
R0 before `BX R0`. The emulation checks normal return and documented writes,
not a C return-value contract.

## Evidence and reproduction

The [execution artifact](../audit/data/control_helper_emulation.json) records
12,921 calls across the eight entries, representative outputs, visited addresses
and the initializer's writes. The companion
[bounded Binary Ninja decode](../audit/data/control_helper_binaryninja.json)
supplies explicit Thumb entry ranges. Linear decoding of literal pools or
alignment remains tool output, not accepted code classification.

```bash
uv run --with unicorn==2.1.4 python audit/tools/emulate_control_helpers.py firmware_v2.8.4HF.bin --output audit/data/control_helper_emulation.json
python audit/tools/build_control_callers.py
python audit/tools/build_image_ledger.py firmware_v2.8.4HF.bin
python -m unittest tests.test_control_helpers -v
```

The harness verifies R4..R11 preservation, stack balance, allowed execution
ranges and permitted data-write ranges. ROM is read/execute, SRAM is read/write,
and no peripherals or device interfaces are mapped. Unicorn ARM926 is a
functional surrogate, not ARM7TDMI timing or bus emulation. Models are bounded
contracts for synthetic helper calls, not proof that every input can occur in
the main loop. Standard tests exercise models and committed evidence; rerunning
the original bytes requires the independently obtained vendor image.

Remaining work includes the floating-point path at `0x46D0`, every writer of
the reviewed globals, reset/interrupt scheduling, internal table mutability and
the remaining 95 baseline entries. No engine setting, flash or hardware I/O was
performed.
