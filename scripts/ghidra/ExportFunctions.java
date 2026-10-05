// ExportFunctions.java — dump ALL functions (addr, size) of the current
// program to work/functions_full.tsv. Run against ghp5/ascend5 (full auto-
// analysis of ascend_restored.bin; base 0x100000, so subtract 0x100000 for
// file offsets). Join with work/attribution.tsv for module labels.
import java.io.PrintWriter;
import ghidra.program.model.listing.*;
import ghidra.program.model.address.Address;

public class ExportFunctions extends ghidra.app.script.GhidraScript {
    public void run() throws Exception {
        PrintWriter w = new PrintWriter(
            "/home/hrethric/projects/ascendancy/work/functions_full.tsv", "UTF-8");
        w.println("file_off\tsize");
        long base = currentProgram.getImageBase().getOffset();
        FunctionIterator it =
            currentProgram.getFunctionManager().getFunctions(true);
        int n = 0;
        for (; it.hasNext(); ) {
            Function f = it.next();
            Address a = f.getEntryPoint();
            long size = 0;
            try {
                size = f.getBody().getNumAddresses();
            } catch (Exception e) { size = 0; }
            w.println(Long.toHexString(a.getOffset() - base) + "\t" + size);
            n++;
        }
        w.close();
        println("EXPORT-FUNCTIONS: " + n + " functions -> work/functions_full.tsv");
    }
}
