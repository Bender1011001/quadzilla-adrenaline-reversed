#!/usr/bin/env python3
"""Bind observed SPI command buffers to an MCP2515-compatible interpretation."""
import argparse
import hashlib
import json
import sys
from pathlib import Path

from build_image_ledger import SHA

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
from mcp2515_protocol import decode_command, decode_identifier


def extract(raw, pointer, count):
    source = 0x96E8+(pointer-0x200000) if 0x200000 <= pointer < 0x2008A0 else pointer
    if not 0x4000 <= source < source+count <= 0xBD00:
        raise ValueError("command source is outside supplied image")
    command = raw[source-0x4000:source-0x4000+count]
    return {"pointer": hex(pointer), "image_source": hex(source),
            "command_hex": command.hex(), "decoded": decode_command(command)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("image", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    raw = args.image.read_bytes()
    if hashlib.sha256(raw).hexdigest() != SHA:
        raise ValueError("unexpected application image")
    initialization = json.loads((ROOT / "audit/data/spi_initialization_emulation.json").read_text(encoding="utf-8"))
    if initialization["raw_sha256"] != SHA:
        raise ValueError("initialization evidence identity changed")
    calls = next(c for c in initialization["cases"] if c["mode"] == "ready")["transfer_calls"]
    sequence = []
    for call in calls:
        registers = [int(v, 0) for v in call["args"]]
        paired = call["helper"] == "0x6b9c"
        row = extract(raw, registers[2] if paired else registers[1], registers[-1])
        row |= {"call_site": call["site"], "helper": call["helper"]}
        if paired:
            row["receive_pointer"] = hex(registers[1])
        sequence.append(row)
    requests = [extract(raw, 0x9FF0+9*i, 9) | {"index": i} for i in range(7)]
    templates = {name: extract(raw, pointer, count) for name, pointer, count in
                 (("capture_rx0", 0x200694, 9), ("capture_rx1", 0x2006A0, 14),
                  ("output_tx2", 0x2006C0, 9), ("secondary_tx_control", 0x2005D0, 3))}
    explicit = {}
    for row in sequence:
        command = bytes.fromhex(row["command_hex"])
        decoded = row["decoded"]
        if decoded["operation"] == "WRITE":
            start = int(decoded["register_start"], 0)
            explicit.update({start+i: value for i, value in enumerate(command[2:])})
        elif decoded["operation"] == "LOAD_TX_BUFFER":
            start = int(decoded["register_start"], 0)
            explicit.update({start+i: value for i, value in enumerate(command[1:])})
    if 0x51 not in explicit or 0x52 not in explicit or explicit[0x52] & 8:
        raise ValueError("expected explicit standard TXB2 identifier fields")
    tx2 = decode_identifier(bytes([explicit[0x51], explicit[0x52], 0, 0])) | {
        "sidh": hex(explicit[0x51]), "sidl": hex(explicit[0x52]),
        "dlc_register": hex(explicit[0x55]),
        "eid_fields": "not required for standard-ID interpretation"}
    result = {"format": "quadzilla-spi-can-command-audit-v1", "raw_sha256": SHA,
              "protocol_interpretation": "MCP2515-compatible command/register layout",
              "physical_part_verified": False,
              "layout_source": "https://ww1.microchip.com/downloads/en/DeviceDoc/MCP2515-Family-Data-Sheet-DS20001801K.pdf",
              "source_sections": ["3", "4", "11", "12"],
              "initialization": sequence, "request_records": requests,
              "capture_output_templates": templates, "explicit_tx2_configuration": tx2,
              "limits": ["decodes initialized buffer bytes; later writers may change command data",
                         "datasheet compatibility is not a measured chip identification",
                         "no hardware, CAN bus, chip-select timing or transfer result modeled",
                         "CAN identifiers/data are decoded without assigning application/PGN meanings"]}
    args.output.write_text(json.dumps(result, indent=2)+"\n", encoding="utf-8")


if __name__ == "__main__":
    main()
