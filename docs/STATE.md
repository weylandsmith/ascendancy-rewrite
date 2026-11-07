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
updated: 2026-11-06T07:10
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

NEXT t329 OQ-019 DISPOSITION PACKET — t324 landed NEGATIVE-ABSOLUTE (its
condition is met; see LANDED t324 below), so the conditional row is now
satisfiable and is the natural consequence of this chain: every capture route
for the select/destination residues is cited-dead (t319/t320 pump, t322 mouse,
t323 activation, t324 class-table). DRAFT (do NOT apply) the final OQ-019 row
text marking residues (1) sugar-cube arrival granularity, (2) per-ship build
path = build decision (D2), (3) magnetron witness as capture-limited with the
cited dead-route closure: t319/t320 pump never posts 0xc, t322 BatModeWnd zero
msgs in-view, t323 activation census-complete, t324 class-table absolute
(live RAM == cited, fn 0x32100 absent — scripts/r324_census.py, 10/10 saves).
Magnetron USE shares the same widget path, so its witness class is cited-dead
too — say so explicitly (it retires the last scripted idea honestly). Update
docs/DECISIONS.md D3 with actual state: rows closeable by the loop = NONE
remaining without user input (D1 ruling or D2 commission). NO LEDGER ROW MOVES
in t329 (strict-close; disposition is the USER's ruling) — t329 produces a
draft packet only. Ordering rationale: t325-t328 are independent of the
OQ-019 chain (shield-byte witness, phase bomb, debugger tool v2, OQ-005
feasibility); landing the OQ-019 disposition now banks the payoff of the whole
t304-t324 chain while it is fresh and hands the user a single crisp ask,
before the queue drifts. If t329's draft is ready, NEXT becomes t325.
Fixed laws carried (do NOT re-trip): t324 note (census anchor = installer
target data 0x58e8; [wmgr+0x3337] is the LANE POOL, not a name registry; slots
= P0+static); t323 amendment (1)-(4); t322 (1)-(3); t321 (1)-(4); t320 (1)-(4);
t319 (1)-(4); msg-0x50 no external sender; fn 0x1b91c decode verbatim (t296 S5
+ t321 S4); fn 0x2351c name arg DEAD (do not re-open as activator); production
:9 (pid 1957) untouched; scratch copies only, never mount game/; sitting check
FIRST (playcap newest turn >1086 => re-run scripts/r1_t85g_sitting.py before
anything).

QUEUE (phase 5b, one session each; finish tN -> rewrite NEXT to tN+1 VERBATIM;
keep this block intact except deleting your completed row; t325 below is row 1):

t325 PER-SLOT SHIELD-BYTE WRITNESS (OQ-016 residue 4; t271 said writer
  reachable, consumer unmapped — the debugger chain makes it cheap now).
  Slot law (STATE WHAT-IS-IN-HAND): slot array at stored-ptr+0x88 conversion,
  slot = 4B {class, itemIdx(0xff empty), flags u8, shield u8} -> shield byte =
  slot base +3. POINTER-VALUE LAW t298 binding: RAM holds guest-PHYSICAL;
  BPLM target = member + 0x88. Scratch copy, OWN ring dir, r322_relaunch.sh
  base, t305 FirePat law (stop line = unique PATTERN), t307/t308 leg shape
  (reproducible 3/3 — copy their run dirs under work/r1/ as templates). Drive
  ~10 turns with a build completing (pending reserves its slot t271: byte1:=
  item id, word2 bit0 CLEAR — completions DO fire in normal play; item-36/35
  branches are the REFUTED zero-witness class, do NOT chase those). On fire:
  capture CS:IP + previous value + which slot; map EIP through the windowed
  disasm recipe; census consumers of the same offset offline. Bank writer +
  consumer law to docs/re/economy.md (or income-law.md if build-phase); update
  the OQ-016 row residue list. Zero-fire after 3 launches = honest negative,
  residue becomes instrumentation-class, say so in the row.

t326 PHASE BOMB FORCED-CAPTURE (OQ-016 residue 1 — the nuke law, the LARGEST
  capture-gated item left; one-run recipe verbatim in docs/BLOCKED.md §Nuke).
  Scratch copy, OWN ring, drive class laws (t285: assert_on_map, no Escape,
  STOP-AND-LOOK). Scripted route: research path per restree prereqs (its tech
  chain, verify availability via t294 planitem law), build at a Shipyard,
  launch at an OWNED planet with >=3 surface items. Capture slot states
  before/launch/after via the ring + pointer law; identify the dispatch-table
  entry by which code first writes FF into a mid-record slot byte at launch
  time. Budget 4 launches MAX (t293 accounting law: only runs that reached the
  build/launch phase count). If Phase Bomb never completes research in-turns
  reachable, bank the turn-cost arithmetic you DID witness (restree cost law
  t295-era pins apply) and exit-1 negative. Default stays NOT modelled either
  way; closing = the witnessed destruction law banked to economy.md + row
  residue updated.

t327 DEBUGGER-SESSION TOOL v2 (compresses every future DAT-writer hunt to 1-2
  sessions; the t306-t323 chain burned ~18 iterations largely on instrument
  bugs — this is the payoff task for that chain). Ship
  scripts/r1_dbg_session.py wrapping the proven pieces (r322_relaunch.sh boot
  shape, leg spec {addr, FirePat pattern, expected-callsite}, whole-log msg
  census, resume-with-fired-BP handling, bank-on-exit). LAWS to bake in, all
  measured: t305 FirePat stop-line = unique pattern (debug.cpp debug.cpp:1560+/
  1586-87); MEMREAD real-mode-only (debug.cpp:2983) — ring is the read surface;
  xsend arg1 = WINDOW TITLE not display (t290); resume-with-fired-BP re-freezes
  (t302 bug 2). VERIFY against two known positives: the t308 DAT_43504 leg
  (must fire 3/3 on an entered-star click; run dir under work/r1/) and the
  t319 poster leg (0x54ac5 msg-4). MUTATION TEST: one deliberately bogus
  pattern must classify zero-fire, not crash. Bank usage doc to
  docs/re/dosbox-debugger.md (append §TOOL v2) + fix any doc drift found.

t328 OQ-005 DRAW-WITNESS FEASIBILITY (offline-first; sharpens D1 for the user,
  closes nothing itself). The decision sheet waits on human ruling because we
  assumed no measurement can see these 80 records — but the vendor game IS a
  measurement instrument (external to us; R13 satisfied). Per-record
  feasibility pass: t200 selector law already PROVES the 12 cos_star k40..k51
  + 25 zero-byte ladder slots draw NOTHING in the vendor too (dims-zero blit
  = error -1 @0x5cb2b) => no witness possible, bank as CITED-NO-WITNESS (this
  alone converts "batch ruling junk?" into "vendor-drawn nothing" — update
  decision-sheet rows B/C + shp.md S25). sg50expl k9 / sg64expl k0 = combat
  explosions = UNREACHABLE-BY-CAPTURE class per t323 amendment — cite, no
  probe. mouse k5/k6/k7 + 1starmap k1: check static sites for who selects
  those indices (windows.txt law + name-imms); if any is reachable in a
  normal screen, DESIGN (do not run) a one-launch scratch draw-capture with
  screen-compare vs our decode, and queue it as a follow-on task. 3cfgnew
  k12: vendor truncation — cite as junk-certain. Deliverable: feasibility
  table + updated DECISIONS.md D1 text (ask shrinks to what is actually
  adjudicable). (NOTE: the old "queue it as t329" text predated t324 landing;
  t329 is now the OQ-019 disposition packet — queue any draw-capture design
  under a new id after t328.)

STANDING LAWS FOR EVERY ITERATION HERE (beyond TASK_CONTRACT):
- FIXED LAWS, do NOT re-trip (t319-t323 amendments are BINDING): poster pass
  posts msg 4 only (27/27); ds:0x484ac = BIOS int16h button state not app flag;
  msg 4/0xc default-handled fn 0x336b4 zero DAT stores; BatModeWnd has NO
  in-session activator ([win+0xb1] writers 14 sites cited); fn 0x2351c name arg
  DEAD; msg-0x50 no external sender; broadcast pump dispatch 0x56c74 COLD
  2x-confirmed.
- DEBUGGER: binary work/r1/dbx-build/dosbox-x-master/src/dosbox-x (copy to
  work/r1/bin/dosbox-x-dbg if not yet there); NEVER /usr/bin/dosbox-x;
  core=normal for stepping legs per docs/re/dosbox-debugger.md; first-BP-fire
  0x00-init artifact check before believing a witness; OFF-BY-H discipline
  (member -0x88 -> physical; t298/t286b).
- OOM LAW (6.4 GB timeline: r1_stream / <=400 KB tail-seek / r214_triage only);
  TWO-WRITER RING LAW (scratch = own ring); KILL BY RECORDED PID (structured
  argv; pkill -f self-kills shells); SIGKILL softlocks; DISPLAY=:9 injected;
  TL=172800; NEVER loadstate to resume; bank ring before restarts.
- Sitting check FIRST every iteration (tail-seek playcap newest turn; >1086 =>
  scripts/r1_t85g_sitting.py before anything). Production :9 pid 1957 t1086 is
  the corpus — untouched unless the task IS a drive task, and then drive laws.
- Ledger 16 closed / 3 open (OQ-005, OQ-016, OQ-019); keep ledger_audit +
  ledger_index_check green; NEVER hand-edit the index block (re-derive).
- OQ-005 ruling = USER's (D1); do not rule for them (R13); draw-witness work
  (t328) is permitted because the VENDOR is the instrument.
- Do NOT re-trod: t323 amendment routes; t293 click-selection; t49/t58/t265
  flight mining; item-35/36 completion witnesses (t271 REFUTED zero-witness,
  AI-unreachable); t212/t213 static exhaustion; everything in STATE.md
  DO-NOT-RE-TROD.
- Gate ~2-3 min; milestone 6 stays; work/ gitignored — findings to docs/re/.
- After the queue drains: author next queue or park WAIT-TRIGGER sentinel
  (task line FIRST); relaunch law MAX_ITERS=20 IDLE_GATE=0.

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
