#!/usr/bin/env python3
"""Bind the remaining literal pools to raw ARMv4T PC-relative word loads."""
import argparse
import hashlib
import json
import struct
from pathlib import Path

from build_image_ledger import REMAINING_LITERAL_RANGES, REMAINING_LITERAL_PADDING, SHA


def literal_target(address, isa, opcode):
    """Recognize only immediate PC-relative word LDR, not byte/register forms."""
    if isa == 'thumb' and opcode & 0xF800 == 0x4800:
        return ((address + 4) & ~3) + (opcode & 255) * 4
    if isa == 'arm' and opcode & 0x0F7F0000 == 0x051F0000:
        return address + 8 + (1 if opcode & (1 << 23) else -1) * (opcode & 4095)
    return None


def audit(raw, root):
    if hashlib.sha256(raw).hexdigest() != SHA:
        raise ValueError('source identity mismatch')
    manifest = json.loads((root / 'audit/data/reviewed_instruction_ranges.json').read_text())
    if manifest['raw_sha256'] != SHA:
        raise ValueError('instruction manifest identity mismatch')
    cache, refs = {}, {}
    for row in manifest['ranges']:
        lo, hi = int(row['start'], 0), int(row['end'], 0)
        path = row['decoder_artifact']
        if path not in cache:
            cache[path] = json.loads((root / path).read_text())
        decode = cache[path]
        if decode['raw_sha256'] != SHA:
            raise ValueError('decoder identity mismatch')
        block = next(r for r in decode['ranges'] if int(r['start'], 0) <= lo and hi <= int(r['end'], 0))
        cursor = lo
        for ins in block['instructions']:
            at = int(ins['address'], 0)
            if not lo <= at < hi:
                continue
            if at != cursor:
                raise ValueError('accepted decoder range has a gap')
            cursor += ins['length']
            width = 2 if row['isa'] == 'thumb' else 4
            opcode = int.from_bytes(raw[at-0x4000:at-0x4000+width], 'little')
            target = literal_target(at, row['isa'], opcode)
            if target is not None:
                refs.setdefault(target, []).append({'site': hex(at), 'isa': row['isa'],
                                                    'opcode': hex(opcode), 'decoder': path})
        if cursor != hi:
            raise ValueError('accepted decoder range incomplete')
    export = json.loads((root / 'audit/data/ida_image_items.json').read_text())
    if export['raw_sha256'] != SHA or not export['database_bytes_match']:
        raise ValueError('IDA export identity mismatch')
    direct = {int(r['decoded_direct_target'], 0) for r in export['items'] if 'decoded_direct_target' in r}
    pools = []
    for lo, hi in REMAINING_LITERAL_RANGES:
        if lo % 4 or hi % 4 or not 0x4000 <= lo < hi <= 0xBD00:
            raise ValueError('literal extent alignment or bounds')
        if any(lo <= t < hi for t in direct):
            raise ValueError('literal extent has an unresolved direct branch target')
        words = []
        for a in range(lo, hi, 4):
            if a not in refs:
                raise ValueError(f'literal word has no accepted-code PC-relative reference: {a:#x}')
            words.append({'address': hex(a), 'value': hex(struct.unpack_from('<I', raw, a-0x4000)[0]),
                          'load_sites': refs[a]})
        pools.append({'start': hex(lo), 'end': hex(hi), 'bytes': hi-lo,
                      'source_sha256': hashlib.sha256(raw[lo-0x4000:hi-0x4000]).hexdigest(), 'words': words})
    padding = []
    for at in REMAINING_LITERAL_PADDING:
        if raw[at-0x4000:at-0x4000+2] != b'\xff\xff' or at in direct:
            raise ValueError('padding bytes or direct branch target changed')
        prior = next(r for r in export['items'] if int(r['end'], 0) == at)
        if prior.get('mnemonic') not in ('BX', 'B'):
            raise ValueError(f'padding lacks preceding unconditional transfer: {at:#x}')
        padding.append({'start': hex(at), 'end': hex(at+2), 'bytes': 'ffff',
                        'preceding_transfer': prior['text']})
    return {'format': 'quadzilla-remaining-literal-audit-v1', 'raw_sha256': SHA,
            'literal_bytes': sum(p['bytes'] for p in pools), 'literal_words': sum(len(p['words']) for p in pools),
            'literal_extents': pools, 'padding_extents': padding,
            'limitations': ['PC-relative load proves literal use, not all semantic meaning of the value',
                            'Decoded direct branch exclusion is not exhaustive alternate-entry analysis',
                            'Complete byte classification does not complete the full firmware analysis']}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('image', type=Path)
    p.add_argument('--output', type=Path, required=True)
    args = p.parse_args()
    result = audit(args.image.read_bytes(), Path(__file__).resolve().parents[2])
    args.output.write_text(json.dumps(result, indent=2)+'\n', encoding='utf-8')
    print(f"{result['literal_words']} referenced words/{result['literal_bytes']} bytes in "
          f"{len(result['literal_extents'])} extents; {len(result['padding_extents'])} alignment pairs")


if __name__ == '__main__':
    main()
