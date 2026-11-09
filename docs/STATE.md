# STATE — machine-readable working memory for the closeout loop (v2)
# A fresh session must be able to resume from THIS file alone.
# Patch discipline: ONE patch per region, read_file verify after. t347
# specifics: the patch tool DROPS the trailing newline of old_string when
# old_string ends with one — never end old_string at a bare newline; for
# multi-line insertions use execute_code's patch() with explicit \n.
# HISTORY (this file was SLIMMED 2026-11-03): every LANDED block t1..t292, the
# full per-iteration narrative, and the pre-slim copy of this file live in
# archive/state-v2-full/2026-11-03/STATE.md (md5 a2faccfb648418045b2647be66364f10);
# v1: archive/ralph-v1/STATE.md. A LANDED block is written once per iteration and
# is working memory only AFTER its task closes — the durable laws were distilled
# into docs/re/*.md at landing time, which is why the archive copy costs nothing.
# USER-FACING asks live in docs/DECISIONS.md (read it; do not answer FOR the user).

phase: P7-closeout
milestone: 6  # keep 6: gate.sh keys build/test/boot stages off milestone >= 3; lowering it silently guts the gate
updated: 2026-11-09T12:10
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
      table planitem.txt, income-law t294 block) (t326 preflight census
      2026-11-07: known-tech mask field LOCATED ds:0x7478e+0x4b*i; Phase
      Bomb tech ALREADY owned by races 0+2; launch-msg post hunt narrowed to
      the fn(0x17c54)/fn(0x16147) walk — income-law.md S-T326.)"
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
  linear consumer. B via scripts/r1_sav_scan.py, NEVER hard-coded. POINTER-VALUE
  LAW (t298, ships.md S26 c.1, BINDING): u32 values STORED in RAM are guest-
  PHYSICAL — read the target at member index value+0x88; scan patterns must be
  (member-0x88), never the member value (t297-B false zero-refuted by this).
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

NEXT t367 per queue row t367 below (D1-RULING APPLICATION — the ruling
ARRIVED 2026-11-09 12:45 via the ruling page; two content-identical
USER blocks at the tail of docs/DECISIONS.md; apply ONCE). Ordering
rationale: it is the only user-unblocked strict-CLOSE available (closes
OQ-005, the oldest open row) and a one-session job; t360 (save parser)
is independent of it and resumes verbatim right after. The full
application checklist is pre-written in docs/re/_wip_t367.md S2
(ledger re-derive, sheet-generator route for index.txt, shp.cpp
signed-bbox dims pin md5 b2d049bbf5b5, the NEW B5-B29 top-part user
testimony handling, DECISIONS status annotate-not-rewrite).

QUEUE (phase 7 — PER-SHIP SIM BUILD, user ruling D2=(b) 2026-11-09: fidelity
to the original; NO permanent toggle — per-ship becomes THE engine once the
pinned-seed suite passes, aggregate demotes to oracle, removed after. One
session each; finish tN -> rewrite NEXT to tN+1 VERBATIM; keep this block
intact except deleting completed rows. Evidence base: docs/re/ships.md,
docs/re/ai-dossier.md (treat as spec), STATE DRIVE-CLASS laws,
docs/re/_wip_d1page.md (signed-bbox dims fix, D1-gated).

t359 PER-SHIP RECORD SPEC DOSSIER — LANDED 2026-11-09 (see LANDED
      t358/t359 block; docs/re/pership-spec.md written, zero code).

t367 D1-RULING APPLICATION (ruling banked 2026-11-09 12:45, DECISIONS.md
      tail; apply ONCE of two identical blocks). Execute the checklist in
      docs/re/_wip_t367.md S2 verbatim: (1) OQ-005 CLOSE strict-close citing
      the USER block VERBATIM + shp.md S25-S27, ledger index RE-DERIVED
      (17/2); (2) index.txt/decision-sheet dispositions via the t347
      generator route (no hand-edit of the sheet body); (3) shp.cpp
      signed-bbox dims read + 4-plane pin (md5 b2d049bbf5b5), -1 blit gate
      untouched; (4) B5-B29 top-part testimony recorded in shp.md (render
      fidelity is NOT a ledger row); (5) audits + gate green, DECISIONS D1
      status annotated APPLIED. NEXT after t367 = t360 VERBATIM.

t360 PER-SHIP SAVE PARSER (read-side). rewrite/src/formats/: ShipRecord
      structs + parser mapping RESUME.GAM ship regions per spec section (6);
      round-trip test: parse banked production frames (work/r1/bank-t1086* /
      ring .sav files — READ ONLY via streaming, OOM law) and assert census
      invariants already measured (62,762-row census, owner/race attribution
      law t273). No behavior change yet; tests only + parse API.

t361 PER-SHIP ENGINE SKELETON: rewrite/src/game/shipsim.{h,cpp} — ship list,
      per-ship dwell countdown, order apply at turn boundary per spec (2).
      Determinism pins first: seeded RNG use matches campaign.cpp law. Unit
      tests for dwell expiry + order transitions (table-driven from spec).

t362 MIXED-FLEET DEPARTURE LAW PARITY: reproduce the vendor piecemeal-
      departure behavior (dwell expiry per ship) from the st4 DWELL law;
      parity test vs banked witnesses; aggregate oracle still passes.

t363 GIZMO INVENTORY + CARRIER/CARGO into shipsim per spec (3)(4); magnetron/
      Phase-Bomb residues get a HOME here (which ship carries what) — do not
      close OQ rows (user-gated), just give the model the fields.

t364 PER-SHIP COMBAT ROUND into shipsim per spec (5) + t292 comparator
      unchanged (aggregate victory law stays; per-ship only redistributes
      losses). Mutation-tested pins like the t290-t292 arms.

t365 ENGINE FLIP: campaign turn loop calls shipsim; aggregate code demoted to
      rewrite/src/game/aggregate_oracle.{h,cpp} used ONLY by tests; full
      pinned-seed suite green; gate green; DECISIONS.md D2 annotated APPLIED;
      OQ-019 residue status updated in OPEN-QUESTIONS (row itself closes only
      on user ruling per t329 packet — annotate 'model exists, awaiting
      user acceptance').

t366 (CONDITIONAL, only if t365 green) SAVE-WRITE SIDE: emit ship records back
      into RESUME.GAM layout; byte-compare vs vendor-written save if one can
      be produced headlessly, else round-trip-through-rewrite tests + honest
      note.

After t366 (or on any hard block): rewrite NEXT to the WAIT-TRIGGER sentinel
shape (see t356 LANDED for the proven script pattern) — do NOT invent new
capture routes against cited-dead laws.


STANDING LAWS FOR EVERY ITERATION HERE (beyond TASK_CONTRACT):
- FIXED LAWS, do NOT re-trip (t319-t323 + t331/t332 amendments BINDING): poster
  pass posts msg 4 only; ds:0x484ac = BIOS int16h button state; msg 4/0xc
  default-handled fn 0x336b4 zero DAT stores; BatModeWnd has no in-session
  activator; no poster of 0x1c01 to slot 61 exists anywhere (8th cited-dead
  leg); broadcast pump dispatch 0x56c74 cold 2x; win+0x6d stride-13 = window-
  ITEM array (t335 retracts t334's state-array reading); state ids = global
  winmgr per-id handle table (winmgr+0x3068/+0x306a); current-state word
  core+0x4228.
- OQ-019 residues = UNREACHABLE-BY-CAPTURE, dispositioned t323/t329/t332: the
  disposition packet is DRAFTED DO-NOT-APPLY (_wip_t329 S4) — rows close on USER
  ruling only. Magnetron scripted-drive idea RETIRED cited-indirect (t329).
- DEBUGGER via scripts/r1_dbg_session.py ONLY (t327): LEGSPEC/expectation
  grammar, preflight gates (FirePat collision, port-busy, Oct-29 md5, game/
  refusal), bank-on-exit BEFORE in-process analyze (t330 ordering fix), run
  under VENV python (system 3.13 has no PIL — t327 INTERPRETER LAW). Never
  /usr/bin/dosbox-x. OFF-BY-H: physical = member - 0x88; RAM values are guest-
  PHYSICAL (t298). First-fire 0x00-init artifact check before believing.
- OOM LAW (timeline ~7 GB now: r1_stream / <=400 KB tail-SEEK / r214_triage;
  never iterate the whole file); TWO-WRITER RING (scratch = own ring; wrapper
  bash holds 0 fds, its python child holds 1 — t215/t340 shape); KILL BY
  RECORDED PID (structured argv; pkill -f self-kills shells); SIGKILL softlocks;
  DISPLAY=:9 injected; TL=172800; NEVER loadstate to resume; bank before restart.
- Sitting check FIRST (tail-seek newest turn; >1086 => r1_t85g_sitting.py before
  anything). Production :9 is the corpus — untouched unless the task IS a drive.
- Ledger 16 closed / 3 open (OQ-005, OQ-016, OQ-019); ledger_audit +
  ledger_index_check green every gate; never hand-edit the index block.
- USER DECISIONS PENDING (docs/DECISIONS.md): D1 .shp ruling (t347 shrinks the
  ask; do NOT rule for them), D2 per-ship sim scope (this is now the ONLY route
  to the nuke law + per-ship residues — EIGHT cited-dead capture legs), D3
  definition of done (t329 rewrote it: loop-closeable-without-user = NONE
  end-to-end). Do not burn iterations re-asking or working around them.
- Do NOT re-trod: t323/t332 route set; t293 click-selection; t49/t58/t265
  flight mining; item-35/36 completion witnesses (t271 zero-witness,
  AI-unreachable); t212/t213 static exhaustion; t326 research leg (races 0+2
  ALREADY own Phase Bomb tech at t1086 — mask 0x05, vacuous).
- Gate ~2-3 min; milestone 6 stays; work/ gitignored (git add -f is the ONLY
  exception, artifacts/ task t343).
- After the queue drains: author next queue or park WAIT-TRIGGER sentinel (task
  line FIRST); relaunch law MAX_ITERS=20 IDLE_GATE=0.


## LANDED t358+t359 — 2026-11-09 (t358 CONDITION NOT MET = honest negative;
## t359 PER-SHIP RECORD SPEC DOSSIER SHIPPED: docs/re/pership-spec.md, the
## build contract for t360-t365, zero new measurement, zero code)

t358 (D1-RULING APPLICATION, CONDITIONAL): condition NEGATIVE —
`grep -c "^USER: D1 mouse" docs/DECISIONS.md` = 0 (exit 1); the only USER:
lines are the 2026-11-09 chat-scribe block (L151-157: D2=(b), "D1 answer to
follow via page submit", D3 deferred); no *ruling*/*reply* files; git porcelain
EMPTY; decision-sheet mtime unchanged 03:40:49.800. Sitting check NEGATIVE
(timeline 8,868,782,651 B, 400 KB tail-seek, 16/16 records turn 1086, newest
42/43/44.sav = ring rotation). Exit ramp taken per the row's own text: honest
negative banked docs/re/_wip_t358.md, queue advanced, no park. NEW HARNESS
FACT (the iteration's only measurement): the d1page ruling server IS live
(pid 43067, 0.0.0.0:8613) but runs the OLD /tmp/d1page/server.py — unpatched
path handler `os.path.join(ROOT, self.path)`; submit leg identical (both
copies REPO=/home/hrethric/projects/ascendancy append the USER block to
docs/DECISIONS.md), so the trigger channel works; relaunch-from-work/r1/d1page
noted for the user, not acted on unilaterally (user's channel).

t359 (PER-SHIP RECORD SPEC DOSSIER, zero code): docs/re/pership-spec.md
written from CITED laws only (ships.md §6/§10/§11/§12/§17/§18/§19 +
S20-S24, combat.md §1/§2/§2b + gizmo tree + resolver-array law, ai-dossier.md
§5/§6/row-16, income-law.md §13.5 cargo chain, selfplay.md t273 attribution/
stale-echo laws, STATE pointer laws OQ-011/t298/t333). Contents: (1) field
table ~45 offsets with per-field law pointer + explicit UNKNOWN gap list;
(2) kind enum {0..5} with the verbatim imm store-site census + 11-row
transition table (T-1 auto-order .. T-11 death; walk law with the 160-units-
per-sugar-cube constants; st5 march body FUN_0004a74c gates; st4 DWELL;
retreat-downgrade 0x220f2; placement 0x21f58 star+(0,-200,0)+rng%200); turn
frame FUN_0003e6e0->FUN_0004a74c + FUN_0004a658 upkeep + FUN_00041260
min-fuel round-robin + descending-power sort; determinism = single LCG
FUN_0007824f, commit mode==1 only; (3) gizmo inventory law (ring 0xab stride
7 x25, cap table 0x6842 1234/1234, phantom-slot off-by-one, mutators,
redesign, design-apply shuffle, upkeep/propulsion nesting); (4) carrier/cargo
(Invasion Module cidx 0x49 first-eligible law, landed-ship-is-planet-slot-0x17,
EVENT-4/8 chain, AI coord picker stays OPEN per BLOCKED OQ-CARGO); (5) combat
round (same-system gate, stored-order volley, no hit roll, clamped
shield->hull layers, death 0x49d2c, owner-race-filtered array + return-fire-
as-separate-run); (6) save/load (array member index B+0x82bb0+0x3a095, count
gate ds:0x43489>>16 cap 0x6b, guest-physical pointer values +0x88 rebase,
ring-corpus streaming constraints, no-window-records law, t366 write-side
shape); (7) ten explicit NON-GOALS (nuke law, AI coord chooser, magnetron
re-hunt, lane-step mapping, SO_ labels, +0x42 semantics, OQ-016 residues,
UI choreography, re-deriving closed rows, early aggregate removal); (8) four
named build gaps (G-a queued-order field home DISPUTED — resolve at t360
against the 0x3ac1c site; G-b +0x90/+0x52 dual-use; G-c phantom origin; G-d
lane-frame transform NOT cited — model lane-local progress only).
Epistemic key in-file: every line carries a docs/re pointer or is marked
INFERRED/DISPUTED; strict-close unaffected — the dossier closes NOTHING.

LEDGER UNCHANGED 16 closed / 3 open (OQ-005/016/019, all user-gated). OQ-019
row got a pointer NOTE only (pership-spec = build contract; closure still per
t329 packet / user acceptance at t365). Hand-authored-file check: no script
references pership-spec (gate regeneration safe). Production :9 HEALTHY
throughout (pid 1555 up 11:54+, watcher 1575, ring 58.sav age 2s, TL expiry
2026-11-11 01:07:10). game/ untouched. ARRIVAL MID-SESSION: the D1 ruling
landed in DECISIONS.md at 12:45:01/12:45:31 (two identical submits from the
ruling page — channel live-validated) AFTER this session's t358 check ran at
~11:52. Per this session's own NEXT note t358 was consumed and the session did
NOT divert; application is queued as row t367 with the checklist pre-written
(docs/re/_wip_t367.md). NEXT = t367 D1-RULING APPLICATION.

## LANDED t356 — 2026-11-09 (WAIT-TRIGGER SENTINEL, EIGHTH PARK: NO TRIGGER,
## HONEST NEGATIVE, ZERO NEW MEASUREMENT)

- Branch (1) sitting check NEGATIVE: 400 KB tail-seek of
  work/r1/playcap/live-timeline.jsonl (8,827,874,725 B, +7,821,330 B vs t355
  baseline = ring rotation), 16 records parsed, turn 1086 on 16/16, newest
  tail records 44.sav/45.sav/46.sav (turn 1086, T=50). r1_t85g_sitting.py NOT
  run (standing law: only on turn > 1086).
- Branch (2) ruling check NEGATIVE pre-launch AND post-poller: DECISIONS.md
  mtime 2026-11-09 03:31:41.300 and work/r1/shp_png/decision-sheet.md mtime
  03:40:49.800 both unchanged from t355 baselines; git status --porcelain
  EMPTY pre-launch; no *ruling*/*reply* files (work/r1/ + repo depth 3);
  grep -c "USER:" = 0 on both the sheet and DECISIONS.md.
- Branch (3) taken: park line appended to BLOCKED.md '## Sentinel park log'.
  Poller sentinel_t356.sh run via terminal(background=true, notify=true)
  (session proc_9913cfae18a0, pid 37541): exit 0 "TIMEOUT:no ruling after
  45min". Waited via process_manage(action='wait', timeout=180) x11; one
  foreground tail --pid 420 s chunk errored with the TOOL's own timeout
  (harmless; the background poller was unaffected) — lesson banked into NEXT:
  skip foreground wait chunks entirely.
- Production :9 HEALTHY: game pid 1555 up 06:54:39, watcher 1575, TL expiry
  2026-11-11 01:07:10, ring 56.sav age 4s (GAME_HEALTH_LIVE.txt).
- Ledger UNCHANGED 16/3 (nine iterations): OQ-005/OQ-016/OQ-019 remain open,
  user-gated; no measurement this iteration by design, so nothing closable
  under strict-close. sentinel_t357.sh pre-staged (copy, same baselines).
- GATE_EXIT=0; ledger audit OK; game/ untouched.

## LANDED t355 — 2026-11-09 (WAIT-TRIGGER SENTINEL, SEVENTH PARK: NO TRIGGER,
## HONEST NEGATIVE, ZERO NEW MEASUREMENT — PLUS TWO HARNESS LAWS BANKED)

Branches, cited: (1) sitting check NEGATIVE — 400 KB tail-seek of
work/r1/playcap/live-timeline.jsonl: 16 records parsed, turn 1086 on 16/16,
newest tail record file=50.sav; size 8,820,053,395 B (mtime 06:19:07) vs the
t354 baseline 8,819,223,860 B — growth is ring rotation, not play.
(2) Ruling check NEGATIVE pre-launch and re-confirmed post-poller:
docs/DECISIONS.md mtime 03:31:41.300 and work/r1/shp_png/decision-sheet.md
mtime 03:40:49.800 both UNCHANGED from the t354 baselines (pre-date commit
964517c 06:15:57); git status --porcelain empty at session start; no
*ruling*/*reply* files (ls grep = 0); grep 'USER:' in DECISIONS.md + sheet =
0 hits. Poller work/r1/sentinel_t355.sh (60 s poll, 45 min cap) ran
06:2x->~07:02 and printed 'TIMEOUT:no ruling after 45min'; post-exit re-check:
sheet mtime still 03:40:49.800, DECISIONS still 03:31:41, pid 1555 alive.
(3) Park line appended to BLOCKED.md '## Sentinel park log'.

HARNESS LAWS BANKED THIS PASS (both now in NEXT): (a) `nohup cmd &` inside
terminal() is REJECTED ("shell-level background wrappers") — launch watchers
with terminal(background=true, notify=true) and track the returned pid;
(b) process_manage(action='wait') clamps timeout to 180 s per call (foreground
tail --pid=$P -f /dev/null chunks cap ~420 s regardless of timeout=). Also:
identify WHICH path a dirty git-status entry names before calling it a user
edit — the lone mid-poll dirty entry was this session's docs/re/_wip_t355.md.

Production :9 HEALTHY: dosbox-x pid 1555 etime 05:12:27 (-time-limit 172800,
TL expiry 2026-11-11 01:07:10), watcher 1575, health readout
work/r1/loop/GAME_HEALTH_LIVE.txt mtime 06:17:40 ('ring 41.sav age 7s').

No row moved strict-close; ledger stays 16/3 (eight iterations; OQ-005/016/
019 all user-gated). +0x0a hunt NOT re-opened (t348(1)-(3) binding); no
research task invented (t178); game/ untouched. NEXT = t356 sentinel verbatim;
work/r1/sentinel_t356.sh pre-staged (BASE_EPOCH unchanged 2026-11-09
03:40:49 — correct while the sheet mtime never moves).

## LANDED t354 — 2026-11-09 (WAIT-TRIGGER SENTINEL, SIXTH PARK: NO TRIGGER,
## HONEST NEGATIVE — FIRST PARK RUN AS A REAL 45-MIN POLLER + PATH AUDIT)
- BRANCH 1 SITTING CHECK NEGATIVE (400 KB tail-SEEK per OOM law, 16 records
  parsed with json, turn field 1086 on 16/16 == corpus floor; timeline
  8,819,223,860 B; tail field files 53/54/55.sav = ring slots, growth =
  rotation only). Production :9 HEALTHY (dosbox-x pid 1555 up 04:22+, TL
  expiry 2026-11-11 01:07:10, watcher 1575, health 'ring 47.sav age 4s' at
  work/r1/loop/GAME_HEALTH_LIVE.txt).
- BRANCH 2 RULING CHECK — first time actually WAITED (45 min live poll via
  work/r1/sentinel_t354.sh, 60 s cycle: sheet mtime vs 03:40:49 baseline,
  git diff vs HEAD, *ruling*/*reply* in git status): TIMEOUT, no trigger;
  post-exit re-confirm: sheet mtime still 03:40:49.800 (t347 generator
  output), git status = own BLOCKED.md edit only. No ruling exists.
- PATH AUDIT (the one new fact): t354 briefly suspected prior sentinels
  watched a phantom docs/decision-sheet.md — REFUTED by re-reading NEXT:
  the assignment has ALWAYS named work/r1/shp_png/decision-sheet.md, which
  is the real file (34,475 B, t347 rebuild). Park lines cite it by bare
  filename, which is what misled t354. Prior scripts t348-t353 untracked and
  gone; trigger fidelity unrecoverable but immaterial — the ask was never
  answered on any path. Full account + lesson (stat watched paths at
  authoring time) in BLOCKED.md park log t354 entry.
- BRANCH 3: park line appended to BLOCKED.md '## Sentinel park log'. No row
  moved strict-close (nothing measured); ledger 16/3 (OQ-005/016/019 all
  user-gated). NEXT=t355 same sentinel, upgraded with the poller shape +
  baselines; work/r1/sentinel_t355.sh pre-staged (copy of t354, same
  baselines — sheet unchanged). GATE_EXIT=0, ledger audit OK, game/ clean.

## LANDED t353 — 2026-11-09 (WAIT-TRIGGER SENTINEL, FIFTH PARK: NO TRIGGER,
## HONEST NEGATIVE, ZERO NEW MEASUREMENT — PLUS THE HEALTH-FILE PATH CORRECTION)
- BRANCH 1 SITTING CHECK NEGATIVE (400 KB tail-SEEK per OOM law, 16 records
  parsed with json, never a full-read): timeline 8,811,378,829 B; turn==day==
  1086 on 16/16 tail records == the corpus floor; newest tail record field
  file=58.sav. On-disk ring confirms rotation, not play: 58.sav 05:20:21,
  59.sav 05:20:31, 60.sav 05:20:41 (10 s cadence). Production :9 HEALTHY:
  dosbox-x pid 1555 elapsed 04:13:36 (-conf work/r1/vnc/session.conf -nogui
  -time-limit 172800, TL expiry 2026-11-11 01:07), watcher pid 1575
  r1_playcap_watch.py --no-exit, health readout 'watcher 1575 / ring 45.sav age
  0s'. r1_t85g_sitting.py correctly NOT run.
- BRANCH 2 NO USER RULING: docs/DECISIONS.md mtime 03:31:41 and
  work/r1/shp_png/decision-sheet.md mtime 03:40:49 BOTH pre-date the t352 commit
  (5af066b, 05:17:00). grep -n -i -E 'USER:|ANSWER:|RULING|RULED|user replied'
  DECISIONS.md = 4 hits, all the author's own ask-text (D1 header L13, 'If
  undecided' L58, status lines L80/L85/L94); the 59 hits in decision-sheet.md are
  the t347 generator's own keep/junk disposition column, not annotations. Post-
  commit find -newermt '2026-11-09 05:17:00' sweep of docs/ + home top level =
  docs/re/{gizmos,economy,modules,fnt,text}.md only (gate regeneration). Per the
  t350 GUARDRAIL the sweep was cross-read against `git status --porcelain` =
  EMPTY — no hand edit exists anywhere in the tree.
- BRANCH 3 TAKEN: t353 park line appended to BLOCKED.md '## Sentinel park log'
  (append, per t349's rule; section already existed at line 87).
- PATH CORRECTION LANDED (small but it bites every future park): the live health
  readout is work/r1/loop/GAME_HEALTH_LIVE.txt. work/r1/GAME_HEALTH_LIVE.txt does
  NOT exist — the t351 and t352 LANDED blocks quoted 'GAME_HEALTH_LIVE.txt'
  without a directory and their checks still held because ps confirmed the pids.
  The sentinel body in STATE.md now carries the full path.
- LEDGER UNCHANGED 16 closed / 3 open (OQ-005 shp keep/junk, OQ-016, OQ-019) —
  all USER-GATED; strict-close forbids closing on a default and no new measurement
  exists without a turn-advancing session (click path still broken: 'window died
  before release'). No row touched, so no OQ status edits.
- DISCIPLINE HELD: +0x0a hunt not re-opened (REFUTED t348(1)-(3)), no click-path
  repair attempted, no invented research task at the sentinel (t178), no second
  capture, game/ untouched, ~8 tool calls.
- GATE_EXIT=0; ledger_audit LEDGER AUDIT OK; ledger_index_check OK.


## LANDED t352 — 2026-11-09 (WAIT-TRIGGER SENTINEL, FOURTH PARK: NO TRIGGER,
## HONEST NEGATIVE, ZERO NEW MEASUREMENT — ALL THREE BRANCHES CITED)
- BRANCH 1 SITTING CHECK NEGATIVE (400 KB tail-SEEK per OOM law, 17 records
  parsed with json, never a full-read): timeline 8,810,407,088 B; turn==day==
  1086 on 17/17 tail records == the corpus floor; newest tail record field
  file=60.sav. Ring saves rotating at the 10 s cadence (53..60.sav mtimes
  05:12:50->05:14:00) — rotation, not play. Production :9 HEALTHY:
  GAME_HEALTH_LIVE 'HEALTHY | game pid 1555; TL expiry 2026-11-11 01:07:10
  (158125 s left); watcher 1575; ring 46.sav age 5s'; ps confirms dosbox-x 1555
  up 04:06:58 and r1_playcap_watch.py 1575 --no-exit. r1_t85g_sitting.py
  correctly NOT run.
- BRANCH 2 NO USER RULING: docs/DECISIONS.md mtime 03:31:41 and
  work/r1/shp_png/decision-sheet.md mtime 03:40:49 BOTH pre-date the t351 commit
  (3d25540, 05:10:33); grep -i -E 'USER:|ANSWER:|RULING|RULED|user replied'
  DECISIONS.md hits only the author's own ask-text (D1 header line 13, status
  lines 80/85/94); decision-sheet.md hits are the t347 generator's own
  disposition/needs-ruling column, not annotations. Post-commit find sweep =
  gate-regenerated docs/re/{gizmos,economy,modules,fnt,text}.md only; per the
  t350 GUARDRAIL read via `git status --porcelain` = EMPTY — no hand edit exists.
- BRANCH 3 TAKEN: t352 park line appended to BLOCKED.md '## Sentinel park log'
  (append, per t349's rule).
- LEDGER UNCHANGED 16 closed / 3 open (OQ-005 shp keep/junk, OQ-016, OQ-019) —
  all USER-GATED; strict-close forbids closing on a default and no new
  measurement exists without a turn-advancing session (click path still broken:
  'window died before release'). No row touched, so no OQ status edits.
- DISCIPLINE HELD: +0x0a hunt not re-opened (REFUTED t348(1)-(3)), no click-path
  repair attempted, no invented research task at the sentinel (t178), no second
  capture, game/ untouched, ~10 tool calls.
- GATE_EXIT=0; ledger_audit LEDGER AUDIT OK; ledger_index_check OK.


## LANDED t351 — 2026-11-09 (WAIT-TRIGGER SENTINEL, THIRD PARK: NO TRIGGER,
## HONEST NEGATIVE, ZERO NEW MEASUREMENT — t350 GUARDRAIL APPLIED, NOT RE-DERIVED)
- BRANCH 1 SITTING CHECK NEGATIVE (400 KB tail-SEEK per OOM law, 16 records
  parsed with json, never a full-read): timeline 8,809,340,543 B; turn==day==1086
  on 16/16 tail records == the corpus floor. Newest ring saves on disk 59.sav
  05:07:10 / 60.sav 05:04:00 (ring rotation at the 10 s cadence, not play).
  Production :9 HEALTHY: GAME_HEALTH_LIVE 'HEALTHY | game pid 1555; TL expiry
  2026-11-11 01:07:10 (158525 s left); watcher 1575; ring 46.sav age 4s'; ps
  confirms dosbox-x 1555 up 04:00:17 and r1_playcap_watch.py 1575 --no-exit.
  r1_t85g_sitting.py correctly NOT run.
- BRANCH 2 NO USER RULING: docs/DECISIONS.md mtime 03:31:41 and
  work/r1/shp_png/decision-sheet.md mtime 03:40:49 BOTH pre-date the t350 commit
  (05:03:50); grep -i 'USER:|ANSWER:|RULING RECEIVED|user replied|RULED'
  DECISIONS.md = 0 hits; decision-sheet 'keep/junk' hits are the generator's own
  disposition column, not annotations. Per the t350 GUARDRAIL the post-commit
  find -newermt '2026-11-09 05:03:50' sweep was read ONLY through
  `git status --porcelain`, which is EMPTY: the sweep's docs/re/{gizmos,economy,
  modules,fnt,text}.md + work/attribution.tsv + loop logs are gate regeneration,
  STATE.md/BLOCKED.md are t350's own writes. No hand edit exists.
- BRANCH 3 TAKEN: t351 park line appended to BLOCKED.md '## Sentinel park log'
  (append, per t349's rule).
- LEDGER UNCHANGED 16 closed / 3 open (OQ-005 shp keep/junk, OQ-016, OQ-019) —
  all USER-GATED; strict-close forbids closing on a default and no new
  measurement exists without a turn-advancing session (click path still broken:
  'window died before release'). No row touched, so no OQ status edits.
- DISCIPLINE HELD: +0x0a hunt not re-opened (REFUTED t348(1)-(3)), no click-path
  repair attempted, no invented research task at the sentinel (t178), no second
  capture, game/ untouched, ~9 tool calls.
- GATE_EXIT=0; ledger_audit LEDGER AUDIT OK; ledger_index_check OK.


## LANDED t350 — 2026-11-09 (WAIT-TRIGGER SENTINEL, SECOND PARK: NO TRIGGER,
## HONEST NEGATIVE, ZERO NEW MEASUREMENT — PLUS ONE NEW HARNESS GUARDRAIL)
- BRANCH 1 SITTING CHECK NEGATIVE (400 KB tail-SEEK, 16 lines parsed with json,
  never a full-read): timeline 8,808,297,699 B; every one of the 16 tail records
  carries turn=1086 / day=1086 == the corpus floor; newest record 54.sav (ring
  saves 57-59.sav on disk stamped 05:00:10/20/30). Growth since t349 = rotation.
  Production :9 HEALTHY: pid 1555 dosbox-x up 03:53:29, TL expiry 2026-11-11
  01:07:10, watcher pid 1575 (r1_playcap_watch.py --no-exit). r1_t85g_sitting.py
  correctly NOT run.
- BRANCH 2 NO USER RULING: docs/DECISIONS.md mtime 03:31:41 and
  work/r1/shp_png/decision-sheet.md mtime 03:40:49 BOTH pre-date the t349 commit
  (04:56:55); grep -i 'USER:' DECISIONS.md = 0 hits; grep -i -E
  'ruling received|ANSWER:|user replied' across docs/ = only the author's own
  in-document Q/A prose (STATE.md:761, REFUTED-ROUTES.md:221, ai-dossier.md:340,
  income-law.md:2258) — no verdict on D1/D2/D3.
- BRANCH 3 TAKEN: t350 park line appended to BLOCKED.md '## Sentinel park log'
  (append, per t349's rule — the section already existed).
- NEW GUARDRAIL (why the find sweep looked alarming and isn't): a post-commit
  find -newermt '2026-11-09 04:56:55' sweep returned 22 files INCLUDING
  docs/re/gizmos.md, economy.md, modules.md, fnt.md, text.md and
  work/attribution.tsv — but `git status --porcelain` is EMPTY, i.e. the gate
  rewrote those files content-identically. So a fresh mtime on docs/re/*.md or
  attribution.tsv proves NOTHING (same class as the t347 decision-sheet pitfall);
  only a dirty tree is an edit. Sentinel body now carries this rule.
- LEDGER UNCHANGED 16 closed / 3 open (OQ-005 shp keep/junk, OQ-016, OQ-019) —
  all three are USER-GATED; strict-close forbids closing them on a default, and
  no new measurement was available without a turn-advancing session (click path
  still broken: 'window died before release'). Gate + both audits green.


## LANDED t349 — 2026-11-09 (WAIT-TRIGGER SENTINEL: ALL THREE BRANCHES CHECKED,
## PARKED, NO TRIGGER — HONEST NEGATIVE, ZERO NEW MEASUREMENT, LOOP STILL PARKS
## AT THE SAME SENTINEL)
- BRANCH 1 SITTING CHECK NEGATIVE (400 KB tail-SEEK per OOM law, 16 lines read,
  never a full-read): newest turn 1086 across the whole tail == corpus floor
  (same as t346/t347/t348). The 8.8 GB timeline GREW since t348's commit but
  only by ring rotation: newest save 51.sav ns-stamp 2026-11-09T04:52:29.856,
  one save/10 s cadence, turn field constant 1086. Production :9 HEALTHY
  (GAME_HEALTH_LIVE.txt: game pid 1555, watcher 1575, TL expiry 2026-11-11
  01:07:10). r1_t85g_sitting.py correctly NOT run (no new sitting to analyse).
- BRANCH 2 NO USER RULING: docs/DECISIONS.md mtime 03:31 (predates the t348
  commit 04:47:07); grep USER:/RULING/RULED/'D1 =' = only the author's own
  example reply-shape at line 4 and the D3 recommendation at 112. A
  post-commit find -newermt sweep of the tree (excluding .git/game/work)
  returned NOTHING — no user note dropped anywhere.
  work/r1/shp_png/decision-sheet.md mtime 03:40 is the t347 generator's own
  rebuild output, not a user annotation (t347 PITFALL: the generator rewrites
  the sheet + index.txt, so a fresh mtime proves nothing).
- BRANCH 3 TAKEN: one dated 'parked, no trigger' line appended to BLOCKED.md
  under a new '## Sentinel park log' section (future parked iterations append
  there, one line each, naming the three checked branches). NEXT rewritten to
  the SAME sentinel verbatim per t348's exit ramp.
- NO LEDGER MOVEMENT — honest negative banked: zero new measurement this
  iteration, so strict-close closes nothing. Ledger 16 closed / 3 open
  (OQ-005, OQ-016, OQ-019 — all three user-gated, none re-opened here).
- DISCIPLINE HELD: no +0x0a re-hunt (REFUTED t348(1)-(3) binding), no click-
  path repair attempted (the t348 xsend break stays a prerequisite, not a task),
  no invented research task at the sentinel (idle is the harness's problem,
  t178), no second capture, game/ untouched, ~12 tool calls.
- GATE_EXIT=0; ledger_audit LEDGER AUDIT OK; ledger_index_check OK; game/
  checksums intact.


## LANDED t348 — 2026-11-09 (PLANET-RECORD +0x0a: OFFLINE FRAMINGS REFUTED,
## LOAD-TIME STAMP WITNESSED, WRITER SITE STAYS UNNAMED — HONEST NEGATIVE,
## EXIT RAMP TAKEN, LOOP PARKS AT THE WAIT-TRIGGER SENTINEL)
- SITTING CHECK first (tail-seek): newest turn 1086 (56/58.sav 03:46),
  negative — same as t346/t347 landings. Production :9 healthy.
- OFFLINE CENSUS (scripts/r348_planet0a_census.py, 48 saves / 7401 rec-samples,
  exit 0): 207 distinct values; V=0 n=2385; bands ~17.07k-17.7k / ~49.9k-50.44k
  differ run-to-run in COUNT (39-91 hi), not just value. HYPOTHESIS BATTERY ALL
  DEAD: low16(+0x10 phys), low16(arr member), (arr-base)&0xffff, data-seg
  offset(p10/rec), star*40 (36/7401 coincidence), bit15 — REFUTED-ROUTES
  t348(2). TARGET-SHAPE: DS+V hits the 'data\\smraceNN.shp' BSS pool ONLY for
  owner 0 (owner1 = string MINUS 7; low band lands MID-AIL_*-string) — the
  shp-name-pointer story is REFUTED, t348(1).
- STATIC bounded pass (one, as budgeted): the only +0xa traffic near planet-
  offset anchors (0x32099/0x320af) is a STRIDE-27 array (t249 planet-object),
  not our stride-123 record. No static writer named (predicted: heap base).
- LIVE LAUNCH 1/2 (r1_wp_session.py lin:0x26D061 = rec0 linear 0x26d057+0xa,
  --expect-base 1bf4d8 --break-early; run work/r1/wp-lin-0x26D061-20261109-
  042523 rc=1): FIRED at boot 'Memory breakpoint : 0000:26D061 - 00 -> 06',
  eip=22d85c. DECODED via the pty code panel ('0160:0022D82E 8B502C mov
  edx,[eax+002C]'; linear=file+P0): fire site FILE 0x6e40c = 'mov edx,
  [eax+0x2c]' inside the generic iterator-reset fn 0x6e3d0 — a READER (law 7),
  NOT the writer. Phase clicks all logged 'window died before release', turn
  stuck 1086 => phase negatives are UNATTRIBUTABLE, launch 2 correctly NOT
  spent against a broken click path.
- THE MEASUREMENT THAT LANDED (post-run save census, all 20 saves + ring-final
  of the wp run): rec0 +0x0a = 17414 CONSTANT while IDLE (its low byte 0x06 ==
  the fired value; 17414 == owner 0's per-race constant in the SAME session).
  Cross-run table (17 runs): per-race constants are run-RANDOM (rec0 V in {0,
  49917, 49996, 50213, 17169, 17414}). Reconciles the self-play within-run
  monotone churn: churn is TURN PROCESSING, not idle repaint (REFUTED t348(3)).
  LAW BANKED: +0x0a = load-stamped once per record with the owner-race's
  run-random runtime constant; turn-rewritten; no income/pop consumer; file
  blob carries previous-session leftovers verbatim (t53). income-law.md +
  r1-savestate.md field lines updated; _wip_t348.md S0-S5 full account.
- LEDGER: NO ROW MOVED (strict-close; writer unnamed, meaning unnamed). The
  field is OQ-003-CLASS but OQ-003 CLOSED t181 on its own question; checked
  OQ-016 — no income link found, row untouched. 16/3 unchanged (OQ-005/016/019
  all USER-gated). Harness note banked: r1_wp_session.py writes core=normal
  under [dosbox] = INERT (t304 law); fix conf shape before any future watch.
- GATE_EXIT=0, ledger_audit + ledger_index_check OK, game/ untouched.

## LANDED t347 — 2026-11-09 (DECISION-SHEET REBUILD POST-SLIM: GENERATOR
## VERIFIED BYTE-IDENTICAL, SHRUNK ASK NOW ASSERTED 40/1/3, index.txt CLOBBER
## STRUCTURALLY REPAIRED; D1 REWRITTEN; NO LEDGER MOVEMENT, HONEST NEGATIVE)
- VERIFY HALF OF THE ROW: all three inputs present
  (scripts/r1_t278_decision_sheet.py 340 L, index_t278pristine.txt 97 L / 44
  RESIDUE rows, ids.tsv 88 L). Generator ran under venv python EXIT=0 and
  reproduced decision-sheet.md BYTE-IDENTICAL (md5
  54f07195806cd8cfe6b30c0d2db37ce9 == pre-run copy /tmp/ds_pre_t347.md) — so
  the sheet never depended on an archived _wip file; NOTHING needed
  repointing. Its only file reads are the two banked inputs (open() grep); all
  user quotes + citations are IN the script.
- SHRUNK ASK IS NOW MACHINE-ASSERTED, not prose-asserted: new disposition()
  law table gives every C-row a cited CLASS+reason (sources shp.md S25 t328
  feasibility census, S26 t330 live blit witness run
  dbg-t330b-20261107-080216, S27 t344 selector law run
  dbg-t344d-20261108-161132, + the t323 combat-unreachable amendment);
  unmapped census rows raise SystemExit. MEASURED SPLIT 40 NO-ASK + 1
  JUNK-CERTAIN (3cfgnew k12 vendor EOF truncation) + 3 ADJUDICABLE (mouse
  k5/k6/k7) = 44, i.e. 41 rows leave the ask. THE ASSERTION EARNED ITS KEEP:
  the author's hand-count of 38 failed the first run (sg50expl k9 + sg64expl k0
  are NO-ASK/unreachable, not a separate class) — headline numbers can no
  longer drift silently.
- STALE PREMISES PURGED from the sheet (superseded by cited measurement, not
  re-litigated): mouse lib "dims words invalid ... only paint-capture could
  resolve"; k5 note "W=0 H=46" (that was ONE HALF of a signed bbox pair, S27);
  "THE HONEST DIMS-UNKNOWN REMAINDER is 16 records".
- TOOL LAND: the generator now writes index.txt ITSELF (pointer header + the
  identical sheet bytes), so r1_t182_pngdump.py clobbering it is recoverable by
  re-running the generator instead of by discipline. Sheet is 176 L.
- DECISIONS.md D1 REWRITTEN to the t347 shape (3 rows + one batch word +
  optional B-ID confirm), D3's OQ-005 line got the t344/t347 addendum, and the
  10status/2savegam/4loadgam triad (A6-A8, user: "possibly junk data") was
  promoted from "restatement only" to a LIVE keep/junk call — a real ask we had
  been not-asking. Hand-authored docs confirmed safe: no script opens
  DECISIONS.md or shp.md for writing (grep).
- LEDGER: NO row moved, honest negative banked in the OQ-005 row — t347
  produced NO new measurement (it re-expressed already-cited measurement and
  repaired tooling), R13 bars self-grading, and the blocker is USER TIME not
  our coverage. The k5/k6/k7 pixel-capture route stays OPEN and is NOT refuted.
  16 closed / 3 open unchanged. GATE_EXIT=0, LEDGER AUDIT OK, LEDGER INDEX OK.
  game/ read-only.
- NEXT = t348 PLANET-RECORD +0x0a WRITER WITNESS, HARD BUDGET + EXIT RAMP
  (last non-user candidate; t349 = sentinel/park).

## LANDED t346 — 2026-11-09 (INPUT-PUMP WRITER WITNESSED — fn 0x2a5f0 IS THE
## LIVE WRITER OF WORD ds:0x484c4/0x484c6; t288 honest-negative (1) CLOSED;
## sitting check negative t1086; candidate (a) verified-refuted t248).
PROVED: (1) STATIC census (work/r331_disasm.txt literal-immediate scan)
names every writer of the pending-input pair: fn 0x2a5f0 INT16h drain
(char 0x2a70e, msg 0x2a72a — msg published LAST, so consumers never see a
half pair), fn 0x2a838 DOSBox-record demux type-3 arm (0x2a911/0x2a91d),
fn 0x54650 pump clear (0x54928, gated msg==0x19). (2) LIVE witness, ONE
launch (run work/r1/dbg-t346-20261109-024828 rc=0 attempt 1, NEW "keys"
phase in scripts/r1_dbg_session.py — t311 shape, keys 'c','1'): census
{w484c4_2a91d:0, w484c4_2a72a:2, c484c4_54928:0, btn_hdlr:2}, banked stop
keys#0 EIP file 0x2a72a EAX=0x2e EDX=0x63 = THE WRITER MID-STORE with the
injected pair in registers; fn 0x2a838 arm DEAD for injected keys
(REFUTED-ROUTES t346(1)). post-rearm btn_hdlr ebx=0x63 ecx=0x2e win
NEXTTURN (ret0 0x56c77/0x3177d) — t311 bare-map focus law reproduced free.
(3) t288's stuck pair (msg=1,char=0x1b) is EXACTLY fn 0x2a5f0's ESC-drain
output shape (scan 1); msg==1 routes to fn 0x54d18 hotkey dispatcher
(0x5494a/0x54951) before any button dispatch — the softlock HALT CAUSE
stays UNNAMED (honest negative; writer-EIP gap closed only). INSTRUMENT:
ctl_census MATCH=False on data-seg-immediate legs is by construction
(REFUTED t346(2)); whole-log census authoritative. Tool delta:
r299_leg_session.py LEGS +3 (payload-verified store bytes),
r1_dbg_session.py LEGSPEC + "keys" phase + --keys CLI (preflight rc=0).
Ledger: NO OQ row touched (t288 negative lives in selfplay.md, not the
ledger) — 16 closed/3 open unchanged, strict-close intact. Launches spent
2/3 (attempt 2 killed at campaign entry — attempt 1 already decisive).
GATE_EXIT=0, both audits OK, game/ read-only. NEXT=t347 VERBATIM.

## LANDED t345 — 2026-11-09 (SLOT MARKER BYTE UNION LAW, OQ-016 residue-(4)
follow-through; ZERO captures, offline corpus + disasm; sitting check negative
t1086. PROVED: (1) runtime item-table FLAGS word bit8 set EXACTLY {18,19,26,27}
/ bit4 EXACTLY {17,28,29,30} — 48/48 saves stable (scripts/r345_gate_word_census
.py exit 0); static 0x73e40 bytes code-shaped garbage, t74 law firsthand.
(2) Writer census EXHAUSTIVE over both addressing forms (*1+0x3 = 1 site,
*4+0x2 = 27 sites, all classified): word2 = (MARKER<<8)|ACTIVE-bit; completion
0x3928b writes constants 15/35 (item 27) gated gate-bit8 AND cell >= +0x18 —
first time shown the cell term is what explains the t325 item-18-vs-26 census;
SETTER fn 0x39760 (pair of getter 0x396cc) writes the SHIP-RECORD INDEX
(orbital-only assert 0x40f; callers 0x3987c ship-assign, 0x3b860, 0x3f87b) —
the S4 "contradiction" (constants can't feed a 25-site resolver) dissolves:
two writer populations by slot class, a UNION FIELD. (3) Getter 0x396cc's 25
call sites are ALL item-23-gated -> shield constants 15/35 functionally INERT;
t340's one-time-marker reading HOLDS for shields. (4) CORPUS CIRCLE
(scripts/r345_marker_census.py exit 0 + inline pass): 17 distinct byte3 values
on item-23 rows; 360/360 ACTIVE ship rows resolve rec owner == planet owner,
+0x59 == planet record (guest-phys +0x88 law), +0x58 == 3; shield contrast
item18 1800 rows byte3 always 0, item26 2932x15+108x0, item27 180x35+240x0,
zero dangling (4-run-lineage correlation honestly noted). DISPOSITION: law
closed measurement-wise (income-law.md S-T345); NO rewrite code delta — the
rewrite carries no per-ship build-slot state to hold the marker (OQ-019
boundary); shieldThreatFor/orbitalThreatFor item sets upgraded from file-file
citation to RUNTIME-verified (code unchanged). OQ-016 row STAYS OPEN per D3
strict-close. NEXT=t346 VERBATIM. game/ untouched.

## LANDED t344 — 2026-11-08 (MOUSE-CURSOR DRAW-WITNESS, OQ-005: SELECTOR LAW
## FOUND STATICALLY + LIVE CORNER WITNESS TL/TR BYTE-EXACT; t328 DIMS DISPUTE
## DISSOLVES (SIGNED-BBOX PAIR, 12/12 FILE-MEASURED); k5/k6/k7 PIXELS
## CAPTURE-LIMITED; ROW STAYS OPEN STRICT-CLOSE)
- SELECTOR FOUND (zero capture): 'DATA\MOUSE.SHP' = payload 0x84314; under
  the pool-relative-immediate law the imm is 0x1764 and the image holds
  EXACTLY ONE code site: fn 0x309d4 @0x309f9 (lazy-open iff [obj+0x733]==0 &&
  ds:0x484cc!=0; gsystem.cpp assert tail). t328's zero-u32-ref negative
  scanned 0x84314 — scan-value artifact, not a fact (REFUTED-ROUTES t344(1);
  scripts/r344_mouse_refs.py).
- GEOMETRY LAW (static): cursor chain fn 0x1be10/fn 0x54650 -> fn 0x5a1e4 ->
  fn 0x30a60 -> fn 0x64ea9(lib,id); W/H = signed-bbox differences
  (fn 0x61058 0x61072..0x61083), hotspot = (+8,+c) (fn 0x6108c), memo quad
  ds:0xa208c/74/90/cc. FILE MEASURED: all 12 mouse.shp records agree
  bbox-diff == (u16@+2+1, u16@+0+1) — the two slots serve DIFFERENT consumers
  (gate reads pair, geometry reads bbox) and neither is "the" dims slot.
  k5=(-77,0,0,46) k6=(0,-46,77,0) k7=(-77,-46,0,0): k4..k7 = ONE 78x47 glyph
  at four corner anchors; t328's "zero-component" was one half of a signed
  pair (REFUTED-ROUTES t344(2)).
- LIVE WITNESS (run work/r1/dbg-t344d-20261108-161132, attempt 1 rc=0, leg
  cur_req = file 0x30AA7 = call 0x64ea9 inside fn 0x30a60): root click (0,0)
  -> request id 4 lib 0x2EC03C rec 0x48b (= k4 TOC offset byte-exact); root
  (799,0) -> id 5 rec 0xc99 (= k5); releases -> id 0 rec 0x68 (k0). TL/TR
  corner law CONFIRMED LIVE. Exact edge required (launch-1 root 788 = guest
  ~630 fired nothing; DOSBox 1.25 scale). ids 6/7 unwitnessed (t285
  title-eject stopped the sweep; mechanism identical). Zero blit_deref at
  k5/k6/k7 offsets => corner glyph NOT drawn through FUN_0005caac in
  captured play: pixel draw-content = CAPTURE-LIMITED (honest negative in
  the row; t344 assignment (b) pixel-compare could not run — no drawn
  corner frames exist in the witness window).
- TOOL LANDS: scripts/r1_dbg_session.py teardown removes the Xvfb
  /tmp/.X<d>-lock+socket iff owner==killed pid (stale lock cost run t344c
  both attempts); scripts/r344_cursor_session.py composes r330 BlitSess with
  cur_req/mode_upd banking + whole-log PTY census (bank-on-exit before
  analyze, t330 ordering law honored). mode_upd attribution anomaly noted
  honestly: 2 fires in pty log, leg=None at bank time (re-arm-gap class).
- Ledger: OQ-005 C27-C29 re-classified 'valid dims (78x47), SELECTOR KNOWN
  (corner modes, TL/TR live-witnessed), drawn-frame pixels capture-limited';
  STAYS OPEN strict-close (pixel MATCH bar never landed; generalization
  beyond mouse still needs per-library witnesses; D1 ask unchanged in
  substance). 16 closed / 3 open unchanged. GATE_EXIT=0, LEDGER AUDIT OK,
  LEDGER INDEX OK. game/ read-only.
- NEXT = t345 SHIELD-BYTE LAW -> REWRITE CODE SITE VERBATIM (queue row 1).

## LANDED t343 — 2026-11-08 (PORTABILITY AUDIT + ARTIFACT CLOSURE, DECISION-FREE,
## THREE CLEAN CLONES MEASURED; NO LEDGER ROW CLOSES BY DESIGN)
Sitting check FIRST: newest tail-seek turn 1086 == corpus (no new sitting; the
file grew only from the production session's own writes). No launch taken this
iteration; game/ read-only; production :9 never signalled.
(1) ARTIFACTS TRACKED: artifacts/{ascend_restored.bin,functions_full.tsv,
README.md} committed as a COPY out of gitignored work/ (cleaner than the
assignment's `git add -f` route; supersession stated in the README). Validation
scripts/r343_artifact_validate.py exit 0, command+output in the README:
V1 rebuild from work/r1/r1sav-20261011-213606 slot 46.sav (H=0x88 B=0x1bf4d8
P0=0x1bf450) is CODE-WINDOW BYTE-IDENTICAL to the committed image; 9 differing
bytes in 3 u32-groups, all data-region (0x8bed0/0x8bedc/0x8bee4) = capture-
dependent fixup-class drift, documented as expected, NOT papered over.
V2 Watcom start density on the RESTORED-SITES population 575/1039 = 55.3% vs
15.6% control (3.55x; banked pairing figure 60%/15% re-confirmed on the
committed bytes). PITFALL BANKED: the naive aligned-self-pointer population
measures 21.6% and CANNOT pass the 2x bar — population definition is part of
the law (first V2 attempt failed on exactly this).
V3 tsv: header exact, 1,144 rows hex-parse, spans in range, 904 overlaps known.
(2) CLEAN-CLONE GATE TEST, tool scripts/r343_clone_gate.sh (file:// clone, zero
network, verbatim output to work/r343/clone-runN-gate.out):
RUN1 (pre-fix): exit 0 BUT three stages self-skipped on the first run — the
build lived at the bottom (stage '4-5'), so 4e/4c/4d saw no binary, and their
single else-note blamed xvfb-run for a missing binary (MISATTRIBUTED SKIP,
confirms the pairing measurement).
FIX LANDED (gate.sh): build/test/boot block hoisted to "3-pre" right after
docs integrity; skip notes split by cause (binary absent vs toolchain absent)
in 4e/4c/4d. No stage weakened: every check that runs still asserts the same
grammar. RUN2 (working-tree gate on clone): exit 0, binary built early, the
run1-vs-run2 skip-note diff is EXACTLY the three lines disappearing (xsend
click line present = real-input check ran). RUN3 (committed tree, SINGLE run,
14:53:36->14:54:20 = 44 s wall INCLUDING the from-scratch cmake+build the gate
itself performed): exit 0; everything runnable executed; remaining skips are
the capture stages (3q pointer-law, 3s star-table) + venv loader-model probes,
notes naming the true cause.
(3) PORTABILITY UPGRADE MEASURED: game/ascend.exe[0x2a50:0x2a50+0x8cc83] ==
work/ascend_payload.bin EXACT (576,643 B) — the payload is a byte-exact slice
of the TRACKED original. attribution_scan.py now derives it when the work copy
is absent, prefers artifacts/ascend_restored.bin, and mkdir -p's work/ for its
tsv; gate 3r guard widened to the tracked path. Net effect: a fresh clone with
the game dir RUNS the attribution stage (was: skip) — run3 confirms.
(4) docs/re/retractions.md: 24 entries (WHAT SAID / BY WHOM / SUPERSEDED BY /
CURRENT LAW), every pair verified against the citing doc this session; covers
the assignment's known family (t31/t32 pop-cap, t47 labels, t187 4.67, t212
alias, t334->t335, t326b->t331, t246 0x131b4, t196->t328 mouse) plus pairs
mined live (t247 +0x5a, t249 occupied, t251 bank-blind, t266 ring collision,
t267 kill SOP, t283 debugger revival, t342 COST +8 + 33/34/35 coverage,
t162 manifest, 05j rv-B mislabel). combat.md ~L467 still prints the narrow
ah>=4 form — flagged in entry #15 rather than silently edited.
(5) docs/re/portability.md: reading order formats -> tables -> worldgen ->
economy -> combat -> dip -> victory -> AI, each step law-file + gate stage /
pin TEST name (verified against gate.sh stage list + rewrite/tests), plus the
NOT-portably-known section (open rows, capture-limited class, box-limited
gates, and the rule a skip note must name the ACTUAL missing prerequisite).
LEDGER: 16 closed / 3 open UNCHANGED (audit task; no row touched, no strict-
close attempted — nothing in this iteration was a law measurement on a row).
Working notes docs/re/_wip_t343.md. Gate green incl both ledger audits.
NEXT = t344 MOUSE-CURSOR DRAW-WITNESS VERBATIM (queue row 1).

## LANDED t342 — 2026-11-08 (OQ-016 RESIDUE-(5) "HUMAN BUILD-ORDER
## MINUTIAE" DISPOSITIONED PLAYER-INPUT CLASS WITH CITED MEASUREMENT, ZERO
## CAPTURE: 4891 PENDING OWNER-0 QUEUE ROWS CENSUSED, VENDOR SIGNATURE 0
## HITS vs AI POSITIVE CONTROL 3/3; THE OQ-016 RESIDUE LIST IS EXHAUSTED)
Offline iteration over existing saves (production work/r1/playcap t1086 +
bank-t1254 t1254 + t340 ring-final t1086..1093; playcap/caps EMPTY — honest
negative). Sitting check NEGATIVE (tail-seek, newest live-timeline turn
1086 == corpus); production :9 never signalled; game/ read-only.
Instrument scripts/r342_queue_census.py (exit 0; turn-sorted adjacent-save
pairing + AI positive control; pinned output
work/r342_census_pinned.out; FULL-CORPUS --all pass
work/r342_census_all.out: 3324 saves, 144,302 owner-0 pending rows,
[p+0x5a]==0 144302/144302, netplay==0 3324/3324, owner-0
complete-then-requeue 0 vs AI control 180 re-queues, 0 counterexamples).
PROVED (income-law.md S-T342):
1. EXCLUSION: netplay ds:0x10ba4==0 and local ds:0x7458e==0 in 60/60 saves;
   [p+0x5a]==0 in 4891/4891 pending owner-0 rows (and 5240/5240 owner-0 rows
   overall) — the t341 verbatim gate 0x3eabf..0x3eacd statically excludes
   the vendor selector FUN_0003f130 from every observed human row.
2. SIGNATURE ABSENT/PRESENT: owner-0 transitions PROGRESS 247, DRAIN 8,
   complete-then-requeue 0; AI control on the SAME instrument fires the
   boundary re-queue 3/3 (Gridsor I item26->item0 t1090->1091, Arcturus I
   item8->item20, Sarsaparilla III item20->item8). All 8 human DRAINs are
   completions (slot word2 bit0 SET next save; item 35 -> word2 0x3 =
   Automation |=2 verbatim) that drain to EMPTY and stay empty — t341's
   13/13 law holds corpus-wide, 0 counterexamples. NO residue-(7).
3. EVERY anomaly class collapses to a banked law: cell 0xffff == flag-bit1
   items {31,32,33,34,37} (t341 writer law); cell>=cells == ORBIT slots
   (cap=cells+10, t340); acc>COST == governor 33/34/35 accrual (t45;
   Mukwonago I 45->60->75 at IND 15) or the bank-t1254 frozen ship rows
   (item 23 COST = ship-design value, t27 S8; all 20 saves turn t1254).
   CORRECTION LANDED: the COST word is DS+0x73E40+8+0x28*idx (flags +6,
   cost +8) — the t342 STATE assignment's "cost word +2" was WRONG (t340's
   own income-law text had it right at S8/L448).
4. UI WRITER LEGS NAMED VERBATIM: fn 0x3aa0a (window ds:0x43508) -> 0x38840
   at 0x3b0d1 (colonize), 0x3d887 (ship design), 0x3b349/0x3b411/0x3b482/
   0x3c9fc/0x3ca44/0x3daa9 (queue-edit arms); fn 0x3a174 -> 0x3a3f0/0x3a455
   (demolish/rebuild); 0x3ae99 (via 0x38818) is nougat-gated (ds:0x10ba0).
   Governor values = mode-3 cell-SELECT writes (+0x54 only; t45).
5. CORPUS CORRECTION to t45: "trigger values 33/34/35 NEVER occur (0/2810)"
   was corpus-limited (Oct-5/6 early-turn captures 0/1838) — production
   t1086 has 320 owner-0 values {34:180, 35:140}. Branch closure stands on
   the static pin, not on corpus vacuity (income-law.md S14 correction).
LEDGER: OQ-016 row STAYS OPEN (strict-close): residue-(5) dispositioned
player-input class = no missing vendor law, nothing to change in code; the
residue list is EXHAUSTED ((1) cited-dead x8 = user ruling, (2)(3)(4)
CLOSED, (6) CLOSED) — remaining movement is USER adjudication (D2/D3).
Ledger count 16/3 unchanged. buildPhase comment upgraded to cite the corpus
witness (rewrite/src/game/campaign.cpp, comment-only, no code delta).
REFUTED-ROUTES t342 amendments 1-2 appended (do not re-census the human
queue; governor accrual is not a cost-1 build). GATE 0, both audits OK.
NEXT = t343 PORTABILITY AUDIT + ARTIFACT CLOSURE VERBATIM.

## LANDED t341 — 2026-11-08 (CANDIDATE OQ-016 RESIDUE-(6) RESOLVED WITH
## CITED MEASUREMENT, ZERO CAPTURE: THE "FACTORY AUTO-RESERVE ON THE HUMAN
## PLANET" WAS AN OWNER MISATTRIBUTION — GRIDSOR I IS OWNER-1 (AI); THE
## RE-QUEUE IS THE BANKED AI SELECTOR; LAW BANKED: THE VENDOR NEVER
## AUTO-QUEUES FOR THE HUMAN PLAYER)
Offline iteration over the t340 ground-truth ring-final + restored-image
disasm (work/r331_disasm.txt). Sitting check NEGATIVE (tail-seek, newest
live-timeline turn 1086 == corpus); production :9 never signalled; game/
read-only. PROVED: (1) OWNER CORRECTION — Gridsor I planet-record owner byte
([base+0x57]==NAME+0x33, t248 law) = 1 in ALL 20 ring saves; named-pool
census {0:80,1:11,2:13,255:41} (owner-0 80 == t248 PROOF 2 t1086 EXACT);
ds:0x7458e=0, ds:0x10ba4=0. t340 LANDED clause (5) VOID as stated.
(2) TURN-TAIL ORDER verbatim (fn 0x24f24): loop A 0x2503c calls
FUN_00038f68 per planet BEFORE loop B 0x25060/0x25083 calls FUN_0003e6e0
per race row; local row after loop at 0x250a5 — completion-reset then AI
re-queue inside one boundary, exactly t340's observation. (3) LOCAL-RACE
GATE verbatim 0x3eabf..0x3eacd: selector FUN_0003f130 (sole caller 0x3eade,
queue-empty-only 0x3ead6) runs on LOCAL-race planets iff [p+0x5a]!=0; ALL
104 owned planets read [p+0x5a]=0 MEASURED. MEASURED LAW: 13 owner-0
empty-queue planets at t1086 stayed empty at t1093 (13/13, 7 turns) while
AI empires re-queued — player build order is UI-driven; rewrite buildPhase
comment upgraded to cite the witness (campaign.cpp, no code delta).
(4) WRITER CENSUS CLOSED (scripts/r341_queue_writers.py exit 0,
work/r341_queue_writers.out; scripts/r341_writer_paths.py exit 0): sole
in-image queue-pair writer fn 0x38840 0x38af5..0x38b26 reached via
0x38818->0x3875c->0x38718->0x38753 (17 direct callers; UI leg fn 0x3aa0a
0x3ae99/0x3b0d1/0x3d887; selector legs 0x3f1f6/0x3f2ff/0x3f403/0x3f4c7);
resets 0x37f8d/0x3a153/0x39290; 0x3a596 block = record copy ctor. Slot43
byte1 ff->0x00 == writer byte1:=item(0) verbatim. (5) PICK CONSISTENCY:
item 0 gate flag 0x0 COST 30, Gridsor I IND=6 (ratio 5 < 70), item 0 ABSENT
from the 76-slot array -> absent-first-pass table order (t28 0x3f6a7 law)
picks Factory DETERMINISTICALLY; cell 43 = rng legal-cell picker. AI
empty-queue non-fires (4 planets, all pop==cap IND 6-7) consistent with the
t28 over-cap path — honest control, closure does not rest on it.
(6) EVENT-15 (completion-tail producer 0x3939b) consumer arm {0,1,2,15} =
EVENTWIN refresh ONLY (banked aicode.md S7.1) — cannot queue builds.
HONEST NEGATIVES: star-bitmask corroboration ATTEMPTED via static base
0x13bc5 = garbage on heap-moved saves (not claimed); per-planet AI pick
adjudication stays residue-(5) minutiae. LEDGER: candidate residue-(6)
CLOSED as non-phenomenon with cited measurement; OQ-016 ROW STAYS OPEN
(residues 1, 5); count 16/3 unchanged. Files: docs/re/_wip_t341.md S0-S5.5,
income-law.md S-T341 (hand-authored, no regenerator — verified),
OPEN-QUESTIONS residue-(6) rewrite, campaign.cpp buildPhase comment,
REFUTED-ROUTES t341 amendment (3 clauses). Tools scripts/r341_dis.py +
r341_queue_writers.py + r341_writer_paths.py exit 0. GATE 0, ledger + index
audits OK. NEXT=t342 residue-(5) corpus census VERBATIM


## LANDED t340 — 2026-11-08 (OQ-016 RESIDUE-(4) CLOSED WITH CITED MEASUREMENT:
## THE SHIELD COMPLETION HANDLER IS THE SOLE SLOT WRITER — word2 |= 0x0f01
## ONCE AT THE COMPLETION TURN (0x3928b); WHILE PENDING THE SOLE MOVER IS THE
## ACC WORD; BPLM FIRED EXACTLY ONCE AT file 0x39290 INSIDE FUN_00038f68;
## t325's STALLS WERE THE PRE-FIX POPUP DETECTOR, NOT THE GAME; NEW LEAD:
## FACTORY AUTO-RESERVE ON THE HUMAN PLANET AT COMPLETION)
ONE scratch debugger session work/r1/t340-shieldc-20261108-014705 (rc=0,
413 s; tool scripts/r340_shield_complete_session.py = r325 FIXED chain
verbatim + 15 s whole-array ring sampling to turns.jsonl; private Xvfb :97,
own ring dir, core=normal, TL 3600; teardown SIGKILL RECORDED dosbox 208428/
Xvfb 208424 (kill_rec prints to STDOUT only, not session.log — read the bg
transcript for teardown lines); production :9 136357/136359 + Xvfb 1461
ps-verified UNTOUCHED;
sitting check NEGATIVE turn 1086; launch-1 …013812 renamed .harnessbug1 =
exit-2 class NameError, not a scientific negative). PROVED: (1) PER-TURN LAW
t1086..1093: pending acc 30/36/42/48/54 (+6=stored IND verbatim), ALL 83
slot dwords frozen; completion at t1091 (54+6 >= COST 60). (2) COMPLETION
STORE witnessed live: 0x3928b `or WORD PTR [ebx+eax*4+0x2],dx` dx=0x0f00 ->
slot76 0x00001a01->0x0f011a01 (byte2 01 active, byte3 15 ONE-TIME marker —
t325 census EXPLAINED), gate flag-word bit8 SET (item 26 @DS:0x74256=0x8
measured; DS base B+0x82bb0) + slot>=cells; reset tail 0x39290..0x3929a
+0x52=0xffff/+0x54=0xff/acc=0 observed same turn; acc resumes +6/turn.
(3) WRITER IDENTITY: BPLM 0x25EAF4 fired EXACTLY ONCE whole-log (00->0F) at
EIP-linear 0x1f86e0 = file 0x39290, inside FUN_00038f68 (0x38f68..0x394d8);
fire regs esi=0x270c66 = Gridsor I linear VERIFIED, eax=76, edx=0xf00.
Static census scripts/r340_slot_writers.py: 4 slot *4-stores in the fn
(0x39164/0x391ce dig, 0x3920d |=2, 0x3928b completion). (4) t325 INSTRUMENT
VERDICT: drain closed 23 popups (7 drain calls) of the exact class that stalled t325
(offline: committed detector returns (406,442) on t325's drain_0.png) —
t325's four zero-fire launches were NEVER the game. (5) NEW named observation
(candidate residue 6, NOT part of the closure): slot43 byte1 ff->00 same
boundary = item 0 FACTORY auto-reserved on the HUMAN planet, queuer
undecoded -> t341. LEDGER: residue-(4) CLOSED strict-close with cited
measurement (OQ-016 ROW STAYS OPEN — residues 1, 5 + candidate 6); count
unchanged 16/3. Files: docs/re/_wip_t340.md S0-S5, income-law.md S-T340
(hand-authored, no regenerator — verified), REFUTED-ROUTES t340 amendment
(3 clauses), OPEN-QUESTIONS residue-(4) rewrite, campaign.cpp buildPhase
comment (no code delta). Tools r340_shield_complete_session.py (rc=0),
r340_writer_site.py + r340_slot_writers.py (exit 0). GATE 0, ledger + index
audits OK. NEXT=t341 factory-auto-reserve decode VERBATIM


## LANDED t339 — 2026-11-07 (BatControlWnd INTAKE DECODED, ZERO CAPTURE: NO
## POSTER OF 0x1c01 TO SLOT 61 EXISTS ANYWHERE; THE MODE-1 CHAIN IS
## UNREACHABLE BY CONSTRUCTION (EIGHTH CITED-DEAD LEG); THE 804..813
## SENDMESSAGE VALUES ARE DORMANT DATA; t331's GATE-BRANCH QUESTION CLOSED)
Zero-capture iteration (static whole-image walk over work/r331_disasm.txt
140,824 insns + windows.txt + offline save scan; tools
scripts/r339_intake_census.py exit 0 (work/r339_intake.out),
scripts/r339_cfg156d4.py, scripts/r339_xreach.py (work/r339_xreach.out),
scripts/r339_dump.py; scripts/r339_rec_census.py exit 1 = instrument negative
S7; working doc docs/re/_wip_t339.md S0-S7; ships.md S58). Sitting check
NEGATIVE turn 1086; production :9 never signalled; game/ read-only. PROVED:
(1) PARENT-SLOT LAW verbatim x3 parser sites (0x59012/0x59618/0x59726 blocks):
[child+0x63] := parent slot-id at parse time + fn 0x30c20 child-list link —
My^Items [w+0x63]==61 BY CONSTRUCTION. (2) ROUTER LAW (fn 0x30c9c, reached via
0x336b4 dx-chain): arms 4/5 (0x30e0e) + 0xc (0x30f46->0x30edc) parent-post the
child's SENDMESSAGE WORD [w+0x45]+SENDPARAM1 to [w+0x63] (0x30ecb); arms 7/8
NEVER parent-post — t302's msg-0xc law fully explained; t338's all-7/8 battery
could not propagate by law. (3) ROAD BLOCKED: pump parent-priority fn 0x56b5c
0x56c34 (`[w+0x63]!=0 && msg>2` -> skip) + parent rect 0,0-0-0-0 rect-test
fail + children have no custom code => 804/805/807..813 can NEVER reach
fn 0x156d4 from observable traffic; whole-image imm census 0x324..0x335 = the
receiver's own cmps only, no poster. (4) THE 0x1c01 ANSWER: literal census 18
sites = 14 receiver cmps + 4 senders (self-post 0x16168 INSIDE the gate tail,
STATSHIPLST 0x33374/0x3338e -> slot 95, LOADSCREEN 0x35696) — t315 inventory
reproduced exactly; windows.txt SENDMESSAGE max value 1006. (5) CFG: gate
block {0x15fed,0x16147,0x16181} has NO in-edge outside itself except the
rebased 0x15ef1 jump table from the 0x1c01 branch; ctor zeroes b9 so external
arrival exits 0x15b39; b9 2/3 writers are inside the gate; the 0x320 posters
{0x1b164,0x1b202,0x1bb5e,0x1bf80} target BatModeWnd's NULL state table (t331
20/20 saves) — never executed. t331 open question CLOSED (0x1c01 branch via
table member; 0x16181 table-only). (6) 0x324->0x158c0 {b9=1, fn 0x16cf0
redraw, self-post msg 0}, 0x325->0x158f3 {b9=4}; 807..813 have no branch.
(7) saves 41..49 contain ZERO window-record strings/magic — records not
persisted at all (t316 clause extended to records; REFUTED-ROUTES t339 (3)).
LEDGER nothing closed strict-close (16/3); residue-(1) REWRITTEN — EIGHTH
cited-dead leg, closure = user ruling D2-c alone (DECISIONS.md OQ-016 note
updated). Files: _wip_t339.md S0-S7, ships.md S58 (hand-authored),
REFUTED-ROUTES t339 amendment (3 binding clauses), DECISIONS.md OQ-016 note,
OPEN-QUESTIONS residue-(1) rewrite. GATE 0, ledger + index audits OK.
NEXT=t340 shield-completion final witness VERBATIM

## LANDED t338 — 2026-11-08 (STATE-16 LIVE DRIVE EXECUTED: THE MODE-1 CHAIN IS
## ZERO IN BATTLE STATE TOO — SECOND INDEPENDENT ZERO; THE STATE-16 TRIGGER IS
## THE GALAXY-MAP ICARUS-PIP CLICK; SET-STATE edx=0x10 + hit-routing WITNESSED
## LIVE; t332's "obstacle is the active screen state" SUPERSEDED)
ONE scratch debugger session work/r1/dbg-t338-20261107-224027 (rc=0 attempt 1;
tool scripts/r338_state16_session.py composing r332_batctrl_session.BatSess +
r337_state_word state oracle; private Xvfb :97, own ring, core=normal, tl 7200;
teardown SIGKILL RECORDED pids dosbox 200239/xvfb 200235; production :9
136357/136359 + Xvfb 1461 ps-verified UNTOUCHED post-run; sitting check
NEGATIVE turn 1086; game/ read-only). PROVED: (1) TRIGGER from existing data:
the five state-16 saves of t299-leg-20261105-112859 sit exactly inside the
star1 census window — pip click (238,282) ENTERS the system view = state 16,
Escape exits; reproduced (diff=94504, oracle sav=56.sav state=16 groups=18).
(2) STATE-SWITCH WITNESS: setstate_56e10 STOP eax=ebp=0x2bc35c edx=0x10 (t337
law live); ringa_55ea3 census x1. (3) ROUTING WITNESS: hit_test_56890 x2
(edx=click Y 0x76/0xc8), btn_hdlr x17 on the state-16 family rows — banked
window names My^Items/Other^Items/Auto/Pass/TOGGRID/BATZOOMIN (SAME pixels
t332 measured NEXTTURNCONT-owned in state 1); focus_56aa4 zero (xsend
press+release law banked). (4) HEADLINE: pty whole-log census ZERO at all
eight chain legs {0x156D4, 0x15EF1, 0x15FED, 0x1615D, 0x1616F, 0x161D1,
0x1B7DD, 0x1B180}; BatModeWnd +0xb7==1 in 0 oracle reads. OUTCOME C: t337's
wrong-state candidate for t332 REFUTED as cause; BatControlWnd is a TYPE-19
parent rect 0,0-0,0 — never a mouse hit target; entry needs a POSTER to
registry slot 61. LEDGER nothing closed strict-close (16/3); residue-(1)
REWRITTEN (SEVEN named unreachable legs; live edge = t339 intake decode or
user ruling D2-c). Files: docs/re/_wip_t338.md S0-S4, ships.md S57
(hand-authored), REFUTED-ROUTES t338 amendment (4 binding clauses),
scripts/r338_state16_session.py (rc=0). GATE 0, ledger + index audits OK.
NEXT=t339 BatControlWnd intake decode VERBATIM

## LANDED t337 — 2026-11-08 (THE STATE TABLE'S READERS ARE THE SCREEN ROUTING
## MACHINERY: CURRENT-STATE WORD core+0x4228 FOUND + MEASURED {0,1,16,17};
## STATE SWITCH = CLICK-POSTED RING-A CODE-1 RECORD; NO BROADCAST TARGETS
## GROUP 16; t333 "NO GLOBAL ACTIVE-STATE DATUM" SUPERSEDED)
Zero-capture iteration (static whole-image walk + offline census; tools
scripts/r337_state_readers.py exit 0, scripts/r337_state_word.py exit 0;
working doc docs/re/_wip_t337.md S0-S7; ships.md S56). Sitting check NEGATIVE
(tail-seek newest turn 1086 == corpus). Production :9 never signalled; game/
read-only. PROVED: (1) dword winmgr+0x4226 = TWO u16s: LOW distinct-group count
(inc 0x57207/dec 0x5711e only), HIGH = winmgr+0x4228 CURRENT STATE ID, image-
wide exactly THREE touchers, sole runtime writer 0x56f66 in SET-STATE fn
0x56e10(core,edx=newstate); all 17 legacy `sar 0x10` sites read the current
state, not a count. (2) READER INVENTORY 16 fns: SET-STATE 0x56e10 (msg 2/1
group broadcasts, per-group LEAVE cb +0x30f0 / ENTER cb +0x30ec, 16-deep
history ring core+0x4736), POP-STATE 0x57020, clear-group 0x57094, BROADCAST-
TO-GROUP 0x56b5c (32 slots, vtable [win+0xa7]+8, re-entrancy byte 0xa2024+g),
POST-TO-HANDLE 0x56ca4 (the t331 msg path), HIT-TEST 0x56890 (mouse globals,
focus core+0x3002, current-state fallthrough 0x569d9), FIND-BY-NAME-IN-STATE
0x56d8c (10 callers incl. the 0x27401-family), record-free 0x574a4 (dec
[core+0x3000], the t316 law home). (3) SET-STATE callers arg-traced: boot
0x21733 edx=0 (trampoline-wired fn 0x20fd4, which also installs ENTER cbs for
16 groups via 0x57464 — NO group-16 cb), hotkeys 0x54d92 edx=2 / 0x54dba edx=4
(fn 0x54d18, WORD ds:0x484c4, guard current!=8), RING-A arm 0x55ea3 edx=record
PARAM. (4) RING-A LAW: poster 0x56ad4(core,edx=code,ebx=param) 44 sites; code-1
resolver arm's new-state = the u32 param verbatim; static param-0x10 posters
0x28ed8/0x51ad1/0x5200f/0x36b0b (all prime ds:0x43504). (5) MEASURED 537 saves
(t336 fingerprint, base 0x2bc3e4 537/537, groups=18 everywhere): current-state
{0:122, 1:236, 16:5, 17:174}, group[state] residency 537/537. State-16 saves =
t299-leg-20261105-112859/save/43..47.sav. (6) All 9 broadcast sites name fixed
groups {1,2,3,4,5,d,e,f} — group 16 NEVER broadcast; BatModeWnd magic-rec
+0xb7=0/+0xb9=0 in EVERY save incl. the state-16 five (BatControlWnd rec
+0xb7=253/+0xb9=1 constant — accessor-vs-magic base note recorded). LEDGER
nothing closed strict-close (16/3); OQ-016 residue-(1) reader side CLOSED by
measurement, row open on the mode-1 arming witness alone, with t332's zero now
having a measured candidate cause (capture states {0,1,17}). Files
_wip_t337.md S0-S7, ships.md S56 (hand-authored), scripts/r337_state_readers.py
+ r337_state_word.py (exit 0). Sitting NEGATIVE t1086; production :9 (136357/
136359, Xvfb 1461) never signalled; game/ read-only. GATE 0, ledger + index
audits OK. NEXT=t338 state-16 live drive VERBATIM


## LANDED t335 — 2026-11-08 (THE win+0x6d STRIDE-13 ARRAY IS THE WINDOW-ITEM
## ARRAY: t334'S "STATE-LINE CONSUMER" RETRACTED, THE id-16 ASSERT PARADOX
## DISSOLVES, RESIDENT-windows.txt LAW FAILS TO REPRODUCE)
Zero-capture iteration (static disasm + offline census; tools
scripts/r335_state_records.py exit 0 (run 1, join failure) and
scripts/r335b_item_array.py exit 0 (decisive); working doc docs/re/_wip_t335.md
S0-S5 (sections landed out of numeric order; read S1->S4->S5); ships.md S54;
REFUTED-ROUTES t335 amendment). Sitting check NEGATIVE (tail-seek, max turn
1086 == corpus). Production :9 never signalled; game/ read-only. PROVED (196/196
needle-verified saves, 22,398 window instances, truth = on-disk windows.txt):
(1) [win+0xa1] == TEXTITEM+SHAPEITEM line count 22398/22398 EXACT (STATE-count
test fails 3844/18554); record byte0 == item kind (0 TEXTITEM / 1 SHAPEITEM)
4900/4900 positional; tag0 u32@+1 resolves through interner ds:0x6fda8 to the
file item's literal name VERBATIM 3528/3528; record-bearing windows == exactly
the 15 item-line windows, both directions. (2) CODE IDENTITY: parse block
0x57ee6..0x58062 (fn 0x575e4) = WINITEMS/TEXTITEM/SHAPEITEM builder — ds:0x30fb
="%s %s", 0x3101="%s %d" (WINITEMS -> loop bound), 0x3107="%s %d" (item kind),
0x310d/0x3119="%s %d %d %d" (name+int triple, u16s into the record tail); fn
0x31690 = item appender, its ([eax+0x9f]>>16 >= 4) gate IS the +0xa1 counter
cap, NOT a type check. (3) PARADOX DISSOLVED: assert 0x5804c reachable only for
kind>1, never shipped (file kinds {0,1}: 18+7 lines) — `STATE 1 16` never enters
the block; assert chain 0x2a438(eax=0)->0x76c79->int3 0x2a424 verified verbatim.
(4) t333 CORRECTION: NUMCONTROLS occurs in 0 of 284 save dirs' Memory members —
windows.txt is NOT resident; STATE-regex hits are C-literal fragments. LEDGER:
nothing closed strict-close (16/3); OQ-016 residue-(1) STATE-consumer question
now closed by MEASUREMENT (no consumer in fn 0x575e4; control table t333 + item
array t335 + no global datum t333 all ruled out); row stays open on the mode-1
witness alone. GATE 0, ledger + index audits OK. NEXT=t336 keyword->store map +
STATE-value disposition VERBATIM.

## LANDED t334 — 2026-11-08 (CONTROL-TABLE ATTACH SITE WALKED; THE STATE LINE'S
## RUNTIME HOME IS win+0x6d STRIDE 13 — CONSUMED AT PAINT TIME, NOT AS A SELECTOR;
## ds:0x13b98 = 4 MEASURED 196/196)
Zero-capture iteration (static disasm + offline census; tools
scripts/r334_parse_map.py exit 0, scripts/r334_state_array.py exit 0, fresh
region objdump work/r334_disasm_57c00.txt; working doc docs/re/_wip_t334.md
S0-S13; ships.md S53; REFUTED-ROUTES t334 amendment). Sitting check NEGATIVE
(tail-seek, max turn 1086 == corpus). Production :9 never signalled; game/
read-only. PROVED: (1) 0x57d56/0x57e48 are fallthrough-only sequential parse
blocks INSIDE the windows.txt parser fn 0x575e4 (sole entry: tail call 0x575da
from winmgr init); guards read scanner status [esp+0x3a6] (>>16==25 -> poison -1,
==15 -> copy parsed u32 verbatim to [win+0xab]); no allocator at the attach site,
no imul-14 in the 2,328-insn body. (2) FORMAT-STRING DOMAIN LAW: parser-pushed
constants in the 0x3000 range are DATA-segment scan format strings (ds:0x3008
reads `%s %d` at B+0x82bb0+0x3008 in 41.sav) — NOT windows.txt offsets; the
earlier "text offset" coincidences are dead. (3) THE STATE-LINE CONSUMER EXISTS:
parse loop 0x57ee6..0x57ff5 builds 13-byte records at win+0x6d (compactor fn
0x31690 verbatim: dst = win + 13*[win+0xa1] + 0x6d, movs 3xDWORD+1xBYTE,
counter++); walker fn 0x31384 renders slots byte0==0 text (format 0x7d3aa) /
byte0==1 handle-resolve (fn 0x1fc34 via 0x9f10c) / else assert — its EXACTLY-2
callers are inside paint fn 0x30fb8, which has NO in-image pointer to it. STATE
slots feed paint-time text/handles, never a screen selector. (4) CENSUS 196
needle-verified saves: WORD ds:0x13b98 = 4 in 196/196; battle-family counters
[win+0xa1]=0 (690-record probe: {0:600,1:30,2:60}, nonzero only for the id==0
name family). (5) SELF-CORRECTIONS banked in-file: interim S12 "global stride-13
array ds:0x6fda8" retracted by S13 (fn 0x315c4/0x31660 body = repnz scas NAME
INTERNER, 0x400 pool, counter ds:0x701a6). LEDGER: nothing closed strict-close
(16/3); OQ-016 residue-(1) disposition rewritten on mechanism, with the
id-branch paradox (`STATE 1 16` vs assert 0x5804c) handed to t335. GATE 0,
ledger audit OK. NEXT=t335 STATE-record file-vs-RAM diff + id-branch
re-derivation VERBATIM.

## LANDED t333 — 2026-11-08 (THE "GLOBAL ACTIVE SCREEN STATE" IS A CATEGORY
ERROR: [win+0xab] IS THE CONTROL TABLE, fn 0x31d58 WRITES CONTROL FLAGS, AND THE
BATTLE-MAP WINDOWS HAVE NO TABLE AT ALL)
Zero-capture iteration (static disasm + offline .sav census; adopted an
interrupted session's uncommitted docs/re/_wip_t333.md S0-S3 +
scripts/r333_state_census.py and finished the task in the same commit).
Production :9 pids 136357/136359 + Xvfb 1461 never signalled; game/ read-only
(ascend00.cob grepped only). MEASURED/PROVED: (1) STATE-LINE GRAMMAR 123/123
lines `STATE <count> <id> [<id>...]` (RACECONTROLS:418 = 3 states {1,7,13};
BatModeWnd:1180 = ONE state id 16) — the state-16 family is 20 windows, t332's
"19" was off by one; (2) LAYOUT from five independent verbatim reads: [win+0xab]
u32 table ptr, [win+0xaf] u16 count, [win+0xb1] u16 CURRENT CONTROL INDEX (never a
state id — t323's wording corrected); (3) BYTE-FOR-BYTE control-record decode:
RACECONTROLS member 0xfd5d84 table->0xfd5e3c rec[0]=`01 00|df 01 ef 01|c1 01 d1
01|05 00|14 00` == windows.txt:429 `RACE1CONTROL 1 479 449 495 465 0 20`, ids
1,2,4,8,16,32,64 = the RACEnCONTROL bitmasks => [win+0xab] is the CONTROL table and
fn 0x31d58's only store 0x31dd0 `mov WORD PTR [eax+0xa],dx` writes CONTROL
enablement, so it cannot select a screen (the task's premise, refuted); (4) flags
372/372 saves: ids 1,2,4,8 = 5, ids 16,32,64 = 0, and since caller D passes val=1
with a MOV (not OR), bit2 is runtime fn 0x32048 (0x320bf/0x320c5) and bit1 is
fn 0x31f30 — enablement is COUNT-CAPPED, [inferred] per player slot (runtime
ds:0x13b98 NOT measured, see the mapping law); (5) RACECONTROLS IS THE ONLY
WINDOW WITH A DECODABLE TABLE in 372 saves — BatControlWnd 0xfdbebc and
BatModeWnd 0xfdc924 measure +0xab=+0xaf=+0xb1=0, which makes the sole runtime
switcher fn 0x31f30 bounds-assert on them (count=0), confirming t323's
construction-pinning by measurement; (6) NO GLOBAL ACTIVE-STATE DATUM: zero store
forms to ds:0x13b98 across the WHOLE code image (r331 covers 0x14bb0..0x826a5,
max inter-line gap 66 B; fresh low-range objdump 0x0..0x14bb0 adds 9 refs, none a
store); (7) the windows.txt keyword literals occur ZERO times in every RE image
(ascend_restored/payload/raw/t73c_obj1slab) and only in game/ascend00.cob
(NUMCONTROLS n=1 @0x2aefb, PARENT n=123) => the STATE-line consumer is
keyword-table-driven from data the RE image lacks; BUT windows.txt text IS
resident in the save (member 0x39db51), which is t334's handle; (8) NEW LAW: the
save-member-to-linear delta is NOT a constant 0x88 across save dirs — the +0x88
probe returns 0x1d5349/0x1d543d/0x1d55d1 in playcap saves where t332 measured
0x15ef9/0x15fed/0x16181, so re-derive per save and validate with a needle before
any ds: read. LEDGER: NOTHING closed strict-close (16/3: OQ-005, OQ-016, OQ-019
open); OQ-016 residue-(1) REWRITTEN to stop pointing at fn 0x31d58 and to name the
loader-side control-table site. Files: docs/re/_wip_t333.md S0-S9,
docs/re/ships.md S52 (hand-authored, no generator), scripts/r333b_state_layout.py
(exit 0), scripts/r333_state_census.py (superseded field map, kept for history).
NEXT = t334 control-table attach-site walk per the block above.

## LANDED t332 — 2026-11-08 (BATCONTROLWND CHAIN LIVE WITNESS: FIFTH LEG
## INSTRUMENTED AND MEASURED ZERO; THE OBSTACLE IS THE ACTIVE SCREEN STATE)
ONE scratch debugger session (work/r1/dbg-t332-20261107-124717, attempt 1 rc=0,
tool scripts/r332_batctrl_session.py; sitting check NEGATIVE turn 1086 via 40 MB
tail-seek; production :9 pids 136357/136359 + Xvfb 1461 never signalled, ps-verified
post-run; teardown SIGKILL recorded PIDs dosbox 174711 / xvfb 174707 only).
MEASURED: (1) PTY whole-log census ZERO at ALL EIGHT chain legs {fn156d4_entry
0x156D4, tbl15ef1, gate15fed, post1615d, relay1616f 0x1616F, post161d1,
mode1_1b7dd 0x1B7DD, backch_1b180} with control btn_hdlr firing 8x and 8/8 banked
stops attributed — fn 0x156d4 (BatControlWnd, slot 61) received NO message of any
id; save axis (19 oracle reads) holds BatControlWnd 0xfdbe34 [+0xb7]=0 [+0xb9]=0
and BatModeWnd 0xfdc89c [+0xb7]=0 in every save before/after every click. Battery
clicked the item rects t322 named as never clicked — (513,118) My^Items /
(591,118) Other^Items — on the map AND in the entered view, plus BatListWnd-interior
(553,200) and the assignment's literal (593,218), plus two leg-armed hold windows.
(2) THE DELIVERY EDGE IS NOW NAMED MECHANICALLY (fresh objdump 0x16060..0x16200):
fn 0x156d4's own shared tail 0x16162..0x1616f relays msg 0x1c01 to ITSELF through
its class table (`mov ebx,[ebp+0xa7]; mov edx,0x1c01; mov eax,ebp; call [ebx+0xc]`),
reached from the 0x16071 shield jmp, the 0x16145 jmp and the fallthrough of the 0x51
post — which is exactly why t331's immediate census saw no poster. (3) WHY ZERO,
MEASURED AT THE PIXEL: banked stops name NEXTTURNCONT (msg 4/8, ret0 0x3177d) as
the owner of the My^Items/Other^Items pixels on the map and PLIND/PLBUILD (msg 4/8,
ret0 0x3cb8d) in the rowjump view; the t253 FLEET rowjump enters the PLANET/orbital
state, NOT a battle screen. (4) STATE-16 CENSUS (fresh windows.txt parse): STATE 1 16
is EXCLUSIVELY the 19-window battle-map family; states witnessed in captures are
{1,3,7,13,17,18} — ZERO overlap. (5) JUMP-TABLE SPACE FIX: t331's "member 0x1d4b04"
is the LINEAR disp32 read from the live instruction; the .sav member is 0x1d4b8c,
where the table reads [0]=0x15ef9 [1]=0x15fed [2]=0x16181 [3]=0x15ef9 (4/5 =
0x1624d/0x161e5, unreachable: the b9 dispatch bounds al<=3) — t331's structure
CONFIRMED as data for the first time. LEDGER: NOTHING closed strict-close (16/3);
OQ-016 residue-(1) REWRITTEN to point at the active-state edge. Files:
docs/re/_wip_t332.md S0-S9, docs/re/ships.md S51 (hand-authored, no generator),
docs/REFUTED-ROUTES.md t332 AMENDMENT (5 binding clauses), scripts/
r332_batctrl_session.py. NEXT = t333 active-screen-state walk per the block above.

## LANDED t331 — 2026-11-08 (BATMODEWND ACTIVATION STATIC WALK: ACTIVATION IS
## THE WRONG QUESTION — THE BATCONTROLWND MSG ROAD IS ALIVE-IN-IMAGE)
Purely STATIC iteration (zero launches; production :9 pids 1461/136357/136359
untouched; sitting check NEGATIVE turn 1086 tail-seek; no D2 answer block).
Instrument: fresh whole-code objdump (work/r331_disasm.txt, 139,026 insns, zero
badbar) — deliberately NOT the t91/tsv segmentation (proven broken past 0x160cb).
MEASURED/PROVED: (1) t326b S8(3) REFUTED — fn 0x1aef8 tail cmp dx,0x50/jb/jbe:
dx==0x51 FALLS THROUGH onto 0x1b7dd BYTE[+0xb7]=1 MODE-1 ARMED (bytes banked);
(2) both 0x51 posters (0x1615d/0x161d1 in BatControlWnd handler fn 0x156d4)
target edx=[[ebp+0xbb]+0x41]=registry slot 63 = BatModeWnd (live MEASURED;
t326b's category-bit-slot reading REFUTED — edx clobbered at 0x1615a); (3) THE
ENTRY: msg 0x1c01 branch 0x15ebf -> RAM jump table (member 0x1d4b04; file read
at disp32 is the "...cosmos.cpp" string = FALSE ZERO, law C5) entry[1] -> gate
0x15fed (gizmo WORD[+0x33]: 0x80 abort / 0x20 shield fn 0x49e78 / CLEAR -> post
0x51); b9 machine fed by msg 0x320 (0x15b51/0x15b48/0x15b1e) + 0x1c01 legs
(0x15f1e/0x15f25/0x15f35, which also post 0x53 to slot 63); (4) gizmo flags
FILE-LOADED sole writer fn 0x49074 (gizmos.txt flag_list; Phase^Bomb {3}=bit8 ->
0x80/0x20/0x40 CLEAR by file data); (5) BatModeWnd RECORD RESIDENT 20/20 saves
(runtime 0xfdc89c, magic+RAW-ASCII law; t324 caveat REFUTED), state 0 +
state-table NULL => setter fn 0x31f30 bounds-asserts any id>=0 (construction-
pinned; STATE-line activation stays dead — 20-save sweep, setter-bounds law);
(6) t322 armed-zero RE-SCOPED: fn 0x156d4 never armed in ANY capture; item-rect
clicks (My^Items screen (559..628,203..233)) never in any battery. OUTCOME per
assignment: NEITHER pure A nor B — road ALIVE (A-class) but one uncited edge
(who posts 0x1c01 to slot 61; image imm census = none; road law fn 0x33320
edx=[win+0x63], STATSHIPLST->95) => t332 capture JUSTIFIED, legs named.
LEDGER: NOTHING closed strict-close (16/3). Files: docs/re/_wip_t331.md S0-S7,
ships.md S50 (hand-authored, no generator verified), REFUTED-ROUTES t331
AMENDMENT (5 clauses binding), OPEN-QUESTIONS residue-(1) REWRITTEN.
NEXT = t332 BatControlWnd chain live witness per the block above.
## LANDED t330 — 2026-11-08 (MOUSE-DIMS DRAW-CAPTURE: draw-time dims slot
## MEASURED = rec+0 u16 pair [H-1,W-1]; C27-C29 'invalid dims' REFUTED)
TWO live debugger sessions on scratch (production :9 pids 136357/136359 +
watcher UNTOUCHED, ps-verified post-run; sitting check NEGATIVE turn 1086 via
tail-seek). RUN 1 dbg-t330-20261107-073530 (blit_entry-armed): banked the
TOOL LAW that an entry-leg stop CONSUMES the census window (6 stops, one per
bar panel, ret0=0x64aa6 = the generic 5-arg blit call 0x64aa1 ADD ESP,0x14;
deref/refuse NEVER fired behind an armed entry — heavy-check does not
re-enter mid-block post-RUN) + DECISIVE: MOUSE.SHP verbatim 10435-B copy at
sav-linear 0x2EC0C4 = PAY 0x2EC03C + 0x88, OUTSIDE the 200-slot cache (attri-
bution by rec_head bytes, not slot name; cache ctx = 0x2E1194 ABSOLUTE in
the .sav — P0+0x9F10C reading REFUTED for .sav scans; registry 0xFFFFFFFF).
RUN 2 dbg-t330b-20261107-080216 (refuse+minus2+deref+btn_hdlr armed,
instance-patched bank_stop — DbgSession COMPOSES Sess, wrapper overrides are
dead code): census {blit_deref:15, blit_refuse:0, blit_minus2:0,
btn_hdlr:10}; 8 attribution rows; the 4 phase-tagged mouse stops (status k2,
fleet/research/specialab k0) show runtime shape hdr (W-1,H-1) == file
(u16@rec+2, u16@rec+0) and NEVER the u32@+0x10 pair (k0: hdr (11,15) vs
+0x10 (10,14)) => DRAW-TIME DIMS SLOT = rec+0 u16 PAIR stored [H-1,W-1]
[verified, mouse k0/k2]; mouse.shp draws on EVERY right-bar panel open.
blit_refuse 0 fires whole-log. post-rearm rows (639x479 full-screen shape,
pixptr 0x2f2af8) = cascade artifact, excluded. CONSEQUENCES: C27-C29
(46,77)@+0 = 78x47 VALID dims — 'invalid dims' classification REFUTED; the
records stay drawn-frame-unwitnessed (no selector names k5/k6/k7; CURSORSHAPE
2 only L216/L1186) but the slot-LOCATION dispute is closed by measurement for
the mouse lib. Generalization bounded: corpus u32@+0x10 == (u16@+2-1,
u16@+0-1) fails 1526/1567 — do NOT rewrite shp.cpp dims reading on mouse-only
data (per-library witnesses needed; queued behind OQ-016 by the t330
instruction). LEDGER: NOTHING closed strict-close (16/3). Files: docs/re/
shp.md S26 (hand-authored, no generator verified), docs/re/_wip_t330.md
S0-S3, scripts/r330_blit_session.py (legs 0x5cb2b BF7B / 0x5cb36 BF86 /
0x5cb59 BFA9 unique-audited vs 61 LEGS; --offline replay 0 drift),
OPEN-QUESTIONS OQ-005 note, DECISIONS.md D1/D3 updated (C27-C29 = formality).
NEXT = t331 BatModeWnd activation static walk per the block above.


## LANDED t328 — 2026-11-07 (OQ-005 DRAW-WITNESS FEASIBILITY: 41 of 44
## C-rows leave the human ask; mouse k5/k6/k7 sole witnessable residue)
OFFLINE-ONLY iteration (zero launches; production :9 pids 136357/136359 +
watcher 136372/136374 untouched, ps-verified). Sitting check NEGATIVE (newest
playcap turn 1086 via tail-seek; OOM law honoured — never full-read the 7.9 GB
timeline). Deliverables all measured, files: docs/re/shp.md S25 (durable law,
hand-authored — verified no script writes shp.md), docs/re/_wip_t328.md S0-S4
(working notes + t330 design), work/r1/shp_png/_t328_dims.json (44-row dims/-
span census), scripts/r328_hdr.py (record-header dumper). MEASURED: (1) blit
-1 gate re-verified from raw asm at 0x5caac..0x5cb2b (inc-then-jle on
[ebx+4]/[ebx+8]); (2) cos_star k40..51 all-zero 24-byte headers 12/12 =>
vendor CANNOT draw them (zero dims every slot) => CITED-NO-WITNESS; (3) the
25 ladder slots are zero-STREAM (span==header: 8 B k0-variant / 24 B k>=1)
NOT dims-zero (task-text framing corrected) + every lib named in
extracted/ascend00/batfx.txt battle-effects list => combat class + zero
draw-content => CITED-NO-WITNESS; (4) 1starmap k1 zero-stream + SHAPEITEM
selects k3/k4/k5/k7 only (windows.txt 456/477/498/517) => CITED-NO-WITNESS;
(5) sg50expl k9 near-empty+EOF + batfx line 58 => cited; sg64expl k0 batfx
line 63 => UNREACHABLE (t323); (6) 3cfgnew k12 EOF-truncated => JUNK-CERTAIN;
(7) MOUSE CORRECTION: t196 "k6/k7 not walkable" was canonical-slot-only —
with u16 dims @rec+0 (46x77) ALL of k5/k6/k7 walk EXACT-H 77/77 from
rec+0x18 (2038 stream bytes real art); canonical u32@+0x10 has a zero
component each ((0,46)/(77,0)/(0,0)) => dims-SLOT-LOCATION dispute, not junk;
windows.txt has no mouse.shp SHAPEITEM and 'DATA\MOUSE.SHP' @0x84314 has zero
u32 refs in code (honest negative, scan calibrated against planets/LGRACE/
planal hits) => selector UNKNOWN => t330 capture designed (S4), NOT run.
LEDGER: NOTHING closed (strict-close; feasibility sharpens, never closes).
OQ-005 row appended with the S25 verdict + t330 pointer; DECISIONS.md D1
REWRITTEN (ask = B-rows + C27-C29 only; 'draw-capture' alternative kept) and
D3 OQ-005 line updated. NEXT = t330 VERBATIM per the block above.


## LANDED t327 — 2026-11-07 (DEBUGGER-SESSION TOOL v2: scripts/r1_dbg_session.py)
Tool SHIPPED and VERIFIED end-to-end. Composes r299_leg_session machinery
(imports it; re-derives nothing): declarative LEGSPEC {addr, callsite, hot},
phase runner (baseline/starN/hold/preturn), expectation grammar
(LEG==N / LEG>=N / LEG@0xRET0), whole-log FirePat census, verdict.json,
atexit bank-on-exit, in-process r322 relaunch loop, SIGKILL-recorded-PID
teardown. Mechanical law gates NEW: last-4 FirePat-collision preflight (the
t305 manual audit as a unit check), port-busy preflight, Oct-29 md5, game/
mount refusal. VERIFIED (all measured, zero drift vs recorded census lines):
offline t308 runs 140250 (9/9: w43504_28ec2 1, btn_hdlr 8) + 143815 (2/2);
offline t319 run 030727 (5/5 incl. s2_56cda 106; poster ret0@0x54aca = post
call 0x54ac5+5 msg-4 found); MUTATION battery 7/7 (bogus leg -> 0 fires no
crash; wrong count/callsite -> FAIL rc=1; unparsable expect/bogus live leg/
busy port/collision -> rc=2 before any launch). LIVE: run
work/r1/dbg-t327v-20261107-050546 attempt 1 rc=0 PASS ~4.6 min wall —
23 green pips (t308b count reproduced), click (182,284) diff=94712 ENTERED,
WITNESS DELTA 0x256825(Icarus)->0x255bc5(Vega) byte-identical to t308,
census {w43504_28ec2:1, btn_hdlr:2}, verdict PASS 3/3 incl.
btn_hdlr@0x3177d, clean teardown, offline replay of the fresh run 0 drift.
INTERPRETER LAW: run with ~/.hermes/hermes-agent/venv/bin/python (system
python3 has NO PIL). Docs: docs/re/dosbox-debugger.md §TOOL v2 appended
(hand-authored file, no generator); docs/re/_wip_t327.md S0-S6. LEDGER:
tooling task, NOTHING closed (strict-close unaffected; 16 closed / 3 open).
Sitting check NEGATIVE (turn 1086); production :9 untouched (ps verified
post-run: 1461/136357/136359). NEXT = t328 VERBATIM per the block above.


## LANDED t326b — 2026-11-07 (STATIC WALK fn(0x17c54)+fn(0x16147): residue-1 verdict OUTCOME B)
OUTCOME B LANDED: the "mode-1/msg-0x4d..0x51 arming family" DOES NOT EXIST as
messages. fn 0x17b2c writes 0x4c/0x4d/0x4e as GIZMO-INDEX values (consumer
0x17cf8 -> [esi+0x1a92+edi*4]/[esi+0x1bcc+edi*4] via bounds-fn 0x1ce1c; call
census ZERO posters). The sibling 0x16147 IS a real post (engine law fn
0x56ca4) but of msg 0x51(81) to a ds:0x7a35c child-table slot (gate: gizmo
WORD[rec+0x33] bit0x20 CLEAR; bit0x80 abort; bit0x20 set -> 0x49e78 shield
charge), and BatModeWnd fn 0x1aef8 consumes ONLY dx in {6,d,3b,46,47,4a,50}
=> 81 cannot reach the mode-1 setter 0x1b7dd even if misdirected there.
Image-wide 0x51 consumers: fn 0x4709c @0x47ac0 (window field +0xe3 := -100.0
float — gauge/score family, UNNAMED window) + fn 0x6f600 @0x6f7f9 (packet
parse, not a window msg). OQ-016 RESIDUE 1 = UNREACHABLE-BY-CAPTURE cited
(4 independent legs); the 4-launch forced capture is VACUOUS — DROPPED from
the plan (research leg vacuous t326 + no citable arming trigger). Row stays
OPEN strict-close; sole live-movement obstacle = BatModeWnd ACTIVATION
(windows.txt:1178 STATE 1 16; t322 armed-zero x2). Docs: docs/re/ships.md S49
(hand-authored verified — ships.md is NOT generated; scripts only cite it) +
docs/re/_wip_t326b.md S1-S8; OPEN-QUESTIONS residue-(1) text rewritten.
Tools: scripts/r326b_extract.py (pad-run segmentation, mnemonic-after-2nd-TAB
law), scripts/r326b_gizmo_rows.py (0x7650c file bytes UNRELOCATED — values
need RAM). Sitting check NEGATIVE (turn 1086); production :9 untouched; gate 0.
NEXT = t327 VERBATIM per the block above.


## LANDED t326 (2026-11-07, session 36) — PHASE BOMB PREFLIGHT CENSUS:
## RESEARCH LEG VACUOUS, LAUNCH-MSG POST HUNT OPEN->NARROWED (OQ-016 residue
## 1 stays OPEN strict-close; zero capture, production :9 untouched, sitting
## check negative — tail-seek newest turn 1086). Tool scripts/
## r326_precensus.py (exit 0, keeper); working notes docs/re/_wip_t326.md
## S0-S5; law banked docs/re/income-law.md S-T326 (NOT economy.md — that file
## IS GENERATED by gizmo_probe.py, BLOCKED trap) + docs/re/research.md S6c
## stale-"unmapped" corrected. MEASURED: (1) KNOWN-TECH MASK FIELD LOCATED —
## tech row i per-race mask byte ds:0x7478e+0x4b*i bit(1<<race), count word
## ds:0x74744 (law from cheat body 0x47828 verbatim); (2) row13
## Molecular^Explosives (Phase Bomb ResReq) mask 0x05 = RACES 0+2 ALREADY OWN
## at t=1086 — the queued forced-capture's research leg is vacuous; prereq-
## closure 110 in-play edges / 10 violations all deep-tree-skip => gate NOT
## strict-AND on this reading, mask semantics corroborated-not-proven (do not
## wire on this datum); (3) cidx-70 carriage ZERO in 30 ship rows (owner-0
## kinds {3:3,5:8}); (4) Shipyard(22) = 30 ACTIVE slots ALL owner-0 ALL
## class-1 ORBITAL + 2 pending (Cambria II/IV) — build leg UI-satisfiable,
## recipe's surface framing sloppy. STATIC: mode-1 arming msgs 0x4d..0x51
## have NO post-senders (mov edx,0x4d sole site 0x15454 = assert reporter
## 0x2a428 ebx=0x122; 0x4e/0x4f/0x51 zero; windows.txt SENDMESSAGE has no
## value in 77..81; msg->mode map cmp dx,0x50 @0x1b7cd re-read verbatim) BUT
## a VALUE-WRITING family was found and deliberately NOT walked (context
## budget): 0x17c63/0x17c72/0x17c81 set [esp+0x54]:=0x4c/0x4d/0x4e on
## BYTE[[edi]+1] in {0x1c,0x1d,0x1e} (post call 0x39b6c), consumed as INDEX at
## 0x17cf8 into [esi+0x1a92+edi*4]/[esi+0x1bcc+edi*4]; sibling 0x16147 mov
## ebx,0x51 after 0x16122 clears [ebp+0xb1]. DECISION (honest, not a shortcut
## claim): the 4-launch capture is GATED behind the zero-capture walk of
## fn(0x17c54)+fn(0x16147) — if that family posts, launching is alive and the
## capture runs; if it's table indexing, residue 1 joins the cited-dead class
## and no launch can ever witness it. Spending 4 launches (~1 hr + lottery)
## before knowing which is the coin-flip error. NEXT = t326b STATIC WALK
## (queue row 1 inserted; t327/t328 unchanged behind it). NO LEDGER ROW
## CLOSED (strict-close). Gate 0, audits OK.

## LANDED t325 (2026-11-07, session 35) — SHIELD-BYTE WITNESS: NEGATIVE +
## CENSUS LAW (OQ-016 residue 4 premise contradicted, row STAYS OPEN).
## MEASURED (production ring52 B=0x1bf4d8 turn 1086, untouched post-run — ps
## == Xvfb :9 pid 1461 + dosbox-x pid 136359 only): 74 shield-item slots,
## slot byte +3 == 0 on ALL 44 pending-class rows (incl. the live Gridsor I
## pending row item 26 word2 0x0) and constant 15 (word2 0xf01) on 43
## completed rows => byte +3 is NOT a per-turn shield progress value
## (docs/re/income-law.md S-T325; binding note in Fixed laws). WITNESS: 4
## launches budget, ZERO reached the completion turn — att1 stale shape (no
## drain), att2/att4 BREAK-lottery channel death at title (t286 law 2), att3
## two instrument bugs of mine (rgb:- headerless parse; root-vs-window-rel
## click coords — window origin (80,100) confirmed here too, content bbox
## (80,100)-(716,576)). ABSENCE-ONLY: does NOT prove the writer leaves +3
## alone; residue 4 becomes instrumentation-class. ASSETS shipped in
## scripts/r325_shield_session.py: early-arm-at-title BPLM (survives load,
## ZERO boot fires 3/3), deterministic heap member 0x25eb7c (3/3), FIXED popup
## drain (ppm:- P6 + root->window-rel (80,100); offline-verified vs a real
## Corncob I popup (406,442) vs expected (408,442)); scripts/r325_shield_scan.py
## + r325b_oct29_check.py offline scanners; RESUME.GAM law: vendor save = RAW
## data not a zip, live state = ring .sav (t259 re-confirmed). SIGNAL LAW
## banked (Fixed laws): SIGTERM on the game pops quit-confirm (Yes)-default —
## teardown is SIGKILL. Working notes docs/re/_wip_t325.md S0-S8. LEDGER:
## OQ-016 residue (4) annotated, NOTHING closed (strict-close). NEXT: t326
## PHASE BOMB FORCED-CAPTURE verbatim.

## LANDED t329 (2026-11-06, session 34) — OQ-019 DISPOSITION PACKET
## DELIVERED (drafts only; row closes on USER ruling). Zero capture, zero
## guest boot. Full working notes docs/re/_wip_t329.md S1-S5; NEW
## scripts/r329_magnetron_census.py (exit 0). Deliverables: (1) DRAFT final
## OQ-019 row text at _wip_t329 S4 — DO NOT APPLY to OPEN-QUESTIONS.md; the
## row flips closed ONLY on USER ruling (D2 a/b/c + accept cited-dead notes).
## (2) NEW MEASUREMENT (magnetron residue): carriage census — production
## playcap/save (t=1086) 20 saves / 600 ship-rows hold ZERO cidx-60 'Lane
## Magnetron' slots; scratch epochs t261-drive (360 owner-0 slots) and
## t288-probe-* (252) DID carry and STILL yielded zero uses across the
## t265/t273/t285 mines -> residue is WITNESS-CLASS, not absence-only
## (r1_t185 table-law control re-run green same session). (3) Scripted-drive
## idea RETIRED cited-indirect (_wip_t329 S2): gizmo-use orders arm ONLY via
## the batmode-family state-WORD tail 0x15c63/0x15da6 (verified verbatim:
## `mov eax,[ebp+0xb1]` state gate -> [ship+0x62]/[+0x63]/[+0x67] stores),
## the field t323 census-proved writerless and t324 RAM-proved unswitchable;
## commit edges 0x25560/0x25570 (t88a) unreachable without the armed order.
## CAVEAT (honest, banked): no census t296..t324 NAMES the window record
## owning the 0x15xxx block — identity inferred from t88 'batmode' labels +
## gate shape; closure class = cited-but-indirect, same class t323 accepted.
## (4) DECISIONS.md D3 rewritten to actual state: rows closeable by the loop
## WITHOUT user input = NONE end-to-end; OQ-016 (t325/t326 queued) is the
## only row with live loop-side movement potential; OQ-005 waits on D1
## (t328 shrinks the ask); magnetron static law stands. LEDGER: OQ-019 note
## appended, row STAYS OPEN strict-close (a disposition is not a measurement;
## no live store witnessed this iteration). Sitting check negative (tail-seek
## newest turn 1086 == corpus). Production :9 (pid 1957) untouched. NEXT =
## t325 PER-SLOT SHIELD-BYTE WRITNESS per the t329 text's own handoff.

## LANDED t324 (2026-11-06, session 33) — RAM CLASS-TABLE CENSUS: THE t323
## RE-OPEN CONDITION IS DISCHARGED — NEGATIVE ABSOLUTE. Live-RAM census of
## the BatModeWnd class table (read surface = production save `Memory` ZIP
## member per the pointer law; zero guest boot, zero scratch copy, production
## :9 untouched). 10/10 saves 50..59 (t=1086 corpus) IDENTICAL; model
## validated per-save via the Icarus star record 0x256825 name read. The
## table at data payload offset 0x58e8 — the SOLE [rec+0xa7] install target
## (image census of all 62 [+0xa7] stores: 0x58e8 appears ONLY at fn 0x1ac21)
## — reproduces the cited BATMODE table BYTE-FOR-BYTE: RAM slots
## 0x1da04c/0x1f0158/0x1da348/0x1dcca8/0x1f0608/0x1dde2c == P0+0x1abfc/
## 0x30d08/0x1aef8/0x1d858/0x311b8/0x1e9dc (6/6 in-code); fn 0x32100 ABSENT
## (also 0x31f30/0x339a4). Rebase model measured: table base = UNREBASED data
## offset, slots = P0 + static fn offset (the t307 code-rebase law does NOT
## apply to class tables). docs/re/_wip_t324.md S0-S4 + scripts/r324_census.py
## (exit 0, self-validating). Task-text correction (banked): [wmgr+0x3337]
## stride 0x27 is the LANE POOL (data 0x16147 = LANE_X), NOT a window-name
## registry — the census anchored on the installer target instead. Honest
## caveat: census is via the unique installer's target offset; no BatModeWnd
## RECORD is resident in the t=1086 save (no u32 -> "BatModeWnd" name pool),
## consistent with t322 never-in-view — that state is itself the closed class.
## OQ-019 note added to the row (strict-close: row STAYS OPEN — no live
## SELECT store ever witnessed; this is a cited-dead-route closure). Every
## OQ-019 capture route now cited-dead: t319/t320 pump, t322 mouse, t323
## activation, t324 class-table. NO LEDGER ROW CLOSED (strict-close).
## Sitting check negative (tail-seek newest turn 1086 == corpus). Production
## :9 (pid 1957) untouched. NEXT = t329 OQ-019 DISPOSITION PACKET (its
## condition "only if t324 landed NEGATIVE-ABSOLUTE" is met; drafts only,
## row closes on USER ruling).

## LANDED t323 (2026-11-06, session 32) — OFFLINE ACTIVATION DECODE: NO
## IN-SESSION TRIGGER EXISTS; OQ-019 SELECT/DESTINATION RESIDUES =
## UNREACHABLE-BY-CAPTURE (t323 amendment binding).
Zero-capture offline decode (work/t91_code_disasm.txt + work/ascend_payload.bin
verbatim; full evidence docs/re/_wip_t323.md S0-S6 + ships.md S49 +
REFUTED-ROUTES t323 amendment). Key measurements: (1) STATE line = state-
RECORD table at load (14B records rect/flags@+0xa/size@+0xc; loader fn
0x31d58, sizing fn 0x32000 value*5+0x14); runtime state WORD [win+0xb1],
count [win+0xaf]. (2) COMPLETE [win+0xb1] writer census 14 sites, all
classified: constructors fn 0x31c54(=0xffff)/0x3377c/0x33d08/0x33c34
(=strlen(name)-1); char-cycler fn 0x339a4 (unreachable for BatModeWnd, no
char handler t296 S5+t321); fn 0x364d2 writes the TABLE not a window; the
ONLY runtime switcher fn 0x31f30 (store @0x31faf) <- EXCLUSIVELY {0x321ad,
0x3221b} inside fn 0x32100 (state-rect-click msgs 0..8, table cs:[0x1d524])
which is NOT in the cited BATMODE table (t296) — sole static reference
0x603ea proven a MISALIGNED jump-table byte false positive. (3) All three
fn 0x2351c callers (0x21530 boot-gated fn 0x78283("resume.gam"), 0x24f96,
0x52a76) pass the "BatModeWnd" pool imm (0x2bf7 VERIFIED) as a DEAD assert
arg (overwritten @0x23558; body = layout bookkeeping ds:0x48c44 +
[wmgr+0x32dda]); fn 0x528ec@0x52a76 result unused; fn 0x156d4 (BATCTRL,
imm 0x5e="BatModeWnd" VERIFIED) stores result UNREAD, resets BatListWnd
(imm 0x77) state table instead (fn 0x32c5c = viewport realloc, not
deactivation). (4) fn 0x1d7dc = repaint/teardown, fn 0x1be10 = cursor
chooser (ds:0x7d35e key) — t322 candidates retired. (5) msg 0x53/0x50
re-probe inside candidate set: none (fn 0x32100 covers 0..8). DISPOSITION:
OQ-019 select/destination = UNREACHABLE-BY-CAPTURE (law stands static-cited
t296 S5 + t321 S1-S4); t322 armed-zero explained as design. NO LEDGER ROW
CLOSED (strict-close: no live store witnessed; the narrowed negative is the
datum; row scope now = t324 RAM-table re-open check + different-sitting
witness only). Sitting check: 200MB tail max turn 1086 == t319..t322's (no
new play; r1_t85g_sitting.py not run). Production :9 (pid 1957) untouched;
gate 0, audits OK.

## LANDED t322 (2026-11-06, session 31) — BATCON CLICK-ROAD LEGS ARMED LIVE
## FIRST TIME: BatModeWnd RECEIVES ZERO MSGS IN-VIEW (branch (b)); THE MOUSE
## ROAD IS DEAD IN-CAPTURE, BLOCKER = WINDOW ACTIVATION.
LIVE capture run work/r1/t299-leg-20261106-055549 rc=0 attempt-1 (loop
short-circuited; legs {batmode_dead, fn1b91c_entry NEW, w43508_1b5e6 NEW,
w43508_1baa7 NEW} + btn_hdlr; scripts/r322_relaunch.sh + scripts/r322_analyze.py
NEW; r299_leg_session.py LEGS +3, bytes payload-verified; battery = t298-shape:
pre-turn 1086->1087, fleet open rails=188, rowjump, sprite 48x151, planet
439x331, NEXTTURN, holds). Measurements (full: docs/re/_wip_t322.md S0-S6 +
ships.md S48 + REFUTED-ROUTES t322 amendment binding): pty-whole-log-census
{batmode_dead:0, fn1b91c_entry:0, w43508_1b5e6:0, w43508_1baa7:0, btn_hdlr:3};
census-ctl MATCH=True; banked btn stops sprite->'PLIND' msg8 / planet->'Cancel'
msg4 (EVENTWIN popup ate it — harness defect banked S5) / nextturn->'PLSQUARE'
msg8; sel43510=0 9/9; DAT_43504 'Icarus' constant; DAT_43508 churn
0x26fe77->0x26f00d writer-less (t298-C law re-observed). DECISION TREE: branch
(b) — BatModeWnd composition-shielded at campaign/system map (windows.txt line
1178 STATE 1 16 never active in captured sessions; t306 entry-zero = second
independent witness). The t321(3) harness blind spot is CLOSED as a blind spot:
the mouse road was finally tested and is dead. NO LEDGER ROW CLOSED
(strict-close: no live store witnessed — the negative is the datum). t323
offline activation decode designed in NEXT ACTION above (zero capture; capture
ONLY after it names an activator). Sitting check: 200MB tail max turn 1086 ==
t319/t320/t321's (no new play; r1_t85g_sitting.py not run). Production :9
(pid 1957) untouched; gate 0, audits OK.

## LANDED t321 (2026-11-06, session 30) — fn 0x51cc4 FULLY DECODED: msg 4
## AND msg 0xc ARE DEFAULT-HANDLED (fn 0x336b4, ZERO DAT STORES); THE
## BATCON WRITER LEGS 0x1b5e6/0x1baa7 WERE NEVER ARMED IN ANY CAPTURE.
Offline decode iteration (zero capture; work/t91_code_disasm.txt verbatim,
every address cited in docs/re/_wip_t321.md S0-S7 + ships.md S47 +
REFUTED-ROUTES t321 amendment binding). Key measurements: (1) fn 0x51cc4
dispatch — cmp dx,2 @0x51ce5 (jb 0x5206f -> msg-1 gate 0x51d29; jbe 0x51f0c
-> msg-2 sets [win+0xaf]=[[rec]+0x8cd]), cmp dx,0x1c01 @0x51cf5 je 0x51f3b,
EVERYTHING ELSE (4, 0xc, ...) falls through 0x51d00 -> tail-call fn 0x336b4:
NO msg-4/0xc branch EXISTS. (2) fn 0x336b4 full tree (0x30f55/0x30de2/
0x30f46/0x30dbb/0x30dd2/0x30fa9/0x30f26): msg 4|5 -> 0x30e0e rect hit-test
-> ring post OR registry dispatch fn 0x56ca4(edx=[win+0x63]); msg 0xc ->
0x30edc rect hit-test -> ring post fn 0x56ad4(code 5, ebx=&[win+0x4f]) ONLY;
ZERO stores to ds:0x43508/0x43504 anywhere in fn 0x336b4. (3) 0x1c01
handler 0x51f3b: fn 0x32fa4 accessor; ecx==5 popup leg; ecx!=5 -> 0x52059
u8 [rec+0x58]-1 jump table cs:[0x3d100] (FILE bytes verified unrelocated
garbage; RAM instance {0x51fb5 x3, 0x51ff6, 0x52037} t313 S8 stands) ->
0x51fc2 DAT_43508 / 0x52003 DAT_43504 / 0x52037 code-3 post. (4) WRITER
CENSUS re-confirmed literal-a3 (5+5) + 0x55bcc 89 15 variant; fn 0x1b91c
re-verified byte-for-byte vs t296 S5 (kind-2 arm gate [ship+0x54]sar16==
ds:0x7458e + [ship+0x88]>0; 0x1baa7 publish iff stored-equal + mode ch==0).
(5) msg-0x50 SENDER HUNT CLOSED image-wide: 3 `mov edx,0x50` sites, all
non-msg (0x1519d nullified by sub edx,eax @0x151a2; 0x3a9e7 -> fn 0x2fb38
103-caller generic; 0x71af3 -> fn 0x782be); sole publish-block entry jbe
0x1b7d7 (cmp dx,0x50 @0x1b7cd) — t296 re-confirmed. (6) HARNESS BLIND-SPOT:
r299_leg_session.py LEGS dict (lines 224-231) = w43504_{28ec2,28ef6,36b01,
52003,55d35} + w43508_{51a8e,51fc2,55bbd}; 0x1b5e6/0x1baa7 never armed
t307..t320 (t306 armed 0x1b71f/0x1ba39 effect-stores, not the DAT sites) —
the mouse road was NEVER live-tested. (7) t297 law re-read: 0x1b070 router
is INTERNAL to fn 0x1aef8, not a global router. NO LEDGER ROW CLOSED
(strict-close: offline decode + re-verification only, no live store
witnessed). t322 designed in NEXT ACTION above. Sitting check: 200MB tail
max turn 1086 == t319/t320's (no new play; r1_t85g_sitting.py not run).
Production :9 (pid 1957) untouched; gate 0, audits OK.

## LANDED t320 (2026-11-06, session 29) — THE MOUSE-ACTIVE POSTER-PASS RUN:
## 27/27 POSTER FIRES, ALL MSG 4. THE CLICK-PULSE LEVER IS DEAD; ds:0x484ac
## IS THE BIOS BUTTON-HELD WORD, NOT A GENERIC MOUSE-ACTIVE FLAG.
LIVE capture run work/r1/t299-leg-20261106-041522 rc=0 attempt-1 (loop
short-circuited; legs {pump_entry_56b5c} ONLY + proven --shipclick 4 + NEW
--pulse-clicks 30 + standard tail; scripts/r320_relaunch.sh NEW;
r299_leg_session.py +--pulse-clicks, pulse sent only in quiet census
iterations, never mid bank cascade). Measurements (full: docs/re/_wip_t320.md
S8-S11 + ships.md S46 + REFUTED-ROUTES t320 amendment binding):
pty-whole-log-census pump=27; EVERY banked stop edx=0x4 (msg 4),
esi=eax=0x2bc35c, edi=0xffffffff, ret0 file 0x54aca = POSTER 0x54ac5,
esp_p8=0; caller histogram 27/27 POSTER; 0x1c01/0x1c02 absent all stops; DAT
oracles unmoved. Baseline windows banked 0 (idle conjunction law holds) —
but under click traffic the poster block ran 27x in 18 min vs 1x in 28 min
(t319): the t319 "rare" reading is CORRECTED to click-traffic-driven, and
484dc=-1 PERSISTS after traffic (control_nextturn windows fired 3x pulse-
free). Save census: 19/20 gate-zero, 1/20 froze the entry conjunction
(484d0=1, 484dc=-1) — save axis corroborates; saves stay blind to
484ac/24da4. STATIC (t91_code_disasm 24853-24866 verbatim): fn 0x2a5f0 =
BIOS int 16h AH=2 poll; 484ac=-1 iff left/right button HELD at poll, else 0
next pass — so msg 0xc needs a HELD button across the poster pass; 50-ms
pulses (cadence eaten to ~20 s by bank cascades) cannot cover it. Host laws
re-confirmed: xdotool ABSENT; SDL2 rejects synthetic MotionNotify (xsend.c
header) — motion-shaped levers dead here. NO LEDGER ROW CLOSED strict-close
(no msg-0xc stop, no live store witnessed) — t321 offline fn 0x51cc4 msg-4/
0xc branch decode designed above. Sitting check negative (no play past
t1086); production :9 (pid 1957) untouched; gate 0, audits OK.

## LANDED t319 (2026-11-06, session 28) — THE POSTER ROAD FIRED LIVE: CALL
## SITE 0x54ac5, MSG 4. THE THREE-WAY QUESTION RESOLVED (GATE-NEVER-EQUAL)
## AND THE DISCRIMINATOR NAMED: [core+0x24da4] = fn 0x54650's MOUSE-ACTIVE FLAG.
Run work/r1/t299-leg-20261106-030727 (attempt-1 WON the BREAK lottery,
SESSION END 03:35:15 rc=0, 108 hits; loop short-circuited per law).
docs/re/_wip_t319.md S0-S6 + ships.md S45 + REFUTED-ROUTES t319 amendment
binding; scripts/r319_{relaunch,analyze,gate_read}.py NEW;
r299_leg_session.py LEGS +3 (pump_entry_56b5c/p54a47/p54a88, bytes
payload-verified). Key measurements: pty-whole-log-census {pump_entry:1,
p54a47:0, p54a88:1, s2_56c74:1, s2_56cda:106}; banked EV stop 03:19:09
tag=post-rearm (6 s after gutter click y=453, inside its armed window):
edx=0x4 MSG-4, esi=eax=0x2bc35c core obj, edi=0xffffffff (=[core+0x24da8]
set at 0x549de), ret0 file 0x54aca = E8 site 0x54ac5 THE POSTER, esp_p8=0
(the msg-4 poster form 0x54ab0 verbatim); p54a88/s2_56c74 counts are
re-arm-gap pty renders (t305 law, contexts verified verbatim this session).
s2_56cda: 102x msg 0x3b COSMOSWnd + 4x msg 8 STATSHIPLST gutter (t317
VERBATIM 3rd reproduction) + 1x msg 0x193 self-send. 0x1c01/0x1c02 literal
absent every banked stop; DAT_43508/43504 oracles unmoved all phases — the
msg-4 poster is NOT the destination road. Static: block-entry conjunction
ds:0x484dc==-1 AND ds:0x484d0!=0 AND [core+0x24da8]==-1 (recorder fn 0x2a7a4
sets -1 on position change); writer census of [core+0x24da4] = 0x546a5 (set
-1 iff ds:0x484ac!=0) / 0x546d0 (reset) / 0x54532 / 0x54b10 — msg 0xc needs
mouse-active SAME pass; ds:0x484a4=0 idle (equal road needs -1 too).
r319_gate_read.py cross-checks t318 oracle gate_484ec=0x1ff EXACT; save
census (20 saves) shows all four flags 0 — saves are save-BLIND to transient
per-pass flags (t260 cadence law), NOT evidence against the mechanism. NO
LEDGER ROW CLOSED strict-close (no live store witnessed) — t320 mouse-active
poster-pass run designed in NEXT ACTION above. Sitting check: playcap newest
turn=1086 unchanged (8GB tail re-checked this session; writer idle) —
r1_t85g_sitting.py not run. Production :9 (pid 1957) untouched; gate 0,
audits OK.

## LANDED t318 (2026-11-06, session 27) — THE BROADCAST-PUMP DISPATCH
## 0x56c74 IS COLD LIVE: NO MSG ID OF ANY KIND REACHED FLEETWND (2ND TIME);
## THE NAMED BLOCKER IS NOW THE POSTER GATE.
Run work/r1/t299-leg-20261106-021602 (attempt-1 lost the BREAK lottery;
attempt-2 rc=0, SESSION END 02:33:42, 9 census windows, 26 stops; relaunch
short-circuited per law). docs/re/_wip_t318.md S0-S6 + ships.md S44 +
REFUTED-ROUTES t318 amendment binding; scripts/r318_relaunch.sh +
r318_analyze.py NEW; r299_leg_session.py bank_stop esp dump widened 8->16 B
(esp_p8/esp_p12 banked — pump dispatch carries msg=[esp+8] BEFORE the
return push; unexercised, harmless, 26/26 stops banked). Key measurements:
pty-whole-log-census s2_56c74=0 | s2_56cda=26 | fn51cc4_entry=0 |
w43508/w43504=0 | btn_hdlr=1; s2_56cda = 18x msg 0x3b COSMOSWnd + 4x msg 8
STATSHIPLST at x=620 gutter clicks (t317 VERBATIM: edi=edx=0x8, ebx=620,
baseline 0) + msg 8/6 PLIND + 2x msg 8 PLANETALLOC; 0x1c01/0x1c02 literal
absent from every banked reg/stack; gate guest 0x600058=0 datum 0;
DAT_43508/43504 unmoved across all four click pairs; mode4226 0x12/0x11/0x1
per phase; gate_484ec=0x1ff. Static: poster block re-read verbatim
(disasm 77195-77245) — msg-4-vs-0xc gated by cmp edi,ds:0x484a4 @0x54a3f
then cmp edi,[esi+0x24da4] @0x54a88 + [esi+0x489e]==0; fn 0x56b5c has NINE
E8 callers; t319 leg bytes payload-verified. SCOPE LAW: legs deleted
between windows/re-arm gaps -> zero means "nothing observable delivered",
NOT "fn 0x56b5c never called" (t319 separates). NO LEDGER ROW CLOSED
strict-close (no live store witnessed) — t319 designed in NEXT ACTION
above. Sitting check: playcap newest turn=1086 (writer alive pid 1979, no
play past t1255) — r1_t85g_sitting.py not run. Production :9 (pid 1957)
untouched; gate 0, audits OK.

## LANDED t317 (2026-11-06, session 26) — GUTTER-CLICK LIVE WITNESS:
## VENDOR CLICKS ARRIVE AS MSG 8 ON STATSHIPLST'S OWN ENTRY; NO 0x1c01 EVER
## FIRED; THE msg-0xc/4 INTAKE IS THE BROADCAST PUMP fn 0x56b5c (s2_56c74).
## Adopted the killed session's in-flight capture (run
## work/r1/t299-leg-20261106-012002 rc=0, SESSION END 01:46:57, 96 stops, 9
## census windows; --shipclick phase + r317_relaunch.sh + r317_gate_probe.py
## were its uncommitted work, committed here). docs/re/_wip_t317.md S0-S8 +
## ships.md S43 + REFUTED-ROUTES t317 amendment binding. Key measurements:
## 4/4 clicks x=620 (strip 632-28=604 verified saves [w+0xb3]=-1) -> EXACTLY
## one s2_56cda stop each, edi=edx=0x8, eax=0xfe7ac0 NAME='STATSHIPLST',
## ebx=620/ecx=ebp=Y verbatim, baseline 0; WHOLE-LOG fn51cc4_entry=0,
## w43508/w43504=0, btn_hdlr=0; gate 0x600058=0 datum 0 x4; oracles unmoved.
## t316 chain intake LIVE-REFUTED (msg 8 -> fn 0x33058 bookkeeping; gutter
## sub-branch = self-send 0x193 + clearers fn 0x56730/fn 0x56434, decoded).
## fn 0x56b5c pump decoded (mask table obj+0x3068 stride 0x8e, dispatch
## 0x56c74, suppression ds:0xa2024, posters 0x54aa9/0x54ab2 off click record
## ds:0x484ec). [w+0x4f] direct-store census CLOSED (sole movb $0 @0x30bdb).
## NO LEDGER ROW CLOSED strict-close (no live store witnessed). t318 designed
## in NEXT ACTION above. Sitting check: newest playcap line turn=1086 == t316's
## newest (50MB tail: 2109 turn-lines all turn 1086; writer alive, no play
## past t1255 per t316's 1.5GB check) — r1_t85g_sitting.py not run. Production :9
## (pid 1957) untouched; gate 0, audits OK.

## LANDED t316 (2026-11-06, session 25) — THE DYNAMIC 0x1c01 EMIT TARGETS
## FLEETWND BY SLOT ID: CHAIN CONTINUOUS STATICALLY; REGISTRY PROVEN
## SAVE-BLIND (685/685) — LIVE WITNESS IS THE ONLY EVIDENCE LEFT.
## docs/re/_wip_t316.md S0-S5 + ships.md S42 + REFUTED-ROUTES t316 amendment
## binding; ZERO capture (corpus = all t299-leg-*/save + playcap/save, 685
## saves, zero read failures); scripts/r316_registry_dump.py +
## r316_registry_probe.py NEW (offline). Key measurements: emit-builder fn
## 0x33320 (sole `bb 01 1c 00 00` 0x33374; span [0x33320,0x33456)) has ONE E8
## caller 0x32778 inside STATSHIPLST slot-2 fn 0x32664 in-rect msg-0xc branch;
## road selector global 0x9f100 (runtime abs 0x2e1100) == 0 (3 saves); target
## edx=[w+0x63]==95 in 685/685; rec+0x41 = registry slot-id PROVEN (ctor fn
## 0x3264c `call fn 0x5712c; mov %eax,0x41(%ebx)`); FLEETWND rec [+0x41]==95;
## fn 0x56ca4 = registry dispatch (win=[obj+edx*12+4], call [win+0xa7+8]);
## registration fn 0x5712c = sole 0x12345678 writer (0x57173), 4 callers all
## obj 0x7a35c; rects STATSHIPLST (7,46,632,472) FLEETWND (7,7,632,472).
## NEGATIVES: [obj+0x4226]==0 AND [obj+0x3000]==0 in 685/685 (u32+u16); zero
## RAM u32 pointers to FLEETWND rec (3 rec-ptr hits total TOGGRID/'I');
## t315 S6 mode4226 0x23c7969f CORRECTED (cmpl disp32 mis-parse, true 0).
## NO LEDGER ROW CLOSED strict-close (no live store witnessed; static chain +
## addressing law only). OQ-019 residue = ONE live question -> t317 capture
## designed in NEXT ACTION above. Sitting check: no new play (1.5GB tail
## 60739 turn-lines max 1255 == t315's; newest line turn=1086 wall 23:41
## restored state); r1_t85g_sitting.py not run. Production :9 (pid 1957)
## untouched; gate 0, audits OK.

## LANDED t315 (2026-11-05, session 24) — DIGIT-HANDLER WINDOW NAMED:
## 'LOADSCREEN' — THE KEY->0x1c01 ROUTE IS A MENU MECHANISM, DEAD BY
## CONSTRUCTION FOR IN-GAME SELECT. docs/re/_wip_t315.md S0-S6 + ships.md S41
## + REFUTED-ROUTES t315 amendment binding; ZERO capture (save dirs of runs
## t299-leg-20261105-212402 + 192246); scripts/r315_handler_scan.py NEW
## (grid scan + B/P0 re-derivation from code-pattern hits). Key measurements:
## fn containing 0x35696 = fn 0x354f8 (prologue 56 57 55 81 ec 44 01 unique
## 2-site, sibling 0x1cf23 zero RAM hits; ZERO E8 callers); grid base RAM
## 0x247da8 slot 2, cp 0x247d20, magic rec 0xfd705c NAME='LOADSCREEN' 3/3
## saves both runs (control fn 0x51834 exactly-1 @0x248050 5th reproduction;
## fn 0x51cc4 exactly-1 @0x248038); payload pool corroborates loadwin.cpp
## ('loadscr','LOADLIST','%02d.sav'). Whole-payload 0x1c01 literal census
## CLOSED at 5 sites incl. one E8-operand false positive (0x1756b); second
## receiver fn 0x16420 grid-named 'BatControlWnd' (slot 3, cp 0x247850);
## fn 0x16754 / fn 0x156d7 zero grid hits (not class slots). GATE CHAIN
## resolved exact (0x51f3b + fn 0x32fa4 + 0x52059 verbatim) AND MEASURED:
## FLEETWND gate byte = GUEST 0x600058 == 0, datum 0x600059..c == 0, 212/212
## valid-chain saves (221 saves [win+0xab]==0 -> accessor error path); record
## block 0x600000..0x600078 all-zero. DAT_7e582 runtime abs 0x2c0582 (read
## from patched code bytes) == 0 in 433/433 saves. Self-send structure: fn
## 0x354f8 IS both digit sender (0x356a5) and 0x1c01 receiver (0x356b9).
## NO LEDGER ROW CLOSED strict-close (no live store witnessed; gate byte
## again never evaluated live). OQ-019 residue: emit-path hunt (t316, designed
## above), then watchpoint 0x600058 or FLEET-rect interior click. Sitting
## check: no new play (1.5GB tail 60740 turn-lines max 1255 == t313's; newest
## lines 50-52.sav t=1086); r1_t85g_sitting.py not run. Production :9 (pid
## 1957) untouched. Gate 0, audits OK.

## LANDED t314 (2026-11-05, session 23) — FLEETWND-FOCUS LIVE TEST VALID +
## NEGATIVE: FLEETWND RECEIVES NO KEYBOARD MSG AT ALL. docs/re/_wip_t314.md
## S0-S7 + ships.md S40 + REFUTED-ROUTES t314 amendment; runs
## t299-leg-20261105-{210255 (attempt 2, focus DEFECT), 212402 (attempt 1,
## VALID)} both rc=0; scripts/r314_relaunch.sh NEW + r299_leg_session.py patch
## (NEW leg fn51cc4_entry=0x51CC4 entry bytes payload-verified; NEW
## --fleet-keys phase with rails+popup double reguard). Key measurements:
## run-1 defect law (rowjump CLOSES FLEET, rails 188->0); run-2 whole-log
## {fn51cc4_entry:0, w43508_51fc2:0, w43504_52003:0, btn_hdlr:4} ctl MATCH=True
## with rails=188 verified at arm; single fleet_keys stop btn_hdlr
## win='STATSHIPLST' edx=0x3 ret0 file 0x32943 (inside STATSHIPLST slot-2 fn,
## cp 0x247c70 RAM-read); sender branch 0x35675..0x356a5 objdump-verbatim
## ([ebp+0xaf] digit-max gate, call [esi+8] on own window [ebp]); fn 0x32fa4 =
## 8-stride accessor [[win]+0xc7+idx*8] (9 E8 callers incl. STATUSWND path
## 0x51a73); STATSHIPLST[+0x58]==0 in 40/40 saves; [r+0x58] store census ZERO
## (file blind, computed offsets). GAP banked: s2_356a5 NOT armed run 2 ->
## sender-zero-under-FLEET-focus = extrapolation. NO LEDGER ROW CLOSED
## (strict-close: no live store witnessed). OQ-019 residue RE-SCOPES: name the
## digit-handler window offline (t315, designed above), then state-byte
## watchpoint route. Sitting check: no new play (400MB window max turn 1150 <
## 1255; newest lines t=1086); r1_t85g_sitting.py not run. Production :9
## (pid 1957) untouched; scratch dosbox killed by recorded PID every window.
## Gate 0, audits OK.

## LANDED t313 (2026-11-05, session 22) — OFFLINE CALLER HUNT LANDED: THE
## t312 WRITERS BELONG TO FLEETWND (msg-0x1c01 continuation via a RUNTIME
## STATE JUMP TABLE); CLASS-GRID LAW FIXED (stride 6, cp=base-0x88,
## dispatcher 0x30d37 call [cp+0xc]; t310 slot-4 was an 8-byte-shifted read).
docs/re/_wip_t313.md S0-S8, ships.md S39, REFUTED-ROUTES t313 amendment; ZERO
capture (save dir of run t299-leg-20261105-192246: 41/50/58.savs); scripts
r313_class_scan.py / r313_grid_names.py / r313_name_entries.py /
r313_name_b.py / r313_fleetwnd_map.py / r313_writer_callers.py /
r313_handler_chain.py (all offline, re-runnable). Key measurements: control
0x51834+P0 exactly 1 hit @0x248050 (4th reproduction); 0x51b68+P0 ZERO (mid-
body datum); FLEETWND cp 0x247fa8 named via magic rec 0xfe7a90; full window
census 115 recs/31 classes; je@0x51cfa->0x51f3b + jne@0x51f57->0x52059 both
raw-verified exact; RAM table 0x211188 {0x51fb5 x3, 0x51ff6, 0x52037} whole-
RAM unique + file 0x3d100 NOT pointers (file blindness proven again). NO
LEDGER ROW CLOSED (strict-close: mechanism named offline, no live store
witnessed). OQ-019 residue now = ONE live question: does msg 0x1c01 reach
FLEETWND under FLEET-window focus (t314). Sitting check: no new play since
t312 (tail 200MB + 1.5GB windows max turn 1255, newest lines t=1086 restored
state) — r1_t85g_sitting.py not run. Gate 0, audits OK.

## LANDED t312 (2026-11-05, session 21) — ORDER-PLACEMENT WRITER RUN: fn
## 0x51b68 DESTINATION-WRITER PAIR UNREACHED WHOLE-LOG (branch (b)); SPRITE-
## PIXEL CLICK DOES NOT SELECT (sel43510=0 every snapshot, 4th-run
## reproduction); BOTH msg-0x1c01 SENDERS MEASURED DEAD (s2_356a5 zero despite
## keys reaching 'NEXTTURNCONT'). docs/re/_wip_t312.md S0-S3, ships.md S38,
## REFUTED-ROUTES t312 amendment; run t299-leg-20261105-192246 rc=0 attempt 1
## (whole-log {fn51834_entry:0, w43504_52003:0, w43508_51fc2:0, s2_356a5:0,
## btn_hdlr:4}, census MATCH=True 7/7); scripts/r312_relaunch.sh NEW (zero
## session-script delta — all five legs already in LEGS). NO LEDGER ROW CLOSED
## (strict-close): OQ-019 residue collapses from two holes to ONE (per-ship
## select drives everything; no selection = no order = no writer). Gate 0,
## audits OK.

## LANDED t311 (2026-11-05, session 20) — STATUSWND RECEIVES NO MSG TRAFFIC
## AT ALL (ENTRY-LEG MEASURED, branch (c)); t310 FOCUS DEFECT FIXED
### (bare-map keys hit btn_hdlr 'NEXTTURNCONT', not 'Cancel'); 0x1c01-into-
### STATUSWND -> REFUTED-ROUTES; entry-leg-as-leg[0] census-ctl law
### (MATCH=True 7/7). docs/re/_wip_t311.md S0-S4, ships.md S37,
### REFUTED-ROUTES t311 amendment; run t299-leg-20261105-182822 rc=0 attempt
### 1 (whole-log {fn51834_entry:0, w43508_51a8e:0, w51ac9:0, s2_1616f:0,
### btn_hdlr:4}); scripts: LEGS+fn51834_entry, digit block MOVED above
### open_fleet w/ assert_on_map + post-arm popup reguard (old in-place block
### deleted), r311_relaunch.sh. NO LEDGER ROW CLOSED (strict-close): OQ-019
### residue = destination-widget fire (next: fn 0x51b68 pair + order
### choreography t312) + per-ship select. Gate 0, audits OK.

## LANDED t310 (2026-11-05, session 19) — DESTINATION WRITER'S CLASS NAMED
## (STATUSWND), MSG-0x1c01 PATH FULLY MAPPED, 0x484ec GATE MEASURED = MOUSE X;
## writer legs zero (honest negative, control alive); class-table RAM-scan
## route executed FIRST TIME (file scan blindness confirmed). docs/re/
## _wip_t310.md S0-S5, ships.md S36, REFUTED-ROUTES t310 amendment; run
## t299-leg-20261105-173627 rc=0 attempt 2 (attempt 1 BREAK-lottery loss);
## scripts/r310_relaunch.sh + r299_leg_session.py t310 patch (w51ac9,
## s2_1616f legs; --pre-turn, --digit-keys phases; oracle gate_7e5aa/7e89e/
## 484ec). NO LEDGER ROW CLOSED (strict-close): OQ-019 residue = destination-
## widget fire (STATUSWND-focus composition untested) + per-ship select.
## Honest negatives: 5 writer/relay legs 0 whole-log x battery with btn_hdlr
## x4 alive; digit keys routed to the 'Cancel' popup (focus defect banked);
## fn 0x51834 received NOTHING on the order battery. Gate 0, audits OK.

## LANDED t309 (2026-11-05, session 18) — TWO-RING MAP + RING DORMANCY
### MEASURED (selection is RENDER-DIRECT; 'consumer timing' was the wrong
### question); DAT WRITER INVENTORY COMPLETED (a3 + 89/15 sweeps: 6+6, the
### t296 census missed 0x51ac9/0x55bcc); objdump -D fallback + jump-resolver
### laws fixed. docs/re/_wip_t309.md S0-S3, ships.md S35/S35b, REFUTED-ROUTES
### t309 amendment; run t299-leg-20261105-161711 rc=0 attempt 2 (attempt 1 =
### BREAK-lottery loss); scripts/r290_disasm.py -D fix, r299_leg_session.py t309
### patch (cons_entry/ringB_post/ringB_w10_{41c17,499e0}/ringA_resolver legs,
### oracle gate snapshot mode4226/ring counters/pump660c/guard, HOT HOLD
### windows), r309_ring_writer_census.py, r309_relaunch.sh. Star witness delta
### reproduced 4th time (Icarus->Vega at (182,284), diff 94712). NO LEDGER ROW
### CLOSED (strict-close): OQ-019 residue = per-ship selection writer +
### msg-0x50 destination widget (now re-scoped to fn 0x51b68/0x51834 live
### windows -> t310). Honest negatives: consumer/post legs all zero (structural
### dormancy, PROVEN for ring-B; ring-A post body proven-not-run via idx
### snapshots); turn advance UNRESOLVED (10 s sav granularity); ringA_resolver
### control vacuous-by-construction at idle (own gate needs [core+0x44aa]>>16>0,
### unincrementable at idle). Gate 0, audits OK.

## LANDED t308 (2026-11-05, session 17) — DAT_43504 STAR WRITER FULLY
### WITNESSED WITH A REAL DELTA (Icarus->Vega, EAX=0x255BC5, fire 3/3);
### DAT-BASE QUESTION CLOSED (sav member = linear+0x88; oracle always right;
### t307 0xff datum VOID); GREEN-ANNULUS pip law (bright-dot law REFUTED).
### docs/re/_wip_t308.md S0-S8, ships.md S34; runs t299-leg-20261105-{140250,
### 143815} both rc=0 attempt 1; scripts/r308_relaunch.sh + r299_leg_session.py
### t308 patches (name-bearing sel_oracle + alt_285504, witness-delta early
### break, green-annulus candidate law). NO LEDGER ROW CLOSED (strict-close):
### OQ-019 residue = per-ship selection writer (no kind-4 owner-0 ship at
### t=1086) + msg-0x50 destination widget + NEW sharpened hole: ring-0x10
### consumer family never observed running -> t309. Honest negatives: battery 1
### produced NO delta (pip law defect, fixed same session); DAT_43508 legs
### zero x3 runs; alt_285504 constant 0xff (void variable, identity unnamed).
### Gate 0, audits OK.

## LANDED t307 (2026-11-05, session 16) — FIRST LIVE FIRE AT A STORE-CENSUS
### MEMBER: w43504_28ec2 EAX=0x256825 (Icarus star) ON AN ENTERED STAR CLICK;
### SELF-RELOCATION LAW (+0x242000 code-RAM data imm rebases); ORACLE-BASE
### QUESTION OPENED. docs/re/_wip_t307.md S0-S6, ships.md S33; run
### work/r1/t299-leg-20261105-112854->-112859 (rc=0 attempt 1), scripts/
### r307_relaunch.sh + r299_leg_session.py t307 patch (8 w4350*/w43508_* legs,
### --star-click N galaxy-pip battery, sel_oracle hoisted, star-mode rc law =
### ran-windows count).
MEASURED: (1) pty whole-log census {w43504_28ec2:1, w43504_28ef6/36b01/52003/
55d35:0, w43508_51a8e/51fc2/55bbd:0, btn_hdlr:5} — the leg instrument CAN
catch the writers, zeros are context; (2) THE FIRE: HL render byte 34151
IP=E8312=P0+0x28ec2 EAX=0256825, between REQ 111 RUN (resume after star1
(238,282) click's btn_hdlr msg-4 stop; click ENTERED Icarus system — screen
diff 94504, vision-verified) and REQ 112 BREAK; follow-on bytes match disasm
0x28ec7..0x28ed8 verbatim (ring post 0x10); writer = fn 0x28e70 COSMOS
fallback star-select (sole caller 0x27332; gates empty [win+0x582],
ds:0x7e582>>16==1); (3) SELF-RELOCATION LAW (MEMDUMPBIN ctl vs payload): RAM
@P0+0x28ec2 = a3 04 55 28 00, 0x7a35c->0x2bc35c — data immediates rebased
+0x242000 in code; (4) star0 (226,238) diff=488 no-enter, star2 (218,308)
diff=488 no-enter (pip law: nearest bright dot may MISS the hit target; only
star1 entered); NEXTTURN control CLEAN msg 0x7 (no Cancel residue this run).
NO LEDGER ROW CLOSED (strict-close): fire = star-fallback writer, NOT the
per-ship selection writer; oracle delta absent (0x256825 before AND after —
and the oracle address itself now suspect, see NEXT); t307 note on OQ-019.
Gate 0, audits OK.

## LANDED t306 (2026-11-05, session 15) — BATMODE SELECTION SITES NEVER
### REACHED BY MAP CLICKS (cited negative; route REFUTED); writer hunt
### re-scoped to the t296 store census. docs/re/_wip_t306.md S0-S3,
### ships.md S32, REFUTED-ROUTES t306 amendment; run
### work/r1/t299-leg-20261105-101054 (rc=0 attempt 1), scripts/
### r306_relaunch.sh + r299_leg_session.py t306 patch (legs bat_s53/
### bat_mouse/bat_router, --target-kinds, selection oracle pairs).
MEASURED: (1) working sprite click (48,151) -> btn_hdlr msg 0x8 win[esi]
NAME='PLIND', ret0 file 0x3cb8d = DIRECT E8 call 0x336b4 at 0x3cb88 (fn
0x3cb00, a window-family dispatcher with call [ecx+0xc] sibling at 0x3cb6e;
u32 refs to entry ZERO = class-table member); (2) the four t296 batmode sites
{0x1aef8 entry, 0x1b070 router, 0x1b71f + 0x1ba39 effects} fired ZERO whole-log
with positive control ALIVE (btn_hdlr x2, census-ctl MATCH x3, liveness x2) —
entry+router zeros are PRE-GATE, so map clicks never dispatch into the
BatModeWnd handler layer (gating fact t=1086 no kind-4 owner-0 ship is
consistent but not load-bearing); (3) selection oracle pairs
(sel43510/DAT_43504/DAT_43508) moved NOTHING attributable (43504 stable =
Icarus star oracle; 43508 churns without input per t297-A); (4) NEXTTURN
control hit the 'Cancel' record msg 0x4 via pump 0x56c74 this run (t304 modal
pattern; turn-advance witness stands from t305). NO LEDGER ROW CLOSED
(strict-close): OQ-019 selection WRITER unnamed; t306 note on the row; writer
hunt = DAT_43508 {0x51a8e, 0x51fc2, 0x55bbd} + DAT_43504 {0x28ec2, 0x28ef6,
0x36b01, 0x52003, 0x55d35}. Gate 0, audits OK.

## LANDED t305 (2026-11-05, session 14) — NORMAL-CORE ANOMALY RESOLVED =
### INSTRUMENT DEFECT; FirePat LAW (source-pinned); CLICK->DISPATCH MAP
### MEASURED. docs/re/_wip_t305.md S0-S5, dosbox-debugger.md t305 block,
### ships.md S31, REFUTED-ROUTES t305 amendment; runs
### work/r1/t299-leg-20261105-{061737(BREAK-lottery-loss),061825(rc=0)},
### work/r1/t305/ loop, scripts/r305_relaunch.sh.
MEASURED: (1) t304 "normal core banks ZERO stops" was FALSE — stops happened
unbanked (highlighted DrawCode render + prompt-back + autosave gap spanning
armed windows in 051904/052925 re-reads). SOURCE LAW: stop line = unique
PAIR_BLACK_GREEN (ESC[30m ESC[42m, debug.cpp:1586-87) prefix; address token =
full 0160:0021612A form OR leading-zero-stripped SUFFIX of VARIABLE length
('1612A','60C4') — fixed-width regex impossible (first-pass 5-hex fix missed
the 0x56c74 empty-click fire; caught same session). FirePat class (r299_leg_
session.py) = HL-token capture + sig6.endswith(token), len>=4 (last-4 unique
across 35 legs audited), bare t302 fallback with HL-proximity exclusion.
REGRESSION EXACT: 033648 cos_hdlr 41, 052925 s2_56cda 3, 061825 60/20/1.
(2) RUN 061825 rc=0 (attempt 1 lost the BREAK lottery — known flaky, loop
absorbed it): witness 3/3 ret0=0x21612d -> site 0x56cda under CORRECT core.
(3) CLICK->DISPATCH MAP (per-window per-leg, drain applied): baseline pump
0x56cda+cos_hdlr msg 0x3b COSMOSWnd x15/60s; sprite(48,151) 0x56cda x2 msg 0x8
'PLIND' + btn_hdlr; planet(439,331) 0x56cda msg 0x8 'PLANETALLOC' (t304
'Cancel residue' SUPERSEDED for planet); empty(236,200) ONLY site 0x56c74;
NEXTTURN 0x56cda x2 msg 0x8 'PLSQUARE' + btn_hdlr; 20 other slot-2 sites ZERO
everywhere. (4) NO LEDGER ROW CLOSED (strict-close): OQ-019 selection WRITER
still unnamed (msg 0x8 = repaint/dispatch at window records, not the selection
store); t305 note appended to the row. Gate 0, audits OK.

## LANDED t304 (2026-11-05, session 13) — DISPATCH INSTRUCTION NAMED
### (0x56cda call [esi+8]); SPRITE CLICK WALKS THE CLASS MSG LAYER via
### btn_hdlr (t302 negative re-scoped); CORE-CONF LAW: all prior runs ran the
### DYNAMIC core. docs/re/_wip_t304.md S0-S4, dosbox-debugger.md t304 block,
### REFUTED-ROUTES t304 amendment; runs work/r1/t299-leg-20261105-033648
### (rc=0, 45 stops), -043543/-051904/-052925 (site probes), r304_loop killed
### by pid after attempt 1 banked.
MEASURED: (1) CALLER WITNESS (--witness 3 --census combined, single boot):
12/12 witness stops + 41/41 census cos_hdlr stops -> [esp] ret0=0x21612d =
call site file **0x56cda** = ff 56 08 **call [esi+8]** (payload-verified);
generic pump shape: mov esi,[eax+0xa7] (class table), record array
[rec+0x4226]>>0x10, msg id stack-dword sar 0x10. t303 slot-1 zero-fires fully
re-attributed. (2) CENSUS (btn_hdlr armed + close_eventwin pre-arm, 4/4
targets measured, guest alive, turn 1086 held): sprite(48,151) -> btn_hdlr
msg 0x1 NAME='Leave Orbit' via 0x56cda = THE WORKING MAP CLICK DOES EXECUTE
THE CLASS MSG LAYER; planet(439,331)+empty(236,200) -> SAME 'Cancel' record
msg 0x4 via 0x56c74 = modal residue, controls invalid-as-run; control_nextturn
-> btn_hdlr msg 0x8 NAME='PLSQUARE', ret0 file 0x3d391 = direct E8 at 0x3d38f
(btn_hdlr has 51 E8 sites; t303 'ZERO' applied to other legs only).
(3) STATIC whole-image ff/2 decode: 22 slot-2 sites (13 esi, 2 edi, 1 ebx,
6 ebp-disp32 — the prior WIP's mod=01 scan missed the 6); ZERO call [ecx+8].
(4) HARNESS LAWS: `core` is a [cpu] setting; every session conf had it under
[dosbox] = inert = ALL t299..t304 ran dyn core (pty warning verbatim); dynrec
heavy-BP check only at run-loop top (core_dynrec.cpp:268) -> mid-block site
legs cannot fire there; launch() conf FIXED (re-opened [dosbox] keeps
autosave+mcp alive, 051904). NEW ANOMALY: normal core banked ZERO stops even
cos_hdlr (052925, guest alive) — unresolved, gates t305. (5) Instrument:
--witness mode; bank_stop ret_stack guard fix (image END vs size) +
ret0_call_site; census default = 22 s2_* + cos_hdlr + btn_hdlr. NO LEDGER ROW
CLOSED (strict-close): OQ-016, OQ-019 stay open.

## LANDED t303 (2026-11-05, session 12) — MSG-CENSUS: SLOT-1 ROUTER LAW
### REFUTED; MAP-CLICK ENTRY NEITHER cos_hdlr NOR SLOT-1 (cited negative);
### census instrument proven freeze-free.
### docs/re/_wip_t303.md S0-S6, ships.md S30, REFUTED-ROUTES t303 amendment,
### dosbox-debugger.md t303 block; runs work/r1/t299-leg-20261105-{015611,
### 020416} rc=1 x2 identical (attempt 3 killed after reproduction).
MEASURED: (1) CENSUS MODE WORKS (--census: per-click arm_census -> MCP click
-> bank-window -> BPDEL * -> autosave liveness; choreography leg-free between
clicks): 2 full sessions, 10 arm/click/disarm cycles, ZERO freezes — the t302
resume bug is ENGINEERED AROUND. pty_peek (non-consuming) added; census-arm
failure path BPDEL*s before RUN. (2) THE HEADLINE: whole-log pty census
{cos_hdlr:15, disp_26eda:0, disp_30d02:0, disp_7a7eb:0, disp_7aa3e:0,
disp_7b020:0} — msg 0x3b reaches COSMOS slot 2 WITHOUT any `call [ecx+4]`
(site set re-verified verbatim vs payload this session, ff5104 count==5);
t302 run 004605 log independently shows STOP endturn-p1 leg=btn_hdlr at
00:48:21 with router 0160:1F0158 in the 00:48:10 re-arm BPLIST. => t301 S6.2
"every msg walks slot1 0x30d08" REFUTED; slot1==0x30d08-in-tables stands,
universal-dispatcher claim dead. (3) A pixel-PROVEN WORKING sprite click
(48,151; 66717 px; vision-cited modal "Ship 'Sparrowhawk'" Leave Orbit/
Abandon/Cancel) fired NONE of the 6 armed legs in its 45 s window = CITED
negative: map-click entry is not cos_hdlr, not slot-1. (4) INSTRUMENT
DEFECTS (not game): no close_eventwin between census clicks (planet/empty/
NEXTTURN controls swallowed by the modal, 225/207 px); btn_hdlr unarmed so
the NEXTTURN control was unwitnessable by construction; turn stayed 1086
(zipfile 'Memory' B+0x82bb0+0x12e10, all 20 autosaves x2 runs). (5) Static:
indexed ff14 modrm calls ZERO in payload; `mov r32,[r32+0xa7]` 21 sites
(0x14de8..0x14f14 x6 cluster = prime suspect); dialog strings NOT payload
plaintext; E8-callsites of cos_hdlr/btn_hdlr/cos_s3/router/cos_entry ZERO.
NO LEDGER ROW CLOSED (strict-close): OQ-016, OQ-019 stay open.


## LANDED t302 (2026-11-05, session 11) — CLASS-DISPATCH LIVE WITNESS: FULL
### rc=0, DISPATCH LAW CONFIRMED + POSITIVE CONTROL + MAP-CLICK NEGATIVE
### (docs/re/_wip_t302.md S1-S5, ships.md S29, dosbox-debugger.md t302 block;
### runs work/r1/t299-leg-{225819,230758,230846,232811,232859,002540,002628,
### 004605}; pre-fix archives work/r1/t299-pre-{t302fix,rearmfix,dropfix}/).
MEASURED: (1) THREE INSTRUMENT BUGS KILLED: (a) fire-detect pattern
`0160:001E5F84` NEVER matches this build's DrawCode stop render `1E5F84 56
push esi...` (bare 6-hex, run-on) — fixed pattern
`(?<![0-9A-Fa-f])<6hex> [0-9A-F]` regression-tested vs arm/BPLIST/echo lines;
(b) resuming with the FIRED code BP still armed re-stops at the same EIP on
the next dispatch (core_normal.cpp:182 top-of-loop check, C_HEAVY_DEBUG has
no 0xCC patch, BP is non-once) — guest FREEZES; fix = BPDEL fired-index ->
RUN -> liveness by autosave .sav growth -> BREAK -> re-arm -> RUN; (c) a
re-armed HOT leg (periodic msg 0x3b pumps COSMOS slot 2 ~1/s) re-freezes it
again — fix = witnessed-set DROP policy, battery runs leg-light. (2) THE
WITNESS RUN 004605 rc=0: cos_hdlr stop eax=COSMOSWnd-record msg edx=0x3b
(periodic, 3 samples); endturn-p1 btn_hdlr (type-0 table 0x247cb8 slot 2)
eax=NEXTTURN-record edx=0x7 == windows.txt SENDMESSAGE 7 VERBATIM = POSITIVE
CONTROL (working clicks DO execute the class msg layer — t299/t300/t301
zero-fires fully re-attributed, NOT a bypass law); endturn-p2 cos_s3
(COSMOS slot 3) edx=0x0 on the click that advanced t1086->1087. (3) CITED
NEGATIVE: sprite(48,151)/planet(439,331)/empty(236,200) Icarus-view clicks
fire NONE of the 5 un-witnessed legs (cos_entry/cos_s5/btn_entry/router/
batmode_dead; pty census 0 each, live guest throughout) — map-click entry is
not a class-table-slot hit; cos_hdlr itself was DROPPED pre-battery so its
per-click msg is UNMEASURED -> t303 census. (4) relaunch.sh success-tell
tightened (lone early STOP no longer stops the loop; needs SESSION END rc=0
or a click-tagged STOP); tl 1800->3600. NO LEDGER ROW CLOSED (strict-close):
OQ-016 r1, OQ-019 r1/r3 stay open (entry class named, selection WRITER not).

## LANDED t301 (2026-11-04, session 10) — TOGGRID CONTROL-CLICK RAN: CONTROL
INVALID (PIXEL-PROVEN) + WINDOW-CLASS DISPATCH LAW CLOSED OFFLINE
(docs/re/_wip_t301.md, ships.md S28, REFUTED-ROUTES t299 t301-amendment; runs
work/r1/t299-leg-20261104-{213540,214042} + 1 lottery loss). MEASURED:
(1) Battery as assigned: 2 full sessions, 8 legs armed, Icarus view reached,
sprite/planet/empty + TOGGRID(572,418) clicks ALL NOFIRE (session.log rc=0
clicks). (2) CONTROL AUDIT: rect 557,403-587,433 uniq colors=2 mean~0 =
BLACK in the Icarus view (BatModeWnd content rect uniq=222); windows.txt
assigns that SAME rect to TOGSHIPS/COSMOSWnd (sm=58) as to TOGGRID/BatModeWnd
(sm=74) — sibling windows both 7,7-465,472, so the t301 disjunction was VOID
AS RUN (new standing law: pixel-verify any control click). (3) OFFLINE LAW
(run 59.sav, B=0x1bf4d8, P0=0x1bf450): live window records = magic u32
0x12345678 (126 hits; rect@+0x08 == windows.txt VERBATIM; NAME@+0x20; class
table phys @+0xa7); dispatch = `mov ecx,[win+0xa7]; call [ecx+4]` (ff5104 x5,
mov-rm+0xa7 x20); TABLE SLOT 1 == file 0x30d08 in EVERY sampled class table
(batmode/cosmos/btn0/toggle/list); tables: COSMOS [0x26818,_,0x26b34,0x27e80,
_,0x2925c], BTN0 [0x30ad8,_,0x336b4,...], BATCTRL [0x15630,_,0x156d4,0x16420];
installers write table-phys imm32 into +0xa7 (batmode img+0x1abe6/0x1ac21,
cosmos img+0x2683f; static placeholder 0x58 -> RAM +P0). (4) => t299/t300
zero-fires = ARMING FAILURE (wrong class table; the WORKING FLEET/End-Turn
clicks ran btn0 legs nobody armed), NOT a bypass law; the t300 'never reach
the batmode msg layer' claim is DOWNGRADED. (5) r299_leg_session.py RE-ARMED
(cos_*/btn_*/router legs, stop dumps record NAME, --control-click 0, control
dump at router; py_compile OK) — run deferred to t302 (3 sittings budget
spent). NO LEDGER ROW CLOSED (strict-close): OQ-016 r1, OQ-019 r1/r3 open.

## LANDED t300 (2026-11-04, session 9) — HANDLER/ROUTER-ARMED RUN: ATTRIBUTED
ZERO-FIRE NEGATIVE (docs/re/_wip_t299.md S7-S8, ships.md S27 update,
REFUTED-ROUTES t299 entry; runs work/r1/t299-leg-20261104-{205111,205500,
205849}). MEASURED: (1) 8 code BPs armed identical x3 incl. handler ENTRY
0x1aef8 + router 0x1b070; MEMDUMPBIN control MATCH=True (dump laws from
session 8 hold). (2) Attempt-1 full good choreography (t 1086->1087, FLEET
diff 122756, row-93 -> Icarus, sprite (48,151) + planet (439,331) + empty
(236,200) clicked): ZERO fires, pty 'Memory breakpoint' count 0, game never
froze. (3) SAME-SESSION CONTRAST = the attribution: FLEET-button/row-jump/
End-Turn clicks PRODUCED state changes, so synthetic clicks reach the game;
yet none of the 8 batmode msg-layer addresses executed on map clicks.
(4) windows.txt VERBATIM cross-check: BatModeWnd 7,7-465,472 contains every
click point, children all x>=479 (TOGGRID 557,403-587,433 SENDMESSAGE 74) —
no child interception possible. (5) Static: 0x1aef8 AND 0x1b070 have ZERO E8
callsites and ZERO u32 refs in the payload image (batcon 0x1b91c has 2, at
0x1da51c/0x1da62e — enclosing fn NOT found by prologue scan, deferred);
payload INT census CD33 x5 / CD31 x42. (6) EXEC-while-running probe answered
rtt 0.05s -> stopped-oracle INVALID, pty scan is the only stop detector.
(7) FLEET reopen after battery fails — one battery per sitting. NO LEDGER ROW
CLOSED (strict-close): OQ-016 r1, OQ-019 r1/r3 stay open; t298's 'not
refuted' is now a CITED negative (REFUTED-ROUTES t299 section). Control-click
probe built (--control-click default 1) -> t301.

## LANDED t299 (2026-11-04, session 8) — DEBUGGER LEG WITNESS: instrument
PROVEN, evidence PARTIAL (honest negative x3; docs/re/_wip_t299.md S1-S7 +
ships.md S27; runs t299-leg-{195933-crash,201408,201757,202146}; scripts/
r299_leg_session.py + r299_relaunch.sh NEW). MEASURED: (1) code-BREAKPOINT
flow works on dosbox-x-dbg headless: BREAK lottery at title (settle 45) ->
RUN -> campaign enter -> post-load BREAK catches pmode window (cs=0160, EIP
in-image) -> arm N legs -> BPLIST confirms -> RUN -> battery; C_HEAVY_DEBUG
adds no 0xCC, check runs every instruction. (2) ARMING IS MODE-BOUND:
GetAddress(seg,off) evaluates AT arm time (seg==CS -> SegPhys(cs)+off) — arm
at the real-mode title bakes a wrong location; gate = stopped + live CS +
P0<=EIP<P0+0x8CC83. (3) AddBreakpoint does NOT Activate (only RUN does) —
`EXEC BP` while running is inert: arm-while-stopped, RUN once, attribute by
EIP. (4) EXEC answers WHILE RUNNING (rtt 0.05 s) — a reply does NOT imply
stopped; fire detection = pty code-view line '0160:<lin8>'. (5) MEMDUMPBIN:
'/' in filename = division -> whole-command reject; ParseCommand UPPERCASES
the filename; length arg is hex; 0000: selector dumps GDT-slot-0 JUNK (use
CS:). (6) Offline re-confirmation: handler physical P0+0x1aef8 has EXACTLY
ONE RAM hit (member 0x247978, static data image — reproducible t297+t298).
NEGATIVE (unattributable, see NEXT): sprite(48,151)/planet/empty clicks in
the Icarus view produced ZERO stops at the 6 downstream legs while the ring
kept autosaving (game running, never frozen). NO LEDGER ROW CLOSED
(strict-close): OQ-016 r1, OQ-019 r1/r3 open. NEXT=t300 run 4 with
handler+router armed (script already patched+committed).

## LANDED t298 (2026-11-04, session 7) — LIVE ORDER-WITNESS #2: HARNESS
NEGATIVE + FIVE BINDING MEASUREMENT CORRECTIONS (docs/re/_wip_t298.md +
ships.md S26; runs t298-order-FAILED-keyerror-172935, t298-run2-swallowed-
popup, t298-order-20261104-174236; scripts/r298_order_session.py NEW).
MEASURED: (1) POINTER-VALUE LAW — RAM stores GUEST-PHYSICAL pointer values,
read target at member value+0x88 (cross-checked vs relocated code immediates
dumped from in-RAM code at 0x1ba16/0x1baa7: imm = X+0x242000; scalar law
B+OFF+X CONFIRMED, t297-A stands); t297-B "handler 0x1aef8 zero refs"
REFUTED (physical pattern -> 1 hit member 0x247978); ds:0x43504 = current-
system STAR record ptr ("Icarus" read at value+0x88+0x1c) = system-identity
oracle. (2) FLEET LIST ORDER != ARRAY ORDER (vision: rows = slots 18/7/16/22;
sort law UNKNOWN; header "14 Ships, 13 more allowed"). (3) ship_array_law
count 30 UNDERCOUNTS — named owner-0 ships at 31/32/33; 14 named == header.
(4) BatModeWnd client rect x 7..465 is a HARD bound for screen finders
(unbounded finders return sidebar chrome; the tan class itself VALIDATED:
found the real sprite at (48,151) in t297's orbital shot, vision (48,148)).
(5) command ring entry stride 10, churns entry0 from NON-order input -> not
an oracle. LAW RE-ENFORCED: post-End-Turn EVENTWIN construction popups
swallow every click; close_eventwin() before any click that must land (run 2
died exactly this way — t293's law, re-broken, now guarded in r298 script).
Drive plumbing end-to-end CLEAN in run 3 (End Turn x2 t1087->1089, escape
ladder held, production :9 t=1086 verified untouched all session). NO LEDGER
ROW CLOSED (strict-close — OQ-016 r1, OQ-019 r1/r3 open). NEXT=t299 debugger
witness (BPLM sentinel technique on the batmode legs; NO fourth mouse launch).

## LANDED t297 (2026-11-04, session 6) — LIVE ORDER-WITNESS #1 NEGATIVE,
INSTRUMENTS FIXED, CHOREOGRAPHY RE-READ (docs/re/_wip_t297.md S1..S3 +
ships.md S25; run work/r1/t297-order-20261104-152048). MEASURED: msg-4 router
0x1b070 dispatches on [win+0xaf] NON-NULL -> batcon 0x1b91c(ecx=1) BEFORE the
mode-2 branch; [win+0xbc] writer census = {0x1ad59 init 0xffff, 0x1c9a0
kind-6 route-edit leg} so the t296 deselect reading holds only on the
null-selection path; the 0x1ba8c leg = mouse-reachable ORDER PUBLICATION
(ds:0x43508 := [[clip+1]] + ring code 0x11 @0x56ad4) without any msg-0x50
widget. CORRECTIONS (binding): T297-A ds:0x43504/0x43508 at B+0x82bb0+X (the
r1_slot.OFF data base — the t296 pin sheet was off by 0x82bb0 and read
constant garbage); BOTH globals have non-order writers (0x43504 = 0x256825
non-null at idle; 0x43508 changes between autosaves with zero input) ->
DELTA-only witnesses; T297-B batwin instance NOT findable via handler-ptr
scan (0x1aef8 zero u32 refs in payload+RAM; 0x1b91c only at 0x22cac1/0x22eb3b
= verbatim payload-image copy). GATING FACT: t=1086 owner-0 fleet has NO
kind-4 ship (11 ships kinds {3,5}); slot 8 kind-4 MOVES=12 at t=1087. Own-bug
autopsy: picker omitted owner==0 (clicked fleet row-1 = owner 1, G3 dead);
check_issue read the wrong-address global absolute -> false "issued". FIXED
same-session in scripts/r297_order_session.py + r293_move_session.py (idx
field); r296_selection_note.py doc corrected. TOOL TRAPS banked: drive scripts
need venv python (system 3.13 lacks PIL); pgrep -f self-match again. NO LEDGER
ROW CLOSED (strict-close — OQ-016 r1, OQ-019 r1/r3 stay open pending the
witness). Production :9 alive and untouched (turn 1086 pinned all session).
NEXT=t298 fixed-picker witness session (End-Turn once first, target slot 8,
colour-class sprite, right-click-empty publish leg).

## LANDED t296 (2026-11-04, session 5) — SELECTION CHOREOGRAPHY CLOSED
STATICALLY (ships.md S24 + docs/re/_wip_t296.md S1..S9; every quoted block
re-dumped VERBATIM from work/t91_code_disasm.txt, 140,824 lines, in an
independent verification pass; 11 machine-checkable anchors pinned in
scripts/r296_selection_note.py, ANCHORS OK 11/11 vs payload 576,643 B).
THE LAW: a click selects a ship iff G1 clip exists (built iff BYTE
[ship+0x58]==4 in-system, builder 0x1d6bb, clip kind:=2 @0x1d6e6, stride 0x35,
overflow assert 0x2a428 ebx=0x750 edx=0x5dc), G2 clip kind==2 (0x1b6fc msg-0x53
leg / 0x1b9f6 mouse leg), G3 owner [ship+0x54]>>16 == BYTE ds:0x7458e
(0x1b709/0x1ba16), G4 MOVES [ship+0x88]>0 (0x1b716/0x1ba2c) -> [batwin+0xb7]:=2
(0x1b71f/0x1ba39); MODE ENUM 0 idle/1 armed (0x1b7dd via msgs 0x4d-0x51)/2
selected/3 route-drag (0x1b103)/4 transient (0x17243). MOUSE IS MSG 4 (0x1b070)
-> 0x1b91c, NOT the internal relay msg 0x53 (0x15f3c posts it). WHY t293 failed,
now EXPLAINED not merely observed: dots are kind-3 PLANET clips (G2 skip leg)
AND a mode-2 plain map click DESELECTS (WORD [win+0xbc]==0xffff -> 0x1b114).
PUBLICATION: ds:0x43504 selected-object (store census EXACTLY {0x28ec2,0x28ef6,
0x36b01,0x52003,0x55d35}), ds:0x43508 order-destination ({0x1b5e6,0x1baa7,
0x51a8e,0x51fc2,0x55bbd}); msg 0x50 leg 0x1b5ba publishes
ds:0x43508 := [sel+0x42+ebx*4] + command-ring 0x56ad4(0x7a35c, code 0x11) =
6B {u16,u32} at [game+0x422c]+slot*6. CORRECTIONS banked: viewer global is
0x7458e not 0x7458c; 0x1aef8 has ZERO immediate references (registered, not
referenced — BatModeWnd attribution rests on windows.txt + r1-savestate E1
list); S1's two `89`-form 0x43504 writers unconfirmed, drop them. HONEST
NEGATIVES: msg-0x50 TRIGGER WIDGET unidentified (statically unreachable);
screen->world camera unmapped; NO LEDGER ROW CLOSED (strict-close — OQ-016 r1,
OQ-019 r1/r3 stay open pending live witness). Pure-static iteration; :9
untouched. NEXT=t297 live move-order witness via the r296 choreography.

## LANDED t295 (2026-11-04, session 4) — HOME-STAR DRAW LAW CLOSED
(OQ-016 residue 2, MEASURED). FUN_00022ce4 0x22eb4..0x22f55 = the draw: per
race r in RACE ORDER loop { one FUN_0007824f LCG draw; k = draw % T (idiv rem
@0x22ec7) } until entry unclaimed (gate 0x22ee0), store row_r+0xd=entry(k)
@0x22edd, claim byte 0x80|(1<<r). UNIFORM rejection sampling, distinct by
construction, NO spread geometry — the old max-min BFS rewrite code was a
documented MISMATCH, now replaced (pickHomeStars + isolated homeLcg_ stream;
interleave vs world-gen stays UNMEASURED, closed law = distribution). Census
scripts/r295_home_draw.py (KEEPER): equal-marker 30/30 turn<=2, distinct
36/36 lineages, index chi2=31.0 (df=49, crit@.01=74.92). Linear capstone
sweeps MISSED the +0xd store (desync); function-aligned disasm found it —
lesson banked. BLAST RADIUS re-derived by measurement, all honest: seed 42
now Extinct t20 (uniform draws produce lethal homes the BFS never could —
real vendor exposure), fixtures moved 42->7 / 4242->23 / cornucopia 8->10,
t274 cadence pin t16->t31 (MUTATION-VERIFIED: >= -> > slips exactly t32),
t41 CB test made structural (per-colonise CB). run_tests 175/0. PLAYTHROUGH
REGENERATED: A seed2024 Extinct t285, B seed23 CONTROL t1406 (NEW exemplar —
seed 1 re-drew Extinct t266; record_playthrough.sh updated, gate greps
Control). Evidence: docs/re/income-law.md S-T295 + docs/re/_wip_t295.md
S1-S7. NEXT=t296 ship-selection choreography (static-first) — it gates BOTH
remaining non-user residues (nuke law, magnetron witness).
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
LOOP CONTROL: relaunch law MAX_ITERS=20 IDLE_GATE=0 (queue-driven; the
nothing-runnable path exits clean). After a queue drains: author the next queue
OR park NEXT on a WAIT-TRIGGER sentinel (task line FIRST — wake selection reads
field 2 of the first non-blank line; notes never go there). Sentinel-slot law:
task line FIRST under NEXT ACTION. work/ is gitignored — findings in docs/re/.

## HISTORY
Per-iteration LANDED blocks t1..t292: archive/state-v2-full/2026-11-03/STATE.md
(+ wip/ notes). v1: archive/ralph-v1/. Slim commit: see git log 2026-11-03.
## LANDED t336 — 2026-11-08 (windows.txt KEYWORD->STORE MAP + STATE VALUE
## DISPOSITION: THE STATE IDS ARE THE GLOBAL WINMGR PER-ID HANDLE TABLE,
## CENSUSED 196/196; KEYWORD DISPATCH IS ON THE TYPE INTEGER, NOT STRINGS)
- VERBATIM: STATE line parsed in PARENT-block fallthrough 0x58f67->0x59021
  ('%s %d' count then '%d' ids); per id fn 0x57194(winmgr=edi, id, handle=
  [ebp+0x41]): stride id*0x8e, u16 count @+0x3068, 32 u32 slots @+0x306a,
  global counter winmgr+0x4226; asserts id<0x20 (:0xb37), handle<0x400
  (:0xb38), slot<0x20 (:0xb5a); remover 0x57284 mirrors. S3's interim stride
  arithmetic (0x11c/0x238) retracted — the lea/add/shl chain computes 0x8e.
- MEASURED (scripts/r336d_state_census.py exit 0, 196 needle-verified saves):
  table located at W=0x2bc3e4 in 196/196; 16/18 ids EXACT windows.txt order
  (id 16 battle family verbatim incl. 1-char windows 'W','S','Z','I' — an
  earlier 0/196 for id 16 was a name-length-filter bug, fixed in-script);
  id 1 prefix+appended by runtime windows (EVENTWIN/Go^to^Planet/OK, 16
  saves); id 17 slot-substituted Leave Orbit/Abandon/Cancel over PLSQBUT0..2
  (22 saves); sum(counts id 0..31)=135=file STATE token count; +0x4226=18=
  distinct file ids. The table is a LIVE runtime registry, not a file mirror.
- KEYWORD DISPATCH LAW: outer loop 0x57687 scans '%s %d' (0x85bcc); the
  INTEGER token (TYPE code) drives the cmp-chain 0x576c4/0x593b7; keyword
  strings are scanned to scratch [esp+0x334]/0x338 and never string-compared
  in-image (keyword literals absent from the RE image, t333 reproduced).
  TYPE n -> class creation 0x78b4c(class literal from pool, size, 2) + alloc
  0x2a4ec + init 0x30c08; full keyword->store map banked docs/re/_wip_t336.md S4.
- LEDGER: nothing closed strict-close (16/3); OQ-016 residue-(1) STATE-line
  disposition rewritten (stored in global per-id table, located, counts
  reproduce), row open on mode-1 witness + table READERS. Files
  _wip_t336 S0-S4, ships.md S55 (hand-authored), OPEN-QUESTIONS residue-(1)
  update, scripts/r336_store_map.py + r336d_state_census.py (exit 0).
  Sitting NEGATIVE t1086; production :9 (136357/136359, Xvfb 1461) never
  signalled; game/ read-only. NEXT=t337 STATE-table reader walk VERBATIM

