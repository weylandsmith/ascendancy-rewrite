# t411 — MAP LOOK PASS 2 (working log)

Assignment: docs/STATE.md queue row t411 — native-vision grade of
work/r1/loop/walk/map_view.png (2026-11-15 22:56, pre-t408..t410 landings)
against the user-supplied vendor original scratchpad/galaxymap-original.png
(642x481, IDENTITY anchor law per t394 F2).

## F0 — own native-vision grades (2026-11-16, both shots loaded natively)
OURS (walk/map_view.png):
- (2) top panel: five bright-green faces in a dark box w/ green frame; at
  turn 0 every face is a zero so they read as "empty green ovals" — SAME
  SHAPE as the vendor at 0, but ours look FILLED/bright vs vendor outline
  style. Pixel-compare owed.
- (5) lanes: exactly two, both touching the boxed home star — t399 law
  LOOKS correct. (6) home star findable.
- (1) NO bevel frame: black cosmos area goes edge-to-edge to the rail and
  window border.
- (3) rail: TV-static grey-teal per-pixel noise.
- (4) stars: bright uniform pips, no visible depth gradation.
- dials: 4 arrow buttons + 2 double-arrows + 4 toggles visible; layout does
  not match the vendor's 4x2 dial grid.
VENDOR (galaxymap-original.png):
- (a) the black starfield is inset inside a lighter textured bevel; whole
  screen perimeter is the same dithered texture.
- (b) five digits read 0 0 0 0 0 (outline-style green on dark) — so the
  vendor at day 0 ALSO shows oval-shaped zeros; the t411 premise "ours are
  EMPTY, vendor shows digits" is about STYLE not binding.
- (c) sidebar = structured dithered teal texture (not per-pixel static).
- (d) stars VARY in size AND brightness (depth classes visible; several dim).
- (e) home marker: a tall green rounded capsule/oval emblem (top-left corner
  AND at the lane junction) — NOT a square ring. Vendor marker art exists.
- (f) 8 dials in a 4x2 grid, each in a dark round recess w/ red-rim ring.
- (g) solid dark band between NEXT TURN buttons and Planets (y~92..126,
  t394 F3 already noted it; unmapped).

## F1 — pixel measurements
(run scripts/t411_measure.py; results appended below)

## F2 — ROOT CAUSE: skip-pixels paint opaque pale green (THE digit defect) [verified]
Mechanical census, vendor vs ours, TURNCOUNT slots x482..624 y7..43:
  vendor green 14-17% dark ~70%; OURS green 63% dark 30%. Ours also contains
  3340 px of exactly (146,178,134) across the whole right column y8..276
  (rail buttons too). (146,178,134) is game.pal INDEX 170 = 0xAA — and 0xAA
  is the byte blitShapeScaled (vendortext.cpp:131-166) stuffs into the
  FIRST decode buffer to detect unchanged (opaque) pixels:
    a filled 0xAA, b filled 0x55, decode both, alpha = (a==b?opaque:transp).
  A .shp TRANSPARENT-SKIP pixel is never written by walkRows, so it stays
  0xAA in a and 0x55 in b -> alpha 0x00 in the ARGB word. CORRECT — except
  the created texture NEVER gets SDL_SetTextureBlendMode(BLENDMODE_BLEND)
  (grep: only vendortext.cpp:34 sets it, on a different texture). SDL
  default blend mode = NONE -> alpha IGNORED -> every skip pixel paints
  game.pal[170] pale sage. THAT is why digit zero-faces read as pale FILLED
  ovals (the "empty ovals" complaint), why rail art has pale bands, and why
  the whole chrome looks washed. FIX: set BLENDMODE_BLEND on the blitShape
  texture. (The vendor k55 face census confirms the faces are dark-boxed
  outline rings: values {16,17,18 green ring, 199/200 dark, 1,0} only.)
## F3 — vendor TURNCOUNT at day 0 reads "0 0 0 0 0" outline-style [verified vision+pixel]
So the t411 premise "vendor shows big digits, ours empty" resolves to: ours
binds turn correctly (ui.cpp:912 kDigitFirstFrame+d) but renders the face's
transparent field as a pale block (F2). No binding change needed; the face
art is already vendor 1:1.

## F4 — texture PATTERN statistics measured [verified]
Vendor sidebar band (x474..632 y100..400, luminance): lag-1 neighbour diff /
mean dev = 0.23 (lag2 0.31, lag4 0.40, 4x4-block lag1 0.28) -> the vendor
texture is SMOOTH/BLOBBY at pixel scale (mottled), NOT per-pixel random.
Ours (splitmix per pixel) = 1.45 (random). The t400 seam (pattern source
record unidentified) stands, but the port's noise now CONTRADICTS a measured
statistic: fix the generator to coarse-grid mottle (same cited colour set +
weights), keep the seam label.
## F5 — cosmos bevel measured [verified, vendor scans]
The black field sits in a RECESSED frame: texture luminance ramps DOWN to
near-black immediately at the field edge, all four sides. Left x1..5 bright
(84,123,124) -> x6 (65,65,65) x7 (49,54,53) x8 (5,6,6) x9 black. Top y1..2
(85,125,125) -> y3..7 (47,75,79)..(31,46,49) -> y8 black. Right x466 (27,32,33)
-> texture resumes x468+. Bottom y472 black -> y473 (54,76,76) -> texture.
Ours paints a flat (120,120,120) 1px rect (kLane) at the COSMOSWnd outset —
no recess. LAW: dark inner shadow ramp between texture band and field.
## F6 — dial cluster: art is correct, recesses are chrome [vision]
4x2 grid; ours blits the right dial faces (rotation arrows, cone, toggle
glyphs) but (a) skip-pixels wash them (F2) and (b) the dark round recesses
with rims are part of the unidentified background chrome record (t400 seam)
— ours has TV-static behind them instead. Blend fix + F4 mottle closes the
visible delta; the recess art itself stays a named seam.
## F7 — pip depth: vendor pips 41 blobs median 9 px (1..20+), ours 45 blobs
median 13 (5..20+); sizes vary in both. Vendor ALSO varies BRIGHTNESS
(vision). Port depthClass already bands z; add monotone luminance dimming
by depth class (display-only, zero rng) so near stars are brighter.

## F8 — fixes landed + witness PASS [measured 2026-11-16]
1. vendortext.cpp blitShapeScaled: SDL_SetTextureBlendMode(BLENDMODE_BLEND)
   on the shape texture (F2). Witness census: pale(146,178,134) px 3340 -> 0.
2. mapchrome.cpp textureColourAt: 6x6-cell mottle (F4). Witness lag-1 on
   OUR shot: 1.45 -> 0.22 (vendor 0.23). Sweep scripts/t411_mottle.py.
3. ui.cpp cosmos frame: two-line dark recess kBevelMid(49,54,53)/
   kBevelIn(5,6,6) in mapchrome.h (F5). Witness pixel (240,7): 136 -> 5.
4. cam3d pipDim256 {96,160,224,256} far->near wired into pip paint (F7);
   native-vision grade of work/r1/loop/t411-map.png: green outline-ring
   digits "0 0 0 0 0" (MATCHES vendor day-0 style), dim stars visible,
   mottled sidebar, no pale wash, recessed field, home ring + 2 lanes.
   Digit-slot green now 0.20/slot vs vendor 0.14-0.17 (was 0.63).
PINS tests/test_maplook_t411.cpp x3 (mottle cell law incl non-power-of-2
boundary probe, depth-dim monotone+domain, bevel verbatim+ramp contract).
Suite 391 -> 394, 0 failed.

## F9 — MUTATION campaign scripts/t411_mutate.py (background + restore-guard,
per the t410 F6 pitfall) [measured]
M1 cell 6->4 CAUGHT (8014 fails) | M2 cell 6->8 CAUGHT (4882) | M3 per-pixel
CAUGHT (10842) | M4 ramp reversed CAUGHT | M5 far unscaled CAUGHT | M6 near
scaled CAUGHT | M7 out-of-domain 0 CAUGHT | M8 bevel brightened CAUGHT |
M9 bevel no-ramp CAUGHT — 9/9 pin-caught. M10 (blend-mode line removed)
MISSED AS EXPECTED AND HONESTLY RECORDED: it is SDL wiring, no pure-law pin
can see it; the WITNESS catches it (pale census 0 -> 3340). AFTER-RESTORE
394/0.

## F10 — dial walk (queue item 6) [measured, witness]
11 "ui cam yaw" lines (7 movers x clicks + TogLanes + baseline) and exactly
3 "map-ctl seam" lines (TogEmpire/TogShips/TogColonies, the named no-overlay
seam). Controls respond; nothing silently dead.

## F11 — LEDGER — HONEST NEGATIVE (strict-close)
NO OQ row moved: the D13 map-look complaint has no ledger owner (same
disposition as t408/t409/t410). Evidence lives here + docs/re/
t399-galaxy-map-3d.md §7. Open seams after this pass: (S-a) texture/recess
pattern SOURCE record (t400, decider unchanged); (S-b) home-marker ART (the
vendor capsule emblem; ours stays the square ring); (S-c) pip brightness
TABLE values (law measured, ramp documented; cos_star unreadable OQ-005);
(S-d) 3 overlay toggles need overlay layers. SEED REGRESSION seeds 1/2024/23
md5 7e794a6d/332a8cf3/0a6b7876 == record EXACTLY (display-only changes, zero
rng). GATE_EXIT=0; ledger audit OK; index check OK (17 closed/3 open).
