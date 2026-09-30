// Export function and direct-call facts from a Ghidra-analyzed Quadzilla image.
// @category Quadzilla
import java.io.File;
import java.io.PrintWriter;
import java.security.MessageDigest;
import java.util.ArrayList;
import java.util.Collections;
import java.util.Comparator;
import java.util.List;

import ghidra.app.script.GhidraScript;
import ghidra.framework.Application;
import ghidra.program.model.address.Address;
import ghidra.program.model.address.AddressRange;
import ghidra.program.model.address.AddressRangeIterator;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.FunctionIterator;
import ghidra.program.model.listing.Instruction;
import ghidra.program.model.listing.InstructionIterator;

public class ExportQuadzilla extends GhidraScript {
    private static final long IMAGE_START = 0x4000L;
    private static final long IMAGE_END = 0xBD00L;

    private static String q(String value) {
        return "\"" + value.replace("\\", "\\\\").replace("\"", "\\\"")
            .replace("\n", "\\n").replace("\r", "\\r") + "\"";
    }

    private static String hx(long value) {
        return String.format("0x%x", value);
    }

    private String imageSha256() throws Exception {
        MessageDigest digest = MessageDigest.getInstance("SHA-256");
        byte[] buffer = new byte[4096];
        long offset = IMAGE_START;
        while (offset < IMAGE_END) {
            int want = (int)Math.min(buffer.length, IMAGE_END - offset);
            int got = currentProgram.getMemory().getBytes(toAddr(offset), buffer, 0, want);
            if (got != want) {
                throw new IllegalStateException("short memory read at " + hx(offset) + ": " + got + "/" + want);
            }
            digest.update(buffer, 0, got);
            offset += got;
        }
        StringBuilder value = new StringBuilder();
        for (byte b : digest.digest()) {
            value.append(String.format("%02x", b & 0xff));
        }
        return value.toString();
    }

    private static class FunctionRow {
        long start;
        long end;
        long size;
        String name;
        int instructions;
        List<long[]> chunks = new ArrayList<>();
    }

    private static class CallRow {
        long caller;
        long site;
        long callee;
        String mnemonic;
    }

    @Override
    public void run() throws Exception {
        String[] args = getScriptArgs();
        if (args.length != 1) {
            throw new IllegalArgumentException("ExportQuadzilla requires one output JSON path");
        }
        List<FunctionRow> functions = new ArrayList<>();
        List<CallRow> calls = new ArrayList<>();
        FunctionIterator iterator = currentProgram.getFunctionManager().getFunctions(true);
        while (iterator.hasNext()) {
            Function fn = iterator.next();
            long start = fn.getEntryPoint().getOffset();
            if (start < IMAGE_START || start >= IMAGE_END) {
                continue;
            }
            FunctionRow row = new FunctionRow();
            row.start = start;
            row.end = fn.getBody().getMaxAddress().getOffset() + 1;
            row.size = fn.getBody().getNumAddresses();
            row.name = fn.getName();
            AddressRangeIterator ranges = fn.getBody().getAddressRanges();
            while (ranges.hasNext()) {
                AddressRange range = ranges.next();
                row.chunks.add(new long[] {
                    range.getMinAddress().getOffset(),
                    range.getMaxAddress().getOffset() + 1
                });
            }
            InstructionIterator instructions = currentProgram.getListing().getInstructions(fn.getBody(), true);
            while (instructions.hasNext()) {
                Instruction instruction = instructions.next();
                row.instructions++;
                if (!instruction.getFlowType().isCall()) {
                    continue;
                }
                for (Address target : instruction.getFlows()) {
                    Function callee = currentProgram.getFunctionManager().getFunctionAt(target);
                    if (callee == null) {
                        callee = currentProgram.getFunctionManager().getFunctionContaining(target);
                    }
                    if (callee == null) {
                        continue;
                    }
                    CallRow call = new CallRow();
                    call.caller = start;
                    call.site = instruction.getAddress().getOffset();
                    call.callee = callee.getEntryPoint().getOffset();
                    call.mnemonic = instruction.getMnemonicString();
                    calls.add(call);
                }
            }
            functions.add(row);
        }
        Collections.sort(functions, Comparator.comparingLong(row -> row.start));
        Collections.sort(calls, Comparator.comparingLong((CallRow row) -> row.caller)
            .thenComparingLong(row -> row.site).thenComparingLong(row -> row.callee));

        File output = new File(args[0]);
        File parent = output.getParentFile();
        if (parent != null) {
            parent.mkdirs();
        }
        try (PrintWriter out = new PrintWriter(output, "UTF-8")) {
            out.println("{");
            out.println("  \"format\": \"quadzilla-disassembler-map-v1\",");
            out.println("  \"tool\": \"Ghidra\",");
            out.println("  \"tool_version\": " + q(Application.getApplicationVersion()) + ",");
            out.println("  \"processor\": " + q(currentProgram.getLanguageID().toString()) + ",");
            out.println("  \"raw_sha256\": " + q(imageSha256()) + ",");
            out.println("  \"image_range\": [\"0x4000\", \"0xbd00\"],");
            out.println("  \"functions\": [");
            for (int i = 0; i < functions.size(); i++) {
                FunctionRow row = functions.get(i);
                out.print("    {\"start\":" + q(hx(row.start)) + ",\"end\":" + q(hx(row.end))
                    + ",\"size\":" + row.size + ",\"name\":" + q(row.name)
                    + ",\"instruction_count\":" + row.instructions + ",\"chunks\":[");
                for (int j = 0; j < row.chunks.size(); j++) {
                    long[] chunk = row.chunks.get(j);
                    if (j > 0) out.print(",");
                    out.print("[" + q(hx(chunk[0])) + "," + q(hx(chunk[1])) + "]");
                }
                out.print("]}");
                out.println(i + 1 < functions.size() ? "," : "");
            }
            out.println("  ],");
            out.println("  \"calls\": [");
            for (int i = 0; i < calls.size(); i++) {
                CallRow row = calls.get(i);
                out.print("    {\"caller\":" + q(hx(row.caller)) + ",\"site\":" + q(hx(row.site))
                    + ",\"callee\":" + q(hx(row.callee)) + ",\"mnemonic\":" + q(row.mnemonic) + "}");
                out.println(i + 1 < calls.size() ? "," : "");
            }
            out.println("  ]");
            out.println("}");
        }
        println("WROTE " + output + " functions=" + functions.size() + " calls=" + calls.size());
    }
}
