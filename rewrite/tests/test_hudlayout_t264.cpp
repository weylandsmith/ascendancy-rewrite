// SPDX-License-Identifier: GPL-3.0-or-later

// t264 HUD layout wiring pins: rail rects/messages vs windows.txt, the
// 1starmap.shp icon law, and the SHIPDESSCREEN tab->gizmo-category table
// (t253 measured 6/6). Citations: docs/re/ui-runtime.md §6a/§6c and
// docs/re/_wip_t264.md. The live-file leg loads the shipped gizmos.txt and
// joins the table against the file's own category column.
#include "ui/hudlayout.h"

#include <string>
#include <vector>

#include "game/economy.h"
#include "harness.h"

#ifndef ASCENDANCY_SOURCE_DIR
#define ASCENDANCY_SOURCE_DIR "."
#endif

namespace {
namespace au = ascend::ui;
namespace ag = ascend::game;
const std::string kRepo = ASCENDANCY_SOURCE_DIR;
}  // namespace

TEST(hud_rail_constants_match_windows_txt_t264) {
    using RB = au::RailButton;
    // Rect + (SENDMESSAGE, SENDPARAM1) verbatim per _wip_t264.md S1.
    struct Want { int x0, y0, x1, y1, msg, p1; };
    const Want w[6] = {
        {474, 130, 632, 160, 1, 10},  // STATUS
        {474, 169, 632, 199, 1, 18},  // FLEET
        {474, 208, 632, 238, 1, 20},  // RESEARCH
        {474, 247, 632, 277, 5, 0},   // SPECIALAB
        {474, 286, 632, 316, 1, 7},   // RACES
        {474, 303, 632, 333, 1, 14},  // Intelligence
    };
    for (int i = 0; i < 6; ++i) {
        au::RailControl r = au::railControl(static_cast<RB>(i));
        CHECK(r.rect.x0 == w[i].x0);
        CHECK(r.rect.y0 == w[i].y0);
        CHECK(r.rect.x1 == w[i].x1);
        CHECK(r.rect.y1 == w[i].y1);
        CHECK(r.sendMessage == w[i].msg);
        CHECK(r.sendParam1 == w[i].p1);
    }
    // SENDPARAM1 == target STATE number law (checked instances, file lines):
    CHECK(au::railControl(RB::Status).sendParam1 == 10);    // STATUSWND '1 10'
    CHECK(au::railControl(RB::Fleet).sendParam1 == 18);     // FLEETWND '1 18'
    CHECK(au::railControl(RB::Research).sendParam1 == 20);  // RESWIN '1 20'
    CHECK(au::railControl(RB::Intelligence).sendParam1 == 14);  // '1 14'
}

TEST(hud_rail_hit_map_t264) {
    using RB = au::RailButton;
    // Click centers t252 actually used (rect centers) hit their button.
    CHECK(au::railButtonFor({553, 145}).value_or(RB::Intelligence) == RB::Status);
    CHECK(au::railButtonFor({553, 184}).value_or(RB::Intelligence) == RB::Fleet);
    CHECK(au::railButtonFor({553, 223}).value_or(RB::Intelligence) == RB::Research);
    CHECK(au::railButtonFor({553, 262}).value_or(RB::Intelligence) == RB::SpecialAbility);
    CHECK(au::railButtonFor({553, 301}).value_or(RB::Intelligence) == RB::Races);
    CHECK(au::railButtonFor({553, 311}).value_or(RB::Races) == RB::Intelligence);
    // Inclusive edges.
    CHECK(au::railButtonFor({474, 130}).value_or(RB::Intelligence) == RB::Status);
    CHECK(au::railButtonFor({632, 160}).value_or(RB::Intelligence) == RB::Status);
    // Off-rail: left of the band, above it, below it, in the inter-button
    // gutters, and beside NEXTTURN (not a rail item).
    CHECK(!au::railButtonFor({473, 145}));
    CHECK(!au::railButtonFor({633, 145}));
    CHECK(!au::railButtonFor({553, 129}));
    CHECK(!au::railButtonFor({553, 334}));
    CHECK(!au::railButtonFor({553, 165}));   // STATUS/FLEET gutter
    CHECK(!au::railButtonFor({600, 60}));    // right of NEXTTURN
    // The documented overlap (RACES y..316 vs Intelligence 303..) resolves
    // to Intelligence (item on top; [inferred] z-order, pinned as law).
    CHECK(au::railButtonFor({553, 310}).value_or(RB::Races) == RB::Intelligence);
}

TEST(hud_sidebar_icon_law_t264) {
    using RB = au::RailButton;
    // SHAPEITEM lines verbatim (windows.txt 439/460/481/500 blocks).
    auto ic = au::sidebarIcon(RB::Research);
    CHECK(ic.has_value());
    CHECK(std::string(ic->shapeFile) == "data\\1starmap.shp");
    CHECK(ic->frame == 3);
    CHECK(au::sidebarIcon(RB::Fleet)->frame == 4);
    CHECK(au::sidebarIcon(RB::Status)->frame == 5);
    CHECK(au::sidebarIcon(RB::SpecialAbility)->frame == 7);
    // Buttons WITHOUT a shape item must yield nullopt, not a frame.
    CHECK(!au::sidebarIcon(RB::Races).has_value());       // WINITEMS 1
    CHECK(!au::sidebarIcon(RB::Intelligence).has_value());  // WINITEMS 0
    // Frame set is exactly {3,4,5,7} — 6 is NOT a rail icon (frame 6 has no
    // rail SHAPEITEM; do not invent one).
    int seen[8] = {0};
    for (int i = 0; i < au::kRailButtonCount; ++i) {
        auto s = au::sidebarIcon(static_cast<RB>(i));
        if (s) seen[s->frame] = 1;
    }
    CHECK(seen[3] && seen[4] && seen[5] && seen[7]);
    CHECK(!seen[0] && !seen[1] && !seen[2] && !seen[6]);
}

TEST(hud_ship_tab_category_map_t264) {
    // THE MEASURED TABLE (t253, 6/6 live vs gizmos.txt category field).
    CHECK(au::gizmoCatForShipTab(51) == 0);  // WEAPONS
    CHECK(au::gizmoCatForShipTab(52) == 1);  // DEFENSES
    CHECK(au::gizmoCatForShipTab(54) == 2);  // ENGINES
    CHECK(au::gizmoCatForShipTab(53) == 3);  // SENSORS
    CHECK(au::gizmoCatForShipTab(55) == 4);  // ENERGY
    CHECK(au::gizmoCatForShipTab(57) == 5);  // SPECIAL
    // Negatives: HULL is not a category; msg 56 belongs to no tab.
    CHECK(au::gizmoCatForShipTab(50) == -1);
    CHECK(au::gizmoCatForShipTab(56) == -1);
    CHECK(au::gizmoCatForShipTab(0) == -1);
    CHECK(au::gizmoCatForShipTab(58) == -1);
    // Non-derivability witness: the naive rule cat == msg-51 holds ONLY for
    // WEAPONS(51)/DEFENSES(52)/ENERGY(55). It breaks on the swapped middle
    // pair (53->cat3, 54->cat2) AND on SPECIAL (57->cat5, msg-51 says 6,
    // because msg 56 has no tab). Deviation set EXACTLY {53,54,57} — pinned,
    // so a "simplifying" rewrite to cat = msg-51 fails here.
    for (int m = 51; m <= 57; ++m) {
        if (m == 56) continue;
        const bool naive = (au::gizmoCatForShipTab(m) == m - 51);
        CHECK(naive == (m == 51 || m == 52 || m == 55));
    }
    // (HULL 50 agrees with the naive rule only coincidentally: -1 == 50-51.)
    CHECK(au::gizmoCatForShipTab(50) == 50 - 51);
    // Inverse is total on 0..5 and round-trips.
    for (int c = 0; c <= 5; ++c) {
        const int m = au::shipTabForGizmoCat(c);
        CHECK(m >= 0);
        CHECK(au::gizmoCatForShipTab(m) == c);
    }
    CHECK(au::shipTabForGizmoCat(-1) == -1);
    CHECK(au::shipTabForGizmoCat(6) == -1);
    // File-order tile list (row1 WEAPONS HULL DEFENSES, row2 ENGINES
    // SENSORS ENERGY SPECIAL) — the kShipTabMessages constant.
    const int want[7] = {51, 50, 52, 54, 53, 55, 57};
    for (int i = 0; i < 7; ++i) CHECK(au::kShipTabMessages[i] == want[i]);
}

TEST(hud_gizlist_join_live_file_t264) {
    // Join the table against the shipped gizmos.txt: per-tab list sizes are
    // the file's category census {0:10 1:6 2:5 3:6 4:5 5:44} (t253 + the
    // loadGizmos 76-record invariant), and the head of each list is the
    // first row the t253 GIZLIST rendered for that tab.
    std::string err;
    const auto gz = ag::loadGizmos(kRepo + "/extracted/ascend00/gizmos.txt", err);
    CHECK(gz.size() == 76);
    if (gz.size() != 76) return;  // err string already checked below
    CHECK(err.empty());
    const int sizes[6] = {10, 6, 5, 6, 5, 44};
    const char* heads[6] = {"Mass Barrage Gun", "Ion Wrap", "Tonklin Motor",
                            "Tonklin Frequency Analyzer", "Proton Shaver",
                            "Lane Blocker"};
    for (int c = 0; c <= 5; ++c) {
        const auto idx = au::gizmoListForTab(gz, au::shipTabForGizmoCat(c));
        CHECK(idx.size() == size_t(sizes[c]));
        if (idx.empty()) continue;
        CHECK(gz[idx[0]].name == heads[c]);
        // Every member really is in category c (join correctness).
        for (int i : idx) CHECK(int(gz[i].cat) == c);
    }
    // HULL / msg 56 yield empty lists.
    CHECK(au::gizmoListForTab(gz, 50).empty());
    CHECK(au::gizmoListForTab(gz, 56).empty());
    // GIZLIST ORDER LAW: per-tab order == file order == gizmosByCategory.
    CHECK(au::gizmoListForTab(gz, 51) ==
          ag::gizmosByCategory(gz, ag::GizmoCat::Weapon));
    CHECK(au::gizmoListForTab(gz, 53) ==
          ag::gizmosByCategory(gz, ag::GizmoCat::Scanner));
}
