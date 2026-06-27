import pefile
import os

def inspect_pe(filepath):
    print(f"\n================ Inspecting {os.path.basename(filepath)} ================")
    try:
        pe = pefile.PE(filepath)
        
        # Check if it has CLR header (indicating .NET)
        has_clr = False
        clr_dir = pefile.DIRECTORY_ENTRY['IMAGE_DIRECTORY_ENTRY_COM_DESCRIPTOR']
        if len(pe.OPTIONAL_HEADER.DATA_DIRECTORY) > clr_dir:
            dir_entry = pe.OPTIONAL_HEADER.DATA_DIRECTORY[clr_dir]
            if dir_entry.VirtualAddress != 0 and dir_entry.Size != 0:
                has_clr = True
                
        print(f"File Type: {'.NET Assembly' if has_clr else 'Native PE'}")
        print(f"Machine: {hex(pe.FILE_HEADER.Machine)} ({pefile.MACHINE_TYPE.get(pe.FILE_HEADER.Machine, 'Unknown')})")
        print(f"Subsystem: {hex(pe.OPTIONAL_HEADER.Subsystem)}")
        
        # Print Exports if any
        if hasattr(pe, 'DIRECTORY_ENTRY_EXPORT'):
            print("Exports:")
            for exp in pe.DIRECTORY_ENTRY_EXPORT.symbols:
                name = exp.name.decode('utf-8') if exp.name else f"ordinal {exp.ordinal}"
                print(f"  {name} at {hex(pe.OPTIONAL_HEADER.ImageBase + exp.address)}")
                
        # Print Imports summary
        if hasattr(pe, 'DIRECTORY_ENTRY_IMPORT'):
            print("Imports:")
            for imp in pe.DIRECTORY_ENTRY_IMPORT:
                print(f"  {imp.dll.decode('utf-8')} ({len(imp.imports)} symbols)")
                
    except Exception as e:
        print(f"Error inspecting {filepath}: {e}")

def main():
    files = [
        'DataMaster-BT.exe',
        'FirmwareUpdater-BT.exe',
        'TtsComLibrary.dll',
        'TtsComUtils.dll',
        'SmartyUSB.exe',
        'ADR9802v2.8.4.exe'
    ]
    for f in files:
        if os.path.exists(f):
            inspect_pe(f)
        else:
            print(f"File not found: {f}")

if __name__ == '__main__':
    main()
