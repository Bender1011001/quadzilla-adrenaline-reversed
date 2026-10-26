# ADC polling, lookup tables and rolling averages

This account is bound to the exact 32,000-byte V2.8.4HF application image,
SHA-256 `1ae519ba6194e8f7bdaaa94333a83a9e6fda3b0563f87f7d48383b37288c1780`.
The [explicit Thumb decode](../audit/data/adc_pipeline_binaryninja.json)
covers six returning entries: `0x41F0..4214`, `0x4214..4302`,
`0x7364..737C`, `0x7380..7390`, `0x7398..73B0` and
`0x73BC..73C6`, totaling **348 instruction bytes and 166 starts**.
The [bounded original-byte campaign](../audit/data/adc_pipeline_emulation.json)
visits all 166 starts. Five cases use synthetic ADC register values between
0 and 1023 and controlled SRAM flags; they are not measurements of the board.

The [SAM7S datasheet](https://ww1.microchip.com/downloads/en/DeviceDoc/doc6175.pdf)
identifies `0xFFFD8000` as the ADC block, offset `0x1C` as status,
offsets `0x3C..4C` as channel data registers 3–7, and a status EOC bit
for each channel. It specifies an 8-bit or 10-bit conversion result;
`0x4330` writes ADC mode value `0x02010A00`, whose LOWRES bit is clear,
selecting 10-bit results. The emulator maps plain memory at those
addresses and does not reproduce hardware's EOC clear-on-read behavior.

## Cycle entry `0x4214`

The control-cycle orchestrator `0x76CC` calls `0x4214` first. It snapshots
ADC status once, then tests ready bits 3, 4, 5, 6 and 7 in that order.
For each ready bit it reads the corresponding ADC_CDR, invokes a local
conversion helper for channels 4–7, optionally updates a 32-word rolling
buffer when that channel's SRAM gate is nonzero, clears the gate, and clears
the corresponding bit in status byte `0x2008A0`. Channel 3 is different:
its sample is compared with 676, stores boolean `sample >= 676` at
`0x200AFE`, and clears bit 3 in `0x2008A0`. Channel 3 is the page selector
for channel 5's lookup table. No physical signal assignment is inferred.

| ADC channel / CDR offset | Local transform | Average gate | 32-word buffer | Averaged word |
|---:|---|---|---|---|
| 4 / `0x40` | `0x7398`: signed halfword table index `min(sample,701)`, then add byte `0x200AFF` | `0x200721` | `0x200934..9B3` | `0x2008A8` |
| 5 / `0x44` | `0x7380`: signed byte from page `64*byte[0x200AFE] + (sample >> 4)` | `0x200722` | `0x2008B4..933` | `0x2008A4` |
| 6 / `0x48` | `0x73BC`: unsigned byte at index `sample >> 3` | `0x200723` | `0x200A34..AB3` | `0x2008B0` |
| 7 / `0x4C` | `0x7364`: signed halfword at index `sample >> 1`, or constant 100 if index is at least 312 | `0x200724` | `0x2009B4..A33` | `0x2008AC` |

The averaging helper `0x41F0` shifts words 1–31 into slots 0–30,
appends the new transformed value at slot 31, sums those 32 words with
32-bit wraparound, and returns the logical result `sum >> 5`. The four
buffers above are adjacent and do not overlap. Synthetic buffers seeded
with words 1–32 shifted to 2–32 plus the new value; the observed averaged
words matched that byte-level model for zero and maximum 10-bit samples.
When a channel's average gate is zero, the transform still runs and its
ready flag clears, but that channel's buffer and averaged output do not
change in the bounded case.

After processing the status snapshot, if `0x2008A0` is zero, the routine
writes `0xF8` there and command value 2 to ADC_CR at `0xFFFD8000`.
The datasheet names ADC_CR bit 1 START, so this is a request for another
conversion sequence; plain emulator memory cannot establish when it
actually completes. With only channel 4 ready in a synthetic case,
`0x2008A0` retains other pending bits and no START write occurs.

The channel-4 averaged word at `0x2008A8` is the value compared with
`uint16[0x2006E0]` by the [initial-state selector](INITIAL_STATE_CONFIG_REVIEW.md)
and with `uint16[0x200794]` by the
[main-loop state dispatcher](MAIN_LOOP_STATE_REVIEW.md). This establishes
the software producer-consumer link. It does not identify the analog sensor,
the value's units, an electrical threshold, or a time interval.

## Four source-bound lookup tables

The [table-layout artifact](../audit/data/adc_table_layout.json) checks
each helper's literal word, indexed load, source bytes, element width and
extent. The four tables are contiguous from `0xA030` through `0xA91B` and
end exactly where the first previously reviewed AID pointer table begins.
The accepted extents use the firmware's index arithmetic and the datasheet's
10-bit result range. The image contains no confirmed execution entry in
these extents; IDA's code items there are conflicting auto-analysis, not
independent execution evidence.

| Range | Elements | Value range | Indexed reader |
|---|---:|---:|---|
| `0xA030..A0AF` | 128 unsigned bytes | 0..100 | Channel 6 `0x73BC` |
| `0xA0B0..A31F` | 312 signed halfwords | 104..300 | Channel 7 `0x7364` |
| `0xA320..A39F` | Two pages of 64 signed bytes | 0..42 | Channel 5 `0x7380` |
| `0xA3A0..A91B` | 702 signed halfwords | 32..1832 | Channel 4 `0x7398` |

These **2,284 bytes** are classified as source-bound lookup data in the
[image ledger](../audit/data/image_coverage_ledger.json). The one byte at
`0xA02F` between the SPI request table and these LUTs remains separately
pending. A synthetic register word outside its specified 10-bit DATA field,
or a corrupted page byte at `0x200AFE`, can drive the local indexed helpers
beyond these table bounds; the hardware-specified ADC result and the
observed channel-3 assignment provide the bounded ordinary-input model.
Complete alias and fault reachability work remains open. No device traffic
was sent.

```text
PYTHONPATH=<Binary Ninja Python path> python audit/tools/decode_image_ranges.py firmware_v2.8.4HF.bin --ranges 0x41f0:0x4214:thumb2,0x4214:0x4302:thumb2,0x7364:0x737c:thumb2,0x7380:0x7390:thumb2,0x7398:0x73b0:thumb2,0x73bc:0x73c6:thumb2 --output audit/data/adc_pipeline_binaryninja.json
python audit/tools/audit_adc_tables.py firmware_v2.8.4HF.bin --output audit/data/adc_table_layout.json
uv run --with unicorn==2.1.4 python audit/tools/emulate_adc_pipeline.py firmware_v2.8.4HF.bin --output audit/data/adc_pipeline_emulation.json
python audit/tools/build_image_ledger.py firmware_v2.8.4HF.bin
python -m unittest discover -s tests -t .
```
