# Alternate axis, stretch lookup and optional timer clamp

This pass adds **265 complete original `0x50F0` calls** on the exact
32,000-byte V2.8.4HF image, SHA-256
`1ae519ba6194e8f7bdaaa94333a83a9e6fda3b0563f87f7d48383b37288c1780`.
The [artifact](../audit/data/control_axis_clamps.json) records actual axis
intermediates, original stretch-helper arguments/results, lookup addresses,
clamp events and timer calls/writes. No function result is stubbed.

## Alternate axis and conditional bound

At `0x51CA`, let T be the already limited R2, D the byte at `0x200589`, and
K the byte at `0x20058D`. Instructions `0x51CA..0x51FE` compute:

```text
axis = 19                                      if T > D + K
     = 0                                       if T < K
     = floor(19*T/D) - floor(19*K/D)           otherwise, D != 0
     = 0                                       otherwise, D == 0
```

The last branch follows the original unsigned/signed runtime helpers' zero
quotient policy. The subtraction uses an unsigned division for T and signed
division for K; K is a byte, so its product 19*K is nonnegative and both
quotients follow the floors shown. Inputs and arithmetic are checked at the
actual intermediate boundary and before the following history store.

With stable input values and an intact frame, the prior byte-plus-one limiter
ensures T <= 256. D/K <= 255, so neither multiply nor D+K overflows. In the
middle branch with D > 0, `0 <= T-K <= D`; therefore the difference of floors
is in 0..19. With D == 0, admission to that branch requires T == K and both
runtime quotients are zero. The two outer branches directly return 0 or 19.
This is a conditional instruction-level bound, not a global asynchronous-writer
proof or an assumption that all input configurations are admitted by handlers.

The main matrix is 250 calls: D/K/source bytes in 0/1/10/100/255 and old
history `0x20042B` in 0/255. One extra case supplies source 255 plus word
offset 1, old history 255, D=255 and K=1. Actual T is **256**, axis is 19,
and the original byte history store narrows T to **0**. That narrowing is
documented as observed arithmetic; its later service-history consequences
are not established by this single call.

## Original stretch consumer

Each call also checks `0x4A94` against the existing
[stretch arithmetic model](../tools/model_stretch_arithmetic.py), using actual
entry arguments and fields. If its gated table read executes, the address
must equal `0x200190 + 13*row + column`. In this suite row is 0..19 and column
0..12; all observed reads remain in the initialized 260-byte stretch window.
No table bytes are overwritten by the harness. Signed-byte loading, staged
division rounding and wrapped products remain part of the model comparison.
Those sampled argument bounds do not exclude other indirect/corrupted calls.

## Directed optional timer clamp

Fourteen cases vary requested stretch over 409, 410, 411, 2729, 2730, 2731
and 5000, each with synthetic TC0 `CLKSTA` clear/set. Capture is 3200,
percent word 100, selector 10, minimum byte 100 and optional enable
`0x2006EC=1`. Original stretch-helper results equal the requested values
in this fixture; original subsequent gates reach the optional clamp.

| Input R6 | Clamped R6 | Timer argument `24*R6+3` |
|---:|---:|---:|
| 409 | 410 | 9843 |
| 410 | 410 | 9843 |
| 411 | 411 | 9867 |
| 2729 | 2729 | 65499 |
| 2730 | 2730 | 65523 |
| 2731 | 2730 | 65523 |
| 5000 | 2730 | 65523 |

The original timer helper receives the same computed argument in each clock
pair. It writes RC only with `CLKSTA` clear. Original helper arguments and
actual writes are checked separately. This tests software admission against
plain-memory status, not measured pulses, timer frequency or peripheral effects.
The clamp is conditional on earlier gates and enable; it is not a universal
bound on all timer requests.

## Coverage and remaining full-analysis requirements

All 19 previously unvisited main starts execute. Union across the initial
scalar, retention, idle, reinitialization, full-response and this suite reaches
**574/574 main-control instruction starts**. There are no unvisited starts in
that union. This milestone is instruction coverage, **not exhaustive paths,
branches, numeric states, asynchronous interleavings or firmware completion**.

Shared/global writer constraints, full parameter-to-output admission, numeric
status and nonfinite-source accounts, other subsystem integration and final
architecture/reference consolidation remain required. The full goal is active.

```sh
python audit/tools/emulate_control_axis_clamps.py firmware_v2.8.4HF.bin --output audit/data/control_axis_clamps.json
python -m unittest discover -s tests -t .
```

No device traffic, flashing or engine-setting change was performed.
