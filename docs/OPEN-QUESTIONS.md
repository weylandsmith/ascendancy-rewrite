# OPEN QUESTIONS — live closeout ledger (v2, strict-close)

Statuses: open | CLOSED. Nothing else. A question closes ONLY with cited
evidence (Ghidra address / extracted-file offset / pointer-law guest-phys
measurement from a named capture) + the rewrite site upgraded + docs/re/
updated + a gate or test pin. FINAL-DEFAULT is not closing (docs/GOAL.txt).
v1 full evidence text for every row: archive/ralph-v1/OPEN-QUESTIONS.md.
v2 FULL LEDGER (every CLOSED row's complete evidence text, archived
2026-11-03 when this file was slimmed to open rows + pointers):
archive/state-v2-full/2026-11-03/OPEN-QUESTIONS.md (md5 e897be73e0fd4b06cb51aa0881c0ff5d).
Full per-iteration working notes for ALL of v2: archive/state-v2-full/2026-11-03/wip/.
Do-not-retry prohibitions: docs/REFUTED-ROUTES.md.

Format: ID | area | question | status | what closes it (in-hand route)

OQ-005 | shp | .shp shape-library codec: in-record DIMS location for the
80-record residual class (container CLOSED 208/208; grammar CLOSED t61-t69)
| open | CLOSED PORTION (full evidence: archive 2026-11-03 + shp.md):
control-byte grammar verbatim FUN_0005caac 0x5cca3..0x5ce77 (shp.md S9); blit
5-arg law + stream=PAY+(tsz|u64dir[k-1])+0x18 (S12/S14); runtime table uniform
delta{sel0:8,k>=1:24} 4 libs x 43 selectors live-RAM (S17 r1_shp_ramtable.py);
corpus MEASURED 208 libs/1557 recs/1484 decode-pass; dims-gate + span-bound
validator artifacts corrected t182/t197 (shp.md S18/S21 — do NOT re-litigate
those 31 records, they decode); cos_star selector law t200 (SEL=4*[star+0]+
cls ladder; k40..k51 addressable-empty, k52..k54 unreachable); pop-slot library
= 17np.shp (t254). CODE SITE: rewrite/src/formats/shp.{h,cpp} ShapeLibrary
(container laws, blit-faithful clamp, 4096 dims cap) + tests/test_shp.cpp.
RESIDUE (80 records/31 files, decomposed t278 shp.md S24.2): 25 zero-byte
ladder slots + 12 cos_star k40..k51 + 4 invalid-dims (mouse k6/k7, 1starmap k1,
sg50expl k9) + 2 t197 demotions (mouse k5, sg64expl k0) + 3cfgnew k12 (vendor
EOF truncation). W3 route EXECUTED NEGATIVE (all 75 decoder sites read dims
from record header only; docs/REFUTED-ROUTES). Closure class = human-verifiable
drawn frame (R13 blocks self-grading) OR user ruling on the shipped decision
sheet work/r1/shp_png/decision-sheet.md (88 rows, docs/DECISIONS.md D1) OR a
vendor draw-capture session. Blind sweeps FORBIDDEN (R2). Default in force:
decode per S16 V/A law, residual skip-and-warn in tooling only (rewrite renders
its own vector art; codec = validation asset). | open

OQ-016 | loop | campaign per-turn constants: income formula, pop growth
curve/cap, starting items, build order, expansion cadence, home placement
| open | CLOSED SUB-LAWS (full evidence + retraction history: archive
2026-11-03 + docs/re/income-law.md): income channel law 138/139 battery (pin
campaign_channel_law_oq016); POP GROWTH pop==+0x42 UPOP dots, counter-50,
colonise :=2 (verified chase capture r1deep-20261007-224831); BUILD QUEUE + AI
SELECTOR LAW (queue 1/planet, acc+=stored IND 0x39005, complete acc>=COST
0x390a3, selector queue-empty-only caller 0x3ead6, COST/IND>=70 abort; rewrite
buildPhase pendingItem/buildAcc + pin campaign_build_queue_law_oq016); POP-CAP
recalc +0x4a = clamp(0..100, +0x55 + MPOP sum ALL active slots) 72066/72066
(income-law T33 — t31/t32 '+2 residual' was the missing +0x88 harness artefact,
RETRACTED); +0x55 seed law nb//3+5 @0x37f84..0x37f9e + pin
campaign_pop_cap_seed_law_oq016; TERRAIN GENERATION LAW end-to-end (rng%5 size,
rng%11 row, draw chain @0x37eb7..0x37ee0, T36); terrain-mutation via item-36 +
world-gen |8 rock only (t29b 40k-sample census); HOME JOIN MEASURED t270
(DWORD[0x12e1d+race*0x1ee] == star base NAME-0x1C; trust turn>=1 only, turn-0 =
template residue) + home placement RUN-LOCAL (11 distinct sets/11 lineages;
rewrite pickHomeStars was a documented MISMATCH (deterministic max-min BFS) —
SUPERSEDED t295 by the cited HOME-STAR DRAW LAW, see S-T295 below);
pending-build reserves its
slot (t271: byte1:=item id, word2 bit0 CLEAR — pending IS ring-observable).
ATTRIBUTION FIXES t273 (binding for all future mining): owner INDEX byte +0x56
(NOT handle u16+0x54); stale-echo pairs mint phantom deltas; the t251 mine is
VOID on both bugs; damage-vs-non-at-war-owner STILL ZERO corpus-wide.
RESIDUE (each with a route): (1) Phase Bomb nuke law — capture-gated, BLOCKED
section + one-run recipe; (2) setup-time home DRAW law — CLOSED MEASURED
2026-11-04 t295: uniform rejection draw per race in race order, k=draw%T,
store row_r+0xd @0x22edd, claim gate 0x22ee0 (FUN_00022ce4 0x22eb4..0x22f55
full disasm + census scripts/r295_home_draw.py: equal-marker 30/30 turn<=2,
distinct 36/36, index chi2=31.0 df=49 crit 74.92); docs/re/income-law.md
S-T295 + docs/re/_wip_t295.md; rewrite pickHomeStars upgraded, stream
interleave vs world-gen stays UNMEASURED (isolated homeLcg_, distribution
law); (3) word[+0x16] template source — CLOSED MEASURED 2026-11-04 t294:
FILE TABLE, planitem.txt ASCII block after '#' (scalar->DS:0x66e4 @0x3802c,
11x4 weights->0x744f4 row-major @0x3801e..0x38067, grid B->0x7445c, grid C
->0x744a8); EXE-constant hypothesis dead two ways (0x744f4 past the
initialised data segment; image-wide SIB-aware store census = ONE writer,
the loader @0x3805f); file == banked runtime == live RAM 58/59/60.sav; the
INDEX itself stays the rng%11 draw @0x23a97; rewrite upgraded
(TerrainTables+loadTerrainTables economy.{h,cpp}, cfg.terrain consumed
campaign.cpp, main.cpp injects; pins tests/test_terrain_t294.cpp x5,
mutation-verified; income-law.md t294 block); (4) per-slot shield-byte
consumer (OQ-019 family); (5) human build-order minutiae 0.4% samples;
item-35/35 completion branches = MEASURED zero-witness + AI-unreachable
(REFUTED t271, re-open conditions there).
| open

OQ-019 | ships | per-ship design model (hull+gizmo inventory), sugar-cube->
hop scale, vendor cost hack, Orbital Docks effect
| open | CLOSED PORTION (full evidence: archive 2026-11-03 + docs/re/ships.md):
gizmo record law FUN_00049074 stride 0x6a x 76 == file census, RESREQ bitmask
+0x33, cat-switch copies Level->+0x52/56/5e/62, generator Power->+0x66 (§6);
cost hack CLOSED t16/§9 (sole gizmo-record write = loader parse 0x491b5; the
inherited +0x46-writers pointer is STALE — do NOT re-census); inventory law
CLOSED t46 (landed ship = active item-23 ring row, §10); Orbital Docks readers
§12-13 (upkeep/propulsion/range/step/fuel; executor has NO drive->distance
term); BUDGETS CITED t101: MOVES=[ship+0x94] refilled each resolver call to
drive stat SUM [ship+0x10] (FUN_0004a658, live 32/35), POWER=[ship+0x88];
SCALE MEASURED t183 (ships.md §17): FUN_00049f54 walks min(d/160, MOVES) sugar
units per resolver call, steps=max(1,round(walk)) capped by fuel; const pool
live 20/20 (1/160@0x25ff, 32.0, 5.0, grid quantizer DAT_000895dc=32);
round-robin = min-fuel one-ship-per-call inside turn loop FUN_00024f24
 (0x12e10 zero obj0 writers — no autonomous day-tick); LANE-STEP
LAW two corpora zero violations (|dx| == step0 or step0/3, step0=u16[+0x8]+
u16[+0xc]; /3 lane-scoped) + TURN-ATOMICITY (same-turn st5 dx EXACTLY 0,
17,595 pairs — t187 '4.67=3 substeps' DEAD, 4.6667 is one step); st4 = DWELL
state, in-system march resolves inside one turn boundary, invisible at 10 s
ring cadence (t265, 21 runs d=0.00 — corpus mining class CLOSED t49/t58/t265,
scripted capture ONLY); MAGNETRON runtime witness ZERO x3 (t265 off-grid
instrument P(false neg)<0.1%, t273, t285) — use-site stays static-cited
(gizhelp.txt:1173-1181 verbatim; kind==5 handler 0x21f58).
RESIDUE: (1) sugar-cube per-turn clamp/arrival granularity — t293 SPENT the
3-launch scripted-capture budget, NEGATIVE (order never issued: orbital-grid
dot-clicks navigate, never select; full autopsy docs/re/_wip_t293.md +
ships.md t293 block; drive background=true, 420 s foreground cap kills a full
session). t296 CLOSED THE SELECTION SUB-PROBLEM STATICALLY (ships.md S24 +
_wip_t296 S1..S9, every block re-dumped verbatim): four cited gates — clip
exists iff [ship+0x58]==4 (builder 0x1d6bb), clip kind==2 (0x1b6fc/0x1b9f6),
owner [ship+0x54]>>16==ds:0x7458e (0x1b709/0x1ba16), MOVES [ship+0x88]>0
(0x1b716/0x1ba2c) -> [batwin+0xb7]:=2 (0x1b71f/0x1ba39); the dots are kind-3
PLANET clips so G2 always skipped, and in mode 2 a plain map click CLEARS
selection (0x1b114). REMAINING UNKNOWN = the destination-entry widget that
posts msg 0x50 (ds:0x43508 := [sel+0x42+ebx*4] @0x1b5dd/0x1b5e6 + command-ring
0x56ad4 code 0x11): no widget-side poster outside the batmode family in the
image-wide imm census; (2) per-ship build/redesign path =
BUILD DECISION not RE unknown (t256c census 62,762 rows, AI dossier row 16
GAP->BOUNDARY; docs/DECISIONS.md D3); (3) magnetron witnessed use (scriptable
via t289 drive class). | open
CLOSED (slimmed 2026-11-03: full evidence text of every row below lives in
archive/state-v2-full/2026-11-03/OPEN-QUESTIONS.md and the cited law file.
DO NOT re-open, re-derive, or re-census any of these from a fresh session —
the law-file citation is the working handle; re-treading is iteration waste.
Format identical to open rows: ID | area | question | CLOSED date+task | evidence; code site.)
OQ-003 | gam | .gam packed-entropy residue | CLOSED 2026-10-13 t181 | measured three-class disclaim scripts/r1_t181_banddiff.py (band boot-vs-played 432/2048 vs header/S-table 87-100%); docs/re/savegame.md section t181; rewrite unchanged (fresh-start-only)
OQ-004 | tables | which tables load; .cob container grammar | CLOSED 2026-10-06 06s | u32 N + N x 50B names + N x u32 offsets, ascend00 54/54 md5; RAM name table 0x250c1c 3/3 captures; pool-relative immediate law 337 sites; docs/re/datafiles.md S3-S5 (gate 3i2 scripts/cob_probe.py); no rewrite delta (reads extracted dir directly)
OQ-006 | audio | headerless sample rate | CLOSED 2026-10-07 | DEVICE rate 22050 measured (open chain PUSH 0x5622 @0x4f690 -> setter 0x6e000 stores [obj+0x3c]; default 11025 always overwritten); docs/re/audio.md 3.1; pin audio_open_rate_measured_oq006; channels documented default mono (no vendor field)
OQ-010 | rules | combat damage application | CLOSED 2026-10-14 t89 | firing order 0x4a5c1, damage design[+0x52]/[+0x4a] no hit roll (measured-negative), shield-then-hull absorb, death 0x49d2c, commit mode==1 0x25560/0x25570; docs/re/combat.md S2d..S2j; rewrite campaign.cpp attackScore/defenseScore/combatPhase + pin campaign_combat_law_oq010
OQ-012 | mapgen | size options + pps + shell position | CLOSED (a 2026-10-12, b-d 06o/06p/06q/06k) | density cycle 50/75/100/15/25; pps U{1..5}; shell position law; docs/re/mapgen.md; rewrite --stars knob + upgraded shells (rewrite site mapgen.cpp)
OQ-013 | tables | restree semantics | CLOSED 2026-10-06 | live = 66 main rows; stride 75 record map; COST LAW runtime = file_cost x (row-20) clamp 65000 reproduced 66/66 (0x4691d..0x46a15); docs/re/research.md 6; rewrite Tech::runtimeCost + 2 pinned tests
OQ-014 | tables | planitem unknowns | CLOSED 2026-10-06 | loader FUN_00037fc0 + checker FUN_0003830c; stride 0x28 record map 39/39 byte-exact; REQUIRES law avail iff req==0xFF || (req<66 && owned) -> 254 DEAD; grid C row sums = size-class cells 2650/2650; docs/re/economy.md section 4; 3 pin tests (gate 3l Trucking grep); rewrite requiresAvailable
OQ-015 | dip | DA_ template order + %token | CLOSED 2026-10-08 t12-t14 | chooser FUN_00044a44 == ACTIONS pool idx; %token census 22/22 == {%m,%y,%s,%t}; pins dip_action_chooser_law_oq015_t12/d_t13/d_t14; rewrite unchanged (trade gates -> engine build, docs/PLAN.md A7)
OQ-018 | audio | soundfx.txt pairs + VOC + theme map | CLOSED 2026-10-07 | voiceBand law 327/328 spans == disk sizes; VOC u16@25==0x0911 15/15; race->theme REFUTED (DAT_00010ba0 sole writer 0x21309); docs/re/audio.md 2.1; rewrite/src/formats/voc.cpp pins + test_audio_voice_band_law_oq018
OQ-020 | abilities | charge days for 14 charged SA_ | CLOSED 2026-10-15 t100 | cadence word WORD[0x6780+2*ability] == FILE 0x89330 zero writers (5:60 6:100 7:62 8:77 9:90 10:150 11:70 12:63 13:66 14:72 16:92 17:100 19:89 20:68); wired kCad[21] in rewrite/src/game/species.cpp abilityChargeTurns + COUNT-UP law; verify scripts/r1_t100_cad_verify.py
OQ-021 | victory | end-ctrl threshold | CLOSED 2026-11-03 t292 | LIVE presenter witness: BPLM sentinel 0028A2FB mid-pass stop 0x24274, evaluator FUN_00024a34, sel 0->5 DAT_00043510 @0x24d9f + rank 42 DAT_0004350c @0x24dab, end-ctrl.txt verbatim on screen; comparator V >= floor(2T/3)+1 MEASURED; run work/r1/t290-poke-a40-20261103-165405; docs/re/score.md S18-S20; rewrite arm campaign.cpp:2157 upgraded t291 + pins test_control_t291.cpp
OQ-022 | audio | music span-vs-check contradiction | CLOSED 2026-10-07 t8 | guard @0x59984 precedes checked call; DS:0xa200c all-zeros 10/10 saves; engine INACTIVE in captured states; docs/re/audio.md 3.4; no rewrite dependency
OQ-023 | dip | relation-state enum semantics | CLOSED 2026-10-29 t189b | state-3 ALLIANCE event OBSERVED @t1335 (cell0i=celli0=3, att +10/+10, 68 rows, scripts/r1_t188_state3_arbiter.py RC=0); flip 631>570 = static law 0x4562f/0x45641; enum 2=WAR/1=PEACE/3=ALLIANCE; docs/re/diplomacy.md 13+16; rewrite unchanged diplomacy.cpp:227/:244; engine residual -> PLAN.md A7
OQ-024 | rules | planet GOVERNOR assignment | CLOSED 2026-10-09 t45 | @0x38df0 branch pinned verbatim (item 33 -> PROS+=IND>>2, 34 -> RES+=IND>>2); [0x743b9]>>0x18 == UPOP(35) 32/32 saves; activator @0x38b26 sole trigger 0/2810; rewrite PlanetState::governor + pin campaign_governor_law_t45; docs/re/economy.md
OQ-025 | mapgen | non-default-density position law | CLOSED 2026-10-15 t79 | shell radii fixed at every size, populations halving law (T//2+1 then halve), reproduces T=50 battery exactly; docs/re/mapgen.md; rewrite shellRadiiFor replaces i%50 wrap
OQ-026 | visibility | fogged lane/star gating | CLOSED 2026-10-29 t195 | implement+pin at the row's own bar: viewerMaskFor == FUN_00021a84 verbatim, filter == 0x2914e AND, shareLaneVision == FUN_00046354 shape; rewrite laneVis_/starLaneVis_/starSelVis_ (obj +0x16/+0x17 twins); pin campaign_visibility_law_oq026_t195; docs/re/ships.md S23 L10

- > OQ-001 .cob offsets -> formats/cob.h reader (format block cites this ledger + FINDINGS P1a)
- > OQ-002 FLIC codec -> formats/flic.h (cites docs/re/flc.md)
- > OQ-007 CP437 -> decode sites game/species.cpp, game/research.cpp, game/starstat.cpp, game/economy.cpp, game/diplomacy.cpp
- > OQ-008 loader control-flow model -> ANALYSIS-ONLY (rewrite is fresh-start-only; no loader in rewrite; spec docs/re/loader.md)
- > OQ-009 AI data side -> ANALYSIS-ONLY input to the W-B-gated diplomacy/AI build (docs/re/ai-data.md; nothing shipped reads it yet)
- > OQ-011 POINTER LAW (scripts/r1_pointer_law.py 12/12 slots, gate 3q) -> measurement instrument only, cited by capture scripts + campaign.cpp:593
- > OQ-017 .fnt codec + UI wiring -> formats/fnt.h (cites docs/re/fnt.md) + ui/ui.cpp wiring
