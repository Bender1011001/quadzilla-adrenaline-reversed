// Seed the raw Quadzilla ARM7 image at its reset vector before auto-analysis.
// @category Quadzilla
import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.Function;

public class SeedQuadzilla extends GhidraScript {
    @Override
    public void run() throws Exception {
        Address entry = toAddr(0x4000);
        currentProgram.getSymbolTable().addExternalEntryPoint(entry);
        disassemble(entry);
        Function fn = getFunctionAt(entry);
        if (fn == null) {
            fn = createFunction(entry, "reset_vector");
        }
        if (fn != null && fn.getName().startsWith("FUN_")) {
            fn.setName("reset_vector", ghidra.program.model.symbol.SourceType.USER_DEFINED);
        }
        println("Seeded Quadzilla reset vector at " + entry);
    }
}
