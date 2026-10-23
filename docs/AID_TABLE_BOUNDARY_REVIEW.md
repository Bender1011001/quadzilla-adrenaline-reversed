# AID table boundary review

The V2.8.4HF resolvers accept AID 255 even though each pointer table contains
255 entries, indexed 0 through 254. Executing the original helpers offline
reproduces an unintended SRAM write alias and an invalid read address. This is
a confirmed in-image bounds defect. Hardware consequences and complete transport
reachability have not been demonstrated.

The source is the 32,000-byte application image with SHA-256
`1ae519ba6194e8f7bdaaa94333a83a9e6fda3b0563f87f7d48383b37288c1780`.
The [complete byte-domain map](../audit/data/aid_table_audit.json) records both
lookup addresses and pointers, profile names, and a controlled reader execution
for each of the 256 possible AID bytes. Profile names describe vendor declarations;
they do not establish implementation semantics for every nonzero pointer.

## Lookup boundary

| Resolver | Table range, end exclusive | Slots | Lookup at AID 255 | Returned pointer |
|---|---|---:|---|---|
| `0x7C1C` | `0xA91C..0xAD18` | 255 | `0xAD18`, table 2 slot 0 | `0x200BBA` |
| `0x7C68` | `0xAD18..0xB114` | 255 | `0xB114`, SRAM-code source | `0x43C02097` |

The bracketed arithmetic in both resolvers simplifies to `base + 4*AID` for
the tested byte domain. The comparisons at 75, 150, 185 and 220 select table
segments; none excludes 255. All 512 resolver executions match the corresponding
little-endian image word. For slots 0..254, table 1 contains 173 zero pointers
and table 2 contains 152. Nonzero pointers include aliases, so slot count is not
a count of distinct parameters.

`0xB114` is independently established as the source of executable code copied to
SRAM by startup. It is not an extra table-2 slot. The alias at `0xAD18` is likewise
the start of table 2, not a separate table-1 entry.

## Read and response behavior

The value reader at `0x7D80` calls the second resolver at `0x7DD8`, tests only for
a null pointer, and executes `LDRB R0,[R0]` at `0x7DE8`. This dereference happens
before the width calculation and payload-capacity checks. With one requested
AID, type 5 and controlled initialized SRAM, all 255 in-range cases return;
AID 255 attempts to read `0x43C02097` and Unicorn reports an unmapped read.
Returning in this experiment does not prove that the other AIDs are meaningful,
safe, or valid in every state.

Calling the actual response builder at `0x7EB4` with AID 255 produces the same
fault at `0x7DE8`. A comparison call for AID 85 returns status 1 and a CRC-valid
five-byte response. These calls exercise image bytes, not a reimplementation.
They begin at the helper entry with synthetic arguments. They do not establish
that a particular incoming radio frame reaches the helper under live scheduling,
nor what the MCU does on this address access. No reset, lockup, denial of service,
or engine effect is claimed.

## Write alias

With payload bytes `[255, 1]`, payload size 2 and type 1, the actual writer at
`0x7CC4` resolves AID 255 through table 1. For AIDs at or above 220 the width
selector retains the first value byte as the width; the chosen value 1 requests
one byte. `STRB R2,[R0]` at `0x7D6C` writes that byte to `0x200BBA`.
The helper returns status 1 and reports one processed AID, 255. The harness
observes `0x200BBA` changing from 0 to 1.

That address is table 2's AID-0 pointer. Its downstream control meaning and
consequences are not established here. This is a concrete alias write, not an
arbitrary-address write primitive. Normal validation and subsequent consumers
require further review before any live impact statement.

## Reproduction and checks

Obtain the exact image independently; it is not distributed here. The optional
emulator package is separate from the standard repository tests:

```bash
uv run --with unicorn==2.1.4 python audit/tools/audit_aid_tables.py firmware_v2.8.4HF.bin --output audit/data/aid_table_audit.json
python -m unittest tests.test_aid_table_boundary -v
```

The harness maps ROM read/execute and SRAM read/write only, copies the startup
initialized data, and clears the remaining SRAM before each call. It checks
normal returns and stack balance, bounds execution to the helper regions, and
records invalid memory accesses. Unicorn's ARM926 is a functional surrogate for
this instruction subset, not an ARM7TDMI bus or timing model. No peripherals or
device interfaces are mapped and no device traffic is sent.

[Bounded Binary Ninja decoding](../audit/data/aid_table_binaryninja.json)
provides instruction anchors, complementing the earlier IDA export. The decoder
is a superset of ARMv4T and its linear output also includes literal pools and
alignment; those decoded data words are not accepted as executable instructions.

The standard tests check the committed evidence, all profile-name associations,
lookup arithmetic, the faulting PC/address, the writer observation and the valid
comparison response's CRC. They do not rerun vendor bytes. Reproducing execution
requires the separate command above.

## Remaining work and corrective direction

Implementations should reject unsupported AIDs before lookup, verify each lookup
is within its table, and validate pointer/width combinations before dereferencing
or modifying storage. A bound of 255 is exclusive; IDs 0..254 still require
individual support checks. No firmware patch or device operation accompanies
this report.

The internal stretch-table question also remains open: the initial 650-byte
window `0x200190..0x20041A` has maximum byte 100 and no high-bit bytes. This
narrows the [signed-cell arithmetic concern](INTEGER_ARITHMETIC_REVIEW.md), but
does not establish the complete table extent, all later writers, or unreachable
high-bit states. Do not equate that internal window with the profile AIDs.

Baseline semantic coverage remains 42 of 145 entries, with 103 pending; this
pass deepens already reviewed helpers. Full analysis remains active.
