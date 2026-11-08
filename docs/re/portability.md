# portability.md — re-implementation reading order (t343)

The question this file answers: "could Ascendancy (The White Label, Watcom
i386 DOS) be re-implemented from these docs alone?" Reading order below is
dependency-ordered: each step consumes only what earlier steps define. Each
line names the LAW FILE and its CHECK (gate stage in scripts/gate.sh, or pin
TEST name in rewrite/tests/). This is a reading order, not a re-narration —
the laws live in docs/re/.

Read FIRST, before any domain:
- docs/re/retractions.md — dead readings; picking one up as fact silently
  mis-ports a whole subsystem.
- docs/re/loader.md §(pointer law pointers) + r1-savestate.md POINTER LAW —
  every address in every doc is base-0 payload-file offset (d = rv - P0);
  misreading the address space was the single biggest historical trap.
  Check: gate 3q (battery), gate 3h (loader model).
- artifacts/README.md — what ascend_restored.bin and functions_full.tsv are,
  their hex-size and overlapping-span pitfalls.

1. CONTAINER FORMATS (no game semantics needed)
   .cob TOC + extraction: docs/re/datafiles.md (grammar S3; every pool name
     has a referrer — the 06r .shp false-zero is refuted).
     Check: gate 3i2, test_cob.
   .shp shape libraries: docs/re/shp.md (record law S9 walk, header variants,
     zero-stream class) + shp-tokenize.md. Check: gate 3c, 3c-2, test_shp.
   .flc video: docs/re/flc.md (stock Autodesk chunks, golden-pinned).
     Check: gate 3o, test_flic (flc_logic_golden / flc_intro_golden).
   .fnt fonts: docs/re/fnt.md (1B/px law, slot==4+w*h, EOF tiling).
     Check: gate 3p, test_fnt.
   audio containers: docs/re/audio.md (VOC field map, voiceBand law, DEVICE
     rate 22050). Check: gate 3e, test_audio (voice-band law pin).
   text: docs/re/text.md (CP437). Check: gate 3g.

2. STATIC TABLES (loaded before any rule runs)
   table inventory + .bin stride-24: docs/re/tables.md. Check: gate 3b.
   planitem records (stride 0x28, COST u16@+8 — the +2 reading is retracted):
     docs/re/economy.md §4 (OQ-014 laws: loader FUN_00037fc0, REQUIRES law,
     count triple 22/9, size-class cells {7,11,23,45,73}).
     Check: TEST(oq014_*) x3, gate 3j.
   restree (stride 75 live table, 66 main rows, runtime cost = file_cost x
     (2row-20) clamp 65000; NO stride-45 table): docs/re/research.md 6.
     Check: gate 3i, test_research, scripts/r1_restree_law.py.
   per-race parameters: docs/re/ai-data.md (21 raceNN.dip, DIPVALUES key).
     Check: gate 3d.
   gizmos: docs/re/gizmos.md (76 gizmos, sentinel counts). Check: gate 3j.
   star table + orbit law (stride 96, name-anchored; +0x5a = system SLOTS,
   not colonised count — retracted reading #9): docs/re/r1-savestate.md
   "STAR TABLE + ORBIT LAWS". Check: gate 3s (capture-gated).

3. WORLD GENERATION (consumes planitem + restree tables)
   docs/re/mapgen.md (density cycle 50/75/100/1xx, shell radii fixed at every
   size, home placement, barren draw: rng 0..32767 LCG — the 0..99 draft is
   retracted #5; weight-row index word+0x16 — NOT a homeworld marker, #7).
   Check: test_mapgen (14), TEST(campaign_home_placement_law_t40),
   TEST(campaign_pop_band_law_t199).

4. ECONOMY / PER-TURN LOOP (consumes world + planitems)
   docs/re/income-law.md — the master law file: channel laws, build queue
   (pendingItem/buildAcc), pop-cap clamp law (+0x88 slot array, CB INCLUDED,
   #1), governor accrual (33/34/35 DO occur in production, #21), seed law
   nb//3+5, S14 correction block. Companion: docs/re/economy.md.
   Turn order + victory check placement: docs/re/turnloop.md.
   Check: TEST(campaign_build_queue_law_oq016), TEST(campaign_pop_cap_seed_law_oq016),
   TEST(campaign_governor_law_t45), TEST(campaign_used_pop_item_sum_t202b),
   gate 3l (seeded campaign reaches VICTORY).

5. MAP/MOVEMENT + COMBAT (consumes ships + gizmos + economy)
   ship design records: docs/re/ships.md (base-offset convention +0x30 — the
   t47 labels are retracted #2; drive stat sum [ship+0x10]; step is ONE per
   turn boundary #3; visibility law S23).
   combat application: docs/re/combat.md S2d..S2j (firing order = stored
   gizmo-slot order; damage = design[+0x52]/[+0x4a], NO hit roll; two-layer
   absorb; commit law mode==1 at 0x25560/0x25570, trap class per #15).
   Check: TEST(campaign_combat_law_oq010), TEST(campaign_visibility_law_oq026_t195),
   TEST(campaign_built_cell_rule_g_t43).

6. DIPLOMACY + ABILITIES (consumes relation state)
   docs/re/diplomacy.md (state enum 2=WAR/1=PEACE/3=ALLIANCE; accept
   threshold comparator 0x4562f/0x45641) + docs/re/abilities.md (21 abilities,
   14 charged/7 passive, cadence word WORD[0x6780+2*ability]).
   Check: test_diplomacy, TEST(campaign_diponattack_t204), gate 3m
   (SA_HealShips fires by t65), OQ-020 pins.

7. VICTORY / SCORE PRESENTATION (the last layer)
   docs/re/score.md (S20 comparator law V >= floor(2T/3)+1, CLOSED t292 by
   live presenter witness; end-*.txt grammar; rank table).
   Check: TEST(score_*) t284 set, test_control_t291 (x4 mutation-verified),
   gate 3l + endtext_probe.

8. AI (behaviour over all of the above — read LAST, port optionally)
   docs/re/aicode.md (+ ai-dossier.md; the t212 alias/producer claims are
   retracted #11 — the real score producer is watchpoint-class, witnessed
   t283). Check: gate stages 3n2 audits, TEST(campaign_research_picker_law_oq016).

## What is NOT portably known (as of t343)
OPEN ledger rows (strict-close; docs/OPEN-QUESTIONS.md):
- OQ-005 shp: in-record DIMS slot-location dispute (mouse k5/k6/k7 have real
  art, EXACT-H 77/77; canonical dims slot reads zero). Porting: ship the
  rec+0 dims pair reading, flag the dispute.
- OQ-016: residues EXHAUSTED t342; what remains is USER adjudication D2/D3
  (accept cited-dead legs / close form), not measurement.
- OQ-019: per-ship design-model residues (per-ship select + destination
  widget widget-wiring; several sub-legs cited-dead) + user ruling pending.
- OQ-012/OQ-025 closed rows carry documented scenario-template residues
  (preset-row worlds via FUN_00037fc0 are corpus residuals, not replay noise).
CAPTURE-LIMITED class (law cited in-image, no runtime witness reachable on
this box's stock build; do not re-hunt without a debugger-enabled dosbox-x —
see retractions #22): zero-stream combat ladder slots (t323 amendment),
AI per-planet pick minutiae (t342 residue-(5) scope note), static star base
0x13bc5 on heap-moved saves (garbage, not claimed).
BOX-LIMITED gates: a fresh clone legitimately skips the capture/venv stages
(pointer-law 3q, star-table 3s, attribution 3r need work/r1 captures;
loader-model probes need the venv payload tsv). Everything else must run and
pass on a first clone run — the stage-order bug that hid this is fixed t343
(gate.sh "3-pre"); docs/re/portability.md's rule: a skip note must name the
ACTUAL missing prerequisite.
