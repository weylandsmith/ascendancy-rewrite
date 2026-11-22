# tNG-F — New Game fix cycle (D20 six defects) [WIP]
Session 2026-11-21/22. Trigger check FIRST (done): DECISIONS.md last USER:
line = D20 (no new reply); ring 20/20 turn=1086 min=max (scripts/t368_ring_turn.py,
feed live: watch pid 1182171, dosbox pid 1182156 alive 1d12h) => NO new sitting,
r1_t85g_sitting.py NOT run (selfplay ring, not play). Assignment = STATE.md
tNG-F F1..F6 in order.

## F1 STARFIELD COLOR + VOLUME
State of the port (read title.cpp:488-595): preview = splitmix->cosmosHash
circle r300 + depth 1000+-300 (cited vendor law F4/F8 _wip_t423), cos_star
sprite rec = 4*0+cls (K=0 NAMED SEAM), rect clip kNewgameCosmosRect{8,8,492,372},
black-fill first. D20 defects: (a) all one colour (K=0 seam => k1..k3 blue
family only); (b) not contained in a volumetric sphere.

### F1-M1 refcap colour census + radial profile (scripts/tNGF_star_census.py)
Run on scratchpad/newgame-original.png vs /tmp/t412_shots/t412-newgame.png
(post-tNGC3 build, 22:39) inside the field rect. NOTE the rect includes the
summary-text zone (rows ~318+ x110..290) which pollutes greys — the
discriminating facts survive:
  VENDOR: warm 10%, blue 16%, green 28%, white 19%, dim 28% (3271 star px);
          radial hist peaks r108..162, hard tail drop >190; corner-px 82.
  OURS:   warm 0%,  blue 34%, green 24%, white 27% (2488 px);
          radial r50/r90 = 148/188 (vendor 152/189) — containment profile
          ALREADY MATCHES (ring annulus, both sides); corner-px 0.
=> D20 "all one colour" CONFIRMED: zero warm stars ours. Root cause is the
   K=0 named seam: sprite rec = 4*K+cls with K=0 -> cos_star k1..k3 only
   (blue family). Vendor field = the FULLY-DIVERSE 100-star galaxy
   (FUN_00022878 type classes via 13-entry weight table DAT_000063aa), so
   its stars span several cos_star colour families. The radial/volume
   profile is NOT the defect (numbers above) — the user's "not contained
   in a volumetric sphere" reads from the Begin panel (F4) + the flat
   single-colour look of the big field.
## F1-M2 static hunt for the preview colour selector
Ghidra: stride-0xd preview table DAT_0003067e has EXACTLY ONE referrer
(FUN_00022728 writes it; 0x227be/0x22834) — the D19 "no static consumer of
the base" negative RE-CONFIRMED. The big field is painted by the shared
COSMOSWnd display-node chain (the live galaxy), NOT the preview table.
## F1-M3 cos_star COLOUR CENSUS (file-measured, decoded k0..k39 game.pal 6-bit)
!!! CORRECTION same session: the first census used a (count,val)-pair
decoder — WRONG grammar. Corrected S9 walk (C odd = literal C>>1 bytes,
C even = run C>>1 of next byte, 0 = row-end); census below is the fixed one:
  SEL=4K+cls grid, every family a 4-step bright ramp:
  K0 BLUE (12,32,48)->(0,20,80)/(0,48,93)->(20,52,117)/(20,93,141)->(36,117,206)/(52,182,234)
  K1 (60,40,16)/(97,36,24) brown -> (133,32,64)/(186,36,56) pink
  K2 RED (72,0,0)/(97,0,0)->(121,0,0)->(153,4,0)/(190,44,16)
  K3 ORANGE (80,16,0)->(121,0,0)->(157,72,4)->(194,97,4)/(255,133,8)
  K4 navy->tan; K5 tan (93,64,32)->(157,109,56); K6 = K1 family; K7 red/pink
  K8..K12 browns/reds/tans; k40..k51 dims-zero (types 10..12 paint NOTHING —
  cited t200 law); k52..k54 unaddressable.
  => THE VENDOR FIELD'S MULTI-COLOUR IS THE STAR TYPE K (13 starstat types),
   sprite = the family ramp position cls. Our K=0 seam => all-blue. FIX:
   preview star i takes the TYPE of wheelGal star i (count law already ties
   N == wheelGal->stars.size() since tNG-B B1) and blits SEL=4*type+cls;
   dims-zero cells draw nothing. Named-seam note: the stride-0xd preview
   records carry no type byte (t423 F8) — runtime paint records DO carry a
   dword[+0] type (0x527d1 shl 2 feeds SEL); the port maps by galaxy index.
## F1-M4 UNIFIED-FIELD HYPOTHESIS REFUTED (scripts/tNGF_field_match.py)
Test: is the big field the SAME star set as the Begin panel (same painter walk
0x526b4 pos law)? Chroma-filtered star px, translation-aligned nearest match:
2% (46/1904). => big field and Begin panel show DIFFERENT star sets in the
vendor refcap. The preview table (circle r300 law) feeds the big field, the
galaxy walk (/5+5 law) feeds the panel — consistent with t423 F8/F9 readings.
Static consumer of DAT_0003067e: still ZERO outside the generator (byte-pass
over ascend_restored.bin for imm 0x3067e/0x306f2/0x306fd: zero hits — the
runtime base is 0x12e10-relative via the manager, so the static imm hunt is
inconclusive BY CONSTRUCTION; the D19 heap-relative negative stands).
## F2 BLACK BACKING MEASUREMENT (scripts/tNGF_header_arrow_geom.py,
## tNGF_backing_probe.py + vision 2x crop)
Vendor "Player Species" header zone (x494..633, rows 1..37): PURE BLACK
(0,0,0) box behind the white title — 32% of the zone is lum<12 neutral
black; the black dominates rows 26..37 (0.86-0.90 fraction) and the text
sits in black at rows 9..37. OURS: 0% black (header band mean (85,110,112)
= chrome texture shows through). The RACELIST well itself (rows 45..372,
SHAPEFRAME 7 -> 7racesel.shp k0..k7 DECODED = solid 158x30 pal242
(12,32,48) navy) already matches BOTH sides (gap px (12,32,48) exact).
Bottom-panel title zones (Star Density/Species/Atmosphere/Player Color):
NO black box (0.0) — the black box is SPECIFIC to the Player Species
header. => F2 FIX: paint pure black rect behind the Player Species title
before drawing the text. Vendor text rows 15..24 centred; box = header
zone rows ~8..37 x 500..633 (measured dark-fraction map; exact rect pinned
below after code shot). NOT windows.txt-driven (NEWGAMEWND has no child
for the header — the state-3 painter draws it; per F1-M2 painter family).
## F3 SCROLL ARROW MEASUREMENT (refcap x617..631)
Vendor UP arrow: a SMALL light triangle inside a 15x14 cell with dark
edges (# columns at x617/x631 = the cell frame), triangle apex rows 57,
base rows 61..62 — colours from the cyan family (190,255,255) highlight +
(123,171,177)/(168,227,229) body — i.e. a ~7px wide glyph in a groove,
NOT a filled blue box. DOWN mirror at y358..372. Cell x617..631 sits over
the RACELIST right edge (RACELIST x1=632). Ours currently paints blue
boxes (the D20 complaint). FIX per measurement: 1px-frame cell + light
triangle glyph, cyan-family colours measured above.
## F4/F5 BEGIN PANEL MEASUREMENTS (scripts/tNGF_begin_probe.py + vision 4x)
(a) VENDOR Begin starfield = MULTI-COLOUR (type-K families, same cos_star
    ramp as the big field) scattered in a LOOSE ROUND CLUSTER in the panel
    left area: vision-verified round blob with generous black margins, NOT
    a rect-fill; bright sprites 2-4 px (the /5+5 law, larger sprites than
    1px). Navy-well px (12,32,48 sat 36) polluted the first sat>25 census —
    star px = sat>60: cluster spans ~x505..565 y388..455 => clip circle
    ~centre (535,421) r~33 (inferred from bbox; honest named value).
    FIX: keep the cited /5+5 position law + add a CIRCLE clip; apply the
    SAME type-K colour law as F1 (vendor stars ARE multi-coloured here).
(b) PORTRAIT: vendor content (non-green, lum>60, r<23 of (600,417.5)) =
    bbox x578..622 y395..440 centre (600.2,417.7); OURS (post-tNGC3)
    bbox x578..622 y395..440 centre (599.8,418.0) — ALREADY MATCHES to
    0.2 px, and the tNGC3 chip witness verified the annulus. The D20
    "too large, cropped, not centred" witness was the PRE-tNGC3 build
    (native 100x100 overflow). Residual action: tighten clipR 23->22.5
    (hole inner edge measured ~22.5-23), pin centre+clip law.
## F6 frame bands
Top bar OK per user; side/bottom bands show the legacy texture — audit
which paint path covers them in the newgame state vs the tA2 generator.

## F1-F5 IMPLEMENTATION STATUS (code landed this iteration; build ok, run_tests 488/488)
- F1 CODE (title.cpp preview loop): rec = 4*ktype + cls with ktype =
  wheelGal star i type (fallback hash%13); dims-zero cells k40..k51 skip
  honestly (no tint); fallback tint uses neutralTint(ktype). K=0 seam CLOSED.
- F2 CODE: pure-black plate rect (503,8)-(633,37) painted before the
  "Player Species" header text (measured box census above).
- F3 CODE: NOT DONE this iteration (budget) — glyph map measured and banked
  (scripts/tNGF_arrow_map.py: navy well + dark-slate frame + cyan triangle
  7px apex-to-base, UP y49..62 x617..631, DOWN mirror y357..372); the blue
  kArrowFill box still live. NEXT task carries it.
- F4 CODE: Begin starfield fit+clip to circle centre (538.1,417.4) r32
  (measured cluster bbox 59x60), type-K colour law applied there too
  (rec = 4*s.type+cls, dims-zero skip); dots unchanged (measured panel-wide).
- F5 MEASURED-CLOSED (no code): vendor Begin hole content bbox
  x578..622 y395..440 centre (600.2,417.7) vs OURS x578..622 y395..440
  centre (599.8,418.0) = MATCH <=0.4px; unclamped probe both sides rmax
  28.0 / r95 24.2 (identical profile) — the D20 witness pre-dates tNGC3
  (the clipR=23 circular clip shipped there). Honest negative: no delta
  needed; vision (Begin 4x): full composition, not a crop.
- F6: NOT STARTED (budget). Named for the next cycle.
- VERIFICATION STATE: build + 488 tests green; NO fresh t412 shot graded
  this iteration (budget) — the next session re-runs scripts/t412_newgame_shot.sh
  + scripts/tNGF_star_census.py (expect warm class >0 ours) +
  tNGF_backing_probe.py (expect black box) BEFORE packaging.
- LEDGER: no OQ row moved (tNG-F is PHASE-17 seam work like tNG-C/U);
  honest negative recorded here; open=[016,019] unchanged.




# tNG-F2 CYCLE 2 (2026-11-22, fresh session) — V0 VERDICTS
Trigger check: DECISIONS.md tail = D20 (no new reply); ring t368 20/20
turn=1086 min=max => NO new sitting, r1_t85g_sitting.py NOT run.
Build current (ascendancy 02:14); bash scripts/t412_newgame_shot.sh re-shot
/tmp/t412_shots/{t412-newgame,t412-raceintro,t412-after-intro}.png.

## V0-F1 PASS (tNGF_star_census.py, fresh shot)
OURS warm 5% (was 0%), blue 20% (was 34%) vs VENDOR warm 10% blue 16%.
Radial r50 147 vs 152, r90 193 vs 189; corner-px 0. The type-K colour law
is live on screen. Residual: warm share still ~half vendor (50-star preview
galaxy draws fewer warm-type stars than the vendor's 100-star field — count
law is cited; share follows the galaxy, not a codec gap).

## V0-F2 PARTIAL — plate landed but FLAT where vendor is SPECKLED
Zone x503..633 y8..37: ours pure-black 0.948 vs vendor 0.367; vendor non-black
= dither families (12,12,16) x304/554 rows26-37, (12,28,48), (12,12,12),
(12,14,20)... parity test shows NO even lattice (0.45-0.52 all four parities)
=> random speckle, not halftone. Vision 4x (/tmp/tNGF2_plate_compare.png):
vendor black backing is TEXTURED (same near-black grain as the cosmos well),
ours is a flat black slab — reads "painted over" vs vendor "recessed window".
HYPOTHESIS (to test next probe): the plate is the SAME background field as
the cosmos well (F1-M2: preview table has no static consumer; the shared
COSMOSWnd field paints behind the header window) — compare vendor cosmos-bg
census vs plate census; if they match, paint the cited well-background
generator under the header instead of flat black.

## V0-F4 witness: /tmp/tNGF2_begin_compare.png (4x, L=vendor R=ours) — see
vision verdict below.

## V0-F4 PASS (vision /tmp/tNGF2_begin_compare.png + numeric)
Begin cluster ours: round-ish bbox x511..566 y400..443 (vendor x510..568
y389..448), multi-colour (warm+blue+white comps visible), dots intact,
portrait full not cropped, centred. Residuals (honest): ours sprite set is
17 single-px comps vs vendor 3 (vendor sprites run 9..59 px), and vendor
vertical extent 60 rows vs ours 44; dots census ours 214x(255,255,255) vs
vendor 46 (vendor dots lean chrome-family (42,60,74)/(103,116,126)).
=> F4 containment law landed; sprite-size/dots nuance = named residual for
the package open-list, NOT a new code task this cycle (D20 budget).

## V0-F2 follow-up MEASUREMENT (plate texture)
Plate x503..633 y8..37 nearest-4-family census: (0,0,0) 46.3% (12,12,16)
35.0% (12,12,12) 7.1% (12,28,48) 11.6% (text excluded). Grain: lag1 horiz
8.87 vs shuffled-iid 25.42 => CORRELATED speckle, same Markov family as
mapchrome introSpeckleAt (whose census is 40/30/25/5 — same four families,
plate reads darker/bluer). Cosmos well bg is 98% pure black => plate is NOT
the cosmos field; it is the intro-speckle family. F2 REFINEMENT (coded this
cycle): paint the plate with the tNGF plate census via the same stateless
chain law instead of the flat black rect.

## F3 CODED (this cycle)
menulaw.h/.cpp: arrowGlyphCovers/arrowGlyphColourAt — 16x17 per-px family
grids kArrowUpGlyph (y47..63) / kArrowDownGlyph (y356..372) x616..631,
six exact refcap colours (N 12,32,48; D 34,60,74; M 79,116,126; C 123,171,177;
B 168,227,229; W 190,255,255). title.cpp paint loop replaces the blue
kArrowFill box + drawn triangle (both REMOVED — dead-static law). Hit rects
kRaceArrowUp/Down unchanged (hit law already correct). Named seam: the vendor
widget record supplying this art is uncited; the GRID is the measurement.

## F2 CODED+VERIFIED (cycle 2)
mapchrome speciesPlateAt: 4-family speckle chain (census 463/350/71/116,
45% copy-left + 50% repeat-up fit on the measured ANISOTROPIC grain, salt
0x420e8910b5e72c97 selected so the REALISED 131x30 window census matches —
chain propagation otherwise drifts the mix). title.cpp paints the plate
px-by-px from the law. ON-SCREEN (fresh t412 shot): census ours 48.6/34.7/
4.6/12.1 vs vendor 46.0/34.8/7.1/12.1; grain h 7.17/13.10/16.62 vs vendor
8.59/12.26/16.36, v 6.47/10.73/13.19 vs 5.50/10.35/13.86. Vision 4x: reads
as the same dark speckle backing (cycle-1 flat slab gone). Residual honest:
pal[1] share 4.6 vs 7.1 (noise floor of a fixed window; salt re-pick if the
user flags it).

## F3 CODED+VERIFIED (cycle 2)
menulaw arrowGlyphCovers/arrowGlyphColourAt 16x17 grids (exact refcap
family map), title.cpp paints the cells px-by-px; kArrowFill/kArrowInk
REMOVED. ON-SCREEN: family-match ours vs refcap = 272/272 UP and 272/272
DOWN; zero (26,87,146) px. Vision 6x: recessed cell + cyan triangle glyph,
style matches. Honest named residuals: (a) the vendor glyph interior carries
4 blend px ((155,220,255)/(133,195,234)) nearest-mapped into the 6 families;
(b) the widget record supplying the art is uncited (grid = the evidence).
Test pinned: menulaw_arrow_glyph_law (run_tests 489/489).

## F6 FRAME-BAND AUDIT (cycle 2) — 1:1 census + defect list (G1 close form)
PAINT PATH (read title.cpp:450-484): ONE generator — chromePage built from
textureColourAt (mapchrome.cpp) over the FULL screen, well/panels painted
over. There is NO second legacy paint path in newgame: the D20 "rest of the
frame is the old wrong texture" is textureColourAt's own census coverage.
Mapping law: vendor refcap png(x,y) = game(x-1,y-1) (643x481 letterbox,
row0/col0 pure black [verified]).
CENSUS (game coords; rows 8..372 for the side bands; fresh t412 shot):
  TOP  y0..7    vendor mean lum 190 (49.4,69.4,70.9) ours 189 (49.4,69.2,70.4)
               MATCH on colour/brightness; ours same-h run 0.39 vs vendor
               0.17 (noise runs along the band 2.3x longer) = the DEFERRED
               top-bar sharpness family — NOT touched (user ruling).
  LEFT x0..7    vendor 235 (61.6,85.3,88.0) ours 228 (61.4,81.8,84.8);
               per-60px row-segs vendor 228..240 ours 225..231; same-h
               0.12/0.16. MATCH within noise (per-column kLeft censuses
               t422 F7 are doing their job).
  RIGHT x632..639  DEFECT CONFIRMED: vendor per-col lum 158,309,393,393,
               362,330,318,314 (bright bevel RIDGE peaking x634/635);
               ours 90,265,293,285,285,275,276,295 — band ~20% too dark
               AND ridge shape missing. ROOT CAUSE: textureColourAt has NO
               per-column census for the newgame right frame band; all
               x>=473 fall through to kRight, the MAP-screen x466..639
               zone census (t422 F10), which mixes sidebar-widget darks
               into what the New Game frame paints as a bright ridge.
  BOTTOM y373..392 vendor 175 (40.8,62.5,71.4) ours 177 (41.0,63.4,72.3);
               navy-dominant both sides; same-h 0.59/0.60. MATCH.
DEFECT LIST (written, G1): (D1) RIGHT band brightness+ridge [named fix:
per-column kNewgameRight[8] census x632..639 measured on this refcap,
branch before kRight; needs the generator-origin seam decision]; (D2) TOP
band run-length (DEFERRED by user); (D3) none LEFT; (D4) none BOTTOM.
1:1 composite: scratchpad/F6-bands.png (4 pairs, vendor over ours).
F6 CLOSE = audit + defect list per assignment; code fix NOT in this cycle
(D20 budget: cycle 2 of 3; D1 named for cycle 3 or ACCEPT-with-list).

## PACKAGE (cycle 2) + honest negative
scripts/tNGU_composite.py extended: --checklist FILE renders the
PLAIN-LANGUAGE NUMBERED CHECKLIST ON THE IMAGE (D20 usability correction;
headlines above the pair, t441 strip unchanged below). Checklist text =
scratchpad/NG-checklist.txt (7 numbered items: 5 changed, 2 open; item 8
"rotation" DRAFTED then REMOVED — unverified, tNG-C cites static positions,
rotation drives class only: no unverified claims on the grader's interface).
COMPOSITE scratchpad/NG-usergrade.png 1290x1548, t441 18/18 PASS rc=0,
vision-verified legible/intact. F6-bands witness scratchpad/F6-bands.png.
LEDGER: no OQ row moved (tNG-F is PHASE-17 seam work); honest negative
recorded; open=[016,019] unchanged. run_tests 489/489 (new
menulaw_arrow_glyph_law).
