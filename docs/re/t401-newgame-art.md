# t401 WIP — NEW GAME FRAMING + PANELS (D11)

Session base: fresh; no new sitting (ring max_turn=1254 == t392..t400 value);
tree clean; ruling server 8613 live; no new USER: lines past 11:37 block.

## S0 — D11 defects to close (user lines verbatim in DECISIONS.md L298)
1. "UI framing is missing" (New Game screen)
2. "artwork is rendered incorrectly in the bottom row (Star Density/
   Species/Atmosphere/Player Color)"
3. "artwork isn't rendered at all in the Player Species column on the right"
4. "Begin New Game box is empty except for text"
5. "species description box ... is empty and transparent (you can see the
   galaxy map behind it, but it should be solid)"

## S1 — windows.txt state-3 section (L575-717, cited verbatim)
- TYPE 100 STATENUMBER 3 SHAPEFILE DATA\3CFGNEW.SHP (the lib header)
- NEWGAMEWND TYPE 18, rect (334,12)-(488,364), STATE "1 3",
  SHAPEFRAME 0  <-- NOT -1: the description panel carries 3cfgnew frame 0.
  t393 drew this window as a text-only transparent box = defect 5.
- GALAXY_MORE (7,381)-(122,472) SHAPEFRAME -1, WINITEMS 2:
  SHAPEITEM 1 data\3cfgnew.shp 0 0 0 + TEXTITEM "Star^Density 2 0 10"
- PLAYERS_MORE (131,381)-(246,472) same shape item, TEXTITEM "Species"
- DIFFICULTYMORE (255,381)-(370,472) same shape item, TEXTITEM "Atmosphere"
- Player^Color (379,381)-(493,419) SHAPEFRAME -1 WINITEMS 0 (no art record)
- RACELIST TYPE 10 PARENT NEWGAMEWND (502,45)-(632,372) SHAPEFRAME 7
- NO record named STARTGAME / map-thumbnail in state 3 (t393 cited negative
  re-confirmed: Begin New Game has NO windows.txt record).

## S2 — 3cfgnew.shp census (banked evidence, decision-sheet.md + XREC pngs)
13 records k0..k12, all ~84x79/80 (k11 88x79, k12 vendor-TRUNCATED at file
EOF — JUNK-CERTAIN, D1 batch accepted). Vision classification (t278 sheet):
dot-wheel menus k0-4 + k7-9; HERALDIC SHIELDS k5-6; GLOWING ORBS k10-12.
KEY CORRECTION to the t401 task prose: 7racesel.shp (8x 158x30) belongs to
the TYPE-100 header STATENUMBER 7 (windows.txt L720-722) = the MAP-screen
species menu (RACE_1..7, rects 474,7-632,37), NOT the New Game list. The
New Game species column is RACELIST (TYPE 10, SHAPEFRAME 7) — its rows are
listbox code, and the row art candidates are the small race libs:
raceflag.shp (21x EXACTLY 14x24, t400 §2), racering k0 53x53, smraceNN
(~49px), lgraceNN (large portrait class).

## S3 — user-original geometry + vision (t401 crops banked work/r1/loop/
## t401-o-{bottomrow,begin,racelist,desc}.png, 2x nearest; montage
## t401-3cfgnew-montage.png)
- NEWGAMEWND interior: BLACK 71.9% (39363/54715 px) — vendor panel IS solid
  black (vision: "no stars through it"). Our transparent box = defect 5.
  Content census: greens (0,106,51)/(0,149,71)/(0,170,81) = name+lore text;
  greys 120-209 = the large portrait ring art; (12,32,48) x110 trace.
- RACELIST interior: navy (12,32,48) 26.9% FILL + portrait art; NO text in
  rows (vision, decisive on crop): rows = circular portraits in silver/grey
  bevel rings over navy. Art run at y=200 spans x512..607 (~96 px wide).
  Bevel greys measured 48..209; edge band x494..501 = t400 §4 page texture.
- BOTTOM ROW (vision): Star Density = dark circular WELL w/ coloured dots;
  Species = blue well w/ FOUR small vertical-rect icons (green/purple/pink/
  yellow); Atmosphere = planet disc w/ central icon + glow lines; Player
  Color = NO well, row of SIX vertical-rect icons (green/purple/red/blue/
  cyan/orange). Text ABOVE artwork in each panel.
  => SHAPEITEM 3cfgnew k0 (the wheel well) is COMMON to the first three;
  per-control OVERLAY content is separate art. raceflag.shp (21x 14x24
  vertical rects, t400 §2) matches the icon shape exactly.
- BEGIN box (vision): thick textured grey-bevel frame (t400 §4 class), dark
  interior, starfield dot-cluster LEFT, GREEN-RINGED circular emblem RIGHT
  (= racering.shp k0 53x53 + portrait), text bottom-centre.
- DESC PANEL (vision): header name green; LARGE circular portrait w/ green
  ring; small planet sphere + green crest rectangle; green lore paragraph.
  No bevel frame on the panel itself.

## S4 — port code state (rewrite/src/ui/title.cpp RaceConfig branch L297-513)
- Panel (3) NEWGAMEWND: draws ONLY a 1-px rect outline kBevel(97,97,97) over
  the starfield => the transparency defect (D11 #5) is literally this.
- Bottom row (7): blits cfgNew k0 ALWAYS, at cx-42, y0+26 (84x79 face) =>
  the "bottom-row artwork wrong" defect (D11 #2): vendor shows DIFFERENT
  frame per control class (dots well / icons circle / orb), never k0 in all.
- RACELIST (6): grey disc + NAME text stand-in => defect #3 (no art).
- Begin box: fill + bevel + label only => defect #4.

## S5 — 3cfgnew frame CLASS census (montage t401-3cfgnew-montage.png, vision)
k0 dark well ~11 dots | k1 ~16 | k2 ~15 | k3 ~22 dots (density class)
k4 4 purple icons | k5 3purple+1yellow | k6 2purple+1yellow+1pink |
k7-k9 1purple+1yellow+1pink+1green (SPECIES class: icons light up per count)
k10 glowing green orb + central icon | k11 bright yellow-white orb (ATMO)
Vendor original at Average/Five/Neutral shows: dots well (Density), 4 icons
(Species), blue-glow planet (Atmosphere) — matches k0 / k4-7 / k10 classes.
SHAPEITEM k0 in the table = the value at table-parse time; the vendor
updates the frame at runtime per setting (the *_MORE msg 501/503/505 path).
FRAME->VALUE mapping = PORT CHOICE (named seam); frame CLASS per control =
MEASURED (user original, allowed evidence).

## S6 — race art libs (dims census, verbatim headers)
racering.shp 8x 53x53 (k0 = green QUARTER ARC — ring assembled from arcs
[unverified]); smraceNN.shp 21 libs x 49x49 (portrait class, unique at
49x49 among race-named libs); lgrace00 296x199 (large portrait);
raceflag 21x 14x24 (crest/flag class); planets.shp has 47x46 records.
Begin-box green ring measured x573..629 y390..446 (57x57 ~ racering scale);
DESC-panel green ring rows 45..149 (105 tall) — LARGER than racering 53:
two scales, ring source = measure next.

## S8 — measurement batch 2 (user original, allowed evidence)
- DESC ring: green ring spans x357..461 (105 px), rows 45..149 => centre
  (409,97) r~52 — LARGER than racering 53 (two scales on screen).
- RACELIST row2 ring greys at x506..511 + x608..612 => ring dia ~107,
  centre x~559; art run between ring edges 512..607 (96 px) is PORTRAIT ART
  (browns/teals), not navy: vendor fills the ring with a big portrait
  (~2x smrace). Row1 art bbox fills the band (9763 non-navy px).
- Begin box: green ring px x573..629 y390..446 (~57 ~ racering 53 native at
  (573,390)); interior navy (12,32,48) 7774 px; scattered dot colours
  (oranges 52..55, blues 71..76 at y=430) LEFT of ring = starfield cluster.
- raceflag decode walk (Python, X-law): dominant per frame = navy (12,32,48)
  base + GREEN (0,170,81)/(0,85,40) crest px -> the DESC "green rectangle
  with emblem" IS raceflag k<specnum> at native 14x24 (desc crest zone rows
  206..230). Base colour = panel navy => seamless, same witness as t400 §2.
- Species frame ANCHOR: original at "Five Species" shows icons
  green/purple/pink/yellow = k7 class (montage census S5) => frame =
  k(2+species) ANCHORED at species 5 -> k7; endpoints 3->k5, 7->k9 inferred.
  NAMED SEAM (decider: original capture at a different species count).
- Page texture present on the New Game original too (x494..501 greys/teals
  at y=200) = t400 §4 class => "framing missing" = port never paints the
  §4 bands on THIS screen (only mapchrome does, campaign screen).

## S10 — measurement batch 3 + LAW DECISIONS (the implementation contract)
- k0 record shape (4x vision t401-k0-4x.png): dark-grey filled circle w/
  scattered coloured dots + DASHED horizontal line mid + mirrored semicircle
  below (two stacked circles, 57x79 content bbox). The ORIGINAL DENSITY zone
  shows exactly this sprite class (vision t401-odens-4x: "resembles vendor
  record k0 — rim + dots + dashed line, not a live starfield"). Content
  circle in original: non-navy bbox x38..92 y408..462 (55 px, centred on
  panel cx 64.5). => WHEEL BLIT LAW: blit frame at (cxp-28, 408) (content
  circle centred; current port blit (22,407) = off by 16 px x + wrong frame).
- Dot-count monotonicity [measured]: k0..k3 bright clusters 23/33/45/62
  (chroma px 187/281/395/546) — dots INCREASE with frame index; originals
  Average=sparse well, Very Dense=crowded (vision) => frame index rises
  with density. EXACT bijection 5 values -> 4 frames = NAMED SEAM (port:
  sorted ladder 15/25/50/75/100 -> k0,k1,k2,k3,k3).
- Species frame: original "Five Species" shows 4 icons (vision) and k7
  carries 4 icons (montage) => ANCHOR species 5 -> k7; law k(2+n);
  endpoints 3->k5, 7->k9 inferred. NAMED SEAM (decider: original at 3/7).
- Atmosphere: original Neutral chroma mode (36,138,190) x99; k10 has
  (36,137,190) x123 AND k11 x195 — WEAK discriminator (both orbs carry the
  blue). Port: 0/1 -> k10, 2 -> k11, declared choice, seam stays named.
- PlayerColor zone census: NO chromatic icons exist in the capture — only
  navy + grey ink (198,203,206)/(225,227,229) rows 383..393 (label) +
  394..404 (icon-row band, greyish) + bevel rows 405..419. The vision's
  "6 coloured icons" is COMPRESSION-BLEED — MECHANICAL REFUTATION banked.
  Port keeps label + 6 CVD-safe chips at rows y0+13 h10; WHICH colours =
  seam (unchanged).
- RACELIST rows: chromatic portrait art x505..613 (109 px wide), NO vendor
  text in rows (t393 crop + this session's crop, two vision reads agree).
  Portrait = smraceNN 49x49 SCALED ~2x (measured 96..109 zone; scale
  filter = named seam) inside grey ring r~53; row centres x~559 (ring
  greys x506..511/608..612).
- DESC panel: fill BLACK (71.9% census + vision "no stars through"); green
  ring (0,142,69) r~52 centre (409,97) (= NEWGAMEWND centre x 411 ±1);
  portrait smrace scaled 2x inside; planet disc x383..419 y198..239 purple
  bands (40,20,32)/(109,56,93)/(125,121,138) — code disc (honest vector);
  CREST = raceflag k<specnum> NATIVE 14x24 at (441,205) (measured green
  bbox 441..455 x 205..229 — exact size match).
- BEGIN box: emblem zone green px x573..629 y390..446 (57x57) centred
  (601,418); smrace NATIVE 49x49 at (577,394) fits it EXACTLY (49+ring);
  dots zone x496..570 greys (225,227,229)/(255,255,255)/(164,171,177)/
  (103,116,126)/(97,97,97) + teals — splitmix64 hash-noise (t400 pattern).
- Page texture on THIS screen: left margin x0..5 + right side x494..639
  (sparse TEX columns 494/498/502/614/634/637/639) = t400 §4 class;
  paint texture FIRST, black cosmos (7,7)-(465,472) over it, then panels.
- Value words inside bottom panels: original has NONE (summary block
  carries values) — port removes the y0+58 words (fidelity).
- racering.shp frames k0..k7 are NOT ring+portrait composites (dominant
  colours vary per frame: green-arc/yellow/pink/olive/blue/orange/grey) —
  role unidentified; NOT blitted (seam: decider = live witness).

## S11 — IMPLEMENTATION + VERIFICATION (landed this session)
- Code: menulaw.h t401 constants block (kWheelBlitTop 408, kWheelBlitHalfW
  28, kDescRingCentre (409,97) r52, kDescCrestRect (441,205,14x24),
  kBeginEmblemRect (577,394,625,442), kBeginDotsBand, kRacePortraitCx/Scale
  2, kNewgameTextureBands {0..6},{494..} full-height); menulaw.cpp pure side
  newgameWheelFrame(control,value) (S10 law) + portraitLibName(specnum)
  "smrace%02d.shp" refuse-not-clamp; vendortext.cpp blitShapeScaled (same
  decode/palette path, integer NEAREST, blitShape now delegates scale=1);
  title.cpp RaceConfig rebuild: (1a) page texture FIRST (t400 §4
  textureColourAt, bands incl. full-height right x494..), cosmos black over
  it; (3) DESC panel OPAQUE pure-black fill 334,12-488,364 + green ring
  (0,142,69) r52 + smrace portrait scaled 2x inside ring + raceflag crest
  k<specnum> NATIVE at kDescCrestRect + planet racehome/homepl blit below
  ring; (6) RACELIST rows blit smraceNN scaled 2x centred kRacePortraitCx;
  (7) bottom-row wheels per newgameWheelFrame law (value words REMOVED —
  original has none); Begin box emblem smrace native + dot-band noise.
- Tests: rewrite/tests/test_newgame_t401.cpp 6 tests (wheel law incl.
  off-ladder refuse; geometry constants fit-inside pins; portraitLibName;
  raceflag 21x14x24 class re-verify; 3cfgnew selected frames decode +
  game.pal bright-pixel MONOTONIC census k0<k1<k2<k3; smrace 49x49
  decode). Suite 340 tests 0 failed (was 334; +6).
- Witness: scripts/t401_newgame_witness.sh + t401_witness_census.py
  (venv PIL). Shots work/r1/loop/t401-newgame{,-set}.png. CENSUS VERDICT
  PASS both shots: desc-panel solid (starish-in-margin 0, black 42149),
  RACELIST chromatic, crest green 103, ring green 1360, wheels distinct
  (chroma [942,3055,2140]; panel0==panel1 px 626/3080 — dominant-colour
  discriminator INVALID, frame family shares fills; zone-equality is the
  anti-k0-everywhere pin), begin dots 233 + emblem chroma 1794, texture
  left 3360/3360 + gutter 3160. Wheel-CLICK shot shows species/atmosphere
  zones change (set-shot chroma deltas) — frame law live-routes.
- app.log routing: FRESHGAME -> raceconfig; PLAYERS_MORE msg 503 -> Three;
  begin density 50 species 3 atmosphere 2 species-pick 0 (wheel click on
  Species cycled 7->3 via msg 503 — law-consistent).

## S12 — MUTATION CAMPAIGN + CLOSEOUT STATUS
- scripts/t401_mutate.py, checkpoint-commit a5f1284 first (revert safety).
  MUTATION 6/6 CAUGHT: M1 density-offladder-accept, M2 density-topshare,
  M3 species-anchor (2+value->1+), M4 atmosphere-swap (10<->11),
  M5 portrait-clamp (refuse->clamp), M6 portrait-nopad (%02d->%d) — M1-M4
  caught by newgame_t401_wheel_frame_law, M5-M6 by
  newgame_t401_portrait_lib_name. Post-revert suite re-run green
  (340/0).
- LEDGER: no OPEN-QUESTIONS row matches t401 (D11 grades are user-ruling
  items in STATE.md's queue, not OQ rows; the only t401-adjacent OQ fact
  — 3cfgnew k12 JUNK — is already inside OQ-005's CLOSED residue
  decomposition). HONEST NEGATIVE: t401 CLOSES NOTHING in OPEN-QUESTIONS.
  The D11 New Game item's visual ACCEPTANCE is not self-gradeable (R13) —
  witness shots work/r1/loop/t401-newgame{,-set}.png ride the t403 grading
  sheet; until the USER grades them the item stays user-pending, though
  every sub-law (framing bands, wheel frames, portrait class, crest class,
  Begin art, opacity) is now cited-measurement-backed and pinned.
- SEAMS kept open (named, deciders listed in S1-S11): racering.shp role
  (decider: live witness vs original crops); density top-two frame share
  k3 (weak discriminator banked); atmosphere Peaceful-vs-Neutral both k10
  (declared choice); RACELIST row-ring scale (port uses scaled portrait,
  vendor 105-px DESC ring vs 53 racering noted S8).
