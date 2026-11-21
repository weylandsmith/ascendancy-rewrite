// SPDX-License-Identifier: GPL-3.0-or-later

// t399 galaxy-map 3D field law pins. Law sources: ui/cam3d.h (vendor affine
// FUN_00053324 + pinhole FUN_00053374, docs/re/_wip_t399.md), the t200 depth
// ladder (docs/re/planets-ui.md §6), the t192 lane-visibility law
// (Campaign::laneVisibleTo), the digit-face decode (scripts/
// t399_digit_faces.py). Star.z law: game/mapgen.h.
#include "ui/cam3d.h"

#include <cmath>
#include <memory>
#include <string>

#include "formats/shp.h"
#include "game/campaign.h"
#include "game/mapgen.h"
#include "harness.h"

#ifndef ASCENDANCY_SOURCE_DIR
#define ASCENDANCY_SOURCE_DIR "."
#endif

namespace {
const std::string kA01 =
    std::string(ASCENDANCY_SOURCE_DIR) + "/extracted/ascend01/data/";

std::shared_ptr<ascend::game::StarStats> shippedStats() {
    auto st = ascend::game::StarStats::load(
        std::string(ASCENDANCY_SOURCE_DIR) + "/extracted/ascend00/starstat.txt");
    return st ? std::make_shared<ascend::game::StarStats>(*st) : nullptr;
}

ascend::game::Star mkStar(int id, int x, int y, int z) {
    ascend::game::Star s;
    s.id = id; s.x = x; s.y = y; s.z = z;
    return s;
}
}  // namespace

using namespace ascend::ui;

// exported by test_campaign.cpp (t202b harness idiom; NOT in an anonymous
// namespace — an internal-linkage decl would never bind the definition).
ascend::game::Campaign makeCampaignForDemolish(unsigned seed);

TEST(cam3d_t399_projection_deterministic_and_centred) {
    Camera3d cam;  // yaw=pitch=0, focal 680 (fit law), mapSize 1024
    const ascend::game::Star centre = mkStar(0, 512, 512, 0);
    Pt q = projectStar(cam, centre);
    const int cx = (kCosmosWnd.x0 + kCosmosWnd.x1) / 2;
    const int cy = (kCosmosWnd.y0 + kCosmosWnd.y1) / 2;
    CHECK(q.x == cx && q.y == cy);
    // pinhole law (FUN_00053374: x * zoom / z): a point at field x=440,
    // z=0 sits at focal/standoff = 680/1760 scale -> round(440*680/1760)
    // = +170 px (fit law, cam3d.h).
    const ascend::game::Star east = mkStar(1, 512 + 440, 512, 0);
    Pt e = projectStar(cam, east);
    CHECK(e.x == cx + 170);
    CHECK(e.y == cy);
    // determinism: same input, 100 calls, same output
    for (int i = 0; i < 100; i++)
        CHECK(projectStar(cam, east).x == e.x && projectStar(cam, east).y == e.y);
}

TEST(cam3d_t399_zoom_clamps_and_rotation_wraps) {
    Camera3d cam;
    const double f0 = cam.focal;
    cam.zoom(+1);
    CHECK(cam.focal == f0 * Camera3d::kZoomStep);
    for (int i = 0; i < 40; i++) cam.zoom(+1);
    CHECK(cam.focal == Camera3d::kFocalMax);
    for (int i = 0; i < 100; i++) cam.zoom(-1);
    CHECK(cam.focal == Camera3d::kFocalMin);
    cam.reset();
    CHECK(cam.focal == 680.0 && cam.yawLog() == 0.0 && cam.pitchLog() == 0.0);
    // t416 REPLACES the old yaw-wrap/pitch-clamp reading: the vendor dial
    // law is a latch + pump (cam3d.h citations); rotation is a free basis
    // orbit with NO clamp. Latch semantics pinned in test_axis_t416.cpp.
    cam.pressSpin(+1);
    for (int i = 0; i < 2000; i++) cam.tick();  // no NaN, basis stays finite
    CHECK(std::isfinite(cam.yawLog()) && std::isfinite(cam.pitchLog()));
    cam.pressSpin(+1);  // same-dir press STOPS (vendor 0x27865 leg)
    CHECK(!cam.moving());
}

TEST(cam3d_t399_field_projects_inside_bounds) {
    // A full generated galaxy projects INSIDE the COSMOSWnd interior at the
    // default camera (D11: every star visible; nothing clipped off-window).
    Camera3d cam;
    ascend::game::MapConfig cfg;  // 50 stars, mapSize 1024
    REQUIRE_DATA();
    auto stats = shippedStats();
    CHECK(stats != nullptr);
    if (!stats) return;
    std::vector<std::string> names;
    for (int i = 0; i < 100; i++) names.push_back("Star" + std::to_string(i));
    ascend::game::MapGenerator gen(cfg, *stats, names);
    const auto g = gen.generate();
    CHECK(int(g.stars.size()) == 50);  // cosmos.txt STARS 50 default
    for (const auto& s : g.stars) {
        Pt q = projectStar(cam, s);
        CHECK(q.x >= kCosmosWnd.x0 && q.x <= kCosmosWnd.x1);
        CHECK(q.y >= kCosmosWnd.y0 && q.y <= kCosmosWnd.y1);
    }
}

TEST(cam3d_t399_star_z_law) {
    // z is deterministic per (seed, slot), bounded by the star's xy radius
    // from centre (shell radius), and NOT all zero (vacuity guard).
    ascend::game::MapConfig cfg; cfg.seed = 4242;
    REQUIRE_DATA();
    auto stats = shippedStats();
    CHECK(stats != nullptr);
    if (!stats) return;
    std::vector<std::string> names;
    for (int i = 0; i < 100; i++) names.push_back("N" + std::to_string(i));
    const auto g1 = ascend::game::MapGenerator(cfg, *stats, names).generate();
    const auto g2 = ascend::game::MapGenerator(cfg, *stats, names).generate();
    int nonzero = 0;
    for (size_t i = 0; i < g1.stars.size(); i++) {
        CHECK(g1.stars[i].z == g2.stars[i].z);  // deterministic
        const double dx = g1.stars[i].x - 512.0, dy = g1.stars[i].y - 512.0;
        const double r = std::sqrt(dx * dx + dy * dy);
        CHECK(std::abs(double(g1.stars[i].z)) <= r + 1.0);  // inside shell
        if (g1.stars[i].z != 0) ++nonzero;
    }
    CHECK(nonzero > 25);  // a flat field would be the D11 defect again
    // different seed -> different z vector (position carries no cross-seed
    // identity, r1-savestate H3)
    ascend::game::MapConfig cfg2 = cfg; cfg2.seed = 7;
    const auto g3 = ascend::game::MapGenerator(cfg2, *stats, names).generate();
    bool anyDiff = false;
    for (size_t i = 0; i < g1.stars.size(); i++)
        if (g1.stars[i].z != g3.stars[i].z) anyDiff = true;
    CHECK(anyDiff);
}

TEST(cam3d_t399_depth_ladder_t200_thresholds) {
    // ±0xdc == ±220 ladder (planets-ui.md §6): v>=220 -> 0, 1..219 -> 1,
    // -220..0 -> 2, < -220 -> 3.
    CHECK(depthClass(300) == 0);
    CHECK(depthClass(220) == 0);
    CHECK(depthClass(219) == 1);
    CHECK(depthClass(1) == 1);
    CHECK(depthClass(0) == 2);
    CHECK(depthClass(-220) == 2);
    CHECK(depthClass(-221) == 3);
    // pips grow monotonically with nearness, owners strictly bigger
    int prev = 0;
    for (int cls = 0; cls <= 3; cls++) {
        const int n = pipRadius(cls, false), o = pipRadius(cls, true);
        CHECK(o > n);
        CHECK(n >= prev);
        prev = n;
    }
}

TEST(cam3d_t399_neutral_tint_domain) {
    // 13 starstat types address the table; out-of-domain clamps (never UB).
    for (int t = 0; t < 13; t++) {
        RGB c = neutralTint(t);
        CHECK(int(c.r) + int(c.g) + int(c.b) > 240);  // every pip is visible
    }
    neutralTint(-1); neutralTint(99);  // must not crash
}

TEST(cam3d_t399_digit_faces_identity_law) {
    // MEASURED law: 1starmap k55..k64 are the digits 0..9 in order; the
    // mechanical discriminator is k56 uniquely narrow (w=18, all others
    // >=24) — the only face that can be '1'. Reads the REAL vendor file.
    REQUIRE_DATA();
    ascend::formats::ShapeLibrary lib;
    std::string err;
    CHECK(lib.load(kA01 + "1starmap.shp", &err));
    if (lib.count() == 0) return;
    CHECK(lib.count() >= 65);
    int w[10];
    for (int d = 0; d < 10; d++) {
        const auto& r = lib.record(kDigitFirstFrame + d);
        w[d] = int(r.width);
        CHECK(r.height >= 30);  // tall faces = the LARGE day-counter digits
    }
    // tA1 bbox re-cite (k55..k64 verbatim): the thin "1" is 9 px; the
    // rest 18..25 (the old 18/24 split was the R,B-corner misparse).
    CHECK(w[1] == 9);
    for (int d = 0; d < 10; d++)
        if (d != 1) CHECK(w[d] >= 18);
    // decoded ink exists (a dims-zero/undecodable face fails here)
    std::vector<uint8_t> px;
    for (int d = 0; d < 10; d++) {
        CHECK(lib.decode(kDigitFirstFrame + d, px));
        bool ink = false;
        for (uint8_t v : px) if (v != 0) ink = true;
        CHECK(ink);
    }
}

TEST(cam3d_t399_home_star_and_turn1_lane_law) {
    // D11: "not possible to find the player's home star" -> the campaign
    // exposes it; "at the beginning the only lines shown should be the star
    // lanes that lead off from your home system" -> every lane visible to
    // the player at turn 1 touches a star the player owns, and the player's
    // home star is owned by the player.
    REQUIRE_DATA();
    ascend::game::Campaign camp = makeCampaignForDemolish(11u);  // test_campaign.cpp
    const int home = camp.homeStarFor(ascend::game::kPlayer);
    CHECK(home >= 0);
    CHECK(camp.starOwner(home) == ascend::game::kPlayer);
    CHECK(camp.homeStarFor(99) == -1);  // out-of-domain
    for (size_t li = 0; li < camp.galaxy().lanes.size(); li++) {
        if (!camp.laneVisibleTo(int(li), ascend::game::kPlayer)) continue;
        const auto& ln = camp.galaxy().lanes[li];
        CHECK(camp.starOwner(ln.a) == ascend::game::kPlayer ||
              camp.starOwner(ln.b) == ascend::game::kPlayer);
    }
    // and the home system's own incident lanes ARE all visible (leads-off law)
    for (size_t li = 0; li < camp.galaxy().lanes.size(); li++) {
        const auto& ln = camp.galaxy().lanes[li];
        if (ln.a == home || ln.b == home)
            CHECK(camp.laneVisibleTo(int(li), ascend::game::kPlayer));
    }
}
