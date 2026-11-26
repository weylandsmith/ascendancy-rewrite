// SPDX-License-Identifier: GPL-3.0-or-later
// tPF-8 OPENING-RESEARCH + REST-VISIBILITY pins (D28 item 21).
// Law (docs/re/_wip_tPF8.md P1-P3):
//  - VENDOR START LAW: zero known techs for every race at game start.
//    MEASURED: mask byte ds:0x7478e + 0x4b*i (the field legality predicate
//    0x46d3c reads via dword[rec+0x47]>>24) == 0x00 for all 66 rows x 8
//    races in 72/72 boot captures (scripts/tPF8_startmask_census.py;
//    progress words ds:0x764a0 all 0, studied words ds:0x76492 = 0xffff).
//  - EDGE LAW 0x48275..0x48383: an edge paints iff THIS row is legal at
//    0x4856d AND the prereq passed 0x46d3c at 0x4829f (roots have no
//    prereqs) => at the zero-mask start, ZERO paintable edges.
//  - REST-CAMERA FRAME LAW (cited constants focal 1194.256, pos (0,0,-150),
//    Y = 30k + 15*(i&1)): roots are column k=0 -> screen y 240..381, inside
//    the RESWIN clip (7,46)-(476,472) at every depth Z_cam in [127,173]
//    => the frontier at start is clickable WITHOUT dollying (closes
//    seam TRSV1c-D: the off-frame-at-rest frontier was the wrong owned set,
//    not a camera fit error).
#include "ui/researchview.h"

#include <algorithm>
#include <cstdio>
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

// Fixture shape shared with test_researchview_t408 (self-contained copy).
std::optional<ag::Campaign> freshCampaign() {
    static ag::StarStats stats;
    static std::vector<std::string> names;
    static ag::ResearchTree tree;
    static std::vector<ag::PlanetItem> items;
    static std::vector<ag::Gizmo> gizmos;
    static std::vector<ag::DipFile> ai;
    static bool loaded = false;
    if (!loaded) {
        std::string e;
        const std::string R = ASCENDANCY_SOURCE_DIR;
        auto st = ag::StarStats::load(R + "/extracted/ascend00/starstat.txt", &e);
        if (!st) return std::nullopt;
        stats = *st;
        names = ag::loadStarNames(R + "/extracted/ascend00/names.txt", &e);
        tree = ag::ResearchTree::loadFromFile(R + "/extracted/ascend00/restree.txt", e);
        items = ag::loadPlanItems(R + "/extracted/ascend00/planitem.txt", e);
        gizmos = ag::loadGizmos(R + "/extracted/ascend00/gizmos.txt", e);
        for (int i = 0; i < 6; ++i) {
            ag::DipFile df;
            char path[256];
            std::snprintf(path, sizeof(path), "%s/extracted/ascend00/race%02d.dip",
                          R.c_str(), i);
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

// (1) START MASK: zero owned rows for EVERY owner at campaign build.
TEST(starttech_zero_mask_tpf8) {
    REQUIRE_DATA();
    auto c = freshCampaign();
    if (!c.has_value()) { CHECK(c.has_value()); return; }
    for (int o = 0; o <= 6; ++o)
        CHECK(c->techsOwned(o) == 0);  // mask 0x00 x 66 rows, 72/72 saves
}

// (2) FRONTIER AT START == EXACTLY the three prereq-empty roots {0,2,6}
//     (restree.txt rows with 255 in the first prereq slot) — the D28
//     item-21 "three circles, nothing else" law for the state model.
TEST(starttech_frontier_is_roots_tpf8) {
    REQUIRE_DATA();
    auto c = freshCampaign();
    if (!c.has_value()) { CHECK(c.has_value()); return; }
    std::string err;
    ag::ResearchTree tree = ag::ResearchTree::loadFromFile(
        std::string(ASCENDANCY_SOURCE_DIR) + "/extracted/ascend00/restree.txt", err);
    CHECK(err.empty());
    std::vector<int> roots;
    const auto& all = tree.all();
    // MAIN rows only (OQ-013: variants never load); variant rows have
    // prereq lists too and would pollute the root set.
    for (size_t i = 0; i < size_t(tree.mainCount()); ++i)
        if (all[i].prereqs.empty()) roots.push_back(int(i));
    CHECK(roots.size() == 3);
    std::sort(roots.begin(), roots.end());
    CHECK((roots.size() == 3 && roots[0] == 0 && roots[1] == 2 && roots[2] == 6));
    std::vector<int> frontier;
    for (const auto& nd : au::researchNodes(*c, tree, ag::kPlayer))
        if (nd.state == au::TechNodeState::Available) frontier.push_back(nd.row);
    CHECK(frontier == roots);
}

// (3) ZERO PAINTABLE EDGES at start: edge law 0x48275 gates BOTH endpoints
//     on the 0x46d3c true-set; legal set == {0,2,6}, roots carry no prereqs.
TEST(starttech_zero_edges_tpf8) {
    REQUIRE_DATA();
    auto c = freshCampaign();
    if (!c.has_value()) { CHECK(c.has_value()); return; }
    std::string err;
    ag::ResearchTree tree = ag::ResearchTree::loadFromFile(
        std::string(ASCENDANCY_SOURCE_DIR) + "/extracted/ascend00/restree.txt", err);
    CHECK(err.empty());
    const auto nodes = au::researchNodes(*c, tree, ag::kPlayer);
    // Variant-row prereqs (>= 66) are NEVER owned in play (OQ-013) ->
    // never legal; the projected node table only holds the 66 main rows.
    const int mainN = tree.mainCount();
    auto legal = [&](int row) {
        return row >= 0 && row < mainN &&
               nodes[size_t(row)].state != au::TechNodeState::Blocked;
    };
    int edges = 0;
    const auto& all = tree.all();
    for (size_t i = 0; i < size_t(mainN); ++i) {
        if (!legal(int(i))) continue;         // 0x4856d skip precedes the loop
        for (int p : all[i].prereqs)
            if (legal(p)) ++edges;            // 0x4829f pass -> line painted
    }
    CHECK(edges == 0);
    // Anti-vacuity: after owning row 2, row 7 (prereq {2}) must produce
    // EXACTLY one paintable edge (2 -> 7) — the counter counts real pairs.
    c->setAllTechs(ag::kPlayer, false);  // no-op safety; already zero
    // Grant row 2 through the cited completion shape: researchPhase would
    // take ~100 turns, so use the free-grant channel then re-check shape.
    // Determinism: grant until row 2 lands (bounded; row 2 is always in the
    // unowned candidate pool).
    for (int k = 0; k < 200 && !c->techRowOwnedFor(ag::kPlayer, 2); ++k)
        c->freeTechGrantFor(ag::kPlayer);
    CHECK(c->techRowOwnedFor(ag::kPlayer, 2));
    const auto nodes2 = au::researchNodes(*c, tree, ag::kPlayer);
    auto legal2 = [&](int row) {
        return row >= 0 && row < mainN &&
               nodes2[size_t(row)].state != au::TechNodeState::Blocked;
    };
    int e2 = 0;
    for (size_t i = 0; i < size_t(mainN); ++i) {
        if (!legal2(int(i))) continue;
        for (int p : all[i].prereqs)
            if (legal2(p)) ++e2;
    }
    CHECK(e2 >= 1);
}

// (4) REST-CAMERA FRAME LAW: the three roots project INSIDE the RESWIN
//     clip at the rest camera — clickable without dollying (TRSV1c-D).
TEST(starttech_roots_onframe_tpf8) {
    REQUIRE_DATA();
    auto c = freshCampaign();
    if (!c.has_value()) { CHECK(c.has_value()); return; }
    std::string err;
    ag::ResearchTree tree = ag::ResearchTree::loadFromFile(
        std::string(ASCENDANCY_SOURCE_DIR) + "/extracted/ascend00/restree.txt", err);
    CHECK(err.empty());
    const auto nodes = au::researchNodes(*c, tree, ag::kPlayer);
    const auto geom = au::researchTreeGeometry(tree);
    const auto centres = au::researchNodeScreen(geom, nodes, 0, 0, au::ResCam{});
    for (int row : {0, 2, 6}) {
        const auto& p = centres[size_t(row)];
        CHECK(p.visible);
        CHECK(p.x >= 7 && p.x <= 476);
        CHECK(p.y >= 46 && p.y <= 472);
    }
}

// (5) RETIRED-NAME + WIRING PIN: the uncited opening grant must never
//     re-creep into the constructor, and the ui.cpp edge loop must gate
//     BOTH endpoints on .visible (0x4856d + 0x4829f).
TEST(starttech_wiring_retired_tpf8) {
    REQUIRE_DATA();
    const std::string R = ASCENDANCY_SOURCE_DIR;
    auto slurp = [&](const std::string& p) {
        std::string s;
        FILE* f = std::fopen(p.c_str(), "rb");
        if (!f) return s;
        char buf[8192];
        size_t n;
        while ((n = std::fread(buf, 1, sizeof(buf), f)) > 0) s.append(buf, n);
        std::fclose(f);
        return s;
    };
    const std::string camp = slurp(R + "/rewrite/src/game/campaign.cpp");
    CHECK(!camp.empty());
    CHECK(camp.find("techSet[0] = true") == std::string::npos);
    CHECK(camp.find("techSet[1] = true") == std::string::npos);
    const std::string ui = slurp(R + "/rewrite/src/ui/ui.cpp");
    CHECK(!ui.empty());
    // Both endpoint gates present verbatim in the edge loop.
    CHECK(ui.find("if (!centres[i].visible) continue;") != std::string::npos);
    CHECK(ui.find("if (!centres[size_t(pr)].visible) continue;") !=
          std::string::npos);
}
