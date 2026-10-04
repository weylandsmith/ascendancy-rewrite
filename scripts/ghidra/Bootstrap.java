// Bootstrap.java — headless postScript for ascend.exe's Watcom LE payload.
//
// Why this exists: work/ascend_payload.bin is loaded as a RAW image because
// Ghidra 12.1.4 has no OS/2 LE loader
// (ghidra/app/util/bin/format/lx/LinearExecutable.java is
//  `throw new NotYetImplementedException()`). With no entry point,
// auto-analysis finds almost nothing, so we perform the bootstrap a loader
// would: disassemble following flow, then create a function at every CALL
// target.
//
// Why file-relative targets are meaningful: scripts/le_contiguity_test.py
// measured rel32 CALL targets resolving 76:1 in-page and 135:1 inter-page
// against a page-shuffled control, i.e. the payload bytes sit in memory order.
//
// API CONTRACT (verified with javap against the shipped jars on 2026-10-04;
// an earlier version of this script failed to compile because it used
// recalled API):
//   * GhidraScript extends ghidra.program.flatapi.FlatProgramAPI, which
//     declares `protected Program currentProgram` and
//     `protected TaskMonitor monitor` as FIELDS. There is no
//     currentProgram() method.
//   * FlatProgramAPI has `createFunction(Address, String)`; there is no
//     disassembleAll(...).
//   * ghidra.app.cmd.disassemble.DisassembleCommand extends
//     BackgroundCommand<Program> and exposes
//     `synchronized boolean applyTo(Program, TaskMonitor)`; it has NO
//     getMessage(). Function counts come from
//     Program#getFunctionManager().getFunctionCount(), not Listing.

import ghidra.app.cmd.disassemble.DisassembleCommand;
import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.address.AddressSet;
import ghidra.program.model.address.AddressSetView;
import ghidra.program.model.listing.FunctionManager;
import ghidra.program.model.listing.Instruction;
import ghidra.program.model.listing.InstructionIterator;
import ghidra.program.model.listing.Listing;

public class Bootstrap extends GhidraScript {

    @Override
    public void run() throws Exception {
        Listing listing = currentProgram.getListing();
        FunctionManager fm = currentProgram.getFunctionManager();
        Address base = currentProgram.getMinAddress();
        Address end = currentProgram.getMaxAddress();
        println("BOOTSTRAP: image " + base + " .. " + end + " span=" + end.subtract(base));

        AddressSetView whole = new AddressSet(base, end);
        DisassembleCommand cmd = new DisassembleCommand(base, whole, true);
        boolean ok = cmd.applyTo(currentProgram, monitor);
        println("BOOTSTRAP: disassemble ok=" + ok);

        int insns = 0;
        java.util.List<Address> callTargets = new java.util.ArrayList<Address>();
        InstructionIterator it = listing.getInstructions(true);
        while (it.hasNext() && !monitor.isCancelled()) {
            Instruction ins = it.next();
            insns++;
            if (ins.getMnemonicString().equals("CALL")) {
                Address[] flows = ins.getFlows();
                if (flows.length > 0) {
                    callTargets.add(flows[0]);
                }
            }
        }
        println("BOOTSTRAP: insns=" + insns + " call_sites=" + callTargets.size());

        java.util.Set<Address> seen = new java.util.HashSet<Address>();
        int created = 0, skippedExisting = 0, failed = 0;
        for (Address a : callTargets) {
            if (!seen.add(a)) {
                continue;
            }
            if (fm.getFunctionAt(a) != null || listing.getDataAt(a) != null) {
                skippedExisting++;
                continue;
            }
            try {
                if (createFunction(a, null) != null) {
                    created++;
                } else {
                    failed++;
                }
            } catch (Exception e) {
                failed++;  // overlapping body: next pass converges
            }
        }
        println("BOOTSTRAP: distinct_targets=" + seen.size()
                + " created=" + created
                + " skipped_existing=" + skippedExisting
                + " failed=" + failed
                + " total_functions=" + fm.getFunctionCount());
    }
}
