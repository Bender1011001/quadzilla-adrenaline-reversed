# Outgoing AID-list filter and count boundary

This account uses the exact 32,000-byte V2.8.4HF application image,
SHA-256 `1ae519ba6194e8f7bdaaa94333a83a9e6fda3b0563f87f7d48383b37288c1780`.
The [explicit Thumb decode](../audit/data/queue_filter_binaryninja.json)
and [original-byte campaign](../audit/data/queue_filter_emulation.json)
review the complete `0x7F58..0x7FD5` body: 126 instruction bytes,
63 starts. Every start agrees with an ordinary IDA item boundary and
executes in the bounded campaign.

## Filter contract

R0 points to a mutable current AID list, R1 to its one-byte count,
R2 to a comparison list, and R3 supplies that list's count. For nonzero
R0 and R3, the helper caps R3 at 14, scans each current AID against the
first R3 comparison bytes, retains those absent from the comparison list
in original order, copies them back to R0, updates `*R1`, and returns
the retained count. Duplicate current AIDs are preserved when absent.
The [independent model](../tools/model_queue_filter.py) matches 4,549
bounded calls with current counts 0..14, comparison counts including
0, 1, 14, 15 and 255, seeded mixed byte lists, and a null R0 case.

The zero-count behavior is specific: if R0 is null **or R3 is zero**,
the helper sets `*R1=0` and returns zero, even when the current list was
nonempty. It does not interpret an empty comparison list as “retain all.”
This may be intentional queue-reset behavior; the caller state semantics
still need review.

## Direct callers and state fields

The [source-bound callsite audit](../audit/data/queue_filter_callers.json)
records four direct calls:

| Call | Current list and count | Comparison input | Locally established source |
|---|---|---|---|
| `0x8126` | `0x200860`, count `0x2007DC` | parsed AID list and count | receive dispatcher type-2 path |
| `0x8172` | `0x200880`, count `0x2007E1` | parsed AID list and count | receive dispatcher type-5 path |
| `0x83C4` | `0x200860`, count `0x2007DC` | outgoing list at `0x200850`, count from `0x2007DB` | larger outgoing state machine |
| `0x84EC` | `0x200880`, count `0x2007E1` | outgoing list at `0x200870`, count from `0x2007E0` | larger outgoing state machine |

All four count fields have zero in the image's startup RAM template.
The reviewed queue copier `0x7FD8` writes at most 14 to `0x2007DC`
and `0x2007E1` in the inspected outgoing branches; the filter cannot
increase a valid current count. Parsed lists from the normal 16-byte
receive frame carry at most 14 AIDs. These observations support a
bounded path for the inspected producers. The complete set of writes
to `0x2007DB/0x2007E0` and the full `0x81A8` state transitions remain
unresolved, so the normal-state invariant is not yet a whole-image proof.

## Local stack boundary

The helper uses 16 bytes at `SP+4..SP+19` for retained AIDs but does
not cap the initial `*R1` or the retained count. A direct synthetic call
with 17 unmatched AIDs stores at `SP+20`, overlapping saved R0. A call
with 18 reaches an unmapped synthetic write at PC `0x7FC0` after that
saved pointer changes. The [artifact](../audit/data/queue_filter_emulation.json)
records original stores and return/fault states for counts 14, 16, 17,
18, 19 and 20. This is a conditional local memory-safety defect.
Physical receive reachability, target exception behavior and engine
effects have not been established.

The full receive and outgoing state machines, indirect writers of queue
counts, transmit scheduling and peripheral effects remain required for
the firmware goal. No device traffic was sent.

```text
PYTHONPATH=<Binary Ninja Python path> python audit/tools/decode_image_ranges.py firmware_v2.8.4HF.bin --ranges 0x7f58:0x7fd6:thumb2 --output audit/data/queue_filter_binaryninja.json
uv run --with unicorn==2.1.4 python audit/tools/emulate_queue_filter.py firmware_v2.8.4HF.bin --output audit/data/queue_filter_emulation.json
python audit/tools/audit_queue_filter_callers.py firmware_v2.8.4HF.bin --output audit/data/queue_filter_callers.json
python -m unittest discover -s tests -t .
```
