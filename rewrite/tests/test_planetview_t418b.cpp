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

// ---- tPL-B1b: the placement chain (XOR / occupied / rock / adjacency) -----
// Pins RE-DERIVED from the raw checker asm (ui/planetview.h F3 block,
// docs/re/_wip_tPLB1.md F7/F9). The t418b original pinned the port's own
// INVERTED adjacency reading (active neighbour = refuse); tPL-B1 F5 proved
// that wrong from raw bytes 0x38666..0x386fc (ACTIVE neighbour exits the
// probe block via jne WITHOUT the 0x386fc `xor edi,edi` = LEGAL; all four
// probes inactive/absent = REFUSE). Replacing those pins with vendor-law
// pins IS the fix.
TEST(planetgrid_placement_t418b) {
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
    const auto& tt = c.terrainTables();
    // Isolate the placement chain: no pop/queue state (placementBlock never
    // reads it — the queue gates are projectOrderable's domain, t406).
    ps.pop = 0;
    // Deterministic fixture terrain: all class 1 (non-rock), one ROCK cell
    // (last surface cell) and one BARREN cell (surf-2) — the rock/dig and
    // terraform arms need both. Cell 0 is non-rock, so the kNbr0 lattice
    // fixtures below hold.
    ps.cellClasses.assign(size_t(surf) + 10, 1);
    ps.cellClasses[size_t(surf - 1)] = 8;
    ps.cellClasses[size_t(surf - 2)] = 0;
    // ---- 0) NO active items at all: rule G zeroes (0x386fc) -> REFUSE.
    // The t418b port returned None here; the vendor refuses every cell for a
    // normal item until something ACTIVE exists (planet.txt info02).
    ps.items.clear();
    ps.itemCells.clear();
    CHECK(au::placementBlock(c, star, 0, 0) ==
          au::PlacementBlock::NoActiveNeighbour);
    // exempt items still order on a bare planet: 5 Colony Base (0x385f6),
    // 35 Automation (0x385ff cmp dl,0x23 — NOT 38; F9 correction).
    CHECK(au::placementBlock(c, star, 5, 0) == au::PlacementBlock::None);
    CHECK(au::placementBlock(c, star, 35, 0) == au::PlacementBlock::None);
    // 38 Xeno Dig is NOT adjacency-exempt, and its rock leg REQUIRES rock
    // (F10: veto iff rock XOR dig) — on non-rock cell 0 it refuses:
    CHECK(au::placementBlock(c, star, 38, 0) ==
          au::PlacementBlock::RockMismatch);
    // ---- 1) XOR leg 0x384db (item < 31 only; EQUAL booleans pass) --------
    // surface item on the orbital ring refuses (true != false):
    CHECK(au::placementBlock(c, star, 0, surf) ==
          au::PlacementBlock::SurfaceVsRing);
    CHECK(au::placementBlock(c, star, 21, surf + 3) ==
          au::PlacementBlock::SurfaceVsRing);
    // orbital item (22..30) on a surface cell refuses (false != true) —
    // INDEPENDENT of adjacency (the t418b code skipped the leg for surface
    // cells entirely; a bare planet separates the two readings):
    CHECK(au::placementBlock(c, star, 22, 0) ==
          au::PlacementBlock::SurfaceVsRing);
    // items 31..38 are EXEMPT from XOR (0x384e0 cmp dl,0x1e ja): 32 on a
    // surface cell reaches the adjacency leg, not the XOR refuse.
    CHECK(au::placementBlock(c, star, 32, 0) !=
          au::PlacementBlock::SurfaceVsRing);
    // the equal-pass shape: surface item on a surface cell is NOT refused
    // by XOR (whatever adjacency says):
    ps.items = {5};
    ps.itemCells = {0};
    CHECK(au::placementBlock(c, star, 0, 1) !=
          au::PlacementBlock::SurfaceVsRing);
    // ---- 2) NO OCCUPIED VETO (F10 consequence 1) --------------------------
    // The checker's rule B (0x38493) reads the CELL-CLASS byte, not
    // occupancy, and is granted for observed play; occupancy is read only
    // by own-active 0x385ee (a SKIP of rule G) and rules E/F. A surface
    // item on the CB's own cell therefore passes: XOR equal, rock law
    // equal, own-active skips adjacency. (The t43 "built items land on
    // EMPTY cells" law is a PICKER law — completion re-picks the cell.)
    CHECK(au::placementBlock(c, star, 0, 0) == au::PlacementBlock::None);
    // occupied ring slot, orbital item: None (XOR equal, ring skips G).
    ps.items = {28};
    ps.itemCells = {surf};  // ring slot 0
    CHECK(au::placementBlock(c, star, 24, surf) == au::PlacementBlock::None);
    // ---- 3) ROCK/LEG 0x38519 + 0x38554 ------------------------------------
    // rock veto = (byte0 bit3) != (item==38): normal item on rock refuses;
    // dig 38 on rock passes the rock leg (adjacency then decides); dig on
    // NON-rock refuses (dig arm 0x38546 sete).
    int rock = -1, nonrock = -1;
    for (int cell = 0; cell < surf; cell++) {
        if (cell >= int(ps.cellClasses.size())) break;
        if (ps.cellClasses[size_t(cell)] & 8) { if (rock < 0) rock = cell; }
        else if (nonrock < 0) nonrock = cell;
    }
    ps.items.clear();
    ps.itemCells.clear();
    if (rock >= 0) {
        CHECK(au::placementBlock(c, star, 0, rock) ==
              au::PlacementBlock::RockMismatch);
        // 38 on rock: rock leg passes; adjacency vetoes on a bare planet.
        CHECK(au::placementBlock(c, star, 38, rock) !=
              au::PlacementBlock::RockMismatch);
    }
    if (nonrock >= 0)
        CHECK(au::placementBlock(c, star, 38, nonrock) ==
              au::PlacementBlock::RockMismatch);
    // 36 Terraforming requires barren+empty+surface (0x38554): on a rock or
    // ring cell it refuses TerraformSite (the rock leg is equal-both-false
    // for 36 on non-rock, so this separates the legs).
    // 36 >= 31 skips XOR; ring skips rock + adjacency; ring is not barren
    // (T36 forces class 1) -> the 0x38554 barren+empty veto:
    CHECK(au::placementBlock(c, star, 36, surf + 1) ==
          au::PlacementBlock::TerraformSite);
    // on a NON-barren surface cell the same veto fires; on the barren cell
    // (surf-2, empty) it passes the barren leg and adjacency decides
    // (bare planet -> NoActiveNeighbour, item 36 not in the {5,35} set):
    CHECK(au::placementBlock(c, star, 36, 1) ==
          au::PlacementBlock::TerraformSite);
    CHECK(au::placementBlock(c, star, 36, surf - 2) ==
          au::PlacementBlock::NoActiveNeighbour);

    // ---- 4) ADJACENCY 0x385b7..0x386fc, CORRECT POLARITY -----------------
    // One active item on cell 0. Neighbours of cell 0 per size class,
    // VERBATIM from the grid tables (t418b measurement: size0 {1,2},
    // size1 {2}, size2 {2}, size3 {1,3}, size4 {1,4}). Each neighbour
    // ACCEPTS (active neighbour = legal); each non-neighbour inactive cell
    // REFUSES (0x386fc).
    ps.items = {5};
    ps.itemCells = {0};
    static const int kNbr0[5][2] = {{1, 2}, {2, -1}, {2, -1}, {1, 3}, {1, 4}};
    for (int k = 0; k < 2; k++)
        if (kNbr0[size][k] >= 0)
            CHECK(au::placementBlock(c, star, 0, kNbr0[size][k]) ==
                  au::PlacementBlock::None);
    int far = -1;
    for (int cell = 1; cell < surf; cell++) {
        if (cell == kNbr0[size][0] || cell == kNbr0[size][1]) continue;
        if (cell < int(ps.cellClasses.size()) &&
            (ps.cellClasses[size_t(cell)] & 8)) continue;  // rock arm owns it
        far = cell;
        break;
    }
    CHECK(far >= 0);
    if (far >= 0)
        CHECK(au::placementBlock(c, star, 0, far) ==
              au::PlacementBlock::NoActiveNeighbour);
    // skip leg 0x385b7: ring cells never ask (XOR passes an orbital item
    // there; adjacency is surface-only):
    CHECK(au::placementBlock(c, star, 22, surf) == au::PlacementBlock::None);
    CHECK(au::placementBlock(c, star, 22, surf + 9) ==
          au::PlacementBlock::None);
    // skip leg 0x385ee own-ACTIVE: the jne-exit BYPASSES rule G (it does not
    // re-grant the occupied veto — that leg fired earlier and stands; here
    // the own cell is tested THROUGH the occupied veto by a bit2 item, and
    // an exempt item 5 on its own cell answers None).
    CHECK(au::placementBlock(c, star, 5, 0) == au::PlacementBlock::None);
    // State C (mutation-M10 shape, polarity-corrected): the FOUR probes are
    // the directional TABLE row±1/col±1 — losing any leg must flip some
    // fixture. Scan every ordered (active A, target B) pair: B is None iff B
    // is a lattice neighbour of A (and not rock), else NoActiveNeighbour.
    {
        auto rc = [&](int cell, int& r, int& cc) {
            return au::gridRowCol(tt, size, surf, cell, &r, &cc);
        };
        int checked = 0, refused = 0;
        for (int A = 0; A < surf; A++) {
            if (A < int(ps.cellClasses.size()) &&
                (ps.cellClasses[size_t(A)] & 8)) continue;  // CB never on rock
            int ar = 0, ac = 0;
            rc(A, ar, ac);
            for (int Bc = 0; Bc < surf; Bc++) {
                if (Bc == A) continue;
                if (Bc < int(ps.cellClasses.size()) &&
                    (ps.cellClasses[size_t(Bc)] & 8)) continue;  // rock arm
                int br = 0, bc = 0;
                rc(Bc, br, bc);
                const bool nbr = au::gridCellFor(tt, size, ar + 1, ac) == Bc ||
                                 au::gridCellFor(tt, size, ar - 1, ac) == Bc ||
                                 au::gridCellFor(tt, size, ar, ac + 1) == Bc ||
                                 au::gridCellFor(tt, size, ar, ac - 1) == Bc;
                ps.items = {5};
                ps.itemCells = {A};
                const auto got = au::placementBlock(c, star, 0, Bc);
                const bool wantLegal = nbr;
                if ((got == au::PlacementBlock::None) != wantLegal) {
                    CHECK(false);  // names the pair below
                    std::printf("placement mismatch size%d A%d(%d,%d) B%d(%d,%d) got %d\n",
                                size, A, ar, ac, Bc, br, bc, int(got));
                    return;
                }
                if (!wantLegal) ++refused;
                ++checked;
            }
        }
        CHECK(checked > 0);
        CHECK(refused > 0);  // the refuse arm must be exercised, not vacuous
    }
}

// ---- tPL-B1b: the FLAG-bit1 cell-less census (0x3b3f5 / 0x38a5a) ----------
TEST(orders_cellless_bit1_t418b) {
    REQUIRE_DATA();
    auto copt = seededCampaign();
    CHECK(copt.has_value());
    if (!copt) return;
    ag::Campaign& c = *copt;
    // Census (tPL-B1 F2 + F9 re-run on the 39-row runtime table): bit1 rows
    // {31 Alien Hospitality, 32 Interstellar Trucking, 33 Endless Party,
    // 34 Scientist Takeover, 37 Lush Growth Bomb} order WITHOUT a cell.
    for (int id = 0; id < c.planItemCount(); id++) {
        const auto* pi = c.planetItem(id);
        if (!pi) continue;
        const bool want = (id == 31 || id == 32 || id == 33 || id == 34 ||
                           id == 37);
        CHECK(au::ordersWithoutCell(c, id) == want);
    }
}
