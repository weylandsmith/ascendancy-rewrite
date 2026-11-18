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

## §8 t416 DIAL LAW SUPERSEDES §"PORT LAW" yaw/pitch EULER (2026-11-17)
The vendor map dials are NOT per-click Euler steps. Press law (COSMOSWnd
handler 0x26b34, latch chain 0x27da2..0x279eb on wnd+0xc0): a dial press
latches (active, direction) — click starts CONTINUOUS motion, click again
stops, the opposite dial flips direction. The periodic pump (msg 0x3b,
0x27a18; live ~1/s t302) applies per latched pair: spin pair +/-2 DEG
about WORLD Y (FUN_000283e4 edx=-1 -> FUN_00053584 -> per-vector
FUN_0005324c mix x'=x*c+z*s, z'=z*c-x*s), tilt pair +/-2 DEG about WORLD
X (edx=0 -> FUN_00053554 -> FUN_000531dc y'=y*c-z*s, z'=z*c+y*s), zoom
pair FUN_00028428 (accumulator, runtime bounds + hard [1,100000]). The
rotated struct at wnd+0x14e is a camera BASIS (up, fwd; right =
cross(up,fwd) recomputed by FUN_00053804 every rotation). Recenter
FUN_00026a9c rest values [verified immediates]: right(1,0,0) up(0,1,0)
fwd(0,0,1), zoom 35.0, position (0,0,-1500). NO clamp on rotation.
Signs verbatim: msg 50 ROTLEFT +2, 51 ROTRIGHT -2, 52 ROTUP -2,
53 ROTDOWN +2. Delta args are degrees (deg2rad f32@0x88b88).
Because the vendor rest view axis is world z and its spin axis world Y,
the spin reads as IN-PLANE rotation at rest (the user's "rotate about Z").
The port (cam3d.{h,cpp}) now models this basis directly; the depth ladder
follows the TRANSFORMED depth (node+0xd law). Full working log:
docs/re/_wip_t416.md F1-F3.

## t425b — RACE FILTER FACE LAW + S-f HONEST NEGATIVE (2026-11-18)

Hand-authored (no script writes this file; grep scripts/ for the name = 0 hits).
Working log: docs/re/_wip_t425.md F3-F6. Census tool: scripts/t425b_face_census.py.

FACE FAMILY LAW [measured, 1starmap.shp canonical rowwalk S16/S17]: filter
slot i (windows.txt RACE<N>CONTROL, rect 479+22i..495+22i / 449..465) owns
FIVE records at base = 20 + 5i:
  +0 16x16 dark tone      +1 16x16 brighter tone
  +2 17x17 dark + idx103 OUTLINE   +3 17x17 brighter + outline
  +4 16x16 GREY (idx0/idx6 neutral)
Tone pairs 16/19, 20/23, 24/27, 28/31, 32/35, 36/39, 40/43 — all seven glyphs
structurally IDENTICAL, only the palette pair differs, so the slot colour IS
the species colour. VISIBLE = +2 / FILTERED = +4 per the vendor's own help
(ascend00/help.txt ln370-373, HELPINDEX rcontrol, verbatim): "Only information
pertaining to the species whose colors are OUTLINED will be displayed."
Measured over the 17x17 rect on the k19 stride backdrop: visible mean lum
82.8..149.8 and CHROMATIC per slot; hidden 23.2 NEUTRAL — on/off encodes hue
+ outline AND luminance, so the vendor art satisfies the CVD law by itself.
Code: rewrite/src/ui/mapchrome.h kRaceSlotFrameBase/Visible/Hidden; paint site
ui.cpp (blitShape through game.pal; kOwnerRgb fill kept ONLY as the data-less
degradation). Pin mapctl_t425b_face_family_five_records_per_slot, mutation
verified +2->+0 and +4->+3 (7 fails each). Witness
scripts/t425_mapctl_witness.sh PASS: slot5 chroma 35.6->0.2, lum 88.3->22.5,
slot1 chroma unchanged 101.8.

REFUTED (two compounding cycle-1 errors, kept so nobody re-walks them):
(1) the "(89,24,56) refcap slot" was NOT the strip — original-strategic-map.png
rows are game rows + 40, so the strip (game y 442..472) is OUTSIDE the 640x480
shot; the maroon blobs measured are the three BUTTONSTATE-1 toggle buttons
(components x 479-509 / 557-587 / 596-626) plus the navy BUTTONSTATE-0 slot.
(2) (89,24,56) IS in game.pal: idx 80 raw (22,6,14) converted via
c=(v<<2)|(v>>4) — cycle 1 compared pixels against the RAW 6-bit table. There is
NO runtime palette for this screen (palette.md S3: 307200/307200 px inside the
CONVERTED table). BONUS LAW from the same components: TYPE-25 toggle faces
SHAPEFRAME 15/16/17/18 read fill idx80 (ON) vs idx242 (OFF).

S-f (filter -> owner/colour) HONEST NEGATIVE, row stays open: the d8 consumer
at 0x29976..0x29998 skips race i when the bit is clear, then reads race-record
BYTE +2 and indexes the colour table with 0x10 + 4*byte (data-driven, NOT
"slot i == owner i"). Live-RAM census over 20 slots (pointer law B+0x82bb0+X,
B=0x1bf4d8; scripts/t425b_race_colour.py + t425b_race_probe.py): row base
VALIDATED by independent anchors (byte +0 == race index i rows 0..4, relation
diagonal [+0x1b2+2i] == 0, [0x13b98]=4, [0x7458e]=0); byte +2 = [0,1,6,2,1] —
NON-INJECTIVE, so it is not a colour permutation, and the paint-site table at
[esp+0x38] plus that loop's row origin (bound 0xd82) are UNRESOLVED. The port
keeps slot i == owner index i and the seam note says so.

## t425c — TOGGLE WELL LAW MEASURED BIT-EXACT + SLOT COLOUR IS OCCUPANT DATA
Hand-authored (no script writes this file). Working log docs/re/_wip_t425.md
F7-F10. Tools: scripts/t425c_toggle_state_law.py (the pin-grade measurement),
t425c_slot_faces.py (second shot), t425c_circle_census.py /
t425c_button_measure.py / t425c_face_diff.py / t425c_shift_sweep.py (censuses).

THE LAW [verified 900/900 bit-exact x4, zero residual pixels]: a TYPE-25
layer toggle blits its SHAPEFRAME (1starmap k15..k18) at its verbatim rect and
substitutes ONE palette entry by state — face well idx242 (raw (3,8,12) ->
conv (12,32,48) navy) renders as idx80 (raw (22,6,14) -> conv (89,24,56)
maroon) when the layer is ON, and stays 242 when OFF. Measured on
docs/assets/refcap/original-strategic-map.png at png = screen + 40 (that png's
rows 0..39 are pure black and the TURNCOUNT digits 474,7-632,43 land at png
y52..80): TOGLANES/TOGSHIPS/TOGCOLONIES (BUTTONSTATE 1) are exact under the
swap, TOGEMPIRE (BUTTONSTATE 0) is exact raw. Three independent sources name
each button's state (windows.txt BUTTONSTATE, the refcap well colour, handler
init 0x2718c) and all three agree, which is what makes a 4/4 exact result
possible from ONE capture. NEGATIVE CONTROL: the spin/zoom row is not
state-painted — the same swap degrades it 74.6% -> 21.5%.
Code: ui_internal.h/vendortext.cpp blitShapePalSwap (blitShape + one index
substitution); paint site ui.cpp step 3 gates on i >= MapCtl::TogLanes and
passes on ? kToggleWellOnIdx : kToggleWellIdx. Constants mapchrome.h
kToggleWellIdx=242 / kToggleWellOnIdx=80. Pins test_mapwell_t425c.cpp x3
(palette colours named, well dominance 577..647 of 900 in every face + glyph
survival, default-state -> colour prediction), mutation-verified: ON idx
80->81 fails 4, well idx 242->200 fails 6. Witness PASS adds togships well
maroon 647->0 / navy 0->647 and togempire 0->644 / 644->0 — the port's
swap-able pixel counts equal the vendor faces' well counts exactly.

RACE SLOTS (second shot only) [geometry verified, colour a NAMED SEAM]:
scratchpad/galaxymap-original.png (642x481, identity mapping) is the only
vendor capture containing the strip. Each slot's best match over all five
family members x 49 offsets is the +2 OUTLINED member at dx0/dy0 (62.3 / 52.6
/ 61.2% for slots 1/6/7; +1/+3/+4 never exceed 13.8%), so t425b's help.txt
VISIBLE=+2 reading holds on real pixels. But the dominant tone in each rect is
idx 16, 24, 20, 32, 28, 36, 40 — the family pair for slots 2<->3 and 4<->5 is
SWAPPED, i.e. [inferred] the vendor draws slot i's GEOMETRY with the COLOUR
PAIR of whichever species occupies slot i (the same substitution mechanism as
the toggles; this is the S-f data-driven colour the t425b RAM probe could not
locate). CAVEAT: that shot is not a pure game.pal render (off-table colours
(95,73,111), (125,121,138) and blends like (0,138,66) between conv idx16 and
idx19), which caps its exact-match percentages and is why the 640x480 refcap
stays the authoritative diff source. The port keeps family-base colours for
slot i; correct only under an identity species order.
