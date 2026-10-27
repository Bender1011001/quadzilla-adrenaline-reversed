#!/usr/bin/env python3
"""Reconcile callback flag helpers and numeric-runtime store-address obligations."""
import argparse
from collections import defaultdict, deque
import hashlib
import json
from pathlib import Path

from audit_callback_store_contracts import analyze
from audit_indirect_transfers import pc_write_kind
from audit_remaining_literals import literal_target
from audit_store_inventory import store_form
from emulate_integer_runtime import SHA

ROOT = Path(__file__).resolve().parents[2]


def arm_edges(at, op):
    condition = op >> 28
    if condition == 15:
        raise ValueError('unmodeled ARM condition encoding')
    if op & 0x0FFFFFF0 == 0x012FFF10:
        if op & 15 != 14:
            raise ValueError('non-LR indirect runtime transfer')
        return ([at+4] if condition != 14 else []), 'LR-return'
    if op & 0x0E000000 == 0x0A000000:
        delta = op & 0xFFFFFF
        if delta & 0x800000:
            delta -= 0x1000000
        targets = [at+8+4*delta]
        if condition != 14 or op & 0x1000000:
            targets.append(at+4)
        return targets, 'direct-call' if op & 0x1000000 else 'direct-branch'
    if pc_write_kind('arm', op) or op & 0x0F000000 == 0x0F000000:
        raise ValueError('unmodeled runtime PC write or software interrupt')
    return [at+4], 'sequential'


def audit(raw):
    def load(name):
        d = json.loads((ROOT / 'audit/data' / name).read_text())
        if d['raw_sha256'] != SHA:
            raise ValueError(('evidence identity mismatch', name))
        return d
    def word(at):
        return int.from_bytes(raw[at-0x4000:at-0x4000+4], 'little')
    callbacks = load('callback_store_contracts.json')
    obligations = [c for b in callbacks['bodies'] for c in b['callee_obligations']]
    targets = {int(c['target'], 0) for c in obligations}
    soft = load('soft_float_binaryninja.json')
    thunks = {int(t['entry'], 0): t for t in load('soft_float_emulation.json')['thunks']}
    wrappers = []; arm_roots = []
    for entry in sorted(targets & thunks.keys()):
        t = thunks[entry]
        end = int(t['instruction_end'], 0)
        words = [int.from_bytes(raw[a-0x4000:a-0x4000+2], 'little') for a in range(entry, end, 2)]
        expected = [0x4B00, 0x4718] if end-entry == 4 else [0xB408, 0x4B02, 0x469C, 0xBC08, 0x4760]
        if words != expected:
            raise ValueError('numeric wrapper encoding differs')
        seed = entry if len(words) == 2 else entry+2
        literal = literal_target(seed, 'thumb', words[0 if len(words) == 2 else 1])
        target = word(literal)
        if literal != int(t['literal'], 0) or target != int(t['target'], 0) or target & 3:
            raise ValueError('wrapper target/literal mismatch')
        wrappers.append({'entry': hex(entry), 'target': hex(target), 'literal': hex(literal),
                         'stack_push_bytes': 4 if len(words) == 5 else 0,
                         'transfer': 'fixed ARM target via R3' if len(words) == 2 else 'fixed ARM target via R12; R3 saved/restored'})
        arm_roots.append(target)
    flags = []
    flag_decode = load('tc2_flag_helper_binaryninja.json')
    for entry in sorted(targets-thunks.keys()):
        block = next(r for r in flag_decode['ranges'] if int(r['start'], 0) == entry)
        rows = {int(i['address'], 0): i for i in block['instructions']}
        account = analyze(raw, rows, entry, {})
        if account['unsupported_starts'] or account['callee_obligations'] or any(s['status'] != 'fixed' for s in account['stores']):
            raise ValueError('flag helper store contract incomplete')
        flags.append({'entry': hex(entry), **account})
    instructions = {}
    for block in soft['ranges'][:2]:
        if block['architecture'] != 'armv7':
            raise ValueError('unexpected numeric decoder ISA label')
        cursor = int(block['start'], 0)
        for row in block['instructions']:
            at = int(row['address'], 0)
            if at != cursor or row['length'] != 4:
                raise ValueError('runtime instruction extent mismatch')
            instructions[at] = row
            cursor += 4
        if cursor != int(block['end'], 0):
            raise ValueError('runtime block end mismatch')
    graph = {}; predecessors = defaultdict(set); runtime_stores = []
    for at, row in sorted(instructions.items()):
        op = word(at)
        successors, kind = arm_edges(at, op)
        for dest in successors:
            if dest not in instructions:
                raise ValueError(('numeric edge leaves accepted runtime', hex(at), hex(dest)))
            predecessors[dest].add(at)
        graph[at] = successors
        form = store_form('arm', op)
        if form:
            if form['base'] == 13 and form['kind'] == 'STM register list' and not form['user_bank']:
                runtime_stores.append({'site': hex(at), 'instruction': row['text'], 'form': form,
                                       'status': 'current-SP-relative; valid nonaliasing runtime frame required'})
            elif at == 0x8964 and form['base'] == 2 and form['source'] == 12 and form['width'] == 1 and form['offset'] == 0:
                runtime_stores.append({'site': hex(at), 'instruction': row['text'], 'form': form,
                                       'status': 'fixed status-byte destination', 'address': '0x200af8'})
            else:
                raise ValueError(('unaccounted numeric-runtime store', hex(at), form))
    # A unique intraregion predecessor chain forces the literal seed before
    # the sole nonstack store, under fixed normal entry and return integrity.
    for at, expected in ((0x895C, {0x8958}), (0x8960, {0x895C}), (0x8964, {0x8960})):
        if predecessors[at] != expected or at in arm_roots:
            raise ValueError('status literal no longer dominates the store chain')
    if [word(a) for a in (0x8958, 0x895C, 0x8960, 0x8964, 0x896C)] != [
            0xE59F200C, 0xE5D2C000, 0xE38CC001, 0xE5C2C000, 0x200AF8]:
        raise ValueError('status-byte chain differs')
    external_direct_entries = [t for t in load('execution_discovery_audit.json')['direct_transfers']
                               if int(t['source_target'], 0) in (0x895C, 0x8960, 0x8964)]
    if external_direct_entries:
        raise ValueError('direct entry bypasses status literal chain')
    reachable = set(); pending = deque(arm_roots)
    while pending:
        at = pending.popleft()
        if at in reachable:
            continue
        reachable.add(at); pending.extend(graph[at])
    return {'format': 'quadzilla-callback-transitive-stores-v1', 'raw_sha256': SHA,
            'call_sites_accounted': len(obligations), 'numeric_wrappers': wrappers, 'flag_helpers': flags,
            'runtime_instruction_superset': len(instructions), 'runtime_reachable_overapproximation': len(reachable),
            'runtime_stores_superset': runtime_stores,
            'status_store_predecessor_chain': ['0x8958', '0x895c', '0x8960', '0x8964'],
            'status_destination': '0x200af8',
            'limits': ['fixed normal wrapper entries and immutable image literals/code assumed',
                       'whole ARM numeric region is a conservative store superset, not all claimed reachable',
                       'direct calls include return fallthrough; LR returns require valid call frames',
                       'SP-relative stores require valid stack placement disjoint from reviewed globals',
                       'caller register-preservation, stack/return integrity and mutable-vector assumptions remain conditions',
                       'address footprint does not establish numeric correctness; prior soft-float mismatches remain',
                       'not DMA, arbitrary entry/corruption, interrupt routing or hardware-output proof']}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('image', type=Path)
    p.add_argument('--output', type=Path, required=True)
    args = p.parse_args(); raw = args.image.read_bytes()
    if hashlib.sha256(raw).hexdigest() != SHA:
        raise ValueError('source identity mismatch')
    doc = audit(raw)
    args.output.write_text(json.dumps(doc, indent=2)+'\n')
    print(f'{len(doc["numeric_wrappers"])} numeric wrappers; {len(doc["flag_helpers"])} flag helpers; '
          f'{len(doc["runtime_stores_superset"])} ARM runtime stores; fixed nonstack status 0x200AF8')


if __name__ == '__main__':
    main()
