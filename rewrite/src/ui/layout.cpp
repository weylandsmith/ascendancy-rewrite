#include "ui/layout.h"

#include <algorithm>
#include <cmath>
#include <cstdlib>

namespace ascend::ui {

Pt starScreenPos(const CosmosView& v, const ascend::game::Star& s) {
    // Linear map-grid -> screen scale (ui-runtime.md §2 [documented default]).
    const double sx = double(v.bounds.x1 - v.bounds.x0) / v.mapSize;
    const double sy = double(v.bounds.y1 - v.bounds.y0) / v.mapSize;
    return Pt{v.bounds.x0 + int(s.x * sx), v.bounds.y0 + int(s.y * sy)};
}

int hitStar(const CosmosView& v, const ascend::game::Galaxy& g, Pt p, int radius) {
    int best = -1;
    long bestD2 = long(radius) * radius;
    for (const auto& s : g.stars) {
        Pt q = starScreenPos(v, s);
        long dx = q.x - p.x, dy = q.y - p.y;
        long d2 = dx * dx + dy * dy;
        if (d2 <= bestD2) { bestD2 = d2; best = s.id; }
    }
    return best;
}

bool inRect(Rect r, Pt p) {
    return p.x >= r.x0 && p.x <= r.x1 && p.y >= r.y0 && p.y <= r.y1;
}

// Palette: searched (not hand-tuned) under the ui-runtime.md §4 rule; the
// same rule is unit-tested via simulateDeuteranopia below, so any future
// edit that breaks CVD separability fails run_tests.
const RGB kOwnerRgb[7] = {
    {255, 255, 255},  // 0 player   hue   0
    {248, 208,  64},  //            hue  47
    { 72, 136,  24},  //            hue  94
    { 40, 208, 112},  //            hue 146
    { 64, 216, 248},  //            hue 190
    { 96,  24, 208},  //            hue 263
    {248, 120, 224},  //            hue 311
};
// Luminances above are of the SIMULATED colour (perceived), not raw — a raw
// luminance ladder hid a deuteranopic collision (the first palette failed its
// own unit test, 2026-10-04). Neutral is ALSO drawn at a smaller radius, so
// its rule may accept pure-chroma separation (test rule below).
const RGB kNeutralRgb = {40, 40, 40};

void simulateDeuteranopia(const RGB& c, RGB* out) {
    // Linear approximation used throughout this project (docs/re/ui-runtime.md
    // §4): r' = .625r + .7g - .325b, g' = .7r + .3g, b' = -.3r + 1.3b.
    const double r = c.r / 255.0, g = c.g / 255.0, b = c.b / 255.0;
    auto clamp = [](double v) { return static_cast<unsigned char>(
        std::max(0.0, std::min(1.0, v)) * 255.0); };
    out->r = clamp(0.625 * r + 0.7 * g - 0.325 * b);
    out->g = clamp(0.7 * r + 0.3 * g);
    out->b = clamp(-0.3 * r + 1.3 * b);
}

void simulateProtanopia(const RGB& c, RGB* out) {
    // Standard protan approximation; the palette is validated under BOTH
    // transforms so no red-green deficiency class sees a collision.
    const double r = c.r / 255.0, g = c.g / 255.0, b = c.b / 255.0;
    auto clamp = [](double v) { return static_cast<unsigned char>(
        std::max(0.0, std::min(1.0, v)) * 255.0); };
    out->r = clamp(0.566678 * r + 0.433322 * g);
    out->g = clamp(0.558621 * g + 0.441379 * b);
    out->b = clamp(0.242184 * g + 0.757816 * b);
}

unsigned luminance601(const RGB& c) {
    return static_cast<unsigned>(
        0.299 * c.r + 0.587 * c.g + 0.114 * c.b + 0.5);
}

}  // namespace ascend::ui
