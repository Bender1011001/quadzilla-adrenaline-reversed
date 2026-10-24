#!/usr/bin/env python3
"""Adjudicate IDA's invalid-ISA item spanning the queue copier entry."""
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
    parser.add_argument('--decode',type=Path,default=ROOT/'audit/data/frame_reader_binaryninja.json')
    parser.add_argument('--items',type=Path,default=ROOT/'audit/data/ida_image_items.json')
    parser.add_argument('--emulation',type=Path,default=ROOT/'audit/data/frame_reader_emulation.json')
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    raw=args.image.read_bytes()
    if hashlib.sha256(raw).hexdigest()!=SHA:
        raise ValueError('unexpected image')
    decode=json.loads(args.decode.read_text(encoding='utf-8'))
    ida=json.loads(args.items.read_text(encoding='utf-8'))
    emu=json.loads(args.emulation.read_text(encoding='utf-8'))
    if any(d['raw_sha256']!=SHA for d in (decode,ida,emu)) or not ida['database_bytes_match']:
        raise ValueError('evidence identities differ')
    starts=[i for r in decode['ranges'] for i in r['instructions']]
    items={i['start']:i for i in ida['items']}
    ordinary=[]
    for i in starts:
        item=items.get(i['address'])
        if item and int(item['end'],0)==int(i['address'],0)+i['length']:
            ordinary.append(i['address'])
        elif i['address']!='0x7fd8':
            raise ValueError(f'unexplained decode boundary at {i["address"]}')
    overlap=items['0x7fd6']
    prefix,entry=struct.unpack_from('<HH',raw,0x7FD6-0x4000)
    callers=[i['start'] for i in ida['items'] if i.get('decoded_direct_target')=='0x7fd8']
    if (len(ordinary),prefix,entry,overlap['end'],overlap['mnemonic'])!=(197,0xFFFF,0xB430,'0x7fda','VSRI.32'):
        raise ValueError('entry boundary evidence changed')
    if len(callers)<7 or '0x7fd8' not in emu['visited']:
        raise ValueError('entry lacks calls or original-byte execution')
    result={'format':'quadzilla-frame-reader-boundary-v1','raw_sha256':SHA,
            'ordinary_matching_starts':len(ordinary),
            'correction':{'entry':'0x7fd8','prefix_halfword':hex(prefix),
                'entry_halfword':hex(entry),'overlapping_ida_item':overlap,
                'decoded_direct_call_sites':callers,
                'disposition':'Thumb PUSH {R4,R5} entry supported; preceding FFFF remains unclassified'},
            'unexplained_boundary_mismatches':[]}
    args.output.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(f'{len(ordinary)} ordinary starts and one corrected helper entry')

if __name__=='__main__':
    main()
