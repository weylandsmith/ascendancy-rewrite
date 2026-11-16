// SPDX-License-Identifier: GPL-3.0-or-later

// t410 SYSTEM VIEW + SCREEN STACK — see sysview.h for the citations. Pure
// data + math (no SDL), compiled into run_tests (statuslist.cpp precedent).
// Working notes: docs/re/_wip_t410.md.
#include "ui/sysview.h"

#include <cmath>

namespace ascend::ui {

void ScreenStack::push(int screen) {
    // Truncate if `screen` is already on the stack: reopening a screen from
    // a rail or a row never stacks a duplicate above a deeper screen
    // (the t299 escape-ladder gap — "after closing the system view, the
    // ladder exits early" — is a stack with lost levels; this law keeps the
    // unwind depth equal to the navigation depth).
    for (size_t i = 0; i < s_.size(); ++i) {
        if (s_[i] == screen) {
            s_.resize(i + 1);
            return;
        }
    }
    s_.push_back(screen);
}

bool ScreenStack::escape() {
    if (s_.size() <= 1) return false;  // bottom: the caller's standing quit
    s_.pop_back();
    return true;
}

const SysCtlControl kSysCtl[kSysCtlCount] = {
    // name, rect (verbatim), SENDMESSAGE, SHAPEFRAME — windows.txt state-16
    // records in FILE ORDER (_wip_t410 F1 census; F3 dims parity).
    {"TOGGRID",      {557, 403, 587, 433}, 74,  0},
    {"BATROTLEFT",   {479, 403, 493, 433}, 50,  1},
    {"BATROTRIGHT",  {494, 403, 509, 433}, 51,  2},
    {"BATZOOMIN",    {518, 403, 548, 418}, 54,  3},
    {"BATZOOMOUT",   {518, 419, 548, 433}, 55,  4},
    {"RECENTER",     {596, 442, 626, 472}, 71,  5},
    {"TOGELEV",      {596, 403, 626, 433}, 76,  6},
    {"ABANDON",      {479, 442, 548, 472}, 84,  8},
    {"My^Items",     {479, 103, 548, 133}, 804, 7},
    {"Other^Items",  {557, 103, 626, 133}, 805, 9},
    {"Repeat",       {531, 55, 574, 85},   809, 17},
    {"Pass",         {479, 55, 522, 85},   807, 16},
    {"Auto",         {583, 55, 626, 85},   808, 18},
    {"W",            {479, 103, 509, 133}, 810, 12},
    {"S",            {518, 103, 548, 133}, 811, 13},
    {"Z",            {557, 103, 587, 133}, 813, 15},
    {"I",            {596, 103, 626, 133}, 812, 14},
};

SysCtl sysCtlFor(Pt p) {
    // LAST MATCH WINS (the t264 file-order/last-hit scan): W/S/Z/I are
    // later records than My^Items and win inside its span — the vendor
    // table's own resolution of the overlap.
    SysCtl hit = SysCtl::None;
    for (int i = 0; i < kSysCtlCount; ++i)
        if (inRect(kSysCtl[i].rect, p))
            hit = static_cast<SysCtl>(i);
    return hit;
}

int sysCtlShapeRecord(SysCtl c) {
    if (c == SysCtl::None) return -1;
    const int fr = kSysCtl[static_cast<int>(c)].shapeFrame;
    // The two named-seam faces (_wip_t410 F3): SHAPEFRAME exists but its
    // record fails the t394 dims-parity law (My^Items FR7 65x28 vs 69x30;
    // ABANDON FR8 67x29 vs 69x30 — k7/k8/k9 is a size ladder). Refuse the
    // face rather than guess a frame.
    if (c == SysCtl::MyItems || c == SysCtl::Abandon) return -1;
    return fr;
}

double orbitAngle(int i) {
    double a = std::fmod(i * kGoldenAngle, 6.283185307179586);
    if (a < 0) a += 6.283185307179586;
    return a;
}

double orbitRadius(int i) {
    if (i < 0) i = 0;
    return kOrbitBase + kOrbitPitch * i;
}

std::vector<OrbitDot> systemOrbits(const ascend::game::Campaign& camp,
                                   int star, const Camera3d& cam) {
    std::vector<OrbitDot> out;
    const auto& g = camp.galaxy();
    if (star < 0 || star >= int(g.stars.size())) return out;
    const auto& s = g.stars[size_t(star)];
    const int owner = camp.starOwner(s.id);
    const int cx = (cam.bounds.x0 + cam.bounds.x1) / 2;
    const int cy = (cam.bounds.y0 + cam.bounds.y1) / 2;
    // Zoom scales the field around the centre (the same pinhole intuition
    // as cam3d.h at a fixed standoff; documented port layout, header).
    const double zs = cam.focal / Camera3d().focal;
    out.reserve(s.planets.size());
    for (const auto& pl : s.planets) {
        OrbitDot d;
        d.planetIndex = pl.index;
        // Colonisation model: ONE PlanetState per star (t406); the colonised
        // world is planet index 0, the rest are bare bodies (mapgen.md §3).
        d.colonised = owner >= 0 && pl.index == 0;
        d.radius = d.colonised ? 7 : 4;
        d.owner = owner;
        const double a = orbitAngle(pl.index);
        const double r = orbitRadius(pl.index) * zs;
        d.pos = Pt{cx + int(std::round(r * std::cos(a))),
                   cy + int(std::round(r * std::sin(a)))};
        out.push_back(std::move(d));
    }
    return out;
}

int hitOrbitDot(const std::vector<OrbitDot>& dots, Pt p, int radius) {
    int best = -1;
    long bestD2 = long(radius) * radius;
    for (const auto& d : dots) {
        long dx = d.pos.x - p.x, dy = d.pos.y - p.y;
        long d2 = dx * dx + dy * dy;
        if (d2 <= bestD2) { bestD2 = d2; best = d.planetIndex; }
    }
    return best;
}

}  // namespace ascend::ui
