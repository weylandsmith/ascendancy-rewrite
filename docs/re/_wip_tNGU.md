# _wip_tNGU — tNG-U PHASE-17 NEW GAME USER-GRADE PACKAGE [in progress, 2026-11-21]

Task = PACKAGE, not law probes (STATE.md NEXT ACTION tNG-U). Deliverables:
(1) scratchpad/NG-usergrade.png composite ours|refcap + per-region table;
(2) region -> law home (t423-newgame-law.md SS..) + verdict + witness map;
(3) D19 correction list marked closed/open with citing witness;
(4) harness polish if cheap; (5) NEXT -> WAIT-USER-GRADE-NG sentinel.

## HARNESS POLISH (item 4) LANDED
scripts/t441_screen_diff.py:175 chrome-recess-row7 fam_min 0.90 -> 0.89.
Rationale (measured last cycle, _wip_tNGB.md 't441 RUN'): same-binary/same-
state grabs 1s apart flip the row-7 fam share between 0.8994 and 0.9035
(spin-animation cosmos stars x304..306 at the row-7 chrome boundary; delta
max 191 at exactly 3 px). The threshold sat INSIDE the dither band. Freeze-
animation alternative rejected: one-line threshold change vs touching the
paint pump; the row still FAILS if the chrome recess itself drifts (the
family set is unchanged and the mean window 23.4+-3.0 still grades).

## REGION TABLE RUN (item 1) — GREEN
Canonical pair (G1 law, one pass): OURS = scripts/t412_newgame_shot.sh
-> /tmp/t412_shots/t412-newgame.png (log carries the law lines); VENDOR =
scratchpad/newgame-original.png (browser shot, load640 im[1:481,1:641]).
t441 --screen newgame: 18/18 PASS, exit 0, this session, post-polish build
tree (8dfcfb3 + row7 polish). Notable margins:
  racelist-row0 ours(109,109) vs vendor(111,111) — the 2px ring-record seam
  (documented t423 SS2 ring law tolerance); desc-planet ours 51x50 vs vendor
  53x51 (tNG-C SS14 tolerance +-2); playercolor-chiprow PASS (vendor
  (111,26) bbox taller = white frame rows — SS15).
Full table is in the composite footer + git commit message summary.

## LAW-HOME MAP (item 2) — regions x law x witness
(verified from t423-newgame-law.md section heads + STATE.md tNG-B c1..c3
LANDED blocks; every row cites its home section, no invented homes)

| region | law home | verdict | witness |
| racelist-row0/1/2 | SS2 wheel+ring dispatcher; SS9 ring==colour idx; SS12 shapeitem paint | ring record racering k<colour>, 1:1 native | t441 dims-vs-cited (this run) |
| racelist-row0-portrait / desc-portrait | SS12 cited stretch site 0x52834..0x52877 (0x8000 affine args); operative scale law = measured 2x (C2-F4) | PASS dims 100x100 both sides; scale-source seam NAMED not closed | t441 + t401 S8 zone census |
| desc-ring | SS6 racering record; kDescRingR=53 | PASS (107,106) both sides | t441 |
| desc-planet | SS14 smhome k<selected race row> native 1:1 anchor (406,217) | PASS 51x50 vs 53x51 | r1_tNGC_chip_witness.py planet zone + t441 |
| playercolor-chiprow | SS15 seven 15x25 chips, 4-slot pal ramp 0x53ee0, white frame on selected | PASS; chip count NEVER follows species wheel (SS17 literal-7 refutation) | r1_tNGC_chip_witness + t441 |
| chrome-* (9 regions) | t433 chrome law instance; tA2 F1 pixel-exact-vs-generator (no double layer) | PASS 9/9 | t441 bands + tA2 field-dump F1 |
| (wheel art zones — not t441 regions) | SS2/SS16 wheel-frame bijection k0..k12; B1 density straddle+regen (SS18 context); SS17 species arm | CLOSED c1/c2 | tNGB_density_witness + tNGB_species_witness (log-class, GREEN) |
| (atmosphere disc) | SS18 atmosphere arm word[+0xbb]++ wrap3, no state call | CLOSED c3 | tNGB4_begin_witness (apply(75,6,2)==live, GREEN) |
| (Begin panel starfield) | SS16b shrunk volume /5+5; B1 wheelGal follows wheel | CLOSED c1/c3 | t412 shot + 'newgame live' law line |

## D19 CORRECTION LEDGER (item 3) — defect-by-defect status
Source: DECISIONS.md D19 verbatim corrections list. Statuses below cite the
closing witness where one exists; OPEN items are the honest negative.

CLOSED (cited):
- double-chrome-layer complaint -> tA2 F1 MECHANICAL verdict: chromePage
  pixel-exact vs textureColourAt field everywhere it shows (top rows0..6
  mismatch n=0, left margin n=0, gutter 0.000); complaint re-read as texture
  character (short-run static vs vendor mineral), the named D19-deferred
  residue stays in chrome.md 4 / tA2 row. NOT a literal second painter.
- race portrait 4x family (species column) -> SS14 replaced the invented
  planets.shp mapping; desc-planet measured 51x50 vs vendor 53x51.
- wrong planet art per species -> SS14 index law smhome k<race row>.
- Player Color two-rows-solid -> SS15: ONE row SEVEN outlined emblem chips,
  white frame on selected; pins tngc_chip_ramp_law.
- atmosphere art drift + next-disc sliver -> wheel art follows the wheel
  bijection (SS16), three distinct panel arts witnessed; hostile k12 shipped
  (SS3). Disc-position drift: the c3 witness shows the arm is word-only
  (no state side effects); t441 desc regions PASS on the current build.
- Begin starfield tied to density -> SS16b shrunk volume + B1 wheelGal
  per-click rebuild; Begin starfield follows wheel (STATE c1 LANDED).
- green ring 1px vs thick beveled -> SS6 racering k0 record (t423 (e) FIXED).
- top bar 1-2px shorter -> t433/tA2 chrome bands: chrome-topbar-row0 +
  rows1-6 PASS geometry-vs-cited this run; the mineral-character nuance is
  the DEFERRED named residue (chrome.md 4), explicitly D19-deferred.
RE-SCOPED (not closed here, named home):
- starfield axis of rotation -> tGM-B (New Game screen has NO dials; axis
  law t416/t425 lives on the galaxy map — BLOCKED.md 2026-11-21 c3 entry).
OPEN / HONEST NEGATIVE:
- portrait scale-SOURCE (which record ds:[0x6fd98] binds; 16.16 param
  semantics) — static analysis exhausted (SS12), measured-2x operative.
- top-bar mineral texture nuance — D19-deferred by the user's own ruling.

## COMPOSITE BUILD (item 1) — LANDED + VERIFIED
scripts/tNGU_composite.py — side-by-side ours|vendor (both 640x480 @1x;
vendor 643x481 browser shot cropped PIL (1,1,641,481) == numpy
im[1:481,1:641] — first attempt (1,1,642,482) off-by-one CAUGHT by the
size assert, a trap worth remembering) + verdict strip that RE-RUNS t441 as
a subprocess and parses its lines, so image and harness can never disagree.
Verdict glyphs are text+shape (P/F in a box, fill luminance differs) per
the user's deuteranopia constraint. Output scratchpad/NG-usergrade.png
(1290x946), 18/18 PASS, exit 0. Vision-checked the artifact: strip legible,
screenshots aligned same-scale, no overlap; with --log passthrough (4th
arg = app.log) the strip carries real ours-dims "(109, 109) n=10411" (the
dimscheck law lines live ONLY in the app log — without --log the ours column
prints "None n=0" but verdicts are unaffected).

## PARK (item 5)
NEXT rewritten to WAIT-USER-GRADE-NG. Ledger: seam-package work, touches no
OQ row, open=[016,019] unchanged. Gate + ledger audit green this session.
