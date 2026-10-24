#!/usr/bin/env python3
"""Execute remaining parameter handlers, reset gate and shared tail entries."""
import argparse
import hashlib
import json
import random
import struct
from pathlib import Path

from audit_aid_tables import SHA
from emulate_selector_updates import UpdateRunner
from model_remaining_updates import SPECS,HANDLERS,writes_for,writes226

ROOT=Path(__file__).resolve().parents[2]
NEW_RANGES=((0x6042,0x604E),(0x64B8,0x6702),(0x67DC,0x6A48))


class RemainingRunner(UpdateRunner):
    def __init__(self,raw):
        super().__init__(raw)
        self.allowed_ranges+=NEW_RANGES+((0x6B08,0x6B0C),(0x6B10,0x6B1A),
            (0x7128,0x7132),(0x7138,0x713C),(0x7160,0x7164),(0x8678,0x96C4),(0x7B60,0x7EFC))
        prior=json.loads((ROOT/'audit/data/control_helper_emulation.json').read_text(encoding='utf-8'))
        if prior['raw_sha256']!=SHA:
            raise ValueError('initializer reference source mismatch')
        default=next(s for s in prior['suites'] if s['entry']=='0x4384')['examples'][0]['writes']
        self.default_writes=[(int(w['address'],0),w['size'],w['value']&((1<<(8*w['size']))-1)) for w in default]

    def sample(self,aid,value=0,high=0,low=5,mode=0,selection=0,prefix=4,reader=False):
        self.prepare(((0x200000,0x202000),))
        self.aids=[aid]
        self.status=1
        self.boundary=[]
        self.cpu.mem_write(0x200580,bytes([0xA7])*0x44)
        self.cpu.mem_write(0x200BBA,bytes([0xA7])*0x80)
        self.cpu.mem_write(0x200426,b'\0')
        self.cpu.mem_write(0x20058D,bytes([low]))
        self.cpu.mem_write(0x2006E6,b'\xa7\xa7'+struct.pack('<I',0x3F800000))
        self.cpu.mem_write(0x200AF8,b'\0')
        if aid in SPECS:
            stage,read_size,work,store_size,echo,echo_size,*_=SPECS[aid]
            self.cpu.mem_write(stage,struct.pack('<H',value) if aid>=75 else bytes([value&255]))
            if aid>=75 and read_size==1:
                self.cpu.mem_write(stage+1,bytes([high]))
            expected=writes_for(aid,value,low)
        elif aid==24:
            self.cpu.mem_write(0x200B34,bytes([value]))
            expected=self.default_writes if value==85 else []
        elif aid==226:
            self.cpu.mem_write(0x200AEC,bytes([prefix,mode,selection])+struct.pack('<H',value))
            expected=writes226(mode,selection,value)
        else:
            raise ValueError('unsupported handler')
        self.checked_call(0x601C,[])
        actual=[(int(w['address'],0),w['size'],w['value']&((1<<(8*w['size']))-1)) for w in self.writes]
        if actual!=expected:
            raise RuntimeError({'aid':aid,'value':value,'mode':mode,'selection':selection,
                                'actual':actual,'expected':expected})
        seen={a for a in self.visited if any(lo<=a<hi for lo,hi in NEW_RANGES)}
        record={'aid':aid,'value':value,'high_byte':high,'low_setting':low,'mode':mode,
                'selection':selection,'prefix':prefix,'writes':self.writes.copy(),
                'scripted_receive':self.boundary}
        if reader:
            self.cpu.mem_write(0x201000,bytes(8))
            self.cpu.mem_write(0x201040,bytes([aid]))
            self.cpu.mem_write(0x201060,b'\x01')
            self.cpu.reg_write(self.arm.UC_ARM_REG_LR,0x3F00)
            result=self.call(0x7D80,[0x201000,5,0x201040,0x201060])
            record['reader']={'result':result,'buffer':bytes(self.cpu.mem_read(0x201000,5)).hex()}
        return record,seen


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('image',type=Path)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    raw=args.image.read_bytes()
    if hashlib.sha256(raw).hexdigest()!=SHA:
        raise ValueError('unexpected image')
    runner=RemainingRunner(raw)
    examples,seen,digest=[],set(),hashlib.sha256()
    totals={'scalar':0,'coupled22':0,'ignored_high_byte':0,'reset_gate':0,'configuration226':0}
    def run(kind,keep=False,**kw):
        record,visited=runner.sample(**kw)
        seen.update(visited)
        totals[kind]+=1
        digest.update(json.dumps(record,sort_keys=True,separators=(',',':')).encode())
        if keep:
            examples.append(record)
    rng=random.Random(0x601C)
    for aid,spec in sorted(SPECS.items()):
        size=spec[1]
        values=range(256) if size==1 else sorted({0,1,255,256,299,300,301,799,800,801,
            2199,2200,2201,3199,3200,3201,3699,3700,3701,65535}|{rng.randrange(65536) for _ in range(256)})
        for value in values:
            run('scalar',aid=aid,value=value,keep=value in (0,1,49,50,150,151,255,256,300,800,2200,3700,65535))
        if aid>=75 and size==1:
            for value in (0,1,50,100,150,255):
                for high in (1,255):
                    run('ignored_high_byte',aid=aid,value=value,high=high,reader=True,keep=True)
    for low in range(26):
        for value in range(256):
            run('coupled22',aid=22,value=value,low=low,keep=low in (0,5,25) and value in (0,1,5,6,25,26,40,41))
    for value in range(256):
        run('reset_gate',aid=24,value=value,keep=value in (0,84,85,86,255))
    for mode in (0,1,2,3,255):
        for selection in (0,4,5,255):
            for value in (0,1,9,10,11,100,1000,65535):
                for prefix in (0,4,255):
                    run('configuration226',aid=226,value=value,mode=mode,selection=selection,
                        prefix=prefix,keep=mode in (0,3) and selection in (0,5)
                        and value in (0,1,65535))
    for index,value in enumerate(rng.sample(range(65536),4096)):
        run('configuration226',aid=226,value=value,keep=index<8)
    contracts=[]
    for aid,spec in sorted(SPECS.items()):
        stage,size,work,store_size,echo,echo_size,minimum,maximum,derived,flag=spec
        contracts.append({'aid':aid,'staging':hex(stage),'source_bytes_read':size,
            'transport_bytes':1 if aid<75 else 2,'working':hex(work),'working_store_bytes':store_size,
            'echo':hex(echo),'echo_bytes_written':echo_size,'minimum':minimum,'maximum':maximum,
            'derived_word':None if derived is None else hex(derived),'sets_byte_200426':flag})
    result={'format':'quadzilla-remaining-handler-emulation-v1','raw_sha256':SHA,
            'entry':'0x601c','cpu':'ARM926 functional surrogate','handler_aids':list(HANDLERS),
            'call_totals':totals,'reference_mismatches':0,'trace_sha256':digest.hexdigest(),
            'examples':examples,'visited':[hex(a) for a in sorted(seen)],
            'scalar_contracts':contracts,'coefficient_sample_seed':'0x601c; RNG follows scalar word sampling',
            'reset_reference':'audit/data/control_helper_emulation.json:entry.0x4384',
            'limits':['0x8038 replaced with explicit receive-result contract; no packet framing/CRC',
                      'scalar sweeps preload staging; reader probes use original 0x7d80 bytes',
                      'reset-trigger effects reuse the separately reviewed initializer contract',
                      '226 first staging byte is varied without running variable-width payload parsing',
                      'no hardware, IRQ interleaving, engineering-unit or application-decoding model']}
    args.output.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(f'{sum(totals.values())} calls; {len(seen)} added starts visited; zero model differences')


if __name__=='__main__':
    main()
