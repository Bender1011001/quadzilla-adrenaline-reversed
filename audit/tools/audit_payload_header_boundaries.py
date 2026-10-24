#!/usr/bin/env python3
"""Adjudicate IDA invalid-ISA items overlapping the two Thumb header getters."""
import argparse
import hashlib
import json
import struct
from pathlib import Path
from audit_aid_tables import SHA
ROOT=Path(__file__).resolve().parents[2]


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('image',type=Path)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    raw=args.image.read_bytes()
    ida=json.loads((ROOT/'audit/data/ida_image_items.json').read_text(encoding='utf-8'))
    bn=json.loads((ROOT/'audit/data/short_value_context_binaryninja.json').read_text(encoding='utf-8'))
    if hashlib.sha256(raw).hexdigest()!=SHA or ida['raw_sha256']!=SHA or bn['raw_sha256']!=SHA or not ida['database_bytes_match']:
        raise ValueError('source mismatch')
    items={r['start']:r for r in ida['items']}
    corrections=[]
    ordinary=0
    for block in bn['ranges']:
        if block['start'] not in ('0x7bcc','0x7be8','0x7bf0'):
            continue
        for i in block['instructions']:
            address=int(i['address'],0)
            item=items.get(i['address'])
            if item is not None and int(item['end'],0)==address+i['length']:
                ordinary+=1
                continue
            overlap=next(r for r in ida['items'] if int(r['start'],0)<address<int(r['end'],0))
            prefix,opcode=struct.unpack_from('<HH',raw,address-2-0x4000)
            if address not in (0x7BE8,0x7BF0) or prefix!=0xFFFF or opcode!=0x7800 or overlap['mnemonic']!='VTBL.8':
                raise ValueError('unexplained header boundary mismatch')
            callers=[r['start'] for r in ida['items'] if r.get('decoded_direct_target')==i['address']]
            if not callers:
                raise ValueError('getter lacks decoded direct-call evidence')
            corrections.append({'entry':i['address'],'explicit_instruction':i,
                'prefix_halfword':hex(prefix),'entry_halfword':hex(opcode),
                'overlapping_ida_item':overlap,'direct_call_sites':callers,
                'disposition':'Thumb LDRB entry supported; preceding FFFF halfword remains outside this instruction review'})
    result={'format':'quadzilla-header-getter-boundary-review-v1','raw_sha256':SHA,
            'ordinary_matching_starts':ordinary,'corrections':corrections,
            'unexplained_boundary_mismatches':[],
            'limits':['ARM7TDMI has no NEON; IDA VTBL.8 item is not accepted as target instructions',
                      'explicit Thumb decode, direct targets and original-byte execution support the getter entries',
                      'preceding FFFF halfwords are not promoted to reviewed padding here']}
    args.output.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(f'{ordinary} ordinary starts and {len(corrections)} getter corrections; no unexplained differences')


if __name__=='__main__':
    main()
