#!/usr/bin/env python3
"""Inventory exact image literals and IDA references around outgoing queue state."""
import argparse
import hashlib
import json
import struct
from pathlib import Path

from audit_aid_tables import SHA


BASE = 0x2007C8
END = 0x200890


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('image', type=Path)
    parser.add_argument('--items', type=Path, default=Path('audit/data/ida_image_items.json'))
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    raw = args.image.read_bytes()
    exported = json.loads(args.items.read_text(encoding='utf-8'))
    if (len(raw) != 32000 or hashlib.sha256(raw).hexdigest() != SHA or
            exported['raw_sha256'] != SHA or not exported['database_bytes_match']):
        raise ValueError('source identity mismatch')
    literals = []
    for offset in range(0, len(raw) - 3, 4):
        value = struct.unpack_from('<I', raw, offset)[0]
        if BASE <= value < END:
            literals.append({'at': hex(0x4000 + offset), 'value': hex(value)})
    refs = [{'at': row['start'], 'text': row.get('text'),
             'data_refs': row.get('data_refs', [])}
            for row in exported['items'] if '0x2007c8' in row.get('data_refs', [])]
    targets = {0x7EFC, 0x7FD8, 0x7EB4, 0x7F58, 0x800C, 0x8038, 0x81A8}
    calls = {hex(target): [row['start'] for row in exported['items']
                           if row.get('decoded_direct_target') == hex(target)]
             for target in sorted(targets)}
    template = raw[0x96E8 - 0x4000:0x9F88 - 0x4000]
    initial = {hex(address): template[address - 0x200000]
               for address in (0x2007DB, 0x2007DC, 0x2007E0, 0x2007E1)}
    result = {'format': 'quadzilla-queue-state-references-v1',
              'raw_sha256': SHA,
              'aligned_words_pointing_into_state': literals,
              'ida_references_to_state_base': refs,
              'decoded_direct_call_sites': calls,
              'initialized_count_bytes': initial,
              'limitations': ['aligned literal inventory does not rule out computed or aliased pointers',
                              'IDA references and direct targets are tool interpretations',
                              'runtime writes from unreviewed entries and interrupts remain to be audited']}
    args.output.write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    print(f'{len(literals)} aligned state-range literals, {len(refs)} IDA base references')


if __name__ == '__main__':
    main()
