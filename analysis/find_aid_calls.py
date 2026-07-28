import idc
import idautils
import ida_funcs

def main():
    print("=== Searching for calls to sub_7C1C and sub_7C68 ===")
    
    targets = {
        0x7c1c: "sub_7C1C",
        0x7c68: "sub_7C68",
    }
    
    for target_ea, name in targets.items():
        print(f"Calls to {name}:")
        for x in idautils.XrefsTo(target_ea):
            func_name = idc.get_func_name(x.frm)
            print(f"  From {hex(x.frm)} in function {func_name} (type {x.type})")
            # Print disassembly around the call
            for ea in range(x.frm - 6, x.frm + 4, 2):
                dis = idc.generate_disasm_line(ea, 0)
                print(f"    {hex(ea)}: {dis}")
                
    idc.qexit(0)

if __name__ == "__main__":
    main()
