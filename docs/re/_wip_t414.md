# t414 WIP — NEW GAME ROUND 3 (D15)

Session base: fresh; live-timeline.jsonl mtime 2026-11-12 06:45 (NO new
sitting since last iteration -> no re-run of r1_t85g_sitting.py needed);
tree clean at dfae9a6; gate not yet run this session.

## S0 — D15 defects for this row (verbatim, docs/DECISIONS.md L354+)
(a) "the decorative framing is still wrong and mostly missing"
(b) "there should be a spinning star field commensurate with the star
    density in the upper left"
(c) "the icons below 'Star Density', 'Species', and 'Atmosphere' are
    repeating"
(d) "the player icons are missing from the 'Player Color' box"
(e) "the race images in the right-hand frame are all 4x size"
(f) "the planet image is missing from the race info frame"

## S1 — planned order of attack
Ground truth first (D13): walk our own New Game screen, grade with native
vision against scratchpad/newgame-original.png, THEN fix. Sub-items (c)
and (d) are the same root-cause family (bottom-row wheel/icon routing);
(e) is a numeric scale bug (record dims vs drawn dims); (f) is a missing
blit; (b) is a new feature (rotating point preview reusing t411 cam3d).

## S2 — findings (measured, this session)
GROUND TRUTH walked: work/r1/loop/walk/newgame-t414.png (Xvfb :9, click
318 295 = FRESHGAME). Compared against scratchpad/newgame-original.png
(643x481, +3px capture offset).

- (a) FRAME LAW [measured]: the original is a TEXTURED CHROME PAGE with
  the cosmos punched in. At y=200 left texture ends x7 (cosmos starts x8);
  at x=300 top texture ends y8, bottom texture starts y374. Chrome colours
  row2: (77,113,117)/(80,117,120)/(85,125,125) = t400 §4 textureColourAt
  family. GAPS between bottom-row panels AND the DESC->RACELIST gutter
  x494..501 are ALSO texture (measured (85,125,125),(65,73,79),(97,97,97)).
  Our port paints texture in 2 bands only and cosmos edge-to-edge = the
  "framing mostly missing" defect. FIX: paint texture FULL 640x480, then
  black cosmos rect (8,9)-(493,373), then panels.
- (b) PREVIEW LAW [measured, user original very-dense capture]: the cosmos
  zone is a STARFIELD of COLOURED points (reds/blues/oranges/whites, ~100
  at Very Dense = ladder rung 100), no lanes, summary text over it at the
  bottom. Ours draws static flat previewCamp projection (lanes + grey
  pips) — wrong class. FIX: Camera3d-projected point field, N ==
  kDensityStarCounts[densityIdx], deterministic hash positions in a
  sphere, yaw advances per frame (spinning), star tint by type.
- (c) WHEELS [measured ours]: the three panels DO render distinct frames
  at default values (zone px-diff 2633/2443/2455, chroma 252/1484/877) —
  but the LAW repeats frames across value steps: density top-two share
  k3, atmosphere Peaceful AND Neutral both k10. 3cfgnew census: 13
  records (k0..k12) vs 5+5+3 = 13 value steps across the three controls
  — the vendor mapping is one DISTINCT record per step. k12 is the
  vendor-TRUNCATED record (X class): decode check pending.
- (d) PLAYER COLOR [measured, REFUTES t401 S10]: the original zone
  (379,381)-(493,419)+capture-offset HAS chromatic icons: bbox x384..492
  y434..459, 1454 chromatic px, SIX column runs (14 px wide each, ~26
  tall): green (5,118,69), purple (103,63,127)/(158,81,174 hi), yellow
  (164,159,79)/(255,235,97 hi), pink (154,108,127)/(239,154,174 hi),
  blue (27,85,147), orange (151,88,20)/(235,121,4 hi). t401's "no
  chromatic px" census scanned rows 394..404 (the LABEL band) — wrong
  rows. Ours renders ZERO chroma in the zone (chips at y0+13 h10 = rows
  394..404, under the label; measured icons live at rows ~431..456 in
  our coords). FIX: 14x26 chips at measured cols/rows with measured
  base+highlight colours (14x24 raceflag shape class, colour per player).
- (e) RACELIST PORTRAITS [measured + native vision]: vendor art is a
  CIRCLE clipped to the silver ring (vision on 2x crop: disc + ring, no
  square corners). Ours: 49x49 smrace scaled 2x = 98 px SQUARE, corners
  overflow the ring = the user's "4x size". FIX: circular clip mask r~52
  on the scaled blit (new blitShapeCircular in vendortext).
- (f) DESC PLANET [measured]: original planet zone x383..419 y198..239
  (~37x42) — our honest-vector concentric circles do not read as a
  planet. planets.shp census (this session, scripts/t414_dims_census.py):
  55 records = 11 groups x 5 sizes (11,18,25,35,47px) — the 47-px class
  fits the zone. FIX: blit planets.shp 47-class record per race.

## S4 — wheel class census + implementation (landed)
- 3cfgnew montage (scripts/t414_3cfgnew_dump.py, native-vision read):
  k0..k4 DOT-WELLS (dot count rises with index), k5..k9 ICON-RINGS,
  k10 GREEN orb / k11 BLUE orb / k12 RED SPIKED orb (k12 truncated at EOF;
  visible 55 rows decode via the Python walk; the PORT decoder refuses it).
- LAW (menulaw.cpp): density rank -> k0..k4 (was k3,k3 repeat); species
  k(2+n) unchanged; atmosphere k(10+v) (was 0/1->k10). BIJECTION pinned by
  new test clause "no frame unused, none repeated" (test_newgame_t401).
  HOSTILE (k12) draws NOTHING + print-once refusal (port decode law refuses
  EOF-truncated records; vendor paints past-EOF resident garbage — named
  seam, decider = a live-RAM capture of the vendor draw).
- CODE: title.cpp RaceConfig — chromePage static texture (textureColourAt
  full 640x480, titleArt pattern) + black cosmos rect kNewgameCosmosRect +
  spinning preview (splitmix64 sphere points, N == density count, yaw +=
  kPreviewSpinPerFrame/frame, neutralTint colours; NEVER the sim rng);
  wheel blits clipped to panel rect (the records' stacked-second-circle
  bled below the panel — own-grade caught it); seven measured chips
  (kPlayerChipRgb, rows 434..459); blitShapeCircular (vendortext +
  ui_internal.h) clips RACELIST + DESC portraits to ring r53/r52;
  planets.shp 35px-class sphere (group = specnum%11, named seam) replaces
  the honest-vector disc. t393 previewCamp backdrop + toSdl/kLane/
  filledCircle REMOVED (0-warning law).
- VERIFIED: build 0 warnings; run_tests 402/0/0 (new
  newgame_t414_frame_and_chip_law). Walk shots work/r1/loop/walk/
  t414-newgame{,2}.png; native-vision grade: frame texture surrounds the
  cosmos + panel gaps YES; coloured point field YES; three distinct wheel
  classes YES; seven coloured chips YES; portraits clipped discs YES;
  planet sphere YES. SPIN MEASURED: 79 cosmos px changed between two shots
  seconds apart (import twice, PIL diff).
- REMAINING DEFECTS owned by later rows: preview points are 1px (vendor
  dots read slightly larger); DESC ring is a vector circle not vendor art;
  k12 Hostile wheel blank (seam above); texture-vs-vendor mottle is the
  t400 hash pattern, not a byte copy of the vendor page.

## S5 — ledger
No OPEN-QUESTIONS row corresponds to D15 grades (t401 precedent: these are
user-ruling queue rows). HONEST NEGATIVE: t414 CLOSES NOTHING in
OPEN-QUESTIONS; the D15 New-Game row's ACCEPTANCE is the user's (t420
sheet), but every sub-law is now cited-measurement-backed and pinned.

