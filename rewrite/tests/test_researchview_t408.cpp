// SPDX-License-Identifier: GPL-3.0-or-later

// t408 RESEARCH SCREEN (state 20 RESWIN) law pins.
// LAW (docs/re/_wip_t408.md F2/F6/F7 + researchview.h citation block):
//  1. PANEL TEXT = static.txt reswin.cpp pool, marker-driven reader (the
//     fleet-screen.md F10 getter-index law — the naive quoted-line counter
//     misaligns from ~entry 90): #122 "Current Project:", #124 "(%d day%s)",
//     #125 "Allows", #130 "%s Knowledge %s".
//  2. CLICK LAW (help reswin verbatim + t268 live dossier): an Available
//     ("empty disk") click SETS the study topic; Owned/Blocked clicks are
//     silent no-ops.
//  3. MEMBERSHIP = the 66 live main rows only (OQ-013 CLOSED); the
//     partition Owned/Study/Available/Blocked is the prereq law.
//  4. ALLOWS = the verified reverse join (ui-runtime.md 6d, 3/3 witnesses):
//     gizmos + planitems whose tech field == row, TABLE ORDER.
//  5. GEOMETRY: the four pan rects verbatim windows.txt (note the 554->563
//     gap — verbatim, not fixed); hit precedence pan -> nodes; node radius
//     from the t268 pixel-diff bbox (41..100 => r 30).
//  6. SET-RESEARCH RESOLVES AT TURN END (the queue row's named closer):
//     setStudy then advanceTurn -> the campaign's queue reflects it (and a
//     completion grants the tech).
#include "ui/researchview.h"

#include <cctype>
#include <algorithm>
#include <cstdio>
#include <fstream>
#include <map>
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
const std::string kRepo = ASCENDANCY_SOURCE_DIR;

// Marker-driven static.txt reader (fleet-screen.md F10 law; the t407 copy —
// kept local so this file stays self-contained like every other pin file).
std::map<int, std::string> staticTxtEntries() {
    std::ifstream f(kRepo + "/extracted/ascend00/static.txt", std::ios::binary);
    std::map<int, std::string> out;
    std::vector<std::string> lines;
    std::string line;
    while (std::getline(f, line)) {
        if (!line.empty() && line.back() == '\r') line.pop_back();
        lines.push_back(line);
    }
    for (size_t i = 0; i < lines.size(); i++) {
        std::string s = lines[i];
        size_t b = s.find_first_not_of(" \t");
        if (b == std::string::npos) continue;
        s = s.substr(b);
        if (s.size() < 3 || s[0] != '/' || s[1] != '/') continue;
        std::string t = s.substr(2);
        size_t p = 0;
        while (p < t.size() && (t[p] == ' ' || t[p] == '\t')) p++;
        size_t q = p;
        while (q < t.size() && isdigit(static_cast<unsigned char>(t[q]))) q++;
        if (q == p) continue;
        int a = std::stoi(t.substr(p, q - p));
        int n = 1;
        size_t d = q;
        while (d < t.size() && (t[d] == ' ' || t[d] == '\t')) d++;
        if (d < t.size() && t[d] == '-') {
            d++;
            while (d < t.size() && (t[d] == ' ' || t[d] == '\t')) d++;
            size_t r = d;
            while (r < t.size() && isdigit(static_cast<unsigned char>(t[r]))) r++;
            if (r > d) n = std::stoi(t.substr(d, r - d)) - a + 1;
        }
        int got = 0;
        for (size_t j = i + 1; j < lines.size() && got < n; j++) {
            std::string u = lines[j];
            size_t bb = u.find_first_not_of(" \t");
            if (bb == std::string::npos) {
                if (got) break;
                continue;
            }
            u = u.substr(bb);
            if (u.empty() || u[0] != '"') {
                if (u.size() > 1 && u[0] == '/' && got) break;
                if (got) break;
                continue;
            }
            std::string e = u;
            while (e.size() < 2 || e.back() != '"') {
                j++;
                if (j >= lines.size()) break;
                std::string nx = lines[j];
                e.pop_back();
                e += nx;
            }
            e = e.substr(1, e.size() - 2);
            size_t np = 0;
            while ((np = e.find("\\n", np)) != std::string::npos)
                e.replace(np, 2, "\n");
            out[a + got] = e;
            got++;
        }
    }
    return out;
}

// Seeded campaign over the SHIPPED data (t402/t407 fixture pattern).
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
        auto st = ag::StarStats::load(kRepo + "/extracted/ascend00/starstat.txt", &e);
        if (!st) return std::nullopt;
        stats = *st;
        names = ag::loadStarNames(kRepo + "/extracted/ascend00/names.txt", &e);
        tree = ag::ResearchTree::loadFromFile(kRepo + "/extracted/ascend00/restree.txt", e);
        items = ag::loadPlanItems(kRepo + "/extracted/ascend00/planitem.txt", e);
        gizmos = ag::loadGizmos(kRepo + "/extracted/ascend00/gizmos.txt", e);
        for (int i = 0; i < 6; ++i) {
            ag::DipFile df;
            char path[256];
            std::snprintf(path, sizeof(path), "%s/extracted/ascend00/race%02d.dip",
                          ASCENDANCY_SOURCE_DIR, i);
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

// ---- 1. the shipped static.txt strings behind the panel -------------------
TEST(researchview_static_templates_t408) {
    REQUIRE_DATA();
    const auto s = staticTxtEntries();
    CHECK(s.count(122) == 1);
    CHECK(s.at(122) == "Current Project:");
    CHECK(s.at(123) == "(No Progress)");
    CHECK(s.at(124) == "(%d day%s)");
    CHECK(s.at(125) == "Allows");
    CHECK(s.at(130) == "%s Knowledge %s");
    // The header join the captures show (t252/t268 "Chamachies Knowledge"):
    // first-%s of #130; the second slot never appears in any capture (seam).
    CHECK(au::researchHeaderText("Chamachies") == "Chamachies Knowledge");
}

// ---- 2. days line: #124 shape + the singular-pair law ---------------------
TEST(researchview_days_line_t408) {
    CHECK(au::researchDaysLine(100.0, 10.0) == "(10 days)");
    CHECK(au::researchDaysLine(95.0, 10.0) == "(10 days)");   // ceil 9.5
    CHECK(au::researchDaysLine(10.0, 10.0) == "(1 day)");     // singular iff 1
    CHECK(au::researchDaysLine(0.0, 10.0) == "(0 days)");     // done/none
    CHECK(au::researchDaysLine(50.0, 0.0) == "(0 days)");     // rate<=0 default
}

// ---- 3. membership + partition over the REAL tree ------------------------
TEST(researchview_partition_t408) {
    REQUIRE_DATA();
    auto camp = seededCampaign();
    if (!camp.has_value()) { CHECK(camp.has_value()); return; }
    std::string err;
    ag::ResearchTree tree = ag::ResearchTree::loadFromFile(
        kRepo + "/extracted/ascend00/restree.txt", err);
    const auto nodes = au::researchNodes(*camp, tree, ag::kPlayer);
    CHECK(nodes.size() == size_t(tree.mainCount()));      // 66 live rows
    CHECK(nodes.size() == 66);                            // research.md §6c
    int owned = 0, avail = 0, blocked = 0, study = 0;
    for (const auto& nd : nodes) {
        switch (nd.state) {
            case au::TechNodeState::Owned: ++owned; break;
            case au::TechNodeState::Available: ++avail; break;
            case au::TechNodeState::Blocked: ++blocked; break;
            case au::TechNodeState::Study: ++study; break;
        }
        // Partition consistency: Available iff unowned && all prereqs owned.
        bool prereq = true;
        for (int p : tree.all()[nd.row].prereqs)
            if (!camp->techRowOwnedFor(ag::kPlayer, p)) prereq = false;
        if (nd.state == au::TechNodeState::Available) CHECK(prereq);
        if (nd.state == au::TechNodeState::Blocked) CHECK(!prereq);
        if (nd.state == au::TechNodeState::Owned) CHECK(camp->techRowOwnedFor(ag::kPlayer, nd.row));
    }
    CHECK(owned == 0);       // tPF-8 START LAW: vendor mask 0x00 for every
                             // row x race at game start (72/72 boot saves,
                             // scripts/tPF8_startmask_census.py)
    CHECK(avail == 3);       // EXACTLY the three prereq-empty roots
    {
        int availRows[3] = {-1, -1, -1};
        int k = 0;
        for (const auto& nd : nodes)
            if (nd.state == au::TechNodeState::Available && k < 3)
                availRows[k++] = nd.row;
        std::sort(availRows, availRows + 3);
        CHECK(availRows[0] == 0 && availRows[1] == 2 && availRows[2] == 6);
    }
    CHECK(blocked == 63);    // everything else gated (roots unowned)
    CHECK(study <= 1);       // at most one current topic
}

// ---- 4. SET-STUDY LAW (help reswin + t268 click witness) -----------------
TEST(researchview_set_study_law_t408) {
    REQUIRE_DATA();
    auto camp = seededCampaign();
    if (!camp.has_value()) { CHECK(camp.has_value()); return; }
    std::string err;
    ag::ResearchTree tree = ag::ResearchTree::loadFromFile(
        kRepo + "/extracted/ascend00/restree.txt", err);
    const auto nodes = au::researchNodes(*camp, tree, ag::kPlayer);
    int availRow = -1, blockedRow = -1, ownedRow = -1;
    // tPF-8: nothing is owned at start (vendor law), so the Owned-state row
    // comes from the cited FREE GRANT channel (0x46f4f..0x46f64 marks one
    // unowned row; test_freetech_t203 pins that law separately).
    const int granted = camp->freeTechGrantFor(ag::kPlayer);
    for (const auto& nd : au::researchNodes(*camp, tree, ag::kPlayer)) {
        if (nd.state == au::TechNodeState::Available && availRow < 0 && nd.row != granted)
            availRow = nd.row;
        if (nd.state == au::TechNodeState::Blocked) blockedRow = nd.row;
        if (nd.state == au::TechNodeState::Owned) ownedRow = nd.row;
    }
    if (!(availRow >= 0 && blockedRow >= 0 && ownedRow >= 0)) {
        CHECK(availRow >= 0 && blockedRow >= 0 && ownedRow >= 0); return; }
    // Available click lands.
    CHECK(au::setStudy(*camp, tree, ag::kPlayer, availRow));
    CHECK(camp->isTechQueuedFor(ag::kPlayer, availRow));
    // Owned click = dossier read only (t268: "no state change").
    CHECK(!au::setStudy(*camp, tree, ag::kPlayer, ownedRow));
    // Blocked click = silent no-op.
    CHECK(!au::setStudy(*camp, tree, ag::kPlayer, blockedRow));
    // Domain refusal: variant rows are not in play (OQ-013).
    CHECK(!au::setStudy(*camp, tree, ag::kPlayer, tree.mainCount()));
    CHECK(!au::setStudy(*camp, tree, ag::kPlayer, -1));
    // The Study state now shows in the partition, exactly one topic.
    int study = 0;
    for (const auto& nd : au::researchNodes(*camp, tree, ag::kPlayer))
        if (nd.state == au::TechNodeState::Study) { study++; CHECK(nd.row == availRow); }
    CHECK(study == 1);
}

// ---- 5. SET-RESEARCH RESOLVES AT TURN END (the row's named closer) -------
TEST(researchview_set_resolves_at_turn_end_t408) {
    REQUIRE_DATA();
    auto camp = seededCampaign();
    if (!camp.has_value()) { CHECK(camp.has_value()); return; }
    std::string err;
    ag::ResearchTree tree = ag::ResearchTree::loadFromFile(
        kRepo + "/extracted/ascend00/restree.txt", err);
    // Pick an Available row with the SMALLEST runtime cost (fastest to
    // complete deterministically within the loop bound).
    const auto nodes = au::researchNodes(*camp, tree, ag::kPlayer);
    int pick = -1;
    for (const auto& nd : nodes)
        if (nd.state == au::TechNodeState::Available &&
            (pick < 0 || tree.all()[nd.row].runtimeCost() <
                             tree.all()[pick].runtimeCost()))
            pick = nd.row;
    if (pick < 0) { CHECK(pick >= 0); return; }
    CHECK(au::setStudy(*camp, tree, ag::kPlayer, pick));
    bool resolved = false;
    for (int t = 0; t < 400 && !camp->over(); ++t) {
        camp->advance();
        if (camp->techRowOwnedFor(ag::kPlayer, pick)) { resolved = true; break; }
        if (!camp->isTechQueuedFor(ag::kPlayer, pick) &&
            !camp->techRowOwnedFor(ag::kPlayer, pick))
            break;  // the engine re-picked (target stolen, t1816 shape): stop
    }
    CHECK(resolved);  // the click's choice was RESEARCHED, not overwritten
}

// ---- 6. ALLOWS reverse join (ui-runtime.md 6d, 3/3 witnesses) ------------
TEST(researchview_allows_join_t408) {
    REQUIRE_DATA();
    auto camp = seededCampaign();
    if (!camp.has_value()) { CHECK(camp.has_value()); return; }
    // Witness 1: Energy^Focusing row 42 = idx 39 -> Myrmidonic^Carbonizer +
    // Accutron (gizmos.txt, file order). Witness 3: Megagraph row 62 = idx 59
    // -> Internet (planitem.txt). The join is table-ordered gizmos-then-items.
    const auto a39 = au::allowsList(*camp, 39);
    CHECK(a39.size() >= 2);
    CHECK(a39[0] == "Myrmidonic Carbonizer");
    CHECK(a39[1] == "Accutron");
    const auto a59 = au::allowsList(*camp, 59);
    bool internet = false;
    for (const auto& s : a59) if (s == "Internet") internet = true;
    CHECK(internet);
    // '^' display law: no joined name keeps a caret.
    for (int r = 0; r < 66; ++r)
        for (const auto& s : au::allowsList(*camp, r))
            CHECK(s.find('^') == std::string::npos);
}

// ---- 7. geometry: pan rects verbatim + hit precedence --------------------
TEST(researchview_geometry_t408) {
    // windows.txt verbatim (L1775-1840): note the 554->563 x gap between
    // RESROTRIGHT and RESMOVEUP — verbatim, NOT "fixed".
    CHECK(au::kResRotLeft.x0 == 524 && au::kResRotLeft.y0 == 442 &&
          au::kResRotLeft.x1 == 539 && au::kResRotLeft.y1 == 472);
    CHECK(au::kResRotRight.x0 == 540 && au::kResRotRight.x1 == 554);
    CHECK(au::kResMoveUp.x0 == 563 && au::kResMoveUp.y1 == 457);
    CHECK(au::kResMoveDown.y0 == 458 && au::kResMoveDown.y1 == 472);
    // The pan buttons live OUTSIDE the RESWIN rect (7,46-476,472): a click
    // at x>=524 must hit the button, never a node.
    ag::ResearchTree tree;  // empty tree: no nodes anywhere
    std::vector<au::TechNode> none;
    CHECK(au::researchHit(tree, none, 530, 460, 0, 0).kind == au::ResHit::RotLeft);
    CHECK(au::researchHit(tree, none, 545, 460, 0, 0).kind == au::ResHit::RotRight);
    CHECK(au::researchHit(tree, none, 570, 450, 0, 0).kind == au::ResHit::MoveUp);
    CHECK(au::researchHit(tree, none, 570, 465, 0, 0).kind == au::ResHit::MoveDown);
    CHECK(au::researchHit(tree, none, 558, 460, 0, 0).kind == au::ResHit::None);  // the gap
}

// ---- 8. node determinism + hit round-trip --------------------------------
// tRS-V1c SUPERSESSION: the t408 GRID coordinates (x = depth*96, prereqs
// strictly LEFT) are dead — the vendor chain-of-circles has no left->right
// invariant (depth runs along the tilted circle-chain axis). What survives
// of this pin: determinism, exact pan offsets, and a hit round-trip on a
// centre that is VERIFIED isolated before the click (never a hard-coded
// row: with overlapping +-24 boxes first-hit-high-wins, not row-30-wins).
TEST(researchview_layout_hit_roundtrip_t408) {
    REQUIRE_DATA();
    auto camp = seededCampaign();
    if (!camp.has_value()) { CHECK(camp.has_value()); return; }
    std::string err;
    ag::ResearchTree tree = ag::ResearchTree::loadFromFile(
        kRepo + "/extracted/ascend00/restree.txt", err);
    const auto nodes = au::researchNodes(*camp, tree, ag::kPlayer);
    const au::ResCam cam;
    // Determinism: same inputs -> same centres; pan shifts exactly.
    const auto a = au::researchNodePos(tree, 5, 0, 0);
    const auto b = au::researchNodePos(tree, 5, 0, 0);
    const auto c = au::researchNodePos(tree, 5, -120, 30);
    CHECK(a.x == b.x && a.y == b.y);
    CHECK(c.x == a.x - 120 && c.y == a.y + 30);
    // Hit round-trip on an ISOLATED centre: pick the first row whose
    // projected centre has no other centre within 49 px on either axis.
    const auto G = au::researchTreeGeometry(tree);
    const auto centres = au::researchNodeScreen(G, nodes, 0, 0, cam);
    int probe = -1;
    for (int r = 0; r < tree.mainCount(); ++r) {
        if (!centres[size_t(r)].visible) continue;
        bool iso = true;
        for (int q = 0; q < tree.mainCount() && iso; ++q) {
            if (q == r || !centres[size_t(q)].visible) continue;
            if (std::abs(centres[size_t(q)].x - centres[size_t(r)].x) <= 49 &&
                std::abs(centres[size_t(q)].y - centres[size_t(r)].y) <= 49)
                iso = false;
        }
        if (iso) { probe = r; break; }
    }
    CHECK(probe >= 0);
    if (probe >= 0) {
        const auto& cc = centres[size_t(probe)];
        const auto h = au::researchHit(tree, nodes, cc.x, cc.y, 0, 0);
        CHECK(h.kind == au::ResHit::Node);
        CHECK(h.row == probe);
    }
    // A corner point is inert: at rest every projected centre has
    // x in [19,451] (|focal*23/127| + 235) and y >= 240 - a hair, so (5,5)
    // is >24 px from every centre on BOTH axes.
    CHECK(au::researchHit(tree, nodes, 5, 5, 0, 0).kind == au::ResHit::None);
}
