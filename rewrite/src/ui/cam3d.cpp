// SPDX-License-Identifier: GPL-3.0-or-later

// t399 3D cosmos camera law — see cam3d.h for citations. Pure math; pins in
// tests/test_cam3d_t399.cpp.
#include "ui/cam3d.h"

#include <cmath>

namespace ascend::ui {

void Camera3d::rotate(int dir) {
    yaw += dir * kRotStep;
    // wrap into [0, 2pi) so long spin sessions cannot drift fp precision
    const double tau = 6.283185307179586;
    yaw = std::fmod(yaw, tau);
    if (yaw < 0) yaw += tau;
}
void Camera3d::tilt(int dir) {
    pitch += dir * kRotStep;
    if (pitch > kPitchLimit) pitch = kPitchLimit;
    if (pitch < -kPitchLimit) pitch = -kPitchLimit;
}
void Camera3d::zoom(int dir) {
    for (int i = 0; i < (dir > 0 ? dir : -dir); ++i)
        focal *= dir > 0 ? kZoomStep : 1.0 / kZoomStep;
    if (focal < kFocalMin) focal = kFocalMin;
    if (focal > kFocalMax) focal = kFocalMax;
}
void Camera3d::reset() {
    yaw = 0.0;
    pitch = 0.0;
    focal = Camera3d().focal;  // the struct default (fit law in cam3d.h)
}

namespace {
// Field point relative to the map-grid centre (Star x/y are grid units).
inline void centreOffset(const Camera3d& cam, const ascend::game::Star& s,
                         double* x, double* y, double* z) {
    const double c = cam.mapSize / 2.0;
    *x = s.x - c;
    *y = s.y - c;
    *z = s.z;
}
}  // namespace

double viewDepth(const Camera3d& cam, const ascend::game::Star& s) {
    double x, y, z;
    centreOffset(cam, s, &x, &y, &z);
    // Yaw about z, then pitch about the screen x-axis; the view axis is +w.
    const double cy = std::cos(cam.yaw), sy = std::sin(cam.yaw);
    const double cp = std::cos(cam.pitch), sp = std::sin(cam.pitch);
    const double x1 = x * cy - y * sy;
    const double y1 = x * sy + y * cy;
    (void)x1;
    return Camera3d::kStandoff + y1 * sp + z * cp;
}

Pt projectStar(const Camera3d& cam, const ascend::game::Star& s) {
    double x, y, z;
    centreOffset(cam, s, &x, &y, &z);
    const double cy = std::cos(cam.yaw), sy = std::sin(cam.yaw);
    const double cp = std::cos(cam.pitch), sp = std::sin(cam.pitch);
    const double x1 = x * cy - y * sy;
    const double y1 = x * sy + y * cy;
    const double y2 = y1 * cp - z * sp;   // camera-space vertical
    const double z2 = Camera3d::kStandoff + y1 * sp + z * cp;  // depth
    // Vendor pinhole (FUN_00053374): round(v * zoom / z) + origin.
    const double sx = std::round(x1 * cam.focal / z2);
    const double sy2 = std::round(y2 * cam.focal / z2);
    const int cx = (cam.bounds.x0 + cam.bounds.x1) / 2;
    const int cyi = (cam.bounds.y0 + cam.bounds.y1) / 2;
    return Pt{cx + int(sx), cyi - int(sy2)};  // y-up field -> y-down screen
}

int depthClass(double fieldZ) {
    // t200 ladder thresholds ±0xdc == ±220 (planets-ui.md §6); port field z
    // needs no offset (vendor f32@0x105e [unverified], documented 0).
    if (fieldZ >= 220.0) return 0;
    if (fieldZ >= 1.0) return 1;
    if (fieldZ >= -220.0) return 2;
    return 3;
}

int pipRadius(int cls, bool owned) {
    // Documented port default (cos_star pips unreadable, OQ-005): nearer
    // bands draw bigger; owners stay bigger than neutrals (CVD: size +
    // colour, never colour alone).
    const int base = cls == 3 ? 4 : cls == 2 ? 3 : cls == 1 ? 2 : 1;
    return owned ? base + 1 : base;
}

RGB neutralTint(int starType) {
    // 13 rows (starstat.txt types). PORT PALETTE [documented default] —
    // families from the user-supplied original (red/yellow/blue/white
    // points; external vision read), green avoided (day-counter chrome).
    static const RGB kT[13] = {
        {235, 235, 245}, {210, 200, 140}, {200, 150, 110}, {170, 190, 235},
        {235, 170, 130}, {150, 170, 220}, {225, 225, 200}, {190, 140, 160},
        {240, 205, 160}, {160, 200, 210}, {205, 175, 195}, {225, 190, 150},
        {175, 175, 205},
    };
    if (starType < 0 || starType >= 13) return kT[0];
    return kT[starType];
}

int hitStarCam(const Camera3d& cam, const ascend::game::Galaxy& g, Pt p,
               int radius) {
    int best = -1;
    long bestD2 = long(radius) * radius;
    for (const auto& s : g.stars) {
        Pt q = projectStar(cam, s);
        long dx = q.x - p.x, dy = q.y - p.y;
        long d2 = dx * dx + dy * dy;
        if (d2 <= bestD2) { bestD2 = d2; best = s.id; }
    }
    return best;
}

}  // namespace ascend::ui
