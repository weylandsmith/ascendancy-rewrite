# STATE — machine-readable working memory for the closeout loop (v2)
# Update EVERY turn. A fresh session must be able to resume from THIS file alone.
# v1 history (full turn log 2026-10-03..2026-10-05l): archive/ralph-v1/STATE.md
# Patch discipline inherited: ONE patch per region, read_file verify after
# (multi-patch batches mangled v1 twice).

phase: P7-closeout
milestone: 6  # keep 6: gate.sh keys build/test/boot stages off milestone >= 3; lowering it silently guts the gate
updated: 2026-10-29T01:55
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
    - "OQ-001 .cob offsets = N not N+1"
    - "OQ-002 FLIC codec (both vendor videos, golden-pinned)"
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
      dark-zone enumeration (t73b); capture fallback. Default >1/2 stands"
    - "OQ-023 dip third-party/trade branch — RE residual OPEN: nonzero
      relation-state ENUM semantics (which of 1/2/3 = war vs allied; idle
      corpus holds ONLY 1, no injected transition), same closure class as
      OQ-021 (interactive original session). Two-party main-branch law itself
      MEASURED diplomacy.md 7/8/9 and implemented; the ENGINE build for
      TRADE/third-party offers is separate build work, not measurement"

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

NEXT t189: MAP THE LANE-STEP WORD IN CODE (close the S21 residue, OQ-019).
The Ghidra bridge is ALIVE (verified t188: instance tcp 127.0.0.1:8089,
program ascend_restored.bin connected) — do the static leg NOW while it is
up. Task: find WHO computes the per-turn lane displacement for state-5
orders: start from the resolver FUN_00041260 (t183 law) and the order-kind
dispatch, find the st5 (kind-5 order / lane) branch that writes the ship
position per turn WITHOUT calling FUN_00049f54 (walk) — the measured corpus
(S21 items 1-3) proves that path exists and reads a speed value scoped to
the +0x52 route/target handle (steps {14, 28, 14/3}: look for a /3 or *
0.3333 const-pool word and a lane-record field read through the handle).
Pin the offset + citation into ships.md S22. Row CLOSES only if the step
AND its divisor are tied to named record fields with cited disasm
(strict-close); the honest output if not is the narrowed writer chain.
PRE-CHECKS first (cheap greps, may override): (1) if
work/r1/playcap/live-timeline.jsonl has REAL new turns again (turn > 0
rows past 1335 — the tail is currently the NEW GAME: 172 t=0 rows, ring
overwrote the campaign star table; run r1_t85g_sitting.py only if A
re-arms with content change AND turn>0 rows appear); (2)
`grep -o 'sel=[1-9]' work/r1/playcap/watch.out | head` and
`grep -c 'DAT_482fb=2[5-9]' work/r1/playcap/watch.out` — OQ-021 override;
(3) any relation cell==3 (OQ-023) — note the OLD game ended at t1335 with
Orfa att 613 (past the 570 extrapolation, NO alliance observed: honest
negative banked; a NEW alliance must come from the new game at t=0).
RATIONALE: every capture-gated closer is watching-only; the lane-step word
is the ONE open question with a static path, and the bridge being up is
time-sensitive.

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
