// SPDX-License-Identifier: GPL-3.0-or-later
// tPL-V2 ORBITAL SLOT LAW pins: the FUN_0003b96c loop-2 slot grid
// (origin (13,119), pitch 70, two columns x five rows — NOT isometric),
// the FUN_0003a880 orbital hit rect (0xe..0x98 x 0x78..0x1d4, cell =
// surface + ((x-13)/70)*5 + (y-119)/70), and the 0x3c546 hover-outline
// gate (outline ONLY on an EMPTY slot with no pick pending). Citations:
// docs/re/_wip_tPLV2.md F1/F2/F4 + the t254 witness pixel census
// (work/r1/screens/t254/02_planet_detail.png: occupied art blobs land
// exactly inside boxes (83,119) and (13,399)).
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

// ---- the slot grid law ------------------------------------------------------
TEST(orbital_slot_grid_tPLV2) {
    // 0x3c33a/0x3c33f seed (13,119) + 0x46 pitch + idiv-5 column step.
    const int ex[10] = {13, 13, 13, 13, 13, 83, 83, 83, 83, 83};
    const int ey[10] = {119, 189, 259, 329, 399, 119, 189, 259, 329, 399};
    for (int k = 0; k < 10; k++) {
        const au::Pt o = au::orbitalSlotOrigin(k);
        CHECK(o.x == ex[k]);
        CHECK(o.y == ey[k]);
    }
    CHECK(au::orbitalSlotOrigin(-1).x == -1);
    CHECK(au::orbitalSlotOrigin(10).x == -1);
    CHECK(au::kOrbitalSlots == 10);   // +0x1a == +0x18 + 10 (OQ-014 census)
    CHECK(au::kOrbitalPitch == 70);   // 0x46
}

// ---- the FUN_0003a880 hit law -----------------------------------------------
TEST(orbital_slot_hit_tPLV2) {
    const int surf = 23;
    const auto H = [surf](int x, int y) { return au::orbitalSlotHitFor(surf, au::Pt{x, y}); };
    // VENDOR QUIRK [verified verbatim FUN_0003a880]: the hit rect is
    // x in [0xe,0x98] y in [0x78,0x1d4] = [14,152]x[120,468] — ONE PX
    // inside the paint origin (13,119). (13,119) itself falls to the
    // lattice leg; (14,120) is slot 0.
    CHECK(H(13, 119) == -1);
    CHECK(H(14, 120) == surf + 0);
    // Bottom-right corner ON the inclusive bounds (0x98=152, 0x1d4=468).
    CHECK(H(152, 468) == surf + 9);
    // Verbatim bounds exclude: x > 0x98, x < 0xe, y < 0x78, y > 0x1d4.
    CHECK(H(153, 300) == -1);
    CHECK(H(12, 300) == -1);
    CHECK(H(50, 119) == -1);
    CHECK(H(50, 469) == -1);
    // Column law: x = 83 jumps +5 cells (the idiv-5 column step).
    CHECK(H(83, 120) == surf + 5);
    CHECK(H(82, 120) == surf + 0);  // x=82: (82-13)/70 == 0 -> column 0
    CHECK(H(146, 130) == surf + 5);
}

// ---- occupancy + hover-outline gate -----------------------------------------
TEST(orbital_hover_outline_tPLV2) {
    auto campOpt = seededCampaign();
    CHECK(campOpt.has_value());
    if (!campOpt) return;
    ag::Campaign& c = *campOpt;
    int star = -1;
    for (const auto& s : c.galaxy().stars)
        if (c.starOwner(s.id) == ag::kPlayer) { star = s.id; break; }
    CHECK(star >= 0);
    if (star < 0) return;
    auto& ps = const_cast<ag::PlanetState&>(c.planetAt(star));  // t204 idiom
    const int surf = ps.surfaceCells;
    ps.items.clear();
    ps.itemCells.clear();
    const au::Pt slot0{20, 130}, slot1{20, 200}, offField{300, 300};
    // EMPTY slot 0 hovered: outline shows ONLY while drawing slot k=0
    // (the vendor's per-slot == +0xac compare), not for any other k.
    CHECK(au::orbitalHoverOutline(c, star, 0, slot0, false));
    CHECK(!au::orbitalHoverOutline(c, star, 1, slot0, false));
    CHECK(!au::orbitalHoverOutline(c, star, 6, slot0, false));
    // Pick pending: NO outline (0x3c574 +0xab == 0xff leg).
    CHECK(!au::orbitalHoverOutline(c, star, 0, slot0, true));
    // OCCUPIED slot 0 (Shipyard item 22 on ring cell surf+0): no outline,
    // and orbitalSlotItem reports it.
    ps.items.push_back(22);
    ps.itemCells.push_back(surf + 0);
    CHECK(au::orbitalSlotItem(c, star, 0) == 22);
    CHECK(!au::orbitalHoverOutline(c, star, 0, slot0, false));
    // A different (empty) slot hovered still outlines for ITS k.
    CHECK(au::orbitalHoverOutline(c, star, 1, slot1, false));
    // Outside the rect: nothing.
    CHECK(!au::orbitalHoverOutline(c, star, 0, offField, false));
    // Out-of-domain star: nothing, no crash.
    CHECK(!au::orbitalHoverOutline(c, -1, 0, slot0, false));
    CHECK(au::orbitalSlotItem(c, -1, 0) == -1);
}

}  // namespace
