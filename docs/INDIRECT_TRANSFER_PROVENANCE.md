# BX provenance and other computed PC writes

This audit continues the [execution-discovery pass](EXECUTION_DISCOVERY_REVIEW.md)
for the exact V2.8.4HF image, SHA-256
`1ae519ba6194e8f7bdaaa94333a83a9e6fda3b0563f87f7d48383b37288c1780`.
It uses the accepted 19,000 instruction bytes plus 138 instruction bytes in
the copied Thumb helper source. The [artifact](../audit/data/indirect_transfer_provenance.json)
records a target-source disposition for every one of the 203 decoded `BX`
sites, including the 60 sites left for context in the prior pass.

| BX form | Sites | What the source establishes |
|---|---:|---|
| LR return-form | 140 | Target is the current LR register, including conditional ARM returns. Incoming calling/exception state and frame integrity still matter. |
| Stack-restored return-form | 38 | The immediately preceding Thumb instruction pops exactly the selected register, which `BX` then consumes. |
| Fixed numeric veneer | 16 | A PC-relative literal supplies a documented, aligned ARM numeric entry, directly through R3 or through R12 while restoring R3. |
| Fixed startup/reset transfer | 4 | An ARM literal supplies a documented Thumb initializer, main continuation, or reset helper. |
| ISA interworking veneer | 3 | Thumb `BX PC` reaches the adjacent aligned ARM body, skipping a NOP. |
| AIC-selected callback | 2 | Target comes from the AIC FIQ or IRQ vector state. Its runtime value is not a fixed literal. |

This resolves the local register source, not every possible runtime target.
No new independent source entry is established. The supported minimum remains
157, and global writer/consumer and subsystem work remains open.

## Return forms and numeric veneers

For each stack-restored case, the audit checks the raw single-register `POP`
encoding immediately before `BX`. It records the source site and selected
register. This establishes a return-shaped stack transfer; it does **not**
prove the popped word is intact or exclude the conditional stack overwrites
already documented in frame/queue reviews. A return classification is not a
memory-safety or complete ABI proof.

The sixteen numeric veneers match the literal targets in the original-byte
[floating-point execution report](../audit/data/soft_float_emulation.json).
Twelve load R3 and branch through it. Four save R3, load the target, copy it
to R12, restore R3 and branch through R12. The audit checks the load encoding,
literal address/value, restoration sequence, target alignment and accepted ARM
instruction start. The artifact lists every veneer and target.

Thumb `BX PC` sites `0x8564`, `0x8574`, and `0x8584` reach ARM `0x8568`,
`0x8578`, and `0x8588`, respectively. Their skipped NOPs remain outside the
instruction accounting, as established in the [residual audit](RESIDUAL_CODE_ADJUDICATION.md).

## Startup, exception, and AIC transfers

| BX site | Target or source | Calling context |
|---|---|---|
| `0x4050` | Literal `0x414D` selects Thumb `0x414C` | Hardware initialization; preceding `MOV LR,PC` supplies the continuation. |
| `0x407C` | Literal `0x4115` selects Thumb `0x4114` | Memory descriptors; preceding `MOV LR,PC` supplies the continuation. |
| `0x4088` | Literal `0x77B9` selects Thumb `0x77B8` | Main continuation; LR is loaded with stop loop `0x408C`. |
| `0x40F4` | Literal `0x7435` selects Thumb `0x7434` | Exception fallback reset request; preceding `MOV LR,PC` supplies a nominal continuation. Electrical reset is not modeled. |
| `0x4030` | R0 loaded at `0x4020` from `[R8+0x104]` | FIQ dispatch. Expected address is `0xFFFFF104` when startup's banked FIQ R8 is `0xFFFFF000`. |
| `0x40BC` | R0 loaded at `0x40A8` from AIC address `0xFFFFF100` | IRQ dispatch. The base is loaded from literal `0x4100 = 0xFFFFF000`. |

The [startup review](STARTUP_VECTOR_CLOCK_REVIEW.md) establishes the vector
roots and banked-register initialization. The dynamic AIC values depend on
programmable vector state, installed handlers, interrupt context and ordering.
This local provenance audit does not claim a complete finite set of values
that those two reads can return.

The subsequent [AIC installation review](AIC_VECTOR_INSTALLATION_REVIEW.md)
composes the selected original initialization segments and records their
programmed vectors, including slot 31 remaining untouched. It retains the
dynamic selection and global-writer limits above.

## Other computed PC writes

The raw encoding scan finds six additional PC-writing instructions in the
accepted source. It recognizes high-register Thumb ADD/MOV PC and POP PC,
ARM LDR PC, LDM including PC, and data-processing PC destinations, while
excluding BX and status-register/test instructions.
No software-interrupt instruction is found in these accepted spans.

| Site | Source operation | Supported disposition |
|---|---|---|
| `0x4040` | `SUBS PC,LR,#4` | FIQ exception return using exception state. |
| `0x40DC` | `LDM SP!,{PC}^` | IRQ exception return using the saved frame/status. |
| `0x4B80` | `ADD PC,R1` | First capture-scalar dispatch: 29 byte-table cases. |
| `0x4C30` | `ADD PC,R1` | Second capture-scalar dispatch: 10 byte-table cases. |
| `0x608A` | `ADD PC,R7` | AID handler dispatch: 218 signed-halfword table slots; out-of-range default is handled before this operation. |
| `0x809A` | `ADD PC,R1` | Receive-type dispatch: six indexed byte-table cases. |

The audit re-reads all dispatch offsets from the image, compares them with the
existing [capture-scalar](CAPTURE_SCALAR_REVIEW.md),
[AID dispatch](AID_DISPATCH_SELECTOR_UPDATES.md), and
[receive-state](RECEIVE_STATE_REVIEW.md) artifacts, and verifies each target is
an accepted Thumb start. Their index guards and ordinary-state assumptions
remain those established by the referenced audits. Exception returns require
valid saved status and stack/LR state; table validation does not establish
interrupt nesting or stack integrity.

Remaining discovery work concerns programmable vector values, synthesized or
mutated pointers, alternative ISA interpretations, physical/remap aliases,
and the data windows retained by the preceding pass. Full parameter paths,
global writers and subsystem integration remain separate completion requirements.

```sh
python audit/tools/audit_indirect_transfers.py firmware_v2.8.4HF.bin --output audit/data/indirect_transfer_provenance.json
```

No connected hardware, device traffic or settings were used.
