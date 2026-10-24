#!/usr/bin/env python3
"""Execute original outgoing AID-list filter with synthetic queue arrays."""
import argparse
import hashlib
import json
import random
import sys
from pathlib import Path

from audit_aid_tables import AidRunner,SHA

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools'))
from model_queue_filter import filter_aids


class FilterRunner(AidRunner):
    def __init__(self,raw):
        super().__init__(raw)
        self.allowed_ranges=((0x7F58,0x7FD6),)
        self.stack_writes=[]
        self.record=False
        self.cpu.hook_add(self.uc.UC_HOOK_MEM_WRITE,self.write)

    def write(self,cpu,access,address,size,value,user):
        if self.record and 0x202fd4<=address<0x203000:
            self.stack_writes.append({'pc':hex(cpu.reg_read(self.arm.UC_ARM_REG_PC)),
                'address':hex(address),'size':size,'value':value&((1<<(size*8))-1)})

    def setup(self,current,remove):
        self.reset()
        self.visited.clear()
        self.stack_writes.clear()
        self.cpu.mem_write(0x201000,bytes(remove)+bytes([0xC7])*(256-len(remove)))
        self.cpu.mem_write(0x201100,bytes([len(current)]))
        self.cpu.mem_write(0x201200,bytes(current)+bytes([0xCC])*(256-len(current)))
        self.record=True

    def sample(self,current,remove,count_arg=None,destination_valid=True):
        self.setup(current,remove)
        count_arg=len(remove) if count_arg is None else count_arg
        result=self.call(0x7F58,[0x201200 if destination_valid else 0,
                                      0x201100,0x201000,count_arg])
        if result['status']!='returned':
            raise RuntimeError((current,remove,count_arg,destination_valid,result))
        expected=filter_aids(current,remove,count_arg,destination_valid)
        count=self.cpu.mem_read(0x201100,1)[0]
        output=bytes(self.cpu.mem_read(0x201200,count))
        if (result['r0'],count,output)!=(len(expected),len(expected),expected):
            raise RuntimeError((current,remove,count_arg,destination_valid,result,count,
                                output.hex(),expected.hex()))
        return {'current':bytes(current).hex(),'remove':bytes(remove).hex(),
                'count_arg':count_arg,'destination_valid':destination_valid,
                'return':result['r0'],'count_out':count,'output':output.hex(),
                'visited':[hex(a) for a in sorted(self.visited)]}

    def oversized(self,count):
        self.setup([154]*count,[9])
        result=self.call(0x7F58,[0x201200,0x201100,0x201000,1])
        scratch=[w for w in self.stack_writes if w['pc']=='0x7fa0']
        return {'initial_count':count,'result':result,
                'count_after':self.cpu.mem_read(0x201100,1)[0],
                'scratch_stores':len(scratch),
                'last_scratch_store':scratch[-1] if scratch else None,
                'writes_saved_register_region':any(int(w['address'],0)>=0x202fe8 for w in scratch),
                'visited':[hex(a) for a in sorted(self.visited)]}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('image',type=Path)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    raw=args.image.read_bytes()
    if hashlib.sha256(raw).hexdigest()!=SHA:
        raise ValueError('unexpected image')
    r=FilterRunner(raw)
    rng=random.Random(0x7F58)
    seen=set()
    digest=hashlib.sha256()
    examples=[]
    count=0
    def check(current,remove,arg=None,valid=True,keep=False):
        nonlocal count
        row=r.sample(current,remove,arg,valid)
        count+=1
        seen.update(int(a,0) for a in row['visited'])
        digest.update(json.dumps(row,sort_keys=True,separators=(',',':')).encode())
        if keep:
            examples.append(row)
    for n in range(15):
        current=[(i*37)&255 for i in range(n)]
        for comparison in ([],[0],[current[0]] if current else [17],current[:],
                           current[::2],[255]*14):
            for arg in (0,1,14,15,255):
                source=(comparison+[0]*14)[:20]
                check(current,source,arg,keep=n in (0,1,7,14) and arg in (0,14,255))
    for _ in range(4096):
        current=[rng.randrange(256) for _ in range(rng.randrange(15))]
        remove=[rng.randrange(256) for _ in range(rng.randrange(21))]
        arg=rng.choice((0,1,7,14,15,20,255))
        check(current,remove+[0]*14,arg,keep=len(examples)<24)
    check([1,2,3],[2],1,keep=True)
    check([1,2,3],[],0,keep=True)
    check([1,2,3],[2],1,valid=False,keep=True)
    oversized=[r.oversized(n) for n in (14,16,17,18,19,20)]
    if (oversized[2]['last_scratch_store']['address']!='0x202fe8'
            or oversized[3]['result']['status']!='emulator_fault'
            or oversized[3]['result']['fault']['pc']!='0x7fc0'):
        raise RuntimeError('oversized caller boundary changed')
    result={'format':'quadzilla-queue-filter-emulation-v1','raw_sha256':SHA,
        'cpu':'ARM926 functional surrogate','bounded_cases':count,
        'reference_mismatches':0,'trace_sha256':digest.hexdigest(),
        'examples':examples,'visited':[hex(a) for a in sorted(seen)],
        'oversized_synthetic_caller':oversized,
        'limits':['bounded reference cases supply current list length at most 14',
                  'oversized probes bypass normal producers of queue counts',
                  'synthetic memory faults are not measured target behavior',
                  'whole receive/outgoing state machines and count provenance remain separate']}
    args.output.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(f'{count} bounded filter calls; {len(seen)} starts; zero model differences')


if __name__=='__main__':
    main()
