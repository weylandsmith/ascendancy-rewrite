// SPDX-License-Identifier: GPL-3.0-or-later

#pragma once
// t399 — 3D cosmos camera (D11 ruling: "a 3d field of colored points that
// can be rotated and zoomed by the controls near the lower right").
// t416 — DIAL LAW UPGRADE (D15 ruling: "the upper left rotation control
// should rotate the galaxy about the Z axis, but it here seems to rotate it
// around the Y axis"). The t399 yaw/pitch-Euler port was NOT the vendor
// mechanism. Full working log docs/re/_wip_t416.md F1-F2; pins
// tests/test_axis_t416.cpp.
//
// VENDOR LAW (cited; base-0 restored image work/ascend_restored.bin):
//  * COSMOSWnd class handler 0x26b34 (t302 LIVE-witnessed NAME='COSMOSWnd').
//    Dial msgs 50..55 (0x32..0x37, windows.txt SENDMESSAGE per child) do NOT
//    step the camera: they latch an (active, direction) BIT PAIR on
//    wnd+0xc0 (bits 0/1 ROTLEFT/ROTRIGHT, 2/3 ROTUP/ROTDOWN, 4/5
//    ZOOMIN/ZOOMOUT) — press inactive -> active(dir), press same dial ->
//    STOP, press opposite dial -> FLIP dir (chain 0x27d6f..0x279eb).
//  * The periodic pump (msg 0x3b, 0x27a18; t302 measured ~1/s unattended)
//    applies motion per latched pair: spin pair delta = bit1 ? -2 : +2
//    (0x27a28/0x27a32), tilt pair delta = bit3 ? +2 : -2 (0x27a60/0x27a6a),
//    zoom edx = bit5 ? +1 : -1 -> FUN_00028428. Deltas are DEGREES:
//    FUN_000531dc/0x5324c multiply the arg by deg2rad f32@0x88b88
//    (0.017453292).
//  * FUN_000283e4(wnd, edx, delta): edx == -1 -> FUN_00053584 else
//    FUN_00053554, both on the camera basis at wnd+0x14e (vectors +0x14e,
//    +0x15a "up", +0x166 "fwd"; right = cross(up,fwd) recomputed by
//    FUN_00053804 after EVERY rotation). FUN_0005324c mixes (x,z) =
//    RIGHT-HAND ROTATION ABOUT WORLD Y (x' = x*c + z*s, z' = z*c - x*s);
//    FUN_000531dc mixes (y,z) = ABOUT WORLD X (y' = y*c - z*s,
//    z' = z*c + y*s). So the spin pair yaws (up stays world-vertical at
//    rest), the tilt pair pitches; NO clamp anywhere in the rotation path.
//  * Recenter FUN_00026a9c (CENTERHOLO msg 56): zoom accumulator
//    [wnd+0x57a] = 35.0 (0x420c0000), position (0,0,-1500.0) (0xc4bb8000),
//    basis IDENTITY right(1,0,0)/up(0,1,0)/fwd(0,0,1) — immediates verified.
//  * Zoom FUN_00028428: accumulator += edx*scale, latch stops at runtime
//    bounds f32[0xfb0]/f32[0xfb4], hard clamp [1.0, 100000.0] (pushed
//    0x3f800000/0x47c35000 at 0x28494/0x2848f).
//  * Projection unchanged (t399): FUN_00053374 pinhole
//    sx = round(v.x * zoom / v.z + K) + originX on the CAMERA-SPACE vector.
// PORT LAW (documented defaults where the vendor value was runtime-only):
//   camera stands kStandoff units behind the field centre along the view
//   axis (vendor 1500 verified at recenter, but the port fit law needs
//   standoff/focal >= 4; port keeps 1760/680 — adopting 1500 would break
//   the t399 bounds pin; named seam); pump cadence kSpinTickMs (vendor
//   ~1/s measured t302); zoom stays MULTIPLICATIVE per tick (vendor is
//   additive on its accumulator; port focal units differ — documented).
//   Right-drag continuous manipulation (help.txt 1spin ln220) is NOT
//   modeled; the latch above is the click law.
//
// Pure math (no SDL) so it is unit-testable: tests/test_cam3d_t399.cpp,
// tests/test_axis_t416.cpp.

#include "game/mapgen.h"
#include "ui/layout.h"

namespace ascend::ui {

struct Vec3d {
    double x = 0.0, y = 0.0, z = 1.0;
};

struct Camera3d {
    // t416 vendor basis (FUN_00026a9c rest values verbatim): the dials
    // rotate up/fwd about WORLD axes; right = cross(up, fwd) is derived.
    Vec3d up{0.0, 1.0, 0.0};
    Vec3d fwd{0.0, 0.0, 1.0};
    // ZOOM analogue; the zoom latch scales it per pump tick. DEFAULT FIT
    // LAW (measured by the bounds pin): the nearest field plane is
    // kStandoff - 440 = 1320 deep; the outer shell r=440 must project
    // inside the COSMOSWnd half-width 229 px -> focal <= 229*1320/440 =
    // 687. 680 keeps the whole galaxy on-window at zoom 1 (t399 D11:
    // "number of points ... should be the number of stars in the galaxy").
    double focal = 680.0;
    int mapSize = 1024;    // MapConfig.mapSize (Star x/y grid)
    Rect bounds = kCosmosWnd;

    // t416 dial latches (vendor wnd+0xc0 bit pairs): 0 = off, +/-1 = the
    // spin/tilt delta sign the pump applies (ROTLEFT +2, ROTRIGHT -2,
    // ROTUP -2, ROTDOWN +2 — pump 0x27a28/0x27a32/0x27a60/0x27a6a).
    int latchSpin = 0;   // msg 50/51 pair -> rotation about WORLD Y
    int latchTilt = 0;   // msg 52/53 pair -> rotation about WORLD X
    int latchZoom = 0;   // msg 54/55 pair -> zoom

    static constexpr double kStandoff = 1760.0;  // 4x outer shell r=440
    static constexpr double kZoomStep = 1.25;
    static constexpr double kFocalMin = 340.0, kFocalMax = 2720.0;
    static constexpr double kRotStepDeg = 2.0;   // pump delta [verified]
    static constexpr double kDeg2Rad = 0.017453292519943295;
    static constexpr int kSpinTickMs = 250;      // documented cadence default

    // Vendor press law (pure): inactive -> start(dir); same dir -> stop;
    // opposite dir -> flip.
    static int dialLatch(int cur, int dir);
    void pressSpin(int dir) { latchSpin = dialLatch(latchSpin, dir); }
    void pressTilt(int dir) { latchTilt = dialLatch(latchTilt, dir); }
    void pressZoom(int dir) { latchZoom = dialLatch(latchZoom, dir); }

    // One pump tick of the vendor msg-0x3b handler (0x27a18): apply one
    // delta per latched pair. No motion bits -> no-op.
    void tick();
    bool moving() const { return latchSpin != 0 || latchTilt != 0 || latchZoom != 0; }

    void zoom(int dir);    // focal *= kZoomStep^dir, clamped (vendor has
                           // runtime + hard [1,100000] clamps; rotation has NONE)
    void reset();          // CENTERHOLO (0x26a9c): identity basis, latches 0,
                           // zoom accumulator default (port focal default).

    // Derived right vector = cross(up, fwd) (FUN_00053804 law). up/fwd stay
    // orthonormal under the tick rotations (each is an isometry applied to
    // both), so the cross product is already unit length.
    Vec3d right() const;

    // Basis rotations (exposed for pins): right-handed about the WORLD axis
    // by `deg` degrees, applied to up and fwd, exactly like the vendor
    // FUN_0005324c / FUN_000531dc component mixes.
    void rotateBasisY(double deg);
    void rotateBasisX(double deg);

    // Log helpers (the "ui cam yaw ..." witness line keeps its old shape):
    // derived Euler readings of fwd, radians.
    double yawLog() const;    // atan2(fwd.x, fwd.z)
    double pitchLog() const;  // atan2(fwd.y, std::fabs(fwd.z))
};

// Camera-space depth along the view axis: kStandoff + dot(fwd, d). Always
// >= kStandoff - 440 > 0 for legal fields (|d| <= shell radius); NO
// z-culling needed in the port — the vendor z-window gate stays vacuous at
// this standoff, which is stated, not hidden.
double viewDepth(const Camera3d& cam, const ascend::game::Star& s);

// t419 GENERIC field-point projection (the research tree reuses the t416
// basis API on its own field plane; same vendor pinhole FUN_00053374 law as
// projectStar but with raw field coordinates and an explicit standoff instead
// of Star grid units). Field axes match projectStar: x right, y up, depth
// grows with +fwd; screen origin = cam.bounds centre, y grows downward.
// scale = focal / z2 (the perspective factor; 1.0 exactly at rest when the
// caller sets focal == standoff — the t419 research rest-equality law).
struct Projected {
    double x = 0.0, y = 0.0;  // screen px offset from the bounds centre
    double scale = 1.0;       // focal / z2
    double z2 = 0.0;          // camera-space depth (painter sort key)
};
double pointDepth(const Camera3d& cam, double x, double y, double z,
                  double standoff);
Projected projectPoint(const Camera3d& cam, double x, double y, double z,
                       double standoff);

// Perspective project a star to screen px inside cam.bounds (documented
// centre = bounds centre; y grows downward like SDL). Camera-space coords
// are dot(right, d) / dot(up, d) / dot(fwd, d) + standoff — at the rest
// basis this is EXACTLY the t399 formula (screen x = field x, y flipped,
// depth = field z + standoff), so the t399 rest-pinhole pins survive.
Pt projectStar(const Camera3d& cam, const ascend::game::Star& s);

// Vendor 4-band ladder on the TRANSFORMED z (planets-ui.md §6 thresholds
// ±0xdc == ±220): v >= 220 -> 0 (far), 1..219 -> 1, -220..0 -> 2, below -> 3
// (near). Pass viewDepth(cam, s) - kStandoff (t416: the ladder follows the
// VIEW axis under rotation, matching node+0xd = transformed z in
// FUN_000284bc).
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
