# Residual code-candidate adjudication

The exact 32,000-byte V2.8.4HF image, SHA-256
`1ae519ba6194e8f7bdaaa94333a83a9e6fda3b0563f87f7d48383b37288c1780`,
now has no remaining **IDA code-candidate bytes** in the current ledger.
At this review 1,802 data-candidate bytes remained; the subsequent
[PC-literal audit](PC_LITERAL_POOL_REVIEW.md) adjudicates them. Alternate entry
discovery, complete writer/consumer paths, interrupt interactions and subsystem
semantics remain open. A tool's code/data label is not an exhaustive execution
inventory, and complete byte classification does not close the full analysis.

The [source audit](../audit/data/residual_code_adjudication.json) checks the
residual candidates against exact bytes, prior bounded decodes and execution
reports. The reviewed instruction total becomes 19,000 bytes: 14,320 Thumb
and 4,680 ARM. Padding and tables are counted separately.

| Adjudicated bytes | Evidence and disposition |
|---|---|
| Integer runtime `0x8564..0x8678` | Six mixed Thumb/ARM spans, 270 actual instruction bytes. The three NOPs at `0x8566`, `0x8576`, `0x8586` are skipped by the `BX PC` veneers and excluded. |
| Eight USART wrappers/flag helpers | 74 Thumb bytes over the explicit ranges in the artifact. New original-byte calls check both staging wrappers, every byte value for both getters, and exact setter writes. |
| Reset-request helper `0x7434..0x743C` | Eight Thumb bytes. Offline execution writes `0xA500000D` to synthetic address `0xFFFFFD00`, then returns. The two following literal words are separately classified. |
| 38 alignment pairs | 60 NOP bytes and 16 `FF` bytes. Each pair follows an unconditional transfer in the byte-verified IDA export and has no decoded direct incoming branch. The artifact records every address and predecessor. |
| Ratio data `0x9F88..0x9FF0` | Three 28-byte rows plus five binary32 coefficients, 104 bytes total. Source words match the already executed ratio scorer's evidence. |
| Wrapper and reset literals | 20 bytes for the USART wrapper/flag helpers and eight for the reset request. Their bodies' executed loads/stores support the address values. |
| `0xA02F` | One zero byte between the 63-byte indexed SPI request table and the ADC lookup region beginning at `0xA030`. Classified as alignment. |

## Division evidence and interworking

The [integer-runtime report](INTEGER_ARITHMETIC_REVIEW.md) already executes
87,141 division calls. This pass reconciles that evidence with the instruction
manifest: the union of those calls visits all 69 non-padding instruction
starts in the bounded decode. The only decoded starts not visited are the
three veneer NOPs. Thumb entry `0x8564` transfers to ARM `0x8568`, `0x8574`
to `0x8578`, and `0x8584` to `0x8588`. Register results, including the
remainder/quotient ABI and exceptional-input behavior, remain as documented
in that earlier review. This is reconciliation of source evidence, not a new
claim of an exhaustive 32-bit proof.

## New wrapper, flag, and reset execution

The new harness performs 519 calls. Getters `0x7B04` and `0x7B10` return each
of the 256 possible source bytes unchanged as an unsigned R0 value. Helpers
`0x7B28` and `0x7B30` clear their documented flag bytes; `0x7B38` and `0x7B4C`
set their documented two-byte flag pairs. `0x7AF8` passes its pointer/count
to the original TX staging helper. `0x7B1C` replaces the supplied count with
16 before entering original RX staging. All 39 starts across those eight
bodies and `0x7434` are visited, with stack and R4–R11 checks.

The reset-request write goes only to mapped synthetic memory. The emulator
continues to the helper's return because it does not implement electrical
reset. Likewise DMA transfers, promotions and serial activity are not
implemented. These results establish original instruction behavior under the
specified memory model and preserve the hardware limitations.

The alignment finding is limited to decoded direct branches and the reviewed
surrounding code. Indirect branches and corrupted control flow could enter
other addresses; they are not disproven by a padding classification.

```sh
python audit/tools/audit_residual_code.py firmware_v2.8.4HF.bin --output audit/data/residual_code_adjudication.json
python audit/tools/build_image_ledger.py firmware_v2.8.4HF.bin
```

No connected hardware, flashing, setting changes or device traffic were used.
