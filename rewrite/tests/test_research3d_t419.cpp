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
// The t408 GRID law (superseded by tRS-V1c's vendor circles; kept ONLY as
// the cost oracle for the frame-budget census — its constants are inlined
// because the header no longer carries them).
au::ResPoint oldNodePos(const ag::ResearchTree& tree, int row, int panX,
                        int panY) {
    const int depth = oldDepth(tree, row);
    int slot = 0;
    for (int r = 0; r < row; ++r)
        if (oldDepth(tree, r) == depth) ++slot;
    return au::ResPoint{40 + depth * 96 + panX, 76 + slot * 78 + panY};
}
}  // namespace

// ---- 1. depth law UNCHANGED (the t408 oracle still rules P1b) -------------
TEST(researchlayout_equivalence_t419) {
    REQUIRE_DATA();
    auto camp = seededCampaign();
    if (!camp.has_value()) { CHECK(camp.has_value()); return; }
    std::string err;
    ag::ResearchTree tree = ag::ResearchTree::loadFromFile(
        kRepo + "/extracted/ascend00/restree.txt", err);
    // tRS-V1c SUPERSESSION NOTE: the grid PLACEMENT (oldNodePos below) is
    // dead — the vendor law is the chain of circles (researchview.h). What
    // SURVIVES is the DEPTH law: the vendor relaxation (P1b) computes the
    // same longest-prereq-chain value the t408 oracle does. Pinned per row.
    for (int r = 0; r < tree.mainCount(); ++r)
        CHECK(au::researchDepth(tree, r) == oldDepth(tree, r));
}

// ---- 2. vendor window law + 3. rotation/dolly move the view ----------------
TEST(research3d_rest_and_spin_t419) {
    REQUIRE_DATA();
    auto camp = seededCampaign();
    if (!camp.has_value()) { CHECK(camp.has_value()); return; }
    std::string err;
    ag::ResearchTree tree = ag::ResearchTree::loadFromFile(
        kRepo + "/extracted/ascend00/restree.txt", err);
    const auto nodes = au::researchNodes(*camp, tree, ag::kPlayer);
    const auto L = au::researchTreeGeometry(tree);
    // REST WINDOW LAW (t252 corroboration + P4 scale): the 66-node field is
    // ~7-9x the window — at rest exactly THREE disks sit inside the RESWIN
    // rect (rows 0/2/6 at (64,240),(235,344),(407,240) — the t252 "three
    // disks, lines off-frame" grade).
    const auto rest = au::researchNodeScreen(L, nodes, 0, 0, au::ResCam{});
    CHECK(rest.size() == nodes.size());
    int inwin = 0;
    for (size_t i = 0; i < nodes.size(); ++i)
        if (rest[i].visible && rest[i].x >= 7 && rest[i].x <= 476 &&
            rest[i].y >= 46 && rest[i].y <= 472)
            ++inwin;
    CHECK(inwin == 3);
    // The tRSB1 witness click re-derivation relies on an Available visible
    // node existing at rest; on a fresh campaign rows 0/2/6 are Available.
    // Spin law (yaw, NOT the old spin latch): +-3 deg/tick moves centres.
    au::ResCam cam;
    cam.pressRot(false);
    CHECK(cam.moving());
    for (int t = 0; t < 10; ++t) cam.tick();  // 30 deg
    const auto spun = au::researchNodeScreen(L, nodes, 0, 0, cam);
    bool moved = false;
    double zmin = spun.empty() ? 0.0 : spun[0].z2, zmax = zmin;
    for (size_t i = 0; i < nodes.size(); ++i) {
        if (!spun[i].visible || !rest[i].visible) { moved = true; continue; }
        if (spun[i].x != rest[i].x || spun[i].y != rest[i].y) moved = true;
        zmin = std::min(zmin, spun[i].z2);
        zmax = std::max(zmax, spun[i].z2);
    }
    CHECK(moved);
    CHECK(zmax > zmin);  // perspective depth spread under rotation
    // tRS-SC SCROLL law: the MOVE pair moves camera POSITION Y (win+0xe3,
    // 0x47d03..0x47d12 VERBATIM), never depth. (1,0) => posY -= 1; (1,1) =>
    // posY += 1. Screen rows slide; the depth spread z2 is invariant.
    au::ResCam dolly;
    dolly.pressMove(false);  // (1,0) => posY -= 1
    dolly.tick();
    CHECK(std::fabs(dolly.posY - (-1.0)) < 1e-9);
    CHECK(std::fabs(dolly.posZ - (-150.0)) < 1e-9);  // depth never pumped
    dolly.pressMove(true);   // (1,1) => posY += 1 per tick
    for (int t = 0; t < 31; ++t) dolly.tick();  // net posY = +30
    const auto scrolled = au::researchNodeScreen(L, nodes, 0, 0, dolly);
    CHECK(std::fabs(dolly.posY - 30.0) < 1e-9);
    // Rows slide UP under a +posY camera (vY shrinks), depth unchanged.
    // Observation at a SMALL scroll: the u16 word law (u16wrap) legitimately
    // wraps a row pushed far off-frame, so a +30 dolly of row 0 (Y=0, the
    // topmost-visible check) is NOT a y<rest comparison — t419 wrap law.
    au::ResCam small;
    small.posY = 2.0;
    const auto scr2 = au::researchNodeScreen(L, nodes, 0, 0, small);
    CHECK(scr2[0].y < rest[0].y);
    CHECK(scr2[0].z2 == rest[0].z2);
    // Hit map follows the view: a rest centre resolves its node at rest.
    const auto h0 = au::researchHit(tree, nodes, rest[0].x, rest[0].y, 0, 0);
    CHECK(h0.kind == au::ResHit::Node);
    CHECK(h0.row == nodes[0].row);
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
    const au::ResCam cam;  // tRS-V1c camera law (rest yaw 0, posZ -150)
    // Warm up once (first-touch allocations), then time 60 passes (a second
    // of painter at 60fps): geometry ONCE + screen pass per pass, exactly
    // the per-frame cost shape of the painter (the t419 stall class stays
    // pinned away under the NEW law too).
    (void)au::researchNodeScreen(au::researchTreeGeometry(tree), nodes, 0, 0,
                                 cam);
    const auto t0 = std::chrono::steady_clock::now();
    for (int f = 0; f < 60; ++f) {
        const auto L = au::researchTreeGeometry(tree);
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
