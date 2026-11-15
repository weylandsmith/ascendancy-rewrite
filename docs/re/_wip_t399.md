# t399 WIP — GALAXY MAP 3D FIELD (D11 headline FAIL)

## Task (STATE.md NEXT ACTION)
D11 galaxy-map ruling (DECISIONS.md:299): "should be a 3d field of colored
points that can be rotated and zoomed by the controls near the lower right...
number of points (stars) show in the rewrite is the wrong number, it should be
the number of stars in the galaxy. At the beginning of the game, the only
lines shown should be the star lanes that lead off from your home system...
not possible to find the player's home star... day counter has large green
numbers, you have green circles with smaller numbers inside".

## Wake procedure results
- Ruling page server LIVE on 8613 (pid 646702). DECISIONS.md mtime 11:40:57,
  newest USER block 11:37:07 = the D11 ruling already applied by t397b/t398
  sessions — NO new rulings since.
- Sitting check NEGATIVE: live-timeline.jsonl mtime 2026-11-12 06:45 (size
  9,385,663,364 B), unchanged since prior iterations -> r1_t85g_sitting.py
  NOT re-run.

## Evidence assembled this session (all pre-existing, re-cited)
1. STAR COUNT DEFAULT: vendor cosmos.txt (`extracted/ascend00/cosmos.txt`) =
   `STARS 50 / RACES 5 / SEED -1` — the shipped default galaxy is 50 stars;
   matches our MapConfig.starCount=50 (r1-savestate.md 2026-10-06p 5/5
   fresh campaigns). [verified]
2. 3D POSITIONS ARE REAL: star runtime records carry name-0x14 f32[x,y,z]
   over a sphere (r1-savestate.md OQ-012(c)/(d): shell radii 440/365/290/
   215/140/65/50 by table slot, random unit-vector direction, z distribution
   consistent with uniform-on-sphere). Our sim keeps the documented 2D hybrid
   (mapgen.md §4.1: xy-plane radius = shell radius directly) — CHANGING xy
   would break the seeded trajectory regression, so the 3D field must be
   UI-side with a z law that consumes NO engine rng (queue pin: "no-engine-RNG
   rule holds"; precedent: visLcg_ separate-stream pattern, campaign.h:721).
3. STAR PIP SELECTOR LAW (t200, planets-ui.md §6): cos_star.shp
   (extracted/ascend01/data/cos_star.shp, 55 records) is painted via
   SEL = 4*K + cls, K = star type index 0..12, cls = 4-band ladder on
   v = frndint(f32[star+0xd] + f32@0x105e) with thresholds ±0xdc. k40..k51
   (types 10..12) are dims-zero in the FILE (vendor-empty, t200 §4);
   k52..k54 unaddressable. cls semantics NOT cited (depth band suspected)
   -> named seam.
4. LANE VISIBILITY LAW (t192/t193/t195, ships.md S23, abilities.md): empire
   sees lanes incident to stars it owns; SA_KnowStarLanes ORs every lane;
   OR-only sticky. Already implemented as Campaign::laneVisibleTo(lane,viewer)
   (campaign.cpp:457) — the UI draw loop IGNORES it (ui.cpp draws all lanes;
   this is the "apparently-random-shaped lines" defect plus the home-lanes
   law violation in one site).
5. MAP CONTROLS ALREADY CITED: kMapCtl (mapchrome.cpp) ROTRIGHT msg51 /
   ROTLEFT msg50 / ROTUP msg52 / ROTDOWN msg53 / ZOOMOUT msg55 / ZOOMIN msg54
   / CENTERHOLO msg56 / TOGLANES msg57... windows.txt ln223-396. Clicks
   currently print "map-ctl seam" (ui.cpp ~line 245) — the camera state to
   drive is what's missing. help.txt 1spin (extracted/ascend00/help.txt
   :211-221): "This button will let you manipulate the Galactic Display. Use
   the right mouse button if you want to zoom or rotate continuously."
   -> continuous-rotate is vendor; per-click step is our documented default.
6. TURNCOUNT DIGITS: t394 anchors — panel 474,7-632,43, five oval slots x
   482/513/544/575/606 pitch 31 (y10..39), DIGITFRAMES 55 => digit FACES are
   1starmap k55..k64; frame->digit mapping was a NAMED SEAM. User ruling +
   external vision read of scratchpad/galaxymap-original.png: "large, bright
   green, blocky numbers", five digits, dark box thin green border. Current
   code draws oval OUTLINES + small text digits (ui.cpp ~line 366) — the
   exact defect. Candidate fix: blit k55+d faces (vendor art, large) at the
   cited oval slots; verify mapping by WIDTH census (a '1' face should be
   narrower) else fall back to VendorText big-face in green.
7. ORIGINAL MAP LOOK (vision read 2026-11-15 of scratchpad/galaxymap-original
   .png): stars = points of varying COLOR (red/yellow/blue/white) and varying
   size/brightness; thin white lane lines radiating from the SELECTED star;
   a small green icon top-left of the map (home marker? unverified); frame =
   textured bevel border.
8. HOME STAR: Campaign::homeStar_ per owner (campaign.h:698) — private; need
   accessor (check if one exists) for the visual-distinct pin.

## VENDOR 3D PROJECTION LAW [verified this session, capstone on
## work/ascend_restored.bin base-0; scripts/t399_disasm.py]
FUN_00053324 (0x53324..0x53373) = AFFINE 3x4 FLOAT TRANSFORM:
  out.x = m[0x00]*v.x + m[0x04]*v.y + m[0x08]*v.z + m[0x0c]
  out.y = m[0x10..0x1c] row;  out.z = m[0x20..0x2c] row
  (eax=&v f32[3], edx=&m 0x30 B, ebx=&out f32[3]) — the camera matrix.
FUN_00053374 (0x53374..0x533da) = PERSPECTIVE PROJECTION TO SCREEN:
  outX = round(v.x * zoom / v.z + K) + originX ; outY likewise (v.y)
  (eax=&v f32[3] CAMERA-SPACE; [esp+0x18]=zoom f32 = COSMOSWnd+0x102 at the
  call sites; fdiv [eax+8] = 1/z is THE pinhole; call 0x76e08 = frndint
  nearest per t199; s16 stores; origins = hi16 of qwords @wnd+0x574/+0x576).
CALL SHAPE in the paint loop FUN_000284bc (work/coswnd_decomp/284bc.c):
  kind 0 (star): transform via 0x53324, z-range gate (wnd+0x106 < z' <
  wnd+0x10a), project via 0x53374, THEN *(float*)(node+0xd) = transformed z
  -> the t200 cls ladder bands THE TRANSFORMED DEPTH (±0xdc): far band cls0,
  mid cls1, near-neg cls2, very-near cls3 => SEL=4*type+cls picks the
  depth-scaled pip. This EXPLAINS the vision-read "varying size/brightness".
  kind 1 (lane): both endpoints projected; node+0xd = (z1+z2)*f32@0xfd4
  (midpoint depth); lane line only when BOTH endpoints inside z-gate.
  K @ds:0x2c50 and f32@ds:0x105e: bytes in the restored image are NOT valid
  floats (relocation-patched at load; [unverified] values) — the port centers
  at the bounds centre instead of K (documented), and uses offset 0 in the
  cls ladder (documented default).
PORT LAW (cam3d): P_cam = Ryaw then Rpitch applied to (star - centre) with
star z from the measured sphere law; screen = P_cam.xy * zoom / (P_cam.z + D)
+ centre (D = camera stand-off so z+D>0 always; named constant). Rotation
INCREMENT per spin click is vendor runtime state never extracted ->
documented default step; continuous right-drag NOT implemented this row.

## DIGIT FACE LAW [measured this session, scripts/t399_digit_faces.py]
1starmap.shp k55..k64 decode cleanly (RLE per shp.h): 24/18/24/24/24/25/25/
28/24/24 px wide, ~33 tall. ASCII art reads IDENTITY mapping frame->digit:
k55='0' k56='1' ... k64='9'. MECHANICAL DISCRIMINATOR (vacuity-safe): k56
width 18 is UNIQUELY narrow (all others >= 24) and its art is a single
stem+base — the only glyph that can be '1'. k64 h=35 (tail descender of the
9). This CLOSES the t394 named seam ("digit->frame mapping uncited") for the
turn counter: blit k55+d at the cited oval slots (482/513/544/575/606,
y10..39), game.pal paints the vendor green. Fallback when lib absent:
VendorText big face, green — never ovals-with-tiny-text.

## Implementation map (this iteration)
- game/mapgen: Star.z added (int), z = splitmix64(seed,slot) scaled to
  [-r_shell, r_shell]; NO rng_ draw (seed-regression safety).
- NEW ui/cam3d.{h,cpp}: Camera{yaw,pitch,focal} + project(star)->screen Pt
  inside bounds + depthClass(v) implementing the ±0xdc ladder (offset 0 =
  documented; value [unverified]); neutralTint(type) = documented CVD-safe
  port table (cos_star pips unreadable until OQ-005); digitFrame(d)=55+d.
- ui.cpp: camera state + map-ctl wiring (ROTLEFT/RIGHT yaw, ROTUP/DOWN
  pitch, ZOOM x1.25 clamped, CENTERHOLO reset, TOGLANES toggles lanes);
  lanes gated by Campaign::laneVisibleTo(lane, kPlayer) (t192 law) AND
  lanes-on; stars = ALL stars, depth-scaled pips, neutral type tint,
  owner kOwnerRgb, HOME star ringed (accessor Campaign::homeStarFor —
  marker shape itself = named seam); day counter per DIGIT LAW; hit-test
  via projected positions.
- tests/test_cam3d_t399.cpp: determinism, bounds-inside-COSMOSWnd, z law
  (deterministic, |z|<=shellR, no rng), digit identity + k56-uniqueness
  (REQUIRE_DATA), depth ladder monotonic.

- Star.z WITHOUT touching engine rng: gate 3l seed regression is byte-
  identical, so mapgen MUST NOT consume new rng_ draws. z = splitmix64(seed,
  slot) uniform-marginal in [-r_shell, +r_shell] — consistent with the
  measured uniform-on-sphere z distribution [r1-savestate OQ-012(c)], pure
  function of data already drawn. xy stays the documented 2D hybrid.
- z per star: deterministic splitmix64(seed, slot) mapped to the star's
  shell-radius band, uniform-marginal like the measured law; stored as int z
  on Star; sim consumers untouched (dist2/lanes stay xy). NO rng_ consumption
  -> seeded trajectories byte-identical (verify gate 3l + spot check).
- Camera: yaw/pitch/zoom in a pure struct (new file ui/cam3d.{h,cpp}),
  orthographic project into kCosmosWnd; rotation = yaw about z then pitch
  about x; zoom scales. Vendor rotation increments NOT cited -> named seam
  (per-click step + right-drag continuous optional).
- Draw law changes in ui.cpp map block: lanes drawn iff laneVisibleTo(lane,0)
  (cited t192) and lanes toggle on; stars = ALL galaxy stars (count pin);
  neutral star tint varies by type (cos_star blit if it paints through
  blitShape/gamepal, else named-seam tint table); owner stars keep kOwnerRgb
  (CVD law); home star gets cited-elsewhere? -> ring marker, named seam.
- Day counter: replace ovals+small-text with large green digits per §6.
