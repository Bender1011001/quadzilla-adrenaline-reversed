"""Independent byte model of the bounded table-2 response reader and builder."""

from model_payload_walker import width
from x2com_crc import add_crc


def read_values(aids, kind, sources):
    """Return (payload, deferred AIDs) for a list of at most 14 AIDs.

    sources maps AID to its current table-2 bytes, or None for a null pointer.
    The 14-entry premise is supplied by callers; the firmware helper does not
    check the initial request count against its local deferred-list capacity.
    """
    if len(aids) > 14:
        raise ValueError('model requires a bounded caller list')
    output=bytearray()
    deferred=[]
    for aid in aids:
        if len(output)>=14:
            break
        if kind&255 in (2,4):
            output.append(aid)
            continue
        value=sources.get(aid)
        if value is None:
            deferred.append(aid)
            continue
        n=width(aid,value[0])
        if len(output)+n+1>=15:
            deferred.append(aid)
            continue
        output.append(aid)
        output.extend(value[:n])
    return bytes(output),bytes(deferred)


def build_frame(aids,kind,sources):
    payload,deferred=read_values(aids,kind,sources)
    header=((kind<<4)&0xF0)|((len(payload)+1)&15)
    return add_crc(bytes([header])+payload),deferred,1 if not deferred else 2
