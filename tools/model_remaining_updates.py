"""Local clamp/curve contracts, distinct from transport widths and physical units."""
from fractions import Fraction
from model_soft_float import binary,convert,encode

# stage, source bytes read, working address, store bytes, echo address,
# echo bytes written, lower/upper bound, derived word, auxiliary flag.
SPECS={
 17:(0x200B20,1,0x200588,1,0x200BED,1,0,30,None,True),
 18:(0x200B21,1,0x20058A,1,0x200BEE,1,0,100,None,False),
 19:(0x200B22,1,0x20058B,1,0x200BEF,1,0,100,None,False),
 22:(0x200B23,1,0x200589,1,0x200BF0,1,None,None,None,False),
 59:(0x200B24,1,0x2005B0,1,0x200BF1,1,0,50,None,True),
 60:(0x200B25,1,0x2005B1,1,0x200BF2,1,0,100,None,False),
 61:(0x200B26,1,0x2005B2,1,0x200BF3,1,0,80,0x20046C,True),
 62:(0x200B27,1,0x2005B3,1,0x200BF4,1,0,40,None,True),
 85:(0x200B30,2,0x200590,4,0x200BFD,2,800,2200,None,False),
 104:(0x200B32,2,0x200594,4,0x200BFF,2,3200,3700,None,False),
 110:(0x200B35,1,0x20058C,1,0x200C01,1,0,50,None,False),
 111:(0x200B37,1,0x20058E,1,0x200C03,1,1,100,None,False),
 112:(0x200B39,1,0x20058D,1,0x200C05,1,0,25,None,False),
 141:(0x200B1E,2,0x200584,4,0x200BEB,2,0,300,0x200468,False)}
for aid in range(113,137):
    i=aid-113
    SPECS[aid]=(0x200B3B+2*i,1,0x200598+i,1,0x200C07+2*i,1,50,150,None,False)
for aid in range(137,141):
    i=aid-137
    SPECS[aid]=(0x200B28+2*i,2,0x2005B4+4*i,4,0x200BF5+2*i,2,0,300,0x200458+4*i,False)
HANDLERS=tuple(sorted((*SPECS,24,226)))


def clamp22(value,low):
    if value>=41:
        return 40
    if value<low+1:
        return (low+5)&255
    return max(value,20)


def writes_for(aid,value,low=5):
    if aid not in SPECS or not 0<=value<=65535 or not 0<=low<=255:
        raise ValueError('bounded scalar handler inputs required')
    source,size,work,store_size,echo,echo_size,minimum,maximum,derived,flag=SPECS[aid]
    value=value&255 if size==1 else value
    value=clamp22(value,low) if aid==22 else min(max(value,minimum),maximum)
    writes=[(work,store_size,value)]
    writes += [(echo+i,1,(value>>(8*i))&255) for i in range(echo_size)]
    if derived is not None:
        writes.append((derived,4,value*128//10))
    if flag:
        writes.append((0x200426,1,1))
    return writes


def coefficient(word):
    if not 0<=word<=65535:
        raise ValueError('unsigned 16-bit source required')
    quotient=binary('div',encode(Fraction(word),64),0x4024000000000000,64)
    return convert(quotient,64,32)


def writes226(mode,selection,word):
    if not 0<=mode<=255 or not 0<=selection<=255:
        raise ValueError('byte selectors required')
    writes=[]
    if mode<3:
        writes.append((0x2006E6,1,mode))
    if selection<5:
        writes.append((0x2006E7,1,selection))
    # Widened binary32 result is compared with binary64 bit pattern 1.
    # Nonzero unsigned inputs yield positive normal results; zero fails >=.
    if word:
        writes.append((0x2006E8,4,coefficient(word)))
    return writes
