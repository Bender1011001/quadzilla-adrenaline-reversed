#!/usr/bin/env python3
"""Inventory raw ARMv4T memory-store forms across every accepted instruction."""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path

from audit_execution_discovery import TEMPLATE_CODE, canonical
from audit_remaining_literals import literal_target
from emulate_integer_runtime import SHA


def store_form(isa, op):
    """Decode memory writes; coprocessor writes are explicitly distinguished."""
    if isa == 'thumb':
        if op & 0xF000 == 0x5000 and ((op >> 9) & 7) in (0, 1, 2):
            width = (4, 2, 1)[(op >> 9) & 7]
            return dict(kind='register-offset store', base=(op >> 3) & 7, source=op & 7,
                        width=width, offset_register=(op >> 6) & 7)
        if op & 0xE800 == 0x6000:
            width = 1 if op & 0x1000 else 4
            return dict(kind='immediate-offset store', base=(op >> 3) & 7, source=op & 7,
                        width=width, offset=((op >> 6) & 31)*width)
        if op & 0xF800 == 0x8000:
            return dict(kind='immediate-offset store', base=(op >> 3) & 7, source=op & 7,
                        width=2, offset=((op >> 6) & 31)*2)
        if op & 0xF800 == 0x9000:
            return dict(kind='SP-relative store', base=13, source=(op >> 8) & 7, width=4, offset=(op & 255)*4)
        if op & 0xFE00 == 0xB400:
            registers = [i for i in range(8) if op & (1 << i)] + ([14] if op & 0x100 else [])
            return dict(kind='PUSH register list', base=13, registers=registers, width=4,
                        offset=-4*len(registers), writeback=True)
        if op & 0xF800 == 0xC000:
            return dict(kind='STM register list', base=(op >> 8) & 7,
                        registers=[i for i in range(8) if op & (1 << i)], width=4, offset=0, writeback=True)
    elif isa == 'arm' and op >> 28 != 15:
        condition = op >> 28
        common = dict(base=(op >> 16) & 15, condition=condition)
        if op & 0x0FB00FF0 == 0x01000090:
            return common | dict(kind='SWP read/modify/write', source=op & 15,
                                 read_destination=(op >> 12) & 15, width=1 if op & 0x400000 else 4, offset=0)
        if op & 0x0E100000 == 0x08000000:
            registers = [i for i in range(16) if op & (1 << i)]
            pre, up = bool(op & (1 << 24)), bool(op & (1 << 23))
            offset = (4 if pre else 0) if up else -4*len(registers)+(0 if pre else 4)
            return common | dict(kind='STM register list', registers=registers, width=4,
                                 offset=offset, writeback=bool(op & (1 << 21)), user_bank=bool(op & (1 << 22)))
        half = op & 0x0E1000F0 == 0x000000B0
        single = op & 0x0C100000 == 0x04000000
        if half or single:
            immediate = bool(op & (1 << 22)) if half else not bool(op & (1 << 25))
            offset = (((op >> 4) & 0xF0) | (op & 15)) if half else op & 0xFFF
            pre = bool(op & (1 << 24))
            row = common | dict(kind='halfword store' if half else 'single-data store', source=(op >> 12) & 15,
                                width=2 if half else 1 if op & (1 << 22) else 4,
                                pre_index=pre, increment=bool(op & (1 << 23)),
                                writeback=not pre or bool(op & (1 << 21)))
            if immediate:
                row['offset'] = (offset if row['increment'] else -offset) if pre else 0
                row['index_adjustment'] = offset if row['increment'] else -offset
            else:
                row.update(offset_register=op & 15, shifted_offset=not half)
                if not pre:
                    row['offset'] = 0
            return row
        if op & 0x0E100000 == 0x0C000000:
            return common | dict(kind='coprocessor memory store', width=None)
    return None


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('image', type=Path)
    p.add_argument('--output', type=Path, required=True)
    args = p.parse_args()
    raw = args.image.read_bytes(); root = Path(__file__).resolve().parents[2]
    if hashlib.sha256(raw).hexdigest() != SHA:
        raise ValueError('source identity mismatch')
    def load(path):
        doc = json.loads((root / path).read_text())
        if doc.get('raw_sha256') != SHA:
            raise ValueError(('evidence identity mismatch', path))
        return doc
    manifest = load('audit/data/reviewed_instruction_ranges.json')
    instructions = {}; cache = {}
    spans = [(int(r['start'], 0), int(r['end'], 0), r['isa'], r['decoder_artifact']) for r in manifest['ranges']]
    spans += [(a, b, 'thumb', 'audit/data/startup_persistence_binaryninja.json') for a, b in TEMPLATE_CODE]
    for lo, hi, isa, path in spans:
        if path not in cache:
            cache[path] = load(path)
        block = next(r for r in cache[path]['ranges'] if int(r['start'], 0) <= lo and hi <= int(r['end'], 0))
        cursor = lo
        for i in block['instructions']:
            at = int(i['address'], 0)
            if not lo <= at < hi:
                continue
            if at != cursor or at in instructions:
                raise ValueError('accepted instruction overlap/gap')
            cursor += i['length']
            size = 2 if isa == 'thumb' else 4
            instructions[at] = dict(isa=isa, length=i['length'], text=i['text'],
                                    op=int.from_bytes(raw[at-0x4000:at-0x4000+size], 'little'))
        if cursor != hi:
            raise ValueError('incomplete accepted span')
    ida = load('audit/data/ida_image_items.json')
    items = {int(i['start'], 0): i for i in ida['items']}
    rows = []; disagreements = []; predecessors = {at+i['length']: at for at, i in instructions.items()}
    for at, ins in sorted(instructions.items()):
        form = store_form(ins['isa'], ins['op'])
        mnemonic = ins['text'].strip().split()[0].lower()
        text_store = mnemonic.startswith(('str', 'stm', 'push', 'swp', 'stc'))
        if bool(form) != text_store:
            disagreements.append(dict(site=hex(at), text=ins['text'], raw_form=form))
        if form is None:
            continue
        item = items.get(at, {})
        annotations = [r for r in item.get('data_refs', []) if 0x200000 <= int(r, 0) < 0x204000 or int(r, 0) >= 0xFFFA0000]
        row = dict(site=hex(at), isa=ins['isa'], instruction=ins['text'], form=form,
                   ida_owner=item.get('function'), ida_destination_annotations=annotations,
                   destination_status='SP addressing form; frame value/integrity required' if form['base'] == 13
                   else 'computed register destination; provenance required')
        # A deliberately narrow witness: the immediately preceding accepted
        # instruction loads this base register from an image literal. This is
        # conditional on straight-line execution, never a global target proof.
        previous = instructions.get(predecessors.get(at))
        if previous and previous['isa'] == ins['isa'] and 'offset' in form:
            op = previous['op']; prev_at = predecessors[at]
            target = literal_target(prev_at, ins['isa'], op)
            destination = ((op >> 8) & 7) if ins['isa'] == 'thumb' else (op >> 12) & 15
            unconditional = ins['isa'] == 'thumb' or op >> 28 == 14
            if target is not None and destination == form['base'] and unconditional and 0x4000 <= target <= 0xBCFC:
                base = int.from_bytes(raw[target-0x4000:target-0x4000+4], 'little')
                start = (base+form['offset']) & 0xFFFFFFFF
                count = len(form.get('registers', [form.get('source')]))
                row['adjacent_literal_witness'] = dict(seed_site=hex(prev_at), literal=hex(target), base_value=hex(base),
                                                       start=hex(start), byte_count=count*form['width'],
                                                       condition='preceding literal load executes immediately before this store')
        rows.append(row)
    if disagreements:
        raise ValueError(('raw/text store classification disagreement', disagreements[:10]))
    # Runtime evidence supplies observed addresses, without asserting all
    # possible executions have been observed.
    observed = {}
    paths = ['audit/data/aic_vector_installation.json', 'audit/data/knot_update_consumers.json',
             'audit/data/control_response_emulation.json', 'audit/data/control_scalar_integration.json',
             'audit/data/vector_table_alias.json']
    used = []
    def walk(obj, path):
        if isinstance(obj, dict):
            if all(k in obj for k in ('site', 'address', 'size', 'value')):
                try:
                    site = canonical(int(obj['site'], 0)); address = int(obj['address'], 0)
                    size = obj['size']
                    if site in store_sites and isinstance(size, int):
                        observed.setdefault(site, set()).add((address, size, path))
                except (TypeError, ValueError):
                    pass
            for value in obj.values():
                walk(value, path)
        elif isinstance(obj, list):
            for value in obj:
                walk(value, path)
    store_sites = {int(r['site'], 0) for r in rows}
    for path in paths:
        if (root / path).exists():
            walk(load(path), path); used.append(path)
    for row in rows:
        row['observations'] = [dict(address=hex(a), size=size, evidence=path)
                               for a, size, path in sorted(observed.get(int(row['site'], 0), set()))]
    counts = Counter(r['form']['kind'] for r in rows)
    doc = dict(format='quadzilla-store-inventory-v1', raw_sha256=SHA,
               accepted_instruction_starts=len(instructions), store_sites=len(rows), counts=dict(sorted(counts.items())),
               explicit_sp_base_sites=sum(r['form']['base'] == 13 for r in rows),
               adjacent_literal_witnesses=sum('adjacent_literal_witness' in r for r in rows),
               ida_annotated_sites=sum(bool(r['ida_destination_annotations']) for r in rows),
               observed_sites=len(observed), raw_text_disagreements=disagreements,
               observation_artifacts=used, stores=rows,
               limits=['inventory includes accepted image instructions and the known copied helper source bodies',
                       'raw addressing forms are not runtime effective addresses or execution-reachability proofs',
                       'IDA destination annotations remain tool interpretations, not proven register values',
                       'adjacent literal witnesses require straight-line execution; entry bypass and changed registers are not excluded',
                       'selected runtime artifacts are observations, not exhaustive address/value/size coverage',
                       'stack addressing still requires valid SP/frame bounds; aliased SP/register values are not excluded',
                       'does not include peripheral/DMA-initiated writes or undiscovered code/ISA alternatives',
                       'global writer exclusion, fault reachability and full firmware completion remain open'])
    args.output.write_text(json.dumps(doc, indent=2)+'\n')
    print({k: doc[k] for k in ('accepted_instruction_starts', 'store_sites', 'counts', 'explicit_sp_base_sites', 'adjacent_literal_witnesses', 'ida_annotated_sites', 'observed_sites')})


if __name__ == '__main__':
    main()
