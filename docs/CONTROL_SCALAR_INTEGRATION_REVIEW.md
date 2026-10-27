# Complete control calls and scalar-input provenance

This pass executes entry `0x50F0` from its actual prologue through its actual
return, including the original helpers reached by each case. It uses the
exact V2.8.4HF 32,000-byte image, SHA-256
`1ae519ba6194e8f7bdaaa94333a83a9e6fda3b0563f87f7d48383b37288c1780`.
The [execution artifact](../audit/data/control_scalar_integration.json) records
325 calls, compact results for every case, detailed examples, observed global
writes and unvisited main starts. No helper result is replaced by a stub.

The checks compare the integrated scalar call with the
[32-bit contract](SCALAR_TELEMETRY_REVIEW.md), including cap/flag/knot effects
and the actual caller telemetry store. They check both table extents, timer
admission, retained-selector return and counter/backdown dispatch. Other
response calculations execute and their writes are recorded, but do not yet
have complete independent models or physical-unit accounts.

## Scalar table indices

The scalar table at `0x200000` is distinct from the capture table at
`0x200294`. The scalar helper indexes it as `20*row+column`. Its only decoded
direct caller constructs the axes as follows, assuming stable input state
across repeated loads and an intact frame:

```text
V = (byte[0x2005DB] + word[0x2008A4]) mod 2^32
D = byte[0x200589]
P = word[0x2005F0]

row    = 19                 when V > D
       = floor(19*V/D)      when V <= D and D != 0
       = 0                  when V == D == 0 (runtime quotient policy)

column = floor(19*P/100)    when P <= 100
       = 19                 when P >= 101
```

At `0x519E`, the caller stores V at `0x20044C`. Instructions
`0x51AA..0x51C8` build local `SP+8` from V and D. The division branch has
V at most D, which is at most 255; `19*V` cannot overflow and its quotient
is at most 19. When D is zero, that branch can only have V zero; the original
unsigned helper returns quotient zero for denominator zero. All other values
take the direct 19 branch. Overflow while forming V does not invalidate this
argument: the comparison uses the already wrapped V.

Instructions `0x5200..0x5220` build local `SP+0xC` from P. In the division
branch P is at most 100, bounding the product and quotient. The argument
setup pushes the low byte of local `SP+8` at `0x5246`, making it the scalar
helper's fifth argument, **row**. It loads local `SP+0xC` into R3 at
`0x5248..0x524C`, making it **column**. These axis roles differ from the
later `0x4B38` table call.

Under those assumptions, the scalar byte lies inside
`0x200000..0x200190` (exclusive end). The 400 initialized bytes come from
`0x96E8..0x9878`, have values 0..100 with no high bits set, and hash to
`1d0a99ad623d85b30f25f4c150901116955243fd126c8998dd2826cc10699bbc`.
This describes initial contents, not an exhaustive later-writer bound.

**Concurrency condition:** `0x5202` reads P for the comparison, and `0x5210`
reads it again before multiplication. The bound requires a stable value
between those reads, or a separate asynchronous-writer invariant. Interrupt
interleavings are not modeled here. The same condition applies to the
[capture-table row proof](CAPTURE_TABLE_BOUNDS_REVIEW.md), which shares this
local value. This is not evidence that an interrupt actually violates it.

## Whole-routine execution and assumptions

Every call starts from the exact initialized-data copy and zeroed remaining
synthetic SRAM, followed by explicit controlled overrides. The matrix varies
capture word `0x2005EC` across 26 boundary/high-word values, word `0x2005F0`
across `0,1,50,100,101,0xFFFFFFFF`, and TC0 `CLKSTA` clear/set: 312 calls.
Thirteen further cases probe zero denominator, byte maxima, wrapped V,
counter boundaries, nonzero mode, disabled scalar arithmetic and a high-bit
base word. All case specifications are retained in the artifact.

Fixed overrides include working selector `0x2006CD=5`, cap `0x200580=11`,
step/offset `0x200433/434=10/0`, ready `0x200431=1`, warmup enable
`0x2006CF=0`, stretch bytes `0x20058A/B/C=10/0/50`, and stretch words
`0x200590/594=1700/10000`. The old equality-count word `0x200448`, slew byte
`0x20042B`, refresh and high-idle enable `0x2006E2` are zeroed. The reproducer
defines the other source/base/counter, denominator, mode and enable overrides.
These direct SRAM assignments do not establish normal parameter admission
or complete-startup reachability.

The suite observes **197 calls** to TC0 helper `0x6FA0`: all **105 calls**
with synthetic `CLKSTA` clear write their passed R1 value to `0xFFFA001C`;
the other 92 make no RC write. This checks software admission under
plain-memory registers, not timer behavior or pulse width. Earlier gates
that skip the helper are distinct from helper-level blocks. Both table-load
sites, when reached, read one byte inside their respective 400-byte extents.
All calls preserve SP and R4–R11 and return the retained selector.

## Counter and periodic backdown

The comparison at `0x5100..0x5106` is **signed** against 1,000,001. An old
value at least that signed threshold is replaced with zero, then incremented
and stored. A negative signed old word is not reset there; increment still
wraps to 32 bits. The signed division at `0x5226` tests the remainder modulo
250; zero calls `0x499C` and writes its return byte to AID 13 response
`0x200BCD`. This is an iteration counter without a measured time base.

| Controlled old counter | Stored counter | Backdown call |
|---|---:|---|
| 249 | 250 | yes |
| 999,999 | 1,000,000 | yes |
| 1,000,001 | 1 | no |
| `0xFFFFFFFF` | 0 | yes |
| `0x80000000` | `0x80000001` | no |

These are checked inside complete original control calls, without asserting
that every old counter occurs in normal service.

## Coverage and remaining work

The later [reinitialization extension](CONTROL_REINITIALIZATION_REVIEW.md)
explicitly enables and executes the setup call with additional peripheral
pages. The base suite retains its default rejection and original scope.

The later [retained-sample review](CONTROL_RETENTION_BRANCH_REVIEW.md) adds
120 calls and twelve previously unvisited starts. The union of these two
suites is 507/574; the original suite's counts below remain its own coverage.

The suite visits **495 of 574 main starts** and lists the other 79 explicitly.
It is not full branch/path coverage. Reinitialization at `0x74E8` is rejected
if reached; no case reaches it. Its omission is not hidden behind a return
stub. Other setup, fresh-idle, response-scaling and gate combinations remain
integration work. Global writers, stable-value invariants under interrupts,
all response scales, live state reachability and physical semantics remain
open. No entries or instruction-byte classifications are added by this pass.

```sh
python audit/tools/emulate_control_scalar_integration.py firmware_v2.8.4HF.bin --output audit/data/control_scalar_integration.json
python -m unittest discover -s tests -t .
```

No connected hardware, device traffic, flashing or settings change was used.
