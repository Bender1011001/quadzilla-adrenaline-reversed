"""Byte-accurate local payload walker, including lookahead and caller R7 state."""
from dataclasses import dataclass
from x2com_crc import crc8


def width(aid,lookahead):
    aid&=0xFFFFFFFF
    return 1 if aid<75 else 2 if aid<150 else 3 if aid<185 else 4 if aid<220 else lookahead&0xFFFFFFFF


@dataclass
class Result:
    status:int
    reported:list
    writes:list
    remaining:int
    reads:list


def walk(payload,pointers,message_type=1,count_arg=None,lookahead=0,incoming_r7=0):
    count=min((len(payload) if count_arg is None else count_arg)&255,14)
    if len(payload)<count or not 0<=lookahead<=255:
        raise ValueError('model requires all declared payload bytes and one byte of lookahead')
    state=1
    remaining=incoming_r7&0xFFFFFFFF
    pointer=0
    report,writes,reads=[],[],[]
    for at in range(count):
        value=payload[at]
        reads.append(at)
        if message_type&255 in (2,4):
            report.append(value)
            continue
        if state==1:
            reads.append(at+1)
            next_byte=payload[at+1] if at+1<len(payload) else lookahead
            remaining=width(value,next_byte)
            pointer=pointers.get(value,0)
            state=2 if pointer else 0
            if pointer:
                report.append(value)
        else:
            remaining=(remaining-1)&255
            if state==2:
                writes.append((pointer,value))
                pointer+=1
            if remaining==0:
                state=1
    return Result(1 if remaining&255==0 else 2,report,writes,remaining,reads)


def parse_frame(frame,pointers):
    if not frame:
        raise ValueError('header byte required')
    last=frame[0]&15
    if last==0:
        return 5,6,Result(5,[],[],0,[])
    if len(frame)<last+1:
        raise ValueError('model excludes physically absent frame bytes')
    if crc8(frame[:last+1])!=0x3B:
        return 4,6,Result(4,[],[],0,[])
    kind=frame[0]>>4
    result=walk(frame[1:last],pointers,kind,lookahead=frame[last],incoming_r7=last-1)
    return result.status,kind,result
