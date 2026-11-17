// SPDX-License-Identifier: GPL-3.0-or-later

// t399 3D cosmos camera law + t416 DIAL LAW — see cam3d.h for citations.
// Pure math; pins in tests/test_cam3d_t399.cpp (t416 blocks included).
#include "ui/cam3d.h"

#include <cmath>

namespace ascend::ui {

int Camera3d::dialLatch(int cur, int dir) {
    // Vendor press law (handler 0x26b34 chain 0x27da2..0x279eb): inactive
    // -> ACTIVE with this dir; active ALREADY in this dir -> STOP; active
    // in the opposite dir -> FLIP to the pressed dir (msg 53 with bit1
    // clear sets bit1 at 0x278ae; msg 52 with bit3 set clears bit3 at
    // 0x278e7 — every leg lands on "pressed direction wins, repeat stops").
    // dir is +/-1 (port sign reading of the pump: ROTLEFT/ROTDOWN = +,
    // ROTRIGHT/ROTUP = -, per 0x27a28/0x27a60).
    if (cur == dir) return 0;
    return dir;
}

void Camera3d::rotateBasisY(double deg) {
    // FUN_0005324c component mix (verified): x' = x*c + z*s ; z' = z*c - x*s
    // (right-handed about world Y; deg is scaled by deg2rad here exactly as
    // the vendor helper scales its argument at 0x53262).
    const double r = deg * kDeg2Rad;
    const double c = std::cos(r), s = std::sin(r);
    auto mix = [c, s](Vec3d& v) {
        const double x = v.x * c + v.z * s;
        const double z = v.z * c - v.x * s;
        v.x = x; v.z = z;
    };
    mix(up);
    mix(fwd);
}

void Camera3d::rotateBasisX(double deg) {
    // FUN_000531dc component mix (verified): y' = y*c - z*s ; z' = z*c + y*s
    // (right-handed about world X).
    const double r = deg * kDeg2Rad;
    const double c = std::cos(r), s = std::sin(r);
    auto mix = [c, s](Vec3d& v) {
        const double y = v.y * c - v.z * s;
        const double z = v.z * c + v.y * s;
        v.y = y; v.z = z;
    };
    mix(up);
    mix(fwd);
}

void Camera3d::tick() {
    // One pump of the vendor msg-0x3b handler (0x27a18): the spin pair
    // applies delta = latchSpin * 2 deg about WORLD Y (bit1 sign mapped to
    // latch sign), the tilt pair delta = latchTilt * 2 deg about WORLD X,
    // the zoom pair scales focal. NO clamp on rotation (vendor has none).
    if (latchSpin != 0) rotateBasisY(latchSpin * kRotStepDeg);
    if (latchTilt != 0) rotateBasisX(latchTilt * kRotStepDeg);
    if (latchZoom != 0) zoom(latchZoom);
}

void Camera3d::zoom(int dir) {
    for (int i = 0; i < (dir > 0 ? dir : -dir); ++i)
        focal *= dir > 0 ? kZoomStep : 1.0 / kZoomStep;
    // Vendor zoom has runtime bounds (f32[0xfb0]/[0xfb4], FUN_00028428) +
    // hard [1,100000]; the port's are its documented fit-law neighbours.
    if (focal < kFocalMin) focal = kFocalMin;
    if (focal > kFocalMax) focal = kFocalMax;
}

void Camera3d::reset() {
    // CENTERHOLO FUN_00026a9c verbatim: identity basis, zoom accumulator
    // default, and the latches stop (port: msg 56 also clears them — the
    // vendor pump stops at the zoom bounds; recenter repainting 0x27b02
    // implies a still frame).
    up = Vec3d{0.0, 1.0, 0.0};
    fwd = Vec3d{0.0, 0.0, 1.0};
    latchSpin = latchTilt = latchZoom = 0;
    focal = Camera3d().focal;  // the struct default (fit law in cam3d.h)
}

Vec3d Camera3d::right() const {
    // FUN_00053804: right = cross(up, fwd). At rest (0,1,0)x(0,0,1) =
    // (1,0,0) == the vendor rest immediate at +0x14e [verified].
    return Vec3d{up.y * fwd.z - up.z * fwd.y,
                 up.z * fwd.x - up.x * fwd.z,
                 up.x * fwd.y - up.y * fwd.x};
}

double Camera3d::yawLog() const { return std::atan2(fwd.x, fwd.z); }

double Camera3d::pitchLog() const {
    return std::atan2(fwd.y, std::fabs(fwd.z) < 1e-12 ? 1e-12 : std::fabs(fwd.z));
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
    return pointDepth(cam, x, y, z, Camera3d::kStandoff);
}

// t419 generic field-point law (header): camera-space coords on the rotated
// basis (same dot products as projectStar), depth = standoff + dot(fwd,d).
double pointDepth(const Camera3d& cam, double x, double y, double z,
                  double standoff) {
    return standoff + cam.fwd.x * x + cam.fwd.y * y + cam.fwd.z * z;
}

Projected projectPoint(const Camera3d& cam, double x, double y, double z,
                       double standoff) {
    const Vec3d r = cam.right();
    Projected p;
    const double cx3 = r.x * x + r.y * y + r.z * z;        // dot(right, d)
    const double cy3 = cam.up.x * x + cam.up.y * y + cam.up.z * z;  // dot(up, d)
    p.z2 = pointDepth(cam, x, y, z, standoff);
    p.scale = cam.focal / p.z2;
    p.x = std::round(cx3 * p.scale);
    p.y = std::round(cy3 * p.scale);
    return p;
}

Pt projectStar(const Camera3d& cam, const ascend::game::Star& s) {
    double x, y, z;
    centreOffset(cam, s, &x, &y, &z);
    const Vec3d r = cam.right();
    // Camera-space coords on the rotated basis (t416); at the rest basis
    // these are exactly (x, y, z) and this reduces to the t399 formula.
    const double cx3 = r.x * x + r.y * y + r.z * z;      // dot(right, d)
    const double cy3 = cam.up.x * x + cam.up.y * y + cam.up.z * z;  // dot(up, d)
    const double z2 = Camera3d::kStandoff +
                      cam.fwd.x * x + cam.fwd.y * y + cam.fwd.z * z;
    // Vendor pinhole (FUN_00053374): round(v * zoom / z) + origin.
    const double sx = std::round(cx3 * cam.focal / z2);
    const double sy2 = std::round(cy3 * cam.focal / z2);
    const int cx = (cam.bounds.x0 + cam.bounds.x1) / 2;
    const int cyi = (cam.bounds.y0 + cam.bounds.y1) / 2;
    return Pt{cx + int(sx), cyi - int(sy2)};  // y-up field -> y-down screen
}

int depthClass(double fieldZ) {
    // t200 ladder thresholds ±0xdc == ±220 (planets-ui.md §6); pass
    // viewDepth - kStandoff (t416: the ladder follows the VIEW axis, like
    // node+0xd = transformed z in FUN_000284bc).
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

// t411 DEPTH DIM [vision-measured law, documented ramp]: the vendor field
// shows pips of VARYING BRIGHTNESS, dimmer with distance (external vision
// read of scratchpad/galaxymap-original.png; pixel census F0: vendor pip
// sizes 1..20+ AND several dim members). Returns the 256ths multiplier on
// the tint per depth class — monotone non-decreasing with nearness, near
// bands unscaled. Values are PORT DEFAULTS (the vendor cos_star brightness
// table is unreadable until OQ-005), the LAW (monotone dim-with-distance)
// is measured.
int pipDim256(int cls) {
    static const int kDim[4] = {96, 160, 224, 256};  // far -> near
    return cls < 0 || cls > 3 ? 256 : kDim[cls];
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
