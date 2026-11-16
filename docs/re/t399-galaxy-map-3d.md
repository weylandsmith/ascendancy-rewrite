# t399 — GALAXY MAP 3D FIELD: vendor projection law + port implementation

D11 headline FAIL addressed: "The galaxy map itself is all wrong - it should
be a 3d field of colored points that can be rotated and zoomed by the
controls near the lower right... The number of points (stars) show in the
rewrite is the wrong number... At the beginning of the game, the only lines
shown should be the star lanes that lead off from your home system... It's
not possible to find the player's home star... the day counter... the
original has large green numbers" (docs/DECISIONS.md:299).

## 1. VENDOR PROJECTION LAW [verified, capstone on work/ascend_restored.bin
## base-0; scripts/t399_disasm.py (tracked)]
- FUN_00053324 (0x53324..0x53373): affine 3x4 float transform of the star's
  f32[x,y,z] (name-0x14 field, sphere law r1-savestate.md OQ-012(c)).
  out.r = m[row]*v + m[row+0xc] per row (rows at m+0x00/0x10/0x20) — the
  camera matrix. eax=&v, edx=&m, ebx=&out.
- FUN_00053374 (0x53374..0x533da): PERSPECTIVE projection to screen words:
  outX = frndint(v.x * zoom / v.z + K) + originX (fdiv [eax+8] = pinhole
  1/z; call 0x76e08 = frndint nearest per t199; s16 stores; zoom f32 =
  COSMOSWnd+0x102 at call sites; origins = hi16 of qwords @wnd+0x574/+0x576).
- Paint loop FUN_000284bc (work/coswnd_decomp/284bc.c): kind 0 (star)
  transforms via 0x53324, gates on a z-window (wnd+0x106 < z' < wnd+0x10a),
  projects via 0x53374, THEN stores transformed z at node+0xd — which the
  t200 selector ladder (docs/re/planets-ui.md §6, thresholds ±0xdc) bands
  into cls 0..3, so SEL = 4*type + cls picks a DEPTH-CLASS pip. That is the
  mechanical explanation of the original's "points of varying size/
  brightness" (vision read). kind 1 (lane): both endpoints projected,
  node+0xd = (z1+z2)*f32@0xfd4 (midpoint depth), line only when BOTH z' in
  gate. Stars are ALWAYS listed (builder kind-0 unconditional, ships.md S23
  L9) — star count on screen == galaxy star count is the vendor law, not a
  port choice.
- [unverified] constants: K @ds:0x2c50 and the ladder offset f32@ds:0x105e
  are relocation-patched (restored-image bytes are not valid floats —
  measured). Port uses centre-screen and offset 0 (documented defaults).

## 2. STAR DEPTH IN THE PORT (no-engine-RNG law holds)
game/mapgen.h Star.z added. Value = splitmix64(seed, slot) uniform-marginal
over [-r_shell, +r_shell] (matches the measured sphere z distribution;
xy stays the documented 2D hybrid). PROOF the engine stream is untouched:
`--headless --campaign 120 --seed 1` log byte-identical before/after
(md5 6f8281d078447b0dd036e1d27c7c3578 both runs — [verified]).

## 3. PORT CAMERA + DRAW LAW (ui/cam3d.{h,cpp}, wired in ui.cpp)
- Camera3d{yaw,pitch,focal}; pinhole projectStar per the vendor law;
  rotate/tilt/zoom/reset driven by the CITED cluster rects (mapchrome.cpp
  msg 50..56); TOGLANES toggles the lane layer; TOGEMPIRE/TOGSHIPS/
  TOGCOLONIES stay named seams (no overlay layers exist yet). Per-click
  step kRotStep=0.25 rad, zoom x1.25 clamped [340,2720]: DOCUMENTED
  DEFAULTS (vendor spin increments are runtime state; help.txt 1spin
  "right mouse = continuous" not implemented — seam).
- Fit law (measured by the bounds pin): standoff 1760 (4x outer shell),
  focal default 680 keeps the whole 50-star field inside COSMOSWnd
  (max |x'| = round(440*680/1320) = 227 <= 229 half-width); field clip
  rect added so zoomed stars never paint the rail.
- LANES: drawn iff Campaign::laneVisibleTo(lane, kPlayer) — the CITED t192
  law (empire sees lanes incident to owned stars; SA_KnowStarLanes widens).
  At turn 1 that is exactly the lanes leading off the home system(s). The
  old code drew ALL lanes (the D11 "random-shaped lines" defect).
- STARS: all stars, depth-sorted far->near, pip radius by depthClass
  (±220 ladder) monotone with nearness, neutral tint by star type (13-row
  PORT palette — vendor pips unreadable until OQ-005; documented), owners
  kOwnerRgb (CVD law preserved: size AND colour).
- HOME STAR: Campaign::homeStarFor(owner) accessor added; the player's
  home renders with a white square ring [named seam shape — vendor marker
  record unmapped; vision read confirms a distinct marker exists].
- HIT TEST: hitStarCam uses projected positions (click what you see).
- DAY COUNTER: t394 named seam CLOSED by measurement (scripts/
  t399_digit_faces.py decodes 1starmap k55..k64 through the project's own
  RLE grammar): IDENTITY digit->frame law; mechanical discriminator = k56
  uniquely narrow (w=18 vs >=24 all others) and reads '1'. Faces blit as
  VENDOR ART 1:1 through game.pal at the cited slot x's (482/513/544/575/
  606), clipped to the panel; oval outlines REMOVED; fallback = big
  VendorText green (never ovals-with-tiny-text).

## 4. WITNESS [measured, /tmp/t399_shots/map.png via t398_palette_witness.sh]
External vision read of the new map: ~60-70 visible star points in
multiple colours; BOTH visible lane lines touch the boxed home star (no
orphan lanes); home star marked; day box shows FIVE blocky green zero
glyphs, no clipping, green frame. Pre-fix shot contrast: ovals + tiny
digits + full lane mesh.

## 5. PINS + MUTATION
8 new tests tests/test_cam3d_t399.cpp: pinhole arithmetic (centre + 440->
+170px), determinism (100x), zoom clamp/rot wrap, FULL-FIELD bounds inside
COSMOSWnd, Star.z law (deterministic, |z|<=shell r, >25 nonzero, seed-
sensitive), depth ladder at ±220 edges, tint domain, digit identity +
k56-uniqueness on the REAL 1starmap.shp, home-star + turn-1 lane-visibility
law on a seeded campaign (every visible lane touches a player star; every
home-incident lane visible). MUTATION 3/3 CAUGHT (digit frame 55->54;
focal 680->900; ladder 220->221), clean revert. Suite 322->330, 0 failed;
gate 0; seed-1 trajectory byte-identical (above).

## 6. WHAT STAYS OPEN (honest)
- Vendor camera MATRIX values / z-window / continuous-drag: runtime state,
  not in any extracted file or save corpus — port law documented, not
  copied. A live-R1 capture of a running cosmos window (camera words at
  COSMOSWnd+0x102/0x106/0x10a/0x574/0x576 + the matrix buffer) would close
  it; queued behind t400-t402 per STATE.
- Home-marker shape, neutral pip art (OQ-005 family), per-click rotation
  quantum: named seams above.
- 3D lane z-gate: port standoff makes it vacuous (stated, not hidden).
- No ledger row closed this iteration (strict-close; queue work t399).
  OQ-012/OQ-005 notes unchanged — the digit seam was never a ledger row.

## 7. t411 MAP LOOK PASS 2 (amendments, 2026-11-16) [measured]
- TRANSPARENCY LAW (vendortext.cpp blitShapeScaled): SDL shape textures
  default to BLENDMODE_NONE which IGNORES the alpha byte; the .shp
  transparent-skip pixels kept the 0xAA decode-stuffer and painted
  game.pal[170] (146,178,134) opaque pale sage — 3340 such px on the map
  screen (washed digit faces, dial faces, rail bands). Fix: set
  SDL_BLENDMODE_BLEND on every blitShape texture (skip = dst untouched,
  matching the vendor blit). Witness census pale px == 0.
- TEXTURE PATTERN (mapchrome.cpp): the vendor sidebar band is SMOOTH at
  pixel scale (lag-1 diff/dev 0.23); the per-pixel hash measured 1.45 (TV
  static). Port now generates the cited colour set + weights on a 6x6 cell
  grid — scripts/t411_mottle.py sweeps the generator's own statistic
  (cell 1:1.57, 2:0.78, 4:0.38, 6:0.25, 8:0.19; vendor 0.23). Pattern
  SOURCE record seam stands (t400).
- COSMOS BEVEL (mapchrome.h kBevelMid/kBevelIn): the field sits in a dark
  recess — texture ramps down to near-black at the edge all four sides
  (scans in _wip_t411 F5). Two-line port ramp replaces the flat
  (120,120,120) frame line.
- DEPTH DIM (cam3d pipDim256 {96,160,224,256} far->near): vendor pips vary
  in BRIGHTNESS with distance (vision + blob census: sizes 1..20+ with
  dim members). Ramp values documented defaults (cos_star unreadable,
  OQ-005); the monotone law is measured.
- Day-counter binding CONFIRMED (not a defect): the vendor at day 0 shows
  five outline-ring ZERO faces — ours binds camp.turn() to kDigitFirstFrame
  +d correctly; the "empty ovals" complaint was the pale-skip wash above.
  Slot green fraction now 0.20 vs vendor 0.14-0.17 (was 0.63).
- Dial wiring witness: 8 cluster clicks print the cam line (7 movers +
  TogLanes), the 3 overlay toggles print the named-seam line x3
  (scripts/t411_maplook_witness.sh dial walk).
