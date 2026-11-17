// SPDX-License-Identifier: GPL-3.0-or-later

// t419 RESEARCH SCREEN stall-fix + 3D law pins.
// LAW (docs/re/_wip_t419.md F1/F6 + researchview.h):
//  1. ResearchLayout answers == the t408 per-call law for EVERY row
//     (depth + slot equivalence census on the live 66-row tree).
//  2. REST 3D equality: researchNodeScreen through the rest camera
//     (focal == kResStandoff) reproduces researchNodePos EXACTLY, r == 30
//     (the t408 witness click coordinates therefore still land).
//  3. Spin changes the view: after pressSpin + tick the projected centres
//     move (and depth z2 varies) — the tree is genuinely 3D.
//  4. FRAME BUDGET: one layout + one screen pass over the full tree under a
//     generous steady_clock bound (5 ms) — proves the O(n^2 x graph)/frame
//     class is gone (the old law ran the full graph walk per slot-row).
//  5. Corner popup law: exitCornerFor corners/edges/interior + rect tuck.
#include "ui/researchview.h"
#include "ui/exitpopup.h"

#include <algorithm>
#include <chrono>
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
const std::string kRepo = ASCENDANCY_SOURCE_DIR;

std::optional<ag::Campaign> seededCampaign() {
    // The t408 fixture pattern verbatim (no startCampaign API exists).
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

// The OLD law, kept here as the pin's ORACLE (verbatim from t408
// researchview.cpp before the stall fix) so equivalence is measured
// against what the port used to answer, not against itself.
int oldDepth(const ag::ResearchTree& tree, int row) {
    std::vector<int> memo(size_t(tree.mainCount()), -1);
    for (int r = 0; r < tree.mainCount(); ++r) {
        std::vector<int> stack{r};
        while (!stack.empty()) {
            const int cur = stack.back();
            bool ready = true;
            for (int p : tree.all()[cur].prereqs) {
                if (p < 0 || p >= tree.mainCount()) continue;
                if (memo[p] < 0) { stack.push_back(p); ready = false; break; }
            }
            if (!ready) continue;
            int best = 0;
            for (int p : tree.all()[cur].prereqs)
                if (p >= 0 && p < tree.mainCount())
                    best = std::max(best, memo[p] + 1);
            memo[cur] = best;
            stack.pop_back();
        }
    }
    return row < 0 || row >= tree.mainCount() ? 0 : memo[size_t(row)];
}
au::ResPoint oldNodePos(const ag::ResearchTree& tree, int row, int panX,
                        int panY) {
    const int depth = oldDepth(tree, row);
    int slot = 0;
    for (int r = 0; r < row; ++r)
        if (oldDepth(tree, r) == depth) ++slot;
    return au::ResPoint{au::kResFieldX0 + depth * au::kResDepthPitch + panX,
                        au::kResFieldY0 + slot * au::kResRowPitch + panY};
}
}  // namespace

// ---- 1. layout == old law (all rows) --------------------------------------
TEST(researchlayout_equivalence_t419) {
    REQUIRE_DATA();
    auto camp = seededCampaign();
    if (!camp.has_value()) { CHECK(camp.has_value()); return; }
    std::string err;
    ag::ResearchTree tree = ag::ResearchTree::loadFromFile(
        kRepo + "/extracted/ascend00/restree.txt", err);
    const auto L = au::researchLayoutFor(tree);
    CHECK(int(L.depth.size()) == tree.mainCount());
    for (int r = 0; r < tree.mainCount(); ++r) {
        CHECK(L.depth[size_t(r)] == oldDepth(tree, r));
        CHECK(au::researchNodePosAt(L, r, 0, 0).x == oldNodePos(tree, r, 0, 0).x);
        CHECK(au::researchNodePosAt(L, r, 0, 0).y == oldNodePos(tree, r, 0, 0).y);
        // pan law preserved on the fast path too
        CHECK(au::researchNodePosAt(L, r, -37, 91).x ==
              oldNodePos(tree, r, -37, 91).x);
    }
    // researchDepth()/researchNodePos() delegating wrappers agree
    for (int r = 0; r < tree.mainCount(); ++r) {
        CHECK(au::researchDepth(tree, r) == oldDepth(tree, r));
        CHECK(au::researchNodePos(tree, r, 11, -5).x ==
              oldNodePos(tree, r, 11, -5).x);
    }
}

// ---- 2. rest 3D equality + 3. spin moves the view --------------------------
TEST(research3d_rest_and_spin_t419) {
    REQUIRE_DATA();
    auto camp = seededCampaign();
    if (!camp.has_value()) { CHECK(camp.has_value()); return; }
    std::string err;
    ag::ResearchTree tree = ag::ResearchTree::loadFromFile(
        kRepo + "/extracted/ascend00/restree.txt", err);
    const auto nodes = au::researchNodes(*camp, tree, ag::kPlayer);
    const auto L = au::researchLayoutFor(tree);
    const auto rest = au::researchNodeScreen(L, nodes, 0, 0,
                                             au::researchRestCam());
    CHECK(rest.size() == nodes.size());
    for (size_t i = 0; i < nodes.size(); ++i) {
        const auto p2 = au::researchNodePos(tree, nodes[i].row, 0, 0);
        CHECK(rest[i].x == p2.x);
        CHECK(rest[i].y == p2.y);
        CHECK(rest[i].r == au::kResNodeRadius);  // scale exactly 1 at rest
    }
    // Scroll law: post-projection pan is exact screen px.
    const auto scrolled = au::researchNodeScreen(L, nodes, 0, -78,
                                                 au::researchRestCam());
    for (size_t i = 0; i < nodes.size(); ++i) {
        CHECK(scrolled[i].y == rest[i].y - 78);
        CHECK(scrolled[i].x == rest[i].x);
    }
    // Spin: latch + pump (t416 law), then the view genuinely changed AND
    // depths spread (z2 not all-equal) — a flat 2D rehash cannot do that.
    au::Camera3d cam = au::researchRestCam();
    cam.pressSpin(+1);
    CHECK(cam.moving());
    for (int t = 0; t < 20; ++t) cam.tick();  // 40 deg
    const auto spun = au::researchNodeScreen(L, nodes, 0, 0, cam);
    bool moved = false;
    double zmin = spun.empty() ? 0.0 : spun[0].z2, zmax = zmin;
    for (size_t i = 0; i < nodes.size(); ++i) {
        if (spun[i].x != rest[i].x || spun[i].y != rest[i].y) moved = true;
        zmin = std::min(zmin, spun[i].z2);
        zmax = std::max(zmax, spun[i].z2);
    }
    CHECK(moved);
    CHECK(zmax > zmin);  // perspective depth spread under rotation
    // Stop law: opposite press then same press stops (dialLatch pair).
    cam.pressSpin(-1);   // flip direction, still moving
    CHECK(cam.moving());
    cam.pressSpin(-1);   // same direction again -> stop
    CHECK(!cam.moving());
    // Hit map follows the rotated view: rest centres hit at rest; under a
    // big spin the rest centre of a node must no longer resolve THAT node
    // for (nearly) every node — at least one centre stops resolving.
    au::Camera3d cam2 = au::researchRestCam();
    const auto h0 = au::researchHit(tree, nodes, rest[10].x, rest[10].y, 0, 0);
    CHECK(h0.kind == au::ResHit::Node);
    CHECK(h0.row == nodes[10].row);
    cam2.pressSpin(+1);
    for (int t = 0; t < 45; ++t) cam2.tick();  // 90 deg: edge-on field
    const auto spun2 = au::researchNodeScreen(L, nodes, 0, 0, cam2);
    const auto h1 = au::researchHit(tree, nodes, rest[10].x, rest[10].y, 0, 0,
                                    cam2);
    // At 90 deg the flat field collapses onto a vertical line: the point
    // that was disk 10's centre is not inside disk 10's projected centre.
    CHECK(spun2[10].x != rest[10].x || h1.row != nodes[10].row);
}

// ---- 4. frame budget: the O(n^2/frame) class is gone -----------------------
TEST(researchframe_budget_t419) {
    REQUIRE_DATA();
    auto camp = seededCampaign();
    if (!camp.has_value()) { CHECK(camp.has_value()); return; }
    std::string err;
    ag::ResearchTree tree = ag::ResearchTree::loadFromFile(
        kRepo + "/extracted/ascend00/restree.txt", err);
    const auto nodes = au::researchNodes(*camp, tree, ag::kPlayer);
    const auto cam = au::researchRestCam();
    // Warm up once (first-touch allocations), then time 60 passes (a second
    // of painter at 60fps): layout ONCE + screen pass per pass, exactly the
    // per-frame cost shape of the fixed painter.
    (void)au::researchNodeScreen(au::researchLayoutFor(tree), nodes, 0, 0,
                                 cam);
    const auto t0 = std::chrono::steady_clock::now();
    for (int f = 0; f < 60; ++f) {
        const auto L = au::researchLayoutFor(tree);
        const auto c = au::researchNodeScreen(L, nodes, f, -f, cam);
        CHECK(c.size() == nodes.size());
    }
    const auto us = std::chrono::duration_cast<std::chrono::microseconds>(
                        std::chrono::steady_clock::now() - t0).count();
    std::printf("    t419 frame cost: %lld us for 60 full-tree layout+screen "
                "passes (%.1f us/frame)\n",
                (long long)us, us / 60.0);
    // Generous bound (5 ms for the whole second of geometry): the OLD law
    // ran researchDepth (full 66-row graph walk) once per slot row per node
    // per frame; even at a conservative 2us/walk that is > 2 s for 60
    // frames. This CHECK is what pins the class away.
    CHECK(us < 5000);
    // SELF-CONTAINED BASELINE: time ONE frame of the OLD law (the oracle
    // above — O(n^2) full graph walks per frame). One old frame must dwarf
    // the entire 60-frame new pass; otherwise the census above proves
    // nothing about the class that was removed.
    const auto t1 = std::chrono::steady_clock::now();
    long sink = 0;
    for (size_t i = 0; i < nodes.size(); ++i)
        sink += oldNodePos(tree, nodes[i].row, 0, 0).x;
    const auto old_us = std::chrono::duration_cast<std::chrono::microseconds>(
                            std::chrono::steady_clock::now() - t1).count();
    std::printf("    t419 OLD-law baseline: %lld us for ONE 66-node frame "
                "(sink %ld)\n", (long long)old_us, sink);
    CHECK(old_us > 10 * us);
}

// ---- 5. corner popup law ----------------------------------------------------
TEST(exitpopup_corner_t419) {
    using EC = au::ExitCorner;
    // Corners hit (probe 24 default); edges alone and interior miss.
    CHECK(au::exitCornerFor(0, 0, 640, 480) == EC::TopLeft);
    CHECK(au::exitCornerFor(23, 23, 640, 480) == EC::TopLeft);
    CHECK(au::exitCornerFor(24, 23, 640, 480) == EC::None);
    CHECK(au::exitCornerFor(639, 0, 640, 480) == EC::TopRight);
    CHECK(au::exitCornerFor(616, 0, 640, 480) == EC::TopRight);
    CHECK(au::exitCornerFor(615, 0, 640, 480) == EC::None);
    CHECK(au::exitCornerFor(0, 479, 640, 480) == EC::BottomLeft);
    CHECK(au::exitCornerFor(639, 479, 640, 480) == EC::BottomRight);
    CHECK(au::exitCornerFor(320, 240, 640, 480) == EC::None);
    CHECK(au::exitCornerFor(10, 240, 640, 480) == EC::None);  // edge only
    CHECK(au::exitCornerFor(320, 10, 640, 480) == EC::None);
    // Rects: 78x47 glyph tucked flush into each corner (vendor anchor
    // posture, shp.md S27 signed bbox halves).
    const auto tl = au::exitPopupRect(EC::TopLeft, 640, 480);
    CHECK(tl.x0 == 0 && tl.y0 == 0 && tl.x1 == 77 && tl.y1 == 46);
    const auto br = au::exitPopupRect(EC::BottomRight, 640, 480);
    CHECK(br.x0 == 640 - 78 && br.y0 == 480 - 47 && br.x1 == 639 &&
          br.y1 == 479);
    const auto tr = au::exitPopupRect(EC::TopRight, 640, 480);
    CHECK(tr.x0 == 562 && tr.y0 == 0);
    const auto bl = au::exitPopupRect(EC::BottomLeft, 640, 480);
    CHECK(bl.x0 == 0 && bl.y0 == 433);
    // None -> empty rect (x1 < x0: nothing paints).
    const auto none = au::exitPopupRect(EC::None, 640, 480);
    CHECK(none.x1 < none.x0);
}
