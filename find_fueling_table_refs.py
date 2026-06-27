import idc
import idautils
import ida_funcs
import ida_ua

def main():
    print("=== Searching for references to the fueling table at 0x6a48 (fixed) ===")
    
    # We look for references to 0x6a48 in instructions or literal pools
    for func_ea in idautils.Functions():
        func = ida_funcs.get_func(func_ea)
        if not func:
            continue
            
        head = func.start_ea
        while head < func.end_ea:
            insn = ida_ua.insn_t()
            if ida_ua.decode_insn(insn, head):
                for op in insn.ops:
                    if op.type == ida_ua.o_imm and op.value == 0x6a48:
                        print(f"Func {hex(func_ea)} ({idc.get_func_name(func_ea)}) at {hex(head)}: Imm 0x6a48")
                    elif op.type == ida_ua.o_mem:
                        addr = op.addr
                        if addr != idc.BADADDR:
                            val = idc.get_wide_dword(addr)
                            if val == 0x6a48:
                                print(f"Func {hex(func_ea)} ({idc.get_func_name(func_ea)}) at {hex(head)}: Loads 0x6a48 from literal pool {hex(addr)}")
            head = idc.next_head(head)
            
    idc.qexit(0)

if __name__ == "__main__":
    main()
