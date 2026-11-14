// SPDX-License-Identifier: GPL-3.0-or-later

#include "game/economy.h"
#include "game/research.h"
#include "harness.h"

#include <algorithm>
#include <filesystem>
#include <fstream>

#ifndef ASCENDANCY_SOURCE_DIR
#define ASCENDANCY_SOURCE_DIR "."
#endif

namespace {
namespace ag = ascend::game;

std::filesystem::path d0(const std::string& f) {
    return std::filesystem::path(ASCENDANCY_SOURCE_DIR) / "extracted" / "ascend00" / f;
}
}  // namespace

TEST(gizmos_loads_76_with_measured_category_counts) {
    REQUIRE_DATA();
    std::string err;
    auto gz = ag::loadGizmos(d0("gizmos.txt").string(), err);
    CHECK(err.empty());
    CHECK(gz.size() == 76);
    int nW = 0, nS = 0, nD = 0, nSc = 0, nG = 0, nSp = 0;
    for (const auto& g : gz) {
        switch (g.cat) {
            case ag::GizmoCat::Weapon: ++nW; break;
            case ag::GizmoCat::Shield: ++nS; break;
            case ag::GizmoCat::Drive: ++nD; break;
            case ag::GizmoCat::Scanner: ++nSc; break;
            case ag::GizmoCat::Generator: ++nG; break;
            case ag::GizmoCat::Special: ++nSp; break;
        }
    }
    // docs/re/gizmos.md §2
    CHECK(nW == 10); CHECK(nS == 6); CHECK(nD == 5);
    CHECK(nSc == 6); CHECK(nG == 5); CHECK(nSp == 44);
}

TEST(gizmo_flag_packing_uses_bit_positions) {
    REQUIRE_DATA();
    std::string err;
    auto gz = ag::loadGizmos(d0("gizmos.txt").string(), err);
    CHECK(!gz.empty());
    // Mass Barrage Gun: flag_list "0 1 2" -> bits 0|2|4 = 7 (gizmos.md §1)
    const ag::Gizmo* mbg = nullptr;
    for (const auto& g : gz)
        if (g.name == "Mass Barrage Gun") mbg = &g;
    CHECK(mbg != nullptr);
    if (mbg) {
        CHECK(mbg->flags == (1 | 2 | 4));
        CHECK(mbg->power == 1);
        CHECK(mbg->range == 25);
        CHECK(mbg->level == 1);     // weapon damage
        CHECK(mbg->industry == 15);
        CHECK(mbg->resReq == 4);    // Superconductivity
    }
    // Ion Wrap: flag_list "5" -> bit 5 = 32 (TOGGLEABLE)
    for (const auto& g : gz)
        if (g.name == "Ion Wrap") CHECK(g.flags == 32);
}

TEST(gizmo_resreq_cross_validates_restree_rows) {
    REQUIRE_DATA();
    std::string err;
    auto gz = ag::loadGizmos(d0("gizmos.txt").string(), err);
    auto tree = ag::ResearchTree::loadFromFile(d0("restree.txt").string(), err);
    CHECK(err.empty());
    const int nt = static_cast<int>(tree.all().size());
    for (const auto& g : gz)
        CHECK(g.resReq == 255 || (g.resReq >= 0 && g.resReq < nt));
    // The named spot-checks from docs/re/gizmos.md §2
    auto techAt = [&](int i) { return tree.all()[i].name; };
    bool ferg = false, pla = false;
    for (const auto& g : gz) {
        if (g.name == "Fergnatz Lens") {
            ferg = g.resReq == 44 && techAt(44) == "Fergnatz's Last Theorem";
        }
        if (g.name == "Plasmatron") {
            pla = g.resReq == 29 && techAt(29) == "Plasmatics";
        }
    }
    CHECK(ferg);
    CHECK(pla);
}

TEST(planitems_loads_39_with_requotes) {
    REQUIRE_DATA();
    std::string err;
    auto items = ag::loadPlanItems(d0("planitem.txt").string(), err);
    CHECK(err.empty());
    CHECK(items.size() == 39);
    const ag::PlanetItem* ship = nullptr;
    const ag::PlanetItem* truck = nullptr;
    int sentinels = 0;
    for (const auto& it : items) {
        if (it.reqByte == 254 || it.reqByte == 255) ++sentinels;
        if (it.name == "Ship") ship = &it;
        if (it.name == "Interstellar Trucking") truck = &it;
    }
    CHECK(sentinels == 6);  // 5x255 + 1x254 (economy.md §1)
    CHECK(ship != nullptr);
    if (ship) {
        // raw row: Ship 0 0 0 0 1 20 1 255  (cost=20, requires=1)
        CHECK(ship->cost == 20);
        CHECK(ship->reqByte == 1);  // Interplanetary Exploration
    }
    CHECK(truck != nullptr);
    if (truck) {
        CHECK(truck->reqByte == 254);  // the undocumented sentinel
        CHECK(!ag::requiresValidTech(truck->reqByte, 106));
    }
}

// OQ-014 CLOSED — MEASURED laws lifted from the original (docs/re/economy.md
// §4; loader FUN_00037fc0, availability checker FUN_0003830c, init
// FUN_00037d80; cross-checked against 17 banked captures).
TEST(oq014_requires_law_254_is_dead_not_ungated) {
    REQUIRE_DATA();
    std::vector<bool> all(66, true), none(66, false);
    CHECK(ag::requiresAvailable(255, 66, none));      // sentinel: ungated
    CHECK(ag::requiresAvailable(26, 66, all));        // owned tech: available
    CHECK(!ag::requiresAvailable(26, 66, none));      // not owned: gated
    // THE law change: 254 passes neither branch in the original, so
    // Interstellar Trucking is permanently unavailable even with ALL techs.
    CHECK(!ag::requiresAvailable(254, 66, all));
    CHECK(!ag::requiresAvailable(254, 106, all));     // even a bigger tree
}

TEST(oq014_count_triple_and_placement_classes) {
    REQUIRE_DATA();
    std::string err;
    auto items = ag::loadPlanItems(d0("planitem.txt").string(), err);
    CHECK(err.empty());
    CHECK(items.size() == 39);                 // "39" == record count (0x38115)
    CHECK(ag::kPlanitemSurfaceCount == 22);    // RAM 0x73e3c == 22 (4/4 runs)
    CHECK(ag::kPlanitemOrbitalCount == 9);     // RAM 0x73e3e == 9  (4/4 runs)
    // Boundary rows by NAME (economy.md §4): rows 0..21 surface, 22..30
    // orbital, 31..38 specials.
    CHECK(items[0].name == "Factory");
    CHECK(items[21].name == "Transport Tubes");
    CHECK(items[22].name == "Shipyard");
    CHECK(items[30].name == "Long Range Orbital Whopper");
    CHECK(items[31].name == "Alien Hospitality");
    CHECK(items[38].name == "Xeno Archeological Dig");
    for (int i = 0; i < 22; ++i) CHECK(ag::itemIsSurface(i));
    for (int i = 22; i < 39; ++i) CHECK(!ag::itemIsSurface(i));
}

TEST(oq014_slot_law_surface_xor_and_size_cells) {
    REQUIRE_DATA();
    // FUN_00037d80: orbital pool is exactly 10 slots above the surface cells;
    // live planet records 2650/2650 carry cap == cells + 10.
    // Grid-C row sums = size-class surface cells (RAM +0x18, 5 classes).
    CHECK(ag::planetSurfaceCells(0) == 7);
    CHECK(ag::planetSurfaceCells(1) == 11);
    CHECK(ag::planetSurfaceCells(2) == 23);
    CHECK(ag::planetSurfaceCells(3) == 45);
    CHECK(ag::planetSurfaceCells(4) == 73);
    CHECK(ag::planetSurfaceCells(5) == 0);
    const int cells = ag::planetSurfaceCells(0);  // 7
    // Surface item: allowed strictly below cells, forbidden at/above.
    CHECK(ag::itemSlotAllows(0 /*Factory*/, 6, cells));
    CHECK(!ag::itemSlotAllows(0, 7, cells));
    // Orbital item: allowed at/above cells, forbidden below.
    CHECK(ag::itemSlotAllows(22 /*Shipyard*/, 7, cells));
    CHECK(ag::itemSlotAllows(22, cells + 9, cells));
    CHECK(!ag::itemSlotAllows(22, 0, cells));
    // Specials are exempt from the XOR rule (checker bound DL <= 0x1e).
    CHECK(ag::itemSlotAllows(31, 0, cells));
    CHECK(ag::itemSlotAllows(38, cells + 9, cells));
}

TEST(best_drive_range_respects_research_gate) {
    REQUIRE_DATA();
    std::string err;
    auto gz = ag::loadGizmos(d0("gizmos.txt").string(), err);
    CHECK(!gz.empty());
    std::vector<bool> owned(106, false);
    const int none = ag::bestDriveRange(gz, owned);
    owned.assign(106, true);
    const int full = ag::bestDriveRange(gz, owned);
    CHECK(full > none);          // gating must actually change the answer
    CHECK(full == 10);           // Hypersphere Driver level 10 (gizmos.md §4)
}

TEST(economy_loaders_reject_corrupt_input) {
    REQUIRE_DATA();
    auto tmp = std::filesystem::temp_directory_path() / "ascendancy_econ_bad.txt";
    struct Bad {
        const char* text;
    } bad[] = {
        {"no marker\nJust text\n"},
        {"#\n1 2 3 255\n"},                                // numeric with no name
        {"#\nName\n1 2 3\n"},                              // dangling name w/o row
        {"#\nName\n1 2 255\n"},                            // short gizmo row
    };
    for (const auto& b : bad) {
        {
            std::ofstream o(tmp, std::ios::binary);
            o << b.text;
        }
        std::string err;
        auto gz = ag::loadGizmos(tmp.string(), err);
        CHECK(gz.empty());
    }
    // planitem: valid gizmo file must fail its 39-record/count-triple checks
    std::string err;
    auto items = ag::loadPlanItems(d0("gizmos.txt").string(), err);
    CHECK(items.empty());
    std::filesystem::remove(tmp);
}
