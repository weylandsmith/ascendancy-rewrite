# STATE — machine-readable working memory for the closeout loop (v2)
# Update EVERY turn. A fresh session must be able to resume from THIS file alone.
# v1 history (full turn log 2026-10-03..2026-10-05l): archive/ralph-v1/STATE.md
# Patch discipline inherited: ONE patch per region, read_file verify after
# (multi-patch batches mangled v1 twice).

phase: P7-closeout
milestone: 6  # keep 6: gate.sh keys build/test/boot stages off milestone >= 3; lowering it silently guts the gate
updated: 2026-10-29T18:30
policy: strict-close  # FINAL-DEFAULT never closes an OQ; only cited measurement does (docs/GOAL.txt)

## LEDGER (statuses mirror docs/OPEN-QUESTIONS.md; that file is the record of
## resolution evidence — this block is the fast index. Update BOTH or neither.
## t157 LESSON: hand-mirroring drifted 6 rows (5 closed rows still listed open,
## OQ-023 missing) and nothing caught it — at t157 gate.sh ran NEITHER ledger
## check, and ledger_audit only checked the record against its own --expect
## list (both statements pre-t158; see the t158 note below for current state).
## RE-DERIVE, don't hand-maintain: python3 scripts/ledger_index_check.py prints
## the true open set from the record and diffs this block against it. AS OF
## t158 gate.sh stage 3t RUNS that check plus ledger_audit on every gate, so
## this block cannot drift out green anymore.)
ledger:
  closed:
    - "OQ-026 visibility layer CLOSED 2026-10-29 t195 (implement+pin, the
      row's own closure bar set t194): rewrite campaign.{h,cpp} models
      laneVis_ (rec+0x20) + starLaneVis_/starSelVis_ (obj +0x16/+0x17 twins,
      kept separate per differing t193 censuses); viewerMaskFor == FUN_00021a84
      verbatim; filter == 0x2914e AND; stars unconditional (L9 honest negative);
      shareLaneVision == FUN_00046354 shape (N=rand%(3|6)+1, OR-only; BIDIR at
      alliance formation 0x45778 wired, RECEIVE-only first-contact one-shot
      per cited shape 0x55f6e); SA_KnowStarLanes/SA_KnowHomeWorlds wired at
      scenario init, LEFT the FILED NO-OP set (kNotes 4->2). Pin
      campaign_visibility_law_oq026_t195, 111 tests 0 fail; ships.md S23 L10;
      residues documented in the ledger row."
    - "OQ-001 .cob offsets = N not N+1"
    - "OQ-002 FLIC codec (both vendor videos, golden-pinned)"
    - "OQ-023 relation-state enum semantics CLOSED 2026-10-29 t189b — state-3
      ALLIANCE event OBSERVED (cell0i=celli0=3 @t1335 wall 23:47:43, att
      +10/+10, 68 sustained raw rows, scripts/r1_t188_state3_arbiter.py RC=0
      re-run); flip comparator atti0=631 > Orfa ACCEPT_ALLIANCE 570 = the t180
      static law (0x4562f/0x45641) corroborated end-to-end; identity
      2=WAR(t85b)/1=PEACE(t187)/3=ALLIANCE(this); docs/re/diplomacy.md §13+§16;
      rewrite unchanged diplomacy.cpp:227/:244; engine-build residual ->
      docs/PLAN.md A7"
    - "OQ-022 music span-vs-check contradiction CLOSED 2026-10-07 t8 — player
      FUN_00059c70's 0x1d4d0 span check never sees theme00 (guard @0x59984
      precedes the checked call; DS:0xa200c all-zeros 10/10 saves,
      DAT_00010ba0==0); engine INACTIVE in captured states, audio.md §3.4,
      no rewrite dependency; menu-music server explicitly unmapped (non-claim
      banked)"
    - "OQ-024 planet GOVERNOR assignment law CLOSED t45 — @0x38df0 branch of
      FUN_00038ba4 pinned verbatim (item 33 -> PROS+=IND>>2, item 34 ->
      RES+=IND>>2); [0x743b9]>>0x18 == item-table UPOP(35), 32/32 saves;
      writer census r1_0x54_writer_sweep.py, activator @0x38b26 sole trigger,
      0/2810 corpus records hold 33/34/35; rewrite PlanetState::governor +
      storedProsFor/storedResFor (campaign.cpp/.h), pin
      campaign_governor_law_t45"
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
    - "OQ-006 headerless sample rate CLOSED 2026-10-07: DEVICE rate = 22050
      MEASURED — open chain PUSH 0x5622 @0x4f690/@0x4f90b -> CALL 0x68816 ->
      unique edge 0x68882 -> rate setter 0x6e000 stores [obj+0x3c]; constructor
      default 11025 @0x6df3e always overwritten; audio.md 3.1; pin
      audio_open_rate_measured_oq006 (channels: no vendor field, mono by
      convention)"
    - "OQ-012 mapgen CLOSED t78: (a) size options measured 2026-10-12 (density
      cycle 50/75/100/15/25, wraps; rewrite --stars knob), (b) closed 06o (pps
      U{1..5}), (c) closed 06p/06q (shell position law; rewrite upgraded +
      tested), (d) closed 06k (sphere extent, refined by (c))"
    - "OQ-015 DA_ template selection order + full %token table CLOSED
      2026-10-08 (t12-t14): chooser FUN_00044a44 return == ACTIONS pool idx;
      DIPVALUES field map via FUN_00044290; trade gates/cadence rekeyed into
      OQ-023 as BUILD work (law in hand, engine unwired); %token census 22/22
      files == {%m,%y,%s,%t}; pins dip_action_chooser_law_oq015_t12 +
      dip_strict_threshold_oq015_t13 + dip_trade_predicate_bytes_oq015_t14"
    - "OQ-020 ability charge days CLOSED t100: cadence word
      WORD[0x6780+2*ability] (live 60.sav == FILE 0x89330, zero writers;
      5:60 6:100 7:62 8:77 9:90 10:150 11:70 12:63 13:66 14:72 16:92 17:100
      19:89 20:68, zeros == passive set) wired as kCad[21] in species.cpp
      abilityChargeTurns + abilityPhase COUNT-UP law; pins + verify tool
      r1_t100_cad_verify.py both legs"
    - "OQ-025 mapgen non-default-density POSITION law CLOSED t79: shell radii
      fixed at every size, populations = halving law (T//2+1 then halve);
      reproduces the T=50 battery table exactly; rewrite shellRadiiFor()
      replaces the wrong i%50 wrap; ladder test extended"
    - "OQ-003 .gam packed-entropy residue CLOSED t181 by MEASURED DISCLAIM
      (the row's own decision option): three-class diff
      scripts/r1_t181_banddiff.py at located RAM addresses — band boot-vs-
      played 432/2048 (21.1%) vs header/S-table/pool/block11200 87-100%;
      baseline member 0x2e7a0e = 0/16 nonzero; not compressed (0/2316 blocks
      >=6.8 b/B); game runs without it x3 (golden resume.gam band span 133
      nonzero bytes boots; RESUME-014 EOF 0x12753). Writer-side copied
      session memory, not a format field set; scratch identity stays
      UNNAMED non-claim. docs/re/savegame.md §t181; rewrite unchanged
      (fresh-start-only)"
  open:
    - "OQ-005 .shp pixel codec — static route exhausted (6 angles,
      docs/REFUTED-ROUTES.md); needs exe shape loader via live image"
    - "OQ-016 campaign per-turn constants — scope NARROWED t29: income,
      growth, cadence, build order, AI SELECTOR LAW (S9) and POP-CAP SEED LAW
      (S10) closed (income-law.md S6..S10). STILL OPEN: per-cell
      terrain/nuke wiring, home-placement verification, +2 residual minutiae
      (0.4% samples), scenario-template preset source"
    - "OQ-019 ship design model (hull+gizmo inventory, cost hack, Orbital
      Docks); per-ship combat application = OQ-010 aggregate caveats S2i"
    - "OQ-021 end-ctrl threshold: comment 'over half' vs prose 'two-thirds' —
      t73 dark-zone hit: score strings at 0x2807b/0x280e7 (pool-rel), score law
      TRUNC(100*DAT_482fb/T), presenter eventwnd.cpp 0x2c03a cluster;
      comparator writes = ZERO direct encodings -> evaluator hunt via
      dark-zone enumeration (t73b); capture fallback. Default >1/2 stands.
      t189b STATUS: 14->21 drift real, NOT systems count; displayed-count
      write-site is now the residue"

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

NEXT t197: SHP SPAN-BOUND CORRECTION — VALIDATOR X-CLASS + REWRITE decode()
FIDELITY (arrives from t196, docs/re/shp.md S20 items 2-3): (1) extend
scripts/r1_shp_unifiedlaw.py with tag X = "canonical stream slot, canonical
dims, EXACT-H row walk with NO [rec,nxt) bound" (keep V/A/B semantics and the
FAIL definition otherwise; paint-profile note per record: trailing all-skip
rows vs header-desync tail via the painted-per-row probe in
docs/re/_wip_t196.md S4); re-run corpus -> new V/A/X/FAIL tally + libs-clean
count, pin as its own gate stage ONLY if cheap (else cite in shp.md S21).
(2) Rewrite decision with citation: rewrite/src/formats/shp.cpp decode()
currently fails these 29 frames on the span bound; the blit (FUN_0005caac) has
NO length arg and NO overrun error (-1 dims/@0x5cb2b, -2 empty clip/@0x5cb36,
-3 outside/@0x5cea5 only) and draws from a verbatim whole-library cache copy —
so faithful behaviour = walk exactly H rows unbounded, W/H sanity clamp 4096
KEPT (1starmap k1-class dims 0x7ffffdbb must still be rejected). Update
decode() contract comment (rows past span are real stream bytes; destination
semantics unchanged), add pin test campaign/shp_span_free_t197: planind k0
walks 99 rows, row-96+ content equals next-header-junk walk (deterministic),
1starmap k1 still rejected, 3cfgnew k12 still rejected (EOF short), mouse k6/7
still rejected (dims word invalid). (3) Regenerate work/r1/shp_png evidence
via r1_t182_pngdump.py + ids.tsv X-tags; update the numbers cited in
OPEN-QUESTIONS OQ-005 + shp.md S18/S20 headers. DO NOT re-open the dims-location
claim for the 29 (t196 measured it); DO NOT touch cos_star k40..k51/mouse/
1starmap k1/sg50expl k9 (paint-routine census is their next gate, queue item
PER-PLANET ECONOMY FIELDS + GAUGE LIBRARY LAW keeps that slot — its (a2)
paint-routine leg also decides those 16 + the level->record compression map).
RATIONALE: t196 PROVED the OQ-005 "80 unknown-dims residue" framing is mostly
a validator artifact — 29 records are full frames under the CLOSED dims law,
and the rewrite (a validation asset per option C) currently refuses to decode
live UI art (planind = the manufacturing gauge). Leaving decode() knowingly
unfaithful is the one state worse than fixing it; the fix is offline, offline-
sized, and testable without play. Vision oracle is INTERMITTENT on this
deployment (works, occasional 500 'image input is not supported' — retry);
R13 substantive ban unchanged: never self-grade codec correctness by pixels,
never derive UI geometry from screenshots; label-digit misreads are a vision
pitfall (trust triage_report.txt numbers).
Do NOT re-open: the visibility layer (CLOSED t195), span-bounded-walk-as-vendor
law (t196 refuted: blit has no length arg), planalNN-as-population-poses
(killed t196 S20.4), the regpair/shift enumeration plan (RETIRED), LIST==mask
(superseded), byte+0x23 (t190), a 7th BLIND .shp codec sweep (FORBIDDEN; the
X-class tag is a bound correction on the CLOSED grammar, not a codec sweep).
If a REAL sitting arms first (TRIGGER-A baselines: full-ns mtime
1793294532100000000 / size 5,721,578,066 / tail md5 9054cc6c), adjudication
via scripts/r1_t85g_sitting.py on the named dir STILL outranks everything.

LANDED t196 (2026-10-29, this session): RESIDUE TRIAGE VIA VISION ORACLE —
the OQ-005 residue is LARGELY A VALIDATOR ARTIFACT. Trigger triage: timeline
size == frozen baseline (no sitting), tree clean at t195. STRUCTURAL CUT
[verified]: 71 FAILs = 26 EMPTY (zero stream bytes; expl*/sg*expl ladder-tail
+ k0-variant slots, dims word 0x7FFFFFFB-class) + 13 TINY (cos_star k40..k51,
sg50expl k9) + 32 ART. UNBOUNDED WALK [verified]: from the canonical stream
slot (rec+8 k0 / rec+0x18 k>=1) with canonical dims and NO span bound, 29/71
complete EXACT-H (planind k0-12, 3cfgnew k0-11, 14intel k8, 1starmap k3/4/6);
tail probe proves past-span rows are transparent skips (planind rows 96-98
all-zero; row 95 = next-record header bytes 6b 00.. desynced into a fill run;
1starmap/14intel tails paint 0.0 px/row). BLIT WITNESS [static S12]:
FUN_0005caac has no stream-length arg, no overrun error code; cache = verbatim
library copy => [rec,nxt) bound = OUR invention (t182 off-by-8 species).
3cfgnew k12 = genuinely truncated at FILE EOF (55/79 rows). dims-location stays
honestly open for exactly 16 non-walkable-dims records (cos_star x12, mouse
k6/7, 1starmap k1, sg50expl k9) + the empty class. VISION IDs banked (5 passes
+ 1 retry after a 500 blip): planind=manufacturing factory ladder (+1 grey
tank/level k8->k12); planres/planpro = monotonic k0..k20 level ladders (index =
plausible level; ~60-level testimony implies a compression map, uncited);
3cfgnew = new-game/race-config art (dot-wheels/shields/orbs — NOT a gauge);
1starmap = star-map sprites ("NEXT TURN <ENTER>" verbatim); mouse = cursors
("Exit <ESC>"); planitem = distinct item icons (not animation); planets = biome
spheres; planal00 = cratered-surface crops -> population-pose hypothesis
KILLED. VISION PITFALL banked: misreads small label digits (rows=77-95 read as
7-9) — numbers from triage_report.txt only. ARTIFACTS: tools/shp_partialdump.
{cpp,bin} (permissive walk, NO candidate search), scripts/r1_t196_sheet.py
(RC=0), work/r1/shp_png/{ids.tsv, _t196_probe.json, sheets/sheet1..5 +
triage_report.txt}. DOCS: shp.md S20 (law + amendment + pitfall),
OPEN-QUESTIONS OQ-005 STATUS t196 (row stays OPEN — strict-close: 16 unknowns
+ player ruling remain), _wip_t196.md S0-S4. Ledger open set UNCHANGED =
005/016/019/021. Gate 0 + LEDGER AUDIT OK + LEDGER INDEX OK.


LANDED t195 (2026-10-29, this session): OQ-026 CLOSED — VISIBILITY LAYER
IMPLEMENTED IN THE REWRITE + PINNED (the row's own closure bar). Trigger
triage first: timeline size/mtime EXACTLY the t194 re-frozen baseline (no new
sitting); harness-reported dirty loop_one_task.sh was a STALE snapshot (git
diff empty, HEAD=t199 already committed) — nothing to adopt. REWRITE
(campaign.{h,cpp}): laneVis_ (rec+0x20), starLaneVis_/starSelVis_ (obj
+0x16/+0x17 twins KEPT SEPARATE — t193 censuses differ), viewerMaskFor() ==
FUN_00021a84 verbatim (0xff->0xff else 1<<(idx&0x1f)); laneVisibleTo/
cosmosLanesFor == the 0x2914e AND-filter over pool order; cosmosStarsFor
UNCONDITIONAL (L9 honest negative pinned); shareLaneVision == FUN_00046354
shape (N=rand%(3|6)+1, OR-only, receive prefix leg + mirrored lend leg);
shareStarVision == FUN_00046524 twin (modulus 4|2). Fire sites: BIDIRECTIONAL
at alliance formation (cited caller 0x45778, wired in diplomacyPhase
ProposeAlliance branch) + visibilityPhase() per-advance one-shot per pair on
FIRST lane-adjacency contact (cited shape 0x55f6e; rewrite-site documented
default). Init seed = own claim EXACTLY (t192 law + t193 re-read); unowned
lanes fogged for all (t193 {0:940}). SA_KnowStarLanes = owner bit on every
lane; SA_KnowHomeWorlds = owner bits on both twin bytes of every alien HOME
star — both LEFT the FILED NO-OP set (species.cpp kNotes rows 3/15;
ability_probe 3m 4->2; abilities.md rows WIRED). Separate visLcg_ stream —
campaign rng_ untouched (RNG discipline). PIN TEST
(campaign_visibility_law_oq026_t195): 25 checks incl spectator AND (mask-0
lanes stay hidden even for viewer 0xff — no bypass at 0x2914e), receive-only
directionality, N envelope, sticky monotonicity over 30 turns, alliance BIDIR
share incl star twin both directions, both ability routes (player species +
race token). Fixture law caught by the first run: homes are ONE star per
empire. 111 tests 0 failed. Docs: ships.md S23 L10 (surface + residues),
OPEN-QUESTIONS row CLOSED (residues documented inside the closure: init path
of first bits, twin caller pairing [unverified], no AI-AI share producer),
ledger_audit --expect drops OQ-026, STATE index mirrored both sides,
_wip_t195.md design D1-D7 + outcomes R1-R6. Gate 0 + LEDGER AUDIT OK + LEDGER
INDEX OK (open = 005/016/019/021).

LANDED t194 (2026-10-29, this session): OQ-026 RE QUESTION DECIDED
AFFIRMATIVE — VISIBILITY CONSUMER MAPPED + LIVE WITNESSED, and the t193 FALSE
ARM ROOT-CAUSED. (1) TRIGGER-A was a STALE-BASELINE false arm, not a new
sitting: size == BASE_SIZE exactly (no append since t193), mtime delta 100 ns
= t193 froze seconds-only, tail md5 differed because the 18.8 MB t193 append
invalidated the t151-era tail edge that was never re-frozen; named dir's
timeline tail = the adjudicated t=1086/13:22:12 rows; dosbox down; no new
caps. FIX ENACTED: idle_probe BASE_TAIL_MD5 -> 9054cc6c..., BASE_MTIME_NS ->
full ns 1793294532100000000, re-freeze rule documented; probe re-run prints
TRIGGER A NEGATIVE. (2) STATIC (Ghidra ascend_restored.bin, decompiles +
censuses): cosmos LIST BUILDER FUN_00028fc0 lane loop filters
rec+0x20 & DAT_00089324 (the viewer mask) — withheld lanes get no entry, so
painter FUN_000284bc never draws them (kind 0 star / 1 lane / 2 encounter)
and they are unclickable; all 5 builder call sites are cosmos repaints.
DAT_00089324 has EXACTLY one writer FUN_00021a84 (mask = idx==0xff?0xff:
1<<idx; ALSO writes X_CUR 0x7458e — t192(c) 'paired mask' weak witness
explained: same setter) and one reader (the filter). Second setter site
0x2754f = debug species-toggle cascade (AL=[ESP+0x2c]-4 bounded by
nraces@0x13b96>>16, or 0xff). STAR SIDE: builder adds stars unconditionally
(+0x16 NOT consumed there — honest negative for star-withholding-by-draw),
but star-click FUN_00028e70 gates select/lane-follow on star+0x17/+0x16 &
DAT_00006774 (data-seg twin of the viewer mask, == 1<<X_CUR measured t192(c))
— invisible star = unselectable. (3) RAM WITNESS (new
scripts/r1_t194_viewer_mask_witness.py, RC=0): 20/20 Oct-29 mid-game saves
mask@B+0x89324 == 0x01 (race-0 viewer), X_CUR==0, law 20/20, filter admits
49/58 lanes => the 9 AI-only lanes (value 6, only bit-0-free value) WERE
WITHHELD during real play. Addressing pitfall banked: 0x89324 lives in the
RELOCATED IMAGE (B+X), X_CUR in the DATA SEG (B+D+X) — mixing them reads code
bytes / zeros. (4) DOCS: ships.md S23 L9 (full law supersedes L8 'consumer
UNMAPPED'); OPEN-QUESTIONS OQ-026 rewritten (open, closure bar now = rewrite
implement+pin; residues: boot-arg value, AI-side audit); abilities.md
SA_KnowHomeWorlds/SA_KnowStarLanes justifications updated (real original
effects, disposition held until rewrite lands); docs/re/_wip_t194.md A1-A6.
Gate 0 + LEDGER AUDIT OK (open = 005/016/019/021/026).

LANDED t193 (2026-10-29, this session): TRIGGER-A = REAL MID-GAME SITTING
adjudicated + THE SHARE PATH WITNESSED + t191 PAINTER LEAD DEAD + LEDGER ROW
OQ-026 OPENED. The sitting (Oct-29 12:30..13:22, still live at session end,
game t=1086 wall-clock, 4 empires, war vs Minions) re-wrote all 20 saves.
MEASURED (scripts/r1_t193_midgame_witness.py, 20/20 saves): lane pool +0x20
census {1:160,3:80,6:180,7:220,11:260,15:260} of 1160 recs — 100/1160
MULTI-BIT => FUN_00046354's OR-share HAS fired in normal play (t192's
new-game zero-witness negative superseded); per-empire fog bit0 9 / bit1 8 /
bit2 25 / bit3 32 of 58; value 6 lanes = AI-only-visible EXIST; star twin
+0x16/+0x17 multi-bit witnesses too; masks md5-STATIC across the window
(4ca8c5c6/99522cd0 — no grant inside it). SUPERSEDED: t192's
LIST=={mask==1<<r} law FALSE mid-game (0/80) — per-race [sub+0x2c] lists are
OWN claimed lanes (cnt=2, second entry always a t190 bridge lane 50..57),
strict subset of the visible pool. rec+0x21 NOT all-zero mid-game {0:720,
1:440}, not a function of +0x20 (writer still open). STATIC: FUN_00020c48 =
ALLOC WRAPPER (FUN_00077b40/FUN_00077b47), the 0x25aa2 loop lives in
FUN_00025604 = game-state SNAPSHOT serialiser (lane pool, diplo rows 0x1ee
x100 dwords, star refs) — the t191 'reader = lane-paint loop' claim is DEAD;
imm-operand census over 98,819 instrs: 4 TEST + 18 CMP byte/dword [reg+0x20]
hits, ZERO lane-pool-scoped => consumer UNMAPPED. Ledger: OQ-026 visibility
layer OPENED (audit default updated); abilities.md SA_KnowHomeWorlds /
SA_KnowStarLanes NO-OP JUSTIFICATIONS corrected (the t192 false-of-original
parenthetical is gone; disposition stands pending OQ-026); OQ-019 STATUS
t193 appended — its st4 residue NOT falsifiable in this window (2238 st4
samples, zero mid-turn displacement, turn never advanced). Banked: ships.md
S23 L7+L8; docs/re/_wip_t193.md F1-F4 (incl. the resumed-game window-method
caveat + idle-probe baselines re-frozen at 5,721,578,066/13:22:12).
Gate 0 + LEDGER AUDIT OK + LEDGER INDEX OK.

QUEUE AFTER t193 (authored by the pairing session 2026-10-29; user has NO
gameplay or rulings available — everything here must be offline-static,
corpus-based, rewrite-side, or vision-on-external-images. t193 NOTE: the
NEXT ACTION above (visibility consumer = OQ-026) OUTRANKS this queue's
"t194 vision oracle" — the queue item re-queues after OQ-026 is decided;
OQ-026 is decision-bearing for the rewrite, the sheet work is not):

  t194 RESIDUE TRIAGE VIA VISION ORACLE (OQ-005 forward motion, no eyeball
  needed for IDENTITY — codec-correctness grading stays R13-reserved):
  render ALL 71 residue records with the corrected 6-bit palette (extend
  scripts/r1_t182_pngdump.py or write r1_t194_sheet.py reusing it), pack
  ~4 LABELED contact sheets (record name under each tile, failure-class
  grouped), then vision_analyze each sheet (proven recipe: layout, verbatim
  text, "what game-screen does each tile belong to"). Bank per-record
  identifications to docs/re/shp.md S20 + work/r1/shp_png/ids.tsv. GOAL: any
  residue identified into a known screen gives that screen's geometry as a
  dims candidate — that is the OQ-005 dims-location route arriving WITHOUT
  play. Flag any tiles matching the 10status/2savegam/4loadgam style cluster
  (still-unseen SVGA question).
  t195 OQ-021 DISPLAYED-COUNT WRITE SITE: DAT_482fb oscillates 12..22 while
  systems_any=36/full=34 are flat (t188b measurement, ships.md/score.md
  cite). Find WHO computes it: t191 method — runtime-slot member search in
  the 20-sav corpus (NOT static file dwords), then disasm the writer chain;
  candidates: per-star percent-controlled aggregate, production-weighted
  count, recompute-only-on-screen-open. Tie the oscillation to a loop or
  bank the narrowed chain as honest residue.
  t196 PER-PLANET ECONOMY FIELDS + GAUGE LIBRARY LAW: planet UI top strip
  CORRECTED (player 2026-10-29 twice + vision x3, shp.md S19 t193 UPDATE):
  FIVE panels L->R research / manufacturing / prosperity / population /
  current-project; the four gauges are EVOLVING SHAPES (no fill bars):
  research lattice->crystal ~60 levels (planres.shp), prosperity sprout->
  flowering plant (planpro.shp), manufacturing 'increasingly convoluted
  factory' (planind.shp — its 13 SPAN-UNDERSIZED residue records are NOW
  LIVE UI ART: dims-location evidence sits in this library, OQ-005
  priority!), POPULATION PANEL LAW (player 2026-10-29, shp.md S19): slot
  array sized to planet CAPACITY; uncolonized = empty circles; free pop =
  yellowish figure facing FORWARD, busy pop = reddish figure facing
  SIDEWAYS; shots corroborate (12-57-35 mostly busy + 1 idle). Slot-icon
  library UNIDENTIFIED — candidates planets.shp (55 recs) / planal00..10
  (11x5 — 5 could be the pose set); NOTE planitem.shp
  40 recs is probably the CURRENT-PROJECT item art (name + item-image in
  that panel), verify both by rendering, don't assume. All three named libs header dword[1]=21
  [unverified record count]. Legs: (a) render EVERY record of planres/
  planpro/planind/planitem (reuse r1_t182 machinery, corrected palette),
  order ladders visually against the player's descriptions, bank
  level->record select law + per-record ids (work/r1/shp_png/ids.tsv +
  shp.md S20); (b) census per-planet records in the .SAV corpus for the
  research/manufacturing/prosperity/population level fields driving those
  gauges, pin offsets with citations to docs/re/economy.md (create if
  absent; check nothing regenerates it); (a2) DERIVE THE VISUALIZATION LAWS
  FROM THE BINARY (user directive 2026-10-29): find the planet-screen paint
  routine that selects gauge records by level + fills population slots by
  capacity/free/busy — player testimony = hypothesis, the paint routine =
  the citation (level->record map for planres ~60-levels-vs-21-records,
  prosperity/industry select, slot-fill rule, idle-vs-busy branch);
  (c) cheap sub-leg: hunt the DAY
  COUNTER dword near the TURNADVANCE path (watcher schema lacks one;
  two-tier-turn testimony untestifiable without it — if found, note watcher
  field addition for next live session).
  t197 REWRITE ALLIANCE STATE (pure code): verify rewrite/src/game/
  diplomacy.cpp implements the now-corroborated law (att > ACCEPT_ALLIANCE
  -> BOTH cells = 3, +10/+10 both cells; refusals leave cells at 1), and add
  a regression pin using the t1335 capture as fixture sequence: atti0
  526/529/532/535/566/569 refuse -> 631 ACCEPTS with both cells 3. Cite
  docs/re/diplomacy.md S15/S16 + the flip frame wall 23:47:43. Gate + tests
  must pass.
  t198 AI GAP ROWS 3+4 (docs/re/ai-dossier.md gap map): threat-byte input
  + emergency chain (period tiers 200/225/300/400) and the min-REQUIRES/
  over-pop demolish channel in rewrite buildPhase. Split into t198a/t198b if
  context pressure appears; bank law citations from aicode.md S3a first.
WATCH-ONLY (need the user's future play — DO NOT burn iterations on these):
OQ-021 end-ctrl firing (colonize past ~50% + press `c`); OQ-019 single-ship
flight straddling the /160 clamp + a magnetron USE frame; OQ-005 the player's
remaining index.txt ruling; day-tick observation post-watcher-field-addition.

LANDED t192 (2026-10-29, this session): TRIGGER-A RE-ARM ADJUDICATED
(stale baseline, NOT new play) + THE LANE-VISIBILITY SHARE LAW CLOSED WITH
MEASUREMENT (ships.md S23 L6; debugflags.md t192; OQ-019 STATUS t192
appended, row stays OPEN on the live-st4 residue). Trigger A armed on
timeline growth (baseline Oct-26 15:44 vs 5,702,731,088 B / Oct-29 00:12:44;
the named dir playcap-20261014-224611 is stale — growth is in the SHARED
timeline). Adjudicated the NEW BYTES EXACTLY (scripts/
r1_t192_window_adjudicate.py RC=0: 280 entries, 178 trusted rows, turns
1131..1335, wall 23:28:02..23:58:42, states outside enum NONE, only
transition = the banked t1335 Chamachies<->Orfa 1->3 ALLIANCE): the growth
IS the Oct-28 night sitting already consumed/banked (diplomacy.md S15/S16,
OQ-023 CLOSED at t189b) -> no ledger row moved; r1_idle_probe.py baselines
RE-FROZEN to the adjudicated state (the probe's own re-freeze clause; six
iterations had re-armed on consumed bytes). t192 legs: (a) FUN_00046354 =
MUTUAL LANE-VISION SHARE between empires' diplo rows (party masks
1<<byte[row+0] / 1<<byte[0x12e16+0x1ee*p2] -- t191's 'contact column'
hypothesis DEAD, 0x12e16 = diplo-row table base, 60.sav rows hold empire
idx 0..4), N = rand%(state==3?6:3)+1 grants/call = ALLIANCE DOUBLES THE
BUDGET; raw listing (not decompiler -- EBX-incoming vs EBX-counter
conflation at 0x4635f/0x46402); callers 0x45778 EBX=0 bidirectional
(alliance-formation block) + 0x55f6e EBX=-1 receive-only per-race event
loop, party-1 = current player; star twin FUN_00046524 (mod 4/2, star-obj
+0x16/+0x17). (b) MEASURED 20/20 saves (scripts/r1_t192_share_mask_scan.py
rev2): per-race list [dword(0x12e1d+0x1ee*r)+0x2c+4*i], i<u16[sub+0x44] =
EXCLUSIVELY lane-pool recs (220/220 mod-39 congruent, 0 star, 0 other) AND
race r's list == EXACTLY {lanes with rec+0x20 == 1<<r} (100/100 lists);
pool +0x20 census {0:940,1:40,2:60,4:40,8:40,16:40} -- all single-bit =
share path ZERO witnesses in the new-game corpus (honest negative; needs a
mid-game shared-lane save). (c) paired mask byte member B+0x82bb0+0x6774
(payload 0x21aa6 = 88 15 74 67 00 00; DAT_00089324 IS payload 0x6774 --
rev1's B+D+0x89324 read was a DOUBLE-OFFSET error caught by race-name
validation at B+D+0x74590) == 1<<[0x7458e] 20/20, WEAK (idx==0 all saves).
CAVEAT BANKED (t191 stickiness now CONDITIONAL): 0x22e60 DOES clear
rec+0x20 via the per-race list (FUN_00022ce4, single caller 0x2271e in
FUN_000226e4; 4 xrefs 0x2142e/0x214b0/0x24f8f/0x52cb6 all read as setup/
new-game paths -- mid-play firing UNMEASURED); sticky law stands for the
cheat/share writers (no inverse of 0x273ca/0x463eb/0x46421). FLAG BANKED:
abilities.md's 'no fog of war (UI draws every star)' parenthetical is FALSE
OF THE ORIGINAL (rec+0x20/star+0x16 exist and the paint loop copies them)
-- FILED NO-OP disposition may stand (rewrite has no visibility layer) but
the justification needs correction; consumption-side question queued t193.
Ring note: 20 distinct Memory blobs, ship count 0, [0x7458e]=0 -- the ring
is title-screen/new-game states only; no 0-loss pair in the ring =
stickiness NOT falsifiable there. Gate 0 + LEDGER AUDIT OK. WIP:
docs/re/_wip_t192.md.

LANDED t191 (2026-10-29, this session): THE 'l' STAR-MAP REVEAL CHAIN
CLOSED WITH CITED MEASUREMENT (debugflags.md t191; ships.md S23 L5 CLOSED;
OQ-019 STATUS t191 appended, row stays OPEN on the live-st4 residue).
Adopted the prior killed session's uncommitted WIP (Findings 1-2 banked;
its regex census had MISSED the 80/7 and 83/r compare forms — corrected).
Proved: (a) the t85f "keymap" region 0x798de..0x79d26 is a vprintf
format-spec engine — ALL t85f leaf addresses REJECTED; every 'l'/'L'
compare immediate in the payload is a printf LENGTH MODIFIER
(0x79694/0x796b4/0x7a4b1/0x7a4bf cmp CL,h/l/L/L); (b) THE REAL DISPATCH:
cosmos-window message handler image 0x26b34, RUNTIME slot member 0x247adc
holds P0+0x26b34 (60.sav, B=0x1bf4d8 — pointer law pointer==P0+X; the
static hunt was structurally dead because the table is UNRELOCATED in the
file image: zero dwords == 0x26b34/reveal-heads); DX==3 = KEYDOWN; (c)
ECX = RAW AT SET-1 SCANCODE, cascade 0x27614..0x27669: 0x13 'R'->0x27476
diplo clone, 0x1f 'S'->0x27401 star reveal, 0x26 'L'->0x273a0 LANE REVEAL
(nougat-gated OR 1<<byte[0x7458e] into every lane rec+0x20, stride 0x27,
then repaint 0x28fc0/0x284bc/vtable), 0x2e 'C'->0x2736f score-overlay
toggle (OQ-021's `c`-press ask is now statically pinned to scancode 0x2e),
0x0c/0x0d -> zoom DAT_0009f108; (d) [0x7458e] = CURRENT-PLAYER INDEX
(writers 0x21aa0 pair-setter with DL=1<<idx / 0x0100 spectator case,
0x52cc6 new-game reset); (e) rec+0x20 = PER-EMPIRE LANE-VISIBILITY MASK:
writers 0x273ca cheat + 0x463eb/0x46421 normal-play share loop (0x46354,
semantics INFERRED flagged) + 0x22074/0x22e60/0x22f28 (base structs
UNPROVEN flagged), reader = lane-paint loop 0x25aa2..0x25b6d -> painter
0x20c48, NO lane-pool-scoped clear except pool-create 0x248ab = STICKY LAW
(player testimony matched). Method bank: search BRANCH EDGES or RAM, never
file-image dwords, for handler bindings. Gate 0 + LEDGER AUDIT OK + LEDGER
INDEX OK. WIP: docs/re/_wip_t191.md.

LANDED t190 (2026-10-29, this session): LANE-RECORD STRUCT + byte+0x23
SEMANTICS CLOSED WITH MEASUREMENT (ships.md S23; OQ-019 updated, stays OPEN
on the live-st4 residue). Intake: steering note in prompt-112 was t189b =
already landed at HEAD 6f4ad8d (tree clean) -> worked STATE NEXT; all
pre-checks negative (ring tail = turn 0 rows wall 00:12:43, dosbox down,
'sel=[1-9]' zero, DAT_482fb=2[5-9] 0). Proved: (a) lane record = 39-byte
pool rec at data-seg+0x3337 (member B+0x82bb0+0x16147, physical 0x258147
this run; rec+0/+4 = star OBJECT ptrs per allocator FUN_00024834
0x248af/0x248b1; cap 148 0x2485f; LIVE congruence: rec.b star-idx
39/29/27/16/37 all integral 20/20 saves); (b) bit0 writer census =
EXACTLY {0x247f7 OR 0x1} (bridge-lane creator FUN_0002446c; never cleared);
(c) r1_t190_lane_pool.py RC=0: nlanes=58 on 50 stars, +0x23 {0:recs0..49,
1:recs50..57} 20/20 — bit0 == BRIDGE-LANE MARKER, x1/3 gate slows the
connectivity filler lanes, and t189's fast/slow handles are pool-congruent
mod 39 (deltas 39x{5,52,56,57}) — handle==lane-ptr CONFIRMED, the S22
L4/L6 confound is resolved (no species difference needed); (d) gate2 species
col +0x12 has NO 0x12 in rows 0..23 in ANY of the 20 LIVE tables (stronger
non-witness; scenario-scoped non-claim); (e) t52 en route: ONE 100-linear
hop matrix data+0x32ddb == folded DAT_00045beb (FUN_0002351c loads authored
lanes from the SAME pool then BFS-fills hop counts; t52's "two buffers /
diagonal not 1" = wrong base window), pipeline = FUN_000234a4 {0x2351c;
loop{23e00 NN-phase; 24018+2446c bridge-phase} while components>1}; (f) the
"scenario object" == the obj0 DATA SEGMENT (every S+offset folds: S+0x2ea ==
species table 0x12fb3 exact). Side-found unattributed: rec+0x20
power-of-two field {1,2,4,8,16} (S23 L5). Gate 0 + LEDGER AUDIT OK. WIP:
docs/re/_wip_t190.md; tool work dump work/r1/t190_pool_dump.txt.

LANDED t189b (2026-10-29, this session; steering-note merge iteration):
OQ-023 CLOSED — first state-3 (ALLIANCE) event banked and INDEPENDENTLY
RE-VERIFIED this session (r1_t188_state3_arbiter.py re-run RC=0: cell0i=
celli0=3 @t=1335 wall 23:47:43, att +10/+10 615/644, 68 sustained raw rows;
flip comparator atti0=631 > Orfa 570 = the t180 static law 0x4562f/0x45641
corroborated end-to-end). Enum identity closed by OBSERVED transitions
2=WAR(t85b)/1=PEACE(t187)/3=ALLIANCE(this); engine-build residual moved to
PLAN.md A7; ledger_audit.py --expect re-triaged (t181 pattern) — open set is
now OQ-005,OQ-016,OQ-019,OQ-021. Merged pairing-session findings from
work/r1/t188b_findings.md (file DELETED after merge) into: diplomacy.md §16
(event + METHODOLOGY LAW: first-row-per-turn scripts miss mid-turn relation
writes — adjudicators must walk raw rows); OPEN-QUESTIONS OQ-021 STATUS
(score_stars 14->21 drift is REAL, not any systems count — systems_any=36/
full=34 dead flat same frames; residue refined to the displayed-count
write-site); debugflags.md ('l' caution LIFTED, player re-confirmed
2026-10-29; zero-cmp-al-'l' anomaly kept as open hunt t184); species.md
(lgraceNN = race-NN portrait law; specnum<->raceNN content-VERIFIED at 7/9/
10 = Swaparamans/Shevar/Govorom); shp.md S19 (6-bit palette darkness bug was
OURS — r1_t182_pngdump.py load_palette() now scales v*255//63, mean luminance
lgrace10 29->125; player verdict all-15-real, residue NOT junk; 10status/
2savegam/4loadgam + planpro/planres style-anomaly note kept open — do NOT
delete on non-recognition). t188b §7 (flight-delta ladder 14/3,14,28) was
already banked by iter-111's t189 ships.md S22 — no double-bank. Pre-checks:
no new turns past 1335 (ring = t=0 new-game rows, dosbox down) -> t85g
re-run not triggered; NEXT t190 (lane-record byte +0x23 writer) stands
unchanged, lane hunt stays queued behind nothing — it IS next.

LANDED t189 (2026-10-29, this session): LANE-STEP WORD MAPPED — FUN_0004a74c
IS THE STATE-5 LANE MARCH BODY (ships.md S22; OQ-019 updated, stays OPEN
strict-close). Intake: pre-checks all negative (no turn>0 past 1335, sel
never armed, DAT_482fb=2[5-9] 0, dosbox down); adopted+committed prior
residue 87dcab9 (game.pal = 6-bit VGA, re-measured: max byte 0x3f, 0/256
entries over; pngdump was rendering at 25% brightness — fix scales
v*255//63; plus t187 session + t188 state3 arbiter scripts). Proved
(disasm 0x4a74c..0x4a968 verbatim + r1_t189_lawcheck.py RC=0): march =
chord advance x := min(x + step, |A-B|) at [ship+0x9e], y/z untouched
(pure-x law STRUCTURAL); step base = float(ship[+8]+ship[+0xc]) — the
words measured (14,0)/(0,28): S21's 14/28 ARE RECORD FIELDS, not
MOVES-derived (every consecutive st5 delta == step0 or step0/3, ZERO
exceptions); gate1 byte[handle+0x23] bit0 -> x moffs 0x263b POOL WORD
LIVE 0.333333 all saves 41..60 (THE 1/3 IS RUNTIME, handle-gated);
gate2 species (dword[+0x54]>>16) row col 0x12 == 0x12 -> x2 (moffs 0x263f
word = 2.0; branch construction assigns the words) with max(step,1) clamp
at 0x4a87c, ZERO observed witnesses.
Handle law in play: SLOW only under handles 0x258933/9cf/9f6 (254 pairs,
zero fast), 15 other handles all fast; slot13 vs slot17 SAME owner,
records byte-identical 0x00..0x27, opposite speed — t188's "+0x52 route
handle" SUPERSEDED (+0x52 is the ETA stamp; +0x59 is the lane pointer).
Identity tie: the function prologue IS t101's POWER-recharge site
(0x4a76c) — explains S21's "POW frozen" (refill lands before autosave
row). Residue -> t190: byte[handle+0x23] writer/semantics + species
table col 0x12 identity. Gate 0 + LEDGER AUDIT OK. WIP:
docs/re/_wip_t189.md.

LANDED t188 (2026-10-29, this session): TRIGGER A RE-ADJUDICATED + FLIGHT
SCALE/FRAME LAWS BANKED (ships.md S21; OQ-019 row status updated, stays
OPEN on strict-close). Intake: sitting re-run RC=0 (45227 trusted rows,
work/r1/t188_sitting_dump.txt) — NO new real turns; the +2.9MB growth is
the player's NEW GAME saving into the same ring (t=0 rows; campaign star
table OVERWRITTEN, do not expect old-map reads); dosbox not running.
Pre-checks all negative (sel never armed, DAT_482fb stuck 21/50, no cell
3; Orfa old-game att crossed 570 at t1285 unattended -> 613@t1335 with NO
alliance: t187's proposal-extrapolation is now a MEASURED non-event).
Proved this iteration (tools r1_t188_speedword.py RC=0, words dump, frame
probe): (a) st5 lane march is NOT the T1 walk law — MOVES+0x94/FUEL+0x88
frozen every turn of the march (measured-negative, 20+ rows); (b) lane x =
k*step exactly from lane entry, steps {14, 28, 14/3} to 4dp; (c) STEP IS
LANE-SCOPED NOT SHIP-SCOPED — one ship (slot13) marched 14 on z=±1824 and
14/3 on z=544 with identical d10/MOVES/POW; slots 13 vs 17 differ only in
the +0x52 route handle among all stable words; (d) st5 coords are LANE-
LOCAL (y exactly 0/1, z multiple of 32 outside star extent ±402 live-read)
— the 1100-2500u "discontinuities" are the state/frame switches (25/27
big rows are 5<->4 flips), magnetron EXONERATED (jitter would break the
observed 32-grid st4 positions). Residue -> t189 static hunt. Gate 0 +
LEDGER AUDIT OK. WIP: docs/re/_wip_t188.md.

LANDED t187 (2026-10-28/29, this session): TRIGGER A WAS REAL AND THE
PLAYER IS FLYING SHIPS. Live at launch: dosbox pid 260973, timeline
+2.47MB, turns 1255->1335 during the session (dir named by trigger
playcap-20261014-224611 = stale Oct-14 all-turn-0 dir, NOT the ingest;
shared work/r1/playcap is). Adjudication (r1_t85g_sitting.py RC=0 +
r1_t187_delta.py RC=0, 45140 trusted pts): (a) FIRST state-4 rows ever
observed x1115 (state5 x584) — t49/t58 zero-flight corpora argument
SUPERSEDED, ships.md S20 banks the raw regularities (14/28/56-u lane
steps vs MOVES 6/12; 4.67=14/3 owner-1 steps; frame-reframe ambiguity
flagged); OQ-019 residue capture IN HAND, law extraction queued t188.
(b) FIRST 2->1 WAR->PEACE transition banked (diplomacy.md S15); state 3
still UNOBSERVED (honest negative, row open) BUT Orfa AI-side attitude
drifted 526->535 unattended (+3/~3-4 turns) — extrapolated 570 crossing
~t1295-1300; PLAYER ASK: propose alliance when high. (c) OQ-021: new
DAT_482fb highs 16 then 21/50 with systems_full=34/50=68% and selector
still never armed in ANY trusted row (score.md S8) — boundary is 4 units
away, passive test continues. (d) mid-turn POWER burn now census-observed
for all three AI owners (live corroboration of the t183 round-robin min-
fuel law). Dumps archived work/r1/t187_{sitting,scale,delta}_dump.txt.
Gate 0 + LEDGER AUDIT OK + LEDGER INDEX OK. WIP: docs/re/_wip_t187.md.

LANDED t186 (2026-10-28, this session): THE IDLE GATE WAS ARMING ITSELF —
diagnosed, fixed, pinned. Trigger A re-confirmed NEGATIVE from the report
(timeline mtime_ns/size == baseline, no dosbox procs; NOT re-probed, t178
rule). Trigger B was a FALSE ARM and structurally so: loop_one_task.sh:135-143
embeds `cat probe-last.log` in every prompt, so prompt-N contains prompt-(N-1)'s
report; the report's "HEAD:" line is the loop's own commit SUBJECT and digit-
stripping (r1_idle_probe.py:498) kills digits, not prose; :515 armed on any
surviving delta. So: loop commits -> subject changes -> next report differs ->
B2 arms -> loop launches, forever. Pair 107/106 delta was literally t184's own
subject, beside the same report's "B3 HEAD == journal sha 5aed299: no commits
outside the loop". Tree fully clean, no STEERING/LOOPSTEER, no foreign paths —
MEASURED this session, not assumed. FIX: B2 diffs only human-authored regions
(contract + STEERING); whole-file delta is a diagnostic line ("report echo /
loop noise -- NOT an arm"). PIN: scripts/r1_t186_b2_regression.py RC=0 —
replays all 107 pairs: old 13 arms -> new 5 (15/17/23/24/99 are real contract
edits: t178-rule insert, BANK-EARLY insert, blank-line noise), 8 flipped to
IDLE = exactly polls 101-108; asserts every ignored delta line provably lies in
a loop-authored region; SKIPs rc=0 if the prompt history is rotated; wired as
gate stage 3u. Live re-run post-fix: B2 prints "human-region delta 0 line(s)"
and the residual arm is my own mid-iteration untracked regression script under
B4 (scripts/ is outside LOOP_OWNED) — disappears at commit. Nine sessions were
burned on this feedback loop (t178-era idle re-checks); the honest negative is
banked in docs/BLOCKED.md t186 with the authorship-segmentation law. No OQ row
moved and none could: queue empty. Gate 0 + LEDGER AUDIT OK. WIP:
docs/re/_wip_t186.md.

LANDED t185 (2026-10-28, this session): OQ-019 MAGNETRON IDENTITY CLOSED
WITH CITED MEASUREMENT (row stays OPEN — flight-delta residue only).
Ships.md §19 is the artifact. (a) LOADED DESIGN TABLE == FILE ORDER:
76/76 gizmos.txt name matches at B+0x82bb0+0x7650c+0x6a*g across 1368
save members, ZERO mismatches (scripts/r1_t185_magnetron_census.py RC=0).
Immediate 0x24 at 0x4159a = RECALLER (gizhelp.txt:695-699 help tag
gizmo36), NOT Disarmer — t183's row map was off by one (Disarmer=37,
Magnetron=60); slot census across saves: cidx36 x129, cidx60 x360, ships
carry both. The FUN_00041260 branch is an emergency auto-recall (0x49768
scan -> kind 5 -> 0x49f28 -> 0x4cd90 case 0x24 -> 0x220a8+0x21f58,
already in combat.md §(a)). (b) MAGNETRON USE-SITE FOUND: FUN_0004ca50
(kind-2 target dispatcher, called from 0x4a3ac) case cl==0x3c at 0x4cd5c
— gate Range*32 >= lane-dist + design flag word bit1, Power burn into
+0x88, placement 0x4cd0d 0x220a8 + kind5 + 0x4cd1f 0x21f58, slot rebuild
0x4cd3f 0x496e4; 0x4a360 guard 0x4a373..0x4a390 decs slot use-word iff
design[+0x42]!=0 (col5 semantics NOT re-derived — flagged). 0x21f58 body
fully read: star triple + f32 DAT_00000aee (LIVE -200.0 MEASURED at
B+0x82bb0+0xaee; static payload bytes there are code, t43 law again) +
TWO rng%200 draws (0x7824f LCG, idiv 200) added to the other two axis
slots, commit 0x49aa8, kind 5->4. §16 item 3 tie now MEASURED; §17-T6
paragraph marked SUPERSEDED. Corpus phrasing corrected: t184's fleet
corpus = 1234 rows over 49 FILES (empty-scenario probe boots are
headless thread runs, not corrupt saves). Tooling lesson: census slice
m[a:m[a+0x40]] is a byte-value end — grep your own slices when a
"76/76 empty names" anomaly appears next to a tool that reads fine.
Gate 0 + LEDGER AUDIT OK. WIP: docs/re/_wip_t185.md.

LANDED t183 (2026-10-28, this session): OQ-019 SCALE MEASURED + TWO-TIER
TURN CODE-MAPPED (row stays OPEN — strict-close; live flight delta still
missing). Ships.md S17 is the artifact. Headline numbers [MEASURED 20/20
playcap saves]: travel body FUN_00049f54 walks min(d_world/160, MOVES
[ship+0x94]) SUGAR-CUBE units per resolver call; steps = max(1, round(walk))
capped by fuel [ship+0x88] (fuel burned == steps); per-step displacement =
unit_dir * (walk/steps) * 32.0 * 5.0 (const pool read LIVE IN SITU via the
save's own FLD-moffs operands: 1/160 @RVA 0x25ff, 32.0 @0x2603, 5.0 @0x2607;
data-slot law m = VA + 0x88, code-slot law m = payload_off + P0 — both
re-verified). Grid quantizer FUN_000533e0 DAT_000895dc = 32 (20/20); live
corroboration 23/35 ships exactly on the 32-grid, all 12 off-grid ships are
mid-transit kind-2 orders. ROUND-ROBIN: turn loop FUN_00024f24 (turn u32
++ at end, sole caller 0x55f06) -> 0x25400/0x255a4 -> FUN_0002547c sweeps
until no resolver reports work; FUN_00041260 picks per call the MIN-FUEL
ship with an order and refills MOVES to drive-stat sum (0x3ea08 <- 0x412d4).
DAT_00012e10: 41 xrefs, ZERO obj0 writers -> no autonomous day-tick in
obj0 code (R12: no byte-scan). LANE TRANSIT = same walk law gated by
lane-matrix DAT_00045beb -1-gradient hop choice (verified, FUN_00041260
case 1). KIND-5 emergency branch (0x4159a, slot-index immediate 0x24) is
NOT the Lane Magnetron — index-36 == Disarmer by t46 file-order law, slot
census 15/35 carry idx36 / 0 carry idx59; S16 item-3 magnetron tie stays
UNMEASURED (corrects this session's mid-run overreach, caught by census).
Tooling lesson: Ghidra headless load_program(work/ascend_restored.bin)
after scripts/ghidra_headless_up.sh + connect_instance(ascend5) — project
work/ghp5. Gate 0 + LEDGER AUDIT OK. WIP: docs/re/_wip_t183.md.

LANDED t184 (2026-10-28, this session): OQ-019 BUILD/REDESIGN INVENTORY
PATH CLOSED WITH CITED MEASUREMENT (row stays OPEN — flight-delta residue
only). Ships.md §18 is the artifact. Law: gizmo ring rec+0xab stride 7 x25
physical slots {cidx u8 (0xFF empty), u16, u32}; CAP dword[+0x15a] :=
dword_live(0x6842+2*hull)>>16 (hull = byte3 of design ptr dword[+0xa7]) —
MEASURED EXACT 1234/1234 owned rows 20/20 saves (tool
scripts/r1_t184_inv_law.py RC=0; table is scenario-loaded, static image
bytes at 0x6842 are code — t43 law re-confirmed); FILLED dword[+0x15e] ==
occupied count over slots 0..cap INCLUSIVE incl. a MEASURED vendor
phantom-slot off-by-one (100 rows, 4 designs, slot idx==cap occupied,
missed by every i<cap walker — 0x49698 bound is jg). Commit = explicit
per-slot cidx adds (production builder FUN_00040358 jumptable cs:[cls*4+
0x2b798] starter kits; design-apply FUN_00040d1c race-filtered RNG-shuffle
over DAT_0x67ec; UI FUN_0004dd50 0x4e425/0x4e4f9) then FUN_00049acc
RE-MATERIALIZE sums (no gizmo record copy ever; supersedes t46 §10's
"queued-order list" label on the ring). Redesign FUN_000497a8 REFUSES iff
new-hull cap < filled (0x497da). Init side-law: integrity [+0x8c]=(hull+1)
*10 doubled if war byte DAT_00012fb3+emp*0x1ee==1; player-designed ships
skip the hull-name copy. Gate 0 + LEDGER AUDIT OK. WIP: docs/re/_wip_t184.md.

NEXT t185 (SUPERSEDED by t185 LANDED above — was DONE this session;
STATIC, LAST FULLY-OFFLINE CANDIDATE): OQ-019 magnetron identity
+ the two §18-adjacent loose ends folded in ONE pass — (a) enumerate what
gizmo category 5 (the kind-5 go-to-star orders, §17 T6/§16 item 3) rows
EXIST in the scenario-LOADED gizmo table live copy (base law t47:
B+0x82bb0+0x7653c), names via the loaded name-pointer table, and re-run the
slot census against the LOADED rows not file order (t183 refuted the file-
order tie; the loaded table may name row 59/idx-36 differently per
scenario); (b) if a loaded row is named Lane Magnetron, cite the row-index
law linking it to immediate 0x24 at 0x4159a. RATIONALE: after t184 the
only OQ-019 residues are flight-delta (BLOCKED t48 — capture window) and
this identity question; every other open row needs a capture or the player
(OQ-005 eyeball index.txt, OQ-016-tail, OQ-021, OQ-023 per t180). If the
loaded table still says Disarmer, that is the honest negative to bank and
MAGNETRON-TEXT vs CODE stays a documented vendor-contradiction, then the
offline queue is EMPTY: re-arm idle and surface OQ-005 at the decision
trigger.

(Prior LANDED t182 block follows; its NEXT/THEN paragraphs are SUPERSEDED
by t183/t184/t185 above.) LANDED t182 (2026-10-28): OQ-005 SHAPE-PNG DUMPER SHIPPED +
VALIDATOR OFF-BY-8 CORRECTION (ledger row stays OPEN — evidence packet now
ready for the player's ruling; nothing closes today). Tooling:
scripts/r1_t182_pngdump.py (run with ~/tools/revenv/bin/python — PIL only
there) + C++ driver tools/shp_pngdump.cpp linking rewrite/build/
libascend_core.a, so every plane comes from the rewrite's OWN
ShapeLibrary::decode (which gained an optional bool* swapped out-param;
110 tests 0 failed, no behaviour change). Output work/r1/shp_png/: 15 PNGs
all self-validated (5 CONTROLS spanning size classes 10x11..639x479 incl.
3 S17-RAM-verified libs; 10 RESTORED — see below) + index.txt (CONTROLS
first, residue grouped by class; palette game.pal labelled UNVERIFIED).
Core measured finding (docs/re/shp.md S18): scripts/r1_shp_unifiedlaw.py:49
k==0 V-trial walked the stream from rec while its own docstring, shp.md S16,
the S17 live-RAM table law (sel0 -> rec0+8), and shp.cpp:106 all say rec+8.
A/B over 208 libs same-function: promoted EXACTLY 10 k==0 records (10status/
2savegam/4loadgam rec0 639x479, planpro/planres 107x99, smship11 45x30,
smship15 39x6, lgrace07/09/10 296x199), DEMOTED zero of 187; all 10 render
canonical (swapped=0). Corpus after fix: V 197 + A 1289 + FAIL 71 = 1557,
libs clean 186/208 (was 176). Genuine residue corrected 80/31 -> 71/28
(planind 13, 3cfgnew 13, cos_star 12, stragglers 46; 3cfgnew rec0 re-
verified still-failing from rec+8). Pipeline proof via vision pass on the
OUTPUT (tool sanity, NOT OQ closure — R13 stands): dkship20 rec3 = coherent
ship art; 10status rec0 = legible "Empire status" panel. Banked: shp.md §18,
OPEN-QUESTIONS OQ-005 STATUS t182 block, BLOCKED t68 amended count, ledger
index unchanged (OQ-005 still open — correct). Gate 0 + both ledger checks.

THEN t185 (DEFERRED — user hold, t179c): the `l` star-map key route. Player
reports the original observation may have been key-mashing error; hold until
the player re-tests live. Evidence so far: user testimony t85f + b-sting page
("All starlanes exposed", OR-sticky); ZERO cmp al,'l' sites in image. If
re-test confirms, resume (scancode 0x1e paths, dispatch tables near
0x79950..0x79c20); if refuted, mark both sources corrected in debugflags.md.

IDLE RULE (t178) still stands for everything else: the harness polls in shell;
a model session runs ONLY on armed trigger, dirty tree, or human queue
(LOOPSTEER.txt / FORCE_RUN). Capture triggers re-arm the menu below.

WHEN A CAPTURE TRIGGER ARMS, the menu (docs/re/stop-report.md §2, t110):
  - OQ-021: colonize past 50% of stars with the autosave ring running, or
    press `c` on the starmap with nougat.lf armed — prints PERCENT CONTROLLED
    = the comparator's own formula output.
  - OQ-023: needs one matrix cell holding 3 (Alliance). PRECISE PER t180
    (docs/re/diplomacy.md §13.2/§13.5 — do NOT re-scan statically): raise the
    target above ITS OWN ACCEPT_ALLIANCE (per-race, §8; Orfa=570 was the
    binding number in the banked campaign, proposals only give +39), then
    propose. Expected signal: BOTH cells -> 3 with +10 attitude each; DA 10
    becomes selectable against any empire the acceptor is at war with. Run
    scripts/r1_t85g_sitting.py on the new ring.
  - OQ-019: needs real FLIGHTS only now (two zero-observation corpora
    t49/t58 prove no offline route; inventory path closed t184, magnetron
    + recall consumers closed t185, scale t183) — consecutive-save flight
    delta pins arrival granularity. A Recaller-triggered jump in the ring
    is itself a bankable observation (0x4159a auto-recall law).
  - OQ-016 tail: per-cell terrain/nuke wiring, same class (stop-report §2).
    (OQ-003 CLOSED t181 — nothing capture-side left on that row.)
  - A battle in the same sitting additionally banks slot-diff damage evidence
    (strengthens OQ-019 caveats at zero protocol cost).

WHEN A DECISION TRIGGER ARMS (user wrote into the repo / LOOPSTEER), the open
decision list (stop-report §3): accept/reject documented defaults for rows
static-only can reach; authorize new capture sittings; t89a-scale code work
resumption if strict-close relaxed.

## HISTORY

Full per-turn log of the v2 era (t1..t177 LANDED blocks, 2026-10-26..28,
including the 64 idle re-checks this file no longer carries):
archive/state-v2-full/STATE-full-2026-10-28.md. Syntheses that matter live in
docs/re/stop-report.md (loop status), docs/re/*.md (laws, per address), and
docs/OPEN-QUESTIONS.md (closure evidence). This file carries only the live
control plane: ledger index, in-hand tools/laws, one next action.
