import ghidra.app.script.GhidraScript;
import ghidra.program.model.symbol.Symbol;
import ghidra.program.model.symbol.SymbolTable;
import ghidra.program.model.listing.Function;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.CodeUnit;
import ghidra.program.model.listing.Reference;
import ghidra.program.model.symbol.ReferenceIterator;

public class find_references extends GhidraScript {
    
    @Override
       public void run() throws Exception {
        String functionName = "calculate_crc8";
        if (getScriptArgs() != null && getScriptArgs().length > 0) {
            functionName = getScriptArgs()[0];
        }
        
        SymbolTable symbolTable = currentProgram.getSymbolTable();
        Symbol[] symbols = symbolTable.getAllSymbols(functionName);
        
        if (symbols.length == 0) {
            printf("No symbols found with name: %s\n", functionName);
            return;
        }
        
        for (Symbol symbol : symbols) {
            if (symbol.getSymbolType().isFunction()) {
                Function function = (Function) symbol.getObject();
                printf("Found function: %s at %s\n", function.getName(), function.getEntryPoint());
                
                // Find references to this function
                ReferenceIterator references = currentProgram.getReferenceManager().getReferencesTo(function.getEntryPoint());
                
                printf("References to %s:\n", functionName);
                boolean foundReferences = false;
                
                while (references.hasNext()) {
                    Reference ref = references.next();
                    Address fromAddr = ref.getFromAddress();
                    printf("  - Referenced from: %s\n", fromAddr);
                    
                    // Try to find the function containing this reference
                    Function fromFunc = currentProgram.getFunctionManager().getFunctionContaining(fromAddr);
                    if (fromFunc != null) {
                        printf("    In function: %s\n", fromFunc.getName());
                    }
                    
                    foundReferences = true;
                }
                
                if (!foundReferences) {
                    printf("  No references found.\n");
                }
            }
        }
    }
}