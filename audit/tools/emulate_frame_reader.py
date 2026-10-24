#!/usr/bin/env python3
"""Execute original table-2 response reading and framing on synthetic SRAM."""
import argparse
import hashlib
import json
import random
import struct
import sys
from pathlib import Path

from audit_aid_tables import AidRunner,SHA

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools'))
from model_frame_reader import read_values,build_frame

RANGES=((0x7B60,0x7BCA),(0x7BF8,0x7C1A),(0x7C68,0x7C9E),
        (0x7D80,0x7E64),(0x7EB4,0x7EFC),(0x7FD8,0x800A))


class FrameRunner(AidRunner):
    def __init__(self,raw):
        super().__init__(raw)
        self.allowed_ranges=RANGES
        self.pointers={aid:struct.unpack_from('<I',raw,0xAD18+4*aid-0x4000)[0]
                       for aid in range(256)}
        self.stack_stores=[]
        self.record=False
        self.cpu.hook_add(self.uc.UC_HOOK_MEM_WRITE,self.on_write)

    def on_write(self,cpu,access,address,size,value,user):
        if self.record and 0x202fc0<=address<0x203000:
            self.stack_stores.append({'pc':hex(cpu.reg_read(self.arm.UC_ARM_REG_PC)),
                                      'address':hex(address),'size':size,
                                      'value':value&((1<<(size*8))-1)})

    def setup(self,aids):
        self.reset()
        self.visited.clear()
        self.stack_stores.clear()
        self.cpu.mem_write(0x201000,bytes(aids)+bytes([0xC7])*(256-len(aids)))
        self.cpu.mem_write(0x201100,bytes([len(aids)]))
        self.cpu.mem_write(0x201200,bytes([0xAB])+bytes([0xCC])*31)
        sources={}
        for aid in sorted(set(aids)):
            pointer=self.pointers[aid]
            if 0x200000<=pointer<0x204000:
                # Distinct data for this controlled call, including the first
                # byte used as width input. This is synthetic working SRAM.
                value=bytes([(aid*13+1)&255,(aid*7+2)&255,(aid*3+3)&255,(aid+4)&255])
                self.cpu.mem_write(pointer,value)
        for aid in set(aids):
            pointer=self.pointers[aid]
            sources[aid]=bytes(self.cpu.mem_read(pointer,4)) if 0x200000<=pointer<0x204000 else None
        self.record=True
        return sources

    def sample(self,aids,kind,builder):
        sources=self.setup(aids)
        entry=0x7EB4 if builder else 0x7D80
        output=self.call(entry,[0x201200,kind,0x201000,0x201100])
        if output['status']!='returned':
            raise RuntimeError((aids,kind,builder,output))
        remaining=self.cpu.mem_read(0x201100,1)[0]
        deferred=bytes(self.cpu.mem_read(0x201000,remaining))
        if builder:
            expected_frame,expected_deferred,expected_status=build_frame(aids,kind,sources)
            actual_frame=bytes(self.cpu.mem_read(0x201200,len(expected_frame)))
            if (output['r0'],actual_frame,deferred)!=(expected_status,expected_frame,expected_deferred):
                raise RuntimeError((aids,kind,'builder',output,actual_frame.hex(),deferred.hex(),
                                    expected_frame.hex(),expected_deferred.hex()))
            result={'frame':actual_frame.hex(),'return':output['r0']}
        else:
            expected_payload,expected_deferred=read_values(aids,kind,sources)
            actual_payload=bytes(self.cpu.mem_read(0x201200,len(expected_payload)))
            if (output['r0'],actual_payload,deferred)!=(len(expected_payload),expected_payload,expected_deferred):
                raise RuntimeError((aids,kind,'reader',output,actual_payload.hex(),deferred.hex(),
                                    expected_payload.hex(),expected_deferred.hex()))
            result={'payload':actual_payload.hex(),'return':output['r0']}
        result.update({'aids':bytes(aids).hex(),'kind':kind,'deferred':deferred.hex(),
                       'visited':[hex(a) for a in sorted(self.visited)]})
        return result

    def oversized_deferred(self,count):
        self.setup([154]*count)
        result=self.call(0x7D80,[0x201200,5,0x201000,0x201100])
        stores=[w for w in self.stack_stores if w['pc']=='0x7e30']
        return {'count':count,'result':result,'deferred_count':self.cpu.mem_read(0x201100,1)[0],
                'last_deferred_stack_store':stores[-1] if stores else None,
                'writes_saved_register_region':any(int(w['address'],0)>=0x202fe0 for w in stores),
                'visited':[hex(a) for a in sorted(self.visited)]}

    def queue_copy(self,count,dest_valid=True):
        self.reset()
        self.visited.clear()
        data=bytes((i*29+7)&255 for i in range(255))
        self.cpu.mem_write(0x201000,data)
        self.cpu.mem_write(0x201100,b'\xAA')
        self.cpu.mem_write(0x201200,bytes([0xCC])*16)
        dest=0x201200 if dest_valid else 0
        outcome=self.call(0x7FD8,[dest,0x201100,0x201000,count])
        if outcome['status']!='returned':
            raise RuntimeError((count,dest_valid,outcome))
        expected_n=min(count,14) if dest_valid and count else 0
        expected_count=expected_n if expected_n else 0xAA
        expected_bytes=data[:expected_n]+bytes([0xCC])*(16-expected_n)
        actual_count=self.cpu.mem_read(0x201100,1)[0]
        actual_bytes=bytes(self.cpu.mem_read(0x201200,16))
        if (actual_count,actual_bytes)!=(expected_count,expected_bytes):
            raise RuntimeError((count,dest_valid,actual_count,actual_bytes.hex(),
                                expected_count,expected_bytes.hex()))
        return {'count_arg':count,'dest_valid':dest_valid,'count_out':actual_count,
                'buffer':actual_bytes.hex(),'visited':[hex(a) for a in sorted(self.visited)]}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('image',type=Path)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    raw=args.image.read_bytes()
    if hashlib.sha256(raw).hexdigest()!=SHA:
        raise ValueError('unexpected firmware image')
    r=FrameRunner(raw)
    digest=hashlib.sha256()
    seen=set()
    examples=[]
    cases=0
    def run(aids,kind,builder,keep=False):
        nonlocal cases
        row=r.sample(aids,kind,builder)
        cases+=1
        seen.update(int(a,0) for a in row['visited'])
        digest.update(json.dumps(row,sort_keys=True,separators=(',',':')).encode())
        if keep:
            examples.append(row)
    for aid in range(255):
        for kind in (1,2,4,5):
            for builder in (False,True):
                run([aid],kind,builder,keep=aid in (9,75,85,149,150,184,185,219,220,226,254))
    for n in range(15):
        for aid in (9,85,154,226):
            for kind in (1,2,4,5):
                run([aid]*n,kind,True,keep=n in (0,1,6,7,14))
    rng=random.Random(0x7D80)
    for i in range(2048):
        aids=[rng.randrange(255) for _ in range(rng.randrange(15))]
        run(aids,rng.choice((0,1,2,4,5,15)),i%2==0,keep=i<12)
    copy_examples=[]
    for count in range(256):
        row=r.queue_copy(count)
        seen.update(int(a,0) for a in row['visited'])
        if count in (0,1,13,14,15,16,255):
            copy_examples.append(row)
    null_destination=r.queue_copy(14,False)
    seen.update(int(a,0) for a in null_destination['visited'])
    overflow=[r.oversized_deferred(n) for n in (14,15,16,17,20,21,22)]
    if not all(not row['writes_saved_register_region'] for row in overflow[:3]):
        raise RuntimeError('local rejection-list boundary changed')
    if not all(row['writes_saved_register_region'] for row in overflow[3:]):
        raise RuntimeError('saved-register write boundary changed')
    if overflow[-1]['result']['status']!='emulator_fault' or overflow[-1]['result']['fault']['pc']!='0x7e48':
        raise RuntimeError('oversized synthetic caller result changed')
    r.setup([255])
    invalid255=r.call(0x7EB4,[0x201200,5,0x201000,0x201100])
    if invalid255['status']!='emulator_fault' or invalid255['fault']['pc']!='0x7de8':
        raise RuntimeError('AID255 alias result changed')
    result={'format':'quadzilla-frame-reader-emulation-v1','raw_sha256':SHA,
            'cpu':'ARM926 functional surrogate','bounded_cases':cases,
            'reference_mismatches':0,'trace_sha256':digest.hexdigest(),
            'examples':examples,'queue_copy_cases':257,
            'queue_copy_examples':copy_examples,'null_destination':null_destination,
            'visited':[hex(a) for a in sorted(seen)],
            'oversized_synthetic_caller':overflow,'aid255_alias':invalid255,
            'limits':['bounded model and cases supply at most 14 AIDs in synthetic SRAM',
                      'oversized rejection-list probes bypass normal caller state',
                      'unmapped faults are emulator observations, not physical device outcomes',
                      'source values are synthetic; framing/queue state outside these helpers remains separate']}
    args.output.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(f'{cases} bounded reader/builder calls; {len(seen)} starts; zero model differences')


if __name__=='__main__':
    main()
