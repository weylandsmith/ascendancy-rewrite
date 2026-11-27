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
#include "ui/planetwin.h"  // tPF-6a: popupButtonIds + kPbBuild

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
    // tPF-6b: pop must be ABUNDANT here — the fill law 0x3b6f3 runs the
    // checker's FREE-POP leg (0x383b3) per row, so a zero-pop fixture would
    // (correctly!) empty the list and make every filter assertion vacuous.
    ps.pop = 50;
    ps.cellClasses.assign(size_t(surf) + 10, 1);
    // tPF-8: nothing is REQUIRES-legal at game start (vendor zero-mask law),
    // which would make the filter test vacuous. The fixture's PREMISE is the
    // full REQUIRES-passing table — force it directly (tPL-D1 fixture
    // precedent); the filter law under test is tech-state-independent.
    c.setAllTechs(ag::kPlayer, true);

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

// tPF-6b FILL-LAW PINS (docs/re/_wip_tPF6b.md P4-P7): the vendor PLANLIST
// fill 0x3b6f3 skips item 5 UNCONDITIONALLY (0x3b76a) and runs the checker's
// FREE-POP leg (0x383b3) per row on EVERY open (PLBUILD param 1 forces the
// cell to -1, windows.txt ln1615 + 0x3b70d; cell -1 bypasses only the CELL
// legs at 0x3843a, not legs A/B).
TEST(planlist_fill_law_tpf6b) {
    REQUIRE_DATA();
    auto copt = seededCampaign();
    CHECK(copt.has_value());
    if (!copt) return;
    ag::Campaign& c = *copt;
    const int star = playerStar(c);
    CHECK(star >= 0);
    if (star < 0) return;
    auto& ps = const_cast<ag::PlanetState&>(c.planetAt(star));
    ps.items.clear();
    ps.itemCells.clear();
    ps.cellClasses.assign(size_t(ps.surfaceCells) + 10, 1);
    c.setAllTechs(ag::kPlayer, true);

    // (1) item 5 is never a row, armed or unarmed, even with all techs and
    // abundant pop (the ONLY law being pinned here).
    ps.pop = 50;
    CHECK(!holds(au::projectOptionsFor(c, star), 5));
    CHECK(!holds(au::projectOptionsFor(c, star, 0), 5));

    // (2) FREE-POP AT LIST TIME: with pop pinned so free == 0, NO row with
    // UPOP > 0 survives — item 23 included (tPF-6a F6: the 0x38420 jne
    // skips the 0x39a9c replacement on pop-FAIL; the tPF-6b "23 exempt"
    // reading was the direction reversed).
    ps.pop = 0;
    const auto tight = au::projectOptionsFor(c, star);
    for (const auto& o : tight) {
        const auto* pi = c.planetItem(o.item);
        CHECK(pi && pi->upop <= 0);
    }
    // (3) ANTI-VACUITY: restoring pop brings the UPOP>0 rows back (a filter
    // that always returns the same set would fail this leg).
    ps.pop = 50;
    const auto loose = au::projectOptionsFor(c, star);
    CHECK(loose.size() > tight.size());
    bool anyPositiveUpop = false;
    for (const auto& o : loose) {
        const auto* pi = c.planetItem(o.item);
        if (pi && pi->upop > 0) anyPositiveUpop = true;
    }
    CHECK(anyPositiveUpop);
}

// Wiring pin (source-text): the ui.cpp popupButtonIds buildable-leg must
// carry the FULL checker (free-pop + REQUIRES + placementBlock) — a lambda
// reverted to placementBlock-only silently re-offers pop-short Builds (the
// 0x3d579 loop runs the same 0x3830c as the fill).
TEST(planlist_popup_leg_wiring_tpf6b) {
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
    const size_t call = src.find("popupButtonIds(");
    CHECK(call != std::string::npos);
    if (call == std::string::npos) return;
    // tPF6-SHIP: window widened 1600 -> 2200 (the 0x39a9c leg comment + call
    // inside the lambda pushed placementBlock past 1600; the pin guards the
    // LAMBDA BODY, so the window must span it).
    const std::string body = src.substr(call, 2200);
    CHECK(body.find("usedPopFor") != std::string::npos);
    CHECK(body.find("requiresAvailable") != std::string::npos);
    CHECK(body.find("placementBlock") != std::string::npos);
    // TPF6-SHIP CLOSED: the lambda must run the 0x39a9c ship leg for item 23
    // (one checker 0x3830c for fill AND popup; a lambda without it re-offers
    // Ship Build buttons on yard-less / fleet-saturated planets).
    CHECK(body.find("vendorShipLegAllowed") != std::string::npos);
    // tPF-6a F6 REVOCATION LAW: the 0x38420 jne skips the 0x39a9c
    // replacement on pop-FAIL, so item 23 takes the free-pop leg like every
    // other in-domain item. A restored `item != 23` exemption in the lambda
    // re-offers pop-short ship Builds the vendor never shows — CAUGHT here.
    CHECK(body.find("item != 23") == std::string::npos);
}

// tPF-6a NEVER-EMPTY INVARIANT (docs/re/_wip_tPF6a.md F4/F8): the vendor
// popup Build button (0x3d550 empty-cell loop, first checker-pass at 0x3d579)
// can never sit above an empty PLANLIST: legs A+B of checker 0x3830c are
// cell-independent (F1/F6) and leg C is inert at cell -1 (0x3843a jae), so
// pass(item, cell) => pass(item, -1) and the fill (forced cell -1,
// windows.txt ln1615 + 0x3b70d) appends the witness item. Port mirror: the
// popupButtonIds buildable-lambda is (freePop AND requires AND placement),
// projectOptionsFor(-1) is (freePop AND requires) — a Build button must
// always imply a non-empty list CONTAINING its witness item, at every cell.
TEST(build_button_implies_nonempty_fill_tpf6a) {
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
    const int size = ag::Campaign::sizeClassFor(surf);
    CHECK(size >= 0);
    if (size < 0) return;
    ps.items.clear();
    ps.itemCells.clear();
    ps.cellClasses.assign(size_t(surf) + 10, 1);
    ps.pop = 50;
    c.setAllTechs(ag::kPlayer, true);

    // The per-cell buildable predicate EXACTLY as ui.cpp wires it (the
    // source-text pin planlist_popup_leg_wiring_tpf6b guards drift; this
    // pin guards the IMPLICATION regardless of how the legs are tuned).
    const auto passes = [&](int item, int cell) {
        if (item != 0xff) {
            const auto* pi = c.planetItem(item);
            const int fp = int(c.planetAt(star).pop) - c.usedPopFor(star);
            if (!pi || fp < pi->upop) return false;
            if (!ascend::game::requiresAvailable(pi->reqByte,
                                                 c.techCountTotal(),
                                                 c.playerTechs()))
                return false;
            if (item == 23 && !au::vendorShipLegAllowed(c, star))
                return false;  // tPF6-SHIP: mirrors the ui.cpp lambda
        }
        return au::placementBlock(c, star, item, cell) ==
               au::PlacementBlock::None;
    };
    int buildCells = 0;
    for (int cell = 0; cell < surf + 10; ++cell) {
        const auto ids = au::popupButtonIds(
            0xff, [&](int item) { return passes(item, cell); });
        bool hasBuild = false;
        for (int id : ids)
            if (id == au::kPbBuild) hasBuild = true;
        if (!hasBuild) continue;
        buildCells++;
        // THE INVARIANT: armed AND plain (-1) lists are both non-empty and
        // both contain the witness item (first popup-loop pass).
        const auto armed = au::projectOptionsFor(c, star, cell);
        const auto plain = au::projectOptionsFor(c, star);
        CHECK(!armed.empty());
        CHECK(!plain.empty());
        int witness = -1;
        for (int item = 0; item <= 0x26; ++item) {
            if (item == 5) continue;  // 0x3d55f skip
            if (passes(item, cell)) {
                witness = item;
                break;
            }
        }
        CHECK(witness >= 0);
        CHECK(holds(armed, witness));
        CHECK(holds(plain, witness));
    }
    // ANTI-VACUITY: the fixture must actually produce Build buttons (an
    // all-refused planet would make the loop above vacuous).
    CHECK(buildCells > 0);

    // POPUP SKIP-5 (0x3d55f) IS LOAD-BEARING and observed directly here:
    // the checker passes item 5 at EVERY cell (pop-short/req-short both land
    // on 0x38435 mov ebp,-1 — F7), so a popup loop WITHOUT the skip would
    // show Build above a list that can never contain item 5 (the fill skips
    // it unconditionally, 0x3b76a). Lambda passes ONLY item 5 => no Build.
    {
        const auto only5 = au::popupButtonIds(
            0xff, [](int item) { return item == 5; });
        bool build = false;
        for (int id : only5)
            if (id == au::kPbBuild) build = true;
        CHECK(!build);
        // Anti-vacuity for THIS leg: same loop, item 4 => Build appears.
        const auto only4 = au::popupButtonIds(
            0xff, [](int item) { return item == 4; });
        bool build4 = false;
        for (int id : only4)
            if (id == au::kPbBuild) build4 = true;
        CHECK(build4);
    }
}

// TPF6-SHIP PIN (docs/re/_wip_tPF6ship.md P1-P9): the 0x39a9c leg runs for
// item 23 ONLY, after a pop PASS (0x38420 jne), at LIST TIME (fill 0x3b6f3
// and popup 0x3d579 share checker 0x3830c; the ORDER path 0x38840 has no
// ship call — projectOrderable unchanged). Legs: ACTIVE Shipyards (22) cell
// AND 0x402d8(race) = 1 + SOLE_STARS - SHIPS + HOME_BIT > 0.
TEST(ship_leg_tpf6ship) {
    REQUIRE_DATA();
    auto copt = seededCampaign();
    CHECK(copt.has_value());
    if (!copt) return;
    ag::Campaign& c = *copt;
    const int star = playerStar(c);
    CHECK(star >= 0);
    if (star < 0) return;
    auto& ps = const_cast<ag::PlanetState&>(c.planetAt(star));
    ps.items.clear();
    ps.itemCells.clear();
    ps.cellClasses.assign(size_t(ps.surfaceCells) + 10, 1);
    ps.pop = 50;
    c.setAllTechs(ag::kPlayer, true);

    // (1) NO Shipyards cell => item 23 is revoked at every list open even
    // with pop abundant (0x39ae0 -> verdict 0). Other rows unaffected.
    CHECK(!holds(au::projectOptionsFor(c, star), 23));
    CHECK(!holds(au::projectOptionsFor(c, star, 0), 23));
    CHECK(!au::vendorShipLegAllowed(c, star));
    // ANTI-VACUITY: the list is non-empty WITHOUT 23 (the gate removes one
    // row, not the list).
    CHECK(au::projectOptionsFor(c, star).size() > 1);

    // (2) ACTIVE Shipyards + small fleet => 23 returns. Fleet 0 < 1 +
    // soleStars + homeBit holds on any owned empire (soleStars >= 1: the
    // player owns its home; homeBit 1).
    ps.items.push_back(22);
    ps.itemCells.push_back(0);
    CHECK(au::vendorShipLegAllowed(c, star));
    CHECK(holds(au::projectOptionsFor(c, star), 23));

    // (3) FLEET SATURATION: N player ships with N >= 1 + soleStars + homeBit
    // revokes 23 again (0x40ec0 census analog = fleet() owner count).
    int sole = 0;
    for (const auto& s : c.galaxy().stars)
        if (c.starOwner(s.id) == ag::kPlayer) sole++;
    const int home = c.homeStarFor(ag::kPlayer);
    const int homeBit = (home >= 0 && c.starOwner(home) == ag::kPlayer) ? 1 : 0;
    std::vector<ag::ShipInTransit> fleet;
    for (int i = 0; i < 1 + sole + homeBit; ++i)
        fleet.push_back({ag::kPlayer, star, star});
    c.setFleetForTest(fleet);
    CHECK(!au::vendorShipLegAllowed(c, star));
    CHECK(!holds(au::projectOptionsFor(c, star), 23));
    // HOME SLACK: fleet EXACTLY 1 + sole (one below saturation) still
    // passes — isolates the HOME_BIT term of 1 + SOLE - SHIPS + HOME (a
    // formula without +HOME revokes here: value 0).
    fleet.pop_back();
    c.setFleetForTest(fleet);
    CHECK(au::vendorShipLegAllowed(c, star));
    CHECK(holds(au::projectOptionsFor(c, star), 23));
    // One ship fewer passes again (boundary is exact, not slack).
    fleet.pop_back();
    c.setFleetForTest(fleet);
    CHECK(au::vendorShipLegAllowed(c, star));
    CHECK(holds(au::projectOptionsFor(c, star), 23));
    // The leg is CELL-INDEPENDENT (0x39a9c reads no cell operand — tPF-6a
    // F1): same verdict armed or plain.
    c.setFleetForTest({});
    CHECK(au::vendorShipLegAllowed(c, star));
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
