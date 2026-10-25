# Reset continuation and main-loop state dispatcher

This review applies to the exact 32,000-byte V2.8.4HF application image,
SHA-256 `1ae519ba6194e8f7bdaaa94333a83a9e6fda3b0563f87f7d48383b37288c1780`.
The [bounded Binary Ninja decode](../audit/data/main_loop_binaryninja.json)
covers `0x77B8..0x7A3E`: 646 Thumb bytes and 307 instruction starts, with no
decode gap. IDA has one continuous function partition and 305 code items.
Two of its displayed items combine neighboring halfwords: at `0x77BE/77C0`,
the actual instructions are `MOVS R1,#0x98; LSLS R1,R1,#1`, yielding
`0x130`; at `0x786C/786E`, they are `MOVS R1,#0xF0; LSLS R1,R1,#7`,
yielding `0x7800`. These are presentation differences, not different bytes.
The [source-bound count-writer inventory](../audit/data/main_loop_count_writers.json)
records the exact boundaries, stores and direct references.

## Reset continuation

The startup sequence branches to Thumb `0x77B8` after RAM initialization;
the caller's LR leads to a fallback self-loop. This function pushes R4–R7/LR
and has no returning epilogue. It initializes R5 once to the state block at
`0x200788`, performs AIC/PIO setup and invokes several helpers. Its first
loop writes `0xFFFFFFFF` to the same address, `[word[0x200798]+0x130]`, ten
times; the loop does not increment that address. The later setup calls
include the copied-to-SRAM helper at `0x200CFC`, PIO setup `0x74E8`,
initializer `0x4384`, and several other distinct callees. Their downstream
effects must be read from their own reviews. The loop waits until
`0x200718` becomes nonzero, calls `0x760C` and stores its returned byte at
`0x200790`, then enters the repeated dispatcher at `0x78E4`. The wait is a
software condition; actual interrupt delivery and elapsed time are not
established here.

## Dispatcher and state bytes

The byte at `0x200790` selects states 1, 2 and 3. Any other value enters
the PIO reinitialization path at `0x786C`. State 1 enables the cycle gate
at `0x200792`, checks PIOA data status, and either calls control cycle
`0x76CC` or moves through the pin/flag branch. That branch can clear the
state to zero or set it to two. State 2 also sets `0x200792`; it compares
the halfword at `0x200794` with `word[0x2008A8]`, checks software flags,
and either calls `0x76CC` or moves to state 3. State 3 either calls
`0x76CC`, returns to state 1, or clears the state depending on its pin and
`0x200718` checks. The PIO writes in this path are **command-register
writes**; synthetic register memory does not model their physical effects.

The [original-byte bounded runs](../audit/data/main_loop_dispatch_emulation.json)
start at `0x78E4` with R4=0, R5=`0x200788`, R6=1 and R7=`0xFFFFF434`,
which are the main-loop register values after setup. Eight synthetic cases
exercise state values 0–3 and selected pin/flag combinations. Their union
visits 157 of the 307 decoded main-loop starts. The harness stops on the
next dispatcher iteration or immediately before `0x76CC` or `0x74E8`.
It therefore does not execute reset initialization or those callees.

| Synthetic case | Observed boundary | State afterward |
|---|---|---:|
| State 0 | Before PIO reinitialization `0x74E8` | 0 |
| State 1, PIO bit 28 clear | Before control cycle `0x76CC` | 1 |
| State 1, bit 28 set, default flags | Next iteration | 0 |
| State 1, bit 28 set, flags `0x2006DF/DE=1` | Next iteration | 2 |
| State 2, default flags | Next iteration | 3 |
| State 2, hold byte `0x200715=1` | Next iteration | 3 |
| State 3, bit 28 clear | Before control cycle `0x76CC` | 3 |
| State 3, bit 28 set | Next iteration | 0 |

These cases establish reachable *instruction paths under supplied memory*.
They do not show that those pin states or software flags occur on a board.
The state-2 branches that call `0x76CC` remain statically traced but were not
entered in this bounded campaign. A gate byte at `0x200792` is set in states
1 and 2; the [cycle review](CYCLE_QUEUE_SELECTION_REVIEW.md) explains how
`0x76CC` consumes related queue state.

## Five telemetry-list count bytes

R5 has one explicit assignment in the bounded body (`0x77C6`) and no later
local reassignment. The 15 direct stores through R5 touch offsets 0, 1, 7,
8, 10 and 12–13. None touches offsets 2–6, the initialized count bytes
`0x20078A..0x20078E`. The byte-verified IDA export has five direct
references to those addresses, all `LDRB` instructions at
`0x7700/771E/773E/775E/777A` in the five-list selector `0x76CC`.
None of the eight bounded dispatcher cases wrote a count byte.

This **narrows the writer search**; it does not prove the counts cannot
change. IDA cross-references do not enumerate computed aliases, an interrupt
can act between loop instructions, and subordinate calls can hold or derive
state-block pointers. The conditional cross-slot read for a synthetic count
above eight in the [five-list review](CYCLE_QUEUE_SELECTION_REVIEW.md)
therefore remains a conditional finding, with ordinary-path reachability
unresolved. No hardware traffic was sent.

```text
PYTHONPATH=<Binary Ninja Python path> python audit/tools/decode_image_ranges.py firmware_v2.8.4HF.bin --ranges 0x77b8:0x7a3e:thumb2 --output audit/data/main_loop_binaryninja.json
python audit/tools/audit_main_loop_count_writers.py firmware_v2.8.4HF.bin --output audit/data/main_loop_count_writers.json
uv run --with unicorn==2.1.4 python audit/tools/emulate_main_loop_dispatch.py firmware_v2.8.4HF.bin --output audit/data/main_loop_dispatch_emulation.json
python audit/tools/build_image_ledger.py firmware_v2.8.4HF.bin
python -m unittest discover -s tests -t .
```
