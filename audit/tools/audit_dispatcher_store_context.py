#!/usr/bin/env python3
"""Resolve dispatcher-local store addresses under its ordinary parent frame."""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path

from audit_callback_store_contracts import analyze
from emulate_integer_runtime import SHA

ROOT = Path(__file__).resolve().parents[2]
FRAME_TARGETS = (0x6042, 0x6048, 0x604C, 0x604E)
CALLER_STACK_CONTRACTS = (0x4384, 0x47B0, 0x6B08, 0x6B10, 0x7128, 0x7138, 0x7160, 0x8574, 0x8584)


def audit(raw):
    def load(name):
        d = json.loads((ROOT / 'audit/data' / name).read_text())
        if d['raw_sha256'] != SHA:
            raise ValueError('evidence source identity mismatch')
        return d
    manifest = load('reviewed_instruction_ranges.json')
    instructions = {}; cache = {}
    for span in manifest['ranges']:
        lo, hi = int(span['start'], 0), int(span['end'], 0)
        if span['isa'] != 'thumb' or not 0x601C <= lo < 0x6A48:
            continue
        path = span['decoder_artifact']
        if path not in cache:
            cache[path] = json.loads((ROOT / path).read_text())
            if cache[path]['raw_sha256'] != SHA:
                raise ValueError('decoder identity mismatch')
        block = next(r for r in cache[path]['ranges'] if int(r['start'], 0) <= lo and hi <= int(r['end'], 0))
        cursor = lo
        for row in block['instructions']:
            at = int(row['address'], 0)
            if lo <= at < hi:
                if at != cursor or at in instructions:
                    raise ValueError('dispatcher instruction overlap/gap')
                instructions[at] = row; cursor += row['length']
        if cursor != hi:
            raise ValueError('dispatcher instruction extent mismatch')
    prior = load('indirect_transfer_provenance.json')
    dispatch = next(r for r in prior['other_pc_writes'] if r['site'] == '0x608a')
    if int.from_bytes(raw[0x608A-0x4000:0x608C-0x4000], 'little') != int(dispatch['opcode'], 0):
        raise ValueError('dispatcher opcode mismatch')
    targets = tuple(sorted({int(a, 0) for a in dispatch['targets']}))
    contracts = {target: {'preserves_caller_stack': True,
                         'preserved_caller_registers': [2, 3] if target in (0x8574, 0x8584) else []}
                 for target in CALLER_STACK_CONTRACTS}
    contract_evidence = ['integer_runtime_emulation.json', 'control_helper_emulation.json',
                         'soft_float_emulation.json', 'callback_transitive_stores.json']
    for name in contract_evidence:
        load(name)
    account = analyze(raw, instructions, 0x601C, {}, computed_targets={0x608A: targets},
                      frame_transfer_targets=FRAME_TARGETS, callee_contracts=contracts, finite_joins=True)
    before = load('thumb_store_provenance.json')
    previous = {s['site']: s for s in before['stores']}
    changed = [s['site'] for s in account['stores']
               if previous[s['site']]['status'] == 'unresolved' and s['status'] != 'unresolved']
    by_site = {s['site']: s for s in account['stores']}
    observed = {}
    def inspect(obj):
        if isinstance(obj, dict):
            site = obj.get('pc', obj.get('site'))
            if site in by_site and 'address' in obj and 'size' in obj:
                row = by_site[site]
                allowed = row.get('addresses', [row['address']] if row['address'] else [])
                if obj['address'] not in allowed or obj['size'] != row['byte_count']:
                    raise ValueError(('handler observation violates contextual address contract', row, obj))
                observed.setdefault(site, set()).add(obj['address'])
            for value in obj.values():
                inspect(value)
        elif isinstance(obj, list):
            for value in obj:
                inspect(value)
    observations = ['selector_update_emulation.json', 'compound_update_emulation.json', 'remaining_update_emulation.json']
    for name in observations:
        inspect(load(name))
    return {'format': 'quadzilla-dispatcher-store-context-v1', 'raw_sha256': SHA,
            'entry': '0x601c', 'selected_starts': len(instructions),
            'frame_transfer_targets': [hex(a) for a in FRAME_TARGETS],
            'callee_contract_assumptions': {hex(a): c for a, c in contracts.items()},
            'callee_contract_evidence': contract_evidence,
            'status_counts': dict(Counter(s['status'] for s in account['stores'])),
            'previous_unresolved_now_classified': changed, **account,
            'runtime_observations': {site: sorted(values, key=lambda a: int(a, 0)) for site, values in sorted(observed.items())},
            'observation_artifacts': observations,
            'limits': ['ordinary 0x601C prologue/frame, not arbitrary standalone continuation entries',
                       'four parent-frame BL targets retain register/stack state and do not return to BL fallthrough',
                       'bounded dispatcher target set retains prior table/index assumptions',
                       'nine specified ordinary callees retain caller-frame facts under their reviewed private-stack/fixed-global contracts',
                       'integer division additionally preserves R2/R3; numeric tail wrappers do not imply return preservation of operand registers',
                       'finite integer/address joins capped at 64 alternatives; overflow widens to unknown, never truncates alternatives',
                       'local handler stores only; receive walker, default initializer and other callees require separate accounts',
                       'no global writer exclusion, interrupt, DMA, physical delivery or firmware-completion claim']}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('image', type=Path)
    p.add_argument('--output', type=Path, required=True)
    args = p.parse_args(); raw = args.image.read_bytes()
    if hashlib.sha256(raw).hexdigest() != SHA:
        raise ValueError('source identity mismatch')
    doc = audit(raw)
    args.output.write_text(json.dumps(doc, indent=2)+'\n')
    print(f'{doc["selected_starts"]} starts; {doc["status_counts"]}; '
          f'{len(doc["previous_unresolved_now_classified"])} previous unresolved sites classified')


if __name__ == '__main__':
    main()
