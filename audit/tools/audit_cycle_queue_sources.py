#!/usr/bin/env python3
"""Bind five control-cycle queue call sites to initialized counts and AID blocks."""
import argparse
import hashlib
import json
import struct
from pathlib import Path

from audit_aid_tables import SHA


BASE = 0x200788
CALLS = (0x7706, 0x7724, 0x7744, 0x7764, 0x7780)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('image', type=Path)
    parser.add_argument('--decode', type=Path,
                        default=Path('audit/data/cycle_queue_binaryninja.json'))
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    raw = args.image.read_bytes()
    decode = json.loads(args.decode.read_text(encoding='utf-8'))
    if (len(raw) != 32000 or hashlib.sha256(raw).hexdigest() != SHA or
            decode['raw_sha256'] != SHA):
        raise ValueError('source identity mismatch')
    instructions = {int(item['address'], 0): item
                    for block in decode['ranges'] for item in block['instructions']}
    template = raw[0x96E8 - 0x4000:0x9F88 - 0x4000]
    alignment = raw[0x77A6 - 0x4000:0x77A8 - 0x4000]
    pool = [struct.unpack_from('<I', raw, at - 0x4000)[0]
            for at in range(0x77A8, 0x77B8, 4)]
    if alignment != b'\xff\xff' or pool != [BASE, 0x200712, 0x200710, 0x200711]:
        raise ValueError('cycle queue alignment or literal pool changed')
    nearby_literals = []
    for offset in range(0, len(raw) - 3, 4):
        value = struct.unpack_from('<I', raw, offset)[0]
        if BASE <= value < 0x2007C8:
            nearby_literals.append({'at': hex(0x4000 + offset),
                                    'value': hex(value)})

    def initial(address, length):
        return template[address - 0x200000:address - 0x200000 + length]

    rows = []
    for index, call in enumerate(CALLS):
        if instructions[call]['text'].strip().lower() != 'bl      #0x7efc':
            raise ValueError(f'queue call changed: {call:#x}')
        count_at = BASE + 2 + index
        source_at = BASE + 0x18 + 8 * index
        count = initial(count_at, 1)[0]
        block = initial(source_at, 8)
        if not count <= 8 or any(block[count:]):
            raise ValueError(f'initialized queue slot has invalid padding: {index}')
        rows.append({'slot': index, 'call': hex(call),
                     'count_address': hex(count_at), 'count_initialized': count,
                     'source_address': hex(source_at), 'block_bytes': block.hex(),
                     'aids': list(block[:count]), 'unused_bytes': block[count:].hex()})
    result = {'format': 'quadzilla-cycle-queue-sources-v1',
              'raw_sha256': SHA, 'state_base': hex(BASE),
              'initialized_selector': initial(BASE + 0xB, 1)[0],
              'initialized_pending': initial(0x200712, 1)[0],
              'alignment': {'start': '0x77a6', 'end': '0x77a8',
                            'bytes': alignment.hex()},
              'literal_pool': {'start': '0x77a8', 'end': '0x77b8',
                               'words': [hex(value) for value in pool]},
              'aligned_literals_into_source_block': nearby_literals,
              'slots': rows,
              'limitations': ['startup values do not bound all later writers',
                              'profile names and physical signal meanings are separate evidence',
                              'call-site decode validates targets but not every upstream producer']}
    args.output.write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    print([(row['slot'], row['count_initialized'], row['aids']) for row in rows])


if __name__ == '__main__':
    main()
