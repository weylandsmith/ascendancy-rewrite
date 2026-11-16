// SPDX-License-Identifier: GPL-3.0-or-later

#pragma once
// t399 — 3D cosmos camera (D11 ruling: "a 3d field of colored points that
// can be rotated and zoomed by the controls near the lower right").
// Pure math (no SDL) so it is unit-testable: tests/test_cam3d_t399.cpp.
//
// VENDOR LAW (cited, docs/re/_wip_t399.md):
//   FUN_00053324 (0x53324) applies a 3x4 float affine to each star's
//   f32[x,y,z] (name-0x14, sphere law r1-savestate OQ-012(c));
//   FUN_00053374 (0x53374) projects camera-space to screen:
//     sx = round(x * zoom / z + K) + originX   (fdiv [eax+8] = pinhole;
//     call 0x76e08 = frndint nearest; s16 stores; zoom = COSMOSWnd+0x102).
//   Paint loop FUN_000284bc gates on a z-window and stores the TRANSFORMED
//   depth at node+0xd, which the t200 selector ladder bands at ±0xdc
//   (SEL = 4*type + cls, docs/re/planets-ui.md §6) -> depth-scaled pips.
// PORT LAW (documented defaults where the vendor value was never captured):
//   camera stands kStandoff units out along +z from the field centre
//   (vendor D and the z-window bounds are runtime state, [unverified]);
//   yaw/pitch rotate the FIELD (equivalently the camera); per-click step
//   kRotStep is a documented default (vendor spin increments are runtime
//   state; help.txt 1spin: right mouse = continuous — NOT implemented);
//   the ladder offset f32@ds:0x105e is relocation-patched ([unverified]) so
//   the port uses offset 0; K (ds:0x2c50) likewise -> screen centre.

#include "game/mapgen.h"
#include "ui/layout.h"

namespace ascend::ui {

struct Camera3d {
    double yaw = 0.0;     // rad about the field z-axis (spin left/right)
    double pitch = 0.0;   // rad about the screen x-axis (spin up/down)
    // ZOOM analogue; zoom clicks scale by kZoomStep. DEFAULT FIT LAW
    // (measured by the bounds pin): the nearest field plane is
    // kStandoff - 440 = 1320 deep; the outer shell r=440 must project
    // inside the COSMOSWnd half-width 229 px -> focal <= 229*1320/440 =
    // 687. 680 keeps the whole galaxy on-window at zoom 1 (t399 D11:
    // "number of points ... should be the number of stars in the galaxy").
    double focal = 680.0;
    int mapSize = 1024;    // MapConfig.mapSize (Star x/y grid)
    Rect bounds = kCosmosWnd;

    static constexpr double kStandoff = 1760.0;  // 4x outer shell r=440
    static constexpr double kZoomStep = 1.25;
    static constexpr double kFocalMin = 340.0, kFocalMax = 2720.0;
    static constexpr double kRotStep = 0.25;
    static constexpr double kPitchLimit = 1.5;   // just under pi/2

    void rotate(int dir);  // yaw += dir*kRotStep (wraps)
    void tilt(int dir);    // pitch clamped to [-kPitchLimit, kPitchLimit]
    void zoom(int dir);    // focal *= kZoomStep^dir, clamped
    void reset();          // CENTERHOLO: yaw=pitch=0, focal default
};

// Camera-space depth along the view axis (always >= kStandoff - 440 > 0 for
// legal fields; NO z-culling needed in the port — the vendor z-window gate
// stays vacuous at this standoff, which is stated, not hidden).
double viewDepth(const Camera3d& cam, const ascend::game::Star& s);

// Perspective project a star to screen px inside cam.bounds (documented
// centre = bounds centre; y grows downward like SDL).
Pt projectStar(const Camera3d& cam, const ascend::game::Star& s);

// Vendor 4-band ladder on the transformed z (planets-ui.md §6 thresholds
// ±0xdc == ±220): v >= 220 -> 0 (far), 1..219 -> 1, -220..0 -> 2, below -> 3
// (near). Port v = camera-space z MINUS the standoff (pure field depth).
int depthClass(double fieldZ);

// Pip radius by depth class (documented port default; the vendor cos_star
// pips are dims-zero/unreadable until OQ-005, so sizes come from the port,
// monotone non-decreasing with nearness).
int pipRadius(int cls, bool owned);

// t411 DEPTH DIM: 256ths brightness multiplier per depth class, monotone
// non-decreasing with nearness (law measured on the vendor original: pips
// dim with distance; ramp values documented port defaults).
int pipDim256(int cls);

// Neutral-star tint by star type (13 rows). PORT PALETTE [documented]: the
// vendor pip art is unreadable (OQ-005); hues follow the user-supplied
// original's red/yellow/blue/white point families (external vision read,
// scratchpad/galaxymap-original.png) and deliberately avoid pure green so
// neutrals never read as the green day-counter chrome.
RGB neutralTint(int starType);

// Digit-face law (t399, scripts/t399_digit_faces.py): digit d renders from
// 1starmap frame kDigitFirstFrame + d (IDENTITY; mechanical discriminator:
// k56 is uniquely the narrow face, width 18 vs >= 24 for all others).
inline constexpr int kDigitFirstFrame = 55;

// Nearest star within `radius` px of p using the CURRENT camera projection.
int hitStarCam(const Camera3d& cam, const ascend::game::Galaxy& g, Pt p,
               int radius = 6);

}  // namespace ascend::ui
