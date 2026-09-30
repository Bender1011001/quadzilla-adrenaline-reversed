// Seed additional, independently confirmed Quadzilla execution entries.
// @category Quadzilla
import java.math.BigInteger;

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.lang.Register;
import ghidra.program.model.listing.Function;
import ghidra.program.model.symbol.SourceType;

public class SeedQuadzillaEntries extends GhidraScript {
    private static final long IMAGE_START = 0x4000L;
    private static final long IMAGE_END = 0xBD00L;

    @Override
    public void run() throws Exception {
        String[] args = getScriptArgs();
        if (args.length == 0) {
            throw new IllegalArgumentException("SeedQuadzillaEntries requires mode@start:end ranges");
        }
        Register thumbMode = currentProgram.getLanguage().getRegister("TMode");
        if (thumbMode == null) {
            throw new IllegalStateException("ARM language has no TMode context register");
        }
        int created = 0;
        int existing = 0;
        for (String arg : args) {
            String[] modeAndRange = arg.split("@", -1);
            if (modeAndRange.length != 2 ||
                !(modeAndRange[0].equals("arm") || modeAndRange[0].equals("thumb"))) {
                throw new IllegalArgumentException("expected arm@start:end or thumb@start:end: " + arg);
            }
            String[] parts = modeAndRange[1].split(":", -1);
            if (parts.length != 2) {
                throw new IllegalArgumentException("expected start:end range: " + arg);
            }
            long value = Long.decode(parts[0]);
            long endValue = Long.decode(parts[1]);
            if (value < IMAGE_START || endValue > IMAGE_END || endValue <= value) {
                throw new IllegalArgumentException("range outside image or empty: " + arg);
            }
            Address entry = toAddr(value);
            Address end = toAddr(endValue - 1);
            clearListing(entry, end);
            BigInteger mode = modeAndRange[0].equals("thumb") ? BigInteger.ONE : BigInteger.ZERO;
            currentProgram.getProgramContext().setValue(thumbMode, entry, end, mode);
            disassemble(entry);
            Function function = getFunctionAt(entry);
            if (function == null) {
                function = createFunction(entry, String.format("entry_%08x", value));
                if (function == null) {
                    throw new IllegalStateException("could not create function at " + entry);
                }
                created++;
            }
            else {
                existing++;
            }
            if (function.getName().startsWith("FUN_")) {
                function.setName(String.format("entry_%08x", value), SourceType.USER_DEFINED);
            }
        }
        println("Seeded confirmed entries: created=" + created + " existing=" + existing);
    }
}
