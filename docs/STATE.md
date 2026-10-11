# STATE — machine-readable working memory for the closeout loop (v2)
# Update EVERY turn. A fresh session must be able to resume from THIS file alone.
# v1 history (full turn log 2026-10-03..2026-10-05l): archive/ralph-v1/STATE.md
# Patch discipline inherited: ONE patch per region, read_file verify after
# (multi-patch batches mangled v1 twice).

phase: P7-closeout
milestone: 6  # keep 6: gate.sh keys build/test/boot stages off milestone >= 3; lowering it silently guts the gate
updated: 2026-10-11T11:10
policy: strict-close  # FINAL-DEFAULT never closes an OQ; only cited measurement does (docs/GOAL.txt)

## LEDGER (statuses mirror docs/OPEN-QUESTIONS.md; that file is the record of
## resolution evidence — this block is the fast index. Update BOTH or neither.)
ledger:
  closed:
    - "OQ-001 .cob offsets = N not N+1"
    - "OQ-002 FLIC codec (both vendor videos, golden-pinned)"
    - "OQ-007 text encodings CP437"
    - "OQ-008 loader model usable for control flow (imagebase 0)"
    - "OQ-009 AI data side (21 raceNN.dip parameter sets)"
    - "OQ-011 POINTER LAW: runtime_u32 = P0 + payload_file_offset(target); P0 = B - H per-run; guest linear == physical; obj0 code [0x14bb0,0x82bb0)@0x1d4000, obj1 data [0x82bb0,0x8cc83)@0x242000 (battery scripts/r1_pointer_law.py 12/12 slots, gate 3q)"
    - "OQ-017 vendor .fnt codec + wired into UI"
    - "OQ-013 RESTREE LIVE TABLE LAW: in play = 66 main rows only (loader
      FUN_00046870 row loop bounded by count line 66; variants 0/40 in 27 slots
      x 13 captures); record = stride 75 (count u16@+0, name 60B@+2 ^->space,
      runtime cost u16@+62, prereq bytes@+64 (0FF term, <=5), child slots@+69..72
      (second pass, 66/66 exact), field0 u8@+76); MEASURED COST LAW runtime =
      file_cost x (2row-20) for row>10 clamp 65000 (instructions 0x4691d..0x46a15,
      reproduced 66/66; row65 300->33000); resume.gam block byte-identical to
      fresh RAM (static data); rewrite upgraded (Tech::runtimeCost,
      includeVariants default false) + 2 pinned tests; docs/re/research.md 6"
    - "OQ-014 PLANITEM LAWS: loader FUN_00037fc0 + checker FUN_0003830c +
      init FUN_00037d80 (restored image; strings verified payload
      0x8488d..0x848d6); record stride 0x28 IND@0 RES@+1 PROS@+2 MPOP@+3
      UPOP@+4 REQUIRES@+5 FLAGS u16@+6 COST u16@+8 name30@+10, 39/39
      byte-exact vs file (2 captures, table phys 0x2b5f50). REQUIRES law:
      avail iff req==0xFF || (req<66 && owned) -> 254 DEAD (rewrite
      requiresAvailable, gatedBy deleted). Count triple: 22=SURFACE
      (RAM 0x73e3c==22 4/4) XOR placement law idx<=30 specials-exempt;
      9=ORBITAL rows 22..30. Grid C row sums = size-class surface cells
      {7,11,23,45,73}: live +0x18 2650/2650 x 17 captures, cap==cells+10
      zero violations. MPOP=upkeep-demolition, UPOP=start-gate. FLAG bits
      consumer-mapped (bit4 set by no shipped row, bit7 no consumer); RAM
      census == file 39/39. Spec docs/re/economy.md §4; 3 pin tests (89
      tests 0 fail); gate green incl seed-2024 Control t145. Per-cell
      terrain/nuke laws documented, rewrite wiring PARKED (no cell model)"
    - "OQ-004 TABLE LOADING + .COB GRAMMAR: pool-relative immediate law (imm =
      str_off-0x82BB0 -> relocated P0+str_off; 337 RAM-verified sites; census
      docs/re/datafiles.md — every pool name has a referrer, refuting 06r .shp
      false-zero); ascend02 .bin/.tsv opened via RAM name table @0x250c1c
      (3/3 captures) from .cob TOC, zero exe literals; .cob = u32 N + N x 50B
      names + N x u32 blob offsets, ascend00 54/54 md5 round-trip; gate
      scripts/cob_probe.py (3i2); NO rewrite delta — rewrite reads the
      extracted dir directly, nothing TOC-side to upgrade (datafiles.md S5)"
    - "OQ-018 soundfx.txt header pairs, VOC u16@25, theme selection mapping
      — CLOSED 2026-10-07 (STATE index was stale, moved 2026-10-08 t28):
      header pairs = voices/size-band law (voiceBand() +
      test_audio_voice_band_law_oq018, 327/328 spans == disk sizes); VOC
      field map 15/15 (u16@25==0x0911 constant, audio.md §2.1, voc.cpp
      pins); race->theme map REFUTED (DAT_00010ba0 single writer 0x21309)"
  open:
    - "OQ-010 combat application formula — R1 frontier; static half bounded
      2026-10-06 (no disp32 orbit/table reads; shape tie FUN_00025604), path =
      click-diff capture (STATE NEXT ACTION)"
    - "OQ-003 .gam full record map — joint with OQ-010 (planet records joined
      151/151 @ stride 123; STAR TABLE + ORBIT laws closed 2026-10-06 give the
      neighbourhood map: star stride 96, planet ptrs name+0x2A, orbit pair
      planet-name+0x57/+0x5f; field semantics open)"
    - "OQ-021 end-ctrl threshold: comment 'over half' vs prose 'two-thirds' —
      static route REFUTED 06s (globals reader-only, no comparator in image);
      path = controlled-mutation capture (docs/BLOCKED.md OQ-021 recipe)"
    - "OQ-020 ability charge days (%d in vendor text, no data file) — R1: read the constant in code"
    - "OQ-005 .shp pixel codec — static route exhausted (6 angles, docs/REFUTED-ROUTES.md); needs exe shape loader via live image"
    - "OQ-006 headerless sample rate — needs exe audio-init constant"
    - "OQ-012 mapgen: ONLY (a) size options open; (b) closed 06o (pps U{1..5}),
      (c) closed 06p/06q (shell position law; rewrite upgraded + tested),
      (d) closed 06k (sphere extent, refined by (c))"
    - "OQ-015 DA_ template selection order + full %token table"
    - "OQ-016 campaign per-turn constants — scope NARROWED t29: income,
      growth, cadence, build order, AI SELECTOR LAW (S9) and POP-CAP SEED
      LAW (S10: capBase=nonbarren/3+5 @0x37f84..0x37f9e, measured preset
      table 0x744f4 + cell table 0x744a8, recalc clamp w/ flags&4 AND
      Colony-Base skips, Lush Growth Bomb +10; rewrite seeded capBase/
      surfaceCells + storedCapFor replaces constant-25, pin test
      campaign_pop_cap_seed_law_oq016) all closed with evidence
      (income-law.md S6..S10). STILL OPEN: per-cell terrain/nuke wiring,
      home-placement verification, +2 residual minutiae (0.4% samples),
      scenario-template preset source"
    - "OQ-019 ship design model (hull+gizmo inventory, cost hack, Orbital Docks)"

## WHAT IS IN HAND (tools + laws — a fresh session starts here, not from scratch)
- R1 save-state capture LIVE: scripts/r1_savestate.sh (boot -> autosave ZIP,
  full guest RAM) + scripts/r1_sav_scan.py (per-run base B, NEVER hard-code;
  member = physical + H, H=136 for dosbox-x 2025.02.01, re-derive per build).
- Deep capture LIVE: scripts/r1_deepcapture.sh (title -> New Game clicks
  318,293 then (511,67) cadence, needle-gated); campaign start proven
  byte-wise (scripts/r1_campaign_probe.py); planet records resume.gam<->RAM
  join 151/151, stride 123 (scripts/r1_planet_layout.py).
- POINTER-INDEX COROLLARY (OQ-014 turn, self-proved): for a Ghidra image
  address X of runtime-loaded data (BSS/data globals like DAT_00073e40), the
  SAVE-ZIP member index is B + 0x82BB0 + X (B = r1_sav_scan.find_base vote),
  and guest PHYSICAL of a member byte is member - 0x88. Reading B + X instead
  yields data 0x88 too low and fails SILENTLY (wrong grid, wrong values, no
  error). Self-proof: item table name-anchored in member 0x2b5ec8 ==
  B+0x82bb0+0x73e40 exactly, and the same index form returned file-identical
  grids + sentinel -1 + growth 50 + research count 66. Heap pointers stored
  in RAM remain physical addresses: member = ptr - 0x88. Helper pattern:
  idx = lambda X,n: m[B+0x82BB0+X : B+0x82BB0+X+n].
- PLANET SYSTEM OBJECT (runtime, OQ-014): base = planet-name - 0x24; +0x10 u32
  slot-array ptr (physical; member = ptr-0x88), +0x12 growth-inc, +0x14 size
  class 0..4, +0x18 surface cells {7,11,23,45,73}, +0x1a cap = cells+10, slot
  = 4B {class, itemIdx (0xff empty), flags u8, shield u8}. Locator law:
  cells in {7,11,23,45,73} AND cap==cells+10 AND ptr sane — 2650/2650 records
  matched across 17 captures, zero false layout reads.
- Turn counter: u16 guest-phys 0x254e10 (idle-pinned 0, NEXTTURN-advanced,
  byte-verified). TURN-BOUNDARY law: planet records mutate only across
  counter-changing slot pairs; hot head-block = older-convention
  +0x35..0x3F (name-based +0x57..0x61), high-entropy u16s every turn.
- STAR TABLE LAW CLOSED 2026-10-06 (battery scripts/r1_star_table.py, gate 3s,
  green 259/259 slots x 13 captures): stride-96 name-anchored star records;
  idx u32 @name-0x18; pos f32[3] @name-0x14; planet ptrs u32[5] @name+0x2A
  targeting planet-NAME-0x24, LIVE iff name prefix matches, single-owner law;
  sub-pool 0x258xxx stride 39 permutation. ORBIT LAW: centered radius constant
  (0 violations 277 planets); per-planet constant dtheta/turn applied by turn
  loop (sample r=544 -> -13.52 deg); unassigned planets subset of static.
  Full field table docs/re/r1-savestate.md "STAR TABLE + ORBIT LAWS". Census
  tool scripts/r1_record_census.py (per-record per-offset planet churn).
- Restored image for Ghidra: work/ascend_restored.bin (built by
  scripts/r1_restore_sites.py; base-0 address space; validation: pointer
  runs >=8 hit Watcom starts 60% vs 15% control). Full analysis ghp5:
  1,144 functions (work/functions_full.tsv).
- Module attribution LIVE: scripts/attribution_scan.py + gate 3r,
  work/attribution.tsv (225 E1 refs, 62% on true fixup sites; flic 43,
  winmgr 24, gsystem 23, race 20, cosmos/batmode 10, planet 8).
- Restree law tool LIVE: scripts/r1_restree_law.py (anchor on row-0 name, walk
  stride 75, no hard-coded address; exit 0 only if the cost law cross-checks
  >=90% of located rows). Green on every banked capture (66/66 rows, 27 slots).
- DATA-FILE STRING -> LOADER ROUTE (proven on OQ-013, 2026-10-06r; the general
  key to the "needs code path" items): the payload holds literal data-file
  names next to their module's debug path (e.g. 'restree.txt' at payload
  offset 0x85014 beside '..\research.cpp'). Tool scripts/r1_datafile_strings.py
  scans guest RAM for u32 == P0 + payload_offset and prints the Ghidra address
  d = (member_off - H) - P0 of every referrer (never hard-code bases). Census
  06r (r1deep-20261006-123049, 20 slots): ALL 23 .txt names referenced --
  batfx 0x1ad97, help 11 refs (0x1bee3...), music 0x212d5, cosmos 0x2140e,
  static 0x218c1, names 0x22894, history 0x2b4d5, end-{xtnc,dest,capt,unit,
  ctrl} 0x2c04e/0x2c065/0x2c07c/0x2c093/0x2c0aa, gwshare 0x31563, tutindex
  0x35a7b, planitem 0x37fcd, restree 0x468d3 (== the independently-found
  loader site -- self-validating), reswin 0x4712b+0x47579, gizmos 0x49081,
  soundfx 0x4ff42, newgame 0x5212c, gizhelp 0x56105, planhelp 0x561f0,
  windows 0x575c3. 06s REFUTES the 06r claim that .shp names had "zero direct
  u32 referrers": the census regex dropped backslash paths and upper-case
  extensions; re-censed correctly, ALL names have referrers (shp 6/6 e.g.
  data\\planets.shp 0x2b224, DATA\\planets.shp 0x51921, MOUSE.SHP 0x309f9;
  HAZ 3/3 in FUN_0001cf20; DIP 2/2; .tmp 10/10 at 0x5a2b3..0x5a39b). Root
  mechanism now CLOSED (pool-relative immediate law, 337 verified sites):
  the obj stores imm = str_off - 0x82BB0 and relocation rewrites it to
  P0 + str_off -- full spec + census in docs/re/datafiles.md. Caveats kept:
  (1) the RESTORED image keeps the unrelocated immediate (Ghidra prints
  'MOV EAX,0x2464' at 0x468d3; live RAM imm 0x244464) -- referrer addresses
  come from the RAM scan, never from image immediates; (2) not every referrer
  lands inside a Ghidra function (end-ctrl.txt 0x2c0aa) -- use disassembly
  context. OQ-004 CLOSED 06s (which tables load + .cob container grammar:
  u32 N + N x 50B names + N x u32 blob offsets; ascend00 54/54 md5; gate
  scripts/cob_probe.py): ascend02 .bin/.tsv have ZERO exe literals -- the
  engine opens them from a RAM name table at guest-phys 0x250c1c (3/3
  captures) sourced from the .cob TOC (anchor ascend01.cob:0x3f98).
- Static trust boundary (from v1 attempt 3): trust rel32 edges + rewritten-
  site immediates ONLY; batch-4-style blind decompile sweeps of E1 batches
  skew UI/allocators (4ae24 = operator-new).
- Gate: bash scripts/gate.sh is the single verification command; ~2-3 min;
  R1 attempts are NEVER gate stages (gate stays fast, side-effect-free).

## NEXT ACTION (exactly one)

T54 LANDED+T54b PROBE (budget spent; income-law.md T54/T54b): preset
tables = compiled image constants (exact 32-B signatures: zero hits across
entire extracted corpus, 1 each in image 0x88f90/0x88fe4, 1 image-copy
each in session RAM) — file-driven scenario-row hypothesis REFUTED for
these tables; T36 draw sites corroborated verbatim in raw asm (%5 then
%11 back-to-back @0x23a86/0x23a97). T36d attribution reduces to the guard
field (Ghidra stack-relative slots ambiguous) -> statics EXHAUSTED, rides
t51 step 2. NEXT: BEGIN t51 step 2 = scripted step sequence on the PROVEN
resume path (r1mut law: needle-verified verified clicks landed first try;
scheduled-unverified clicks remain refuted 2026-10-06c): (a) this turn's
prep = map in-game UI from windows.txt VERIFIED keys + banked strategic-
map screenshot (End Turn button, planet panel, ship build queue), design
click script ship-build -> End Turns x N -> per-turn autosaves; (b) launch
bounded run; parse offline incl. guard-field/preset correlation, ability
obs (step 3), score screen if any end fires (step 4), scenario-table join
with bounded recipe. Exit-1 nulls banked once. Do NOT re-grep preset
signatures; do NOT decompile FUN_000238e8 again whole.
PRIOR T45 LANDED (SELECTED-ABILITY / GOVERNOR BRANCH CLOSED, income-law.md S14):
branch @0x38df0..0x38e29 pinned verbatim; the [0x743b9]>>0x18 operand IS
item-table UPOP(35) (row base 0x73e40+35*0x28=0x743b8, runtime value 1
32/32); accumulator identities cross-verified by the three doubler blocks;
exhaustive +0x54 writer census (scripts/r1_0x54_writer_sweep.py — 88/89/
8a/8b/c6/c7/80-group/86/87/8f + SIB; 23w/130r/61sib, zero XCHG/POP): only
trigger path = activator @0x38b26 (queue+selected = SAME field, closing
the S6/S8 naming tension); corpus 0/2810 records hold 33/34/35 (484 saves,
scripts/r1_governor_census.py). Rewrite: PlanetState::governor (default -1
= measured), branches in storedProsFor/storedResFor/usedPopFor, consumers
routed; pin campaign_governor_law_t45; run_tests 103/0; branch inert so
timelines UNCHANGED (2024 Control t777 / 42 Extinct t583 / 13 Control
t593, CLI finite-proved); OQ-024 ledger CLOSED. NEXT: OQ-019 SUB-ITEM
vendor cost hack — record field +0x46 WRITER census on the GIZMO record
(stride 0x6a, ships.md S6) using the t45 sweep method (r1_0x54_writer_
sweep.py generalized to offset 0x46 + stride-context check via runtime
gizmo-table anchor), then decompile whatever writes it. Fallback if sweep
inconclusive in 2 rounds: record one line and take the OQ-003 planet
field-semantics walk (star table join already banked).
NOTE t45 HARNESS LESSON: an operand that LOOKS like a magic constant
(MOV EAX,[abs]; SAR 0x18) may be ITEM-TABLE DATA — compute base+row*stride
before calling it a constant (this turned OQ-024's last open operand into
a runtime-measured value).
PRIOR T42 LANDED (CB-CELL DRAW LAW CLOSED). Home seed FUN_000238e8
@0x23ca2..0x23cb2: owner:=empire, pop:=2, EBX:=0xffff EDX:=5 CALL
FUN_00038818 = PICKER; FUN_0003875c collects checker-legal empty cells,
ONE FUN_0007824f draw, IDIV count, list[rem] = UNIFORM AMONG LEGAL
EMPTIES. Checker FUN_0003830c rule chain (raw listing — decompiler
flattens EDI): CB legal on EVERY non-rock surface cell, BARREN INCLUDED
(rule B class!=0 rule falls through for item 5 — RAM flags 0x0001
verified), illegal rock (rule D), illegal orbital (rule C: (slot<surf)
XOR (item<22)). Census: 72 turn<=1 homes KS D=0.085 (crit .192) PASS,
19/72 barren ~= terrain share, 0/2810 CB-on-rock corpus-wide (scripts/
r1_cb_rank_final.py + r1_cb_picker_law.py VERDICT 0; t40 rank 2..70 was
a nonbarren-filter artifact — RETRACTED, rank0/1 0/72 residual p~.09 unpinned).
Rewrite drawCbCell = ONE worldNext draw % nb over non-rock cells; pins
campaign_home_placement_law_t40 + campaign_cb_cell_uniform_t42; timelines
2024 Control t762 / 13 Extinct t324 / 42 Extinct t561; PLAYTHROUGH.md
regenerated. HARNESS LESSON: member = phys + (base-0x1BF450) per run —
hard-coded +136 and corpus-first dedupe BOTH silently corrupt populations
(mis-mapped mid-run worlds inflated 72->162; retracted before landing).
T43 LANDED (BUILT-ITEM CELL LAW CLOSED). Picker FUN_0003875c IGNORES
the caller's slot register (item stashed @0x38769 pre-EDX-clobber, pushed
EBX never re-read) — all 16 EBX=0 build sites in FUN_0003f130/3f758/fc4c
are uniform draws; checker rule G @0x385b7..0x386fe: non-CB items need an
ACTIVE neighbour (exemptions items 5 @0x385f9, 0x23 @0x38602); graph =
continuous-x hex over RUNTIME row tables (fingerprint-anchor: kRows-44B
fingerprint, widths at -76, starts at -152; identical 484/484 saves, sums
== live +0x18) — image DAT copies are stale code bytes, static RAM reads
ZERO in dumps (harness law: locate DAT tables by CONTENT, never VA).
Census scripts/r1_built_cell_law.py: 213 worlds, 0/362 Factory active w/o
neighbour, 0 transitional anomalies (first-run "REFUTED 4" was the
zeroed-table artifact, caught pre-landing). Rewrite: buildPhase completion
-> drawItemCell (one worldNext over empty non-rock rule-G-legal cells;
degenerate fallback documented), static cellActiveNeighbour/sizeClassFor,
pin campaign_built_cell_rule_g_t43 (symmetry x5 types, degree 1..4, draw
spread). run_tests 102/0. TIMELINES (CLI finite-proved): 2024 Control
t777, 42 Extinct t583, 13 CONTROL t593 (seed 13 flipped Extinct->Control
under adjacency production); PLAYTHROUGH.md regenerated; gate ALL CHECKS
PASS. T44 LANDED (CARGO-SLOT CHAIN, docs-only): +0xae writer sweep
(search_instructions "xae", 31 hits, all handler/UI) resolves the sub-item
into a CHAIN — EVENT 8 +0xac := FUN_0003a880 PURE coord->slot converter
(orbital-direct band 13<X<153,119<Y<469 -> surfaceCells + 5*((X-13)/70) +
(Y-119)/70; fallback FUN_0003a820 decode + FUN_000395c4), EVENT 4 copies
+0xac->+0xae, nothing fires unless <0xffff, legality re-runs FUN_0003830c
@0x3afed, item '05' branch = owner/pop2/activator @0x3b0d6 = the exact t41
arrival state; player coords come from the mouse. AI landing COORD chooser
-> docs/BLOCKED.md (dispatch-site recipe; rewrite picker default stands,
observation-consistent — CB is rule-G exempt). income-law.md S13.5; gate
ALL CHECKS PASS (docs-only). NEXT ACTION: AI EVENT DISPATCHER — find
callers of FUN_0003aa0a (get_xrefs_to 0x3aa0a + dispatcher-table scan for
the (obj,type,payload) call shape; the decompiled handler shows the
triple-field event protocol, param_2<9/==3/>=0x33 bands) and locate the AI
ship-control site that builds type-8 payloads for transports with cargo
item 5 — that coordinate pick is the AI landing law (closes the t44
BLOCKED entry). If the dispatch scan fails to bound in ~2 rounds, leave
BLOCKED (record one line) and move to OQ-024 governor-assignment law
(@0x38df0 branch, docs/OPEN-QUESTIONS.md line 58) — static route exists.
NOTE t36: terrain law closed; NOTE t35: raw-array re-audit.
NOTE t34: DISPLAY-WORD CHANNEL LAW — see income-law.md T34 + commit
91b90c0 (+0x44 max(1,trunc((v+1)^.85)) 97.98%, +0x46 raw, +0x48
max(1,PROS-pop>>2) 94.82%; +0x54 = queue id, gov branch dead).

NOTE t33 SUPERSEDES NOTE t31 IN FULL: the slot-array pointer bug below
("T33 LANDED") explains t31's grid-law failures, t31b's "generation-state
vs render-state boundary", AND the t32 +-2 residual. All three were the
same +0x88 heap-header offset missing from find_records.

(1) Re-audit pre-t33 subsystem claims that read the raw slot array:
    terrain-authored battery results (S10 T29b/T30c numbers), ship-record
    census (also: its exit-1 negativity needs a separate look — surface=0/
    orbital=0 on a game with 5 homes + ships means its stride/owner filters
    never fire on our captures), and any income_channels figure.
(2) GOVERNOR LEDGER ROW (new, from T34): the @0x38df0 '+0x54 governor'
    branch never fires in 466 saves (byte always a queue id) — needs a
    capture where a governor is actually assigned; route = deep-schedule
    click capture with the governor UI (OQ-012(a) glyph route unlocks it).
(3) OQ-012(a): new-game size options — unchanged (glyph-lift route).

T33 LANDED (POINTER-OFFSET FIX + FORMULA UPGRADE): find_records slot array
= [planet+0x10] + 0x88 (heap object header; pointer law r1-savestate.md:188).
Cap law now 72066/72066 (100.00%, 466 saves); seed law 21.79% -> 98.6%
(residual = scenario/preset-row worlds, first-save-only census 98.63% — NOT
replay noise); tail-all-1 54.7% -> 99.5%. K1 answer: NO post-gen byte0
rewriter needed — the raw array showed churn because it was a misaligned
window; disasm FUN_00037d80 (ECX loop: tail slots class 1, mines < cells)
matches the +0x88 array exactly. Rewrite: storedCapFor drops skip-CB and
skip-flags&4 (r1_cap_models.py: DIS incl-CB 100.00% vs skip-CB 96.07% pure
+2 fails; flags&4 rows all mpop=0), campaign.h cites t33; r1_ship_record
sign corrected (+0x88; its -0x88 cited a nonexistent r1_planet_layout read);
r1_cap_ledger model-A label fixed. 98/98 tests, gate ALL CHECKS PASS.

NOTE t31: fresh new-game capture done (r1deep-20261008-190330, scratch
resume.gam MOVED ASIDE to resume.gam.bak-20261008 — restore or re-move as
needed; next capture starts a NEW world). Recalc cap law RE-CONFIRMED on
full corpus (46132 samples, 96.19%, +2-only residual; a mid-turn
retraction was itself wrong and was un-retracted — the equation is
+0x4a==clamp(+0x55+MPOP-sum), NOT grid nb//3+5). Grid battery results in
S10 T31/T31b: saved cell array is NOT the verbatim generation output.

T31 LANDED (measurement-only): fresh new-game capture proves terrain seed
RANGES reproduce exactly ({5..7},{5..8},{5..12},{5..20},{5..29} per size
class on fresh world) but per-planet grid/array equations (nb//3+5,
orbital tail-all-1) FAIL on saved state (22.5% / 19-138) — recorded
S10 T31/T31b with raw slot hist (byte0/byte1/word+2); +2 event modifier
first direct sighting @0x4404b..0x44058; word2==1 ACTIVE definition for
the cap ledger (item5 CB on 5 home slots, t27 law re-observed); full
corpus = 298 slots / 46132 samples now the standing recalc ledger.

T30 LANDED (measurement-only; harness script added): S10 T30 call-site law
(scenario-init per-star rng%5 size + rng%11 row normal path; 21-dword
T0/T1 table copies only in special mode @0x23aaa/0x23ac2; byte[STAR+7]
index NOT used in our captures — all b7=0); T30b FUN_00037fc0 scenario
loader law (record 0x1ce0 overwrites ALL FOUR w-bytes per preset row
0..10 @0x3803c..0x38067, 0x1ce3/0x1ce6 -> 0x7445b/0x744a7, item-table
record load incl. FLAGS bitmask accumulation and COST words, sentinel
[0x74458]=-1 makes it run once); T30c world-identity census (7 captures
share ONE world, 6 are distinct games — old '285 differ' battery conflated
games with re-rolls; terrain built once at 0x37d80, never re-drawn on
resume; cell-array pointer uniqueness kills aliasing hypothesis; static
best-fit 152/927 vs 84 chance = no per-planet static-row law).
scripts/r1_terrain_authored.py = terrain fixity/battery harness.

T29B LANDED (measurement-only, no code change): terrain mutation CLOSED
(40k consecutive-save census: base classes mutate ONLY via item-36
Terraforming law + world-gen rock; apparent changes = slot-aliasing);
rng 0x7824f range CORRECTED 0..32767 in S10; preset-row->histogram
mapping REFUTED (13 runs, ~70k cells; preset 0 predicts all-barren,
observed 51%) — per-cell terrain shape stays OPEN, rewrite does NOT
model cell classes (claim reverted before landing in campaign.h).

T29 LANDED: POP-CAP SEED LAW CLOSED + WIRED (S10: world-gen func 0x37d80
single caller 0x23b49; cell loop rng<barren-w0 law w/ MEASURED preset
table 0x744f4 11x4 + cell-count table 0x744a8 (row sums {7,11,23,45,73}
== live +0x18 exact); seed = nonbarren/3+5 into +0x55 AND +0x4a; recalc
ledger 38772/40318 exact w/ MPOP skips flags&4 AND Colony Base (CB
derivation: -2 residuals vanish); Lush Growth Bomb item37 completion +10
once @0x39212..0x39229; +2 residual 0.4% stays open). Rewrite: PlanetState
capBase/surfaceCells/growthBoom, constructor binomial seed per S10,
storedCapFor() replaces constant-25 + popCapFor rewired + slot-cap uses
seeded surfaceCells, constant cfg_.popCap retired; pin test
campaign_pop_cap_seed_law_oq016; 98/98 tests, gate ALL CHECKS PASS,
600-run VICTORY Extinct t219.

T28 LANDED: AI BUILD SELECTOR LAW CLOSED + WIRED (S9: full 0x3f130 region;
rows 0..21 minus item5; ABSENT pick immediate, PRESENT scored by
FUN_0003fec4 need-class with d66 roll; 70-ratio rejects AND aborts scan;
jump table image 0x3f120 live-relocation-verified; research tail byte
0x7478b+75t measured 0 in 26 slots x 13 captures; live q54=0/Factory on
all 4 AI planets matches law). Rewrite: PlanetState.pendingItem/buildAcc,
buildPhase = tick+selector, storedIndFor/ResFor/ProsFor + needClassFor,
instant ind_ deduction REMOVED (ind_ = launch budget); pin test 93/93;
gate ALL CHECKS PASS; 600-run still ends Extinct t256.

T27 LANDED: BUILD-QUEUE LAW CLOSED (S8: COST=item+8 via 0x73e40+8+28i
[earlier stride-8 cap-table reading CORRECTED]; +0x50 += IND (+1 AI
catch-up when IND<4 && DAT_00013bc4==2); completion when +0x50 >= COST;
item completion effects banked (Ship pop -= DAT_000741dc flag-gated,
Terraforming sets byte0=1, Automation |= bit1, item37 +0x55+=10 once));
GROWTH BONUS CORRECTED: active CLONING PLANT (item 15, 0x393ad MOV
EDX,0xf + FUN_0003958c EDX signature) not Hyperpower — docs S6b/S6 +
campaign.cpp hasClone shipped; AI 70-ratio policy observed, NOT wired
(selector unresolved); ctest 100%, gate ALL CHECKS PASS.

BANKED t11: renderer FUN_00036ed8 token law (m/y swapped pair via
DAT_00074590 stride-0x14 names, s/t via DAT_00013000/DAT_000066d8 chains;
exactly {m,y,s,t} confirmed in CODE); queue cap 0x1d @0x363f1; dispatch
FUN_0003634a event table incl. AI gate species byte 0x0e (&DAT_00012fff
chain). See docs/re/diplomacy.md §5.
BANKED THIS TURN (t9): OQ-017 was CLOSED at v1 (index line 168) — earlier
NEXT ACTION was stale, fonts already load (formats/fnt, docs/re/fnt.md).
OQ-021 RE-CONFIRMED decision-gated: end-*.txt pool literals have NO code
refs (raw imm scan, matches BLOCKED.md); static DS 0x3a095 owner table reads
ALL ZEROS in ck005 (heap-relocated — mutation capture needs the name-anchor
route of r1_star_table.py, stride 96 name records, NOT the raw DS offset);
capture route stays valid but prep required, pair with OQ-016 idle capture.
Ledger: OPEN = OQ-005, OQ-012(a), OQ-015, OQ-016, OQ-019, OQ-021 (user
ruling (a) or capture (c)); BLOCKED = OQ-020 (30 turns). 92 tests.
CROSS-CUTTING WARNING (t20, HARD): docs/re/economy.md and docs/re/gizmos.md
are REGENERATED wholesale by scripts/gizmo_probe.py every gate run
(gate.sh:146) — hand-written addenda THERE are silently destroyed (proved:
dc9fb13 lost 87 lines; two mid-turn reverts 2026-10-07). Income/growth law
now lives in docs/re/income-law.md (hand-maintained, probe-immune). §4
(availability law, cited by economy.h) was already lost to the probe before
this session — RESTORE it into income-law.md from rewrite/tests/test_economy
.cpp law text + FUN_0003830c re-verification when that area is next touched.
CROSS-CUTTING WARNING STILL ACTIVE: pin bytes from RESTORED image, read
semantics from Ghidra payload program, cross-check both (993 diff
clusters; 850 imm-fixups, 143 other).
OQ-016 EVIDENCE (not offline-solvable 2026-10-07): r1deep-230146 t2..t9 is
not an idle empire (orbital f32 churn, AI timers +256/turn at 0x255228/
0x255605); planet grid 0x26d103 (stride 123) and star grid 0x255c69
(stride 96) are byte-static over 8 turns; strict-increase u16 scan found only
DOS tick clocks (0x4f4, 0xa467); 144225 turn-adjacent empire data is in
relocated heap. Needs: New Game -> clean Next-Turn ck ladder capture.

## KNOWN-ISSUES / PARKING LOT (operational; research negatives live in
## docs/REFUTED-ROUTES.md)
- ORBIT PAIR = ORDINAL-KEYED SHARED TABLE, NOT planet position: value is
  keyed by planet ordinal (I=(320,-960) etc., identical across campaigns);
  reading per-planet 'position' or extents from name+0x57/+0x5f is RETRACTED
  law (2026-10-06k). f32 x @+0x57, f32 y @+0x5f (gap 8; +0x5b zero pad — the
  "<ff" read fakes a radial law, hit 06d).
- NO xdotool on this host: synthetic keys go via tools/xsend key KEYSYM
  (rebuild: gcc -O1 -o xsend xsend.c -lX11). ESC closes the sticky planet
  view. r1_adcapture has a cmd_key channel using this.
- ckdiff planets() window-base law: name offsets key off H+0x255b00 (adding
  only H silently decodes nothing / garbage — hit twice); colonized test =
  u16@NAME+0x28 ONLY (ffffff@+0x2e is residue on every fresh-map planet).
- ADAPTIVE CAPTURE (scripts/r1_adcapture.sh): campaign-entry law = planet
  grid hash AT POINTER-LAW BASE CHANGES ('cosmic exiles' needle is the SETUP
  screen, NOT campaign — false breaks); checkpoint must double-read slot
  size (autosave rewrites in place -> torn BadZipFile copies); adaptive
  phase fits inside BOOT (-time-limit kills the game mid-drive); fresh-
  campaign LORE screen needs 2-3 center clicks (drive by shot-classify).
- vision_analyze intermittent 500 ('image input is not supported') — pixel
  statistics (panel dark-frac, color histogram) classify screens without it.
- DOSBOX RULE: never launch dosbox with stdout/stderr to a log unless you
  first confirmed it will not sit at an interactive prompt (EOF at a prompt =
  infinite "Are you sure to quit anyway now?" -> the 12 GB incident). Bound
  with timeout + head -c, or drive via pty. nosound=true.
- Kill dosbox ONLY by pkill -x dosbox-x (pkill -f once matched the gate
  shell's own cmdline and killed the gate mid-run).
- dosbox-x has NO gdb stub; -break-start exists but is DO-NOT-PILOT
  (docs/REFUTED-ROUTES.md).
- Ghidra MCP may be down: restart via scripts/ghidra_headless_up.sh
  (127.0.0.1:8089). After restart verify loaded memory is NONZERO before
  trusting results. API contract: docs/re/loader.md footer + v1 lessons
  (getReferencesFrom -> Reference[]; r.isCall()/r.isJump(), NOT isCALL()).
- gam_probe.py bare run (no --out) TRUNCATES hand-written savegame.md
  sections — always pass --out or read the script before running (hit
  2026-10-05k, restored via git checkout).
- restree separators are literal '^' (0x5E) bytes — normalise BEFORE
  comparing names (v1 miscount bug).
- radare2 unavailable on Debian 13; no LE-capable Python pkg cached; do not
  hunt for either. dosbox-x -help hangs: use strings on the binary.
- rsync NOT installed (cp -a). numpy absent host-wide; revenv PIL is the
  image host (~/tools/revenv/bin/python).

## DEFINITION-OF-DONE (v2 — strict)
gate.sh exit 0 AND ledger.open EMPTY: every OQ moved to closed with (1) its
evidence (Ghidra address / extracted-file offset / pointer-law guest-phys
measurement), (2) the rewrite code site upgraded to the original behaviour,
(3) docs/re/ spec updated, (4) a gate or unit-test assertion pinning it.
Items whose evidence genuinely cannot exist on this box are NOT closed
quietly — they get a BLOCKED.md entry with what machine/evidence would be
needed, and stay open. Under this policy "loop ends" may mean "you tell the
user the remaining items need X", not silent completion.
