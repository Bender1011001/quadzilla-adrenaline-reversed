#!/usr/bin/env python3
"""Bound reviewed copy/fill callers and AID-directed payload destinations."""
import argparse
import hashlib
import json
from pathlib import Path

from emulate_payload_walker import WalkerRunner
from emulate_integer_runtime import SHA

ROOT = Path(__file__).resolve().parents[2]


def intervals(addresses):
    result = []
    for address in sorted(addresses):
        if result and result[-1][1] == address:
            result[-1][1] += 1
        else:
            result.append([address, address+1])
    return [dict(start=hex(a), end_exclusive=hex(b), byte_count=b-a) for a, b in result]


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('image', type=Path); p.add_argument('--output', type=Path, required=True)
    args = p.parse_args(); raw = args.image.read_bytes()
    if hashlib.sha256(raw).hexdigest() != SHA:
        raise ValueError('source identity mismatch')
    def word(a):
        return int.from_bytes(raw[a-0x4000:a-0x4000+4], 'little')
    if (word(0x4144), word(0x4148)) != (0x96C4, 0x96E8):
        raise ValueError('descriptor loop bounds changed')
    descriptors = []
    for at in range(0x96C4, 0x96E8, 12):
        count, destination, source = (word(at+i) for i in (0, 4, 8))
        descriptors.append(dict(descriptor=hex(at), helper='0x854c' if source == destination else '0x8530',
                                destination=hex(destination), source=hex(source), byte_count=count,
                                end_exclusive=hex(destination+count), fill_byte=0 if source == destination else None))
    discovery = json.loads((ROOT / 'audit/data/execution_discovery_audit.json').read_text())
    if discovery['raw_sha256'] != SHA:
        raise ValueError('call evidence identity mismatch')
    calls = [e for e in discovery['direct_transfers'] if e['kind'] == 'BL' and int(e['source_target'], 0) in (0x8530, 0x854C)]
    r = WalkerRunner(raw)
    rows = []; normal_union = set(); full_union = set(); cases = 0
    for aid in range(256):
        pointer = r.pointers[aid]
        width = 1 if aid < 75 else 2 if aid < 150 else 3 if aid < 185 else 4 if aid < 220 else 13
        payload = bytes([aid])+((bytes([13])+bytes([0xFE])*12) if aid >= 220 else bytes([0xFE])*width)
        observed = r.sample(payload)
        cases += 1
        stores = [w for w in observed['writes'] if int(w['address'], 0) < 0x201000]
        expected_addresses = list(range(pointer, pointer+width)) if pointer else []
        if [int(w['address'], 0) for w in stores] != expected_addresses:
            raise ValueError(('single-value footprint mismatch', aid, stores))
        extent = set(expected_addresses)
        if aid < 255:
            normal_union |= extent
        full_union |= extent
        rows.append(dict(aid=aid, table1_slot_in_bounds=aid < 255, pointer=hex(pointer),
                         maximum_single_value_bytes=width if pointer else 0,
                         end_exclusive=hex(pointer+width) if pointer else None,
                         kind='variable count, bounded by payload budget' if aid >= 220 else 'fixed width',
                         observed_store_count=len(stores), original_status=observed['status']))
    variable = []; digest = hashlib.sha256()
    for aid in (226, 255):
        for count in range(256):
            case = r.sample(bytes([aid, count])+bytes([0xFE])*12)
            cases += 1
            stores = [w for w in case['writes'] if int(w['address'], 0) < 0x201000]
            length = min(count, 13) if count else 13
            pointer = r.pointers[aid]
            if [int(w['address'], 0) for w in stores] != list(range(pointer, pointer+length)):
                raise ValueError(('variable extent mismatch', aid, count))
            digest.update(json.dumps(case, sort_keys=True, separators=(',', ':')).encode())
            if count in (0, 1, 5, 12, 13, 14, 255):
                variable.append(dict(aid=aid, count=count, writes=stores, status=case['status']))
    if min(full_union) != 0x200AEC or max(full_union) != 0x200BC6:
        raise ValueError('unexpected byte-domain staging envelope')
    doc = dict(format='quadzilla-generic-writer-footprints-v1', raw_sha256=SHA,
               descriptor_operations=descriptors, direct_copy_fill_calls=calls,
               config_copy=dict(source='0x10ff00', destination='0x2006cc', byte_count=44,
                                end_exclusive='0x2006f8', condition='first source byte equals 0xa5'),
               walker_cases=cases, mapped_in_bounds_aids=sum(r.pointers[a] != 0 for a in range(255)),
               rows=rows, in_bounds_union=intervals(normal_union), byte_domain_union=intervals(full_union),
               byte_domain_envelope=dict(start=hex(min(full_union)), end_exclusive=hex(max(full_union)+1)),
               variable_count_examples=variable, variable_cases_sha256=digest.hexdigest(),
               limits=['unmodified image pointer table and byte AID domain; payload budget capped to 14',
                       'unions concern resolved staging-data writes, not caller-provided list/count outputs or stack stores',
                       'single fixed values and all count bytes at maximum payload length are executed; mixed payload bounds follow the reviewed walker contract',
                       'direct copy/fill caller inventory does not exclude indirect calls or corrupted argument/descriptor state',
                       'does not establish physical delivery, framing/authentication acceptance or all firmware memory writers'])
    args.output.write_text(json.dumps(doc, indent=2)+'\n')
    print(f'{cases} original walker calls; {doc["mapped_in_bounds_aids"]} mapped in-bound AIDs; envelope {doc["byte_domain_envelope"]}')


if __name__ == '__main__':
    main()
