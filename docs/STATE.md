# STATE — machine-readable working memory for the closeout loop (v2)
# A fresh session must be able to resume from THIS file alone.
# Patch discipline: ONE patch per region, read_file verify after.
# HISTORY (this file was SLIMMED 2026-11-03): every LANDED block t1..t292, the
# full per-iteration narrative, and the pre-slim copy of this file live in
# archive/state-v2-full/2026-11-03/STATE.md (md5 a2faccfb648418045b2647be66364f10);
# v1: archive/ralph-v1/STATE.md. A LANDED block is written once per iteration and
# is working memory only AFTER its task closes — the durable laws were distilled
# into docs/re/*.md at landing time, which is why the archive copy costs nothing.
# USER-FACING asks live in docs/DECISIONS.md (read it; do not answer FOR the user).

phase: P7-closeout
milestone: 6  # keep 6: gate.sh keys build/test/boot stages off milestone >= 3; lowering it silently guts the gate
updated: 2026-11-04T10:40
policy: strict-close  # FINAL-DEFAULT never closes an OQ; only cited measurement does (docs/GOAL.txt)
## LEDGER (statuses mirror docs/OPEN-QUESTIONS.md — that file is the record;
## this is the fast index. RE-DERIVE via scripts/ledger_index_check.py, never
## hand-edit; gate 3t runs both audits every gate.)
ledger:
  closed:
    - "OQ-021 end-ctrl threshold CLOSED 2026-11-03 t292 (live presenter
      witness): comparator V >= floor(2T/3)+1 MEASURED — scratch poke session
      work/r1/t290-poke-a40-20261103-165405 (scripts/r290_poke_session.py
      --mode poke 40, freeze-free): sentinel BPLM 0028A2FB mid-pass stop file
      0x24274, drain 0x243b3/0x243f4/0x24372 V 40->56, evaluator FUN_00024a34
      fired: ring t1087 20/20 sel 0->5 (DAT_00043510 @0x24d9f) + rank
      65535->42 (DAT_0004350c @0x24dab) + end-ctrl.txt text verbatim on screen
      ('Your score is 42%', 'Interstellar Subjugator'); law distilled
      docs/re/score.md S20; rewrite arm campaign.cpp:2157 upgraded t291 to the
      cited law (pins test_control_t291.cpp x4 mutation-verified)."
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
      (0.4% samples). (scenario-template preset source CLOSED t294 — file
      table planitem.txt, income-law t294 block)"
    - "OQ-019 ship design model (hull+gizmo inventory, cost hack, Orbital
      Docks); per-ship combat application = OQ-010 aggregate caveats S2i"

## WHAT IS IN HAND (tools + laws — start here, not from scratch)
Full pre-slim text + all measurement provenance: archive copy above + docs/re/.
- DEBUGGER LIVE: master-built dosbox-x with C_DEBUG+C_HEAVY_DEBUG (BPLM/BPPM/
  RUNWATCH/mcp_server verified in binary; source work/r1/dbx-build/dosbox-x-master,
  autotools env work/r1/localprefix/autotools.env.sh). Operating rules + build
  recipe: docs/re/dosbox-debugger.md. It CLOSED OQ-021 (t290/t292). NEVER
  replaces /usr/bin/dosbox-x; scratch sessions only.
- POINTER LAW (OQ-011 CLOSED): runtime_u32 = P0 + payload_file_offset; P0 = B - H;
  guest linear == physical. Save-ZIP member index for Ghidra address X of
  runtime data = B + 0x82BB0 + X; member byte -> physical = member - 0x88.
  H=136 for dfsg 2025.02.01 (re-derive per build). OFF-BY-H DISCIPLINE (t286b):
  anything found BY A MEMBER SCAN is a member index — convert before BPLM or any
  linear consumer. B via scripts/r1_sav_scan.py, NEVER hard-coded.
- V LAW (OQ-021 CLOSED): V = DAT_000482fb controlled-systems count, producer
  FUN_00024274 replayable via scripts/r284_vreplay.py [dir...]; victory
  comparator V >= floor(2T/3)+1 (FUN_00024a34; docs/re/score.md S18-S20).
- CAPTURE: scripts/r1_savestate.sh + r1_deepcapture.sh + r1_playcap_vnc.sh
  (production session, TL default 172800) + r1_playcap_watch.py (ring writer) +
  r1_game_health.py (self-heal) + r1_t261_drive.py (drive class, t289/t285 laws
  implemented) + r287_title_nav/r287_vncinput (title recovery) + r290_poke_session.py
  (debugger poke skeleton) + r1_wp_session.py (watchpoint sessions).
- TURN COUNTER u16 guest-phys 0x254e10; day == turn (t249b). STAR TABLE stride 96
  name-anchored (battery r1_star_table.py, gate 3s); planet records NAME+0x33 ==
  owner race, star+0x14&0x7f == OR(1<<owner) (t248), star+0x5a = colonized count;
  PLANETALLOC header = screen-open snapshot u16[list+0x8c7] (t249) — ring
  planets_mine counts STARS, header counts PLANETS (t247 law: 102 = 100 sole + 2
  co-owned). Full tables: docs/re/r1-savestate.md + docs/re/selfplay.md.
- RESTORED IMAGE for Ghidra: work/ascend_restored.bin (r1_restore_sites.py);
  ghp5 1,144 functions (work/functions_full.tsv); module attribution
  scripts/attribution_scan.py + gate 3r. Static trust boundary: rel32 edges +
  rewritten-site immediates ONLY; t212/t213 verdict: offline static EXHAUSTED.
- Gate: bash scripts/gate.sh is the single verification command (~2-3 min); R1
  attempts are NEVER gate stages. Ledger: python3 scripts/ledger_audit.py AND
  scripts/ledger_index_check.py must print OK (both in gate 3t).

## NEXT ACTION (exactly one)

NEXT t295 OQ-016 RESIDUE 2 — SETUP-TIME HOME-DRAW LAW VIA DEBUGGER SESSION
(ordering rationale: with t294 closed, the remaining non-user-ask routes split
two ways — the nuke law (OQ-016 r1) and magnetron witness (OQ-019 r3) BOTH now
depend on the UNSOLVED ship-selection choreography that killed t293 (each
needs a device/ability used BY a selected ship), and residue 5 is HELD per
t273; OQ-005 + OQ-019-r2 are USER ASKS (D1/D3, do not rule). The home-draw
route is the ONLY open-row route that needs no ship selection: scenario-init
runs at new-game before any fleet exists, and the debugger toolchain is
PROVEN — the master-built dosbox-x (docs/re/dosbox-debugger.md) closed OQ-021
exactly this way.) Task: on a SCRATCH new-game session (own dir, NO
resume.gam so FUN_00037d80 + the scenario-init loop 0x23a20..0x23d22 run;
scripts/r290_poke_session.py skeleton; HARNESS LAW: background=true
notify=true, 420 s foreground cap kills a full session), BPLM-sentinel the
loop and answer ONE question: WHICH rng draw (stream position + modulus)
picks each race's home star — i.e. the consumer path from CALL 0x7824f to the
home-star store (t270 measured the JOIN DWORD[0x12e1d+race*0x1ee] == star
base NAME-0x1C; the draw law is the gap; t30c proved it is run-local uniform
over candidate stars, 11 distinct sets/11 lineages). CAVEATS: scratch copies
only, never mount game/; production :9 is the corpus (read ring tail only);
NEVER replaces /usr/bin/dosbox-x; kill-by-recorded-PID (BLOCKED runbook); if
the loop is reached but the draw-to-store chain is ambiguous in Ghidra output,
bank the raw register trace and stop (one session, no spiral). Closure = cited
draw law (addresses + live values) -> upgrade rewrite pickHomeStars
(campaign.cpp:301, currently a documented MISMATCH: deterministic max-min BFS
instead of the vendor draw) + pin. If the session dies on harness mechanics
twice, bank the negative and queue the residue back to BLOCKED.

## LANDED t294 (2026-11-04, session 3) — word[+0x16] TEMPLATE SOURCE CLOSED:
FILE TABLE, planitem.txt. Pure-static iteration (zero launches; :9 untouched,
healthy t1086 the whole time). The 11 terrain weight rows at runtime 0x744f4
are LOADED FROM planitem.txt (ASCII text after the '#' line: scalar 50 ->
DS:0x66e4 @0x3802c; 11x4 weights -> 0x744f4 row-major, loader loop
0x3801e..0x38067, sole store @0x3805f; grid B -> 0x7445c; grid C -> 0x744a8)
— NOT EXE constants: 0x744f4 lies past the initialised data segment (BSS) and
the image-wide SIB-aware store census finds exactly ONE writer into the
window. File == banked runtime == live production RAM (58/59/60.sav, 44/44
bytes). The per-byte grid-C split campaign.cpp called "not observed" is now
observed (file + RAM). The INDEX word[+0x16] itself stays the rng%11 draw
@0x23a97 (file supplies contents, draw picks row; retracted-R11 stands).
T54b boundary noted so nobody re-refutes the row from it (T54b = the OTHER,
image-mapped 21-dword preset pair for the special scenario mode). WHY earlier
hunts missed it: values are decimal TEXT — packed-byte signature search is
blind by construction. REWRITE UPGRADED: TerrainTables + loadTerrainTables()
(economy.{h,cpp}), CampaignConfig.terrain consumed by world-gen + growth-wrap
(campaign.cpp), main.cpp injects the loaded file; vendor default = measured
values so stock behaviour + seeded pins + PLAYTHROUGH.md are UNCHANGED.
Pins tests/test_terrain_t294.cpp x5, MUTATION-VERIFIED (revert-to-constants
=> 3 consumption legs fail 96 tests; restore => 175/0). Ledger: OQ-016 stays
open (residues 1,2,4,5), residue 3 CLOSED with citation; income-law.md t294
block; docs/re/_wip_t294.md working notes.

## LANDED t293 (2026-11-04, session 2) — SCRIPTED MOVE-ORDER CAPTURE, BUDGET
SPENT, NEGATIVE (honest). 4 scratch launches on Oct-29 t1086 RESUME.GAM
(Xvfb :96, own ring, kill-by-recorded-PID, production :9 untouched+healthy
t1150 the whole time). PROVEN: title->campaign->FLEET(553,184)->row-1
(200,93)->system-view route is DETERMINISTIC ~75 s (scripts/
r293_move_session.py reusable skeleton). KILLED THE RUN: ship SELECTION never
happened — orbital bright-dot clicks NAVIGATE (~65k px diff), never select;
click3/click destinations then do nothing (green constant 32-34, ring order
bytes never move, owner-0 kinds stay {3,4,5}, never 2). EVENTWIN construction
popup swallowed End-Turn presses 2-3 (OK clicks at windows.txt geometry do
NOTHING — Escape is the law, script fixed). One L2 spurious POSITIVE retracted
(lane-step lane traffic is never a flight; verdict now requires the
order-issued slot itself to move). Observation: slot 8 kind 5->4 + position
snap at t1087 = travel order consumed into in-system on arrival, live
corroboration of static 0x220a8->0x21f58. HARNESS LAW: foreground terminal
caps at 420 s — a full capture session (~9-12 min) MUST run
background=true notify=true (L4 died to exactly this). Ledger UNCHANGED
16/3; OQ-019 residue 1 stays open with the negative banked. Autopsy:
docs/re/_wip_t293.md + ships.md t293 block.

## DRIVE-CLASS LAWS (t285/t289 — apply to EVERY drive row; full text docs/re/driver-selfharm-t285.md)
Title menu detected FROM SCREEN before any click (assert_on_map orange-frac);
2 consecutive no-advance presses = STOP-AND-LOOK (bank + flag); NEVER Escape at
the bare map (exits campaign to title, ring keeps saving, RAM guards blind).
Production resumes via title 'Return to Current Game' (318,333); live state
lives in the RING, not RESUME.GAM. Safety runbook (OOM/two-writer/kill-by-PID/
TL/cadence/mining): docs/BLOCKED.md §R1 runbook — binding.

## STANDING CONTEXT (pairing sessions)
USER GRANT (verbatim 2026-11-02): "Go ahead with everything. Don't worry about
my save games or a VNC grabbing the session - I'm done with the game on this
box, if I want to play more I'll fire up a session on my main PC." Network
fetches authorized for RE work; the Oct-29 campaign on :9 IS the production
corpus (RESUME.GAM md5 5b382afbb78918 = t1086; restore from
work/r1/game/RESUME.GAM.user-oct29 if clobbered); tutorial discarded
(RESUME.GAM.tutorial-nov2 for archaeology); VNC attaches harmless to assume,
keep drive laws anyway (engine, not user). R13 STANDING: never self-grade our
own renders; external vision OK for identification. Never issue player attack
orders; never PROPOSE/DECLARE in diplomacy panels (t244 accident law).
LEDGER STATE: 16 closed / 3 open (OQ-005, OQ-016, OQ-019). OQ-005 awaits the
USER's ruling on work/r1/shp_png/decision-sheet.md (docs/DECISIONS.md D1) — do
NOT rule for them and do NOT burn iterations on it.
DO NOT RE-TROD (measured-dead or keeper): t212/t213 static exhaustion; t255
screen-open; t258 candidicide; t259 sav-pair census; t262 fleet-census trigger;
t265 st4-dwell; t269 threshold census; t272 dfsg-debugger (superseded by the
build); t273 attribution fixes (owner INDEX +0x56, stale-echo deltas — build on
them); t49/t58/t265 flight-mining class (scripted capture only).
LOOP CONTROL: relaunch law MAX_ITERS=12 IDLE_GATE=0 (queue-driven; the
nothing-runnable path exits clean). After a queue drains: author the next queue
OR park NEXT on a WAIT-TRIGGER sentinel (task line FIRST — wake selection reads
field 2 of the first non-blank line; notes never go there). Sentinel-slot law:
task line FIRST under NEXT ACTION. work/ is gitignored — findings in docs/re/.

## HISTORY
Per-iteration LANDED blocks t1..t292: archive/state-v2-full/2026-11-03/STATE.md
(+ wip/ notes). v1: archive/ralph-v1/. Slim commit: see git log 2026-11-03.
