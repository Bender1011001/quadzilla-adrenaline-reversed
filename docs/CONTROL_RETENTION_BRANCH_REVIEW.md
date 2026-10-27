# Retained-sample counter and optional timer floor

This extension executes 120 complete original `0x50F0` calls on the exact
32,000-byte V2.8.4HF image, SHA-256
`1ae519ba6194e8f7bdaaa94333a83a9e6fda3b0563f87f7d48383b37288c1780`.
The [artifact](../audit/data/control_retention_branches.json) retains every
override, counter snapshot, optional-branch event and timer admission result.
No function return is stubbed. Existing scalar-model, table-extent, preserved
register, stack and timer-write checks run for every call.

## Retained samples

Instructions `0x55BA..0x55DC` read old counter `0x200448`, compare retained
capture `0x20043C` with current `0x2005EC`, and compare retained source
`0x200440` with current `0x200600`. Both equalities and unsigned capture at
least 601 are required to increment. Otherwise the counter becomes zero.
Increment is a wrapping 32-bit addition. The subsequent comparison is unsigned
against 2001; crossing that threshold calls setup `0x74E8`.

The fixture varies capture over 600, 601, 2000, 3200 and 4000; old counter over
0, 1, 1999 and `0xFFFFFFFF`; and both-equal, capture-mismatch and source-mismatch
conditions. Current source is zero in every executed case. The counter model
is checked against actual memory before the threshold comparison. In particular,
1999 becomes 2000 and returns without setup; `0xFFFFFFFF` becomes zero and
also avoids setup. These are controlled old states, not established live histories.

The epilogue refreshes the two retained words from their current sources in all
120 calls. This counter is separate from iteration counter `0x200470` and has
no measured time base. Old count 2000 with matching qualifying samples is not
included: the inherited runner rejects setup rather than faking its return.
Setup reachability and its complete caller effects remain follow-up work.

## Optional timer paths

Each case runs with optional bytes `0x2006EC` and `0x200ADD` both zero or both
one. Setting the former admits `0x536A` in 24 calls (the 3200/4000 capture
cases). The instruction account clamps unsigned R6 to 410..2730 before the
`24*R6+3` timer request. All 24 observed inputs are below 410 and become 410;
the in-range and upper-clamp branches are not exercised by this matrix.
The artifact checks actual R6 at `0x5382` against the clamp calculation.

With synthetic timer clock status clear, original `0x6FA0` writes the passed
value to RC. Existing timer checks compare calls and writes. The enabled
`0x200ADD` cases also visit `0x539E..0x53A0`, the conditional byte-flag store
to `0x200725`. These are software admission observations, not measured pulses.

The entry override of `0x20042D` does **not** cause the idle-helper branch at
`0x52F0` to execute. It is retained in the artifact as an attempted entry-state
variation; this pass makes no claim that it proves that branch unreachable.
Its producer and earlier gate behavior need a separate account.

The subsequent [idle integration review](IDLE_CONTROL_INTEGRATION_REVIEW.md)
supplies that earlier-gate account and reaches the original branch, including
persistent transition/fresh-consumption ordering. This suite's original
non-admission observation remains valid for its disabled/nonzero-selector fixture.

## Coverage and limits

Twelve previously unvisited main starts execute. Union with the original
325-call integration suite reaches **507/574** main starts, leaving 67 explicitly
listed. This union is only for those two suites, not a recomputation across
all repository harnesses or exhaustive path coverage. The new suite has 120
calls and zero checked-model differences.

All cases start from initialized SRAM and explicit overrides. No input-admission,
interrupt, DMA, hardware timing or physical-output claim follows. Response
instructions execute, but this extension does not independently validate every
response result. Global writer bounds and normal-service state reachability
remain open. The full firmware-analysis goal remains incomplete.

```sh
python audit/tools/emulate_control_retention_branches.py firmware_v2.8.4HF.bin --output audit/data/control_retention_branches.json
python -m unittest discover -s tests -t .
```

No device traffic, flashing or engine-setting change was performed.
