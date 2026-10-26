#!/usr/bin/env python3
"""Compose selected original initializer segments and audit their AIC vectors."""
import argparse
import hashlib
import itertools
import json
from pathlib import Path

from audit_remaining_literals import literal_target
from emulate_startup_init import make_cpu
from emulate_integer_runtime import SHA

VECTORS, SPURIOUS = 0xFFFFF080, 0xFFFFF134
RANGES=((0x414C,0x41BE),(0x4114,0x4144),(0x8530,0x854A),(0x854C,0x8562),
        (0x77DE,0x77E8),(0x74E8,0x757E),(0x6FB4,0x70CA),(0x6BD8,0x6C14),(0x725C,0x72FE))
PHASES=(('clock_fallbacks',0x414C,None),('memory_descriptors',0x4114,None),
        ('main_spurious_slice',0x77DE,0x77E4),('pio_prefix',0x74E8,0x757A),
        ('timer_setup',0x6FB4,None),('spi_setup',0x6BD8,None),('usart_setup',0x725C,None))
OVERRIDES={2:0x7449,5:0x6B45,6:0x7179,12:0x6C49,13:0x6C69,14:0x6C95}


def run(raw,seed,pin,clock_enabled,control_read):
    cpu,arm,visited,_=make_cpu(raw,RANGES)
    for base in (0xFFFA0000,0xFFFC0000,0xFFFE0000):cpu.mem_map(base,0x1000)
    def word(a,v):cpu.mem_write(a,int(v).to_bytes(4,'little'))
    def get(a):return int.from_bytes(cpu.mem_read(a,4),'little')
    for n in range(32):word(VECTORS+4*n,seed+n)
    word(SPURIOUS,seed+0x80);word(0xFFFFFC68,0xD);word(0xFFFFF43C,pin<<17)
    for base in (0xFFFA0000,0xFFFA0040,0xFFFA0080):word(base+0x20,clock_enabled<<16)
    vector_writes=[];stop_at=None
    def write(_,access,address,size,value,__):
        if VECTORS<=address<VECTORS+0x80 or address==SPURIOUS:
            if size!=4 or address%4:raise RuntimeError('non-word AIC vector write')
            vector_writes.append({'site':hex(cpu.reg_read(arm.UC_ARM_REG_PC)),'address':hex(address),'value':hex(value)})
    def read(_,access,address,size,value,__):
        if address==0xFFFC0000:word(address,control_read)
    def boundary(_,address,size,__):
        if address==stop_at:cpu.emu_stop()
    import unicorn as uc
    cpu.hook_add(uc.UC_HOOK_MEM_WRITE,write)
    cpu.hook_add(uc.UC_HOOK_MEM_READ,read)
    cpu.hook_add(uc.UC_HOOK_CODE,boundary)
    phases=[]
    for name,entry,stop in PHASES:
        stop_at=stop;begin=len(vector_writes);visited.clear()
        cpu.reg_write(arm.UC_ARM_REG_CPSR,0x13)
        cpu.reg_write(arm.UC_ARM_REG_SP,0x203000)
        cpu.reg_write(arm.UC_ARM_REG_LR,0x3F00)
        for n in range(13):cpu.reg_write(getattr(arm,f'UC_ARM_REG_R{n}'),0x12340000+n)
        cpu.emu_start(entry|1,0x3F00,count=50000)
        if cpu.reg_read(arm.UC_ARM_REG_PC)!=(stop if stop else 0x3F00):raise RuntimeError('phase did not finish')
        if stop is None:
            if cpu.reg_read(arm.UC_ARM_REG_SP)!=0x203000:raise RuntimeError('returning phase stack imbalance')
            if any(cpu.reg_read(getattr(arm,f'UC_ARM_REG_R{n}'))!=0x12340000+n for n in range(4,12)):
                raise RuntimeError('returning phase changed preserved registers')
        phases.append({'phase':name,'entry':hex(entry),'stop':hex(stop) if stop else 'returned',
                       'stack_pointer_after_segment':hex(cpu.reg_read(arm.UC_ARM_REG_SP)),
                       'vector_writes':vector_writes[begin:],'visited_starts':len(visited)})
        if get(VECTORS+31*4)!=seed+31:raise RuntimeError('slot 31 was modified')
        if name=='clock_fallbacks':
            if [get(VECTORS+4*n) for n in range(31)]!=[0x40E0]+[0x40E4]*30 or get(SPURIOUS)!=0x40E8:
                raise RuntimeError('clock fallback vector state differs')
        if name=='main_spurious_slice' and get(SPURIOUS)!=0x7445:raise RuntimeError('spurious update differs')
    final=[get(VECTORS+4*n) for n in range(32)]
    expected=[0x40E0]+[0x40E4]*30+[seed+31]
    for n,pointer in OVERRIDES.items():expected[n]=pointer
    if final!=expected or get(SPURIOUS)!=0x7445:raise RuntimeError('final installed vectors differ')
    if len(vector_writes)!=39:raise RuntimeError('unexpected vector write inventory')
    return {'seed':hex(seed),'pio_pin17':pin,'tc_clock_enabled':clock_enabled,'us_cr_read':hex(control_read),
            'vector_write_count':len(vector_writes),'final_vectors':[hex(x) for x in final],
            'spurious_vector':hex(get(SPURIOUS)),'phases':phases}


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('image',type=Path);p.add_argument('--output',type=Path,required=True)
    args=p.parse_args();raw=args.image.read_bytes();root=Path(__file__).resolve().parents[2]
    if hashlib.sha256(raw).hexdigest()!=SHA:raise ValueError('source identity')
    cases=[run(raw,*values) for values in itertools.product((0xA5000000,0x5A000000),(0,1),(0,1),(0,0xFFFFFFFF))]
    catalog=json.loads((root/'audit/data/execution_entry_catalog.json').read_text())
    extra=json.loads((root/'audit/data/entry_adjudications.json').read_text())
    known={int(r['entry'],0) for r in catalog['entries']}|{int(r['start'],0) for r in extra['entries']}
    installed={int(x,0)&~1 for x in cases[0]['final_vectors'][:31]}|{0x7444}
    if not installed<=known:raise ValueError('installed vector has no documented entry')
    manifest=json.loads((root/'audit/data/reviewed_instruction_ranges.json').read_text())
    export=json.loads((root/'audit/data/ida_image_items.json').read_text())
    if any(d['raw_sha256']!=SHA for d in (catalog,extra,manifest,export)):raise ValueError('evidence identity')
    written={int(w['value'],0) for c in cases for phase in c['phases'] for w in phase['vector_writes']}
    for pointer in written:
        source=pointer&~1
        mode=next(r['isa'] for r in manifest['ranges'] if int(r['start'],0)<=source<int(r['end'],0))
        if source not in known or mode!=('thumb' if pointer&1 else 'arm'):
            raise ValueError('written vector target entry/ISA differs')
    seeds=[]
    for item in export['items']:
        values={int(v,0) for v in item.get('data_refs',[]) if VECTORS<=int(v,0)<VECTORS+0x80 or int(v,0)==SPURIOUS}
        if not values:continue
        site=int(item['start'],0)
        accepted=next(r for r in manifest['ranges'] if int(r['start'],0)<=site<int(r['end'],0))
        width=2 if accepted['isa']=='thumb' else 4
        target=literal_target(site,accepted['isa'],int.from_bytes(raw[site-0x4000:site-0x4000+width],'little'))
        if target is None or {int.from_bytes(raw[target-0x4000:target-0x4000+4],'little')}!=values:
            raise ValueError('AIC address seed is not a verified PC literal')
        if not any(a<=site<b for a,b in RANGES):raise ValueError('literal vector seed lies outside reviewed initializer segments')
        seeds.append({'site':hex(site),'literal':hex(target),'value':hex(next(iter(values)))})
    raw_seeds=[];cache={}
    for r in manifest['ranges']:
        path=r['decoder_artifact']
        if path not in cache:cache[path]=json.loads((root/path).read_text())
        if cache[path]['raw_sha256']!=SHA:raise ValueError('decoder identity')
        lo,hi=int(r['start'],0),int(r['end'],0)
        block=next(b for b in cache[path]['ranges'] if int(b['start'],0)<=lo and hi<=int(b['end'],0))
        for ins in block['instructions']:
            site=int(ins['address'],0)
            if not lo<=site<hi:continue
            width=2 if r['isa']=='thumb' else 4
            target=literal_target(site,r['isa'],int.from_bytes(raw[site-0x4000:site-0x4000+width],'little'))
            if target is None or not 0x4000<=target<=0xBCFC:continue
            value=int.from_bytes(raw[target-0x4000:target-0x4000+4],'little')
            if VECTORS<=value<VECTORS+0x80 or value==SPURIOUS:
                raw_seeds.append({'site':hex(site),'literal':hex(target),'value':hex(value)})
    if sorted(raw_seeds,key=lambda r:int(r['site'],0))!=sorted(seeds,key=lambda r:int(r['site'],0)):
        raise ValueError('raw/IDA vector-address literal seeds differ')
    out={'format':'quadzilla-aic-vector-installation-v1','raw_sha256':SHA,
         'scope':'Composed selected returning initializers, PIO prefix and main spurious slice; not a complete startup execution',
         'cases':cases,'case_count':len(cases),'segments_per_case':len(PHASES),'literal_address_seeds':seeds,
         'installed_source_entries':[hex(a) for a in sorted(installed)],
         'all_written_source_entries':[hex(a) for a in sorted(p&~1 for p in written)],
         'slot31':'Untouched in all selected segments; seeded sentinel is not a device measurement',
         'limits':['Clock ready, PIO and TC status are supplied synthetic values','US_CR reads are explicit synthetic values for a write-only register',
                   'No hardware interrupt selection, DMA or command side effects are modeled','Skipped initialization/security/vector-page operations prevent a full startup claim',
                   'Literal-seed coverage does not exclude computed/generic-pointer writers or runtime mutation']}
    args.output.write_text(json.dumps(out,indent=2)+'\n',encoding='utf-8')
    print(f'{len(cases)} composed cases, {len(PHASES)} segments each; {len(seeds)} vector-address literal sites; slot 31 unchanged')


if __name__=='__main__':main()
