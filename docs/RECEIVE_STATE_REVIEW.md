# Completed-buffer receive dispatcher

This review applies to the exact 32,000-byte V2.8.4HF application image,
SHA-256 `1ae519ba6194e8f7bdaaa94333a83a9e6fda3b0563f87f7d48383b37288c1780`.
The [bounded decode](../audit/data/receive_state_binaryninja.json) covers
the two actual Thumb spans `0x8038..0x809B` and `0x80A2..0x81A1`: **356
instruction bytes and 162 starts**. All 162 agree with ordinary IDA item
boundaries and are visited by 14 [original-byte controlled cases](../audit/data/receive_state_emulation.json).
The intervening six bytes at `0x809C..0x80A1` are a type-switch table,
verified separately in the [layout artifact](../audit/data/receive_state_layout.json).
The `FFFF` alignment at `0x81A2..0x81A3` and `0x2007C8` state-base literal
at `0x81A4..0x81A7` are data, not executable instructions.

## Buffer and admission path

Inputs R0 and R1 are respectively the output AID-list buffer and its
one-byte count pointer. The dispatcher tests the receive-pending byte at
`0x200AFD` via `0x7B10`. A clear byte returns zero. When set, it saves the
completed-buffer pointer from `0x2007E8`, toggles that pointer between
`0x2007F0` and `0x200800`, calls `0x7B1C` to rearm receive hardware, and
checks the completed frame's CRC with `0x7BCC`. The parser continues only
for CRC status 3. Bad CRC returns 4. These observations require a completed
buffer and pending flag; the emulator supplies both and maps USART registers
as passive memory.

The type is the header's high nibble. At `0x8094..0x809A`, the routine
rejects values over 5 and indexes six unsigned bytes, then branches to
`0x809E + 2*offset`:

| Type | Table byte | Target | Dispatch action |
|---:|---:|---:|---|
| 0 | `1D` | `0x80D8` | Parse, copy at most 14 AIDs to state `+0x58`, set count `+0x24`, arm flag `+9` when the parsed count is nonzero. |
| 1 | `02` | `0x80A2` | Parse and return its result to the caller. |
| 2 | `31` | `0x8100` | Require list-A flags `+0x11/+0x12`; parse and filter current list A against parsed AIDs. |
| 3 | `02` | `0x80A2` | Share type-1 parse path. |
| 4 | `0A` | `0x80B2` | Parse, copy at most 14 AIDs to state `+0x48`, set count `+6`, arm flag `+7` when nonempty. |
| 5 | `57` | `0x814C` | Require list-B flags `+0x16/+0x17`; parse and filter current list B against parsed AIDs. |

Types 1/3 return the parser's status. Type 0/4 can return parser status 2
while queuing response work; type 2/5 return the parser status after filtering.
The guarded type-2/5 cases return 3 before parsing when either required
flag is zero. A CRC-valid type 6 is rejected by the type gate and returns
3 in the controlled case. The meanings of these numeric statuses are
local control-flow observations, not proof of a documented wire protocol.

For type 2, if filtering leaves `+0x14` zero, the routine clears latch
`+0x12`, calls `0x7B30` to clear `0x20070C`, and may clear `+0x11` and set
flag `+1` according to `+4/+3`. Type 5 mirrors this with `+0x19`, latch
`+0x17`, helper `0x7B28`/`0x20070E`, and flags `+0x16/+5/+2/+0`;
that completion branch assigns return code 6. The controlled cases visit
both conditional chains. Full interrupt and scheduler interplay is still
needed to explain when each flag combination arises on hardware.

## Count provenance and limitations

This routine writes bounded response-list counts `+6/+0x24` for type 4/0
through `0x7FD8`. It reads and may filter working counts `+0x14/+0x19`
on type 2/5. It does not directly populate the outgoing *source* counts
`+0x13/+0x18` (`0x2007DB/0x2007E0`). The
[outgoing scheduler](OUTGOING_STATE_REVIEW.md) passes those separate fields
to the frame builder, which rewrites them to deferred counts. An audit of
indirect producers and callers outside these two routines remains necessary
before treating the direct-call stack-boundary cases as physically reachable
or impossible.

The 14 cases execute exact image bytes in an ARM926 functional surrogate.
They cover no-pending, types 0–5, guarded and armed acknowledgments,
completion flags, bad CRC, type 6 and the alternate buffer. They do not
measure USART/PDC DMA, interrupt timing, Bluetooth delivery or board V2.2
behavior. No traffic was sent to the hardware.

```text
PYTHONPATH=<Binary Ninja Python path> python audit/tools/decode_image_ranges.py firmware_v2.8.4HF.bin --ranges 0x8038:0x809c:thumb2,0x80a2:0x81a2:thumb2 --output audit/data/receive_state_binaryninja.json
python audit/tools/audit_receive_jump_table.py firmware_v2.8.4HF.bin --output audit/data/receive_state_layout.json
uv run --with unicorn==2.1.4 python audit/tools/emulate_receive_state.py firmware_v2.8.4HF.bin --output audit/data/receive_state_emulation.json
python audit/tools/build_image_ledger.py firmware_v2.8.4HF.bin
python -m unittest discover -s tests -t .
```
