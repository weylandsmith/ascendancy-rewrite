# REFUTED ROUTES — do not retry (knowledge transfer from v1)

Read the matching section before starting any research action. Each entry:
what was tried, how it died, what evidence killed it. Re-running a FORBIDDEN
route costs a turn and is itself a contract violation (docs/GOAL.txt
constraints). Sources: v1 turn log (archive/ralph-v1/STATE.md),
docs/OPEN-QUESTIONS.md, docs/re/*.md, gate stages 3q/3r.

## R1. Static absolute load base for the Watcom LE image — FORBIDDEN (5th attempt)
Four independent scripted tests, all refuted (v1 2026-10-04):
- vtable plateau vote 25/169 vs 0.4 expected
- ebx-relative vote 71 < spacing control 82
- zero anchor-valued operands over 604k disassembled insns
- high-coverage-immediate->ASCII 4/52 vs 1.0 control
Pattern each time: plausible vote, dies to its control. Details docs/re/loader.md §4.
THE ANSWER instead: runtime pointer law, OQ-011 CLOSED — runtime_u32 =
P0 + payload_file_offset(target); P0 = B - H per-run from r1_sav_scan.py;
work/ascend_restored.bin is the Ghidra-ready artifact. Never hard-code a base.

## R2. Blind .shp pixel-codec sweeps — FORBIDDEN (7th sweep)
Six static angles exhausted, all negative (OQ-005): (1) 5 RLE grammars x hdr
offsets exact-span sweep, 0 survivors; (2) tokenisation-grammar BFS, 100/100
negative (scripts/shp_tokenize.py, docs/re/shp-tokenize.md); (3) u8-len-per-
line tiling 3/1530 = noise; (4) rec1+ +16 'base dims' refuted (33.9% == rec0);
(5) cos_ship same-box diff: only colour bytes [3,6,11] vary; (6) nested-sublib
/ metadata-slot negatives. Entropy 3.4-3.9 b/B => light RLE. Container is
CLOSED 208/208 (docs/re/shp.md). Only sanctioned route: find the exe shape
loader via call graph + live image (W3).

## R3. LE header field-map / 'page table' readings — CLOSED NEGATIVE
le_tables_anchored.py: no object parse sums cbObject==cbImage; the +0x100
stride 'page table' is code-pattern-ambiguous (0x90c300cd int3 run). Header
image size 0xa7710 is NOT summed-object memory (obj1 mem size >= 0xa28e3 from
stored maxima — identity open but NOT via the LE header). docs/re/
r1-savestate.md lists the trail. Pointer-law decoding of live RAM is the route.

## R4. External ptrace on dosbox-x — DEAD ON THIS BOX
dosbox-x 2025.02.01 self-blocks: PTRACE_ATTACH/SEIZE EPERM within 2 s,
/proc/pid/maps EACCES, while probes on a plain child succeed (harness
self-check). No gdb stub in the binary (strings: 0 markers). Do not hand-roll
tracer probes; scripts/r1_tracer.py is kept for the record only.

## R5. dosbox-x -break-start pilot — DO NOT PILOT
Superseded by the save-state route (captured the same state without a
debugger) and it walks straight into the DOSBOX RULE EOF-spam trap. v1
BLOCKED.md records the do-not-pilot decision.

## R6. gam_probe.py bare run — TRUNCATION FOOTGUN (not a research negative, but
it bit v1): running scripts/gam_probe.py without --out overwrites/truncates
hand-written docs/re/savegame.md sections (hit 2026-10-05k; restored via git
checkout). Always pass --out or read the script first.

## R7. Encoding-garbage readings recorded so they are not re-believed
- u32 0x343FD at a code site = coincidental CALL rel32, NOT an MSVC LCG
  constant. (Real LCG: hand-rolled glibc-constant at 0x7825b, unmapped.)
- 'mid-turn u16 table' claim = UTF-16 text misread.
- immediate-encoding frames: trust rel32 edges + rewritten-site immediates
  ONLY (worked refutation at 0x7478b, v1 attempt 3).
- +0x68/+0x69 in planet records are generation constants, NOT the turn clock
  (refuted same-minute in v1). The turn counter is u16 phys 0x254e10.
- member-offset H: compiled-header estimate 104 was 32 B short; measurement
  says 136 (size census exact + unique BDA signature). Re-derive per build.

## R8. Comparison-method traps in refcap (docs/re/refcap.md)
1:1 blit row search passes on black-row dominance; logic.flc palette control
is vacuous (shared engine palette); bbox-normalised frame ID unscored. The
live law: movie shots >=85% in intro65a union palette, menus far <2%.

## R9. Font readings corrected (do not re-adopt)
NOT a bit format (1 byte/pixel, 0xFF bg). Higher byte = BRIGHTER ink (the
'255-value=intensity' phrasing inverted rendered brightness; direction now
asserted by fnt_probe every gate run). Row-major geometric law dies on
smfont; 'AA core = stroke width' dead; font ink cannot be palette-relative
(only index 0 is grey in intro65a).

## R10. Media/misc dead ends
- radare2: not in Debian 13 repos. No LE-capable Python pkg cached offline.
- dosbox-x -help hangs without guards — strings on the binary instead.
- .tsv are NOT text-.bin (seed claim falsified; see docs/PLAN.md erratum).
- FLIC 'Ascendancy-specific payload' verdict was a chunk-NAME-TABLE bug
  (missing 0x0007 DELTA_FLC) — stock FLC with three measured quirks
  (docs/re/flc.md); do not re-open OQ-002 from old notes.
- .cob offset table is N not N+1; the old extractor silently dropped each
  archive's last file (fixed; gate asserts counts now).
- 2026-10-04h "contract complete" claim covered v1's contract ONLY; under
  v2's strict policy the open ledger still has 15 items — that sentence is
  not evidence anything in the ledger is done.

## R11. Terrain preset-row == 0x744f4[+0x16] as GENERATION row — REFUTED (t29b)
*** RETRACTED t35 — the refutation was the t33 raw-slot-array bug. ***
Re-running the SAME first-save battery with the corrected array
(+0x10 stored ptr + 0x88; 29 runs, ~150k cells, scripts/r1_terrain_authored.py
--runs 'work/r1/*'): barren% tracks the row's w0 monotonically, every row —
row0 w0=100 -> 99.3% barren; w0=50 -> 48.1%; w0=40 -> 41.3/37.8/40.3%;
w0=20 -> 20.9/22.8/20.8/20.8%; w0=0 -> 0.7% and 0.2%. The old "preset-0
planets show 51% barren" was a misaligned grid window. The save-time +0x16
ROW IS the generation row for the barren draw. Also settled same run:
AUTHORED-vs-GENERATED = GENERATED (410 planet names carry multiple grid
hashes across capture runs vs 13 identical — the identical ones are the
all-barren row-0 style grids that hash-collapse; 0x37d80 runs on every new
game, never mid-game). Residual residue: the ~0.7% barren leakage on w0=0
rows and full class-chain shape for classes 2..7 (only the barren leg is
w0-predicted by this battery). See income-law.md T35.
--- original text (kept for provenance) ---
The class-draw law itself is verified instruction-level (barren iff
rng<scaled(w0) @0x37e51..0x37ea4, cumulative chain @0x37eb7..0x37ee0,
rng 0..32767 @0x78269). But a 13-run first-save battery (~70k surface
cells binned by the SAVE's +0x16) refutes the row as the generation
source: preset 0 row [100,0,0,0] predicts all-barren, preset-0 planets
show 51% barren; no monotone reading fits. Do NOT wire rewrite cell-class
generation off the save-time +0x16 row. Sanctioned route: +0x16 writer
census post-world-gen, else scenario data-file lift (docs/re/income-law.md
S10 OPEN RESIDUE t29b).

## Meta-lessons (how v1 self-corrected; keep doing this)
- Verify the number, THEN write the sentence. Controls on every vote/census.
- Ambiguous windows don't vote (fake-base incident).
- Catch claims before they leave the tree; when wrong, correct the doc the
  same turn and record the episode (pointer-law retraction whiplash).
- Behaviour tests catch wrong inference even when constants are uncheckable
  (stockpile starvation, fortify-on-wrong-star oscillation).
- RNG discipline: features must never add/skip draws on the campaign stream.

## R12. Direct-reference scans for string/DAT sites in ascend_restored.bin — DEAD METHOD (t51)

- Proven-blindness demonstration: `planitem.txt` string @0x84888 has ZERO
  u32-immediate references and Ghidra `get_xrefs_to(0x84888)` == 0, yet its
  loader FUN_00037fc0 is CLOSED (OQ-014) — references are LEA-computed or the
  restored image lacks the reference metadata. Same for `resume.gam` (five
  string copies, all zero-xref), `cosmos.txt`, `DAT_00074508`.
- The 12 byte-scan hits for packed u32 0x857de (and kin) are MID-INSTRUCTION
  false positives: Ghidra reports 'No instruction at address' for every one.
  The lone contextable hit 0x38205 is PUSH EAX inside the item-table parser —
  unrelated bytes.
- DO NOT re-run: u32 scans of string addresses, search_byte_patterns on these
  VAs, get_xrefs_to on the same DATs. To find a field WRITER use runtime
  memory-modification capture or controlled save mutation instead.

## R13. Screenshot-reading for UI geometry — UNAVAILABLE (t55)
- vision_analyze returns 500 'image input is not supported' for this
  deployment's model group (measured 2026-10-11). UI button geometry comes
  ONLY from windows.txt X0/Y0/X1/Y1 offsets (file evidence) + the banked
  click law (root = window + 40); verify every new click target by a RAM
  signal (turn counter / grid hash / needle), never by looking at pixels.

## R12 amendment (t60): file-provenance law for image scans

u32-immediate scans over ascend.exe MUST use work/ascend_restored.bin (the
Ghidra image with reconstructed VA immediates), NOT work/ascend_payload.bin
(same length 576643, 6244 differing bytes in 1069 clusters). The t59
"shp-string u32 scans zero hits" negative was a wrong-file artifact and is
VOID; corrected restored-image scan hit 6 of 16 shp/asset strings at base 0
(LGRACE/SMSHIP registration, planal, planets->FUN_0001fe20 chain, suns x2).
Absence remains uninformative (R12); presence is a lead.
