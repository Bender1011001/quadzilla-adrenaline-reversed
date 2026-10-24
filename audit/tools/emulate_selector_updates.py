#!/usr/bin/env python3
"""Execute ingest AID9/15 paths with an explicit scripted receive boundary."""
import argparse
import hashlib
import itertools
import json
import struct
from pathlib import Path

from audit_aid_tables import SHA
from emulate_control_helpers import ControlRunner
from model_selector_updates import updates

RANGES=((0x601C,0x6042),(0x604E,0x608C),(0x6240,0x6274),(0x6482,0x64B8))


class UpdateRunner(ControlRunner):
    def __init__(self, raw):
        super().__init__(raw)
        self.allowed_ranges += RANGES+((0x506C,0x50DC),)
        self.aids=[]
        self.status=1
        self.boundary=[]

    def trace(self,cpu,address,size,user):
        if address == 0x8038:
            dest=cpu.reg_read(self.arm.UC_ARM_REG_R0)
            count=cpu.reg_read(self.arm.UC_ARM_REG_R1)
            cpu.mem_write(dest,bytes(self.aids) or b'\0')
            cpu.mem_write(count,bytes([len(self.aids)]))
            self.boundary.append({'aid_list_pointer':hex(dest),'count_pointer':hex(count),
                                  'aids':self.aids,'return_status':self.status})
            cpu.reg_write(self.arm.UC_ARM_REG_R0,self.status)
            cpu.reg_write(self.arm.UC_ARM_REG_PC,cpu.reg_read(self.arm.UC_ARM_REG_LR))
            return
        super().trace(cpu,address,size,user)

    def sample(self,aids,staged_selector=0,staged_count=11,selector=2,count=11,
               step=10,offset=0,blocked=False,receive_status=1):
        if len(aids)>14:
            raise ValueError('scripted contract capped to the reviewed 14-byte AID list')
        self.prepare(((0x20042F,0x200435),(0x200580,0x200581),(0x2006CD,0x2006CE),
                      (0x200AC4,0x200AC5),(0x200BC4,0x200BC5),(0x200BEA,0x200BEB)))
        for at,v in ((0x200B00,staged_selector),(0x200B1D,staged_count),
                     (0x2006CD,selector),(0x200580,count),(0x200433,step),(0x200434,offset),
                     (0x2006CF,int(blocked)),(0x2006D0,100),(0x200BCD,0),(0x200BEA,0xA7),
                     (0x200AC4,0)):
            self.cpu.mem_write(at,bytes([v]))
        self.cpu.mem_write(0x20042F,bytes([120,0,0,0]))
        self.word(0x20044C,15)
        self.word(0x2005F4,0)
        self.aids=list(aids)
        self.status=receive_status
        self.boundary=[]
        self.checked_call(0x601C,[])
        seen={a for a in self.visited if any(lo<=a<hi for lo,hi in RANGES)}
        actual={'selector':self.cpu.mem_read(0x2006CD,1)[0],
                'count':self.cpu.mem_read(0x200580,1)[0],
                'step':self.cpu.mem_read(0x200433,1)[0],
                'offset':self.cpu.mem_read(0x200434,1)[0],
                'changed':self.cpu.mem_read(0x200AC4,1)[0],
                'count_echo':self.cpu.mem_read(0x200BEA,1)[0],
                'latch':list(self.cpu.mem_read(0x20042F,4))}
        expected,post_expected=updates(aids,staged_selector,staged_count,selector,count,step,
                                        offset,blocked,receive_status)
        if actual!=expected:
            raise RuntimeError((aids,actual,expected))
        ingest_writes=self.writes.copy()
        self.cpu.reg_write(self.arm.UC_ARM_REG_LR,0x3F00)
        mapped=self.checked_call(0x506C,[])
        post={'mapped':mapped,'response':self.cpu.mem_read(0x200BC4,1)[0],
              'latch':list(self.cpu.mem_read(0x20042F,4))}
        if post!=post_expected:
            raise RuntimeError((aids,post,post_expected))
        return {'inputs':{'aids':aids,'staged_selector':staged_selector,'staged_count':staged_count,
                          'selector':selector,'count':count,'step':step,'offset':offset,
                          'blocked':blocked,'receive_status':receive_status},
                'scripted_receive':self.boundary,'after_ingest':actual,'after_selector':post,
                'ingest_writes':ingest_writes},seen


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('image',type=Path)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    raw=args.image.read_bytes()
    if hashlib.sha256(raw).hexdigest()!=SHA:
        raise ValueError('unexpected image')
    r=UpdateRunner(raw)
    examples,seen,digest=[],set(),hashlib.sha256()
    total=0
    def run(aids,keep=False,**kw):
        nonlocal total
        case,visited=r.sample(aids,**kw)
        seen.update(visited)
        total+=1
        digest.update(json.dumps([case['inputs'],case['after_ingest'],case['after_selector']],
                                 sort_keys=True,separators=(',',':')).encode())
        if keep:
            examples.append(case)
    for value,count,blocked in itertools.product(range(256),range(5,15),(False,True)):
        step,offset=divmod(100,count-1)
        run([9],staged_selector=value,count=count,step=step,offset=offset,blocked=blocked,
            keep=value in (0,2,127,128,255) and count in (5,14))
    for value in range(256):
        run([15],staged_count=value,selector=13,keep=value in (0,4,5,11,14,15,255))
    for aids in ([9,15],[15,9],[9,9],[15,15],[0,8,227,255,9,15],[],[9]*14):
        run(aids,staged_selector=10,staged_count=11,count=5,step=25,keep=True)
    for value,old in ((0,0),(128,0),(130,2),(2,2)):
        run([9],staged_selector=value,selector=old,keep=True)
    for status in (0,2):
        run([9,15],staged_selector=10,staged_count=14,receive_status=status,keep=True)
    run([9],staged_selector=255,count=0,step=1,keep=True)
    run([15,9],staged_selector=13,staged_count=5,selector=13,count=14,step=7,offset=9,keep=True)
    result={'format':'quadzilla-selector-update-emulation-v1','raw_sha256':SHA,
            'entry':'0x601c','cpu':'ARM926 functional surrogate','calls':total,
            'reference_mismatches':0,'digest_inputs_and_outputs_sha256':digest.hexdigest(),
            'examples':examples,'visited':[hex(a) for a in sorted(seen)],
            'limits':['0x8038 is replaced by a scripted receive-result contract; its instructions do not execute',
                      'staging bytes are preloaded, not written by actual transport or payload walker',
                      'only AID9/15 handlers, loop and default selection are executed here',
                      'no IRQ interleaving, hardware, packet framing or physical effects modeled',
                      'existing invalid configuration probes do not establish live reachability']}
    args.output.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(f'{total} ingest + selector calls; {len(seen)} ingest starts visited; zero model differences')


if __name__=='__main__':
    main()
