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
updated: 2026-11-24T00:30
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
    - "OQ-027 intro TUNEID index base + per-button vendor SFX id CLOSED
      2026-11-20 t440 ((b) t437 + (a) t440). (a) MEASURED ZERO-BASE: DIGITALMUSIC
      dispatch 0x2ee3b calls FUN_0004f86c on static audio obj (save fixup
      runtime linear 0x2ba638); index law 0x4f929..0x4f945 obj+0x37a+tuneid*28
      NO bias, bound WORD[+0x6fa]==29; table 29/29 music.txt order in 20/20
      banked saves (scripts/t440_music_table.py PASS) -> TUNEID 6=intro00,
      7=intro01; 'heap-relative/not statically decidable' REFUTED (audio.md
      S6.1/S6.3a); port outcome already correct, comments cited, pin
      audio_tuneid_zero_based_t440 mutation-verified. (b) windows.txt
      SOUNDCHANNEL -> record +0x59 == 0 on 2400/2400 x 20 saves: vendor plays
      manifest[0] 'button' on file-declared presses, nothing on map
      (audio.md S6.9); sfxForPress upgraded + pin sfx_press_buttons_button_t437"
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
    - "OQ-005 .shp pixel codec CLOSED 2026-11-09 t367 (D1 USER RULING, the
      row's own named closer; docs/DECISIONS.md USER block 2026-11-09 12:45
      verbatim: mouse k5/k6/k7 keep, batch-41 accepted, A6-A8 keep, no B-row
      misID). t367 code+pin: corner-anchor gate fallback in
      rewrite/src/formats/shp.cpp decode() decodes k5/k6/k7 at signed-bbox
      78x47 (planes byte-identical md5 b2d049bbf5b5..., census 543287,
      TEST shp_corner_anchor_fallback_t367 admits EXACTLY these 3 corpus-
      wide; cos_star/1starmap/sg50expl stay vendor-gate-rejected); Python
      validator unchanged by design (two-consumer law); docs/re/shp.md S28."
  open:
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
NEXT tPL-D1 HOME PLANET BY RACE (D26) — ordering rationale: tPL-B2
(2026-11-24) landed the msg-50 productivity-box popups with a PASSing
pixel + vision witness (docs/re/_wip_tPLB2.md P8/P9), so the planet-view
D26 queue advances. D1: the Chamachi home planet shows WRONG ART and
WRONG MAX POPULATION vs the vendor new-game. Derive the vendor new-game
home-planet law per race: fixed TABLE vs RNG-at-seed decides the route —
debugger on a scratch new-game as Chamachies settles it (scratch savedir
law; protected saves untouchable); cross-check Minions. The max-pop
half likely folds into the seeded capBase law (income-law.md S10 t29+t33
— capBase = NONBARRENCOUNT/3 + 5 into +0x55/+0x4a): if the vendor home
worlds carry a DIFFERENT seeded cap, measure it against the save corpus
first (cheap) before any debugger leg. Recipe reminders: capture via the
shot() in scripts/tplb2_port_witness.sh (winpos substring + root-crop +
assert 640x480; NEVER import -window NAME — title flips at RESUME;
export DISPLAY in scripts; clear stale /tmp/.X99-lock; POINTER-ONLY moves
use `xsend warp x y` — the legacy `x y` mode CLICKS). THEN tRS-B1
RESEARCH: SET PROJECT (D26: "I can't set any projects") — derive the
vendor set-project handler, PORT + walkthrough witness. THEN tRS-V1
RESEARCH TREE DRAW (D26) per D19 G1/G2 (3D projection ported t419/t399;
diff regions, fix laws not pixels). THEN tPR-U: USER GRADE PACKAGE
(checklist format, ours|vendor side-by-side) for planet + research; NEXT
becomes WAIT-USER-GRADE-PR1. RULES: D19 G1-G6 binding; Athens shots layout/
color only; no synthetic stand-ins (RE-FIRST t423 law); protected saves
01/02/03/04.SAV + RESUME.GAM untouchable (scratch savedir law); game ring
TL EXPIRES 2026-11-24 14:53 — if a live witness needs the production ring
and it's dead, run the t439 recovery pattern FIRST; C1-C5 cosmetic backlog
+ race intro stay DEFERRED (D25) — do not touch.

tPL-B2 LANDED 2026-11-24 (PRODUCTIVITY-BOX POPUPS PORTED + LIVE WITNESS
PASS; no OQ row touched — tPL tracks none, honest negative under
strict-close; open=[016,019] unchanged).
PROVED (docs/re/_wip_tPLB2.md P1-P9; prior session derived P1-P6, this
session re-verified every leg instruction-exact on work/ascend_restored.bin
and shipped the port):
 - KEY->CASE LAW (live jump table, member delta 0xfd0): PLRES=RESEARCH
   (0x3dc61), PLIND=INDUSTRY (0x3dd17), PLPRO=PROSPERITY (0x3ddc0),
   PLPOP=FULL-INFO (0x3e2c8); key>4 = no lines (0x3dc53 ja).
 - TWO-LINE LAW 0x3e4db..0x3e5db: L-D getter(99) "%s %s: %d per day"
   (hold 0xf) + L-E getter(100) "%s will %s in %d day%s." (hold 0x50,
   plural pair getter28/29 iff days==1); sentinel fmt getter(67/73/74)
   on the 0xffff leg. COUNTDOWN 0x47010 = max(1,ceil((target-acc)/rate)),
   rate<=0 -> 0xffff.
 - PROSPERITY fill 0x3ddc0 EXACT incl. `cmp %bx,%dx; jae` (pop >= maxpop
   -> getter74) and 0x47010(eax=wrap 50 @0x66e4, edx=+0x4e counter,
   ebx=+0x48 pros). POPUP RECT (wrec+10, wrec+0x145/0xcf).
 - PORT: rewrite/src/ui/indpopups.{h,cpp} (pure law + Campaign-fed
   builders), Campaign::queuedTechFor read, ui.cpp msg-50 arm (BEFORE the
   tile arms — panel click wins) + dismiss + render. SEAMS named:
   TPLB2-A Ship/Automation cost legs (statuslist precedent), TPLB2-B
   inline |%d| chip not rendered (code computed+pinned), TPLB2-C chip
   raceIdx runtime table analog, hold-tick consumer unrecovered (show
   until next click = documented default).
 - PINS: tests/test_indpopups_tplb2.cpp x6 (countdown values, rect law,
   L-D/L-E verbatim+gates+plural+sentinel, full-info chain+"No One"+chip
   code, campaign cases all keys). Suite 511/0/0 (was 505).
 - WITNESS (scripts/tplb2_port_witness.sh + tplb2_census.py): per-key
   line counts 1/1/2/5 match the law; pixel census VERDICT PASS (own-rect
   93.8% changed x4, no-overlap control 0px, dismiss 0px full-frame);
   vision oracle reads "Amoroso I Prosperity: 1 per day / Population will
   grow in 50 days." — the D26 user-witness text shape reproduced.
 - HARNESS NOTE: tests/harness.h has CHECK/REQUIRE_DATA only (no REQUIRE);
   local REQUIRE = CHECK+return idiom (now used in the tplb2 pins).

tPL-V2 LANDED 2026-11-24 (ORBITAL SLOTS LEFT + HOVER OUTLINE PORTED,
PORT PIXEL CENSUS VERDICT PASS; no OQ row touched — tPL tracks none,
honest negative under strict-close; open=[016,019] unchanged).
PROVED (docs/re/_wip_tPLV2.md F1-F7):
 - GEOMETRY LAW (FUN_0003b96c loop 2): 10 slots, origin (13,119), pitch 70,
   col0 x13 / col1 x83, rows y=119+70*r — NOT isometric; occupied slot =
   planitem art CENTRED in the 70x70 box; empty slot at rest paints
   NOTHING (witness t254: eight empties are starfield). Witness-confirmed
   against t254 screenshot (x=83 col1 exact; occupied blobs land on cells).
 - HIT LAW (FUN_0003a880 verbatim): rect x in [14,152] y in [120,468]
   (1px INSIDE the paint origin — vendor quirk pinned), k = (x-13)/70 +
   2*((y-119)/70); hover word +0xac set at 0x3ac14.
 - HOVER OUTLINE LAW (0x3c546..0x3c5d7): 69x69 box OUTLINE pal 150
   (conv6->8 = (16,69,77)) iff hovered cell == +0xac PER SLOT DRAWN, slot
   EMPTY, no pick pending. The per-slot compare is load-bearing: the first
   port built a whole-field compare and the census CAUGHT all ten boxes
   outlining at once (leak 2447px) — fixed via orbitalHoverOutline(...,
   int slot, ...) + anti-leak pins.
 - PORT WITNESS PASS: scripts/tplv2_port_witness.sh + tplv2_census.py —
   rest 0px all ten boxes (x2 shots), hover-slot0 box(13,119) 276/272 pts
   exact pal-150 colour with other nine 0, hover-slot6 box(83,189) same.
 - TOOLING: tools/xsend gained `warp x y` (XWarpPointer, NO button events)
   — pointer-only moves for hover witnesses; suite 505/0/0 (3 new
   test_planetview_tplv2 pins: geometry, hit law incl. bounds quirk, hover).
 - SEAMS banked: TPLV2-A item-23 race-table runtime-unrecovered (Ship
   draws planitem icon); flag334 tutorial ghost leg not modelled.

tPL-V1f LANDED 2026-11-24 (FORMAL PORT PIXEL CENSUS VERDICT PASS; no OQ
row touched — tPL tracks none, honest negative under strict-close;
open=[016,019] unchanged). PROVED (docs/re/_wip_tPLV1.md F5):
 - CENSUS v2 scripts/tplv1f_census_v2.py PASS 2x (f1, then f2 after
   mutation-restore): old (24,24,32) outline 0 px; size-1 fill 11/11 (10
   exact conv(150) + 1 structure-art-covered cell (4,3)); adjacency 12/12
   pairs OK; CONTROL 5/5 law-A centres outside the painted B-union BLACK
   (anti-vacuity). Mutant M-T1 (tileCenter re-transposed to law A) CAUGHT:
   census FAILs "best size class 4 != expected 1"; source restored md5
   9c55fe6a3ccfb7130013048f57bd9b39, rebuild green, suite 502/0/0.
 - V1 CENSUS PREMISES REFUTED (the law was never wrong): (a) >=200 white
   edge px — seed-5 home planet surface classes are ALL 0 (app log), and
   class 0 draws BLACK edges (0x3bbd6), so white-px count is meaningless
   there (edge colour law stays pinned by planettile_edge_colour_tPLV1);
   (b) "midpoint non-black" — the midpoint sits ON the shared edge line,
   legitimately black; the gap signature is a black point that should be
   INSIDE a diamond (census v2 probes 3px inside each side).
 - GRAB LAW REPLACED: `import -window NAME` needs EXACT WM_NAME; title
   flips "Ascendancy" (title.cpp:135) -> "Ascendancy rewrite (P5a)"
   (ui.cpp:114/122) at RESUME, so the tPL-V1 name grab died exactly there.
   SHIPPED recipe in tplv1_port_witness.sh shot(): tools/winpos substring +
   `import -window root -crop WxH+X+Y +repage` + assert 640x480. Also:
   export DISPLAY inside scripts (per-cmd DISPLAY= prefixes didn't reach
   import); rm stale /tmp/.X99-lock + /tmp/.X11-unix/X99 before Xvfb.
 - SITTING CHECK ran first (r1_t85g_sitting exit 0): tail rows all
   turn=1086 (newest wall ~23:37), production dosbox-x pid 1470999 alive,
   no new sitting, stale assignment stood.
 - INCIDENT + RECOVERY (full text _wip_tPLV1.md F6): my cleanup
   `pkill -x Xvfb --older ...` killed the PRODUCTION Xvfb :9 at 00:01:33 ->
   dosbox-x 1470999 died (t277 golden farewell, not a crash). RECOVERED per
   the t439 pattern: no VNC client attached, `bash scripts/r1_playcap_vnc.sh
   start`, new pid 1623906, ring rotating 00:30:38+. LAW: on this host kill
   Xvfb BY PID only — never bulk-pkill by user/age.

tPL-V1 LANDED 2026-11-23 (TILE GRID PITCH + COLOURS: THE PORT'S CURSORS
WERE TRANSPOSED; no OQ row touched — tPL tracks none, honest negative under
strict-close; open=[016,019] unchanged). PROVED (docs/re/_wip_tPLV1.md
F1-F4, planets-ui.md §14):
 - PITCH RE-DERIVED from the raw paint record 0x3c211..0x3c274: the field
   with SYMMETRIC +-0x22 offsets is X (68-wide), the 0/+11/+22 field is Y
   => centre = (410+34*(col-row), 127+17*(col+row)); |det| 1156 == diamond
   area = EXACT tiling (D26 "rows have gaps" was the t418 shorthand's
   |det| 1445). VENDOR WITNESS scripts/tplv1_lattice_witness.py on
   t254/02_planet_detail.png: corrected law 100.0% edge support vs 26.0%;
   controls (shifted fits) <=52.9%, baseline 0.6%.
 - EDGE COLOUR LAW 0x3bbd6..0x3bc52: EXACT class-byte compares 0->black,
   2->red(117), 3->green(146), 4->blue(255), default white(12) in game.pal
   — exactly the user's "white/blue/green/red + black"; rock-flagged byte =
   white. Grey-ramp fill arm gated by widget+0x18b bit0, ZERO pixels in the
   witness (SEAM TPLV1-A). Fill stays uniform pal[150] (t421 reconfirmed).
 - PORT SHIPPED: tileCenter corrected, tileEdgePaletteIndex pure law,
   fills-then-outlines two-pass painter, invented (24,24,32) outline +
   rock-darker fill DELETED. Pins re-derived + new edge-colour pin; suite
   502/0/0. LIVE CLICK PROOF: seed-5 clicks at computed centres (410,297)/
   (444,280) select tiles 5 then 3 (adjacent) — the hit-map follows the
   corrected law. HONEST NEGATIVE: formal pixel census PASS cut by budget
   (stale-Xvfb root-grab offset; fixed the script to window-by-name on
   :99) -> queued as tPL-V1f, the FIRST task above.
 - SITTING CHECK ran first (r1_t85g_sitting exit 0): tail all turn=1086, no
   new sitting, stale assignment stood.
 - HAZARD BANKED: never `import -window root` on this host (stale Xvfbs
   :9/:97); grab the app window by name and assert 640x480.

tPL-B1c LANDED 2026-11-23 (PLACEMENT PINS MUTATION-PROVEN 10/10 CAUGHT;
no OQ row touched — tPL tracks none, honest negative under strict-close;
open=[016,019] unchanged). PROVED (docs/re/_wip_tPLB1c.md):
 - scripts/t418b_mutate.py M8..M17 one background session (notify), ~78s/
   mutant, ALL CAUGHT, failing pin every time planetgrid_placement_t418b;
   AFTER-RESTORE 501/0. Per-mutant FAIL line cites in the wip doc (M8 L233/
   L281 rock; M9 L229/230 exempt {5,35}; M10 L316/369 row-1 probe; M11
   POLARITY INVERSION L316/369 — the t418b bug re-introduced is caught, pin
   encodes the raw 0x38666..0x386fc law; M12 L225/302 all-inactive; M13 15
   fails XOR polarity; M14 L244 bound item22; M15 L237/239 ring domain; M16
   L295/300 terraform barren arm; M17 L263 own-skip). The corrected chain
   has NO vacuous pin and NO missing separator.
 - HAZARD NEW VARIANT: a killed background campaign (SIGTERM mid-M8) left
   the MUTANT ON DISK; recovery = md5 vs /tmp snapshot, copy back + touch +
   rebuild green BEFORE relaunch. Snapshot pre-flight verified clean this
   run (md5 91932a9704d412c91c476183bc344b07 == working file at 0925966).
 - SITTING CHECK ran first (r1_t85g_sitting exit 0): playcap tail all
   turn=1086 (newest wall 20:34), production dosbox-x pid 1470999 alive, no
   new sitting, stale assignment stood.

tPL-B1b LANDED 2026-11-23 (BUILD LOOP SHIPPED: TWO-STEP UI + CORRECTED
PLACEMENT CHAIN + POLARITY FLIP; no OQ row touched — tPL tracks none,
honest negative under strict-close; open=[016,019] unchanged). PROVED
(docs/re/_wip_tPLB1.md F7-F10 + ui/planetview.h F3 block):
 - F10 DECISIVE: checker FUN_0003830c placement region is a GRANT
   ACCUMULATOR (0x38444 xor edi,edi reset; mov edi,-1 legs grant, xor legs
   veto). Rule B 0x38493 reads the CELL-CLASS byte, NOT occupancy — there
   is NO OCCUPIED VETO (t43's empty-cell law is a PICKER law). Vetoes
   shipped: XOR (item<31, booleans differ refuse, 0x384db), rock/dig XOR
   (0x38519 dig legal ONLY on rock, 0x38546), terraform barren+empty+
   surface (0x38554), adjacency (0x385b7..0x386fc). Rule A modelled
   always-granted [inferred: t43 barren-build census 263/892==terrain rate
   + picker filters by this checker]; rule F (item 35 own-active+bit1)
   UNMODELLED, named.
 - POLARITY FLIP SHIPPED: ACTIVE neighbour = LEGAL (jne-exit skips the
   0x386fc xor), ALL-inactive = REFUSE. OrderCellBlock{None,
   ActiveNeighbour} -> PlacementBlock{None, SurfaceVsRing, RockMismatch,
   TerraformSite, NoActiveNeighbour}; test planetgrid_adjacency_t418b
   (which pinned the port's INVERTED reading) REPLACED by
   planetgrid_placement_t418b + orders_cellless_bit1_t418b (bit1 census
   {31,32,33,34,37} pinned vs ordersWithoutCell).
 - UI TWO-STEP (ui.cpp): PLANLIST row click SETS planetPick (no order,
   msg 0x1c02 shape); tile click WITH pick = checker + orderProject, pick
   cleared on accept AND refuse (0x3b487/0x3b419); tile click WITHOUT pick
   keeps the outline affordance; FLAG-bit1 items skip the checker (0x38a5a)
   and order on a miss (0x3b402); PLBUILD click always re-opens the list.
   Witness instrument: planet-view open logs "home-cb cell/size/surf +
   classes"; scripts/tPLB1b_tilepx.py derives tile pixels from the B/C
   tables (never eyeballed).
 - WITNESS PASS (scripts/tPLB1b_buildloop_witness.sh, seed 5 scratch):
   pick Factory (no order) -> non-adjacent 297,376 REFUSED "no active
   neighbour" -> re-pick -> adjacent 314,342 ORDERED. Suite 501/500->501/0.
 - RESIDUES: mutation sweep M8..M17 NOT RUN (foreground timeout blew the
   budget; restore-from-snapshot law above) -> queued as tPL-B1c; sitting
   check ran first (tail rows all turn=1086, no new play, stale assignment
   stood); cmd-numbering label correction banked (queue gates = cmd0 arm
   0x38b8c, tile click = cmd2 0x38a38; port keeps both, labelled).

tPL-B1 LANDED 2026-11-23 (BUILD-LOOP LAW DERIVED + BANKED; SHIP DEFERRED
to tPL-B1b; no OQ row touched — tPL tracks none, honest negative under
strict-close; open=[016,019] unchanged). PROVED (docs/re/_wip_tPLB1.md
F1-F6):
 - F1 TILE CLICK = ORDER STEP 2, NOT a POPUP: msg 0x1c01 branch 0x3b3b6
   verbatim (asm + decompile L535-566): list pick writes rec+0xb2; tile
   click runs checker 0x3830c then writer 0x38840 CMD2; fields cleared
   unconditionally after the attempt (0x3b487). The t428
   "content-dependent popup" premise is VOID for the build path.
 - F5 DECISIVE: adjacency polarity INVERTED in our t418b port — raw asm
   0x38666..0x386fc: ACTIVE neighbour jne-exits WITHOUT xor edi,edi =
   LEGAL; all-inactive zeroes EDI = refuse. t43 static law + planet.txt
   info02 ("Squares adjacent to existing structures ... indicate valid
   locations") corroborate. A flip attempt was REVERTED mid-iteration to
   keep the tree green (code+enum+pins+ui report must flip together);
   full ship spec handed to tPL-B1b.
 - F2 FLAG CENSUS (extracted planitem.txt, loader SHL law): bit1
   {31,32,33,34,37} cell-less items; bit2 {17,28,29,30} build-on-top;
   bit0 {5,21,35,36,38} cell-ban (race-exception arm unverified, NOT
   modelled). F4 XOR leg (item<31: surface-vs-ring) + item-38 adjacency
   exemption confirmed from fresh Ghidra decompile of 0x3830c.
 - SITTING CHECK ran first (r1_t85g_sitting, exit 0): newest trusted
   turn still 1086 in the shared playcap dir (tail rows wall 14:50-15:04
   all turn=1086) — no new sitting, stale assignment stood.

tNG-S S30 LANDED 2026-11-23 (HOVER-ADDER CLOSED BY MEASUREMENT — NEGATIVE;
checklist item 5 done; no OQ row touched — tNG-S tracks none, honest
negative under strict-close; open=[016,019] unchanged). PROVED (docs/re/
_wip_tNGS.md S30-X0..X6):
 - S30-X1 GREEN+REPRODUCIBLE: cmake/build 0, run_tests 500/500, composite
   re-run byte-IDENTICAL (md5 == committed S29 NG-usergrade.png), sitting
   check 20/20 turn=1086 (no new play; r1_t85g_sitting NOT run).
 - S30-X5 HOVER-ADDER NEGATIVE (run dbg-tngh-20261123-130254, scratch
   debugger, pump fire witnessed win 0xfd2310 latch=1): basis-integration
   windows cursor OUT(600,250)/IN(436,446 zone centre)/OUT — UNWRAPPED
   totals 690/678/702 deg over 11.8 s = 58.5/57.5/59.5 deg/s, ratio 0.98,
   reversibility holds => hovering the zone adds NOTHING to cadence. Base
   beat re-measured 58.5+-1 deg/s (agrees S28 60-65; port 62.5 inside
   circuit band). Static corroboration (t423 §5 F2/F7): hover script only
   SETs specnum ds:0x7458e (repaint flag); latch [win+0xc0] never written
   by the hover path. t423-newgame-law.md §5 amended with the closure.
 - INSTRUMENT LAWS BANKED: (1) dosbox-x BREAK-caught stops at the pump leg
   may report eip = BP+6 (next instr boundary after the 6-byte mov
   dh,[esi+0xc0]) — accept BP..BP+6 as a fire (run 124235 lost P0 to the
   strict equality); (2) basis windows >4.5 s at 60 deg/s exceed the
   +-180 wrap — UNWRAP (+360, cap 65 deg/s) BEFORE aggregating medians
   (S28's -62/-78 = 298/642; S30 run-2's -30/-56/-32 = 330/304/328).
 - NEXT = WAIT-USER-GRADE-NG5 (above); items 6-7 are user-priority calls.


tNG-S S29 LANDED 2026-11-23 (SIGN DOUBLE-INVERSION CAUGHT + REMOVED,
MUTATION-PROVED; NG5 PACKAGED; no OQ row touched — tNG-S tracks none, honest
negative under strict-close; open=[016,019] unchanged). PROVED (docs/re/
_wip_tNGS.md S29-X1/X2, steering D24 executed):
 - S29-X1 THE SHIPPED WIRING VIOLATED THE D24 LAW. The D24 check validated
   the menulaw FORMULA at raw +2 deg, never the composition: title.cpp fed
   previewYaw = -newgameSpinDeg (S28-X3), so near-side stars moved RIGHT.
   Composition probe (/tmp/s29_sign_check.cpp, g++ -I rewrite/src): raw +2
   near 200->190 LEFT (== law); shipped negated 200->210->...->248 RIGHT.
   Root read-back: azimuth-increase and near-left are ONE fact about one
   rotation; the camera->star conversion is a single inversion, S28 applied
   it twice. Cadence constants untouched.
 - FIX + PINS (suite 500/500 = 498+2): both negations removed (previewYaw,
   beginYaw); tngs_s29_near_star_moves_left_per_tick (near z=-400 sx
   strictly decreases / far strictly increases per +2 deg tick, 35 ticks —
   window measured strict through 72 deg, flat past ~73 at px quantisation);
   tngs_s29_title_wiring_is_unnegated (source-text: "previewYaw =
   newgameSpinDeg" present, "-newgameSpinDeg" absent).
 - MUTATION-VERIFY (S28-X4 residue CLOSED): M1 previewSpinWorldY=R(-t)
   FAILS 71 incl. both direction pins; M2 re-negation FAILS the wiring pin;
   both reverted, re-run green. PIXEL WITNESS: tNGS4_ours_shot.sh 1095 px /
   774 in-well over 4 s ctrl 0 = animates post-fix.
 - NG5 PACKAGE: scratchpad/NG-checklist.txt cycle-5 (owns the 30x mis-ship,
   CONFIRMS 5.3 s, direction CLOSED-by-user-witness, open 5-7 = hover-adder/
   right-edge/Begin-sprites) + tNGU_composite -> scratchpad/NG-usergrade.png
   1290x1782 18/18 PASS t441 rc=0. docs/DECISIONS.md D24 amended (law stands;
   S29 closes COMPLIANCE).
 - NEXT = WAIT-USER-GRADE-NG5 (above).

tNG-R S28 LANDED 2026-11-23 (PUMP CADENCE MEASURED — USER VINDICATED, SHIPPED
RATE WAS 30x SLOW; no OQ row touched — tNG-S tracks none, honest negative
under strict-close; open=[016,019] unchanged). PROVED (docs/re/_wip_tNGS.md
S28; run dbg-tngr-20261123-103130 rc=0, scratch debugger, cursor parked):
 - PUMP LEG FIRES AT NEWGAME: 12 banked stops 0x27a18, win 0xfd2310,
   latch=1 (bit0) every fire. Pass-1's zero-fires was an instrument artifact
   (leg armed but BREAK cadence lost it) — law banked: a hot-leg zero counts
   only with BPLIST proof + a control fire.
 - CADENCE MEASURED ALIASING-FREE (basis integration): camera fwd azimuth at
   win+0x166 drifts +104/+132/+128/+298/+642 deg over 2.25/2.25/2.25/5.25/
   10.25 s RUN windows (fwd.y constant = pure world-Y; zero drift while
   stopped). Each fire = exactly 2 deg => 28-33 fires/s => 60-65 DEG/S =>
   CIRCUIT 5.6-6.1 s. USER STOPWATCH 5.3 s CONFIRMED; shipped 2 deg/s
   (180 s) REFUTED ~30x; the t302 "~1/s" was OUR POLL RATE on the campaign
   map (REFUTED-ROUTES S28 block); S27-X5 blob fit was twinkle-matching
   (1 s cadence vs ~100 px steps).
 - DIRECTION (checklist #5, newgame): azimuth atan2(fwd.x,fwd.z) INCREASES
   with latch bit0, mouse parked => camera basis +2 deg/fire world-Y =>
   apparent stars -2 deg/fire. SIGN FIX SHIPPED: menulaw.h
   kPreviewSpinTickMs 1000->32; title.cpp previewYaw AND beginYaw negated;
   pins tngs_s28_* (rate + circuit-band 5.4-6.3 s kills slow mutations);
   suite 498/498. RESIDUES: sign not mutation-verified (pixel-free pin owed,
   step 2); clock units/s unmeasured (dump_mem tag collision + DAT_000a2044
   mapping unverified — cadence cited from the basis counter instead);
   scheduler slot layout guess garbage, do not cite.
 - NEXT = S29 NG5 RE-PACKAGE (above).

tNG-S S27 LANDED 2026-11-23 (CYCLE 4 PORT THE SPIN, D22 steering fully
executed; no OQ row touched — tNG-S tracks none, honest negative under
strict-close; open=[016,019] unchanged). PROVED + SHIPPED (docs/re/
_wip_tNGS.md S27):
 - L3 RATE DEBT CLOSED (S27-X1/X2): the "0x28fc0 delay arg" was a
   MISIDENTIFICATION (it is the draw-list builder; 0x2900b/0x2a428 =
   assert with context-id ebx, not a period). Code rate = dispatcher
   0x27a18 imm 2 at 0x27a32 per msg-0x3b tick (t302 ~1/s) = 2 DEG/S,
   world-Y. Newgame IS the state==3 branch (well rect match) => latch
   0x26dd1 ON at init => spins with no input. Agrees with D22 + pixels.
 - PRODUCTION WITNESS (S27-X4/X5, run tngs4-20261123-010308, 61 frames
   @1 s, cursor parked (600,250)): big field ~950 changed px/step ctrl 0
   = ANIMATES; matched bright stars 3.58 px/s = 2.05 deg/s; lag curve
   FLAT lag1..8 (972-993, no dip at 5) — D22's ~5 s/circuit REFUTED by
   pixels (2nd independent flat curve after the vendor's); rotation-
   correlation + single-blob arc = honest negatives (twinkle reclass
   kills continuity; direction NOT recoverable from 1 s pixels).
 - BEGIN CLUSTER (S27-X5): positions STATIC (130/145 matched peaks,
   displacement 0.0) while ~700 px/step churn brightness = the class-
   cycling law; D22's "both spin" holds as the colour sweep. HARNESS
   TRAP banked (S27-X4): missing save/ dir -> autosave modal swallows
   every click (3 false "deaf" fires before root-caused).
 - PORT (S27-X6): menulaw.h kPreviewSpinDegPerTick=2.0/kPreviewSpinTickMs
   =1000 + previewSpinWorldY; previewStar(yawDeg) world-Y BEFORE depth;
   title.cpp ONE accumulator newgameSpinDeg pumps both fields (big =
   POSITION, Begin = CLASS); S22 hover-only advance + per-frame fudge
   REMOVED. Pins: rate, world-Y isometry, wiring (source-text), motion+
   determinism+census; tngs_p4_no_idle_spin_term rewritten SUPERSEDED.
   MUTATION-VERIFY: M1 rate FAILS, M2 axis FAILS (51), M3 detach FAILS,
   M4 sign SURVIVES = named seam (direction unmeasured, checklist #5).
   Suite 498/498 (494+4). OUR PORT ANIMATES: scripts/tNGS4_ours_shot.sh,
   539 changed px/4 s ctrl 0 (pre-port 0).
 - W1 CLOSED-BY-USER-REFCAP (S27-X8, D22 rule 3) + composite
   scratchpad/NG-usergrade.png re-packaged (18/18 PASS t441 rc=0) with
   NG-checklist.txt cycle-4 text: owns the wrong-at-rest claim, states
   the 2 deg/s law with both witnesses cited, corrects the 5 s eyeball
   gently, opens direction (#5) + hover-adder (#6). NEXT =
   WAIT-USER-GRADE-NG4.

tNG-S S26 LANDED 2026-11-23 (D22 adoption + W1 WITHDRAWAL; no OQ row
touched — tNG-S tracks none, honest negative under strict-close; open=
[016,019] unchanged). The harness launched this session on D22 (user,
recorded d997ab6: "both starfields do spin all the time... ~5 s
circuit"), which contradicts the S22 W1 close. PROVED (all measurement,
docs/re/_wip_tNGS.md S26):
 - STATIC (byte-exhaustive): the ONLY base+0xc0 dword stores in obj0 are
   0x26c89 (=0 tail) and 0x26dd1 (=1, state==3) — S14's owed state==0xd
   branch has NO latch store; latch alone cannot explain a newgame spin,
   pointing at the L3 pump family whose RATE was never read.
 - S22's "at-rest" evidence RE-MEASURED and RE-READ: run 215511 frames
   show field changed-px 1147/1152/1145/1146/1153 per 12 s step with
   ctrl=0 — a FLAT floor is equally the signature of continuous motion
   sampled far past its decorrelation time; the tol-6 centroid match
   cannot see >=6 px steps. W1 "does not auto-spin" WITHDRAWN as an
   over-claim (S22's C3 production-fires + dbg-deaf verdicts STAND).
 - VENDOR refcaps (15 shots, 1 s cadence, mouse parked): matched bright
   stars move median 3.16 content-px/s (82% >=1.5 px); changed-px lag
   curve flat 856-889 lag 1..9 with NO dip at lag 5 (ctrl 15-20) =>
   continuous animation CONFIRMED, D22's ~5 s circuit NOT supported
   (~5 s would need ~150 px/s at r~100 — not observed); rotation-
   correlation rate = honest negative (weak, scattered sign). Leading
   rate candidate stays t416 2deg/tick @ ~1/s pump (~180 s/circuit,
   3.8 px/s at r~100) — PRODUCTION 1 s-cadence witness owed (R1).
 - NEXT rewritten to tNG-S CYCLE 4 (PORT THE SPIN): the cycle-3c P4
   port removed idle spin from title.cpp and is now known-wrong; R1
   rate witness -> R2 Begin field -> R3 port+pins -> R4 re-package.

tNG-S CYCLE 3c LANDED 2026-11-22 (ADOPTED — the executing session died
before its FINISH SEQUENCE; a fresh session verified + committed it as
6263f62, then wrote this block. Full record docs/re/_wip_tNGS.md S21-S24).
PROVED THIS ITERATION (measured on production /usr/bin/dosbox-x, scratch
game-wp, fresh Xvfb :97, runs c3-20261122-214652 / 215511):
 - C3 CONTROL FIRED: RFB move(250,295)+click x2 takes production off the
   title (orange 0.679 -> 0.006; hover band teal rows 240..270 -> 280..310).
   => the dbg build dosbox-x-dbg IS input-deaf at a fresh unfocused Xvfb
   (S19/S20 four witnesses explained); R-tNGS3c banked: newgame dynamic
   questions are answered with PRODUCTION + FRAMES, never debugger legs.
 - W1 CLOSED BY MEASUREMENT: the newgame starfield does NOT auto-spin —
   6 frames over 60 s, star-centroid displacement MEDIAN 0.0 px (p90 4 =
   twinkle), field-changed px flat ~1085, control box 0; run 214652
   corroborates (rotation-correlation peak at theta=0). Consistent with the
   S14 static law (latch store 0x26dd1 only in the state==3 cosmos-map
   branch; newgame init tail 0x26c89 CLEARS [win+0xc0]). D21's "rotating" =
   the cosmos map. Scope honest: at-rest field, first 60 s, cursor inside
   the panel; the t423 F7 hover-spin zone law is separate.
 - P4 PORT LANDED: menulaw.h kCosmosCamZ/FovDeg/FocalPx + previewDraws/
   previewStar (3x %1000-500 -> normalize x shellRadiiFor(k), camera
   (0,0,-1500), focal 769.1, +0.5 bias, class ladder, NO sphere clip);
   shellRadiiFor made public; title.cpp t423 cylinder + old sphere sampler
   REMOVED; idle spin REMOVED (F7 zone spin kept). 5 new pins incl.
   boundary-reachability and exact-shell tests; mutation-verified (cls
   220->221 and %1000->%999 both FAIL as intended). Suite 494/494.
   Honest negative: refcap radial-census pin RETIRED (well contains the
   summary text block — R-tNGS3c-B).
 - P5 RE-PACKAGED: scratchpad/NG-usergrade.png 1290x1704 18/18 PASS t441
   rc=0; checklist states honestly: placement law cited, at-rest law
   MEASURED, hover-spin rate = named seam.
 - ADOPTION VERIFICATION (S24): rebuild 0, run_tests 494/494, composite
   reproducible via ~/tools/revenv/bin/python (system python3 has no PIL —
   trap banked), gate 0, ledger OK open=[016,019], ring HEALTHY pid
   1470999, sitting check NEGATIVE. No OQ row moved this cycle (tNG-S
   tracks no ledger row — honest negative under strict-close).
NEXT: WAIT-USER-GRADE-NG3 (assignment above).

--- SUPERSEDED tNG-S CYCLE 3c assignment (EXECUTED; record S21-S24 in
docs/re/_wip_tNGS.md, LANDED block above):

C3 CONTROL (docs/re/_wip_tNGS.md S19/S20 have the full failure chain —
    READ THAT FIRST): on a SCRATCH copy (work/r1/game-wp, never game/),
    launch the PRODUCTION /usr/bin/dosbox-x on a fresh private Xvfb :97
    (copy r299_leg_session launch minus dbg bits; x11vnc WITH
    LD_LIBRARY_PATH=work/r1/localdeb/root/usr/lib/x86_64-linux-gnu —
    required, S18), then RFB (r287_vncinput, offsets 80/100): move(250,295),
    click x2, and key Return. VERDICT: if the production binary LEAVES the
    title (orange <0.20), input works there and the dbg build is
    INPUT-DEAF at fresh Xvfb (hover repaints, presses/keys never fire —
    4 witnesses this iteration: runs 151714/153216/155718/165042). Then
    CLOSE W1 on the S14 STATIC LAW (auto-latch 0x26dd1 fires iff state==3
    => the newgame field does NOT auto-spin; D21's "rotating" = the COSMOS
    map), name the instrument ceiling, and P4 proceeds with NO auto-spin
    for the newgame field (Begin-panel field too — same law).
    If production ALSO does not fire: the fresh-Xvfb unfocused-window class
    is the blocker; try xsend key Return once (it XSetInputFocus first) and
    a 1-s press-hold (move, press, sleep 1.0, release) before concluding;
    if still deaf, W1 closes on the same static law with the ceiling named
    (the verdict is identical either way for the port).
 P4 PORT (spec docs/re/_wip_tNGS.md S15+S19; unblocked by C3 either way):
    newgame starfield = the galaxy generator law (3x rng%1000-500 ->
    normalize -> x shell(k); shell 440 start, -75 step, clamp 50 —
    replaces the t423 FUN_00022728 cylinder AND the splitmix sampler in
    title.cpp:536-600; per-slot shell = shellRadiiFor(n) mapgen.cpp:20,
    type = wheelGal->stars[i].type already wired); camera (0,0,-1500)
    FOV 35 (focal = 242.5/tan(17.5deg) = 769.1 px; shell 440 -> 225.6 px
    fits the 8..492 well); perspective divide + 0.5-bias + viewport
    centre offsets; depth-band sprite classes v=round(d-1500): >220 /
    1..220 / -219..0 / <=-220 -> cos_star 4*type+cls; NO sphere clip.
    Rotation: per C3 verdict — static law says NO auto-spin at newgame
    (Begin-hover faster-spin zone law t423 F7 stays as-is until cited
    otherwise); cam3d.cpp's +-2deg law stays for the COSMOS map.
    Pins: count + radial profile + colour census vs refcap (t441
    newgame regions); mutation-verify changed constants.
 P5 re-package scratchpad/NG-usergrade.png (scripts/tNGU_composite.py
    --checklist; open list MUST state honestly: starfield law cited,
    auto-rotate dynamic witness blocked by instrument ceiling) -> rewrite
    NEXT to WAIT-USER-GRADE-NG3.
GAME: production ring HEALTHY (pid 1470999, TL expiry 2026-11-24 14:53,
turn 1086 20/20 re-verified this iteration; sitting check NEGATIVE).
NEVER pkill Xvfb with -u (matches :9). Kill scratch orphans by exact PID.
KNOWN (do NOT re-derive): Z1 star law S15; W1 static half S14; rotation
+-2deg t416; pump ~1/s t302; projection+camera cycle-1 S5; colour law
tNG-F1; Begin panel /5+5; RFB = only proven firing channel on
production (t439); xsend presses are synthetic (S17); x11vnc needs
LD_LIBRARY_PATH (S18); fresh-Xvfb window origin (80,100) (S18).

tNG-S CYCLE 3b LANDED 2026-11-22 (W1 WITNESS STILL UNDECIDED — honest
negative, NO OQ row moved, open=[016,019] unchanged; the nav failure
chain is now FULLY DIAGNOSED to one control experiment. Full record
docs/re/_wip_tNGS.md S17-S20).
PROVED THIS ITERATION (all measured on real runs):
 - xsend (XSendEvent) presses are SYNTHETIC on this SDL build: the
   XWarpPointer half moves the real cursor (hover repaints — frame diff
   bands 339-370/380-410, ZERO px elsewhere) but the press NEVER fires;
   neutral-first AND same-row-double variants both failed (runs 151714,
   153216, 153535). scripts/tNGS3_w1_framediff.py = the band-diff tool.
 - ROOT CAUSE of the dead RFB channel (all prior tNGS3 sessions): the
   bundled x11vnc died at exec (libvncserver.so.1). FIX = LD_LIBRARY_PATH
   =work/r1/localdeb/root/usr/lib/x86_64-linux-gnu in the Popen env
   (r1_playcap_vnc.sh:158 precedent); verified 0.9.17 starts + accepts.
   rfb_* helpers also carried WRONG offsets (192/184); fresh-Xvfb window
   origin is (80,100) (vision: content 80..720 x 100..580) = r287
   defaults. Both FIXED in r_tNGS3_w1_session.py.
 - With a LIVE RFB channel at correct coords on the dbg build: hover
   lands on New Game and stays (vision 155718 _raw_04), guest RUNNING,
   yet clicks AND key Return (C2, run 165042 after_ng_orange_key=0.679)
   do not activate. => the dbg dosbox-x-dbg at a fresh unfocused Xvfb is
   INPUT-DEAF for activation; the C3 production-binary control (NEXT)
   decides the class. Consequence banked: W1 can CLOSE on the S14 static
   law (auto-latch 0x26dd1 iff state==3 => newgame field does NOT
   auto-spin) with the instrument ceiling named, if C3 confirms.
 - GAME UNTOUCHED: ring HEALTHY (pid 1470999), turn 1086 20/20, sitting
   check NEGATIVE (t368_ring_turn baseline re-confirmed). Scratch orphans
   killed by exact PID only (never pkill -u). ~10 scratch runs under
   work/r1/dbg-tngs3w1-20261122-15*/16* (frames/logs kept for archaeology).

--- SUPERSEDED tNG-S CYCLE 3b assignment (remnant; P4/P5 specs moved into
the CYCLE 3c assignment above):
 P4 PORT (unblocked once W1 lands): newgame starfield = the galaxy generator
    law now fully cited (S15: 3x rng%1000-500 -> normalize -> x shell(k);
    shell 440 start, -75 step, clamp 50 — replaces the t423 FUN_00022728
    cylinder model AND the splitmix sampler in title.cpp:536-600); camera
    (0,0,-1500) FOV 35 (focal = half-width 242.5/tan(17.5deg) = 769.1 px;
    shell 440 -> 225.6 px, fits the 8..492 well); perspective divide +
    0.5-bias + viewport centre offsets; depth-band sprite classes
    v=round(d-1500): >220 / 1..220 / -219..0 / <=-220 -> cos_star
    4*type+cls; NO sphere clip (containment intrinsic). Rotation per the W1
    verdict using cam3d.cpp's already-pinned +-2deg latch law.
 P5 re-package scratchpad/NG-usergrade.png (scripts/tNGU_composite.py
    --checklist) -> rewrite NEXT to WAIT-USER-GRADE-NG3.
GAME: production ring was RESTARTED this iteration (my pkill -x Xvfb -u
hrethric killed Xvfb :9; recovered via r1_playcap_vnc.sh start — HEALTHY
pid 1470999, TL expiry 2026-11-24 14:53, ring banking age 0-5 s). NEVER
run pkill with -u against Xvfb again: it matches the production :9 too.
The ring is now at the resume.gam baseline (turn 1086 class); the t368
sitting test baseline must be RE-DERIVED before the next sitting check.
KNOWN (do NOT re-derive): Z1 star-position law S15; W1 static half S14
(auto-latch 0x26dd1 state==3); rotation +-2deg t416; pump ~1/s t302;
projection + camera cycle-1 S5; colour law tNG-F1; Begin panel /5+5.

--- SUPERSEDED tNG-S CYCLE 3 assignment part 1 (W1 witness remains live
above; Z1 CLOSED, see the LANDED block):
NEXT tNG-S CYCLE 3 — Z-AXIS GEN LAW + AUTO-ROTATE WITNESS + PORT (D21
verbatim: "The original is a rotating sphere containing a volume of
stars in both places. Rather than trying to make something that looks
approximately like that, can we reverse engineer that in the original
and reimplement faithfully in the rewrite?" — grading HELD until this
closes + re-package). CYCLE 2 LANDED (below): P1 CLOSED — the star
source IS the campaign galaxy table (star record +0x30/+0x34/+0x38
float triple, STATE+0xd8d+0x60j law, t441 census); producer
FUN_00028fc0 fills the 21B clip cursor array [win+0xb3] (kind 0 =
stars &LAB_00013bc5+k*0x60), builder FUN_000284bc transforms +0x30
triple via FUN_00053324 and appends visible clips to the [win+0x172]
pointer array (count word +0x572) — the cycle-1 +0x172-vs-+0xb3
confusion is RESOLVED, one table two stages. Rotation law ALREADY
CLOSED by t416 (docs/re/_wip_t416.md F1-F3: +-2 DEG per pump tick
about WORLD Y (L/R) / WORLD X (U/D) on basis [win+0x14e], toggle
latch [win+0xc0], pump msg 0x3b ~1/s t302-measured, no clamp; port
cam3d.cpp implements it). f32[0x9f108] delta-scale measured ~0 in
bank-41 (t416 S-d stands). REMAINING = z-gen law, the newgame
auto-rotate question, port, pins, re-package. ORDER (rationale: W1 is
one dbg session and decides whether the port must auto-spin at all;
Z1 is cheap static and gates source fidelity; port can't be cited
without both; re-package last per D21):
 W1 AUTO-ROTATE WITNESS (dbg build work/r1/bin/dosbox-x-dbg, scratch
    savedir law, t302 BPDEL-before-RUN protocol): to the newgame
    screen (r287_title_nav + positional RFB click law, NEVER Escape),
    BP FUN_000283e4 ENTRY (the rotation writer, NAMED tNGS cycle 2,
    payload 0x283e4); bank edx selector + pushed angle f32 +
    [win+0xc0] twice ~2 s apart. FIRING unattended => vendor
    auto-latches on newgame (find who sets [win+0xc0] bits then);
    ZERO fires => newgame field is STATIC in the vendor and D21's
    "rotating" refers to the COSMOSWnd map — that verdict changes the
    port (no auto-spin) and is itself the measurement.
 Z1 STAR Z LAW: who writes the float at star rec +0x34 (z) at
    new-game? Hunt writers around the mapgen family (OQ-012c shell
    position law is CLOSED for x/y; z is the uncited third axis).
    Measured envelope to reproduce (41.sav T=50, 50/50 decoded):
    x[-412.9,376.9] y[-421.9,436.3] z[-421.3,402.4], radius in
    [50,440], z independent of x/y. If the writer is found, lift the
    law verbatim; if not (static exhaustion class, t212/t213), the
    port draws z uniform-in-envelope as a NAMED STATISTICAL SEAM —
    say so honestly, do not present it as law.
 P4 PORT: newgame starfield = galaxy-table stars (x,y mapgen law + z
    law/seam), camera (0,0,-1500) FOV 35 near 1 far 1e5, perspective
    divide + 0.5-bias round + viewport-centre offsets, depth-banded
    sprite classes v=round(d-1500): >220/1..220/-219..0/<=-220 ->
    shapes 0..3, NO sphere clip (containment intrinsic — our clip is
    the D21 bug); reuse cam3d.cpp basis math for any rotation the W1
    verdict requires (latch law already pinned there); retire the
    ad-hoc shell sampler. Pins: count + radial profile + colour census
    vs refcap (t441_screen_diff newgame regions) + rotation pin per
    W1 verdict.
 P5 re-package scratchpad/NG-usergrade.png (tNGU_composite --checklist)
    -> rewrite NEXT to WAIT-USER-GRADE-NG3.
Budget: cycle 3 of the D18 <=3 rule — HARD cap; anything unresolved
goes on the plain-language open list in the package, honestly. KNOWN
(do NOT re-derive): colour law tNG-F1; Begin panel = SHRUNK same field
(tNG-C F11, /5+5 law); projection + sprite bands + camera FUN_00026a9c
(cycle 1 S5); producer/builder/table chain (cycle 2 S10-S13);
rotation +-2deg axes t416; pump ~1/s t302; capstone =
~/tools/revenv/bin/python scripts/t442_disasm.py; Ghidra bridge
127.0.0.1:8089 live. GAME UNTOUCHED this iteration (turn 1086
baseline re-verified 20/20; do NOT mount the pristine dir).

tNG-S CYCLE 3 LANDED 2026-11-22 (Z1 STAR-Z LAW CLOSED WITH CITATIONS; W1
INSTRUMENT FIXED BUT VERDICT PENDING — honest negative, no OQ row moved,
D21 starfield work tracks no ledger row, open=[016,019] unchanged. Full
record docs/re/_wip_tNGS.md S14-S16).
PROVED THIS ITERATION:
 - Z1 CLOSED (S15): the star-position generator is FUN_00022878
   (work/tNGS3_22878a/b.asm): 3x (rng%1000-500) -> normalize (FUN_00052fa0)
   -> scale by shell radius from the schedule at tables 0x63ac/0x63aa
   (start 440, -75 step, clamp 50). The z-coordinate is REAL (unit-sphere
   direction x shell), replacing the t423 cylinder model and the
   splitmix sampler in title.cpp. P4 focal math pre-computed: FOV 35,
   half-width 242.5 -> focal 769.1 px; shell 440 at depth 1500 -> 225.6 px
   (fits the 8..492 well).
 - W1 static half (S14): auto-latch site 0x26dd1 (COSMOSWnd init, fires iff
   state==3 i.e. the COSMOS map; writer leg 0x283e4, pump leg 0x27a18).
 - W1 witness NOT decided (S16): legs armed 4x via
   scripts/r_tNGS3_w1_relaunch.sh (BREAK lottery ~50%/launch, t286 law), but
   the title->NewGame nav failed for three now-diagnosed reasons: (1) fresh
   scratch title rows sit 200..310 NOT the t287 193..473 table; (2) the
   bundled x11vnc cannot exec this build (libvncserver.so.1 missing) so the
   RFB channel is silently dead — all r287_vncinput moves/clicks were lost;
   (3) xsend's first click only establishes hover (t385b law re-witnessed).
   Script now: xsend-only nav, neutral click then NewGame click (250,295).
   Next session runs the relaunch wrapper ONCE; verdict semantics are in the
   NEXT ACTION block.
 - GAME INCIDENT (disclosed, recovered): cleanup pkill "-x Xvfb -u hrethric"
   matched production Xvfb :9 and killed it (its dosbox was already TL-dead
   since 12:02). Restarted via r1_playcap_vnc.sh start; HEALTHY pid 1470999,
   TL expiry 2026-11-24 14:53, ring banking (45/47.sav age 0-5s). Ring is at
   the resume.gam baseline; t368 sitting baseline must be re-derived. NEVER
   pkill Xvfb with -u again.
 - r287_vncinput.py now honours RFB_PORT (default 5910 unchanged); session
   scripts must run under ~/.hermes/hermes-agent/venv/bin/python (PIL).

tNG-S CYCLE 2 LANDED 2026-11-22 (P1 CLOSED WITH CITATIONS + t416
SUPERSEDURE; no code change, no OQ row moved — D21 starfield work
tracks no ledger row, honest negative: open=[016,019] unchanged. Full
record docs/re/_wip_tNGS.md S9-S13).
(i) CYCLE-1 LEAD REFUTED: FUN_0004709c is the TECH-TREE layout
  generator (iterates RESTREE census WORD[0x74744] stride 0x4b, places
  nodes y=240+30*step+15*(step&1), rotates 360/(slot-1)+0.1*i — asm
  work/tNGS_gen1/2.asm), NOT the star source. reswin.txt absence
  stands but is moot.
(ii) PRODUCER/CONSUMER CHAIN CLOSED: FUN_00028fc0 (cycle-1 mislabelled
  pump-only) appends 21B clips at [win+0xb3]+count*0x15: kind0 stars
  = star-record pointers (&LAB_00013bc5+k*0x60 == STATE+0xdb5), kind1
  lines, kind2 ships; builder 0x284bc kind-0 leg transforms
  [clip_src+0x30] triple via FUN_00053324 (VERIFIED 4x4 affine decomp)
  + 0x53374 perspective -> rec+5/+7/+0xd, appends to [win+0x172] ptr
  array via 0x2974c (count +0x572). Allocation 0x26a4f size count*21.
(iii) MEASURED: star float triple at rec+0x30/34/38 IS the campaign
  star table (t441 census coords match); 41.sav T=50: full 3D spread,
  radius [50,440], z independent — the volume is the GALAXY, D21
  honest-negative branch stays resolved-negative.
(iv) ROTATION: independently re-derived the dispatcher (0x27a18 latches
  [win+0xc0], writer 0x283e4 -> 0x53554/0x53584 on [win+0x14e]) then
  found t416 already closed it (+-2deg world-Y/X, latch semantics,
  cam3d.cpp shipped) — corroboration, not new law; f32[0x9f108]
  measured ~0 (bank-41, P0-anchored via pi/180 const).
(v) PITFALLS banked: guest-physical vs MEMBER anchor slip (P0 =
  member-0x88-X, not B+X twice-over); restored-bin bytes past
  0x8cc83 absent — bss fields (0x9f108, 0xfb0/fb4) must be read from
  SAVES not the image; t441 census script is the star-table reader
  (manual STATE math error-prone, reuse it).
(vi) GAME UNTOUCHED (turn 1086 HEALTHY 20/20 via t368_ring_turn; no
  sitting — r1_t85g_sitting NOT run; no capture session this
  iteration).

--- SUPERSEDED tNG-S CYCLE 2 assignment (executed above; kept for archaeology):
NEXT tNG-S CYCLE 2 — STARFIELD ROTATION WITNESS + FAITHFUL PORT (D21
2026-11-22 verbatim: "The original is a rotating sphere containing a
volume of stars in both places. Rather than trying to make something
that looks approximately like that, can we reverse engineer that in
the original and reimplement faithfully in the rewrite?" — grading
HELD until this closes + re-package). CYCLE 1 LANDED (below): L1
star-table + L2 projection LAWS CLOSED WITH CITATIONS (docs/re/
_wip_tNGS.md S5-S8: 100 stars, 21-byte clips at COSMOSWnd+0x172,
count WORD +0x572; camera pos (0,0,-1500) FOV 35 far 1e5 (FUN_00026a9c);
perspective divide + 0.5-bias (FUN_00053374); depth-banded sprite
classes v=round(d-1500): >220/1..220/-219..0/<=-220 -> shapes 0..3).
The 3D model is REAL (not a 2D fake — the honest-negative branch of
the assignment is resolved: volume exists). REMAINING = L3 rotation
law + port + pins + re-package. ORDER (rationale: P1 is one cheap
string decode and gates the star SOURCE; P2 is THE witness and needs
the dbg build; port/pins can't be cited without P2's axis+rate;
re-package last per D21):
 P1 star source: FUN_0004709c opens 'reswin.txt' (ds:0x24b0 VERIFIED)
    which is ABSENT from the shipped tree -> generator branch is the
    vendor law; decode the FULL generator body (asm 0x471f9..0x47320+
    rng draws over the tech-record census 0x74784 stride 0x4b, then
    the rotate loop at 0x4743d via FUN_0005324c degrees) and lift the
    exact N=100 (x,y,z) law. NOTE 0x4709c's own camera (fov 30, z=-150,
    far 5e4, 320) is a DIFFERENT camera from the COSMOSWnd one — do
    not blend them.
 P2 ROTATION WITNESS (dbg build work/r1/bin/dosbox-x-dbg, scratch
    savedir law, t302 BPDEL-before-RUN protocol): BP at clip-builder
    FUN_000284bc entry; bank [cam+0x14e..0x16e] orientation matrix +
    ret0 twice ~2 s apart => AXIS + RATE MEASURED. If zero fires at
    the newgame screen, the builder is campaign-only — then BP the
    painter FUN_000526b4 and watch the clip record coords rec+5/+7
    across two stops instead.
 P3 pump rate: read FUN_00028fc0 body (delay arg) + census msg
    0x1f6/0x1f7/0x1f9 fires/s. CAUTION: those arms' counters
    (+0xb7/+0xb9/+0xbb, wraps 5/8/3) are read by the HEAD painter
    0x52160 as TEXT-carousel indices (0x524f8..0x5252a) — they may
    NOT be the star spin; do not assume, witness.
 P4 PORT (spec = _wip_tNGS.md S6): 3D star gen, camera (0,0,-1500)
    FOV 35, perspective divide + 0.5 round, depth-banded sprite, NO
    sphere clip (containment is intrinsic — our clip is the D21 bug);
    retire the ad-hoc shell sampler. Pins: count=100 + radial profile
    + colour census vs refcap (t441 regions) + ROTATION pin (two
    shots ~2 s apart, cited rate/axis).
 P5 re-package scratchpad/NG-usergrade.png (tNGU_composite --checklist)
    -> rewrite NEXT to WAIT-USER-GRADE-NG3.
Budget: cycles 2+3 of the D18 <=3 rule. KNOWN (do NOT re-derive):
colour law tNG-F1; Begin panel = SHRUNK same field (tNG-C F11);
painter chain + disasm dumps work/tNGC_paint_head.asm /
tNGC_paint526b4.asm; capstone = ~/tools/revenv/bin/python
scripts/t442_disasm.py; Ghidra bridge 127.0.0.1:8089 live,
FUN_000526b4 created this iteration (save project if prompted).
tNG-S-CYCLE1-ASSIGNMENT (kept for provenance): derive L1 star table /
0x52eb->0x528eb wheels); disasm dumps work/tNGC_paint_head.asm
(0x52100..0x526b4) + work/tNGC_paint526b4.asm (0x526b4..0x52f60);
capstone helper scripts/t442_disasm.py; debugger build available
(RUNWATCH, scratch savedir law, blanket grant).
DERIVE (the three laws, in order):
 L1 STAR TABLE: where do the stars live? candidates: (a) 3D xyz table
    generated at new-game (Borland LCG cluster 0x24f4b is the banked
    new-game seed site — census its draws for a triple/normalized
    vector pattern), (b) pre-baked table in data, (c) 2D-only table
    (then "volume" is FAKE and we say so honestly). Find the table
    base + stride + count (vendor field ~100 stars per tNGF census).
 L2 PROJECTION: how does 3D->screen happen — orthographic drop-one-
    axis, or perspective divide? Read it FROM THE PAINT CODE (the
    0x526b4 body between the event arm and the blit site: look for
    the sprite blit 0x1fc34/0x5d5a1 call and walk backwards what
    computes its x,y args; sin/cos lookup table? multiply by a global
    angle?). Cite every step. The clipping-to-sphere question (user:
    stars must read INSIDE the sphere) is answered by L1+L2: if the
    table is spherical, no clip is needed and our clip is the bug.
 L3 ROTATION: who advances the angle — msg pump (the 0x52eb arm), a
    timer tick, or the main loop? Rate + axis (per D19 the axis was
    wrong; the law says which axis, not us). BOTH fields share the
    painter => one law, two rects (big field + Begin shrunk rect
    (538.1,417.4) r32 per F4).
IMPLEMENT: port the cited laws (table gen at seed time, projection,
angle pump), retire our ad-hoc shell/volume sampler; pins: star-count
+ radial profile + color census vs refcap (t441 regions) AND a
ROTATION pin — two shots ~2s apart, assert the field rotated by the
cited rate about the cited axis (xsend-free: the app pumps it; log
angle per frame behind a debug flag if needed).
CLOSE: both fields rotate on screen (witness pair), mechanical
profiles pass, laws cited FUN-by-FUN in _wip_tNGS.md. Then RE-PACKAGE
NG-usergrade.png (checklist format) and rewrite NEXT to
WAIT-USER-GRADE-NG3. Budget <=3 cycles (D18); if L1 proves a 2D fake,
that IS the faithful answer and ships as cited law.

tNG-S CYCLE 1 LANDED 2026-11-22 (L1+L2 CLOSED WITH CITATIONS; L3 partial
with named instrument; no code change yet, no OQ row moved — D21 starfield
work tracks no ledger row, honest negative for the ledger: open=[016,019]
unchanged. Full record docs/re/_wip_tNGS.md S3-S8).
(i) L1 STAR TABLE CLOSED: painter FUN_000526b4 resolves COSMOSWnd by name
(0x56d8c, ds:0x2bdb VERIFIED 'COSMOSWnd'); count = WORD [COSMOSWnd+0x572]
(sole read 0x52768), table = [COSMOSWnd+0x172] u32 ptr array; records are
21-byte clips (stride proven by builder FUN_000284bc tail += 0x15): +0 shape
bank, +4 skip-flag, +5/+7 screen x/y PRECOMPUTED, +0xd f32 depth.
(ii) L2 PROJECTION CLOSED: perspective divide FUN_00053374 (fdiv [cam+8],
0.5 bias qword ds:0x2c50 VERIFIED, frndint helper 0x76e08) + viewport
offsets [COSMOSWnd+0x574/0x576]>>16; camera init FUN_00026a9c (call chain
VERBATIM in banked dump at 0x52aa1..0x52aad): pos (0,0,-1500.0) [0xc4bb8000],
FOV 35, near 1, far 1e5, orientation identity 3x3 at cam+0x14e. Sprite class
law: v=round(depth-1500) bands >220 / 1..220 / -219..0 / <=-220 -> shapes
bank+0..3 (asm 0x52817..0x5282f+0x52787..0x5279e, Ghidra agrees).
(iii) THE VOLUME IS REAL: not a 2D fake — the assignment's honest-negative
branch is resolved negative; containment is intrinsic to 3D+camera, OUR
sphere clip is the D21 bug class.
(iv) STAR SOURCE LEAD: FUN_0004709c (sole caller = window-parse fn 0x575e4)
opens 'reswin.txt' (ds:0x24b0 VERIFIED) — ABSENT from the shipped tree ->
generator branch is the vendor law: N=100 (x=0, y=k, z=0) init then rng/
rotate passes (degrees primitive FUN_0005324c, DAT_00088b88=pi/180 VERIFIED).
Its own camera (FOV 30, z=-150, far 5e4, 320) is DISTINCT — do not blend.
(v) L3 PARTIAL (honest): pump = self-reposting one-shot FUN_00028fc0; msg
0x1f6/0x1f7/0x1f9 arms inc counters +0xb7/+0xb9/+0xbb (wraps 5/8/3 -> period
120 ticks) BUT those counters are read by head painter 0x52160 as TEXT
carousel indices — NOT proven to be the star spin. The orientation-matrix
writer is UNNAMED statically; instrument named for cycle 2 (dbg BP at
FUN_000284bc entry, matrix dump twice ~2s apart).
(vi) GAME UNTOUCHED (production ring turn 1086 healthy, watcher 1182171 up,
dosbox 1182154 up; NO capture run this iteration; no new sitting — live-
timeline tail 09:46-10:13 all t=1086 in_game=True, no turn change in last
60 MB => r1_t85g_sitting re-run NOT triggered). Ghidra: FUN_000526b4 created
in the live project (was function-less); no image edits.

tNG-F2 CYCLE 2 LANDED 2026-11-22 (V0 all-PASS; F2 REFINED + F3 CODED +
F6 AUDITED + PACKAGE rebuilt with on-image checklist; build ok, run_tests
489/489, gate GATE_EXIT=0; ledger open=[016,019] unchanged — honest
negative: seam work moves no OQ row). Full record docs/re/_wip_tNGF.md.
(i) V0-F1 PASS: warm class 0%->5% (vendor 10%), blue 34%->20% (vendor 16%),
radial r50 147 vs 152 — type-K colour law live on screen.
(ii) V0-F2 -> F2 REFINED: cycle-1 flat black slab was wrong — vendor plate
x503..633 y8..37 is the dark SPECKLE family (census 46.0/34.8/7.1/12.1 over
(0,0,0)/(12,12,16)/(12,12,12)/(12,28,48), anisotropic grain h 8.59/12.26/
16.36 v 5.50/10.35/13.86 [measured]). mapchrome speciesPlateAt (chain 45/50,
salt 0x420e8910b5e72c97 selected so the REALISED 131x30 window matches —
chain propagation otherwise drifts the mix; honest: salt-fit = statistical
match, generator origin named seam). On-screen census 48.6/34.7/4.6/12.1,
grain h 7.17/13.10/16.62 — reads as the vendor backing (vision 4x).
(iii) F3 CODED: menulaw arrowGlyphCovers/arrowGlyphColourAt — 16x17 exact
refcap family grids (6 families), title.cpp px-by-px paint, kArrowFill/
kArrowInk REMOVED. Witness: 272/272 family-match both cells, ZERO blue-box
px; test menulaw_arrow_glyph_law pinned. Named seam: vendor widget record
supplying the glyph uncited (grid = evidence); 4 interior blend px
nearest-mapped.
(iv) V0-F4 PASS: Begin cluster round bbox x511..566 y400..443 (vendor
x510..568 y389..448), multi-colour, dots intact; residuals (ours sprites
smaller/sparser: 17 1-px comps vs vendor 3; dots lean (255,255,255))
banked honestly, on the package open-list.
(v) F6 AUDITED (close form = 1:1 bands + defect list): ONE paint path
(chromePage/textureColourAt) — no second legacy painter. TOP/LEFT/BOTTOM
match on census+brightness; RIGHT x632..639 DEFECT D1: vendor ridge lum
158,309,393,393,362,330,318,314 vs ours 90,265,293,285,285,275,276,295
(~20% dark, ridge shape absent) — root cause: no per-column census for the
newgame right band, falls through to the MAP-screen kRight census. Fix
named for cycle 3; witness scratchpad/F6-bands.png.
(vi) PACKAGE: tNGU_composite.py --checklist renders the plain-language
numbered checklist ON the image (scratchpad/NG-checklist.txt, 7 items: 5
changed 2 open; drafted item 8 REMOVED as unverified — no unverified claims
on the grader's interface). scratchpad/NG-usergrade.png 18/18 PASS,
vision-verified legible.

tNG-F2 NEW GAME FIX CYCLE 2 assignment (executed above; kept for history):
 V0 VERIFY: bash scripts/t412_newgame_shot.sh; then with
   ~/tools/revenv/bin/python: scripts/tNGF_star_census.py /tmp/t412_shots/
   t412-newgame.png (PASS = ours warm class >0% AND blue share drops toward
   vendor 16%); scripts/tNGF_backing_probe.py /tmp/t412_shots/t412-newgame.png
   (PASS = ours header-zone points go black (0,0,0) in the plate rows);
   vision side-by-side /tmp/tNGF_begin_ref.png vs a fresh ours-crop (Begin
   cluster round, multi-colour, dots intact). If a check FAILS, fix root
   cause first; bank verdicts in docs/re/_wip_tNGF.md.
 F3 SCROLL ARROWS (measured, not yet coded): replace the blue kArrowFill
   boxes at kRaceArrowUp/Down with the cited glyph map (scripts/
   tNGF_arrow_map.py output, banked _wip_tNGF F3): navy well (12,32,48),
   dark-slate frame (34,60,74) + mid (79,116,126), cyan triangle body
   (123,171,177) bright (168,227,229) highlight (190,255,255); UP apex
   row 51 base rows 60..62 x619..629 (cell x617..631), DOWN mirror y357..372.
   Pin pure-law arrowGlyphAt in menulaw.h + test.
 F6 FRAME TEXTURE REST OF SCREEN: audit which paint path covers the
   side/bottom bands in RaceConfig vs the tA2 generator (top bar close per
   user — do NOT touch sharpness, user-deferred). CLOSE = 1:1 side-by-side
   of ALL four bands vs refcap + written defect list (G1).
 PACKAGE: rewrite scripts/tNGU_composite.py output scratchpad/NG-usergrade.
   png WITH the PLAIN-LANGUAGE NUMBERED CHECKLIST ON THE IMAGE (D20
   usability correction: what changed / what to look at / what stays open —
   machine wip is never the grader's interface). Then rewrite NEXT to
   WAIT-USER-GRADE-NG2 (same resume rules as WAIT-USER-GRADE-NG).
F1 NEW GAME FIX CYCLE 1 (2026-11-22) = LANDED below. Original assignment:
 F1 STARFIELD COLOR + VOLUME (user: "stars... are all one color, and
    they don't appear to be contained within a volumetric sphere").
    Multi-color law: the vendor star palette is a RECORD/palette
    question — census the newgame starfield painter (tNG-C cited
    0x52114/0x526b4) for the color-selection source (pal indices per
    star? record k-frames? per-star random index from the SAME seed
    draw?); the refcap newgame-original.png has the ground-truth color
    census (reds/oranges/blues/whites per D19). VOLUME containment:
    stars must read as INSIDE a sphere (dimmer/denser toward the
    shell, none outside) — compare our render vs refcap radial density
    profile; the tNG-C3 shrunk-field law may apply per-star clipping
    the viewport not the sphere. Pins: radial profile + color-class
    histogram vs refcap (mechanical, t441_screen_diff region).
 F2 PLAYER SPECIES BLACK BACKING (user: "missing the black backing to
    the Player Species box in the upper right"). windows.txt NEWGAMEWND
    child census for that box: is the black a window STATE/paint or a
    record? cite + paint (the refcap shows pure black behind the three
    portraits inside the frame).
 F3 SCROLL ARROW STYLE (user: "arrow buttons... still the wrong style
    and color"). The vendor arrows are SMALL glyphs in the chrome
    recess (refcap: tiny light triangles top/bottom of a groove), not
    blue boxes. Find their record (widget lib per SHAPEFRAME or the
    painter's own blit; tNG-C painter region) and blit cited art.
 F4 BEGIN-PANEL STARFIELD RECT (user: "taking up too much of the frame
    and not spherical"). Field must be clipped to the sphere volume
    inside the panel (refcap: round field, generous black margin);
    our rect-fill = wrong clip. Cite the clip from the painter
    (same 0x52114 family), fix, pin dims+round-profile.
 F5 BEGIN-PANEL PORTRAIT SIZE/CENTER (user: "species art in the green
    circle... drawn too large, cropped, and not perfectly centered").
    Portrait circle CENTERED in the green ring at the ring's inner
    diameter (tA1 dims law applies; check the center math against the
    ring rect, not the panel rect). Pin: center offset <=1px + dims.
 F6 FRAME TEXTURE REST OF SCREEN (user: "the rest of the frame is
    still the old wrong texture" — only the TOP BAR is close).
    tA2's single generator evidently reaches the top bar but the
    side/bottom bands still show the legacy look: find WHY (second
    paint path still live in newgame specifically? different band
    widths sampling the field wrong?). CLOSE = side-by-side of ALL
    four bands vs refcap at 1:1, defect list written against the
    original (G1). Top-bar SHARPNESS nuance = POLISH BACKLOG, user-
    deferred, do NOT touch.
FINISH: re-package scratchpad/NG-usergrade.png with the NEW PLAIN-
LANGUAGE CHECKLIST format (D20 usability correction: numbered plain
lines ON the composite image — what changed / what to look at / what
stays open; wip docs = machine record only, never the grader's
interface). Then rewrite NEXT to WAIT-USER-GRADE-NG2 with the same
resume rules. Budget: <=3 cycles per D18; anything unresolved goes on
the open list in plain language, honestly.

tNG-F1 CYCLE 1 LANDED 2026-11-22 (D20 F1/F2/F4 CODE + F5 MEASURED-CLOSED;
F3/F6 OPEN -> tNG-F2; ledger open=[016,019] unchanged — honest negative:
this cycle moves no OQ row, PHASE-17 seam work; build ok, run_tests
488/488, gate GATE_EXIT=0). Full record docs/re/_wip_tNGF.md.
(i) F1 ROOT CAUSE MEASURED: cos_star.shp decoded (S9 walk; FIRST census used
a wrong (count,val) grammar — corrected in-file) = SEL=4K+cls grid, ONE
bright-ramp per star TYPE (K0 blues, K2 reds, K3 oranges, K5 tans, K6/K7
pinks/reds); our K=0 named seam = the "all one color" defect. Code: preview
rec = 4*type+cls, type from the wheel galaxy (count law ties N since tNG-B
B1); dims-zero cells k40..k51 (types 10..12, cited t200) draw NOTHING ->
skipped honestly. Refcap census: vendor warm 10% blue 16% vs ours warm 0%.
(ii) VOLUME adjudicated: big-field radial profile ALREADY matches (r50
148v152, r90 188v189) — the sphere complaint is the BEGIN PANEL: vendor
star cluster = circle centre (538.1,417.4) r99=31 bbox 59x60 (dots are
panel-wide hash, 778/799 dot px OUTSIDE the cluster — different family).
F4 CODE: /5+5 law KEPT, fit-to-circle + hard clip + type-K colours there.
(iii) F2 MEASURED + CODED: pure-black plate rows 8..37 x503..633 behind
"Player Species" (vendor 32% lum<12, ours 0%); RACELIST navy well already
matches (7racesel k0..k7 = solid pal242 (12,32,48), file-decoded).
(iv) F5 MEASURED-CLOSED NO CODE: vendor hole content bbox x578..622
y395..440 centre (600.2,417.7) == ours (599.8,418.0) <=0.4px, identical
radial profile (rmax 28.0 both) — D20 witness pre-dated the tNGC3 clipR=23
clip; vision: full composition, not a crop.
(v) UNIFIED-FIELD HYPOTHESIS REFUTED (scripts/tNGF_field_match.py): big
field vs Begin panel star sets match 2% — different sets, consistent with
t423 F8/F9 (preview table vs galaxy walk). Preview-table static consumer:
still ZERO (D19 negative re-confirmed).
(vi) TOOLS new: tNGF_star_census.py, tNGF_field_match.py,
tNGF_refcap_probe.py, tNGF_backing_probe.py, tNGF_header_arrow_geom.py,
tNGF_box_geom.py, tNGF_arrow_map.py, tNGF_begin_probe.py (all
~/tools/revenv/bin/python). F3 glyph map + F6 pointer in NEXT.
CAVEAT: F1/F2/F4 code is UNWITNESSED (no graded fresh shot this cycle) —
tNG-F2 V0 is the gate before packaging.

tNG-C2 CYCLE 2 LANDED 2026-11-21 (NEW GAME CONTENT IMPLEMENTED — planet
index + chip row laws in code, pinned, mutation-proven; ledger
open=[016,019] unchanged, seam work, NO OQ row moved — honest negative:
this row's laws have no OQ row by design, they are PHASE-17 queue work).
(i) DESC PLANET = smhome.shp k<race row> NATIVE 52x52 at screen (382,191)
(title.cpp smhomeLib; kDescPlanetCentre {406,217} = NEWGAMEWND X0/Y0 +
push (72,205); bbox census (-24,-26) F13) — the t414 planets-ladder
invention REPLACED. (ii) CHIP ROW = SEVEN raceflag ramp blits at
(381+16i,433) via NEW blitShapePalRamp/chipInkSlot (slots 16..19 :=
pal[16+4i..19+4i], 0x53ee0 law; navy 242 + strays identity) +
selected-chip frame (white hlines 434/458, grey vlines 435..457,
refcap-measured); t401 constants superseded, kPlayerChipRgb DELETED (the
D19 "2 rows of solid swatches" root). (iii) HARNESS: desc-planet region
cited ("fixed",(52,52)) + widened rect; NEW playercolor-chiprow region
(tight-to-content rect law — the padded task rect saturated the NAVY
detector, banked); t441 newgame 18/18 PASS. (iv) PINS
test_newgame_content_tNGC.cpp x4 (smhome class+anchor, ramp slot law+
geometry+frame, raceflag data+ink-domain census, wheel bijection wrap
terms) all ok; ctest 0 failed. (v) WITNESS scripts/r1_tNGC_chip_witness.py
GREEN on BOTH sides: chip-i brightest ink == pal[4i+19] EXACT i=1..6,
framed-chip count == 1, framed-chip presence check (brightest test is
frame-polluted on both sides — banked), planet 51x51 vendor / 51x50 ours
(52+-2 law). (vi) MUTATION 10/10 CAUGHT (scripts/r1_tNGC_mutate.py:
M1-M8 constants via tests, M10 family-zero + M11 frame-off via live
witness; launch guard + md5-verified restore, AFTER-RESTORE tree clean).
(vii) SS12 READING CORRECTED in t423-newgame-law.md (7 blits not 8,
4-slot rewrite not 5-entry ramp, white FRAME not 0xf3 well) + SS14/15/16
banked. Full detail: docs/re/_wip_tNGC.md F13/F14.

tNG-C CYCLE 1 LANDED 2026-11-21 (NEW GAME CONTENT MEASUREMENTS —
MEASUREMENT-ONLY, NO CODE DELTA; budget exhausted before implementation,
cycle 2 queued above; ledger open=[016,019] unchanged, seam work, NO OQ
row moved). All laws in docs/re/_wip_tNGC.md F1-F12 (hand-authored),
disasm windows work/tNGC_paint526b4.asm + work/tNGC_paint_head.asm.
(i) STATE-3 PAINTER CHAIN cited: head 0x52114 (sole caller of body
0x526b4 at 0x52174; both GAP fns — capstone, Ghidra has no fn there).
FIELD PAIRING LAW (F7, the key unlock): every "dword[win+0xbN]; sar 16"
== word[+0xbN+2]: +0xb3 SELECTED RACE ROW, +0xb5 player colour, +0xb7
density 0..4, +0xb9 species count 3..7 (wrap 8->3), +0xbb atmosphere
0..2 (wrap 3->0). (ii) PLANET INDEX LAW CLOSED (D19 seed #2): DESC
planet = smhome.shp k<selected race row> NATIVE 52x52 at window-rel
(72,205) = screen (382,191) — name fetch 0x5231d "DATA\smhome.shp"
(payload 0x85751) + 0x5caac push law + bbox (-24,-26); assert cmp 0x15
== 21 recs. Port's planets.shp k[(sel%11)*5+1] = invented, REPLACES in
cycle 2. (iii) CHIP LAW CLOSED (D19 seed #4): raceflag k<sel> blitted
7x at (381+16i,433)..(395+16i,463) with palette slots 16..19 :=
game.pal[16+4i..19+4i] (0x53ee0 decompile = 4-slot rewrite + tinted
blit) + white 1px frame on the player's chip (0x2fe04 4-line family);
REFCAP WITNESS: chip-i brightest ink == pal[4i+19] EXACT i=1..6, chip0
green + white frame (work/tNGC_chip_cols.py). (iv) WHEEL CHILD LAW:
parent writes child[win+0x67][j]->+0x72 = density verbatim / count+2 /
atm+10 — windows.txt k0 is pre-runtime; port's newgameWheelFrame
bijection CONFIRMED, cycles already match (no delta). (v) BEGIN
STARFIELD answer (D19 open q): SHRUNK VOLUME — full-field coords /5 + 5
(idiv 5 at 0x527a4/0x527c9), NOT same-field-scaled. (vi) 0x52389 crest
call REASSIGNED to RACELIST row0 flag (rect 193,107 win-rel) — DESC
crest index stays a named caveat. PITFALLS banked: boot-patch table
0x32f1 entries are CODE patches {u16 0x1007,u24 site,u24 imm} not
slot writes (t442 P3 reading re-verified); shp bbox quad is i32x4 at
stream-0x10 (shorts misparse = garbage dims); patch tool silently
consumed an adjacent "## F5" header twice when old_string was the
header itself — re-add the header in new_string. GAME UNTOUCHED (turn
1086 HEALTHY, sitting test run this iteration). Build/tests untouched
(NO code delta).

tA3 TEXT LAW LANDED 2026-11-21 (PHASE-17 STAGE A ROW 3 CLOSED — Stage A
(tA1 blit scale + tA2 chrome + tA3 text) COMPLETE; ledger open=[016,019]
unchanged, seam work). (i) FONT-FIELD LAW: TEXTITEM face fields 0/2/3
ALL render the BIG face — measured decisive at all three (rail iou
1.000 vs sm 0.24-0.37 palette-exact map refcap; control labels big
0.80-0.85 vs sm 0.21-0.30; title t392); smfont = body text only (lore
8-row bands, sm>big). (ii) BASELINE LAW: TEXTITEM draw TOP = y0+dy
VERBATIM (rail dy=2 EXACT, root=window+40); rail cell x = x0+2; centred
x = (x0+x1)/2 - adv/2; browser drift +-1 per window banked as a PITFALL
(pre-tA3 kNameTop/kHeaderTop/kSummaryTop were raw-row errors off by 1;
lore drew 7 px high). (iii) CODE: rail labels bigface kRailInk
(255,255,255) at x0+2/y0+2 (D19 "button text too small" root cause);
control/PlayerColor/header/name/summary/Begin labels bigface
kNewgameInk; kNameTop 17, kHeaderTop 15, kSummaryTop 326, kLoreTextTop
265 new; title untouched (t392 palette). (iv) WITNESS GREEN:
scripts/r1_tA3_capture.sh + r1_tA3_witness.py — ours 11/11 sites big-
face iou 0.935-1.000 + core255 frac 1.000 + first-ink-row baselines
exact; vendor 8/8 static sites big wins (dynamic-word sites SKIP per
tA1-CONT contract). CLOSE term met: ours-vs-law 0 px (<=1px). (v)
MUTATION 12/12 CAUGHT (8 pins + 4 witness; honest two-run record
_wip_tA3 F6 — a killed foreground run poisoned run 1's snapshot; M7
re-verified CAUGHT on a green tree; launch-guard added). Pins
test_textlaw_tA3.cpp x3. Build 0, ctest 475 0 failed, gate 0, ledger
audit OK open=[016,019]. LAW HOME: docs/re/typography.md (hand-
authored; fnt.md/text.md are generated — never hand-edit).

tA2-CONT CHROME CLOSE LANDED 2026-11-21 (all five items; ledger
open=[016,019] unchanged, seam work). (i) RIDGE CHAIN-ANCHOR FIXED:
newgameWellEdgeColourAt recursion now excludes rows 373/374 entirely
(vendor census proves per-row rung draws: grey 169/169, teal 108/107 —
not a vertical carry; the 374->373 variant rejected on stationary math
~92.7). Witness scripts/r1_tA2c_witness.py: ridge 64.4/103.1 vs vendor
64.5/102.8 (was 50.6/90.4), recess row7 22.5/24.3, col7 6.5/6.5, col493
19.1/22.9, well rows pure black — WITNESS PASS. (ii) HARNESS: 10
chrome-band regions kind='band' ADDED to scripts/t441_screen_diff.py
(mean-lum window + exact-census family share both sides; row0 geometry-
only per t433 per-instance law); newgame 17/17 PASS, planetslist 2/2
PASS unchanged. (iii) MUTATION 12/12 CAUGHT (scripts/r1_ta2c_mutate.py;
pin strengthened first with band-mean + exact-colour-share windows —
mean alone blind to weight swaps, proven by M4/M5 caught only by shares);
AFTER-RESTORE 472 tests 0 failed, md5 -c pristine OK. (iv) APPLICATION
VERDICTS cited, no change: map frameTex 100.00% pixel-exact bands (right
deviations = windows.txt widget rects); title = 0opening.gif single
RenderCopy, no kBevel site. Banked chrome.md 3a + _wip_tA2 F7-F11. Build
0, ctest 100%. FULL DETAIL: docs/re/_wip_tA2.md + docs/re/chrome.md 3a.

tA2 LANDED 2026-11-21 (CHROME LAW ROUND 2 — double-layer RESOLVED, bar
extent FIXED, bevel law MEASURED; ridge bias + harness bands owed via
tA2-CONT; ledger open=[016,019] unchanged, seam work). (i) DOUBLE-LAYER
VERDICT: grep + pixel-exactness (static-texture argument) prove ONE chrome
generator pass per screen — map left/bottom/top bands 100.00% exact vs a
textureColourAt field dump; right-column deviations = windows.txt widget
rects exactly; newgame chromePage pixel-exact everywhere except the
designed t401 dot band. The D19 "almost-right bar ON TOP of the older
rougher frame" root cause = the port's bar EXTENT: kNewgameCosmosRect
{8,9,493,373} exposed two BRIGHT chrome rows 7-8 where the vendor shows a
1-px DARK RECESS row 7 + pure-black well from row 8. (ii) BAR EXTENT LAW
(browser shot +1,+1; pure refcap for the map bar): gradient rows 0..6,
recess row 7 x7..493 (mean 24.3), well 8..372 x8..492, RAISED RIDGE rows
373..374 (dark rung row 64.5 + same-x-quantisation light rung row 102.8 =
DARK-ABOVE/LIGHT-BELOW everywhere; light never appears above a fill edge).
PITFALLS banked: browser-vs-refcap row-0 means differ per t433 repaint
INSTANCE (never infer offsets from one row); refcap png row = screen+40.
(iii) IMPLEMENTED: newgameWellEdgeAt/ColourAt (per-edge vendor censuses,
full 98.5%-mass ridge tables) painted INSIDE the one chromePage pass (G6);
kNewgameCosmosRect -> {8,8,492,372}; FOUR symmetric kBevel outlines
replaced by newgamePanelTopAt/LeftAt dark-inset law (right/bottom = no
line, 91/91 + 115/116 flat-fill witnesses); Begin panel fill moved to the
MEASURED kBeginPanelVisual {502,381,632,472} (gutter x494..501 no longer
navy; hit rect unchanged). (iv) MINERAL CENSUS (item 3): run-length ratios
match vendor +-0.03 on all three band classes; residual = lag-1 luminance
step 1.58x too jumpy (ramp-adjacent fresh-draw rule uncited) — NAMED
CEILING re-quantified, no guessing attempted. (v) WITNESS post-fix: row7
22.5 (vendor 24.3), col7 6.5 (6.5), col493 19.1 (22.9), well 100% black;
ridge 50.6/90.4 vs 64.5/102.8 = the NAMED chain-anchor defect for
tA2-CONT. Build 0; ctest 100% (new pin mapchrome_tA2_well_edge_law);
gate GATE_EXIT=0; ledger audit OK rows=20 open=[016,019].

--- SUPERSEDED tA1 ASSIGNMENT (law landed; only the CLOSE remains above) ---
NEXT tA1 BLIT-SCALE LAW (PHASE-17 STAGE A FIRST — see the PHASE-17 QUEUE row tA1 verbatim; ordering rationale: user D19 ruling 2026-11-20 — one blit-scale law explains the quadrant family on newgame portrait/species column/planet art AND planets-list art; fix the law before per-screen content gates). Trigger check FIRST: USER: lines after the D19 block in docs/DECISIONS.md win.

DO, in order (all inputs are in docs/re/_wip_t442.md P3/T-OPEN + the ui-runtime.md
"t442 ... PARTIAL" block — READ THOSE FIRST; do NOT re-run t442's censuses):
(1) BOOT TABLE: parse 0x32f1..0x3478 as 9-byte entries {u16 val, u16 0x1007,
    u32 dst} (anchor pattern '07 10' at entry+2; 42 entries; t442's first-entry
    parse at 0x32f1 is correct, its 10-byte walk desynced). Produce the full
    slot map: which val lands at 0x6fd44/0x6fd52/0x6fd96/0x6fd9a (word slots the
    painter reads) and the capacity words. NOTE static bytes at those slots are
    PRE-PATCH; the table is the runtime ground truth.
(2) DISASM 0x2c4ec..0x2c7c5 (the pre-loop half of the same GAP function; entry
    ~0x2c053/0x2c0be prologue region) tracking registers esi/edi/ebp from the
    window-object fields [esp+0x2c8]/[esp+0x2d4] (windows.txt RACE_k rects are
    x474..632 pitch 39 — compare against the pitch-62 strip) and locating EVERY
    fetch of word[0x6fd52+2*o] vs word[0x6fd44+2*k]. The discriminator: the
    r=170 ring painter MUST produce centres ~ (234,238)+170*{0,90,180,270deg};
    the race-list painter produces x>=474 rows. sin/cos helpers 0x77514/0x77556
    have only 5 call sites total (P3) — check them.
(3) If (2) finds the ring painter: read its slot->position construction verbatim
    (integer math or table — NO float-170 constant exists), and settle t441's
    n>4 named caveats (angle pitch, count filter, ring index). If the law
    DIFFERS from the port, upgrade ui/speciesmenu.{h,cpp} + ui.cpp state-7 block
    and re-pin against tests/test_speciesportrait_t441.cpp (mutation-verify each
    changed constant). If it CONFIRMS, cite addresses and say so.
(4) BANK in ui-runtime.md (hand-authored) + _wip_t442.md (continue it; do not
    create _wip_t443.md until P3 is resolved).
(5) LEDGER: seam work, touches no OQ row. If the region names a relation field
    relevant to OQ-016, note WITHOUT closing.

GAME STATE t443 STARTS FROM (re-verified t442 end): production pid 1182156
HEALTHY (TL expiry 2026-11-22 12:02:26, watcher 1182171), ring turn 1086 on
20/20 saves (scripts/t368_ring_turn.py — the sitting test; live-timeline.jsonl
growth is NOT the signal, t439 law). SITTING CHECK: run t368_ring_turn.py; turn
> 1086 means the user played -> re-run scripts/r1_t85g_sitting.py BEFORE the
task. Ghidra headless :8089 is UP and PROGRAM ANALYZED (1143 fns; t442 ran
run_analysis — decompiles work again).

SEAMS carried: T433-C chrome generator seed/state (live debugger only, NOT
queued), H3 race bytes 1..20, T428-B, T427-A..F, gizmo-icon rows + class
selector (t434b), research panel art join D3 (t435 F6). CLOSED t441: T436-A,
T436-B (do not re-open; R-t441 in REFUTED-ROUTES.md).
OPEN-LEDGER HANDOFF STATE (unchanged from t440): OQ-016 = USER ADJUDICATION per
D3 (residue list EXHAUSTED; Phase-Bomb sub-capture machine-closable but needs a
Phase-Bomb fleet built first); OQ-019 = user acceptance of the per-ship sim +
debugger-class witness (t298 budget law, REFUTED-ROUTES.md:465-467). RULING
CHECK t441: find work/r1/d1page -newermt 2026-11-20 11:52 = EMPTY -> D2/OQ-019
acceptance still PENDING. NO GIT REMOTE (deliverables = local commits).

tA1-CONT LANDED 2026-11-21 (BLIT-SCALE CLOSE — tA1 CLOSED; harness built,
witnesses green, mutation-verified; ledger open=[016,019] unchanged, seam
work). (i) scripts/t441_screen_diff.py BUILT (G2 single home; region tables
newgame 7 regions + planetslist 2). CONTRACT: port prints one-shot "ui
dimscheck <name> W H x y" (cited bbox dims + dest anchor) at each gated
blit — title.cpp x5 (desc ring/portrait/planet, racelist rows), ui.cpp x2
(row sun/planet); harness crops our render at the declared rect and asserts
the measured content bbox FILLS it (>=0.85 cited, <=cited+2) — the D19
quadrant slice (~0.5x) fails by construction; vendor side = presence mass +
cited-ladder/fixed witness (crops are DIFFERENT campaign states by design;
content equality is tNG-C/tPL-C territory, NOT claimed here). (ii) VERDICTS:
newgame 7/7 PASS (ours ring 109, portrait 100x100 == vendor 99..101,
desc-ring band 107x106 BOTH sides, desc-planet 37x38 on ladder — the +1
size-index correction CONFIRMED by the harness), planetslist 2/2 PASS (ours
sun 107x107 vendor 130x126 both on the suns ladder; ours planet 37x38,
vendor 68x69 on the size ladder). QUADRANT SIGNATURE GONE on both screens.
Vendor crop rects: newgame game-rect +1,+1 CONFIRMED by texture-band scan;
planets row0-planet vendor rect re-anchored y80..160 (header divider at
y66-68 contaminated the y60 top — banked as detector pitfall).
(iii) MUTATION 9/9 CAUGHT (checkpoint commit d719e33 first; every restore
md5-verified): kRacePortraitScale, kStatusArtScale, kSpeciesPortraitScale,
kSpeciesPortraitClipR, kSpeciesRingHalf, kFieldRecordW, kFieldRecordH,
poppanel want-table, stripGauge width 108. AFTER-RESTORE build 0; ctest
100% (62s); gate.sh GATE_EXIT=0; ledger_audit rows=20 open=[016,019] OK;
ledger_index_check OK. (iv) HONEST LIMIT banked _wip_tA1 F6: the CLOSE
proves the SCALE LAW (fill + ladder), not pixel equality vs the crops; the
tNG-U user-grade park does same-state side-by-side vision. F3 (affine
scale direction) stays a named static seam — unneeded by any port site.
(v) GAME UNTOUCHED (turn 1086 HEALTHY, sitting test run this iteration).

tA1 LANDED 2026-11-21 (BLIT-SCALE / BBOX-DIFF DIMS LAW — the D19 quadrant
family root cause; ledger open=[016,019] unchanged, seam work, CLOSE owed
via tA1-CONT). (i) TRUE DIMS LAW [verified decompile FUN_00061058 =
(short)[hdr+0x10]-[hdr+8]+1 bbox DIFFERENCE; FUN_0006108c returns (L,T),
0x5d5a1 places anchor+(L,T)] + EXACT-SPAN CENSUS over all 165 libs:
bbox-at-stream-0x10 completes 1413/1436 (1403 exact-span + t197 cross-span
class), old u32-pair law 31/1436 and every one of those is the SAME quad's
corner/canvas re-read (zero regressions, script-measured). Four witnesses
banked _wip_tA1 F2 (code/census/pixel-render/measured-drawn-sizes 1:1:
suns k1 130x127 vs drawn 130x126; racering 109; smrace 100; planets k1 38
vs zone 37). The port's fake 2x scales (portrait/ring/statuslist) were
COMPENSATING the port's own truncated dims read — the vendor blits NATIVE.
(ii) CODE: shp.{h,cpp} parse = bbox-diff, Record.left/top; render sites
title.cpp DESC ring+portrait+planet (size idx +3->+1 cited: ladder
{24,38,52,71,95}, measured zone matches 38 only), RACELIST rows, ui.cpp
state-7 portraits+rings, planets-list sun+planet — all NATIVE at
anchor+(L,T); constants kRacePortraitScale/kStatusArtScale 2->1,
kSpeciesPortraitScale 1/ClipR 50/RingHalf 55, kFieldRecord 626x358,
poppanel {9x9,6x9,8x8}, stripGauge width 108 (heights vary per record —
dropped from identity term). (iii) PINS RE-CITED to bbox values x12 test
files (mapchrome/sysview/resface parity becomes FULL-INCLUSIVE-RECT; the
old minus-1 parity WAS the misparse; suns/planets/raceflag/racering/smrace
ladders re-measured; cos_star k40..k51 + sg50expl k9 = 1x1 degenerate
placeholders that DECODE; 1starmap k1 0x7FFFFFBB variant decodes 3x3 —
old rejects were misparse artifacts). SUITE ctest 100% (62.25s).
(iv) HONEST NEGATIVE: the affine blitter's 16.16 scale direction stays
UNRESOLVED statically (C3-F8 pitfall stands; not needed — 1:1 reproduces
every measured witness); tA1's CLOSE (t441_screen_diff.py harness, 1:1
render witnesses, mutation verification) is OWED — see NEXT tA1-CONT.
(v) GAME UNTOUCHED (turn 1086 HEALTHY, sitting test run this iteration).
t442 LANDED 2026-11-20 (STATE-7 PAINTER HUNT — PARTIAL, region located; seam
work, ledger open=[016,019] unchanged, NO OQ row moved, no code delta).
(i) PAINTER REGION = unindexed GAP 0x2b3d2..0x2cf04 (functions_full.tsv ==
Ghidra's 1143 auto-fns exactly, so GAP bodies are invisible to both — capstone
via scripts/t442_disasm.py). One GAP fn dispatches on byte[0x43510] through
jumptable 0x2bf90 into the painter arms. (ii) SHAPE-SLOT INDIRECT LAW [verified
disasm]: no RACERING string exists in the image (0 hits, any case) and no float
170.0 (f32/f64); a 9-byte boot table 0x32f1..0x3478 {u16 val,u16 0x1007,u32 dst}
(42 entries) pre-seeds word slots 0x6fd44 (per-row shape), 0x6fd52 (per-player),
0x6fd96 (ring), 0x6fd9a + capacities; the painter fetches FUN_0001fc34(0x9f10c,
word[slot]) then blits 0x5d5a1/0x53dd8. (iii) Overlay loop 0x2c823..0x2c90a:
bound dword[0x13b96]>>16 (race-count mirror — the painter does NOT read
word[STATE+0xd88]; exhaustive disp32 census in _wip_t442 P2), per-row shape +
ring shape + relation gate byte[0x12e16+k+player*0x1ee+0x1c0]==3/2 -> ebx 8 vs
skip; strip pitch 0x3e with k==4 override — ATTRIBUTION OPEN (race-list strip vs
r=170 ring; t441 image laws stand either way, nothing contradicts them).
(iv) RULED OUT by decompile (reasons banked): 0x2635c, 0x2547c, 0x41260,
0x196c8, 0x19e94, 0x284bc, 0x2925c, 0x3aa0a, 0x156d4 (state-setter: msg 0x320
obj+0xab=STATE, obj+0xb9 mode, vtable+0xc repaint), 0x28fc0 (draw-list builder:
stars/anomalies/colonies only), 0x53fe8 (screen save/load; reads
byte[0x12e17]=specnum, [0x12e18]=colour, word[0x12fd3+o*0x1ee]=relation-to-player
— SECOND WITNESS that display code keys on specnum/colour/relation, consistent
with t441). (v) GAME UNTOUCHED (turn 1086, HEALTHY); gate.sh GATE_EXIT=0;
ledger_audit rows=20 open=[016,019] OK; ledger_index_check OK. NEXT t443 =
finish the region attribution (boot-table slot map + 0x2c4ec..0x2c7c5 disasm).

t441 LANDED 2026-11-20 (SEAMS T436-A + T436-B CLOSED — species-screen portrait
law measured offline; ledger open=[016,019] unchanged, seam work).
(i) FINGERPRINT: the t252 species capture campaign == bank-t251-live1255
(turn 1255, n=4): Chamachies(col 0, player)/Orfa(1)/Ungooma(6)/Minions(2,
eliminated ships=0) via the watcher name law — the capture's races are
save-known, not hypothesised. (ii) T436-B CLOSED: ring index = race colour byte
row+8, NOT owner%7 — Ungooma (row2, colour 6) wears the ORANGE ring while GOLD
(k2, Minions' colour) sits at row3's slot; second witness = row ink follows the
same byte (t436 F7). (iii) T436-A CLOSED: ONE portrait per RACE TABLE ROW,
PLAYER INCLUDED (row0 = top slot), contact/elimination IRRELEVANT. t436's
"portraits on home stars, player excluded" REFUTED two ways: the baseline band
under every slot is 90% pure black (star markers 64-105 px away; the four blob
centres are an r=170 circle about (234.2,238.0) at angles 89.7/180.3/269.9/0.0
= cardinals), and home-star map-y signs (+214.7 vs -234.4 -> same screen row 238)
are impossible under projection. METHOD LAW banked (R-t441): census the
REPAINT DIFF of a baseline+overlay capture pair, never blobs in the overlay
image alone. (iv) SAVE-LAW CORRECTION: star record base = STATE+0xd8d+0x60j,
NOT t295's STATE+0xdb5 (that is the record's +0x28 field; +0x2c sequential
index, +0x30/+0x34 float x/y, +0x3c marker|race, +0x3e owner bitset, +0x44
name) — verified 50/50 records + all four homeptrs; _wip_t295.md patched;
scripts/t441_race_table_census.py decodes every bank tried (50/50, n matches
word[STATE+0xd88]). (v) CODE: speciesmenu.{h,cpp} speciesSpecnumOfOwner +
speciesPortraitSlot (r=170; n>4 uses 90+360/n — UNMEASURED tail, named, since
no 5+-race capture exists and fixed-90 overlaps rows 4..6 on 0..2); ui.cpp
state-7 block rewritten (owners 0..min(count,7), racering k<colour byte> via
the vendor-default assignRaceColours call). (vi) PINS
tests/test_speciesportrait_t441.cpp x4, mutation-verified (fixed-90 pitch 3
fails, r=160 4, y-sign flip 7, nslots-ignored 17 — all CAUGHT); suite 471/0
(was 467). Witness t409_species_witness.sh VERDICT PASS, 7 owners at 7 distinct
slots. (vii) gate.sh GATE_EXIT=0; ledger_audit rows=20 open=[016,019] OK;
ledger_index_check OK. NEXT t442 = state-7 portrait PAINTER static hunt (closes
the n>4 caveats with code, offline).

t440 LANDED 2026-11-20 (OQ-027 CLOSED — TUNEID INDEX BASE MEASURED, ledger
open=[016,019]). (i) A prior session was killed mid-task (OPEN-QUESTIONS.md
edited + _wip_t440.md + t440_music_table.py untracked); its CENTRAL claim was
true but its draft had THREE errors, all corrected: it called save-member
0x2baa3a a "payload file offset" (wrong system: member = linear+H; the object
is .bss 0x242000+0x78638, payload bytes at the naive offset are garbage —
measured); its script used stride 0xc and mem[B+0x78638] (returned RC=1 as
left); its 0-vs-1-base scare text ("0-based would loop intro01, 7=race00") was
muddled arithmetic. LESSON: an adopted draft's self-report is a hypothesis —
re-verified every address this iteration before banking. (ii) MEASUREMENTS
(objdump + banked saves, zero capture): DIGITALMUSIC dispatch 0x2ee9e/0x2eeb7
-> 0x2ee3b `b8 38 86 07 00` (fixup -> runtime linear 0x2ba638) call 0x4f86c;
0x4f89a bounds WORD[obj+0x6fa]==29; index law 0x4f929..0x4f945 = obj+0x37a +
tuneid*28 NO bias; 29/29 pitch-28 names in EXACTLY music.txt order in 20/20
saves 41..60 (scripts/t440_music_table.py VERDICT PASS, run-independent
locator = scan tail 8b9208020000 + read fixup). => TUNEID ZERO-BASED: 6=
intro00, 7=intro01. audio.md S6.1's dispatch claim + the heap-relative/
"not statically decidable" class REFUTED -> R-t440 written. (iii) CODE: port
outcome was already correct (cue table ui.cpp 6->1, 7->2); comments corrected
in audio.cpp/ui.h/ui.cpp to the measured law; NEW PIN audio_tuneid_zero_based_
t440 (music.txt 0-based indices + cue pairing; mutation-verified: {20,2}
swap-mutant CAUGHT); suite 467/0 (was 466). (iv) LAWS banked: r1-savestate.md
"TWO SAVE COORDINATE SYSTEMS — NEVER MIX THEM" + run-independent locator
pattern; REFUTED-ROUTES R-t440 generalises: before arming a debugger on a live
game, check (i) fixup-addressed operand (ii) save-resident — both true here,
the whole INT 21h/scratch-tree/nosound-vacuity plan was unnecessary. (v)
RULING CHECK NEGATIVE: d1page find -newermt 2026-11-18 13:05 EMPTY; D2 +
OQ-019 acceptance still PENDING; D12 item 5 now MOOT for OQ-027(a). (vi)
LEDGER: OQ-027 row CLOSED (both items measured + code sites); STATE index
re-derived; ledger_audit --expect -> OQ-019,OQ-016 (rows=20 closed=18 OK);
gate green. NEXT t441 = seams T436-A/T436-B (offline-first; no ledger row is
machine-closable until the user rules on D2/D3).

t439 LANDED 2026-11-20 (GAME-RING RECOVERY — LIVE GAME RESTORED, ZERO CAPTURE,
no OQ closed: recovery enables routes, it measures nothing). (i) DEATH CAUSE
CONFIRMED t277 TL-EXPIRY, no crash investigation opened: dosbox.log tail
`LOG: Active save slot: 1 [Empty]` + `X connection to :9 broken`; TL expiry
2026-11-11 01:07, ring froze Nov 14 12:33, dead 9 days because
loop_one_task.sh:205 puts relaunch on the research schedule. (ii) PRE-FLIGHT
GATES PASSED: bank-t438-ring-2200 present (20 slots/43M, not re-copied);
structured /proc census (basename(argv[0])=='dosbox-x') = ZERO procs; `ss -tn
| grep 5910` empty => no human VNC client to evict. (iii) RELAUNCH (not park):
`bash scripts/r1_playcap_vnc.sh start` -> `BRINGUP OK (ring row landed within
30 s: 41.sav)`; r1_game_health.py 12:04:18 `HEALTHY | game pid 1182156; TL
expiry 2026-11-22 12:02:26; watcher 1182171; ring 51.sav age 1s`; pid recorded
to work/r1/vnc/dosbox.pid; re-check 12:11:21 still HEALTHY slot age 3s.
(iv) RESUME TO THE MAP: title menu reached, hover-verified R4 'Return to
Current Game' (band 0.88 + vision label) then POSITIONAL RFB click (318,333) ->
strategic map, HUD '01086'. (v) t259 LAW MEASURED WITH NUMBERS + R-t439
WRITTEN: pre-death ring = 20/20 slots turn=1254; post-resume ring = 20/20
turn=1086 == RESUME.GAM (md5 5b382afbb789186c3654f3cec085b2e2, untouched). The
168 turns 1086->1254 existed ONLY in dosbox Memory and are unrecoverable — do
NOT try to restore them; capture drivers must take an in-game Save if evidence
depends on a state. (vi) THREE NEW OPERATIONAL LAWS banked docs/re/selfplay.md:
WINDOW-ORIGIN DRIFT (t250/t287 +80,+100 is NOT stable — measured
`640x480+192+184`; r287_title_nav.py's hard-coded crop reported
`highlight=NONE bands=3:0.49` while the real highlight was TUTORIAL; use
RFB_XOFF/RFB_YOFF env overrides + xwininfo, and confirm the row LABEL by vision
before Enter — the t287 tutorial-clobber class); KEYS vs POINTERS OVER RFB (on
a focus-less restart both `r287_vncinput.py key Return` and `xsend ... Return`
failed to fire the menu while PointerEvents worked; positional XTEST click is
the focus-independent channel — xsend's `window died before release` is a red
herring, the window kept accepting clicks); SITTING TEST BY TURN NUMBER
(an unattended live game grows live-timeline.jsonl ~1 row/10 s — 9,385,663,364
-> 9,388,633,285 B in 17 min at constant turn 1086 — so use t368_ring_turn.py,
baseline 1086, never file size). (vii) CORRECTION TO THE t438 HANDOFF: it
offered scripts/r297_order_session.py as an OQ-019 route; REFUTED-ROUTES.md:
465-467 makes the scripted-mouse session class budget-spent (t293 x3 + t297 x1
+ t298 x3, next witness = debugger class) — t440 must NOT run it. (viii) NO
ruling arrived: DECISIONS.md 2026-11-18 13:05 < HEAD 2026-11-20 11:52, no
d1page submission newer than HEAD, :8613 still listening; D2 + D12 item 5
remain PENDING, nothing interpreted for the user. (ix) GATE WENT RED AND WAS
FIXED AT THE ROOT — THE LESSON OF THIS ITERATION: the relaunch rotated the LIVE
ring work/r1/playcap/save/ (20-slot window, now turn 1086), which silently
invalidated rewrite/tests/test_observer_t382.cpp
`observer_savestate_import_t382` (5 failures: day 1254->1086, ships.size,
kind4, attributed, ships[0].name) with ZERO code change — a scalar witness was
pinned to a rotating directory. FIX: the test now reads the frozen t438 bank via
`kWitnessSave = "/work/r1/bank-t438-ring-2200/60.sav"` (identical bytes, zero
writers) — suite back to 466 tests / 0 skipped / 0 failed, gate GATE_EXIT=0
with production live. LAW banked docs/re/r1-savestate.md "PIN A BANK, NEVER THE
LIVE RING": future ring pins point at a bank dir, never playcap/save/. Ledger
stays rows=20 open=[OQ-016,OQ-019,OQ-027] closed=17; LEDGER AUDIT OK, LEDGER
INDEX OK, production HEALTHY at 12:39:18 (pid 1182156, ring age 0 s).

t438 LANDED 2026-11-20 (FINAL VERIFY + HANDOFF, ZERO CAPTURE, no OQ closed —
none was closable). (i) SITTING CHECK NEGATIVE: live-timeline.jsonl and every
playcap file oldest-modified 2026-11-12 06:45; no new sitting, so
r1_t85g_sitting.py correctly NOT run. (ii) RULING CHECK NEGATIVE: DECISIONS.md
mtime 2026-11-18 13:05 < last commit 2026-11-20 11:28; decision-sheet.md
2026-11-09; d1page dir (server :8613 alive, pid 646702) has no submission
file newer than HEAD; D2 acceptance and D12 item-5 (audio match/differ) both
still PENDING — recorded verbatim-status, nothing interpreted for the user.
(iii) FULL VERIFY REAL: bash scripts/gate.sh GATE_EXIT=0 ('ALL CHECKS PASS
(milestone=6)'); unit suite /tmp/gate_tests.log tail '466 tests, 0 skipped,
0 failed' (gate runs run_tests under VENDOR=1); ledger_audit.py 'rows=20
open=[OQ-016, OQ-019, OQ-027] closed=17 LEDGER AUDIT OK';
ledger_index_check.py 'LEDGER INDEX OK' (STATE index mirrors record).
(iv) t437 ARTIFACTS SPOT-VERIFIED on disk: pin
rewrite/tests/test_sfxpress_t404.cpp:35 sfx_press_buttons_button_t437;
sfxForPress MapClick nullptr / RailButton|NextTurn|TitleButton 'button'
(rewrite/src/ui/audio.cpp:30-38); scripts/t437_soundchannel_store_census.py
present; R-t433 present (REFUTED-ROUTES.md:1495). (v) NEW ENVIRONMENT FACT:
GAME_DEAD.txt 2026-11-20 11:31:10 — production game process gone, feed
stale (slot 60.sav 514658 s), watchdog intentionally does not relaunch
(loop_one_task.sh:205); recovery queued as t439. RING BANKED THIS ITERATION:
work/r1/bank-t438-ring-2200 (cp -a, 20 slots, 43M, newest 60.sav Nov 14
12:33) — t439 starts at the relaunch-decision step, banking is done. (vi) NO GIT REMOTE — push step closed as N/A with evidence
(git remote -v empty), recorded in the handoff block so future sessions stop
checking. GATE_EXIT=0, LEDGER AUDIT OK, LEDGER INDEX OK.

t437 LANDED 2026-11-20 (OQ-027(b) CLOSED BY MEASUREMENT, ZERO CAPTURE;
docs/re/audio.md S6.9 + docs/re/_wip_t437.md F0-F6; assignment note: the STATE
t437 text still quoted the +0x1bcc route — superseded by R-t429; the LIVE
residue (t429-narrowed question) is what was worked). (i) windows.txt
SOUNDCHANNEL IS the strategic sfx id: parser fn 0x575e4 stores it at
record+0x59 (0x57e7a mov WORD [edx+0x59],ax), grammar position pinned by the
X0/Y0/X1/Y1 rect stores +8/+c/+10/+14 in file order; +0x59 == HIWORD of
dword[+0x57]. (ii) Strategic press handler identified 0x30c9c..0x30edb: rect
hit-test then play HIWORD(dword[rec+0x57]) (0x30e75, -1 = silent) then
SENDMESSAGE/SENDPARAM1 into control pool 0x7a35c. (iii) VALUE: 0 on all 119
file lines ("-0" scans to 0); live RAM +0x59 == 0 on 2,400/2,400 file-declared
records x 20 saves (scripts/t437_soundchannel_store_census.py); only
COSMOSWnd/BatModeWnd/INTROFLIC/WMGRDEBUG (runtime, no file block) carry -1.
=> vendor plays soundfx manifest[0] "button" on every file-declared button
press; NOTHING on the map; no per-button vendor id exists for the strategic
UI. (iv) PORT UPGRADE: rewrite/src/ui/audio.cpp sfxForPress
RailButton/NextTurn/TitleButton click08 -> "button" (click08 off-manifest,
vendor-unreachable since t395 — the old port sound was ALWAYS silent);
MapClick nullptr now cited (COSMOSWnd -1). Pin sfx_press_buttons_button_t437
mutation-verified (click08 mutant CAUGHT); suite 466/0; witnesses
t404_sfx_witness.sh + t395_sound_witness.sh updated to "sfx button", both
live VERDICT PASS. TOOLING LAWS banked: modrm rm=5 mod=01 is EBP+disp32
(STACK), not record disp8 — naive disp8 scans over-count record writes ~10x;
byte-scan + objdump grammar walk is the reliable store-census pair. LEDGER:
OQ-027 STAYS OPEN (item (a) TUNEID base = user-hearing/heap-capture bar;
(b) closed text carries the measurement + code site). GATE_EXIT=0,
LEDGER AUDIT OK, LEDGER INDEX OK.

t433 LANDED 2026-11-20 (CHROME MEMORY-SURFACE ROUTE ANSWERED, ZERO CAPTURE,
NEGATIVE; docs/re/chrome.md SS7 + docs/re/_wip_t433.md F0-F7). (i) THE t433
PREMISE IS REFUTED: the chrome field is not ONE canonical pattern but MANY
instances tied deterministically to UI/repaint state — a 49-shot census over
work/screens/{t252,t253,t268} puts every shot on one of five instances at
100.0% index identity (map / window-open / research / design / diplomacy), the
map instance byte-identical across THREE independent sessions, so repainting
happens per window transition and reproduces its instance exactly (SS1.1
"painted once" -> painted once PER repaint). (ii) Instances are NOT phases of
one buffer: dy sweep +-300 over all 20 ordered pairs gains <=2.0 pts, no
index-offset law. (iii) NO SURFACE ON DISK: 396 x 28 B band signatures + one
448 B top-band block, 0/471 extracted/ files (the 16 files hitting on 7 B rows
are low-entropy coincidences — same regions give 0 at 28 B). (iv) NO SURFACE
IN THE SAVES: 0 hits in Memory (17 MB) and Vga (2.6 MB) of 20 saves, and the
vacuity gate is CLOSED — game.pal's raw 768 B is found in both members
(Vga 0x845c5, Memory 0x28a6b3 -> phys 0x28a62b) while 45 64 B signatures of
distinctive screen content score 0/45 in BOTH, i.e. the displayed frame is not
stored packed anywhere. (v) Planar caveat handled: vertical-run pitch test
gives 183 supports at pitch 640 vs 0 at 639/641/632/648 and 4 on a shuffled
null control, so a real 640-pitch paletted buffer exists (member
0x2f69f9..0x335979) — but it is 82% black / 6.2% chrome-family and 0/60 of its
40 B rows appear in any refcap: NOT the backdrop. (vi) CENSUS TOOLING LAWS
banked (chrome.md SS7.5, each cost probes): refcap png row = screen row + 40
while work/screens/*_game.png rows ARE screen rows (mixing them silently gave
22.8% where aligned is 100.0%); the palette scale is raw6*4+raw6//16 (100.0%
exact; the *255//63 quoted in SS1 only 91.2%); compare INDEX planes not rgb
(the DOSBox scaler blends rgb — VNC grabs 69.3% palette-exact, max distance 8 —
yet decodes to the vendor index 100.0% of the time, tie-controlled); numpy
index planes must be uint8-cast before .tobytes() and needles asserted
non-empty. R-t433 written. NO OQ closed (strict-close honest negative: the
chrome generator has no OQ owner — open rows remain OQ-016/019/027, none
touched). GATE_EXIT=0, LEDGER AUDIT OK.
PROCESS LESSON (self-inflicted, bank so no one repeats it): do NOT rebuild a
docs file from read_file() output — read_file returns 'N|'-prefixed lines and
the renumbering write CLOBBERED docs/re/chrome.md mid-iteration; recovered by
`git checkout -- docs/re/chrome.md` (the file was clean at HEAD) and re-applied
as an append. Append with patch(), never rewrite-by-read.

t436b LANDED 2026-11-20 (SPECIES SCREEN IMPLEMENTATION COMPLETE — all F9
items; docs/re/_wip_t436.md G1/G2 + ui-runtime.md t436b block). (i) STATE-7
RIGHT COLUMN = frameTex chrome (cluster zone measured 99.85% == map) +
speciesWellAt dark-speckle wells (header + EMPTY slots; census pal
{200:625,0:257,196:90}, chain 45% copy-left/35% repeat-up FITTED on the
re-measured mean-run statistic 4.03/3.74 — the F8 lag-1 numbers were the
interpolation-affected ones; fit on run length instead). (ii) POPULATED ROWS
= flat kStatusWellNavy (8,32,49), grey outline DELETED, names CENTRED (bbox
centre 553 law), Extinct WHITE, flag row-local (14,3). F9's "(12,32,48)"
stale quote CORRECTED to (8,32,49) per the F4 decisive colour law (G1).
(iii) PORTRAITS = smrace<specnum> rec0 scale2 clipR49 + racering k<owner%7>
scale2 ring-LAST at projectStar(homeStarFor(o)), per KNOWN AI owner,
raceVisibleMask-filtered, witness log "ui species portrait owner N at x,y".
Census lesson [measured]: point-sampling the ring circle is brittle (art
gaps); annulus census at the LOGGED centre is the robust law (244 chromatic
px band + 4668 px disc on the witness shot). PINS test_speciesmenu_t436 x6,
suite 466/0. Witness t409 VERDICT PASS + t436b_witness_census.py VERDICT
PASS. SEAMS T436-A (count) + T436-B (ring index) stay open, named. NO OQ
closed (strict-close honest negative — species-screen visuals have no OQ
owner; t409..t436 precedent; OQ-016/019/027 untouched). GATE_EXIT=0, LEDGER
AUDIT OK.

t436 LANDED 2026-11-20 (SPECIES SCREEN LAWS MEASURED — measurement-only
iteration, NO code delta; docs/re/_wip_t436.md F0-F9 + ui-runtime.md t436
block). (i) CHROME LIB CLOSED: state 7 binds DATA\7RACESEL.SHP (TYPE-100
ln720) — but k0..k6 decode BYTE-IDENTICAL FLAT navy (t393 row-face premise
REFUTED) and (12,32,48) occurs ZERO times in both t252 captures; k7 == the
RACECONTROLS strip face. (ii) LAYER LAW [measured t252 capture vs own
baseline]: column = CHROME mottle; header + EMPTY slots = DARK SPECKLE
(pal 200:63/0:26/196:9, lag-1 2.96/2.99 correlated); POPULATED rows +
Intelligence = FLAT navy idx242; cluster zone y360..472 99.85% identical to
map => overlay never repaints it. Root cause of "quite off": port paints
flat (16,16,24) + grey outlines + LEFT-aligned names; vendor = speckle/
navy wells + names CENTRED (bbox centre 553 all rows) + flag row-local
(14,3). (iii) PORTRAITS: centred on star markers, disc r~48 + three-tone
owner ring r50..55 == smrace x2 + racering x2 (t423c2 ring-index law
RECORROBORATED: racering palettes green/purple/gold/orange/grey == the four
measured ring hues); player home has NO portrait; count law = seam T436-A.
(iv) ABILITY leg UNCHANGED (wired+witnessed t409; use-fire = sim seam).
Tooling notes for successors: shp_pngdump needs <out>/raw/ to EXIST; the
kernel python has NO PIL — census scripts run under
~/.hermes/hermes-agent/venv/bin/python. NO OQ closed (strict-close honest
negative — species-screen visuals have no OQ owner; t414..t435 precedent;
OQ-016/019/027 untouched). GATE_EXIT=0, LEDGER AUDIT OK.

t435 LANDED 2026-11-20 (RESEARCH SCREEN live re-check + 2 defects fixed;
docs/re/ui-runtime.md t435 block via _wip_t435.md F0-F6). LIVE RE-CHECK LIST ALL PASS:
t419 witness FAIL was a WITNESS-ORDERING bug (t425(d) made the popup click
fire doEscape -> Esc poll counted on the map screen); fixed order, 5/5 PASS,
esc_ms=204, CPU delta 144 ticks/4s (~36% core), spin-latch stop law
witnessed by md5 (stopped frame == spin2 frame BYTE-IDENTICAL). D1 FIX: pan
faces = 20res.shp records SHAPEFRAME 0..3 blitted at the verbatim rects
(rect==record dims HALF-OPEN; faces carry (12,32,48) panel bg; k4/k5 exist
but no windows.txt record consumes them — not blitted); our-render box
censuses == decoded-record histograms EXACTLY (220/29/24, +18 orange, 243,
171). D2 FIX: player plaque upper-left (t426 map law reused; vendor census
38/38 *_game.png crest bbox x10..24 y10..34 — ours matches). PINS
test_resface_t435 x2, suite 460/0. NAMED SEAMS: D3 panel disk-icon + planet
art join (needs the STATE-20 vtable [win+0xa7]+0xc paint chain identified
live — closure witness named), D4 chrome frame = t433's row. NO OQ closed
(strict-close; research-screen complaints have no OQ owner — t408/t419
precedent). GATE_EXIT=0, LEDGER AUDIT OK (open rows unchanged:
OQ-016/019/027).

t434b LANDED 2026-11-20 (COMPLETE SHIPS SCREEN — BOTH legs closed; docs/re/
_wip_t434b.md F0-F6 + ships.md S70). LEG 1: witness t407_fleetlist_witness.sh
VERDICT PASS (select/deselect/scroll, zero laser01); t434_witness_census.py
"FAIL" was a CENSUS BUG x2 (wrong ink y-window 56..76 vs measured 62..83;
green censused on the SELECTED shot where white is law) — fixed script now
VERDICT PASS on the same shots (green 69+397, white-on-selected 69, cyan 0,
navy-frame 0). LEG 2 [MEASURED LIVE, run work/r1/dbg-t434b2-a1-20261120-
034958, tool scripts/r434b_art_session.py]: ROW-ART LIB IDENTITY = the cache
payload is BYTE-IDENTICAL to smship19.shp (16 KB dump, unique over 208 libs)
— identity by CONTENT, R-t434 honored; selector = BYTE_HI([ship+0xa7]) live
1 (t434 F5's 0x41-record reading was an x-coord misread — push order account
F4); ORIGIN LAW x=65+8+(-46)=27, y=50+47+(-26)=71 == t253 bbox top-left
EXACTLY (rec+8 signed pair = hotspot; dims 49x15 do NOT give the origin).
PORT: smship<species>.shp loaded + blitShape(27, rowTop+19) per row
(ui.cpp), kFleetArt* law constants (fleetlist.h), pin
fleetlist_row_art_origin_t434b; our render census: 114 ink px in the 49x15
window. HONEST RESIDUALS (named seams, not claimed): gizmo-icon rows not
ported (t253 column extends y112), per-ship class field absent (t256c) ->
selector default 1. CLICK LAW: rail switch = FLEET widget (553,184), NOT
TOGSHIPS. BUILD clean, run_tests 458/458. NO OQ closed (strict-close;
OQ-016/019/027 untouched — ships-screen visuals have no OQ owner, t424b/
t428f precedent). GATE_EXIT=0, LEDGER AUDIT OK.

t434 LANDED 2026-11-20 (SHIPS SCREEN INK/SELECTION LEG; ROW ART NOW CLOSED
BY t434b ABOVE; docs/re/_wip_t434.md F0-F6). (i) PAINT LAW [verified fn 0x50d12 0x50d50..
0x50d8d, work/t434_fleetwin.asm]: row name+location drawn game.pal[raceByte*4
+0x13] (race row +0x1, stride 0x1ee, BYTE-masked 0x50d6c), SELECTED row
overrides to immediate 0xf3 == pal[243] white — same law family as t427
planets rows. Witness [measured t253]: row1 name band 48px (255,255,255),
rows 0/2/3 (0,170,82) green, ZERO cyan. (ii) PORT DEFECTS FIXED: fixed-cyan
location line, synthetic navy row frame + green marker (t253 census: vendor
paints NEITHER). fleetRowPalIndex() in fleetlist.h; 3 pins
tests/test_fleetlist_t434.cpp; BUILD clean, run_tests 457/457. (iii) HONEST
NEGATIVE: row-art library identity NOT closed (smship/dkship TOC probes
inconclusive; F5/F6) — t434b leg (2) routes via the 0x50d12 blit arg chain,
NOT filenames. Witness census script written (scripts/t434_witness_census.py)
but UNRUN — t434b leg (1). NO OQ closed this iteration (strict-close).

t424b LANDED 2026-11-20 (RACE INTRO BACKGROUND + INK FIXED; docs/re/
_wip_t424b.md F0-F5 + REFUTED-ROUTES R-t424b + _wip_t415.md corrections).
All OFFLINE census off the user vendor screenshot + one Xvfb witness run
(scripts/t424b_intro_witness.sh + t424b_witness_census.py VERDICT PASS) — no
R1 session. (i) GIF/CINE PREMISE DEAD: zero .cine/.FLI strings in the payload;
gif sites = logo/Alt-G/0opening only. (ii) BOUNDARY LAW [measured]: the bright
chrome page covers ONLY the margins outside the outer frame (x0..6, x634..639,
y0..6, y474..479); the ENTIRE frame interior is a DARK speckle
{game.pal 0:40% 200:30% 1:25% 196:5%} — t415's "chrome page full-screen"
reading was the root cause of BOTH reported defects (greyscale background +
unreadable ink). Port: mapchrome.{h,cpp} introSpeckleAt (stateless 5/25
Markov chain, distinct salt, measured census); vendortext.cpp runRaceIntro
renders chrome margins + dark interior. (iii) GRAIN: correlated not iid
(vendor lag profile + same-colour adjacency 0.348 > iid 0.315); exact chain
parameters UNFITTABLE from the 1.6266x-scaled shot (simulated discriminator
collapse — R-t424b(3)); generator origin stays a named seam (t433 route).
(iv) INK WITNESS: Minions runtime racebyte = 0 (vendor ink pal[19]) — static
kIntroRaceBytes[0] 16->0; other 20 bytes stay seam H3. (v) INCIDENTAL FIX:
lgrace portrait path snprintf char[64] TRUNCATED long dataRoots (portrait
silently never loaded on this machine); now std::string. Tests 454/454
(+4 introspeckle_t424b; t412 ink pin updated), 0 warnings. LEDGER closes
NOTHING (strict-close honest negative — race-intro visuals have no OQ owner;
t414..t429 precedent; OQ-016/019/027 untouched). GATE_EXIT=0; LEDGER AUDIT OK
(open rows unchanged: OQ-016/019/027).

t429 LANDED 2026-11-20 (OQ-027(b) PREMISE REFUTED + FULL PLAY-PATH CENSUS;
docs/re/audio.md S6.8 + docs/re/_wip_t429.md T429-A..C + REFUTED-ROUTES
R-t429). All OFFLINE (objdump over work/ascend_payload.bin + banked decomp
work/coswnd_decomp/500e0.c) — no R1 session run. (i) The cited sites 0x17488/
0x1749b are KEYBOARD gizmo-fire calls: lea ebx,[ecx+4*keycharcode], read
[ebx+0x1bcc]/+0x1bce, sar $0x10 (HIWORD = manifest index), eax=0x78638 audio
object — batmode.cpp handlers; mouse clicks never reach them. (ii) LOADER LAW:
the +0x1bcc table IS batfx.txt — ctor 0x1acd0 opens it (pool-rel 0x3bd),
sscanf "%d" count<=0x64, "%s" key chars -> u16[obj+0x19c6+2i], "%d %d %d %d"
columns -> low u16s at +0x1a92/+0x1a94/+0x1bce/+0x1bcc; batfx columns 3/4 =
sfx1/sfx2 per the file's own header comment. windows.txt SOUNDCHANNEL never
feeds it. (iii) CENSUS of the whole play path (34 call sites, eax=0x78638 at
all): 17 batfx-keyboard table reads (13 wrapper + 2 direct + 2 variants); 8 immediate-0 = manifest[0] "button" (md5
cef40f13a210357d8d9379d52a5ab484; 0x1b0b0/0x1b1c5/0x27e46 verified inside
rectangle click hit-tests); 6 record-field sites mov edx,[obj+0x57]; sar 0x10;
cmp -1; je skip (records via control pool 0x7a35c = strategic pool); 1
imm7="trust01" (0x1791c); 2 computed. (iv) FUN_000500e0 id-space = the 86-name
soundfx.txt manifest BY CONSTRUCTION — button01/button02/click08 are
vendor-unreachable. LEDGER closes NOTHING (strict-close: the strategic rail/
NEXTTURN site is not yet identified; sfxForPress UNCHANGED, click08 stays a
documented port choice; OQ-027 stays OPEN, row text updated with the narrowed
question; OQ-016/019 untouched). GATE_EXIT=0; LEDGER AUDIT OK (open rows unchanged: OQ-016/019/027).

t428f LANDED 2026-11-19 (k5 GATED OFF LIVE — ORIGIN QUESTION CLOSED AS A
NON-QUESTION; working log docs/re/_wip_t428f.md F0-F5 + docs/re/planets-ui.md
§14 + REFUTED-ROUTES R-t428f). (i) LIVE WITNESS (run
work/r1/dbg-t428f-20261119-210504, tool scripts/r428f_k5_session.py): BP
0x3c7cd fired on the planet-detail paint with the paint head control (blit1
0x3b9df) firing the SAME paint; eax = PLANLIST widget head 0xfe6814 (magic
0x12345678 + NAME@+0x20 verified live), DWORD[+0x35]==0 -> cmpl $-1 FAILS ->
k5 fetch+blit NEVER execute (k5_blit leg armed, 0 fires). Offline: PLANLIST
+0x35==0 in 20/20 bank-t251-live1255 slots; 0/126 RAM magic-records hold -1.
(ii) The t428c (224,107) peak (1566 px, z=18.6) = FALSE POSITIVE (palette
coincidence); k5 STAYS UNPORTED — porting would add art the vendor does not
draw. (iii) E6 ARG LAW CORRECTED: the k5 site pushes FIVE explicit args
($0,$0,$5 + handle + &struct; add $0x14 esp) — "p3/p4/p5 frame leftovers"
retired (composition law 5caac.c:58-64 stands). (iv) HARNESS LAW F5: cold-leg
censuses must POLL-BY-BREAK — stock resume_and_rearm's BPDEL * releases a
pending halt at the NEXT cold leg UNBANKED (attempt 1 lost the gate stop this
way; the whole-log census then counted the mem_ctl filename as a false fire —
census filenames must not contain leg signatures). Residual banked: what sets
+0x35=-1 (writers 0x3ab24/0x3d3a7; state never witnessed). LEDGER closes
NOTHING (strict-close honest negative — planet-screen visuals have no OQ
owner; t414..t428e precedent; OQ-016/019/027 untouched). GATE_EXIT=0;
LEDGER AUDIT OK.

<!-- SUPERSEDED t428f assignment (kept for archaeology):
NEXT t428f — K5 ORIGIN VIA RUNTIME FRAME READ (ordering rationale: t428e
closed k5's SITE and IDENTITY but proved the origin is statically unpinnable
— docs/re/_wip_t428e.md E6: fn 0x5caac composes x = p4 + struct[+4] +
WORD*(payload+0x10), y twin (work/combat_decomp/5caac.c:58-64), and the k5
site (0x3c82d) pushes ONLY p1,p2 — p3/p4/p5 are frame leftovers + the payload
slot rect is runtime cache state (shp.md S12.2). The closed pointer law
(docs/re/r1-savestate.md) is exactly the tool for this: run ONE bounded R1
save-state session (mandatory invariants: scratch copy never mounts game/,
headless, -time-limit, pkill -x dosbox-x only), open the planet screen (state
17 — geometry clicks per windows.txt; t65's queued recipe in docs/re/shp.md
S12), checkpoint, then read from RAM: (1) the PLANLIST widget object found by
the 0x56d1c walk (game obj 0x7a35c member table; verify DWORD[widget+0x35] —
tests the E1 gate on a live frame AND settles whether witness B's peak implies
gate-pass); (2) the 17np cache slot (runtime cache base = RAM ctx - image VA
law, shp.md S12.2/S12.4) — its +0x10/+0x14 rect fields; (3) if reachable, the
paint-body frame words at the 0x5caac call. THEN: compute the E6-law origin;
if it lands on the witness-B peak (224,107) within tolerance, PORT k5 as the
planet backdrop (ui.cpp kScreenPlanet, under the k4 field blit per vendor
order) with a pin binding the law; if it lands elsewhere, bank the corrected
origin and re-run the t428e_k5_origin census at the computed point before any
port. Do NOT port (224,107) directly — that is a plausible default, not a
law. Do NOT re-hunt the k5 site (E1/E2 CLOSED), do NOT re-derive blit-1/2/3
laws (t428d F2/F4), do NOT touch blit-2 (census NEGATIVE E5, stays unported),
do NOT start the tile-click popup law (task (c) was gated on (a)+(b) landing;
(b) came back negative). SEAMS carried: T428-B (witness-A lineage),
T427-A..F unchanged, T428c-A narrowed to k5 ORIGIN ONLY (identity CLOSED).
-->

t428e LANDED 2026-11-19 (K5 SITE + IDENTITY CLOSED; BLIT-2 CENSUS NEGATIVE;
working log docs/re/_wip_t428e.md E0-E7 + docs/re/planets-ui.md §13). (i) THE
k5 BLIT EXISTS IN THE SAME PAINT BODY: 0x3c7bc..0x3c832 [verified asm] —
0x56d1c(0x7a35c, 0x1f06) lookup, gate DWORD[result+0x35]==-1, fetch 17np
(lib slot esp0+0x370 = WORD[0x6fd9c] = 44) record IMMEDIATE 5 at (0,0)-args,
blit 0x5caac with struct {112, stale, 528}; the only edge to the site is the
lattice loop exit (0x3c4ed, bound WORD[planet+0x1a] — NEW record field) and NO
ret exists between head and site, so every paint runs it unless the gate fails
(t428d's "k5 unreachable" was head-scoped — corrected). (ii) WIDGET =
"PLANLIST": 0x1f06+0x82bb0=0x84ab6 [measured in work/ascend_restored.bin],
RESWIN control 0x2c0c+0x82bb0=0x857bc EXACT — pool-relative law holds for
0x56d1c name immediates. (iii) ORIGIN OPEN: 0x5caac arg law +
struct/payload composition pinned (work/combat_decomp/5caac.c:58-64), but the
site pushes only 2 of 5 args — origin = stale frame words + runtime payload
rect; measured placements (224,107)=1566/10748 (permute ~360) vs
(112,120)=56, (0,0)=436, (408,296)=28 [scripts/t428e_k5_origin.py]; PLSQUARE
interior 0/2048 matched (backdrop-behind-panel consistent). NOT ported
(strict-close). (iv) BLIT-2 CENSUS at (408,296): rec0 62/49558, rec1-3 zero,
rec4 1/269; rect 71% pure black -> blit-2 INERT, stays unported. SUITE
unchanged (no code delta). LEDGER closes NOTHING (strict-close honest negative
— planet-screen visuals have no OQ owner; t414..t428d precedent; OQ-016/019/
027 untouched). GATE_EXIT=0; LEDGER AUDIT OK.

t428d LANDED 2026-11-19 (k4 FIELD PORTED + PAINT-BODY HEAD FULLY CLOSED;
working log docs/re/_wip_t428d.md F1-F4). (i) BLIT-1 SELECTOR CORRECTION
[verified asm 0x3b9c0..0x3b9df]: the third push is `push $0x4` — record 4
is an IMMEDIATE (t428 F4's "selector = SENDMESSAGE" conflated the gate
test at 0x3b9b1 with the arg pushes); pushes $0x73,$0x7 = y=115,x=7
calibrated against the t428c measured k4 registration — seam T428c-A's
record-index question CLOSED by nonexistence (no selector law; constant).
(ii) PORT: planetstrip.{h,cpp} kFieldRecord/kFieldBlitOrigin/
fieldLibraryConforms + ui.cpp kScreenPlanet branch blits 17np k4 at (7,115)
FIRST (under strip+lattice, vendor order). Pins test_planetfield_t428d x3
(blit-law constants + span; census 17np conforms/gauge libs decline;
DECODED rec4 byte census lit=269 bbox x26..620 y2..353 == the t428c
script, scatter test, rec0 frame-class control 49558 lit px MEASURED).
SUITE 450/0/0. (iii) WITNESS: t428_witness_census.py FIELD leg on our own
render: 246/269 matched tol-8, 22 bright (overpaint), 1 dark -> VERDICT
PASS. (iv) BLIT-2 LAW [verified stack arithmetic]: lib = widget+0x175
slot table, record = SIZE CLASS (esp0+0x340), at (408,296), gate
BYTE[widget+0x18b]&4; BLIT-3 = 17np k1 at (0,0) unported (no witness).
k5 NOT reachable from the head (5 not in {4, size 0..4, 1}) — k5 hunt is
t428e(a). LEDGER closes NOTHING (strict-close honest negative — no OQ
owner; t414..t428c precedent; OQ-016/019/027 untouched). GATE_EXIT=0;
LEDGER AUDIT OK (17 closed / 3 open); LEDGER INDEX OK.

t428c LANDED 2026-11-19 (FIELD PROVENANCE: k4 BLIT ANCHORED + B/C INDEX LAW
CORRECTED; working log docs/re/_wip_t428b.md F1 correction + docs/re/
_wip_t428c.md F1-F4). (i) B/C TABLES PINNED (they were already banked — t428b's
"unpinned" was a ledger misread): 0x7445c/0x744a8 = planitem.txt grids B/C,
OQ-014 CLOSED 2026-10-06; NEW index law [verified asm]: both reads use
idx = 15*u16[planet+0x14] + row (0x3bb2c shl4-sub builds 15*size into esp+0x358,
0x3bb63 inc/row; 0x3c1e2..0x3c20b inner loop runs EXACTLY C[size][row] cells at
cols B..B+C-1). t428b F1's "per-cell count" reduction WRONG in granularity —
per-(size,row); its no-vendor-gate conclusion STANDS. Port ui.cpp:1767 already
matches — no edit. (ii) k4 MEASURED: decoded 9/9 17np recs; k4 = 625x357,
99.88% black, 269 navy/grey specks (starfield). Exhaustive-offset registration
in witness B: 158/269 at png (87,215) = SCREEN (7,115) = EXACTLY the 0x3b9c0
blit-1 pushes; colour-shuffle control 6..12 (pairing real); fresh-array
random-offset best 13 = background (peak unique). k4-as-field-backdrop SETTLED (painted at (7,115),
overpainted by lattice/pop art — 101/111 anchor mismatches are BRIGHT px).
(iii) k5 registers at screen (224,107) z=18.6 but 14.6% — widget/selector open
(seam T428c-A). (iv) PORT GAP found: nothing paints the k4 speckle -> t428d(a).
Banked: scripts/t428c_field_register.py; docs/re/planets-ui.md §11 annotated;
_wip_t428b F4 annotated. LEDGER closes NOTHING (strict-close honest negative —
planet-screen visuals have no OQ owner; t414..t428b precedent; OQ-016/019/027
untouched — OQ-014 re-cited, stays CLOSED). GATE_EXIT=0; LEDGER AUDIT OK
(17 closed / 3 open); LEDGER INDEX OK.

t428b LANDED 2026-11-19 (MUTATION 4/4 + H-FIELD-STATE PREMISE REFUTED; working
log docs/re/_wip_t428b.md F0-F4). (i) VACUITY PROBE before any mutant: seed-2024
turn-0 fixture has res=0 ind=1 pros=1 pending=-1 for EVERY star, so the const-0
arm was moved to IND and the res/ind swap + project+1 confirmed visible.
(ii) MUTATION 4/4 CAUGHT (scripts/t428b_mutate.py; AFTER-RESTORE 447/0/0;
pristine md5s verified after every restore): M1 RES/IND panel-binding swap ->
planetstrip_gauge_rects :101/:102; M2 kPopGridOrigin 355->350 ->
planetstrip_pop_anchor :141; M3 PLIND selector const-0 -> gauge_rects :102;
M4 projectItem=pending+1 -> star_domain :154. No MISSED mutant -> the t428
strip pins encode the law. (iii) STATIC FIELD FINDING [verified control flow,
work/t198_planwin.asm 0x3bb19..0x3c26d]: the lattice walk is UNCONDITIONAL once
reached — head edi=110/eax=410/edx=0, step +0x11/-0x22/+1, bound cmp $0x16d ->
15 iterations always; the only skip legs are the owner test (0x3baf4, jumps to
the TAIL and only for non-owned planets) and the fixed per-cell table test
(0x3c1f2/0x3c1fa reads BYTE[0x7445c]/BYTE[0x744a8] — table identity UNPINNED,
semantics [inferred] per-cell art counts). Witness A shows the player OWNS the
planet, so its own state would RUN the walk => A's BLACK field is NOT a vendor
conditional: H-FIELD-STATE premise REFUTED, seam T428-A re-scoped into the
T428-B lineage question. Port lattice UNCHANGED (no edit justified).
(iv) CAMPAIGN PITFALL banked (F3 + skill rule 8 family): first battery run was
fully bogus — mutant tuples keyed the SNAPSHOT path, so M1 built pristine
(false MISSED) and "restored" the mutated file, poisoning M2/M4 + AFTER-RESTORE.
Detection = red AFTER-RESTORE + FAIL lines naming tests unrelated to the
mutant; recovery = git checkout (only after git status proves no hand edits in
those files), rebuild, green, re-run; prevention = mutants on WORKING paths +
md5-verified restores that ABORT on mismatch. LEDGER closes NOTHING
(strict-close honest negative — planet-screen visuals have no OQ owner;
t414..t428 precedent; OQ-016/019/027 untouched). GATE_EXIT=0; LEDGER AUDIT OK
(17 closed / 3 open); LEDGER INDEX OK.

t428 LANDED 2026-11-19 (PLANET-SCREEN STRIP LAW MEASURED + SHIPPED;
working log docs/re/_wip_t428.md F1-F10). (i) WITNESS SPLIT [measured]:
refcap original-planet-view.png (A) is NOT state-17 geometry — its strip
is the STATUS-ROW composition (F8 seam T428-B: flag/sun/planet anchors
disagree with the t3-derived t417/t427 laws; sun/planet vertical order
REVERSED); t254/02_planet_detail.png (B, 1:1, origin (80,100)) IS the
state-17 strip. (ii) STRIP LAW [measured on B + byte-level census]:
PLRES/PLIND/PLPRO blit planres/planind/planpro record = the compressed
gauge selector at the windows.txt rect origins (each lib EXACTLY 21 recs
x 107x99 filling the 108x100 rect; rec0 = navy mottle); PLPOP = the t263
pop-grid law anchored (355,7); PLBUILD = centred WHITE project name +
planitem k[item] thumbnail (B "Scientist Takeover"), "No Project" text
only when none (A, static.txt #141). (iii) PAINT BODY 0x3b96c head +
grid-gate hunt decoded (F4/F6): the two owner-vs-player tests are NOT
grid gates (0x3958c = cell-array byte search; jump target is the tail
loop) — H-FIELD-STATE stays OPEN, port field unchanged (T428-A).
(iv) PORT: new PURE ui/planetstrip.{h,cpp} + conform census; ui.cpp
grey-outline loop DELETED -> strip painter; t406 "Project: X - N days"
line DELETED (witness B: name only). PINS test_planetstrip_t428 x4,
SUITE 447/0/0. WITNESS scripts/t428_strip_witness.sh +
t428_witness_census.py VERDICT PASS (PLIND/PLPRO >40-colour photos,
PLPOP sprites, PLBUILD white n=111; PLRES rec0 mottle 8 cols = low
gauge, threshold per record). NOT RUN: mutation battery (t428b).
LEDGER closes NOTHING (strict-close honest negative — planet-screen
visuals have no OQ owner; t414..t427b precedent; OQ-016/019/027
untouched). GATE_EXIT=0; LEDGER AUDIT OK (17 closed / 3 open).

t427b LANDED 2026-11-19 (VERIFY + CLOSE t427 — witness, mutation, capsule
retirement; working log docs/re/_wip_t427.md F9-F11). (i) GATE_EXIT=0 on
the t427 tree BEFORE any edit (the never-gated t427 edits pass; suite
442/0/0). (ii) WITNESS scripts/t427_statusrow_witness.sh +
t427_witness_census.py VERDICT PASS 14/14 on our own Xvfb render (seed 5
--species 0; the --species flag is REQUIRED — default playerSpecies=-1
paints no flag): row0 line1 GREEN g=413 unselected -> WHITE w=413 selected
(same-row control; seed-5 owns ONE planet so rows 1/2 are the never-WHITE
control), ZERO flat-(255,0,0) capsule px x3 rows, sun warm px x16..145
n=6512, raceflag px x12..26 n=336, pip dots start x498 exactly with
dot-start pitch 5/5/5/5/5, old x428 strip n=0, planet art px n=976.
(iii) CAPSULE RETIRED: kStatusMarkerRect DELETED from statusbg.h; pin
statusbg_marker_and_wells_t417b re-scoped to statusbg_wells_t417b
(arrow-well navy half kept; capsule half deleted citing F6). (iv) SELECTOR
LAWS made PURE + pinned (statusSunSelector raw type 0..12 else -1;
statusPlanetSelector 5*type+size with asymmetric-arg pin) and wired into
ui.cpp; pin statusrow_selector_laws_t427b; suite 443/0/0. (v) MUTATION
4/4 CAUGHT (M1 colour swap, M2 pip pitch 5->4, M3 sun selector const-0,
M4 5*s+t swap; checkpoint-commit 106b9db first; AFTER-RESTORE 443/0/0).
(vi) NATIVE self-grade vs /tmp/t427_row0.png: composition law holds; NEW
named seams T427-E (row thumbnails unpainted) + T427-F (pip colour law).
LEDGER closes NOTHING (strict-close honest negative — status-list visuals
have no OQ owner; t414..t427 precedent; OQ-016/019/027 untouched).
GATE_EXIT=0 (post-everything); LEDGER AUDIT OK (17 closed / 3 open).

t427 LANDED 2026-11-19 (PLANETS LIST ROW COMPOSITION DERIVED FROM RE;
working log docs/re/_wip_t427.md F1-F8). (i) VENDOR ROW PAINT fn 0x500e0
(disasm 0x504d0..0x50647) decoded: 3 blits per row on the row surface —
SUN = suns.shp (init 0x51954 resolves verbatim "DATA\\suns.shp" @0x856a7)
selector RAW star-type dword; PLANET = planets.shp selector 5*type+size
(words +0x16/+0x14, the SAME words the row string reads); FLAG =
raceflag.shp via FUN_0x53dd8 at row-local (10,4) gated by the owner-mask
law 0x505f1..0x50647; slot globals + cache dir resolved from live save
60.sav (count 150; slot 29 planets, 32 raceflag, 52 suns). (ii) VENDOR
BUG CANDIDATE: init stores the suns slot into [0x69ce], not the [0x8957e]
it reads (byte-level scan: [0x8957e] has exactly 2 refs, both READs, zero
writers; 20/20 in-game slots read 0). NAMED SEAM T427-A. (iii) FLAG FACE
ROOT CAUSE for the t417b "flat red vs vendor gradient" seam: 0x53e81..
0x53ea5 rewrites palette slots 15..19 := raceByte-i (race row +0x1)
before the flag blit — palette-ramp shading, seam T427-D. (iv) t417b RED
CAPSULE REFUTED [measured, decisive]: row0 line1 WHITE x522 vs rows1/2
GREEN x551/x375 — the SELECTION LAW IS TEXT COLOUR; the capsule was
fitted to the sun art's upper-left arc (rows 1/2 red px below x185 =
ZERO). Capsule DELETED from the port. (v) SCALE LAW: drawn sun 130x126
vs content 61x68 => 2x blit; anchors MEASURED sun centre (80,row+64),
planet centre (215,row+53), flag (12,row). (vi) POP PIP GRID 10x4 pitch
5 at x498 row+50 (replaces the wrong-column x428 strip). PORT:
statuslist.h pure constants + suns.shp lib + row painter rewritten; PINS
test_statusrow_t427.cpp x5; SUITE 442/0/0. NOT RUN: gate/witness/mutation
(budget — owned by t427b NOW). LEDGER closes NOTHING (strict-close honest
negative — status-list visuals have no OQ owner; t414..t426c1 precedent;
OQ-016/019/027 untouched).

t426 CYCLE 2 LANDED 2026-11-19 (CHROME-BAND GRADIENT LAW — option (a)
CONFIRMED, (b) NOT NEEDED; working log docs/re/_wip_t426.md F6.1-F6.4;
durable law docs/re/chrome.md §6). MEASUREMENTS on the pure refcap
(round-palette space; pitfall: the *255//63 FLOOR map mislabels ~50% of
band px OFF — always round): (i) TOP band rows 0..6 = per-ROW census with
disjoint colour families bright(55/6/56/57/176)->mid(53/54/52/157/4)->
dark(50/51/49/48)->near-black(2/1/200), mean-lum 106.5->28.3, row7 100%
black; census IDENTICAL across map/planet-view/species-research (92-99.8%
rows 0,2-5) -> same screen-fixed field, census tables are the law shape,
NOT a ramp generator (option (b) dead by measurement, matching R-t422c).
(ii) CHAIN ORIENTATION: noise repeats ALONG the band (vendor h-run k1
0.653); edge-normal 5/25 replay blows the per-row chi-square on rows 2-4
(147/182/168 vs along-band 25/0 = 17/14/12, n=459/row). (iii) RIGHT
field-edge strip x466..472 = per-COLUMN census; col467/468 bright idx58/
173/59 ridge (133.6/133.7 mean lum) ABSENT from kRight -> flat law
refuted there; right edge BRIGHT vs left edge dark = NO mirror symmetry,
per-edge tables. (iv) LEFT band has NO row gradient (t422 F7 stands);
BOTTOM band mean-lum profile measured (65->ridge 160@475->104) but the
scratchpad census is 24-100% OFF-palette interpolation and every refcap
clips at screen 439 -> NO colour table derivable on disk, stays flat,
NAMED SEAM (closer: pure bottom-edge capture). PORT: textureColourAt
dispatches y-first kTopRow[7] (chain copy-left 25%, no repeat-up), then
kRightEdge[7]. PINS test_bandgrad_t426c.cpp x3, MUTATION x4 CAUGHT
(edge-normal chain -> hrep/vrep FAILs; flat-top -> dark+envelope FAILs;
flat right strip -> 4 named FAILs incl idx173-absent; AFTER-RESTORE 437/
0/0). WITNESS scripts/t426c_grad_witness.sh + t426c_witness_census.py
VERDICT PASS on our render (row means 109.0..28.8 vs vendor 106.5..28.3;
strip 87.0/131.2/133.2/121.8 vs 86.1/133.6/133.7/120.7); t426_plaque_
witness.sh still PASS (plaque 375/375). Residual: our h-repeat 0.406 vs
vendor 0.347 (copy-left 25% slightly long; 25/30 scored worse on row
chi2 — kept 25/25). LEDGER closes NOTHING (strict-close honest negative —
map visuals have no OQ owner; t414..t426c1 precedent). GATE_EXIT=0;
LEDGER AUDIT OK (17 closed / OQ-016, OQ-019, OQ-027 open). NEXT -> t427
planets list screen cycle (queue EXECUTION order; t426 thread closed at
its D18 cap).

t426 LANDED 2026-11-19 (GALAXY-MAP VISUALS CYCLE 1; working log
docs/re/_wip_t426.md F1-F5; distilled docs/re/t399-galaxy-map-3d.md "t426").
BORDER + PLAQUE + HOME MARKER MEASURED AND SHIPPED. (i) BORDER LAW: chrome
frames the field on all four sides (top rows 0..6, bottom 473..479, left
cols 0..6, right 466+), interior pure black to 7,7..465,472 — the t411
two-line bevel was the port defect (built off the NON-pure scratchpad);
REFUTED R-t426 banked. Port: black field fill + kTextureBands 2->4. (ii)
PLAQUE LAW 336/336 exact: raceflag k0 (rec+8 header law — my probe's
rec+0x18 k0 decode was WRONG; the C++ pin caught it) is a 14x24 half-frame
(row 0 = 14x idx19, col 0 idx19); vendor = 15x25 idx19 outline + navy at A
+ raceflag k<specnum> at the SAME A; residual 39 = right col 25 + bottom row
14. Plaque A=(10,10) UPPER-LEFT per user verbatim. (iii) HOME MARKER: same
composite at (starx-7, stary+3) + ONE white idx15 ring (ellipse centre
(starx,stary-2) rx6; NOT a shape record — census best 37.1% junk). The user's
"two rings" second ring = the lane-trace diamond idx111/idx115 through the
star [inferred]; no second constant-radius ring exists in the pure shot.
(iv) PINS test_plaque_t426.cpp x3 + test_rail_t400 band 2->4; SUITE 434/0/0.
WITNESS scripts/t426_plaque_witness.sh (--species 0): plaque block exact-diff
vs pure refcap 375/375 ZERO residual, bands 360/360 at y3/y473, crest frame
at the LOGGED home anchor; VERDICT PASS. MUTATION x2 caught (anchor +1 ->
166/375; band row shift -> black). LEDGER closes NOTHING (map visuals have
no OQ owner; t414..t425c precedent). GATE_EXIT=0; LEDGER AUDIT OK (17 closed
/ OQ-016, OQ-019, OQ-027 open). NEXT -> t426 cycle 2 chrome-band gradient
(the last named seam on this screen; D18 cycle 2 of 2).

t425c LANDED 2026-11-18 (GALAXY-MAP CONTROLS CYCLE 3; working log
docs/re/_wip_t425.md F7/F8/F9/F10; distilled docs/re/t399-galaxy-map-3d.md
"t425c" section). TOGGLE WELL LAW MEASURED BIT-EXACT AND SHIPPED. (i) THE
ASSIGNMENT'S PREMISE WAS WRONG: the four circles are NOT "pitch 44 inside the
race strip" — the strip is not in original-strategic-map.png at ALL. That png
is png = screen + 40 (rows 0..39 pure black, TURNCOUNT 474,7-632,43 measures
at png y52..80), so png rows 443..473 == screen 403..433 == the FOUR TYPE-25
LAYER TOGGLES at pitch 39 (x 479/518/557/596 = TOGLANES/TOGEMPIRE/TOGSHIPS/
TOGCOLONIES). Cycle 2's "pitch 44" numbers were RACE1/3/5/7 x0s. Cycle 2's own
ui.cpp comment ("strip at png rows 482..512, outside the shot") had it right
and contradicted the assignment's "do NOT add +40" — REFUTED ROUTE R-t425c
banked so nobody re-reads slot pixels from this file. (ii) THE LAW [verified
900/900 bit-exact x4, ZERO residual pixels]: a toggle blits its SHAPEFRAME
(1starmap k15..k18) at its verbatim rect and substitutes ONE palette entry by
state — well idx242 (raw (3,8,12) -> (12,32,48) navy) renders as idx80
(raw (22,6,14) -> (89,24,56) maroon) when ON, stays 242 when OFF. TOGLANES/
TOGSHIPS/TOGCOLONIES (BUTTONSTATE 1) exact under the swap, TOGEMPIRE
(BUTTONSTATE 0) exact raw; three independent sources agree on each button's
state (windows.txt BUTTONSTATE, the refcap well colour, handler init 0x2718c).
NEGATIVE CONTROL: the spin/zoom row is not state-painted (same swap degrades
74.6% -> 21.5%). (iii) PORT: blitShapePalSwap (vendortext.cpp + ui_internal.h)
= blitShape with one index substitution; ui.cpp step 3 gates i >=
MapCtl::TogLanes and passes on ? kToggleWellOnIdx : kToggleWellIdx; constants
mapchrome.h kToggleWellIdx=242 / kToggleWellOnIdx=80. PINS
test_mapwell_t425c.cpp x3, MUTATION-VERIFIED x2 (ON 80->81 fails 4; well
242->200 fails 6). SUITE 431/0/0 (+3). WITNESS PASS extended: togships well
maroon 647->0 / navy 0->647, togempire 0->644 / 644->0 — the port's swappable
pixel counts EQUAL the vendor faces' well counts (t425b face checks still
PASS; slot5 chroma 35.6->0.2). (iv) SECOND-SHOT SLOT RESULT
(scripts/t425c_slot_faces.py on scratchpad/galaxymap-original.png, the only
capture containing the strip): GEOMETRY confirmed — each slot's best match over
all five family members x 49 offsets is the +2 OUTLINED member at dx0/dy0
(62.3/52.6/61.2% slots 1/6/7; +1/+3/+4 <=13.8%), so t425b's help.txt
VISIBLE=+2 reading survives on real pixels. COLOUR is a NAMED SEAM: dominant
tone per slot is idx 16/24/20/32/28/36/40 — the family pair is SWAPPED for
slots 2<->3 and 4<->5 => [inferred] the vendor paints slot i's geometry with
the colour pair of the species occupying it (same substitution mechanism as
the toggles; this is the S-f data-driven colour). CAVEAT [verified]: that shot
is NOT palette-pure (off-table (95,73,111), (125,121,138); blend (0,138,66)
between conv idx16/idx19), which caps its percentages and keeps the 640x480 png
the exact-diff authority. (v) t425b's own "measured" slot numbers are now
corrected in place: they were toggle pixels (maroon/navy/maroon/maroon ==
BUTTONSTATE 1,0,1,1 — an independent confirmation of (ii)). LEDGER closes
NOTHING (strict-close: galaxy-map controls have no OQ owner, t414..t425b
precedent; the dial row needs the live feel verdict). GATE_EXIT=0; LEDGER
AUDIT OK (17 closed / OQ-016, OQ-019, OQ-027 open). NEXT -> t426 galaxy-map
VISUALS (breadth row for the same screen; D18 cycle cap reached for controls).

t425b LANDED 2026-11-18 (GALAXY-MAP CONTROLS CYCLE 2; working log
docs/re/_wip_t425.md F3/F4/F5; distilled docs/re/t399-galaxy-map-3d.md
"t425b" section). S-e CLOSED AS REFUTED, S-f HONEST NEGATIVE, FACE LAW
SHIPPED. (i) RUNTIME-RAMP PREMISE DEAD: (89,24,56) IS converted game.pal
idx 80 = raw (22,6,14) — cycle 1 compared refcap pixels against the RAW
table (false miss) AND mis-attributed refcap bottom-right pixels to race
slots when they are four ~37px layer-toggle circles at pitch 44 (x
479,523,567,611; scripts/t425b_face_census.py + vision). palette.md S3
already said the refcap is 307200/307200 inside the CONVERTED pal. No
runtime palette writer needed or found. (ii) FACE FAMILY LAW [verified,
canonical B-family rowwalk stream@rec+0x18 — the t399 k>=1 grammar
stream@rec+8 MIS-WALKS 1starmap, desyncs on over-paint ops]: slot i owns
FIVE records k(20+5i)..k(24+5i): dark face / bright face x plain + 103-
outline variant + grey k(24+5i). Faces are structurally IDENTICAL glyphs;
only the 2-colour index pair differs (16/19,20/23,24/27,28/31,32/35,
36/39,40/43). Port now paints them (ui.cpp drawMapOverlay step 4 +
mapchrome.h kRaceSlotFrameBase/Visible/Dimmed; visible=+2, dimmed=+4).
(iii) S-f: stride-0x1ee race-table colour byte (star-draw 0x29980 reads
race-row+2 as pal idx 0x10+4*b) could NOT be validated in any save —
scripts/t425b_race_probe.py found no base passing independent anchors;
diplomacy.md S10 already flagged the t423c2 0x12e16 census as unvalidated.
Port assumption slot i == owner i STANDS (unrefuted, not confirmed).
(iv) help.txt verbatim filter law banked ("species whose colors are
OUTLINED" == the +103 outline variant — vendor outline law). TESTS 428/0/0
(+1 mapctl_t425b_face_family_five_records_per_slot, mutation-verified x2:
+2->+0 fails, +4->+3 fails 7 tests). Witness PASS on the new law (slot5
chroma 35.6->0.2, lum 88.3->22.5, neighbours stable). LEDGER closes
NOTHING (no OQ owner; t414 precedent). GATE_EXIT=0; LEDGER AUDIT OK.

t425 LANDED 2026-11-18 (GALAXY-MAP CONTROLS CYCLE 1; working log
docs/re/_wip_t425.md F0/F1/F1b/F2). MEASUREMENTS: (i) COSMOSWnd 0x26b34
FULL MSG MAP closed (tree 0x26b4b + 0x27d2a + 0x27cce; 56 recenter
0x26a9c, 57 toggle win+0xc4, 58 toggle win+0xc8, 60 toggle win+0x58a,
61 toggle win+0xd0 AND win+0xcc, 62 toggle byte win+0xd8 bit(param),
63 mask-clear; init 0x2718c sets all visible, d8=0xff). PITFALL BANKED:
the handler's misaligned dword reads at [esp+0x36] sar 0x10 == the MSG ID
(word at esp+0x38) — NOT param1; a mid-iteration retraction is in the WIP
(F1b). (ii) DIAL-LAW SELF-CORRECTION: the t416 latch-on-click model was
RIGHT (gate 0x27d99 compares msg ids 50..55; buttons send SENDMESSAGE
50..55 — the earlier "gate on param1" draft claim refuted by the default
path 0x26b8f passing the same read to parent 0x336b4); what was wrong was
CADENCE — t302 measured msg 0x3b PERIODIC ~1/s, so the vendor spins at
2 DEG/s; kSpinTickMs 250->1000 (cam3d.h, cited). The D17 feel verdict
stays open pending a live read (not closed). (iii) THREE DEAD BUTTONS
ROUTED (ui.cpp): TOGSHIPS->shipsOn (transit pips), TOGCOLONIES->coloniesOn
(owner tint), TOGEMPIRE->empireOn (single-owner lane re-strike, starts OFF
per BUTTONSTATE 0 ln365); printed-only seam removed. (iv) RACE FILTER
(msg 62): raceVisibleMask XOR (1<<slot), slots' bit column verbatim 1..64
(ln429-435), consumer hides owner stars+pips, slot square dims half
luminance; FILTER ART honest negative: k20..k50 are solid swatches dark in
static pal vs refcap (89,24,56) runtime ramp — seam S-e named, NOT faked.
(v) CORNER POPUP CLICK: doEscape factored (t409+t410 verbatim), click in
exitPopupRect fires it. PINS test_mapctl_t425.cpp x4, MUTATION-VERIFIED x2
(empire default flip -> 1 fail; race-5 bit 16->8 -> 3 fails). Suite
427/0/0. WITNESS scripts/t425_mapctl_witness.sh PASS (four toggle flips in
one log line; slot5 mask 0xef; slot5 lum 137.0->68.5, slot1 unchanged;
field 1348 px; corner click EXITS the process). Shots
work/r1/loop/t425_{base,after}.png. LEDGER: closes NOTHING (strict-close:
galaxy-map controls have no OQ owner, t414..t423c3 precedent; the dial row
needs the live feel verdict). NEXT -> t425 CONT cycle 2 (S-e runtime-pal
ramp, S-f filter->owner chain).


t424 LANDED 2026-11-18 (PHASE-16 VERIFY + RE-EXPORT + PUSH + D17r2 SHEET;
full account docs/re/_wip_t424.md F0-F5). Verification PASS first: gate 0;
run_tests 423/0/0; SEED REGRESSION seeds 1/2024/23 md5 EXACTLY the banked
record (7e794a6dfb495800502762def9331e85 / 332a8cf3cebc95359924ce6a6b94a830
/ 0a6b7876719f38796e8235cb772a43d3; Extinct t266 / Extinct t285 / Control
t1406) — phase 16 (t421..t423c3) moved ZERO sim rng. CHIP-CLICK RNG AUDIT
(the row's VERIFY item): assignRaceColours (menulaw.cpp:47) consumes ONLY
the local colourLcg in the title loop, never the sim rng — click path
cannot move md5s; the regression is the mechanical confirmation. EXPORT
/tmp/pubpush-t424 vendor-free 7202 obj; data-less build 0 warnings;
data-less tests 423/245-skipped/0-failed; gate --portable 0. PUSH: remote
NAME pitfall hit in-flight (ascendancy.git does not exist — canonical is
ascendancy-rewrite.git); set-url BEFORE fetch (t389 law), fetched tip
9692126 zero foreign commits, FAST_FORWARD --force-with-lease landed
9692126..8525086 (11-commit gap t421..t423c3 CLOSED); POST-PUSH ls-remote
VERIFIED 8525086bc31bea4d458dbe8d6b2822259b16c322; askpass deleted,
verified absent. D17r2 SHEET (fallback only — web workflow PAUSED per D17):
scripts/t424_grading_page.py (tracked), 10 crops from MEASURED inventory +
PIL before/after DIFF-CLUSTER scan (chip diff -> DESC ring zone
352..448/32..160; hostile diff -> atmosphere wheel 288..352/384..480);
native-vision verified live content (red spiked orb + chip row; pink ring);
scratch-8699 self-test PASS incl traversal 403 (pitfall: server.py forks —
kill the LISTEN pid, not the shell pid); live :8613 serves it without
restart; D17r2 ask block appended to DECISIONS (q0 chrome/q1 newgame/q2
hostile orb/q3 chip — zero re-asks, no audio row). Shots banked
/tmp->work/r1/loop (t412-newgame refreshed; t412-raceintro-current added).
LEDGER: 17 closed / 3 open — closes NOTHING (strict-close honest negative:
verify+push+sheet ships no measurement; t420/t413/t403 precedent). NEXT ->
t425 galaxy-map controls cycle.

t423 CYCLE 3 LANDED 2026-11-18 (SCALE-LAW PAINT SITE CITED + BYTE+8
CENSUS CLOSED + FINAL GRADE PASS; working log docs/re/_wip_t423c3.md
C3-F0..F10; laws docs/re/t423-newgame-law.md SS12/SS13). MEASUREMENTS:
(i) PAINT-VTABLE ARCHITECTURE: window field +0xa7 = class vtable, paint/
invalidate slot +0xc; FOUR data-pool vtables registered by ctors
0x1abe6/0x31c5a/0x4d956/0x5b265 (0x88498/0x88838/0x88ac4/0x88c24, stride-4);
census scripts/t423c3_a7census.py. PITFALLS: the low-region +0xa7 imms are
SCRIPT pointers (different class, movsd chains) — conflated on first pass;
0x49359 is a memset ZEROING loop not a registration. (ii) vtable 0x88838
slot 0x32314 = generic shapeitem-list paint: FUN_0001fc34(0x9f10c,
sel=word[win+0x18]) + FUN_0005caac NATIVE run-decode + child-record loop
(stride 0xe, type->tint jump table 0x322f4, assert shapefile.cpp:0x186b).
(iii) DECISIVE (d): the state-3 paint function 0x526b4 (sole rel32 caller
0x52174, bounds == bottom panel EXACT) contains the CITED STRETCH SITE
0x52834..0x52877 — FUN_0005d5a1 called with NON-IDENTITY 16.16 affine args
(0,0x8000,0x8000; identity=(0,0x10000,0x10000) per decompile head) = the
vendor stretches the portrait record at this site; the 0x62 immediate is
the COLOUR arg (pal[62]) NOT a width (w98 coincidence superseded); exact
param semantics unresolved statically (named seam: selector ds:[0x6fd98]
->record, decider BPLM 0x52867). MEASURED 2x stands as the scale law.
(iv) CHIP CHAIN COMPLETE: 8 native blits x=379+16i via 0x53ee0 (tint ramp
pal[byte*4+0x13-k] from record +8), click stores word[win+0xb5] THEN
FUN_000232ec THEN repaint — port law exact incl. the field. (v) BYTE+8
CENSUS CLOSED "UI-only": imm 494 = EXACTLY 3 sites, the 0x44xxx pair is a
494-byte rep movsd RECORD COPY; [reg+8] byte reads 4/49k instrs none
race-adjacent => no campaign/map tinting consumer exists; cycle-2 "78
stride sites" premise was record copies. SEAM CLOSED honestly.
(vi) FINAL GRADE: t412/t423_hostile/t423c_chip witnesses all re-shot exit
0 + native-vision PASS (distinct wheels, solid DESC, ring portrait, 7
chips, red hostile orb). DEFECT (d) GRADE-CLOSED per the row's budget law
(t422 precedent). No code delta (measurement iteration); tests UNCHANGED
423/0/0. GATE_EXIT=0; LEDGER AUDIT OK 17/3 (closes NOTHING — New Game
laws have no OQ owner, t414..t423c2 precedent). NEXT -> t424 verify+push.


t423 CYCLE 2 LANDED 2026-11-18 (PLAYER-COLOUR LAW + RING-INDEX DISCOVERY;
working log docs/re/_wip_t423c2.md C2-F0..F7; laws docs/re/t423-newgame-law.md
SS9-SS11). MEASUREMENTS: (i) RACERING lib IS 8 colour-tinted 53x53 rings —
run-decode palette census: k0 green (0,141,68) .. k6 orange, k7 NEUTRAL
grey; same 7 hues + neutral as the t414 chip palette, same ORDER => ring
record index == player-colour index (race-record byte +8, stride 0x1ee);
DESC ring = k<idx> (measured (0,142,69)==k0), RACELIST row rings = k7
(row ring edges ZERO chroma, greys 35..186) — cycle-1's fixed k0 was a
port bug; FIXED both sites. (ii) FUN_000232ec CAPSTONE law (0x232ec..
0x23385; first decompiler read INVERTED the collision flag): slot0 =
clicked idx verbatim (7 allowed), AI slots rand()%7 distinct vs
already-written (scan bound j<i); guard 1<count. Ported pure
(menulaw newgameChipAt + assignRaceColours) + title.cpp click; tests
test_racecolour_t423c.cpp; witness scripts/t423c_chip_shot.sh (click
435,446 -> "player colour idx 3", DESC ring green->pink, 1105px diff).
(iii) windows.txt MSG 0 on Player^Color = "sends no message", NOT inert —
t401 reading REFUTED by the 0x529d2 handler. (iv) SCALE LAW (d): full
archive census — NO lib has a ~98 square record; lgrace 296x199 aspect-
wrong; portrait art run 94..101 px (2 bboxes) => smrace 49 STRETCHED 2x
via cited FUN_0005d5a1; per-site scale SOURCE (TYPE-10 paint field) NOT
found (RACELIST/class strings have zero data refs — strcmp family);
HONEST NEGATIVE, (d) grade-clean but law-unclosed -> cycle 3. Planet
zone w38 vs planets.shp 35px class NATIVE = no scaling, port stands.
(v) SMRACE preload string = "HBDATA\SMRACE%02d.SHP" (fallback dir absent
from the archives; DATA\ twin loaded). Tests 423/0/0; GATE_EXIT=0;
LEDGER AUDIT OK 17/3 (closes NOTHING — New Game laws have no OQ owner,
t414..t423 precedent). NEXT -> t423 CONT cycle 3.

t423 CYCLE 1 LANDED 2026-11-17 (NEW GAME LAWS: wheels/k12/volume/
sprites/spin/rings — deliverable docs/re/t423-newgame-law.md, working
log docs/re/_wip_t423.md F0-F10). MEASUREMENTS: (i) windows.txt state-3
table F0 (beginnew.txt premise FALSE — it's the tutorial script;
per-state record = RUNTIME field child+0x72); (ii) dispatcher 0x528eb
wheel law: density k(idx 0..4) table {15,25,50,75,100}@0x895c8,
species k(count+2)=k5..k9 (Five=k7 == t401 anchor), atmosphere
k10/11/12; port mapping EQUIVALENT (WIP F3 off-by-three was a misread);
(iii) 3cfgnew k12 truncation is IN THE SHIPPED ARCHIVE (cob blob 27349
md5 b2550068... == extracted; scripts/t423_f5_sibling.py) -> port
refusal was a BUG: walkRows partialOk LAST-record-only paints the
Hostile orb (test_shp pin FLIPPED; witness scripts/t423_hostile_shot.sh
shows red spiked orb + "Hostile Atmosphere"); (iv) FUN_00022728 preview
= circle r300 + depth 1000+-300 VOLUME (LCG consumer; R-t422c chrome
census unaffected), sprites cos_star SEL=4*K+cls K=0 seam -> k1..k3
2x2 native (census: k1..k15 2x2, k16..k39 1x1, k40..k51 zero, k52 3x6,
k53/54 8x8); (v) spin pump = script @0x69b8 SET ds:0x7458e armed by
cursor zone x379..493 y420..472 (0x52993/0x529c1; 43 xrefs, zero
state-3 writers) -> port hover-pump x6 (rate = named seam); (vi) rings
= racering.shp k0 53x53 record @2x both sites (defect e); (vii)
3cfgnew.tmp = SPARSE chrome-frame layer (10% px, margins only), NOT a
screenshot — sibling .tmp files same class. DEFECT SCOREBOARD: b,e,f,g
FIXED w/ witnesses; a law-equivalence; c no-delta; d OPEN (cycle 2);
player-colour click-reassign OPEN (cycle 2, SS7). Tests 421/0/0 (k12
pin flipped WITH the law, content witness rows 25..50). GATE_EXIT=0;
LEDGER AUDIT OK 17/3 (OQ-005 residue note updated with the shipped-
archive measurement; closes NOTHING new). NEXT -> t423 CONT cycle 2.

t422 CONT CYCLE 2 LANDED 2026-11-17 (NOISE-GENERATOR ROUTE EXHAUSTED —
STATISTICAL LAW DECLARED CEILING per the row's budget law; full account
docs/re/_wip_t422.md F11-F16 + REFUTED-ROUTES R-t422c). MEASUREMENTS:
(1) the exe's ONLY RNG is the Borland C-runtime LCG 0x7824f
(state=state*0x41C64E6D+0x3039, return (state>>16)&0x7fff; srand
0x78273; MSVC 0x343FD/0x269EC3 absent image-wide — not MSVC-built);
rel32 census = 59 call sites, 27 clusters, ALL sim/init/save-restore
(walked: 0x24f4b new-game seed draws then the banked preload cluster;
0x3f67a planitem picker %100; 0x2caec position pair; 0x21490/0x54f0d
srand FROM SAVED state) — NO chrome paint path consumes rand().
(2) FUN_0005d5a1 decompiled: affine shape-record STRETCH blit (16
vertex sets 0x8408..0x8457, 16.16 interpolation, byte 255 =
transparent skip, cache 0x9f10c via FUN_0001fc34, single xref 0x18676)
— zero noise math; FUN_00061058 = record-dims getter. (3) DECISIVE
scripts/t422c_rowperiod.py: the F8 stretched-buffer hypothesis REFUTED
— left-band row-identity has NO plateau at any k=1..440 (max 0.040).
(4) no static pattern table (single 13-byte run of the chrome colour
set image-wide). CONSEQUENCE: chrome.md SS4(a) rewritten as the named
honest seam (remaining conceivable decider = live debugger frame-pair,
NOT queued); NO rewrite delta shipped — swapping the fresh draw for an
uncited neighbour rule would violate D17 law (1); suite UNCHANGED
421/0/0 (no code touched — measurement iteration). PITFALLS: restored
DB coverage sparse (created FUN_00018686 this session; queries fail on
undefined regions); Cs.disasm has no skipdata kwarg in the revenv
build; Hermes kernel python has NO capstone/numpy — terminal +
revenv. LEDGER closes NOTHING (strict-close honest negative — chrome
seam has no OQ owner; t414..t421 precedent).

t422 LANDED 2026-11-17 (CHROME FIELD LAW DERIVED — root-cause row; full
account docs/re/chrome.md + docs/re/_wip_t422.md F0-F10). MEASUREMENT
(all on the PINNED 640x480 refcap shots; the 642x481 scratchpad shots
are interpolated garbage for texture stats — pitfall F3): the vendor
chrome mottle is a SCREEN-FIXED noise FIELD, not shape art — left band
x1..6 is 83.2%/99.1% pixel-identical across three DIFFERENT vendor
screens at zero shift; NOT a repeating tile (y-period k=8..240 at noise
floor); NOT iid and NOT cells (vendor v-run 0.616/0.234/0.092 vs iid
0.907/0.08). ROOT CAUSE of D17 "grainier everywhere": our per-pixel
splitmix hash = TV static (lag1 1.46/1.21 vs vendor 0.62/0.40) AND
t411's 6x6-cell recalibration was fitted on a WIDGET-CONTAMINATED band
(x474..632; pure-band v lag-1 is 0.40 not 0.23) so the cell grid was
wrong in KIND. NEW LAW (implemented, mapchrome.cpp textureColourAt):
per-pixel Markov chain copy-left 5% / repeat-up 25% / fresh draw from
the PER-COLUMN game.pal census (left kLeft[7][10] F7, right kRight[10]
F10), deterministic via splitmix64(x,y), no rng_. Witness: ours v_eq
0.405 (vendor 0.398), vrun 0.603/0.233/0.098 (vendor .616/.234/.092),
off-palette 120-grey px 0; native-vision grade: fine per-pixel noise,
no blocks/stripes. RESIDUAL (why CONT cycle 2): lag-1 h 0.96 vs 0.62 —
fresh-draw neighbour skew, decider = vendor generator decompile (above).
PINS: mottle_cell_law_t411 REPLACED by mottle_field_law_t422 (vrep
window [0.27,0.45] + cell-absence <60%); MUTATION M1 cell-quantisation
CAUGHT, M2 iid CAUGHT; suite 421/0/0; scripts/t422_fit.py tracked
(PH=0.05 PV=0.25-0.30 err 0.074). LEDGER closes NOTHING (strict-close
honest negative — chrome seam has no OQ owner; t414..t421 precedent).
GATE_EXIT=0; LEDGER AUDIT OK (17/3).

t421 LANDED 2026-11-17 (0x892ac TILE-COLOUR SEAM CLOSED — PER-CLASS LAW
REFUTED; full account docs/re/_wip_t421.md F0-F5 + pitfalls). MEASUREMENT:
copy site 0x3c274..0x3c2d9 capstone-verbatim — mov $0x892ac is UNINDEXED
(esi lifecycle: load is the ONLY write in the 13-insn window), movsd x2 =
8 bytes to esp+0x310, and all FOUR vertex colour slots get the same
immediate 0x960000=pal[150]; whole-image operand census (md.detail +
X86_OP_IMM/MEM walk; raw scan's 76 hits were misalignment false positives)
= EXACTLY ONE referrer 0x3c2a3, zero data-region pointers; callee 0x61770
never touches the caller stack; esp+0x310 overwritten at 0x3c5b4; runtime
mem[B+0x892ac] byte-verbatim 178/178 saved runs + deepest slot 60
(scripts/r1_t421_c3_runtime.py RC=0). CONSEQUENCE: t418's per-class reading
was a misparse; the port's uniform pal[150] fill IS the vendor law; no
rewrite delta; t420's blanket "every seam needs a live witness" is FALSE —
machine-closable work EXISTED. PLANETS-UI §12 + SUPERSEDED marker §11;
REFUTED-ROUTES R-t421. PITFALLS BANKED: payload-vs-restored fixup delta
0x82bb0 at 0x3c2a3 (0x66fc intra form); B = byte base, P0 = pointer-decode
constant (first C3 cut read P0 -> 178 false DIFFERs, law-window control
catches it); capstone linear sweeps desync on mixed code/data (skipdata=
True or trust banked objdump grep); capstone only in ~/tools/revenv.
LEDGER closes NOTHING (strict-close honest negative — seam has no OQ owner,
t414..t420 precedent). Gate + audits below.

t420 LANDED 2026-11-17 (PHASE-15 VERIFY + RE-EXPORT + PUSH + D16 SHEET; full
account docs/re/packaging.md t420 block + docs/re/_wip_t420.md). Verification
PASS first: gate 0; run_tests 421/0/0; SEED REGRESSION seeds 1/2024/23 md5
EXACTLY the banked record (7e794a6dfb495800502762def9331e85 / 332a8cf3cebc
95359924ce6a6b94a830 / 0a6b7876719f38796e8235cb772a43d3; Extinct t266 /
Extinct t285 / Control t1406) — phase 15 (t414..t419b) moved ZERO sim rng.
Export /tmp/pubpush-t420 vendor-free 7080 obj, uniform noreply identity;
data-less build 0 WARNINGS (t413's carried sign-compare hygiene CLOSED by
8877e8c) ; data-less tests 421/245-skipped/0-failed; gate --portable 0. PUSH:
set-url BEFORE fetch (t389 trap avoided), fetched tip c178a43 zero foreign
commits, FAST_FORWARD_OK, --force-with-lease=main:c178a43 landed
c178a43..9692126 (17-commit gap t413..t419b CLOSED); POST-PUSH ls-remote
VERIFIED 96921269e9267d601711a9591834e2ffa2e075ed; throwaway askpass
recreated from ~/.config/gh-pub-token, DELETED, verified absent. D16 SHEET:
scripts/t420_grading_page.py (tracked), 18 crops from MEASURED inventory
(t403_sheet_inventory run; all nine phase-15 shots md5-DISTINCT — no dead
frames), t419 shots banked /tmp/t419_shots -> work/r1/loop/; scratch-8699 +
scratch-DECISIONS self-test PASS (GET 200s, POST -> USER: line verified in
the SCRATCH file, scratch server killed by pid from ss — pkill pattern
didn't match); live :8613 serves D16 without restart (GET 200, crops 200).
D16 ask block appended to DECISIONS. LEDGER: 17 closed / 3 open — closes
NOTHING (strict-close honest negative: verify+push+sheet ships no measurement).

t419 LANDED 2026-11-17 (RESEARCH SCREEN: CPU STALL KILLED + 3D TREE + CORNER
EXIT POPUP; full account docs/re/_wip_t419.md F0-F7). STALL ROOT CAUSE fixed
as cited in the D15 addendum: researchDepth cleared its memo per call and
researchNodePos called it O(row) times — the painter ran the full prereq
graph O(n^2) PER FRAME. New law: ResearchLayout ONE memoised pass (depth +
slot + bbox centre) + researchNodePosAt/researchNodeScreen; wrappers keep
t408 signatures (all 8 t408 pins pass unchanged). MEASURED: 60 full-tree
layout+screen passes = 122 us (2.0 us/frame) vs the OLD law 2160 us for ONE
frame — the pin CHECK(old > 10x new-second) is self-contained. 3D: flat-XY
tree field projected through the t416 Camera3d BASIS API (generic
projectPoint added to cam3d, projectStar refactored onto it); focal ==
kResStandoff == 1200 makes the REST projection EXACTLY the t408 2D law
(pins + witness coordinates survive); rotate dials msg 50/51 pressSpin
(latch+pump, kSpinTickMs), move pair scrolls (user spec "up/down"); depth
z2 painter sort + perspective ring scale. RE LEG honest negative: no vendor
reswin draw-chain FUN exists in any on-disk disassembly window and the
Ghidra defined-strings table answered 0 even for known-present strings this
session — mechanism reuse of the CITED cosmos law shipped with the seam
NAMED. CORNER EXIT POPUP: ui/exitpopup.{h,cpp} pure law (24px corner probe
[port default], 78x47 glyph tuck); art = mouse.shp k5 (the t367
corner-anchor fallback record, shp.md S27/S28, D1 ruling KEEP — the image
the user remembered); polled SDL_GetMouseState (synthetic MotionNotify is
rejected by SDL — xsend warp still moves the real pointer); transition log
"ui corner exit popup shown/hidden". PINS tests/test_research3d_t419.cpp
(layout==old-oracle all rows; rest equality EXACT + spin moves view with z2
spread + dialLatch stop + hit-map follows rotation; frame budget; corner
law). Suite 417->421/0/0, 0 warnings. WITNESS
scripts/t419_research3d_witness.sh 5/5 PASS: study click lands, popup
shown+hidden, ESC 204 ms (was minutes), CPU delta 138 ticks/4s ~35% core
(ps pcpu 14.7-15.3 — NOT pegged), NATIVE-VISION PASS (rest grid + mid-spin
perspective + live Current Project panel). LEDGER closes NOTHING
(strict-close honest negative — D15 chrome has no OQ owner; t414..t418b
precedent). Gate 0, audits OK (17/3).

t418b LANDED 2026-11-17 (PLANET VIEW IMPLEMENTED — the planet itself, the
isometric tile grid, tile select, the F3 adjacency report; full account
docs/re/_wip_t418.md F6-F8). THE INVERSE-LAW CORRECTION (the session's
measurement delta): FUN_0003965c's row-walk test at 0x396b0/0x396b5 is
cum+C — B enters ONLY the col formula 0x3969a..0x396a6; the t418 F1
shorthand "cum+B+C" was a MISPARSE that lands invalid cols whenever B>0
(size-2 cell14: buggy row5 col8 invalid vs vendor row6 col4; cell18: buggy
row6 col8 vs vendor row7 col5). Code: TerrainTables carries grids B/C
(rowOffset/rowWidth; loader tokens 45..119 READ — grid B's t294 "no
consumer" skip retired, planetview is its cited consumer; operator==
covers both so test_terrain_t294's file==vendor pin now covers the grids);
Campaign::terrainTables() display accessor; planetview.{h,cpp} pure law
gridCellFor/gridRowCol/tileCenter/tileHitFor/orderCellBlock (citations
inline); ui.cpp kScreenPlanet paints planal[terrainRow].record(sizeIdx)
[F4 inferred seam] centred on the grid bbox centre (365,325 for EVERY size
class — derived), per-cell diamond fill pal[150] (0x960000 @0x3c274) +
dark outline (rock |8 darker [documented default]), planitem k[item] art
on occupied tiles, white outline on the selected tile; tile click selects
(diamond hit |dx|/34+|dy|/17<=1; GAP points refuse honestly — the witness
caught itself clicking one), project list annotates "(cell refuses)" via
the F3 leg. PINS tests/test_planetview_t418b.cpp x4; suite 413->417/0/0,
0 warnings. MUTATION 9/10 CAUGHT + M4 MISSED=PROVABLY VACUOUS (integer
dominance: the walk fallback rejects cell==+0x18 under both gate laws —
banked); M10 missed on run 1 (cell-0 fixtures only exercise +col/+row),
fixed with the State C all-pairs directional scan -> standalone CAUGHT
(skill rules 5+6 applied). WITNESS scripts/t418b_planetview_witness.sh +
t418b_witness_census.py VERDICT PASS (fill pal[150] 100% of 7 centres;
disc+structure art 1288 px; selection white 0->136) + NATIVE-VISION GRADE
PASS (grid, highlight, disc crop, sprite, PLANLIST — own eyes, D13). LEDGER:
closes NOTHING (strict-close honest negative — D15 chrome has no OQ owner;
t414/t415/t416/t417 precedent). Gate 0, audits OK (17/3).

t418 LANDED 2026-11-17 (PLANET VIEW — LAWS MEASURED; implementation ->
t418b; full account docs/re/_wip_t418.md F0-F5). THE 15-ROW DIAMOND GRID
LAW CLOSED [verified verbatim, FUN_000395c4 + FUN_0003965c disasm]: grid =
15 row-slots per size class; valid cols B[size][row] <= col < B+C
(B=rowOffset grid @0x7445c, C=rowWidth grid @0x744a8 — planitem.txt tokens
45..119 / 120..194, loader FUN_00037fc0 t294; the t294 loader SKIPS grid B
("no consumer") — IT NOW HAS THE CONSUMER); cell = cumWidth(size,row)+col-
B[size][row], inverse walks rows while cum+B+C<=target (0x396af..0x396c2).
ISOMETRIC LAW CLOSED [verified immediates, paint body 0x3b96c
work/t198_planwin.asm 0x3bb2c..0x3c26d]: center = origin + col*(34,17) +
row*(17,-34); x-cursor 110 +17/row (end 365), y 410 -34/row; tile diamond
68x34 (corners x±0x22, y/y+0x22 mid y+0x11) — the lattice steps are exactly
the diamond-tiling half-steps, so the four build-probe neighbours ARE the
four visual edge-neighbours; hit-test |dx|/34+|dy|/17<=1. Bare-tile fill
pal[150] (0x960000 x4 @0x3c274); per-terrain-class colour table 0x892ac
{00 00 01 03 01 03 02 02} -> 24-byte vertex-parameter sets UNRESOLVED
(NAMED SEAM). ADJACENCY LAW CLOSED verbatim (checker 0x385b7..0x3870d):
four FUN_000395c4 probes (row±1,col),(row,col±1); ACTIVE (word+2 bit0)
neighbour REFUSES an inactive new item; skips: cell >= WORD[+0x18], own
cell ACTIVE, item 5 Colony, item 38 Xeno Dig. DISC PROVENANCE HONEST
NEGATIVE: 0x3b98b blits slot 44 = 17np k4/k5 BACKDROP panels (625x357/
416x316), NOT the disc; port will use planal[terrainRow].record(sizeIdx)
(11 libs x 5-rung ladder 47/75/103/140/189, shp.md S23.3) [inferred];
closing witness = live-RAM census of cache 0x9f10c selectors during a
vendor planet-view frame. NATIVE-VISION grade of the vendor capture
work/r1/screens/t254/02_planet_detail.png: sphere ~250px centred (390,320)
under ISOMETRIC diamonds, structures ON tiles — confirms the shape law.
Tooling pitfall banked: r331_disasm.txt is INTEL syntax; store census must
parse dest-FIRST (three failed regex attempts before the fix). Tests
UNCHANGED (no code touched — measurement iteration). MUTATION N/A.
LEDGER: closes NOTHING (strict-close honest negative — D15 chrome rows
have no OQ owner; t414/t415/t416/t417 precedent). Gate 0.

t417b LANDED 2026-11-17 (PLANETS LIST BACKGROUND — IMPLEMENTATION OF THE
MEASURED LAW; full account docs/re/_wip_t417.md F8-F10). D15 defect
closed: ui.cpp no longer blits 10status k0 on state 10 (pure decline
screenPaintsShapeBackdrop in NEW ui/statusbg.{h,cpp}, citing the F1
4.5%-registration measurement + F6 TYPE-100 census; 17np/other screens
keep the size test). Status now paints the MEASURED code-drawn chrome:
black full-screen fill, perimeter texture bands x0..6/x633..639/y0..6/
y472..479 (textureColourAt, static tex built once), header speckle y8..36
(per-pixel weighted census + green title (0,170,82) at y18), divider ramp
y38..46 to solid (33,56,57), left border x7; row navy frame+outline
REMOVED (F4 zero separators); marker RED x16..69 top+2 h24 (F5); text col
200->288; pop bands 380->428; sphere centred x100/row-top+64 (F5 well);
generic tan header box + grey interior box skipped on status. GEOMETRY:
kStatusRowsTop 117->57, kStatusRowPitch 112->141 (F3; 57+3*141==480
exact) with the three named pin sites RE-SCOPED not deleted
(test_statuslist_t402 geometry, test_planetview_t406 fence,
test_statusnav_t405 probes). PINS tests/test_statusbg_t417b.cpp x5; suite
407->413/0/0, 0 warnings. MUTATION 9/9 CAUGHT (scripts/t417b_mutate.py:
backdrop-accepts, pitch-112, top-117, ramp-y46, weights-119, marker-x62,
rowguard-drop, ramp-pale-single, well-navy-k0) + AFTER-RESTORE 413/0.
WITNESS scripts/t417b_statusbg_witness.sh + t417b_witness_census.py
VERDICT PASS (k0 navy 0 px, interior strip p_black 1.000, perim texfrac
0.951-0.977, speckle census n=1099..6522, y46 solid 1.000, sep_rows 0;
marker red px 1296 on selected row, 0 unselected) + NATIVE VISION GRADE
PASS all six law points (work/r1/loop/t417b-status.png). WITNESS CAUGHT A
REAL BUG: first-draft speckle weights summed 119 vs modulus 98 -> rare
teals never fired (n=0); rekeyed to sum EXACTLY 98 + CHECK(sum==98)+
CHECK(counts[3]>0) pins. SEED REGRESSION seeds 1/2024/23 md5 7e794a6d/
332a8cf3/0a6b7876 EXACTLY per record (display-only, zero rng). PITFALLS
banked (F9): xsend keys need `key <NAME>` (bare word = click at point);
mutation campaign + parallel make in the same tree = poisoned AFTER-
RESTORE (skill rule 8 third manifestation — restore() now os.utime; run
campaigns ONLY as tracked background with timeout > runtime). LEDGER:
closes NOTHING (strict-close honest negative — D15 chrome rows have no OQ
owner, t414/t415/t416/t417 precedent). REFUTED-ROUTES t405(3) annotated:
arrow rects STAND, the "k0 is a backdrop" premise is dead — do not re-add
a k0 blit. Seam: marker FACE is flat (255,0,0) vs the vendor's measured
red gradient (face art uncited; shape/position law met).

t417 LANDED 2026-11-17 (PLANETS LIST BACKGROUND — ROOT CAUSE CLOSED WITH
MEASUREMENT; implementation deferred to t417b; full account
docs/re/_wip_t417.md F1-F7). D15 "the background... seems to be using one
of those images we determined wasn't used anywhere" RESOLVED: the port
blits 10status.shp k0 full-frame (ui.cpp:752 via backdropFor), and k0 IS
the D1 "A-series historical curiosity" asset the user called unused.
PROOF [measured, scripts/t417_k0_register.py — index plane via t391 law,
colour through game.pal + DOSBox conv, vs the t3 LIVE capture
work/screens/t3/planets_header_t1086_after_open.png]: registration at
shift(0,0) = 4.5% exact / 6.4% within-30 / mean|d| 149; k0 interior is idx
242 NAVY (12,32,48) x186,722 where the vendor shows (0,0,0) — THE VENDOR
NEVER PAINTS k0. windows.txt re-census: TYPE-100 SHAPEFILE binds ONLY
states 0,1,3,7,8,13,16,20,TESTDLG — no record binds 10status to any state
(status chrome is CODE-DRAWN). Vendor law [measured on t3 + user original
scratchpad/planets-screen-original.png, both agree]: BLACK interior;
perimeter mottled texture band x0..6/x633..639/y0..6/y472..479 (texfrac
0.94-1.0, same family as t400/t411); header y8..36 per-pixel dark speckle
(0,0,0)/.349 (8,12,16)/.327 (8,12,8)/.172 (8,28,49)/.062 + green title
(0,170,82); divider ramp y38..46 to SOLID (33,56,57) at y46; left border
x7 (33,56,57); NO row separator lines. GEOMETRY REFUTED+REPLACED [F3]:
rows top 57 (flag-box bands 57/198/339), pitch EXACTLY 141 (column-profile
autocorrelation single peak 0.634; user original agrees ~140), 3 visible
rows EXACT (57+3*141=480); t402's 112 was fit to the SURFACE-THUMBNAIL
art-centres (135.6/248.8/360.8 = row-top + ~78), not row tops. Selection
marker is RED x16..69 rows top+2 h~24 (t3 red census). Honest negatives
banked: header speckle values are DISPLAY-space (no game.pal exact match
under the conv — DOSBox X11 grab); row-0 column census ported to F5 table.
Tests UNCHANGED this session (no code touched — measurement iteration);
gate 0. LEDGER: closes NOTHING (strict-close honest negative — D15 chrome
rows have no OQ owner; t414/t415/t416 precedent). Tool banked:
scripts/t417_k0_register.py.

t416 LANDED 2026-11-17 (ROTATION AXIS WIRING; full account
docs/re/_wip_t416.md F1-F3; law docs/re/t399-galaxy-map-3d.md S8). VENDOR
DIAL LAW recovered fully static (capstone base-0): dial msgs 50..55 latch
an (active,dir) BIT PAIR on wnd+0xc0 (handler 0x26b34 chain
0x27da2..0x279eb: press starts CONTINUOUS motion, repeat stops, opposite
flips); the msg-0x3b pump (0x27a18, live ~1/s t302) applies +/-2 DEG/tick
about WORLD Y (spin pair, FUN_000283e4 edx=-1 -> 0x53584 -> per-vector
0x5324c x/z mix) / WORLD X (tilt pair, edx=0 -> 0x53554 -> 0x531dc y/z
mix) to the camera BASIS at wnd+0x14e (up,fwd; right=cross by FUN_00053804
every rotation); NO rotation clamp; recenter FUN_00026a9c rest immediates
right(1,0,0)/up(0,1,0)/fwd(0,0,1)/zoom 35.0/pos -1500 z [verified]; delta
unit = degrees (deg2rad f32@0x88b88). Sign table verbatim ROTLEFT +2 /
ROTRIGHT -2 / ROTUP -2 / ROTDOWN +2. The user's "rotate about Z" = the
vendor world-Y spin reading IN-PLANE at rest (vendor view axis = world z).
Code: cam3d.{h,cpp} REWRITTEN as the basis model (dialLatch pure law,
tick() pump application, yawLog/pitchLog keep the witness line shape);
ui.cpp map dials + sysview RotateLeft/Right press the latches; pump loop
before present gates on cam.moving() + kSpinTickMs 250 (documented; idle
cost unchanged); depthClass fed the TRANSFORMED depth (node+0xd law,
identical at rest). Rest projection reduces EXACTLY to the t399 formula —
t399 pins pass UNCHANGED. Tests 407/0/0 (+4 test_axis_t416.cpp: latch
table, world-Y in-plane + 90-degree fwd->x, world-X + 100k-tick
orthonormality, recenter immediates). MUTATION NOT RUN (budget) — pins
un-proven, named. SEAMS (S-a..S-d in _wip): pump cadence, standoff 1760
kept over vendor 1500 (fit law), right-drag continuous unimplemented,
f32[0x9f108] scale documented 1.0. LEDGER: closes NOTHING (honest
negative — D15 grades have no OQ owner, t414/t415 precedent); acceptance
is the user's via the t420 D16 sheet (LIVE re-check: one click = the field
KEEPS spinning; click same dial = stops; opposite dial flips).

t415 LANDED 2026-11-16 (RACE INTRO FRAMING + ART; full account
docs/re/_wip_t415.md F1-F7). LGRACE identified from the payload pool
(DATA\LGRACE%02d.SHP pool 0xB68, single PUSH site 0x233ff inside the
shape-loader cluster FUN_00023388 — per-race preload of SMRACE/LGRACE/
SMSHIP/DKSHIP, stride 0x1ee, verified). FUN_0002fb38's own field
accesses RESOLVE the three t412 "unmapped" rects: header (7,7)-(632,37),
right well (312,46)-(632,245), body (7,261)-(632,465) — all agree with
the bright-run census off the user screenshot to <=1 px. Section->well
mapping [verified decompile buffers + screenshot content]: INTRO ->
acStack_16c -> right well WHITE (0xf3 == pal[243]); TEXT+gated ->
acStack_624 -> body well race ink. PORTRAIT lgrace k0 NATIVE 296x199 at
(7,46) — template match MSE 73 (vs 336 best-of-coarse) at that origin;
EMBLEM raceflag k<specnum> native 14x24 at (9,10); FRAME colour pal[62]
(124,180,180), outer (2,2)-(636,477), header divider y40, band divider
y248, vertical separator x305 TOP BAND ONLY; pitch 13; both wells
CENTRE their lines; background = the t414 chrome page (no black fill).
Code: IntroPanel gains introWell/textWell (paragraphs KEPT for the t412
pins); runRaceIntro rewritten (+raceName param, title.cpp passes
speciesNameAt); lgrace from extracted/ascend02 refuse-once. Witness:
walk/t415_raceintro.png native-vision PASS on all six elements; the ONE
defect (body ink red vs vendor green for Minions) is the H3 runtime-
table seam, NOT the law — do not hardcode. Tests 403/0/0
(+raceintro_t415_well_split), 0 warnings, gate 0, ledger audit OK.
LEDGER: closes NOTHING (honest negative — no OQ row covers the intro;
t412 precedent); acceptance is the user's via the t420 D16 sheet.

WALKTHROUGH TABLE (own-grade before -> after; what to re-check LIVE after
`git pull`; all rows self-graded via native vision PASS unless noted):
  map clicks      | laser01 on every click (D13 regression) -> silent; rail/
                  | nav sfx only. LIVE: click empty map space, rotate, zoom.
  galaxy map look | pale sage wash + TV-static sidebar + flat frame + washed
                  | digits (t411 root cause: blitShapeScaled never set
                  | SDL_BLENDMODE_BLEND) -> blend fix, 6x6 mottle, bevel
                  | recess, outline-ring zero digits, depth-dim pips.
                  | LIVE: whole screen vs memory of vendor; day counter at
                  | turn 1; spin/zoom cluster still works.
  race intro      | ABSENT -> t412 text screen -> t415 FRAMED: chrome-
                  | page bg, outer frame + 3 dividers (pal[62]), lgrace
                  | portrait native (7,46), raceflag emblem (9,10),
                  | centred "Name: Power" header, INTRO white right well,
                  | TEXT+gated race-ink bottom well. LIVE: New Game ->
                  | Begin: framing + portrait + emblem show; text right
                  | for YOUR species; ink colour vs your species colour
                  | (H3 seam: Minions show red, vendor screenshot green).
  system view     | unreachable -> map STAR click opens orbit grid + 17
                  | LIVE: click any star; TOGGRID toggles grid.
  rotation dials  | one 0.25-rad step per click (t399 Euler port) -> t416
                  | vendor LATCH: one click = field KEEPS spinning, click
                  | again stops, opposite dial flips; spin = world-Y
                  | (in-plane at rest), tilt = world-X, no clamp.
                  | LIVE: click ROTLEFT once and watch; re-click stops.
  planet view +   | unreachable / could not set project -> colonised dot in
  project         | system view opens planet view; project list click sets.
                  | LIVE: set a project, next turn honours it.
  ships screen    | EMPTY -> fleet rows (name/location/orders, fn 0x50d12
                  | law). LIVE: rows match your fleet.
  research screen | EMPTY / could not select tech -> list + set-study law.
                  | LIVE: pick a tech, current study row updates.
  species +       | quite off / ability button DEAD -> menu content law +
  ability         | ABILITYWIN dialog (vendor path 0x55ffb). LIVE: both.
  escape chain    | flat -> one level per press map<->system<->planet
                  | (t252 law). LIVE: press Escape repeatedly, expect
                  | planet->system->map, map quit only at bottom.

t414 LANDED 2026-11-16 (NEW GAME ROUND 3 — ALL SIX D15 DEFECTS; full
account docs/re/_wip_t414.md). (a) FRAME: chrome-page law — textureColourAt
full 640x480 as a static texture + black cosmos rect kNewgameCosmosRect
(8,9)-(493,373) measured; panel gaps now show texture. (b) PREVIEW:
spinning coloured point field, N == kDensityStarCounts (splitmix64 sphere,
NEVER the sim rng; yaw += kPreviewSpinPerFrame; neutralTint); SPIN
measured (79 cosmos px moved between shots), density scaling measured
(633->699 visible-strip px, 50->100). The t393 previewCamp backdrop is
REMOVED. (c) WHEELS: 3cfgnew class census (k0..k4 dot-wells / k5..k9
icon-rings / k10 green / k11 blue / k12 red-spiked orbs) -> BIJECTION law
density k0..k4, species k(2+n), atmosphere k(10+v); repeated-frame defect
closed + pinned ("no frame unused, none repeated" test clause); k12
Hostile = print-once refusal (EOF-truncated record; port decode law;
named seam). Wheel blits clipped to panel (stacked-circle bleed caught by
own-grade). (d) PLAYER ICONS: t401's "no chromatic px" census REFUTED
(scanned the label rows); measured 7 chips x384+16k rows 434..459 with
measured base+hi colours (kPlayerChipRgb) + panel extended to y472
(measured navy extent). (e) PORTRAITS: blitShapeCircular clips the scaled
smrace to the ring (r53/r52) — the square-corner "4x size" defect closed.
(f) PLANET: planets.shp 35px-class sphere blit (group specnum%11, named
seam) replaces the vector disc. Tests 402/0/0 (+1
newgame_t414_frame_and_chip_law; wheel pins updated), 0 warnings, gate 0,
ledger audit OK. LEDGER: closes NOTHING in OPEN-QUESTIONS (honest
negative — D15 grades are user-ruling rows, t401 precedent); acceptance is
the user's via the t420 D16 sheet.

t413 LANDED 2026-11-16 (PHASE-14 VERIFY + RE-EXPORT + PUSH + D14 SHEET;
full account docs/re/packaging.md t413 block + docs/re/_wip_t413.md).
Verification PASS first: gate 0, run_tests 401/0/0, SEED REGRESSION seeds
1/2024/23 md5 EXACTLY record (full md5s re-pinned in _wip F2) — phases 13/
14 moved zero sim rng. Export /tmp/pubpush-t413 vendor-free 6889 obj,
uniform noreply identity; data-less build exit 0 but 2 sign-compare
warnings (test_statuslist_t402.cpp:201,226 — H1 above); data-less tests
401/241/0 (data-optional law HOLDS); gate --portable 0. PUSH: set-url
BEFORE fetch (t389 trap avoided), remote tip 06da9b2 zero foreign commits,
FAST-FORWARD --force-with-lease landed 06da9b2..c178a43; POST-PUSH
ls-remote VERIFIED c178a43c1f71...; 9-commit gap (t404..t412) closed;
askpass deleted. D14 sheet: scripts/t413_grading_page.py (tracked), 20
crops (3 low-colour flagged, native-vision verified LIVE content not dead
frames — FLAT flag is a census heuristic, vision is the arbiter), scratch-
8699 self-test PASS (POST fields -> USER: lines, traversal 404), :8613
live without restart (GET 200, D14 x10). D14 ask block appended to DECISIONS.
LEDGER: 17 closed / 3 open — closes NOTHING (strict-close honest negative:
verify+push+sheet ships no measurement).

t412 LANDED 2026-11-16 (NEW GAME FIXES + RACE INTRO; measurement log
docs/re/_wip_t412.md F0-F6). SPECIES-ROW SQUARES premise CLOSED by t411
(the blend fix already paints them -- current capture shows full portrait
art). RACE INTRO built: vendor law [verified Ghidra] FUN_0002b48a reads
history.txt (pool 0x82BB0+0x1190), SPECNUM-block scan, POWER/INTRO/
PEACE/NEUTRAL/HOSTILE/TEXT sections, transform '@'->newline '_'->space,
missing species -> 'Species %d not found in history file.'; TEXT-ONLY
screen (no portrait blit inside the parser -- the t412 queue's art census
resolves to text). Port ui/raceintro.{h,cpp} pure law; real-file census
[measured]: 21/21 blocks parse; specnum 1 is the ONLY race with non-empty
atmosphere-gated sections (107/76/108 chars) -- pinned gating BOTH ways
(including the 20 unchanged races). Ink law game.pal[racebyte*4+0x13] +
kIntroRaceBytes[21] static census. Wiring pitfall landed with witness
evidence: Begin handler's `continue` re-tests while(Title||RaceConfig), so
runRaceIntro is called DIRECTLY (state-assign-only exited the loop --
'ui title exit: raceintro'). WITNESS chain: raceconfig begin -> 'ui
raceintro specnum 0 atmosphere 1 ok' -> native-vision PASS (heading
'Supreme Planet Invaders', full Minion body red ink, no clipping, prompt
line) -> dismiss -> campaign map ('ui home star Amoroso'). MUTATION 6/6
pin-CAUGHT (terminator/'@'-law/clamp/ink*4/truncate/err-wording) +
AFTER-RESTORE 401/0. Suite 394->401/0 (+7 pins; test_boot_t385 state loop
7->8). LEDGER closes NOTHING (honest negative -- no OQ row covers the
intro; seams above).

t411 LANDED 2026-11-16 (MAP LOOK PASS 2; measurement log docs/re/_wip_t411.md
F0-F11; durable law docs/re/t399-galaxy-map-3d.md §7). ROOT CAUSE [verified]:
blitShapeScaled never set SDL_BLENDMODE_BLEND — SDL default NONE IGNORES the
alpha byte, so every .shp transparent-skip pixel (kept the 0xAA decode
stuffer) painted game.pal[170] (146,178,134) opaque pale sage: 3340 px on
the map screen = the washed digit faces ("empty ovals"), dial faces, rail
bands. One-line fix vendortext.cpp; witness census pale 3340->0. DAY
COUNTER premise RESOLVED: the vendor at day 0 shows five outline-ring ZERO
faces (vision + pixel census: vendor slot green 14-17%, ours 63%) — ours
binds camp.turn() to kDigitFirstFrame+d CORRECTLY (ui.cpp:912); after the
blend fix slot green 0.20 (vendor 0.14-0.17). MOTTLE LAW [measured]: vendor
sidebar band lag-1 diff/dev 0.23, our per-pixel hash 1.45 (TV static);
textureColourAt now generates the cited colour set+weights on a 6x6 cell
grid (scripts/t411_mottle.py sweeps our own statistic: cell1 1.57/2 0.78/
4 0.38/6 0.25/8 0.19 -> cell 6 closest); pattern SOURCE record stays the
t400 seam. Witness lag-1 on our shot 0.22. BEVEL LAW [measured vendor
scans]: field sits in a dark recess ramping to near-black at all four edges
(left x6 65->x7 49->x8 5->black; top/bottom/right in _wip F5); flat
(120,120,120) frame line replaced by kBevelMid(49,54,53)+kBevelIn(5,6,6)
two-line ramp (mapchrome.h); witness pixel (240,7) 136->5. DEPTH DIM:
cam3d pipDim256 {96,160,224,256} far->near wired into pip paint (vendor
pips vary brightness AND size, blob census 1..20+; ramp VALUES documented
defaults, cos_star unreadable OQ-005). DIAL WITNESS (queue item 6):
scripts/t411_maplook_witness.sh dial walk = 11 cam lines + exactly 3
named-seam lines (TogEmpire/TogShips/TogColonies = no-overlay seam);
t399 wiring confirmed live, nothing silently dead. Lanes-at-start + home-
star findability: verified correct in the grade (2 lanes touch the boxed
home star). PINS tests/test_maplook_t411.cpp x3 (mottle cell law incl
non-power-of-2 boundary probe, depth-dim monotone+domain, bevel verbatim+
ramp contract); suite 391->394/0. MUTATION scripts/t411_mutate.py (run in
BACKGROUND with restore-guard per t410 F6): 9/9 pin-CAUGHT; M10
(blend-line-removed) MISSED BY PINS AS EXPECTED — SDL wiring, the witness
pale census catches it (honest record F9). AFTER-RESTORE 394/0. NATIVE
VISION GRADE of work/r1/loop/t411-map.png: outline-ring green digits,
mottled sidebar, recessed field, dim far pips, no pale wash. SEED
REGRESSION seeds 1/2024/23 md5 7e794a6d/332a8cf3/0a6b7876 EXACTLY per
record (display-only, zero rng). LEDGER: NOTHING closed (strict-close
honest negative — D13 map-look has no OQ owner; seams S-a recess/pattern
art, S-b home-marker capsule ART, S-c pip brightness table, S-d overlay
toggles named in _wip F11). GATE_EXIT=0; audits OK (17 closed/3 open).

t410 LANDED 2026-11-16 (SYSTEM VIEW + MAP->PLANET CHAIN; law + working log
docs/re/_wip_t410.md F1-F6; state-16 census = windows.txt STATE "1 16" x20
records incl BatModeWnd/BatListWnd + 17 console buttons verbatim rects/
messages, chrome lib 16battle.shp via TYPE-100 ln1140-1142, NO full-screen
backdrop — max frame 173x141 so the orbit grid is code-drawn). ENTRY LAW:
a STAR click on the map opens the System Display (t338 measured state==16;
help.txt ln1149 names it — state 16 has NO TEXTITEM, so screenName
special-cases it); a click INSIDE BatModeWnd 7,46-465,437 on a COLONISED
orbit dot opens the t406 planet view (state 17) — bare bodies stay silent
(the port models one PlanetState per star, t406; opening 17 on a bare dot
would fabricate data). ESCAPE CHAIN: one level per press (t252 pixel-diff;
t369 corroborated), stack bottom = map standing-quit; push() re-entry
truncates instead of stacking duplicates; screens not in the stack (t252:
intel-from-species returns to species) stay flat — the stack only governs
the map/system/planet family. LANDED: ui/sysview.{h,cpp} pure (ScreenStack,
kSysCtl table 17 entries verbatim windows.txt incl Auto msg 808, shapeFrame
identity + t394 dim parity, orbitRadius 60+34i / orbitAngle, hitOrbitDot
radius law, systemOrbits zero-rng display accessor, seam census MyItems/
Abandon = -1), statuslaw 16 known+named, ui.cpp: map star click enters,
BatModeWnd click chain, state-16 paint (code grid via Camera3d default
focal — FIT LAW pinned: outer ring of a 5-body system stays inside the
viewport), home-star diagnostic (display-only, zero rng) for witness
targets, 16battle.shp joined the 7-lib chrome set. PINS
test_sysview_t410.cpp x7 (3 REQUIRE_DATA) incl named closer
star-click->system->dot->planet->esc->esc->map stack walk. Suite
384->391/0. MUTATION scripts/t410_mutate.py 9/9 CAUGHT (stack duplicate,
escape-past-bottom, rect drift, first-match-wins, shape offset, seam-face
accepted, colonised index shift, orbit pitch, hit radius) — AFTER-RESTORE
391/0. WITNESS scripts/t410_sysview_witness.sh VERDICT PASS (8 markers:
home-star diag, ui screen map -> systemview, ui systemview -> planet,
two esc unwinds, map return) + my native-vision grade: wireframe grid +
dots + right-column consoles render clean; one defect found and fixed
(BatListWnd seam text clipped at the list edge -> shortened). Seeds 1/2024/
23 headless md5 EXACTLY per record (no sim touched). GATE AMENDMENT 4c-d:
the t388 stage clicked NEXTTURN after ONE Escape from Intelligence, encoding
the OLD flat escapeToMap law; the pinned t252 opener-return law (now the
stack) goes Intelligence->Species->map, so the stage presses Escape TWICE
(cited in-script; gate green after amendment, GATE_EXIT=0). LEDGER: NOTHING
closed (strict-close honest negative — the D13 screen-chain complaint has
no OQ row; evidence stays here + _wip_t410.md; state-routing rows inside
OQ-016's closed block unchanged). PITFALL BANKED (F6): mutation campaign
foreground-timeout poisons the /tmp snapshot — see rationale above.

t409 LANDED 2026-11-16 (SPECIAL ABILITY DIALOG + SPECIES MENU CONTENT; law
+ full working log docs/re/_wip_t409.md F1-F6; durable law docs/re/
ui-runtime.md "t409" section). CENSUS VERDICT: a special-ability window
EXISTS — ABILITYWIN windows.txt ln2136 TYPE 22 STATE "0" 60,100-395,355
SHAPEFRAME -1 (code-drawn modal lib with HELPWINDOW/EVENTWIN; ABILBUTTON0/1
ln2152-2185 both cover the FULL rect, msg 50 dismiss). THE VENDOR BUTTON IS
WIRED: winmgr 0x55ffb `MOV EDX,0x85975`("ABILITYWIN")+CALL 0x56d1c -> CALL
0x37b14: specnum [0x7458e] -> race table 0x12e16+specnum*494 word +0x19a
>>24 -> sprintf "abil%02d" (pool 0x84848) -> CALL 0x33f40 -> WAIT (0x56015/
0x5526c). The rewrite's msg-5 NO-OP WAS the D13 defect. LANDED: ui/
abilitylaw.{h,cpp} (21-block parse, refusal census, rect+hit, %d day%s
formatter), ui/speciesmenu.{h,cpp} (static #11 header "K of T Species
Known" — t252 live "3 of 3"; rows = contacted owners, dipName in owner
colour + raceflag face (frame==specnum), static #12 "Extinct" at 0 stars —
t252 third row), Campaign ownerCount()/playerKnows()/ownerName()
(display-only), ui.cpp modal (draw last; swallows Esc/Return/Space/Alt +
all clicks; inside-dismiss/outside-inert) + species rows in kRaceRows[1..6]
+ row-press NEGSCREEN seam log. PINS test_speciesmenu_t409.cpp x7, suite
376->384/0. MUTATION scripts/t409_mutate.py 9/9 CAUGHT (M8 first MISSED =
VACUOUS FIXTURE seed-11 no-contact; re-scoped to seed-5 flip-observable ->
CAUGHT :298). WITNESS scripts/t409_species_witness.sh VERDICT PASS (open
abil00 / inside-dismiss / modal swallowed 2 of 10 Returns via "ui key next"
count=8 / species-row log / zero laser01) + NATIVE VISION GRADE ("Minions
Special Ability" + body + OK legible inside bounds; "1 of 6 Species Known"
+ FLUDENTRI row w/ flag over the map; shots /tmp/t409_shots/{ability-open,
ability-closed,species-menu}.png). SEED REGRESSION seeds 1/2024/23 md5
7e794a6d/332a8cf3/0a6b7876 == record EXACTLY. SEAMS (honest): S1 per-button
split of the full-rect hit law unmapped; S2 body wrap width = port choice;
Use-Ability msg-1 FIRE path (dispatcher 0x37b6a DX==1 -> 0x43b50 edx=1) NOT
wired — sim stays auto-fire (abilities.md §3), click-to-use would move the
seed md5s and needs its own sim row; species portrait art over the map +
NEGSCREEN state-13 chrome stay named seams. LEDGER: closes NOTHING
(strict-close honest negative — no OQ row owns the D13 chrome; OQ-016/019/
027 untouched). Gate 0; ledger audit OK; index check OK (17 closed/3 open).

WAKE PROCEDURE (t397, updated): (0) health-check the page server FIRST —
`ss -tlnp | grep 8613`; if dead, `cd work/r1/d1page && python3 server.py`
background (server code is generic: POST fields:[[label,value]] -> "USER:"
lines; regenerate page+crops with the HERMES venv python
`scripts/t397_grading_page.py` — system python3 has NO PIL; numpy now IS in
~/tools/revenv since t398). (1) read docs/DECISIONS.md tail + grep `USER:`
after the newest block; apply answers per strict-close (audio OQ-027 closes
only on a final HEARING verdict — the 11:37 line "seems OK at first listen"
is NOT it; chrome grades close nothing by themselves; D11b answered = drop).
(2) D12 ruling lines (labels 'D12 title hover ='..'D12 audio ='): record
verbatim in docs/re/_wip_t403.md F7+ and disposition the named screen item;
if a ruling reopens a screen, author ONE queue row citing the ruling phrase
(no fix-by-eye). NOTE: the 11:37 D11 ruling PREDATES the t401/t402 landings —
it grades neither; do not treat it as their disposition.

t408 LANDED 2026-11-16 (RESEARCH SCREEN STATE 20 + SET-STUDY LAW; law + full
working log docs/re/_wip_t408.md F0-F11; module docs in ui/researchview.h).
PRE-FLIGHT CLOSED first: t407 mutation re-run — TWO bugs (the named cwd bug
AND the real vacuity: run() grepped 'fleetlist.*FAIL' but harness.h:52 prints
'FAIL <file>' FIRST, so it could never match) — fixed to an exit-code verdict
with the 'fleetlist' filter; M1 CAUGHT with named FAILs :224-226, M2-M6
CAUGHT rc=1, fails=0: t407 pins PROVEN (fleet-screen.md F13 rewritten).
t408 CORE: (1) STATE 20 CENSUS [verified windows.txt]: TYPE-100 binds
20RES.SHP; RESWIN 7,46-476,472 + EXACTLY four pan children (RESROTLEFT
524,442-539,472 msg50 / RESROTRIGHT 540,442-554,472 msg51 / RESMOVEUP
563,442-593,457 msg52 / RESMOVEDOWN 563,458-593,472 msg53) => the RIGHT INFO
PANEL (x484..632, vision-measured) IS CODE-DRAWN, not a window. (2) CLICK LAW
= help reswin verbatim ln1668-1690 ("empty disks ... click on an empty disk to
make it your current topic") + the t268 live dossier (empty-disk click SETS,
confined 900px, no popup; discovered-disk = readout only): setStudy() Available
-> queue, Owned/Blocked SILENT. (3) PANEL TEXT = static.txt reswin.cpp pool
marker-driven: #122 "Current Project:" #123 "(No Progress)" #124 "(%d day%s)"
#125 "Allows" #130 "%s Knowledge %s" (second %s never rendered in ANY capture
= seam; t268 no-project panel BLANK -> #123 pinned as data only). (4) ALLOWS
= the banked 3/3 reverse join (gizmos+planitems tech field == row, table
order; Gizmo.resReq/PlanetItem.reqByte). (5) LAYOUT = derived depth x row
(restree carries NO coordinates; vendor organic positions = NAMED SEAM S1,
closer = pointer-law capture of the node table); pan = 4 buttons, rotate
pair X / move pair Y. (6) Campaign additions ALL display-only zero-rng:
researchTree()/techProgressFor/techRateFor + techRate_ write beside
techProgress, gizmoAt/gizmoCount. PINS test_researchview_t408.cpp x8
(includes the queue row's named closer: setStudy -> resolves at turn end on
the seeded campaign), suite 368->376/0. MUTATION scripts/t408_mutate.py 9/9
CAUGHT (M1 owned-accept, M2 blocked-accept, M3 header, M4 plural, M5 floor,
M6 allows-order, M7 MoveUp extent = the verbatim 554->563 gap, M8 precedence,
M9 Study-merge). WITNESS scripts/t408_research_witness.sh VERDICT PASS +
NATIVE VISION GRADE (gold-rim study ring, filled discovered discs, panel
"Current Project: / Spacetime Surfing / (0 days) / Allows / Star Lane Drive";
shots work/r1/loop/t408-{research-open,research-study,research-pan}.png).
WITNESS PITFALLS banked: grep-race sleep 0.4; SHOT-race (md5-identical at
+0.1 s) sleep 1.2; NEVER echo into app.log (the app's stdout offset
overwrites appended bytes — use probe.log). SEED REGRESSION seeds 1/2024/23
md5 7e794a6d/332a8cf3/0a6b7876 == record EXACTLY. LEDGER: closes NOTHING
(strict-close honest negative — no OQ row owns the D13 research chrome;
OQ-016/019/027 untouched). Gate 0; ledger audit OK.

t406 LANDED 2026-11-16 (PLANETS OWNED-ONLY + PLANET VIEW STATE 17 + PROJECT
SET; law + full working log docs/re/_wip_t406.md F0-F9). THE OWNER'S TWO
PLANETS COMPLAINTS ARE CLOSED AT THE MECHANISM LEVEL. (1) MEMBERSHIP:
statusPlanets/statusHeaderFor emitted ONE ROW PER STAR-RECORD NAME (Amoroso
II..N have no pop/items/queue — fabricated worlds = "displays planets I
don't own"); now ONE COLONISED PLANET per owned star, the port's per-star
PlanetState being the ownership unit (vendor basis t248 PROOF 1/2: owner byte
set == colonised, header counts NAMED+owner). Repro shot
/tmp/t406_repro/status-open.png showed 2 rows for a 1-colony campaign; the
after-shot shows exactly 1 ("Amoroso I (Small Husk Planet)"). (2) THE PLANET
VIEW EXISTS: row click -> state 17 (planet.txt info05 "click on either the
planet or the star to go directly to them"); NEW pure ui/planetview.{h,cpp}
(readout = shared statusLine1 assembly + pop/used/cap + the t276 gauge
selectors + project/days + the 0x508da noFreePopulation predicate); 17np.shp
k0 DECODED and joins the chrome libs (five panel borders land on the
windows.txt TYPE-29 rects — binding [inferred], rects cited). (3) PROJECT
SET: PLBUILD click opens the PLANLIST (planet.txt info04), list = REQUIRES-
gated table order with item<39 (0x388ec), and Campaign::orderProject applies
fn 0x38840 cmd0 gates verbatim (queue-empty 0x388e2, item<39 0x388ec,
freePop>=UPOP 0x388f7..0x38922); a gate failure stores NOTHING (silent
reject = vendor shape, SOUNDCHANNEL 0 on every PLANETALLOC child); the acc
word is untouched (resets live at completion 0x39290) and the cell stays the
cited t43 completion picker. [honest negative] the 0x3892a 4th leg
(ds:0x73e3c vs [rec+0x18]) is UNRESOLVED and unexercised (no cell passed) —
recorded, not modelled. AFTERCARE FIXED BY MEASUREMENT: kStatusRowsTop
46->117 (t3 capture table top border native 116.8; art header cells y 48..85
numpy) so the "name"/"size and type" cells are fully visible; marker/sphere/
text moved into the art's columns (62 / icon cell 136..167 / x 200). PINS
test_planetview_t406.cpp x4, suite 356->360/0 (t402 membership + t388
no-clamp pins re-scoped with regression fences, not deleted). WITNESS
scripts/t406_planetview_witness.sh VERDICT PASS (open view / list open /
"Amoroso I Factory (ordered)"). NAMED SEAMS left open (F8a-e): 17np's flat
green field (palette/key class), PLANLIST over the readout (PORT placement;
PLSQUARE surface grid unimplemented), decorative 34px art grid showing
through (vendor does the same), no surface/orbital grid, Esc from 17 ->
MAP per escapeToMap (vendor returns to the opener [unmeasured] — t410 pins
the chain depth). LEDGER: closes NOTHING (strict-close honest negative — no
OQ row owns D13 chrome/function rows; OQ-016/019/027 untouched). Gate 0;
ledger audit OK.

t405 LANDED 2026-11-16 (SUB-SCREEN NAVIGATION + RAIL STATEMENT; law +
full working log docs/re/_wip_t405.md F1-F10). PREMISE REFUTED with three
measured lines: (1) windows.txt re-parsed (136 records) — the five plain
rail buttons are STATE "1 1", NO sub-screen id appears in any rail list,
so no list "keeps the rail live"; (2) 10status.shp k0 DECODED via
tools/shp_pngdump + native-vision-graded (game.pal): full-width backdrop,
NO button faces at the rail y-bands — the standings panel + scrollbar
OCCUPY x>=474 in state 10; (3) the t3 live capture of the original agrees
(no rail visible, arrows far-right). The shipped rail-hiding law was
CORRECT; the owner's witnessed fall-through was the HIT-MAP: old PORT
arrow rects {566,...} + unbounded row test swallowed every click at the
rail's last-known position. FIX: unified pure statusHitFor (statuslist.h)
— arrows at rects MEASURED on the backdrop plane (up {619,48,638,94},
down {620,425,638,476}), scrollbar column {619,48,638,476} INERT between
them, rows only x 7..618; ui.cpp click chain replaced by one dispatch,
rejected points silent+inert; row-frame paint 632->618 so the vendor
scrollbar art shows (native-vision after-shot confirms). Esc-hint hunt:
"Esc: return to galaxy" is NOT vendor data (CP437 sweep of every extracted
file + exe strings = zero hits; t3 capture bottom-left has no text) — the
port's existing hint stands as a labelled PORT AFFORDANCE. PINS
test_statusnav_t405.cpp x4, suite 352->356/0. MUTATION (scripts/
t405_mutate.py, revert by FILE COPY from /tmp/t405-snap): M1 arrows->566,
M4 precedence flip, M5 rail-always-active, M6 clamp-unknown, M7 Esc-dead-
intel all CAUGHT with named FAILs; M2/M3 single-guard drops VERIFIED
VACUOUS manually (redundant guards, skill rule 6) — the old-code-shape
mutant M2c CAUGHT with named FAILs (test lines 42/44/56/60). WITNESS
scripts/t405_statusnav_witness.sh (Xvfb :97, dummy audio + trace): VERDICT
PASS — (580,60)=row select not scroll, measured boxes scroll, trough inert
(exactly 4 status lines), rail-position click switches nothing, Esc->map,
zero laser01. LEDGER: closes NOTHING (strict-close honest negative — no OQ
row owns chrome geometry; OQ-016/019/027 untouched). AFTERCARE banked on
queue row t406 (row-0 frame clips the art "name" header cell to "na";
vendor row content richer than ours). Gate 0; ledger audit OK.

t404 LANDED 2026-11-15 (LASER-SOUND REGRESSION + INPUT HYGIENE; law
docs/re/audio.md §6.7). Root cause ui.cpp:348 (pre-fix): EVERY left click
in COSMOSWnd played laser01 — an early placeholder the §5 note itself
labelled a documented port choice, never vendor law (SOUNDCHANNEL census
{0 x118, -0 x1} names no sample; laser01 = soundfx index 2, band2 combat
sample; port has NO fire-order interaction). Fix shape: ONE pure lookup
sfxForPress/sfxForEvent in ui/audio.{h,cpp} — MapClick SILENT,
RailButton/NextTurn/TitleButton click08 (rail GAINS it per the owner pin),
event "captured" -> bang01, out-of-range -> silent; all four call sites
(ui.cpp x3 incl. bang01, title.cpp x1) route through it, so the sweep pin
"no play(\"<literal> anywhere in ui/ui.cpp|title.cpp|main.cpp" is TOTAL.
PINS test_sfxpress_t404.cpp x5, suite 347->352/0. MUTATION 6/6 CAUGHT
(scripts/t404_mutate.py, revert by FILE COPY from /tmp/t402-style snap —
land uncommitted, skill rule 1; M1 map=laser01, M2 rail silent, M3
out-of-range->bang01, M4 captured-typo, M5 inverted gate, M6 placeholder
re-added). PIN LESSON (banked in-file + audio.md §6.7): CHECK(std::string(f())
=="x") is std::string(nullptr) UB when a mutant goes silent — suite died
rc-crash "CAUGHT ?" with no FAIL lines (M2/M4/M5); null-safe streq() helper
makes silent mutants fail with NAMED lines, re-run confirmed. WITNESS
scripts/t404_sfx_witness.sh (Xvfb :97, SDL_AUDIODRIVER=dummy — the
silent-degrade law nulls the engine, and the trace rides on it, so the dummy
driver is what makes --audio-trace deterministic; campaign seed 5 ENDS AFTER
TURN 1: order the script map->rail->Esc->next-turn or the window dies):
map click zero sfx lines, rail press click08 before its switch line,
next-turn click08 after its marker, laser01 zero anywhere — VERDICT PASS.
LEDGER: closes NOTHING (strict-close honest negative — removing a
placeholder measures nothing about the vendor's per-button choice; OQ-027
(a)+(b) stay OPEN on their own bars; D13 audio line unchanged, still awaits
the final hearing verdict). ADOPTION: tools/winpos ELF was untracked —
.gitignore now lists it beside the other three tool binaries.
t412 queue note updated (uncommitted prior-session USER WITNESS adopted in
the same commit): Begin->map ~3 s is mapgen time exposed BECAUSE the race
intro screen that should sit between them doesn't exist — sequence the
intro, don't chase a slow-mapgen bug.

t403 LANDED 2026-11-15 (PHASE-12 VERIFY + RE-EXPORT + PUSH + D12 SHEET;
full account docs/re/packaging.md t403 block + docs/re/_wip_t403.md).
Verification: gate 0; suite 347/0; seed regression seeds 1/2024/23 md5
EXACTLY the banked record (7e794a6d/332a8cf3/0a6b7876, Extinct t266 /
Extinct t285 / Control t1406) — transitivity law: t396 proved cbe7b8f ==
baseline c7a3fda, so phase-11/12 UI rows moved ZERO sim rng WITHOUT a
redundant baseline rebuild. REAL FINDING (export battery's reason to
exist): t402 REGRESSED the t396 data-optional law —
statuslist_word_tables_match_static_txt_t402 lacked REQUIRE_DATA();
data-less clone -> empty vector -> s[41+i] OOB UB -> run_tests SIGSEGV
139 (stdbuf -o0 pinned it). LAW: run the guard census (awk TEST/
REQUIRE_DATA pairing) on EVERY new data-reading test file. Fix cda9cb1.
Export /tmp/pubpush-t403: vendor-free 6654 obj, 0-warning build without
data, 347/218-skipped/0-failed, gate --portable 0. PUSH fast-forward
3be7e9a..06da9b2 (lease-pinned to fetched tip; t389 export-origin trap
RE-HIT — set-url BEFORE the deciding fetch); ls-remote verified ==
06da9b2fa8a4dc1a5e21838def2964a85b2ec262; askpass deleted. D12 SHEET
LIVE :8613 (scripts/t403_grading_page.py tracked; 12 crops non-flat PASS;
POST self-test PASS scratch port 8699/scratch DECISIONS; server serves
ROOT/index.html so no restart needed). LEDGER: closes NOTHING
(strict-close; honest negative); OQ-027 awaits the item-5 verdict.

t402 LANDED 2026-11-15 (PLANETS LIST SCREEN AS CODE, D11 "wrong and
unusable"). rewrite/src/ui/statuslist.{h,cpp} (pure law, no SDL) + ui.cpp
status painter/click branch + campaign.h buildAccFor/itemAt accessors +
runCampaignUi optional roster param (species dipName for the #151 header).
Laws cited in-file and banked planets-ui.md S8: row-assembly cluster
0x50647..0x5091f (size word = record+0x14 -> static.txt #41-45 Tiny..
Enormous; type word = +0x16 -> #46-56 Husk..Cornucopia; content-anchor
census r402_sizetype_census.py PASS slot order == runtime table order;
#137 Self-Managed leg 0x5077f); line2 #138/#139/#140/#141/#142 verbatim
(singular iff days==1 cited 0x5084e/0x50855); DAYS = FUN_0x47010 shape
(ind<=0 -> 0xffff sentinel else (cost-acc-1)/ind+1; Automation x3 leg =
named seam); membership t249 (owner==player); header #151 via
formatPlanetHeader; pitch 112 + 3 visible rows MEASURED on the t3 capture
(markers native y 135.6/248.8/360.8). PINS test_statuslist_t402.cpp 7
cases, suite 340->347/0. MUTATION 8/8 CAUGHT (scripts/t402_mutate.py —
reverts by FILE COPY from /tmp/t402-snap, land uncommitted; M0 word-table
content, M1 days division, M2 singular, M3 self-managed, M4b zero-ind
wrong sentinel [M4 ind<0 was SIGFPE crash not clean catch, skill rule 7],
M5 scroll overrun, M6 hit off-by-one, M7 header systems). WITNESS
scripts/t402_status_witness.sh on Xvfb: STATUS rail opens the screen,
scroll x2 + row-click land ("ui status select Amoroso"); shots
work/r1/loop/t402-status-{open,scroll1,select}.png show "Amoroso I
(Small Husk Planet)" / "No Project" rows + header "(2 Planets Occupied,
1 System Controlled)" correct singular. LEDGER: no OQ row matches (D11
chrome items live in the STATE queue); strict-close held — D11 planets
item USER-PENDING, nothing closed (honest negative).

t401 LANDED 2026-11-15 (NEW GAME FRAMING + PANELS, D11). Proved by
cited measurement + pins, law doc docs/re/t401-newgame-art.md:
windows.txt L575-717 state-3 SHAPEFILE 3CFGNEW.SHP binds NEWGAMEWND
SHAPEFRAME 0 / RACELIST SHAPEFRAME 7; wheel law newgameWheelFrame() —
density ladder-rank k0..k3 (top-two share seam), species k(2+n) anchored
k7@Five, atmosphere k10/k11; portrait class smraceNN.shp rec0 49x49
scaled 2x (NEW blitShapeScaled, vendortext.cpp); DESC panel OPAQUE pure-
black + green ring (0,142,69) r52@(409,97) + raceflag crest k<specnum>
NATIVE 14x24 + planet blit; Begin box = dot-noise band + smrace emblem
native; page texture t400 §4 class bands x0..6 + x494.. (right band x494,
NOT the map screen's 466). Value words inside bottom panels REMOVED
(original has none — summary block carries them). Suite 340/0 (+6 pins,
rewrite/tests/test_newgame_t401.cpp); MUTATION 6/6 CAUGHT
(scripts/t401_mutate.py, checkpoint a5f1284); witness
scripts/t401_newgame_witness.sh + t401_witness_census.py census VERDICT
PASS both shots (solid panel black 42149 / starish 0; racelist chromatic;
ring 1360; wheels distinct; begin dots 233; texture 3360/3360). LEDGER:
closes NOTHING (honest negative in S12 — no OQ row matches; D11 item is
user-pending). 3cfgnew k12 stays JUNK (OQ-005 residue, re-confirmed).

t400 LANDED 2026-11-15 (RAIL + SPECIES FLAGS + TITLE HOVER + FRAME
TEXTURE — LAW docs/re/t400-rail-hover.md + _wip_t400.md S1-S14):
(1) RAIL PLACEMENT [verified]: windows.txt SHAPEITEM = <enabled> <lib>
<frame> <dx> <dy>; rail rows carry 1starmap k5/k4/k3/k7 dx=109 dy=0 =>
icon at (rect.x0+109, centre-h/2) = RIGHT of label at NATIVE size
(583 vs measured 584/585; "wrong size" defect = user graded pre-t394 push
5373c66). Port was painting rr.x+4 (left) — FIXED. RACES/Intelligence
have NO SHAPEITEM (grep: SHAPEITEM only x4 rail + x3 3cfgnew).
(2) SPECIES FLAGS: raceflag.shp = 21x EXACTLY 14x24 (unique census class),
dominant colour EXACTLY (12,32,48) = rail fill (seamless blit); boxes
measured x521/x540 y288. Port law DECLARED (left=player, right=first AI,
human -> left empty): WHICH TWO races vendor shows = NAMED SEAM, decider
= live witness w/ known species. (3) TITLE HOVER [verified]: hovered band
fill (0,28,36) EXACTLY 9691px vs (0,0,8) elsewhere (pinned shot, cursor
on PLAYTUTORIAL); teals are consecutive t386-TSV GIF columns; windows.txt
has NO hover-state field (grep MOUSEFOCUS|HIGHLIGHT|BUTTONSTATE|... = 0)
=> code-drawn law. Implemented via titleButtonFill() + SDL_GetMouseState.
Bevel-vs-cursor residue in the one hovered sample = NAMED SEAM. RAIL
hover: NO witness, NO law — deliberately NOT implemented (honest).
(4) FRAME TEXTURE [geometry+palette verified, source record UNKNOWN]:
mottled grey-teal bands x0..6 + x466..639 full height in BOTH vendor
shots; field interior black; 10-colour census ALL in game.pal (weights
sum 74 + tail 4); 1starmap k0 REFUTED at cluster (7172 conflicts, 21%).
Port = splitmix64 hash-noise over the measured set/bands (pattern = named
seam). Cluster "missing bg art" resolves to this band; no panel record
exists. (5) rail fill (40,40,56)->(12,32,48) [palette.md §4].
VERIFICATION: suite 330->334/0 (test_rail_t400.cpp); mutation 6/6 CAUGHT
(scripts/t400_mutate.py; M2 top-align MISSED first — tolerance pin ->
re-scoped exact cy-h/2 -> CAUGHT; skill rule 4 followed); witness census
PASS on our own render (t400_rail_witness.sh + t400_witness_census.py:
bands 100%/97.9% in game.pal w/ port frame grey named+excluded, icon-zone
chroma 1128/806/984, flag zone non-flat w/ raceflag green, hovered LOAD
band (0,28,36)); shots work/r1/loop/t400-{map,title-hover}.png; headless
seed-1 md5 6f8281d078447b0dd036e1d27c7c3578 == t399 (engine untouched).
LEDGER: no OQ row matches (D11 chrome items live in the STATE queue);
strict-close held — SEAMS banked (two-race law, hover bevel, texture
source, rail hover), nothing closed on defaults.

t399 LANDED 2026-11-15 (GALAXY MAP 3D FIELD — D11 HEADLINE FIXED WITH
MEASUREMENT; LAW docs/re/t399-galaxy-map-3d.md + _wip_t399.md):
(1) VENDOR LAW [verified static]: FUN_00053324 = affine 3x4 float (the
camera matrix); FUN_00053374 = pinhole sx=frndint(x*zoom/z+K)+originX (fdiv
[eax+8]; zoom=COSMOSWnd+0x102; origins hi16 @+0x574/+0x576); paint loop
FUN_000284bc stores the TRANSFORMED z at node+0xd -> the t200 ±0xdc ladder
bands DEPTH, so SEL=4*type+cls picks depth-class pips (the original's
"varying size/brightness" EXPLAINED). Stars always listed (builder kind-0
unconditional) => screen star count == galaxy count IS the vendor law.
K@0x2c50/offset@0x105e relocation-patched [unverified] -> port centre/0.
(2) CODE: ui/cam3d.{h,cpp} (Camera3d yaw/pitch/focal + projectStar per the
law; fit law focal 680 standoff 1760 keeps 50 stars inside COSMOSWnd —
bounds pin; field CLIP rect so zoom never paints the rail); mapctl clicks
msg50..56 DRIVE rotate/tilt/zoom/reset, TOGLANES toggles lanes (per-click
step + continuous-drag = named seams); Star.z = splitmix64(seed,slot) in
[-r_shell,r_shell] — NO rng_ consumption PROVEN: seed-1 120-turn headless
log byte-identical before/after (md5 6f8281d0...); lanes drawn iff
Campaign::laneVisibleTo (t192 law — turn 1 = home-system lanes ONLY; old
code drew the full mesh = the D11 defect); home star exposed
(Campaign::homeStarFor) + ringed [shape named seam]; hit-test via
projection. (3) DAY COUNTER: t394 seam CLOSED by measurement (scripts/
t399_digit_faces.py decodes 1starmap k55..k64): IDENTITY digit->frame,
discriminator k56 uniquely narrow (w18 vs >=24, reads '1'); vendor faces
blit 1:1 through game.pal at the cited slot x's, CLIPPED to the panel,
ovals GONE (D11: "green circles with smaller numbers inside" removed).
(4) WITNESS /tmp/t399_shots/map.png (copy work/r1/loop/t399-map.png):
vision read — ~60-70 coloured points, BOTH lane lines touch the boxed home
star, five blocky green zeros, no clipping/glitches. (5) PINS 8
(tests/test_cam3d_t399.cpp: pinhole arithmetic 440->+170px, determinism,
zoom clamp/wrap, full-field bounds, z law, ladder ±220 edges, tint domain,
digit identity+k56 on real shp, home+turn-1 lane law); MUTATION 3/3 CAUGHT
(frame 55->54, focal 680->900, ladder 220->221), clean revert. Suite
322->330/0; gate 0. NO ledger row closed (strict-close; queue work; OQ-012
already CLOSED). Tools banked: scripts/t399_disasm.py (capstone base-0
disassembler — REVENV python has capstone, system python3 does NOT),
t399_digit_faces.py. Pitfalls banked: run_tests compiles ui/*.cpp sources
DIRECTLY — a new ui source must be added to BOTH ascend_ui AND the
run_tests list; a decl inside anonymous namespace never binds an exported
definition; t398_palette_witness.sh env is OUT= (not SHOTS).

t398 LANDED 2026-11-15 (PALETTE FIDELITY — THE GREYSCALE DEFECT CLOSED WITH
MEASUREMENT; game.pal IS THE IN-GAME PALETTE; LAW docs/re/palette.md):
(1) IDENTITY [verified]: the exe names `DATA\game.pal` verbatim at payload
0x83579 (corn.cpp init cluster) + 0x84207 (flicwin/font cluster); file = 768 B,
256 triples, all channels <= 0x3f (6-bit DAC). (2) MEMBERSHIP LAW [measured]:
ALL 307200 px of each pinned in-game refcap shot (strategic-map, species-
research, planet-view) lie inside game.pal under the DOSBox conv c=(v<<2)|
(v>>4); title only 8.79% (title keeps the t386 TSV — the old boot.md seam
prose had conflated the title refutation with the chrome question).
(3) REGISTRATION [measured]: 1starmap k5/k4/k3 through the table match the
pinned shot rail at mean |RGB diff| 3/6/6 (93-97% px within 12) at the cited
kRail rows; icon x=584/585 = RIGHT of label (geometry delta -> t400); k7
position exact, degraded by the Intelligence-row overlap. Rail fill teal
(12,32,48) == idx 242 exact. (4) CODE: formats/gamepal.{h,cpp} (refuse-not-
clamp 768 B, conv table, argb wraps), blitShape paints through it, ramp kept
ONLY as the announced degradation (`ui palette: ... (degraded: greyscale
ramp)` — live-witnessed on a scratch data root minus game.pal, never game/);
loadChromePalette once-per-process in both loops. (5) WITNESS: scripts/
t398_palette_witness.sh + t398_witness_census.py VERDICT PASS — rail zone 131
chromatic colours, 130 in game.pal, the ONE outside = (40,40,56) our own port
fill; the ramp yields EXACTLY 0 chromatic px (mechanical discriminator, R13-
safe). Screenshots work/r1/loop/t398-{title,load,newgame,map}.png for the
next ruling sheet. (6) PINS 4 (whole-table FNV + v*4-vs-law discriminator at
v=16 + alpha + size-refusal + title-refutation half); MUTATION 3/3 CAUGHT,
clean revert. Suite 318->322/0; gate 0; seed-1 spot Extinct t266 == record
(UI-only change). Tools banked: t398_band_register.py (conflict-richness
selection law: flat placements are VACUOUS — flag them), t398_palette_
register.py; numpy pip-installed into ~/tools/revenv. NO ledger row closed
(strict-close; queue work). Harness observation banked: the 11:40:35
"selftest=ok" ruling line was stripped from DECISIONS.md by t397b but
survives in work/r1/d1page/server.log — no ledger meaning.

t397 LANDED 2026-11-15 (D11 GRADING PAGE — channel repair, not a measurement):
trigger audit NEGATIVE (DECISIONS.md mtime 04:55 predates commit 04:57; no
USER: after D11; no *ruling*/*reply* files; timeline last grew Nov 12 -> no
sitting, r1_t85g_sitting.py correctly NOT re-run). FINDING: the live ruling
server (pid since Nov-09) still SERVED the closed D1 sheet and its POST
handler was HARDCODED to D1 fields — a D11 answer posted to it would have been
mangled into D1 lines. Fixes: work/r1/d1page/server.py generalized (fields
shape + legacy D1 fallback + env overrides D11_PAGE_PORT/D11_PAGE_ROOT/
D11_DECISIONS_FILE, defaults identical) and RESTARTED on 8613; old sheet
archived at /index-d1.html; scripts/t397_grading_page.py (tracked generator)
rebuilds index.html + 2x-nearest crops from loop captures — readability law:
text bands shown as native-res crops, NEVER browser-scaled 640x480; crops
VERIFIED by vision read before shipping (hints "Load Game/Alt-L", title art
"ASCENDANC"+menu, map sidebar ovals+arrows+Planets/Ships/Research, race rows
Minions/SNOVEMDOMAS/Orfa — SNOVEMDOMAS is real vendor data,
extracted/ascend00/static.txt:304); map-turn1.png EXCLUDED (black post-quit
teardown frame would misreport a black screen). Self-test PASS on SCRATCH port
8699 + scratch DECISIONS (real file never a test target): POST->USER: block,
GET 200s, traversal 403. Pitfalls banked _wip_t397 (crop-by-measurement not
guess; pkill -f self-match). NO ledger row closed (strict-close; a shipped
page is not an answer); OQ-016/027 notes point at the page, OQ-019 note
re-pins DEFERRED-do-not-re-ask. Full account docs/re/_wip_t397.md.

t396 LANDED 2026-11-15 (PHASE-11 VERIFY + RE-EXPORT + PUSH): verification
PASS first (gate ALL PASS; 318/0/0; seed regression seeds 1/2024/23
byte-IDENTICAL vs c7a3fda baseline, md5s == t389 record — engine untouched by
t393-t395 PROVEN). REAL FINDING: the t383 privacy gate was VACUOUS — `xargs
git cat-file --batch` appends ids as ARGS (git dies "batch modes take no
arguments"), 2>/dev/null+||true hid it, 0-byte scan made exit-5 unreachable;
REAL stdin scan (3399 blobs, positive control) found 1 blob with the FULL
personal ISP address (docs/re/_wip_t383.md historical — t383's SCRUB_PATHS
covered only one other file) AND proved it was ALREADY PUBLIC (same blob in
pushed pubt391). Fixes shipped in publish_public.sh: stdin scan + fail-closed
<1MB + positive control; full-address + bare-domain ERE masks over ALL paths
(sed BRE pitfall MEASURED: bare | is literal — both seds run -E); --msg-filter
pass (commit c953fc8's MESSAGE held the domain). Data-optional law restored:
newgame_t393_lore_file_real_data lacked REQUIRE_DATA() -> lore[0] UB ->
run_tests SIGSEGV on data-less clones (stdbuf -o0 pinned it; census: only true
crasher). Canonical export /tmp/pubpush-t396c: vendor-free 6459 obj, build 0
warnings, tests 318/205skipped/0-failed WITHOUT data, uniform noreply
identity. PUSH force-with-lease=main:5373c66 (fetched first; remote tip tree ==
pubt391 tree, zero foreign commits); ls-remote VERIFIED ==
3be7e9af6c242ec90a0d3a83391375f1587a1511; askpass deleted. NO ledger row
closed (strict-close). Full account docs/re/packaging.md t396 block +
docs/re/_wip_t396.md.

t395 LANDED 2026-11-15 (SOUND AUDIBILITY, D10 "not hearing any sound on
Athens"): THREE defects, all pinned + live-witnessed
(scripts/t395_sound_witness.sh PASS: `audio: driver=dummy sfx=86 tunes=3
vol=127` / `music 0 theme00` on title entry / `sfx click08` on the INTRO
button click, NO --audio flag passed): (1) AUDIO WAS OPT-IN on the --ui
path (plain boot opened NO device and printed NO line — indistinguishable
from a dead card); now default-ON, --no-audio opts out, non-UI paths keep
opt-in; (2) ROOT CAUSE MEASURED: click08.voc exists in ascend01/data but
soundfx.txt does NOT list it -> play("click08") was a SILENT NO-OP since
t388; init() loads it explicitly (85->86 chunks, gate 4d updated); title
buttons play click08 symmetric with the rail (port choice per §6.5, never
vendor law); (3) tried-paths diagnostic: degrade line names last path,
missing-music error names BOTH archive layouts. MENU-MUSIC ENTRY LAW made
pure + pinned (bootTune(Title)==0, else kTuneNoChange=-2); playTune
hardened t<-1 no-op (was UB). SOUNDCHANNEL census RE-RUN
(scripts/t395_soundchannel_census.py): {0 x118, -0 x1}, -0 in ALIENDIP
0x51aa — re-pins §6.5, "channel 0 = click08" stays NOT citable. Suite 318/0.
NO ledger row closed (OQ-027 stays OPEN — census re-pins the negative;
strict-close). Law banked audio.md §6.6 + _wip_t395.md.
t394 LANDED 2026-11-15 (galaxy-map sidebar chrome + WM-scale fix, D10
"galaxy map still wonky... all the buttons off the galaxy map are wonky
too"): DIAGNOSIS closed mechanically — user's shot IS the map screen where
NO backdrop exists by law (10status blits in state 10 only); wonkiness =
user's WM rescaled our 640x480 window to 512x384 (clean resample: 408
colours, nearest-upscale adds ZERO; our Xvfb witness 640x480 exact). FIX:
SDL_RenderSetLogicalSize(640,480) on every renderer (SDL_render.h doc:
mouse events rescale into logical space; letterbox default) — ui.cpp
applyLogicalSize + title.cpp. MAP SCREEN REBUILT to cited chrome
(mapchrome.{h,cpp}, 5 pins, suite 313/0): string dump REMOVED; TURNCOUNT
474,7-632,43 + five green ovals MEASURED x482/513/544/575/606 pitch 31
(digits via port face, frame-mapping NAMED SEAM); NEXTTURN k65/
NEXTTURNCONT k66 faces (74x30/75x30 exact); spin/zoom/toggle cluster
SHAPEFRAMEs 8..18 — DIMS PARITY LAW every shape == rect minus-1 (pinned
vs real 1starmap.shp); RACECONTROLS k19 158x30 strip + 7 species squares
479+22i,449 (slot-1 green MEASURED exact; CVD palette seam). Click seam
lines printed for pan/zoom/continue (never fake). CAPTURE LAW CORRECTION:
t394 original maps IDENTITY (t393 minus-1 does NOT generalise). Witness
scripts t394_map_witness.sh + t394_map_mass.py CENSUS PASS (oval green
350, dump band 0 white, clusters non-flat, 7 slot dominants distinct);
shots work/r1/loop/t394-map.png (map-turn1.png = post-quit, --campaign 1
exits after advance — grade map.png). Law banked ui-runtime.md t394 block
+ _wip_t394.md. NO ledger row moved (strict-close; queue work).
t393 LANDED 2026-11-15 (New Game screen rebuild, D10 "garbled and
unusable"): ROOT CAUSES closed — (1) RaceConfig was an OVERLAY under the
live title frame (title.cpp rewired to a full-screen else-branch; screen law
mechanically witnessed: title fill (0,0,8) count 0 on the New Game shot);
(2) the user's clipping = their WM scaled the window to 512x384 (0.8x) —
law rects all FIT 640x480 (pinned) and a `ui window WxH (logical 640x480)`
diagnostic line now prints at title entry (our own Xvfb: 640x480 exact).
LAYOUT LAW banked boot.md S8 + menulaw t393 block: state-3 window-table
re-parse (COSMOSWnd "4 1 3 7 13" => starfield backdrop IS the table's law;
rail children registered but NOT painted [verified on original]); Begin New
Game (494,373)-(639,472) CITED-MEASURED off the user-supplied original
(STARTGAME STATE "1 12" cited negative; capture->screen = minus 1, anchored
on GALAXY_MORE x0=7 + bevel census); RACELIST = THREE-slot scroll window
(pitch 108, bands 49-153/157-262/266-372) + 16x16 arrows (616,47)/(616,356)
[measured]; text law static.txt //153 name green rows 18-27, //154 "The %s
%s" x newgame.txt line N+1 (21 fragments, EOF 0x1a, loadNewgameLore refuses
otherwise — REAL file pinned incl. the race00 "for the Minions" leading-the
strip), //168 summary template words 155-167 on the t78 MEASURED ladder
(50/75/100/15/25), Neutral default measured on the original. INPUT: arrows
scroll, rows select, *_MORE cycle one rung, Begin -> Campaign (prints
settings; APPLYING them = named seam, buildCampaign already ran),
Player^Color MSG 0 inert. PORTRAITS stay a named seam (t391 witness weak):
grey disc + dipName. 7 pins (test_newgame_t393.cpp), suite 308/0, gate 0,
witness scripts t393_newgame_witness.sh + t393_witness.py (13 checks PASS;
RUN WITH ~/tools/revenv/bin/python — repo .venv has no PIL, banked),
screenshots work/r1/loop/t393-*.png for USER grading. NO ledger row moved
(strict-close; queue work).

PHASE-10 HISTORY: PUSH GAP CLOSED 2026-11-14 (user: "nothing has been committed to Github"
— CORRECT: t390/t391 were local-only; t389's push covered phase-10 proper.
Export /tmp/pubt391 verified vendor-free 6349 obj, builds WITHOUT data
0 warnings, run_tests 297/199-skipped/0-failed, EXE present; FAST-FORWARD
36bf92d..5373c66 verified post-push by ls-remote). t390 ART WITNESS: our
own Xvfb render art-zone coverage 0% -> 100% (PIL mass, mechanical);
screenshot work/r1/loop/t390-title-after.png for USER look-grading.
(phase-10-era note "every remaining closer is a human witness" proved
premature: the human witness ARRIVED as D10 and generated phase 11.)

t391 LANDED 2026-11-14 (presentation sweep — every screen now art-backed-or-
honestly-vector, cited): windows.txt TYPE-100 sections head each state's
windows; FIVE headerless sections (load/save 2-4-15, status 10, intel 14,
planet-alloc 17, fleet 18) — on disk 10status/4loadgam/2savegam/14intel/17np
exist, NO 18*.SHP exists at all => FLEET chrome honestly-vector in ANY
faithful port. REGISTRATION PASS at shift (0,0) through our own ramp blit:
10status k0 295,063 px 0 conflicts; 4loadgam k0 50,296 px 0 conflicts (task
(a) answered: k0 IS the full backdrop). SHAPEITEM census 7/7 all implemented
(rail -> 1starmap k3/4/5/7; NEWGAME children -> 3cfgnew k0). Mass census
PASS 8/8 shots (work/r1/loop/t391-<screen>.png). NAMED SEAMS kept open:
7racesel 8x158x30 species-row strips (size-match only, SHAPEFRAME -1 — do
NOT blit without a stronger witness), 2savegam art-in-hand (no save screen),
17np k0 for state 17, chrome COLOUR = luminance-ramp palette seam. HONEST
NEGATIVE: zero code change — no screen had vendor art the port paints vector.
Law docs/re/ui-runtime.md t391 block; NO ledger row moved (strict-close).

t390 LANDED 2026-11-14 (title art blit — user grade "still not drawing the
UI" mechanically closed on our own render): C++ GIF87a index-plane decoder
rewrite/src/formats/gif.{h,cpp} BIT-EXACT vs the PIL reference plane
(ndiff 0 / 307,200 B; FNV pins tests/test_gif_t390.cpp; code-width law
grow-at-next>=2^width MEASURED, early-change desyncs at 11208; interlace
read from the IMAGE DESCRIPTOR — the logical screen byte 0xd7 is a TRAP);
titlepalette.{h,cpp} loads title_palette_t386.tsv (52 mapped, GCT fallback
flagged per-index); title.cpp blits at (0,0) with index-255 alpha-0 key
hole, then band fill (0,0,8) + VendorText white (215,215,215) per the NEW
BAND-CLOSURE LAW (measured per band on the pinned vendor shot: rect pixels
are EXACTLY fill+white). NEW NEGATIVE [verified]: 0opening.shp strips are
NOT the label glyphs (best shift overlap 74/234; bbox mismatch) — t386 §7
composition corrected, residue banked title-art.md §6.6. Witness
work/r1/loop/t390-artzone-witness.png + scripts/t390_artmass.py PASS
(mass 124,800, all 7 bands other=0, top-5 colours in TSV vendor set).
297 tests 0 failed; --campaign 400 seed 1 spot-check Extinct t266 ==
record. NO ledger row moved (strict-close; queue work). Full evidence
docs/re/title-art.md §8.

PHASE 10 LANDED + PUSHED, LATEST 2026-11-14:
https://github.com/weylandsmith/ascendancy-rewrite.git main = 36bf92dbb4bd
(verified ls-remote post-push; FAST-FORWARD b2539b3..36bf92d — 7 commits:
D9 records, t385+t385b boot state machine, t386 title art, t387 menu wiring,
t388 campaign screen, t388b sound fidelity; 49 files +4690/-195). Export
/tmp/pubpush-t389 verified vendor-free (6298 objects, 5.6M .git, uniform
noreply identity), builds WITHOUT data 0 warnings incl. ascend_ui, run_tests
293 tests / 196 skipped / 0 failed, gate --portable exit 0. SEED REGRESSION
PASS: baseline worktree @ c7a3fda (pre-phase-10) vs HEAD, --headless
--campaign 1600 seeds 1/2024/23 byte-IDENTICAL (Extinct t266 / Extinct t285 /
Control t1406 == t365 record). Full witness docs/re/packaging.md t389 block
(incl. the export-origin-points-at-local-SRC trap: set-url BEFORE fetch).

WHAT THE USER CAN GRADE (the only closers left need a human witness):
(1) TITLE ART: run --ui, compare the title screen against the vendor game —
    t390 LANDED the blit (0opening.gif 1:1 + palette swap, docs/re/title-art.md
    §8); our current render is screenshotted at work/r1/loop/
    t390-artzone-witness.png — a screenshot of either screen settles it.
(2) SOUND (grades OQ-027 1-based law): run --ui --audio (real device);
    listen for theme00 loop at the TITLE screen; click Play Introduction —
    intro00 should start ~1.4 s in (frame 20 x 71 ms) and switch to intro01
    near the movie end; wrong tune/loop order => TUNEID base is 0-based.
    --audio-trace prints `music N <name>` lines headless for the wiring half.
(3) MENU SHAPE: seven items per D9 (Play Introduction / Tutorial / New Game /
    Return to Current Game / Load Game / Save Game / Exit to DOS), Alt-L /
    Alt-S hotkeys — any vendor-screenshot diff is a ruling.
LEDGER: 17 closed / 3 OPEN (OQ-016, OQ-019 deferred per user — do NOT re-ask,
do NOT apply the t329 S4 draft; OQ-027 opened t388b, closes on user hearing or
pointer-law capture of the heap tune table). t389 closed NO row (strict-close:
verify+push moves no measurement).

t390 TITLE ART BLIT — LANDED 2026-11-14 (see LANDED block above +
title-art.md §8). (1) GIF decoder LANDED bit-exact; (2) TSV palette LANDED;
(3) blit + key-255 skip LANDED; (4) "0opening.shp strips + text" — the
STRIPS HALF REFUTED by measurement (§8.3): fill + VendorText is what the
vendor shot shows; strip role residue §6.6. USER GRADING STILL OPEN on the
LOOK (see item (1) below).
MECHANICAL WITNESS (PIL scan of our own Xvfb screenshot — our own render,
self-graded VISION stays banned, geometry/mass counting is mechanical):
art zone rows 0-195 mass = 0 non-bg pixels; menu zone 195-475 mass 1006.
Buttons + caption band draw; the ART does not exist in the code path.
t386 CLOSED the identity (docs/re/title-art.md §7 checklist is this row's
spec) but no row implemented the blit. Implement per §7: (1) C++ GIF
index-plane decoder in rewrite/src/formats/gif.{h,cpp} — GIF87a, ONE
frame 640x480, GCT 256 (the file's own shape, cite title-art.md §
table); LZW-min-code decode, interlace NOT expected (verify the
descriptor, refuse-not-clamp if interlaced); NO new dependencies (no
SDL2_image, no stb — athens builds without them, deps are a publish
surface); (2) colour via rewrite/tests/data/title_palette_t386.tsv
(index-preserving swap, the t386 map f(gif_index)=vendor rgb); (3) blit
at (0,0), SKIP index 255 (key-hole -> the shp/text on top shows through);
(4) then 0opening.shp state-0 strips + VendorText labels at the SEVEN
windows.txt rects (already law in t385). Wordmark + creature come FREE
from the GIF — do NOT add shp/text art for them (§7). Pins: decoder
against the REAL 0opening.gif (first-N index-plane hash + full-frame
row-0 hash vs a Python-decoded reference generated IN the test or
banked as a data artifact), key-255 skip count, palette-map round-trip,
headless-safe (no display -> decode still testable, render path skipped).
Verification beyond pins: registration conflict-count at shift 0 between
our decoded plane and our own Xvfb screenshot (§7 law) + bank the
screenshot path for the USER to grade the LOOK (user is the external
grader).

t391 PRESENTATION SWEEP (user: look/play/sound like the original). With
the title art landed, audit the OTHER screens for the same class of gap
— chrome drawn as vector OUTLINES where the vendor has ART: (a) campaign
STATUSWND (ui.cpp:244 blits 10status k0 — confirm it is the full backdrop
per the t388 FULL-BACKDROP test comment, not a strip; if k0 is not a
backdrop, cite the right record/frame, do NOT invent); (b) NEWGAMEWND /
LOAD screens (t387 draws frames + wheel faces — check windows.txt
SHAPEITEM/SHAPEFRAME for a backdrop record the vendor paints that we
skip); (c) any TYPE-18 window frame that should carry art. Deliverable:
each screen is art-backed-or-honestly-vector (cite the windows.txt record
that decides it, or bank it as a named seam with the reason). NO engine
touches. Same screenshot-per-screen + user-grading handoff as t390.

t392 TITLE TEXT FIX (D10 user grade: "text is a tad too high in the
boxes" + "Alt-L/Alt-S/Alt-X second lines are missing on the last three
buttons"). (a) Vertical: title.cpp draws labels at rect.y0+4 — measure
the vendor baseline from scratchpad/newgame-original.png context OR the
refcap title pin (band-centre law refcap.md §1: buttons centred in 30px
rects; centre = y0 + (30 - fontH)/2, NOT +4). (b) Second lines: vendor
shot shows "Load Game Alt-L" / "Save Game Alt-S" (vision read 2026-11-14,
user testimony adds Alt-X on Exit to DOS — user is authoritative). Draw
the hotkey hint as a second line (smaller font slot if cited, else same
VendorText at +fontH+2) on Load/Save/Exit ONLY. TEXTITEM caret law: the
'^' in "Load^Game" marks the hotkey LETTER (underline if the vendor
underlines — check the pin, do NOT invent). Pins: baseline geometry
table, second-line presence test, hotkey map Alt-L/Alt-S/Alt-X.

t393 NEW GAME SCREEN REBUILD (D10: "garbled and unusable"). USER-
SUPPLIED original (scratchpad/newgame-original.png, external vision read
2026-11-14 — ALLOWED evidence): full-screen layout, NOT an overlay:
LEFT/centre = live starfield PREVIEW of the generated map; RIGHT =
"Player Species" scroll list with portrait thumbnails + up/down arrows;
CENTRE = selected-species detail (large circular portrait, planet icon,
species symbol, green lore text verbatim per race e.g. "The Minions are
a mysterious group..."); TOP = species name in green; BOTTOM = config
bar: Star Density / Species / Atmosphere / Player Color panels + map
thumbnail + "Begin New Game"; summary strings "Average Star Cluster",
"Five Species", "Neutral Atmosphere". OUR rewrite shot: translucent grey
panels floating top-right, bottom row CLIPPED below screen edge, labels
cut off left — coordinate-space + backdrop bugs. Fix: (1) NEWGAMEWND is
a full SCREEN SWITCH (title chrome must NOT show through — t388 screen
law applies); (2) bank the real rects from windows.txt NEWGAMEWND
section (L575+, controls L598+) into a layout table, verify each rect
FITS 640x480 (the clipping says ours don't — find the coordinate-space
error, do not offset-by-eye); (3) backdrop: t391 said no 18*.shp — the
original shows the STARFIELD behind, so backdrop = map preview render
(reuse the map draw), panels opaque; (4) species rows: 7racesel strips
seam from t391 stays a seam IF witness still weak — draw placeholder
portraits, say so; lore text from history.txt/help.txt verbatim per race
(supply-your-own data, NEVER embed); (5) config bar widgets = wheel
faces (3cfgnew) at cited SHAPEITEM records; setting values can stay a
named seam but the WIDGETS must sit right; (6) "Begin New Game" wires
to the existing campaign-start (mapgen seed law already shipped). Pins:
layout table vs windows.txt (every rect cited), fit-in-640x480 assert,
screen-law (title chrome absent), opaque-panel test. Screenshots per
state -> work/r1/loop/t393-*.png for USER grading.

t394 GALAXY MAP + RAIL BUTTONS (D10: "galaxy map still wonky... all the
buttons off the galaxy map are wonky too"). USER-SUPPLIED original
(scratchpad/galaxymap-original.png, external vision read 2026-11-14):
map framed left (bevel chrome, stars as pixel dots, lanes as thin vector
lines, colony icon with sprite inside); RIGHT column top-to-bottom: FIVE
green oval resource counters, TWO wide blue nav buttons w/ arrows +
circular icons, category list (Planets/Ships/Research/Special Ability/
Species each with sprite art right), 3x3 grid of circular command
buttons, bottom row SIX small coloured squares (green yellow purple red
grey blue). OUR rewrite shot: no chrome at all, text string-dump
("turn 0 player stars 1 score"), flat stacked rectangles. Diagnose FIRST
why t391's 10status/1starmap blits do NOT appear in the user's shot
(user ran latest main = 5373c66): plausible causes — blit gated behind a
state the user's path didn't reach, lib load failure degrading silently
(print it), or the 512x384 window scale (why is the rewrite window
512x384 when kDisplayW is 640?? CHECK SDL scale/integer-scaling law —
vendor is 640x480 logical; a half-scale window explains "everything
small/wonky"). Then per-element: ovals = resource counters (cite the
windows.txt STATUSWND children + the shp records), nav buttons, 3x3
grid, six squares — EACH cited to windows.txt + a 1starmap/10status
record, or banked as named seam. Status line: vendor has NO string dump
— stats live in the ovals; remove/replace ours per citation. Pins:
window-size law assert (640x480 logical), blit-present mass test per
screen state, every button rect cited. Screenshots -> t394-*.png.

t395 SOUND AUDIBILITY (D10: "not hearing any sound... on Athens").
LOCAL FACTS (2026-11-14): fresh --ui boot lands on Title and NOTHING
calls playTune until after Intro (title.cpp:279 is the only Title-side
call) — a fresh launch is SILENT BY CODE even with working audio; click
SFX only wired for campaign-map click08 (ui.cpp:213), title buttons
play nothing. FIX: (1) title-entry plays theme00 (audio.md §3.3 law:
DAT_00010ba0==0 in every banked save = menu selector tune 0) — call
playTune(0) on ENTERING Title state, not just intro-exit; (2) button
click SFX via the windows.txt SOUNDCHANNEL field law (119 instances —
census the seven title buttons' SOUNDCHANNEL values + the FUN that
maps channel->soundfx id, cite or seam); (3) ATHENS DIAGNOSTIC: startup
ALREADY prints "audio: <err> (degraded: silent)" on init failure —
make it unmissable (print device + tune loaded count + sfx loaded count
on SUCCESS too, one line); user report of that line decides device
failure vs code gap. (4) verify theme*.raw load path vs --data layout
variants (audio looks in dataDir/extracted/... — if the user points
--data at a dir WITHOUT extracted/ beside the cobs, sfx+music load
NOTHING while the game still boots: print which paths were tried on
failure). Pins: tune-on-title-entry state test, SOUNDCHANNEL census
table, path-tried diagnostic, silent-degrade still never aborts.

t396 PHASE-11 VERIFY + RE-EXPORT + PUSH — LANDED 2026-11-15 (see NEXT ACTION
block + packaging.md t396; force-with-lease push, remote==3be7e9af6c24; the
row's "fast-forward expected" premise FAILED because the privacy rewrite
diverged history by construction — force-with-lease pinned to the FETCHED tip
is the correct shape, skill publish-sanitized-repo).

t398 PALETTE FIDELITY (D11 root cause for MOST "greyscale/wrong art"
reports). t391 banked the seam: chrome COLOUR = luminance-ramp palette.
User now confirms: rail icons, bottom-right cluster, hide/show box art,
New Game bottom-row art ALL read greyscale/wrong. Extract the REAL
palettes: per-shp-file palette law (SHP header? shared .pal? palette
records inside the lib? — inspect 1starmap/10status/3cfgnew/7racesel
byte-shape + cross-check against the user-supplied originals in
scratchpad/ via colour-histogram of matching regions (user-supplied =
allowed evidence). The t386 title-palette method (measured swap table)
generalises: build per-lib palette tables, pin first-N colours, replace
the ramp in blitShape's colour-uplift path. Deliverable: named-colour
screenshots per screen + t398-palette.md; every lib either tabled or
honestly-seamed with the missing witness named.

t399 GALAXY MAP 3D FIELD (D11: "should be a 3d field of colored points
that can be rotated and zoomed by the controls near the lower right...
number of points is wrong... at the beginning only lanes off your home
system show... can't find the home star"). Our RE ALREADY HOLDS THE
PIECES: per-star x/y/z (starstat law — census the z field; ships.md/
pership-spec.md carry the z-projection law from captures: Ilmarinen
lane-witness z -2144 etc). Implement: (1) render ALL stars as coloured
points (count = galaxy star count, pin it); (2) camera = rotation
(pitch/yaw from the spin cluster SENDPARAMs) + zoom, projected per the
cited vendor law (cite the FUN that projects, or bank the capture-derived
affine + its witnesses); (3) LANE VISIBILITY LAW at game start: only
lanes touching systems the player can see (home system at turn 1 =
lanes from home); expansion law when sensors widen view — cite SA_KnowStarLanes
already in test_campaign; (4) home star visually distinct (measured from
original: brighter/ringed — verify against scratchpad original); (5) day
counter = LARGE GREEN NUMBERS (vendor LED style; the circles-with-small-
numbers is wrong — check smfont/bigfont slots for the digit face, else
named seam). Pins: star count, projection determinism (fixed camera
fixture), lane visibility set at turn 1 == home-system law, no-engine-RNG
rule holds.

t400 RAIL + CLUSTER + HOVER LAW (D11: rail art greyscale/wrong-side/
wrong-size, species-button icons missing entirely, bottom-right cluster
bg art + small icons missing; TITLE: "original highlights the button
when you mouse over it, rewrite doesn't"). After t398 palettes: re-verify
each rail icon lib/frame/position vs windows.txt SHAPEITEM + the original
screenshot geometry (icons on the RIGHT of labels per original vision
read; species row = TWO portraits); bottom-right hide/show box: bg art
record + per-button small icons cited; HOVER: census SOUNDCHANNEL/
MOUSEFOCUS/SHAPEFRAME hover-state law in windows.txt (frame swap on
focus?) — implement highlight for title + rail buttons; if vendor hover
state has no data law, bank seam with what would decide it.

t401 NEW GAME FRAMING + PANELS — LANDED 2026-11-15 (see LANDED block
above; law docs/re/t401-newgame-art.md; D11 grade user-pending).
[original brief kept for the record:] (D11: usable now, but: UI framing
missing, bottom-row artwork wrong, Player Species column art not
rendered, Begin New Game box empty except text, species description box
transparent/galaxy visible behind). (1) framing: bevel chrome — census
which shp paints NEWGAMEWND frame (t393 said no 18*.shp; the ORIGINAL
shows bevels — maybe drawn from a generic frame lib or 3cfgnew frames:
find the record, cite it, else bank honest-vector-with-citation); (2)
7racesel species-row strips: t391 seam (8x158x30, SHAPEFRAME -1) — the
user shot now SHOWS portraits in the list = they DO blit; re-derive the
frame mapping using the user-supplied original as geometry evidence;
(3) description panel OPAQUE + populated (lore verbatim from history.txt
per race — supply-your-own data law holds); (4) Begin box art per cited
record; (5) bottom-row wheel art via t398 palettes. Screenshots per
state -> t401-*.png.

t402 PLANETS LIST SCREEN (D11: "the planets list screen is wrong and
unusable"). First pass at the PLANETALLOC/planet-window law we already
banked (docs/re/planetalloc*.md, planetwin.{h,cpp}): render the real
list screen — columns, per-planet name/atmosphere/pop/manufacturing from
the campaign model, chrome per windows.txt (17np lib, state 17), click
to select. Content law citations over pixel-perfection; screenshots ->
t402-*.png for user grading.

t403 PHASE-12 VERIFY + RE-EXPORT + PUSH — LANDED 2026-11-15 (see LANDED
block + packaging.md t403; data-optional regression caught+fixed cda9cb1;
remote == 06da9b2fa8a4; D12 sheet live :8613). Original brief: Full
gate + run_tests + headless seed regression byte-identical; export;
verify vendor-free/build-without-data/identity; fetch FIRST; push;
ls-remote verify; rewrite NEXT to WAIT-USER-RULING t374 verbatim with
D11-item-by-item grading handoff. AUDIO NOTE: user tentative-OK ("music
plays, heard a click") — OQ-027 stays OPEN until the final "more
playable" verdict per the row's own bar.

t414 NEW GAME ROUND 3 (user D15, verbatim): (a) DECORATIVE FRAMING
still wrong/mostly missing — the bevel law: find the record that paints
window frames in the vendor (generic frame lib? 3cfgnew edge records?
census which shp file's records match the original's bevel pixels —
user originals in scratchpad/ are allowed geometry evidence); (b) UPPER
LEFT = SPINNING STARFIELD preview scaled to Star Density (vendor shows a
live rotating preview; ours missing — implement: rotating 3D point
preview reusing the t411 camera, point count == density setting, in the
preview rect per windows.txt); (c) icons under Star Density/Species/
Atmosphere REPEAT — wheel frame mapping wrong: k0..kN per value step
must be DISTINCT records (census 3cfgnew record count vs value range);
(d) Player Color box: player icons MISSING (raceflag/square color
records — cite); (e) right-hand race images are 4x SIZE — blit scale
law: our shp decoder or blitShape scaling frames with 4-byte headers?
compare record dims vs drawn dims mechanically (PIL), fix the divisor;
(f) race info frame missing the PLANET image (home-world planet art
record — planet*.shp? cite). Self-grade law: walk newgame, grade, fix,
re-walk.

t415 RACE INTRO FRAMING + ART (user D15: text present now — good — but
needs decorative framing + race image). Same frame law as t414(a); race
portrait = race*.dip or the 7racesel big frames (t412 banked
FUN_0002b48a + history.txt law — check what that FUN blits alongside
the text; the vendor intro screen shows the species portrait large).
Cite the record the vendor uses; seam only if genuinely undecidable.

t416 ROTATION AXIS WIRING (user D15: upper-left rotation control should
rotate about Z [in-plane spin] but ours rotates about Y [tumble]). The
8-dial cluster: t400/t411 banked SENDPARAMs; map each dial to its axis
per the SENDPARAM value + vendor behavior (spin = screen-plane rotation
= our yaw-vs-roll naming; verify by rotating a KNOWN star: pick a star,
click dial, assert its screen-space path is circular-about-center (Z)
not vertical-arc (Y) — PIL mechanical witness on two shots). Fix the
dial->axis table; pin per-dial behavior.

t417 PLANETS LIST BACKGROUND (user D15: background = one of the images
we determined was NOT used anywhere — wrong lib). Re-derive: which
record is the status-list backdrop per windows.txt SHAPEITEM/SHAPEFRAME
for the status window; the "unused" finding (D1 ruling: A-series
historical curiosity) says we picked a dead asset. Fix to the cited
record; if the vendor backdrop is actually the starfield + frame chrome
(t393 law), do that instead — cite which.

t418 PLANET VIEW: THE PLANET ITSELF + TILE GRID (user D15: planet
display present but renders NO planet; should be a PICTURE of the planet
overlaid with colored squares in ISOMETRIC view, selectable, adjacent-to-
structure -> build order). Data law already RE'd (planetalloc docs:
tile grid, terrain colors, structure placement, adjacency for build
placement): render the planet disc (planet art record per atmosphere/
size class — cite; race0X-style libs? planet*.shp?) + isometric tile
overlay (colored squares per terrain per the palette law), click tile =
select, adjacent-to-existing-structure -> project/build-order UI (reuse
t406 project-set seam; the ADJACENCY rule is in the planetalloc docs —
cite the FUN). Self-grade: planet visible + tiles clickable + build
order lands in PLANETALLOC state.

t419 RESEARCH SCREEN: CPU STALL FIX + 3D TREE REBUILD + CORNER EXIT
(corner popup built campaign-wide — user confirmed 2026-11-17 this matches the vendor: the original has no title-screen popup)
(user D15 addendum: screen pegs one core at 100%, input + window close
queue behind it and drain MINUTES later — console spurt like 'ui
research readout Orbital Structures'; last round's 'Esc trap' is the
SAME bug, reclassified). ROOT CAUSE STATIC-CITED (DECISIONS.md D15
addendum): researchview.cpp:99 researchDepth() clears its memo EVERY
call and re-walks the whole prereq graph; researchNodePos calls it once
per slot row (O(n) each) => the painter (ui.cpp:1444-1466) recomputes
every node position O(n^2 x graph) PER FRAME at ~60fps, and researchHit
repeats it per click. FIX: compute the depth table ONCE per tree (build
on load / cache keyed by tree pointer+count), node positions once per
(pan, rotation) change not per frame; add a frame-budget pin (research
paint of the full 66-row tree < 5 ms — measure inside the test with
steady_clock, generous bound, it just has to prove the O(n^2/frame)
class is gone). THEN the user spec: research screen = 3D ROTATING tree
("another 3d rotating dealie") + info frame RIGHT + controls lower
right: ROTATION about Z + SCROLL up/down. Derive the rendering from RE
(user instruction): the vendor reswin draws the tech disks on a 3D
spinning structure — Ghidra the reswin draw chain (start from the
RESWIN window handler family / research.md's cited FUNs; find the
projection: disk positions rotated by a global angle, depth -> size/
brightness?), cite the FUN + the angle accumulator; reuse the t411
camera + the t416 dial->axis law (upper-left rot controls = Z). The
four pan-button rects already cited become the vendor's rotate/scroll
controls per the table (census which SENDPARAM does what). Info frame
right = the readout panel (name/cost/progress — data law already in
researchview.h). Self-grade: walk research, watch CPU (pgrep + ps -o
pcpu — must NOT peg), rotate/scroll respond, Esc instant, click disk
sets study; screenshots t419-*.png. (b) CORNER EXIT POPUP stays:
census shp libs for the Exit<ESC> art (user recalls an image found in a
previous round — grep prior docs) + windows.txt corner sections; mouse
in corner rect -> popup renders; Esc returns.

t420 PHASE-15 VERIFY + PUSH + HANDOFF (push-gap law MANDATORY). Full
gate + run_tests + seed regression byte-identical; export; fetch FIRST;
push; ls-verify (NOTE banked: public SHAs NEVER exist locally — the
export is history-rewritten; "c178a43 not a valid object" locally is
NORMAL, not a push gap); rewrite NEXT to WAIT-USER-RULING t374 verbatim
+ D16 sheet (:8613, per-screen before/after from OUR native-vision
grades + the live re-check list); comparison screenshots from user
welcome, not blocking.

SELF-GRADE LAW (D13, applies to EVERY row in phase 14): R13 is LIFTED by
owner order for OUR OWN UI screens. Harness fact banked: vision_analyze
routes NATIVE (image lands in your own context) only when
agent.image_input_mode=native AND model.supports_vision=true — set on
this box 2026-11-15 via `hermes config set model.supports_vision true`
(before that every call silently went to the external aux model; the
user caught it). Walkthrough kit: scripts/r1_ui_walk.sh STATE [click X
Y|key K]... -> work/r1/loop/walk/STATE.png (xsend takes WINDOW coords,
now focuses first; kill via pkill -x ascendancy, NEVER -f = self-kill).
Per row: walk the screen, grade it with your OWN eyes, fix, re-walk,
re-grade; a row may NOT close while your own grade still lists a defect
the evidence can fix; honest seams only where the DATA law is missing
(name the witness that would close it).

t404 LASER-SOUND REGRESSION + INPUT HYGIENE (user D13: "clicking
anywhere in the galaxy map makes a laser-fire sound"). ROOT CAUSE
LOCALISED: ui.cpp:348 — ANY click inside the COSMOSWnd rect plays
audio->play("laser01") (early placeholder). Fix: laser01 only on a real
fire-order interaction (or removed until combat UI exists — cite the
soundfx/help law for what laser01 IS); map clicks follow windows.txt
SOUNDCHANNEL (census map children); dead areas play NOTHING. Sweep all
placeholder sounds (grep play( sites, cite each or remove). Pins:
click-empty-map silent / rail click click08 / no laser without fire.
LANDED t404 — see the LANDED block above; laser01 plays NOWHERE until a
cited fire-order interaction exists.

t405 SUB-SCREEN NAVIGATION + RAIL LIVENESS (I WITNESSED D13: Planets
opens Empire status, then Ships/Research/Species clicks route into the
status screen's scroll/select — ui.cpp:342-348 deliberately makes the
rail inert while a screen is open; vendor law: rail stays live, screens
SWAP; 'Esc: return to galaxy' is printed bottom-left). Implement per the
windows.txt STATE id-lists (t388 banked 123/123 law — cite which list
keeps the rail live during sub-screens): rail rects evaluated before
sub-screen children; Esc returns to map from ANY sub-screen. Pins:
Ships-from-Planets swaps screens; Esc from every sub-screen -> map;
scroll still lives inside its own rects.
LANDED t405 — PREMISE REFUTED, DEFECT FIXED. No STATE list keeps the
rail live (rail buttons are "1 1" ONLY; the 10status k0 backdrop paints
OVER the rail column, native-vision-graded): screens swap, rail hidden,
Esc back — already the shipped law, now pinned (statusnav_*_t405 x4).
The witnessed fall-through was the hit-map: old 566-wide arrow rects +
unbounded row test swallowed rail-position clicks. Unified statusHitFor
(arrows at MEASURED art rects 619..638, trough inert, rows x 7..618),
row paint stops at 618. Witness t405_statusnav_witness.sh PASS; suite
356/0; law docs/re/_wip_t405.md F1-F10.

t406 PLANETS: OWNED-ONLY + PLANET VIEW (user: "displays planets I don't
own, can't click a planet"; I WITNESSED: Empire status lists the 3
Highbeam planets + logs 'ui status select Highbeam (planet detail =
state-17 seam)' — selection exists, planet view does NOT). (a) statuslist
filter to OWNER == player (0x50647 law banked _wip_t402; find the owner
predicate — ours absent/wrong); (b) BUILD the planet view (state 17,
17np lib, windows.txt PLANET* sections; planetalloc docs bank the data
law): name, atmosphere, size, population+growth, manufacturing, and the
PROJECT slot with project-SET interaction (user: "can't set a project on
my home planet" — project list law in planetalloc/income docs), terrain/
keywords, surface art record; row click opens it. Pins: owned-only count
== campaign model; project-set mutates PLANETALLOC state; row->detail
routing.
AFTERCARE (t405 native grade): row 0's PORT frame clips the backdrop's
"name" header cell to "na" at the left edge (pre-existing t402; the
header cells are ART at y~48..82 — either anchor rows below y 94 or
clip row painting to the table interior). The vendor row content
(system circle + cyan system name + planet icon + gauges RIGHT, t3
capture F7) is richer than our current row — grade vs
work/screens/t3/planets_header_t1086_after_open.png.

t407 SHIPS SCREEN (user: "ships screen is empty"; I WITNESSED: click
dead, no fleet window). Build the fleet list from the per-ship model
(shipsave+shipsim hold the data): row per owned ship — name (word 26
law), design, system/position, fuel/damage; click row = select;
right-click deselect (selfplay.md) lands here; chrome: t391 proved NO
18*.shp exists -> honestly-vector WITH citation. Map interplay may stay
a named seam; the LIST renders real campaign ships.

t408 RESEARCH SCREEN (user: "research is empty"; I WITNESSED: dead).
LANDED t408 — see the LANDED block; law docs/re/_wip_t408.md. [original
brief:] Build per banked RE: tech tree, current project + progress,
click-to-SET research; pins incl. set-research resolves at turn end.

t409 SPECIAL ABILITY + SPECIES SCREEN (user: "special ability button
doesn't even do anything" + "species screen quite off"). Census
windows.txt for a special-ability window: if NONE exists in vendor data,
say so with the table citation and disposition the rail label per its
SENDPARAM/help index (do NOT invent a screen). Species screen: every
species + portrait (7racesel after t398 palettes) + ability text
(help.txt verbatim) + relation standing from the campaign model.

t410 SYSTEM VIEW + MAP->PLANET CHAIN (user: "haven't found any way to
pull up the system view screen, or planet view screen"). System view law
lives in the playtest/selfplay docs (system view = planets-in-orbit
layout + ships present; Escape unwinds — the t1253 turn-drive era walked
it live). Wire: click (or double-click — cite which from the vendor
table/law) a STAR on the map -> system view; click a PLANET dot there ->
t406 planet view; Escape chain depth pinned. This is ALSO the route the
user has been missing.

t411 MAP LOOK PASS 2 (my own native-vision grade of
work/r1/loop/walk/map_view.png, 2026-11-15): structure right, LOOK
wrong: (1) no bevel frame around the map area (find the record:
1starmap frames or generic frame lib; cite or honest-seam); (2) resource
ovals EMPTY — vendor shows big green LED day digits (t399 claimed digits
landed; my shot shows empty ovals: re-derive which record/slot paints
them + does the counter bind campaign day); (3) rail panel reads noisy
grey (t398 palette partial — re-check vs game.pal); (4) star field FLAT
2D — camera rotation/zoom law (if the projection witness is genuinely
missing, derive the affine from captures + bank witnesses, else seam);
(5) lane visibility: at game start ONLY home-system lanes (user D11
law); (6) home star visually findable. Bottom-right 8-dial cluster:
witness EACH dial via xsend, log current behavior, wire per SENDPARAM
law (user: controls "don't work quite right"). Pins per item.

t412 NEW GAME FIXES + RACE INTRO (user: "new game screen still off" +
"race introduction screen that appears after the new game screen and
before the galaxy map display is MISSING"). My grade: frames present,
species-row squares EMPTY (no portraits — after t398 palettes re-derive
the 7racesel 8x158x30 mapping; the user's original DOES show portraits),
bottom-row wheels small/greyish. RACE INTRO: vendor plays a race
sequence after Begin — content law = history.txt per-race opening text
(verbatim, supply-your-own data); art = race*.dip or movie (census,
cite; minimum ship the text panel + click-to-continue, name the art
seam). Begin robustness: my witness logged 'raceconfig begin density 50
species 7 atmosphere 1' but the campaign never appeared in that session
— distinguish SLOW mapgen (this box) vs DEAD: log line before/after
generation, and verify fresh-process Begin lands
intro->map. USER WITNESS 2026-11-15: Begin -> map takes ~3 s on this
box = generation time (intro absent, so nothing masks it). SEQUENCE the
vendor flow: Begin -> race intro (text scroll takes seconds naturally)
-> map; if gen still shows, pre-generate behind the intro panel. The
delay is NOT the missing intro causing work — it's mapgen exposed
because the intro screen that should sit between them doesn't exist.

t413 PHASE-14 VERIFY + PUSH + HANDOFF (push-gap law MANDATORY). Full
gate + run_tests + seed regression byte-identical; export; fetch FIRST;
push; ls-remote verify; rewrite NEXT to WAIT-USER-RULING t374 verbatim
with a WALKTHROUGH TABLE: per screen, own-grade before/after + what the
user should re-check live. Rebuild the :8613 sheet to the D14 asks
(scripts/t403_grading_page.py pattern; t397b server hardening stays).

DISPOSITIONED t403-prep (D11b USER: drop, 2026-11-15): no support email
will be sent; old-object GC exposure (manual pages + the one ISP-email
blob at old tip 5373c66) is ACCEPTED risk by the user. Current remote
history verified clean (fail-closed gates in publish_public.sh).
REMOVED ITEM: GitHub backend GC may still serve old commit SHAs (Removal mechanics landed: docs/assets fully filtered,
fail-closed gate + .gitignore, local copies untracked.)

PHASE-17 QUEUE (authored ON USER RULING D19 2026-11-20 — DECISIONS.md).
PIPELINE: Stage A = global draw laws ONCE (blit scale, chrome, text);
then per screen in FLOW ORDER two gates (C=content, B=behavior);
framing per screen is an A2 APPLICATION CHECK inside each C-gate, not
a separate pass. Polish backlog items NEVER block a gate. First screen
(New Game) ends with a USER-GRADE PARK; later screens batch-park.

PHASE-17 GRADE LAWS (binding every row; supersedes phase-16 self-grade
practice; root cause of six rounds of 'minor improvements': element
laws closed against the session's own expectations, composite never
graded):
 G1 SIDE-BY-SIDE, NOT MEMORY: every vision grade loads OUR render AND
   the vendor refcap crop for the same region in one pass; the defect
   list is written against the ORIGINAL pixels. A grade citing only
   the law doc is void.
 G2 MECHANICAL FIRST: per named region, palette-class histogram diff +
   drawn-dims-vs-cited-dims assertion + art-presence mass, via a shared
   harness scripts/t441_screen_diff.py (BUILD it in tA1; every later
   row extends its region table, never re-homes it). Mechanical FAIL
   = gate FAIL regardless of how the render looks.
 G3 BEHAVIOR GATES ARE SCRIPTED: clicks/wheels/spin/filters asserted
   via log lines + state reads (xsend + app log), never screenshots.
   Rotation-axis-class bugs live here.
 G4 USER-TESTIMONY MECHANIZATION: D19 correction list is the seed
   defect list for the matching gates; close each by measurement,
   pin by test.
 G5 HONEST MEASUREMENT SOURCES: Athens screenshots are 512x384 scaled
   = layout/color evidence ONLY; pixel-scale numbers come from refcap
   captures or Xvfb :9 640x480 root grabs, never from Athens shots.
 G6 ONE FIX PER ROOT CAUSE: when two screens show the same signature
   (e.g. quadrant-blit), fix the LAW, then verify BOTH screens in the
   same row; per-screen patches of a shared bug are rejected.

tA1 BLIT-SCALE LAW [CLOSED tA1-CONT 2026-11-21 — see the tA1-CONT
LANDED block + _wip_tA1 F6; the harness/ladder/dimscheck contract there is what
every later C-gate row reuses] (STAGE A, FIRST; user D19: portrait/species column/
planet art/planets-list art = 'top left quadrant of a 4x-size render'
clipped to circle = ONE bug family). Derive the vendor destination-size
law per call site class: FUN_0005d5a1 is an affine STRETCH blit (t422c
cited: 16.16 interpolation, 16 vertex sets 0x8408..0x8457) — find WHO
supplies dest dims for each UI record class (portrait circles, planet
discs, list icons, wheel frames): decompile 2-3 representative paint
bodies (newgame portrait painter, planet painter, PLANLIST row painter
0x500e0 t427) and read the dims source (record header? fixed const?
scale word?). THEN: port blitShape call sites to the cited law (per
class), add drawn-dims pin tests per class, build
scripts/t441_screen_diff.py (region table: name, rect, expected palette
classes, dims assertion; diff report per region; exit code = gate).
CLOSE: quadrant signature GONE on newgame (portrait, species column,
planet disc) AND planets-list sun+planet render at cited dims; diff
harness on those two screens exits clean on dims+presence (content
index errors may remain — tNG-C/tPL-C own those).

tA2 CHROME LAW ROUND 2 (STAGE A — CLOSED tA2-CONT 2026-11-21: law landed,
witness within +-6, harness bands, mutation 12/12; named lag-1 mineral
ceiling stays in chrome.md 4; queue verbatim below) (user D19: texture = MINERAL (stone/
galvanized), not static; our top bar CLOSE but 1-2px short; TWO chrome
layers — almost-right bar laid ON TOP of the older rougher frame).
ASSISTANT PRE-PROBE 2026-11-21 (user: planet screen frame PIXEL-PERFECT
— 'whatever you did there, do it everywhere'; scratchpad/athens-
comparison-t439-v-original.png): the planet frame is pixel-perfect
because it BLITS 17np.shp k0 (ui.cpp:1613) — the method = find the
vendor record, never synthesize. CENSUS (165 libs, scripts/
tA1_chrome_backdrop_probe.py): full-screen 639x479 records exist ONLY
in 10status/17np/2savegam/4loadgam; the two decoded ones share only
20.2% of overlapping opaque px = per-screen ART, not one global frame.
=> PRIMARY ROUTE for tA2: hunt the chrome ART for record-less screens
(map/newgame/species/research): candidates (a) per-window SHAPEFRAME
widget-lib records the winmgr tiles (cross-check windows.txt SHAPEFRAME
values x 1starmap/3cfgnew/7racesel record dims), (b) winmgr backdrop
paint FUN (debugger RUNWATCH on the band region, scratch game —
blanket grant). PITFALLS banked: pinned refcap = direct 640x480 (NO
+40 offset — that's scratchpad-only; my first probe mis-aligned on
this and got a phantom 0%); xcorr scripts on disk =
scripts/tA1_chrome_{backdrop_probe,xcorr}.py (fix alignment, re-run
before ANY new chrome synthesis is considered; t422c no-rand-in-paint
+ t433 zero-capture now READ AS 'art not yet found', not 'generated').
(a) FIND + REMOVE the double paint: grep the paint path for both the
t426 gradient band AND the legacy splitmix/static call sites; one
chrome renderer, one pass (G6). (b) bar width: measure the vendor top
bar extent from refcap at 1:1 (G5), fix the 1-2px. (c) mineral
character: correlation-length census of vendor vs ours (run-length
2-D, lag-1/2 h+v per band from _wip_t422 data + chrome.md); tune the
Markov parameters toward the mineral signature; if the census says our
parameters cannot reach it, bank the measured gap as the named ceiling
(D18 ruling stands: honest seam, not new guessing). (d) BEVEL DIRECTION
law: original panels are RAISED (light top/left, dark bottom/right) —
derive from refcap edge pixels, cite, implement one drawBevel used by
all frames. CLOSE: single-layer verified (paint-order log or debugger
breakpoint at both sites), dims match, bevel cited + applied on
newgame + map + title, diff harness chrome-band regions pass.

tA3 TEXT LAW (STAGE A): font identity + cell size + baseline + color
classes measured from refcaps ONLY (G5): the vendor .fnt law is banked
(docs/re font notes); render a reference string table at 1:1 and diff
glyph metrics vs refcap text rows (height, advance, weight). Fix the
port's text draw to cited metrics. CLOSE: metric diff within 1px on
title + newgame + map button text; pins.

tNG-C NEW GAME CONTENT GATE (gate C = every region: record index +
clip mask + palette cited; framing = A2 application check). Seed
defects (D19): portrait circle clip + green ring correct size (after
tA1); planet art INDEX law (husk shown for Minions; wrong for most
species cycled — derive the race->planet record law from the vendor
painter, cite); atmosphere wheel: frame-per-option (ghost sliver +
stray white line under peaceful/neutral = wrong frame index or double
blit; hostile is the correct reference); star-density + species boxes
extraneous art; Player Color = ONE row of SEVEN outlined race-emblem
chips (tinted), not 2 rows of solid swatches; Begin New Game panel:
starfield tied to density setting (rotating; same-field-scaled vs
shrunk-volume undetermined — derive from the vendor painter), thick
BEVELED green ring. G1+G2 close.

tNG-B NEW GAME BEHAVIOR GATE (G3): star density/species/atmosphere
wheels cycle state + art together (no drift — D19); starfield spin
AXES correct per dial (user: axis wrong; reuse t416/t425 dial law);
Begin New Game launches race intro with chosen settings; player-color
chips select. Assert via log/state.

tNG-U NEW GAME USER-GRADE PACKAGE + PARK (FIRST-SCREEN checkpoint per
D19): build side-by-side composite (ours | refcap | diff report) at
scratchpad/NG-usergrade.png + per-region table; rewrite NEXT to
WAIT-USER-GRADE-NG sentinel (human wake resumes: user reply ->
DISPOSITIONS row or straight to tSI-C per ruling).

tSI-C/tSI-B RACE INTRO gates (seeds: frame texture (A2), text size/
font (A3), background still wrong).
tGM-C/tGM-B GALAXY MAP gates (seeds: stars too big + CIRCLES not ovals
around stars; frame slightly off; button text size/font; starfield
control buttons behavior; Hanshaks species-button shows ALL player
species; bottom colored buttons ONLY for present players).
tPL-C/tPL-B PLANETS LIST gates (seeds: frame texture; 4x quadrant art
(tA1 verify); research/industry/prosperity as PICTURES not text;
population indicator circle count vs refcap; REMOVE 'Esc return to
galaxy' lower-left text; click behaviors).
tPS-C/tPS-B PLANET SCREEN gates (frame EXACT — do not touch; seeds:
top-row art, planet frame bg, disc size/z-order vs grid, tile click
window, orbital column).
tSV-C/tSV-B SYSTEM VIEW gates. tSH-C/tSH-B SHIPS gates.
tRS-C/tRS-B RESEARCH gates. tSP-C/tSP-B SPECIES + SPECIAL ABILITY
gates. t17-V FINAL VERIFY + PUSH + HANDOFF (push-gap law; handoff =
per-screen grade table, NO ruling sheet; park WAIT-USER-RULING).
Rows tSI..tSP: if a gate closes clean first try, the session MAY fold
the next gate of the SAME screen into one run (breadth preserved);
CONT cycles stay capped at 2 per D18.

PHASE-16 QUEUE (authored ON USER RULING D17 2026-11-17 — DECISIONS.md;
per-screen iteration structure, RE-FIRST LAW). Ordering: t422 first
(one shared root cause: the chrome texture appears wrong on EVERY
screen the user graded); then one row per screen in flow order; then
verify+push. A COMPLETING SESSION REWRITES NEXT TO THE NEXT ROW
VERBATIM in EXECUTION order (2026-11-20 reconciliation): done
t422,t423,t424(push),t425,t426(+C2),t427(+b),t428(+b..f),t429(audio
premise REFUTED),t424b(race intro LANDED 2026-11-20); REMAINING
t434(ships — FIRST),t435(research),t436(species+
ability),t433(chrome EXACT memory-surface),t437(OQ-027b record-field
closure),t432(final verify+push+handoff); after t432 park WAIT-USER-
RULING. NEVER reuse a consumed tag and never move a row's TEXT under
another row's executed tag — the lineage must stay greppable.

PHASE-16 DERIVE-FROM-RE LAW (binding every row; user D17 verbatim:
"Can you derive the exact UI drawing paradigms from reverse
engineering"; proof it works: the planet-screen frame landed EXACTLY
via windows.txt panel table + cited paint dispatch — "can you apply
that process to the other screens?"):
  (1) NO SYNTHETIC STAND-INS. Every pixel class the user can see
      (frame texture, ring stroke, star, icon, background) must trace
      to a shape record (lib + record idx + dims from the shp census)
      or a cited FUN address. splitmix64 hash-noise texture, hand-
      drawn vector rings, and shell-mapped star dots are BANNED
      placeholders — replacing one with derived art is progress;
      adding a new synthetic one is a gate-level regression.
  (2) DERIVE BEFORE CODING: per screen, decompile the vendor draw
      chain FIRST (GhidraMCP headless v7.0.0 CONNECTED — check via
      mcp ghidra check_connection; if down, fall back to banked
      docs/re disassembly windows, and if the window is missing that
      is an honest seam NAMED in the wip, not a licence to guess),
      read the windows.txt table for the screen's windows (rects,
      STATE, SHAPEFRAME, SENDMESSAGE/SENDPARAM), census which shape
      lib+record the draw code selects, bank law + citations in
      docs/re/_wip_tNNN.md, THEN implement.
  (3) ITERATE TO CLEAN (user D17 verbatim: "work on a screen, do a
      comparison, and work on that screen again, iterating until it's
      right"): within the session, loop walk (scripts/r1_ui_walk.sh)
      -> native-vision grade vs vendor refs (user screenshots in
      scratchpad/ where present + own captures; vendor pixels are
      always allowed) -> fix -> RE-WALK -> RE-GRADE. Mechanical
      supports: render_mass_probe.sh zone masses, dims census
      (drawn px vs record px — the 4x-scale class), md5 of painted
      planes vs vendor-decoded planes (identity without vision).
  (4) CLOSE LAW: a row closes only when its own final grade lists no
      fixable-with-available-evidence defect AND its pins pass. If
      defects remain at session end, rewrite NEXT to "<tag> CONT
      cycle N+1" with the defect list verbatim (fresh tag arms the
      wake trigger; a new session continues the cycle). Max 3 cycles
      per screen, then bank the honest seam naming the missing
      evidence.
  (5) USER-TESTIMONY PRECEDENCE: round-4 items (D17) are the seed
      defect list per screen; they do NOT cap the grade — the walk
      may find more.

t422 CHROME LAW — TEXTURED FRAME DERIVED FROM RE (ROOT-CAUSE ROW,
[CLOSED 2 CYCLES 2026-11-17: cycle 1 field law chrome.md SS1.5, cycle 2
generator route EXHAUSTED -> statistical ceiling is the close reading;
R-t422c binds. Original row text follows for history.])
runs FIRST). The synthetic hash-noise chrome (mapchrome texture-
ColourAt / splitmix64, menulaw §4, statusbg, title) reads "larger,
grainier than the original" on every screen (D17). Derive the real
law: the vendor chrome is SHAPE ART — census the shp libs (165 files
under extracted/ascend01/data/) for the frame/border families: the
t391 note "vendor lacks 18*.shp" needs RE-VERIFICATION against the
full lib list (13negot, 3cfgnew, 7racesel, 20res, 0opening, 2savegam,
4loadgam... every window's chrome must come from SOME lib; windows.txt
SHAPEFRAME fields + each window's paint FUN name the record). Ghidra:
pick a window WITH textured chrome (e.g. a TYPE-29 panel or a dialog)
and decompile its paint body — find the blit of frame tiles/records
(corner+edge+tile tiling law? whole-panel records?). Deliverable: a
CHROME LAW doc (docs/re/chrome.md): for each chrome class, lib+record
+dims+tiling, cited; a shared drawFrame() in the port using ONLY
derived records; migrate EVERY screen off the synthetic texture in
this row or name per-screen migration debt explicitly. Grade: side-
by-side of one frame vs vendor pixels at 1:1 (md5 painted vs decoded
is the identity pin). CONT cycle: remaining screens' migrations.

t423 NEW GAME SCREEN CYCLE (seed defects D17): wheel icons repeat
across steps AND hostile-atmosphere variant missing AND extra art
drawn below the circles (census 3cfgnew.shp records per option step —
the vendor TEXTITEM/SHAPEFRAME table in beginnew.txt names which
record per state); species + planet art STILL 4x (dims pin: drawn
rect == record dims /2 or as-cited — find the vendor scale law, do
not eyeball); species rings need THICK TEXTURED lines (chrome law
from t422 or the ring's own record, not a vector stroke); preview
starfield fills the VOLUME not a shell, stars LARGER + pixelated
(decompile the newgame preview draw — vendor star sprite + placement
law: volume sampling, sprite size); Begin New Game BUTTON spins the
starfield too (vendor law: spin pump while button held/hovered?
census the button's SENDMESSAGE). Framing via t422 chrome law. Grade
clean per close law.

t424b RACE INTRO SCREEN CYCLE: LANDED 2026-11-20 (background greyscale +
text unreadable root-caused: the frame interior is the DARK speckle, not
the bright chrome page — docs/re/_wip_t424b.md F1-F5; portrait truncation
bug fixed; ink byte witnessed). Original row text kept for lineage:
background greyscale + text unreadable
(root cause likely palette: the intro art needs the vendor palette
transform the gif/cine path applies — decompile the intro screen
paint, cite the palette source) + textured framing via t422 + race
portrait position/size per the draw chain (t412's FUN_0002b48a lead).
[GIF/CINE PREMISE REFUTED — R-t424b(1).]

t425 GALAXY MAP CONTROLS + LIVENESS CYCLE: (a) dial SPIN LAW — ours
rotates continuously on click, the original does NOT (D17): decompile
the 8-button control cluster handlers (1starmap control windows,
SENDPARAM law) — discrete step per click? latch-until-release? timed
burst? implement the cited law; (b) THREE of the eight lower-right
buttons DEAD — windows.txt table lists all eight with
SENDMESSAGE/SENDPARAM; route each to its cited effect, verify each
changes state (log line or frame diff); (c) player FILTER buttons
missing art (census starmap/race lib for filter glyphs — t416 banked
some filter law, reuse); (d) corner Exit popup is DRAWN BUT INERT
(D17) — click on it must EXIT per screen per the t405 stack law;
handler missing; wire + witness per screen.

t426 GALAXY MAP VISUALS CYCLE: map BORDER missing (chrome law t422 +
windows.txt COSMOS rect); PLAYER ICON UPPER LEFT (user correction
2026-11-17 verbatim: "the galaxy map is supposed to show the player
icon in the upper left, not the upper right" — census the status-bar
icon records, 10status.shp lead); HOME STAR shows player icon + TWO
rings at game start (user: smaller player-colour ring + larger white,
meanings [unverified] — derive from the draw code which condition
paints each ring; do NOT copy the guess); chrome texture per t422.

t427 PLANETS LIST SCREEN CYCLE (user D17: "hard to describe, hoping
you can just derive the drawing rules from reverse engineering"):
full derive-from-RE pass on PLANLIST (windows.txt line ~1504 rect +
paint FUN + planets.shp record selection per row: owned vs unowned
marker law, row layout, scroll window law per menulaw three-slot
precedent); grade vs scratchpad refs + vendor pixels.

t428 PLANET SCREEN CYCLE (frame ALREADY EXACT — do not touch it;
seed defects D17): top-row art missing (TYPE-29 panels PLRES/PLIND/
PLPOP/PLPOP dispatch keys 0..4 paint which records? census); planet
frame BACKGROUND missing (17np.shp already loaded — which record?);
planet art TOO SMALL + covered by the squares (z-order: vendor paints
planet THEN grid? dims per F4 law; squares overlay per-cell but the
planet must read through); SQUARES DRAWN WRONG (compare diamond law
|dx|/34+|dy|/17 hit vs vendor painted diamond dims — the FILL and
OUTLINE records/colours come from the paint FUN, cite); tile click
pops a CONTENT-DEPENDENT WINDOW (PLSQUARE child msg law + which
window per tile state — empty/owned/structure); ORBITAL STRUCTURES
column on the LEFT missing (planets-ui law).

t434 SHIPS SCREEN CYCLE (RE-TAGGED: original t429 tag was consumed by
the audio-premise row 2026-11-19, lineage law): full pass — derive the fleet list paint
(fleetlist law banked t402 era; grade it against vendor now), row art
(ship class sprites), selection/info panel, per close law.

t435 RESEARCH SCREEN CYCLE (RE-TAGGED: original t430 tag consumed by
the audio record-field row 2026-11-20): grade the t419 rebuild against the D15-
addendum spec (3D tree, right info frame, Z-rotate + scroll controls,
corner popup) + the live re-check list (spin latches per t425 law,
Esc instant, no CPU peg — ps -o pcpu assertion); fix what fails.

t436 SPECIES SCREEN + SPECIAL ABILITY CYCLE (RE-TAGGED: original
t431 collided with the loop's own D16-era numbering): species screen "quite
off" (derive its window paint chain + race art records); SPECIAL
ABILITY BUTTON DOES NOTHING (windows.txt button SENDMESSAGE -> which
handler? decompile the target; implement or bank the honest negative
IF the handler provably requires state we cannot reach — name the
witness).

t433 CHROME: EXACT LAW VIA MEMORY-SURFACE CENSUS (user D18 verbatim:
"it looks like it's still trying to guess at what things should look
like, rather than recreate exactly from the original code" — the
statistical Markov field is the named ceiling of the STATIC route per
t422c; this row attacks the remaining hypothesis class directly).
HYPOTHESIS H-CHROME-SURFACE: the mottle is NOT painted per-frame at
all — it is a PRE-GENERATED surface (built once at init, or shipped
as a data blob) that the chrome blit samples screen-fixed. Evidence
shape: t422c proved no rand() call in any paint path AND no static
colour-pattern table — a pre-baked surface fits both facts. METHOD:
run the DEBUGGER dosbox-x build (banked: --enable-debug=heavy +
mcp_server, see docs/re/debugger notes; scratch savedir law, production
stays down) to a title/menu screen, DUMP the DOS memory region(s)
behind the chrome rects (window-manager backdrop pointers from the
winmgr chain ui-runtime.md:581 neighbourhood), census each candidate
region for the t422 band statistics (run-stats match + lag-1 skew
0.62). If a region MATCHES byte-for-byte against vendor screen pixels
(the screenshot IS the ground truth): the surface + its addressing
law = exact law; implement port-side generation to reproduce the
dumped bytes (seed + algorithm cited from the init code that wrote
it). If no region matches: dump-adjacent code census for the writer
(RUNWATCH on the paint address, one-shot, banked tooling). CLOSE:
md5/pixel-exact chrome vs vendor capture at 1:1 on at least the
newgame + map frames, or honest seam naming what the dump showed.
Blanket grant 2026-11-14 covers scratch experimentation; NEVER mount
the production game dir; bank ring first if anything touches saves.)


t437 OQ-027(b) VIA THE RECORD-FIELD ROUTE (MOVED VERBATIM from NEXT
2026-11-20 so race intro runs first; the tag t430 was already consumed by
the audio-premise row): DOES windows.txt
SOUNDCHANNEL LAND AT RECORD +0x57, AND WHICH SITE COVERS STRATEGIC RAIL /
NEXTTURN PRESSES (ordering rationale: t429 refuted the +0x1bcc premise
(R-t429) and left exactly one measurable path for the only OQ row with a
user-free closure bar. t429 measured the full play-path census: 8 immediate-0
("button") sites — 0x1b0b0/0x1b1c5/0x27e46 inside rect click hit-tests,
0x47e09/0x529f9/0x52a5b/0x36632/0x549f9 modules UNIDENTIFIED — and 6 sites
reading record-HIWORD sfx id at +0x57 with -1 = silent (0x30e75 et al., records
reached through control pool 0x7a35c = the strategic pool per t428e). PLAN
(offline-first, ~no live session needed): (1) identify the windows.txt parser:
the file opens via pool-rel imm 0x2ffc ("windows.txt" @payload 0x85bac) at
0x575c2 (call 0x5b587, enclosing 0x575e4 parses; second referrer 0x750ba is the
resource-mount path) — trace where the parser stores each keyword's value; the
keyword literals are NOT plaintext in the payload (case-insensitive census
MEASURED t429), so find the keyword TABLE (likely a struct of {name-ptr,
offset} pairs) and read the SOUNDCHANNEL field offset. (2) IF that offset ==
0x57: the t395 census {0 x118, -0 x1} becomes cited law "vendor strategic
controls play manifest[0] button.voc (3,340 B), -1 records silent" -> UPGRADE
sfxForPress rail/next-turn/title click08->button + retarget pins/witness
(t404_sfx_witness.sh pattern), CLOSE (b) with the census. (3) IF offset !=
0x57 or keyword table absent: honest negative, row stays open on the hearing
bar, R-t429 stands. Do NOT re-derive FUN_000500e0/0x4fb30 (cited audio.md
S6.8); do NOT re-plan click censuses at 0x17488/0x1749b (R-t429); do NOT touch
k5/planets visuals (R-t428f).

t432 PHASE-16 VERIFY + PUSH + HANDOFF (push-gap law MANDATORY): full
gate + run_tests + seed regression byte-identical; export; fetch
FIRST; push; ls-verify (public SHAs never exist locally — ls-remote
is truth). HANDOFF: NO ruling sheet (user D17: web sheet paused —
"we just need to get nearer to the mark for it to be a good fit");
instead rewrite NEXT to WAIT-USER-RULING and record in the LANDED
block the per-screen final grade table (clean / CONT-cycled / honest
seam) so the user's next freeform round grades against our own
claims.


Standing context: OQ-016/OQ-019 acceptance DEFERRED (rows stay OPEN; do
NOT re-ask, do NOT apply the t329 S4 draft); user saves 887/1086/1253
PROTECTED (~/ascendancy-saves-protected/, law: raw .SAV u32@0 = game-day).
A session woken by a DECISIONS.md edit or a *ruling*/*reply* file: read
docs/DECISIONS.md, apply what the ruling says, close rows per strict-close,
then author the next queue or re-park a WAIT sentinel.
PHASE-16 QUEUE ACTIVE (t422..t432, above) — phases 10-15 fully drained (t385..t420 all LANDED; per-row
text lives in git history + LANDED blocks). Phase-15 queue authored ON USER
RULING (see NEXT carried items H1-H4).

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
- Sitting check FIRST — RING-FIRST since t368 (the timeline watcher died
  2026-11-09 17:26; a stale feed's tail proves only that nothing was BANKED).
  `python3 scripts/t368_ring_turn.py` -> max_turn > 1086 => run
  r1_t85g_sitting.py before anything. Production :9 is the corpus — untouched
  unless the task IS a drive.
- Ledger 17 closed / 3 open (OQ-016, OQ-019, OQ-027; OQ-005 CLOSED t367 by the D1
  user ruling); ledger_audit +
  ledger_index_check green every gate; never hand-edit the index block.
- USER DECISIONS (docs/DECISIONS.md): D1 ANSWERED + APPLIED t367 (nothing
  owed); D2 ANSWERED (b) — the per-ship queue t360+ IS its application (this is
  the ONLY route
  to the nuke law + per-ship residues — EIGHT cited-dead capture legs), D3
  definition of done (t329 rewrote it: loop-closeable-without-user = NONE
  end-to-end; still DEFERRED by user). Do not burn iterations re-asking or
  working around them.
- Do NOT re-trod: t323/t332 route set; t293 click-selection; t49/t58/t265
  flight mining; item-35/36 completion witnesses (t271 zero-witness,
  AI-unreachable); t212/t213 static exhaustion; t326 research leg (races 0+2
  ALREADY own Phase Bomb tech at t1086 — mask 0x05, vacuous).
- Gate ~2-3 min; milestone 6 stays; work/ gitignored (git add -f is the ONLY
  exception, artifacts/ task t343).
- After the queue drains: author next queue or park WAIT-TRIGGER sentinel (task
  line FIRST; relaunch law MAX_ITERS=20 IDLE_GATE=0).
- SENTINEL-TAG LAW (t368, measured): loop_one_task.sh trigger C extracts field 2
  of the task line and arms whenever it is NOT WAIT*/IDLE*/PARK*/steer and differs
  from work/r1/loop/last_task. A sentinel written as 'NEXT t369 —' therefore
  reads as a QUEUE TASK: every park renumbers it and self-arms (loop.log 289885
  'WAKE: TRIGGER C queue drain (t366 -> t368)' armed the t368 session itself;
  the same class burned t214..t242 = 29 sessions). Law: parked sentinel task
  lines begin 'NEXT WAIT-<...> tNNN —' and the tag is NEVER renumbered (keep the
  tNNN in field 3 for the human reader). Human steering is tag-independent
  (dirty tree / LOOPSTEER.txt / FORCE_RUN), and IDLE_GATE=1 polls without
  launching, so a WAIT tag costs nothing and loses no wake route.


## LANDED t392 — 2026-11-14 (TITLE TEXT BASELINE + Alt-L/S/X SECOND LINES:
## THE D10 TEXT COMPLAINTS CLOSED WITH MEASUREMENT; VENDOR ROW-FOR-ROW
## WITNESS; UNDERLINE CLAIM REFUTED; LEDGER 17/3 UNCHANGED)

- Sitting check RING-FIRST: t368_ring_turn parsed=20/20 max_turn=1254 (same
  sitting as t380..t383/t391); zero new play; assignment stood. Tree clean
  at launch.
- TABLE LAW (windows.txt L128-170 cited): LOAD/SAVE/EXITTODOS = WINITEMS 2
  with second TEXTITEM verbatim "Alt-L"/"Alt-S"/"Alt-X" (dy fields 4/18);
  first four buttons WINITEMS 1. Alt-X is table-cited — user testimony
  corroborated, not merely adopted.
- PIXEL LAW (measured on pinned docs/assets/refcap/original-title-menu.png,
  capture shift +40 verified by pure-fill rows): single-line ink rows
  dy8..17/18 -> draw TOP y0+8; pair buttons dy4..13 + dy18..27 -> TOPs
  y0+4/y0+18 (dy fields land ON the ink tops); both lines centred (spans
  symmetric about rect centre 318). FACE: hint span 27 == bigfont 28
  (smfont 22 refuted) — vendor draws BOTH lines big.
- PORT DELTA: pre-fix our ink was the vendor profile shifted EXACTLY -4
  (title.cpp drew y0+4) — decisive explanation of "text is a tad too
  high". CODE: TitleButton gains `hint` (nullptr x4, verbatim Alt-* x3);
  bootHotkey gains 'x'->Quit; title.cpp draws per the three constants
  (kTitleLabelTopSingle/Pair/kTitleHintTop in boot.h).
- WITNESS (mechanical, our own render — R13-safe): scripts/
  t392_title_witness.sh boots Title in one Xvfb window; screenshot ink-row
  profile is ROW-FOR-ROW identical to the vendor on all seven buttons
  (btn0 8:11 9:7 10:7 11:39 ...; btn4/5/6 pairs 4..13 + 18..27); Esc exits
  live ("ui title esc" -> OK: EXITED_AFTER_ESC). Screenshot banked
  work/r1/loop/t392-title-after.png for USER look-grading.
- UNDERLINE NEGATIVE: external vision on the 3x crop claimed the 'L' of
  Load is underlined — MECHANICALLY REFUTED: inside the rect the census
  holds EXACTLY {fill (0,0,8), ink (215,215,215)}, dy14 white=0 (no row of
  underline pixels). '^' = word joiner; the port draws NO underline.
- HONEST LIMITS: xsend sends one keysym without modifier state, so the
  Alt-chords are unit-pinned only (test_titletext_t392.cpp x4), not
  live-synthesised; the hint-face finding is a size census (2/3 font-field
  semantics stay OQ-015 sub-grammar territory). Suite 301 tests 0 failed
  (297 -> +4). LEDGER: NO row moved (strict-close — queue work; the D10
  grade is testimony + our own-render measurement, not a witness for any
  OQ row's named closer). Law banked docs/re/boot.md §7 + _wip_t392.md.
  GATE_EXIT=0; ledger_audit OK; ledger_index_check OK; game/ untouched;
  production :9 untouched. NEXT = t393 NEW GAME SCREEN REBUILD (worst-
  graded screen first; its coordinate-space hunt precedes t394's).

## LANDED t391 — 2026-11-14 (PRESENTATION SWEEP: EVERY SCREEN ART-BACKED-OR-
## HONESTLY-VECTOR, CITED; ZERO CODE CHANGE; MASS 8/8 + REGISTRATION 0-
## CONFLICT PASS; LEDGER 17/3 UNCHANGED — STRICT-CLOSE, WAIT-USER-RULING
## RE-PARKED)

- Sitting check RING-FIRST: t368_ring_turn parsed=20/20 max_turn=1254 (same
  sitting as t380..t383); zero new play; assignment stood. Tree clean at
  launch.
- STRUCTURAL AUDIT (windows.txt parsed whole, 132 records): the eight
  TYPE-100 blocks head their state's window section; FIVE sections are
  headerless (2/4/15 load+save, 10 status, 14 intel, 17 planet-alloc, 18
  fleet). Disk census over all 165 .shp: 2savegam/4loadgam/10status/14intel/
  17np exist; NO 18*.SHP exists => FLEETWND SHAPEFRAME 0 cites nothing
  resolvable — honestly-vector in ANY faithful port. LOADSCREEN+LOADLIST
  STATE "2 4 15" serve load AND save; state 15 = [inferred] save-side
  variant (2savegam k0 art-in-hand; our port has no save screen, t382).
  TYPE-18 census = EXACTLY ONE record (NEWGAMEWND): 3cfgnew has no
  backdrop-size record (13 recs max 88x80) — frame honestly-vector, wheel
  faces cited art. Self-correction mid-session: first-pass grep claimed NO
  SHAPEITEM keyword; it exists x7 (ui.md §1 had it; banked the correction) —
  all seven implemented in the port (rail 1starmap k3/4/5/7, NEWGAME children
  3cfgnew k0): item-level art gaps NONE.
- NEW TOOLS + REAL RUNS: scripts/t391_screen_shot.sh (Xvfb :96 one-window
  tour, app-log-verified transitions, 8 shots -> work/r1/loop/t391-*.png);
  scripts/t391_screen_mass.py VERDICT PASS 8/8 (title 232,554 / load 59,803
  / status 53,438 art; fleet 4,035 / research 2,447 / intel 4,124 vector;
  map 32,096 / species 12,768 content-class) — pitfall banked: background =
  per-shot dominant colour (kBg differs per screen; fixed constant
  false-fails all 8); scripts/t391_registration.py (t386 conflict law
  through our ramp blit; S9 walk re-implemented value-emitting incl. the
  C==1 p-no-advance quirk + 0xAA/0x55 prefill-collision mask): 10status k0
  shift(0,0) 295,063 ramp-px 0 conflicts PASS, 4loadgam k0 50,296 0 PASS,
  off-shifts strictly degrade (sharp, not vacuous).
- NAMED SEAMS (none blocking): 7racesel 8x158x30 species-row strips =
  size-match witness ONLY (all eight rows SHAPEFRAME -1) — do NOT blit
  without a stronger witness; 17np k0 639x479 banked for state 17; chrome
  COLOUR stays the luminance-ramp palette seam (title-art.md §4) — geometry
  is what registers.
- LEDGER: NO row touched (strict-close — an audit moves no measurement on
  OQ-016/019/027). HONEST NEGATIVE: zero code change — the sweep found NO
  screen where the vendor has backdrop art and the port paints vector.
  Law banked docs/re/ui-runtime.md t391 block (ui.md is REGENERATED by
  ui_probe.py:271 — never bank there). NEXT re-parked WAIT-USER-RULING t374
  (queue fully drained; the three grading checks stand: title screenshot,
  --ui --audio listen = OQ-027 closer, seven-item menu shape). GATE_EXIT=0;
  ledger_audit OK; ledger_index_check OK; game/ untouched; production :9
  untouched.

## LANDED t389 — 2026-11-14 (PHASE-10 VERIFY + RE-EXPORT + PUSH)

What landed: phase 10 is PUBLIC. Suite 293/0 (rebuild clean). SEED REGRESSION
proven with a real baseline: worktree @ c7a3fda (last pre-phase-10 commit)
built with matching EMPTY CMAKE_BUILD_TYPE; `--headless --campaign 1600`
seeds 1/2024/23 byte-IDENTICAL base vs HEAD (md5 7e794a6d/332a8cf3/0a6b7876),
victories Extinct t266 / Extinct t285 / Control t1406 == the t365 banked
record — phase-10 UI/audio rows moved ZERO sim rng. Export
/tmp/pubpush-t389 via publish_public.sh: vendor-free (6298 objects, 5.6M
.git), uniform noreply identity, builds WITHOUT data 0 warnings incl.
ascend_ui (t389 key-fact 1 survived the history filter), run_tests 293/196
skipped/0 failed, gate --portable 0. PUSH: fetch-first law respected; TRAP
banked — the export's `origin` is the local SRC clone path, so fetch/ls-remote
grade the WRONG remote until `git remote set-url origin
https://github.com/weylandsmith/ascendancy-rewrite.git`; remote tip was
b2539b3, ancestor check FAST_FORWARD_OK, push b2539b3..36bf92d landed,
ls-remote verified == 36bf92dbb4bd. Askpass helper deleted (verified absent).
Ledger: NO row closed (strict-close — verify+push is not a measurement;
OQ-027 stays open on user-hearing/pointer-law witnesses). NEXT re-parked as
WAIT-USER-RULING t374 (tag law: never renumber) with the three concrete
grading checks (title-art screenshot compare; --ui --audio theme00/intro00
~1.4s/intro01 listen = OQ-027 closer; seven-item menu shape). Gate
GATE_EXIT=0 + ledger_audit OK + ledger_index_check OK (17 closed / 3 open).

## LANDED t388b — 2026-11-14 (SOUND FIDELITY: SUBTITLE CUE ENGINE + VOLUME LAW + SILENT-DEGRADE)

What landed: the intro-movie music law is now CODE, cited. AudioEngine
grew a cited tune table trackNames()={theme00,intro00,intro01} (race00..20
stay UNLOADED — selector never captured, §3.3), playTune with switch/same-
no-restart/stop semantics whose RANGE law is static so the machine is
device-independent, setMusicVolume mirroring the vendor's drop-not-clamp
0..127 guard, and --audio-trace (fflush'd `sfx <name>`/`music N <name>`
lines). playIntro(flic,maxFrames,audio) fires the subtitle.txt cue table
{20:TUNEID6->intro00, 966/971/976/981:VOLUME 100/80/60/30, 988:VOLUME 127
then TUNEID7->intro01} at replay index == FRAMENUMBER-1 (base ±1 named);
title.cpp restores theme00 after the movie (captured-selector law §3.3);
main.cpp: --audio init failure now DEGRADES TO SILENT (was exit 1) and the
dead P3-era second Mix_OpenAudio/CloseAudio pair is removed. Law banked
docs/re/audio.md §6.1-§6.5 (all addresses payload-relative: parser 0x2e46c
verb-NUMBER dispatch 0x2e4fe, case 16 stores 0x1e/0x1f @0x2e9e8, case 11
stores 0xb @0x2ea81, consumer 0x2ed37, volume FUN_0004feec guard -1<v<=0x7f,
play FUN_000678ec->FUN_00074a88 [handle+0x8868]). 4 new pins
(293 tests, 0 fail): audio_subtitle_script_cues_oq018 (cue lines byte-
exact incl. trailing-space law), audio_music_tune_table_law (table + real
file sizes + headerless shape), audio_vendor_volume_scale_law,
audio_tune_switch_law. LIVE WITNESS (scripts/_wip_t388b_intro_witness.sh,
Xvfb+xsend click 318,215): `music 0 theme00` boot -> `ui title click INTRO
-> intro` -> `music 1 intro00` fired mid-movie at frame 20. Silent-degrade
witness: ascend01/data emptied -> `audio: ... (degraded: silent)` +
`ui ok: turn 1` exit 0. MEASURED NEGATIVES banked: verb words
DIGITALMUSIC/FADEMUSIC exist ONLY in ascend00.cob:0x2811f (zero in image —
the numbers are the verbs); windows.txt SOUNDCHANNEL census {0 x118, -0 x1}
carries NO per-button sound id; STATE.md's '"2 10000 button" is the cited
SFX id' was FALSE (no such line). LEDGER: no row closed (strict-close —
the cue table is cited but the TUNEID BASE and button ids are not); row
OQ-027 OPENED for those two residues (closing witnesses = user hearing or
pointer-law capture of the heap tune table). Honest mid-session
correction: first cue reading transposed the frames (6@1/7@20); cat -A
proved 6@20/7@988 before any commit. Gate GATE_EXIT=0 + ledger_audit OK +
ledger_index_check OK (STATE index re-derived: 17 closed / 3 open).

## LANDED t388 — 2026-11-14 (CAMPAIGN SCREEN LAW + RAIL ROUTING + STATUS CHROME)

What landed: pure screen-law module rewrite/src/ui/statuslaw.{h,cpp} + 8
pins test_statuslaw_t388.cpp (289 tests 0 fail): screenAfterRailPress (msg
1 + param1 known-id switches; msg 5/7/8 + unknown ids NO-OP, never clamp),
railActive/railButtonForScreen (STATE id-lists), escapeToMap, verbatim
chrome rects (STATUSWND 7,7-632,472 + STATPLANLST 7,46-632,472, INTELSCREEN
7,7-632,34 + INTELLIST, FLEETWND, RESWIN 7,46-476,472, RACE_1..7 rows),
screenTitle/railLabel (TEXTITEM verbatim), screenShapeLib naming law. THE
DECISIVE TABLE FACT [verified 123/123 records]: STATE = "<count> <id>..."
id-LIST — Intelligence "1 7" is species-menu-ONLY, dissolving t264's
[inferred] z-order rule for the RACES/Intelligence 14-px overlap; rail "1
1" map-only; COSMOSWnd "4 1 3 7 13" keeps the map visible under the species
menu (t252 corroborates); STATUSWND is an independent FULL screen — the task
prose "bottom bar" is REFUTED by rect + STATE lists. SDL side ui.cpp:
screen variable + per-screen chrome backdrop blit (mechanical full-backdrop
test: record k0 >= 600x400 — measured 10status k0 639x479 FULLY OPAQUE
306081 px zero skip rows, scripts/r388_status_census.py imports the V/A law
from r1_shp_unifiedlaw, no re-implementation); rail draw per sidebarIcon
law (icons 1starmap k3/k4/k5/k7 censused; text-only buttons get none);
opened screens = frame + title + named content seams (species = race-row
frames over the map; NEGSCREEN state 13 inert); Escape inside->map/on-map->
quit; runLoadScreen + blitShape MOVED title.cpp -> vendortext.cpp (shared
via ui_internal.h; title.cpp behaviour unchanged, gate 4c-c still green).
HONEST NEGATIVES (all 132 records searched): NO button named Galaxy /
Production / Design exists anywhere in windows.txt (the task's button list
was prose, the table wins); SAVE/LOAD exist ONLY in STATE "1 0" — campaign
Alt-L (opens the t387 load window) / Alt-S (prints the no-campaign-writer
seam, t382) are LABELLED PORT ADDITIONS. Live witness Xvfb :81: map->
Planets->map->Species->Intelligence->map->NEXTTURN turn 1; wired as gate
4c-d (:82, greps every transition). NO LEDGER ROW CLOSED (strict-close:
this row wires cited table law; no OQ asks it). Right-click deselect
(selfplay.md): lands in the ui.cpp map-selection branch once selection
widgets exist — noted per task, not implemented.


## LANDED t387 — 2026-11-14 (MAIN MENU WIRING: NEWGAMEWND + LOAD SCREEN)

What landed: pure menu-law module rewrite/src/ui/menulaw.{h,cpp} (NEWGAMEWND
+ RACELIST + LOADSCREEN/LOADLIST rects verbatim windows.txt L575-717; the
three state-3 child buttons GALAXY_MORE/PLAYERS_MORE/DIFFICULTYMORE with
msgs 501/503/505; newgameControlAt hit-map; listSaveSlots + loadRowAt +
loadPickAccepts). SDL side title.cpp: blitShape (two-buffer prefill-diff
mask, skipped px -> alpha 0 per shp.h untouched-destination law; luminance-
ramp palette = NAMED SEAM, no cited chrome palette exists — index sets
disjoint from the t386 TSV 19/19 and 31/44), the Load seamLoop replaced by
the real load screen (4loadgam.shp k0 backdrop 639x479 [inferred role],
LOADSCREEN strip + slot rows pitch-39 law, hover, pick/refuse/cancel), the
RaceConfig placeholder replaced by NEWGAMEWND frame + k0 wheel face + child
buttons + RACELIST frame (clicks ACKNOWLEDGE, refuse-not-clamp). main.cpp
--saves DIR (supply-your-own only, NEVER game/; default <data>/saves).
Gate: 4c-c added — LOAD click opens the screen with slots=1 + backdrop
line, Esc cancels, RESUME+NEXT TURN still reach the campaign (timeout-wrapped
app, stale-X-lock cleanup; DISPLAY=:80 on the app launch is MANDATORY —
without it SDL silently fell to KMSDRM and every grep failed, measured).
Suite 276 -> 281, 0 failed (test_menulaw_t387.cpp x5). Live witness
(scripts/t387_menu_check.sh, Xvfb :79, ONE window): LOAD->open slots=4->pick
07.sav day 300->LOAD->refuse 43.sav torn->Esc->FRESHGAME->GALAXY_MORE msg
501->RESUME->next-turn->ok turn 1. Laws distilled docs/re/boot.md §6
(coordinate-space law binds every future windows.txt consumer).
Honest negatives: accepted slot does NOT import into a live Campaign (no
campaign-state importer; Observer read-only by contract — pick prints,
screen returns to Title); wheel-value setting is a campaign-seed seam;
RACELIST rows = t388 chrome; chrome COLOUR is a palette seam (needs a
vendor screenshot, none pinned); NO OQ ledger row moved (queue work;
open=OQ-016,OQ-019 unchanged). Gate ALL PASS GATE_EXIT=0; ledger_audit OK;
ledger_index OK. game/ untouched; production :9 untouched. NEXT=t388
STATUSWND + in-game menu bar VERBATIM.

Full law + every measurement: docs/re/title-art.md (hand-authored; grep
verified no generator or gate stage writes it). Instruments:
scripts/t386_title_art.py, t386_colour_witness.py, t386_remap_test.py,
t386_registration.py; derived pin data
rewrite/tests/data/title_palette_t386.tsv. NO rewrite code changed (this is
an identity row; the blit lands with t387's wiring). Ledger untouched
(OQ-016/OQ-019 stay open; phase-10 queue work moves no OQ row).
- IDENTITY LAW [verified]: the vendor title screen IS extracted/ascend01/
  data/0opening.gif (GIF87a, ONE frame 640x480, 53 used indices) blitted
  1:1 at (0,0) through an index-preserving palette swap. Decisive: the
  gif_index -> shot_colour map over the pinned vendor screenshot has ZERO
  conflicts across all 52 art indices at capture shift +40 (the banked
  window-chrome offset, refcap.md §1), vs 213,415 at +39 and 117,327 at
  +41. Label bands land on windows.txt centres +40; seventh button below
  the crop exactly as D9 predicts.
- KEY-SOLID LAW [verified]: GIF index 255 (GCT [0,0,255]) covers EXACTLY
  (159,200)-(477,470) = the windows.txt seven-button union; it is the only
  non-singleton map index (11,039 conflicts = the game's own menu chrome
  composited there). Port: blit GIF skipping 255, then 0opening.shp state-0
  strips + VendorText at (159,200..440 step 40, h30).
- REFUTED ARMS banked: 0opening.shp is strips-only (318x30 + 6x(30x318),
  zero records >=150x150 — it CANNOT be the figure); the GIF is NOT a movie
  frame (0/1144 intro65a + 0/226 logic exact-plane matches); palette
  membership laws are BLIND at the title (every candidate d0=9.2%); the
  .haz index-remap hypothesis 0/45; the GIF's own GCT is not the title
  palette (1/39). Chamachies lead NOT supported: lgrace19.shp = single
  record, smrace19.shp = 49-px sprite; figure = GIF prerender.
- MEASUREMENT LAW for t387+: identify/verify chrome by single-valued
  index-map CONFLICT COUNTS at the registration shift, not by palette
  membership, not by self-graded vision.
- RESIDUES (named, none blocking): blit-chain edge = referrers only as the
  0x2183x cluster (neither imm 0xa06 nor raw 0x835b6 occurs as u32 in
  work/ascend_restored.bin — a Ghidra xref walk is the named instrument,
  unexercised); the vendor title palette TABLE's origin unresolved (the TSV
  substitutes); GIF rows 440..479 clipped by the +40 capture, witnessed
  from the GIF only.
- ADOPTED from the dirty tree: notes/cmake-error.txt + cmake-warnings.txt
  (user's build-log dumps corroborating the t384 reqByte rename — 15x
  -Wc++20-compat before, clean after) committed so the tree is clean.

## LANDED t385 + t385b — 2026-11-14 (BOOT STATE MACHINE + TITLE SCREEN + D9 GAP CLOSED)
Queue rows t385 and t385b, one session. Full law + measurements:
docs/re/boot.md (hand-authored; ui_probe.py writes only ui/species/
diplomacy.md — checked, nothing regenerates it).
- BOOT LAW LANDED: --ui boots to the TITLE SCREEN (D8/D9). Seven vendor
  buttons verbatim from windows.txt L34-175 (INTRO/PLAYTUTORIAL/FRESHGAME/
  RESUME/LOAD/SAVE/EXITTODOS; column x159-477, h30, pitch 40, first y200;
  msg/param1 1/6,1/15,1/3,1/1,1/4,1/2,2/0). Pure routing law bootClick/
  bootHotkey (rewrite/src/ui/boot.{h,cpp}) — headless-unit-testable, no SDL.
  TITLERECT band 0,379-639,419 + BIGFONT name drawn; the campaign is ONE
  transition (RESUME), not the constructor path (runTitleScreen hands the
  live window to runCampaignUi).
- MEASURED t385b (boot.md §4): SDL2/X11 under WM-less Xvfb DROPS the first
  synthetic Button event on a freshly-created window (click#1 lost, click#2
  landed; single-window boots never lose). State transitions MUST reuse the
  window. Gate 4c-b now drives Title->RESUME->NEXTTURN through one window
  grepping both print lines; --resume added (autoplay gates 4c/4d use it);
  scripts/title_input_check.sh is the standing instrument.
- D9 GAP CHECK (boot.md §5): seven buttons/labels/exit ALREADY met;
  Alt-L/Alt-S hotkeys were the ONE gap — fixed via bootHotkey + pin.
  Honest negative: zero-diff would have been false.
- Suite 270 -> 276 (+6: rects/names verbatim, routing table, inclusivity/
  no-clamp, reachability, vendor labels, D9 hotkeys), 0 failed. Gate ALL
  PASS (incl. xvfb real-input chain + audio smoke). Ledger untouched (no
  OQ row moved this task; OQ-016/019 stay open/deferred per standing rule).
- HONEST SCOPE: title ART not rendered (t386); Tutorial/Load/Save are named
  seams that print and return to Title; RaceConfig overlay is placeholder
  text (t387 lands 3cfgnew/7racesel chrome).

## LANDED t383 — 2026-11-12 (VERIFIED PUSHABLE TREE + HISTORY PRIVACY SCRUB;
## QUEUE DRAINED — NEXT IS THE WAIT-PUSH-USER SENTINEL)
Delivered queue row t383 verbatim + one finding the row's own privacy bar
exposed. Full account docs/re/packaging.md §12 + docs/re/_wip_t383.md.
- Sitting check RING-FIRST: t368_ring_turn parsed=20/20 max_turn=1254 (same
  sitting as t380..t382); zero new play; assignment stood.
- EXPORT: GITHUB_USER=weylandsmith bash scripts/publish_public.sh
  /tmp/pubpush-t383b exit 0 — "vendor-free history, 6149 objects, 11M .git,
  tree intact." THE VERIFIED TREE = /tmp/pubpush-t383b (stale /tmp/pubpush +
  /tmp/pubpush-t383 deleted; script refuses existing dirs by design).
- HISTORY PRIVACY LEAK FOUND + FIXED (the iteration's real work): the
  personal [ISP-DOMAIN]-domain git-identity address survived the tip redaction in
  25 HISTORICAL blobs of docs/re/_license_draft_t372.md (git grep over
  rev-list; the full sweep timed out at 300 s — bounded count banked).
  publish_public.sh 1b now rewrites every blob (--tree-filter sed scoped to
  that path; --blob-filter does NOT exist on this box's git — banked pitfall)
  and a NEW fail-closed gate (exit 5) batch-scans ALL blobs via
  cat-file --batch. Post-scrub independent scan: 0 hits "[ISP-DOMAIN]", 0
  hits "hrethric@".
- VERIFIED ON THE CLONE, no vendor data: build exit 0; run_tests exit 0
  "270 tests, 192 skipped, 0 failed" (observer_* pins x7: 5 SKIP no-vendor +
  synthetic-terminator + render-map ok); identities 568x uniform "Weyland
  Smith <weylandsmith@users.noreply.github.com>", zero [ISP-DOMAIN], refs/original
  0; keep-checks pass; NOTICE copyright line intact. origin set on the tree
  to the user's repo URL (set-url ONLY — push is USER-gated, NOT run).
- OPEN DISPOSITION (user's call): 160 tracked files carry the plain username
  "hrethric" in /home/hrethric paths; username not credential; NOT scrubbed.
- Ledger 17 closed / 2 open UNCHANGED (queue mandate; nothing closable and
  nothing closed — strict-close held). NEXT = WAIT-PUSH-USER t383 sentinel
  (queue drained; tag NOT renumbered per SENTINEL-TAG LAW).

## LANDED t382 — 2026-11-12 (--save READ-ONLY OBSERVER + NATIVE .SAV SAVE LAWS)
Delivered queue row t382 verbatim: `ascendancy --save FILE` boots a save as a
READ-ONLY OBSERVER (day + fleet roster + star map + ship field; zero writes,
zero SDL, runs before archive load; --help states OBSERVER-not-gameplay scope;
refusal-not-clamp on parse failure — junk input exits 1 with the reason).
THE ITERATION'S REAL FINDING (not in the row's scope, found by probing the
row's input question): the NATIVE raw .SAV carries the ship array and star
table VERBATIM — laws MEASURED + banked docs/re/savegame.md "t382" section +
docs/re/_wip_t382.md (probes 1-14):
- day = u32@0 (4/4 saves: 1086/1253/887/1254).
- SHIP BLOCK: save-DEPENDENT home (content discovery by marker-chain scan;
  fixed offsets REFUTED — 01.SAV chain starts at marker 1), stride 0x166 =
  u32 slot-id marker + 0x162 record, markers strictly ascending, terminator =
  first violation; block == live list at save instant (01.SAV markers ==
  bank-t1086 live set EXACTLY 30/30; 04.SAV 38 slots vs ring-60 40 = same-day
  drift both directions, slot 12 died / {19,21,23} born after the save).
- STAR BLOCK: stride 0x60 K8 star-slot table (planets-ui.md §1 shape): name
  CP437 +0x1c, coords f32 +0x08, owner byte +0x14; 47/50 verbatim vs same-
  world ring RAM (3 owner-byte drifts); type domain 0..12 pinned.
- NEEDLE-ARTIFACT CORRECTION (method law): a probe window straddling record
  +0x52 (pointer fields) MISSES in save space (writer rewrites pointers,
  t298 class) — name-window needles at +0x34 hit. The first probe's "ship
  array absent from .SAV" reading was WITHDRAWN mid-session and superseded.
- FRAME RESIDUE (honest negative, kept OPEN as a named residue, no OQ row):
  ship pos = 32-aligned world frame (~±2300), star-record triples ~±430;
  NO scale unifies them (scan 3.5..8.0 no snap; placement-anchor f32
  -1560.0 = ZERO hits in the whole ring-60 member). Bridge = the kind-4
  +0x59 star-object pointer (ZIP path member = phys+0x88, 19/19 attribution
  incl. s23->Atropos; raw path pointer region rewritten -> no deref).
  Observer renders the two frames as SEPARATE maps, claims no projection.
Code: rewrite/src/game/observer.{h,cpp} (ascend_core, no SDL), main.cpp
--save branch, CMakeLists wired. Pins test_observer_t382.cpp x7 (day law,
ship-block law + witness pos, star-block law, savestate import + deref,
buildSim/findShip + junk refusal, SYNTHETIC terminator/K-domain pins, render
projection). MUTATION 6/6 CAUGHT (M1 stride 0x166->0x162, M2 dup-marker
terminator, M3 pos offset, M4 K-bound 12->50, M5 member-law sign flip, M6
dead-filter drop; M2/M4 first MISSED on corpus data — synthetic pin added per
mutation-campaign skill rule 4, then both CAUGHT with named FAILs). Suite
270/0; gate green; ledger audits green (17 closed / 2 open — NO OQ row
touched, queue mandate). NEXT -> t383 verbatim (last queue row).

## LANDED t381 — 2026-11-12 (GIZMO-USE DECREMENT + INVASION CONSUMPTION
LANDED: HANDLER-1 CHARGE LAW SUPERSEDES THE t364 NO-CHARGE READING;
resolveInvasion COUNT-LIMITED NEED = MIN(COUNT, SHIELDS+1); 10 PINS +
MUTATION 10/10 CAUGHT; SUITE 263/0; LEDGER 17/2 UNCHANGED — HONEST,
USER-GATED)

- Sitting check RING-FIRST: t368_ring_turn parsed=20/20 max_turn=1254 (same
  sitting as t380); assignment stood (zero-capture row).
- WITNESS RE-READ (work/r1/t370_slot_events_all.txt IN FULL, 29 lines —
  _wip_t381 S0): the S64 M2 "LOST 2x Invasion Module" summary HID slot
  multiplicity — Ignatz's ring held SIX cidx-73 slots (2..7) and EXACTLY the
  first TWO were cleared at launch (00:28:48 frame), four survive =>
  consumption is COUNT-LIMITED, not single-use, not all-or-nothing.
- STATIC (work/r331_disasm.txt; _wip_t381 S1/S1b/S1c): FUN_0003a174
  (callers EXACTLY {0x3d951, 0x42c8e}) — count loop 0x3a2a2 counts ALL
  cidx-0x49 slots i<cap; deficit loop 0x3a2f1 counts ACTIVE planet item 18
  +1 / item 19 +2 (income-law.md:565); cap 0x3a327 need := min(count,
  deficit+1); consume loop 0x3a360 clearSlot first-match walk-order stop at
  need. Owner-7 override 0x3a342 (table [0x12fb3+494*o] bytes {6,157,226,1,
  39,24,7,0} file-measured; zero only o7) NOT modelled, named. Handler-1
  FUN_0004c794: affordable+cost 0x4c7cf, null-target assert 0x4c7ea, range
  gate 0x4c831 (range0 = unlimited; status bit0x4 doubles via ds:0x85312 ==
  f32 2.0 FILE-MEASURED; cidx-0x2f leg is DEAD — dist*0.75 vs dist), commit
  gate 0x4c91d = affordable AND inRange AND (flags AND 0xc) (TARGETORBIT|
  TARGETSURFACE — first cited consumer as a GATE; t377's TARGETLANE finding
  is a different leg), mode==1 charge design[+0x36] at 0x4c958; DEC is
  dispatcher-side mode-1-gated (0x4a38b) — mode-0 probe lands NOTHING.
  Nanomanipulator gizmos.txt:116 `0 6 50 13 3 100 0 0 56` — DEC 3->2 AND
  -6 SAME FRAME twice (Stainer, Gofriller) reproduced EXACTLY.
- CODE: shipsim.cpp commitShot orderType==1 leg + ShipSim::resolveInvasion
  (contracts shipsim.h; SimDesign.targetOrbitSurface NEW); bridge wires the
  0xc mask. resolveInvasion is NOT wired into campaign.cpp's capture branch
  (aggregate volley has no per-ship transport ring — OQ-019 boundary, same
  shape as t209; named in _wip_t381 S3).
- PINS test_shipsim_t381.cpp x10; MUTATION 10/10 CAUGHT (checkpoint c41bc3d
  first; driver scripts/r381_mutate.sh): M1 dec-removed / M2 charge-mode-
  gate-removed / M3 gate-mask-dropped / M3b gate-range-dropped / M3c gate-
  affordable-dropped / M4 status-doubler-removed / M5 invasion-cap-removed /
  M6 off-by-one / M8 consume-stop-removed / M9 charge-from-power. M7 window-
  widening DROPPED vacuous (rule 6: need <= real count always).
- SUITE 263/0. Ledger 17 closed / 2 open UNCHANGED — no OQ row closes
  (user-gated). ships.md S69; OPEN-QUESTIONS t381 NOTE.
- NEXT: t382 VERBATIM (playtest boot OBSERVER --save mode).


## LANDED t380 — 2026-11-12 (QUANTIZER STORE LAW LANDED: EVERY COMMITTED
GALACTIC POSITION IS 32-ALIGNED — ARRIVAL-ONLY READING SUPERSEDED; 6 PINS +
2 GOLDENS CORRECTED + MUTATION 7/7 CAUGHT; SUITE 253/0; LEDGER 17/2
UNCHANGED — HONEST, USER-GATED)

- Sitting check RING-FIRST: t368_ring_turn parsed=20/20 max_turn=1254;
  timeline 9,349,893,839 B 400 KB tail-SEEK 12 rows ALL turn 1254 (wall
  03:42:07) = ring rotation only; r1_t85g_sitting.py NOT run; assignment
  stood (zero-capture row).
- STATIC (work/r331_disasm.txt verbatim, _wip_t380 S1a..S1d): FUN_00049aa8 IS
  a quantizing store (store +0x9e triple then call 0x533e0, all 3 axes
  verified through 0x534c9); callers 0x2202a placement / 0x399df scatter.
  The WALK quantizer call 0x4a2cf is UNCONDITIONAL; copy-back 0x4a2d9 gated
  ONLY by cmp edi,0x1 (edi=arg2 at 0x49f63, no intervening writes verified).
  Caller census of wrapper 0x49f28: executor commit 0x25560 edx=1; dry-runs
  0x15cc5/0x15df0 edx=0. => PARTIAL walks commit ON-GRID; arrival is
  bookkeeping only. Ties banked: trunc(round(v+16*sign(v))/32)*32 =
  AWAY-FROM-ZERO — identical to the sim's snapGrid shape.
- RUNTIME (scripts/r380_grid_census.py, new tool, zero capture): banks 100
  saves 4020 live rest rows / 1140 off-grid, off-by-kind {5:1140} — kinds
  1/3/4 ZERO exceptions; ring 20 saves same shape. Off-grid rows NOT
  lane-local (S22 L4 y in {0,1}, z x32): ZERO both sides. REFRAME: the t370
  mid-transit rows were kind-5 lane-local all along — consistent with the
  law, never evidence against it.
- CODE (shipsim.{h,cpp}): walkLaw snap unconditional after the walk math
  (moves := round(remaining RAW) order preserved); laneMarch lane-END +
  landingAttempt scatter snap (both 0x49aa8-shaped vendor stores); shipsim.h
  walkLaw doc rewritten. GOLDENS CORRECTED IN PLACE: t361 lane placement
  (1164,300,1006)->(1152,288,992); t362 clamp-operand 277.333->288 (clamp
  mutant separation preserved — walk-operand mutant lands 320).
- PINS test_shipsim_t380.cpp x6: mid-transit snap; negative-coord ties
  (-48->-64, -80->-96, -81->-96, -47->-32); lane-END arrival grid rest;
  lane march stays lane-local (pos frozen, laneX off-grid OK); scatter
  on-grid invariant + |d|<=516; corpus census (off-grid => kind5 lane-local,
  floors 400/150, self-skips on public clone).
- MUTATION 7/7 CAUGHT (r363r_mutate.py, checkpoint 7962fb8 FIRST per skill
  rule 1): M1 walk-snap-removed (10 fail) / M2 grid-16 (16) / M3 ties-toward-
  zero (7) / M4 lane-end-snap-removed (6) / M5 scatter-snap-removed (1,
  isolated by the t380 scatter pin alone) / M6 snap-identity (21) / M7
  ARRIVAL-GATED = the SUPERSEDED t361 reading restored (4 fails — the
  partial-walk pins are the isolator; the pre-t380 suite was blind to this
  law). Clean revert verified 253/0; campaign spot-check --seed 2024 exit 0.
- LEDGER 17/2 UNCHANGED — honest negative: no OQ row's named closer touched
  (OQ-019 user-gated; t380 NOTE added: law refinement + S64 reframe). GATE
  green; both audits OK; game/ untouched; production :9 untouched.

## LANDED t379 — 2026-11-12 (DEATH-vs-RECLAIM SHAPES RECONCILED + COUNT-WINDOW
SEAM + FINALIZER STORE-SET CORRECTION + 5 PINS + MUTATION 9/9 CAUGHT; SUITE
247/0; LEDGER 17/2 UNCHANGED — HONEST, USER-GATED)

- Sitting check RING-FIRST: scripts/t368_ring_turn.py max_turn=1254 (20/20)
  + 300 KB tail-SEEK of live-timeline.jsonl (rows still turn 1254, wall to
  02:01:31) => no new turn boundary; assignment stands (zero-capture row).
- MEASURED (banks on disk, scripts/r379_shape_census.py + r379_shape_verify.py,
  zero capture): the queue's TWO shapes are ONE law. s12 death = C4 in-place
  corpse (word diff: EXACTLY 5/177 words — name NUL-stamp +0x34, owner word
  +0x56:=0xffff, kind byte +0x58:=0 (high byte kept), act +0x5d:=0 (new leg
  the RAM adds to the disasm), +0x90:=0 UNATTRIBUTABLE-not-wired); s40
  'Intil-Za' NEVER WRITTEN (whole 0x162 record sha256-identical across the
  boundary) — its vanishing is the count DEC 41->40 at index 12 applied to
  the range(0,count) walk: the top live record orphans OUTSIDE the window.
  LAW 60/60 saves (both banks + production ring): count == live census;
  corpses-in-window == live-beyond-window; NO compaction ever seen.
- CORRECTIONS banked (not silent): ships.md S64 addendum's s12 'own0' is
  wrong (handle 0x00020000 => race 2, t273 law); the pre-t379 finalizer's
  +0x62/+0x63/+0x68 clears were unwitnessed hygiene — +0x68 is affirmatively
  RETAINED (0x002589f6 survived death) — removed from shipsim.cpp;
  [ds:0x3067b] (the C4 disasm's DEC word) is 0 in BOTH banks => it is NOT
  the array count word; the DEC writer stays UNATTRIBUTED (do not attribute
  it to 0x249b4). s12 integrity 20->20: this corpse was NOT produced by the
  hull<1 path — death producer unattributed; do NOT add integrity:=0.
- CODE: ShipSim::liveCount() (census mirror), countWindow() (array-order
  window, size==liveCount, corpse-in-window BY CONSTRUCTION, orphan law
  id >= census per the corpus boundary witness s40 id 40 == count 40),
  orphanedShips(); ships() keeps seeing orphans (fleet-list item 3).
- PINS test_shipsim_t379.cpp x5: real-commitShot death + full retention law
  (orderType/fireTarget/dispatcherGate/activeSlot/pos/power/eta/ring
  cidx+use-words/cap/filled); corpse-in-window + orphan boundary row;
  clean-boundary NEGATIVE CONTROL (DENSE ids — a sparse fixture is vacuously
  orphaned, learned this session); corpus dead-row shape both sides
  (self-skips without work/); s40 record byte-identity std::equal.
- MUTATION 9/9 CAUGHT (r363r_mutate.py, checkpoint 0a55a05 FIRST per skill
  rule 1): M1 liveCount-counts-corpses / M2 window-filters-corpses / M3
  window-no-trim / M4 window-sorts-eta / M5 orphan-strict-> (boundary row
  isolates >= vs >) / M6 orphan-no-owner-filter / M7 death-clears-gate /
  M8 death-clears-fireTarget / M9 death-keeps-act (t364 pin fires too).
  LESSON banked in ships.md S67: CHECK does not abort — index containers
  only behind guarded size CHECKs (unguarded orph[1] segfaulted the suite,
  rc=139, no FAIL lines, first M1/M5 run).
- CORPUS NOTE: production ring work/r1/playcap/save rolled over to turn 1254
  (same state as bank-play-20261111-late); test_shipsave_t360 frozen-exact
  case self-skips by design; durable law case green.

## LANDED t378 — 2026-11-12 (DESTINATION-TRIPLE ATOMICITY CODE LANDED:
issueDestination/clearDestination + 4 PINS + MUTATION 9/9 CAUGHT; SUITE
242/0; LEDGER 17/2 UNCHANGED — HONEST, USER-GATED)

- Sitting check RING-FIRST: live-timeline tail-SEEK (OOM law) — all parsed
  rows turn 1254 (wall to 01:22:48); the production capture is still live but
  no NEW turn boundary occurred since t377R => assignment stands (t378 is a
  zero-capture code row anyway; witnesses already banked).
- EVIDENCE RE-READ (_wip_t378 S1/S2, zero new capture): the S64 M3 witness
  resolves to FOUR in-window issue frames (s16/s38/s25/s18; s14's issue
  pre-dates the window, its END leg 00:24:02 is in-window): type (+0x67) ->3
  + triple (+0x6c) written SAME FRAME, kind stays 4 (NOT part of the pair),
  act 0->7 at every issue (7 outside the cited enum — banked observation, not
  wired). The queue's "0xFFFF no-target sentinel" does NOT exist on the order
  fields (honest negative): the cited 0xffff law is the OWNER half at the
  0x24a00 clear / 0x249b4 death (pinned t364/t360, not duplicated).
- CODE: ShipSim::issueDestination(shipId,x,y,z) — kind-4 gate (walk-guard
  family FUN_00049f54; no prior-type gate is cited so none imposed), accept
  writes type 3 + triple in ONE step, refusal writes NOTHING (no torn
  type-3/stale-triple state reachable). ShipSim::clearDestination — iff type
  3, clears BOTH fields atomically (Stainer order-end shape); type 1/2 never
  own +0x6c -> refuse, state untouched. shipsim.h note carries the full
  citation trail incl. the cadence-blind two-click non-model (N8 honoured).
- PINS test_shipsim_t378.cpp x4: atomic-pair (4 MEASURED triples exact
  round-trip, kind untouched); refusal-writes-nothing (kinds 1/2/3/5 + id
  999); order-end leg (+ object-order refusal); executor-consumes-the-pair
  (walk toward the EXACT issued triple; post-clear: act-driven pick still
  fires, type-0 arm walks NOTHING, pos frozen, power refill-only).
- MUTATION 9/9 CAUGHT (scripts/r363r_mutate.py, checkpoint 203f503 FIRST per
  skill rule 1): M1 kind-gate removed / M2 type-store removed / M3 triple-
  stores removed / M4 y,z-stores dropped / M5 type-store-before-guard (the
  refusal-totality isolator) / M6 clear-no-type-zero / M7 clear-no-triple-
  zero / M8 clear-guard removed / M9 clear-returns-false — all CAUGHT, clean
  revert verified (suite 242/0 post-campaign).
- BANKED: docs/re/ships.md S66 (full law + sentinel adjudication); OQ-019
  t378 NOTE appended (row stays OPEN, user-gated). Gate + both audits green
  (see commit). NEXT -> t379 verbatim.

## LANDED t377R — 2026-11-12 (MAGNETRON USE-SITE CODE LANDED: useMagnetron
+ 12 PINS + MUTATION 9/9 CAUGHT; SUITE 238/0; LEDGER 17/2 UNCHANGED —
HONEST, USER-GATED)

- Sitting check RING-FIRST: t368_ring_turn parsed=20/20 max_turn=1254 (ring
  kept rotating WITHIN turn 1254 after t377's 21:16 bank — 41/60.sav cksums
  differ, turn identical). 1254 > 1086 => r1_t85g_sitting.py re-run per the
  standing rule (background, work/r1/t377R_sitting.out): presence events
  t>=1240 are EXACTLY the already-witnessed M5 boundary + history rows +
  the Oct-28 t1335 echo (t377 FEED LAW); mid-turn offset census shows no NEW
  class. NO new witness; M1-M6 stand; t377R assignment confirmed.
- CODE (799c9c4): ShipSim::MagnetronReport useMagnetron(shipId, mode) in
  rewrite/src/game/shipsim.{h,cpp}, composed VERBATIM per _wip_t377 S3:
  entry derefs activeSlot (no [+0x62] test at 0x4a360; -1/0xff named
  refusals) -> C7 prologue DEC mode-1-only BEFORE handler, ungated ->
  C1 CORRECTED range gate (FAIL iff dist < Range*32, Range==0 skips) ->
  C2 bit0-only commit test, TARGETLANE = return flag (SimDesign.targetLane,
  bridge-wired gizmos flags bitpos 1; row 60 MEASURED flags=0x2) -> C3
  charge min(design,power) entry value -> 220a8 target-gate surrogate
  (kind==InSystem + targetStar resolves) -> FUN_00021f58 placement (star
  triple + (0,-200,0) + TWO LCG draws %200 x/z, ebx=200 both idivs) ->
  snapGrid 3 axes -> kind net 4 -> clearSlot(activeSlot) [C4]. Flagged
  composition consequences (zero-witness): gate-fail pays DEC no charge;
  committed-use-with-unresolved-target pays DEC+charge lands nothing;
  mode-0 lands NOTHING incl. no DEC, no draws.
- PINS test_shipsim_t377.cpp x12 (M1-valued fixture; expected placement
  computed from the sim's own LCG, NEVER vendor coordinates — S64 neg-(a)
  stands): burn-exact 90->80 / slot-consumed-once / placement-form+grid+
  2-draws / no-second-use (digest-identical) / zero-carried / gate-fail-
  DECs-still / unaffordable-DECs-still / mode-0-lands-nothing / non-
  magnetron-cidx-no-leg / TARGETLANE-not-a-gate / target-gate-shape /
  determinism. SUITE 238/0 (session start 226; +10 then +2 pins).
- MUTATION 9/9 CAUGHT (r363r_mutate.py; checkpoints b09cefb+799c9c4 FIRST
  per skill rule 1): M1 charge-amount, M2 clearSlot, M3 0xff-refusal,
  M4 POLARITY-INVERTED-to-t185-reading (27 fails — the corrected law is the
  suite-visible law), M5a DEC-removed, M5b DEC-affordability-gated (the
  unaffordable pin ISOLATES it, 1 fail), M6 mode!=1-exit, M7 TARGETLANE-as-
  gate, M8 snapGrid. Full per-mutant verdicts _wip_t377R S3; laws distilled
  ships.md S65.
- LEDGER 17/2 UNCHANGED — honest negative: no OQ row's named closer touched
  (OQ-019 user-gated; t377R NOTE added to the row: implementation of the
  corrected law, not the closer). GATE_EXIT=0; ledger_audit OK;
  ledger_index_check OK; game/ untouched; production :9 untouched; no new
  capture run.

## LANDED t377 — 2026-11-11 (MAGNETRON USE-SITE EVIDENCE COMPLETE + THREE
STATIC CORRECTIONS C1/C2/C7; RAM DESIGN-ROW READOUT NEW TOOL; CODE DEFERRED
TO t377R BY RUN BUDGET; LEDGER 17/2 UNCHANGED — HONEST, USER-GATED)

- Sitting check RING-FIRST: parsed=20/20 max_turn=1254 > 1086 => ran
  r1_t85g_sitting.py per the standing rule (exit 0, work/r1/t377_sitting.out).
  NEW SPAN FOUND (r369_playwindow exit 0, lo_ns 1794429182264000000, first
  turn!=1086 row wall 15:33:07) — but scripts/r377_feedcheck.py (new, reuses
  r370_slot_events.stream): 2236 frames 15:33->21:35 ALL turn 1254,
  first-vs-last ship_raw diff 0/40 slots. The user resumed the session but
  issued ZERO ship-record events. No new witness; t377 assignment stood.
  INSTRUMENT LAW banked (_wip S0b): the r1_stream trust law filters BELOW the
  watermark only — the accumulating timeline carries the OLD Oct-28 game
  (turn 1335 rows at line 239178, mtime_ns 1793245...), so an unfloored
  sitting census false-fires on turns ABOVE today's watermark; floor at the
  playwindow mtime_ns. Ring banked work/r1/bank-play-20261111-t377/ (20).
- STATIC RE-READS (work/r331_disasm.txt, verbatim, audit trail
  docs/re/_wip_t377.md C1..C8): windows FUN_0004a360 prologue, FUN_0004ca50
  whole body + case tree 0x4cd51.., magnetron leg 0x4cd0d..0x4cd43,
  FUN_000220a8 entry, FUN_00021f58 whole body, FUN_00049aa8, FUN_000533e0,
  FUN_000496e4. THREE CORRECTIONS to t185's S19 (in-place in ships.md):
  (C1) RANGE-GATE POLARITY INVERTED — raw 0x4cb76..95 fail leg fires when
  dist < Range*32 (TOO-CLOSE rejected; Range==0 skips via je 0x4cb99); M1
  (dist ~4700 vs bound 1600, COMMITTED) corroborates the bytes; the inverted
  reading would have REFUSED M1. (C2) "GATE 2" TARGETLANE is a RETURN-WORD
  bit, not a commit gate — 0x4cbd4 tests bit0 only (affordable AND rangeOK).
  (C7) dispatcher prologue DECs the slot use word BEFORE the handler,
  mode-1-only, UNGATED by handler-side gates: a gate-failed use still
  consumes a charge (zero-witness, flagged).
- MEASUREMENT (scripts/r377_design_rows.py, new tool; bank-play-20261111 3/3
  saves, B=0x1bf4d8 anchor-vote): loaded RAM design rows at B+0x82bb0+0x7650c
  stride 0x6a — row 60 cat=5 flags=0x0002(TARGETLANE) power=10 range=50
  level=0 numUses=1; row 9 cat=0 flags=0x000f power=6 range=50 numUses=3;
  row 73 cat=5 flags=0x0080(PASSIVE) power=10 range=0 numUses=0. LOADED==FILE
  re-confirmed for all three witness keys (t185 T1 law holds on the playtest
  saves).
- CODE: NOT landed (run budget expired after evidence; the complete landing
  contract — seam shape, gate order, pins, mutation targets — is _wip S3;
  STATE NEXT carries it as t377R, evidence re-read FORBIDDEN by the NEXT text
  to protect the next session's budget). Tree stayed clean of rewrite/ edits.
- LEDGER 17/2 UNCHANGED — honest negative: no OQ row's named closer touched
  (OQ-019 user-gated per t329; t377 NOTE added to the row: corrections are
  law refinements, not the closer). GATE_EXIT=0; ledger_audit OK;
  ledger_index_check OK; game/ untouched; production :9 untouched.

## LANDED t373 — 2026-11-11 (REPO HYGIENE EXECUTED: LICENSE/NOTICE/README
ROOT SWAP LIVE, work/ TRACKED-FILE LANDMINE DEFUSED + GATE-PROOFED, SPDX 505,
gate --portable + ASCENDANCY_DATA VERIFIED ON THREE CLONE SHAPES, QUOTE
AUDIT CLEAN — packaging.md S11 is the full landing record)
Steering: r369_playwindow lo_ns UNCHANGED (1794373326560000000); post-t372-
bank span frames=94 events=0 (idle since ~02:22); ring already banked at
t372 — nothing new to witness, assignment stood.
EXECUTED per _license_draft S3 + queue row: (1) LICENSE installed from
/usr/share/common-licenses/GPL-3, post-install ASSERT PASS md5 1ebbd3e3 +
sha256 3972dc97...36986; (2) NOTICE = _notice_draft minus 4-line header
(2417 B, sha256 2e5f4153...dd3bf; copyright line stays <TBD-t373> — author
identity USER-gated S7); (3) README replaced by t371 draft + t373 edits —
ascend01/02 importer stated as fact BY MEASUREMENT (cob.py extract: 328/89
files, diff -r clean vs reference trees; packaging S9b CLOSED), Windows
vcpkg honestly "not tested", authentic/defaults/open sections corrected
AGAINST THE LEDGER RECORD (old README still called OQ-003/005/006/010 open
— all closed t181/t367/t8/OQ-006; public statement now says 2 open of 26:
OQ-016, OQ-019); (4) landmine: git mv t368_ring_turn.py + sentinel_t369.sh
-> scripts/ (ring-turn re-verified parsed=20/20 from new path), git
rm --cached the 2 evidence files (on-disk + regenerable); git ls-files work/
= EMPTY, and gate.sh now FAILS if it ever isn't (recurrence invariant);
(5) SPDX sweep via scripts/r373_spdx_sweep.py: 505 inserted (rewrite 82 /
scripts 420 / tools 3, archive skipped), cookie-safe placement (4 files
have PEP-263 on L2), idempotent check exits 0; all py_compile-clean EXCEPT
scripts/r1_shp_streamlaw_variants.py which is broken AT HEAD since t67
(literal "...[truncated]" paste — verified identical pre-sweep; not a t373
regression; gate never runs it); (6) gate.sh --portable: 25 stages wrapped
in VENDOR guards + 4f predicate-fixed (pub-clone test CAUGHT it opening
extracted intro65a.flc) + 3r revenv guard (t343 fresh-clone gap);
ASCENDANCY_DATA=<vendor dir> symlinks game/ + auto-extracts extracted/.
VERIFY (queue bar: fresh clone + --portable exit 0 on THIS box): three
shapes all exit 0 — raw clone; PUBLISHED shape (minus game/+extracted/, 28
notes); published+ASCENDANCY_DATA (auto-extract ran, FULL vendor stages
executed). (7) quote audit scripts/r373_quote_audit.py: worst span in all
of docs/re = 4 consecutive lines (ui.md table rows), positive control
reports 6/6 — NOTICE fair-use-length claim holds (S9a CLOSED).
HONEST NEGATIVES: gnu.org byte-diff still not run (URL budget; hashes are
the anchor); GitHub push NOT done (USER-gated); vcpkg matrix unchecked.
No OQ row closed (hygiene is not measurement; strict-close: nothing closable
was closed). NEXT = WAIT-USER-RULING t374 sentinel (queue drained).

## LANDED t372 — 2026-11-11 (LICENSE DRAFT: GPL-3.0-OR-LATER + CREATOR
GRANT OFFER DRAFTED, CONTACT ROUTE CITED BY THE ONE APPROVED FETCH —
docs/re/_license_draft_t372.md + _notice_draft_t372.md)
Steering check per NEXT: ring parsed 20/20 turn 1254; r369_playwindow exit
0 but lo_ns UNCHANGED (1794373326560000000 = same t370 window); timeline
live (03:52:50); r370_slot_events over post-t371-bank span (lo = bank mtime
ns 1794385936844000000): frames=141 wall 03:32:18->03:54:29, events=0 —
user idle since ~02:22, nothing new to witness, t372 assignment stands.
Ring banked anyway per rotation law -> work/r1/bank-play-20261111-t372/
(20 slots, 43 MB).
LICENSE TEXT: source = /usr/share/common-licenses/GPL-3 (Debian
common-licenses) MEASURED verbatim-ready: 35,149 B / 674 L, md5
1ebbd3e34237af26da5dc08a4e440464, sha256 3972dc97...36986; structure greps
all pass (header L1-2, FSF verbatim-copy notice L4-6, TERMS L71, sections
0..17 L73..L612, END OF TERMS L621, apply-appendix L623). HONEST NEGATIVE:
byte-diff vs gnu.org NOT run (URL budget = 1 fetch, spent below); hashes are
the anchor of record. "or later" shape: LICENSE = v3 text alone; the + lives
in per-file SPDX ids + notice blocks (S2).
THE APPROVED FETCH: motesandbeams.com/about.html — VERBATIM "created by
Todd Templeman ... co-Founder of The Logic Factory, developer of the
original Space Strategy game, Ascendancy"; contact routes mailto
contact@motesandbeams.com + X @motesandbeams; site live/maintained (Mobe
public testing). SCOPE STATED HONESTLY: page carries NO rights statement —
the NOTICE grant is an OFFER, nothing closes on it. Quote + caveat banked
packaging.md S8; README draft <TBD-t372> placeholder resolved with the cited
route.
NOTICE DRAFT (_notice_draft_t372.md): GPL header block; dual-grant offer
(unrestricted incl. commercial, at their option, changes nothing for anyone
else, explicit "no license has been granted to us, we claim none");
publisher caveat honored per t371 (offer covers OUR code only; Virgin/
Broderbund/Softgold rights may sit elsewhere — text says so); vendor-
exclusion + abandonware-is-not-a-license statements.
SPDX SWEEP CENSUS (measured, git ls-files x ext filter x first-400B scan):
506 code-ish tracked files, HAS=0 (rewrite 82, scripts 418, tools 3,
archive 1, work 2). Sweep rules banked S4 (comment-first-line per language,
archive/ skipped, work survivors leave the set if untracked -> 504,
post-sweep grep -rL must be empty + gate green).
DECISIONS.md: D5 ADDED 'APPLIED 2026-11-10 user decision: GPL-3.0-or-later
+ creator grant'; still-user-gated items named (author identity for
published copyright lines, artifacts/, remote). Landing procedure atomic at
t373 per S3 (root LICENSE/NOTICE confirmed ABSENT this session — drafts
unclobberable). HAND-AUTHORED CONTROL re-run: no script opens packaging.md/
README draft/license drafts for writing.
LEDGER: NO OQ ROW TOUCHED (license adoption is a decision application, not a
measurement; strict-close trivially holds — nothing closable, nothing
closed). 17 closed / 2 open (OQ-016, OQ-019) unchanged. GATE_EXIT=0,
ledger_audit OK, ledger_index_check OK, game/ untouched. NEXT = t373 VERBATIM.

## LANDED t371 — 2026-11-11 (DISTRIBUTION SPLIT: PUBLISHABLE INVENTORY,
EXCLUDED SET, CASE AUDIT CLEAN, CI DRAFT, README DRAFT — docs/re/packaging.md)
Steering check FIRST per contract: r369_playwindow exit 0 but SAME window as
t370 (lo unchanged, first turn!=1086 row t1253 wall 00:02:09); session still
LIVE (dosbox pid 107664, watcher 107679, turn 1254 frames to 03:37). Banked
ring cp -p -> work/r1/bank-play-20261111-t371/ (20 slots, all 20 differ from
bank-play-20261111-late = ring rotated, saves live). r370_slot_events over
the post-late span (lo_ns 1794400000000000000..EOF): frames=466 wall
02:22:05->03:37:09, events=0 — NO ship-record field changes: user idle since
~02:22, nothing new to witness, t371 assignment stands.
INVENTORY (git ls-files measured): 1362 tracked files, 182.0 MB. Publishable
set 864 files / ~14.3 MB: rewrite 84/1.03, docs 178/8.11 (docs/re 115),
scripts 425/2.55, archive 166/2.03 (state-v2-full 159 + ralph-v1 7; vendor-
extension grep inside archive = 0 hits), artifacts 6/0.62, tools 3, root 2.
Excluded: game 23/94.2 MB + extracted 471/73.5 MB (167.7 MB vendor bytes —
user decision 2026-11-10: ship WITHOUT vendor data), work/ 17 GB incl
live-timeline.jsonl 9.1 GB (largest single file, live-appended).
LANDMINE FOUND (measured, not theorised): work/ is gitignored BUT 4 files
are tracked anyway (historical add -f): work/r1/sentinel_t369.sh,
work/r1/t368_ring_turn.py, work/r363_gizmo_census.out,
work/r363_gizmo_rows.json — a naive publish filter dropping work/ MISSES
them; t373 disposition listed in packaging.md S3.
CASE AUDIT (Windows, mechanical over 1362 paths): case-collisions 0,
file/dir case collisions 0, non-ASCII 0, spaces 0 — tree is Windows-clone
safe at path level; runtime-include/case checklist for t373 banked S5.
CI DRAFT S6: ubuntu/gcc13/apt-SDL2 vs windows/msvc/vcpkg vs macos/clang/
brew, scope = cmake build + run_tests (226 tests 0 failed MEASURED this
iteration ./rewrite/build/run_tests); capture-stack gate stages out of CI;
vcpkg sdl2-mixer availability NOT verified (no vcpkg on box) — draft status
stated honestly.
IMPORTER CONTROL: scripts/cob.py list game/ascend00.cob -> '54 entries,
table=ok' (extract subcommand exists, cmd_extract cob.py:82); ascend01/02
compressed-side importer NOT verified end-to-end -> supply-your-own-data
flow is INCOMPLETE, README draft says so instead of pretending (S9b).
README DRAFT landed docs/re/_readme_draft_t371.md (evidence rule, build/run,
supply-your-own-data, abandonware note w/ CITED sources: archive.org item
msdos_ascendancy 'is currently abandonware' + Wikipedia The Logic Factory
(Templeman brothers, site ceased June 2014) — both fetched 2026-11-11;
publisher caveat Virgin/Broderbund/Softgold -> NOTICE must not claim dev
grant covers publisher rights). Root README.md deliberately UNTOUCHED —
t373 swaps README+LICENSE+NOTICE+.gitignore atomically.
HAND-AUTHORED CHECK: grep 'packaging' scripts/* = 0 hits; no generator can
touch packaging.md or _readme_draft_t371.md (gate regenerants list unchanged).
HONEST NEGATIVES: docs/re quote-length audit not run (t373 checklist);
motesandbeams.com not fetched (URL policy; t372 fetches once); vcpkg matrix
unverified. NO OQ ROW TOUCHED (packaging is a distribution task; OQ-016/
OQ-019 stay open on user ruling — strict-close respected, nothing closable
here). GATE_EXIT=0, ledger_audit OK (rows=19 open=OQ-016,OQ-019 closed=17),
ledger_index_check OK, game/ untouched.

## LANDED t370 — 2026-11-11 (PLAYTEST WITNESS CENSUS: FIRST RUNTIME
WITNESSES LANDED — MAGNETRON USE, GIZMO-USE DECREMENTS, ATOMIC TYPE-3
DESTINATION WRITES; ships.md S64)
Window FOUND (r369_playwindow exit 0, lo_ns 1794373326560000000, first
turn!=1086 row = t1253 wall 00:02:09). Ring banked TWICE per rotation law:
work/r1/bank-play-20261111/ (all 20 slots t1253, orders placed, turn
UNENDED) + work/r1/bank-play-20261111-late/ (02:19, t1254 — user ended the
turn in between). New tools (both exercised on real data):
scripts/r370_slot_events.py (raw ship-record word-event stream over the
timeline window; full dump work/r1/t370_slot_events_all.txt) and
scripts/r370_bank_deref.py (Memory deref + star-grid census).
WITNESSED M1: magnetron use s28 00:13:50 — instant jump d=(+2464,-3104,
+2528), POWER 90->80 = gizmos.txt Lane Magnetron 'Power 10' EXACT, ring
slot 14 (cidx 60 use 1) REMOVED same event = single-use consumption.
+0x8c 40->39 lands LATER = hull, NOT charges: the t369 manual-pass
'charges' note is RETRACTED (spec +0x8c = INTEGRITY stands).
WITNESSED M2: gizmo use-counter decrements (Stainer cidx9 3->2 power -6 =
Nanomanipulator 'Power 6' EXACT; Gofriller 3->2->1; Ignatz LOST 2x cidx73
Invasion Module at invasion launch). cidx == gizmos.txt entry index (9/60/
73 independent hits).
WITNESSED M3 (record level): every empty-space move writes order type->3 +
[+0x6c] destination triple ATOMICALLY in one frame (5 ships); object moves
write type 1/2 + ptr. Two-click x/y-then-z testimony UNRESOLVED at field
level — 10 s watcher cadence is blind to sub-gap clicks (adjacent XY->Z
census = 0; cadence-blind != refuted). OQ-019 residue-(1) ANNOTATED
measurement-wise per queue law (amended, NOT closed; user-gated).
M4: SPARROWHAWK 10-s-cadence anomaly RESOLVED = watcher samples the
real-time glide (trip==pos each frame, power burn per step), not commits.
M5 end-turn bookkeeping: player POWER refills (84->90 etc), 5 lane-entries,
s12 cleared + s40 GONE n 41->40 = losses; corroborates S13-D at runtime.
QUANTIZER LAW CONFIRMED RUNTIME: mid-transit rows are OFF the 32-grid
((14,1,-224)x5, (28,0,-2144), 144.7->149.3), rest rows ON — K3b
off-grid-at-rest test is BLIND BY CONSTRUCTION (amend instrument, use
mid-transit signal). HONEST NEGATIVES (rows stay open): magnetron landing
vs star-table triple UNIDENTIFIED at scales 1/5/160 (S64 neg-a; +0x59
rebase law for the placement target needs the 0x220a8 disasm leg, NOT RAM
pokes); star-space vs ship-space unit mapping open; Vernunft I owner byte
unchanged across the end turn; two-click sub-gap unresolved.
CENSUS RUNS: r369_magnetron_hit --window C1=carriage-present 3850, C2=0
(by-construction, see above), C3=0; r369_order_diff --window kinds {4:8986,
3:2440, 5:3784, 1:780}, BOTH=2, two_click=0, decrements=4; --dir on the
first bank = 1 dedup sample (turn never ended inside it — honest negative,
instrument correct). game/ untouched; gate + both ledger audits green.

## LANDED t369 — 2026-11-10 (CENSUS TOOLS PRE-BUILT + CONTROL-VERIFIED;
## PLAYTEST WINDOW NOT YET OPEN — HONEST NEGATIVE; NEXT STAYS t369)

- Sitting check RING-FIRST: t368_ring_turn.py parsed=20/20 max_turn=1086 —
  no play yet at session start (watcher pid 107679 alive this time; game pid
  107664). Tree clean at launch.
- BUILT (queue row t369, zero corpus assumptions):
  scripts/r369_playwindow.py (window locator: disk mtime signal on
  work/r1/game/{RESUME.GAM,0*.SAV} vs banked baselines + bounded-tail
  turn!=1086 timeline scan with a MANDATORY mtime floor),
  scripts/r369_magnetron_hit.py (C1 carriage cidx60 / C2 off-grid st4 K3b /
  C3 W2 frame; --dir .sav mode + --window timeline mode),
  scripts/r369_order_diff.py (order/inventory ring diff; dest-vector classes
  XY / Z / BOTH; two-click witness = adjacent XY->Z events same slot;
  gizmo use-counter decrements; --selftest).
- CONTROLS (all real runs): zero-hit on work/r1/bank-t1086-preplay for both
  censuses (C1=C2=C3=0, 0 witnesses); POSITIVE fixture
  work/r1/t369-fixture (synthetic edited copies of a bank slot) fires every
  counter: C1=2, C2=2, C3=1, decrements=1, XY/Z classes fire, --selftest
  two_click=1 PASS. Timeline mode exercised on the real 8.9 GB file (814
  deduped idle samples, all counters 0 — correct pre-play shape).
- TRAP CAUGHT + FIXED (banked _wip_t369): the Nov-3 DRIVE EPOCH (turns
  1086->1236) lives in the same live-timeline.jsonl; an unfloored turn!=1086
  scan false-fires on it (observed: turn 1150 wall 14:09:29 mtime 2026-11-03).
  Playwindow floors at 2026-11-10 11:18 (pre-play bank time). t251 rewind
  caveat re-confirmed; wall clock collides across days — mtime is the only
  selector.
- INSTRUMENT LAW (fixture-derived): shared payload triples (bank ships 3+25
  both p=0x26d339) fan one edit into two slot-events and break XY->Z
  adjacency by design; issued orders allocate per-ship ptrs so live adjacency
  is meaningful. tl mode cannot deref +0x68 — full derefed two-click
  measurement requires --dir on a BANKED play dir; ring rotation ~200 s means
  t370 banks immediately post-session (RUNBOOK in _wip_t369).
- GATE RACE (the run went RED once, then green): shipsave_writeback_idempotent
  _t366 raced the LIVE 10 s ring writer — a torn ZIP mid-rewrite was counted
  in the denominator (zero divergences printed => not a law break; 3x direct
  reruns passed). Fixed TESTS ONLY (game/ untouched): torn-slot tolerance in
  test_shipsave_t360.cpp (reader loop + frozen-ring: was re-listing
  ringSaves().front() per record, i.e. the slot being rewritten NOW) and
  test_shipsave_t366.cpp (idempotence over parsed slots, parsed>=10 floor).
  LAW banked: any test reading playcap/save while production runs must be
  torn-tolerant. Full gate G_EXIT=0 after fix.
- LEDGER: NOTHING closed (strict-close; no witness exists yet — the tools
  are instruments, not evidence). OQ-016/OQ-019 rows untouched (user-gated,
  DEFERRED pending playtest). Ledger 17 closed / 2 open unchanged.
- NEXT: t369 rerun (queue law: 'Exit honest-negative if the window doesn't
  exist yet — then NEXT stays t369'). Runbook in docs/re/_wip_t369.md.


## LANDED t368 — 2026-11-10 (EIGHTH PARK: NO TRIGGER — PLUS THE DISCOVERY THAT
## THE STANDING SITTING CHECK HAD BEEN BLIND FOR ~14 HOURS, AND ITS FIX)

Branches, cited (full working detail docs/re/_wip_t368.md F1..F7):
- F1 THE FEED IS DEAD (the iteration's real finding). Branch-(1) as written
  tail-seeks work/r1/playcap/live-timeline.jsonl. That file is 8,917,535,608 B
  with mtime **2026-11-09 17:26** — zero growth vs the recorded baseline, ~14 h
  stale at session start — because the collector (`r1_playcap_watch.py`, pid
  1575) is GONE (`ps -p 1575` empty, no matching process) while the game (pid
  1555) kept autosaving every 10 s. GAME_HEALTH_LIVE.txt says exactly this:
  `UNHEALTHY | W:NOWATCHER(feed not banking)` + `ring 50.sav age 6s`. A dead
  feed means the tail law reports "no new sitting" even for REAL play (the
  20-slot ring rotates in ~200 s and leaves no trace). The law was satisfied
  literally while being blind.
- F2/F7 NEW PRIMITIVE (read-only, reusable):
  **work/r1/t368_ring_turn.py** — for each work/r1/playcap/save/*.sav: unzip
  `Memory`, resolve the base via the CITED cached-anchor law
  (`r1_slot.anchors_cached` + `base_of`), read the turn scalar
  (`r1_slot.read_slot`, OFF 0x82bb0 + 0x12e10). Two real runs: 07:2x and 08:0x,
  both **parsed 20/20, max_turn 1086, min_turn 1086**, ring mtimes live through
  07:57:46. Turn is monotonic in a running save, so a CURRENT ring reading of
  1086 retroactively covers the feed-dead window (mid-turn-only actions remain
  invisible to this probe AND to the standing law — stated, not hidden).
  => Branch (1) NEGATIVE before and after the poll; r1_t85g_sitting.py NOT run.
- Branch (2) ruling check NEGATIVE pre-launch, mid-poll, and post-exit:
  DECISIONS.md mtime **2026-11-10 06:23:41.040** == baseline exactly, `git diff`
  empty, porcelain = only this session's own docs/re/_wip_t368.md (t355
  path-audit applied), no *ruling*/*reply* files (the three
  dosbox-x `clock_reply.h`/`host_notify_reply.defs` hits are tracked vendored
  macOS headers — the poller greps `git status --porcelain`, so they cannot
  fire it). The OQ-005 sheet baseline stays unwatched (CLOSED t367).
- Branch (3) taken: park line appended to BLOCKED.md '## Sentinel park log'.
  Poller work/r1/sentinel_t368.sh via terminal(background=true, notify=true)
  (proc_6d442daa5692, pid 102048): exit 0 `TIMEOUT:no ruling after 45min`.
  Waited via process_manage(timeout=180) x7; TWO foreground tail --pid chunks
  hit the tool's 420 s cap (a timeout=590 request is REFUSED, not clamped) —
  harmless; NEXT now forbids them in favor of process_manage only.
- Watcher relaunch DELIBERATELY NOT DONE (F6): not the assigned task; launching
  a long-running writer from a sentinel session risks two writers on
  live-timeline.jsonl (the t85b dedup handles restarts, not concurrency).
  Harness/user call; safe procedure recorded in NEXT.
- Production :9 ALIVE: pid 1555 etime 1-06:50:34, -time-limit 172800, TL expiry
  **2026-11-11 01:07:10** (~17 h after this iteration — the corpus clock is the
  real deadline for any further live capture; note it).
- Ledger UNCHANGED 17/2 (OQ-016, OQ-019 — user-gated): zero measurement of any
  open-row constant this iteration, so nothing closable under strict-close;
  honest negative recorded. GATE_EXIT=0; ledger audit OK; game/ untouched.
- SECOND FIX (F8, harness): the sentinel itself was the wake. Written
  `NEXT t368 —`, its field-2 tag `t368` is not WAIT*/IDLE*/PARK*, so trigger C
  (`loop_one_task.sh:103-111`) read it as a queue task and armed THIS session
  (`loop.log:289885`, `queue drain (t366 -> t368)`) — the documented t243
  self-arm class returning through the instruction 'rewrite NEXT to the SAME
  sentinel verbatim' (words kept, number incremented). Field 2 is now
  `WAIT-USER-RULING` with tNNN in field 3; STANDING LAWS carry the rule.
  Validated by the scheduler's exact extraction (=> never arms), and the wake
  routes were audited first (dirty tree / LOOPSTEER.txt / FORCE_RUN / IDLE_GATE=1
  are all tag-independent, so no wake is lost). Under the live IDLE_GATE=0 run
  the scheduler will now log 'batch complete' and EXIT — correct t248 behaviour;
  relaunch (`bash scripts/loop_one_task.sh`) is the user's call.
- NEXT = same sentinel, RING-FIRST sitting law, tag WAIT-USER-RULING;
  work/r1/sentinel_t369.sh pre-staged (copy, baselines unchanged).

## LANDED t366 — 2026-11-10 (SAVE WRITE-SIDE SHIPPED: WRITE-BACK BYTE-IDENTICAL
ON 20/20 RING SAVES; VENDOR-EMITTED SAVE HEADLESS-UNREACHABLE = HONEST
NEGATIVE; SUITE 226/0; MUTATION 6/6 CAUGHT; LEDGER 17/2 UNCHANGED)

- Sitting check NEGATIVE (timeline 8,917,535,608 B unchanged; 400 KB tail-seek,
  turn 1086 on all records; r1_t85g_sitting.py NOT run per the >1086 rule).
  Tree clean at launch.
- CODE (rewrite/src/formats/shipsave.{h,cpp}, pership-spec §6 S7):
  serializeRecord() under a CITED-ONLY PATCH LAW — stores EXACTLY the parser's
  field set (the +0x00..+0x15e cited fields, ring cidx bytes at +0xab+7*i),
  NEVER touches unmodelled stride gaps or ring use-word/payload bytes (whole-
  record emit into fresh memory is therefore NOT yet faithful in the gaps —
  named limitation, pinned). writeShipRecords() = full-window 0x6b contract,
  geometry refusal (refuse-not-clamp), count refusal. rebaseRecord() per the
  t298 POINTER-VALUE LAW: shifts ONLY +0x59/+0x63/+0x68 by (newB - oldB);
  delta 0 = same-run no-op; self-inverse pinned.
- THE BYTE-COMPARE LEG (honest negative + real substitute): a GAME-EMITTED
  vendor save with ship records is NOT headlessly producable — game save is
  UI-driven, click path cited-broken (REFUTED-ROUTES t261/N8), second capture
  contract-forbidden, bank-t260-roundtrip-1255 is an emulator re-save of the
  input-dead class (REFUTED-ROUTES L273). Shipped substitute IS a byte-compare
  against vendor-saved bytes: parse->write-back->whole 17,055,880-B Memory
  member fnv1a64-IDENTICAL, 20/20 ring saves, stable across a second pass.
- CHURN CENSUS grounding the durable/transient note
  (scripts/r366_churn_census.py RC=0, work/r366_churn.out): same-turn ring
  pairs 19 — every field churns 0; t340 drive ring-final pairs 19 (turns
  1089-1093) — churn ONLY at +0x58/+0x59/+0x5d/+0x5e (order/act) and
  +0x9e..+0xa9 (pos). HONEST SCOPE: zero-churn at +0x62/+0x63 is observation,
  not vendor promise (no captured save holds an in-combat-at-boundary ship);
  t365's stance/gate/activeSlot transience stays a law reading; the writer
  round-trips those bytes verbatim.
- PINS test_shipsave_t366.cpp x3 (writeback idempotence / synthetic round-trip
  + patch law / rebase + refusals). SUITE 226/0 (223 + 3). MUTATION 6/6
  CAUGHT (scripts/r366_mutate.py; checkpoint e7ca7a2 BEFORE first mutant per
  the skill law): M1 gap write, M2 no-ring, M3 rebase-hits-value,
  M4 rebase-skips-slotptr, M5 geometry off-by-one (MISSED first — 16 B buffer
  slack hid the exact-equality edge; re-scoped to zero-slack, CAUGHT),
  M6 count-check dropped (abort class).
- LEDGER 17/2 UNCHANGED — honest negative: OQ-019 stays user-gated (t329);
  the write side completes the model's I/O surface (note added to the row),
  it is not the row's named closer. Files: docs/re/_wip_t366.md S0-S3,
  ships.md S63, OPEN-QUESTIONS t366 note.
- QUEUE EXHAUSTED (t359-t366 all landed). NEXT = t368 WAIT-TRIGGER SENTINEL
  (DECISIONS.md baseline 2026-11-10 06:23:41 = t365's own annotation write;
  the OQ-005 sheet baseline is CLOSED — do not watch it).

## LANDED t365 — 2026-11-10 (ENGINE FLIP: THE PER-SHIP ENGINE IS THE COMBAT
ENGINE; aggregate demoted to oracle; SEEDS AGREE — D2=(b) acceptance condition
MET). campaign_fleet_bridge.{h,cpp} (new): CampaignFleetBridge owns a ShipSim;
combatPhase() calls advanceBoundary() once/turn + resolveEngagement() per
border engagement; capture verdict = garrison death (cited C4). Surrogate
ledger S1..S12 in the bridge header (garrison-as-ship, synthetic pop-reserve
row at design idx 76+owner, power-gate-only sapping, chase-leg decision (a)
targetPos:=victim pos, isolated LCG = zero campaign rng draws).
aggregate_oracle.{h,cpp} (new): old volley/defense/absorb math moved VERBATIM;
Campaign::attackScore/defenseScore kept as delegating PIN SURFACES (production
combatPhase no longer calls them — grep-verified). test_campaign_fleet_t365
x5: P1 flip-live+determinism, P2 exact per-engagement oracle equivalence +
the named S3 sapping divergence both directions, P3 chase targetPos/stance,
P4 seed determinism, P5 80/80 census agreement. SUITE 223/0; GATE_EXIT=0;
seeds 1/2024/23 headless-1600 logs byte-IDENTICAL pre/post flip (Extinct
t266 / Extinct t285 / Control t1406 unchanged). DECISIONS.md D2 annotated
APPLIED; OQ-019 annotated "model exists, awaiting user acceptance" (row stays
open, user-gated per t329). FIVE first-run bugs fixed + banked
(docs/re/engine-flip-t365.md + _wip_t365b.md): dangling Ship* across
addShip-realloc; unaffordable shield upkeep (+1 top-up); missing first-pass
refreshUseCounts; invCap window must grow with fill (setSlot admits idx==cap);
STALE STATE ACROSS RECORD REBIRTH (cap=0/filled=1 -> shots=0 -> zero
captures -> seed-1 Extinct vanished) fixed by RESET-PER-ENGAGEMENT, matching
the aggregate's statelessness. LAW NOTES: loadGizmos never sets Gizmo::shield
(charge law = SUM cat-1 Level gated); InvSlot payload default 0 fails the
upkeep -1 test (0x4a6f9) -> synced slots get 0xffffffff (ledger S12);
run_tests' failure count counts CHECKs not tests. NEXT=t366 (its
"only if t365 green" condition is met).

## LANDED t364 — 2026-11-10 (PER-SHIP COMBAT ROUND INTO SHIPSIM: verbatim
windows 0x4a55c/0x4a360/0x4b8e4/0x4b740/0x42c60-region re-read FRESH with cap-
stone AND objdump (both agree); THREE banked claims corrected in place; code +
test_shipsim_t364.cpp x12, run_tests 218/0, MUTATION 6/6 CAUGHT; LEDGER 17/2
UNCHANGED — honest, both open rows user-gated)

- Sitting check NEGATIVE (live-timeline 8,917,535,608 B, tail 400 rows all
  turn 1086; r1_t85g_sitting.py NOT run per the >1086 rule). Tree clean at
  launch. One stray dosbox-x (pid 1555, vnc session) noted, untouched.
- CORRECTIONS (docs/re/_wip_t364.md C1..C9; in-place notes in combat.md
  S2g/S2k; pership-spec K2 updated): (C1) the 0x4a399 dispatcher KEY is
  BYTE [ship+0x67] (handler id 0 gun/1/2 drive/5 special), NOT design[+0x32]
  — the category gate is the volley loop's (0x4a5e1); (C2) stance map is
  0->2, 1->1, 2->1, 3->0 (t88's "2->0" read the jbe at 0x4a5a1 wrong);
  (C7) the resolver's no-carrier ownership branch has its polarity swapped
  in S2k (JNE=IS-local -> 0x437ee; fall-through NOT-local -> 2).
- LAW QUIRKS banked verbatim: (C3) APPLY + death are BOTH behind the
  0x4b7f1 mode==1 cmp — mode-0 probes set flags only; the dispatcher DEC
  precedes the handler and is mode-1-only; (C4) death finalizer 0x249b4:
  owner:=0xffff, kind:=0, live-count DEC (corroborates A3/A4); (C5) the
  volley writes [+0x63] for EVERY cat-0 slot before the call — the commit
  fires the LAST scanned gun, not the last hit one; charge fires EVEN ON
  ZERO DAMAGE (0x4bb64 falls through to 0x4bb6c); (C6) Leg A commits and
  RETURNS — no gunfire in the same resolution; (C9) Range 0 = UNLIMITED
  (0x4b9a3 je keeps the -1 in-range sentinel; zero-witness, flagged).
- CODE (rewrite/src/game/shipsim.{h,cpp}): Ship gains dispatcherGate
  (+0x62)/activeSlot (+0x63 index surrogate)/fireTarget (+0x68 ship-id)/
  systemId (K1 stand-in); SimDesign gains targetShip (+0x33 bit0; all 10
  cat-0 file rows carry it — re-measured) and special1 (+0x4a, the 0x2f
  Carbonizer override); API setStance/volleyTail/companionScan/commitShot/
  engageRound; digest extended with the engagement quadruple. Named
  non-inventions: handler-1/2 returns undecoded (sim returns false, state
  changes per stores; engageRound substitutes the GUN stance arg 3 — C8
  note); 0x437ee unmodelled; chase leg (walk toward +0x68) deferred t365.
- MUTATION 6/6 CAUGHT (scripts/r364_mutate.sh, driver r363r_mutate.py,
  checkpoint 08a6693 BEFORE the first mutant per the skill law): M1 stance
  map (MISSED first — pin re-scope: each stance step must START from a
  different handler value than the arg-under-test writes; re-run CAUGHT),
  M2 store-on-hit, M3 mode-agnostic apply, M4 charge-after-damage, M5
  mode-0 DEC (MISSED first — fixture used an unlimited-ammo row; finite
  numUses makes it observable; re-run CAUGHT), M6 Leg-A fall-through.
- HONEST NEGATIVE: no OQ row closes (t364 contract: user-gated); the
  aggregate engine stays THE engine until t365 flips it; per-ship-vs-
  aggregate seed parity is NOT claimed anywhere — it is t365's test.

## LANDED t363R — 2026-11-09 (GIZMO INVENTORY + UPKEEP BURN + CARRIER LAW
CODE LANDED VERBATIM: shipsim.{h,cpp} + test_shipsim_t363.cpp x9, run_tests
206/0, MUTATION 6/6 CAUGHT; LEDGER 17/2 UNCHANGED, HONEST NEGATIVE)

- Sitting check NEGATIVE (live-timeline 8,917,535,608 B unchanged from the
  t363 baseline; 400 KB tail 16/16 rows turn 1086; r1_t85g_sitting.py NOT
  run per the >1086 rule). Tree clean at launch (shipsim.{h,cpp} == HEAD,
  the t363 revert claim CONFIRMED before coding).
- Contract docs/re/_wip_t363.md S5 executed ITEMS 1-8 IN ORDER; raw re-reads
  banked as _wip_t363 S6. NEW from the re-reads: fillFirstEmpty window is
  CAP (0x4964a `cmp eax,[+0x15a] jl`) — spec G3 "scans all 25" superseded;
  the recalc also zeroes +0x18 (0x49af5); completion zeroes DWORD[+0x9e]
  (lane-local x) at store 0x49a78.
- WIRED (the three named seams CLOSED): (i) upkeep FUN_0004a658 at BOTH
  call sites — sweep prologue (burn BEFORE the MIN pick) and tail (after
  refill+refresh+march); bit0 zeroes MOVES, ring scan STILL RUNS; payable
  gate = whole-slot skip (no partial burn, charges NESTED); bit3 zeroes
  charges. (ii) tail refresh loop use := design[+0x42] (+0x42 operand
  measured 5940/5940 save-side; the "+0x4e" queue wording SUPERSEDED).
  (iii) kind-2 completion FUN_00049a34 inside commitMove orderType-2
  arrival (admission FUN_000499f8: lane gear OR species flag AND lane NOT
  closed, bit 0x2 SET == DENIED; admitted -> kind 5, laneId, laneToB; the
  assert leg COUNTS kind 5). t361-era scatter-on-type-2 fallback superseded.
- CARRIER/CARGO FIELDS per spec C1-C4 (no C5 chooser): ring InvSlot[25],
  invCap/invFilled verbatim import (NO recalc on import — powerMax law);
  recalcShip carrier law (LaneDrive->stepX 14, Hyperdrive->stepZ 28 pools
  DERIVED from measured live pairs; Colonizer->targetSlot -1; Cloaker->
  specialCount); carriesCode / firstCarrier (C2 loop 0x42d09 verbatim shape:
  InSystem + slot==code, list order, no strength test).
- MUTATION CAMPAIGN 6/6 CAUGHT (scripts/r363r_mutate.py, reusable): M1 bare
  re-grant (first pin was NOT sweep-visible — re-scoped powers 28/22 so only
  the SWEEP burn flips the pick; MISSED then CAUGHT after the pin fix), M2
  skip-ring-on-bit0, M3 charges-unnested, M4 refresh operand +0x3e, M5
  recalc window inclusive, M6 phantom rejected at idx==cap.
- INCIDENT (self-inflicted, fully recovered): the first mutation run's
  `git checkout --` revert fired while the code was still UNCOMMITTED and
  wiped the cpp work; re-applied all six patches verbatim from transcript,
  re-verified build+suite, THEN checkpoint e9c8bae before the real campaign.
- Banking: ships.md S62; pership-spec G9 polarity correction IN PLACE
  (global added when bit SET, raw 0x4a68e); OPEN-QUESTIONS t363R note on
  OQ-019 (row STAYS OPEN — user-gated, honest negative: no named closer
  touched, magnetron/Phase-Bomb remain zero-carried, HOME = ring field).
  LEDGER 17/2 UNCHANGED; gate + both audits green. NEXT = t364 VERBATIM.

## LANDED t363 — 2026-11-09 (GIZMO INVENTORY EVIDENCE COMPLETE: UPKEEP/
RECALC/REFRESH/KIND-2-COMPLETION ALL BANKED BYTE-LEVEL + SAVE CENSUS
5940/5940; CODE RE-LAND DEFERRED TO t363R BY RUN BUDGET — DRAFT REVERTED
CLEAN; LEDGER 17/2 UNCHANGED, HONEST NEGATIVE)
- Sitting check NEGATIVE (live-timeline mtime 17:26:31 == t362 baseline; turn
  1086 standing law; r1_t85g_sitting.py NOT run per the >1086 rule).
- VERBATIM (docs/re/_wip_t363.md S1/S3/S4, work/r331_disasm.txt line refs
  in-file): FUN_0004a658 upkeep body (MOVES re-grant IS part of it — bit0
  zeroes MOVES but the RING SCAN STILL RUNS, S4 item 1 corrects the first-
  pass reading; payable gate `cmp/jl` skips the slot ENTIRELY — no partial
  burn, no charges; shield recharge NESTED under affordability);
  FUN_00049acc recalc byte-level (the lane-step pool constants DERIVE to
  14.0/28.0 from the MEASURED live pairs (14,0)/(0,28) — closes the S22
  step-constant residue as a CARRIER law: 1 Star Lane Drive -> +0x08 14,
  1 Hyperdrive -> +0x0c 28); turn-tail refresh operand IS RAW design[+0x42]
  (0x7654e-0x7650c; STATE's t362-era "+0x4e" wording was off-by-convention —
  S1c CORRECTION); FUN_00049a34 kind-2 completion FULLY banked incl.
  FUN_000499f8 admission (lane byte+0x23 bit 0x2 SET == CLOSED, polarity
  adjudicated from the raw jne — S4 item 3) and the +0xa2 direction flag.
- MEASUREMENT (scripts/r363_gizmo_census.py RC=0, work/r363_gizmo_census.out;
  20 saves / 2140 live rows / 5940 real ring slots): REFRESH LAW 5940/5940
  (design0 slots all carry word 0; NumUses-1 slots all carry 1; below/above
  buckets EMPTY); RESIDUE HOME census — Invasion Module 0x49 on 500 slots/
  260 ships, Colonizer 960/140, Lane Drive 980/500, Hyperdrive 200/100,
  Magnetron 0x3c and Phase Bomb 0x46 ZERO slots (consistent t326b/t329);
  slot payload dword 5860==0x0 / 80==0xFFFFFFFF and ALL 80 sit on upkeep-
  gate rows — the `-1` gate is SELECTIVE in real data; duplicate cidx legal
  re-confirmed (600 rows).
- FILE-vs-RAM cross-validation: gizmos.txt parse (work/r363_gizmo_rows.json)
  reproduces the RAM-measured upkeep-gate census EXACTLY (rows 10..15 only,
  all cat-1, costs {1,2,0,2,4,3}, levels 1/2/1/3/4/5) — loadGizmos IS the
  design table for every column the cited laws read. pership-spec G9 bit-
  polarity correction banked (addend applies when bit 0x2 SET, not clear).
- CODE: full draft landed mid-session then REVERTED (git checkout, tree
  clean) when the run budget expired pre-build/pins. The complete rewrite
  contract (structs, gates, advanceBoundary ordering, digest, fromRecord,
  8 pins, 6 mutants) is _wip_t363.md S5 — t363R executes it verbatim.
- LEDGER 17/2 UNCHANGED (honest negative: every census fact corroborates
  laws already credited t47/t86/t89/t101/t184; no OQ row's named closer was
  touched; magnetron/Phase-Bomb rows stay user-gated).

## LANDED t362 — 2026-11-09 (MIXED-FLEET DEPARTURE LAW: THE EXECUTOR DRIVER
REPEATS — PIECEMEAL DEPARTURE IS VERBATIM LAW, t361's ONE-PICK READING
SUPERSEDED; 7 PINS, run_tests 197/0, LEDGER 17/2 UNCHANGED)
- Sitting check NEGATIVE (16/16 records turn 1086, ring rotation only; ring
  FILES rotate even when the turn does not — shipsave_t360 flaked once
  mid-run from a 19:04-19:05 ring touch, clean on re-run — environmental).
- WITNESS CENSUS scripts/r362_departure_witness.py (exit 0, output
  work/r362_witness.out; t265 corpus law verbatim: file_mtime_ns windows,
  regimes A+B healthy, softlock gap excluded; 163,432 lines, 602 rows):
  MID-TURN kind flips ZERO (10267 st5 same-turn deltas all 0.0); PER-BOUNDARY
  3-same-owner flips EXIST — owner 1 slots 17/20/29 t1104->1105, owner 2
  12/21/23 t1111->1112 (both directions twice). st4 off-grid {} re-confirmed.
- STATIC (work/r331_disasm.txt verbatim, _wip_t362.md S4/S6/S7, ships.md S61):
  DRIVER FUN_0002547c 0x2550c..0x25527 `or edi,eax` + `test edi,edi; jne`
  = re-run the whole per-race pass while any race reports work; ah arms
  1/2/3 -> commit hooks 0x49f28/0x39c10, other -> assert 0x8f5. COMMIT EXIT
  FUN_00041260 0x41b8f..0x41ba6: work iff REMAINING WALK > 0 (sar 0x10; jle
  -> return 0). kind-5 stores are FOUR sites (0x22243/0x2228f/0x49a74/
  0x4cd16 — the 0x49a74 leg inside the kind-2 completion body now banked in
  part). MOVES re-grant 0x412cf is INSIDE the re-invoked prologue => per
  sweep. Termination: 0x4134e POWER gate drains the race.
- CODE (shipsim.cpp advanceBoundary): sweep loop, repeat driven by commitMove
  status (status = post-walk remaining > 0 — the most literal mapping; the
  raw-vs-rounded micro-edge 0<remaining<0.5 NAMED in _wip_t362 S7, no witness
  either way); T-10 decrement hoisted ONCE per boundary AFTER all sweeps read
  the words; stale-act clear once per boundary (named simplification);
  BoundaryReport.sweeps + executorStalled safety cap (never fires, pinned);
  laneMarch made a PUBLIC seam (march law invisible at boundary observation).
- PINS test_shipsim_t362.cpp x7: piecemeal order (ascending POWER 30/20/10
  departs 3 ships in ONE boundary, sweeps==4 incl. the silent drain sweep),
  exhausted-budget stop (remaining 0 -> no repeat; continues next boundary),
  POWER-gate no-op sweep (clamp->0 power: acted 1, sweeps 2, re-grant makes
  moves 10 NOT 9 — remaining is STATUS not durable state), dwell suppression
  across sweeps, march-spends-NEITHER (seam pin), power-clamp-operand
  (d=2.6 sugar/power 2: pos 277.333 separates scale-operand mutants), stall-
  cap negative control (6-ship 2-day drain, 12 acts, cap never fires).
  MEASUREMENT FACTS: landing always fires the T-6 scatter — pin flags not
  coordinates (t361's r3.landed pins already respected this).
- MUTATION 4/4 CAUGHT: clamp-scale power/walk (condition swap is VACUOUS —
  integer power makes both conditions equal; S60 wording corrected by this
  measurement), march-burns-MOVES, no-repeat (t361 behavior, x20 collateral),
  per-sweep decrement (breaks t361 expiry pins too). All restored; 197/0.
- LEDGER 17/2 UNCHANGED — honest negative: no OQ row's named closer touched
  (sweep-count coupling was a queue-row mandate, not an OQ row).
GATE_EXIT=0. NEXT = t363 VERBATIM.

## LANDED t361 — 2026-11-09 (PER-SHIP ENGINE SKELETON SHIPPED:
## rewrite/src/game/shipsim.{h,cpp} + 11 PIN TESTS, run_tests 190/0; EXECUTOR
## PICK ADJUDICATED MIN (ai-dossier §5 MAX wording corrected in place);
## MUTATION CAMPAIGN 3 CAUGHT / 2 NAMED GAPS BANKED FOR t362; LEDGER 17/2
## UNCHANGED — honest negative on closes, strict-close held)

Sitting check FIRST: NEGATIVE — timeline 8,897,010,542 B (15:05 mtime), 400 KB
tail-seek, 16/16 records turn 1086; r1_t85g_sitting.py not run; production :9
untouched; game/ read-only.

DISPUTED-INPUT ADJUDICATION (_wip_t361 S1, resolved BEFORE encoding): the
executor POWER pick — pership-spec §2 says MIN (strict <, first ties), ai-
dossier §5 t179 P1 says MAX. Raw objdump of work/ascend_payload.bin: Intel
`cmp 0x88(%edx),%eax` + `jge`-skip = replace-on-STRICTLY-SMALLER, matching
the t183 decompile (ships.md S17 T4 verbatim MIN). The 0x41949 threshold-zero
path is a post-commit re-scan, not the sweep entry (stated honestly; sweep
init not re-derived, budget-bounded). ai-dossier §5 annotated CORRECTION in
place. Also raw-confirmed: eligibility gates 0x4134e (POWER>0) / 0x41357
(kind!=1) / 0x419a7 (act set), assert law 0x419cf..0x419f1 (id 0x93e at
0x2a428), stale-act clear 0x41a30 + re-decide 0x41a45, sort comparator 0x40eb4
operand = +0x52 (the "design power" label vs +0x52 stays DISPUTED — sim
encodes the verbatim comparator, ascending stable), list builder 0x40ec0
(stride 0x162, cap 0x6b, live gate ds:0x43489>>16 — A1/A3 code-level echo).
0x3ac1c read: word store +0xac on the pending-slot object (0x3ac880 converter,
+0xab==0x05 guards) — spec G-a CONFIRMED: queued-order field home on the ship
record is NOT cited; sim models the T-10 suppress-and-decrement behaviour at
sim level, never invents a record offset.

CODE: shipsim.{h,cpp} — OrderKind {0..5}, Lcg (FUN_0007824f verbatim, own
ISOLATED stream per campaign-RNG discipline), turn frame per spec (2): tail
(+0x9c zero, t101 refill, kind-5 march T-7 with third-speed gate, NEITHER
MOVES nor POWER spent), sort, per-race executor (MOVES re-grant, stale-act
clear, MIN-pick, T-10 suppression pre-decrement read + post-pick decrement,
assert COUNTED not fatal), walk law T-9 (guard kind==4 verbatim; clamp operand
STEPS; +0x94 := round(remaining); x87 fistp round-half-to-EVEN — C round()
diverges on .5 ties, pinned), T-3 placement (star + (0,-200,0) + %200 x2,
sequential draws — call-order-in-one-statement hazard fixed), T-6 no-slot
branch + act consumed (S24 stasis-forced), T-4/T-5 transitions, digest()
FNV-1a64 determinism pin surface. SEAMS named in ships.md S60 (upkeep t363,
FUN_00049a34 body unbanked, decider scoring unbanked, dangling-lane hold).

TESTS: test_shipsim_t361.cpp x11 — golden LCG vectors seeds 1/7/2024 + state
pin 0x264e4f5d; x86round 10 cases; powerRefill 9 cases; walk vectors (arrival/
moves-limited/power-clamp/2.5-tie off-grid-snap/zero-dist); table-driven
T-4/T-5 admit+refuse; march+placement golden jitter (164,6) + third-speed +
no-rng/no-fuel; dwell stasis 5 boundaries + expiry 2->1->0->fire + act
consumed; MIN-pick flip/tie-first/POWER==0/stale-act; assert counter;
12-boundary two-run digest equality + seed divergence; fromRecord mapping.
run_tests 190/0 (179 baseline + 11). MUTATION (ships.md S60): max-pick 3 fail,
no-decrement 7 fail, tie-away 5 fail CAUGHT; power-clamp-operand and march-
burns-MOVES NOT caught -> named t362 parity mandate.

LEDGER: no row touched (skeleton per D2=(b); OQ-016/OQ-019 user-gated). 17/2
unchanged; both audits green. Production :9 untouched; game/ read-only.
GATE_EXIT=0. NEXT = t362 VERBATIM.

## LANDED t360 — 2026-11-09 (PER-SHIP SAVE PARSER READ-SIDE SHIPPED:
## rewrite/src/formats/shipsave.{h,cpp} + 3 PIN TESTS, run_tests 179/0;
## SAVE-SIDE LAWS MEASURED ships.md S59; FILLED-LAW DISPUTE RESOLVED; LEDGER
## 17/2 UNCHANGED — honest negative on closes)

Sitting check FIRST: NEGATIVE — timeline 8,890,184,654 B, 400 KB tail-seek,
16/16 records turn 1086; r1_t85g_sitting.py not run; production :9 untouched;
game/ read-only. Corpus: production ring work/r1/playcap/save/41..60.sav
(turn 1086, 20/20 base-verified; the queue's "bank-t1086*" glob matches
nothing on disk — the ring IS the banked frame set; noted, not a blocker).

MEASURED (scripts/r360_save_shipcensus.py + probes, all cited in
docs/re/_wip_t360.md S2 + ships.md S59): B==0x1bf4d8 20/20 (anchor-vote
re-derivation, agrees t333 needle); whole 0x6b-slot window byte-identical
across the ring (md5 54bea6e3e9cd66236dd3ff0d6ba34738, FNV-1a64
0x3acb4b625a289f54); count word 30 is NOT the census — 4 live records at
indices >=30 (ships.md fleet-list item 3 confirmed save-side); dead marker
u32@+0x54==0xffff0000 (NOT 0xffffffff) with uniform (kind,cap,filled)==(0,5,0)
1540/1540; attr law (handle>>16==race) 600/600 live (t273 re-confirmed);
live kinds {3:80,4:60,5:460} subset A4; caps {10:500,15:20,25:80}. FILLED-LAW
RESOLUTION: exclusive law holds 600/600 here vs §18 inclusive 1234/1234 on
t184 — consistent because the ring span ends AT the cap dword (+0xab+7*25 ==
0x15a): probe(idx==cap) on a cap==25 row self-reads the cap low byte. No
contradiction remains; pership-spec +0x15e row annotated RESOLVED.

CODE: formats/shipsave.{h,cpp} — ZIP EOCD->central-dir->Memory raw-inflate
(zlib; ascend_core PUBLIC ZLIB::ZLIB, find_package(ZLIB REQUIRED) added),
anchor-vote findImageBase port, parseShipRecords full-window (cited fields
only, dead rows flagged not skipped, ring cidx x25, UNKNOWN gaps unmodelled).
PORT TRAP BANKED (S59 L5): build_anchors' zero law is strip() END-semantics —
anywhere-zero port gets 0 anchors (cost 3 debug rounds).
TESTS test_shipsave_t360.cpp x3: reader determinism + negative controls
(zero-filled member no vote; 4 KiB stub window-refused-not-clamped); durable
corpus-law pins; frozen-ring EXACT pin self-skipping past turn 1086.
run_tests 179/0 (176->+3). Engine behavior UNCHANGED (read-side only).

LEDGER: nothing closed strict-close (17/2 — parser artifacts + law
re-confirmations are not a row's named closer; OQ-019 stays user-gated per
t329, read-side model existing is noted in _wip_t360 S5, not the row).

## LANDED t367 — 2026-11-09 (D1-RULING APPLICATION: OQ-005 CLOSED STRICT-CLOSE,
## CORNER-ANCHOR GATE FALLBACK SHIPPED + PINNED, SHEET DISPOSITIONS FINAL;
## b2d049bbf5b5 PIN CONFIRMED; LEDGER 17/2 — FIRST CLOSE SINCE t292)

Sitting check FIRST: NEGATIVE — timeline 8,884,069,796 B, 400 KB tail-seek,
16/16 records turn 1086, newest 56/57/58.sav (ring rotation); r1_t85g_sitting
correctly not run; production :9 never signalled; game/ read-only throughout.

THE CLOSE (the row's OWN named closer, R13 satisfied): USER RULING 2026-11-09
12:45:01 via the ruling page (identical resubmit 12:45:31; applied ONCE),
cited VERBATIM in docs/OPEN-QUESTIONS.md: "D1 mouse k5/k6/k7 = keep as-is /
D1 batch 41 dispositions = accept all 41 / D1 A6 keep=True, A7 keep=True, A8
keep=True / D1 B-rows misidentified = none" + notes. OQ-005 status cell ->
CLOSED; ledger_audit --expect default retargeted to OQ-019,OQ-016 (the t292
precedent); STATE index RE-DERIVED (ledger_index_check OK, 17 closed/2 open —
first ledger movement since t292).

MEASURED (all file-level, zero capture; full detail docs/re/shp.md S28 +
docs/re/_wip_t367.md S4): (1) mouse.shp k5/k6/k7 signed bbox -> 78x47, row
walk 47/47 rows to span end 2062; planes BYTE-IDENTICAL md5
b2d049bbf5b571bfc4ea3b97db7a4fa7 — THE d1page pin b2d049bbf5b5 CONFIRMED
reproducible (an early scratch reference walk that failed to reproduce it had
a pixel-position bug; retracted in _wip S4.7, C++ walkRows was always right).
(2) GENERALISATION REFUTED: canonical dims == bbox-diff in 3 of 1,349 k>=1
records — a blanket signed-bbox dims read would corrupt 1,313 good records.
(3) BLAST RADIUS: naive bbox fallback rescues 17 records (14 of them vendor-
-provably-undrawable: cos_star k40..k51 zero headers, 1starmap k1, sg50expl
k9); the SHIPPED rule (canonical gate failed AND bbox >=2x2 AND (L<0||T<0)
AND walk completes) admits EXACTLY mouse k5/k6/k7 corpus-wide, measured.

CODE + PINS (rewrite): shp.cpp decode() corner-anchor gate fallback (the
canonical -1-gate path bit-identical for every record passing it; the Python
validator r1_shp_unifiedlaw.py DELIBERATELY unchanged — two-consumer law: it
models blit FUN_0005caac, the fallback models cursor geometry fn 0x61058);
NEW TEST(shp_corner_anchor_fallback_t367) = decode x3 + plane identity +
census 543287/nonzero 3666/fnv64 3ba44ef8c0c54974 pins + determinism +
NEGATIVE CONTROL (cos_star x12, sg50expl k9, 1starmap k1 stay rejected) + k4
canonical-size assert; shp_span_free_t197 clause (3) amended; parity floors
1513/187 -> 1516/188 (MEASURED: "208 libs, 1557 records, 1516 decode-pass,
188 clean libs"). run_tests 176 tests 0 failed.

SHEET ROUTE (per checklist, generator owns the files):
r1_t278_decision_sheet.py disposition() ADJUDICABLE -> KEEP-RULED, header/
footer rewritten to "ASK CLOSED", assertion re-keyed {40,1,3} KEEP-RULED,
re-run -> decision-sheet.md + index.txt regenerated (C27-C29 = RULED keep).
DECISIONS.md: D1 annotated APPLIED + status snapshot 17/2 (USER blocks
untouched, appended-not-rewritten).

USER TESTIMONY BANKED (new info, NOT a ledger row): B5-B29 ruling-page
renders are a top-part-offset chain ("Bn contains the top of Bn+1", "drawn
wrong here"); prime suspect = our dumper's X-class span-crossing paint
(shp.md S20.2/S21), NOT vendor bytes; no sub-investigation opened (the k4..k7
pin work does not touch r1_t182_pngdump.py's walk); revisit only if the
dumper is ever the task.

GATE_EXIT=0 (full gate incl 3c/3c-2 shp stages + run_tests + both audits);
game/ checksums intact. NEXT = t360 PER-SHIP SAVE PARSER VERBATIM.

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

## LANDED 2026-11-16 t407: ships screen (state 18) — fleet list law, pins, PASS witness
- ui/fleetlist.{h,cpp} (pure law): row per owned ship = campaign.fleet()
  (ships exist ONLY in transit in the model — named seam), vendor fn 0x50d12
  location law: orbiting "#143 Orbiting %s" / in-lane "#146 In Starlane to
  %s\nETA - %d %s"; header "#152 %s (%d %s, %d more allowed)"; allowance =
  systems+1-ships clamped>=0. Hit-map: arrows x619..638 (art rects, up y48-94
  down y425-476), trough inert, rows x7..605 top52 pitch106 (windows.txt
  STATSHIPLST rect 7,46-632,472).
- ui.cpp: kScreenFleet render+press branches, right-click deselect (selfplay
  law), scroll state, log lines "ui fleet select/deselect/scroll".
- static.txt GETTER INDEX LAW measured: marker-driven ("// N" comment ==
  entry N); naive line counter misaligns from ~90 (F10, fleet-screen.md).
- pins test_fleetlist_t407.cpp: suite 360->368, 0 failed.
- witness scripts/t407_fleetlist_witness.sh VERDICT PASS + native vision
  grade (header singular legs, cyan 2-line location, selection marker);
  timing law seed 5: ship in transit t278 only (F12).
- HONEST NEGATIVES: mutation campaign NOT proven (script cwd bug, F13 —
  t408 pre-flight); ship-name source stays PORT DEFAULT "Ship" (vendor name
  pool seam); SHIPDESSCREEN art + production census seams unchanged; NO OQ
  row closed (strict-close).
