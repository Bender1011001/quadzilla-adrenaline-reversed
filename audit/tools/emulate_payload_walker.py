#!/usr/bin/env python3
"""Execute width/CRC/payload parsing against synthetic memory, without devices."""
import argparse
import hashlib
import json
import random
import struct
from pathlib import Path

from audit_aid_tables import AidRunner,SHA
from model_payload_walker import width,walk,parse_frame
from x2com_crc import add_crc,crc8

RANGES=((0x7B60,0x7BCA),(0x7BF8,0x7C1A),(0x7C1C,0x7C52),
        (0x7CC4,0x7D7E),(0x7E64,0x7EB4))


class WalkerRunner(AidRunner):
    def __init__(self,raw):
        super().__init__(raw)
        self.allowed_ranges=RANGES
        self.cpu.mem_map(0x210000,0x1000)
        self.writes=[]
        self.input_reads=[]
        self.input_pointer=0x201000
        self.cpu.hook_add(self.uc.UC_HOOK_MEM_WRITE,self.write)
        self.cpu.hook_add(self.uc.UC_HOOK_MEM_READ,self.read)
        self.pointers={aid:struct.unpack_from('<I',raw,0xA91C+4*aid-0x4000)[0] for aid in range(256)}

    def write(self,cpu,access,address,size,value,user):
        if 0x202E00<=address<0x203004:
            return
        self.writes.append({'pc':hex(cpu.reg_read(self.arm.UC_ARM_REG_PC)),
                            'address':hex(address),'size':size,'value':value&((1<<(8*size))-1)})

    def read(self,cpu,access,address,size,value,user):
        if self.input_pointer<=address<self.input_pointer+0x20:
            self.input_reads.append(address-self.input_pointer)

    def prepare(self,incoming_r7=0):
        self.reset()
        self.visited.clear()
        self.writes.clear()
        self.input_reads.clear()
        self.input_pointer=0x201000
        for n in range(4,12):
            self.cpu.reg_write(getattr(self.arm,f'UC_ARM_REG_R{n}'),
                               incoming_r7 if n==7 else 0x12340000+n)
        self.cpu.mem_write(0x203000,struct.pack('<I',0x201140))

    def checked(self,entry,args,incoming_r7=0):
        for i,value in enumerate(args):
            self.cpu.reg_write(getattr(self.arm,f'UC_ARM_REG_R{i}'),value)
        self.cpu.emu_start(entry|1,0x3F00,count=100000)
        if self.cpu.reg_read(self.arm.UC_ARM_REG_PC)!=0x3F00 or self.cpu.reg_read(self.arm.UC_ARM_REG_SP)!=0x203000:
            raise RuntimeError('call did not return with balanced stack within instruction budget')
        for n in range(4,12):
            expected=incoming_r7 if n==7 else 0x12340000+n
            if self.cpu.reg_read(getattr(self.arm,f'UC_ARM_REG_R{n}'))!=expected:
                raise RuntimeError('callee-saved register changed')
        return self.cpu.reg_read(self.arm.UC_ARM_REG_R0)

    def sample(self,payload,kind=1,count_arg=None,tail=0,incoming_r7=0):
        self.prepare(incoming_r7)
        count_arg=len(payload) if count_arg is None else count_arg
        self.cpu.mem_write(0x201000,payload+bytes([tail])+bytes(32))
        result=self.checked(0x7CC4,[0x201000,count_arg,kind,0x201100],incoming_r7)
        expected=walk(payload,self.pointers,kind,count_arg,tail,incoming_r7)
        count=self.cpu.mem_read(0x201140,1)[0]
        report=list(self.cpu.mem_read(0x201100,count))
        staging=[(int(w['address'],0),w['value']) for w in self.writes
                 if int(w['address'],0)<0x201000]
        if (result,report,staging,self.input_reads)!=(expected.status,expected.reported,expected.writes,expected.reads):
            raise RuntimeError((payload.hex(),kind,result,report,staging,self.input_reads,expected))
        return {'payload':payload.hex(),'kind_arg':kind,'count_arg':count_arg,'lookahead':tail,
                'incoming_r7':hex(incoming_r7),'status':result,'reported':report,
                'remaining_reference':expected.remaining,'writes':self.writes.copy(),
                'input_offsets_read':self.input_reads.copy()}

    def frame(self,frame):
        self.prepare()
        self.cpu.mem_write(0x201000,frame+bytes(32))
        status=self.checked(0x7E64,[0x201000,0x201160,0x201100,0x201140])
        kind=self.cpu.mem_read(0x201160,1)[0]
        count=self.cpu.mem_read(0x201140,1)[0]
        report=list(self.cpu.mem_read(0x201100,count))
        expected_status,expected_kind,expected=parse_frame(frame,self.pointers)
        staging=[(int(w['address'],0),w['value']) for w in self.writes
                 if int(w['address'],0)<0x201000]
        if (status,kind,report,staging)!=(expected_status,expected_kind,expected.reported,expected.writes):
            raise RuntimeError((frame.hex(),status,kind,report,staging,expected))
        return {'frame':frame.hex(),'status':status,'type_out':kind,'reported':report,
                'writes':self.writes.copy(),'input_offsets_read':self.input_reads.copy()}

    def guard(self):
        self.prepare()
        self.input_pointer=0x210FFF
        self.cpu.mem_write(self.input_pointer,b'\xe2')
        result=self.call(0x7CC4,[self.input_pointer,1,1,0x201100])
        return {'payload':'e2','payload_address':hex(self.input_pointer),'result':result,
                'writes':self.writes.copy(),'limits':'unmapped guard page demonstrates the local read, not a physical fault'}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('image',type=Path)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    raw=args.image.read_bytes()
    if hashlib.sha256(raw).hexdigest()!=SHA:
        raise ValueError('unexpected image')
    r=WalkerRunner(raw)
    examples,frames,seen,digest=[],[],set(),hashlib.sha256()
    totals={'direct':0,'frame':0,'crc':0,'width':0}
    def record(case,kind,keep=False):
        totals[kind]+=1
        seen.update(r.visited)
        digest.update(json.dumps(case,sort_keys=True,separators=(',',':')).encode())
        if keep:
            (frames if kind=='frame' else examples).append(case)
    for aid in range(256):
        for tail in (0,1,5,255):
            record(r.sample(bytes([aid]),tail=tail),'direct',keep=aid in (9,85,154,220,226,255))
    for size in range(256):
        for n in range(2,15):
            payload=bytes([226,size])+bytes((i*37)&255 for i in range(n-2))
            record(r.sample(payload),'direct',keep=size in (0,1,2,5,13,14,255) and n in (2,6,14))
    for kind in range(16):
        for n in range(15):
            for inherited in (0,1,255,256,0xFFFFFFFF):
                record(r.sample(bytes(range(n)),kind=kind,incoming_r7=inherited),'direct',
                       keep=kind in (1,2,4) and n in (0,1,14))
    rng=random.Random(0x7CC4)
    for index in range(2048):
        n=rng.randrange(15)
        payload=bytes(rng.randrange(256) for _ in range(n))
        record(r.sample(payload,kind=rng.randrange(16),tail=rng.randrange(256),
                        incoming_r7=rng.getrandbits(32)),'direct',keep=index<8)
    for count in (0,1,14,15,255,256,257,0xFFFFFFFF):
        record(r.sample(bytes([9,1])*8,count_arg=count,incoming_r7=0x100),'direct',keep=True)
    for kind in range(16):
        for payload in (b'',bytes([9,1]),bytes([226,0,2,4,10,0]),bytes([226,1]),
                        bytes([226,5,2,4,10,0]),bytes(range(14))):
            frame=add_crc(bytes([(kind<<4)|(len(payload)+1)])+payload)
            record(r.frame(frame),'frame',keep=True)
            damaged=frame[:-1]+bytes([frame[-1]^1])
            record(r.frame(damaged),'frame',keep=True)
    record(r.frame(b'\x10'),'frame',keep=True)
    for aid in range(256):
        for lookahead in (0,1,255,0xFFFFFFFF):
            r.prepare()
            actual=r.checked(0x7BF8,[lookahead,aid])
            if actual!=width(aid,lookahead):
                raise RuntimeError('width mismatch')
            record({'aid':aid,'lookahead':lookahead,'result':actual},'width')
    for n in (0,1,2,15,16,255,256,257,0xFFFFFFFF):
        r.prepare()
        data=bytes(rng.randrange(256) for _ in range(255))
        r.cpu.mem_write(0x201000,data)
        actual=r.checked(0x7B60,[0x201000,n])
        if actual!=crc8(data[:n&255]):
            raise RuntimeError('CRC length mismatch')
        record({'count_arg':n,'result':actual},'crc')
    guard=r.guard()
    result={'format':'quadzilla-payload-walker-emulation-v1','raw_sha256':SHA,
            'cpu':'ARM926 functional surrogate','call_totals':totals,'reference_mismatches':0,
            'trace_sha256':digest.hexdigest(),'examples':examples,'frame_cases':frames,
            'lookahead_guard':guard,'visited':[hex(a) for a in sorted(seen)],
            'limits':['direct API payloads and completed frames in synthetic memory, not physical receive traffic',
                      'the frame parser is executed; 0x8038 transport/state admission is not part of these sweeps',
                      'guard-page fault is a local read-bound observation, not a measured device exception',
                      'pointer table includes the separately documented AID255 out-of-bounds slot']}
    args.output.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(f'{totals}; {len(seen)} instruction starts visited; zero model differences')


if __name__=='__main__':
    main()
