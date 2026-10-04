// Seed2.java — headless postScript that performs the loader bootstrap Ghidra
// cannot do for an OS/2 LE image.
//
// WHY THIS EXISTS
//   work/ascend_payload.bin is the Watcom flat image extracted from
//   game/ascend.exe at MZ+0x3c (=0x2a50), running to EOF (10832 + 576643 =
//   587475 = the file size exactly). Ghidra 12.1.4 has no LE loader
//   (ghidra/app/util/bin/format/lx/LinearExecutable.java is
//   `throw new NotYetImplementedException()`), so a raw load has no entry
//   point: flow-following disassembly from address 0 decodes 83 instructions
//   and stops (verified in the 2026-10-04 Bootstrap run).
//
// WHY FILE-RELATIVE TARGETS ARE VALID
//   scripts/le_contiguity_test.py measured rel32 CALL targets resolving
//   inside their own page 76:1 against a page-shuffled control, and
//   inter-page targets 135:1 better than the shuffled control. The image is
//   stored in the file in memory order, so disassembling at VA == file offset
//   within the payload is correct for control flow. Absolute data references
//   additionally need the unknown load base (OQ-011) and are NOT attempted
//   here.
//
// SEEDING STRATEGY (no linear sweep, so data never becomes fake instructions)
//   Pass 1: every 0xE8 rel32 CALL whose target lands on a Watcom prologue
//   becomes a function. Pass 2+: scan instructions inside known function
//   bodies for CALL/JMP targets on prologues that are not functions yet.
//   Repeat until the count stops growing (max 6 passes).
//
// API CONTRACT — verified with javap against the shipped jars on 2026-10-04.
//   GhidraScript extends ghidra.program.flatapi.FlatProgramAPI which declares
//   `protected Program currentProgram` and `protected TaskMonitor monitor` as
//   FIELDS (there is no currentProgram() method); createFunction(Address,
//   String) exists, disassembleAll(...) does not; DisassembleCommand exposes
//   applyTo(Program, TaskMonitor) but no getMessage(); function counts come
//   from Program#getFunctionManager(), not from Listing.

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

import java.io.PrintWriter;
import java.util.ArrayList;
import java.util.HashSet;
import java.util.List;
import java.util.Set;

public class Seed2 extends GhidraScript {

    private static boolean isPrologue(byte[] img, int i) {
        if (i < 0 || i + 2 >= img.length) {
            return false;
        }
        int a = img[i] & 0xff, b = img[i + 1] & 0xff, c = img[i + 2] & 0xff;
        // push ebp; mov ebp, esp        (the Watcom -5 default)
        if (a == 0x55 && b == 0x8b && c == 0xec) {
            return true;
        }
        // push ebp; mov [ebp+x], reg style variants
        if (a == 0x55 && b == 0x89) {
            return true;
        }
        // push ebx; push esi / push eax; push edi (frame-pointer-omitted funcs)
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
        // Memory.getBytes(Address, byte[], int arrayOffset, int length) -- the
        // third argument is an OFFSET INTO THE ARRAY, not a length. An earlier
        // revision passed (base, img, size, 0) which asked for zero bytes at
        // the end of the array and silently produced an all-zero image, making
        // the run report prologues=0/e8=0. Use the two-argument overload.
        currentProgram.getMemory().getBytes(base, img);
        int nz = 0, e8total = 0;
        for (int i = 0; i < img.length; i++) {
            if (img[i] != 0) {
                nz++;
            }
            if ((img[i] & 0xff) == 0xe8) {
                e8total++;
            }
        }
        println("SEED2: size=" + size + " nonzero=" + nz + " e8_bytes=" + e8total);
        if (nz == 0) {
            println("SEED2: ABORT - program memory is zero-filled (the load never copied bytes)");
            return;
        }

        // ---- pass 1: 0xE8 rel32 CALL -> prologue
        List<Long> seeds = new ArrayList<Long>();
        int callSites = 0;
        for (int i = 0; i + 5 < img.length; i++) {
            if ((img[i] & 0xff) != 0xe8) {
                continue;
            }
            callSites++;
            int disp = (img[i + 1] & 0xff) | ((img[i + 2] & 0xff) << 8)
                     | ((img[i + 3] & 0xff) << 16) | ((img[i + 4] & 0xff) << 24);
            long t = i + 5L + disp;
            if (t >= 0 && t < size && isPrologue(img, (int) t)) {
                seeds.add(Long.valueOf(t));
            }
        }
        println("SEED2: pass1 call_sites=" + callSites + " target_on_prologue=" + seeds.size());

        AddressSetView whole = new AddressSet(base, currentProgram.getMaxAddress());
        Set<Long> made = new HashSet<Long>();

        for (int pass = 1; pass <= 6; pass++) {
            int created = 0;
            List<Long> next = new ArrayList<Long>();
            for (Long s : seeds) {
                long off = s.longValue();
                if (made.contains(s)) {
                    continue;
                }
                Address a = base.add(off);
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
                    // overlapping body / bad start: ignore, later passes converge
                }
            }
            println("SEED2: pass" + pass + " created=" + created + " total_functions=" + fm.getFunctionCount());
            if (pass == 1 || created > 0) {
                // grow the seed set from what is now real code
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
                        int disp = (img[(int) (p + 1)] & 0xff) | ((img[(int) (p + 2)] & 0xff) << 8)
                                 | ((img[(int) (p + 3)] & 0xff) << 16) | ((img[(int) (p + 4)] & 0xff) << 24);
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

        // ---- coverage + export
        // Coverage: union of function body addresses, computed through the
        // listing rather than a FunctionManager helper (getBodies() does not
        // exist on FunctionManager in this build - verified by javap).
        long covered = 0;
        FunctionIterator cit = fm.getFunctions(true);
        while (cit.hasNext()) {
            ghidra.program.model.address.AddressSetView b = cit.next().getBody();
            if (b != null) {
                covered += b.getNumAddresses();
            }
        }
        println("SEED2: DONE functions=" + fm.getFunctionCount()
                + " code_bytes_covered=" + covered + "/" + size
                + " (" + (100.0 * covered / size) + "%)");

        PrintWriter out = new PrintWriter("/home/hrethric/projects/ascendancy/work/functions.tsv", "UTF-8");
        out.println("offset\tsize\tname");
        FunctionIterator fit = fm.getFunctions(true);
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
        println("SEED2: wrote work/functions.tsv");
    }
}
