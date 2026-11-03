# STATE — machine-readable working memory for the closeout loop (v2)
# Update EVERY turn. A fresh session must be able to resume from THIS file alone.
# v1 history (full turn log 2026-10-03..2026-10-05l): archive/ralph-v1/STATE.md
# Patch discipline inherited: ONE patch per region, read_file verify after
# (multi-patch batches mangled v1 twice).

phase: P7-closeout
milestone: 6  # keep 6: gate.sh keys build/test/boot stages off milestone >= 3; lowering it silently guts the gate
updated: 2026-11-03T05:55
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
      write-site is now the residue. t212 STATUS: write-site static route
      EXHAUSTED — aicode P7 producer claim REFUTED (writes word[0x48300],
      not the displayed dword); zero writer across disp32+imm census,
      decoder-free raw scan (fb 82 04 00 = 4 hits, all accounted), RAM
      pointer scan (all relocated operand fields), 145-base [reg+disp]
      trace. Writer = runtime-computed-address class -> dosbox-x write
      watchpoint, same session as the comparator-firing ask. score.md S9."

## WHAT IS IN HAND (tools + laws — a fresh session starts here, not from scratch)
- CONTROLLED-SYSTEMS LAW (V = DAT_000482fb) CLOSED as a mechanism t284 and
  REPLAYABLE: scripts/r284_vreplay.py [dir...] re-runs the decoded producer
  (FUN_00024274 flood from the home star, three gates per lane) against any banked
  .sav dir and prints V + the visited-lane set vs the slot's persisted marks.
  Law + citations: docs/re/score.md S18. Use it as a mine-check on any new V data.
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

NEXT t286 MCP/PTY DEBUGGER AS A GENERAL INSTRUMENT (queue order; t285 LANDED —
the drive leg self-harmed on the softlock class and the harvest leg delivered
honest negatives, so the V>=25 ask returns to the drive queue REQUIRING the
hardened driver below; ordering vs t287: the debugger is offline-safe while the
drive class keeps hitting the t285/t261 bug class every ~6-16 presses, and
characterising that class with the debugger is t288 — build the instrument
first). Script scripts/r1_wp_session.py so OTHER writer questions can be hunted
without hand-held sessions: u16@data 0x131b4 (the maintained "Planets Occupied"
snapshot, t249 residue), star byte +0x5a (colonised-planet count, t247 law —
writer unmapped), the PLANETALLOC getter chain 147/149/151/152/153
(selfplay.md) to confirm the header format-string law at runtime. Each hunt =
one scratch session (work/r1/game-wp scratch tree, OWN ring dir — two-writer
law), one address, one captured EIP. Use scripts/r1_t283_wp_session.py as the
template (settle laws banked there: 45 s post-load settle, ONE bp, BPLM fires
+3.1 s after NEXTTURN). Bank results to the relevant docs/re/*.md; a scratch
negative is still a result.

DRIVE-CLASS PRECONDITION (t285 law, docs/re/driver-selfharm-t285.md — applies
to EVERY future drive row incl. any V>=25 re-drive): the driver must (1) detect
the TITLE MENU FROM THE SCREEN before any click (probe_b fixture:
work/r1/bank-t285-flip1255/probe_b_043813.png; orange title background dominates
the game area above the white menu box at rows ~330-565), (2) treat 2
consecutive no-advance presses as STOP-AND-LOOK (bank + screenshot + flag),
NEVER probe-then-click, (3) never send Escape at the bare galaxy map — it EXITS
THE CAMPAIGN to the title menu, and the ring keeps autosaving so RAM-side guards
are blind. The ~30 genuine rows t1087-1092 are banked (bank-t285-predrive);
the drive resumes from t1086 (production is parked there, shipfp f4e5e715).

PAIRING-SESSION NOTE (phase-4 handoff, 2026-11-02 ~22:45): sentinel-slot law
stands — task line FIRST, notes below. USER GRANTS (verbatim, this session):
"Go ahead with everything. Don't worry about my save games or a VNC grabbing the
session - I'm done with the game on this box, if I want to play more I'll fire
up a session on my main PC." Consequences: (1) network fetches are authorized
(git clone worked without proxy vars; sudo still needs a password so ALL build
deps were staged sudo-free into work/r1/localprefix — source
work/r1/localprefix/autotools.env.sh for autoconf/automake/m4/curses); (2) the
Oct-29 campaign on :9 is the production corpus, RESUME.GAM md5 5b382afbb78918
(= t1086) — restore from work/r1/game/RESUME.GAM.user-oct29 if clobbered;
(3) a VNC client may attach at any time and its input is now HARMLESS to assume
for RE purposes, but keep the drive laws anyway (they're about the engine, not
the user); (4) the vendor tutorial is DISCARDED (it had clobbered RESUME.GAM;
preserved as RESUME.GAM.tutorial-nov2 for archaeology only).

QUEUE (phase 4, one session each; finish tN -> rewrite NEXT to tN+1 VERBATIM;
keep this block intact except deleting your completed row):

t286 MCP/PTY DEBUGGER AS A GENERAL INSTRUMENT (needs t282): once one watchpoint
  flow works, script it (scripts/r1_wp_session.py) so OTHER writer questions can
  be hunted without hand-held sessions: u16@data 0x131b4 (the maintained
  "Planets Occupied" snapshot, t249 residue), star byte +0x5a (colonised-planet
  count, t247 law — writer unmapped), the PLANETALLOC getter chain 147/149/151/
  152/153 (selfplay.md) to confirm the header format-string law at runtime.
  Each hunt = one scratch session, one address, one captured EIP. Bank results
  to the relevant docs/re/*.md; a scratch negative is still a result.

t287 DIPLOMACY SECOND-CAMPAIGN CORROBORATION (t279, now released): production
  live at t1086 fresh campaign; the t273 release conditions (no VNC client +
  production lineage) are superseded by the user's "don't worry about a VNC
  grabbing the session". Open ALIENDIP per race, bank disposition +
  relation-state cells vs watcher RAM rows at the same wall-second; cross-check
  the c-overlay STARS CONTROLLED line vs DAT_482fb again on a NEW campaign seed.
  READ-ONLY panels only — NEVER PROPOSE/DECLARE/ABANDON/END-TURN (t244 abandoned
  a system by accident; Escape does NOT unwind PLANETALLOC, t254). Bank to
  diplomacy.md as second-campaign corroboration (race-seed invariance test).

t288 SOFTLOCK-CLASS FOLLOW-UP WITH THE DEBUGGER (needs t282/283): the class is
  characterized (t266: modal-freeze from a second writer; t261: input-dead
  ON LOAD, i.e. the save captured the frozen state) but the ENGINE state that
  makes input dead is still unnamed. If the debugger is usable, break into a
  softlocked scratch session and dump the input-callback queue / the game's own
  input flag rather than guessing. Bank to selfplay.md §7 + flag anything that
  changes the drive SOP.

STANDING LAWS FOR EVERY ITERATION HERE (beyond TASK_CONTRACT):
- OOM LAW: NEVER read live-timeline.jsonl except r1_stream.py / <=400 KB
  tail-scan / r214_triage.py (6.4 GB; t251 session OOM-killed its whole tmux
  scope at 13.4 GB RSS).
- TWO-WRITER RING LAW (t266): a second dosbox-x on the SAME ring dir corrupts
  evidence AND freezes the game. Scratch sessions ALWAYS get their own ring dir.
- KILL BY RECORDED PID ONLY. pkill -f / pgrep -f match the searching shell's own
  command line and have killed this session's shell TWICE (t267 + this pairing
  session) — use structured argv matching (ps -eo pid=,args= parsed in Python,
  basename(toks[0]) == 'dosbox-x').
- SIGKILL a softlocked dosbox (SIGTERM pops its quit-confirm with (Yes) DEFAULT).
- Background shells need DISPLAY=:9 injected explicitly (silent xsend failure).
- NEVER loadstate a bank (input-dead-on-load, t261). NEVER replace
  /usr/bin/dosbox-x.
- Ring = work/r1/playcap/save/ (20 slots, 10 s cadence, ~200 s). Bank before
  restarts + every ~30 turns.
- Ledger: 15 closed / 4 open (OQ-005, OQ-016, OQ-019, OQ-021). Keep
  ledger_audit + ledger_index_check green; never hand-edit the index block.
- OQ-005 needs the USER's ruling on the 88-row decision sheet (t278,
  work/r1/shp_png/index.txt) — do NOT rule for them (R13) and do NOT burn
  iterations on it.
- Do NOT re-trod: t212/t213 static exhaustion; t255 screen-open (REFUTED);
  t258 candidicide (KEEPER); t259 sav-pair census (KEEPER); t262 fleet-census
  trigger (DEAD); t265 st4-dwell (t193 route dead); t269 threshold census
  (KEEPER); t272 dfsg-no-debugger (SUPERSEDED by this build — verify the NEW
  binary, don't re-prove the old negative); t273 attribution fixes (build on
  them, don't re-mine with the old buggy analyzer).
- Gate ~2-3 min; milestone: 6 stays. work/ is gitignored — findings in docs/re/.
- After the queue drains: park NEXT on a WAIT-TRIGGER sentinel (task line FIRST)
  or author a new queue; relaunch law MAX_ITERS=12 IDLE_GATE=0.

LANDED t285 (2026-11-03): DRIVE SELF-HARM ROOT-CAUSED WITH WITNESSES — ESCAPE
AT THE GALAXY MAP EXITS TO THE TITLE MENU; RING GUARDS ARE BLIND THERE; THE
NOV-1 21:38 CAMPAIGN SWAP IS THE SAME MECHANISM (docs/re/driver-selfharm-t285.md
+ _wip_t285.md; NO OQ closed — strict-close honoured, OQ-016/019/021 annotated,
ledger 15/4). (1) DRIVE 04:33:53 advanced 1086->1092 (6 presses, ~30 genuine
rows banked), then SOFTLOCK-CLASS struck (NEXTTURN at measured (511,67) dead,
no popup, drained=0). (2) The old driver's probe sent ONE Escape: screenshots
witness CAMPAIGN t1092 -> TITLE MENU (rows transcribed verbatim, incl. "Load
Game Alt-L"); probe "ALIVE changed_px=306624" was the t266 starfield false
positive; the drain then clicked two white menu rows -> the GAME'S OWN Load Game
swapped the RAM campaign: fp 3a189896 (t1086 V0 owned104, 20/20 slots) ->
39614c7c (t1255 V14 owned124, 20/20, no interleave). Press 10 advanced the
LOADED campaign -> driver printed FALSE "TARGET REACHED". (3) CORROBORATION vs
the Nov-1 incident log (drive_20261101-213051.log): identical tell sequence
(no-advance x2, probe ALIVE 306624, drained=2, flip to 1255) AND the Nov-1 flip
slots carry the SAME fp 39614c7c — t266's two-writer ring analysis stands for
ring-content corruption, but the RAM campaign swap in BOTH incidents is driver
self-harm via title-menu Load, mechanism no longer [unverified]. (4) TOOLS:
scripts/r285_fp.py KEEPER (planet-name+owner md5; equality valid WITHIN a run,
NOT across a load — recs 152->156 locator drift witnessed; use the r1_slot
ship_records census instead across loads: pre-drive shipfp f4e5e715 == restored
f4e5e715, loaded 0272c480); r1_t261_drive.py PATCHED (ring_in_game gate on the
drain + input_alive rewritten 'c'-first/Escape-last). (5) RECOVERY SOP EXECUTED
(bank -> SIGKILL recorded pid 636955 -> vnc start -> ONE click (318,333)):
production RESUMED t1086 V0, shipfp-verified; new pid 660167 TL expiry
2026-11-05 05:26; RESUME.GAM md5 5b382afb untouched throughout; banks t285-
predrive/-flip1255 (incl. screenshots)/-loaded1255/-restored-t1086. (6) HARVEST
on the 6 genuine turns (r273_harvest window 04:33-04:39:41): leg A ZERO damage/
destructions/flips, 11 att deltas all -1 drift; leg B V held 23 from the first
end-turn pass, ZERO V>=25, selector 0, rank 65535; leg C ZERO magnetron frames.
REPLAY MINE-CHECK on the loaded campaign: r284_vreplay 20/20 EXACT (V=14,
vis=mk=13) — the S18 law reproduces on a foreign seed. (7) TWO harness failures
banked honestly: system python3 has NO PIL (t283 trap, killed launch 1 silently)
and a launch without the T261_* env prefix "reached target" on the stale scratch
ring (zero clicks; spurious bank deleted; production ring verified untouched).
NEXT=t286 verbatim + the DRIVE-CLASS PRECONDITION block.

LANDED t284 (2026-11-03): THE V PREDICATE DECODED, CORPUS-REPLAYED, AND THE
REWRITE UPGRADED — OQ-021 ANNOTATED (stays OPEN, threshold residue; strict-
close honoured: the producer/predicate closes on replay, the comparator does
not). Artifacts: docs/re/score.md S18 (permanent), docs/re/_wip_t284.md (law +
validation), scripts/r284_vreplay.py (THE replay, reusable as a mine-check),
scripts/r284_contest_census.py + r284_deref.py (pointer-class readers).
(1) BASE OBJECT RESOLVED: witnessed ebp 0x254e10 = data base + 0x12e10 = THE
TURN COUNTER's game-state object; V = field +0x354eb == 0x482fb (t283's
"arithmetic coincidence" was the state-object root all along). Caller
FUN_00024f24 (turn ++ at its tail) is the end-of-turn pass; its TAIL is the
producer protocol: clear lane marks (pool 0x16147 stride 0x27 rec+0x21), seed
V=1 iff the HOME star (HOME POINTER dword[0x12e1d+0x1ee*player], t246/t248 law)
carries the player's presence bit else V=0, then FUN_00024274 flood. (2) PREDI-
CATE (the t283 open question) = three gates per candidate lane: far star +0x17
SELECT mask has the PLAYER bit (allies do NOT satisfy); far presence pair
+0x14|+0x15 — MEASURED == races owning a planet at that star (48/50, the 2
exceptions multi-owner) — has no bit outside (allied|player); and no live ship
holds an ORDER INTO the lane (ship+0x59 == lane record pointer; kind-5 orders
measurably carry lane-pool pointers, kind-4 star records, kind-0 null — first
misread was the 0x88 trap, now a REFUTED-ROUTES entry). Admit: mark, V+=1,
RECURSE; a failing lane PRUNES ITS SUBTREE (explains t912 11->22 and 23->14).
(3) REPLAY vs 409 banked in-game slots, 20+ runs, turns 1..1255: V EXACT 295,
ALL 114 misses = pre-first-end-turn slots (stored 0), ZERO V>PRED, ZERO
nonzero mismatches (ladder V=1 x13 runs, 14@t1255, 23@t1087 == the t283 walk
terminal); visited set == persisted +0x21 marks 409/409. UNIT CORRECTION: V
counts ADMITTED LANES + home, not stars (cycles double-enter) — S6's V=22 vs
systems_any=14 finally reads. S10 #3 REFINED: V is a pure snapshot function;
the lineage-pair history hypothesis is SUPERSEDED (REFUTED-ROUTES t284).
Vendor off-by-one edge (break on last live slot still accepts): 0/2310 contest
pairs — not observable, rewrite uses plain any(). (4) REWRITE: campaign.cpp
recomputeScoreStars()/floodControlled() mirror the pass (0 at construction,
recompute ONLY at end of advance() after diplomacyPhase); playerScorePct() =
TRUNC(100*V/T) per S2 (was rounded owned-star share); settlement grants the
claimant's +0x16/+0x17 bits (without it the flood prunes its own colonies);
presence via owner_ proxy [documented single-owner limit]. Pins
tests/test_score_t284.cpp x7; 166 tests 0 fail; Control VICTORY comparator
deliberately UNTOUCHED (threshold residue). Gate 0, LEDGER AUDIT OK, LEDGER
INDEX OK. Production :9 untouched, healthy (pid 636955).

LANDED t283 (2026-11-03): OQ-021 PRODUCER RESIDUE CLOSED WITH CITED MEASUREMENT
— THE DAT_482fb WRITER IS A WITNESSED END-OF-TURN ACCUMULATOR (9 scratch
emulator runs; docs/re/dosbox-wp-t283.md hand-authored + score.md S17; ledger
row OQ-021 ANNOTATED, stays OPEN on the threshold residue — strict-close: the
producer residue closes on a non-artifact fire + cited disasm, both delivered):
(1) TARGET from this session's own ring (r1_sav_scan 6 votes B=0x1bf4d8) ->
guest-linear 0x28A2FB == 0x242000+0x482fb law-anchor exact. (2) FIRES x4 runs
reproducible "0000:28A2FB - 00 -> 01" +3.1-3.3 s after NEXTTURN; phase protocol
decisive: quiet 90 s ZERO fires, 'c' overlay x6 ZERO fires (t189b
overlay-recompute hypothesis REFUTED), turn phase fires. Non-artifact PROVEN by
derived law (artifact needs byte NONZERO at arm; score_stars=0 at arm in every
run — and production 51.sav reads 0 too: the displayed count is DERIVED state,
0 at load, repopulated by the end-of-turn pass). (3) WALK 0,1,3,6,11,12,15,16,
16,18,22,23 monotone, terminal 23 == banked corpus max (S6) — an accumulator,
not a territory read. (4) WRITER SITE: fire EIP 1e3803 = file 0x243B3 (loop-top
check law: fire EIP is one PAST the store) -> UNIQUE store `mov DWORD PTR
[ebp+0x354eb],ecx` at file 0x243A8 (pattern 898deb5403 exactly once image-wide;
t212's census missed it precisely because base+disp has no static disp32 form —
S9's predicted residue shape positively witnessed); arithmetic anchor
EAX=0x254e10 == 0x28A2FB-0x354EB exact; loop context ship stride 0x162 + live-
count gate ds:0x4348b + race stride 0x1ee cmp-3 (aicode.md P8 tail). (5) NEW
HARNESS scripts/r1_t283_wp_session.py (phase protocol + walk + per-fire EIP;
--phases quiet,c,turn --walk N) + scripts/r1_t283_disasm.py (objdump -b binary
-m i386 -M intel --adjust-vma; --start-address with -b binary prints NOTHING —
trap) + scripts/r1_t283_tailturn.py. (6) OPERATIONAL LAWS banked (doc §4):
BREAK after a campaign LOAD needs its OWN ~45 s settle (run 5 silent stall,
RECEIVED but never answered, no glibc error — distinct from t282's crash);
-savedir does NOT mkdir and autosave-fail makes the X window vanish;
DISPLAY needs the colon; system python3 has NO PIL (use compare -metric AE);
MEMDUMPBIN-with-filename over MCP EXEC is DEAD ("Invalid memory dump arguments"
x2 — read the ring saves instead, do not re-guess syntax); the BREAK "Dynamic
core" warning prints UNCONDITIONALLY (debug.cpp:5350). (7) NO-sitting
adjudication first (tail max turn 1086 == baseline; sitting script NOT run).
Production :9 HEALTHY untouched (pid 636955, TL Nov-04 22:33); no strays
(all scratch dosbox/Xvfb by recorded PID; manual diagnostic Xvfb :95 reaped).
NEXT=t284 rewrite the V semantic in rewrite/src/game/score.cpp.


LANDED t282 (2026-11-02): DEBUGGER INSTRUMENT VERIFIED LIVE — WATCHPOINTS FIRE
ON THIS BOX (offline gate task + 4 scratch emulator runs; NO OQ closed —
strict-close honored, OQ-021 ANNOTATED, ledger 15/4 unchanged):
(1) BUILD GATES verified: config.h :43 C_DEBUG 1, :115 C_HEAVY_DEBUG 1, :172
C_SDL2_NET 1; binary copied to work/r1/bin/dosbox-x-dbg (md5 ebc6a785... vs
/usr/bin/dosbox-x 15c49346... — production untouched). Exact-word strings BPLM/
BPPM/RUNWATCH/mcp_server all present (dfsg: zero of each; pairing-note x3/x3/x4/
x2 were substring counts — both true, restated precisely).
(2) DIRECTION LAW READ THEN MEASURED: mcp_server makes dosbox-x CONNECT OUT to
our listener (debug_mcp.cpp CONTROL_HOST + SDLNet_TCP_Open); connect observed at
+0.2 s. The MCP EXEC parser is NOT tty-gated but BREAK is (debug.cpp:5410
isatty x3) — hence pty-for-the-gate + socket-for-the-words (deliberate deviation
from the assignment's PTY-suggested mechanism, on cited source grounds;
-break-start NOT used, GOAL decision respected).
(3) LIVE HELP CAPTURED (79 lines, unpaged — capture suppresses the pager,
debug_gui.cpp:685): verbatim list + key map banked to dosbox-debugger.md; live
list carries NO HELP entry for RUN/RUNWATCH though EXEC RUN works — parser is the
authority, not strings.
(4) ACCEPTANCE MEASURED 3/3: BPLM 00FA0000 / BPPM 0040:0000 / BPM 0040:0010 all
armed (BPLIST shows them; list spells BPM's entry "BPMEM"); BPDEL * clears.
(5) FIRE MEASURED 2/2 (--settle 40): BPLM on guest phys 0x46C (BIOS tick) fired
at +2.1 s — "Memory breakpoint : 0000:046C - 00 -> 69" (and -> 94 rerun), CPU
stopped, stopped debugger STILL ANSWERED EXEC BPLIST over the same socket
(ControlServer_Poll inside DEBUG_Loop, debug.cpp:5267). The t272 general
negative is now SUPERSEDED with a live demonstration (REFUTED-ROUTES + score.md
S15 marked; dfsg-only scope preserved).
(6) TRAPS BANKED: (a) BREAK at +0.2 s aborted the emulator 1/2 with glibc
"corrupted double-linked list" (mechanism NOT proven; --settle 40 mitigated 2/2);
(b) the BPLIST "(00)" is the armed baseline — the fire test is
bp->GetValue()!=current (debug.cpp:870), which IS the VOGONS 0x00-artifact, so
the first fire of any nonzero location is spurious-by-design; (c) a BPLM fire
line prints seg 0000 — no usable address, arm ONE breakpoint; (d) fire
granularity one byte; (e) probe crash mid-session must still reap child+Xvfb
(finally-block law in the scripts). New tools: scripts/r1_mcp_dbg.py (listener
lib), scripts/r1_t282_dbx_probe.py (bring-up + sweep + fire sanity). Scratch
copy work/r1/game-wp (148 MB, gitignored) persists for t283. Production :9
HEALTHY after every run (pid 636955), no stray dosbox/Xvfb, timeline unchanged
(no new sitting; last turn 1335).
WIP: docs/re/_wip_t282.md S1..S8. Permanent: docs/re/dosbox-debugger.md (LIVE
VERIFICATION section). NEXT: t283 (the BPLM-on-DAT_482fb session — everything it
needs is now measured, including which pitfalls are real).

LANDED t281 (2026-11-02): SA_CORNUCOPIA REPAINT WIRED VERBATIM — THE LAST
STATE-CARRYING §6.3 BODY CLOSED OUT + THE +0x16 SKIP KEY MEASURED (offline,
pure code; NO OQ closed — strict-close honored, OQ-016 ANNOTATED, ledger 15/4):
(1) RAW RE-READ sharpened the law (work/t280_bodies.txt:152): repaint BOUND is
WORD[rec+0x18] = SURFACE slots only (orbital ring never touched), no occupied-
slot gate, tie law strict-< with FIRST pool record winning (cx carries best pop,
`jbe` prune @0x43e24). (2) MEASUREMENT (keeper scripts/r1_t281_w16_census.py
RC=0): WORD[rec+0x16] over the static pool in two lineages (bank-t1254 n=145/
owned 124, bank-t273-tutorial645 n=135) is UNIFORM over 0..10 owned AND unowned
=> +0x16 is the STORED world-gen weight-row index (ctor rng%11 @0x23a97/aa8),
NOT a homeworld marker — t105 §3's one-sample [inferred] reading REFUTED; row
10 == [0,33,34,33] zero-barren preset. t29b histogram non-prediction STANDS
(persistence != provenance; template source stays an OQ-016 residue).
(3) REWRITE: PlanetState.terrainRow stores the previously-discarded ctor draw;
Cornucopia case = verbatim select (owner, skip row 10, strict-min pop, null-
exit) + repaint cellClasses raw {0,1} -> 2+worldNext()%3 over the surface bound
(worldLcg_ = terrain-family stream, rng_ trajectories untouched, choice jus-
tified not defaulted); richPros field + richProsFor + storedProsFor join
DELETED (income rides the T35 class-cell bonuses in channelAccFor — the channel
the stand-in approximated; govBonus t45 law KEPT through the surgery).
(4) PIN species_cornucopia_repaints_min_pop_colony_t281 (split from the
more_max_pop test): seed-16 control differential (target recomputed in the
test from owner/pop/terrainRow; all other stars byte-frozen; ring frozen) +
seed-8 SKIP/NULL-EXIT leg (temp seed-scan MEASURED owner 1's only home sits on
row 10 for seeds 8/9/14/18/18/26/31 -> no event, no cell change). MUTATION-
VERIFIED: bound-widened CAUGHT (10 fails), skip-neutered CAUGHT (line 304);
tie-break flip NOT caught (no pop tie at seed 16's argmin — honest negative,
law stands on the raw jbe). Suite 159/0. Mid-edit slip banked honestly: first
storedProsFor patch dropped +govBonus, caught same-minute.
(5) Docs: aicode.md §6.3 t281 amendment, abilities.md row, ai-dossier row 11
(Cornucopia leaves the abstraction list), income-law.md +0x16 note, OQ-016
STATUS t281 STAYS OPEN, _wip_t281 S0..S5. Machine UNTOUCHED: :9 pid 576895,
ESTAB VNC client present AND ring still tutorial-645 -> t279 release conditions
BOTH unmet, drive HOLD; no clicks/saves. QUEUE DRAINED -> NEXT = WAIT-TRIGGER
SENTINEL (triggers A-D named inline; after-drains relaunch law stands:
MAX_ITERS=12 IDLE_GATE=0 — sentinel sessions are cheap by construction since
they check four triggers and end).

LANDED t280 (2026-11-02): AI GAP ROW 11 REMAINING BODIES CLOSED OUT — A
MISSING BODY FOUND, TWO §6.3 CITATIONS REFUTED, CODE UPGRADED (offline, pure
code; NO OQ closed — strict-close honored, OQ-016 ANNOTATED, ledger 15/4):
(1) BODY 14 SA_MoreMaxPop 0x4402a EXISTS but §6.3 NEVER documented it
(jump-table re-dump restored FILE 0x43b10: case al=9 -> 0x4402a; keeper tool
scripts/r1_t280_bodies.py reproduces the whole listing, work/t280_bodies.txt).
CITED LAW: every owned planet (static pool 0x2b057 stride 0x7b, owner byte
+0x57) WORD capBase +0x55 += 2 then recalc 0x38ba4 — PRE-CLAMP seed operand,
NO pending/[+0x16] gates. Independently corroborated: income-law.md S10 had
measured the same site from the corpus side with "no in-code caller found" —
the caller IS the ability dispatcher 0x441d8 (identity CLOSED, S10 note).
REWRITE UPGRADE: capBase += 2 verbatim (old capBonus += 25 was wrong operand
POST-clamp AND wrong magnitude; field + popCapBonusFor deleted, source census:
no UI reader ever). Pin species_more_max_pop... control differential,
MUTATION-VERIFIED (capBase+=0 CAUGHT).
(2) ERRATUM E2 (ForcePeace 0x43bf0): threshold = TARGET ROW's PROPOSE_PEACE
+20 (dword row_x+0x1cb >>16 lands on +0x1cd per the loader positional map),
not self's ACCEPT_PEACE; the vendor FLOORS att[x->self] to arm x's chooser —
it never ends wars. Rewrite keeps the end-the-wars abstraction, DIVERGENCE
labelled (floor needs player->AI attitudes, absent state).
(3) ERRATUM E3 (Hatred 0x440b5 — the body t256 wired): cell word[row(x)+
0x1b2+2k] is att[x->k] (holder = row, target = col — three witnesses: §13.2
att[self][other], t207 §19 victim-row clamp, watcher relation() docstring)
and the line is DECLARE_WAR(x) (x's OWN), not r's. t256's Campaign::
hatredClamp clamped att[x->self] at DW(r) = wrong cell AND wrong threshold;
RETIRED (every corrected-law cell is AI->AI = row-12 absent state) ->
CauseWar announce-only under every owner; pin species_cause_war_hatred_
ceiling_t256 -> species_cause_war_two_party_boundary_t280 (deterministic
control differential, MUTATION-VERIFIED: a dipState_ write in the case
CAUGHT). Mid-session the cell-direction reading was self-corrected once
(first draft said att[k->x]); the retirement conclusion held under BOTH
readings, the docs ship the corrected law (=_wip_t280 S4).
(4) REMAINING BODIES 5/6/7/8/9/10/11/13/16 + NOPs 15/18 re-read raw and
CONFIRMED as documented (Shield T2 exit stores cad-counter == 0 at the
equality point -> rewrite's single reset is EXACT both legs). Docs: aicode.md
§6.3 t280 amendment E1-E3, abilities.md rows MoreMaxPop/ForcePeace/CauseWar,
ai-dossier row 11 T280 pass, income-law.md S10 closure note,
docs/re/_wip_t280.md S0..S5. Machine UNTOUCHED: :9 HEALTHY pid 576895 (TL
exp 11-04 10:07), no new sitting (r214_triage RC=0, tail 400 rows all turn
645 tutorial-lineage churn), ESTAB VNC client :5910 -> t279 stays HELD,
drive HOLD; suite 158/0; gate 0; ledger audit OK 15/4, index OK; NEXT=t281
(Cornucopia repaint — the last body whose operands the rewrite state
carries; task card authored with the +0x16-skip honesty caveat).


LANDED t278 (2026-11-02): OQ-005 RULING PACKAGE SHIPPED — index.txt REBUILT
AS AN 88-ROW DECISION SHEET (offline; user-time-shortening; nothing closed):
(1) DELIVERABLE work/r1/shp_png/index.txt (twin decision-sheet.md, generator
scripts/r1_t278_decision_sheet.py over banked inputs index_t278pristine.txt +
ids.tsv). Rows A1-15 (already-shown CONTROL/RESTORED-V, Oct-29 verdicts quoted
VERBATIM — source session 20261022_024226_01e8e7 msg 40813 recovered via
session_search), B1-29 (SPAN-FREE full frames, bright thumbnails on disk, cited
library identification per row incl. planind drawn-in-play law), C1-44 (FAIL
class w/ span bytes + honest status). Every row carries a one-line keep/junk/
re-render RECOMMENDATION; R13 held — recommendations are proposals, the user
rules. (2) MEASURED decomposition of the 44 FAILs reconciles EXACTLY: 25
zero-byte ladder slots (batch-rulable) + 12 cos_star addressable-empty (t200
selector law) + mouse k6/k7 + 1starmap k1 + sg50expl k9 (invalid dims) +
mouse k5 + sg64expl k0 (t197 demotions) + 3cfgnew k12 (EOF-broken vendor data;
the only JUNK candidate — windows.txt selects k0 only). (3) RENDER-STATE
MEASURED: on-disk PNGs carry the t189b bright palette (lgrace10 mean
[148,126,102] max 255) so no re-render was owed; sheets/ contact sheets ARE
dark-era (Oct-1) and are flagged as such in the sheet, regeneration offered not
performed. (4) KEEPER PITFALL: scripts/r1_t182_pngdump.py OVERWRITES index.txt
every run — hand content there must be regenerable (generator + pristine census
copy banked). Banked: shp.md S24, BLOCKED.md t68 amendment (sheet path into the
OQ-005 ask), OQ-005 STATUS t278. NO OQ MOVED (row stays open strict-close —
closure = the user's per-row reply or a draw-capture). Machine UNTOUCHED: :9
pid 576895, ESTAB VNC client still present -> t279 stays HELD, drive HOLD;
ledger 15/4 audit OK, index OK; gate green; NEXT=t280 VERBATIM.


LANDED t277 (2026-11-02): TL-EXPIRY FORENSICS CLOSED THE LOOP'S STANDING
UNKNOWN ABOUT GAME DEATHS + SOP/DEFAULTS SHIPPED (offline; production :9
576895 untouched and HEALTHY throughout — TL expiry 2026-11-04 10:07:01):
(1) LAW 1 MEASURED n=18 — 18 of 33 logged :9 sessions died at 28810..28820 s
wall; 17 of them banked EXACTLY 2880 = TL/CADENCE autosaves. ALL THREE deaths
the t273 handoff note called "unexplained" are TL expiries (S21 ends 15:43:56 /
28816 s = the "+15:45 pattern" leg, S28 ends 15:45:08 / 28811 s = the Nov-1
incident, S31 ends 07:04:27 / 28819 s = the Nov-2 incident; S31 banked 2780
saves — row-suppression window, banked as a residue). The ring
save count IS the -time-limit counter read through the 10 s cadence law => a
session's death cause is diagnosable from the ring ALONE. Census method:
banner-line boundaries (33 "DOSBox-X version") + per-session first/last guest
`LOG: [hh:mm:ss]` + `Saving state to slot` counts via one awk pass over the
290 MB log (never a full read). Table: docs/re/_wip_t277.md; laws: selfplay.md
t277 block. [inferred] residual: internal exit vs the timeout -s KILL $((TL+30))
wrapper is NOT separable from wall clock (lifetime sits between TL and TL+30).
(2) LAW 2 MEASURED NEGATIVE — the queue's "exact farewell line" DOES NOT
EXIST: grep 'Shutting down' == 0 and 'kill' == 0 over the whole production log;
/usr/bin/dosbox-x holds only the help text + conf name; golden witness ON DISK
work/r1/selftest-t111-playcap/dosbox.out (TL=90: 9 saves, last line
'Saved. (Slot 49)', EOF at 'Active save slot: 1 [Empty]'). BINDING CONSEQUENCE:
never hunt a log marker for TL death again; liveness is /proc-polled, which is
what r1_game_health.py does. (3) LAW 3 MEASURED n=198 (journal.tsv gaps: p50
1502 s / p90 6206 / p95 8682 / max 15156) — the loop samples health ONCE PER
ITERATION, so t267's 600 s warn window was ~4-11% likely to ever be observed:
structurally unobservable (Nov-2 death reported 35 min AFTER the fact, zero
T:WARN rows in loop.log). SHIPPED: r1_game_health.py WARN_AHEAD 600->14400
(VERIFIED both directions on a /tmp fixture: fake dosbox-x compiled with gcc,
own vnc/out/loop dirs, TL=1200 -> T:WARN RC=1 at default, silent at
WARN_AHEAD=600; production HEALTHY RC=0 with no false warn; fixture killed by
its RECORDED pid -> G:DEATH + GAME_DEAD.txt; production never signalled);
r1_playcap_vnc.sh TL default 28800->172800 (48 h runaway guard, measurement
cited inline — matches what the t273 hand-relaunch already used so a future
relaunch cannot regress); gate.sh stage 3n3 pins all three invariants,
MUTATION-VERIFIED (reverting either constant in a copy FAILS the stage;
positive path OK1-OK3; bash -n clean). SOP documented VERBATIM (selfplay.md
t277 + BLOCKED.md t277): bank ring -> confirm no human VNC client -> 'stop'
(TERM to recorded pid) -> 'start' -> health shows the NEW expiry; restart is
the ONLY lever since no binary string extends -time-limit at runtime. NO OQ ROW
MOVED (harness/forensics row; ledger 15 closed / 4 open unchanged, audit OK,
index OK). NEXT=t278 VERBATIM.

LANDED t276 (2026-11-02): PLANETALLOC WINDOW COMPOSITION WIRED AS CODE —
rewrite/src/ui/planetwin.{h,cpp} (pure, no SDL; hudlayout.h t264 template) +
tests/test_planetwin_t276.cpp 8 cases, suite 158 tests 0 fail; CMakeLists
gains both files (ascend_ui + run_tests direct-compile lists). LAWS WIRED
(all cited upstream, doc section planets-ui.md S7): (1) five TYPE-29 panel
table kPlanetPanels verbatim windows.txt 1536..1604 (rect+msg+param+help),
file order == left-to-right, disjoint X-bands 9 px gutter, joined against
the SHIPPED windows.txt by the test (loader reads TYPE->NAME block order);
(2) dispatch ui::paintKey = the two remaps verbatim (param 4->3 @0x3cc1c,
msg 51->4 @0x3cc29) — LOAD-BEARING: PLBUILD param 1 collides with PLIND key
1 without it; MUTATION-VERIFIED catcher (deleting the override fails the
pin; reverted, rebuilt green); five panels key 0..4 exactly once, key == file
order; (3) header strings verbatim static.txt #147/#148/#149/#150/#151/#152/
#153 + plural pair #28/#29, byte-exact join incl. the DOUBLE SPACE in
#151/#152 and the literal-backslash-n file bytes vs real-newline module
constants (loader-interprets law [inferred], both pinned); pluralization
singular-iff-==1 for #151/#152 marked [inferred] (pair's ==1 use cited only
for the ability countdown aicode.md §8.2); formatPlanetHeader takes the
MAINTAINED planets counter as an argument — nothing derives it (t248 PROOF 3
says the table count is NOT the header source); (4) planetGaugesFor =
{gaugeSelector RES+0x46, gaugeSelector IND+0x44, prosSelector PROS+0x48}
over channelWordsFor (seed-2024: per-star match + S3 ladder bounds);
popPanelFor composed at origin (355,7) inside PLPOP rect; plbuildIcon =
data\planitem.shp identity domain 0..39, CITED only 34->k34 (shp.md S23.4).
HONEST BOUNDARIES: NO OQ row moved (composition of already-cited laws; the
39-item planitem identity extension stays an OQ-005 contact-sheet fold; the
pluralization stays [inferred]) — strict-close unaffected. Machine untouched
:9 HEALTHY (TL expiry 2026-11-04 10:07), no new sitting (tail all t645, r214
tail census decisive: 613 rows last 2 MB all turn 645), VNC client still
ESTAB :5910 -> drive HOLD holds; game/ untouched. NEXT = t277 VERBATIM.

LANDED t275 (2026-11-02): COMBAT INTEGRATION ADJUDICATED — ENGAGEMENT
RESOLVER 0x42c60..0x42e6e READ VERBATIM (first time; t179 P3 was a summary).
TRIAGE: the queue row's four sub-laws (deterministic damage, ordered cat-0
volley, shield-then-hull absorb, death at <1) are code-verified LANDED since
t89 (attackScore SUM campaign.cpp:1842, absorbSplit campaign.h:383, rng_
draws removed :1956, capture/Extinct mapping, pin campaign_combat_law_oq010)
— re-implementing them would churn. NEW LAWS (docs/re/combat.md S2k, listing
work/t275_resolver.txt, capstone via /home/hrethric/tools/revenv/bin/python
— HOST pythons have NO capstone): (1) enclosing fn 0x41e34 (size 6087), sole
caller 0x41910 inside movement resolver 0x41260 (callers 0x16eb0/0x2554f);
(2) caller-side ship array is OWNER-RACE FILTERED ([ship+0x54]>>16 ==
engagement race, POWER>0, kind!=1) — the resolver NEVER sees the defender ->
return fire is a SEPARATE resolution pass (corroborates t85g discrete steps
40>38>36>34); (3) leg-selection gate 0x39a00: objective planet with ACTIVE
item 23 Ship / 26 Orbital Shield / 27 Orbital Mega Shield SKIPS the
invasion-carrier leg straight to firepower (item map verified income-law.md
§6h); (4) 0x4a55c inside leg B WRITES stance/target (+0x62/67/68) — resolver
commits the firing order. HONEST NEGATIVES: region never reads +0x59 (queue
citation misdirected); every selection input is per-ship/per-planet state ->
aggregate-mappable content is COMPLETE; DECISION: gate + t207 defense term
NOT wired (no call site in the conflated aggregate engagement; operands are
OQ-019 per-ship state; zero invasion-vs-shield witnesses 20/20 saves —
wiring would add un-witnessed behaviour). OQ-019 row annotated STAYS OPEN;
ai-dossier row 14 annotated; rewrite code UNCHANGED (correct strict-close
outcome: no default changed on this evidence). Machine untouched: :9
HEALTHY (TL expiry 2026-11-04 10:07), no new sitting (tail all t645), VNC
client still ESTAB :5910 -> drive HOLD holds; RESUME.GAM untouched; no game/
changes. NEXT = t276 VERBATIM.

LANDED t274 (2026-11-02): ECONOMY/RESEARCH E2E TEST PIN — rewrite/tests/
test_econres_t274.cpp (4 tests, CMakeLists registered; suite 150/0 green, gate
green). FIXTURE HONEST NEGATIVE: the queue row said "use the watcher JSON
scalars" — MEASURED the watcher schema (r1_playcap_watch.py): NO per-planet
economy fields exist (turn/score/selector/rank/ships/ship_raw/relation/
planets_mine only), so per-planet pins run on the seeded sim with vendor-truth
constants cited from income-law.md (banked T274). MUTATION-VERIFIED the
task's target ("catch a regression if buildPhase/research wiring changes")
with 3 single-token campaign.cpp mutations, each caught, each REVERTED
(src tree verified clean via git diff): completion gate >= -> > CAUGHT
(e2e_build_queue_opening exact cadence t16 -> t17); growth +1-boost leg
deleted CAUGHT (474 fails, e2e_growth_counter); research
includeVariants=false -> true CAUGHT (1270 fails incl. queued-row q<66
legality, e2e_research_tier_chain). Pins: (1) channel words are RATES +
per-turn acc delta == word IND + completion shape (0x39005/0x3907b/0x390a3);
(2) full growth law per planet per turn incl. cap-reset @0x393f9, +1 iff
AI&&word<4, threshold 50, Cloning +1, clamp (S6c/S6e/T56); (3) t0 zero-queue
/ t1 all-AI-homes-queued (T56(3)) + seed-7 EXACT first-completion t16;
(4) research chain: variants never owned 240 turns, prereq-before-complete,
one completion/owner/turn, cumulative injected RES >= runtimeCost at
completion (research.md §7). TWO SIM DIVERGENCES BANKED (income-law.md T274
D1/D2, ai-dossier rows 2/5 annotated): D1 rewrite auto-queues the PLAYER home
where T56 [verified] says 0xFFFF (documented default; re-trajectories all
seeded pins + PLAYTHROUGH — deferred, NOT silently fixed); D2 AI opening item
Factory 6/6 vs T56 Agriplot 4/4 (witness n=4 one run — adjudication needs
fresh-run selector witnesses, drive class HELD). OQ-016 row annotated, STAYS
OPEN (strict-close — pins guard laws already closed as sub-laws; no new
closure evidence). Machine untouched: :9 HEALTHY (health script run at start;
VNC client still established -> drive-class HOLD re-confirmed); RESUME.GAM
untouched; no game/ changes. NEXT = t275 VERBATIM.

LANDED t273 (2026-11-02): LONG DRIVE WITNESS HARVEST II — DRIVE LEG LOST TO A
TITLE-MENU MISCLICK (law banked), HARVEST LEG DELIVERED over the full corpus,
t251's mine exposed as TWO measurement bugs, FIRST nonzero selector byte lands
and REFUTES the naive selector=threshold reading. (1) INTAKE CLEAN: production
:9 healthy 1086/4-power, single watcher, RESUME.GAM md5 5b382afbb789186c...,
pre-drive bank bank-t273-predrive (20 slots). (2) 4 s after the t250-v4 driver
opened, its popup drain had clicked game-y 237 = the TITLE MENU Tutorial
button (refcap rows 252/293/333 + ui.md PLAYTUTORIAL rect cited) and the ring
flipped to the vendor TUTORIAL campaign (645, 3 powers, Terpsichore screen
shot). LAW: popup drain must never run at the title menu; clicks band-measured
per screen. Remote VNC client attached during part of the window => human
touch not excluded; driver killed 11:49, zero further input, RESUME.GAM
re-verified UNCHANGED, tutorial ring banked (bank-t273-tutorial645). (3)
r273_harvest.py over 72,327 rows / 72,128 guarded pairs: LEG A damage-vs-
non-at-war-owner STILL ZERO (32 hull hits, 26 AT_WAR, 6 fail the new
r273_vet.py attribution vet); multi-volley 12 pairs ALL inside the known t1253
AT-WAR battle (filter validated there); SECOND -40 price+WAR-flip witness
(Ungooma->Chamachies 477->437, wall 00:35:35 t1253) + a -28 price with NO flip;
clamp 280 never hit. t251's owner HANDLE-vs-INDEX bug (+0x54 vs +0x56) and
stale-echo pairing void its '252 non-war candidates'. LEG B: zero V>=25 rows;
selector=2/rank=1 at V=0 in the tutorial lineage = score.md S16 (arm list
gains end-capt @0x2c07a; selector->arm mapping unverified). LEG C: magnetron
USE frames zero (160,747 control rows). LEDGER: OQ-016/019/021 ANNOTATED, all
STAY OPEN (strict-close honored — honest negatives banked). BLOCKED.md t273
block written with the relaunch release conditions (no :5910 client AND ring
still tutorial-lineage; bank first). :9 LEFT RUNNING THE TUTORIAL — a human
signal decides. NEXT = t274 (pure code, machine-free).

LANDED t272 (2026-11-02): V-PRODUCER WATCHPOINT SESSION RUN ON SCRATCH —
INSTRUMENT MEASURED-DEAD ON THIS BOX (honest negative; no row closed,
strict-close honored). (1) Session built per every standing law:
scripts/r1_t272_wp.sh — scratch tree work/r1/wp-t272/game (game/ never
mounted), OWN ring dir work/r1/wp-t272/save (two-writer law), display :94,
FIFO-held stdin (no EOF-spam), tracked-PID kills only; production :9 untouched
and healthy throughout (pre-flight HEALTHY pid 576895, TL expiry Nov 4 10:07;
post-run ring fresh, RESUME.GAM md5 5b382afbb789 unchanged — no new sitting,
assignment stood). (2) INSTRUMENT CENSUS -> NEGATIVE (score.md S15 +
REFUTED-ROUTES t272): dosbox-x 2025.02.01+dfsg-3 SDL2 has NO debugger command
set — strings -n 2 (the length catching 3-char verbs; the pairing session's
-n 3/4 census was on the wrong artifact but its conclusion stands): zero
bpm/bph/clrbp*/bplist/dbgcon/breakpoint/watchpoint literals; the en_US.lng
DEBUGBOX/:DEBUGCMD/debugger_runwatch strings are DEAD tables — EMPIRICS:
DEBUGBOX ASCEND.EXE -> "Bad command or filename" (shot2.png); live GUI menu bar
= Main/CPU/Video/Sound/DOS/Drive/Capture/Help, NO Debug menu (shot_help.png
Capture list = screenshot/record/state only); -break-start ACCEPTED AND IGNORED
(shot1.png: title screen, autosave ran) — GOAL.txt's do-not-pilot decision
empirically VINDICATED. No bochs/qemu/valgrind on the box; /usr/bin/dosbox
0.74-3: zero debugger strings; ptrace stays R4-dead. (3) KEEPER: a
title-screen scratch boot has NO ascend.exe image in guest RAM
(scripts/r272_scratch_resident.py RC=0: payload 16B-chunk hits 3 vs 118
production, "STARS CONTROLLED" 0 vs 1, non-zero 1MB pages 3 vs 17) — any
debugger-class session must ENTER A CAMPAIGN first; scratch copy itself works
(ring lands, base tooling reachable once campaign resident). (4) LEDGER EFFECT:
the watchpoint class named as closure route by OQ-021 (producer write-site) and
OQ-019 (t265 sub-ring residue) is measured-dead here; OQ-021 row updated with
t272 status (STAYS OPEN; live routes = t273 V>=25 witness + ENDGAME-window);
route re-opens ONLY if the user supplies a debugger-enabled dosbox-x build
(upstream builds ship the debugger; Debian +dfsg evidently links it out —
score.md S15.5). Harness gains kept: r1_t272_wp.sh (prep/launch/status/stop,
GUIFLAG + CONF knobs), r272_scratch_resident.py. t273's writer-EIP verify leg
VOID. NEXT = t273 VERBATIM.

LANDED t268 (2026-11-02): LIVE SCREEN SWEEP 3 — NEGSCREEN FLOW + INTEL DEPTH
+ RESWIN DOSSIERS (no row closed — strict-close honored; OQ-023 post-closure
ANNOTATED with the FIVE-row option-list measurement, STAYS CLOSED; dossier
docs/re/ui-runtime.md §6d NEW + selfplay.md t268 laws; 1 tool
scripts/r1_t268_screen.py = t253 primitive, OUT->work/screens/t268/).
PROVED: (1) NEGSCREEN option list is posture-AND-campaign-dependent — FIVE
rows at t1236 (Goodbye/DA_DeclareWar/DA_ProposeAlliance/DA_TradeStarlanes/
DA_TradeStars, player.dip :67/:31/:34/:37/:40 verbatim) vs THREE at t252/
t1255; Goodbye is file-LAST but render-FIRST (hoist law); alien line "Uh oh.
What's wrong now?" == race02.dip:172 DR_NoDipResponse exact; player.dip holds
the BASE DIPVALUES (ACCEPT_ALLIANCE 200) — race files override (Orfa 570
live), engine must read per-race. (2) INTELSCREEN race rows NOT clickable
(204 px blink floor) — manifest-level IS terminal intel depth (honest
negative; no detail screen exists). (3) RESWIN Allows list = REVERSE JOIN
proven 3/3 vs files: restree row N -> idx N-3; rendered Allows == exactly the
gizmo/planitem records whose tech field == idx (Energy Focusing 39 ->
Myrmidonic Carbonizer+Accutron; Repulsion Beam 42 -> Fleet Disperser;
Megagraph 59 -> planitem Internet); "(N days)" renders ONLY on the current
topic; empty-disk click SETS the topic with NO popup (900 px confined to the
disk) — STATE-CHANGING sweep law banked; t268 set Repulsion Beam Tech once,
recorded honestly (autoplay campaign, no revert control). (4) Species-menu
race-row hit target = the text line only (~10 px), between-row click is a
no-op. SAFETY: 15 steps, ring turn HELD 1236, NEXTTURN never clicked, only
the band-measured Goodbye row clicked; parked on galaxy (242 px = blink
floor); game/ untouched. NEXT=t269 verbatim.

LANDED t267 (2026-11-02): HARNESS SELF-HEAL — DEATH/TL/WATCHER DETECTION
SHIPPED, AND THE 3-WRITER COLLISION WAS CAUGHT LIVE AND KILLED. Pre-flight
MEASURED three r1_playcap_watch.py writers on playcap (524207/524532/535187,
all holding timeline fds per the t215 writerhood law) with dup amplification
MEASURED in the tail (16 rows / 6 slot-keys, reps {3x5,1x1} — per-process
`seen` dedup cannot see sibling writers). SHIPPED: scripts/r1_game_health.py
(RC 0/1/2; G recorded-pid + adoption rule [pidfile lost + exactly one
harness dosbox-x in /proc => record, not death; MULTI checked even with a
valid pidfile = the t261 class] + GAME_DEAD.txt on DEATH; T TL expiry from
/proc ctime + own cmdline arg, WARN 600 s BEFORE expiry — the t266 ask; W
watcher census naming the reaper when >1; F ring-mtime freshness 60 s, NEVER
reads the timeline jsonl — OOM law; B bring-up 30 s). scripts/
r1_watch_reaper.py (per-PID /proc-verified SIGTERM, keep-newest, no pattern
kills): LIVE REAP of 524532+524207 keeping current 535187; POST-REAP
MEASURED reps all 1 — duplication gone. Wiring: vnc 'status' runs the health
pass; 'start' reaps --keep 0 then BRINGUP-verifies, and a t267 ADOPTION
GUARD closes the t261 ROOT (lost pidfile + live harness game used to launch
a SECOND game on the same ring; now adopts+records). loop_one_task.sh runs
the health check every iteration pre-gate (advisory stamp even under
IDLE_GATE=0 — takes effect at next loop relaunch; MEASURED bash 5.2.37 law:
tmp+rename leaves a running survivor on the old inode, in-place
rewrite corrupts it at its parse offset). VERIFIED: production HEALTHY
04:31/04:59 (TL line == hand computation 23:03:57+28800=07:03:58); fixture
battery DEATH/adopt/MULTI/WARN/PIDSTALE/foreign/zombie/RC2 all behave; full
lifecycle E2E in isolated sandbox (:10, copied scratch — game/ never
mounted — TL=120): BRINGUP OK -> T:WARN pre-expiry -> TL kill -> G:DEATH +
GAME_DEAD.txt; adoption proven (rm pidfile + live game => ADOPTED, one
dosbox). Limits banked in selfplay.md t267 (detects, does not relaunch —
evidence law; TL read from cmdline only). NO OQ closed strict-close (005/
016/019/021 open; control-plane iteration by design); gate 0, ledger audit
OK, index OK; production :9 untouched (its TL dies 07:03:58 — t268 pre-flight
handles it); NEXT = t268 VERBATIM
CORRECTION TO "untouched" (same session, later): my sandbox CLEANUP line
pattern-killed production (pkill -x dosbox-x matched 535172) -> quit-confirm
modal freeze 04:58:58-05:15:51; r1_game_health.py FEED-STALE caught it
(331 s), tclick.c-by-window-ID clicked No, ring resumed, campaign readouts
identical across the freeze, ZERO data loss — full account + the banked
never-pattern-kill law in selfplay.md t267 incident block + STATE standing
laws. The detector earned its keep on its first night, on its author.

LANDED t266 (2026-11-02): SOFTLOCK-CLASS FORENSICS — THE t261 "PRODUCTION
:9 SOFTLOCK AT 21:38" IS CONTENT-REFUTED AS A PRODUCTION EVENT: TWO-WRITER
RING COLLISION (REFUTED-ROUTES t266 block). The flip slot-pair is banked
(bank-t261-t1255 53->54, mtimes 21:38:12/22): CAMPAIGN changes across it
(campaign-fingerprint law NEW: md5 of star->planet-owner table; production
f8bf068b76 vs restored-t1255 lineage e1d3bdc128/47d063a23e) and production's
dosbox.log has ZERO "Loading state from slot" lines (n=0 over 5.8M lines;
"Extracting:" n=3.89M are SAVE-path churn — misreading them was a live trap).
A stray second dosbox with savedir redirected to playcap/save wrote every
t1255/V=14 row 21:38-23:06; production's own autosave went SILENT at
21:38:12 (its silent guest hang is real but cause-on-disk unresolvable — last
driver action press 19 + drain 2, misclick-on-galaxy [unverified]). THE
OSCILLATION QUANTIFIED (restored campaign, shared-ring witness): 511 rows
21:41-23:03 = 11 state-runs; single-row t1254 run with CONSTANT ship hash
ede612 every ~150 s, each followed by a 14-row t1255 run whose ship hash is
NEW per cycle; frozen single run (hash 3fb209ad, 403 rows) from 21:58:33 =
the title-menu transition. t265's slot-30 tail-running feed STANDS as a
bug witness of the restored campaign, not of production. I3 (15:45 death)
ROOT CAUSE MEASURED: -time-limit expiry (07:46 launch + 28800 s); watch.out
gap 15:45->18:35 brackets the unnoticed window — t267 scope updated. PROBE
LAW AMENDMENT: full-frame diff on an animating screen (starfield, 306k px)
is ALWAYS "ALIVE" — drive-log mid-window ALIVE readings were false
positives; liveness = c-leg overlay toggle or RAM needle only. CROSS-INCIDENT
common engine state: NOT identified from disk (honest negative; popup-queue
hypothesis unsupported — I2 had no popup). Rewrite note: vendor can hang
with emulator alive; rewrite watchdog per t250 law c-leg version. THREE
stale playcap watchers alive at session end (524207/524532 stale, 535187
current — reap in t267). NO OQ CLOSED (bug-class RE; 005/016/019/021 stay
open). Docs: selfplay.md t266 block, REFUTED-ROUTES t266, _wip_t266.md.
NEXT = t267 VERBATIM (+ the t266 scope feed above).

LANDED t265 (2026-11-02): OQ-019 DRIVE-CORPUS FLIGHT MINING DONE — the t193
st4 residue ROUTE is MEASURED-DEAD and a REFUTED route was filed. On the t261
production drive (1086->1236, ~150 real turn advances, softlock window
21:38-23:06 excluded; tools scripts/r265_st4_magnetron.py + r265_pass2.py +
r265_pass3.py + KEEPER r265_keeper.py all RC=0): (1) 21 multi-row st4 runs
spanning >=1 turn advance have net displacement 0.00 with CONSTANT [+0x59]
— st4 is a DWELL state; every big mover is a 4<->5 frame switch; the
in-system march is unobservable at 10 s ring cadence (sub-ring instrument or
drop). (2) t189 LANE-STEP LAW RE-CONFIRMED on a second independent corpus,
ZERO violations: consecutive-turn st5 |dx| == step0 or step0/3,
step0 = float(u16[+0x8]+u16[+0xc]) same window (2,400+ pairs); /3 branch is
lane-scoped (6 mixed handle values = route re-points + pool recycling).
(3) TURN-ATOMICITY: same-turn st5 x-deltas EXACTLY 0.0 in 17,595 pairs —
t187's "4.67 = three sub-steps" reading is DEAD (4.6667 = single step);
entry-x all multiples of step (S21 x=k*step corroborated). (4) MAGNETRON
ZERO-CENSUS with a sharp instrument (landings must be off-32-grid in x AND z,
P(false neg) <0.1%/landing): 0 of 6,184 st4 rows off-grid, y mod 32 == 0 all;
use-site law stays static-cited S19 T3. (5) t266 FEED: the only st4 mid-turn
moves sit INSIDE the softlock window — TURN-FROZEN-BUT-TAIL-RUNNING tell.
Banked: ships.md S24 (authoritative law text), _wip_t265.md S1..S4,
REFUTED-ROUTES t265 entry, OQ-019 row STATUS t265 (STAYS OPEN strict-close —
the route died, no law closed, no rewrite default changes). Harness lesson
banked in the pass3 header: lexicographic wall-string bucketing drops
post-midnight ranges — bucket by mtime_ns. NO OQ closed this iteration
(005/016/019/021 open); gate 0, ledger audit OK, index OK; :9 untouched
(alive, PID 535172); NEXT = t266 VERBATIM.

LANDED t264 (2026-11-02): REWRITE HUD LAYOUT WIRING SHIPPED — the t252/t253
rail + ship-design measurements are CODE + PINS in rewrite/src/ui/
hudlayout.{h,cpp} (pure, no SDL; 146 tests 0 fail, +5 hud_*_t264; CMake:
ascend_ui + run_tests; poppanel template followed; ui-runtime.md §2c NEW;
working log docs/re/_wip_t264.md S1..S3). MEASURED THIS SESSION (primary
sources re-parsed, not dossier-inherited): (1) windows.txt block-parse
(132 TYPE blocks) — all six rail rects match §6a verbatim and the
SENDPARAM1==target-STATE law EXTENDS beyond the dossier's two checked
pairs: 10 STATUSWND (line 1020) / 18 FLEETWND (1725) / 20 RESWIN (1763) /
14 INTELSCREEN (1109), RACES 7 = the '1 7' menu class [inferred general
law]. (2) SHAPEITEM lines exact: 1starmap.shp frames 3=Research 4=Ships
5=Planets 7=Special; RACES WINITEMS 1 / Intelligence WINITEMS 0 — iconless
buttons are representable by construction (nullopt, not a fabricated
frame). (3) gizmos.txt re-parse: 76 records, cat counts {10,6,5,6,5,44},
categories CONTIGUOUS in file order 0..5 — the GIZLIST order law ==
gizmosByCategory, and the join test asserts per-tab sizes + live GIZLIST
head names (Mass Barrage Gun / Ion Wrap / Tonklin Motor / Tonklin
Frequency Analyzer / Proton Shaver / Lane Blocker). (4) TAB MAP pinned 6/6
+ HULL(50)->-1 + msg56->-1 + inverse total; non-derivability pinned
combinatorially STRONGER than the dossier: naive cat==msg-51 holds ONLY
for {51,52,55}, deviations EXACTLY {53,54,57} (the swapped pair AND the
msg-56 gap at SPECIAL). Mutation probe: flipping 53->2 in the MODULE fails
11 checks across 3 tests; reverted, green. HONEST: the RACES/Intelligence
14 px overlap resolution (->Intelligence) is [inferred] z-order pinned as
law (file has no draw order; no live click ever landed there); task text
said "cite docs/re/ui.md" — the dossier blocks are actually in
ui-runtime.md §6a/§6c, cited there; NO sprite drawn (ui.cpp untouched,
OQ-005 scope unchanged); NO OQ closed strict-close (005/016/019/021 stay
open, ledger untouched). :9 untouched (zero clicks/turns, no loadstate);
no sitting (r1_t85g_sitting.py not run). NEXT = t265 VERBATIM (OQ-019 live
mining on the t261 corpus).

LANDED t263 (2026-11-02): REWRITE POP-PANEL SHIPPED — population panel
visualization law is CODE + PINS in rewrite/src/ui/poppanel.{h,cpp} (pure,
no SDL; 141 tests 0 fail, +4 poppanel_*_t263; docs/re/_wip_t263.md S0..S8 +
ui-runtime.md §2b NEW). MEASURED THIS SESSION (not inherited): (1) gwshare
entry census — 45 .shp entries among non-blank lines (blank-separated + 0x1a
terminator: the physical line 63 of entry #44 is why "line-1" mis-states the
slot law); entry #44=17np / control #41=14intel pinned against the t254
live-RAM chain ([0x6fd9c]=44 -> cache 44 verbatim == 17np). (2) 17np dims
census (V/A law): 9 records, k1 9x9/k2 7x9/k3 8x8, all walk canonically.
(3) CONTENT FIXTURE on game.pal (6-bit v*255//63): k1 red-body 25px + BLUE
tool 9px (idx 80-85/105-107); k2 yellow idx89 x12, ZERO blue of 30 painted;
k3 interior 16/16 centre bytes NEVER painted = hollow ring byte-confirmed —
the icon<->role binding is now executable (mutation probes: swap SEL1/SEL2 ->
103 failures; swap k1/k2 dims -> conformance gate fails on the real file;
both reverted). (4) RAW ASM re-read (work/t198_planwin.asm) confirms the
0x3ce39 loop verbatim (cap +0x4a exit jge; incl at ==+0x4c then ==+0x42;
[0x6fd9c]; +0x0a pitch; idiv-10 cmp 9) and adds an unrecorded per-case setup
CALL 0x5e940 with 0xf2/0x96 [semantics unverified] — layout is
origin-parameterised, default widget-local (EDI=EBP=0 at 0x3ce59). (5) PANEL
ARITHMETIC: windows.txt:1587 PLPOP 355,7..454,106 == 100x100 == exactly 10
rows x 10 slots x 10 px, and storedCapFor's clamp to 100 (campaign.cpp:811)
equals that capacity — paint cannot overflow the panel; cap 39 -> 4 rows
matches the t254 Vega IV live census (cell 39 never painted). Selector->
record = IDENTITY (t254 sel table 9/9). HONEST: role NAMES stay the cited
chain (asm band order + t254 vision/player corroboration), the pixel census
is corroboration made executable not an independent semantic proof; no
sprite DRAWN anywhere (ui.cpp untouched, OQ-005 scope unchanged); NO OQ
closed strict-close (wiring cited law; 005/016/019/021 stay open, ledger
untouched). :9 untouched (zero clicks/turns, no loadstate); watcher timeline
growth = parked-campaign churn, no sitting (r1_t85g_sitting.py not run).
NEXT = t264 VERBATIM (layout wiring; poppanel is the module template).

LANDED t262 (2026-11-02): OQ-021 CENSUS/INVENTORY TRIGGER DISCRIMINATOR —
FLEET-CENSUS HYPOTHESIS MEASURED-DEAD BOTH LEGS on the driven corpus
(score.md S13 + _wip_t262.md S1..S4; KEEPER tools scripts/r262_census_disc.py
= segment-aware 2x2 contingency + functionality join, whole-file single pass;
scripts/r262_legA.py = leg-A deep field check; outputs
work/r1/t262_census_{full,early}.out). MEASURED 808 boundaries (Oct run) +
207 (Oct-29+ run) under the NEW per-SEGMENT trust law (session split >600 s
PLUS splits at reload class V==0@turn<=wm and foreign-lineage class
turn-drop>2 — generalizes the t255 pitfall; the t261 softlock oscillation and
re-drive land in separate segments). RESULTS: leg A fails — 27 of 37 V-change
boundaries have byte-identical fleet inventory (n_live, per-owner counts,
design multiset, gizmo-ring multiset), INCLUDING the t258 doubling
(t911->912 V 11->22) and halving (t1140->1141 V 22->11) shape clues — the
fleet never doubled/halved, V did. Leg B fails — 121 inventory-change
boundaries with V static. FUNCTIONALITY KILL: 18/149 inventory sigs carry
MULTIPLE V values within one continuous lineage; worst case ONE sig
(n_live=37, {0:23,1:7,2:7}) carried V in {12,15,16,19,21,21,22} across driven
turns 1255..1335. Conclusion banked: V is NOT a function of the ship census;
the End-Turn recompute reads NON-FLEET state (economy/garrison/research class
— none in the watcher schema; watchpoint ask stays user-gated). leg-A detail:
ship targets moved 27/27 but order-churn is ubiquitous (539/808), so
correlation-not-cause exactly as t258 for order features. PRE-FLIGHT: t261
re-drive was alive (t1198) and COMPLETED during the session — TARGET REACHED
1236 23:37:12, banks bank-t261-t1236 + bank-t261-final-1236; game parked t1236
(PID 535172), zero clicks by this session, no loadstate (REFUTED honored).
Pitfalls banked: ns-vs-s epoch units in corpus gates; close_seg must flush the
pending snapshot; a REJECTED compound terminal call may still have applied its
sed — grep the file before editing on top. NO OQ CLOSED (strict-close: a
hypothesis died, the row lives; threshold unobserved, driven max V=22@t1301
decayed 21@t1335). NEXT = t263 VERBATIM (pop-panel rewrite, pure code).


LANDED t261 (2026-11-01): t1255 RESTORED-STATE DRIVE ROUTE REFUTED (input-dead
ON LOAD — the softlock class lives INSIDE the save; REFUTED-ROUTES t261 block;
t260's structural verification cannot see input liveness — NEW LAW: probe
'c'-toggle on any restored state before planning a drive); PRODUCTION :9 hit
the bug class MID-DRIVE at 21:38 (healthy t1111 banked bank-t261-t1255 slots
53/54 capture the 10-second flip to a t1255/V=14 profile with ZERO loadstate
log lines, then title menu, then input-dead there; ring oscillates t1254<->1255
while the loop mutates the turn site at 89.7% CPU — 4th incident, prime t266
material; mechanism [unverified], human-sitting hypothesis weakened: the VNC
"client" is an Oct-16 zombie, bytes_acked frozen); RECOVERY SOP EXECUTED
(bank->SIGKILL->vnc start->Return-to-Game: resumed t1086 23:05, re-drive to
1236 launched, session-bound — PRE-FLIGHT in NEXT). HARVEST LANDED: score.md
S12 (+0x15 star-set growth table from the DRIVEN corpus; V=23 constant while
stars15 grew 1087->1111 — S6 non-join re-corroborated; OQ-021 STAYS OPEN) +
combat.md §5 (20 non-war change-hits, ZERO volleys/destructions at engagement
scale — OQ-016 STAYS OPEN, honest negative). TOOLING: KEEPER
scripts/r261_harvest.py (mtime-epoch corpus gate; wall windows are
cross-day-poisoned); BUGFIX r1_t251_mine.window_rows off-by-one (quote char in
the wall slice — the trust=False "newsession" pass returned ZERO rows since
t251; every earlier such pass was VACUOUS — re-run any that mattered);
r1_t261_session.sh + r1_t261_load.py (isolated :8 loadstate bring-up, md5-gated,
keep-save mode for recovery); r1_t261_drive.py env-parameterized one-code-path
driver. pkill/pgrep -f self-match footgun fired twice more (killed only my own
shell both times) — use ps|awk|kill. NO OQ CLOSED (strict-close: honest
negatives only). Bank new: t261-final-1096, t261-t1255, t261-soft1255,
t261-prod-titlesoft. NEXT = t262 VERBATIM (census discriminator on the driven
corpus; pre-flight: re-drive liveness).

LANDED t260 (2026-11-01): GUI-LOADSTATE RESTORE EXPERIMENT SUCCEEDED — t1255
IS ALIVE AGAIN IN A RESTORABLE PROCESS; HEADLESS RESTORE CONFIRMED DEAD —
MEASURED on isolated display :8 (production :9 t1086 session untouched: ring
kept writing, RESUME.GAM still 5b382afb/Oct-29, timeline current at 20:31):
Capture-menu "Load state" click (xsend synthetic BUTTON events drive the SDL2
menu bar; rows located PROGRAMMATICALLY via scripts/r1_t260_menulocate.py
neutral-dark census — 16-bit txt gotcha documented) -> "Loading state from
slot: 60" + "[20:19:13]: Loaded. (Slot 60)" -> SCREENSHOT shows the campaign
map, turn readout 01255. STRUCTURAL PROOF: re-save from the loaded process ->
watcher decode of the round-trip ZIP (banked work/r1/bank-t260-roundtrip-1255/)
reads turn=1255 V=14 == the frozen t1255 row. Bank 0024340d verified intact
before AND after. TL-TIME-BOUNB LAW (measured both ways): a loading process
carrying -time-limit expels the loaded state within seconds -> NEVER pass TL
to a loadstate target. Menu census: state items live ONLY under Capture (Save
state F12+S / Load state F12+L); no CLI flag, no autoexec cmd, no [hotkeys]
section; conf-only (saveslot+forceloadstate) sets the ACTIVE SLOT only;
mapper editor refuses mid-program ("Another program is already running.");
xsend keys carry state=0 so chords are NOT deliverable — clicks only. All
negatives banked to REFUTED-ROUTES (t260 block); full law + bring-up recipe to
docs/re/selfplay.md t260 block; _wip_t260_loadstate.md holds the raw sequence.
HONEST NOTES: t1255 death-frame ZIP loss (324d2d75, pairing-session churn)
does not block t261 (bank copy is the source); attempt-1 exit MECHANISM is
[unverified] (no TL value found in the ZIP members) though the operational law
is clean; NO OQ closed strict-close this iteration (t260 is tooling/route
work; the ledger is unchanged and audit-clean). NEXT = t261 VERBATIM (base
t1255 restored, target 1405).

LANDED t259 (2026-11-01): SENTINEL ADJUDICATION FOUND THE ENVIRONMENT DEAD —
WITNESS PIPELINE DARK; LAST OFFLINE OQ-021 HANDLE MEASURED-CLOSED (_wip_t259
S1..S7; docs/BLOCKED.md t259 ADDENDUM; OQ-021 annotated, STAYS OPEN — strict
close: nothing closed, honest negatives recorded). MEASURED: parked :9 dosbox-x
process DEAD (pgrep -x empty) with timeline/ring/dosbox.log frozen at the SAME
second 15:45:08 (60.sav t=1255 V=14); Xvfb+x11vnc alive; cause UNVERIFIED
(journalctl zero 'killed process' lines today, dmesg unreadable; [inferred]
memory-spike class per t251, r258_vdisc window 15:34-16:20 — not proven).
Consequence banked: passive trigger A is IMPOSSIBLE while dark (not merely
unobserved); ask (A) "keep ending turns" is dead as authored; a relaunch
resumes from RESUME.GAM which MEASURED == Oct-29 backup md5 5b382afb (the game
never wrote a newer resume slot) — t1255 exists ONLY as savestate ZIPs;
loadstate path unexercised. TRIGGERS RE-CENSUSED: zero witness rows in tail
400KB, zero playcap-* dirs, no steering, no ask answers. OFFLINE: same-turn-
different-V sav-pair RAM-diff route (complement of t212 write-site zero) run
over ALL 122 banked/ring savs via scripts/r259_savpair_census.py (KEEPER;
bounded RSS one-Memory-at-a-time; work/r1/t259_savpair.out): PAIRS = NONE
(turn set {1086:V0,1096:V23,1254:V23,1255:V14}); cross-bank diffs confounded —
route CLOSED negative. HARNESS findings banked: (a) EIGHT r1_playcap_watch.py
procs hold O_APPEND fds on the timeline (fdinfo census; all append at EOF;
tail-400KB = 14 rows/9 UNIQUE) — t258 corpus safe via (file,mtime_ns) dedup
(misread caught and corrected mid-session, honestly), but ~7x write cost +
~700MB RSS; orphan retirement = user ask; (b) scripts/r1_t259_sentinel.sh is
the new ~1-call read-only sentinel census (game-alive FIRST, timeline heartbeat,
witness, playcap dirs, watcher count, RESUME md5, ring newest); (c) probe law:
timeline tails must be byte-capped AND cut to fields BEFORE printing (a raw
uniq -c piped ~150 KB of ship_raw). NEXT = SENTINEL v2 verbatim; DO NOT
relaunch the batch. Live :9 untouched (already dead); no capture run; gate 0,
ledger audit OK (open = OQ-005/016/019/021), index OK.

LANDED t258 (2026-11-01): OQ-021 END-TURN-RECOMPUTE DISCRIMINATOR EXECUTED —
CANDIDICIDE COMPLETE, SURVIVORS NONE (score.md S11 + _wip_t258; queue drained
-> WAIT-TRIGGER sentinel + t258 USER ASK banked BLOCKED.md; no OQ closed —
strict-close: an exhaustive negative is an honest keep-open, not a close).
Instrument scripts/r258_vdisc.py (KEEPER; one streaming pass = boundary dump +
candidicide + per-session trajectories; work/r1/t258_vdisc4.out). MEASURED
303,625 lines / 53,412 trusted V!=0 rows / 25 sessions: 0 mid-turn V changes
(t255 §1 re-corroborated with the fixed predicate); 38 V-change turn boundaries
vs 795 V-stable control — territory counts die BOTH legs (1/38 + 1-2 stable),
all 12 per-owner order-kind features + alive counts die BOTH legs (best A_k4/
A_k5 33/38 vs 277-278 false positives), closed-form aggregates fit at most
10.6% of rows (coincidence; first-miss t37 V=1 zero-ships). NEW FACTS: 3rd
independent determinism witness (S14/S15 replay 14->12->14 at t1169-71);
V==0 = LOAD-CLASS not turn==0 (33 session-turn pairs, turns 692..1254); shape
clues 11->22 doubling + 22->11 halving banked (per-star floor/threshold over a
rebuilt quantity, [inferred]). CORPUS STILL HAS ZERO V>=25 rows and zero
selector arms — threshold unobserved; rewrite >1/2 (campaign.cpp:2093) stands,
consistent with every frame. Instrument-hygiene laws banked (_wip_t258 S2/S4):
brace-deficient fast JSON slices die "Extra data: line 1 column 4";
except-swallow + isinstance guard SILENCES a parse bug (none_census caught it);
verifier agreement is VACUOUS when both sides return None — assert non-degenerate
content. Live :9 untouched (t1255 parked); no capture run. Gate 0, ledger audit
OK (open = OQ-005/016/019/021), index OK; NEXT = WAIT-TRIGGER sentinel verbatim
(IDLE_GATE=1 or no relaunch; re-arm recipe in the sentinel + BLOCKED.md ask).

LANDED t257 (2026-11-01): WATCHER SCHEMA + DAY FIELD — "day" PURE ALIAS LIVE
(selfplay.md "t257" block + _wip_t257.md S1..S5; queue drained -> NEW QUEUE
authored per AFTER-DRAINS). scripts/r1_playcap_watch.py process() emits
d["day"]=d["turn"] (t249b law: no second RAM read — none exists); schema
16->17 keys, docstring records pre-t257 rows lack the key (consumers:
j.get("day", j["turn"])). r214_triage: canonical_shape() folds day out so the
16/17-key MIXED-SHAPE WINDOW (expected while orphan pre-t257 watchers live —
retirement stays the user's call, STATE pairing note) counts as ONE schema for
multiplicity math; raw shapes + day/turn agreement printed separately.
VERIFIED: scratch --once on banked t251 savs (17 keys, day==turn==1255); live
relaunch — sitting pair 479981/479983 /proc-validated + reaped, replacement
detached ppid-1 (work/r1/playcap/watch-t257.pid), first live day-rows
{53,54,55}.sav 15:14, 7/7 agree, 0 disagree. Harness laws banked: watcher
relaunch streams the whole timeline to rebuild `seen` (~2-3 min at 7.4 GB,
bounded RSS) before its first emit — "watch: start" in watch.out is the
liveness signal, not row presence within 30 s; terminal background=true
processes die with the session — detach via Popen(start_new_session=True).
Queue-text correction banked honestly: r214_triage never ASSERTED one key
shape (it censuses), so the queue's branch-2 trigger did not fire. NO rewrite
change, no pin (schema not law, t256c precedent); NO OQ closed (strict-close:
harness plumbing closes nothing; 005/016/019/021 stay open, ledger untouched);
live :9 untouched (zero clicks/turns, still t1255 parked). Gate 0, ledger
audit OK, index OK; NEXT=t258 verbatim.

LANDED t256c (2026-11-01): AI GAP ROW 16 DISPOSITION — AGGREGATE MODEL
ACCEPTED PERMANENTLY, BACKED BY THE FIRST FULL PER-SHIP ORDER-STATE CENSUS
(no ledger row closed — strict-close honored; OQ set unchanged 4 open; OQ-019
ANNOTATED with the census and stays OPEN). Instrument
scripts/r256c_shipstate.py (KEEPER; streams the watcher's per-slot ship_raw
177-u16 window; SINGLE-PASS — buffering decoded rows on the 7.35 GB corpus is
the t251 OOM class; sessions/watermarks work unbuffered because the timeline
is append-ordered). MEASURED 62,762 trusted rows / 25 sessions / t240..1335:
live order-kind set is EXACTLY {1..5} (kind 0 only on dead slots — imm0
0x24a00 command-clear law corroborated); AI holds kind 2 ZERO times (kind 2 =
player-command issuer 0x3ca60); AI travel/arrival pair kind4<->kind5
symmetric 416/416 (0x220a8/0x21f58 observed live in self-play for the first
time); retreat-downgrade 0x220f2 fired 143x (both owners); Invasion Module
0x49 ring carriers in 480 distinct ships (ring = bytes at +0xab stride 7,
count dword +0x15a); POWER/MOVES nonzero for ~all live slots (t179 P1
tie-break inputs banked). kind changes = 1,938 of ~1.8M slot-pair obs
(0.107%). HONEST CAVEAT: sticky_kept=1,160,582 does NOT prove stickiness —
the parked t1255 ring re-samples identical state every 10 s. DISPOSITION
rationale (a)-(d) banked ai-dossier.md S11 NEW: scope mismatch is the OQ-019
per-ship build not an AI task; the aggregate projection is NOT observably
distorted in captured play (unlike pre-wire rows 4/12); a guessed per-ship
layer would drive never-witnessed arms (kind-2 0 obs, ACT=2 17 obs); the
firing laws stay cited verbatim in §5 for a future OQ-019 build — remainder
is ENGINE BUILD. Row 16 label "GAP (largest)" -> BOUNDARY + priority-read
paragraph updated. NO semantic rewrite change: campaign.h ShipInTransit
carries the boundary comment (no silent stub); NO pin added (a pin would
freeze a boundary, not a law). Tool pitfalls banked (_wip_t256c): ship_raw
sits at line offset ~3200 (find+bracket-depth, head/tail miss it); ring is
BYTE-odd so rebuild bytes via struct.pack from the u16 window; oc_of must
treat owner 0xffff/0xffffffff as DEAD before the PLAYER/AI split. Live :9
UNTOUCHED (zero clicks; ring kept banking; still parked t1255). gate 0, 137
tests 0 fail, ledger audit OK rows=19 open=OQ-005/016/019/021, index OK;
NEXT=t257 (day-field, with the t249b day==turn alias resolution folded in —
deliberate deviation from verbatim, recorded in the QUEUE note).

LANDED t256b (2026-11-01): AI GAP ROW 12 DISPOSITION — TWO-PARTY PROJECTION
ACCEPTED PERMANENTLY, BACKED BY THE FIRST FULL LIVE n x n MATRIX CENSUS (no
ledger row closed — strict-close honored; OQ set unchanged 4 open; the census
is MEASUREMENT that INFORMS the disposition, it closes no OQ). Instrument
scripts/r256b_relmatrix.py (KEEPER; streams the watcher's "relation" field —
the full matrix was ALREADY banked per slot, no dig needed): 65,751 unique
rows / 24 sessions / per-session watermark. MEASURED: state census off-diag
{0:118268, 1:539740, 2:90992, 3:136}; AI-AI cells ever-held {0,1} ONLY (all
6 directed cells, every session entry); all 34 0->1 transitions RECIPROCAL
with att:=issuer START_ATTITUDE (== §13.4b bl=0 seeding writer); post-contact
AI-AI attitude bands 256..470 over 348,936 obs NEVER crossed the issuer's DW
(200/210/290) or ACCEPT_ALLIANCE (570/600/600) line — thresholds STATIC in
RAM (min==max) — the inter-race ladder is real in state space but DORMANT in
every captured lineage (2nd independent lineage corroborating §11).
DISPOSITION rationale (a)-(d) banked diplomacy.md §20 NEW: rewrite consumers
of AI-AI cells exist only at player-attacker call sites (t204) or are static
clamps (t256); guessed AI-AI dynamics would ADD never-witnessed behaviour;
firing LAW already cited statically (§13 + rungs 0x44c1a/0x44c71/0x44ce0) for
any future OQ-019-boundary build — remainder is ENGINE BUILD, not RE unknown.
Row-12 label rewritten in ai-dossier.md gap map. NO rewrite code change
(war_[][] already full-matrix; dipState_ deliberately stays AI->PLAYER).
Tool pitfalls banked (_wip_t256b S4): relation sits at line offset ~28800
(after 28 KB ship_raw — head/tail slices MISS it); nested values INDENTED
(int(slice.strip())); "n" precedes "states" (derive n=len(states)). Live :9
UNTOUCHED (zero clicks; ring kept banking; game still parked at t1255 on the
planet screen). gate 0 (ran twice, incl. finish-sequence), ledger audit OK
rows=19 open=OQ-005/016/019/021, index OK; NEXT=t256c verbatim.

LANDED t256 (2026-11-01): AI GAP ROW 11 (16 SA_ bodies) AUDITED + UPGRADED —
NO LEDGER ROW CLOSED (strict-close honored; gap map is a work item, OQ set
unchanged 4 open). ROW TEXT WAS STALE (claimed Repel/BlockStarLanes filed
no-ops — both wired long before t205); restated with per-body citations.
FOUR BODIES UPGRADED TO CITED LAW (aicode.md §6.3 t99): SA_FreeResearch
0x4414e queued-target-ONLY (uncited "cheapest if none" leg REMOVED);
SA_StealResearch 0x43eec target-reset leg ADDED (stolen==own target ->
re-pick); SA_IndustryBoost 0x4418e per-planet buildAcc+=100 behind the
pending gate (old ind_+=20 = WRONG OPERAND, ind_ is the ship budget);
SA_CauseWar 0x440b5 CEILING law via new pure static Campaign::hatredClamp
(third-party x!=r clamped to the belligerent's DECLARE_WAR word; player-
projection documented; the same-turn declare-war cascade of a clamped
onlooker = the vendor effect, measured in probe). Remaining bodies labelled
honestly in row 11: model-level abstractions (OQ-019 boundary) vs mechanism
divergence (ForcePeace, row-12 family). Pins x3 (137 tests 0 fail); kNotes
CauseWar/IndustryBoost lines updated; blast radius MEASURED nil on gate
seeds (specnums 17/19/20 never in default AI slots 0..5): seed 2024 Control
t1255 + seed 42 Extinct t979 verbatim. Pin pitfalls banked (_wip_t256 S4):
mood+chooser cascade kills tight attitude bands; completion-reset bounds
buildAcc below any +N delta — pin via control differential. Debug pattern:
standalone g++ vs libascend_core.a, -DASCENDANCY_SOURCE_DIR=<repo root>.
Docs: ai-dossier row 11 rewritten, abilities.md 5 rows updated,
docs/re/_wip_t256.md S0..S6. gate 0, ledger audit OK, index OK;
NEXT=t256b (gap row 12) verbatim.

LANDED t255 (2026-11-01): OQ-021 WRITER RE-PROBE LANDED — NO ROW CLOSED
(strict-close honored; OQ-021 ANNOTATED + residue NARROWED, stays open).
Full-corpus behavioural law (scripts/r255d_persession.py, 65,380 deduped rows
/ 25 sessions / turns 37..1335, PER-SESSION trust): ZERO mid-turn V changes
(39 boundary changes, 0 same-turn) -> screen-open recompute REFUTED; V==0 at
every session's load turn on FULL active worlds (not title class) + same
loaded state reproduced V=23@t1087 twice -> V is NOT save-persisted and the
End-TURN recompute is deterministic in the world state; same turn t1254 read
V=14 vs V=23 across lineages (any=36 both) -> V != snapshot, lineage-history
dependent; NO V>=25 and NO selector arm anywhere -> Control boundary still
unobserved passively. Banked docs/re/score.md S10 (+ _wip_t255.md incl. a
self-caught WITHDRAWN claim: ring sampling hid turns 1097..1254 during the
6-min drive — "flat 167 turns" was an artifact). Harness laws banked: watcher
appends systems_*/mtime/wall at line END (head-parse blind there);
'"file": "' is 9 chars — r1_stream.py header fn is silently '' (dedup OK on
mtime); global stale-echo watermark drops deliberately-re-loaded lower-turn
campaigns -> per-session trust required (r255d). Tools scripts/r255{,b,c,d,e,f}*
.py (d/f are the keepers; b dead, c superseded by d). gate 0, ledger audit OK,
index OK; NEXT=t256 verbatim.

LANDED t254 (2026-11-01): POPULATION-SLOT LIBRARY IDENTIFIED + PLANITEM RULING
(no ledger row closed — strict-close honored; OQ-005 ANNOTATED with the
pop-slot closure chain, STAYS OPEN; shp.md S23 NEW + planets-ui.md S4
corrected in place + ids.tsv +11 rows; tools scripts/r1_t254_sheets.py +
r1_t254_pi_match.py). (1) THE CATCH: pop-slot icon library = 17np.shp, cited
live-RAM — u16[DAT 0x6fd9c]=44 (bank-t251-live1255/41.sav) -> cache slot 44
PAY=0x435400, verbatim 1.10 copy at +0x88 content-matches 17np.shp (control
slot 41=14intel.shp; slot == gwshare.txt line - 1, 45 entries); runtime
selector table sel 0..8 -> recs 0..8 9/9. IDs: k1 9x9 sideways red humanoid
=BUSY, k2 7x9 front-facing yellow =FREE, k3 8x8 hollow green ring =EMPTY —
player S19 testimony corroborated record-for-record. (2) GEOMETRY EXCLUSION
measured: dims census (u32 pairs at canonical V/A slots — my FIRST pass read
u16s and printed garbage; law restated shp.md S23.3) — planets.shp 11 groups
x 5-size ladder min 11x11, planitem min 24x23, planalNN min 47x47: ALL
excluded from the 0x0a PLPOP pitch; the t254 candidate list was structurally
wrong and the RAM chain beat it. (3) PLANITEM CONFIRMED (t244 hypothesis):
live PLBUILD icon 'Scientist Takeover' (item idx 34) == planitem.shp k34 1:1
sliding-window MAD 1.5, next best 42.1 — vision-first said k33 and was WRONG
(t254 pitfall banked: for icon identity use 1:1 pixel match, not vision, when
a live crop exists; vision misjudged because the crop included panel padding).
(4) LIVE leg: hazard check clean; STATUS button (553,145) -> planet list ->
row 2 click (200,105) -> Vega IV detail; pixel census 37 busy + 2 free + 1
unpainted cell (cap-sized array law holds); zero turn drift at 1255 (ring
tail-scan); game left PARKED ON THE PLANET SCREEN — Escape was sent
(xsend DOSBox-X key Escape) and did NOT unwind it (planet screen survives
Escape; t252 'Escape unwinds ONE level' applies to research/diplomacy
overlays, NOT PLANETALLOC — t255 note above updated accordingly). DAT_43508
pointer read returned zeros at
PL+0x42/4a/4c (0x26f3e5) — honest negative, field offsets NOT re-verified
(t198 law stands, read may need a different base/segment class). NEXT=t255
verbatim.

LANDED t253 (2026-11-01): LIVE SCREEN SWEEP 2 — FLEET + SHIP DESIGN (no row
closed — strict-close honored; OQ-005 ANNOTATED with the frame->role anchor set,
STAYS OPEN; dossier docs/re/ui-runtime.md §6c NEW + ships.md §7 corollary +
selfplay.md t253 laws; 1 tool scripts/r1_t253_screen.py = the t252 primitive
with OUT->work/screens/t253/; screens + _state.json there). PROVED: (1) the
SHIPDESSCREEN tab->gizmo-CATEGORY map measured 6/6 EXACT against gizmos.txt
category field and file order (WEAPONS=cat0 DEFENSES=cat1 ENGINES=cat2
SENSORS=cat3 ENERGY=cat4 SPECIAL=cat5) — and the map is NOT the SENDMESSAGE
order (SENSORS msg 53=cat3 vs ENGINES msg 54=cat2; msg 56 has no tab), so any
rewrite must carry a TABLE, not arithmetic; independent live corroboration of
ships.md §6's Ghidra category dispatch. (2) HULL (msg 50) is NOT a gizmo
category: press changed 1973 px confined to bbox x524-632 y7-76 (tab rows only;
GIZLIST 0 px) — hull-SIZE selector per help hull; where size choices render is
UNPROVEN (noted). windows.txt has SEVEN tabs, not eight — the "8" in
8SHIPDES.SHP is the name-table index. (3) FLEET row click laws confirmed
end-to-end vs help fleetwin: LEFT-click = jump to location (Escape returns to
the LIST), RIGHT-click (xsend click3) = ship contents display, whose measured
panel edges match SHIPDESSCREEN+GIZLIST rects (tab grid x478-639 y0-81 vs
windows.txt 485,7-632,76). (4) Header law "<race> (<N> Ships, <M> more
allowed)" = ship-maintenance allowance shown as HEADROOM; scroll arrows
measured at (620,63)/(620,453). (5) HAZARD DEFUSED: orphaned
`xmessage -buttons Yes:1,No:0 -default Yes` quit-confirm (PID 461872, PPID 1,
14 h older than the live dosbox) sat MAPPED on :9 — killed by PID only; NEW
PRE-SWEEP LAW: xwininfo -root -tree | grep -i warning must print nothing before
clicks; xsend's "REFUSING blocker window" line is a warning about ANOTHER
window and it still sends. SAFETY: 20 steps, ring turn HELD 1255 throughout,
NEXTTURN never clicked, no war/proposal/sell/dismiss; game PARKED back on the
galaxy screen (3471 px vs baseline == t252's 3452 blink noise floor). NEXT=t254
verbatim.

LANDED t252 (2026-11-01): LIVE SCREEN SWEEP 1 — RESEARCH + DIPLOMACY (no row
closed — strict-close honored; dossier docs/re/ui-runtime.md §6a/§6b NEW +
selfplay.md §5 bullet; 1 tool scripts/r1_t252_screen.py: click/key + root
shot + 640x480 crop@(80,100) + pixel-diff + ring-turn guard, run via
hermes-venv python; screens work/screens/t252/). SAFETY RECORD: 16 steps,
ring turn HELD 1255 through every step (NEXTTURN never clicked), no war, no
proposal, no abandon; option-row-1 (Goodbye) clicked from a MEASURED band
(bands 329-339/358-367/387-396, ~29 px pitch) and closed the negotiation
cleanly; game left PARKED on the galaxy screen (final2 vs baseline 3452 px);
game/ untouched (git status clean for game/; pristine user backup
work/r1/game/RESUME.GAM.user-oct29 md5 5b382afb intact; note: the LIVE
work/r1/game/RESUME.GAM is md5 f5ffb840 = the seed-commit copy of the
PRISTINE template, 81647 B — the "5b382afb ... never overwrite" note in the
PAIRING-SESSION NOTE refers to the user-oct29 backup; the live file is the
self-play scratch copy and self-play never Saves, so both are consistent).
MEASURED: (1) sidebar rects exact on live (click centers fired STATUS/RESEARCH/
RACES/Intelligence as windows.txt predicts); button icons ARE 1starmap.shp
SHAPEITEM records frames 3=Research 4=Ships 5=Planets 7=Special + 9-key
SHAPEFILE->screen map banked (OQ-005 W3-eyeball targets, codec still R2-blocked).
(2) RESWIN = NODE GRAPH (blue ring=discovered, gold=current) + right panel
"Current Project: Accel Energy Replenishment (15 days) Allows Lush Growth
Bomb"; pan-click (570,455) moved ONLY the minimap column (472 px, bbox
552-593 x 222-469; 2nd click 0 px = edge). (3) Species menu = sidebar overlay
("3 of 3 Species Known": Orfa/Ungooma/Extinct) + map portraits; race-row click
-> NEGSCREEN: ALIENDIP one dialogue line (band 252-262) verbatim raceNN.dip
DR_NoDipResponse with %m substitution ("How can we little %m help you?" ==
race11.dip:173); PLAYERDIP posture-dependent option list; Escape unwinds ONE
level per press (intel 82k-diff -> menu -> galaxy 3.4k). (4) INTELSCREEN/
INTELLIST: "Chamachies Intelligence", rows incl. self, Fleet/Colonies/
Discoveries as RELATIVE symbol counts (vision-read 10/12/6, 8/8/4, 6/6/5 —
flagged unverified per R13 pitfall), relation flags row-right. Ledger:
OQ-005 + OQ-023 annotated (both keep status), index untouched.
NEXT = t253 verbatim (ship design + fleet sweep, same laws).

LANDED t251 (2026-11-01): DRIVE 1086->1255 + FIRST POSITIVE ATTACK-CLASS
CASCADE WITNESS + WITNESS (b) LANDS (no row closed — strict-close honored;
record docs/re/selfplay.md "t251" section; working log docs/re/_wip_t251.md
S1..S6; 1 tool scripts/r1_t251_mine.py). DRIVE (hermes-venv python,
--target 1150 --max-presses 75): presses 1-10 advanced 1086->1096 (34
popups drained); presses 11-13 zero advance (probe input ALIVE 306,624 px);
press 14 ring JUMPED 1096->1255 in <=22 s — one click cannot advance 159
turns, so a LOAD happened inside the modal chain the drains were closing
(candidate [unverified]: a resume dialog confirmed into the Oct-29 t1254-era
state); drive exited 0, zero softlocks, recovery never fired. Vision on
work/screens/t2/drive_final_t250.png: healthy galaxy screen, readout 01255.
Banks: bank-t251-predrive (20 slots @1086), bank-t251-live1255 (20 @1255);
live-copy resume.gam md5 5b382afb UNCHANGED. WITNESS MINING (trust=True per
t214 law; watermark law banked: after a mid-campaign LOAD the new session is
INVISIBLE to trust=True — mine post-rewind windows trust=False + wall
pairing, r1_stream's own caveat): (1) FIRST POSITIVE ATTACK-CLASS WITNESS —
t887 att[Minions][Chamachies] 324->284 EXACTLY -40 with state 1->2 WAR in
the same window, no other transition (t204 price + t208 chooser cascade
observed live; -40 == 2 committed weapons per t210). Honest MINUS: direction
attribution stream-ambiguous; the t205 victim mark is ABSENT everywhere
(bank-t1254 holds ONLY byte[0x48304+38]=0x1 = contact latch, first nonzero
byte ever); clamp target 280 NOT hit (284 = price, not clamp) — clamp
witness still absent, OQ-016 stays OPEN, row ANNOTATED. (2) WITNESS (b)
LANDS: t212's roots missed work/r1/bank-* — bank-t1254 all 20 slots V=23
with NINE byte[star+0x15] rows, live1255 V=14 with TEN; SEMANTIC NON-JOIN
measured (V!=ownP 23vs9/14vs9, !=occ, V==systems_full 0%, ==systems_any 10%
over 45,227 trusted slots); P7 single-owner-bit label KILLED (row 2 +0x15==
0x3 co-ownership); the 9 intra-turn V->0 dips all sit at session boundaries
= LOAD artifacts (feeds t255). OQ-021 ANNOTATED, stays OPEN (writer =
watchpoint class). Damage channel sharpened to a negative: 0 named-owner
disappearances; all 10 shield-agg drops = slot remap/garbage-owner class;
raw-window streak proxies INVALID (day byte +0x67 churn — trap banked).
Side effects on :9: the drive advanced the self-play campaign to 1255 (via
the unattributed load path); user save untouched; marker law honored (clean
exit removed it). Gate 0, LEDGER AUDIT OK rows=19 open=OQ-005/016/019/021.

LANDED t250 (2026-11-01): TURN-DRIVER v4 WITH SOFTLOCK DETECT + AUTO-RECOVERY,
VALIDATED LIVE (no ledger row moved: harness robustness is not an OQ row;
record docs/re/selfplay.md S10; working log docs/re/_wip_t250.md; 1 tool
scripts/r1_t250_turndrive.py). BUILT: v3 laws inherited verbatim; softlock =
input-dead AND ring-tail frozen except {wall,file,file_mtime_ns} over 20 s,
interrogated only after 2 zero-advance presses with drain==0 (popup-presence
logged, NOT required — t247 signature recurred without popup; sequencing
provides the safety the task text's popup-check stood in for: documented
deviation). Recovery = bank save/*.sav -> bank-t250-recovery-<ts>/, SIGKILL
pidfile-then-comm (never SIGTERM), relaunch r1_playcap_vnc.sh start,
Return-to-game (318,333) polling in_game, resume toward same absolute target;
SELFPLAY.marker written at start, removed on clean exit. PROBE LAW (measured,
kills the literal c-key-probe design): 'c' overlay is galaxy-screen-only —
healthy game on planet-list read c=0 px / Escape=153,672 px; on galaxy c=1,152
px. v4 probes Escape first. VALIDATION (live :9): --target 1096 from ring 1086
=> 10/10 presses advanced, 34 popups drained, TARGET REACHED exit 0, run log
work/r1/t250_drive_20261101-014141.log, ring now 1096, pre-drive ring banked
(bank-t250-predrive, 20 slots). HONEST NEGATIVE: the recovery branch never
fired this session (no softlock occurred) — only its primitives are individually
verified. Interpreter law: PIL lives ONLY in the hermes venv python. Gate 0,
ledger audit OK; side effect: live session advanced 1086->1096 (self-play,
RESUME.GAM untouched, marker law in force).

LANDED t249b (2026-11-01): DAY-COUNTER PINNED — DAY == TURN, MEASURED THREE
WAYS (no ledger row moved: the day readout is not an OQ row; strict-close
honored; docs/re/selfplay.md "t249b" section is the record; docs/re/_wip_t249b.md
S1..S6 working log; 1 tool scripts/r1_t249b_dayscan.py). PROVED: (1) SCREENSHOT
(vision on existing banked work/screens/t3/resumed_t247.png, live :9 at turn
1086): the only number-bearing string on screen is the big green 7-segment
readout reading "01086" — the turn zero-padded to 5 digits; the user's "day
1254" was this readout at turn 1254. (2) CENSUS: dword==turn in bank-t1254
intersects (20/20 slots) to EXACTLY 3 sites — member 0x254e98 == data X=0x12e10
(the turn dword itself) + two heap addresses (0xfd7268 per-entity block field;
0x100141c inside a sequential-id dword array 1238..1257 — NOT a counter);
u16==turn: ZERO data-seg hits; cross-session re-run on the live ring at t=1086
reproduces the shape (u32 intersection {0x254e98, 0x270248, 0x100117c}, last
two heap). No maintained day scalar exists at ANY stable data-seg offset in
both sessions. (3) SEMANTIC: vendor equates day==turn (t244 verbatim "52 per
day" research gauge, research accrues per turn). "Day %d" forensics: string is
from static.txt (ascend00.cob blob 20 @0x269d0 entry "// 17", loadwin.cpp
block), loaded verbatim into the RAM pool (member 0x253032); ALL-RAM u32
referrer census (calibrated on restree.txt->0x468d3) = ZERO genuine referrers,
the single nominal hit 0x252c74 is locale date-format ASCII "\xaa/%\0" —
false positive banked as a census trap. t257 DEPENDENCY SETTLED: watcher
timeline "turn" IS the day; a literal day key = pure alias, no second read.
Side effects on :9: NONE (zero clicks, zero turns; only pre-banked artifacts
read). Gate 0, ledger OK.

LANDED t249 (2026-10-31, next day 11-01 local): HEADER-PLANETS COUNTER FOUND —
SCREEN-OPEN SNAPSHOT LAW, MEASURED WITH A CONTROLLED LIVE EXPERIMENT (no
ledger row moved: OQ-005/016/019/021 untouched, strict-close honored;
docs/re/selfplay.md "t249" section is the record; docs/re/_wip_t249.md S1..S11
is the working log; 9 tools scripts/r1_t249_*.py). PROVED: (1) the header's
PLANETS number == u16[list+0x8c7], item count of a generic scrollable-list
heap object, reset+refilled with exactly {planets NAME+0x33==race} on EVERY
Planets-screen open (FUN_00051834 case 1; filter const DAT_0002b0ae ==
rec0+0x33; bound u16@dsx0x3a093=145), FROZEN between opens (program-wide
+0x8c7 writers: add 0x32eb6, resets 0x325b5/0x33015 only). (2) bank-t1254:
ONE sig-obj 0xfda074 count 102 == header EXACT (all 20 bank slots; set
{entry+0xac}==owner-recs 102/102). (3) LIVE: zero sig-objs in 20 pre-click
ring slots -> click sidebar Planets (553,145 window-rel) -> sig-obj count 80
in every post slot AND header renders "80 Planets Occupied, 26 Systems
Controlled" (work/screens/t3/planets_header_t1086_after_open.png). t248's
60-vs-80 anomaly = stale snapshot; "occupied==populated" REFUTED (80/80
owner-flag planets counted, no pop filter); why the older open saw 60 stays
UNRESOLVED (t1092 RAM rotated). (4) leg (c) closed: u16@0x131b4 = 60 at THREE
timestamps + ZERO absolute references in code — race-block-relative field,
not a counter. Honest negatives banked: entry-pointer-shape scans (0xcb and
0xc7 record-target hypotheses) were wrong instruments (entries are item
handles); widget anchor not found (torn down). SIDE EFFECT (disclosed): the
live :9 session now has the Planets screen OPEN with the stamped list (count
80) — zero turns advanced (ring still 1086), no in-game Save, user save
untouched. NEXT = t249b verbatim (day-counter dword hunt; sig-scan
instrument + live-experiment method now in house style). Gate 0, ledger OK.

LANDED t248 (2026-10-31): PER-PLANET OWNER TABLE FOUND — THE 102-PLANET LAW
HAS ITS CITATION (no ledger row moved: OQ-005/016/019/021 untouched, strict-
close honored; docs/re/selfplay.md "t248" section is the record; 8 new tools
scripts/r1_t248_*.py). PROVED: (1) planet table (stride 0x7b, name-anchored,
rec0 "Vega I" phys 0x26d07b) holds OWNER at NAME+0x33 (byte, 0xFF=unowned) —
structural proof: star+0x14 & 0x7f == OR(1<<owner over its planets), 50/50
systems keyed, ZERO violations at BOTH t1086 (live ring) and t1254 (bank);
static init signature in vendor resume.gam: exactly 7 records hold 0..6
(home planets), 144 hold 0xFF. (2) count(NAMED && owner==race0)=102 == header
EXACT at t1254 (hist {0:102,1:11,2:11,255:21}). (3) Ghidra FUN_00051684:
the header's SYSTEMS number is the star-table sole-owner loop (35+home=36
EXACT); the PLANETS number is a stored u16 via *(u16*)(*(obj+0xab)+0x8c7) —
a maintained heap-window value, NOT a table count. REFUTED: t247's star+0x5a
"colonised count" — it is TOTAL planet slots per system (sum=145=record count;
the 104-vs-102 delta was one unowned Fomalhaut II + one blank slot, not a
co-ownership split; co-owned stars each have all planets owned by bit-set
parties). HONEST NEGATIVE: the header's 60 @t1086 is NOT count(owner==race)
(=80): exhaustive predicate sweeps (123 offsets x 256 values, bit-k, u16/u32,
owner-AND) produced ZERO predicates hitting 60@t1086 AND 102@t1254; the
t248u16-intersection tool compared a t1086 slot vs t1254 (the header-60
belongs to t1092, RAM rotated) — caveat banked, NOT a refutation of a plain
counter. NEXT=t249 retargeted (header-counter address + writers; u16@0x131b4
folded as leg c) — deviation from the verbatim-queue rule is deliberate and
recorded in the queue row itself. Live session untouched (watcher banking,
:9 game at t1086+, user save md5 5b382afb verified absent from writes —
nothing this iteration touched game/ or the live session at all).


LANDED t243 (2026-10-31): ADOPTED THE t243h SENTINEL-FIX DELETION + THIRTIETH
CONSECUTIVE BYTE-IDENTICAL ADJUDICATION (NO ledger row moved — strict-close
honored; docs/re/_wip_t243.md S1..S5 hand-authored; no new tools). THE ANSWERS:
(1) Axis 1: r214_triage.py RC=0 at 03:21:36Z — all three TRIGGER-A baselines
equal (ns 1793294532100000000 / size 5721578066 / tail-md5 9054cc6c...; script
prints its own 'sitting delta: False'), zero comm-class dosbox/ascend.exe, tail
intact (400 rows / 0 bad json / turn 1086 / 275 distinct / one key shape).
Baseline age INDEPENDENTLY RECOMPUTED: session epoch 1793418871.8 ==
2026-10-31T03:54:31Z vs baseline 2026-10-29T17:22:12.100Z => 124339.7 s =
34.5388 h, monotone vs t242's 32.9877 h at 02:21:28Z (delta 5583.8 s == the
1h33m04s wall gap exactly); sitting script correctly NOT run (t152 trap).
(2) Axis 2: 1409 *.sav/*.gam under HOME (population unchanged since t216);
newest playcap/save/41.sav ns 1793294530.108 — bit-identical to t216..t242;
#2..#6 60/59/58/57/56.sav on the 10 s end-series cadence; gap re-measured
1.992 s (twenty-fifth consecutive) — watcher-death condition did NOT fire.
(3) ADOPTED WORK (this session's substance — control-plane, not ledger): the
dirty tree was exactly a 9-line deletion — the PAIRING-SESSION NOTE t243h
paragraph dc008fb had inserted FIRST under '## NEXT ACTION'. Wake selection
reads field 2 of the first non-blank line there, so the tag extracted was
'NOTE' — not a WAIT*/IDLE*/PARK*/steer sentinel — and trigger C self-armed on
NOTE != last_task: the t243h guard defeated by its own note, the same self-arm
class t243h claimed to kill. Verified BOTH states by running the loop's exact
awk: working tree -> WAIT-TRIGGER (never arms); dc008fb -> NOTE (arms). The
deletion is committed as-is; the note text stays recoverable via git show
dc008fb:docs/STATE.md and its substance lives in that commit message +
scripts/loop_one_task.sh comments. LAW BANKED (and restated in NEXT): notes
never go in the sentinel slot.
(4) Ledger: NO row closed or opened; OQ-005/016/019/021 stay OPEN (no sitting =>
witness classes unobservable; strict-close). OPEN-QUESTIONS.md untouched;
honest negative in _wip_t243 S3. Watchers unchanged; nothing killed
(supervised-session decision, USER ASK #3). Gate exit 0 + LEDGER AUDIT OK
rows=19 open=OQ-005/016/019/021 closed=15. STATE NEXT=t244 WAIT-TRIGGER
sentinel — the harness owns the next move, not a research iteration.


LANDED t242 (2026-10-31): NO SITTING — TWENTY-NINTH CONSECUTIVE BYTE-IDENTICAL
ADJUDICATION, ~4-CALL CAP HELD, DELIBERATELY CONTENT-FREE (NO ledger row moved —
strict-close honored; docs/re/_wip_t242.md S1..S5 hand-authored; no new tools —
r214_triage.py RC=0 at 02:21Z: ns 1793294532100000000 / size 5721578066 /
tail-md5 9054cc6c... all == TRIGGER-A baselines, script prints its own 'sitting
delta: False', zero comm-class dosbox/ascend.exe, tail intact 400 rows/0 bad
json/turn 1086/275 distinct; baseline age INDEPENDENTLY RECOMPUTED -- baseline
ns == 2026-10-29T17:22:12.100Z, session epoch 1793413288 == 2026-10-31T02:21:28Z
=> 118755.9 s = 32.9877h, monotone vs t241's 32.8125h at 02:10:57Z, delta
631.0s == the 10m31s wall gap exactly; sitting script correctly NOT run -- t152
trap) AND: save axis bit-identical to t216..t241 (1409 files, newest
playcap/save/41.sav ns 1793294530.108, #2..#10 60/59/58/57/56/55/54/53/52.sav
on the 10s end-series cadence, still OLDER than the timeline baseline --
watcher-death gap stays closed; gap re-measured 1.992s twenty-fourth consecutive
time) AND: NO new content manufactured -- t242 held the cap at exactly the two
axis calls, no new code path / no fd census / no static hunt / no open-marker
grep, and did NOT re-run ledger_audit out-of-band (no sitting => the open set
cannot have moved; gate exit 0 + LEDGER AUDIT OK rows=19 open=OQ-005/016/019/021
closed=15) -- none of the three steering overrides applied (no prepended note,
no OQ-019/OQ-005 ruling, no supervised-session grant) -- SCHEDULING FACT
(control-plane only, banked once per t218 law): twenty-ninth session re-armed
10m31s after t241 despite its explicit DO-NOT-RUN-ON-CADENCE clause; idle
sessions t238 01:46 / t239 01:53 / t240 02:02 / t241 02:10 / t242 02:21 are
~7-10 min apart = cadence-armed not trigger-armed; unfixable from inside an
iteration, remedy is in USER ASKS -- watcher population unchanged (wrapper 27772
bash/no-writer-fd + child 27774 + orphans 260988/290953/292085, no new orphans,
no retirements; nothing killed, supervised-session decision) -- NO row closed
(strict-close: no sitting => witness classes unobservable; OQ-005/016/019/021
stay OPEN; OPEN-QUESTIONS untouched; honest negative in _wip_t242 S3; nothing
beyond the two adjudication axes censused per t212 law; no static route re-trod
per t213 S7) -- docs: NEW _wip_t242 S1..S5 hand-authored (t226 generator-safety
rule holds) -- STATE NEXT=t243 TRIGGER-ARMED IDLE ('do not run on cadence') +
LANDED -- NEXT=t243 axes only (r214_triage.py + one save-axis find by ns) or
steering override, else one-line idle + stop -- harness owns the next move, not
a research iteration


LANDED t241 (2026-10-31): NO SITTING — TWENTY-EIGHTH CONSECUTIVE BYTE-IDENTICAL
ADJUDICATION, ~4-CALL CAP HELD, DELIBERATELY CONTENT-FREE (NO ledger row moved —
strict-close honored; docs/re/_wip_t241.md S1..S4 hand-authored; no new tools —
r214_triage.py RC=0 at 02:10Z: ns 1793294532100000000 / size 5721578066 /
tail-md5 9054cc6c... all == TRIGGER-A baselines, script prints its own 'sitting
delta: False', zero comm-class dosbox/ascend.exe, tail intact 400 rows/0 bad
json/turn 1086/275 distinct; baseline age INDEPENDENTLY RECOMPUTED -- baseline
ns == 2026-10-29T17:22:12.100Z, session epoch 1793412657 == 2026-10-31T02:10:57Z
=> 118124.9 s = 32.8125h, monotone vs t240's 32.6730h at 02:02:35Z, delta
502.0s == the 8m22s wall gap exactly; sitting script correctly NOT run -- t152
trap) AND: save axis bit-identical to t216..t240 (1409 files, newest
playcap/save/41.sav ns 1793294530.108, #2..#10 60/59/58/57/56/55/54/53/52.sav
on the 10s end-series cadence, still OLDER than the timeline baseline --
watcher-death gap stays closed; gap re-measured 1.992s twenty-third consecutive
time) AND: NO new content manufactured -- t241 held the cap at exactly the two
axis calls, no new code path / no fd census / no static hunt / no '| open |'
grep, and did NOT re-run ledger_audit out-of-band (no sitting => the open set
cannot have moved; gate stages ran both checks) -- none of the three steering
overrides applied (no prepended note, no OQ-019/OQ-005 ruling, no
supervised-session grant) -- SCHEDULING FACT (control-plane only, banked once
per t218 law and not re-printed as a finding): twenty-eighth session re-armed
8m22s after t240 despite its explicit DO-NOT-RUN-ON-CADENCE clause; idle
sessions t237 01:37 / t238 01:46 / t239 01:53 / t240 02:02 / t241 02:10 are
~7-9 min apart = cadence-armed not trigger-armed; unfixable from inside an
iteration, remedy is in USER ASKS -- watcher population unchanged (wrapper
27772 bash/no-writer-fd + child 27774 + orphans 260988/290953/292085, no new
orphans, no retirements; nothing killed, supervised-session decision) -- NO row
closed (strict-close: no sitting => witness classes unobservable;
OQ-005/016/019/021 stay OPEN; OPEN-QUESTIONS untouched; honest negative in
_wip_t241 S3; nothing beyond the two adjudication axes censused per t212 law;
no static route re-trod per t213 S7) -- docs: NEW _wip_t241 S1..S4 hand-authored
(t226 generator-safety rule holds) -- STATE NEXT=t242 TRIGGER-ARMED IDLE ('do
not run on cadence') + LANDED -- NEXT=t242 axes only (r214_triage.py + one
save-axis find by ns) or steering override, else one-line idle + stop --
harness owns the next move, not a research iteration

LANDED t240 (2026-10-31): NO SITTING — TWENTY-SEVENTH CONSECUTIVE BYTE-IDENTICAL
ADJUDICATION, ~4-CALL CAP HELD, DELIBERATELY CONTENT-FREE (NO ledger row moved —
strict-close honored; docs/re/_wip_t240.md S1..S3 hand-authored; no new tools —
r214_triage.py RC=0 at 02:02Z: ns 1793294532100000000 / size 5721578066 /
tail-md5 9054cc6c... all == TRIGGER-A baselines, script prints its own 'sitting
delta: False', zero comm-class dosbox/ascend.exe, tail intact 400 rows/0 bad
json/turn 1086/275 distinct; baseline age INDEPENDENTLY RECOMPUTED -- baseline
ns == 2026-10-29T17:22:12.100Z, session epoch 1793412155 == 2026-10-31T02:02:35Z
=> 117622.9 s = 32.6730h, monotone vs t239's 32.5253h at 01:53:43Z, delta
532.0s == the 8m52s wall gap exactly; sitting script correctly NOT run -- t152
trap) AND: save axis bit-identical to t216..t239 (1409 files, newest
playcap/save/41.sav ns 1793294530.108, #2..#10 60/59/58/57/56/55/54/53/52.sav
on the 10s end-series cadence, still OLDER than the timeline baseline --
watcher-death gap stays closed; gap re-measured 1.992s twenty-second consecutive
time) AND: NO new content manufactured -- t240 held the cap at the two axis
calls, no new code path / no fd census / no static hunt / no '| open |' grep,
and did NOT re-run ledger_audit out-of-band (no sitting => the open set cannot
have moved; gate stages ran both checks) -- none of the three steering overrides
applied (no prepended note, no OQ-019/OQ-005 ruling, no supervised-session
grant) -- SCHEDULING FINDING (the only one available to an idle session, and it
is a control-plane fact not a ledger fact): the harness re-armed a twenty-seventh
session 8m52s after t239 despite t239's explicit DO-NOT-RUN-ON-CADENCE clause;
consecutive idle sessions t236 01:30 / t237 01:37 / t238 01:46 / t239 01:53 /
t240 02:02 == ~7-9 min apart, i.e. cadence-armed, not trigger-armed. Nothing a
research iteration does can convert that; the remedy is in USER ASKS.
-- watcher population unchanged (wrapper 27772 bash/no-writer-fd + child
27774 + orphans 260988/290953/292085, no new orphans, no retirements; nothing
killed, supervised-session decision) -- NO row closed (strict-close: no sitting
=> witness classes unobservable; OQ-005/016/019/021 stay OPEN; OPEN-QUESTIONS
untouched; honest negative in _wip_t239 S3; nothing beyond the two adjudication
axes censused per t212 law; no static route re-trod per t213 S7) -- docs: NEW
_wip_t239 S1..S3 hand-authored (t226 generator-safety rule holds) -- STATE
NEXT=t240 TRIGGER-ARMED IDLE ('do not run on cadence') + LANDED -- NEXT=t240
axes only (r214_triage.py + one save-axis find by ns) or steering override,
else one-line idle + stop -- harness owns the next move, not a research
iteration


LANDED t238 (2026-10-31): NO SITTING — TWENTY-FIFTH CONSECUTIVE BYTE-IDENTICAL
ADJUDICATION, ~4-CALL CAP HELD, DELIBERATELY CONTENT-FREE (NO ledger row moved —
strict-close honored; docs/re/_wip_t238.md S1..S3 hand-authored; no new tools —
r214_triage.py RC=0 at 01:46Z: ns 1793294532100000000 / size 5721578066 /
tail-md5 9054cc6c... all == TRIGGER-A baselines, script prints its own 'sitting
delta: False', zero comm-class dosbox/ascend.exe, tail intact 400 rows/0 bad
json/turn 1086/275 distinct; baseline age INDEPENDENTLY RECOMPUTED -- baseline
ns == 2026-10-29T17:22:12.100Z, session epoch 1793411186 == 2026-10-31T01:46:26Z
=> 116653.9 s = 32.4039h, monotone vs t237's 32.2625h at 01:37:57Z, delta
509.0s == the 8m29s wall gap exactly; sitting script correctly NOT run -- t152
trap) AND: save axis bit-identical to t216..t237 (1409 files, newest
playcap/save/41.sav ns 1793294530.108, #2..#10 60/59/58/57/56/55/54/53/52.sav
on the 10s end-series cadence, still OLDER than the timeline baseline --
watcher-death gap stays closed; gap re-measured 1.992s twentieth consecutive
time) AND: NO new content manufactured -- t238 held the cap, 3 calls before the
finish sequence, no new code path / no fd census / no static hunt, and did NOT
re-run ledger_audit out-of-band (no sitting => the open set cannot have moved;
one cheap grep re-derived the 6 '| open |' markers at lines 232/583/1240/1403/
1431/1451, all inside OQ-005/016/019/021; gate stages ran both checks) --
watcher population unchanged (wrapper 27772 bash/no-writer-fd + child 27774 +
orphans 260988/290953/292085, no new orphans, no retirements; nothing killed,
supervised-session decision) -- NO row closed (strict-close: no sitting =>
witness classes unobservable; OQ-005/016/019/021 stay OPEN; OPEN-QUESTIONS
untouched; honest negative in _wip_t238 S3; nothing beyond the two adjudication
axes censused per t212 law; no static route re-trod per t213 S7) -- docs: NEW
_wip_t238 S1..S3 hand-authored (t226 generator-safety rule holds); the STATE
do-not-re-open list CONSOLIDATED t214..t238 into one entry (all ids retained,
substantive findings kept individually) to arrest linear STATE growth -- STATE
NEXT=t239 TRIGGER-ARMED IDLE ('do not run on cadence') + LANDED -- NEXT=t239
axes only (r214_triage.py + one save-axis find by ns) or steering override,
else one-line idle + stop -- harness owns the next move, not a research
iteration


LANDED t237 (2026-10-31): NO SITTING — TWENTY-FOURTH CONSECUTIVE BYTE-IDENTICAL
ADJUDICATION, ~4-CALL CAP HELD, DELIBERATELY CONTENT-FREE (NO ledger row moved —
strict-close honored; docs/re/_wip_t237.md S1..S3 hand-authored; no new tools —
r214_triage.py RC=0 at 01:37Z: ns 1793294532100000000 / size 5721578066 /
tail-md5 9054cc6c... all == TRIGGER-A baselines, script prints its own 'sitting
delta: False', zero comm-class dosbox/ascend.exe, tail intact 400 rows/0 bad
json/turn 1086/275 distinct; baseline age INDEPENDENTLY RECOMPUTED -- baseline
ns == 2026-10-29T17:22:12.100Z, session epoch 1793410677 == 2026-10-31T01:37:57Z
=> 116144.9 s = 32.2625h, monotone vs t236's 32.1397h at 01:30:35Z, delta
442.0s == the 7m22s wall gap exactly; sitting script correctly NOT run -- t152
trap) AND: save axis bit-identical to t216..t236 (1409 files, newest
playcap/save/41.sav ns 1793294530.108, #2..#10 60/59/58/57/56/55/54/53/52.sav
on the 10s end-series cadence, still OLDER than the timeline baseline --
watcher-death gap stays closed; gap re-measured 1.992s nineteenth consecutive
time) AND: NO new content manufactured -- t237 held the cap, 3 calls before the
finish sequence, no new code path / no fd census / no static hunt, and did NOT
re-run ledger_audit out-of-band (no sitting => the open set cannot have moved;
one cheap grep re-derived the 6 '| open |' markers, all inside
OQ-005/016/019/021; gate stages ran both checks) -- watcher population unchanged
(wrapper 27772 bash/no-writer-fd + child 27774 + orphans 260988/290953/292085,
no new orphans, no retirements; nothing killed, supervised-session decision) --
NO row closed (strict-close: no sitting => witness classes unobservable;
OQ-005/016/019/021 stay OPEN; OPEN-QUESTIONS untouched; honest negative in
_wip_t237 S3; nothing beyond the two adjudication axes censused per t212 law;
no static route re-trod per t213 S7) -- docs: NEW _wip_t237 S1..S3 hand-authored
(t226 generator-safety rule holds), STATE NEXT=t238 TRIGGER-ARMED IDLE ('do not
run on cadence') + LANDED -- NEXT=t238 axes only (r214_triage.py + one save-axis
find by ns) or steering override, else one-line idle + stop -- harness owns the
next move, not a research iteration

LANDED t236 (2026-10-31): NO SITTING — TWENTY-THIRD CONSECUTIVE BYTE-IDENTICAL
ADJUDICATION, ~4-CALL CAP HELD, DELIBERATELY CONTENT-FREE (NO ledger row moved —
strict-close honored; docs/re/_wip_t236.md S1..S3 hand-authored; no new tools —
r214_triage.py RC=0 at 01:30Z: ns 1793294532100000000 / size 5721578066 /
tail-md5 9054cc6c... all == TRIGGER-A baselines, script prints its own 'sitting
delta: False', zero comm-class dosbox/ascend.exe, tail intact 400 rows/0 bad
json/turn 1086/275 distinct; baseline age INDEPENDENTLY RECOMPUTED -- baseline
ns == 2026-10-29T17:22:12.100Z, session epoch 1793410235 == 2026-10-31T01:30:35Z
=> 115702.9 s = 32.1397h, monotone vs t235's 31.9892h at 01:21:33Z, delta
541.8s == the 9m02s wall gap exactly; sitting script correctly NOT run -- t152
trap) AND: save axis bit-identical to t216..t235 (1409 files, newest
playcap/save/41.sav ns 1793294530.108, #2..#10 60/59/58/57/56/55/54/53/52.sav
on the 10s end-series cadence, still OLDER than the timeline baseline --
watcher-death gap stays closed; gap re-measured 1.992s eighteenth consecutive
time) AND: NO new content manufactured -- t236 held the cap, 2 calls before the
finish sequence, no new code path / no fd census / no static hunt, and did NOT
re-run ledger_audit out-of-band (no sitting => the open set cannot have moved;
gate stages ran both checks) -- watcher population unchanged (wrapper 27772
bash/no-writer-fd + child 27774 + orphans 260988/290953/292085, no new orphans,
no retirements; nothing killed, supervised-session decision) -- NO row closed
(strict-close: no sitting => witness classes unobservable; OQ-005/016/019/021
stay OPEN; OPEN-QUESTIONS untouched; honest negative in _wip_t236 S3; nothing
beyond the two adjudication axes censused per t212 law; no static route re-trod
per t213 S7) -- docs: NEW _wip_t236 S1..S3 hand-authored (t226 generator-safety
rule holds), STATE NEXT=t237 TRIGGER-ARMED IDLE ('do not run on cadence') +
LANDED -- NEXT=t237 axes only (r214_triage.py + one save-axis find by ns) or
steering override, else one-line idle + stop -- harness owns the next move, not
a research iteration

LANDED t235 (2026-10-31): NO SITTING — TWENTY-SECOND CONSECUTIVE BYTE-IDENTICAL
ADJUDICATION, ~4-CALL CAP HELD, DELIBERATELY CONTENT-FREE (NO ledger row moved —
strict-close honored; docs/re/_wip_t235.md S1..S3 hand-authored; no new tools —
r214_triage.py RC=0 at 01:21Z: ns 1793294532100000000 / size 5721578066 /
tail-md5 9054cc6c... all == TRIGGER-A baselines, script prints its own 'sitting
delta: False', zero comm-class dosbox/ascend.exe, tail intact 400 rows/0 bad
json/turn 1086/275 distinct; baseline age INDEPENDENTLY RECOMPUTED -- baseline
ns == 2026-10-29T17:22:12.100Z, session epoch 1793409693 == 2026-10-31T01:21:33Z
=> 115161.2 s = 31.9892h, monotone vs t234's 31.8455h at 01:12:56Z, delta
517.3s == the 8m37s wall gap exactly; sitting script correctly NOT run -- t152
trap) AND: save axis bit-identical to t216..t234 (1409 files, newest
playcap/save/41.sav ns 1793294530.108, #2..#10 60/59/58/57/56/55/54/53/52.sav
on the 10s end-series cadence, still OLDER than the timeline baseline --
watcher-death gap stays closed; gap re-measured 1.992s seventeenth consecutive
time) AND: NO new content manufactured -- t235 held the cap, 3 calls before the
finish sequence, no new code path / no fd census / no static hunt, and did NOT
re-run ledger_audit out-of-band (no sitting => the open set cannot have moved;
gate stages ran both checks) -- watcher population unchanged (wrapper 27772
bash/no-writer-fd + child 27774 + orphans 260988/290953/292085, no new orphans,
no retirements; nothing killed, supervised-session decision) -- NO row closed
(strict-close: no sitting => witness classes unobservable; OQ-005/016/019/021
stay OPEN; OPEN-QUESTIONS untouched; honest negative in _wip_t235 S3; nothing
beyond the two adjudication axes censused per t212 law; no static route re-trod
per t213 S7) -- docs: NEW _wip_t235 S1..S3 hand-authored (t226 generator-safety
rule holds), STATE NEXT=t236 TRIGGER-ARMED IDLE ('do not run on cadence') +
LANDED -- NEXT=t236 axes only (r214_triage.py + one save-axis find by ns) or
steering override, else one-line idle + stop -- harness owns the next move, not
a research iteration

LANDED t234 (2026-10-31): NO SITTING — TWENTY-FIRST CONSECUTIVE BYTE-IDENTICAL
ADJUDICATION, ~4-CALL CAP HELD, DELIBERATELY CONTENT-FREE (NO ledger row moved —
strict-close honored; docs/re/_wip_t234.md S1..S3 hand-authored; no new tools —
r214_triage.py + one save-axis find did the whole assigned job). No steering note
was prepended and no OQ-019/OQ-005 ruling appeared in docs/BLOCKED.md, so no
override applied.
THE ANSWERS:
(1) Axis 1: r214_triage.py RC=0 at 2026-10-31T01:12:08Z — all three TRIGGER-A
baselines equal the recorded values for the twenty-first iteration running
(ns_mtime 1793294532100000000, size 5,721,578,066, tail-64KiB md5
9054cc6c66802e6f80431d4ffa1416ee; script prints its own "sitting delta: False"),
ZERO dosbox/ascend.exe processes, tail intact (400 rows / 0 bad json / turn 1086
/ 275 distinct / one 16-field key shape). Baseline age independently RECOMPUTED:
baseline ns 1793294532100000000 == 2026-10-29T17:22:12Z vs session epoch
1793409176 == 2026-10-31T01:12:56Z ⇒ 114643.9 s = 31.8455 h, monotone against
t233's 31.6800 h (Δ 596.0 s == the 9 m 56 s wall gap exactly). r1_t85g_sitting.py
correctly NOT run (t152 trap).
(2) Axis 2: 1409 *.sav/*.gam under HOME (population unchanged since t216);
newest playcap/save/41.sav ns 1793294530.108 — BIT-IDENTICAL to t216..t233;
#2..#9 60/59/58/57/56/55/54/53.sav on the 10 s end-series cadence; baseline −
newest == 1.992 s (sixteenth consecutive measurement). No save newer than the
timeline ⇒ the watcher-death condition did NOT fire.
(3) Watchers: 5 processes, 4 orphaned (260988/290953/292085 + wrapper 27772),
child 27774 alive; no new orphans, no retirements, nothing killed
(supervised-session decision).
LEDGER: no sitting ⇒ OQ-016's multi-volley-vs-non-at-war witnesses and OQ-021's
mid-campaign-slot witness are unobservable; strict-close forbids closing on a
default, so OQ-005/016/019/021 stay OPEN and OPEN-QUESTIONS.md is untouched;
honest negative banked in _wip_t234 S3. No rewrite code touched.
STATE: NEXT=t235 TRIGGER-ARMED IDLE ("do not run on cadence") — the harness
owns the next move, not a research iteration.


LANDED t233 (2026-10-31): NO SITTING — TWENTIETH CONSECUTIVE BYTE-IDENTICAL
ADJUDICATION, ~4-CALL CAP HELD, DELIBERATELY CONTENT-FREE (NO ledger row moved —
strict-close honored; docs/re/_wip_t233.md S1..S3 hand-authored; no new tools —
r214_triage.py + one save-axis find did the whole assigned job). No steering note
was prepended and no OQ-019/OQ-005 ruling appeared in docs/BLOCKED.md, so no
override applied.
THE ANSWERS:
(1) Axis 1: r214_triage.py RC=0 at 2026-10-31T01:03:00Z — all three TRIGGER-A
baselines equal the recorded values for the twentieth iteration running
(ns_mtime 1793294532100000000, size 5,721,578,066, tail-64KiB md5
9054cc6c66802e6f80431d4ffa1416ee; script prints its own "sitting delta: False"),
ZERO dosbox/ascend.exe processes, tail intact (400 rows / 0 bad json / turn 1086
/ 275 distinct / one 16-field key shape). Baseline age independently RECOMPUTED:
baseline ns 1793294532100000000 == 2026-10-29T17:22:12.100Z vs session clock
2026-10-31T01:03:00Z ⇒ 114047.9 s = 31.6800 h, monotone against t232's 31.5516 h
(Δ 461.9 s == the 7 m 42 s wall gap exactly). r1_t85g_sitting.py correctly NOT run
(t152 trap).
(2) Axis 2: 1409 *.sav/*.gam under HOME (population unchanged since t216);
newest playcap/save/41.sav ns 1793294530.108 — BIT-IDENTICAL to t216..t232;
#2..#9 60/59/58/57/56/55/54/53.sav on the 10 s end-series cadence; baseline −
newest == 1.992 s (fifteenth consecutive measurement). No save newer than the
timeline ⇒ the watcher-death condition did NOT fire.
(3) Watchers: 5 processes, 4 orphaned (260988/290953/292085 + wrapper 27772),
child 27774 alive; no new orphans, no retirements, nothing killed
(supervised-session decision).
LEDGER: no sitting ⇒ OQ-016's multi-volley-vs-non-at-war witnesses and OQ-021's
mid-campaign-slot witness are unobservable; strict-close forbids closing on a
default, so OQ-005/016/019/021 stay OPEN and OPEN-QUESTIONS.md is untouched;
honest negative banked in _wip_t233 S3. No rewrite code touched.
STATE: NEXT=t234 TRIGGER-ARMED IDLE ("do not run on cadence") — the harness
owns the next move, not a research iteration.


LANDED t232 (2026-10-31): NO SITTING — NINETEENTH CONSECUTIVE BYTE-IDENTICAL
ADJUDICATION, ~4-CALL CAP HELD, DELIBERATELY CONTENT-FREE (NO ledger row moved —
strict-close honored; docs/re/_wip_t232.md S1..S3 hand-authored; no new tools —
r214_triage.py + one save-axis find did the whole assigned job).
THE ANSWERS:
(1) Axis 1: r214_triage.py RC=0 at 2026-10-31T00:55:18Z — all three TRIGGER-A
baselines equal the recorded values for the nineteenth iteration running
(ns_mtime 1793294532100000000, size 5,721,578,066, tail-64KiB md5
9054cc6c66802e6f80431d4ffa1416ee; script prints its own "sitting delta: False"),
ZERO dosbox/ascend.exe processes, tail intact (400 rows / 0 bad json / turn 1086
/ 275 distinct / one 16-field key shape). Baseline age independently RECOMPUTED:
date -u -d @1793294532 == 2026-10-29T17:22:12Z vs session clock
2026-10-31T00:55:18Z ⇒ 113586 s = 31.5516 h, monotone against t231's 31.396 h
(Δ 560 s == the 9 m 20 s wall gap exactly). r1_t85g_sitting.py correctly NOT run
(t152 trap).
(2) Axis 2: 1409 *.sav/*.gam under HOME (population unchanged since t216);
newest playcap/save/41.sav ns 1793294530.108 — BIT-IDENTICAL to t216..t231;
#2..#8 60/59/58/57/56/55/54.sav on the 10 s end-series cadence; baseline −
newest == 1.992 s (fourteenth consecutive measurement). No save newer than the
timeline ⇒ the watcher-death condition did NOT fire.
(3) Watchers: 5 processes, 4 orphaned (260988/290953/292085 + wrapper 27772),
child 27774 alive; no new orphans, no retirements, nothing killed
(supervised-session decision).
LEDGER: no sitting ⇒ OQ-016's multi-volley-vs-non-at-war witnesses and OQ-021's
mid-campaign-slot witness are unobservable; strict-close forbids closing on a
default, so OQ-005/016/019/021 stay OPEN and OPEN-QUESTIONS.md is untouched;
honest negative banked in _wip_t232 S3. No rewrite code touched.
STATE: NEXT=t233 TRIGGER-ARMED IDLE ("do not run on cadence") — the harness
owns the next move, not a research iteration.


LANDED t231 (2026-10-31): NO SITTING — EIGHTEENTH CONSECUTIVE BYTE-IDENTICAL
ADJUDICATION, ~4-CALL CAP HELD, DELIBERATELY CONTENT-FREE (NO ledger row moved —
strict-close honored; docs/re/_wip_t231.md S1..S3 hand-authored; no new tools —
r214_triage.py + one save-axis find did the whole assigned job).
THE ANSWERS:
(1) Axis 1: r214_triage.py RC=0 at 2026-10-31T00:45:58Z — all three TRIGGER-A
baselines equal the recorded values for the eighteenth iteration running
(ns_mtime 1793294532100000000, size 5,721,578,066, tail-64KiB md5
9054cc6c66802e6f80431d4ffa1416ee; script prints its own "sitting delta: False"),
ZERO dosbox/ascend.exe processes, tail intact (400 rows / 0 bad json / turn 1086
/ 275 distinct / one 16-field key shape). Baseline age independently RECOMPUTED:
date -u -d @1793294532 == 2026-10-29T17:22:12Z vs session clock
2026-10-31T00:45:58Z ⇒ 113026 s = 31.396 h, monotone against t230's 31.2489 h
(delta 531 s ≈ the 8 min 50 s wall gap). r1_t85g_sitting.py correctly NOT run
(t152 trap).
(2) Axis 2: 1409 *.sav/*.gam under HOME (population unchanged since t216);
newest playcap/save/41.sav ns 1793294530.108 — BIT-IDENTICAL to t216..t230;
#2..#8 60/59/58/57/56/55/54.sav on the 10 s end-series cadence; baseline −
newest == 1.992 s (thirteenth consecutive measurement). No save newer than the
timeline ⇒ the watcher-death condition did NOT fire.
(3) Watchers: 5 processes, 4 orphaned (260988/290953/292085 + wrapper 27772),
child 27774 alive; no new orphans, no retirements, nothing killed
(supervised-session decision).
LEDGER: no sitting ⇒ OQ-016's multi-volley-vs-non-at-war witnesses and OQ-021's
mid-campaign-slot witness are unobservable; strict-close forbids closing on a
default, so OQ-005/016/019/021 stay OPEN and OPEN-QUESTIONS.md is untouched;
honest negative banked in _wip_t231 S3. No rewrite code touched.
STATE: NEXT=t232 TRIGGER-ARMED IDLE ("do not run on cadence") — the harness
owns the next move, not a research iteration.

LANDED t230 (2026-10-31): NO SITTING — SEVENTEENTH CONSECUTIVE BYTE-IDENTICAL
ADJUDICATION, ~4-CALL CAP HELD, DELIBERATELY CONTENT-FREE (NO ledger row moved —
strict-close honored; docs/re/_wip_t230.md S1..S3 hand-authored; no new tools —
r214_triage.py + one save-axis find did the whole assigned job).
THE ANSWERS:
(1) Axis 1: r214_triage.py RC=0 at 2026-10-31T00:37:08Z — all three TRIGGER-A
baselines equal the recorded values for the seventeenth iteration running
(ns_mtime 1793294532100000000, size 5,721,578,066, tail-64KiB md5
9054cc6c66802e6f80431d4ffa1416ee; script prints its own "sitting delta: False"),
ZERO dosbox/ascend.exe processes, tail intact (400 rows / 0 bad json / turn 1086
/ 275 distinct / one 16-field key shape). Baseline age independently RECOMPUTED:
date -u -d @1793294532 == 2026-10-29T17:22:12Z vs session clock
2026-10-31T00:37:08Z ⇒ 112495 s = 31.25 h, monotone against t229's 31.06 h
(delta 672 s ≈ the 11 min 13 s wall gap). r1_t85g_sitting.py correctly NOT run
(t152 trap).
(2) Axis 2: 1409 *.sav/*.gam under HOME (population unchanged since t216);
newest playcap/save/41.sav ns 1793294530.108 — BIT-IDENTICAL to t216..t229;
#2..#8 60/59/58/57/56/55/54.sav on the 10 s end-series cadence; baseline −
newest == 1.992 s (twelfth consecutive measurement). No save newer than the
timeline ⇒ the watcher-death condition did NOT fire.
(3) Watchers: 5 processes, 4 orphaned (260988/290953/292085 + wrapper 27772),
child 27774 alive; no new orphans, no retirements, nothing killed
(supervised-session decision).
LEDGER: no sitting ⇒ OQ-016's multi-volley-vs-non-at-war witnesses and OQ-021's
mid-campaign-slot witness are unobservable; strict-close forbids closing on a
default, so OQ-005/016/019/021 stay OPEN and OPEN-QUESTIONS.md is untouched;
honest negative banked in _wip_t230 S3. No rewrite code touched.
STATE: NEXT=t231 TRIGGER-ARMED IDLE ("do not run on cadence") — the harness
owns the next move, not a research iteration.

LANDED t229 (2026-10-31): NO SITTING — SIXTEENTH CONSECUTIVE BYTE-IDENTICAL
ADJUDICATION, ~4-CALL CAP HELD, DELIBERATELY CONTENT-FREE (NO ledger row moved —
strict-close honored; docs/re/_wip_t229.md S1..S3 hand-authored; no new tools —
r214_triage.py + one save-axis find did the whole assigned job).
THE ANSWERS:
(1) Axis 1: r214_triage.py RC=0 at 2026-10-31T00:25:55Z — all three TRIGGER-A
baselines equal the recorded values for the sixteenth iteration running
(ns_mtime 1793294532100000000, size 5,721,578,066, tail-64KiB md5
9054cc6c66802e6f80431d4ffa1416ee; script prints its own "sitting delta: False"),
ZERO dosbox/ascend.exe processes, tail intact (400 rows / 0 bad json / turn 1086
/ 275 distinct / one 16-field key shape). Baseline age independently RECOMPUTED:
date -u -d @1793294532 == 2026-10-29T17:22:12Z vs session clock
2026-10-31T00:25:55Z ⇒ 111823 s = 31.06 h, monotone against t228's 30.91 h
(delta 0.15 h ≈ the 9.2 min wall gap). r1_t85g_sitting.py correctly NOT run
(t152 trap).
(2) Axis 2: 1409 *.sav/*.gam under HOME (population unchanged since t216);
newest playcap/save/41.sav ns 1793294530.108 — BIT-IDENTICAL to t216..t228;
#2..#8 60/59/58/57/56/55/54.sav on the 10 s end-series cadence; baseline −
newest == 1.992 s (eleventh consecutive measurement). No save newer than the
timeline ⇒ the watcher-death condition did NOT fire.
(3) Watchers: 5 processes, 4 orphaned (260988/290953/292085 + wrapper 27772),
child 27774 alive; no new orphans, no retirements, nothing killed
(supervised-session decision).
LEDGER: no sitting ⇒ OQ-016's multi-volley-vs-non-at-war witnesses and OQ-021's
mid-campaign-slot witness are unobservable; strict-close forbids closing on a
default, so OQ-005/016/019/021 stay OPEN and OPEN-QUESTIONS.md is untouched;
honest negative banked in _wip_t229 S3. No rewrite code touched.
STATE: NEXT=t230 TRIGGER-ARMED IDLE ("do not run on cadence") — the harness
owns the next move, not a research iteration.

LANDED t228 (2026-10-31): NO SITTING — FIFTEENTH CONSECUTIVE BYTE-IDENTICAL
ADJUDICATION, ~4-CALL CAP HELD, DELIBERATELY CONTENT-FREE (NO ledger row moved
— strict-close honored; docs/re/_wip_t228.md S1..S3 hand-authored, generator
safety re-confirmed BY THIS SESSION's grep over scripts/*.sh scripts/*.py —
scripts/r1_idle_probe.py only READS _wip_*.md (L50/L361/L373/L389) and gate.sh
mentions _wip_ inside a comment (L373); no new tools — r214_triage.py + one
save-axis find did the whole assigned job).
THE ANSWERS:
(1) Axis 1: r214_triage.py RC=0 at 2026-10-31T00:16:43Z — all three TRIGGER-A
baselines equal the recorded values for the fifteenth iteration running
(ns_mtime 1793294532100000000, size 5,721,578,066, tail-64KiB md5
9054cc6c66802e6f80431d4ffa1416ee; the script prints its own "sitting delta:
False"), plus ZERO dosbox/ascend.exe processes. Tail intact (400 rows / 0 bad
json / turn 1086 / 275 distinct / exactly one 16-field key shape). Baseline age
independently RECOMPUTED, not carried forward: date -u -d @1793294532 ==
2026-10-29T17:22:12Z, session clock 2026-10-31T00:16:43Z ⇒ 30 h 54 m 31 s =
30.91 h, monotone against t227's 30.80 h at 2026-10-31T00:09:56Z (delta 0.11 h
≈ the 6.8 min wall gap), so the age chain in this file stays self-corroborating.
r1_t85g_sitting.py correctly NOT run (t152 trap: no sitting ⇒ nothing to
adjudicate).
(2) Axis 2: newest *.sav/*.gam under HOME (1409 files — population unchanged
since t216, %T@-sorted) == playcap/save/41.sav ns 1793294530.108 — BIT-IDENTICAL
to t216..t227; #2..#8 are 60.sav 1793294520.040 / 59.sav 1793294510.004 /
58.sav 1793294500.004 / 57.sav 1793294489.988 / 56.sav 1793294479.980 /
55.sav 1793294469.964 / 54.sav 1793294459.956 — the 10 s end-series cadence.
The newest save is OLDER than the timeline baseline, so the WATCHER-DEATH
condition (save newer than timeline ⇒ watchers died) did NOT fire. Gap
baseline−newest re-measured 1.992 s (1793294532.100 − 1793294530.108) a tenth
consecutive time.
(3) Watcher population unchanged: wrapper 27772 (bash, holds NO writer fd) +
child 27774 + orphans 260988 / 290953 / 292085 (triage reports 5 total, 4
"orphaned" by its ppid heuristic — the fd-level writer set is the four python3s,
per the t215 law writerhood = open fd, not process presence). NO new orphans and
NO retirements since t215; nothing killed (retiring them is a supervised-session
decision, USER ASK #3).
(4) Ledger: NO row closed, none opened, OPEN-QUESTIONS.md byte-untouched.
Honest negative banked in _wip_t228 S3: with no sitting, the two witness classes
the open rows need — (a) a multi-volley battle vs a NON-at-war owner (OQ-016
clamp witnesses, the only thing that closes the zero-witness residue) and (b) a
MID-CAMPAIGN slot with V=dword[0x482fb] > 1 AND some byte[star+0x15] nonzero
(OQ-021 S6 semantic non-join + the P7 label question) — are unobservable from
the corpus, and strict-close forbids closing on a plausible default.
ledger_audit deliberately NOT re-run out-of-band (no sitting ⇒ the open set
cannot have moved); it ran as a gate stage on this iteration.
STATE: NEXT=t229 TRIGGER-ARMED IDLE ("do not run on cadence") — the harness
owns the next move, not a research iteration.

LANDED t227 (2026-10-31): NO SITTING — FOURTEENTH CONSECUTIVE BYTE-IDENTICAL
ADJUDICATION, ~4-CALL CAP HELD, DELIBERATELY CONTENT-FREE (NO ledger row moved
— strict-close honored; docs/re/_wip_t227.md S1..S3 hand-authored, generator
safety re-confirmed by this session's grep — scripts/r1_idle_probe.py only
READS _wip_*.md (L50/L361/L373/L389) and gate.sh mentions _wip_ inside a
comment (L373); no new tools — r214_triage.py + one save-axis find did the
whole assigned job).
THE ANSWERS:
(1) Axis 1: r214_triage.py RC=0 at 2026-10-31T00:09:56Z — all three TRIGGER-A
baselines equal the recorded values for the fourteenth iteration running
(ns_mtime 1793294532100000000, size 5,721,578,066, tail-64KiB md5
9054cc6c66802e6f80431d4ffa1416ee; the script prints its own "sitting delta:
False"), plus ZERO dosbox/ascend.exe processes. Tail intact (400 rows / 0 bad
json / turn 1086 / 275 distinct / exactly one 16-field key shape). Baseline age
independently RECOMPUTED, not carried forward: baseline ns ==
2026-10-29T17:22:12.100Z, session clock 2026-10-31T00:09:56Z ⇒ 30 h 47 m 44 s =
30.80 h, monotone against t226's 30.66 h at 2026-10-31T00:01:37Z (delta 0.14 h
≈ the 8.3 min wall gap), so the age chain in this file stays self-corroborating.
r1_t85g_sitting.py correctly NOT run (t152 trap: no sitting ⇒ nothing to
adjudicate).
(2) Axis 2: newest *.sav/*.gam under HOME (1409 files — population unchanged
since t216, %T@-sorted) == playcap/save/41.sav ns 1793294530.108 — BIT-IDENTICAL
to t216..t226; #2..#8 are 60.sav 1793294520.040 / 59.sav 1793294510.004 /
58.sav 1793294500.004 / 57.sav 1793294489.988 / 56.sav 1793294479.980 /
55.sav 1793294469.964 / 54.sav 1793294459.956 — the 10 s end-series cadence.
The newest save is OLDER than the timeline baseline, so the WATCHER-DEATH
condition (save newer than timeline ⇒ watchers died) did NOT fire. Gap
baseline−newest re-measured 1.992 s (1793294532.100 − 1793294530.108) a ninth
consecutive time.
(3) Watcher population unchanged: wrapper 27772 (bash, holds NO writer fd) +
child 27774 + orphans 260988 / 290953 / 292085 (triage reports 5 total, 4
"orphaned" by its ppid heuristic — the fd-level writer set is the four
python3s, per the t215 law writerhood = open fd, not process presence). NO new
orphans and NO retirements since t215; nothing killed (retiring them is a
supervised-session decision, USER ASK #3).
(4) Ledger: NO row closed, none opened, OPEN-QUESTIONS.md byte-untouched.
Honest negative banked in _wip_t227 S3: with no sitting, the two witness
classes the open rows need — (a) a multi-volley battle vs a NON-at-war owner
(OQ-016 clamp witnesses, the only thing that closes the zero-witness residue)
and (b) a MID-CAMPAIGN slot with V=dword[0x482fb] > 1 AND some byte[star+0x15]
nonzero (OQ-021 S6 semantic non-join + the P7 label question) — are
unobservable from the corpus, and strict-close forbids closing on a plausible
default. ledger_audit deliberately NOT re-run out-of-band (no sitting ⇒ the
open set cannot have moved); it ran as a gate stage on this iteration.
STATE: NEXT=t228 TRIGGER-ARMED IDLE ("do not run on cadence") — the harness
owns the next move, not a research iteration.

LANDED t226 (2026-10-31): NO SITTING — THIRTEENTH CONSECUTIVE BYTE-IDENTICAL
ADJUDICATION, ~4-CALL CAP HELD, DELIBERATELY CONTENT-FREE (NO ledger row moved
— strict-close honored; docs/re/_wip_t226.md S1..S3 hand-authored, generator
safety re-confirmed by the t225 grep — scripts/r1_idle_probe.py only READS
_wip_*.md and gate.sh mentions _wip_ inside a comment; no new tools —
r214_triage.py + one save-axis find did the whole assigned job).
THE ANSWERS:
(1) Axis 1: all three TRIGGER-A baselines equal the recorded values for the
thirteenth iteration running (ns_mtime 1793294532100000000, size 5,721,578,066,
tail-64KiB md5 9054cc6c66802e6f80431d4ffa1416ee; script RC=0, prints its own
"sitting delta: False"), plus ZERO dosbox/ascend.exe processes. Tail intact
(400 rows / 0 bad json / turn 1086 / 275 distinct / exactly one 16-field key
shape). Baseline age independently RECOMPUTED, not carried forward: baseline ns
== 2026-10-29T17:22:12.100Z, session clock 2026-10-31T00:01:37Z ⇒ 30 h 39 m 25 s
= 30.66 h, monotone against t225's 30.52 h at 2026-10-30T23:53:29Z (delta 0.14 h
≈ the 8.1 min wall gap), so the age chain in this file stays self-corroborating.
r1_t85g_sitting.py correctly NOT run (t152 trap).
(2) Axis 2: newest *.sav/*.gam under HOME (1409 files, %T@-sorted) ==
playcap/save/41.sav ns 1793294530.108 — BIT-IDENTICAL to t216..t225; #2..#8 are
60.sav 1793294520.040 / 59.sav 1793294510.004 / 58.sav 1793294500.004 /
57.sav 1793294489.988 / 56.sav 1793294479.980 / 55.sav 1793294469.964 /
54.sav 1793294459.956 (the 10 s end-series cadence). Still OLDER than the
timeline baseline, so the "watchers died and hid a sitting" gap stays closed on
the independent signal. Gap re-measured 1.992 s for the eighth consecutive
iteration. Zero saves since the 2026-10-29 13:22 end series.
(3) Ledger: NOT re-audited out of band (deliberate — with no sitting the open set
cannot have moved; t219 measured rows=19 open=OQ-005/016/019/021 closed=15).
ledger_audit ran only as a finish-sequence stage and printed LEDGER AUDIT OK;
gate.sh exit 0. No row closed and no row annotated: the OQ-016 clamp witnesses
and the OQ-021 mid-campaign-slot semantic join are OBSERVABLE ONLY from a new
sitting, and OQ-005 (index.txt + dims residue) and OQ-019 (per-commit attack
pricing) need a USER ruling, not measurement. Honest negative recorded in
_wip_t226 S3; docs/OPEN-QUESTIONS.md untouched.
WATCHERS: unchanged — wrapper 27772 [bash, ppid 1, holds no writer fd] + child
27774 [python3] + orphans 260988 / 290953 / 292085. No new orphans since t215, no
retirements (uptimes ~4d12h / ~4d12h / ~1d20h / ~1d07h / ~1d07h). Nothing killed
(supervised-session decision, user ask #3).
NEXT=t227 axes only (python3 scripts/r214_triage.py + the one save-axis find by
ns) or a steering override (prepended note / OQ-019 or OQ-005 ruling / supervised
watchpoint grant), else one-line idle + STOP. The harness owns the next move, not
a research iteration.

LANDED t225 (2026-10-30): NO SITTING — TWELFTH CONSECUTIVE BYTE-IDENTICAL
ADJUDICATION, ~4-CALL CAP HELD, DELIBERATELY CONTENT-FREE (NO ledger row moved
— strict-close honored; docs/re/_wip_t225.md S1..S3 hand-authored, verified no
generator touches docs/re/_wip_*.md — scripts/r1_idle_probe.py only READS them
and gate.sh mentions _wip_ inside a comment; no new tools — r214_triage.py + one
save-axis find did the whole assigned job).
THE ANSWERS:
(1) Axis 1: all three TRIGGER-A baselines equal the recorded values for the
twelfth iteration running (ns_mtime 1793294532100000000, size 5,721,578,066,
tail-64KiB md5 9054cc6c66802e6f80431d4ffa1416ee; script RC=0, prints its own
"sitting delta: False"), plus ZERO dosbox/ascend.exe processes. Tail intact
(400 rows / 0 bad json / turn 1086 / 275 distinct / exactly one key shape).
Baseline age independently RECOMPUTED, not carried forward: baseline ns ==
2026-10-29T17:22:12.100Z, session clock 2026-10-30T23:53:29Z ⇒ 30.52 h, monotone
against t224's 30.35 h at 23:42:56Z (delta 0.17 h ≈ the 10.5 min wall gap), so
the age chain in this file stays self-corroborating. r1_t85g_sitting.py
correctly NOT run (t152 trap).
(2) Axis 2: newest *.sav/*.gam under HOME (1409 files, %T@-sorted) ==
playcap/save/41.sav ns 1793294530.108 — BIT-IDENTICAL to t216..t224; #2..#8 are
60.sav 1793294520.040 / 59.sav 1793294510.004 / 58.sav 1793294500.004 /
57.sav 1793294489.988 / 56.sav 1793294479.980 / 55.sav 1793294469.964 /
54.sav 1793294459.956 (the 10 s end-series cadence). Still OLDER than the
timeline baseline, so the "watchers died and hid a sitting" gap stays closed on
the independent signal. Gap re-measured 1.992 s for the seventh consecutive
iteration. Zero saves since the 2026-10-29 13:22 end series.
(3) Ledger: NOT re-audited out of band (deliberate — with no sitting the open set
cannot have moved; t219 measured rows=19 open=OQ-005/016/019/021 closed=15).
ledger_audit ran only as a finish-sequence stage and printed LEDGER AUDIT OK;
gate.sh exit 0. No row closed and no row annotated: the OQ-016 clamp witnesses
and the OQ-021 mid-campaign-slot semantic join are OBSERVABLE ONLY from a new
sitting, and OQ-005 (index.txt + dims residue) and OQ-019 (per-commit attack
pricing) need a USER ruling, not measurement. Honest negative recorded in
_wip_t225 S3; docs/OPEN-QUESTIONS.md untouched.
WATCHERS: unchanged — wrapper 27772 [bash, ppid 1, holds no writer fd] + child
27774 [python3] + orphans 260988 / 290953 / 292085. No new orphans since t215, no
retirements (uptimes ~4d12h / ~4d12h / ~1d20h / ~1d07h / ~1d07h). Nothing killed
(supervised-session decision, user ask #3).
NEXT=t226 axes only (python3 scripts/r214_triage.py + the one save-axis find by
ns) or a steering override (prepended note / OQ-019 or OQ-005 ruling / supervised
watchpoint grant), else one-line idle + STOP. The harness owns the next move, not
a research iteration.

LANDED t224 (2026-10-30): NO SITTING — ELEVENTH CONSECUTIVE BYTE-IDENTICAL
ADJUDICATION, ~4-CALL CAP HELD, DELIBERATELY CONTENT-FREE (NO ledger row moved
— strict-close honored; docs/re/_wip_t224.md S1..S3 hand-authored, verified no
generator touches docs/re/_wip_*.md — scripts/r1_idle_probe.py only READS them
and gate.sh mentions _wip_ only inside a comment; no new tools — r214_triage.py
+ one save-axis find did the whole assigned job).
THE ANSWERS:
(1) Axis 1: all three TRIGGER-A baselines equal the recorded values for the
eleventh iteration running (ns_mtime 1793294532100000000, size 5,721,578,066,
tail-64KiB md5 9054cc6c66802e6f80431d4ffa1416ee; script RC=0, prints its own
"sitting delta: False"), plus ZERO dosbox/ascend.exe processes. Tail intact
(400 rows / 0 bad json / turn 1086 / 275 distinct / exactly one key shape).
Baseline age independently RECOMPUTED, not carried forward: baseline ns ==
2026-10-29T17:22:12.100Z, session clock 2026-10-30T23:42:56Z ⇒ 30.35 h, monotone
against t223's 30.21 h at 23:34:45Z (delta 0.14 h ≈ the 8.2 min wall gap), so
the age chain in this file stays self-corroborating. r1_t85g_sitting.py
correctly NOT run (t152 trap).
(2) Axis 2: newest *.sav/*.gam under HOME (1409 files, %T@-sorted) ==
playcap/save/41.sav ns 1793294530.108 — BIT-IDENTICAL to t216..t223; #2..#6 are
60.sav 1793294520.040 / 59.sav 1793294510.004 / 58.sav 1793294500.004 /
57.sav 1793294489.988 / 56.sav 1793294479.980 (the 10 s end-series cadence).
Still OLDER than the timeline baseline, so the "watchers died and hid a sitting"
gap stays closed on the independent signal. Gap re-measured 1.992 s for the
sixth consecutive iteration. Zero saves since the 2026-10-29 13:22 end series.
(3) Ledger: NOT re-audited out of band (deliberate — with no sitting the open set
cannot have moved; t219 measured rows=19 open=OQ-005/016/019/021 closed=15).
ledger_audit ran only as a finish-sequence stage and printed LEDGER AUDIT OK;
gate.sh exit 0. No row closed: the OQ-016 clamp witnesses and the OQ-021
mid-campaign-slot semantic join are OBSERVABLE ONLY from a new sitting, and
OQ-005 (index.txt + dims residue) and OQ-019 (per-commit attack pricing) need a
USER ruling, not measurement. Honest negative recorded in _wip_t224 S3;
docs/OPEN-QUESTIONS.md untouched — nothing there needed annotating.
WATCHERS: unchanged — wrapper 27772 [bash, ppid 1, holds no writer fd] + child
27774 [python3] + orphans 260988 / 290953 / 292085. No new orphans since t215, no
retirements (uptimes ~4d12h / ~1d20h / ~1d07h / ~1d07h). Nothing killed
(supervised-session decision, user ask #3).
NEXT=t225 axes only (python3 scripts/r214_triage.py + the one save-axis find by
ns) or a steering override (prepended note / OQ-019 or OQ-005 ruling / supervised
watchpoint grant), else one-line idle + STOP. The harness owns the next move, not
a research iteration.
LANDED t223 (2026-10-30): NO SITTING — TENTH CONSECUTIVE BYTE-IDENTICAL
ADJUDICATION, ~4-CALL CAP HELD, DELIBERATELY CONTENT-FREE (NO ledger row moved
— strict-close honored; docs/re/_wip_t223.md S1..S3 hand-authored, verified no
generator touches docs/re/_wip_*.md — scripts/r1_idle_probe.py only reads them;
no new tools — r214_triage.py + one save-axis find did the whole assigned job).
THE ANSWERS:
(1) Axis 1: all three TRIGGER-A baselines equal the recorded values for the
tenth iteration running (ns_mtime 1793294532100000000, size 5,721,578,066,
tail-64KiB md5 9054cc6c66802e6f80431d4ffa1416ee; script RC=0, prints its own
"sitting delta: False"), plus ZERO dosbox/ascend.exe processes. Tail intact
(400 rows / 0 bad json / turn 1086 / 275 distinct / one key shape). Baseline age
independently RECOMPUTED, not carried forward: baseline ns ==
2026-10-29T17:22:12.100Z, session clock 2026-10-30T23:34:45Z ⇒ 30.21 h, monotone
against t222's 30.06 h at 23:25:39Z (delta 0.15 h ≈ the 9.1 min wall gap).
r1_t85g_sitting.py correctly NOT run (t152 trap).
(2) Axis 2: newest *.sav/*.gam under HOME (1409 files, %T@-sorted) ==
playcap/save/41.sav ns 1793294530.108 — BIT-IDENTICAL to t216..t222, #2/#3 are
60.sav 1793294520.040 / 59.sav 1793294510.004. Still OLDER than the timeline
baseline, so the "watchers died and hid a sitting" gap stays closed. Gap
re-measured 1.992 s for the fifth consecutive iteration. Zero saves since the
2026-10-29 13:22 end series.
(3) Ledger: NOT re-audited out of band (deliberate — with no sitting the open set
cannot have moved; t219 measured rows=19 open=OQ-005/016/019/021 closed=15).
ledger_audit ran only as a finish-sequence stage and printed LEDGER AUDIT OK;
gate.sh exit 0. No row closed: the OQ-016 clamp witnesses and the OQ-021
mid-campaign-slot semantic join are OBSERVABLE ONLY from a new sitting, and
OQ-005 (index.txt + dims residue) and OQ-019 (per-commit attack pricing) need a
USER ruling, not measurement. Honest negative recorded in _wip_t223 S3.
WATCHERS: unchanged — wrapper 27772 [bash, ppid 1, holds no writer fd] + child
27774 [python3] + orphans 260988 / 290953 / 292085. No new orphans since t215, no
retirements. Nothing killed (supervised-session decision, user ask #3).
NEXT=t224 axes only (python3 scripts/r214_triage.py + the one save-axis find by
ns) or a steering override (prepended note / OQ-019 or OQ-005 ruling / supervised
watchpoint grant), else one-line idle + STOP. The harness owns the next move, not
a research iteration.

LANDED t222 (2026-10-30): NO SITTING — NINTH CONSECUTIVE BYTE-IDENTICAL
ADJUDICATION, ~4-CALL CAP HELD, DELIBERATELY CONTENT-FREE (NO ledger row moved
— strict-close honored; docs/re/_wip_t222.md S1..S3 hand-authored, verified no
generator touches docs/re/_wip_*.md — scripts/r1_idle_probe.py only reads them;
no new tools — r214_triage.py + one save-axis find did the whole assigned job).
THE ANSWERS:
(1) Axis 1: all three TRIGGER-A baselines equal the recorded values for the
ninth iteration running (ns_mtime 1793294532100000000, size 5,721,578,066,
tail-64KiB md5 9054cc6c66802e6f80431d4ffa1416ee; script RC=0, prints its own
"sitting delta: False"), plus ZERO dosbox/ascend.exe processes. Tail intact
(400 rows / 0 bad json / turn 1086 / 275 distinct / one key shape). Baseline age
independently RECOMPUTED this iteration rather than carried forward: baseline ns
== 2026-10-29T17:22:12.100Z, session clock 2026-10-30T23:25:39Z ⇒ 30.06 h,
monotone against t221's 29.94 h at 23:18:02Z (delta ≈ the 7.6 min wall gap), so
the age chain in this file is self-corroborating. r1_t85g_sitting.py correctly
NOT run (t152 trap).
(2) Axis 2: newest *.sav/*.gam under HOME (1409 files, %T@-sorted) ==
playcap/save/41.sav ns 1793294530.108 — BIT-IDENTICAL to t216..t221, #2/#3 are
60.sav 1793294520.040 / 59.sav 1793294510.004. Still OLDER than the timeline
baseline, so the "watchers died and hid a sitting" gap stays closed. Gap
re-measured 1.992 s for the fourth consecutive iteration. Zero saves since the
2026-10-29 13:22 end series.
(3) Discipline held rather than content manufactured. The session stayed at the
assigned cap, appended no new code path, no fd census, no static hunt, and did
NOT re-run ledger_audit out-of-band (with no sitting the open set cannot have
moved; gate stage 3t still runs both ledger checks). docs/OPEN-QUESTIONS.md
untouched — nothing there needed annotating.
(4) Watcher population unchanged as an incidental read — wrapper 27772 (bash,
holds no writer fd) + child 27774 + orphans 260988/290953/292085, no new
orphans, no retirements. Nothing killed: retiring watchers is a
supervised-session decision, not a research-iteration action.
HONEST NEGATIVE: with no sitting the witness classes stay unobservable, so
OQ-005 / OQ-016 / OQ-019 / OQ-021 all remain OPEN and nothing else was censused
(t212 law). NEXT: t223 TRIGGER-ARMED IDLE — axes only, or a steering override;
otherwise one-line idle and STOP.

LANDED t221 (2026-10-30): NO SITTING — EIGHTH CONSECUTIVE BYTE-IDENTICAL
ADJUDICATION, ~4-CALL CAP HELD, DELIBERATELY CONTENT-FREE (NO ledger row moved
— strict-close honored; docs/re/_wip_t221.md S1..S3 hand-authored, verified no
generator touches docs/re/_wip_*.md — scripts/r1_idle_probe.py only reads them;
no new tools — r214_triage.py + one save-axis find did the whole assigned job).
THE ANSWERS:
(1) Axis 1: all three TRIGGER-A baselines equal the recorded values for the
eighth iteration running (ns_mtime 1793294532100000000, size 5,721,578,066,
tail-64KiB md5 9054cc6c66802e6f80431d4ffa1416ee; script RC=0, prints its own
"sitting delta: False"), plus ZERO dosbox/ascend.exe processes. Tail intact
(400 rows / 0 bad json / turn 1086 / 275 distinct / one key shape). Baseline age
29.94 h at 2026-10-30T23:18:02Z — mutually corroborating with t220's 29.80 h at
23:09:59Z (delta ~8.4 min ≈ the wall gap between the two sessions).
r1_t85g_sitting.py correctly NOT run (t152 trap).
(2) Axis 2: newest *.sav/*.gam under HOME (1409 files, %T@-sorted) ==
playcap/save/41.sav ns 1793294530.108 — BIT-IDENTICAL to t216..t220, #2/#3 are
60.sav 1793294520.040 / 59.sav 1793294510.004. Still OLDER than the timeline
baseline, so the "watchers died and hid a sitting" gap stays closed. Gap
re-measured 1.992 s for the third consecutive iteration. Zero saves since the
2026-10-29 13:22 end series.
(3) Discipline held rather than content manufactured. The session stayed at the
assigned cap, appended no new code path, no fd census, no static hunt, and did
NOT re-run ledger_audit out-of-band (with no sitting the open set cannot have
moved; gate stage 3t still runs both ledger checks). docs/OPEN-QUESTIONS.md
untouched — nothing there needed annotating.
(4) Watcher population unchanged as an incidental read — wrapper 27772 (bash,
no writer fd; triage flags it because ppid is 1) + child 27774 + orphans
260988/290953/292085: no new orphans, no retirements in ~15 h. Nothing killed;
standing supervised-session ask restated.
HONEST NEGATIVE: OQ-016, OQ-021, OQ-019, OQ-005 all stay OPEN — no cited
measurement was obtainable without play or a user ruling, and no plausible
default was allowed to close anything. Gate + both ledger checks green.
NEXT: t222 is trigger-armed idle (two axes only), or a steering override — the
harness owns the next move, not a research iteration.

LANDED t220 (2026-10-30): NO SITTING — SEVENTH CONSECUTIVE BYTE-IDENTICAL
ADJUDICATION, DELIBERATELY CONTENT-FREE (NO ledger row moved — strict-close
honored; docs/re/_wip_t220.md S1..S4; no new tools — r214_triage.py + one
save-axis find did the whole assigned job). THE ANSWERS:
(1) Axis 1: all three TRIGGER-A baselines equal the recorded values for the
seventh iteration running (ns_mtime 1793294532100000000, size 5,721,578,066,
tail-64KiB md5 9054cc6c66802e6f80431d4ffa1416ee; script RC=0, prints its own
"sitting delta: False"), plus ZERO dosbox/ascend.exe processes. Tail intact
(400 rows / 0 bad json / turn 1086 / 275 distinct / one key shape). Baseline age
29.80 h at 2026-10-30T23:09:59Z. r1_t85g_sitting.py correctly NOT run (t152
trap).
(2) Axis 2: newest *.sav/*.gam under HOME (1409 files, %T@-sorted) ==
playcap/save/41.sav ns 1793294530.108 — BIT-IDENTICAL to t216/t217/t218/t219
and still older than the timeline baseline, so the "watchers died and hid a
sitting" gap stays closed. Gap re-measured 1.992 s (t219's corrected arithmetic,
re-confirmed in-session). Zero saves since the 2026-10-29 13:22 end series.
(3) NO new content claimed, on purpose. t219 measured the idle premise from the
primary source; an eighth angle invented to look busy would violate the idle
discipline, so this iteration banked a reproduction plus the age stamp and
nothing else. docs/OPEN-QUESTIONS.md untouched (nothing to annotate).
(4) Watcher population unchanged as an incidental read — wrapper 27772 (bash,
no writer fd; the triage script flags it as orphaned because its ppid is 1) +
child 27774 + orphans 260988/290953/292085: no new orphans, no retirements.
Nothing killed; standing supervised-session ask restated.
HONEST NEGATIVE: OQ-016, OQ-021, OQ-019, OQ-005 all stay OPEN — no cited
measurement was obtainable without play or a user ruling, and no plausible
default was allowed to close anything. Gate + both ledger checks green.
NEXT: t221 is trigger-armed idle (two axes only), or a steering override — the
harness owns the next move, not a research iteration.

LANDED t219 (2026-10-30): NO SITTING — SIXTH CONSECUTIVE BYTE-IDENTICAL
ADJUDICATION + LEDGER-PREMISE RE-MEASURED FROM PRIMARY SOURCE (NO ledger row
moved — strict-close honored; docs/re/_wip_t219.md S1..S4 NEW; no new tools —
r214_triage.py + one save-axis find + the two standing verification commands did
the whole assigned job). THE ANSWERS:
(1) Axis 1: all three TRIGGER-A baselines equal the recorded values for the
sixth iteration running (ns_mtime 1793294532100000000, size 5,721,578,066,
tail-64KiB md5 9054cc6c66802e6f80431d4ffa1416ee; script RC=0, "sitting delta:
False"), plus ZERO dosbox/ascend.exe processes. Tail intact (400 rows / 0 bad
json / turn 1086 / 275 distinct / one key shape). Baseline age 29.63 h at
2026-10-30T23:00:15Z. r1_t85g_sitting.py correctly NOT run (t152 trap).
(2) Axis 2: newest *.sav/*.gam under HOME (1409 files) == playcap/save/41.sav
ns 1793294530.108 — BIT-IDENTICAL to t216/t217/t218 and still older than the
timeline baseline, so the "watchers died and hid a sitting" gap stays closed.
Zero saves since the 2026-10-29 13:22 end series. PROSE FIX banked: the gap is
1.992 s, not t218's 1.892 s (same conclusion, correct arithmetic).
(3) NEW CONTENT (the only non-reproduction): the idle answer's load-bearing
premise — "no open row can advance without play or a ruling" — was asserted but
never measured in t213 S7 / t218 S5, so t219 measured it. python3
scripts/ledger_audit.py: rows=19 open=['OQ-005','OQ-016','OQ-019','OQ-021']
closed=15, LEDGER AUDIT OK. Independent grep: six '| open |' markers at lines
232/583/1240/1403/1431/1451, ALL inside those four rows, none stray. Verdict:
the premise HOLDS — no neglected non-play-gated row exists, which is what makes
six idles acceptable rather than six wasted iterations. [verified]
(4) Watcher population unchanged as an incidental read — wrapper 27772 (bash, no
writer fd) + child 27774 + orphans 260988/290953/292085: no new orphans, no
retirements in ~14 h. Nothing killed; standing supervised-session ask restated.
HONEST NEGATIVE: OQ-016, OQ-021, OQ-019, OQ-005 all stay OPEN — no cited
measurement was obtainable without play or a user ruling, and no plausible
default was allowed to close anything. Gate + both ledger checks green.
NEXT: t220 is trigger-armed idle (two axes only), or a steering override — the
harness owns the next move, not a research iteration.

LANDED t218 (2026-10-30): NO SITTING — FIFTH CONSECUTIVE BYTE-IDENTICAL
ADJUDICATION (NO ledger row moved — strict-close honored; docs/re/_wip_t218.md
S1..S5 NEW; no new tools — r214_triage.py + one save-axis find did the whole
assigned job). THE ANSWERS:
(1) Axis 1: all three TRIGGER-A baselines equal the recorded values for the
fifth iteration running (ns_mtime 1793294532100000000, size 5,721,578,066,
tail-64KiB md5 9054cc6c66802e6f80431d4ffa1416ee; script RC=0), and the same
pass reports ZERO dosbox/ascend.exe processes, corroborating the file-side
negative from the process side. r1_t85g_sitting.py correctly NOT run (t152
trap: adjudicating an unchanged dir fabricates a sitting).
(2) Axis 2 (independent of watcher health): newest *.sav/*.gam under HOME
(1409 files, %T@-sorted) == playcap/save/41.sav ns 1793294530.108, BIT-IDENTICAL
to the t216/t217 reading and still 1.892 s OLDER than the timeline baseline ns
1793294532.1; 60.sav/59.sav/58.sav follow at 10 s spacing, all last-sitting end
saves of 2026-10-29 13:22. No save post-dates the baseline, so the
"watchers died and hid a sitting" gap stays closed.
(3) Watcher population unchanged as an incidental read of the triage call —
wrapper 27772 (bash, no writer fd) + child 27774 + orphans 260988/290953/292085
(all --no-exit): no new orphans, no retirements in the ~13 h since t217. The
standing supervised-session hygiene ask is restated; nothing was killed.
(4) NEW THIS ITERATION (the only non-reproduction content): _wip_t218.md S5 —
the idle-adjudication TASK SHAPE is itself exhausted as an information source.
Five identical results means an idle t219 adds nothing beyond re-printing
S1..S3, and every remaining open row is play-gated (OQ-016 clamp witnesses,
OQ-021 comparator firing), BLOCKED-USER (OQ-019 pricing ruling, OQ-005
index.txt + dims), or watchpoint-class (OQ-021 writer, needs a supervised
session). A recommendation about loop arming, NOT a research route; opens no
refuted route and closes nothing.
HONEST NEGATIVE: OQ-016, OQ-021, OQ-019, OQ-005 all stay OPEN — no cited
measurement was obtainable without play or a user ruling, and no plausible
default was allowed to close anything. Gate + both ledger checks green.

LANDED t217 (2026-10-30): NO SITTING — FOURTH CONSECUTIVE BYTE-IDENTICAL
ADJUDICATION (NO ledger row moved — strict-close honored; docs/re/_wip_t217.md
S1..S4 NEW; no new tools — r214_triage.py did the triage job exactly as
designed, RC=0). THE ANSWERS:
(1) All three TRIGGER-A baselines byte-identical a fourth consecutive
    iteration (ns 1793294532100000000 / size 5721578066 / tail-64KiB md5
    9054cc6c66802e6f80431d4ffa1416ee). Zero dosbox/ascend.exe comm-class
    processes => sitting script correctly NOT run (t152 trap).
(2) Save axis idle with BIT-IDENTICAL values to t216: newest .sav/.gam
    anywhere under /home/hrethric == playcap/save/41.sav ns 1793294530.108
    (then 60.sav 1793294520.040, 59.sav 1793294510.004); newest < timeline
    baseline ns 1793294532.1, so the watcher-death gap stays closed on the
    independent signal.
(3) Watcher population unchanged (from the triage script's own fixed census,
    not a new census): wrapper 27772 + writer child 27774 + orphans
    260988/290953/292085 — no new orphans, no retirements. Orphan-retirement
    remains a standing supervised-session user ask.
HONEST NEGATIVE (S4): no sitting => no new witness class => OQ-016/OQ-021 stay
open unmodified; OPEN-QUESTIONS untouched this iteration (nothing moved);
nothing beyond the two adjudication axes censused (t212 law); no static route
re-trod (t213 S7). Four axes-agreeing iterations (t214..t217) = steady-state
idle; only new play, a user ruling, or a supervised watchpoint session moves
the ledger.
Gate 0 + LEDGER AUDIT OK + LEDGER INDEX OK; NEXT=t218 sitting adjudication ONLY
(r214_triage.py + the one save-axis find by ns), else honest idle-wait +
standing asks.

LANDED t216 (2026-10-30): NO SITTING — THIRD CONSECUTIVE BYTE-IDENTICAL
ADJUDICATION + ONE PRECISION FIX (NO ledger row moved — strict-close honored;
docs/re/_wip_t216.md S1..S4 NEW; no new tools — r214_triage.py did the triage
job exactly as designed, RC=0). THE ANSWERS:
(1) All three TRIGGER-A baselines byte-identical again (ns
    1793294532100000000 / size 5721578066 / tail-md5
    9054cc6c66802e6f80431d4ffa1416ee), verified via r214_triage.py AND an
    independent in-session stat+md5 pass (different code path, same numbers).
    Zero dosbox/ascend.exe comm-class processes (via /proc/*/comm grep), caps/
    absent => sitting script correctly NOT run (t152 trap).
(2) Save axis idle-corroborated with a PRECISION FIX: newest save anywhere
    under /home/hrethric (1409 files, sorted by %T@) is playcap/save/41.sav at
    ns 1793294530.108 (2026-10-29 13:22:10), NOT 60.sav as t215 stated
    (minute-resolution imprecision; 60.sav is 1793294520.040). Both are the
    last sitting's end saves and both predate the timeline baseline ns
    1793294532.1; zero saves modified since 2026-10-29 18:00. Law stands,
    wording corrected: name the newest save by full ns, never wall-minute.
(3) Writer census REPRODUCED at fd level (t215 method): exactly four writer
    fds on live-timeline.jsonl — 27774/260988/290953/292085 (wrapper 27772
    zero) — NO new orphans since t215; the writer population is stable, which
    strengthens the t214 inflation figure's provenance. Orphan retirement
    remains a standing supervised-session user ask.
HONEST NEGATIVE (S4): no sitting => no new witness class => OQ-016/OQ-021 stay
open unmodified; nothing beyond the two adjudication axes was re-censused (t212
law); no static route re-trod (t213 S7). Loop is steady-state idle.
Gate 0 + LEDGER AUDIT OK + LEDGER INDEX OK; NEXT=t217 sitting adjudication ONLY
(r214_triage.py + the one save-axis find by ns), else honest idle-wait +
standing asks.

LANDED t215 (2026-10-31): NO SITTING + WRITER POPULATION MEASURED (NO ledger
row moved — strict-close honored; docs/re/_wip_t215.md S1..S3 NEW; no new tools
needed — r214_triage.py did the triage job exactly as designed, RC=0). Trigger
triage: all three TRIGGER-A baselines byte-identical a second consecutive
iteration (ns 1793294532100000000 / size 5721578066 / tail-md5
9054cc6c66802e6f80431d4ffa1416ee), zero dosbox/ascend.exe comm-class processes,
caps/ absent, no vfat/msdos mount => sitting script correctly NOT run (t152
trap). THE ANSWERS:
(1) NEW INDEPENDENT AXIS closes the "watcher died and hid a sitting" gap: the
    newest .sav/.gam ANYWHERE under /home/hrethric (1409 files, no date filter)
    is playcap/save/60.sav at 2026-10-29 13:22 — exactly the save the last
    sitting ended on — and ZERO saves modified since 2026-10-29 18:00. A player
    who advanced the game leaves a newer autosave slot regardless of watcher
    health, so idle is confirmed on a signal the capture pipeline cannot mask.
(2) WRITERHOOD MEASURED at fd level (/proc/<pid>/fd, not pgrep presence):
    EXACTLY four processes hold live-timeline.jsonl open for append — 27774
    (child of wrapper 27772, which holds NO writer fd) plus orphans
    260988/290953/292085, all r1_playcap_watch.py --no-exit. t214's 4.26x
    inflation figure now has its producer population verified; the
    orphan-retirement user ask is upgraded from inference to measurement.
    Method law banked in BLOCKED.md R1 runbook (writerhood = open fd; plus the
    save-axis corroboration recipe).
(3) LEDGER: OQ-016 + OQ-021 STATUS t215 lines appended (both rows STAY OPEN —
    witness classes unobservable without new play); nothing re-censused per the
    t212 law; no static route re-trod per t213 S7.
Gate 0 + LEDGER AUDIT OK + LEDGER INDEX OK; NEXT=t216 sitting adjudication ONLY
(r214_triage.py + the one save-axis find), else honest idle-wait + standing asks.

LANDED t214 (2026-10-31): NO SITTING + CAPTURE-HEALTH AUDIT (four-writer
multiplicity measured; NO ledger row moved — strict-close honored; docs/re/
_wip_t214.md S1..S8 NEW; tools r214_triage.py / r214_inflation_profile.py NEW,
RC=0). Trigger triage: all three TRIGGER-A baselines byte-identical, zero
dosbox/ascend.exe processes (comm-class matching — a pgrep -f "hit" was the
probe's own cmdline), zero new saves anywhere under /home/hrethric, caps/ empty,
no game mount, 240,249 rows unchanged -> sitting script correctly NOT run (t152
trap). THE ANSWERS:
(1) FOUR watcher instances share the capture dir: wrapper+child pair
    (27772/27774, the t115-sanctioned shape) PLUS three orphaned instances
    (260988 up since 10-28, 290953/292085 since 10-29) — NOT explained by the
    t115 pair law; live with --no-exit, appending to the same jsonl.
(2) RAW-ROW INFLATION MEASURED (r214_inflation_profile.py, whole-file streaming
    regex pass): 240,249 rows / 56,377 distinct (file,file_mtime_ns) keys =
    4.26x overall; per-key reps up to 12; per-4k-row append-order chunks drift
    1.96x -> ~10x -> reset 1.45x at the sitting boundary ~line 192k -> 3.66x at
    the tail. NO single correction constant exists.
(3) CLAIM-SAFETY AUDIT (the part that protects the ledger): every count banked
    from this file (t187 x1115 flight census via r1_t187_delta.py:30, t189
    68-sustained via r1_t188_state3_arbiter.py:20, the 28k trusted obs in
    diplomacy.md S11 / score.md S6) uses r1_stream.observations(trust=True);
    build_index dedupes on exactly (file,mtime_ns) and duplicate groups carry
    ZERO content conflicts (tail-1200 audit: rows differ only in wall) — first-
    wins is lossless, NO banked number needs restatement.
(4) TIMELINE-MINING LAW banked in docs/BLOCKED.md R1 runbook + OQ-021/OQ-016
    STATUS t214 lines: counts only via the trusted path; r214_triage.py as the
    pre-mining gate for any fresh sitting.
PITFALLS BANKED: (i) process-presence claims need comm-class matching — pgrep -f
matches the probing shell's own command line; (ii) the wall field is time-of-day
with NO date — binning w[-5:] silently bins MM:SS (my first-draft "hours");
binning code needs a unit check, and append-order is the safe time axis;
(iii) multi-instance watchers on a shared dir is a SILENT capture-health failure:
counts look fine, per-event facts are duplicated — audit the writer population
before trusting any new capture.
Gate 0 + LEDGER AUDIT OK + LEDGER INDEX OK; NEXT=t215 sitting adjudication ONLY
(r214_triage.py as the one triage call), else honest idle-wait + standing asks
(incl new watcher-retirement hygiene ask).

LANDED t213 (2026-10-30): AL-FORM [ship+0x62] VALUE-SOURCE CLOSED — MEASURED
NEGATIVE, NO >=2 PHASE EXISTS (docs/re/_wip_t213.md S1..S7 NEW; tools
r213_cfg_15b / r213_probe_a..e NEW, all RC=0). Trigger triage: timeline
mtime/size/tail-md5 ALL == frozen baselines, dosbox down -> no sitting; STATE
t212 item (b) stood. THE ANSWERS:
(1) BOTH al-forms live in the batcon ORDER-COMMIT dispatcher 0x156d4..0x17c25
    (t211 "UI/setup family" SUPERSEDED; Ghidra class batmode/batcon E1 per
    r1-savestate.md:393). Both sites stamp the ship order record
    (+0x62 phase, +0x63 target, +0x67 day-code, +0x68.. params) and call
    0x49f28 edx=0 in-place — the producer side of the t206..t211 consumer map.
(2) SITE 1 0x15c6d == phase 1 ALWAYS: [esp+0x50] has EXACTLY one byte-def
    (0x15c34, bl=1), and cutting the init block 0x15c14 from the CFG makes
    0x15c6d unreachable (641->564 blocks, r213_probe_e). Order-arg codes
    {5,1,0,2} land in the DAY byte [ship+0x67], never +0x62.
(3) SITE 2 0x15d98 == phase 0 ALWAYS: cluster [0x15d36,0x15e7c) in-edges
    EXACTLY {0x16329,0x16378,0x16391,0x163df}; the only def reaching the
    store is 0x16385 mov [esp],dh under gate 0x16376 test dh,dh ZERO-side
    (dh==[ebp+0xb0]==0); the dl=2 def 0x16361 is straight-line overwritten;
    the 1-def 0x15e23 jumps to the tail (0x15e7c: [ebp+0xb9]=1, call 0x16cf0,
    vtable [ebx+0xc]) never reaching the store.
(4) COROLLARY: with t211's constant-writer census the static [ship+0x62]
    writer population is COMPLETE and BINARY {0,1} — the cl>=2 arm at 0x49f28
    is defensive dead code in the original; REWRITE NO CHANGE (the
    per-engagement charge model is untouched).
(5) 0x156d4 has ZERO direct callers; sole image dword == 0x156d4 at file
    0x88408 (code-address table, magic pair 3c8efa35/42652ee1) — indirect
    registration; banked, NOT re-litigated (value verdict is intra-function).
(6) TASK (a) DONE: STATIC CORPUS FORMALLY EXHAUSTED (S7) — every remaining
    open-row residue is play-gated, BLOCKED-USER, or watchpoint-class.
PITFALLS BANKED: (i) t211's family label for 0x15bd0/0x15c00 sites came from
address-adjacency not edges — always edge-census a cluster before naming it;
(ii) packed-byte locals: def census must be on the BYTE form (mov byte
[esp],X) — dword writes at the same offset belong to the packed record and
dominate reads differently; (iii) functions_full.tsv sizes are HEX and the
containing-function span can be 9.5KB of jump-table-dispatched arms — a
linear decode is fine (2,673 insns, 1 gap) but CFG edges, not order, decide
reaching defs.

LANDED t212 (2026-10-30): OQ-021 DISPLAYED-COUNT WRITE SITE — STATIC ROUTE
EXHAUSTED, P7 PRODUCER CLAIM REFUTED (docs/re/_wip_t212.md S1..S7 +
score.md S9 NEW; tools r212_ref_census / r212_raw_and_ptr / r212_code_identity
/ r212_base_disp / r212_predicate_corr NEW, all RC=0). Trigger triage:
timeline mtime 1793294532 / size 5,721,578,066 / tail md5 9054cc6c... ==
frozen baselines, dosbox down, tree clean at 6bca4ce -> no sitting; STATE
t212 stood. THE ANSWERS:
(1) AICODE P7 "SCORED-STAR PRODUCER" IS THE WRONG SLOT: block 0x250aa..
    0x2523e writes ONLY inc word[0x48300] (0x2519b) + RMW 0x25217/0x25225 —
    OUTSIDE the displayed dword [0x482fb..0x482fe]; gated [0x10ba0]==-1
    (never fires in banked play); calls 0x77ece(0x838bf,0xd12)+printf 0x7865a
    per iteration = debug dump with line counter. aicode.md corrected in place.
(2) ZERO WRITERS image-wide, three controlled instruments: (i) capstone
    disp32+imm census region [0x48200,0x48400): only the presenter reads
    0x28074/0x280be + word[0x48300] triple + 0x48304 mark family; (ii)
    DECODER-FREE raw scan: LE fb 82 04 00 EXACTLY 4x = 2 relocation-table
    entries (0x2783/0x27ae — that window is the fixup table, shape 05 02
    <addr> 07) + the 2 presenter disp fields; (iii) 60.sav RAM pointer scan
    both reloc forms: all 17 dwords into the region are relocated operand
    fields of KNOWN instructions (byte-exact prefix+dword match; unrelocated
    forms absent). (iv) base+disp sweep: 145 mov/lea reg,imm bases in
    [0x47f00,0x48b00), forward-traced to register death = ZERO stores into
    the window (140,156 insns decoded, t211-count check caught my own
    silent-gap death at 8,961 — t201 pitfall RE-HIT and banked with the
    count-guard fix).
(3) CONCLUSION (honest negative, row OPEN strict-close): the 12..22
    oscillation needs a RUNTIME-COMPUTED store address (scaled-index /
    memory-loaded base / rep-span / register-transient); decisive instrument
    = dosbox-x write watchpoint on the slot — bundle that ask with OQ-021's
    existing comparator-firing interactive session.
(4) SEMANTIC NON-JOIN banked: V in {0,1} across ALL 90 trusted banked slots
    (mid-campaign slots no longer on disk); every V==1 slot has ALL 50
    byte[star+0x15]==0; current new-game ring: V=0 with 4 nonzero +0x15 —
    P7's owner-bit label joins FAIL against V; [unverified] flagged in
    aicode.md, do not re-assert as measured.
(5) REWRITE: NO change (OQ-021 default >1/2 campaign.cpp:738 stands;
    semantic surface untouched). Docs: _wip_t212 NEW, score.md S9 NEW,
    aicode.md P7 correction block, OQ-021 STATUS t212 appended, STATE ledger
    index mirrored.
Gate 0 + LEDGER AUDIT OK + LEDGER INDEX OK; NEXT=t213 (sitting check first —
mid-campaign slot now settles TWO residues; else al-form [ship+0x62] value
trace at 0x15c6d/0x15d98, then formal static-exhaustion declaration + honest
idle-wait list).

LANDED t211 (2026-10-30): COMMIT-CHAIN TAIL CLOSED — SECOND-DOOR NEGATIVE +
SPLASH BOUND NAMED (docs/re/_wip_t211.md S1..S6; tools r211_probe_a..f NEW,
RC=0). Trigger triage: timeline mtime 1793294532 / size 5,721,578,066 /
tail-64KiB md5 9054cc6c... == frozen baselines, dosbox down, tree clean at
0620fc9 -> no sitting; STATE t211 stood. THE ANSWERS:
(1) 0x49f28 IS THREE-ARMS (the assignment's "!= 1" imprecise): mov cl,
    [ship+0x62]; cl==0 -> 0x49f54 travel resolver (t83's walk law — same
    function); cl==1 -> 0x4a360 attack leg; cl>=2 -> NO call, result 0
    (xor eax,eax @0x49f2f precedes every arm). [ship+0x84] := result.
(2) SECOND DOOR: NO. 0x49f54 entry edges EXACTLY {0x49f37}; callee closure
    depth-3 (24 functions) ZERO hits into {0x4b740,0x43a4c,0x4cd90,0x4b8e4,
    0x4a360}; zero indirect jmp/call in the body (E8-only closure sound
    here). 0x4a360 entry EXACTLY {0x49f45}. Scanner VALIDATED first: E8 pass
    reproduces t210's six 0x4b740 callers exactly. => t210 commit law stands:
    committed orders pay 0x43a4c ONLY via the six censused callers.
(3) PHASE-FLIP BLOCK 0x4a350 (mov byte[eax+0x62],1 @ first insn + 0x67
    day-stamp clear) is UNBOUND corpus-wide: zero branch edges over 140,156
    decoded insns, zero image dwords, zero RAM aligned dwords == P0+0x4a350
    (3 saves, B=0x1bf4d8; t191 binding class checked). Honest negative —
    NOT claimed dead. cl==1 population = constant writers: ==1 sites
    0x415b4/0x423e2/0x4245f/0x43392/0x4340f/0x43843/0x43900/0x4a350/0x4a591;
    0x4a591 = the cat-0 volley PREAMBLE arms phase=1 (lea ecx,[eax+0xab] gizmo
    ring + order-kind switch DX->0x67 byte, assert 0x4a5b0 else), then the
    0x4a5c9 ring-slot scan (0xFF skip, cat byte [giz+0x7653e]==0 gate)
    dry-runs 0x49f28 edx=0 — exactly t210's dry-run loop, phase set in the
    preamble never by travel. al-form writers 0x15c6d/0x15d98 = UI/setup
    family (value residue, low priority); 0x42211/0x43188 alignment-suspect
    (t108 law: preceding byte undecodable).
(4) SPLASH BOUND NAMED: [esp+0x730]/[esp+0x734] (sole writers 0x4d09e/
    0x4d2a4) == 4 * FUN_00022304([engaging_ship+0x59]) — CO-LOCATED SHIP
    COUNT (ship table 0x3a095+0x162*i, i<108 movsx-bound, owner!=-1;
    location key = star record 0x13bc5+96*([[ship+0x59]+0xa]>>16) for kinds
    1/2/3, RAW lane handle for kind 4 — 0x22304 verbatim 0x22304..0x223a1).
    Multiplier <= N-1 (self-skip 0x4d0ac; loop-2 gates owner!=@0x4d2be +
    byte[0x12fd6+0x1ee*owner]==2@0x4d2ca). First-draft "lane-segment group"
    SELF-CORRECTED same session (star-garrison case).
(5) REWRITE: NO semantic change (OQ-019 boundary, t209/t210 pattern). Docs:
    OQ-016 STATUS t211 appended (residues re-listed); ai-dossier row 13
    residue line extended with the tail closure. PITFALLS: an E8/edge census
    must carry a positive control before a zero is trusted; t108 boundary law
    flags alignment-suspect store sites (preceding byte undecodable).
Gate 0 + LEDGER AUDIT OK + LEDGER INDEX OK; NEXT=t212 (sitting check first;
else OQ-021 displayed-count write-site via obj0 writer census + t191
runtime-slot method; fallback = al-form value trace then static-exhaustion
declaration).

LANDED t210 (2026-10-30): LAST STATIC RESIDUE OF THE 0x4b875 ATTACK-PRICE
LEG CLOSED — STACKING LAW MEASURED (docs/re/_wip_t210.md S1..S6; tool
scripts/r210_loop_nesting.py NEW, Tarjan-SCC loop detector, positive control
= finds the known 0x3a2c9 defense loop). Trigger triage: timeline mtime
1793294532100000000 / size 5,721,578,066 / tail-64KiB md5 9054cc6c... ==
frozen baselines, dosbox down, tree clean at 59755c4 -> no sitting; STATE
t210 stood. THE ANSWER: STACKING IS REAL, but per COMMITTED WEAPON / per
VICTIM, NOT per shot.
(1) 0x4b740 END-TO-END loop-free: every branch forward, single 0x43a4c call
    0x4b875, gated `cmp [esp+8],1; jne 0x4b8d8` @0x4b7f1 — mode==1-only
    RE-CONFIRMED at the gate itself; attacker-row select 0x13bc5+96*row
    @0x4b82c; tail (shield/hull subtract, death 0x49d2c) outcome-independent.
(2) SIX-caller census (E8 EXACTLY {0x1a146,0x39d9f,0x3a0b3,0x4bb56,0x4d191,
    0x4d2dd}, zero thunk sites): 0x1a146 mode-0 DEAD; 0x3a0b3 acyclic mode-1
    (item-0x17 t204 family); 0x4bb56 inside cat0 handler 0x4b8e4 (its ONLY
    0x4b740 edge), and the volley loop 0x4a5c1 calls 0x49f28 with edx=0
    (@0x4a5ec) = DRY-RUN, so t88a's commit law holds — volley never charges;
    0x4d191/0x4d2dd INSIDE the splash loops 0x4d0a5..0x4d1a4 / 0x4d2ab..
    0x4d2fd of cat-5 dispatcher 0x4cd90 (sole caller 0x4a3c4 = dispatcher
    cat5 arm; mode invariant [esp+0x73c] sole writer 0x4cd9d; gates owner!=
    victim @0x4d2be + race-alive byte[0x12fd6+494*owner]==2 @0x4d2ca).
(3) COMMIT LAW QUANTIFIED: command-exec 0x2547c loop 0x2550c..0x25527,
    bound = matched-gizmo count; ONE mode-1 arm per matched gizmo (ah==3 gun
    -> 0x25560 -> 0x49f28 -> 0x4a360 -> 0x4b8e4 -> 0x4bb56; ah==2 ability ->
    0x25570 -> 0x39c10 -> dispatcher); ah==1 ALSO hits assert trap 0x2a438
    (t88a correction: 'ah>=4' -> 'ah==1 or ah>=4').
(4) REWRITE: NO semantic change (OQ-019 boundary rule, t209 pattern) —
    campaign.cpp:1935 comment rewritten to cite the t210 law; the per-
    engagement charge is the DOCUMENTED UNDER-MODEL (under-fires per extra
    committed weapon at the same victim + per splash victim beyond first).
(5) docs: NEW _wip_t210.md S1..S6, _wip_t204.md AMENDMENT (S2/D4 'per shot'
    mechanism corrected), ai-dossier row 13 residue amended (stacking
    RESOLVED), OQ-016 STATUS t210 appended. SELF-CAUGHT x3: capstone
    operand-type constant (CS_OP_IMM==2, not 3 — first CFG pass silently
    zero edges); back-edge != target<=site (loop heads can sit mid-range —
    use SCC); '0x4cd90 reached only indirectly' claimed from a literal-only
    search before running the E8 pass (0x4a3c4 exists).
OQ-016 STAYS OPEN (strict-close): zero in-corpus clamp witnesses (play-
gated); invasion defense law + per-ship channel unmodelled (OQ-019);
runtime entity-loop bounds play-gated; [0x13bc4] semantics other-family.
Gate 0 (comment-only rebuild) + LEDGER AUDIT OK (rows=19 open=
OQ-005/016/019/021). NEXT=t211 (sitting check first; else 0x49f54 else-
branch second-door census + splash loop-bound array identity; no
combatPhase semantic change without a cited per-commit loop).

LANDED t209 (2026-10-30): LAST TWO STATIC-LAW RESIDUES OF THE 0x3a174
INVASION LEG CLOSED — OUT-PARAM CALLER LAW + CLAMP-VS-REPEL POSITION.
Trigger triage: timeline mtime 1793294532 / size 5,721,578,066 == frozen
baselines, dosbox down, tree clean at 1b00c13 -> no sitting; STATE t209
stood. LAWS [all cited, docs/re/_wip_t209.md S1..S6; windows via
r205d_windows + REVENV python (project .venv lacks capstone)]:
(1) OUT-PARAM LAW CLOSED: 3rd arg = pointer in EBX (->ECX @0x3a17f);
    sole writer 0x3a35e `mov [ecx],eax` (284-insn full-body operand pass:
    zero other [ecx] writes, ECX unrewritten before the store, NO ret in
    [0x3a174,0x3a35e), assert arms -> 0x2a428 vendor reporter never
    returns); value = defense result [esp+0x14] FORCED 1 iff ability byte
    row+0x19d == 0 — t207's [unverified] witness reading VERIFIED; value
    doubles as strip-loop bound (min-1 defense consumption).
(2) CALLERS DISAGREE (the finding): engine caller 0x42c8e never pre-inits
    [esp+0x30c], DISCARDS the return (0x42c97 clobbers EAX; 0x42c9c =
    identity assert 0xbc4), overwrites the slot @0x42cba with the 0x39894
    return -> out param DEAD in the engine path; 0x3d951 = UI announcement
    family (residue (c) closed by measurement): reads [ebp-0x24]==1 ->
    message 0x1c vs 0x1d (0x21a20), ids 0x1fc5/0x1fd3 (0x56d1c), UI words
    [ecx+0xcb1/0xcb3/0xccc].
(3) CLAMP POSITION CLOSED (t207 DOCUMENTED DIVERGENCE): clamp 0x3a25a..
    0x3a291 runs AT ATTEMPT TIME — before the defense score is even
    counted (loop 0x3a2c9..0x3a325, result select 0x3a327); success-vs-
    repel branches ONLY at 0x3a45c; caller tail outcome-INDEPENDENT. =>
    original pays the guarantee-war clamp on a REPELLED invasion too;
    rewrite capture-branch wiring = documented UNDER-MODEL (per-attempt
    wiring = OQ-019 boundary, NOT done). NO semantic change: campaign.cpp
    divergence comment replaced with the cites (blast radius trivially
    nil), _wip_t207 S7e (b)+(c)+divergence lines closed, diplomacy.md §19
    t209 update, OQ-016 STATUS t209 appended. Row STAYS OPEN (strict-
    close): zero in-corpus clamp witnesses unchanged; defense law
    unmodelled; per-shot stacking (-> t210); [0x13bc4] other-family.
PITFALLS banked: capstone operand pass must skip cmp/test when hunting
writes and must know ECX reg-id mapping (rname check, not magic ints);
0x2a428-style assert reporters make 'no early ret' claims conditional on
assert arms not returning. Gate 0 + LEDGER AUDIT OK + LEDGER INDEX OK;
NEXT = t210 per-shot stacking vs per-engagement aggregate at 0x4b875.

LANDED t208 (2026-10-30): POSITIVE E2E PIN FOR THE GUARANTEE-WAR CLAMP +
RESIDUE-LINE HOUSEKEEPING. Trigger triage: timeline mtime 1793294532 /
size 5,721,578,066 == frozen baselines, dosbox down, tree clean at e77fd03
-> no sitting; STATE t208 stood. CODE: NEW header-inline scenario hook
setIndustryForTest (campaign.h — mirror of ind_, NO production call site,
zero semantic delta); buildFixture207 gained a playerSpecies param (-1
default keeps T3's negative arm). PIN invasion_capture_war_e2e_t208:
player = SA_SuperMarines via CampaignConfig::playerSpecies ->
ability_[kPlayer] (campaign.cpp:234-235), industry 50 clears the invasion
ship-cost gate (:1895), one advance(): capture RAN (starOwner(1)==0),
handler -20, clamp 320->280, chooser DeclareWar flipped dipState_.atWar
and the post-advance cell == 280 - negPlayerTurns/4 EXACTLY (mood(1)==0
carried from t204's 320 pin); without the clamp atWar stays false
(320-neg/4 >= DECL 290 -> act None) — both arms distinguishing.
SELF-CAUGHT: first run failed 3/3 arms — the playerSpecies param existed
but was never assigned into cfg (capture never ran); fixed. 134 tests
0 failed. BLAST RADIUS UNCHANGED (header-inline hook + test only per the
t206 rule; Control t1255 / Extinct t979 stand). OQ-016 STAYS OPEN
(strict-close): the e2e pin proves REWRITE wiring, not original runtime —
zero in-corpus clamp witnesses unchanged; out-param + 0x3d951 context +
clamp position + OQ-019 boundary all banked for t209. Docs: OQ-016 STATUS
t208 appended; ai-dossier gap row 13 residue amended ('planet-event
callers unwired' STALE -> per-ship channel = OQ-019 family);
diplomacy.md §19 t208 update; _wip_t207 S7e(a) CLOSED; new doc
_wip_t208.md. PITFALLS: e2e pins must wire the lever they add (param ->
cfg) or they silently test the negative arm twice. Gate 0 + LEDGER AUDIT OK
+ LEDGER INDEX OK; NEXT = t209 out-param caller-law + 0x42c8e repel-position
tail.

LANDED t207 (2026-10-30): PLANET-EVENT CALLERS OF 0x43a4c CLOSED +
GUARANTEE-WAR LAW CODED/PINNED. Triage: timeline frozen-baseline size,
tree clean at 099e6c4 -> no sitting; STATE t207 stood. LAWS [all cited,
docs/re/_wip_t207.md S1..S7e; windows work/t207_w1..w16 via
r205d_windows (REVENV python -- project .venv lacks capstone, re-hit);
tools r207_disp_cluster.py + r207_opinion_census.py RC=0]:
(1) E8 full-image caller census of 0x43a4c EXACTLY {0x39fba,0x3a255,
    0x4b875} -- t204's thread fully accounted.
(2) 0x39f00 = GUN-BOMBARDMENT planet path (sole caller 0x4c97f inside the
    gizmo-attack shared tail; success+mode1+cat-0 gated after power
    subtract): victim = planet owner byte +0x57 (0xff skips), dip price
    FIRE-AND-FORGET + one-item loss tail; rewrite HONEST NO-DELTA.
(3) 0x3a174 = INVASION/CAPTURE resolution (0x42c8e = t179 invasion leg):
    item-0x17 slot -> ship 0x3a095+0x162*i via 0x396cc; on the handler's
    -1 return, CLAMPS attitude cell to DECLARE_WAR-10 while still above
    the line => INVASION GUARANTEES WAR (t180 chooser fires; 200/200
    fresh pairs slam-eligible MEASURED). Defense law (invmod vs 0x12 +
    2*0x13, strip via 0x496e4, deactivate via 0x38840, event 0xd)
    measured, per-ship = OQ-019 boundary, unmodelled.
(4) SCALE-2 ALGEBRA CORRECTION: compiler splits 494 as 247x read scale-2
    -- [eax*2+0x12fb3] is diplo-row+0x19d ability byte (distribution
    {0,2,11,19} == t202 census), 0x12fdf+494v = +0x1c9, 0x12fc8+494v+2a =
    the ATTITUDE cell (NOT the third-party matrix -- my S4 draft was
    wrong, corrected same session).
CODE: guaranteeWarOnInvasion (diplomacy.{h,cpp}) wired at combatPhase
capture branch; pins test_invasion_war_t207.cpp x3, 133 tests 0 failed;
BLAST RADIUS UNCHANGED Control t1255 / Extinct t979. OQ-016 STAYS OPEN
(strict-close): zero in-corpus clamp witnesses; positive e2e needs
owner-0 guaranteed capture (fixture self-caught 320!=280); clamp-vs-repel
position undetermined statically. PITFALLS capstone disasm() STOPS at
first undecodable byte -- seed-and-restart loop (r207_disp_cluster
pattern); compiler 494=247x scale-2 split on diplo rows; test ability
vector indexes OWNER not attacker. Gate 0 + LEDGER AUDIT OK + LEDGER
INDEX OK; NEXT=t208 player-guaranteed-capture e2e pin for the clamp +
residue-line housekeeping.

LANDED t206 (2026-10-30, this session): ATTACKED-MARK CONSUMER LAW
MEASURED — THE 0x48304 BYTE IS TWO INDEPENDENT CHANNELS, AND NEITHER FEEDS
DIPLOMACY VALUES OR AI. Trigger triage: timeline size 5,721,578,066 ==
frozen baseline, dosbox down, tree clean at d9db21a -> no sitting; STATE
t206 stood. LAWS [all cited, docs/re/_wip_t206.md S1..S7 + diplomacy.md
§18 NEW; windows work/t206_w1..w7.txt via r205d_windows; function spans
from functions_full.tsv (OVERLAPPING entries — pick tightest); E8 edge
census over the FULL image for callers]:
(1) VICTIM BITS 1..7 (writer 0x43afa, t204): sole mid-play consumers are
    INSIDE THE ORDER RESOLVER 0x41260..0x43270, both gated owner==current
    player [0x7458e]: 0x41610..0x41661 unit-at-star -> status byte |=0x20
    ("under attack" alert); 0x42b7d..0x42be8 slot scan -> result nonzero
    (action-availability eligibility; WAR-relation skip guard 0x42bb1 sits
    inside the same loop). NO diplo-value feed, NO AI target pick, NO
    emitter. => the rewrite's unconsumed attackedMarks()/attackedAt()
    mirror is FAITHFUL (no code delta); gap row 12 residue SHRINKS.
(2) t204's PERMANENT claim SURVIVED HEAD-ON (the task's key question):
    0x4610b/0x4611c = cl=[star]; or cl,1; [star]=cl — an OR-set of BIT 0,
    no decay, no transfer. Sole victim-bit clear anywhere = the scenario-
    init fill 0x25008 (mov eax,0x48304/call 0x76e30) in star-init 0x24f24
    (single caller 0x55f06).
(3) BIT 0 = contact/announcement channel, never touched by the attack
    handler: 0x45e48 (march-body caller 0x4a90a, ship-owner==player gate;
    bit0 GATE 0x45e93 BEFORE fire-then-latch 0x4611c; undiscovered-races
    test byte[row+0x1c0]==0; codes 3/0x14 by star-vision; 0x55a60's EAX
    0x7a35c = the event-RING game object, aicode :979/:1042 — NOT a string,
    bytes there are code re-measured); 0x46144 first-contact ESTABLISH
    (0x4a932 vision-already branch; relation byte 0->1 PEACE init 0x461a8
    + contact bookkeeping; gate 0x46213; latch AFTER fire 0x4623e; codes
    8/9); 0x24dd0 turn-advance notice producer (callers 0x55ed0/0x55f98
    pass EAX=0x12e10; CLEARS bit0 on ALL stars first — bound u16@0x16145
    MEASURED 50 == star count 20/20 by NEW script
    r206_mark_context_census.py RC=0, C1 dword[0x12e10+2]>>16==0 20/20 —
    then latches and announces AT MOST ONE star/call (event 0x13) iff
    vision byte +0x15 & occupant owner!=player & relation
    [owner*0x1ee+0x12fd6]==2 & u32[occ+0x88]>0). Call-scoped duplicate-
    notice suppression, NOT a permanent star state (S5 self-correction).
(4) HONEST NEGATIVE (strict-close; OQ-016 STAYS OPEN): C3 re-measured
    window [0x48304,+0x40) ALL-ZERO 20/20 — zero witnesses for EVERY
    branch of the bit-0 machinery (corpus is post-first-contact, nobody
    fires at a non-at-war power); event codes 3/8/9/0x13/0x14 are ring
    codes decoded only as "queued announcement"; [0x13bc4] semantics still
    open (other-family saves needed).
(5) CODE/PINS: campaign.h comment rewritten to the two-channel law; NEW
    pin mark_channels_separate_t206 (attack mirror never carries bit 0;
    victim bits only on engagement cells) — 130 tests 0 failed. BLAST
    RADIUS: SEMANTIC CODE UNCHANGED (comment + test only) — no CLI re-run
    owed; t205's Control t1255 / Extinct t979 stand. Docs: ai-dossier gap
    row 12 residue line amended. PITFALLS BANKED: functions_full.tsv spans
    OVERLAP (Ghidra nested entries — attribute to the tightest containing
    span, else 0x45e8d "belongs" to six functions); .SAV member is the
    ZIP entry NAMED "Memory" (a size->0x200000 heuristic silently found
    zero saves; use r205's read("Memory") pattern); mid-window capstone
    seeds drift a couple bytes — anchor on an instruction whose jcc target
    lands on a decode boundary and re-verify (R108). Gate + LEDGER AUDIT +
    LEDGER INDEX below. NEXT = t207 planet-event callers 0x39fba/0x3a255.

LANDED t205 (2026-10-30, this session): TABLE IDENTITY ADJUDICATED — 0x13bc5
stride 0x60 is the per-STAR runtime STAR RECORD TABLE (t200 wins; the per-
race/"species table" readings are the losers). Trigger triage: timeline size
5,721,578,066 == frozen baseline, dosbox down, tree clean at 6c144fe -> no
sitting; STATE t205 stood. WITNESSES [docs/re/_wip_t205.md S1..S8; tools
r205_table_identity.py (20-save census), r205b_operand_census.py (disp32 +
indexed), r205c_strided_consumers.py (IMMEDIATE-form bases — PITFALL:
capstone CS_OP_IMM==2, an interim rev used type==1 and printed a FALSE zero),
r205d_windows.py (verbatim windows) all RC=0]: rows 0..49 initialised 20/20,
u32[+0] in {0..12} ALL 50 rows, name "Vega" row0, boundary == star count
(u16[0x16145]==50) NOT race count (4); 36 absolute-base sites on 0x13bc5;
stride-96 idiom verbatim 0x39f8b..0x39f9c/0x4b823..0x4b834; self-handle law
MEASURED dword[0x13bc5+96k+2]>>16 == k (20/20). 0x13bc4 = ABSOLUTE SCALAR
global: all 8 refs scalar byte reads (0x2b848/932/a19 three-way switch,
0x39070/0x40bdd ==2 gates, 0x3f086, 0x40955, 0x43a99), ZERO strided refs,
ZERO enumerated writers (rep-stos/copy init — outside operand enumeration);
live value 1 20/20, ==2 arms never fire in captured scenarios (semantics need
other-family saves — banked open). CONSEQUENCES LANDED: (1) t204's EBX =
"species record per race" CORRECTED to the engagement-location STAR record
(0x4b81a [esi+0x59] -> 0x4b82c -> 0x4b868); (2) [0x48304] is a PER-STAR BYTE
ARRAY (byte[0x48304+star_idx] |= 1<<victim) — rewrite attacked_ upgraded from
one byte to per-star vector + attackedAt(star), attackedMarks() OR-reduce
keeps the t204 pin surface; honest negative SURVIVES (full window
0x48304..+0x3f all-zero 20/20 — re-measured under the array reading); pin
diponattack_mark_is_per_star_t205 discriminates array-vs-global; 129 tests
0 failed; BLAST RADIUS UNCHANGED seed 2024 Control t1255 / seed 42 Extinct
t979 CLI. (3) Docs corrected in place: diplomacy.md S17.1 (EBX + bitmap
shape) + S17.3 (identity RESOLVED), income-law.md S6-caveat(a) (species
table REFUTED, star-modifier candidate survives), ai-dossier S2 para + row
11 housekeeping DONE (ForcePeace WIRED :1636, CauseWar WIRED-PARTIAL :1720,
"Hatred" is NOT a 21-token roster token). OQ-016 STATUS t205 appended; row
STAYS OPEN (mark consumer law unmapped -> t206; zero in-corpus witnesses;
0x13bc4 semantics). PITFALLS BANKED: capstone imm-operand type == 2 (a
type==1 census silently reports zero bases); test fixture owners referencing
race 2 with aiCount=1 SEGFAULTS buildPhase (no dip row) — use default owners
or supply every dip file. NEXT = t206 attacked-mark CONSUMER law.

LANDED t204 (2026-10-30, this session): DIPLOMACY-ON-ATTACK CODED + PINNED
(gap map row 13 GAP -> MODELLED — the last pure-GAP static row). Trigger
triage: timeline size 5,721,578,066 == frozen baseline exactly, dosbox down,
tree clean at 38f728c -> no sitting; STATE NEXT stood. LAWS [all cited,
docs/re/_wip_t204.md S1..S4 + diplomacy.md §17]: FUN_00043a4c 0x43a4c..
0x43b0e verbatim (capstone revenv). TWO CORRECTIONS vs t87 S2f-b: (1) the
subtrahend key is MOVSX of the BYTE at [0x13bc4] (not word) — live census
20/20 playcap saves == 1 => d=20, state-3 doubled 40 (the assignment's
"word==2 => 30" did NOT reproduce — banked as correction, pins parameterize
govByte 0/1/2); (2) the state-3 clamp is a CEILING (0x43acc..0x43ae7: JLE
skips when att <= word[obj+0x1cf]=BREAK_ALLIANCE; slams to line-10 ONLY when
still above) => firing at an ALLY GUARANTEES the alliance dies — T4 pins
this end-to-end (560->520>510->500->break; without the ceiling no break).
CALLER CENSUS (E8 byte-pass, first ever): EXACTLY {0x39fba, 0x3a255, 0x4b875};
the combat one fires BEFORE the shield/hull subtraction 0x4b87a/0x4b888 (the
price of FIRING — repelled attacks pay too); row=VICTIM (0x12e16+0x1ee*r),
EDX=attacker; EBX=record at 0x13bc5+0x60*r (identity question -> t205);
bitmap base [dword[edi+2]>>16], bit = 1<<victim (0x43afa). Rewrite:
applyAttackDipCost + kAttackDipGovByte=1 (diplomacy.{h,cpp}); Campaign::
attacked_ byte + attackedMarks() mirror [0x48304] PERMANENT (no clear incl.
peace); combatPhase wired at the 0x4b875 position, player-attacker only
(two-party projection, gap row 12 — documented, no ladder invented). Pins
test_diponattack_t204.cpp x4 — 128 tests 0 failed. BLAST RADIUS: MEASURED
Control t1255 / Extinct t979 FINITE, unchanged (CLI). Mechanism: under the
FFA default dipState_.atWar is FALSE (only DeclareWar latches it), so player
attacks DO pay -20/engagement there — no threshold crossed an outcome on the
checked seeds (falling attitude only makes ProposePeace rarer). HONEST NEGATIVES (OQ-016 STAYS OPEN, strict-
close): zero in-corpus attack-event witnesses ([0x48304]==0 20/20 — nobody
fired at a non-at-war power in captured play); [0x13bc4] row identity open
(-> t205); planet-event callers unwired (no planet-attack-event model); per-
engagement aggregate vs per-shot stacking (S2i pattern). PITFALLS BANKED:
(1) an aiCount-1 alliance fixture trips end-unit Unification at t1 -> over()
-> later advance()s silently no-op — pins need a second never-allied AI
(race02 Orfa works); (2) CEILING engage/skip direction bites (low line
ENGAGES). Docs: ai-dossier row 13 MODELLED + §2 para corrected; combat.md
S2f-b t204 block ("star-defense contribution" VOID). Gate 0 + LEDGER AUDIT
OK + LEDGER INDEX OK; open = 005/016/019/021. NEXT = t205 table identity.

LANDED t203 (2026-10-30, this session): FREE-TECH GRANT MEASURED + CODED +
PINNED (gap map row 7 GAP -> MODELLED). Trigger triage: timeline size
5,721,578,066 == frozen baseline exactly (md5 3d6c9cce), dosbox down, tree
clean at 7dc461c -> no sitting; STATE NEXT stood. LAWS [all cited,
docs/re/_wip_t203.md S1..S4]: FUN_00046e84 0x46e84..0x46f9d verbatim
(capstone revenv). GATE CORRECTED vs dossier S3c: caller 0x3913b is
ITEM-BLIND — key = completing slot byte0 bit3 (ROCK marker, mapgen 0x37f7b);
placement rule D 0x38533..0x38552 legal iff (byte0&8)==(itemIdx==0x26) makes
the Xeno Dig the only item ever on rock => dig-on-rock completion IS the
grant trigger; rock branch clears rock (0x39156) + frees slot (0x39164, dig
consumes itself — explains banked T38 "zero |8 item bytes ever") THEN calls
0x46e84; non-rock = normal activation 0x3917a, no grant. GRANT = uniform rng
over unowned rows MINUS the research-target word (0x46ee6 ==DAT_00076492),
NO prereq legality call at all (dossier "legal rows" CORRECTED — grants land
deep, prereqs unmet); rng 0x7824f 15-bit LCG always >=0 (idiv uniform);
empty-guard 0x46f1c precedes the draw; mark +0x4a/+0x4b; target word NEVER
written. Rewrite: freeTechGrantFor (campaign.cpp/h, rng_ stream documented
default), drawItemCell dig exemption (dig draws draw ONLY from rock cells),
buildPhase dig-completion branch. Pins test_freetech_t203.cpp x5 (+1 owned
per grant + exhaustion -1, target-exclusion, e2e dig-on-rock grants exactly
1, dig-on-nonrock 0 + item stands, seeded determinism) — 124 tests 0 failed.
BLAST RADIUS: seed 2024 Control t1255 FINITE (unchanged vs t202b), seed 42
Extinct t979 FINITE (CLI this session). ai-dossier row7 MODELLED + S3c
correction; aicode.md S3b correction paragraph. HONEST RESIDUES (row OPEN,
strict-close): zero in-corpus grant-event witnesses (0x55a60 code-0x16 never
observed in ring — grant is rare: dig-armed AI + dig completes + legal rock);
event string + EDI quirk unmodelled (cosmetic); completion-tail rng ORDER in
the original single stream unrecoverable. TOOL PITFALL banked: capstone
lives ONLY in ~/tools/revenv (project .venv lacks it).
LANDED t202b (2026-10-30, this session): DEMOLISH CHANNEL CODED + PINNED
(gap map row 4 GAP -> MODELLED; t202's measured law set transcribed with
zero new measurement). Trigger triage: timeline size 5,721,578,066 ==
frozen baseline exactly, tail md5 faa71c20, dosbox down, tree clean at
9520c9a -> no sitting; STATE NEXT stood.
WHAT LANDED [all cited, docs/re/_wip_t202b.md T4 + _wip_t202 S1..S13]:
(1) usedPopFor UPGRADED to the MEASURED M4 law = item-UPOP sum over
slotted items (excl item 23 Ship, excl flags&0x40 rows 20/21, gov-35
Automation term kept) — pending-term removed (INERT 2900/2900).
(2) buildPhase AI branch = original order: over-cap 0x3f178 (picker
overCapDemolishPick — skip CB, skip MPOP!=0, STRICT max UPOP, first-cell
ties, UPOP==0 never wins; no candidate -> skip selector = 0x3f20b assert
path; post recheck used'>=pop -> skip) -> no-free-pop 0x3f220 -> PRE-
TRIAGE 0x3f252 (runs iff eNR<2 OR eNR==eB && !BuildOnBlack) -> sweep
0x3f354 minRequiresDemolishPick (NO CB skip, 0xFF REQUIRES participates)
-> shared gate 0x3f41e -> t201 chain + scorer UNCHANGED. Cell-order slot
view via stable_sort on itemCells; demolishAt rebases indices (both
sweeps can fire in ONE turn via the 0x3f22f fallthrough).
(3) BLAST RADIUS MEASURED: 0x3f220 is now real traffic — AI builds
serialize behind pop growth (seed 42 first colony t169->t279, seed 2024
Control win t831->t1255, both CLI-verified FINITE). Three pacing guards
+ gate.sh budget widened WITH dated comments (pacing windows, NOT laws):
test_campaign 220->420 turns, test_species/test_ships 1200->1600, gate
1200->1600.
(4) PINS tests/test_demolish_t202b.cpp (4 tests): picker edge classes
O1-O6/S1-S5, used-pop exclusions + gov-35 reversibility + band formula
intact, end-to-end over-cap (one Factory gone in ONE advance(), CB
alive, queues), end-to-end barren-triage CB sweep (REQUIRES 5 < 255).
119 tests 0 FAILED.
(5) DOCS: income-law.md S9 OVER-CAP para CORRECTED (largest-MPOP ->
largest-UPOP-among-MPOP-0 with 0x3f1bb/0x3f1c1 byte identities) +
pre-triage gate + sentinel reason + M4 line folded; ai-dossier gap row 4
-> MODELLED; OQ-016 STATUS t202b appended — row STAYS OPEN (strict-close:
still zero in-corpus demolition EVENT witnesses; residues +0x54 mid-game
identity, 0x3f4b8 cmd1-on-tail, M3-shape 140-row discriminator).
TOOLS: scripts/r202b_item_table.py (planitem dump mirroring
loadPlanItems; PITFALL: rows are NAME-line THEN numeric-line, names may
contain spaces, flags = OR 1<<pos over v[7:-1] — first two naive parses
mis-aligned silently).
Gate 0 + LEDGER AUDIT OK (open OQ-005/016/019/021). NEXT = t203 free-tech
grant above.

LANDED t202 (2026-10-30, this session): AI GAP ROW 4 DEMOLISH CHANNEL —
LAWS FULLY MEASURED; CODE DEFERRED to t202b (budget stop; measurements
were the risk, they are banked). Trigger triage: timeline size == frozen
baseline exactly, dosbox down, tree clean at 85afdf7 -> no sitting.
KEY MEASUREMENTS [all cited, _wip_t202.md S1..S13; tools NEW
r202_triage_census.py RC=0 (dump work/r1/t202_triage_dump.txt),
r202b_layout_verify.py, r202c_usedpop_adjudicate.py,
r202d_usedpop_models.py RC=0]:
(1) +0x4c USED-POP = UPOP sum over ALL slotted items (excl item23 /
item flags&0x40 / slot flags&2) — 2760/2900 exact; residual 140 =
act+1 Automation shape; pending-term INERT 2900/2900. t28 "inactive/
pending-only" READING SUPERSEDED.
(2) OVER-CAP 0x3f178 IS LIVE TRAFFIC: 220/2900 fire (always used==pop
==cap); VICTIM LAW CORRECTED (t28 had bytes inverted): skip item 5,
skip MPOP!=0 (0x3f1bb), pick LARGEST UPOP (byte+4, 0x3f1c1, strict>,
first cell ties, UPOP>0 floor). No candidate -> vendor assert + RETURN.
(3) PRE-TRIAGE GATE 0x3f252 (never banked by t28): triage RUNS iff
emptyNonRock<2 OR (emptyNonRock==emptyBarren AND ability != 2); ability
byte = diplo row +0x19d (measured 60.sav {0:19,1:2,2:11,3:0,4:8}; ==2 ==
SA_BuildOnBlack). Healthy planets NEVER triage.
(4) SWEEP 0x3f354 verbatim: margin cap-pop, MPOP<margin, min-REQUIRES
strict-<, 0xFF PARTICIPATES (sentinel 0x1869f never prunes — t28's
"never binds" stands with corrected reason); NO item-5 skip. Post-
demolish recheck path provably unreachable from the pre-guard (banked).
(5) t201 CALLER WIRING RE-VERIFIED FAITHFUL: FUN_0003fc4c returns
0xffffffff ON EVERY SUCCESSFUL BUY and 0 on no-force (t201_fc4c lines
19/62/116/158/193 vs 3feb9) — je-0x3f74c means forced->no-scoring; the
rewrite's item-id/-1 mapping matches. A mid-session "inversion bug"
claim was WRONG (S12 documents both states so nobody re-fixes it).
(6) ZERO in-ring demolition EVENT witnesses (adjacent-save multiset diff
0/20 pairs — same-turn ring cluster); branch PRECONDITIONS measured
instead (honest negative, strict-close: no row moved).
TOOLS PITFALLS BANKED: member base B = H + 0x1BF450 (H=find_base vote
- 0x1BF450; wrong SIGN wraps indices to zeros SILENTLY — item-table
name self-check mandatory); slot walk bound must cover cap<=83 (a
capw<40 bound silently skipped every big planet); planitem.txt item rows
start after the '39 22 9' line. rewrite/ UNCHANGED this session (one
drafted usedPopFor edit REVERTED — land it with its pins in t202b).
Gate + ledger checks below.


LANDED t201 (2026-10-29, this session): AI THREAT-BYTE INPUT + EMERGENCY
CHAIN CLOSED WITH MEASUREMENT; REWIRED + PINNED (gap map row 3 ->
MODELLED). Trigger triage: timeline size == frozen baseline exactly,
dosbox down, tree clean at 8ac9dd8 -> no sitting.
KEY LAWS [all cited, ai-dossier.md S10 + _wip_t201.md S1d/S1e/S1f]:
(1) THREAT INPUT: +0x59 = #{ACTIVE slots whose item file FLAGS word bit8}
(shield class EXACTLY {18,19,26,27}) VERIFIED 2900/2900 corpus records;
+0x58 = bit4 set ({17 Tractor Beam, 28,29,30 orbital whoppers}) 2880/2900
(all 20 misses = ONE record, the evaluator self-init 0x3fb3e signature);
recalc FUN_00038ba4 ZEROES+rederives both every run (xored locals @0x38baf
-> stores @0x38ef7/0x38efe); only other writers = self-inits + save
round-trip FUN_0003a558 (snapshot deserialiser callers 0x258dd/0x26044).
Threat = SELF-ASSESSED defence infra, not enemy scan. (2) EMERGENCY CHAIN
FUN_0003fc4c full verbatim control flow re-disassembled (t28's summary was
directionally right; THREE corrections banked: chain-A item is 38 Xeno dig
not 22; chain-B needs item 22 PRESENT and its precondition failures are
HARD EXITS skipping D+E; chain-D IND gate is STRICTLY >20): A rock-armed
Xeno dig > B Shield18 > C MegaShield19 with period tiers 200/225/300/400
VERBATIM at 0x3fd73/7f/8b/92 (hop==0/1/<4/>=4, hop byte DAT_00045beb,
FIRE iff UNSIGNED (day-[+0x67])/period > +0x59 @0x3fda1; mega-illegal
falls to buy-18-AGAIN shared block) > D Cloaker11 > E fallback template
MEASURED live {12,13,14,15,37}; ret -1 skips scoring @0x3f4da. (3) The
0x89360 template belongs to FUN_0003f758's shipyard tail (obj1 data ==
pool 0x67b0 window {28,29,30,0,26} orbital-defence) — NOT this chain.
REWRITE: emergencyChainPick (pure) + emergencyPeriodFor +
shieldThreatFor/orbitalThreatFor + digQueuedOrDone armed by the rock event
(same original branch 0x37f7b) wired into buildPhase AI branch BEFORE
scoring (0x3f4d5 ordering); documented defaults INSIDE code comments
(hop = lane-BFS to nearest enemy star; stamp on C-buy; rng draw timing).
PIN campaign_emergency_chain_law_t201 (period table, chain-A illegal-stays-
armed, all four B hard exits, B fire + shields==6 skip, C unsigned-quotient
edges 599/600 x2, mega-illegal->18, D strict-gate edges x5, E first-legal-
absent + file-table flag-bits leg) — 115 tests 0 failed.
HONEST NEGATIVES (OQ-016 stays OPEN, STATUS t201 appended): chain-C row
operand [ctx+7]->[+2]>>16 identity UNVERIFIED; +0x67 buy-path stamp WRITE
site not found by the obj0 writer census; DAT hop-matrix stride-100 (t190)
vs chain-C index-stride tension unresolved. Gap row 4 (demolish sweeps) =
t202. TOOLS NEW: r201_threat_writers.py (capstone-resume census; PITFALL
banked: sequential capstone STOPS at first data gap — blind pass found 36
of 325 sites), r201_threat_census.py (self-check IND/RES/PROS maxima ==
t198 exactly), r201_threat_law_verify.py. Docs: ai-dossier.md S10 NEW +
gap row 3 -> MODELLED; OPEN-QUESTIONS OQ-016 STATUS t201 (insertion pit-
fall: annotation must land at the block's LAST line, not the next row's
header — caught and repaired same session). Gate + ledger checks below.


LANDED t200 (2026-10-29, this session): COS_STAR SELECTOR SEMANTICS — THE
LAST UN-ADJUDICATED SELECTION CLASS MEASURED; OQ-005 RESIDUE SHRUNKS TO A
CITED BOUND. Trigger triage: timeline size 5,721,578,066 == frozen baseline
(mtime 13:22:12.10), dosbox down -> no sitting; tree clean at d88371f.
KEY LAWS [all cited, planets-ui.md S6]: (1) t198's "site 0x2925c" was the
FUNCTION START — the real STAR_SHAPES blit is at 0x298dc inside
FUN_00029788 (coswnd.cpp, span 0x2925c..0x2a493); (2) STAR SELECTION LAW
SEL = 4*[star_record+0x00] + cls where K = star TYPE index (starstat.txt's
13 types mapgen.md S1) and cls = 4-band ladder on v=frndint(f32[star+0xd]+
f32@0x105e): v>=0xdc->0, 1..0xdb->1, -0xdc..0->2, <-0xdc->3; payload =
[wnd+0xab]; x/y = unaligned s16 hi-words at node+3/+5; (3) K CENSUS MEASURED
(scripts/r200_kcensus.py RC=0, 20 saves x 50 stars, pointer law): set
{0,1,2,4,5,6,7,8,9,11,12} subset {0..12} -> SEL reach 0..51 -> the dims-zero
residue k40..k51 (= types 10/11/12 x 4 classes, file-verified the COMPLETE
dims-zero set, offs 0x8f2..0xa1b span 0x1b each) is ADDRESSABLE (draws
nothing: zero-row walk; the blit's -1 @0x5cb2b checks the window shape-
struct, not the record), and k52..k54 are provably UNADDRESSABLE (need
K>=13 > type domain); (4) cosmos site 0x2a223 adjudicated NOT star art:
relation BADGE blit SEL in {9 ALLIANCE, 8 WAR, -1 skip} off the t189
relation-state byte, fixed x=0xe y=3. CORROBORATION: 60.sav guest RAM holds
exactly two '1.10' lib buffers; member 0xfd2934 matches cos_star.shp
header+dir byte-for-byte. HONEST NEGATIVES (row OQ-005 stays OPEN): WHY the
12 slots are empty (vendor defect vs dims-location) stays unmeasured;
[wnd+0xab] itself unmeasurable in-corpus (no COSMOSWnd object in the 20-sav
ring). Docs: planets-ui.md S6 NEW, shp.md S22 fold, OPEN-QUESTIONS OQ-005
STATUS t200. TOOLS: scripts/r200_kcensus.py NEW; scripts/r200_espmap.py NEW
+ fixed (capstone reg-constant 41 != ESP -> use reg_name; cdecl call
preserves ESP; run LO after prologue sub). PITFALLS: functions_full.tsv
sizes are HEX; unquoted heredoc eats $vars in python. Gate 0 + LEDGER AUDIT
OK + LEDGER INDEX OK; open = 005/016/019/021.


LANDED t199 (2026-10-29, this session): REWRITE WIRING OF THE t198
PLANET-UI VIS LAWS + POP-BAND PIN (pure code + docs; the cheapest landing
t198 predicted). Trigger triage: timeline size 5,721,578,066 == frozen
baseline (mtime 13:22:12.10), dosbox down -> no sitting; tree clean at
d3b7ee6. CODE: ui::gaugeSelector (clamp0..20(lround(L^0.75))),
ui::prosSelector (identity clamp) in rewrite/src/ui/layout.{h,cpp};
Campaign::popBands (pure static) + popBandsFor on the +0x4c/+0x42/+0x4a
analogs in campaign.h. LAWFULNESS EXTRA [proved before coding]: .5 ties in
L^0.75 are IMPOSSIBLE (16*L^3 == odd^4, mismatched 2-adic valuations), so
lround == the x87 frndint-nearest the original called — the C++ law is
bit-identical on all inputs; full first-level table banked (0,1,2,4,6,8,10,
13,15,18,21,23,26,30,33,36,39,43,46,49,53; unclamped 21 from L=57 -> the
clamp20 branch is REAL for IND>=57). ARITHMETIC CORRECTION banked:
planets-ui.md S3's "pow(53,0.75)=20.2" is actually 19.64 (t198 conclusion
unaffected; doc amended). PINS: layout_planet_gauge_selector_law_t199
(corpus anchors RES52->19 / IND53->20 / IND77->20-clamped, boundary-exact
both sides at all 21 selectors, monotone 0..300, PROS identity 0..16 + clamp
21->20) and campaign_pop_band_law_t199 (all five edge-class shapes verified
against the verbatim formula — one synthetic expectation was wrong in MY
first draft (used>pop), implementation correct, test fixed; independent band
histograms count1==used/count2==pop-used/count3==cap-pop + used<=pop<=cap
over 300 turns x all planets of seed 2024). 114 tests 0 failed. Rendering
stays blocked on OQ-005 (ui-runtime.md §2 no-vendor-sprites rule) — landing
documented as §2a; selection census ids folded into shp.md S22 (1starmap
k3,k4,k5,k7 per windows.txt:456/477/498/517 re-verified this session;
3cfgnew k0; planind ladder addressed 0..20). OQ-005 row stays OPEN (STATUS
t199 appended — no residue evidence moved, wiring only). WIP:
_wip_t199.md S0-S1. Gate 0 + LEDGER AUDIT OK + LEDGER INDEX OK; open =
005/016/019/021.

LANDED t198 (2026-10-29, this session): PLANET-SCREEN PAINT ROUTINE CENSUS —
THE GAUGE COMPRESSION LAW AND POPULATION BAND LAW MEASURED (user directive
"derive the visualization laws from the binary"). Trigger triage: timeline
size == frozen baseline (no sitting); tree clean at ab28629. ARTIFACT
docs/re/planets-ui.md (hand-authored; economy.md deliberately NOT touched —
gate-regenerated by gizmo_probe.py). KEY LAWS [all cited]: paint body
0x3b96c (planwin.cpp; 12 blit sites; listing work/t198_planwin.asm);
selector switch 0x3cc9f jmp *cs:0x27fe8(,key,4) with the TABLE READ LIVE
(41.sav member image_off 0x3cb98 == [3cca7,3cd3b,3cdcf,3ce39,3cefd] —
jump tables relocate, image bytes are code); gauge cases clamp0..20(
round(pow(LEVEL,0.75))) with the double built as push 0x3fe80000/push 0
(= 0.75, NOT 1.8125 — a caught mid-run misread of the f64 pair), FUN_00078a90
=pow, FUN_00076e08=x87 round-to-nearest; fields IND=+0x44 RES=+0x46
PROS=+0x48 (matches campaign.cpp:768); POP grid SEL(i)=1+[i>=+0x4c]+
[i>=+0x42] over i<+0x4a, 10 per row (planets-ui.md S4). CORPUS CENSUS
[measured 2900 records/20 saves via locator law; DAT_00043508 ptr law
member=ptr+0x88 verified 20/20, 60.sav="Icarus II"]: IND max 77, RES max 52,
PROS max 16; selectors span 0..20 non-uniformly; used<=pop<=cap 2900/2900
-> the three band classes ARE the player's idle/free/empty testimony, now
cited. OQ-005 by-product: planind k0..k12 X-class all inside drawable
selector range (placeholder reading REFUTED); t197 past-span-band question
ANSWERED (no clip override; one complete record per draw); 1starmap k3/k4 +
3cfgnew k0 selected per windows.txt SHAPEITEM lines. HONEST NEGATIVES (row
OQ-005 stays OPEN): slot-library identity of cache globals [0x6fd90/2/4/9c]
(zero direct writers A3/89 05/C7 05 corpus-wide; registration path = live-
capture class), cos_star 0x2925c selector semantics, 44 dims-unknowns.
TOOLS: scripts/r1_t198_blit_callers.py (E8 byte-pass + module attribution:
reproduces t83's 75 sites/53 functions; gwindow/planwin/planet/sssystem/
shipwin map), scripts/r1_t198_site_context.py (context disasm + pool-string
annots). PITFALLS BANKED (_wip_t198.md S0): Ghidra get_function_callers
reports only 15 of 75 callers — byte-pass is authoritative; run_script_inline
is POISONED by three pre-existing broken scripts in ~/ghidra_scripts (whole
build skips); switch tables only readable from save members. Gate 0 +
LEDGER AUDIT OK + LEDGER INDEX OK; open = 005/016/019/021.

LANDED t197 (2026-10-29, this session): SPAN BOUND REMOVED + PYTHON/C++ SHP
LAWS RECORD-EXACT UNIFIED. Trigger triage: timeline size == frozen baseline
(no sitting); tree carried only tools/shp_partialdump (t196 renderer BINARY,
orphaned by t196 — gitignored per tools/shp_pngdump parity, adopted).
(1) VALIDATOR: scripts/r1_shp_unifiedlaw.py gained tag X (canonical slots +
EXACT-H walk + NO [rec,nxt) bound; rowwalk_free; --profiles paint probe;
--no-x escape). X set == EXACTLY the t196 EXACT-H set (29). PAINT-PROFILE
MEASUREMENT CORRECTS t196 S20.2: past-span rows PAINT (planind k0 tail = 40
distinct indices, 1.4% index-0; 3cfgnew 21-92 distinct) and are NOT the
successor record's rows (sims ~0.5 both sides) — the "transparent tail" was
the span-exhausting partial dumper never painting them. Whether widgets SHOW
those bands is the paint-routine question (now t198).
(2) DIMS GATE: Python's per-component `continue` walked degenerate frames
the blit refuses (-1/-2 branches); demoted exactly mouse k5 (W=0,H=46) +
sg64expl k0 (H=0xfffffffb), zero other changes corpus-wide.
(3) REWRITE rewrite/src/formats/shp.{h,cpp}: walkRows bound r.end ->
img.size(), decode() 4096 clamp KEPT, contract comments rewritten; TEST
shp_span_free_t197 pins both sides (planind k0 99-row canonical deterministic
+ bottom band written; 3cfgnew k0-11 decode / k12 rejected EOF; 1starmap k1
+ mouse k6/7 rejected dims; 14intel k8 + 1starmap k3/4/6 decode). 112 tests
0 failed.
(4) NUMBERS PINNED BOTH SIDES [measured]: V196+A1288+X29+FAIL44=1557, libs
clean 187/208, rewrite decode-pass 1513 = 1557-44 EXACTLY (pre-t197 Python
1486/186, C++ 1484/185). NEW GATE STAGE 3c-2 greps the five law lines
(~0.2s). Evidence packet regenerated (r1_t182_pngdump.py + SPAN-FREE set):
44 rendered/44 validated incl. 29 XREC-- full frames; ids.tsv
validator-tagged (73 rows = 29 X + 44 FAIL) + 2 DEGENERATE t197 rows;
index.txt warns past-span bands are desynced bytes not vendor art. Docs:
shp.md S21 (+S18 supersession header), OPEN-QUESTIONS OQ-005 STATUS t197
(row stays OPEN — strict-close: 44 dims-unknown remain, closure class =
player ruling / t198 selection census), BLOCKED.md t68 AMENDED t197.
PITFALLS: enumerate unpack must be (idx,value) (null-result bug,
r1_t197_pastrows2.py); never splice tsv by index math — repair lost rows
explicitly (ids.tsv near-miss this session). Gate 0 + LEDGER AUDIT OK +
LEDGER INDEX OK; open = 005/016/019/021

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
