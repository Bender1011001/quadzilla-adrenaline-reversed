#!/usr/bin/env python3
"""Execute compound handlers and a partial-walker cross-AID sequence offline."""
import argparse
import hashlib
import json
import struct
from pathlib import Path

from audit_aid_tables import SHA
from emulate_selector_updates import UpdateRunner
from model_compound_updates import HANDLERS,FIELDS,apply,put,snapshot

NEW_RANGES=((0x6274,0x63AC),(0x63F0,0x6482))


def initial(value=0,old=0):
    memory={0x200B00+i:value for i in range(29)}
    for at,size in FIELDS.items():
        put(memory,at,int.from_bytes(bytes([old])*size,'little'),size)
    put(memory,0x200AC4,0)
    for at in (0x200AC8,0x200ACC,0x20073C,0x200748,0x20074C):
        put(memory,at,0x12345678,4)
    return memory


class CompoundRunner(UpdateRunner):
    def __init__(self,raw):
        super().__init__(raw)
        self.allowed_ranges+=NEW_RANGES+((0x7B60,0x7EFC),)

    def seed(self,memory):
        self.prepare(((0x2006CD,0x2006F7),(0x200AC4,0x200AD0),(0x20073C,0x200750),
                      (0x200AFF,0x200B1D),(0x201000,0x201180)))
        for at,value in memory.items():
            self.cpu.mem_write(at,bytes([value]))

    def ingest(self,aids,memory,status=1):
        self.aids=list(aids)
        self.status=status
        self.boundary=[]
        self.writes.clear()
        self.visited.clear()
        self.cpu.reg_write(self.arm.UC_ARM_REG_LR,0x3F00)
        self.checked_call(0x601C,[])
        expected,writes=apply(aids,memory) if status==1 else (dict(memory),[])
        actual={hex(at):int.from_bytes(self.cpu.mem_read(at,size),'little') for at,size in FIELDS.items()}
        actual_writes=[(int(w['address'],0),w['size'],w['value']&((1<<(8*w['size']))-1))
                       for w in self.writes]
        if actual!=snapshot(expected) or actual_writes!=writes:
            raise RuntimeError({'aids':aids,'actual':actual,'expected':snapshot(expected),
                                'actual_writes':actual_writes,'expected_writes':writes})
        seen={a for a in self.visited if any(lo<=a<hi for lo,hi in NEW_RANGES)}
        return expected,{'aids':aids,'status':status,'before':snapshot(memory),'after':actual,
                          'staging_hex':bytes(memory[0x200B00+i] for i in range(29)).hex(),
                          'writes':self.writes.copy(),'scripted_receive':self.boundary},seen

    def walker(self,payload,memory):
        self.cpu.mem_write(0x201000,payload)
        self.cpu.mem_write(0x201100,bytes(0x80))
        self.cpu.mem_write(0x203000,struct.pack('<I',0x201140))
        self.cpu.reg_write(self.arm.UC_ARM_REG_LR,0x3F00)
        self.writes.clear()
        result=self.checked_call(0x7CC4,[0x201000,len(payload),1,0x201100])
        count=self.cpu.mem_read(0x201140,1)[0]
        aids=list(self.cpu.mem_read(0x201100,count))
        for at in range(0x200B00,0x200B1D):
            memory[at]=self.cpu.mem_read(at,1)[0]
        return result,aids,{'payload':payload.hex(),'status':result,'reported_aids':aids,
                           'writes':self.writes.copy()}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('image',type=Path)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    raw=args.image.read_bytes()
    if hashlib.sha256(raw).hexdigest()!=SHA:
        raise ValueError('unexpected image')
    r=CompoundRunner(raw)
    examples,seen,digest=[],set(),hashlib.sha256()
    calls=0
    for aid in HANDLERS:
        for value in range(256):
            for equal in (False,True):
                memory=initial(value,old=value if equal else value^255)
                if equal:
                    memory,_=apply([aid],memory)
                    put(memory,0x200AC4,0)
                r.seed(memory)
                after,case,visited=r.ingest([aid],memory)
                seen.update(visited)
                digest.update(json.dumps([aid,value,equal,case['after'],case['writes']],
                                         sort_keys=True,separators=(',',':')).encode())
                calls+=1
                if value in (0,1,127,128,255):
                    case['sweep_value']=value
                    case['after_first_apply']=equal
                    examples.append(case)
    asymmetric=[]
    for aid,at in ((150,0x200B0F),(151,0x200B12),(152,0x200B03),
                   (153,0x200B15),(154,0x200B06)):
        for value in (0,1,255,256,0x1234,0x8000,0xFFFF):
            memory=initial()
            put(memory,at,value,2)
            r.seed(memory)
            _,case,visited=r.ingest([aid],memory)
            seen.update(visited)
            case['word_input']=value
            asymmetric.append(case)
    # Partial AID146 writes staging but fails completion. A later successful
    # AID154 update reaches that staging through the handler's fall-through.
    memory=initial()
    for at,value in ((0x200B17,10),(0x200B18,20),(0x2006F4,10),(0x2006F5,20)):
        put(memory,at,value)
    r.seed(memory)
    status,aids,first_walk=r.walker(bytes([146,77]),memory)
    memory,first,visited=r.ingest(aids,memory,status)
    seen.update(visited)
    status,aids,second_walk=r.walker(bytes([154,0,0,0]),memory)
    memory,second,visited=r.ingest(aids,memory,status)
    seen.update(visited)
    # Isolate the 16-bit compare / byte store with matching low byte and no
    # other change, then repeat without resetting the working state.
    narrow=initial()
    put(narrow,0x200B06,0x1234,2)
    put(narrow,0x2006D0,0x34)
    r.seed(narrow)
    narrow,narrow_first,visited=r.ingest([154],narrow)
    seen.update(visited)
    put(narrow,0x200AC4,0)
    r.cpu.mem_write(0x200AC4,b'\0')
    narrow,narrow_second,visited=r.ingest([154],narrow)
    seen.update(visited)
    result={'format':'quadzilla-compound-update-emulation-v1','raw_sha256':SHA,
            'entry':'0x601c','cpu':'ARM926 functional surrogate','handler_aids':list(HANDLERS),
            'sweep_calls':calls,'reference_mismatches':0,'sweep_trace_sha256':digest.hexdigest(),
            'examples':examples,'visited':[hex(a) for a in sorted(seen)],
            'asymmetric_word_cases':asymmetric,'extra_ingest_calls':39,
            'cross_aid_sequence':{'partial_walker':first_walk,'failed_ingest':first,
                                  'complete_walker':second_walk,'later_ingest':second},
            'repeated_narrow_store':[narrow_first,narrow_second],
            'limits':['0x8038 replaced by explicit receive-result contract; packet framing/CRC not executed',
                      'sweeps preload staging; cross-AID example executes original 0x7cc4 walker',
                      'no hardware, IRQ interleaving, measured units or application decoding',
                      'transport reachability, downstream consumers and severity remain separate questions']}
    args.output.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(f'{calls} sweep calls + 39 word/sequence ingests; {len(seen)} added starts visited; zero model differences')


if __name__=='__main__':
    main()
