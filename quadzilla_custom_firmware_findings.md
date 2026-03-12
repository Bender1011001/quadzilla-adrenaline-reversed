# Quadzilla Custom Firmware — What We Learned, Evidence, and What We Can Really Do

This document consolidates the reverse-engineering findings from the provided Quadzilla update assets and decompiled code, explains the true nature of the core “state machine,” and identifies concrete, feasible customizations you can perform on the firmware payloads today. All statements are backed with exact code/file references and external specs where appropriate.

Executive takeaways:
- The large “state machine” function is a bzip2 decompressor implementation, not an ECU fueling-table builder.
- The Windows updater executable (ADR9802v2.8.4.exe) contains and processes the compressed payload (overlay.bin); the analyzed decompiled functions are part of the PC-side toolchain semantics rather than the microcontroller’s runtime logic.
- The present evidence does not expose the microcontroller’s true fueling calculation path; however, it does expose how to decode/modify/re-encode the payload content, which includes calibration tables or images used by the device.
- Feasible immediate customizations include extracting and modifying calibration tables or payload assets, then re-packing them (bzip2) without tripping integrity checks as bzip2 has built-in CRC; no standalone CRC-8 lookup tables are present in overlay.bin.
- Adding a new live input dimension (TPS) to fueling in the device’s runtime would require patching the microcontroller program (not just the payload), for which we currently lack confirmed MCU-side disassembly.

Contents:
- 1) Evidence: The “State Machine” Is A bzip2 Decompressor
- 2) Roles of Key Helper Routines
- 3) What overlay.bin Is and How It’s Packed
- 4) What We Can Do Right Now with Custom Firmware
- 5) What Would Be Required to Add TPS-Based Fueling Logic
- 6) Practical Workflow (Decode → Modify → Repack → Validate)
- 7) Appendix: Scripts, Headless Ghidra Outputs, and Cross-Checks
- 8) Sources and References

==================================================

1) Evidence: The “State Machine” Is A bzip2 Decompressor

The critical function previously suspected to be a custom state machine that “builds fueling tables” is actually parsing the bzip2 format. The signature of bzip2 streams is unambiguous:
- bzip2 header starts with ASCII “BZh”, followed by a digit ‘1’..‘9’ indicating block size.
- bzip2 blocks contain a fixed 6-byte magic “0x314159265359” which corresponds to the string “1AY&SY” in ASCII and appears in block headers.
- bzip2 uses bit-level streams, Huffman-coded symbol tables, move-to-front (MTF), and the Burrows–Wheeler transform (BWT).

We see these exact markers and behaviors in the decompiled function:
- Checks for ‘B’, ‘Z’, ‘h’ in sequence:
  - ‘B’ test: [decomp_FUN_00427401.c](decomp_FUN_00427401.c:130)
  - ‘Z’ test: [decomp_FUN_00427401.c](decomp_FUN_00427401.c:151)
  - ‘h’ test: [decomp_FUN_00427401.c](decomp_FUN_00427401.c:172)
- Then reads a character and enforces ‘0’..‘9’ as the level digit (bzip2 block size digit):
  - Digit path: [decomp_FUN_00427401.c](decomp_FUN_00427401.c:195)
- The sequence “1 AY&SY” (part of bzip2 block header) cascades through subsequent character checks as the state advances:
  - Branch chain immediately after header: [decomp_FUN_00427401.c](decomp_FUN_00427401.c:236)
- Bit-buffered input, classic for bzip2:
  - Repeated “fill at least N bits” loops: e.g., [decomp_FUN_00427401.c](decomp_FUN_00427401.c:367)
- Huffman decode table construction and symbol-frequency accumulation, consistent with bzip2 canonical Huffman routines and MTF/BWT:
  - Table-building logic: [FUN_0042c706()](decomp_FUN_0042c706.c:5)
  - Symbol map consolidation: [FUN_004292a0()](decomp_FUN_004292a0.c:4)
- Index and width checks aligning with code-length bounds and per-block decoding flows seen in bzip2 inflators:
  - Bound checks and tree-walk: [decomp_FUN_00427401.c](decomp_FUN_00427401.c:1401)

External bzip2 format sources that match the above:
- bzip2 File Format & Algorithm Overview: https://en.wikipedia.org/wiki/Bzip2
- Official bzip2 documentation (format and decompression design): https://sourceware.org/bzip2/ and http://www.bzip.org/1.0.8/bzip2-manual-1.0.8.html

Conclusion: The “state machine” is a bzip2 inflator for the overlay payload, not the MCU fueling calculator.

==================================================

2) Roles of Key Helper Routines

- [FUN_0042c706()](decomp_FUN_0042c706.c:5): Constructs canonical Huffman decoding tables and prefix-sum count arrays used in bzip2 blocks. Note the symbol length histogramming, cumulative counts, and per-length bounds typical in canonical Huffman.
- [FUN_004292a0()](decomp_FUN_004292a0.c:4): Builds symbol lists (active byte values) used in the MTF/BWT step; it populates a compact indexing of symbols present in the block, again matching bzip2 behavior.

These are canonical parts of bzip2, not fueling logic.

==================================================

3) What overlay.bin Is and How It’s Packed

- overlay.bin is a bzip2-compressed payload extracted from the Windows updater executable [ADR9802v2.8.4.exe](ADR9802v2.8.4.exe:1) using the repository script [extract_pe_overlay.py](extract_pe_overlay.py:1).
- Our regex scan for CRC-8 lookup tables over overlay.bin returned none, consistent with bzip2’s built-in per-block CRC (and trailing stream CRC) instead of an external CRC-8:
  - No CRC-8 tables found: [crc_table_hits_overlay.txt](crc_table_hits_overlay.txt:1)
- The presence of a bzip2 inflator in the updater and the bzip2 header in the decompiled function strongly suggest the overlay is decompressed on the PC side and/or staged for device programming.

Implication: You can treat overlay.bin as a bzip2 container. Once decompressed, you get the raw programming image(s) and/or calibration blobs that the device consumes.

==================================================

4) What We Can Do Right Now with Custom Firmware

Because the payload is bzip2-compressed, we can:
- Decompress overlay.bin to obtain the raw data images/calibration tables.
- Edit the decompressed data (e.g., fueling tables, axis breakpoints, limiters, feature toggles) if you can identify them in the decoded image.
- Recompress with bzip2 and re-embed to build a modified overlay that the updater will accept (its internal CRCs are handled by the bzip2 encoder; our scan found no standalone CRC-8 tables in overlay.bin).

Instrumented assets and scripts:
- Overlay file: [overlay.bin](overlay.bin:1)
- Extraction scripts present beside the project (you can use standard bzip2 tooling as well):
  - [extract_bzip_payloads.py](extract_bzip_payloads.py:1)
  - [extract_pe_overlay.py](extract_pe_overlay.py:1)

What types of modifications are viable now:
- Fueling table value edits: If the raw (decompressed) data contains lookup tables (e.g., RPM × boost), you can alter magnitudes to change delivered fueling under given conditions.
- Axis breakpoint edits: If axes are present as breakpoint arrays, you can move their positions to remap the interpolation behavior (e.g., denser bins at critical regions).
- Limiters/enablers: Many calibration images include flags and thresholds (temperature limits, pressure thresholds, torque caps) that may be changed.
- Power levels: The repository already indicates a power-level concept (e.g., [autotune_state.json](autotune_state.json:1) shows “power_level”: 5). If the payload uses multiple maps/levels, you can alter these sets.

Important constraint:
- Without identified microcontroller fueling code and its symbol map, you cannot add new input dimensions (like TPS) purely by editing calibration data unless the firmware already supports it. Calibration changes can only influence what the runtime code already indexes/uses.

==================================================

5) What Would Be Required to Add TPS-Based Fueling Logic

The user goal was to “adjust CAN-bus fueling based on TPS data.” To truly add TPS as a new axis or a blended input, the MCU runtime must:
- Read TPS (from CAN or ADC) and normalize it.
- Use TPS as an index in the fueling computation path (e.g., as a 3rd axis or as a blend factor affecting the existing 2D table result).
- Possibly transmit or apply a different CAN payload based on TPS-adjusted fuel.

What we currently lack:
- A confirmed disassembly of the device’s microcontroller code that computes fueling and sends the CAN messages. The decompiled functions we examined such as [FUN_0041d527()](decomp_FUN_0041d527.c:4) and [FUN_004227b8()](decomp_FUN_004227b8.c:5) are in the Windows updater, not MCU firmware. In fact:
  - [FUN_0041d527()](decomp_FUN_0041d527.c:4) is a standard printf/formatting-like implementation (format flags, width/precision, length modifiers, cases for %d/%x/%s/%c), not a sensor parser.
  - [FUN_004227b8()](decomp_FUN_004227b8.c:5) is a numeric parser akin to strtod/decimal exponent handling, also PC-side utility code.

Therefore, to implement TPS-based fueling you would need:
- The MCU image (not just the PC updater’s payload decompressor) disassembled and analyzed for:
  - The table lookup routine (e.g., boost- and RPM-indexed).
  - The sensor acquisition layer (CAN/ADC) receiving boost/RPM and whether TPS already exists.
  - The CAN message preparation path (if fueling is sent via CAN).
- Patching strategy on MCU:
  - Insert TPS read/normalization.
  - Modify the lookup to include TPS either as an additional dimension or as a blend factor between maps.
  - Re-link and fit code within MCU memory constraints (or add a trampoline to free space).
  - Recalculate any device-side integrity checks or signatures (separate from bzip2 encapsulation).

Status: Not yet feasible from the current artifacts alone. We need the actual MCU firmware code region and architecture details. The presence of a PIC processor was hypothesized, but we haven’t confirmed device-side binary and entry points here.

==================================================

6) Practical Workflow (Decode → Modify → Repack → Validate)

Given the constraints, here is a robust, repeatable process to do what’s feasible today:

- Step A: Decompress overlay.bin
  - Use any standard bzip2 tool or Python’s bz2 module to decompress:
    - The “BZh” header is confirmed by code checks at [decomp_FUN_00427401.c](decomp_FUN_00427401.c:130), [decomp_FUN_00427401.c](decomp_FUN_00427401.c:151), [decomp_FUN_00427401.c](decomp_FUN_00427401.c:172).
  - Alternatively, adapt [extract_bzip_payloads.py](extract_bzip_payloads.py:1).

- Step B: Identify and map the data
  - Search the decompressed image for:
    - Obvious table shapes (2D arrays with regular strides).
    - Axis breakpoint arrays (monotonic sequences corresponding to RPM, PSI, etc.).
    - Multiple map “packs” for staged power levels.

- Step C: Make calibration edits
  - Edit fueling magnitudes or axes as required.
  - Keep table sizes/strides unchanged unless you fully understand the MCU’s indexing and bounds.

- Step D: Repack as bzip2
  - Recompress to produce a valid bzip2 stream; internal CRCs are handled by the compressor.
  - Our CRC scan for overlay.bin showed no external CRC-8 LUTs:
    - [crc_table_hits_overlay.txt](crc_table_hits_overlay.txt:1)

- Step E: Reinsert and test
  - Replace the overlay resource or provide through the PC updater as appropriate.
  - Bench-test on a hardware-in-the-loop or strictly controlled environment to validate effects.

==================================================

7) Appendix: Scripts, Headless Ghidra Outputs, and Cross-Checks

- Switch/dispatcher enumeration shows our “state machine” function with many cases, but these cases simply step through bzip2 bitstream parsing states:
  - [aid_switch_candidates.txt](aid_switch_candidates.txt:3)
  - [aid_dispatch_map.txt](aid_dispatch_map.txt:1)

- Headless Ghidra run was performed against the Windows executable to sanity-check function call relationships and highlight “potential” parser/utility functions. Our headless post-script identified printf-like and numeric parsing functions as callers/callees that live in the PC app, not on the device:
  - Script used: [find_table_references.py](find_table_references.py:1)
  - Example callers:
    - FUN_0041d527 called from FUN_0041a9e4 and FUN_0041acde in the PE (output excerpt captured during headless run).

- The presence of bzip2 “1AY&SY” block magic was evident in the state chain (ASCII spelled across the subsequent case checks in [decomp_FUN_00427401.c](decomp_FUN_00427401.c:236)), which is an exact bzip2 block header marker (see bzip2 sources below).

==================================================

8) Sources and References

Internal code/files (clickable):
- bzip2 state machine (Windows updater): [decomp_FUN_00427401.c](decomp_FUN_00427401.c:1)
  - “B” check: [decomp_FUN_00427401.c](decomp_FUN_00427401.c:130)
  - “Z” check: [decomp_FUN_00427401.c](decomp_FUN_00427401.c:151)
  - “h” check: [decomp_FUN_00427401.c](decomp_FUN_00427401.c:172)
  - post-header chain (matches block magic “1AY&SY”): [decomp_FUN_00427401.c](decomp_FUN_00427401.c:236)
- Huffman table builder: [FUN_0042c706()](decomp_FUN_0042c706.c:5)
- Symbol list/active set builder (used by MTF/BWT step): [FUN_004292a0()](decomp_FUN_004292a0.c:4)
- printf-like formatter (PC-side): [FUN_0041d527()](decomp_FUN_0041d527.c:4)
- numeric parser akin to strtod (PC-side): [FUN_004227b8()](decomp_FUN_004227b8.c:5)
- CRC-8 LUT scan result: [crc_table_hits_overlay.txt](crc_table_hits_overlay.txt:1)
- overlay payload container: [overlay.bin](overlay.bin:1)
- PE updater containing overlay: [ADR9802v2.8.4.exe](ADR9802v2.8.4.exe:1)
- Utility scripts:
  - [extract_bzip_payloads.py](extract_bzip_payloads.py:1)
  - [extract_pe_overlay.py](extract_pe_overlay.py:1)
  - [find_table_references.py](find_table_references.py:1)
- Switch discovery outputs:
  - [aid_switch_candidates.txt](aid_switch_candidates.txt:3)
  - [aid_dispatch_map.txt](aid_dispatch_map.txt:1)
- Project configs:
  - [quadzilla.gpr](quadzilla.gpr:1)
  - [quadzilla.rep](quadzilla.rep/project.prp:1)

External specifications and references:
- bzip2 format and algorithm:
  - Wikipedia overview (headers “BZh”, block magic “1AY&SY”, Huffman/MTF/BWT): https://en.wikipedia.org/wiki/Bzip2
  - Official bzip2 documentation and manual: https://sourceware.org/bzip2/ and http://www.bzip.org/1.0.8/bzip2-manual-1.0.8.html
- Canonical Huffman coding (general background): https://en.wikipedia.org/wiki/Canonical_Huffman_code
- Ghidra headless usage (AnalyzeHeadless): https://ghidra-sre.org/ and Ghidra docs on “analyzeHeadless” (bundled with Ghidra distribution)

==================================================

Bottom Line

- The present artifacts and decompilations show we are dealing with a bzip2-compressed overlay payload inside the Windows updater tool. The “state machine” is a bzip2 inflator, not the embedded fueling logic.
- You can immediately decompress, edit, and recompress the overlay payload to change calibrations that the installed firmware consumes (axes, fuel values, limits). This is the most reliable, low-risk route to “custom firmware” with today’s evidence.
- To realize true TPS-based fueling logic (a new runtime input dimension), we must obtain and reverse the microcontroller firmware that performs live fueling calculations and CAN messaging. Only then can we propose exact patch points and safe code-insertion plans.

If you want, we can proceed next to: (a) fully decompress overlay.bin and identify its tables/images, (b) document table formats and offsets, and (c) build a safe editing/repack pipeline with automated checks.