#!/usr/bin/env python3
"""Build an exhaustive byte ledger while preserving unresolved classifications.

IDA item types are candidates. Only explicit source-bound layout facts override
them; a covered byte is not automatically a manually reviewed byte.
"""
import argparse
import hashlib
import json
import struct
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SHA = "1ae519ba6194e8f7bdaaa94333a83a9e6fda3b0563f87f7d48383b37288c1780"
BASE, END = 0x4000, 0xBD00
LAYOUT = (
    (0x40F8, 0x4114, "arm_startup_literal_pool"),
    (0x4144, 0x414C, "sram_descriptor_loop_literals"),
    (0x41BE, 0x41C0, "clock_setup_alignment_nop"),
    (0x41C0, 0x41F0, "clock_setup_literal_pool"),
    (0x48C2, 0x48C4, "input_gate_alignment_nop"),
    (0x48C4, 0x48E8, "input_gate_literal_pool"),
    (0x4A88, 0x4A94, "backdown_literal_pool"),
    (0x4B26, 0x4B28, "stretch_alignment_nop"),
    (0x4B28, 0x4B38, "stretch_literal_pool"),
    (0x4B82, 0x4B84, "capture_scalar_alignment_nop"),
    (0x4B84, 0x4BA2, "capture_scalar_jump_table_1_and_pad"),
    (0x4C32, 0x4C34, "capture_scalar_alignment_nop"),
    (0x4C34, 0x4C3E, "capture_scalar_jump_table_2"),
    (0x4D0A, 0x4D0C, "capture_scalar_alignment_nop"),
    (0x4D0C, 0x4D38, "capture_scalar_literal_pool"),
    (0x5016, 0x5018, "scalar_helper_alignment_nop"),
    (0x5018, 0x506C, "scalar_helper_literal_pool"),
    (0x53C4, 0x5414, "main_control_literal_pool_1"),
    (0x5612, 0x5614, "main_control_alignment_nop"),
    (0x5614, 0x56FC, "main_control_literal_pool_2"),
    (0x7446, 0x7448, "spurious_callback_alignment_ff"),
    (0x74DE, 0x74E0, "sram_predicate_alignment_nop"),
    (0x74E0, 0x74E8, "sram_predicate_literal_pool"),
    (0x608C, 0x6240, "aid_validation_dispatch_table"),
    (0x6FB2, 0x6FB4, "tc0_helper_alignment_ff"),
    (0x71BE, 0x71C0, "usart_alignment_nop"),
    (0x71C0, 0x71D0, "usart_literal_pool"),
    (0x7256, 0x7258, "usart_alignment_ff"),
    (0x7258, 0x725C, "usart_literal_pool"),
    (0x72FE, 0x7300, "usart_alignment_nop"),
    (0x7300, 0x7364, "usart_literal_pool"),
    (0x77A6, 0x77A8, "cycle_queue_alignment_ff"),
    (0x77A8, 0x77B8, "cycle_queue_literal_pool"),
    (0x7CA0, 0x7CC4, "aid_resolver_literal_pool"),
    (0x800A, 0x800C, "queue_helper_alignment_ff"),
    (0x8034, 0x8038, "queue_state_base_literal"),
    (0x809C, 0x80A2, "receive_type_jump_table"),
    (0x81A2, 0x81A4, "receive_alignment_ff"),
    (0x81A4, 0x81A8, "receive_state_base_literal"),
    (0x8500, 0x8504, "queue_state_base_literal"),
    (0x896C, 0x8970, "soft_float_status_pointer"),
    (0x96C4, 0x96E8, "startup_region_descriptors"),
    (0x96E8, 0x997C, "initialized_ram_data_source"),
    (0x997C, 0x9B0C, "capture_scalar_20x20_table_source"),
    (0x9B0C, 0x9F88, "initialized_ram_data_source"),
    (0x9FF0, 0xA02F, "spi_request_tx_table"),
    (0xA030, 0xA0B0, "adc_channel6_byte_lut"),
    (0xA0B0, 0xA320, "adc_channel7_signed_halfword_lut"),
    (0xA320, 0xA3A0, "adc_channel5_two_page_lut"),
    (0xA3A0, 0xA91C, "adc_channel4_signed_halfword_lut"),
    (0xA91C, 0xAD18, "aid_pointer_table_1"),
    (0xAD18, 0xB114, "aid_pointer_table_2"),
    (0xB114, 0xB1B8, "ram_executable_template"),
    (0xB1B8, END, "erased_tail_ff"),
)

# Source-checked residual alignments follow unconditional transfers; the three
# interworking NOPs are skipped by BX PC. See residual_code_adjudication.json.
LAYOUT += tuple((a, a+2, "reviewed_function_alignment_nop") for a in (
    0x4302,0x435E,0x4596,0x46C2,0x4942,0x570E,0x5736,0x5756,
    0x5CBA,0x5DEA,0x5EF2,0x5F2E,0x6702,0x6B1A,0x6BD2,0x6C5E,
    0x6C82,0x6F56,0x70CA,0x7132,0x7172,0x73C6,0x742E,0x7486,
    0x7A3E,0x7B0A,0x7B16,0x7C52,0x7C9E,0x84FE))
LAYOUT += tuple((a, a+2, "reviewed_function_alignment_ff") for a in (
    0x6B46,0x74C2,0x7B02,0x7BE6,0x7BEE,0x7FD6,0x852E,0x8562))
LAYOUT += tuple((a, a+2, "integer_interworking_alignment_nop") for a in (0x8566,0x8576,0x8586))
LAYOUT += (
    (0x743C,0x7444,"reset_request_literals"),
    (0x7B0C,0x7B10,"uart_wrapper_literals"),
    (0x7B18,0x7B1C,"uart_wrapper_literals"),
    (0x7B44,0x7B4C,"uart_wrapper_literals"),
    (0x7B58,0x7B5C,"uart_wrapper_literals"),
    (0x9F88,0x9FDC,"ratio_score_row_table"),
    (0x9FDC,0x9FF0,"ratio_score_coefficients"),
    (0xA02F,0xA030,"spi_adc_zero_alignment"),
)


REMAINING_LITERAL_RANGES = (
    (0x4304, 0x4330),
    (0x4360, 0x4384),
    (0x4598, 0x4650),
    (0x46C4, 0x46D0),
    (0x4790, 0x47B0),
    (0x4810, 0x4818),
    (0x4944, 0x495C),
    (0x4978, 0x497C),
    (0x50DC, 0x50F0),
    (0x5700, 0x5704),
    (0x5710, 0x5714),
    (0x5718, 0x571C),
    (0x5738, 0x573C),
    (0x5758, 0x575C),
    (0x59CC, 0x59E8),
    (0x5CBC, 0x5CF0),
    (0x5DEC, 0x5E04),
    (0x5EA0, 0x5EBC),
    (0x5EF4, 0x5F04),
    (0x5F08, 0x5F0C),
    (0x5F10, 0x5F14),
    (0x5F30, 0x5F34),
    (0x5FEC, 0x601C),
    (0x63AC, 0x63F0),
    (0x6704, 0x67DC),
    (0x6A48, 0x6B08),
    (0x6B0C, 0x6B10),
    (0x6B1C, 0x6B20),
    (0x6B60, 0x6B64),
    (0x6BD4, 0x6BD8),
    (0x6C14, 0x6C48),
    (0x6C60, 0x6C68),
    (0x6C84, 0x6C94),
    (0x6F58, 0x6FA0),
    (0x70CC, 0x7120),
    (0x7124, 0x7128),
    (0x7134, 0x7138),
    (0x713C, 0x7140),
    (0x7144, 0x7148),
    (0x714C, 0x7150),
    (0x7154, 0x7158),
    (0x715C, 0x7160),
    (0x7164, 0x7168),
    (0x7174, 0x7178),
    (0x737C, 0x7380),
    (0x7390, 0x7398),
    (0x73B0, 0x73BC),
    (0x73C8, 0x73CC),
    (0x73D0, 0x73D4),
    (0x73D8, 0x73DC),
    (0x73E0, 0x73E4),
    (0x7430, 0x7434),
    (0x7488, 0x7498),
    (0x7598, 0x760C),
    (0x7698, 0x76CC),
    (0x7A40, 0x7AF8),
    (0x7B5C, 0x7B60),
    (0x7C54, 0x7C68),
)
REMAINING_LITERAL_PADDING = (0x499A,0x59CA,0x74B2,0x7BCA,0x7C1A,0x7D7E,0x854A)
LAYOUT += tuple((a,b,"remaining_pc_literal_pool") for a,b in REMAINING_LITERAL_RANGES)
LAYOUT += tuple((a,a+2,"remaining_literal_alignment_ff") for a in REMAINING_LITERAL_PADDING)


def validate_item_coverage(rows, base=BASE, end=END):
    cursor = base
    for row in rows:
        lo, hi = int(row["start"], 0), int(row["end"], 0)
        if lo != cursor or not lo < hi <= end:
            raise ValueError("IDA item coverage has a gap, overlap, or invalid range")
        cursor = hi
    if cursor != end:
        raise ValueError("incomplete image item coverage")


def validate_instruction_reviews(document):
    if document.get("format") != "quadzilla-instruction-range-reviews-v1" or document.get("raw_sha256") != SHA:
        raise ValueError("instruction-review identity mismatch")
    reviewed = []
    for row in document["ranges"]:
        lo, hi = int(row["start"], 0), int(row["end"], 0)
        alignment = {"thumb": 2, "arm": 4}.get(row.get("isa"))
        if not alignment or not BASE <= lo < hi <= END or lo % alignment or hi % alignment:
            raise ValueError("invalid reviewed instruction range or ISA alignment")
        if not row.get("evidence") or not row.get("account"):
            raise ValueError("reviewed range lacks supporting account")
        if any(lo < b and hi > a for a, b, _ in LAYOUT):
            raise ValueError("instruction review overlaps a supported layout region")
        reviewed.append((lo, hi, row["entry"], row["isa"]))
    reviewed.sort()
    if any(a[1] > b[0] for a, b in zip(reviewed, reviewed[1:])):
        raise ValueError("overlapping instruction reviews")
    return reviewed


def build(raw, export, reviews=None):
    digest = hashlib.sha256(raw).hexdigest()
    if digest != SHA or export.get("raw_sha256") != digest or not export.get("database_bytes_match"):
        raise ValueError("source identity mismatch")
    rows = export["items"]
    validate_item_coverage(rows)
    reviewed = validate_instruction_reviews(reviews) if reviews is not None else []
    if raw[0xB1B8-BASE:] != bytes([255]) * (END-0xB1B8):
        raise ValueError("tail is not erased")
    descriptors = []
    for ea in range(0x96C4, 0x96E8, 12):
        length, dest, source = struct.unpack_from("<III", raw, ea-BASE)
        descriptors.append({"at": hex(ea), "length": length, "destination": hex(dest),
                            "source": hex(source), "operation": "zero_fill" if source == dest else "copy"})
    ranges = []
    conflicts = []
    for row in rows:
        lo, hi = int(row["start"], 0), int(row["end"], 0)
        cuts = sorted({lo, hi} | {v for a, b, *_ in (*LAYOUT, *reviewed) for v in (a, b) if lo < v < hi})
        for a, b in zip(cuts, cuts[1:]):
            purpose = next((name for x, y, name in LAYOUT if x <= a and b <= y), None)
            review = next(((entry, isa) for x, y, entry, isa in reviewed if x <= a and b <= y), None)
            classification = purpose or ("reviewed_"+review[1]+"_instructions" if review else row["kind"] + "_pending_review")
            if purpose and row["kind"] == "ida_code" and purpose != "ram_executable_template":
                conflicts.append({"start": hex(a), "end": hex(b), "ida_text": row.get("text"),
                                  "layout": purpose})
            record = {"start": hex(a), "end": hex(b), "classification": classification,
                      "review_state": "layout_role_supported" if purpose else
                                      "instruction_range_supported" if review else "needs_instruction_or_data_review"}
            if review:
                record["review_entry"] = review[0]
            ranges.append(record)
    counts = Counter()
    for row in ranges:
        counts[row["classification"]] += int(row["end"], 0)-int(row["start"], 0)
    return {"format": "quadzilla-image-ledger-v1", "raw_sha256": digest,
            "image_range": [hex(BASE), hex(END)], "covered_bytes": END-BASE,
            "completion": "incomplete; item coverage is not proof of manual classification",
            "startup_descriptors": descriptors, "classification_bytes": dict(counts),
            "ida_layout_conflicts": conflicts, "ranges": ranges}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("image", type=Path)
    parser.add_argument("--items", type=Path, default=ROOT / "audit/data/ida_image_items.json")
    parser.add_argument("--reviews", type=Path, default=ROOT / "audit/data/reviewed_instruction_ranges.json")
    parser.add_argument("--output", type=Path, default=ROOT / "audit/data/image_coverage_ledger.json")
    args = parser.parse_args()
    result = build(args.image.read_bytes(), json.loads(args.items.read_text(encoding="utf-8")),
                   json.loads(args.reviews.read_text(encoding="utf-8")))
    args.output.write_text(json.dumps(result, indent=2)+"\n", encoding="utf-8")
    print(json.dumps({"bytes": result["covered_bytes"], "classifications": result["classification_bytes"],
                      "conflicts": len(result["ida_layout_conflicts"])}))


if __name__ == "__main__":
    main()
