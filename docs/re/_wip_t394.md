# t394 WIP — galaxy map + rail buttons (phase 11, D10 "galaxy map still wonky... all the buttons off the galaxy map are wonky too")

Started 2026-11-15. Inputs on disk: scratchpad/galaxymap-original.png
(642x481, user-supplied vendor original), scratchpad/galaxymap-rewrite.png
(512x384!), work/r1/loop/t391-map.png (640x480, our own Xvfb witness).

## Finding 1 (task's FIRST job, diagnosis) — blit-absence DISSOLVES; scale is WM-side [verified]:
- The user's rewrite shot IS THE MAP SCREEN (state 1); t391 banked [verified,
  ui-runtime.md t391 block] MAP state 1 has NO backdrop record (1starmap k0
  is 158x75 element art; 10status k0 blits in STATUS state 10 only, per
  STATUSWND STATE "1 10" windows.txt ln1020). Absence of a backdrop in a
  MAP-screen shot is correct behaviour. Rail icons (1starmap k3/k4/k5/k7)
  ARE visible in the user's shot -> blits landed.
- Our code requests 640x480 (title.cpp:112, ui.cpp:53); our Xvfb witness
  measures 640x480 (t391-map.png). The user's shot measures 512x384 = 0.8x
  (PIL). Colour census: 408 colours; nearest-upscale to 640x480 adds ZERO
  new colours -> clean resample of a 640x480 render; WM rescaled, our
  renderer never saw it. Grep: no scale/logical/min-size call anywhere in
  rewrite/src. SDL 2.32.4 headers have NO window-scale hint (only
  SDL_HINT_RENDER_SCALE_QUALITY ln1970 = texture filter).
- CONSEQUENCE (the "all the buttons are wonky" mechanism, [inferred from
  verified]: hit-testing uses windows.txt LOGICAL rects (kRail x-band
  474..632); if the WM scales the window to 512x384 and SDL reports mouse
  coords in window pixels, every click lands at 1.25x its intended logical
  position -> every button "wonky". Fix candidate: SDL_RenderSetLogicalSize
  (uniform scale + SDL rescales mouse into logical space) or
  SDL_SetWindowMinimumSize; decision below after doc check.

## Finding 2 — the user-supplied ORIGINAL capture is 1:1, offset 0 [verified]:
Category-button bevel bands measured on galaxymap-original.png rows:
button top-white-lines at y=130,169,208,248,286 vs windows.txt rects
Planets 130..160, Ships 169..199, Research 208..238, SpecialAb 247..277,
Races 286..316. t393's "capture->screen = minus 1" does NOT generalise
(642x481 = capture-tool border, not a 1px content shift). Anchor law here:
IDENTITY (png x,y == screen x,y).

## Finding 3 — vendor sidebar inventory vs windows.txt (measurements pending precision pass):
- FIVE GREEN OVALS: components at screen x 482,513,544,575,606 (pitch 31,
  ~19 px wide), green rows y10..40 -> inside TURNCOUNT rect 474,7-632,43
  (TYPE 15 SHAPEFRAME 65 DIGITFRAMES 55, ln521-537). TURNCOUNT = the five
  ovals + digits. Our rewrite paints NONE (string dump instead).
- TWO WIDE BLUE BUTTONS: bevel bands y45..49 + y52..83 (white edges 45/84)
  = ~474,45-632,84 vs table NEXTTURN 474,52-548,82 + NEXTTURNCONT 557,52-
  632,82 (ln539-572): the vendor ART (SHAPEFRAME 65/66) paints wider/taller
  than the hit rects. Solid blue y92..126 = ? (above Planets button 130).
- 3x3 GRID = the COSMOSWnd children (ln223-414): spin cluster ROTLEFT
  479,364-494,394 / ROTRIGHT 495,364-509,394 / ROTUP 518,364-548,379 /
  ROTDOWN 518,380-548,394 / ZOOMIN 557,364-587,379 / ZOOMOUT 557,380-587,394
  / CENTERHOLO 596,364-626,394 + toggle row TOGLANES 479,403-509,433 /
  TOGEMPIRE 518,403-548,433 / TOGSHIPS 557,403-587,433 / TOGCOLONIES
  596,403-626,433. SHAPEFRAMEs 8..18.
- SIX COLOURED SQUARES = RACECONTROLS (ln415-435): frame 474,442-632,472
  SHAPEFRAME 19, NUMCONTROLS 7, RACE1CONTROL 1 479 449 495 465 (pitch 22,
  16x16 squares, bits 1/2/4/8/16/32/64). MEASURED on original: green square
  screen 479,448-495,465 EXACT match of RACE1CONTROL rect. (D10 prose
  "six" = one control per OTHER species visible; table holds 7.)
- OUR MAP SCREEN LACKS: ovals, blue nav art, spin/zoom/toggle cluster,
  race squares; and prints a string dump ("turn 0 ... score") the vendor
  never shows (stats live in the ovals + TURNCOUNT).

## Decision (scale law): TAKEN — SDL_RenderSetLogicalSize(640,480) on every
renderer we create (ui.cpp runCampaignUi + title.cpp runTitleScreen). Law
source = the installed SDL 2.32.4 header doc itself (SDL_render.h,
SDL_RenderSetLogicalSize): "If the output display is a window, mouse and
touch events in the window will be filtered and scaled so they seem to
arrive within the logical resolution." That fixes the hit-map under WM
scaling; letterbox is the documented default mode (SDL_hints.h:1942), left
untouched. No hint exists in this SDL version for WM-scale refusal
(SDL_hints.h full-census: only RENDER_SCALE_QUALITY = texture filter).

## Closure state
- 5 pins tests/test_mapchrome_t394.cpp; suite 313/0; gate exit 0; ledger
  audit OK (17 closed / 3 open, UNCHANGED — strict-close: this was queue
  work, NO OQ row moved; the honest negative is that the digit-frame
  mapping, pan/zoom behaviour, and species-square vendor palette remain
  named seams, not measurements).
- Witness: scripts/t394_map_witness.sh; scripts/t394_map_mass.py CENSUS
  PASS (green oval mass 350, dump band white=0, 11 cluster rects non-flat,
  7 race-slot dominants distinct = kOwnerRgb). Shots work/r1/loop/
  t394-map.png (grade THIS; t394-map-turn1.png captured post-quit —
  --campaign 1 exits right after the advance) + t394-frames-contact.png.

