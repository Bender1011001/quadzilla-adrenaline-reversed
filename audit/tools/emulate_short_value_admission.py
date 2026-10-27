#!/usr/bin/env python3
"""Run completed-buffer admission, CRC, walker and ingest without function stubs."""
import argparse
import hashlib
import json
import struct
from pathlib import Path

from audit_aid_tables import SHA
from emulate_control_helpers import ControlRunner
from emulate_remaining_updates import RemainingRunner
from emulate_payload_walker import RANGES
from x2com_crc import add_crc,crc8


class AdmissionRunner(RemainingRunner):
    def __init__(self,raw):
        super().__init__(raw)
        self.allowed_ranges+=RANGES+((0x720C,0x7256),(0x7B10,0x7B16),(0x7B1C,0x7B28),
            (0x7BCC,0x7BE6),(0x7BE8,0x7BEE),(0x7BF0,0x7BF8),
            (0x8038,0x809C),(0x80A2,0x80B2),(0x8198,0x81A2))
        self.cpu.mem_map(0xFFFC0000,0x1000)
        self.calls=[]
        self.results=[]

    def trace(self,cpu,address,size,user):
        # Deliberately bypass UpdateRunner.trace: 0x8038 executes original bytes.
        ControlRunner.trace(self,cpu,address,size,user)
        if address in (0x8038,0x7BCC,0x7E64,0x7CC4,0x66AC):
            self.calls.append(hex(address))
        if address==0x6028:
            self.results.append(cpu.reg_read(self.arm.UC_ARM_REG_R0))

    def setup(self):
        self.prepare(((0x200000,0x202000),(0xFFFC0000,0xFFFC1000)))
        self.cpu.mem_write(0xFFFC0000,bytes(0x1000))
        self.word(0x200728,0xFFFA0080)
        self.word(0x2007E8,0x2007F0)
        self.cpu.mem_write(0x2006E6,b'\0\0'+struct.pack('<I',0x3F000000))

    def admission(self,payload,corrupt_crc=False):
        frame=add_crc(bytes([0x10|(len(payload)+1)])+payload)
        if corrupt_crc:
            frame=frame[:-1]+bytes([frame[-1]^1])
        buffer=int.from_bytes(self.cpu.mem_read(0x2007E8,4),'little')
        self.cpu.mem_write(buffer,frame+bytes(16-len(frame)))
        # Explicit completed-receive boundary: emulate the IRQ's pending flag
        # and zeroed current receive count, not actual DMA or UART activity.
        self.cpu.mem_write(0x200AFD,b'\x01')
        self.word(0xFFFC0104,0)
        self.writes.clear()
        self.visited.clear()
        self.calls.clear()
        self.results.clear()
        self.cpu.reg_write(self.arm.UC_ARM_REG_LR,0x3F00)
        self.checked_call(0x601C,[])
        if len(self.results)!=1:
            raise RuntimeError('missing receive return observation')
        return {'payload':payload.hex(),'frame':frame.hex(),'completed_buffer':hex(buffer),
                'receive_status_at_ingest_gate':self.results[0],
                'original_entry_calls':self.calls.copy(),
                'staging226':bytes(self.cpu.mem_read(0x200AEC,5)).hex(),
                'staging226_extended':bytes(self.cpu.mem_read(0x200AEC,13)).hex(),
                'numeric_status_byte':self.cpu.mem_read(0x200AF8,1)[0],
                'working226':{'mode':self.cpu.mem_read(0x2006E6,1)[0],
                              'selection':self.cpu.mem_read(0x2006E7,1)[0],
                              'coefficient_f32_bits':hex(self.read_word(0x2006E8))},
                'writes':self.writes.copy(),'visited':[hex(a) for a in sorted(self.visited)]}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('image',type=Path)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    raw=args.image.read_bytes()
    if hashlib.sha256(raw).hexdigest()!=SHA:
        raise ValueError('unexpected image')
    r=AdmissionRunner(raw)
    r.setup()
    first=r.admission(bytes([226,0,2,4,10,0]))
    second=r.admission(bytes([226,1]))
    corrupt=r.admission(bytes([226,5,0,0,20,0]),corrupt_crc=True)
    empty=r.admission(b'')
    oversized=r.admission(bytes([226,13,0,0,10,0])+bytes([0xA5])*7+bytes([0x5A]))
    if first['receive_status_at_ingest_gate']!=2 or first['working226']!={'mode':0,'selection':0,'coefficient_f32_bits':'0x3f000000'}:
        raise RuntimeError('failed variable update unexpectedly applied')
    if second['receive_status_at_ingest_gate']!=1 or second['working226']!={'mode':2,'selection':4,'coefficient_f32_bits':'0x3f800000'}:
        raise RuntimeError('short successful update did not apply retained staging')
    if corrupt['receive_status_at_ingest_gate']!=4 or corrupt['working226']!=second['working226']:
        raise RuntimeError('damaged CRC changed working configuration')
    if empty['receive_status_at_ingest_gate']!=1 or empty['working226']!=second['working226']:
        raise RuntimeError('empty frame context mismatch')
    status_stores=[w for w in oversized['writes'] if w['address']=='0x200af8' and w['pc']=='0x7d6c']
    if (oversized['receive_status_at_ingest_gate']!=1 or oversized['numeric_status_byte']!=0x5A
            or not status_stores):
        raise RuntimeError('oversized variable value did not reach numeric status byte')
    helper_seen=set()
    getter_digest=hashlib.sha256()
    for byte in range(256):
        for entry,expected in ((0x7BE8,byte>>4),(0x7BF0,byte&15)):
            r.prepare(((0x200000,0x202000),))
            r.cpu.mem_write(0x201000,bytes([byte]))
            actual=r.checked_call(entry,[0x201000])
            if actual!=expected or r.writes:
                raise RuntimeError('header getter mismatch')
            helper_seen.update(r.visited)
            getter_digest.update(bytes([actual]))
    envelope=[]
    for kind in range(16):
        for payload in (b'',b'\x09\x01',b'\xe2\x01'):
            frame=add_crc(bytes([(kind<<4)|(len(payload)+1)])+payload)
            for corrupt_flag in (False,True):
                data=frame if not corrupt_flag else frame[:-1]+bytes([frame[-1]^1])
                r.prepare(((0x200000,0x202000),))
                r.cpu.mem_write(0x201000,data)
                actual=r.checked_call(0x7BCC,[0x201000,data[0]&15])
                if actual!=(3 if crc8(data)==0x3B else 4) or r.writes:
                    raise RuntimeError('CRC envelope mismatch')
                helper_seen.update(r.visited)
                envelope.append({'frame':data.hex(),'status':actual})
    result={'format':'quadzilla-short-value-admission-v1','raw_sha256':SHA,
            'cpu':'ARM926 functional surrogate','function_stubs':[],
            'sequence':[first,second,corrupt,empty,oversized],
            'header_helpers':{'getter_cases':512,'getter_output_sha256':getter_digest.hexdigest(),
                'envelope_cases':envelope,'visited':[hex(a) for a in sorted(helper_seen)
                    if 0x7BCC<=a<0x7BE6 or 0x7BE8<=a<0x7BEE or 0x7BF0<=a<0x7BF8]},
            'limits':['completed receive buffer, pending flag and RCR state supplied explicitly',
                      'USART/PDC register cells are plain memory without DMA/interrupt side effects',
                      'original receive dispatcher, CRC checks, payload walker, validation and numeric handlers execute',
                      'only ordinary type1 admission path exercised, not full 0x8038 state-machine coverage',
                      'physical delivery, pairing, intended schema and downstream impact not established']}
    args.output.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print('Original completed-buffer -> receive -> CRC -> walker -> ingest -> AID226 sequence reproduced')


if __name__=='__main__':
    main()
