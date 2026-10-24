"""Independent bounded model for the outgoing AID-list filter at 0x7F58."""


def filter_aids(current,remove,comparison_count=None,destination_valid=True):
    if len(current)>14:
        raise ValueError('bounded model requires at most 14 current AIDs')
    count=len(remove) if comparison_count is None else comparison_count
    if not destination_valid or count==0:
        return b''
    comparison=set(remove[:min(count,14)])
    return bytes(aid for aid in current if aid not in comparison)
