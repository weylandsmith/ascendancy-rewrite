// RefProbe.java — settle OQ-011: does the image use absolute addressing, and
// if so what is C where VA = payload_file_offset + C?
//
// Run against the EXISTING project (already seeded by Seed2.java):
//   analyzeHeadless work/ghp3 ascend3 -process ascend_payload.bin \
//       -noanalysis -scriptPath work -postScript RefProbe.java
//
// WHY THIS PROBE INSTEAD OF A RAW-DWORD SWEEP
//   A previous raw-dword sweep rejected its top candidate as a density
//   artefact: adjacent short string literals sit ~7 bytes apart, so a random
//   dword hits "some string start" often enough to fake a consensus. This
//   version only counts operands that a DISASSEMBLER decoded (imm32 operands
//   and disp32 displacements), and its discriminator is not the hit count but
//   the number of DISTINCT anchor strings a single C explains - a fake C
//   cannot explain a whole cluster of far-apart literals.
//
// Also reports whether the code is Watcom position-independent ([ebx+disp32]
// style, compiled -FPi), because if it is, absolute-address recovery is the
// wrong question entirely.

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.Instruction;
import ghidra.program.model.listing.InstructionIterator;
import ghidra.program.model.listing.Listing;
import ghidra.program.model.scalar.Scalar;

import java.util.ArrayList;
import java.util.Collections;
import java.util.Comparator;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;

public class RefProbe extends GhidraScript {

    // Anchors are DISCOVERED, not listed. An earlier revision hard-coded 15
    // guessed names, of which only 5 existed, and 4 of those sat inside a
    // 60-byte cluster (0x83704..0x83740) - a candidate C aligning "4 anchors"
    // there is arithmetic coincidence, not a base. Every DATA\<file> path in
    // the image is used instead (26 of them, spanning 0x830f0..0x88e4c, which
    // is wide enough that one C explaining ~all of them cannot be luck).
    // These strings are also the highest-value anchors for the P2 work: they
    // name the shape libraries (SHP), the UI shape libraries (the .tmp files
    // - 1starmap, 3cfgnew, 7racesel, 8shipdes, 9ENDGAME, 12start, 13negot,
    // 16battle, 20res, 10status) and the hazards (HAZ).
    private static final java.util.regex.Pattern ANCHOR_PAT =
        java.util.regex.Pattern.compile("DATA\\\\[A-Za-z%0-9._]{2,32}");

    @Override
    public void run() throws Exception {
        final Address base = currentProgram.getMinAddress();
        final long size = currentProgram.getMaxAddress().subtract(base) + 1;
        byte[] img = new byte[(int) size];
        currentProgram.getMemory().getBytes(base, img);
        println("REFPROBE: size=" + size);

        // Locate anchors inside the image (case-insensitive, so it works
        // whether the template is upper- or lower-case in the binary).
        List<Long> anchors = new ArrayList<Long>();
        List<String> anchorNames = new ArrayList<String>();
        String asText = new String(img, "ISO-8859-1");
        java.util.regex.Matcher am = ANCHOR_PAT.matcher(asText);
        while (am.find()) {
            anchors.add(Long.valueOf(am.start()));
            anchorNames.add(am.group() + "@" + Long.toHexString(am.start()));
        }
        println("REFPROBE: anchors_found=" + anchors.size());
        for (int i = 0; i < anchorNames.size(); i++) {
            print("  " + anchorNames.get(i));
        }
        println("");
        if (anchors.size() < 4) {
            println("REFPROBE: too few anchors, aborting");
            return;
        }

        // Collect disassembler-decoded operands.
        final Listing listing = currentProgram.getListing();
        List<Long> imms = new ArrayList<Long>();
        List<Long> disps = new ArrayList<Long>();
        int insns = 0, ebxRel = 0, absAbs = 0;
        InstructionIterator it = listing.getInstructions(true);
        while (it.hasNext() && !monitor.isCancelled()) {
            Instruction ins = it.next();
            insns++;
            String txt = ins.toString();
            if (txt.contains("[EBX") || txt.contains("[ebx")) {
                ebxRel++;
            }
            // getOpObjects per operand index (this build has no
            // ghidra.program.model.operands package; verified by scanning every
            // shipped jar for that class - not present).
            for (int oi = 0; oi < ins.getNumOperands(); oi++) {
                Object[] objs = ins.getOpObjects(oi);
                for (int k = 0; k < objs.length; k++) {
                    Object o = objs[k];
                    if (o instanceof Scalar) {
                        imms.add(Long.valueOf(((Scalar) o).getUnsignedValue()));
                    } else if (o instanceof Address) {
                        long va = ((Address) o).getOffset();
                        disps.add(Long.valueOf(va));
                        if (va >= 0 && va < size) {
                            absAbs++;
                        }
                    }
                }
            }
        }
        println("REFPROBE: insns=" + insns + " imm_operands=" + imms.size()
                + " mem_operands=" + disps.size() + " in_image=" + absAbs
                + " ebx_relative_insns=" + ebxRel);

        // Control: how often would a random in-image address coincide with an
        // anchor's first 12 bytes being "stringy"? Measured directly.
        long anchorBytes = 0;
        for (Long a : anchors) {
            anchorBytes += 14;
        }
        println("REFPROBE: control_random_hit_rate=" + (1.0 * anchorBytes / size));

        // Candidate C = operand - anchor, scored by DISTINCT anchors explained.
        Map<Long, Set<Long>> explained = new HashMap<Long, Set<Long>>();
        List<Long> all = new ArrayList<Long>();
        all.addAll(imms);
        all.addAll(disps);
        for (Long v : all) {
            long vv = v.longValue();
            if (vv <= 0 || vv >= (1L << 31)) {
                continue;
            }
            for (Long a : anchors) {
                long c = vv - a.longValue();
                if (c < 0 || c > size) {
                    continue;
                }
                Set<Long> s = explained.get(Long.valueOf(c));
                if (s == null) {
                    s = new HashSet<Long>();
                    explained.put(Long.valueOf(c), s);
                }
                s.add(a);
            }
        }
        List<Map.Entry<Long, Set<Long>>> entries = new ArrayList<Map.Entry<Long, Set<Long>>>(explained.entrySet());
        Collections.sort(entries, new Comparator<Map.Entry<Long, Set<Long>>>() {
            public int compare(Map.Entry<Long, Set<Long>> x, Map.Entry<Long, Set<Long>> y) {
                return y.getValue().size() - x.getValue().size();
            }
        });
        println("REFPROBE: candidate C count=" + entries.size());
        int shown = 0;
        for (Map.Entry<Long, Set<Long>> e : entries) {
            if (shown++ >= 8) {
                break;
            }
            println("REFPROBE: C=0x" + Long.toHexString(e.getKey().longValue())
                    + " distinct_anchors=" + e.getValue().size()
                    + " (need ~" + anchors.size() + " for a real base)");
        }
        println("REFPROBE: DONE");
    }
}
