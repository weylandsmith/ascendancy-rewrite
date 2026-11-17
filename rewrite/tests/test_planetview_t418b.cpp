// SPDX-License-Identifier: GPL-3.0-or-later
// t418b SURFACE TILE GRID pins: the F1 grid law (valid cols B..B+C, cell =
// cumWidth+col-B, FUN_000395c4 verbatim), the FUN_0003965c inverse INCLUDING
// the loop-test correction (cum+C at 0x396b0/0x396b5, NOT cum+B+C — with B>0
// the wrong test lands invalid cols), the F2 isometric lattice + diamond
// hit-test, and the F3 adjacency refuse with its four skip legs (0x385b7
// cell>=+0x18, 0x385ee own-ACTIVE, 0x385f6 item 5, 0x385ff item 38).
// Citations: ui/planetview.h header, docs/re/_wip_t418.md F1/F2/F3.
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

const ag::TerrainTables& TT = ag::vendorTerrainTables();

inline const std::string& kRepoDir() {
    static const std::string s = ASCENDANCY_SOURCE_DIR;
    return s;
}

// Fixture pattern verbatim from test_planetview_t406 (shared shape).
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
}  // namespace

// ---- F1: the grid table + valid-cell census --------------------------------
TEST(planetgrid_census_t418b) {
    // Spot values, planitem.txt verbatim (tokens 45..194; the full-table
    // file==vendor equality is pinned by test_terrain_t294, which now
    // covers grids B/C through TerrainTables::operator==).
    CHECK(TT.rowOffset[2][8] == 7);
    CHECK(TT.rowWidth[4][5] == 9);
    for (int size = 0; size < 5; size++) {
        std::vector<int> seen(size_t(TT.surfaceBySize[size]), 0);
        int valid = 0;
        for (int row = 0; row < 15; row++) {
            const int B = TT.rowOffset[size][row], C = TT.rowWidth[size][row];
            // just-outside cols refuse on both ends
            CHECK(au::gridCellFor(TT, size, row, B - 1) == -1);
            CHECK(au::gridCellFor(TT, size, row, B + C) == -1);
            for (int col = B; col < B + C; col++) {
                const int cell = au::gridCellFor(TT, size, row, col);
                CHECK(cell >= 0 && cell < TT.surfaceBySize[size]);
                if (cell >= 0 && cell < TT.surfaceBySize[size]) seen[size_t(cell)]++;
                valid++;
            }
        }
        // rows with C==0 have NO valid col at all (col 0 included)
        for (int row = 0; row < 15; row++)
            if (!TT.rowWidth[size][row])
                CHECK(au::gridCellFor(TT, size, row, 0) == -1);
        CHECK(valid == TT.surfaceBySize[size]);  // 7/11/23/45/73
        for (size_t c = 0; c < seen.size(); c++) CHECK(seen[c] == 1);
    }
    // domain guards
    CHECK(au::gridCellFor(TT, -1, 4, 4) == -1);
    CHECK(au::gridCellFor(TT, 5, 4, 4) == -1);
    CHECK(au::gridCellFor(TT, 2, -1, 3) == -1);
    CHECK(au::gridCellFor(TT, 2, 15, 3) == -1);
}

// ---- F1: the worked example + the inverse loop-test correction ------------
TEST(planetgrid_inverse_t418b) {
    // Worked example size class 2 (23 cells): row2 col3 -> cell0, row8 col7
    // -> cell22 (docs/re/_wip_t418.md F1).
    CHECK(au::gridCellFor(TT, 2, 2, 3) == 0);
    CHECK(au::gridCellFor(TT, 2, 8, 7) == 22);
    // THE CORRECTION WITNESS (0x396b0/0x396b5 test cum+C, B only in the col
    // formula): size-2 cell 14 -> row6 col4 (cum=14, B[6]=4). A walk testing
    // cum+B+C breaks early at row5 and lands col 8 — OUTSIDE row 5's valid
    // cols 3..7 — so this coordinate separates the two loop laws directly;
    // cell 18 (correct row7 col5; buggy row6 col8 invalid) is a second.
    int row = -1, col = -1;
    CHECK(au::gridRowCol(TT, 2, 23, 14, &row, &col));
    CHECK(row == 6 && col == 4);
    CHECK(au::gridCellFor(TT, 2, 6, 4) == 14);
    CHECK(au::gridRowCol(TT, 2, 23, 18, &row, &col));
    CHECK(row == 7 && col == 5);
    CHECK(au::gridCellFor(TT, 2, 7, 5) == 18);
    // round-trip EVERY cell of EVERY class, and the inverse lands on a col
    // gridCellFor accepts (this is what kills the cum+B+C mutant wholesale).
    for (int size = 0; size < 5; size++)
        for (int cell = 0; cell < TT.surfaceBySize[size]; cell++) {
            int r = -1, c = -1;
            CHECK(au::gridRowCol(TT, size, TT.surfaceBySize[size], cell, &r, &c));
            CHECK(au::gridCellFor(TT, size, r, c) == cell);
        }
    // the 0xffffffff leg: non-surface cells refuse. DIRECT call (orderCell
    // -Block's own 0x385b7 guard otherwise masks this boundary — mutation
    // M4 triage): cell == surfaceCells must refuse (0x39671 jae).
    CHECK(!au::gridRowCol(TT, 2, 23, 23, &row, &col));
    CHECK(!au::gridRowCol(TT, 2, 23, -1, &row, &col));
    CHECK(!au::gridRowCol(TT, 2, 23, 30, &row, &col));  // orbital ring
    CHECK(!au::gridRowCol(TT, 0, 7, 7, &row, &col));
}

// ---- F2: the isometric lattice + diamond hit-test --------------------------
TEST(planetgrid_lattice_t418b) {
    // Immediates: x-cursor 110 step +17/row (0x3bb5d), y 410 step -34/row;
    // per-cell x += 34 (imul 0x22 @0x3c211), y += 17 (imul 0x11 @0x3c23f).
    const au::Pt o = au::tileCenter(0, 0, 0);
    CHECK(o.x == 110 && o.y == 410);
    const au::Pt a = au::tileCenter(2, 3, 4), b = au::tileCenter(2, 3, 5),
                 d = au::tileCenter(2, 4, 4);
    CHECK(b.x - a.x == 34 && b.y - a.y == 17);   // col step (34,17)
    CHECK(d.x - a.x == 17 && d.y - a.y == -34);  // row step (17,-34)
    // absolute col law (col incl. B — the paint loop counts from B[row]):
    // size-2 row2 (B=3) first cell col3 sits at 110 + 2*17 + 3*34 = 246.
    const au::Pt t = au::tileCenter(2, 2, 3);
    CHECK(t.x == 246 && t.y == 410 + 3 * 17 - 2 * 34);
    // hit-test: EVERY tile centre hits ITSELF (uniqueness over the tiling).
    for (int size = 0; size < 5; size++)
        for (int r = 0; r < 15; r++)
            for (int c = TT.rowOffset[size][r];
                 c < TT.rowOffset[size][r] + TT.rowWidth[size][r]; c++) {
                const au::Pt p = au::tileCenter(size, r, c);
                CHECK(au::tileHitFor(TT, size, TT.surfaceBySize[size], p) ==
                      au::gridCellFor(TT, size, r, c));
            }
    // outside the diamond: 35 px right of a centre is beyond the x±34
    // vertex (and the col-neighbour centre at +34,+17 is beyond too:
    // 17*1+34*17 > 578) -> miss.
    const au::Pt mid = au::tileCenter(2, 5, 5);
    CHECK(au::tileHitFor(TT, 2, 23, au::Pt{mid.x + 35, mid.y}) == -1);
    CHECK(au::tileHitFor(TT, 2, 23, au::Pt{mid.x, mid.y + 18}) == -1);
    // inside: 33 px right (within the vertex) hits the same tile.
    CHECK(au::tileHitFor(TT, 2, 23, au::Pt{mid.x + 33, mid.y}) ==
          au::gridCellFor(TT, 2, 5, 5));
}

// ---- F3: the adjacency refuse + the four skip legs -------------------------
TEST(planetgrid_adjacency_t418b) {
    REQUIRE_DATA();
    auto copt = seededCampaign();
    CHECK(copt.has_value());
    if (!copt) return;
    ag::Campaign& c = *copt;
    int star = -1;
    for (const auto& s : c.galaxy().stars)
        if (c.starOwner(s.id) == ag::kPlayer) { star = s.id; break; }
    CHECK(star >= 0);
    if (star < 0) return;
    // established harness idiom (t45/t204): const_cast on planetAt.
    auto& ps = const_cast<ag::PlanetState&>(c.planetAt(star));
    const int surf = ps.surfaceCells;
    const int size = ag::Campaign::sizeClassFor(surf);
    CHECK(size >= 0);
    if (size < 0) return;
    // State A: ONE active item on cell 0 (Factory, item 0).
    ps.items = {0};
    ps.itemCells = {0};
    // Neighbours of cell 0 per size class, VERBATIM from the grid tables
    // (measured by hand this session: size0 {1,2}, size1 {2}, size2 {2},
    // size3 {1,3}, size4 {1,4}). Each neighbour REFUSES, each non-neighbour
    // inactive cell ACCEPTS (None).
    static const int kNbr0[5][2] = {{1, 2}, {2, -1}, {2, -1}, {1, 3}, {1, 4}};
    for (int k = 0; k < 2; k++)
        if (kNbr0[size][k] >= 0)
            CHECK(au::orderCellBlock(c, star, 1, kNbr0[size][k]) ==
                  au::OrderCellBlock::ActiveNeighbour);
    // skip leg 0x385f6: item 5 Colony is exempt even on an active neighbour.
    CHECK(au::orderCellBlock(c, star, 5, kNbr0[size][0]) ==
          au::OrderCellBlock::None);
    // skip leg 0x385ff: item 38 Xeno Dig exempt.
    CHECK(au::orderCellBlock(c, star, 38, kNbr0[size][0]) ==
          au::OrderCellBlock::None);
    // skip leg 0x385b7: cell >= surfaceCells (orbital ring) never asks.
    CHECK(au::orderCellBlock(c, star, 1, surf) == au::OrderCellBlock::None);
    CHECK(au::orderCellBlock(c, star, 1, -1) == au::OrderCellBlock::None);
    // a NON-neighbour inactive cell passes. Pick a surface cell that is
    // neither 0 nor a neighbour (every shipped grid has one).
    int far = -1;
    for (int cell = 1; cell < surf; cell++) {
        if (cell == kNbr0[size][0] || cell == kNbr0[size][1]) continue;
        far = cell;
        break;
    }
    CHECK(far >= 0);
    if (far >= 0)
        CHECK(au::orderCellBlock(c, star, 1, far) == au::OrderCellBlock::None);
    // State B (skip leg 0x385ee, mutation-rule-5 shape): items on cell 0 AND
    // on its FIRST neighbour — so cell 0 is active AND HAS an active
    // neighbour. The own-ACTIVE skip is now the only leg that can answer
    // None for cell 0; deleting it flips this to ActiveNeighbour.
    ps.items = {0, 0};
    ps.itemCells = {0, kNbr0[size][0]};
    CHECK(au::orderCellBlock(c, star, 1, 0) == au::OrderCellBlock::None);
    // and cell 0's OTHER neighbour (active via cell 0) still refuses.
    if (kNbr0[size][1] >= 0)
        CHECK(au::orderCellBlock(c, star, 1, kNbr0[size][1]) ==
              au::OrderCellBlock::ActiveNeighbour);
    // State C (mutation M10 triage): the FOUR probes are the directional
    // TABLE row±1/col±1 — losing any leg must flip some fixture. For the
    // seeded planet's size class, scan every ordered (active cell A, other
    // cell B) pair: B refuses iff B shares a row/col lattice line with A
    // (B in {(Ar±1,Ac),(Ar,Ac±1)} via gridCellFor). This exercises all four
    // directions (a dropped leg drops exactly the refusals it owns).
    {
        const auto& tt = c.terrainTables();
        auto rc = [&](int cell, int& r, int& cc) {
            return au::gridRowCol(tt, size, surf, cell, &r, &cc);
        };
        int checked = 0;
        for (int A = 0; A < surf; A++) {
            int ar = 0, ac = 0;
            rc(A, ar, ac);
            for (int Bc = 0; Bc < surf; Bc++) {
                if (Bc == A) continue;
                int br = 0, bc = 0;
                rc(Bc, br, bc);
                const bool nbr = au::gridCellFor(tt, size, ar + 1, ac) == Bc ||
                                 au::gridCellFor(tt, size, ar - 1, ac) == Bc ||
                                 au::gridCellFor(tt, size, ar, ac + 1) == Bc ||
                                 au::gridCellFor(tt, size, ar, ac - 1) == Bc;
                ps.items = {0};
                ps.itemCells = {A};
                const auto got = au::orderCellBlock(c, star, 1, Bc);
                const bool wantRefuse = nbr;
                if ((got == au::OrderCellBlock::ActiveNeighbour) != wantRefuse) {
                    CHECK(false);  // names the pair below
                    std::printf("adjacency mismatch size%d A%d(%d,%d) B%d(%d,%d) got %d\n",
                                size, A, ar, ac, Bc, br, bc, int(got));
                    return;
                }
                ++checked;
            }
        }
        CHECK(checked == surf * (surf - 1));
    }
    // NO active items at all: nothing refuses.
    ps.items.clear();
    ps.itemCells.clear();
    CHECK(au::orderCellBlock(c, star, 1, 0) == au::OrderCellBlock::None);
}
