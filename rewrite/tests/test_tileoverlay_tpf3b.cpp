// SPDX-License-Identifier: GPL-3.0-or-later

// tPF-3b TILE-OVERLAY + STRUCTURE-ART ANCHOR pins.
// Law: docs/re/_wip_tPF3.md F8..F11 (raw asm dumps of work/ascend_restored.bin;
// planitem.shp bbox census measured this session via the port's own loader).
//   1. OVERLAY GEOMETRY 0x3bc5b INSET vs 0x3bd4d TINY — both branches shrink the
//      SAME full vertex table (centre +-{34} x, +-{17} y): inset deltas
//      y+1/x-2/y-1/x+2 -> half-extents {32,16,32,16}; tiny deltas y+14/x-28/
//      y-14/x+28 -> {6,3,6,3}. Both strictly inside the full diamond.
//   2. LEGALITY = placement checker 0x3830c called with ITEM ARG 0xff
//      (mov edx,0xff @0x3c2c7), reduced at bytes: rule B 0x38493 GRANTS
//      unconditionally for 0xff (0x384af cmp dl,0xff / je 0x384d6), rule C
//      skipped, rule D 0x38519 vetoes rock, rule G vets all-inactive and skips
//      the probe when the cell's own slot is active.
//      => inset iff NOT rock AND (own slot active OR an ACTIVE 4-neighbour).
//      Barren (class 0) non-rock adjacent is INSET — F5's class gate REFUTED.
//   3. ANCHOR LAW: dest = (centre.x + recLeft, centre.y - 17 + recTop); the
//      measured planitem.shp surface records 0..21 are all left=-34 with top in
//      {-1..-18} (rec0 Colony Base -34,-9 H=43), so the port's old
//      (w/2, h/2) centring sat 5 px LOW for the CB (D28 P7).
//   4. PAINT WIRING: the full-boundary class-colour pass stays (F11 pixel test:
//      full 28/28 edge groups vs inset 3/28 vs density-matched scatter 0/28 on
//      the unscaled vendor capture) and the overlay is an ADDED pass.
#include <cstdio>
#include <fstream>
#include <iterator>
#include <optional>
#include <string>
#include <vector>

#include "formats/shp.h"
#include "game/campaign.h"
#include "ui/planetview.h"
#include "harness.h"

namespace {
namespace au = ascend::ui;
namespace ag = ascend::game;
inline const std::string& kRepoDir() {
    static const std::string s = ASCENDANCY_SOURCE_DIR;
    return s;
}
#define REQUIRE(cond)                        \
    do {                                     \
        CHECK((cond));                       \
        if (!(cond)) return;                 \
    } while (0)

// Fixture verbatim from test_planetview_t418b (same loaders, same seed).
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
        auto st = ag::StarStats::load(kRepoDir() + "/extracted/ascend00/starstat.txt", &e);
        if (!st) return std::nullopt;
        stats = *st;
        names = ag::loadStarNames(kRepoDir() + "/extracted/ascend00/names.txt", &e);
        tree = ag::ResearchTree::loadFromFile(kRepoDir() + "/extracted/ascend00/restree.txt", e);
        items = ag::loadPlanItems(kRepoDir() + "/extracted/ascend00/planitem.txt", e);
        gizmos = ag::loadGizmos(kRepoDir() + "/extracted/ascend00/gizmos.txt", e);
        for (int i = 0; i < 6; ++i) {
            ag::DipFile df;
            char path[256];
            std::snprintf(path, sizeof(path), "%s/extracted/ascend00/race%02d.dip",
                          kRepoDir().c_str(), i);
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

int playerStarOf(const ag::Campaign& c) {
    for (const auto& s : c.galaxy().stars)
        if (c.starOwner(s.id) == ag::kPlayer) return s.id;
    return -1;
}

std::string slurp(const std::string& p) {
    std::ifstream f(p, std::ios::binary);
    if (!f) return {};
    return std::string(std::istreambuf_iterator<char>(f), std::istreambuf_iterator<char>());
}
}  // namespace

TEST(tileoverlay_geometry_tpf3b) {
    // 1. The two vendor branches are shrinks of the full (34,17) diamond.
    const au::TileHalfExtents inset = au::tileOverlayHalfExtents(true);
    const au::TileHalfExtents tiny = au::tileOverlayHalfExtents(false);
    CHECK(inset.left == 32 && inset.right == 32 && inset.top == 16 && inset.bottom == 16);
    CHECK(tiny.left == 6 && tiny.right == 6 && tiny.top == 3 && tiny.bottom == 3);
    // Strictly inside the full diamond on EVERY side (D28 P2 "smaller").
    for (int k = 0; k < 2; k++) {
        const au::TileHalfExtents h = k ? tiny : inset;
        CHECK(h.left < 34 && h.right < 34 && h.top < 17 && h.bottom < 17);
    }
    // The inset is the 2px-x / 1px-y shrink of the full table: 34-2 and 17-1.
    CHECK(inset.left == 34 - 2 && inset.top == 17 - 1);
    // The tiny is the 28px-x / 14px-y shrink: 34-28 and 17-14.
    CHECK(tiny.left == 34 - 28 && tiny.top == 17 - 14);
}

TEST(tileoverlay_legality_tpf3b) {
    auto copt = seededCampaign();
    if (!copt) { printf("SKIP tileoverlay_legality_tpf3b: no vendor tables\n"); return; }
    ag::Campaign& c = *copt;
    const int star = playerStarOf(c);
    REQUIRE(star >= 0);
    auto& ps = const_cast<ag::PlanetState&>(c.planetAt(star));
    const int surf = ps.surfaceCells;
    REQUIRE(surf > 4);
    const int size = ag::Campaign::sizeClassFor(surf);
    REQUIRE(size >= 0);
    const auto& tt = c.terrainTables();

    ps.pop = 0;
    ps.cellClasses.assign(size_t(surf) + 10, 1);  // flat non-rock
    ps.items.clear();
    ps.itemCells.clear();

    // (a) NOTHING active -> rule G vetoes (0x386fc xor edi,edi) -> ALL tiny.
    for (int cell = 0; cell < surf; cell++)
        CHECK(au::tileOverlayInset(c, star, cell) == false);

    // Pick a cell with at least one in-range grid 4-neighbour.
    int rA = 0, cA = 0, A = -1;
    for (int cell = 0; cell < surf && A < 0; cell++) {
        if (!au::gridRowCol(tt, size, surf, cell, &rA, &cA)) continue;
        for (int d = 0; d < 4; d++) {
            const int r2 = rA + (d == 0 ? 1 : d == 1 ? -1 : 0);
            const int c2 = cA + (d == 2 ? -1 : d == 3 ? 1 : 0);
            const int n = au::gridCellFor(tt, size, r2, c2);
            if (n >= 0 && n < surf) { A = cell; break; }
        }
    }
    REQUIRE(A >= 0);
    REQUIRE(au::gridRowCol(tt, size, surf, A, &rA, &cA));

    ps.items = {0};
    ps.itemCells = {A};
    // (b) own-slot-active skips the adjacency probe (0x385ee) -> INSET.
    CHECK(au::tileOverlayInset(c, star, A) == true);
    // (c) an ACTIVE 4-neighbour grants (rule B exit) -> INSET.
    int nbr = -1;
    for (int d = 0; d < 4; d++) {
        const int r2 = rA + (d == 0 ? 1 : d == 1 ? -1 : 0);
        const int c2 = cA + (d == 2 ? -1 : d == 3 ? 1 : 0);
        const int n = au::gridCellFor(tt, size, r2, c2);
        if (n >= 0 && n < surf) { nbr = n; break; }
    }
    REQUIRE(nbr >= 0);
    CHECK(au::tileOverlayInset(c, star, nbr) == true);
    // (d) two steps away: no active neighbour -> veto -> TINY.
    int far = -1;
    for (int cell = 0; cell < surf; cell++) {
        int r = 0, col = 0;
        if (!au::gridRowCol(tt, size, surf, cell, &r, &col)) continue;
        bool adj = (cell == A);
        for (int d = 0; d < 4 && !adj; d++) {
            const int r2 = r + (d == 0 ? 1 : d == 1 ? -1 : 0);
            const int c2 = col + (d == 2 ? -1 : d == 3 ? 1 : 0);
            if (au::gridCellFor(tt, size, r2, c2) == A) adj = true;
        }
        if (!adj) { far = cell; break; }
    }
    if (far >= 0) CHECK(au::tileOverlayInset(c, star, far) == false);

    // (e) ROCK vetoes even with an active neighbour (rule D 0x38519; item 0xff
    //     never takes the dig arm, so nothing rescues it).
    ps.cellClasses[size_t(nbr)] = 1 | 8;
    CHECK(au::tileOverlayInset(c, star, nbr) == false);
    // (f) BARREN class 0 adjacent is INSET — the leg F5 got wrong (0x384af
    //     cmp dl,0xff / je 0x384d6 GRANT precedes any class test for 0xff).
    ps.cellClasses[size_t(nbr)] = 0;
    CHECK(au::tileOverlayInset(c, star, nbr) == true);
    // Rock on the cell's OWN active slot still vetoes (D precedes the own-skip).
    ps.cellClasses[size_t(A)] = 1 | 8;
    CHECK(au::tileOverlayInset(c, star, A) == false);
    ps.cellClasses[size_t(A)] = 1;

    // (g) Out-of-range and ring slots refuse rather than crash (the painter only
    //     overlays surface cells; ring slots are the orbital pass's domain).
    CHECK(au::tileOverlayInset(c, star, -1) == false);
    CHECK(au::tileOverlayInset(c, star, surf) == false);
    CHECK(au::tileOverlayInset(c, star, surf + 5) == false);
    CHECK(au::tileOverlayInset(c, -1, 0) == false);
}

TEST(structure_anchor_law_tpf3b) {
    // 3. dest = (centre.x + left, centre.y - 17 + top). Cited: 0x3c13e pushes
    //    esp+0x264 == the diamond TOP VERTEX y into FUN_0005caac, whose dest is
    //    anchor + record signed bbox; tileCenter() is the CENTRE = top + 17.
    const au::Pt ctr{410, 300};
    const au::Pt cb = au::structureBlitPos(ctr, -34, -9);
    CHECK(cb.x == 376 && cb.y == 274);
    const au::Pt zero = au::structureBlitPos(ctr, 0, 0);
    CHECK(zero.x == 410 && zero.y == 283);
    const au::Pt tall = au::structureBlitPos(ctr, -35, -31);
    CHECK(tall.x == 375 && tall.y == 252);
    // The 5 px the old centring was out at the CB's top edge: (300 - 43/2) =
    // 279 vs the law's 274.
    CHECK((ctr.y - 43 / 2) - cb.y == 5);
    // Anchor law is linear in the record bbox, never in width/height.
    CHECK(au::structureBlitPos(ctr, -34, -1).y == ctr.y - 18);
    CHECK(au::structureBlitPos(ctr, -34, -18).y == ctr.y - 35);
}

TEST(structure_anchor_bbox_census_tpf3b) {
    // 3b. MEASURED planitem.shp bbox law, read through the port's own loader so
    //     the pin tracks the decode law and not a transcription: surface items
    //     0..21 all carry left == -34 with top in {-1..-18}, so blitting is
    //     never a symmetric centring.
    ascend::formats::ShapeLibrary lib;
    std::string err;
    const std::string path =
        kRepoDir() + "/extracted/ascend01/data/planitem.shp";
    if (!lib.load(path, &err)) {
        printf("SKIP structure_anchor_bbox_census_tpf3b: %s\n", err.c_str());
        return;
    }
    const auto& r0 = lib.record(0);
    CHECK(r0.left == -34);
    CHECK(r0.top == -9);
    CHECK(r0.height == 43);
    for (int i = 1; i <= 21 && i < lib.count(); i++) {
        const auto& r = lib.record(i);
        CHECK(r.left == -34);
        CHECK(r.top >= -18 && r.top <= -1);
    }
    // Asymmetry proof: for rec0 the content box is NOT centred on the anchor.
    CHECK(r0.top != -int(r0.height) / 2);
}

TEST(tileoverlay_paint_wiring_tpf3b) {
    // 4. Source-text wiring pin (pixel-free leg): the painter keeps the
    //    FULL-boundary pass (F11: 28/28 vs inset 3/28 vs scatter 0/28), adds the
    //    checker-driven overlay, and never re-centres tile structure art.
    const std::string src = slurp(kRepoDir() + "/rewrite/src/ui/ui.cpp");
    REQUIRE(!src.empty());
    CHECK(src.find("tileOverlayHalfExtents(") != std::string::npos);
    CHECK(src.find("tileOverlayInset(camp, planetStar, cell)") != std::string::npos);
    CHECK(src.find("structureBlitPos(c, sr.left, sr.top)") != std::string::npos);
    // The invented centring of tile art must stay gone.
    CHECK(src.find("c.x - int(sr.width) / 2") == std::string::npos);
    // Full-boundary pass retained with the 34/17 half-extents.
    CHECK(src.find("c.x - 34, c.y, c.x, c.y - 17") != std::string::npos);
}

TEST(tiny_fill_law_tpf3c) {
    // 5. tPF-3c F13 FILL LAW. Vendor pixels (433 composite RIGHT half): tiny
    //    class-colour diamonds are SOLID-filled (red 58/73 = 0.79 of the bbox
    //    diamond, raw (188,44,17) == conv(117) family); BOTH vendor fill calls
    //    are skipped when the pen is 0 (0x3bd31 / 0x3be2a `test,je`) — pen 0
    //    is exactly class 0 (F9). The inset ramp is unrecovered -> no fill.
    CHECK(au::tileOverlaySolidFill(false, 2) == true);    // tiny red
    CHECK(au::tileOverlaySolidFill(false, 3) == true);    // tiny green
    CHECK(au::tileOverlaySolidFill(false, 4) == true);    // tiny blue
    CHECK(au::tileOverlaySolidFill(false, 1) == true);    // tiny white (default)
    CHECK(au::tileOverlaySolidFill(false, 0) == false);   // black pen skip
    CHECK(au::tileOverlaySolidFill(true, 2) == false);    // inset: ramp open
    CHECK(au::tileOverlaySolidFill(true, 0) == false);
    // Wiring: the painter consults the law and never fills the inset branch.
    const std::string src = slurp(kRepoDir() + "/rewrite/src/ui/ui.cpp");
    REQUIRE(!src.empty());
    CHECK(src.find("tileOverlaySolidFill(inset, cls)") != std::string::npos);
}
