# Startup, exception entries and persistence helpers

The counts below describe this pass. The subsequent [USART0 review](USART0_BUFFER_REVIEW.md)
raises baseline semantic coverage to 36 roles and reduces its pending queue to 109.

This continues the active full-image analysis. It establishes six additional
source execution entries, giving **at least 151 supported source starts** when
combined with the historical 145-entry catalog. Runtime copies are aliases, not
extra source functions. The baseline still has 124 entries awaiting semantic
review; more entry candidates may emerge.

Evidence: [entry adjudications](../audit/data/entry_adjudications.json),
[explicit-mode Binary Ninja ranges](../audit/data/startup_persistence_binaryninja.json),
and the byte-verified [IDA item export](../audit/data/ida_image_items.json).
All bind to the same V2.8.4HF image hash. Analysis changes below do not patch the
original firmware or assume the earlier IDA mode flags were correct.

## Startup sequence and ABI

At `0x4044`, ARM code initializes SP to `0x204000`, then calls the Thumb hardware
initializer at `0x414C`. It sets FIQ-mode R8 to `0xFFFFF000`, allocates an IRQ stack
beginning at `0x204000`, reserves `0x60` bytes before setting the supervisor stack,
and calls `0x4114` for initialized data, zero fill and the executable RAM copy.
It branches to Thumb `0x77B8`, with LR pointing to the self-loop at `0x408C`.
Actual SRAM density and stack high-water marks remain hardware questions.

`0x414C` writes clock/watchdog/flash-mode registers and installs fallback AIC
handlers. The constants are verified instructions; exact oscillator frequency and
every configuration field have not yet been reconstructed. Its outputs include
changed peripheral state; it preserves the caller's R4 and returns through LR.

`0x4114` takes no explicit arguments: descriptor bounds are literal addresses.
Its helper at `0x8530` takes destination/source/byte-count in R0/R1/R2, copies
forward, and preserves R4. The helper at `0x854C` takes destination/fill/count in
R0/R1/R2 and fills bytes. Both require suitable valid memory ranges; the copy does
not implement overlap-safe backward movement. Neither waits on an external event.

## Newly adjudicated exception and reset entries

| Entry | Mode and input state | Behavior and output | Limits |
|---|---|---|---|
| `0x401C` | ARM, FIQ-vector execution; banked registers and exception LR active | Saves incoming R0 in banked R9, loads handler through `[R8+0x104]`, switches mode for callback, then performs exception return | Depends on startup's R8 and valid AIC handler; complete nesting analysis remains |
| `0x4090` | ARM, target of IRQ vector `0x4018` | Adjusts exception LR, saves SPSR and registers, loads AIC vector, calls handler, writes end-of-interrupt address and restores status | IRQ timing and nested-handler behavior unmeasured |
| `0x40EC` | ARM, target of five exception-vector branches | Calls Thumb helper via pointer `0x7435` | Reset-request fallback, not a proven safe return path if reset fails |
| `0x7434` | Thumb; no explicit argument | Writes `0xA500000D` to reset-controller address `0xFFFFFD00`, returns via LR | A keyed request is proven; electrical reset outcome is not measured |

The existing self-loop entries `0x408C`, `0x40E0`, `0x40E4`, and `0x40E8` are
stop/fallback loops, with no memory stores in the single branch instruction.
They are distinct from the reset-request path.

## Flash-controller interpretation

The [Microchip SAM7S datasheet](https://ww1.microchip.com/downloads/en/DeviceDoc/doc6175.pdf),
sections 19.2.4–19.3, identifies command `0x01` as page programming and `0x0F` as
setting the security bit. Registers at `0xFFFFFF60/64/68` are mode, command and
status. Security activation restricts external debug/programming access; clearing
it requires hardware erase, which erases flash. These are documented chip-family
semantics, not a measurement of the installed tuner's state or exact part suffix.

At `0x77E4`, normal startup calls runtime alias `0x200CFC` (source `0xB18C`). The
helper writes `0x5A00000F`, waits for status bit 0 and returns status masked by
`0x10`. Therefore this image **attempts to set the security bit during startup**.
Successful execution on the owner's device has not been observed. Do not infer
that JTAG access is currently available or unavailable from this static trace.

## Page-write helper and callers

Source `0xB124`, runtime `0x200C94`, takes R0 destination address, R1 byte count,
and R2 source pointer. It stages words and issues command
`0x5A000001 | ((((address - 0x100000) mod 2^32) >> 7) << 8 & 0x3FF00)`.
It polls ready, then returns 0 or 1 based on status mask `0x0C`.

Its copy loop treats the count as signed, writes a whole word while the remaining
count is positive, and stops after 128 word writes. Thus nonmultiples of four
round upward and negative register values stage nothing. Even a zero count still
reaches command construction. These are preconditions to check at every caller;
they do not establish a reachable defect or successful flash programming.

`0x6B20` calls ready helper `0x200C84`, saves/masks interrupt state through
`0x7498`, calls the writer, then restores interrupt state through `0x74B4`.
The initialized pointer at SRAM `0x200798` is AIC base `0xFFFFF000`; the two wrappers
use offsets `0x110`, `0x124` and `0x120`, retaining the saved value at `0x20079C`.
Other interrupt effects and concurrent callers still need review.

The wrapper does not preserve the writer's R0 result across the restore-helper
call: `0x74B4` loads the saved interrupt mask into R0. Callers must not be assumed
to receive the writer's 0/1 status. Whether any caller relies on that value is
still an open data-flow question.

`0x73E4` compares a word at address `0x4` with the application's word at physical
`0x104004` adjusted by `0x1000`. If different, it copies 128 bytes from address zero
to RAM `0x200000`, replaces words 1–5 with similarly adjusted application words,
and calls `0x6B20` with destination zero and length 128. This is a conditional
vector-page rewrite path; it does not replace the reset word or prove the missing
bootloader's entire behavior. The alias/remap state requires further review.

## Runtime ISA correction

At `0x8564`, `0x8574` and `0x8584`, Thumb `BX PC` switches to ARM bodies beginning
four bytes later. Explicit ARM decoding of `0x8578` yields `PUSH {R2,R3}` and
ordinary ARM instructions. Decoding that body as Thumb produces misleading
instructions and gaps. These observations explain part of the old runtime-region
disassembly failure; the full arithmetic library and other mode transitions still
need instruction-level review.

## Verification and remaining work

`tests/test_startup_persistence.py` checks source/runtime alias arithmetic, distinct
entry starts, branch/command anchors, explicit mode boundaries, signed count
behavior and page-selector wrap. The model is pure arithmetic, not a flash driver
or a CPU emulator. No hardware traffic was sent.

Next: map every persistence caller, identify its address/count/source bounds,
correct the rest of the ARM runtime region, and reconstruct interrupt scheduling
and peripheral configuration. The full firmware-analysis goal remains incomplete.
