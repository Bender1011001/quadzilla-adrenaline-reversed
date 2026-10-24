# Table-2 response reader, frame builder and queue-copy bound

This account applies to the exact 32,000-byte V2.8.4HF application image,
SHA-256 `1ae519ba6194e8f7bdaaa94333a83a9e6fda3b0563f87f7d48383b37288c1780`.
The [bounded decode](../audit/data/frame_reader_binaryninja.json),
[original-byte campaign](../audit/data/frame_reader_emulation.json) and
[byte model](../tools/model_frame_reader.py) cover four Thumb entry bodies:
`0x7C68..0x7C9D`, `0x7D80..0x7E63`, `0x7EB4..0x7EFB`, and
`0x7FD8..0x8009`. They add **404 instruction bytes** and 198 decoded starts.
IDA agrees with 197 individual boundaries. At `0x7FD8`, IDA combines the
preceding `FFFF` with the first `B430` Thumb halfword and displays an
invalid ARM7TDMI `VSRI.32` item. The
[boundary adjudication](../audit/data/frame_reader_boundary.json) records
the source words, seven decoded direct calls, explicit Thumb decode and
original-byte execution; the preceding `FFFF` remains unclassified.
One branch at `0x7FEE`
is statically decoded but unreachable from the normal `0x7FD8` entry,
which returns earlier on a zero count; 197 starts were executed.

The adjacent nine words at `0x7CA0..0x7CC3` are a shared resolver
literal pool. They contain table addresses
`AD18`, `AE44`, `AF70`, `AFFC`, `B088` and four negative index offsets
`FFFFFED4`, `FFFFFDA8`, `FFFFFD1C`, `FFFFFC90`. The reviewed table-2
instructions at `0x7C6E`, `0x7C7A..0x7C94` read the pool; four offset
words are also referenced by the previously reviewed table-1 resolver.
The two bytes at
`0x7C9E..0x7C9F` remain outside the accepted instruction and data ranges.

## Local contracts

| Entry | Inputs | Result and effects |
|---|---|---|
| `0x7C68` | R0 byte AID | Return its table-2 pointer. The address expression indexes the 255-slot table at `0xAD18`; AID 255 reads the next word beyond that table, as previously documented. |
| `0x7D80` | R0 output payload; R1 type; R2 mutable AID list; R3 pointer to list count | Return output payload length. For types 2/4, copy listed AID bytes. For other types, resolve table-2 values and copy `AID,value` pairs while they fit. Unmapped or nonfitting AIDs are rewritten to the front of R2 and their count replaces `*R3`. |
| `0x7EB4` | R0 frame buffer; R1 type; R2 mutable AID list; R3 count pointer | Write header, reader output and CRC. Return 1 when no AIDs are deferred, else 2. It uses the low four bits of `payload_length+1` for the header; there is no independent initial-count bound here. |
| `0x7FD8` | R0 destination; R1 count pointer; R2 source; R3 requested count | For nonzero destination and count, copy `min(R3,14)` bytes and write that count to `*R1`. With a null destination or zero count, return without changing `*R1`. |

The reader's output budget is 14 bytes. It tests
`(current_length + value_width + 1) mod 65536 < 15` before copying a
value pair. For types 2/4 it copies AID bytes directly. Type and AID
arguments are narrowed to bytes at their use sites. A nonzero table-2
pointer supplies both the value bytes and, for AIDs 220 and above, a
variable width from its first byte. All mapped table-2 entries in this
image are below AID 220; AIDs 220..254 are null. AID 255's aliased
pointer is invalid in the synthetic memory map and was recorded as a
separate local fault, not as a measured device exception.

The bounded campaign executes **4,328** reader/builder calls across every
AID 0..254, types 1/2/4/5, repeated lists of length 0..14 and 2,048
seeded mixed lists. Another 257 calls sweep the `0x7FD8` count argument
0..255 and a null destination. All bounded results match the byte model.
For example, a synthetic AID 9 type-1 reply is `13 09 76 64`; AID 226
with a null table-2 pointer yields empty frame `11 EB`, status 2, and
retains AID 226 in the deferred list. CRC bytes are verified from the
same source-bound CRC function reviewed earlier. The synthetic values
and frame type do not establish a live protocol exchange.

## Direct-call rejection-list capacity

The reader allocates 16 bytes at `SP+0x10..SP+0x1F` for deferred AIDs,
then appends to it without checking the deferred count. With 17 null
AIDs supplied directly in `*R3`, original instruction `0x7E30` writes
to `SP+0x20`, overlapping saved registers. At 21 it overwrites the saved
list pointer's first byte; at 22 it overwrites its second byte and the
subsequent copy faults on an unmapped synthetic address at PC `0x7E48`.
The [artifact](../audit/data/frame_reader_emulation.json) records cases
14, 15, 16, 17, 20, 21 and 22 and the actual stack-store addresses.

This proves a missing intrinsic bound for direct calls with oversized
rejection lists. The examined `0x7FD8` helper caps each copy to 14,
and a parsed incoming frame can carry at most 14 AIDs. The complete
provenance of every state count passed by the larger `0x81A8` outgoing
state machine remains to be reviewed. Therefore this is a conditional
local memory-safety defect; reachability through physical receive or
ordinary state transitions is not established. The synthetic fault
does not prove a target crash, code execution or engine effect.

## Remaining path work

The outbound queue filter `0x7F58`, the whole `0x81A8` state machine,
its count producers, transmit scheduling and USART/PDC effects still
need instruction-level review. The full firmware-analysis goal remains
incomplete. No device traffic was sent.

```text
PYTHONPATH=<Binary Ninja Python path> python audit/tools/decode_image_ranges.py firmware_v2.8.4HF.bin --ranges 0x7c68:0x7c9e:thumb2,0x7d80:0x7e64:thumb2,0x7eb4:0x7efc:thumb2,0x7fd8:0x800a:thumb2 --output audit/data/frame_reader_binaryninja.json
uv run --with unicorn==2.1.4 python audit/tools/emulate_frame_reader.py firmware_v2.8.4HF.bin --output audit/data/frame_reader_emulation.json
python -m unittest discover -s tests -t .
```
