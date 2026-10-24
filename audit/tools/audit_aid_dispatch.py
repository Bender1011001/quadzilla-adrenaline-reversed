#!/usr/bin/env python3
"""Decode source switch offsets and independently execute dispatch for all AIDs."""
import argparse
import hashlib
import json
import struct
from pathlib import Path

from audit_aid_tables import AidRunner,SHA
from model_compound_updates import HANDLERS

ROOT=Path(__file__).resolve().parents[2]


class DispatchRunner(AidRunner):
    def __init__(self,raw):
        super().__init__(raw)
        self.allowed_ranges=((0x6074,0x608C),)
        self.target=None

    def trace(self,cpu,address,size,user):
        if not 0x6074<=address<0x608C:
            self.target=address
            cpu.emu_stop()
            return
        super().trace(cpu,address,size,user)

    def select(self,aid):
        self.reset()
        self.target=None
        self.cpu.mem_write(0x203004,struct.pack('<I',0))
        self.cpu.mem_write(0x20300C,bytes([aid]))
        self.cpu.emu_start(0x6075,0x3F00,count=32)
        if self.target is None:
            raise RuntimeError('dispatch failed to reach target within instruction budget')
        return self.target


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('image',type=Path)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    raw=args.image.read_bytes()
    if hashlib.sha256(raw).hexdigest()!=SHA:
        raise ValueError('unexpected image')
    profiles=json.loads((ROOT/'audit/data/aid_table_audit.json').read_text(encoding='utf-8'))
    if profiles['raw_sha256']!=SHA:
        raise ValueError('profile/table audit source mismatch')
    runner=DispatchRunner(raw)
    rows=[]
    for aid in range(256):
        address=0x608C+2*(aid-9) if 9<=aid<=226 else None
        offset=struct.unpack_from('<h',raw,address-0x4000)[0] if address is not None else None
        expected=0x608E+offset if offset is not None else 0x604E
        actual=runner.select(aid)
        if actual!=expected:
            raise RuntimeError((aid,actual,expected))
        pointers=[hex(struct.unpack_from('<I',raw,base+4*aid-0x4000)[0])
                  for base in (0xA91C,0xAD18)]
        row=profiles['rows'][aid]
        if pointers!=[row['table1']['pointer'],row['table2']['pointer']]:
            raise ValueError('pointer audit mismatch')
        rows.append({'aid':aid,'table_address':None if address is None else hex(address),
                     'signed_offset':offset,'target':hex(actual),
                     'default_path':actual==0x604E,'profile_names':row['profile_names'],
                     'staging_pointer':pointers[0],'response_pointer':pointers[1],
                     'pointer_slot_in_bounds':aid<255,
                     'review_disposition':'selection/default loop only' if actual==0x604E else
                         'bounded update handler reviewed' if aid in (9,15)+HANDLERS else
                         'target established; handler semantics pending',
                     'handler_review': 'docs/COMPOUND_AID_UPDATE_REVIEW.md' if aid in HANDLERS else
                         'docs/AID_DISPATCH_SELECTOR_UPDATES.md' if aid in (9,15) else None})
    result={'format':'quadzilla-aid-validation-dispatch-v1','raw_sha256':SHA,
            'table_range':['0x608c','0x6240'],'table_bytes':436,'slots':218,
            'offset_rule':'signed little-endian halfword; target = 0x608e + offset',
            'out_of_range_rule':'u32(AID-9) > 217 selects default 0x604e',
            'executed_selector_cases':256,'nondefault_handlers':sum(not r['default_path'] for r in rows),
            'reference_mismatches':0,'rows':rows,
            'reviewed_nondefault_handlers':2+len(HANDLERS),
            'pending_nondefault_handlers':sum(not r['default_path'] and r['handler_review'] is None for r in rows),
            'limits':['selector execution stops before any handler instruction',
                      'default in this dispatcher does not imply no staging or response support',
                      'profile declarations are descriptive; pointer presence is not complete parameter semantics',
                      '44 other nondefault handler accounts remain pending complete review']}
    args.output.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print('256 selector destinations agree; 57 nondefault handlers; 436 source-bound table bytes')


if __name__=='__main__':
    main()
