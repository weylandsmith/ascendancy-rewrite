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
updated: 2026-11-16T15:30
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
    - "OQ-027 audio intro TUNEID index base + per-button vendor SFX id
      (OPENED t388b 2026-11-14): tune table heap-relative (FUN_00074a88
      stores [handle+0x8868]) so the 0/1-base of subtitle.txt TUNEID 6/7 is
      not statically decidable — port law 1-based (6=intro00, 7=intro01,
      sizes-fit-only witness); closes on user hearing or pointer-law capture
      of the heap table. Per-button SFX ids come from runtime control fields
      +0x1bcc/+0x1bce (windows.txt SOUNDCHANNEL census {0 x118, -0 x1} = no
      id); port click names stay documented choices. law docs/re/audio.md §6"

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

NEXT t416 per queue row t416 below (ROTATION AXIS WIRING, phase 15 per
the USER'S ROUND-3 RULING D15). ORDERING: t415 (race intro framing+art)
LANDED 2026-11-16 (docs/re/_wip_t415.md F1-F7; live witness graded with
own vision). Remaining rows t416-t419 are independent of each other;
t416 is next because it is the smallest measured-code change (a dial->
axis table in the map view), and t419 (Esc trap) benefits from being
last of the three UI rows so its per-screen regression sweep sees all
phase-15 screen changes. D13 self-grade law CONTINUES.
SHORTHAND FACT: public SHAs never exist locally (history-rewritten
export); verify pushes by ls-remote only. Sentinel history below.
CARRIED STATE: phase-13/14 pushed (remote main == c178a43c1f71 at t413;
t414+ are LOCAL commits — t420 owns the mandatory push). H1 (sign-compare
warnings) DONE t412-era. H2 (bottom-wheel clipping) CLOSED by t414's
panel clipRect. Remaining carried seams: (H3) runtime race-colour bytes
census (live-RAM during intro) — t415 RE-SHARPENED it: the vendor intro
screenshot shows Minions ink GREEN pal[19] (racebyte 0) while the static
dump byte is 16 (red pal[83]); the ink LAW is verified, the runtime INPUT
is the open question; a live-RAM census of 0x12e18+specnum*494 during a
vendor intro would close it. Vendor intro draw immediates now MAPPED
(t415). Intro scroll driver seam stays (truncation printed once).
(OQ-027 closes ONLY on the user's pasted `audio:` line + verdict;
OQ-016/OQ-019 stay DEFERRED — do NOT re-ask.)

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
                  | consoles. LIVE: click any star; TOGGRID toggles grid.
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
Standing context: OQ-016/OQ-019 acceptance DEFERRED (rows stay OPEN; do
NOT re-ask, do NOT apply the t329 S4 draft); user saves 887/1086/1253
PROTECTED (~/ascendancy-saves-protected/, law: raw .SAV u32@0 = game-day).
A session woken by a DECISIONS.md edit or a *ruling*/*reply* file: read
docs/DECISIONS.md, apply what the ruling says, close rows per strict-close,
then author the next queue or re-park a WAIT sentinel.
QUEUE: EMPTY — phases 10-14 fully drained (t385..t413 all LANDED; per-row
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
