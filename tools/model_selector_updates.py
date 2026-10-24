"""Local AID 9/15 ingest model; transport and physical effects are excluded."""
from model_control_helpers import latch_state, selector_state


def updates(aids, staged_selector, staged_count, selector, count, step, offset,
            blocked=False, receive_status=1):
    if len(aids)>14 or any(not (a in (9,15) or 0<=a<9 or 227<=a<=255) for a in aids):
        raise ValueError('model admits only AID9/15 and out-of-range default AIDs, at most 14 entries')
    if any(not 0<=v<=255 for v in (staged_selector,staged_count,selector,count,step,offset)):
        raise ValueError('configuration values must be bytes')
    latch=[120,0,0,0]
    changed=0
    if receive_status == 1:
        for aid in aids:
            if aid == 9:
                ready,latch=latch_state(0,0,int(blocked),selector,100,15,latch)
                if ready and selector != staged_selector:
                    selector=staged_selector & 127
                    if selector >= count:
                        selector=(count-1) & 255
                    changed=1
            elif aid == 15:
                count=min(max(staged_count,5),14)
                step,offset=divmod(100,count-1)
    state={'selector':selector,'count':count,'step':step,'offset':offset,'changed':changed,
           'count_echo':count if receive_status == 1 and 15 in aids else 0xA7,
           'latch':latch}
    ready,post_latch=latch_state(0,0,int(blocked),selector,100,15,latch)
    mapped,response=selector_state(selector,count,step,offset,0,ready)
    return state,{'mapped':mapped,'response':response,'latch':post_latch}
