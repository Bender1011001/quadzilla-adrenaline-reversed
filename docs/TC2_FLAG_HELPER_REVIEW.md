# Two TC2-triggered SRAM flag helpers

This review covers Thumb entries `0x7F28` and `0x7F40` in the exact
32,000-byte V2.8.4HF application image, SHA-256
`1ae519ba6194e8f7bdaaa94333a83a9e6fda3b0563f87f7d48383b37288c1780`.
The [bounded decode](../audit/data/tc2_flag_helper_binaryninja.json) contains
48 instruction bytes, while the [original-byte execution artifact](../audit/data/tc2_flag_helper_emulation.json)
records SRAM writes for both sides of each gate. There are no peripheral
accesses in either helper.

## Source and caller relationship

Both helpers load the same SRAM base `0x2007C8` from image literals:
`0x7F28` uses a word at `0x81A4`; `0x7F40` uses `0x8034`. Each word is
`0x2007C8` in the exact image. The baseline call graph names `0x6C94` as the
caller of both. Its instruction sequence calls `0x7F40` at `0x6CDA` after
incrementing the word at `0x200754` when byte `0x20070C` is set, and calls
`0x7F28` at `0x6CFA` after incrementing `0x200758` when byte `0x20070E`
is set. Both paths compare the *previous* counter value against literal
`0x3E9` (1001). These caller sites establish reachability from the larger
routine; the full `0x6C94` contract is still under review.

## Exact helper effects

Each case starts with a controlled zeroed `0x2007C8..0x2007DF` SRAM window,
with the listed gate byte set to 0 or 1. Writes are in instruction order.

| Entry | Always writes | Additional writes when gate is nonzero |
|---|---|---|
| `0x7F28` | `0x2007CA=1`, `0x2007DF=0` | If `0x2007CD` is nonzero: `0x2007C8=1`, `0x2007DE=0`. |
| `0x7F40` | `0x2007CB=1`, `0x2007DA=0` | If `0x2007CC` is nonzero: `0x2007C9=1`, `0x2007D9=0`. |

Both bodies end in `BX LR` and make no further calls. The stores express
software flag transitions. The names of these flags, elapsed real time, and
effects of the larger callback are not established by these 48 bytes.

## Reproduction

```text
PYTHONPATH=<Binary Ninja Python path> python audit/tools/decode_image_ranges.py firmware_v2.8.4HF.bin --ranges 0x7f28:0x7f40:thumb2,0x7f40:0x7f58:thumb2 --output audit/data/tc2_flag_helper_binaryninja.json
uv run --with unicorn==2.1.4 python audit/tools/emulate_tc2_flag_helpers.py firmware_v2.8.4HF.bin --output audit/data/tc2_flag_helper_emulation.json
python -m unittest discover -s tests -t .
```

The tools require the exact image hash and use only local memory. No firmware
image is redistributed and no device is accessed.
