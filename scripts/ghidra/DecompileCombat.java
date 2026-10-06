// DecompileCombat.java — decompile an address list against program ascend4.
// Targets are read ONE PER LINE (hex) from work/combat_decomp_targets.txt
// (file offsets == image addresses; program ghp4/ascend4 imported base 0 by
// seed3_run.sh; run with: analyzeHeadless work/ghp4 ascend4 -process
// ascend_restored.bin -noanalysis -scriptPath scripts/ghidra -postScript
// DecompileCombat.java  — the program name for -process is the IMPORTED
// FILE NAME, not the project name (measured 2026-10-05j)).
// Writes work/combat_decomp/<addr>.c. Decompiler warnings on these outputs
// ("bad instruction data", unaff registers) are stream-quality caveats, not
// law violations — cite offsets, re-verify arithmetic on raw bytes.

import java.io.File;
import java.io.PrintWriter;
import ghidra.app.decompiler.*;
import ghidra.program.model.listing.*;
import ghidra.program.model.address.*;

public class DecompileCombat extends ghidra.app.script.GhidraScript {
    public void run() throws Exception {
        java.util.List<Long> tl = new java.util.ArrayList<Long>();
        java.util.Scanner sc = new java.util.Scanner(
            new File("/home/hrethric/projects/ascendancy/work/combat_decomp_targets.txt"), "UTF-8");
        while (sc.hasNextLine()) {
            String s = sc.nextLine().trim();
            if (s.isEmpty() || s.startsWith("//")) continue;
            tl.add(Long.valueOf(s, 16));
        }
        sc.close();
        long[] targets = new long[tl.size()];
        for (int i = 0; i < tl.size(); i++) targets[i] = tl.get(i).longValue();
        println("DECOMPILE-COMBAT: targets=" + targets.length);
        File dir = new File("/home/hrethric/projects/ascendancy/work/combat_decomp");
        dir.mkdirs();
        DecompInterface decomp = new DecompInterface();
        decomp.openProgram(currentProgram);
        AddressSpace is = currentProgram.getImageBase().getAddressSpace();
        long imgBase = currentProgram.getImageBase().getOffset();
        // targets are FILE offsets; program addresses are file_off + imgBase
        // (0 for ghp4/ascend4, 0x100000 for ghp5/ascend5)
        for (long t0 : targets) {
            long t = t0 + imgBase;
            Address a = is.getAddress(t);
            Function f = currentProgram.getFunctionManager().getFunctionAt(a);
            if (f == null) { println("no function at " + a); continue; }
            DecompileResults r =
                decomp.decompileFunction(f, 60, monitor);
            String out = r.decompileCompleted()
                ? r.getDecompiledFunction().getC()
                : "// FAILED: " + r.getErrorMessage();
            PrintWriter w = new PrintWriter(
                new File(dir, Long.toHexString(t0) + ".c"), "UTF-8");
            w.print(out);
            w.close();
            println("decompiled " + a + " -> " + (r.decompileCompleted() ? "ok" : "FAIL"));
        }
        decomp.dispose();
        println("DECOMPILE-COMBAT: DONE");
    }
}
