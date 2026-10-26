#!/usr/bin/env python3
"""Audit direct ARMv4T transfers and code-address data windows from accepted bytes."""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path

from audit_remaining_literals import literal_target
from emulate_integer_runtime import SHA

COPY_SOURCE, COPY_RUNTIME, COPY_LENGTH = 0xB114, 0x200C84, 0xA4
TEMPLATE_CODE = ((0xB114,0xB122),(0xB124,0xB17C),(0xB18C,0xB1B0))


def signed(value, bits):
    return value-(1<<bits) if value & (1<<(bits-1)) else value


def direct_transfer(site, isa, data):
    if isa == 'thumb':
        op=int.from_bytes(data[:2],'little')
        if op & 0xF800 == 0xE000:
            return 'B',site+4+(signed(op & 0x7FF,11)<<1),14
        if op & 0xF000 == 0xD000 and ((op>>8)&15)<14:
            return 'B',site+4+(signed(op & 255,8)<<1),(op>>8)&15
        if len(data)==4 and op & 0xF800 == 0xF000:
            tail=int.from_bytes(data[2:],'little')
            if tail & 0xF800 == 0xF800:
                return 'BL',site+4+(signed(op & 0x7FF,11)<<12)+((tail & 0x7FF)<<1),14
    elif isa == 'arm':
        op=int.from_bytes(data,'little')
        if op>>28 != 15 and op & 0x0E000000 == 0x0A000000:
            return ('BL' if op & 0x01000000 else 'B'),site+8+(signed(op & 0xFFFFFF,24)<<2),op>>28
    return None


def canonical(address):
    if COPY_RUNTIME <= address < COPY_RUNTIME+COPY_LENGTH:
        return address-COPY_RUNTIME+COPY_SOURCE
    return address


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('image',type=Path)
    p.add_argument('--output',type=Path,required=True)
    args=p.parse_args();raw=args.image.read_bytes();root=Path(__file__).resolve().parents[2]
    if hashlib.sha256(raw).hexdigest()!=SHA:raise ValueError('source identity mismatch')
    def load(path):
        doc=json.loads((root/path).read_text())
        if doc.get('raw_sha256')!=SHA:raise ValueError(f'evidence identity mismatch: {path}')
        return doc
    manifest=load('audit/data/reviewed_instruction_ranges.json')
    catalog=load('audit/data/execution_entry_catalog.json');extra=load('audit/data/entry_adjudications.json')
    known={int(e['entry'],0) for e in catalog['entries']}|{int(e['start'],0) for e in extra['entries']}
    instructions={};code=set();cache={}
    spans=[(int(r['start'],0),int(r['end'],0),r['isa'],r['decoder_artifact']) for r in manifest['ranges']]
    spans += [(a,b,'thumb','audit/data/startup_persistence_binaryninja.json') for a,b in TEMPLATE_CODE]
    for lo,hi,isa,path in spans:
        if path not in cache:cache[path]=load(path)
        block=next(r for r in cache[path]['ranges'] if int(r['start'],0)<=lo and hi<=int(r['end'],0))
        cursor=lo
        for ins in block['instructions']:
            at=int(ins['address'],0)
            if not lo<=at<hi:continue
            if at!=cursor or at in instructions:raise ValueError('instruction overlap/gap')
            cursor+=ins['length']
            instructions[at]=(isa,ins['length'],ins['text'])
        if cursor!=hi:raise ValueError('incomplete accepted code span')
        code.update(range(lo,hi))
    if not known.issubset(instructions):raise ValueError(('known entries not decoded',known-set(instructions)))
    edges=[];literal_refs={};indirect=[]
    for at,(isa,size,text) in sorted(instructions.items()):
        data=raw[at-0x4000:at-0x4000+size]
        transfer=direct_transfer(at,isa,data)
        if transfer:
            kind,target,condition=transfer;source=canonical(target)
            if source not in instructions or instructions[source][0]!=isa:
                raise ValueError(('unadjudicated direct target or ISA',hex(at),hex(target),isa))
            if kind=='BL' and source not in known:
                raise ValueError(('unadjudicated direct-call entry',hex(at),hex(source)))
            edges.append({'site':hex(at),'isa':isa,'kind':kind,'condition':condition,'target':hex(target),
                          'source_target':hex(source),'documented_entry':source in known})
        op=int.from_bytes(data[:2] if isa=='thumb' else data,'little')
        target=literal_target(at,isa,op)
        if target is not None and 0x4000<=target<=0xBCFC:
            literal_refs.setdefault(target,[]).append(hex(at))
        reg=None
        if isa=='thumb' and op & 0xFF87 == 0x4700:reg=(op>>3)&15
        elif isa=='arm' and op & 0x0FFFFFF0 == 0x012FFF10:reg=op&15
        if reg is not None:
            indirect.append({'site':hex(at),'isa':isa,'register':f'r{reg}','instruction':text,
                             'status':'LR return-form' if reg==14 else
                             'Thumb BX PC interworking veneer' if isa=='thumb' and reg==15 else
                             'requires register-source/prologue context'})
    export=load('audit/data/ida_image_items.json');items={int(x['start'],0):x for x in export['items']}
    mismatches=[];cross=[]
    for edge in edges:
        at,target=int(edge['site'],0),int(edge['source_target'],0);item=items.get(at,{})
        if 'decoded_direct_target' in item and canonical(int(item['decoded_direct_target'],0))!=target:
            mismatches.append(edge)
        if edge['kind']=='B' and target not in known and item.get('function')!=items.get(target,{}).get('function'):
            cross.append(edge)
    if mismatches:raise ValueError(('IDA/raw direct-target disagreement',mismatches))
    expected_cross={(0x86EC,0x870C),(0x8808,0x883C),(0x9160,0x91BC),(0x927C,0x929C)}
    if {(int(e['site'],0),int(e['source_target'],0)) for e in cross}!=expected_cross:
        raise ValueError('cross-IDA-owner branch inventory changed')
    soft=load('audit/data/soft_float_emulation.json');reviews=load('audit/data/soft_float_function_reviews.json')
    for edge in cross:
        at,target=int(edge['site'],0),int(edge['source_target'],0)
        edge['ida_source_owner']=items.get(at,{}).get('function')
        edge['ida_target_owner']=items.get(target,{}).get('function')
        edge['disposition']='shared numeric continuation; no independent-call evidence'
        edge['primary_source_roles']=[e['entry'] for e in reviews['entries'] if int(e['entry'],0)<=at<int(e['primary_instruction_end'],0)]
        edge['target_visited_from_entries']=[s['entry'] for s in soft['suites'] if hex(target) in s['visited_addresses']]
        if not edge['target_visited_from_entries']:raise ValueError('shared target lacks execution evidence')
    pointers=[]
    for at in range(0x4000,0xBCFD):
        if any(a in code for a in range(at,at+4)):continue
        value=int.from_bytes(raw[at-0x4000:at-0x4000+4],'little');target=canonical(value&~1)
        if target not in code:continue
        requested='thumb' if value&1 else 'arm';accepted=instructions.get(target,(None,))[0]
        compatible=accepted==requested and (requested=='thumb' or target%4==0)
        if target in known and compatible:
            disposition='documented entry address; use still depends on consumer'
        elif at==0x6F6C:
            if value!=20001 or literal_refs.get(at)!=['0x6e0e'] or instructions[0x6E10][2].strip()!='cmp     r2, r0':
                raise ValueError('scalar-threshold disposition changed')
            disposition='scalar counter threshold 20001 compared at 0x6e10'
        elif at==0x75CC:
            if value!=0x7860 or literal_refs.get(at)!=['0x754a'] or instructions[0x754C][2].strip()!='str     r2, [r0]' or int.from_bytes(raw[0x75F8-0x4000:0x75FC-0x4000],'little')!=0xFFFFF470:
                raise ValueError('PIO mask disposition changed')
            disposition='PIO configuration mask written at 0x754c'
        elif at==0x96E0:
            if value!=COPY_RUNTIME:raise ValueError('copy descriptor destination changed')
            disposition='startup copy descriptor destination address, not a function-pointer use'
        elif at==0x96E4:
            if value!=COPY_SOURCE:raise ValueError('copy descriptor source changed')
            disposition='startup copy descriptor source address, not a function-pointer use'
        elif not compatible:
            disposition='data window incompatible with reviewed target ISA/start alignment; no entry evidence'
        else:
            disposition='overlapping data window; no identified code-pointer consumer; not promoted to entry'
        pointers.append({'source':hex(at),'initialized_runtime_window':hex(0x200000+at-0x96E8) if 0x96E8<=at<0x9F88 else None,
                         'aligned_word':at%4==0,'value':hex(value),'source_target':hex(target),
                         'requested_isa':requested,'accepted_target_isa':accepted,'accepted_instruction_start':target in instructions,
                         'pc_literal_load_sites':literal_refs.get(at,[]),'disposition':disposition})
    incoming=Counter(int(e['source_target'],0) for e in edges)
    pointed={int(p['source_target'],0) for p in pointers if p['disposition'].startswith('documented entry')}
    out={'format':'quadzilla-execution-discovery-audit-v1','raw_sha256':SHA,
         'scope':'Accepted 19000 instruction bytes plus 138 source bytes of the three copied Thumb helper bodies',
         'known_source_entries':len(known),'decoded_instruction_starts':len(instructions),
         'pc_literal_words_scanned':len(literal_refs),
         'direct_calls':sum(e['kind']=='BL' for e in edges),'direct_branches':sum(e['kind']=='B' for e in edges),
         'direct_transfers':edges,'raw_ida_target_disagreements':mismatches,
         'resolved_runtime_calls':[e for e in edges if e['target']!=e['source_target']],
         'cross_ida_owner_dispositions':cross,'code_address_data_windows':pointers,
         'bx_sites':indirect,'known_entries_without_incoming_audited_edge_or_pointer':[hex(a) for a in sorted(known) if not incoming[a] and a not in pointed],
         'limitations':['Not an exhaustive indirect/computed-target proof','Data-window scanning includes unaligned coincidences; a numeric match alone is not an entry',
                       'Canonical addresses cover image coordinates and the known SRAM copy; other physical/remap aliases are not normalized',
                       'Other ISA interpretations, synthesized pointers and runtime mutation still require review','No new independent source entry established in this bounded pass']}
    args.output.write_text(json.dumps(out,indent=2)+'\n',encoding='utf-8')
    print(f"{out['direct_calls']} calls, {out['direct_branches']} branches, {len(pointers)} data windows; "
          f"{len(cross)} shared continuations; {len(indirect)} BX sites")


if __name__=='__main__':main()
