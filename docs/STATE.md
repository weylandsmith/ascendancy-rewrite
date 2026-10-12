# STATE — machine-readable working memory for the closeout loop (v2)
# Update EVERY turn. A fresh session must be able to resume from THIS file alone.
# v1 history (full turn log 2026-10-03..2026-10-05l): archive/ralph-v1/STATE.md
# Patch discipline inherited: ONE patch per region, read_file verify after
# (multi-patch batches mangled v1 twice).

phase: P7-closeout
milestone: 6  # keep 6: gate.sh keys build/test/boot stages off milestone >= 3; lowering it silently guts the gate
updated: 2026-10-11T12:55
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

T56 LANDED + CORRECTED (PER-TURN BRACKET PARSE, income-law.md T56/T56b;
BLOCKED t55 CLOSED): End-Turn (511,67) works-but-flaky (advance try 3, then
6/6 at 25 s); channel words +0x44/+0x46/+0x48 = RATES not stockpiles
(verified across all 19 ck); growth tick player +PROS / AI +PROS+1 fresh
40/40 (t24 law re-measured); word +0x52 = CELL INDEX NOT item id (corpus
0..59 > 39 items; S10 map confirmed) — mid-turn correction of an earlier
wrong reading; FRESH-RUN AI opening build = AGRIPLOT (+0x54 := 0x01) 4/4
thin; c1c -1 co-occurrence with queue flip 4/4 (cell reservation at queue
time [inferred]); T56b per-pair offset census + heap BASE-DRIFT hazard law
(never one absolute base across a session's checkpoints). Player home sits
at RECORD 89 — parsers must scan 151.
T57 LANDED (OQ-012(a) density probe AMBIGUOUS -> best default fixed-50,
BLOCKED t57: one-click (65,427) during setup, fresh-map star count 50 ==
cosmos.txt default; click-inert vs cycle-wrap inseparable (glyph readout,
R13); scripts/r1_t57_density.sh banked.
T57b LANDED (income-law.md): OQ-020 item SUPPLY side closed verbatim
(FUN_00039b6c + raw-asm slot-writer attribution 0x38fc8..0x39003: top-up
OR word+2 hi |= p3; p3=7 MissileBase/ShortWhopper, 8 LongWhopper, 0
TractorBeam skips write; flag&4 items exactly 17/28/29/30 [battery];
EBX 45/45/90/200 + p4 slots UNATTRIBUTED; same-turn draft mislabels
retracted in-place). Decrement period capture-gated (zero flag&4 slots in
corpus, T49); r1_ability_charge.py banked; OQ-020 stays OPEN (period half).
T57c LANDED (income-law.md): OQ-020 use path FUN_00039c10 fully mapped
(counter = slot word+2 hi, use-gated write |= (c-1)<<8, OR-semantic hazard
flagged unresolved, EBX=range x32 gate consumer located, +0x70 parallel
countdown). Amass formula UNMEASURED, OQ-020 stays OPEN, capture-gated
(zero flag&4 slots, T49). OQ-006 stale-NEXT corrected: CLOSED 2026-10-07.
T58 LANDED (income-law.md T58; ledger OQ-019 escalated BLOCKED-USER-LEVEL,
OQ-016 queue-chain note): deep run turns 0..52, 113 ck. Scale leg NULL at
depth (565 slot obs, 0 state-4/0 owned/0 moved, 0 landings) — no save-
observable route contains flight; only original-hardware capture remains.
First live t28 queue completion (Tubes->Agriplot re-queue, cheap-first,
player never queues). Threshold-50 wrap exactly once at pop 2->3, 8 AI
drops on pop steps; rewrite growthPhase unchanged. HARNESS LESSONS:
r1_trajectory_regression.py IGNORES argv (scans ALL runs) — read its header
before quoting numbers; the constant-7 byte at 0x1BF450+H is NOT the turn
counter (T42 law needs a KNOWN phys).
NEXT (t59): full-ledger classification DONE t58b — remaining open: OQ-005
(W3 in progress: recon banked docs/re/shp.md S7 — registration pass
FUN_00023388 sole-caller of FUN_0001fa60; t59 u32-scan NEGATIVE VOID by t60
file-provenance law (wrong file); INT21 wrapper cluster 0x777xx-0x77dxx
found, 74 CD21 sites),
OQ-010 combat application (static route bounded; scripted campaigns have NO
combat -> capture class same as scale), OQ-012(a) blocked glyph-readout,
OQ-016 attribution + OQ-003 meanings replay-only, OQ-019 scale
BLOCKED-USER (t58), OQ-020 amass capture-gated-unreachable, OQ-021
end-screen rides multi-hour gameplay BLOCKED-USER, OQ-023 build-work parked
by standing option-C decision (not RE). CONCRETE NEXT ACTION (t61b): DECODER FOUND t61 (docs/re/shp.md S9):
FUN_0005caac shape blit w/ control-byte grammar (C==0 end-row, C==1 skip,
odd literal C>>1, even run of next byte C>>1); cache module mapped
(FUN_0001fc34 accessor + 20 callers, FUN_00020acc raw-load, cache.cpp
strings). Corpus exact-span 27/208 libs clean, rec0 grammar well-formed
198/208; rec1+ prefix law NOT universal -> live-RAM anchor queued: grep
banked ck heap spans for loaded-shape run patterns (e.g. listbox stream
bytes) to pin per-record stream start; then full-corpus revalidation; then
REWRITE upgrade (PNG/sample renderer decision per shp.md S6 — rendering
before codec closure fabricates pixels; after closure it is legitimate).
t62 live-RAM anchor (shp.md S10): cache payload = VERBATIM whole-library
file copy (constant-delta image match ck113); runtime shape structs DO NOT
exist in RAM (negative) — [ptr][W-1][H-1] assembled per draw (widget
descriptor law: array +0x6d, u16 count +0xa1, stride 0x0d, type byte0,
+5 u32 -> FUN_0001fc34 -> FUN_0005caac). Payload-array base offsets from
regparm decompiles NOT trustworthy (ASCII-hit artifact banked; t61 slot-
flag readings VOID). CONCRETE: raw asm 0x3144a..0x31470 arg order +
FUN_00031660 to pin dims/pixel-ptr provenance, then corpus revalidation.
T63 LANDED (shp.md S11): both raw-asm reads done — widget pass passes the
UNADJUSTED lib base (record selection excluded there and in the cache);
FUN_00031660 = trivial row helper (closed). CONCRETE t63b: FUN_0005caac
prologue stack-arg mapping (stream cursor vs shape struct; clip pushes
0x14 survive per ADD ESP,0x14 @0x31467) + PLANETS.SHP inter-ck
in-place-rewrite test.
OQ-005 stays OPEN until revalidated across corpus.T64 LANDED (shp.md S12): blit input law code-pinned (5 cdecl args; stream
cursor = payload + u32[payload+8+8*sel] + 0x18); cache anatomy measured
([0x88][verbatim 1.10], base 0x242088); .tmp ARE libraries; DECISIVE
NEGATIVE: 0/12 loaded payloads satisfy the blit law autoplay — raw !=
draw-time payload. t65 RUNNING (r1ad-20261011-180908, proc_965332c0bf73 +
r1_intel_drive.sh proc_c5780e49dc24): intel panel opened via verified
(553,318) + 12 turns; post-run = strict blit-input scan on loaded/
rewritten payloads; RESULT t65 NULL (S13): 71 ck x 200 slots x sel 0..7
= 0 survivors despite verified click delivery + mid-run cache misses ->
blit-5arg path does not consume raw payloads. REFUTED t66 as a
SCAN-BASE BUG (shp.md S14): correct arg2 = slot+0x88 verbatim base (file
u64 dir at file+0x10 == u32 stride-8 series at PAY+8; tsz doubles as
rec0 virtual slot) -> 3504 strict survivors over 72 ck, raceflag sel1
pixels RAM==FILE. Caller idiom: slot=[widget+24], sel=[widget+28]>>16,
payload UNMODIFIED to blit — no transform pass. Rows x-unbounded
(writes clamp @0x5cd31/0x5cd62); exact-span 2xH = animation frames.
DONE t67 (b1b20b8): widget arglaw pinned (@0x31001..32: arg1=widget+4
DEST struct => W/H clamp is DESTINATION; slot [widget+24], selector
[widget+28]>>16, -1 skips); header-pair stream-start discriminator ran
with fixed bounds: 57/208 libs all-records-pass, 151 hold failing
records (UI-lib cluster) — NOT closure (shp.md S15).
DONE t67b/t67c: autopsy + unified law (shp.md S16,
scripts/r1_shp_unifiedlaw.py): V(k0 rec+8)/A(k>=1 rec+0x18 dims@+0x10)/
B(k>=1 rec+0x20 dims u16@+0x18) -> 1477/1557 records pass, 176/208 libs
clean; residual 80 records/31 files in 3 classes (span-undersized
planind+3cfgnew 26, simple-format cos_star 12, stragglers 42).
DONE t68: runtime table UNIFORM [measured ck072,
scripts/r1_shp_ramtable.py]: 4 verbatim-cached libs x all selectors,
hist {sel0 delta 8, k>=1 delta 24} zero exceptions (shp.md S17) —
S16 V/A law holds code-side; fixup-vary theory dead for table region.
OQ-005: codec grammar CLOSED (S9+S12+S14+S16+S17); dims-location
residue (80 recs/31 files + non-verbatim .tmp heads) recorded
BLOCKED-USER-LEVEL (needs human-verifiable drawn frame).
DONE t69: rewrite/src/formats/shp.{h,cpp} ShapeLibrary (container laws
S1, V/A stream-start S16/S17, S9 control-byte grammar with blit-faithful
write-clamp + untouched-destination semantics) + tests/test_shp.cpp
(raceflag law pins, in-memory container rejection, corpus parity floors
from the measured Python run). MEASURED: 107 tests 0 failed; corpus
208 libs / 1557 recs / 1484 decode-pass / 185 clean libs — EXCEEDS the
1477/176 floors (4096 dims cap added after a FAIL-class record's
garbage dim words triggered bad_alloc: decode REPORTS, never allocates).
NEXT t70: ledger hygiene pass — re-mark OQ-005 sub-parts in
OPEN-QUESTIONS per S17 closure split (grammar CLOSED, dims-location
residue BLOCKED-USER-LEVEL), then first non-blocked ledger item.
