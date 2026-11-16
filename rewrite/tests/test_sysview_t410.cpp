// SPDX-License-Identifier: GPL-3.0-or-later
// t410 SYSTEM VIEW + SCREEN STACK pins: the state-16 console table (rects/
// messages verbatim windows.txt), the SHAPEFRAME->record identity + t394
// dims-parity law on the REAL 16battle.shp, the orbital layout law, the
// screen law for id 16, and THE CHAIN (1 -> 16 -> 17 with Escape unwinding
// one level per press — the queue row's named closer). Citations:
// ui/sysview.h header, docs/re/_wip_t410.md F1-F4.
#include "ui/sysview.h"
#include "ui/statuslaw.h"

#include <cstdio>
#include <optional>
#include <string>
#include <vector>

#include "formats/shp.h"
#include "game/campaign.h"
#include "harness.h"

#ifndef ASCENDANCY_SOURCE_DIR
#define ASCENDANCY_SOURCE_DIR "."
#endif

namespace {
namespace au = ascend::ui;
namespace ag = ascend::game;
const std::string kRepo = ASCENDANCY_SOURCE_DIR;

// Campaign fixture (same shape as test_planetview_t406 — loads the vendor
// tables; nullopt without data, every caller REQUIRE_DATA()s).
std::optional<ag::Campaign> seededCampaign() {
    static ag::StarStats stats;
    static std::vector<std::string> names;
    static ag::ResearchTree tree;
    static std::vector<ag::PlanetItem> items;
    static std::vector<ag::Gizmo> gizmos;
    static std::vector<ag::DipFile> ai;
    static bool loaded = false;
    if (!loaded) {
        std::string e;
        auto st = ag::StarStats::load(kRepo + "/extracted/ascend00/starstat.txt", &e);
        if (!st) return std::nullopt;
        stats = *st;
        names = ag::loadStarNames(kRepo + "/extracted/ascend00/names.txt", &e);
        tree = ag::ResearchTree::loadFromFile(kRepo + "/extracted/ascend00/restree.txt", e);
        items = ag::loadPlanItems(kRepo + "/extracted/ascend00/planitem.txt", e);
        gizmos = ag::loadGizmos(kRepo + "/extracted/ascend00/gizmos.txt", e);
        for (int i = 0; i < 6; ++i) {
            ag::DipFile df;
            char path[256];
            std::snprintf(path, sizeof(path), "%s/extracted/ascend00/race%02d.dip",
                          ASCENDANCY_SOURCE_DIR, i);
            if (!df.loadFromFile(path, &e)) return std::nullopt;
            ai.push_back(std::move(df));
        }
        loaded = !items.empty();
    }
    if (!loaded) return std::nullopt;
    ag::CampaignConfig cfg;
    cfg.seed = 2024;
    cfg.aiCount = 6;
    cfg.freeForAll = true;
    ag::MapConfig mc;
    mc.seed = 2024;
    std::string err;
    ag::Galaxy g = ag::MapGenerator(mc, stats, names).generate();
    if (g.stars.empty()) return std::nullopt;
    auto camp = std::make_optional<ag::Campaign>(cfg, g, &tree, items, gizmos, ai, &err);
    if (!err.empty()) return std::nullopt;
    return camp;
}
}  // namespace

// ---- the screen stack: THE CHAIN (named closer of queue row t410) ---------
TEST(sysview_escape_chain_t410) {
    au::ScreenStack st(au::kScreenMap);
    CHECK(st.top() == au::kScreenMap);
    // map -> system view -> planet view (planet.txt info00 route one).
    st.push(au::kScreenSystemView);
    CHECK(st.top() == au::kScreenSystemView);
    st.push(au::kScreenPlanet);
    CHECK(st.top() == au::kScreenPlanet);
    CHECK(st.depth() == 3);
    // Escape unwinds ONE level per press (t252 measured pixel-diff law):
    // 17 -> 16 (NOT straight to the map — the chain depth is the point).
    CHECK(st.escape());
    CHECK(st.top() == au::kScreenSystemView);
    CHECK(st.escape());
    CHECK(st.top() == au::kScreenMap);
    // At the bottom Escape returns false: the standing port quit (t388 law).
    CHECK(!st.escape());
    CHECK(st.top() == au::kScreenMap);
}

TEST(sysview_stack_no_duplicate_levels_t410) {
    au::ScreenStack st(au::kScreenMap);
    st.push(au::kScreenSystemView);
    st.push(au::kScreenPlanet);
    // Re-entering a screen that is already below truncates to it — the
    // stack never stacks a second copy, so unwind depth == navigation depth
    // (the t299 escape-ladder gap class).
    st.push(au::kScreenSystemView);
    CHECK(st.depth() == 2);
    CHECK(st.top() == au::kScreenSystemView);
    st.push(au::kScreenPlanet);
    st.push(au::kScreenStatus);
    // Not-present screens stack (t252: intel opened FROM the species menu
    // Escapes back TO the species menu, not to the galaxy — so a rail-opened
    // screen sits ABOVE what was open); present screens truncate to them.
    CHECK(st.depth() == 4);
    CHECK(st.top() == au::kScreenStatus);
    CHECK(st.levels()[0] == au::kScreenMap);
}

// ---- the state-16 console table (windows.txt verbatim) --------------------
TEST(sysview_console_table_t410) {
    // Rects/messages are the windows.txt state-16 records (file order,
    // _wip_t410 F1 census). A drift here means the table was hand-edited.
    using au::SysCtl;
    CHECK(au::kSysCtlCount == 17);
    struct Exp { const char* name; int x0, y0, x1, y1, msg; };
    const Exp exp[17] = {
        {"TOGGRID",     557, 403, 587, 433, 74},
        {"BATROTLEFT",  479, 403, 493, 433, 50},
        {"BATROTRIGHT", 494, 403, 509, 433, 51},
        {"BATZOOMIN",   518, 403, 548, 418, 54},
        {"BATZOOMOUT",  518, 419, 548, 433, 55},
        {"RECENTER",    596, 442, 626, 472, 71},
        {"TOGELEV",     596, 403, 626, 433, 76},
        {"ABANDON",     479, 442, 548, 472, 84},
        {"My^Items",    479, 103, 548, 133, 804},
        {"Other^Items", 557, 103, 626, 133, 805},
        {"Repeat",      531, 55,  574, 85,  809},
        {"Pass",        479, 55,  522, 85,  807},
        {"Auto",        583, 55,  626, 85,  808},
        {"W",           479, 103, 509, 133, 810},
        {"S",           518, 103, 548, 133, 811},
        {"Z",           557, 103, 587, 133, 813},
        {"I",           596, 103, 626, 133, 812},
    };
    for (int i = 0; i < 17; ++i) {
        const au::SysCtlControl& cc = au::kSysCtl[i];
        CHECK(std::string(cc.name) == exp[i].name);
        CHECK(cc.rect.x0 == exp[i].x0 && cc.rect.y0 == exp[i].y0);
        CHECK(cc.rect.x1 == exp[i].x1 && cc.rect.y1 == exp[i].y1);
        CHECK(cc.sendMessage == exp[i].msg);
    }
    // Hit law: centre of a rect hits it; outside all rects is None.
    CHECK(au::sysCtlFor({572, 418}) == SysCtl::TogGrid);
    CHECK(au::sysCtlFor({611, 457}) == SysCtl::Recenter);
    CHECK(au::sysCtlFor({100, 240}) == SysCtl::None);
    // LAST MATCH WINS resolves the table's own overlaps (t264 scan law):
    // W/S sit inside My^Items' span (file order puts W/S later).
    CHECK(au::sysCtlFor({490, 110}) == SysCtl::W);
    CHECK(au::sysCtlFor({530, 110}) == SysCtl::S);
    // The gutter between the console clusters is inert.
    CHECK(au::sysCtlFor({470, 420}) == SysCtl::None);
}

// ---- SHAPEFRAME->record identity + dims parity on the REAL lib -----------
TEST(sysview_shape_identity_parity_t410) {
    REQUIRE_DATA();
    ascend::formats::ShapeLibrary lib;
    std::string e;
    if (!lib.load(kRepo + "/extracted/ascend01/data/16battle.shp", &e)) {
        CHECK(!"16battle.shp failed to load");
        return;
    }
    CHECK(lib.count() == 20);  // dims census work/r1/t410_16battle_dims.py
    // No full-screen record exists (F3): the backdrop test must decline it.
    for (int i = 0; i < lib.count(); ++i) {
        const auto& r = lib.record(i);
        CHECK(r.width < 600 || r.height < 400);
    }
    for (int i = 0; i < au::kSysCtlCount; ++i) {
        const au::SysCtl c = static_cast<au::SysCtl>(i);
        const au::SysCtlControl& cc = au::kSysCtl[i];
        const int rec = au::sysCtlShapeRecord(c);
        if (c == au::SysCtl::MyItems || c == au::SysCtl::Abandon) {
            // The two named-seam faces (off-parity ladder, F3): refused.
            CHECK(rec == -1);
            CHECK(cc.shapeFrame == 7 || cc.shapeFrame == 8);
            continue;
        }
        CHECK(rec == cc.shapeFrame);  // IDENTITY law (t394)
        if (rec < 0 || rec >= lib.count()) continue;
        const auto& r = lib.record(rec);
        // DIMS PARITY: shape == rect minus 1 on both axes (t394 law re-run).
        CHECK(int(r.width) == cc.rect.x1 - cc.rect.x0 + 1 - 1);
        CHECK(int(r.height) == cc.rect.y1 - cc.rect.y0 + 1 - 1);
    }
}

// ---- orbital layout law ----------------------------------------------------
TEST(sysview_orbit_layout_t410) {
    // angle wrapped into [0, 2pi), deterministic; radius ladder linear.
    for (int i = 0; i < 64; ++i) {
        CHECK(au::orbitAngle(i) >= 0.0 && au::orbitAngle(i) < 6.283185307179586);
        CHECK(au::orbitAngle(i) == au::orbitAngle(i));  // pure
    }
    CHECK(au::orbitAngle(0) == 0.0);
    CHECK(au::orbitRadius(0) == 60.0);
    CHECK(au::orbitRadius(4) == 60.0 + 34.0 * 4);
    // FIT LAW (the ui systemCam default focal, zs = 1): the outer ring of a
    // 5-body system (196 px) sits inside the BatModeWnd half-height 232.
    CHECK(au::orbitRadius(4) <= 232.0);
    // hitOrbitDot on hand-built dots: at the dot, near it, far from it.
    std::vector<au::OrbitDot> dots;
    au::OrbitDot a; a.planetIndex = 0; a.pos = au::Pt{100, 100}; a.radius = 7;
    au::OrbitDot b; b.planetIndex = 2; b.pos = au::Pt{300, 200}; b.radius = 4;
    dots.push_back(a); dots.push_back(b);
    CHECK(au::hitOrbitDot(dots, {100, 100}) == 0);
    CHECK(au::hitOrbitDot(dots, {305, 203}) == 2);
    CHECK(au::hitOrbitDot(dots, {100, 300}) == -1);
}

TEST(sysview_orbit_dots_campaign_t410) {
    REQUIRE_DATA();
    const auto camp = seededCampaign();
    if (!camp) { CHECK(!"fixture failed"); return; }
    au::Camera3d cam;
    cam.bounds = au::kBatModeWnd;
    // Find one owned star and one neutral star (seeded 2024 campaign).
    int owned = -1, neutral = -1;
    for (const auto& s : camp->galaxy().stars) {
        if (camp->starOwner(s.id) == ag::kPlayer && owned < 0) owned = s.id;
        if (camp->starOwner(s.id) < 0 && neutral < 0) neutral = s.id;
    }
    CHECK(owned >= 0);
    CHECK(neutral >= 0);
    if (owned < 0 || neutral < 0) return;
    const auto odots = au::systemOrbits(*camp, owned, cam);
    const auto& s = camp->galaxy().stars[size_t(owned)];
    CHECK(int(odots.size()) == int(s.planets.size()));  // every body shows
    // Colonisation law: ONE PlanetState per star (t406) -> index 0 is the
    // colonised world, the rest are bare.
    CHECK(odots[0].colonised);
    for (size_t i = 1; i < odots.size(); ++i) CHECK(!odots[i].colonised);
    CHECK(odots[0].owner == ag::kPlayer);
    // Neutral system: no dot is colonised.
    const auto ndots = au::systemOrbits(*camp, neutral, cam);
    for (const auto& d : ndots) CHECK(!d.colonised);
    // Determinism: same inputs, same pixels (zero rng).
    const auto again = au::systemOrbits(*camp, owned, cam);
    CHECK(again.size() == odots.size());
    for (size_t i = 0; i < again.size() && i < odots.size(); ++i) {
        CHECK(again[i].pos.x == odots[i].pos.x);
        CHECK(again[i].pos.y == odots[i].pos.y);
    }
    // Out-of-domain star: empty, never a crash.
    CHECK(au::systemOrbits(*camp, -1, cam).empty());
    CHECK(au::systemOrbits(*camp, int(camp->galaxy().stars.size()) + 5, cam)
              .empty());
}

// ---- the screen law for id 16 ---------------------------------------------
TEST(sysview_screen_law_t410) {
    CHECK(au::kScreenSystemView == 16);  // windows.txt STATE id, t338 edx
    CHECK(au::screenKnown(au::kScreenSystemView));
    CHECK(std::string(au::screenShapeLib(au::kScreenSystemView)) ==
          "16battle.shp");  // TYPE-100 ln1140-1142 EXPLICIT naming
    CHECK(std::string(au::screenName(au::kScreenSystemView)) ==
          "System Display");  // help.txt ln1149 verbatim
    // COSMOSWnd's STATE list "4 1 3 7 13" excludes 16: NO rail button is
    // active in the system view (the t369 NEXTTURN-stuck note, table-cited).
    for (int b = 0; b < au::kRailButtonCount; ++b)
        CHECK(!au::railActive(static_cast<au::RailButton>(b),
                              au::kScreenSystemView));
    // 13 (NEGSCREEN) stays unknown; 16 joins the known set.
    CHECK(!au::screenKnown(13));
}
