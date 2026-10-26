# Remaining PC-relative literal pools

The [source audit](../audit/data/remaining_literal_audit.json) adjudicates the
last 1,802 data-candidate bytes in the exact V2.8.4HF image, SHA-256
`1ae519ba6194e8f7bdaaa94333a83a9e6fda3b0563f87f7d48383b37288c1780`.
There are 447 referenced words (1,788 bytes) in 58 extents and seven two-byte
`FF` alignment pairs (14 bytes). Every address, word value, source-slice hash,
and accepted-code load site is recorded in the artifact.

The [image ledger](../audit/data/image_coverage_ledger.json) now assigns a
supported instruction, data, alignment or erased-space role to all 32,000
bytes. Its instruction total remains 19,000. This completes the current byte
classification pass; it does not establish exhaustive entry discovery or
complete firmware semantics. The full-analysis goal remains active.

## Instruction evidence

The [audit script](../audit/tools/audit_remaining_literals.py) walks only the
explicit accepted ARM/Thumb instruction spans in the review manifest. It
checks the image, manifest, decoder artifacts and byte-verified IDA export
against the same source hash. It derives each target directly from the raw
instruction encoding:

| Accepted load | Literal target |
|---|---|
| Thumb immediate word `LDR Rd,[PC,#imm]` (`opcode & 0xF800 == 0x4800`) | `align_down(site+4,4) + 4*imm8` |
| ARM immediate, pre-indexed, non-writeback word `LDR Rd,[PC,+/-imm]` | `site+8 +/- imm12`, according to U bit |

The ARM check excludes stores, byte loads, register-offset and post-indexed
forms. All 447 candidate words have at least one such load from accepted
code. Shared constants retain all discovered load sites. The audit also
checks that no decoded direct branch targets a newly accepted literal extent.

This proves use as a literal word, including constants that happen to resemble
instructions. It does not automatically assign the loaded value a pointer,
unit, parameter meaning or reachable downstream effect. A loaded address may
still need a writer/consumer account, and an indirect branch or alternate
entry requires its own investigation.

## Alignment disposition

The remaining two-byte pairs are at `0x499A`, `0x59CA`, `0x74B2`, `0x7BCA`,
`0x7C1A`, `0x7D7E`, and `0x854A`. Each is exactly `FF FF`, follows an
unconditional transfer in the byte-verified source export, and has no decoded
direct incoming branch. The artifact records its preceding instruction.
This supports alignment in the reviewed control flow; corrupted or indirect
entry is not excluded by the classification.

The largest accepted extents belong to the AID handler/continuation pools,
default initializer, main-loop continuation and peripheral initialization.
Their literal identity is now explicit even where complete interpretation of
the value or all downstream paths remains open. No unresolved byte category
is being used to represent those semantic questions; they remain requirements
in the [full-analysis progress document](FULL_ANALYSIS_PROGRESS.md).

```sh
python audit/tools/audit_remaining_literals.py firmware_v2.8.4HF.bin --output audit/data/remaining_literal_audit.json
python audit/tools/build_image_ledger.py firmware_v2.8.4HF.bin
```

No connected hardware, flashing, settings or device traffic were used.
