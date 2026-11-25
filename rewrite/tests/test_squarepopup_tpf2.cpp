// SPDX-License-Identifier: GPL-3.0-or-later

// tPF-2 SQUARE-INFO POPUP pins (D28 P3/P5 refcaps; law docs/re/_wip_tPF2.md
// F3b/F3c, indpopups.h):
//   1. CONTENT LAW (builder key-3 case 0x3de5a..0x3e2c8): title
//      getter(89) "<Colour> Square" + body per class:
//      White -> getter(91) verbatim; Black -> getter(92) verbatim (TWO
//      spaces); Red/Green/Blue -> getter(93) with producer noun; orbital
//      -> getter(83) title + getter(90) body. Holds 0x14 / 0x50.
//   2. RUINS: class&8 + owner==player -> "Xenoarcheological Ruins"
//      (getter 88) with NO body (0x3e1c1 jne), never buildable.
//   3. BUTTON LAW (refcaps): buildable iff surface cell, EMPTY, with an
//      ACTIVE 4-neighbour; occupied / no-neighbour / orbital -> false.
#include <cmath>
#include <cstdio>
#include <cstdlib>
#include <optional>
#include <string>
#include <vector>

#include "game/campaign.h"
#include "ui/indpopups.h"
#include "ui/planetview.h"  // gridRowCol / gridCellFor
#include "harness.h"

namespace {
namespace au = ascend::ui;
namespace ag = ascend::game;
#define REQUIRE(cond)              \
    do {                           \
        CHECK((cond));             \
        if (!(cond)) return;       \
    } while (0)

// Fixture verbatim from test_indpopups_tplb2 (seed-2024 Control).
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
        auto st = ag::StarStats::load(ASCENDANCY_SOURCE_DIR "/extracted/ascend00/starstat.txt", &e);
        if (!st) return std::nullopt;
        stats = *st;
        names = ag::loadStarNames(ASCENDANCY_SOURCE_DIR "/extracted/ascend00/names.txt", &e);
        tree = ag::ResearchTree::loadFromFile(ASCENDANCY_SOURCE_DIR "/extracted/ascend00/restree.txt", e);
        items = ag::loadPlanItems(ASCENDANCY_SOURCE_DIR "/extracted/ascend00/planitem.txt", e);
        gizmos = ag::loadGizmos(ASCENDANCY_SOURCE_DIR "/extracted/ascend00/gizmos.txt", e);
        for (int i = 0; i < 6; ++i) {
            ag::DipFile df;
            char path[256];
            std::snprintf(path, sizeof(path), ASCENDANCY_SOURCE_DIR "/extracted/ascend00/race%02d.dip", i);
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

TEST(square_popup_content_law_tpf2) {
    auto campOpt = seededCampaign();
    REQUIRE(campOpt.has_value());
    ag::Campaign& camp = *campOpt;
    int star = -1;
    for (size_t s = 0; s < camp.galaxy().stars.size() && star < 0; ++s)
        if (camp.starOwner(int(s)) == ag::kPlayer) star = int(s);
    REQUIRE(star >= 0);
    auto& ps = const_cast<ag::PlanetState&>(camp.planetAt(star));
    const int surf = ps.surfaceCells;
    REQUIRE(!ps.cellClasses.empty());
    struct Case { int cls; const char* title; std::string body; };
    const Case cases[] = {
        {0, "Black Square",
         "Black squares are uninhabitable.  Most structures cannot be built on them."},
        {1, "White Square",
         "White squares are ordinary habitable surface squares."},
        {2, "Red Square",
         "Red squares increase the effectiveness of industry-producing structures."},
        {3, "Green Square",
         "Green squares increase the effectiveness of prosperity-producing structures."},
        {4, "Blue Square",
         "Blue squares increase the effectiveness of research-producing structures."},
    };
    for (const auto& c : cases) {
        ps.cellClasses[0] = c.cls;
        auto si = au::squareInfoLines(camp, star, 0);
        REQUIRE(si.lines.size() == 2);
        CHECK(si.lines[0].text == c.title);
        CHECK(si.lines[0].hold == 0x14);
        CHECK(si.lines[1].text == c.body);
        CHECK(si.lines[1].hold == 0x50);
    }
    // Ruins flag (bit3) on an OWNED cell: title switches, NO body, never
    // buildable (0x3e12f ruins arm + 0x3e1c1 jne).
    ps.cellClasses[0] = 1 | 8;
    {
        auto si = au::squareInfoLines(camp, star, 0);
        REQUIRE(si.lines.size() == 1);
        CHECK(si.lines[0].text == "Xenoarcheological Ruins");
        CHECK(!si.buildable);
    }
    // Orbital slot: colour word Orbital + getter(90) body; no Build.
    {
        auto si = au::squareInfoLines(camp, star, surf);
        REQUIRE(si.lines.size() == 2);
        CHECK(si.lines[0].text == "Orbital Square");
        CHECK(si.lines[1].text.find("Orbital squares are used for building") == 0);
        CHECK(si.lines[1].text.find("Shipyards and Ships.") != std::string::npos);
        CHECK(!si.buildable);
    }
    // Out-of-domain: no popup at all (0x3de66 jl / slot cap).
    CHECK(au::squareInfoLines(camp, star, surf + 10).lines.empty());
    CHECK(au::squareInfoLines(camp, -1, 0).lines.empty());
}

TEST(square_popup_button_law_tpf2) {
    auto campOpt = seededCampaign();
    REQUIRE(campOpt.has_value());
    ag::Campaign& camp = *campOpt;
    int star = -1;
    for (size_t s = 0; s < camp.galaxy().stars.size() && star < 0; ++s)
        if (camp.starOwner(int(s)) == ag::kPlayer) star = int(s);
    REQUIRE(star >= 0);
    auto& ps = const_cast<ag::PlanetState&>(camp.planetAt(star));
    const int surf = ps.surfaceCells;
    REQUIRE(surf > 2);
    // EMPTY planet: no active neighbour anywhere -> never buildable.
    ps.items.clear();
    ps.itemCells.clear();
    CHECK(!au::squareBuildable(camp, star, 0));
    // Place one ACTIVE structure directly (item 0 at cell 0).
    ps.items.push_back(0);
    ps.itemCells.push_back(0);
    // The occupied cell refuses (empty-cell gate).
    CHECK(!au::squareBuildable(camp, star, 0));
    const int size = ag::Campaign::sizeClassFor(surf);
    REQUIRE(size >= 0);
    int row = 0, col = 0;
    REQUIRE(au::gridRowCol(camp.terrainTables(), size, surf, 0, &row, &col));
    // A lattice 4-neighbour of the base grants (D28 P3: Build+Cancel).
    int nb = -1;
    const int dr[4] = {1, -1, 0, 0}, dc[4] = {0, 0, -1, 1};
    for (int d = 0; d < 4 && nb < 0; ++d) {
        const int n = au::gridCellFor(camp.terrainTables(), size, row + dr[d],
                                      col + dc[d]);
        if (n >= 0 && n < surf && n != 0) nb = n;
    }
    REQUIRE(nb >= 0);
    CHECK(au::squareBuildable(camp, star, nb));
    // Manhattan grid distance >= 3 from the base refuses (D28 P5: OK only).
    int far = -1;
    for (int c = 0; c < surf && far < 0; ++c) {
        if (c == 0) continue;
        int r2 = 0, c2 = 0;
        if (!au::gridRowCol(camp.terrainTables(), size, surf, c, &r2, &c2))
            continue;
        if (std::abs(r2 - row) + std::abs(c2 - col) >= 3) far = c;
    }
    if (far >= 0) CHECK(!au::squareBuildable(camp, star, far));
    // The info popup agrees with the gate on the neighbour cell.
    auto si = au::squareInfoLines(camp, star, nb);
    CHECK(si.buildable);
    CHECK(si.lines.size() == 2);
}
