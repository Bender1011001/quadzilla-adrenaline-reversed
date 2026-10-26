#!/usr/bin/env python3
"""Adjudicate residual code candidates with source bytes and execution evidence."""
import argparse
import hashlib
import json
import struct
from pathlib import Path

from emulate_usart_pdc import Harness, CODE, U
from emulate_integer_runtime import SHA

NOP = (0x4302,0x435E,0x4596,0x46C2,0x4942,0x570E,0x5736,0x5756,
       0x5CBA,0x5DEA,0x5EF2,0x5F2E,0x6702,0x6B1A,0x6BD2,0x6C5E,
       0x6C82,0x6F56,0x70CA,0x7132,0x7172,0x73C6,0x742E,0x7486,
       0x7A3E,0x7B0A,0x7B16,0x7C52,0x7C9E,0x84FE)
FF = (0x6B46,0x74C2,0x7B02,0x7BE6,0x7BEE,0x7FD6,0x852E,0x8562)
VENEER_NOP = (0x8566,0x8576,0x8586)
WRAPPERS = ((0x7AF8,0x7B02),(0x7B04,0x7B0A),(0x7B10,0x7B16),
            (0x7B1C,0x7B28),(0x7B28,0x7B30),(0x7B30,0x7B38),
            (0x7B38,0x7B44),(0x7B4C,0x7B58),(0x7434,0x743C))


class ResidualHarness(Harness):
    def write(self, cpu, access, address, size, value, user):
        if address == 0xFFFFFD00 and size == 4:
            self.writes.append((address, size, value))
        elif address in (0x20070C,0x20070D,0x20070E,0x20070F) and size == 1:
            self.writes.append((address, size, value))
        else:
            super().write(cpu, access, address, size, value, user)


def load(name):
    return json.loads(Path('audit/data', name).read_text())


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('image',type=Path)
    p.add_argument('--output',type=Path,required=True)
    args=p.parse_args(); raw=args.image.read_bytes()
    if hashlib.sha256(raw).hexdigest()!=SHA:raise ValueError('source mismatch')
    items=load('ida_image_items.json')['items']
    targets={int(x['decoded_direct_target'],0) for x in items if 'decoded_direct_target' in x}
    align=[]
    for at in (*NOP,*FF):
        expected=b'\xc0\x46' if at in NOP else b'\xff\xff'
        if raw[at-0x4000:at-0x4000+2]!=expected or at in targets:
            raise ValueError(f'alignment bytes or incoming branch differ: {at:#x}')
        prior=next(x for x in items if int(x['end'],0)==at)
        if prior.get('mnemonic') not in ('BX','B'):
            raise ValueError(f'alignment lacks preceding unconditional transfer: {at:#x}')
        align.append({'start':hex(at),'bytes':expected.hex(),'preceding_transfer':prior['text']})
    if raw[0xA02F-0x4000]!=0:raise ValueError('SPI/ADC pad changed')
    division=load('integer_runtime_emulation.json'); decode=load('integer_runtime_binaryninja.json')
    if division['raw_sha256']!=SHA or decode['raw_sha256']!=SHA:raise ValueError('division identity')
    starts={int(i['address'],0) for r in decode['ranges'] for i in r['instructions']}
    visited_div={int(a,0) for s in division['suites'] for a in s['visited_addresses']}
    if starts-visited_div != set(VENEER_NOP) or any(s['mismatches'] for s in division['suites']):
        raise ValueError('division execution coverage differs')
    for at in VENEER_NOP:
        if raw[at-0x4000:at-0x4000+2]!=b'\xc0\x46':raise ValueError('interworking pad changed')
    ratio=load('drivetrain_score_emulation.json')
    if ratio['raw_sha256']!=SHA:raise ValueError('ratio identity')
    for row in ratio['transmission_rows']:
        at=0x9F88+row['selector']*28
        words=struct.unpack_from('<7I',raw,at-0x4000)
        if words[0]!=row['count'] or [hex(x) for x in words[1:1+words[0]]]!=row['ratio_bits']:
            raise ValueError('ratio row changed')
        if any(words[1+words[0]:]):raise ValueError('unused ratio slots are not zero')
    if [hex(x) for x in struct.unpack_from('<5I',raw,0x9FDC-0x4000)]!=ratio['axle_ratio_bits']:
        raise ValueError('coefficient table changed')
    h=ResidualHarness(raw); h.allowed_ranges=CODE+WRAPPERS
    seen=set(); cases=0; samples=[]
    for entry,flag in ((0x7B04,0x20070B),(0x7B10,0x200AFD)):
        for value in range(256):
            h.prepare();h.cpu.mem_write(flag,bytes((value,)));h.call(entry)
            if h.cpu.reg_read(h.arm.UC_ARM_REG_R0)!=value or h.writes:raise RuntimeError('getter mismatch')
            seen.update(h.visited);cases+=1
    for entry,expected in ((0x7B28,[(0x20070E,1,0)]),(0x7B30,[(0x20070C,1,0)]),
                           (0x7B38,[(0x20070F,1,1),(0x20070E,1,1)]),
                           (0x7B4C,[(0x20070D,1,1),(0x20070C,1,1)]),
                           (0x7434,[(0xFFFFFD00,4,0xA500000D)])):
        h.prepare();h.call(entry)
        if h.writes!=expected:raise RuntimeError((entry,h.writes,expected))
        seen.update(h.visited);cases+=1
        samples.append({'entry':hex(entry),'writes':[[hex(a),n,hex(v)] for a,n,v in h.writes]})
    for entry,cp,cc,nc,count in ((0x7AF8,0x108,0x10C,0x11C,23),(0x7B1C,0x100,0x104,0x114,16)):
        h.prepare();h.call(entry,0x200840,23)
        if (h.get(U+cp),h.get(U+cc),h.get(U+nc))!=(0x200840,count,0):raise RuntimeError('call wrapper mismatch')
        seen.update(h.visited);cases+=1
        samples.append({'entry':hex(entry),'writes':[[hex(a),n,hex(v)] for a,n,v in h.writes]})
    uart=load('uart_buffer_binaryninja.json'); reset=load('startup_persistence_binaryninja.json')
    if uart['raw_sha256']!=SHA or reset['raw_sha256']!=SHA:raise ValueError('wrapper decode identity')
    expected={int(i['address'],0) for d in (uart,reset) for r in d['ranges'] for i in r['instructions']
              if any(a<=int(i['address'],0)<b for a,b in WRAPPERS)}
    wrapper_seen={a for a in seen if any(lo<=a<hi for lo,hi in WRAPPERS)}
    if expected!=wrapper_seen:raise RuntimeError('wrapper/reset code not fully visited')
    out={'format':'quadzilla-residual-code-adjudication-v1','raw_sha256':SHA,
         'alignment_after_unconditional_transfer':align,'interworking_nops':[hex(a) for a in VENEER_NOP],
         'division_visited_starts':[hex(a) for a in sorted(visited_div)],
         'ratio_table_range':['0x9f88','0x9ff0'],'ratio_table_sha256':hashlib.sha256(raw[0x9F88-0x4000:0x9FF0-0x4000]).hexdigest(),
         'spi_adc_zero_pad':'0xa02f','new_execution_cases':cases,
         'wrapper_reset_ranges':[[hex(a),hex(b)] for a,b in WRAPPERS],
         'wrapper_reset_visited_starts':[hex(a) for a in sorted(wrapper_seen)],'examples':samples,
         'limits':['No electrical reset or DMA effect is simulated','No exhaustive alternate-entry or global writer claim',
                   'Byte classification does not close the full subsystem analysis']}
    args.output.write_text(json.dumps(out,indent=2)+'\n',encoding='utf-8')
    print(f'{cases} new calls; {len(wrapper_seen)} wrapper/reset starts; {len(align)} alignment pairs; {len(visited_div)} division starts')


if __name__=='__main__':main()
