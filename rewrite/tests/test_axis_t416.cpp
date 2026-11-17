// SPDX-License-Identifier: GPL-3.0-or-later

// t416 — ROTATION AXIS WIRING pins (D15: "the upper left rotation control
// should rotate the galaxy about the Z axis, but it here seems to rotate it
// around the Y axis"). Law + full citations: docs/re/_wip_t416.md F1-F2,
// cam3d.h. The vendor dials latch a (dir) pair per press and a periodic
// pump rotates the camera BASIS about WORLD Y (spin pair) / WORLD X (tilt
// pair) by 2 DEG/tick (FUN_000283e4 -> FUN_00053584/0x53554; pump 0x27a18).
#include "ui/cam3d.h"

#include <cmath>

#include "harness.h"

using ascend::ui::Camera3d;
using ascend::ui::Vec3d;

static bool nearEq(double a, double b) { return std::fabs(a - b) < 1e-9; }

TEST(axis_t416_latch_press_law) {
    // Vendor press chain (0x27da2..0x279eb): inactive -> active(dir);
    // active ALREADY this dir -> STOP; active opposite -> FLIP to pressed.
    CHECK(Camera3d::dialLatch(0, +1) == +1);
    CHECK(Camera3d::dialLatch(0, -1) == -1);
    CHECK(Camera3d::dialLatch(+1, +1) == 0);   // repeat press stops
    CHECK(Camera3d::dialLatch(-1, -1) == 0);
    CHECK(Camera3d::dialLatch(+1, -1) == -1);  // opposite flips direction
    CHECK(Camera3d::dialLatch(-1, +1) == +1);
    // Dial sign table verbatim from the pump (0x27a28: bit1 set -> -2;
    // 0x27a60: bit3 set -> +2): ROTLEFT +, ROTRIGHT -, ROTUP -, ROTDOWN +.
    Camera3d cam;
    cam.pressSpin(+1);  // ROTLEFT
    CHECK(cam.latchSpin == +1 && cam.moving());
    cam.pressSpin(-1);  // ROTRIGHT while spinning left -> FLIP
    CHECK(cam.latchSpin == -1 && cam.moving());
    cam.pressSpin(-1);  // ROTRIGHT again -> STOP
    CHECK(cam.latchSpin == 0 && !cam.moving());
    // Zoom pair latches independently (msg 54/55, bits 4/5).
    cam.pressZoom(+1);
    CHECK(cam.latchZoom == +1 && cam.moving() && cam.latchSpin == 0);
    cam.reset();
    CHECK(!cam.moving() && cam.focal == 680.0);
}

TEST(axis_t416_spin_is_about_world_y_and_rest_projection_is_identity) {
    // At rest the port projection must equal the t399 formula EXACTLY
    // (screen x = field x + centre, y flipped, depth = z + standoff):
    // east star at field x=+440 sits at round(440*680/1760) = +170 px.
    Camera3d cam;
    ascend::game::Star e; e.id = 1; e.x = 512 + 440; e.y = 512; e.z = 0;
    const int cx = (cam.bounds.x0 + cam.bounds.x1) / 2;
    const int cy = (cam.bounds.y0 + cam.bounds.y1) / 2;
    ascend::ui::Pt q = ascend::ui::projectStar(cam, e);
    CHECK(q.x == cx + 170 && q.y == cy);

    // WORLD-Y spin: a point straight AHEAD of the camera (field +z) moves
    // in the screen PLANE (x changes, depth ~unchanged near the centre);
    // the up vector stays world-vertical (up.y == 1) — this is the vendor
    // behaviour the user calls "rotate about Z" (the picture spins in
    // plane at rest), NOT a tumble.
    ascend::game::Star ahead; ahead.id = 2; ahead.x = 512; ahead.y = 512;
    ahead.z = 300;
    Camera3d c2;
    c2.pressSpin(+1);  // ROTLEFT = +2 deg/tick (pump sign)
    c2.tick();
    CHECK(nearEq(c2.up.y, 1.0));  // world-Y rotation keeps up vertical
    ascend::ui::Pt a0 = ascend::ui::projectStar(cam, ahead);
    Camera3d c2b = c2;
    for (int i = 1; i < 10; i++) c2b.tick();  // 20 deg of spin total
    ascend::ui::Pt a1 = ascend::ui::projectStar(c2b, ahead);
    // 300-unit-deep centre point: dot(right',d) = -300*sin(20deg) = -102.6,
    // depth 1760+300*cos(20deg) -> x shifts ~34 px (in-plane, tangential).
    CHECK(std::abs(a1.x - a0.x) >= 30);   // in-plane path (x moved)
    // depth near-unchanged at the field centre line: the pip size class
    // (ladder band 220 wide) must NOT change after one 2-deg spin tick.
    CHECK(ascend::ui::depthClass(ascend::ui::viewDepth(cam, ahead) -
                                 Camera3d::kStandoff) ==
          ascend::ui::depthClass(ascend::ui::viewDepth(c2, ahead) -
                                 Camera3d::kStandoff));

    // 90 degrees of spin maps the east point to where the field-z axis was:
    // rotateBasisY(+90) turns fwd (0,0,1) -> (1,0,0) [right-handed about
    // world Y per FUN_0005324c: x' = x*c + z*s with c=0,s=1 -> fwd'=(1,0,0)].
    Camera3d c3;
    c3.rotateBasisY(90.0);
    CHECK(nearEq(c3.fwd.x, 1.0) && nearEq(c3.fwd.y, 0.0) &&
          nearEq(c3.fwd.z, 0.0));
}

TEST(axis_t416_tilt_is_about_world_x_and_no_pitch_clamp) {
    // Tilt pair (msg 52/53) rotates about WORLD X: up leaves vertical,
    // up.x stays 0 (FUN_000531dc mixes only y,z components).
    Camera3d cam;
    cam.pressTilt(+1);  // ROTDOWN = +2 deg/tick
    cam.tick();
    CHECK(nearEq(cam.up.x, 0.0));
    CHECK(!nearEq(cam.up.y, 1.0));
    // NO clamp in the vendor rotation path: 100000 ticks stay finite and
    // the basis stays orthonormal (right = cross(up,fwd) unit).
    for (int i = 0; i < 100000; i++) cam.tick();
    const Vec3d r = cam.right();
    CHECK(std::isfinite(r.x) && std::isfinite(r.y) && std::isfinite(r.z));
    CHECK(std::fabs(std::sqrt(r.x * r.x + r.y * r.y + r.z * r.z) - 1.0) <
          1e-6);
}

TEST(axis_t416_rest_basis_matches_recenter_immediates) {
    // FUN_00026a9c (CENTERHOLO) writes right(1,0,0) up(0,1,0) fwd(0,0,1);
    // the port rest values + derived right must match EXACTLY.
    Camera3d cam;
    const Vec3d r = cam.right();
    CHECK(nearEq(r.x, 1.0) && nearEq(r.y, 0.0) && nearEq(r.z, 0.0));
    CHECK(nearEq(cam.up.x, 0.0) && nearEq(cam.up.y, 1.0) && nearEq(cam.up.z, 0.0));
    CHECK(nearEq(cam.fwd.x, 0.0) && nearEq(cam.fwd.y, 0.0) && nearEq(cam.fwd.z, 1.0));
    // Pump delta is 2 DEG [verified immediates 2/-2 + deg2rad f32@0x88b88].
    CHECK(nearEq(Camera3d::kRotStepDeg, 2.0));
    CHECK(std::fabs(Camera3d::kDeg2Rad - 0.017453292) < 1e-8);
}
