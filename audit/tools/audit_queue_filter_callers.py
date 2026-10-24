#!/usr/bin/env python3
"""Bind queue-filter direct call sites and nearby argument setup to the image."""
import argparse
import hashlib
import json
from pathlib import Path

from audit_aid_tables import SHA

ROOT=Path(__file__).resolve().parents[2]
WINDOWS=((0x811A,0x812A,0x8126,'incoming_type2'),
         (0x8166,0x8176,0x8172,'incoming_type5'),
         (0x835A,0x83C8,0x83C4,'outgoing_group_a'),
         (0x842E,0x84F0,0x84EC,'outgoing_group_b'))

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('image',type=Path)
    parser.add_argument('--items',type=Path,default=ROOT/'audit/data/ida_image_items.json')
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    raw=args.image.read_bytes()
    ida=json.loads(args.items.read_text(encoding='utf-8'))
    if hashlib.sha256(raw).hexdigest()!=SHA or ida['raw_sha256']!=SHA or not ida['database_bytes_match']:
        raise ValueError('source identities differ')
    sites=[i['start'] for i in ida['items'] if i.get('decoded_direct_target')=='0x7f58']
    if sites!=[hex(site) for _,_,site,_ in WINDOWS]:
        raise ValueError('queue-filter call set changed')
    rows=[]
    for lo,hi,site,role in WINDOWS:
        context=[{'address':i['start'],'text':i.get('text'),
                  'decoded_direct_target':i.get('decoded_direct_target')}
                 for i in ida['items'] if lo<=int(i['start'],0)<hi and i['kind']=='ida_code']
        if not any(i['address']==hex(site) and i['decoded_direct_target']=='0x7f58' for i in context):
            raise ValueError('window lacks expected call')
        rows.append({'call':hex(site),'context':role,'window':[hex(lo),hex(hi)],
                     'items':context,'source_bytes_sha256':hashlib.sha256(raw[lo-0x4000:hi-0x4000]).hexdigest()})
    initialized=[]
    for address in (0x2007DB,0x2007DC,0x2007E0,0x2007E1):
        byte=raw[0x96E8-0x4000+address-0x200000]
        if byte!=0:
            raise ValueError('queue count initial value changed')
        initialized.append({'address':hex(address),'byte':byte})
    result={'format':'quadzilla-queue-filter-callers-v1','raw_sha256':SHA,'calls':rows,
            'initialized_count_fields':initialized,
            'limits':['context windows support local register setup only; full state-count provenance requires whole-caller review',
                      'IDA text is treated as evidence data and checked against the source image identity']}
    args.output.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(f'{len(rows)} source-bound direct filter calls')

if __name__=='__main__':
    main()
