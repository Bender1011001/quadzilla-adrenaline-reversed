# Counter-triggered peripheral setup inside original control

This pass executes the formerly rejected `0x55E4 → 0x74E8` call inside the
complete original control routine. Source is V2.8.4HF, 32,000 bytes, SHA-256
`1ae519ba6194e8f7bdaaa94333a83a9e6fda3b0563f87f7d48383b37288c1780`.
The [artifact](../audit/data/control_reinitialization.json) records 32 returned
calls and one instruction-budget wait. No function result is stubbed.

## Admission and original setup sequence

The fixture supplies matching retained/current capture 2000 and source zero.
Old equality count `0x200448` varies over 1999, 2000, 2001 and `0xFFFFFFFF`.
After wrapping increment, unsigned count at least 2001 calls setup. Thus old
1999 returns with count 2000; old 2000/2001 invoke setup; old `0xFFFFFFFF`
wraps to zero and does not invoke it. These are supplied sample histories,
not normal-service or duration claims.

Ready cases vary PIO bit 17, USART command-register reads 0/`0xFFFFFFFF`, and
old byte `0x200424` over 0/255. SPI status is explicitly `0x30` and PIO status
is `0x800 | (pin17 << 17)`. Peripheral pages are reset between cases. Registers
are plain emulator memory; write-one command semantics are not implemented.

All 16 triggered ready cases execute the original coordinator and its six
subordinate initializers in this order:

```text
0x74E8 → 0x6FB4 → 0x6BD8 → 0x575C → 0x4330 → 0x725C → 0x800C
          TC       SPI      CAN/SPI    ADC      USART    comms
```

The artifact retains all **221 non-stack writes** within setup for each of
these cases, with instruction sites, widths and values. The six calls execute
their original subordinate helpers too. PIO bit 17 produces its established
opposite byte at `0x200791`. Setup leaves the watched lookup region
`0x200000..0x200424` unchanged in every returned triggered case; hashes are
checked before and after setup. This does not exclude changes before/after
that interval or by other writers.

Setup itself writes TC0 RC at `0x7018` with `0x1B`. That initializer store is
recorded separately from normal timer helper `0x6FA0`'s RC admission check.
The original check remains applied to the helper's stores; the extension
does not mistake initialization for an extra admitted timer request.

## Caller continuation and blocked readiness

After setup returns to `0x55E8`, the caller increments byte `0x200424` with
eight-bit narrowing, then clears equality count `0x200448`. The tested old
bytes 0/255 become 1/0. Both retained source words are subsequently refreshed
by the original epilogue. All 32 ready calls return with balanced stack and
preserved R4–R11; existing scalar-model, table and timer checks also run.

The negative case uses old count 2000 and SPI status zero. It enters setup,
executes TC/SPI setup and reaches `0x575C`, then repeatedly executes readiness
helper `0x6B48` and its transfer caller. With no interrupt-driven timeout
progression, the 100,000-instruction budget stops at `0x6B4C`. The setup return
and three later initializers are not reached. Count remains 2001 and byte
`0x200424` remains zero. This is a bounded emulator wait, not proof of a real
permanent hang: the TC2 timeout mechanism is intentionally not advancing.

## Coverage and remaining scope

Six additional main-control starts execute. Union with the initial scalar,
retention and idle integration suites reaches **526/574**, leaving 48 listed
starts. Complete original setup now executes in this caller context under the
recorded ready conditions. Other status combinations, live event histories,
interrupt interleavings, DMA completion and physical output effects remain
unverified. The wider firmware-analysis goal remains active.

The base integration runner still rejects reinitialization by default. Only
this explicit extension enables it and supplies the additional peripheral pages.

```sh
python audit/tools/emulate_control_reinitialization.py firmware_v2.8.4HF.bin --output audit/data/control_reinitialization.json
python -m unittest discover -s tests -t .
```

No device traffic, flashing, firmware-file modification or engine-setting change
was performed.
