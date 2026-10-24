#!/usr/bin/env python3
"""Adjudicate IDA combined constant-load items against exact Thumb halfwords."""
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
    bn=json.loads((ROOT/'audit/data/remaining_update_binaryninja.json').read_text(encoding='utf-8'))
    if hashlib.sha256(raw).hexdigest()!=SHA or ida['raw_sha256']!=SHA or bn['raw_sha256']!=SHA or not ida['database_bytes_match']:
        raise ValueError('source identity mismatch')
    items={r['start']:r for r in ida['items']}
    instructions={i['address']:i for r in bn['ranges'] for i in r['instructions']}
    macros=[]
    explained=set()
    for at,i in instructions.items():
        item=items.get(at)
        if item is None or int(item['end'],0)==int(at,0)+i['length']:
            continue
        address=int(at,0)
        if i['length']!=2 or int(item['end'],0)!=address+4 or item.get('mnemonic')!='MOVS':
            raise ValueError('unexpected IDA span mismatch')
        first,second=struct.unpack_from('<HH',raw,address-0x4000)
        if first&0xF800!=0x2000:
            raise ValueError('first instruction is not Thumb MOVS immediate')
        reg=(first>>8)&7
        initial=first&255
        if second&0xF800==0x3000 and (second>>8)&7==reg:
            value=(initial+(second&255))&0xFFFFFFFF
            operation='add_immediate'
        elif second&0xF800==0 and (second>>3)&7==reg and second&7==reg:
            value=(initial<<((second>>6)&31))&0xFFFFFFFF
            operation='logical_shift_left'
        else:
            raise ValueError('unrecognized second instruction')
        if value!=int(item['text'].rsplit('#',1)[1],0):
            raise ValueError('combined constant differs from IDA item')
        starts=(at,hex(address+2))
        macros.append({'start':at,'end':item['end'],'ida_text':item['text'],
            'halfwords':[hex(first),hex(second)],'register':reg,'operation':operation,
            'constructed_value':hex(value),'explicit_instructions':[instructions[s] for s in starts]})
        explained.update(starts)
    mismatches={at for at,i in instructions.items() if at not in items or
                int(items[at]['end'],0)!=int(at,0)+i['length']}
    if mismatches!=explained:
        raise ValueError('unexplained instruction boundary differences')
    result={'format':'quadzilla-ida-constant-macro-adjudication-v1','raw_sha256':SHA,
            'macro_items':macros,'explained_explicit_starts':sorted(explained,key=lambda x:int(x,0)),
            'ordinary_matching_starts':len(instructions)-len(explained),
            'unexplained_boundary_mismatches':[],
            'limits':['constant result and aggregate source extent verified; IDA item is not an individual instruction',
                      'condition flags follow explicit MOVS/ADDS/LSLS, not an imagined single MOVS']}
    args.output.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(f'{len(macros)} combined IDA items explain {len(explained)} explicit starts; no unexplained differences')


if __name__=='__main__':
    main()
