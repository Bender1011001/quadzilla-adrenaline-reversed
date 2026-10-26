#!/usr/bin/env python3
"""Trace BX register sources and inventory other computed ARMv4T PC writes."""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path

from audit_execution_discovery import TEMPLATE_CODE
from audit_remaining_literals import literal_target
from emulate_integer_runtime import SHA


def pc_write_kind(isa, op):
    if isa == 'thumb':
        if op & 0xFC00 == 0x4400 and ((op>>8)&3) in (0,2) and ((op&7)|((op>>4)&8)) == 15:
            return 'high-register ADD/MOV PC'
        if op & 0xFE00 == 0xBC00 and op & 0x100:
            return 'POP PC'
    elif isa == 'arm':
        if op & 0x0FFFFFF0 == 0x012FFF10:
            return None
        if op & 0x0E100000 == 0x08100000 and op & 0x8000:
            return 'LDM including PC'
        if op & 0x0C10F000 == 0x0410F000:
            return 'LDR PC'
        if op & 0x0C00F000 == 0x0000F000 and ((op>>21)&15) not in (8,9,10,11):
            if op & 0x0E000090 != 0x00000090:
                return 'data-processing PC destination'
    return None


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('image',type=Path)
    p.add_argument('--output',type=Path,required=True)
    args=p.parse_args();raw=args.image.read_bytes();root=Path(__file__).resolve().parents[2]
    if hashlib.sha256(raw).hexdigest()!=SHA:raise ValueError('source mismatch')
    def load(path):
        d=json.loads((root/path).read_text())
        if d.get('raw_sha256')!=SHA:raise ValueError(f'evidence identity: {path}')
        return d
    discovery=load('audit/data/execution_discovery_audit.json')
    manifest=load('audit/data/reviewed_instruction_ranges.json');instructions={};cache={}
    spans=[(int(r['start'],0),int(r['end'],0),r['isa'],r['decoder_artifact']) for r in manifest['ranges']]
    spans += [(a,b,'thumb','audit/data/startup_persistence_binaryninja.json') for a,b in TEMPLATE_CODE]
    for lo,hi,isa,path in spans:
        if path not in cache:cache[path]=load(path)
        block=next(r for r in cache[path]['ranges'] if int(r['start'],0)<=lo and hi<=int(r['end'],0))
        for i in block['instructions']:
            at=int(i['address'],0)
            if lo<=at<hi:instructions[at]=(isa,i['length'],i['text'])
    def opcode(at):
        isa,size,_=instructions[at]
        return int.from_bytes(raw[at-0x4000:at-0x4000+(2 if isa=='thumb' else 4)],'little')
    soft=load('audit/data/soft_float_emulation.json')
    thunks={int(t['instruction_end'],0)-2:t for t in soft['thunks']}
    fixed={0x4050:(0x4048,0x414D),0x407C:(0x4074,0x4115),0x4088:(0x4084,0x77B9),0x40F4:(0x40EC,0x7435)}
    dispositions=[]
    for bx in discovery['bx_sites']:
        at=int(bx['site'],0);reg=int(bx['register'][1:]);op=opcode(at)
        row=dict(bx)
        row.pop('status')
        if reg==14:
            row.update(kind='LR return-form',target_source='current LR register; incoming calling/exception context required')
        elif reg==15 and bx['isa']=='thumb':
            if at not in (0x8564,0x8574,0x8584):raise ValueError('unknown BX PC veneer')
            row.update(kind='ISA interworking veneer',target=hex(at+4),target_isa='arm')
        elif bx['isa']=='thumb' and opcode(at-2)==0xBC00|(1<<reg):
            row.update(kind='stack-restored return-form',source_site=hex(at-2),
                       target_source='word popped from current SP immediately before BX; frame integrity required')
        elif at in thunks:
            t=thunks[at];entry=int(t['entry'],0);site=entry if reg==3 else entry+2
            lit=literal_target(site,'thumb',opcode(site))
            if lit!=int(t['literal'],0) or ((opcode(site)>>8)&7)!=3:
                raise ValueError('numeric veneer literal changed')
            value=int.from_bytes(raw[lit-0x4000:lit-0x4000+4],'little')
            if value!=int(t['target'],0) or value%4 or instructions[value][0]!='arm':
                raise ValueError('numeric veneer target changed')
            if reg==12 and (instructions[at-4][2].strip()!='mov     r12, r3' or opcode(at-2)!=0xBC08):
                raise ValueError('register-preserving numeric veneer changed')
            row.update(kind='fixed numeric veneer',entry=t['entry'],source_site=hex(site),literal=hex(lit),
                       target=hex(value),target_isa='arm',r3_preserved=reg==12)
        elif at in fixed:
            source,value=fixed[at];lit=literal_target(source,'arm',opcode(source))
            if lit is None or int.from_bytes(raw[lit-0x4000:lit-0x4000+4],'little')!=value:
                raise ValueError('startup/reset literal changed')
            if instructions[value&~1][0] != ('thumb' if value&1 else 'arm'):
                raise ValueError('startup/reset target ISA differs')
            if at==0x4088:
                anchor=literal_target(0x4080,'arm',opcode(0x4080))
                if anchor!=0x4108 or int.from_bytes(raw[anchor-0x4000:anchor-0x4000+4],'little')!=0x408C:
                    raise ValueError('main continuation return anchor changed')
            elif instructions[at-4][2].strip()!='mov     lr, pc':
                raise ValueError('startup/reset link setup changed')
            row.update(kind='fixed startup/reset transfer',source_site=hex(source),literal=hex(lit),
                       target=hex(value&~1),pointer_bits=hex(value),target_isa='thumb' if value&1 else 'arm',
                       return_strategy='LR loaded with stop loop 0x408c' if at==0x4088 else 'MOV LR,PC before BX')
        elif at==0x4030:
            if instructions[0x4020][2].strip()!='ldr     r0, [r8,  #0x104]':raise ValueError('FIQ vector load changed')
            row.update(kind='AIC-selected callback',source_site='0x4020',target_source='word[R8+0x104]',
                       expected_address='0xfffff104',precondition='startup-initialized banked FIQ R8 = 0xfffff000')
        elif at==0x40BC:
            lit=literal_target(0x40A4,'arm',opcode(0x40A4))
            if lit!=0x4100 or int.from_bytes(raw[lit-0x4000:lit-0x4000+4],'little')!=0xFFFFF000 or instructions[0x40A8][2].strip()!='ldr     r0, [lr,  #0x100]':
                raise ValueError('IRQ vector source changed')
            row.update(kind='AIC-selected callback',source_site='0x40a8',target_source='word[0xfffff100]',
                       expected_address='0xfffff100',precondition='AIC vector state and installed handler ABI')
        else:raise ValueError(('unresolved BX target source',hex(at)))
        dispositions.append(row)
    counts=Counter(r['kind'] for r in dispositions)
    expected_counts={'LR return-form':140,'ISA interworking veneer':3,'stack-restored return-form':38,
                     'fixed numeric veneer':16,'fixed startup/reset transfer':4,'AIC-selected callback':2}
    if counts!=expected_counts:raise ValueError(('BX inventory changed',counts))
    computed=[];software_interrupts=[]
    for at,(isa,size,text) in sorted(instructions.items()):
        kind=pc_write_kind(isa,opcode(at))
        if kind:computed.append({'site':hex(at),'isa':isa,'opcode':hex(opcode(at)),'instruction':text,'kind':kind})
        op=opcode(at)
        if (isa=='thumb' and op & 0xFF00 == 0xDF00) or (isa=='arm' and op>>28!=15 and op & 0x0F000000 == 0x0F000000):
            software_interrupts.append(hex(at))
    if software_interrupts:raise ValueError(('software interrupt needs disposition',software_interrupts))
    if {int(r['site'],0) for r in computed}!={0x4040,0x40DC,0x4B80,0x4C30,0x608A,0x809A}:
        raise ValueError(('computed PC writer inventory changed',computed))
    capture=load('audit/data/capture_scalar_structure.json')
    aid=load('audit/data/aid_validation_dispatch.json');receive=load('audit/data/receive_state_layout.json')
    jump_targets={}
    for site,table in zip((0x4B80,0x4C30),capture['byte_jump_tables']):
        lo=int(table['start'],0);base=int(table['pc_base'],0);targets=[]
        for e in table['entries']:
            target=base+raw[lo+e['index']-0x4000]
            if hex(target)!=e['target']:raise ValueError('capture jump target changed')
            targets.append(target)
        jump_targets[site]=targets
    targets=[]
    for r in aid['rows']:
        if r['table_address'] is not None:
            source=int(r['table_address'],0);offset=int.from_bytes(raw[source-0x4000:source-0x4000+2],'little',signed=True)
            if hex(0x608E+offset)!=r['target']:raise ValueError('AID jump target changed')
            targets.append(0x608E+offset)
    jump_targets[0x608A]=targets
    table=receive['switch'];lo=int(table['start'],0)
    targets=[0x809E+2*b for b in raw[lo-0x4000:int(table['end'],0)-0x4000]]
    if [hex(t) for t in targets]!=table['targets']:raise ValueError('receive jump targets changed')
    jump_targets[0x809A]=targets
    for row in computed:
        site=int(row['site'],0)
        if site in jump_targets:
            targets=jump_targets[site]
            if any(t not in instructions or instructions[t][0]!='thumb' for t in targets):raise ValueError('jump target ISA/start')
            row.update(disposition='bounded indexed dispatch to accepted Thumb starts',table_cases=len(targets),targets=[hex(t) for t in targets])
        else:row.update(disposition='exception return using saved LR or stack/SPSR state; valid exception frame required')
    out={'format':'quadzilla-indirect-transfer-provenance-v1','raw_sha256':SHA,
         'scope':discovery['scope'],'bx_count':len(dispositions),'bx_kind_counts':dict(counts),
         'bx_dispositions':dispositions,'other_pc_writes':computed,
         'software_interrupt_sites':software_interrupts,
         'limits':['Return-form classification does not prove frame integrity or exclude stack overwrite',
                   'AIC callback values depend on programmable vector state and interrupt context',
                   'Table proofs retain the referenced audits bounds and ordinary-state assumptions',
                   'No new independent entry established; global writers, mutable code and alternate ISA evidence remain open']}
    args.output.write_text(json.dumps(out,indent=2)+'\n',encoding='utf-8')
    print(f'{len(dispositions)} BX dispositions {dict(counts)}; {len(computed)} other PC writes')


if __name__=='__main__':main()
