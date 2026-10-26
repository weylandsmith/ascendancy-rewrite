# STATE — machine-readable working memory for the closeout loop (v2)
# Update EVERY turn. A fresh session must be able to resume from THIS file alone.
# v1 history (full turn log 2026-10-03..2026-10-05l): archive/ralph-v1/STATE.md
# Patch discipline inherited: ONE patch per region, read_file verify after
# (multi-patch batches mangled v1 twice).

phase: P7-closeout
milestone: 6  # keep 6: gate.sh keys build/test/boot stages off milestone >= 3; lowering it silently guts the gate
updated: 2026-10-26T17:30
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
    - "OQ-010 combat application law CLOSED t89 (static law S2d..S2h
      instruction-verified t85g..t88a + rewrite UPGRADE S2j): firing order =
      stored gizmo-slot order every cat-0 engages (0x4a5c1); damage =
      design[+0x52] guns / [+0x4a] specials, NO hit roll (measured-negative);
      two-layer clamped absorb shield-then-hull + death 0x49d2c; commit law
      mode==1 only 0x25560/0x25570. Code sites: rewrite/src/game/
      campaign.cpp attackScore (volley = SUM researched cat-0 Levels,
      replaces MAX), defenseScore (hull layer only), combatPhase (noise draws
      REMOVED per cited determinism; capture iff volley - MIN(volley,
      shieldChargesFor) > hull), shieldChargesFor/setAllTechs + campaign.h
      absorbSplit; pin TEST(campaign_combat_law_oq010) (file sums 49/16,
      volley delta 49 full-vs-none tech, split edges, determinism). 109 tests
      0 failed; timelines regenerated: 2024 Control t777 / 42 Extinct t581 /
      13 Extinct t503 / 1 Control t842 / 2 Control t677, all FINITE <1200;
      PLAYTHROUGH.md regenerated. AGGREGATE model caveats S2i (no per-ship
      slots/same-system/range gates; per-ship = OQ-019)"
  open:
    - "OQ-003 .gam full record map — joint with OQ-010 (planet records joined
      151/151 @ stride 123; STAR TABLE + ORBIT laws closed 2026-10-06 give the
      neighbourhood map: star stride 96, planet ptrs name+0x2A, orbit pair
      planet-name+0x57/+0x5f; field semantics open)"
    - "OQ-021 end-ctrl threshold: comment 'over half' vs prose 'two-thirds' —
      t73 dark-zone hit (docs/re/score.md S1-S3): score strings referenced at
      0x2807b/0x280e7 (pool-rel), score law TRUNC(100*DAT_482fb/T), presenter
      eventwnd.cpp 0x2c03a cluster; comparator writes = ZERO direct encodings
      -> evaluator hunt via dark-zone enumeration (t73b); capture fallback.
      Default >1/2 stands"
    - "OQ-020 ability charge days (%d in vendor text, no data file) — R1: read the constant in code"
    - "OQ-005 .shp pixel codec — static route exhausted (6 angles, docs/REFUTED-ROUTES.md); needs exe shape loader via live image"
    - "OQ-006 headerless sample rate — needs exe audio-init constant"
    - "OQ-012 mapgen CLOSED t78: (a) size options measured 2026-10-12
      (density cycle 50/75/100/15/25, wraps; rewrite --stars knob),
      (b) closed 06o (pps U{1..5}),
      (c) closed 06p/06q (shell position law; rewrite upgraded + tested),
      (d) closed 06k (sphere extent, refined by (c))"
    - "OQ-025 mapgen non-default-density POSITION law CLOSED t79: shell
      radii fixed at every size, populations = halving law (T//2+1 then
      halve); reproduces the T=50 battery table exactly; rewrite
      shellRadiiFor() replaces the wrong i%50 wrap; ladder test extended"
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

NEXT t91 (STATIC task, docs/re/aicode.md): W6-A4 AI RESEARCH PICKER —
find the writer of race research-target word row+0x1d4e (and its partner
+0x1d5c accumulator reset sites) in the restored image. t90 narrowed the
field: the completion consumer FUN_00046aec READS +0x1d4e and clears it
to 0xffff on completion (aicode.md §3); the 0x257cf call site of
FUN_00046fa0 is only a 0x1d72-byte restree buffer COPY (0x46870 loader
fallback + 0x20c48 copy primitive) — so the PICK happens in the AI
command executor FUN_00041260 (callees 0x38818 build-cmd/0x39894 —
aicode.md §1 P8) or in the research module around 0x46fa0 (grep the
image for moffs/disp disp reads+stores of 0x1d4e relative to row base
0x2b057+race-row and of the restree runtime 0x7478b preferred mask).
Method: objdump full-code scan for imm 0x1d4e / 0x1d5c operands
(store-form census pattern = scripts/r1_t86_write_census.py), then
decompile the enclosing function(s). Bank the PICK law in aicode.md §3
(rewrite researchPhase uniform-random pick is UNCITED — if the original
law is e.g. preferred-list-first like expansion 0x40018, bank the exact
tier order + rng thresholds; rewrite delta = t92, one task per session).
Rationale: t90 mapped the AI turn loop end-to-end; the two W6 items the
map feeds directly are A4 (research picker — the ONLY AI decision still
with zero cited law: build=done t28, expansion=selection half closed
t90, diplomacy=structure cited) and A5 (order enum). A4 is cheaper
(single field-writer census) and closes a rewrite placeholder the user
explicitly named. A5 next after. Sitting watch: live-timeline 5.69 GB,
user idle at t=1254 all week (sitting check 2026-10-26 16:40 ran clean:
no new turn-boundary rows past t=1254, t85g sitting stands as newest); a
NEW turn-boundary sitting outranks this -> scripts/r1_t85g_sitting.py
first, and any new sitting's combat frames are a free cross-check of
combat.md S2j (volley steps == design Levels).
OQ-021 passive watch continues (boundary sample 23/50, selector never
armed).
T90 LANDED (STATIC task — W6-A3 AI TURN LOOP MAP CLOSED to docs/re/
aicode.md, first content of that file): full phase-ordered map of the
original turn: master FUN_00024f24 (single caller 0x55f06 in the
END-TURN dispatcher FUN_00055df4) = random-event window -> income
0x2501c -> ship orders 0x25023 -> research 0x2502f (FUN_00046aec) ->
growth 0x2503c (t81 law) -> pop-cap 0x25056 -> per-race AI 0x25083/
0x250a5 (FUN_0003e6e0, SKIP iff row idx == DAT_0007458e player idx) ->
scored-star ownership scan (the INC-word producer at 0x251a2 for
DAT_00048300 — first cited producer path near the OQ-021 field) ->
command-exec tail incl. 0x2554f FUN_00041260 (the AI acts through the
SAME gun/ability primitives 0x49f28/0x39c10 as the player — callee-set
verified). Per-race decision block FUN_0003e6e0: eliminated-race fleet
DEATH law (0x40ec0 collect -> 0x49d2c per ship), extinction writer
(row+3 := 0xffffffff + event 0xa), decision block 0x3ea54 order =
diplomacy chain (0x3ecb8->0x3ef2c->0x44690->0x3eb88) -> build-selector
loop (0x3f130 called ONLY at 0x3eade on queue-empty own planets, gate
[+0x5a]==0 && [+0x54]==0xff — t28 law re-verified from the caller side)
-> expansion 0x40018 -> race maintenance 0x43b50 (integrity restore
ship+0x8c := +0x98; global attitude FLOOR enemy-strength+20 write at
0x43c36; moves x2 recharge loop 0x43c5b — the t85g boundary recharge is
THESE TWO sites) -> per-ship orders 0x40178 (kind/target +0x58/+0x59;
congregation-to-nearest-friend via 0x4aa10 starlane-cost table 0x45beb).
Expansion SELECTION law cited: tech-legal candidates (0x46d3c prereq
chain, restree rows) -> preferred-list scan (runtime 0x67be 11 u32) ->
rng%100<45 sentinel -2 -> uniform rng fallback; store DAT_00076492[race]
(19-site census). Research COMPLETION law cited (progress = +1/planet
gated govtype==2&&word<15, + planet RES word; x1.2 f64 pair
0x3feb3333; >= cost -> owned-mask +0x4a/+0x4b). NEW tool
scripts/r1_t90_callgraph.py (rel32 edge census over obj0 + pinned caller
sets, RC=0; pkl at work/t90_callgraph.pkl). NO ledger closure (strict-
close — structure map, not a constant/formula closure): OQ-016 row
annotated with the t90 status + explicit STILL-OPEN set (research PICKER
= A4, order ENUM = A5, 0x43b50 tail/0x2ef60 cases = A6/A7, random-event
module). No rewrite code change (map task by design; delta candidates
listed aicode.md §5). Gate GATE_EXIT=0, ledger_audit LEDGER AUDIT OK.

T89 LANDED (CODE task — OQ-010 CLOSED, the loop's first static-law closure
with changed code sites): the assignment executed in full: (1) rewrite/src/
game/campaign.cpp attackScore volley = SUM of researched cat-0 weapon Levels
(NumUses!=0 gate) replacing v1 MAX — cites volley loop 0x4a5c1 every-weapon
law + design[+0x52]==file Level (t87 t87_gizmo_table map); (2) defenseScore
= HULL layer only (pop/10 + fortify 2) — the v1 shield-addend was REFUTED by
the cited hit path 0x4b740, which never adds shields to a defense total but
clamped-absorbs MIN(damage,[t+0x90]) and spills (0x4b7c4..0x4b7d1); the split
is now Campaign::absorbSplit (campaign.h) used by combatPhase: capture iff
volley - absorb > defenseScore; (3) the uniform(0,10) noise draws REMOVED per
the S2g measured-negative hit roll — decision (b) of S2i taken explicitly,
rng_ re-diversion regenerated ALL timelines and every checked seed stays
FINITE inside the 1200 gate budget: 2024 Control t777, 42 Extinct t581,
13 Extinct t503, 1 Control t842, 2 Control t677; PLAYTHROUGH.md regenerated
(record_playthrough.sh echo-lines carried a stale 600 literal since T41 —
fixed, display-only); (4) new shieldChargesFor() = SUM researched cat-1
Levels (charge law 0x49f15); (5) TEST(campaign_combat_law_oq010) pins
re-extracted file sums (10 weapons SUM=49, 6 shields SUM=16), the full-vs-
no-tech volley delta == 49 (a MAX model cannot produce 49), absorb/clamp/
spill edges, seed determinism over 40 FFA turns: 109 tests 0 failed.
Ledger: OQ-010 row CLOSED (status cell + STATUS t89 with sites + caveats);
ledger_audit default open set updated to
{003,005,016,019,020,021,023}; STATE ledger block mirrors. combat.md gains
S2j (landing + honest aggregate-model caveats: per-ship slots, same-system
gate 0x4b982, range gate 0x4ba57, per-shot power accounting are NOT modelled
— OQ-019 territory); turnloop.md §5 rewritten from [INFERRED] to the cited
law. BLOCKED t89a budget-block marked RESOLVED. Mid-task self-corrections
recorded: first defenseScore draft folded shields into the total (contradicts
0x4b740, fixed before build), vector<bool> proxy trap in setAllTechs (fixed),
const-qualified atk blocked SA_DoublePower doubling (compiler caught, fixed).
Sitting watch: no new turn (all readouts t=1254). Gate GATE_EXIT=0, ledger_audit
LEDGER AUDIT OK (open set now {003,005,016,019,020,021,023}).
T89A LANDED (scoping pass for the t89 CODE task — budget-interrupted, honest
negative, NO code change): the assignment's own "check first" gate EXECUTED
and PASSED — rewrite/src/game/campaign.cpp:1247-1322 IS a combat phase
(attackScore :1204 / defenseScore :1226 / capture walk :1289-1321, advance()
:1376), so the "rewrite never modelled combat" BLOCKED branch is DEAD.
Scoping measured the structural constraint (S2i): no per-ship gizmo
inventory exists in the rewrite (ShipInTransit {owner,from,target} only,
fleet_ cleared every turn campaign.cpp:929), so the upgrade is an
AGGREGATE-law change: (a) volley = SUM of researched cat-0 Levels replaces
MAX (:1217, cites 0x4a5c1 every-weapon law; file cat-0 rows re-verified
this pass: Levels 1,2,4,4,1,4,6,4,10,13 / NumUses 1,1,1,1,5,1,2,2,2,3);
(b) the :1275/:1305-1306 noise draws are an UNCITED v1 abstraction the S2g
measured-negative determinism forbids — removal decision + PLAYTHROUGH
regeneration procedure banked; (c) shield-then-hull maps to fleetDamage_
ordering, no new pool invented. docs/re/combat.md S2i + OPEN-QUESTIONS
t89a status + BLOCKED t89a (budget interrupt, supersession note for the
t70 research-block entry) written. OQ-010 STAYS OPEN (strict-close: closing
measurement = the code change + its pin test). Sitting watch: live-timeline
5.68 GB, all readouts t=1254 DAT_482fb=14 — no new turn, assignment stands.
Gate GATE_EXIT=0, ledger_audit LEDGER AUDIT OK (open set unchanged
{003,005,010,016,019,020,021,023}).
T88A LANDED (S2g audit + COMMIT LAW): re-verified instruction-by-instruction
every load-bearing t88 draft claim (dispatcher 0x4a360 category legs, gate
0x49f28 [ship+0x62], volley loop 0x4a5c1 stored-order law, gun handler
0x4b8e4 same-system/range/damage gates, hit call 0x4bb56 arg law, hit path
0x4b740 full body incl. two-layer clamp + death 0x49d2c + event 0x55a60) —
census tool scripts/r1_t88_caller_census.py RC=0 (6 callers of 0x4b740,
LCG unique 0x7825b, zero rng edges [0x4a360,0x4f097)). NEW MEASUREMENT: mode
census of all 13 callers of 0x49f28 — mode==1 COMMIT edges are EXACTLY
0x25560 (gun) and 0x25570 (ability 0x39c10) inside player-command-exec
0x2547c (per-system loop stride 0x60 @campaign+0x3335, ah==3 gun / ah==2
ability / ah>=4 assert 0x2a438); AI-attack module + volley loop all pass
mode==0 dry-run. Self-destruct 0x4d191/0x4d2dd pass the dispatcher mode var
(0x4d2dd at-war-gated [edx+0x12fd6]==2). Banked docs/re/combat.md S2h +
OPEN-QUESTIONS t88a status. OQ-010 STAYS OPEN (strict-close: needs the code
site change = t89). No code change this iteration. Gate + audit green.
T87 LANDED (W6-A2 gizmo dispatcher case table + column map CLOSED):
(c) CLOSED-BY-MEASUREMENT: gizmos.txt -> design record map 76/76 rows,
76/76 names, 10/10 fields (tool scripts/r1_t87_gizmo_table.py exit 0;
loader FUN_00049074 store sites 0x49183..0x491d3 + runtime join save/50.sav,
B=0x1bf4d8 6/6 anchors, member=B+0x82bb0+X). CORRECTS t86: +0x4a = FILE
Special1 column, NOT Industry (the t86 75/76 "Industry" match was value
coincidence); +0x46 is Industry. Post-pass 0x4923a + Cat jump table 0x344b0
derive +0x52/+0x56/+0x5e/+0x62/+0x66 from Level (cats 0-3) or Power (cat 4).
(a) case table decoded (combat.md S2f, all 13 case bodies disassembled):
0x4cd90 is the SPECIAL-GIZMO ACTIVATION handler (tree trap: every jbe after
cmp+jb captures a SINGLE cl value, not a range) — 0x24 Recaller target-list
reset, 0x26 Smart Bomb area fire GATED on relation byte==2 (0x12fd6 matrix),
0x2e Gravimetric Catapult negates ship xyz, 0x35 Cannibalizer self-damage +
moves gain, 0x38 Condensor range scan, 0x3a Remote Repair heals clamped at
NEW FIELD +0x98 = max integrity, 0x3f/0x39/0x41/0x45 flag/charge ops
(+0x9c bits 2/4/0x10 — Invulnerablizer sets the absorb-null bit t85g saw at
0x4b7bc), 0x48 Self Destructotron = 0x4d075 (t85g's "combat loop" SCOPED to
this case), 0x4b Hyperfuel +40 moves; mode==1 charges power before the
effect (0x4d594). (b) 0x43a4c identity CLOSED: NOT star-defense — the
DIPLOMACY-ON-ATTACK handler (attitude -= 10*(word[0x13bc4]+1), doubled at
state==3, at-war short-circuits, attacked-bitmap [[edi+2]>>16 + 0x48304]
bit-set). OQ-010 stays OPEN (strict-close): hit-probability roll still
unseen anywhere, firing order lives in the generic-gun caller chain (t88);
the four 0x4b740 callers banked. No rewrite code change. Gate + audit green.
T86 LANDED (W6-A1 shield-layer census + attacker-object correction):
tool scripts/r1_t86_write_census.py (store-form byte census, objdump
boundary-verified, R12-safe; control passed: finds 0x4d1ea). Results
(docs/re/combat.md S2d): ship +0x90 = SHIELD CHARGES with full writer set —
charged by CAT==1 gizmo Level design[+0x56] (0x49f15 per-gizmo loop over
ship+0xab count [ship+0x15a], gate gizmo[+0x33]&0x20; fire loop 0x4a71f;
zeroed at fire-loop entry 0x4a6a6, by flag [ship+0x9c]&8 at 0x4a73a, and in
0x4a756 init which also sets +0x88 = gizmo-power sum 0x4a99c). CORRECTED
t85g: EDI at 0x4cddc = 0x7650c + 0x6a*gizmo (static design table; 76 rows
names byte-verified from held-turn slot 48 via string-anchor base vote —
note r1_sav_scan anchors need payload strings, 'Factory' needle alone gets
zero votes on this slot) — NOT a battle-built combat object; dispatcher
0x4cd90 case cl==0x3x/0x4x family routes the fire modes, 0x4b740 hit path
re-read whole (flag +0x9c bit0x10 zeroes the +0x90 absorb; +0x9c bit2/bit3
set on shield/hull overflow). Design table values measured live (weapons
+0x3a=range 25..1000, +0x56=level only for shields 1..5). OQ-010: shield
identity CLOSED-with-evidence-in-doc, row STAYS OPEN (hit prob / order /
0x43a4c / +0x4a column identity remain — strict-close). OQ-021: no new
boundary frames, passive watch continues. Gate + ledger_audit green.
T85g LANDED (t1253 sitting adjudication — FIRST mid-turn combat frames):
user played turn 1253 (alliance proposal #2 to Orfa DECLINED, war on
Ungooma, one Ungooma fleet destroyed, return fire) and saved slot 4 at
t1254. Captured: ring + banked copy work/r1/playcap/evidence_slot04_t1254.
SAV (nine stale watchers killed first; one live kept). Findings (docs/re/
combat.md S1-S3, scripts/r1_t85g_sitting.py + r1_t85g2_slots.py): ship
+0x8c = INTEGRITY with volley-step decrements to 0 then owner->free
(death law, MEASURED mid-turn for the first time); +0x88 = MOVES with
boundary recharge; +0x90 = SHIELD LAYER live in-battle (0->10->5->0
cycles, design-dependent, always 0 at boundary); return fire VERIFIED
(player slot14 40->38->36->34, matches testimony "fired back once or
twice"); static: the ONLY +0x8c subtract in the image at 0x4d1ea inside
combat loop 0x4d075 (distance-squared range gate, xyz law cross-confirm)
-> hit path 0x4b740 two-layer clamped absorb -> death handler 0x49d2c.
Diplomacy: PROPOSAL moves the AI-side cell (+39, corrects t85c); war
reciprocity law reproduced a second time. OQ-021: DAT_482fb OSCILLATES
(8..15) independent of territory — systems_full hypothesis FALSIFIED
(0/786 rows match). PLAN.md gains W6 (AI behavior decode A1..A7, user-
requested loop for closing rewrite placeholders). OQ-010/021/023 rows
updated with t85g statuses; all remain open (strict-close).
T84 LANDED (contract-compliance sweep): every CLOSED ledger row audited
for BOTH legs (cited evidence + changed-code-site-or-explicit-disposition)
-> 12 full rows PASS; two real gaps fixed: OQ-004 row now names its code
site (formats/bin_table.h, consumer main.cpp:151 counts-only) and the
7-item closed-index block now cites code sites per item or marks
ANALYSIS-ONLY (OQ-008 fresh-start-only, OQ-009 W-B input) — all cited
paths verified to exist before commit (ai-data.md, loader.md present;
ui.cpp has 9 fnt refs). Tooling traps banked mid-audit: (1) '| open |'
wraps across lines -> whitespace-join rows before status match; (2) the
index block must not start lines with bare ^OQ- or row tools misparse it
-> entries now prefixed '- >'. NEW scripts/ledger_audit.py reruns the
whole check (open-set equality + leg audit): AUDIT_RC=0, open set
exactly {003,005,010,019,021,023}. OQ-020 confirmed status BLOCKED (not
open) + legs present. Docs-only turn, no code change.
NEXT t85: open items are ALL capture/user-blocked; remaining productive
offline work is thin by design. Do one honest loop-state consolidation
pass (STATE/BLOCKED single-source the user-ask; verify scripts/
ledger_audit + r1_playcap are referenced from STATE), then STOP-REPORT
to the user: the loop cannot close the last six items without the
r1_playcap session (repeat exact command + what to do in-game).
T85b LANDED (playcap harness repair + first-capture analysis; user report:
combat analyzer OOM-killed mid-run on the multi-sitting capture):
(1) ROOT CAUSE measured: r1_t85_combat loaded ALL of live-timeline.jsonl
(4.3 GB, 191k rows x up to 107 ship windows) = 65 MB/1k points, projected
12.1 GB on the 16 GB VM -> thrash then SIGKILL. New scripts/r1_stream.py
streams: offset index only, ONE point in RAM; whole 4.3 GB pass = 290 MB
measured. All three t85 analyzers rewritten onto it (victory now prints
per-turn, not per-slot; combat caps stdout 400 lines and keeps counting).
(2) DATA-HYGIENE LAWS (each measured first, r1_stream docstring): trusted
ORDER = (file_mtime_ns, file); DEDUP first-per-(file,mtime) — watcher
`seen=set()` re-init AFTER the jsonl re-ingest banked 73,052 dup rows
(FIXED at source r1_playcap_watch.py); STALE-INSTANCE = a second dosbox
picked up an older save and autosaved one End-Turn BEHIND live for days
(12,516 rows; file-order diffing FABRICATED bounce transitions — the first
relation-analyzer run showed 260 transitions, the true set is 24).
(3) HARNESS LEAK: 12 stale watchers (up to 6 days old) were alive at once
— each sitting's setsid watcher never died (--no-exit kept it looping;
single watch.pid tracked only the newest). Killed all 12 by recorded-PID
+ /proc/cmdline verify; vnc harness now REAPS watch*.pid before relaunch;
live watcher replaced with fixed code (session untouched, dosbox alive).
(4) FIRST-EVIDENCE BANKED from the user's campaign (turns 37..1131):
diplomacy.md §11 (war = cell 1->2 reciprocal at t887->888 per user's
stated war-on-Minions; Orfa alliance = attitude +280 sustained, NO cell
change; values {1,2} only) + score.md S6 (DAT_482fb census: never crossed
half, max 23/50, selector never armed at 26 systems_full; t912 spike
11->22 unexplained; >1/2-on-DAT_482fb stands CONSISTENT, not closed) +
ledger rows OQ-010/021/023 status notes. OQ-010: ZERO destruction in 1100
turns incl 244 war turns — turn-boundary sampling cannot see combat; the
capture class that could is in-battle recording, banked in the row.
NEXT: user asks remain open (victory screen seen by t1131? alliance
ACCEPTED or just proposed?); analyzers run clean on all future sittings.
gate GATE_EXIT=0, ledger_audit AUDIT_RC=0 (open set unchanged).
T83 LANDED (OQ-005 W3 sanctioned route executed to its boundary):
decoder FUN_0005caac caller census = 75 direct sites / 32 functions;
header law re-read verbatim @0x5cabe/0x5cac7 (dims ALWAYS record-start
[ptr][W-1][H-1], clip rect comes from caller widgets); both raw-[reg]
arg-prep sites (0x50535,0x50e60) adjudicated as screen-coord/dst pushes,
not dims; cache load FUN_0001fc34->FUN_00020acc = verbatim file->slot
copy, no dims parse/transform anywhere. Net: NO non-standard dims reader
exists in the image — residue closure class unchanged (drawn-frame, R13),
sanctioned negative now cited in shp.md W3 + ledger. Mid-turn trap:
functions_full.tsv offsets are HEX (decimal bisect gave garbage func
0x142ca, discarded). No code change (ShapeLibrary garbage-dims behaviour
already matches original: report, never allocate).
NEXT t84 (contract-compliance sweep, offline): verification criterion
demands EVERY closed item names evidence AND the changed code site —
scripted audit over docs/OPEN-QUESTIONS.md closed rows (heuristic:
contains a hex address|offset AND a rewrite/ path|'no code change'|
'documented default'); fix any row missing a leg by tracing its doc;
this directly de-risks the final gate-of-gates and has zero capture need.
T82 LANDED (ledger triage + capture readiness): open set confirmed
exactly {OQ-003 packed-entropy residue (OQ-005 closure class), OQ-005,
OQ-010, OQ-019, OQ-021, OQ-023}; every one states its closure class in
the ledger. Harness fact surfaced: OQ-021's scratch build is
work/r1/game/ascend.exe (lowercase; mounted as C:\ASCEND.EXE). NEW
scripts/r1_playcap.sh BANKED READY: one user-run session of the original
closes OQ-021+OQ-023+OQ-010 together (colonize >50%; war+alliance
accepted; one fire exchange), autosave ring + instant per-slot readout
of T/scored-stars/selector/rank; title-menu T=0 slots carry uninitialized
selector heap (0xC500 observed) -> analyzer law: trust T>0 slots only.
Safety invariants kept (scratch-only mount, -time-limit, pkill -x only);
interactive BY DESIGN for the user, agent never plays.
NEXT t83 (offline, sanctioned route ONLY): my first t83 idea (grammar-
differential of well-formed vs undersized heads) was checked against R2
and RETIRED pre-attempt — R2's six angles include span/dims/metadata-slot
variants, and R2 names the sole sanctioned route: the exe shape loader
via call graph + live image (W3). t83 = caller analysis of the banked
decoder FUN_0005caac (control-byte grammar source): find its callers in
the restored image, decompile the loader caller, and look for where an
in-record DIMS field would be READ (the grammar asm never mentions dims;
a consumer read site would name the offset). If no caller reads dims,
bank that as the hard static boundary for the residue.
T81 LANDED (OQ-003 field-meanings leg): growth pass decompiled
(FUN_00038f68 -> work/coswnd_decomp/38f68.c) and revalidated against the
FULL 20-slot r1deep timeline: 90/90 owned-planet transitions agree
(rate = stored PROS + 1 iff owner != DAT_0007458e and PROS<4; threshold
DAT_000066e4; cap clamp to +0x4a; upkeep>=cap resets accumulator; slot0
excluded as banked seed residue, slot n in {0,1} fitted because
DAT_00012e10 reads 0 across all r1deep slots). Live global votes 20/20:
DAT_000066e4=50, DAT_0007458e=0 — rewrite campaign.cpp growth block
matches EXACTLY, evidence upgraded, no code change. +0x4a=POP CAP and
+0x55=population SEED named (equation re-measured; uniform +2 = banked
event-50 bonus, not a gap); +0x0a explicit UNMAPPED. Mid-turn trap:
payload-FILE reads at 0x82bb0+X are pre-relocation garbage (returned
threshold 100); only live member P0+0x82bb0+X is valid — banked so no
future turn re-trusts the file read. scripts: r1_t81_census.py,
r1_t81_mpop.py. OQ-003 residue now = packed-entropy regions only (shares
OQ-005 blocked closure class).
NEXT t82 (ledger triage + capture-class prep): the open ledger is now
OQ-003 (packed-entropy residue), OQ-005 (blocked), OQ-010 (one-battle
recipe banked), OQ-019 (blocked), OQ-021 (BLOCKED-USER-LEVEL), OQ-023
(state-enum capture). Verify each still states its closure class and
exit-code route; prepare (do not run blind) the cheapest R1 capture that
would close a real item: the one-battle OQ-010 recipe — confirm its
harness still exists and gate-cleans, record readiness, no spiral.
T80 LANDED (OQ-003 join leg, offline): star->planet JOIN CLOSED by
measurement — pointer law star-rec +0x2A/2E/32 u32 P -> planet NAME at
file offset P-2507337 (116/116 RESUME.GAM; banked-base form P-K-0x24),
plus pool-membership law u8 name-0x18 == owning star idx 138/138 over the
whole contiguous stride-123 planet pool 0x8e0e..0xd05c (22 IV/V rows are
beyond the 3-pointer capacity and unlinked — membership field is the
authoritative join). Star chain: 96-B records mirror BYTE-VERBATIM into
live RAM (50/50 rows; single 12-byte repair window on Barataria's 0xFF
tail) — copied-not-parsed re-confirmed star-side. Mid-turn "two planet
regions" reading caught and corrected before commit (bad walk-back base;
t75 0xaae2 chain = mid-pool entry, its owner-join law stands). Star-idx
field t50 [inferred] -> [verified]. OQ-003 stays OPEN: +0x0a/+0x20/+0x4a/
+0x55 meanings, counter identity, packed-entropy regions remain; no
rewrite behaviour change (rewrite is fresh-start-only; mapgen already
generates 3+ planets/star).
NEXT t81 (OQ-003 field-meanings leg): the t50 banked unknowns +0x0a/
+0x20/+0x4a/+0x55 (name-0x24-base) — census each across the r1deep 20-slot
timeline for monotone/turn-coupled behaviour (population/shield/production
candidates), and cross-check candidate meanings against the banked income-
law channel words; every field either gets a cited meaning or an explicit
UNMAPPED verdict.
T77b LANDED (diplomacy state-enum: honest block, one retraction banked):
static re-read of the chooser entry @0x447ba (`cmp byte [ebp+0x1c0],0 / JE
skip`) proves the relation-state byte gates ALL diplomacy emission, but
the banked corpus cannot settle WHICH nonzero value is war vs allied: an
idle-slots census (945 slots) shows ONLY value 1 off-diagonal and the §7
rung structure admits no injective enum from idle data alone. A first
window-census draft claiming '1 = AT WAR' was CAUGHT BY CROSS-AUDIT
against the chooser gate and RETRACTED in diplomacy.md §10 before any code
site consumed it (also recorded: the base-0x12e16 window needs per-run
re-validation before any future census trusts it; the drift-filter rerun
was itself mis-implemented — noted so its all-drifted output is not
re-read as confirmation). Kept facts: matrix structure law (attitude i16
+0x1b2+2t, state +0x1c0+t, row stride 0x1ee @0x12e16 static) + live
START_ATTITUDE values 310..620 match race files verbatim. LEDGER: OQ-023
stays open with the state-enum RESIDUAL RE UNKNOWN named explicitly
(same closure class as OQ-021: interactive session); diplomacy.h header
comments updated MEASURED->[inferred]-retired ( DECLARE_WAR range
re-measured 130..450 across 21 race files mid-turn, my draft's 150 fixed
before commit). No rewrite behaviour change this turn; 108 tests stand.
NEXT t80 (OQ-003 field-semantics leg, offline): star-record fields
(name-0x1C small per-system value; name+0x10 stride-0x39 sub-pool; star
+0x17 owner byte per §9; starlanes table 0x16147 stride 0x27 owner bits
+0x20) cross-joined against .gam star chain (0x1e46 stride 96) and
planet chain (0xaae2 stride 123) over the banked r1deep slots — every
field gets a join or an explicit UNMAPPED note; save-writer code dive
(FUN_0004* save family) only if joins suffice to name the packed regions.
T79 LANDED (OQ-025 CLOSED same-turn it was opened): the t78 "non-shell-slot
at T=100" lead was a MEASUREMENT BUG — hypot(x,y) is the xy-PROJECTION of
the sphere point f32[x,y,z]@name-0x14; projection scatters discs by
geometry. Correct measurement (scripts/r1_t79_pos.py; records gated idx==k
+ planet-pointer-on-grid; in-play = chain head cut at slot DAT T) across
T=15/25/50/75/100 arms + r1deep control: shell radii FIXED (440,365,290,
215,140,65,50) at every size; shell POPULATIONS = halving law (shell0 =
T//2+1, shells 1..5 halve the remainder (rem 1 keeps), shell6 keeps tail):
15->8/3/2/1/1, 25->13/6/3/1/1/1, 50->26/12/6/3/1/1/1 (== the 2026-10-06p
battery table EXACTLY — the battery was an instance of the general law),
75->38/18/9/5/2/1/2, 100->51/24/12/6/3/2/2; zero monotonicity violations
everywhere (viol=0 all arms). Self-caught on the positive control (deep
run disagreed with the banked 0/1225 law -> checked my own reading before
doubting the banked law). Rewrite UPGRADED: shellRadiiFor(n) (mapgen.cpp
anon namespace) replaces the i%50 wrap (measured WRONG for T>50: slot 50
lives on shell 440 pop 51); at n=50 output identical to old table so
default timelines untouched; ladder test extended with per-size shell-run
expectations (108 tests 0 failed); mapgen.md §OQ-025 + ledger + mapgen.h
comment re-cited.
T78 LANDED (OQ-012(a) CLOSED BY MEASUREMENT + OQ-025 opened): GALAXY_MORE
button (windows.txt NEWGAMEWND rect 7,381..122,472 -> (64,426)) cycles FIVE
densities, each arm a fresh New Game, T read from slots via pointer law
(scripts/r1_t78_read.py over save/*.sav Memory): Average 50 -> Dense 75 ->
Very Dense 100 -> Vacuous 15 -> Sparse 25 -> wraps Average (runs
r1size-{033341,040859,041459,042719,043229,044658,045501}; labels from
screenshot crops, click law per run click.log). Harness bug found+fixed
mid-turn: env var is NCLICKS (CLICKS silently no-op'd two arms, re-ran
them). GATE FIX: the t78 capture harnesses leaked their Xvfb servers on
exit (t75 has a cleanup trap; the t78 scripts didn't) -> 9 orphan Xvbfs
held displays :90-:98, and the intro pixelcheck on :91 captured a stale
root window (1024x768) instead of the game; pkill -x Xvfb + EXIT traps
added to all three t78 harnesses, gate re-green (GATE_EXIT=0). Non-default-T POSITION law measured NON-shell-slot (T=100 chain
idx==k verified: 3537/4950 slot-radius inversions vs 0/1225 at T=50;
envelope max r=440.0 holds) -> new OQ-025 open, banked offline-solvable
from r1size-* slots. Rewrite UPGRADED: --stars CLI knob (main.cpp
Options::stars -> MapConfig::starCount, usage text), default 50 re-cited
mapgen.h, mapgen.cpp:92 comment re-marked DOCUMENTED DEFAULT (OQ-025);
test galaxy_density_ladder_matches_measured_sizes pins the five sizes +
connectedness + r<=441 envelope; 108 tests 0 failed; CLI spot-verified
T=100 and T=15 campaigns run. mapgen.md new §OQ-012(a) CLOSED section.
T76 LANDED (OQ-021 CLOSED-EXHAUSTIVE FINAL + OQ-023 lead): all 10 code
readers of the star-owner block DAT_00013bc5 decompiled (work/coswnd_decomp/
3ecb8.c 220a8.c 3a4e0.c 3eb88.c 439f4.c 44634.c 49c14.c 49d2c.c 500e0.c):
NONE is the end-ctrl comparator — 0x3ecb8 = per-race AI ATTITUDE scorer
(state table [obj+r+0x1c0]: 1=ally-ish path sums star-bitmap +0x14/+0x15
product with 0x67aa 31-byte record entries and 0x13b9c stride-6 weights,
applies -1/+3 on the two-others-ally comparison and -2/+4 on relative-
strength deltas; state 2 = rank-distance path clamp(0,3); accumulator
u16@(obj+r*2+0x1b2) clamped [50(0x32), 950(0x3b6)] with hi-word gate
(obj+r*2+0x1b0)>>16); 0x439f4 = ally-bitmask builder (state==2 races);
0x44634 = pair-adjacency test on star bitmap +0x17. => comparator ABSENT
from image at full scope (confirms 06s; t74 S5 + t75 capture death, see
BLOCKED T75 POST-MORTEM). Corpus adjudication: 745 banked slots across
every r1* run, 0 with DAT_43510/DAT_4350c armed — idle scripts never
colonize, so no banked evidence can ever close OQ-021. LEDGER UPDATED:
OQ-021 BLOCKED-USER-LEVEL, default >1/2 unchanged.
(t80 NEXT superseded — see T80 block above.)

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
DONE t70: ledger OQ-005 rewritten (closed portion cites S9/S12/S14/S17 +
code site rewrite/src/formats/shp.cpp + measured corpus; residue
BLOCKED-USER-LEVEL). OQ-010 triaged: batmode join=6 small funcs under full
analysis; static route at banked hard boundary; headless corpora zero ships
-> in-battle capture = OQ-019 class (BLOCKED entry filed w/ one-battle
closing recipe). Ledger open set now: OQ-010/OQ-019/OQ-021 (capture-class),
OQ-003/OQ-016 (replay-only/documented), OQ-012(a) (R13), OQ-023 (parked).
DONE t71: RECALC RESIDUAL CLOSED (income-law.md T71; ledger).
byte-exact FUN_00038ba4 recompute == stored +0x44/46/48 at ck001/020/060/
100 of the 52-turn run AND .gam-restored slots (5/5 everywhere). t55b
"missing term" + S6 52/139 were harness-era artifacts (pre-t33 raw slot
reads). Harness: r1_income_law.py --slot now finds ck/ AND save/ (was
silently failing late-timeline verification). Rewrite code UNCHANGED —
existing channel chain verified exact, pin campaign_channel_law_oq016.
DONE t72: OQ-021 restored-image scan — strings FOUND (0x83b16/0x83b2a in
a GAMEWND/..\coswnd.cpp pool => consumer module identified); VA==file
offset encoding re-inverted from known-good 0x2b224; zero u32 code-region
refs (R12: lead-out not proof). NEW bounded angle banked: 36 coswnd.cpp
functions never decompiled (batches 1/3 skipped coswnd).
NEXT t73: DONE (see T73 block) — t73b = eventwnd.cpp module decompile batch
(OQ-021 comparator hunt).

T74 LANDED (OQ-021 static CLOSED-EXHAUSTIVE + capture de-risked; score.md S5):
selector-writer hunt negative under ALL direct encodings (moffs, mod00/disp32
incl SIB-25, mod10 base, cmp grp, f6/f7) AND under runtime-relocated
full-RAM scans: relocated 0x43510 addr occurs EXACTLY 3x in 16MiB (= the 3
known readers), struct base 0x4348d EXACTLY 1x (0x1d740 end-EVENT-QUEUE
builder: c6 35 byte-stores, sub-record stride 13, type bytes 0..8 measured,
count u16@0x43502==9 both runs). f32 2/3: ZERO image-wide; f32 0.5: only a
data bitmask ramp. STRUCT MAP: 0x4348d queue (count/counters 0x43502/04/08),
0x4350c rank, 0x43510 fired-selector. LIVE OWNER LAW MEASURED: static table
0x3a095 (stride 0x162, owner byte +0x56) stays ALL-0xFF for the ENTIRE
campaign (19 slots, 2 runs incl deep ck067) — the BLOCKED recipe's inject
site is WRONG TABLE. Live copy = heap: found at corollary X=0x38ad8 in ck067
(16 owner-0 + 85 x0xFF of 101 cap; candidates cluster stride-0x162 phase-4,
(43 hits — pin with two checkpoints before injecting). Owner dword +0x54 in the
STATIC table reads 0xFFFF always (do not confuse with live +0x56).
T74b SCENARIO CORRECTIONS (offline, RESUME.GAM + ck067): total stars T=50
(hi-u16 DAT_16143 measured — NOT 101; my 101-record table scans over-ran the
table). .gam STAR CHAIN FOUND: 0x1e46 stride 96 x 50 records (names verified:
Masticon..Barataria); .gam contains NO 0x162-stride owner table (exhaustive
offset scan) -> owner encoding rides the planet/system records (t50 join
class), NOT a star-table copy. Discriminating injection band at T=50:
owned 26..33 (fires >1/2, not >=2/3) — use 30. RAM star chain is NOT
contiguous at name+stride 96 in ck067 (allocator scatters; chain-walk law
holds per-record via idx/pos anchors only).
CONCRETE NEXT t75 (capture, exit-code driven per R1 law): via r1_planet_layout
join, find the RAM byte within the 123B planet record that is player-owned in
a colonized AI/player planet (ground truth: banked ck corpus mid-campaign)
vs unowned; verify same offset in .gam planet chain (0xaae2 stride 123, t53
convention); inject owned=player at 30 systems' home-planet records in scratch
RESUME.GAM, boot r1_mutation_run pattern, end-turn x2, read DAT_43510 byte
(corollary idx) + end-screen screenshot. Fire @30 => >1/2; no fire => 2/3. If
owner ground truth unresolvable from banked corpora -> record one line
(capture class, needs interactive colonization), move to OQ-003 replay
semantics.

T75 LAUNCH (in flight): join SOLVED offline — .gam planet chain 0xaae2/123
+0x33 == RAM planet +0x57 (83/83 join rows on r1mut world incl owned Verithil
I==0; star-chain +0x33 writes VOID — unowned stars legitimately hold 18/250).
Chain spans 29 distinct stars; the 4 AI home stars are NOT in the chain
(zero-collision verified) -> injecting owner=0 on ALL chain planets = 29/50 =
58% band: fire => (50,58]% (>over half), no fire => >=58% (two-thirds class).
Harness banked: scripts/r1_t75_inject.py + r1_t75_run.sh (511,67 end-turn x4
at 30 s, t56 law) + r1_t75_read.py (per-slot owned/selector/rank + VERDICT).
rev1/rev2 FAILURE DIAGNOSED (shot-02 = still title menu): clicks went to
(318,333) = NEW GAME row; pixel-measured rows put Return-to-Current-Game at
(318,372). HERMESSEN needle useless at verify (text RAM-resident at boot from
the .gam). rev1 endturns=0 (absolute-vs-relative NOW bug, t75b); rev2 clicks
landed but game stayed at menu -> DAT_482fb stayed 0 = INVALID not no-fire;
read.py now tri-state (FIRING / NO-FIRE-with-counting / INVALID rc=1).
rev3 IN FLIGHT proc_f5c3fcaf82cd (r1thr-*, BOOT=200, resume (318,372) x6
from t=75, end-turns optimistic from t=150, adjudication POST-HOC: counting
>=1 star only happens in-campaign). On completion: read analysis.log ->
update OQ-021 (CLOSE only if FIRING or NO-FIRE-with-counting), possibly
campaign.cpp:738, gate, commit. If rev3 INVALID: one line per exit-code law,
OQ-021 capture needs interactive session -> BLOCKED, move to OQ-003.

T73 LANDED + CORRECTED (OQ-021 static, dark-zone HIT; docs/re/score.md NEW):
(1) ATTRIBUTION CORRECTION: work/attribution.tsv est_func is a BACKWARD-SCAN
estimate, NOT a function start — all 36 coswnd est_func values landed mid-
function (0/36 in functions_full.tsv); re-resolved to 12 CONTAINING functions,
decompiled all 12 (scripts/coswnd_run.sh, fresh ghp6 project, DecompileCombat
.java now env-driven DECOMP_TARGETS/DECOMP_OUT; ghp4/ghp5 untouched).
(2) t72's "zero u32 refs to the score strings" is REFUTED by corrected scan
base (t66 lesson): OQ-004 pool-relative immediates = str_off - 0x82BB0 (NOT
VA). push 0xf66/push 0xf7a sites = 0x2807b/0x280e7, inside the DARK ZONE
0x26b32..0x284bb which holds ZERO Ghidra functions (auto-analysis never
reached it) — that is why every static-xref route was blind there. Runtime
law re-verified live (r1deep-20261007-224831/41.sav): code relocates
0xf66->P0+0x83b16, 0xf7a->P0+0x83b2a exactly at the anchored site (window
0x280de.., block base == B vote); obj1 data at B+0x82bb0+X law re-confirmed
(item table 'Factory' name anchor).
(3) SCORE-DISPRODUCER LAW (dark zone 0x280be..0x280e7, raw objdump
-b binary -M intel on work/ascend_restored.bin — banked harness tool):
percent = TRUNC( DAT_000482fb * 100 / (DAT_00016143 >> 16) ) — mul-100 idiom:
lea eax,[edx*4]; sub eax,edx (=3N); shl 3 (=24N); add edx,eax (=25N);
shl edx,2 (=100N); mov eax,edx; sar edx,1f; idiv ebx (ebx = signed hi-word
of DAT_00016143 = total stars). "STARS CONTROLLED %d" prints DAT_000482fb
itself (push eax @0x28079 after mov eax,ds:0x482fb @0x28074); shown only
when DAT_0010ba0 == -1 == [ebp+0x58e] (0x28059..0x2806e gates). [inferred:
DAT_482fb = player-owned star count; producer not yet traced.]
(4) end-ctrl PRESENTER is eventwnd.cpp (NOT coswnd): jump-table handler
cluster 0x2c03a..0x2c0b6 pushes pool-rel end-*.txt names (0x130c/0x1319/
0x1333/0x1340/0x134d -> end-xtnc/-dest/-unit/-ctrl.txt + "Couldn't open %s",
payload 0x83ebc.. verified); file-name dispatch by ReadFile (0x7739d) +
strcmp (0x775aa) against 0x1371/0x1375 strings. DAT_43510/4350c: ZERO write
encodings in image (A0/A2/88/8A/89-05/c7-05/A3/80-grp scans over 0x200..
0x82bb0) — comparator consumer is a BYTE reader (a0 at 0x2c01d) fed by the
END-CONDITION EVALUATOR, which must live in the same dark zone (0x26b32..) as
its 0x280be sibling. CONCRETE t73b: enumerate dark-zone functions by
prologue/epilogue walk (objdump whole 0x26b32..0x2c600 span; find the block
containing 0x2c01d), grep for cmp idioms x*2 vs N / x*3 vs N*2 feeding the
DAT_43510 byte; default >1/2 stands until cited comparator.
HARNESS LESSONS: objdump -b binary -m i386 -M intel works directly on the
restored image (no Ghidra round-trip for dark zones); Ghidra function names
FUN_ + 8 hex digits (6-digit regex = silent zero); r1_sav_scan.find_base
returns (votes,positions) tuple — vote most_common(1) with >=5 threshold.
T85c LANDED (user testimony adjudicated against the banked stream):
(a) CONTROL: player saw NO victory screen through t1131 -> consistent with
>1/2 on DAT_482fb (max 23/50=46%); cheapest closer is the score screen's
own percent (law percent=TRUNC(100*DAT_482fb/50)).
(b) ORFA: never accepted because att[Orfa->Chamachies] peaked 485, never
crossing their ACCEPT_ALLIANCE=570; player PROPOSE moves only the
player-side cell (600). docs/re/diplomacy.md §12.
(c) COMBAT OQ-010 CORRECTED: t85b's "zero AI-ship events" was a
free-record (65535) filter artifact; presence-law census banks 9
owner->free deletions, 4 of them Minion ships (slots 0/5/8/12 — the
Minions fielded exactly 4 ships in 1100 turns, all died in-war; matches
"only one ship, it didn't shoot back"). scripts/r1_t85c_focus.py.
(d) NIMBULOIDS: NOT in the campaign window — every trusted row n=4
[Chamachies,Orfa,Ungooma,Minions], ship owners ever {0,1,2,3}; the
repulsion cannot be their SA_IndustryBoost (or Frutmaka's, also absent).
Only Ungooma holds a lane effect (SA_BumpShipsInLanes); reversal census
is proportional-to-movement (cannot isolate firing race by kinematics).
OPEN USER CHECK (10 s): read the race NAMES off the in-game diplomacy
screen — if it shows "Nimbuloids" where memory decodes "Ungooma", the
+0x1c0 name-byte decode is wrong, not the player.
NEXT: war on the real 5th power is NOT possible in this campaign (n=4);
combat-law closure needs either in-battle frame recording or the static
application-code site (Ghidra, no capture). Gate GATE_EXIT=0, audit
AUDIT_RC=0, open {003,005,010,016,019,020,021,023}.
T85c-followup (player answers): race-name check RESOLVED — decode says
Ungooma, screen says Ungooma; "Nimbuloids" was a player typo. Name-byte
law validated; repulsion attribution (Ungooma SA_BumpShipsInLanes) stands
unopposed. Score-screen closer DEAD — no score screen exists in the SP UI
(disproducer is debug-pool/gated, score.md S7). OQ-021 closer is now
passive: keep playing; when a turn-boundary DAT_482fb sample reaches 25+
(26 systems_any currently, but boundary sample 23; the current held-turn
autosave reads DAT_482fb=0 — turn-boundary reads only), watch whether the
0x2c01d end-ctrl arm fires. Combat (OQ-010) needs in-battle recording or
the static app-code site; Nimbuloid war is impossible (campaign is n=4).
