// SPDX-License-Identifier: GPL-3.0-or-later
// tPF-6 ARMED-CELL PLANLIST FILTER pins (D28 item 11). Law: when PLANLIST
// opens from a square popup's Build button on an ARMED cell, the item list is
// the REQUIRES-gated table filtered by the placement checker for THAT cell —
// the vendor's 54-append loop 0x3d550..0x3d58e calls checker 0x3830c(item,
// cell) per item before ever appending Build (docs/re/_wip_tPF2d.md D6), so a
// row the checker refuses never appears next to a Build button. armedCell = -1
// (plain PLBUILD open) keeps the pre-tPF-6 membership EXACTLY.
// Citations: ui/planetview.h projectOptionsFor block; docs/re/_wip_tPF6.md P4.
#include "ui/planetview.h"

#include <cstdio>
#include <memory>
#include <optional>
#include <string>
#include <vector>

#include "game/campaign.h"
#include "harness.h"

#ifndef ASCENDANCY_SOURCE_DIR
#define ASCENDANCY_SOURCE_DIR "."
#endif

namespace {
namespace au = ascend::ui;
namespace ag = ascend::game;

inline const std::string& kRepoDir() {
    static const std::string s = ASCENDANCY_SOURCE_DIR;
    return s;
}

// Fixture pattern verbatim from test_planetview_t418b (shared shape).
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

// planetview.cpp:208 file-local constant (0x384f5 domain boundary).
constexpr int kSurfaceItemMax = 22;

int playerStar(const ag::Campaign& c) {
    for (const auto& s : c.galaxy().stars)
        if (c.starOwner(s.id) == ag::kPlayer) return int(s.id);
    return -1;
}

bool holds(const std::vector<au::ProjectOption>& opts, int item) {
    for (const auto& o : opts)
        if (o.item == item) return true;
    return false;
}
}  // namespace

// The filter itself: ring cell keeps ONLY orbital items; surface cell keeps
// ONLY surface items; -1 is the untouched full list.
TEST(planlist_armed_cell_filter_tpf6) {
    REQUIRE_DATA();
    auto copt = seededCampaign();
    CHECK(copt.has_value());
    if (!copt) return;
    ag::Campaign& c = *copt;
    const int star = playerStar(c);
    CHECK(star >= 0);
    if (star < 0) return;
    auto& ps = const_cast<ag::PlanetState&>(c.planetAt(star));
    const int surf = ps.surfaceCells;
    CHECK(surf > 0);
    const int size = ag::Campaign::sizeClassFor(surf);
    CHECK(size >= 0);
    ps.pop = 0;
    ps.cellClasses.assign(size_t(surf) + 10, 1);

    // -1 baseline: every REQUIRES-passing item, both domains present.
    const auto base = au::projectOptionsFor(c, star);
    CHECK(!base.empty());
    bool baseHasSurface = false, baseHasOrbital = false;
    for (const auto& o : base) {
        if (o.item < kSurfaceItemMax) baseHasSurface = true;
        if (o.item >= 22 && o.item <= 30) baseHasOrbital = true;
    }
    CHECK(baseHasSurface);
    CHECK(baseHasOrbital);

    // ARMED RING SLOT: an orbital item the REQUIRES gate passes must survive;
    // every SURFACE item must be gone (XOR leg 0x384db refuses both-differ,
    // and the vendor would never append Build for it).
    ps.items.clear();
    ps.itemCells.clear();
    const auto ring = au::projectOptionsFor(c, star, surf);
    for (const auto& o : ring)
        if (o.item < 31)
            CHECK(o.item >= kSurfaceItemMax);  // no surface rows on the ring
                                               // (XOR leg; items 31..38 are
                                               // XOR-EXEMPT 0x384e0 and may
                                               // legitimately remain)
    // Colony Base (item 5, adjacency-exempt 0x385f6) is a SURFACE item: it
    // must NOT appear on the ring even though it needs no neighbour.
    CHECK(!holds(ring, 5));

    // ARMED SURFACE CELL next to an ACTIVE item: orbital rows must be gone.
    // The ACTIVE cell must be found from the SCENARIO state (the home CB
    // lands on a rng cell, not cell 0 — pinning itemCells={0} and arming
    // cell 1 would test a planet with NO active neighbour, where refusing
    // everything is the correct law). Derive an adjacent pair with the grid
    // law itself: cell whose (row+1) exists.
    ps.items.clear();
    ps.itemCells.clear();
    const auto& tt = c.terrainTables();
    int activeCell = -1, armedCell = -1;
    for (int cell = 0; cell < surf && activeCell < 0; cell++) {
        int r = 0, col = 0;
        if (!au::gridRowCol(tt, size, surf, cell, &r, &col)) continue;
        const int n = au::gridCellFor(tt, size, r + 1, col);
        if (n >= 0 && n < surf) { activeCell = cell; armedCell = n; }
    }
    std::printf("tpf6 fixture active=%d armed=%d\n", activeCell, armedCell);
    CHECK(activeCell >= 0 && armedCell >= 0);
    if (activeCell < 0) return;
    ps.items = {5};
    ps.itemCells = {activeCell};
    const auto sfc = au::projectOptionsFor(c, star, armedCell);
    for (const auto& o : sfc)
        CHECK(!(o.item >= 22 && o.item <= 30));  // no orbital rows on surface
                                                 // (always XOR-refused)
    // Kept-set law: the armed-surface list is EXACTLY {base rows the checker
    // grants on armedCell} (the active neighbour at activeCell grants
    // adjacency via the 0x386fc jne-exit).
    for (const auto& o : base) {
        const bool kept = holds(sfc, o.item);
        const bool grants =
            au::placementBlock(c, star, o.item, armedCell) ==
            au::PlacementBlock::None;
        CHECK(kept == grants);
    }
    // And the surface list is non-empty on this fixture (an all-refused list
    // would make the loop above vacuous): at least one base row survives.
    CHECK(!sfc.empty());

    // Consistency pin (anti-stub): every surviving row is exactly a
    // checker-pass row of the baseline for that cell — no row appears that
    // placementBlock refuses, none disappears that it grants.
    for (const auto& o : au::projectOptionsFor(c, star, surf))
        CHECK(au::placementBlock(c, star, o.item, surf) == au::PlacementBlock::None);
    for (const auto& o : sfc)
        CHECK(au::placementBlock(c, star, o.item, armedCell) ==
              au::PlacementBlock::None);
    for (const auto& o : base) {
        const bool ringKept = holds(au::projectOptionsFor(c, star, surf), o.item);
        const bool ringGrants =
            au::placementBlock(c, star, o.item, surf) == au::PlacementBlock::None;
        CHECK(ringKept == ringGrants);
    }
}

// Wiring pin (source-text, tPF-6): the three ui.cpp call sites must pass the
// armed cell — a dropped argument silently reverts to the unfiltered list.
TEST(planlist_armed_cell_wiring_tpf6) {
    REQUIRE_DATA();
    const std::string path =
        std::string(kRepoDir()) + "/rewrite/src/ui/ui.cpp";
    FILE* f = std::fopen(path.c_str(), "rb");
    CHECK(f != nullptr);
    if (!f) return;
    std::string src;
    char buf[8192];
    size_t n;
    while ((n = std::fread(buf, 1, sizeof(buf), f)) > 0) src.append(buf, n);
    std::fclose(f);
    // Every projectOptionsFor call in ui.cpp passes the armed-cell argument.
    size_t pos = 0, calls = 0, armed = 0;
    while ((pos = src.find("projectOptionsFor(", pos)) != std::string::npos) {
        calls++;
        const size_t end = src.find(")", pos);
        const std::string arg = src.substr(pos, end - pos);
        if (arg.find("planetCellArmed") != std::string::npos) armed++;
        pos += 10;
    }
    CHECK(calls >= 3);
    CHECK(armed == calls);
}
