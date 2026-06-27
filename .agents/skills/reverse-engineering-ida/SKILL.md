---
name: reverse-engineering-ida
description: Instructions and guidelines for reverse engineering mixed ARM/Thumb firmware using headless IDA Pro 9.3 and IDAPython scripts on Windows.
---

# Reverse Engineering with Headless IDA Pro 9.3

This skill provides verified procedures, command patterns, and best practices for executing automated reverse engineering tasks on mixed ARM7TDMI (ARM/Thumb) firmware and PE binaries using headless IDA Pro on Windows.

## 1. Environment & Setup

* **IDA Pro Executable (32-bit/64-bit console)**: `C:\Program Files\IDA Professional 9.3\idat.exe`
* **Headless Mode Configuration**: Set the environment variable `TVHEADLESS=1` to prevent IDA from opening any GUI dialogs.
* **Database Format**: Prefer opening the existing `.i64` database rather than re-importing the raw `.bin` file on each run to preserve comments, names, and custom function definitions.

### Executing an IDAPython Script
Run the following PowerShell command pattern to execute a script synchronously:

```powershell
$env:TVHEADLESS="1"; & "C:\Program Files\IDA Professional 9.3\idat.exe" -A -L"<logfile>" -S"<script_path>" "<database_i64_path>"
```

* `-A`: Autonomous mode (suppresses interactive prompts).
* `-L"<logfile>"`: Redirects console output and analysis messages to the specified logfile.
* `-S"<script_path>"`: Path to the IDAPython script to run.

---

## 2. Dealing with Mixed ARM/Thumb Firmware

When dealing with mixed instruction-set architectures (like ARM7TDMI):
1. **Startup Code**: Usually runs in ARM mode (32-bit).
2. **Application Code**: Usually runs in Thumb mode (16-bit).
3. **Literal Pools**: Constants placed directly between functions.

### The Auto-Analyzer Cascade Trap
Ghidra and IDA Pro auto-analyzers frequently fail on literal pools, classifying them as code or vice versa, leading to corrupted function boundaries. 

* **Best Practice**: Use **Restricted-Range Disassembly**. Force disassembly of known entry points with strict address boundaries (capping disassembly at the distance to the next entry point) to prevent code-flow analysis from cascading into data regions.

---

## 3. Advanced Binary Auditing Patterns

### Locating Offset-Based RAM Writes
In Thumb code, writing to specific RAM addresses (e.g., `0x2005D7`) is often done dynamically using a base pointer + offset (e.g., `STRB R0, [R4,#0x13]` where `R4` is loaded with the base address `0x2005C4`). 

To locate all potential writers of a variable:
1. Search all literal pools in the disassembly for addresses within a ±32 byte window of the target variable.
2. In functions loading those base addresses, scan for `STR`/`STRB`/`STRH` instructions matching the target offset.

---

## 4. Script Examples

### Template for IDAPython Analysis Script

```python
import idc
import idautils
import ida_funcs
import ida_ua

def main():
    print("=== Custom Analysis Run ===")
    # Perform binary exploration, print findings to stdout
    for func_ea in idautils.Functions():
        name = idc.get_func_name(func_ea)
        print(f"Function {hex(func_ea)}: {name}")
        
    # Always exit cleanly to close the headless IDA process
    idc.qexit(0)

if __name__ == "__main__":
    main()
```
