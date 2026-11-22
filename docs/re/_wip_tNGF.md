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



