#!/usr/bin/env python3
"""Verify the shared AID-resolver literal pool against image words and IDA refs."""
import argparse
import hashlib
import json
import struct
from pathlib import Path

from audit_aid_tables import SHA

ROOT=Path(__file__).resolve().parents[2]
VALUES=(0xAD18,0xAE44,0xAF70,0xAFFC,0xB088,
        0xFFFFFED4,0xFFFFFDA8,0xFFFFFD1C,0xFFFFFC90)

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('image',type=Path)
    parser.add_argument('--items',type=Path,default=ROOT/'audit/data/ida_image_items.json')
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    raw=args.image.read_bytes()
    if hashlib.sha256(raw).hexdigest()!=SHA:
        raise ValueError('unexpected firmware image')
    ida=json.loads(args.items.read_text(encoding='utf-8'))
    if ida['raw_sha256']!=SHA or not ida['database_bytes_match']:
        raise ValueError('IDA export identity mismatch')
    rows=[]
    for index,expected in enumerate(VALUES):
        address=0x7CA0+index*4
        actual=struct.unpack_from('<I',raw,address-0x4000)[0]
        if actual!=expected:
            raise ValueError(f'literal value changed at {address:#x}')
        refs=[i['start'] for i in ida['items'] if hex(address) in i.get('data_refs',[])]
        if not refs or not any(0x7C68<=int(site,0)<0x7C9E for site in refs):
            raise ValueError(f'literal lacks resolver reference at {address:#x}')
        rows.append({'address':hex(address),'word':hex(actual),'reader_sites':refs})
    result={'format':'quadzilla-frame-reader-literals-v1','raw_sha256':SHA,
            'range':['0x7ca0','0x7cc4'],'words':rows,
            'classification':'shared AID resolver literal pool; 0x7c9e..0x7ca0 excluded',
            'limits':['IDA references confirm use sites; exact value roles follow the decoded resolver arithmetic']}
    args.output.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(f'{len(rows)} source-verified literal words and use sites')

if __name__=='__main__':
    main()
