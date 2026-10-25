#!/usr/bin/env python3
"""Verify the receive type switch bytes and adjacent non-executable layout."""
import argparse
import hashlib
import json
import struct
from pathlib import Path

from audit_aid_tables import SHA


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('image', type=Path)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    raw = args.image.read_bytes()
    if len(raw) != 32000 or hashlib.sha256(raw).hexdigest() != SHA:
        raise ValueError('unexpected firmware image')
    table = raw[0x809C - 0x4000:0x80A2 - 0x4000]
    targets = [0x809E + 2 * value for value in table]
    expected = [0x80D8, 0x80A2, 0x8100, 0x80A2, 0x80B2, 0x814C]
    if targets != expected:
        raise ValueError('receive jump targets changed')
    padding = raw[0x81A2 - 0x4000:0x81A4 - 0x4000]
    pointer = struct.unpack_from('<I', raw, 0x81A4 - 0x4000)[0]
    if padding != b'\xff\xff' or pointer != 0x2007C8:
        raise ValueError('receive alignment or state-base literal changed')
    result = {'format': 'quadzilla-receive-layout-v1', 'raw_sha256': SHA,
              'switch': {'start': '0x809c', 'end': '0x80a2',
                         'bytes': table.hex(), 'index_rule': 'header high nibble 0..5',
                         'target_rule': '0x809e + 2 * unsigned_table_byte',
                         'targets': [hex(a) for a in targets]},
              'alignment': {'start': '0x81a2', 'end': '0x81a4',
                            'bytes': padding.hex()},
              'state_base_literal': {'start': '0x81a4', 'end': '0x81a8',
                                     'value': hex(pointer), 'reader': '0x804c'},
              'limitations': ['layout and local transfer target evidence; no physical frame admission claim']}
    args.output.write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    print('verified six switch targets, alignment and state-base literal')


if __name__ == '__main__':
    main()
