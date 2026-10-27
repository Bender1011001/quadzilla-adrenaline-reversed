#!/usr/bin/env python3
"""Conditional address provenance for the normal-entry reviewed Thumb CFG."""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path

from audit_callback_store_contracts import analyze, POINTERS
from emulate_integer_runtime import SHA

ROOT = Path(__file__).resolve().parents[2]


def audit(raw):
    def load(name):
        d = json.loads((ROOT / 'audit/data' / name).read_text())
        if d.get('raw_sha256') != SHA:
            raise ValueError(('evidence identity mismatch', name))
        return d
    manifest = load('reviewed_instruction_ranges.json')
    catalog = load('execution_entry_catalog.json')
    extra = load('entry_adjudications.json')
    inventory = load('store_inventory.json')
    for slot, value in POINTERS.items():
        source = 0x96E8+slot-0x200000
        if int.from_bytes(raw[source-0x4000:source-0x4000+4], 'little') != value:
            raise ValueError('pointer assumption differs from initialization source')
    instructions = {}; cache = {}; declared_entries = set()
    for span in manifest['ranges']:
        if span['isa'] != 'thumb':
            continue
        path = span['decoder_artifact']
        if path not in cache:
            d = json.loads((ROOT / path).read_text())
            if d['raw_sha256'] != SHA:
                raise ValueError('decoder identity mismatch')
            cache[path] = d
        lo, hi = int(span['start'], 0), int(span['end'], 0)
        block = next(r for r in cache[path]['ranges'] if int(r['start'], 0) <= lo and hi <= int(r['end'], 0))
        cursor = lo
        for row in block['instructions']:
            at = int(row['address'], 0)
            if lo <= at < hi:
                if at != cursor or at in instructions:
                    raise ValueError('accepted Thumb overlap/gap')
                instructions[at] = row
                cursor += row['length']
        if cursor != hi:
            raise ValueError('incomplete accepted Thumb extent')
        declared_entries.add(int(span['entry'], 0))
    roots = ({int(r['entry'], 0) for r in catalog['entries']} |
             {int(r['start'], 0) for r in extra['entries']} | declared_entries) & instructions.keys()
    if not roots:
        raise ValueError('no selected normal entries')
    dispatches = []
    transfer_evidence = load('indirect_transfer_provenance.json')
    for row in transfer_evidence['other_pc_writes']:
        if row['isa'] != 'thumb' or 'targets' not in row:
            continue
        at = int(row['site'], 0)
        if int.from_bytes(raw[at-0x4000:at-0x4000+2], 'little') != int(row['opcode'], 0):
            raise ValueError('bounded dispatch opcode mismatch')
        if any(int(a, 0) not in instructions for a in row['targets']):
            raise ValueError('bounded dispatch leaves accepted Thumb starts')
        dispatches.append(row)
    computed = {int(row['site'], 0): tuple(sorted({int(a, 0) for a in row['targets']})) for row in dispatches}
    first, *others = sorted(roots)
    account = analyze(raw, instructions, first, POINTERS, others, allow_external_edges=True, computed_targets=computed)
    bx_kinds = {r['site']: r['kind'] for r in transfer_evidence['bx_dispositions']}
    for row in account['exit_obligations']:
        if row['site'] in bx_kinds:
            row['condition'] = bx_kinds[row['site']]+'; retain prior indirect-transfer audit conditions'
    known = {s['site']: s for s in inventory['stores']}
    observed_fixed = []
    for row in account['stores']:
        source = known[row['site']]
        if source['form'] != row['form']:
            raise ValueError('raw store inventory disagreement')
        row['ida_owner_navigation_only'] = source['ida_owner']
        if row['status'] == 'fixed' and source['observations']:
            for obs in source['observations']:
                if int(obs['address'], 0) != int(row['address'], 0) or obs['size'] != row['byte_count']:
                    raise ValueError(('observed destination differs from conditional fixed result', row, obs))
            observed_fixed.append(row['site'])
    expected = {s['site'] for s in inventory['stores'] if s['isa'] == 'thumb' and int(s['site'], 0) in instructions}
    if {s['site'] for s in account['stores']} != expected:
        raise ValueError('selected Thumb stores not fully represented')
    unresolved = [s for s in account['stores'] if s['status'] in ('unresolved', 'unreached-by-local-CFG')]
    overlap = [s for s in account['stores'] if s['address'] and
               int(s['address'], 0) < 0x2005F4 and int(s['address'], 0)+s['byte_count'] > 0x2005F0]
    return {'format': 'quadzilla-thumb-store-provenance-v1', 'raw_sha256': SHA,
            'selected_instruction_starts': len(instructions), 'entry_roots': [hex(a) for a in sorted(roots)],
            'status_counts': dict(Counter(s['status'] for s in account['stores'])),
            'unresolved_owner_counts_navigation_only': dict(Counter(s['ida_owner_navigation_only'] or 'unowned' for s in unresolved)),
            'conditional_fixed_percent_overlaps': [s['site'] for s in overlap],
            'matched_observed_fixed_sites': observed_fixed,
            'excluded_store_sites': [{'site': s['site'], 'isa': s['isa'], 'instruction': s['instruction'],
                                      'reason': 'outside selected reviewed Thumb manifest domain'}
                                     for s in inventory['stores'] if int(s['site'], 0) not in instructions],
            'pointer_assumptions': {hex(a): hex(b) for a, b in POINTERS.items()},
            'bounded_dispatch_assumptions': [{'site': row['site'], 'table_cases': row['table_cases'],
                                              'distinct_targets': len(set(row['targets'])),
                                              'targets': sorted(set(row['targets']), key=lambda a: int(a, 0))} for row in dispatches],
            **account,
            'limits': ['normal entry roots from reviewed catalog, adjudications and manifest; discovery is not claimed exhaustive',
                       'computed exits and out-of-domain edges are obligations; missing dispatch roots can invalidate global exclusion',
                       'four provided computed-target sets retain the bounds/normal-state assumptions of the indirect-transfer audit',
                       'calls summarize preserved SP/R4-R11; callee preservation and writes require separate contracts',
                       'fixed results conditional on modeled entry/flow, immutable image and stable three peripheral pointers',
                       'stack addresses require valid disjoint frames; unresolved and unreached stores remain live obligations',
                       'ARM stores and copied executable template bodies are outside this selected Thumb domain',
                       'generic pointer ranges, DMA and corruption are not excluded by fixed-target rows',
                       'no whole-image writer exclusion, source-word stability or firmware completion claim']}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('image', type=Path)
    p.add_argument('--output', type=Path, required=True)
    args = p.parse_args(); raw = args.image.read_bytes()
    if hashlib.sha256(raw).hexdigest() != SHA:
        raise ValueError('source identity mismatch')
    doc = audit(raw)
    args.output.write_text(json.dumps(doc, indent=2)+'\n')
    print(f'{doc["selected_instruction_starts"]} Thumb starts; {len(doc["entry_roots"])} selected roots; '
          f'{doc["status_counts"]}; conditional P overlaps {doc["conditional_fixed_percent_overlaps"]}')


if __name__ == '__main__':
    main()
