// Seed3.java — bootstrap + data-xref export for work/ascend_restored.bin.
//
// WHY THIS EXISTS
//   Seed2 bootstrapped control flow on the RAW payload (269 functions) but
//   could do nothing with data: absolute operands were unresolved (OQ-011).
//   The POINTER LAW is CLOSED (docs/re/r1-savestate.md 2026-10-05i):
//   runtime_u32 = P0 + payload_file_offset(target), and the image was linked
//   at base 0x1d4000 = P0 + 0x14bb0. scripts/r1_restore_sites.py rewrote the
//   2,080 IMAGE-class pointer slots to d = rv - P0, i.e. payload-file-offset
//   values — the SAME address space a raw Ghidra load uses (base 0). So the
//   disassembler's constant-reference machinery now produces data xrefs
//   natively, and Seed3's job is: seed functions (Seed2 strategy, unchanged
//   — code bytes are byte-identical between raw and restored except at fixed-
//   up slots), then EXPORT what the xrefs make possible.
//
// EXPORTS (absolute paths, overwriting):
//   work/functions3.tsv     offset  size  name           (all functions)
//   work/code2data.tsv      target  hits  entry|?   first_ref
//       one row per address referenced BY A FUNCTION in the code object
//       [0x14bb0, 0x82bb0) via a DATA reference (operand or pointer target);
//       entry = hex entry point of the function containing the target if the
//       target is inside a function (vtable callee!), else '?'.
//
// API contract: same as Seed2 (loader.md footer) — currentProgram/monitor are
// FIELDS; Memory.getBytes(base,img) two-arg overload ONLY.

import ghidra.app.cmd.disassemble.DisassembleCommand;
import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.address.AddressSet;
import ghidra.program.model.address.AddressSetView;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.FunctionIterator;
import ghidra.program.model.listing.FunctionManager;
import ghidra.program.model.listing.Instruction;
import ghidra.program.model.listing.InstructionIterator;
import ghidra.program.model.listing.Listing;
import ghidra.program.model.symbol.Reference;
import ghidra.program.model.symbol.ReferenceIterator;
import ghidra.program.model.symbol.RefType;
import ghidra.program.model.symbol.SourceType;

import java.io.PrintWriter;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.TreeMap;

public class Seed3 extends GhidraScript {

    private static final long CODE_LO = 0x14bb0L;
    private static final long CODE_HI = 0x82bb0L;

    private static boolean isPrologue(byte[] img, int i) {
        if (i < 0 || i + 2 >= img.length) {
            return false;
        }
        int a = img[i] & 0xff, b = img[i + 1] & 0xff, c = img[i + 2] & 0xff;
        if (a == 0x55 && b == 0x8b && c == 0xec) {
            return true;
        }
        if (a == 0x55 && b == 0x89) {
            return true;
        }
        if (a == 0x53 && (b == 0x56 || b == 0x57)) {
            return true;
        }
        if (a == 0x56 && (b == 0x57 || b == 0x53)) {
            return true;
        }
        return false;
    }

    @Override
    public void run() throws Exception {
        final Listing listing = currentProgram.getListing();
        final FunctionManager fm = currentProgram.getFunctionManager();
        final Address base = currentProgram.getMinAddress();
        final long size = currentProgram.getMaxAddress().subtract(base) + 1;

        byte[] img = new byte[(int) size];
        currentProgram.getMemory().getBytes(base, img);
        int nz = 0;
        for (byte b : img) {
            if (b != 0) {
                nz++;
            }
        }
        println("SEED3: size=" + size + " nonzero=" + nz);
        if (nz == 0) {
            println("SEED3: ABORT - zero image (getBytes misuse? see Seed2 header)");
            return;
        }

        // ---- function seeding (Seed2 strategy verbatim) ----
        List<Long> seeds = new ArrayList<Long>();
        for (int i = 0; i + 5 < img.length; i++) {
            if ((img[i] & 0xff) != 0xe8) {
                continue;
            }
            int disp = (img[i + 1] & 0xff) | ((img[i + 2] & 0xff) << 8)
                     | ((img[i + 3] & 0xff) << 16) | ((img[i + 4] & 0xff) << 24);
            long t = i + 5L + disp;
            if (t >= 0 && t < size && isPrologue(img, (int) t)) {
                seeds.add(Long.valueOf(t));
            }
        }
        println("SEED3: pass1 seeds=" + seeds.size());

        // ---- vtable-entry seeding (2026-10-05j) ----
        // The restored image carries the game's pointer tables in-file
        // (r1_restore_sites wrote their entries). A run >=4 of image-class
        // pointers is a vtable/GOT-style table; its ENTRY slots are function
        // addresses, and C++ member calls go through them, so control flow is
        // dark without them (Seed2's 269 functions saw only 431 data refs).
        // Seed every table entry that sits on a prologue, and record the
        // tables themselves (they are data landmarks, exported separately).
        Set<Long> made = new HashSet<Long>();
        int vt = 0, vtSeeds = 0;
        PrintWriter outT = new PrintWriter(
                "/home/hrethric/projects/ascendancy/work/vtables3.tsv", "UTF-8");
        outT.println("table_off\tn\tentries(first 16, restored)");
        {
            int o = (int) CODE_LO;
            while (o + 16 <= img.length) {
                List<Long> run = new ArrayList<Long>();
                int q = o;
                while (q + 4 <= img.length && run.size() < 64) {
                    long v = (img[q] & 0xffL) | ((img[q + 1] & 0xffL) << 8)
                           | ((img[q + 2] & 0xffL) << 16) | ((img[q + 3] & 0xffL) << 24);
                    if (v >= CODE_LO && v < CODE_HI && v % 4 == 0) {
                        run.add(Long.valueOf(v));
                        q += 4;
                    } else {
                        break;
                    }
                }
                if (run.size() >= 4) {
                    vt++;
                    StringBuilder sb = new StringBuilder();
                    for (int i = 0; i < Math.min(run.size(), 16); i++) {
                        sb.append(Long.toHexString(run.get(i).longValue()));
                        sb.append(i + 1 < Math.min(run.size(), 16) ? "," : "");
                    }
                    outT.println(Long.toHexString(o) + "\t" + run.size() + "\t" + sb);
                    for (Long v : run) {
                        if (isPrologue(img, v.intValue())) {
                            Long key = v;
                            if (!made.contains(key) && !seeds.contains(key)) {
                                seeds.add(key);
                                vtSeeds++;
                            }
                        }
                    }
                    o = q;
                } else {
                    o += 4;
                }
            }
        }
        outT.close();
        println("SEED3: vtables>=4entries=" + vt + " extra function seeds=" + vtSeeds);

        AddressSetView whole = new AddressSet(base, currentProgram.getMaxAddress());
        for (int pass = 1; pass <= 6; pass++) {
            int created = 0;
            List<Long> next = new ArrayList<Long>();
            for (Long s : seeds) {
                if (made.contains(s)) {
                    continue;
                }
                Address a = base.add(s.longValue());
                if (fm.getFunctionAt(a) != null) {
                    made.add(s);
                    continue;
                }
                try {
                    DisassembleCommand dc = new DisassembleCommand(a, whole, true);
                    dc.applyTo(currentProgram, monitor);
                    if (createFunction(a, null) != null) {
                        created++;
                        made.add(s);
                    }
                } catch (Exception e) {
                    // overlapping / bad start: next passes converge anyway
                }
            }
            println("SEED3: pass" + pass + " created=" + created
                    + " functions=" + fm.getFunctionCount());
            if (pass == 1 || created > 0) {
                next.clear();
                FunctionIterator fit = fm.getFunctions(true);
                while (fit.hasNext()) {
                    Function f = fit.next();
                    Address sa = f.getEntryPoint();
                    long fo = sa.subtract(base);
                    Address ea = f.getBody().getMaxAddress();
                    long feo = (ea == null) ? fo : ea.subtract(base);
                    if (fo < 0 || feo < fo || feo >= size) {
                        continue;
                    }
                    for (long p = fo; p + 5 < feo + 6 && p + 5 < img.length; p++) {
                        if ((img[(int) p] & 0xff) != 0xe8) {
                            continue;
                        }
                        int disp = (img[(int) (p + 1)] & 0xff)
                                 | ((img[(int) (p + 2)] & 0xff) << 8)
                                 | ((img[(int) (p + 3)] & 0xff) << 16)
                                 | ((img[(int) (p + 4)] & 0xff) << 24);
                        long t = p + 5L + disp;
                        if (t >= 0 && t < size && isPrologue(img, (int) t)) {
                            Long key = Long.valueOf(t);
                            if (!made.contains(key)) {
                                next.add(key);
                            }
                        }
                    }
                }
                seeds = next;
            }
            if (created == 0 && seeds.isEmpty()) {
                break;
            }
        }

        // ---- code -> data xref census ----
        // For every instruction inside every function whose ENTRY lies in the
        // code object, collect DATA references (operand targets). A target is
        // "useful" if it is in [0, size) — the restored image-class pointers
        // land there; unfixed runtime garbage (0x1d4xxx-era values were
        // rewritten; heap pointers stay > size and are skipped).
        Map<Long, long[]> agg = new TreeMap<Long, long[]>();   // target -> [hits, firstRefOff]
        long dataRefs = 0;
        FunctionIterator fit = fm.getFunctions(true);
        while (fit.hasNext()) {
            Function f = fit.next();
            long entry = f.getEntryPoint().subtract(base);
            if (entry < CODE_LO || entry >= CODE_HI) {
                continue;
            }
            InstructionIterator iit = listing.getInstructions(f.getBody(), true);
            while (iit.hasNext()) {
                Instruction ins = iit.next();
                // javap-verified 2026-10-05: Instruction.getReferencesFrom()
                // returns Reference[] (NOT ReferenceIterator as assumed).
                Reference[] refs = ins.getReferencesFrom();
                for (Reference r : refs) {
                    RefType rt = r.getReferenceType();
                    // javap-verified 2026-10-05 (SoftwareModeling.jar):
                    // RefType is an abstract class; every CALL/JUMP kind is a
                    // FlowType subclass -> instanceof is the control filter.
                    if (rt instanceof ghidra.program.model.symbol.FlowType) {
                        continue;   // control flow already covered
                    }
                    Address to = r.getToAddress();
                    if (!to.isExternalAddress()) {   // NOT isInExternalSpace
                        long off = to.subtract(base);
                        if (off >= 0 && off < size) {
                            dataRefs++;
                            long[] v = agg.get(Long.valueOf(off));
                            if (v == null) {
                                agg.put(Long.valueOf(off),
                                        new long[]{1L, ins.getAddress().subtract(base)});
                            } else {
                                v[0]++;
                            }
                        }
                    }
                }
            }
        }
        println("SEED3: data refs from code-object functions=" + dataRefs
                + " distinct targets=" + agg.size());

        // ---- exports ----
        PrintWriter out = new PrintWriter(
                "/home/hrethric/projects/ascendancy/work/functions3.tsv", "UTF-8");
        out.println("offset\tsize\tname");
        fit = fm.getFunctions(true);
        while (fit.hasNext()) {
            Function f = fit.next();
            Address sa = f.getEntryPoint();
            Address ea = f.getBody().getMaxAddress();
            long off = sa.subtract(base);
            long fs = (ea == null) ? 0 : ea.subtract(sa) + 1;
            String nm = f.getName();
            if (nm != null) {
                nm = nm.replace('\t', ' ');
            }
            out.println(Long.toHexString(off) + "\t" + fs + "\t" + nm);
        }
        out.close();

        // function-span lookup for the entry column
        List<long[]> spans = new ArrayList<long[]>();
        List<Function> fns = new ArrayList<Function>();
        fit = fm.getFunctions(true);
        while (fit.hasNext()) {
            Function f = fit.next();
            Address ea = f.getBody().getMaxAddress();
            long fo = f.getEntryPoint().subtract(base);
            long fe = (ea == null) ? fo : ea.subtract(base);
            spans.add(new long[]{fo, fe});
            fns.add(f);
        }

        PrintWriter out2 = new PrintWriter(
                "/home/hrethric/projects/ascendancy/work/code2data.tsv", "UTF-8");
        out2.println("target\thits\tentry\tfirst_ref");
        int withEntry = 0;
        for (Map.Entry<Long, long[]> e : agg.entrySet()) {
            long t = e.getKey().longValue();
            String ent = "?";
            for (int i = 0; i < spans.size(); i++) {
                long[] sp = spans.get(i);
                if (t >= sp[0] && t <= sp[1]) {
                    ent = Long.toHexString(sp[0]);
                    break;
                }
            }
            if (!"?".equals(ent)) {
                withEntry++;
            }
            out2.println(Long.toHexString(t) + "\t" + e.getValue()[0] + "\t"
                    + ent + "\t" + Long.toHexString(e.getValue()[1]));
        }
        out2.close();
        println("SEED3: DONE functions=" + fm.getFunctionCount()
                + " distinct_data_targets=" + agg.size()
                + " targets_inside_functions=" + withEntry
                + " -> work/functions3.tsv work/code2data.tsv");
    }
}
