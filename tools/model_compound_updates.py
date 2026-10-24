"""Bounded byte-memory model of eleven reviewed compound AID handlers."""
HANDLERS=(10,64,80,81,82,146,150,151,152,153,154)
FIELDS={0x200AFF:1,0x2006CF:1,0x2006D0:1,0x2006D1:1,0x2006D2:1,
        0x2006D3:1,0x2006D4:1,0x2006D5:1,0x2006D6:1,0x2006D7:1,
        0x2006D8:2,0x2006DA:1,0x2006DC:2,0x2006DE:1,0x2006DF:1,
        0x2006E0:2,0x2006E2:1,0x2006E4:2,0x2006F4:1,0x2006F5:1,0x2006F6:1,
        0x200AC4:1,0x200AC8:4,0x200ACC:4,0x20073C:4,0x200748:4,0x20074C:4}


def read(memory,address,size=1):
    return sum(memory[address+i]<<(8*i) for i in range(size))


def put(memory,address,value,size=1):
    for i in range(size):
        memory[address+i]=(value>>(8*i))&255


def snapshot(memory):
    return {hex(a):read(memory,a,n) for a,n in FIELDS.items()}


def apply(aids,memory):
    if len(aids)>14 or any(a not in HANDLERS for a in aids):
        raise ValueError('model admits at most fourteen reviewed compound AIDs')
    memory=dict(memory)
    writes=[]
    def store(at,value,size=1):
        put(memory,at,value,size)
        writes.append((at,size,value&((1<<(8*size))-1)))
    def flag():
        store(0x200AC4,1)
    def copy(source,dest,size=1,source_size=None):
        value=read(memory,source,source_size or size)
        if read(memory,dest,size)!=value:
            store(dest,value,size)
            flag()
    def offset146():
        lo,hi=read(memory,0x200B17),read(memory,0x200B18)
        if read(memory,0x2006F4)!=lo:
            store(0x2006F4,lo)
            store(0x20073C,0,4)
            flag()
        if read(memory,0x2006F5)!=hi:
            store(0x2006F5,hi)
            q=hi*125//100
            store(0x200AC8,q,4)
            store(0x200ACC,q*25//100,4)
            flag()
    for aid in aids:
        if aid==10:
            copy(0x200B01,0x200AFF)
        elif aid==64:
            value=read(memory,0x200B1B)
            if read(memory,0x2006F6)!=value:
                store(0x2006F6,value)
                store(0x200748,0,4)
                store(0x20074C,0,4)
                flag()
        elif aid in (80,81,82):
            source=0x200B08+2*(aid-80)
            dest=0x2006D1+2*(aid-80)
            copy(source,dest)
            copy(source+1,dest+1)
        elif aid in (150,151,153):
            source,byte_at,word_at={150:(0x200B0E,0x2006D7,0x2006D8),
                151:(0x200B11,0x2006DA,0x2006DC),153:(0x200B14,0x2006E2,0x2006E4)}[aid]
            copy(source,byte_at)
            copy(source+1,word_at,2)
        elif aid==152:
            bits=read(memory,0x200B02)
            for dest,value in ((0x2006DF,bits&1),(0x2006DE,(bits>>1)&1)):
                if read(memory,dest)!=value:
                    store(dest,value)
                    flag()
            copy(0x200B03,0x2006E0,2)
        elif aid==154:
            copy(0x200B05,0x2006CF)
            copy(0x200B06,0x2006D0,1,source_size=2)
            offset146()
        elif aid==146:
            offset146()
    return memory,writes
