import idc
import idautils
import ida_funcs
import ida_bytes
import ida_ua

def main():
    print("=== Searching for RAM accesses (0x200b00-0x200c00) ===")
    
    for func_ea in idautils.Functions():
        func = ida_funcs.get_func(func_ea)
        if not func:
            continue
            
        head = func.start_ea
        while head < func.end_ea:
            insn = ida_ua.insn_t()
            if ida_ua.decode_insn(insn, head):
                for op in insn.ops:
                    if op.type == ida_ua.o_imm:
                        val = op.value
                        if 0x200b00 <= val <= 0x200c00:
                            print(f"Func {hex(func_ea)} ({idc.get_func_name(func_ea)}) at {hex(head)}: Imm RAM {hex(val)}")
                    elif op.type == ida_ua.o_mem:
                        addr = op.addr
                        if addr != idc.BADADDR:
                            val = idc.get_wide_dword(addr)
                            if 0x200b00 <= val <= 0x200c00:
                                print(f"Func {hex(func_ea)} ({idc.get_func_name(func_ea)}) at {hex(head)}: Loads RAM {hex(val)} from literal pool {hex(addr)}")
            head = idc.next_head(head)
            
    idc.qexit(0)

if __name__ == "__main__":
    main()
