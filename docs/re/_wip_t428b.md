# _wip_t428b.md — PLANET-SCREEN CYCLE 2 (MUTATION + FIELD THREAD)

Task: docs/STATE.md NEXT ACTION t428b. Cycle 1 (t428) shipped the STRIP law
(pins 447/0/0, witness PASS) with NO mutation battery. Cycle 2 = MUTATION the
strip pins, then the FIELD thread if budget allows. The frame is ALREADY EXACT
(t406 17np k0 backdrop) — do not touch it. Seams carried: T428-A (vendor field
BLACK on witness A), T428-B (witness A lineage), T427-A..F unchanged.

Sitting check [verified]: work/r1/playcap/live-timeline.jsonl mtime
2026-11-12 06:45 (9.38 GB, unchanged since t418-era) — NO new sitting, so the
t428b assignment stands (no r1_t85g_sitting.py re-run needed).

## F0 — FIXTURE VACUITY PROBE (t428b, BEFORE any mutant)
Skill rule 5 (state-carryover vacuity). Probe /tmp/t428b_probe.cpp linked
against rewrite/build/libascend_core.a (Campaign seed 2024 AND seed 5, turn 0):
EVERY star reports pop=2.0 res=0 ind=1 pros=1 pending=-1 items<=1.
Consequences for mutant design [verified by the probe + layout.cpp laws]:
- gaugeSelector(0)==0, so a const-0 mutant on the RES arm is VACUOUS (the pin
  cannot see it). The non-vacuous const-0 arm is IND (gaugeSelector(1)==1).
- The RES/IND binding SWAP is visible: gaugeSelector(res)=0 != gaugeSelector(ind)=1.
- projectItem +1 is visible (-1 -> 0; pendingItemFor(0)==-1 at turn 0).
Battery scripts/t428b_mutate.py (snapshot /tmp/t428b_snap, restore+os.utime):
  M1 RES/IND channel->panel swap            -> tests planetstrip_gauge_rects
  M2 kPopGridOrigin 355 -> 350              -> tests planetstrip_pop_anchor
  M3 PLIND selector const-0 (non-vacuous)   -> tests planetstrip_gauge_rects
  M4 projectItem = pendingItemFor(star)+1    -> tests planetstrip_star_domain
RESULT: see the LANDED block in docs/STATE.md (battery appends here).

## F1 — GRID LOOP IS UNCONDITIONAL: THE FIELD IS CLIPPED, NOT GATED (t428b)
The H-FIELD-STATE / H-GRID-INVOCATION question from t428 F6/F7 resolved by
reading the loop head and its STEP/BOUND (work/t198_planwin.asm):
- Head 0x3bb19..0x3bb46: edi := 0x6e (=110), eax := 0x19a (=410), edx := 0
  (cell index), then jmp 0x3bb85. NO per-planet, per-pop, or per-cell
  condition precedes it other than the t428 F6 owner test at 0x3baf4 (which
  jumps FORWARD to 0x3c33a, the tail, and only when the planet is NOT ours
  AND the cell search hits).
- Step 0x3bb5d..0x3bb72: edi += 0x11 (17), eax -= 0x22 (34), edx += 1.
- Bound 0x3bb79: cmp $0x16d (=365); je 0x3c33a. So the walk runs while
  edi goes 110 -> 365 = (365-110)/17 = 15 ITERATIONS (the t418 15-row law),
  and it terminates unconditionally — there is no state under which the
  paint body walks zero rows for a planet that reaches 0x3bb19 at all.
- Body 0x3bb8e: al := BYTE[0x7445c + edx] banked at esp+0x318 and INCREMENTED
  per cell (0x3c1c8); at 0x3c1f2..0x3c20b edx := BYTE[0x7445c][cell],
  eax := BYTE[0x744a8][cell], eax += edx, then `cmp %ecx,%eax; jle 0x3bb48`
  SKIPS THE DRAW when eax <= ecx (AT&T operand order: jle on eax-ecx). Since
  ecx == BYTE[0x7445c][cell] + (cells walked so far), the skip condition
  reduces to BYTE[0x744a8][cell] <= walked — i.e. the 0x744a8 table is a
  PER-CELL COUNT of how many lattice positions get art [semantics inferred;
  table identity not yet pinned]. Either way it is a fixed table read, NOT a
  function of the planet's improvement/pop state, so it cannot explain a
  fully BLACK field.
CONCLUSION [inferred from the verified control flow]: a planet that reaches
this paint always walks the full 15-row lattice. Witness A's BLACK field is
therefore NOT a vendor conditional on the grid — it is the t428 F8 CAPTURE
LINEAGE seam: A is not the state-17 PLANETALLOC frame, so PLSQUARE/the grid
paint was never invoked in A's screen. H-FIELD-STATE has no static closer
inside 0x3b96c (honest negative) and the port's always-on lattice stands.
SEAM T428-A RE-SCOPED: it is a WITNESS-A LINEAGE artifact (fold into T428-B),
not a missing vendor gate. CLOSER if ever needed = a fresh pure capture of the
state-17 field on an UNIMPROVED planet (user checklist item, not a probe).
Corroboration from the owner test itself: witness A's header says the PLAYER
owns the shown planet, so at 0x3bafb owner==player -> `je 0x3bb19` -> the grid
walk RUNS. A planet that reaches this paint in A's own state cannot skip the
lattice. The port's always-on lattice therefore stands UNCHANGED (no edit was
justified by this finding — it removes a suspected defect that the control
flow says the vendor cannot have).

## F2 — MUTATION BATTERY RESULT (t428b, scripts/t428b_mutate.py)
4/4 CAUGHT, AFTER-RESTORE 447/0/0, pristine md5 verified after every restore
(planetstrip.cpp 7d63a0d65ba0a571e7adbc530669b904, .h 6d704fcd361ee84903cdea3c564b473c):
  M1 RES/IND channel->panel swap      CAUGHT planetstrip_gauge_rects_t428 :101,:102
  M2 kPopGridOrigin 355->350          CAUGHT planetstrip_pop_anchor_t428  :141
  M3 PLIND selector const-0           CAUGHT planetstrip_gauge_rects_t428 :102
  M4 projectItem = pending+1          CAUGHT planetstrip_star_domain_t428 :154
=> the t428 strip pins DO encode the law (dispatch binding, pop anchor, gauge
selector arm, planitem 1:1 record law). No MISSED mutant -> no weak seam, no
pin re-scope needed.

## F3 — CAMPAIGN PITFALL LEARNED (t428b, skill rule 8 family)
FIRST RUN OF THIS BATTERY WAS FULLY BOGUS: each mutant tuple keyed the
SNAPSHOT path instead of the WORKING path, so M1 built the PRISTINE file
(false MISSED) and its "restore" copied the mutated snapshot back over the
working file, poisoning M2/M4 (they "caught" the M1 poison at :101/:102, not
their own mutants) and AFTER-RESTORE read 4 failed. Detection signal: an
AFTER-RESTORE that is red, plus FAIL lines that name a test UNRELATED to the
mutant's target. Recovery: `git checkout --` the two files (safe here only
because `git status` proved they held NO hand edits — otherwise reconstruct
from the pin), rebuild, confirm green, re-run. Prevention now IN the script:
mutants apply to WORKING paths only, and every restore md5-checks against the
snapshot-time pristine hash and ABORTS rather than continuing.

## F4 — NOT DONE THIS CYCLE (carried)
- Field backdrop 17np k4 (625x357 per shp.md S23.2) decode-and-compare against
  witness B's field region: NOT run (dims are already cited; the CONTENT
  comparison is the open half). Row-table identity 0x7445c/0x744a8 unpinned.
  [t428c SUPERSEDED BOTH: k4 registers at screen (7,115) (shuffle control
  6..12 vs real 158/269); the tables are planitem.txt grids B/C (OQ-014,
  closed 2026-10-06) indexed 15*[planet+0x14]+row — this file's "per-cell"
  reduction above was wrong in GRANULARITY (per-(size,row)); the
  no-vendor-gate conclusion stands. docs/re/_wip_t428c.md F1-F2.]
- Tile-click CONTENT-DEPENDENT popup law (PLSQUARE SENDMESSAGE 1 -> command fn
  0x3aa0a legs): NOT touched.
- Seam T428-B (witness A lineage) now has STATIC SUPPORT from F1 and stays a
  DECISIONS-page ruling candidate.
