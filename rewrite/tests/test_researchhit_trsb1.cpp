// SPDX-License-Identifier: GPL-3.0-or-later

// tRS-B1 VENDOR HIT-LAW pin (D26 research set-project; derivation
// docs/re/_wip_tRSB1.md P2: reswin click sub 0x47478, bounds legs
// 0x474fb..0x4752d in work/tRS_reswin_fn.asm):
//   accept iff nodeX-25 < cx AND cx < nodeX+25 AND nodeY-25 < cy AND
//            cy < nodeY+25      (signed jle/jge reject AT exactly +-25)
//   => INCLUSIVE +-24 SQUARE about the projected centre, FIXED size.
// The pre-tRS-B1 port used a DISC of the perspective-scaled ring radius
// (r30 at rest): it MISSED the square corners (24,24) (d=33.9>30) and HIT
// axis points 25..29 the vendor rejects. These legs pin the difference in
// BOTH directions; mutating kResHitHalf to 25, back to a circle, or to a
// radius-scaled box fails at least one CHECK here. Pure geometry — the
// node vector is fabricated (researchHit reads only row + the layout).
#include "ui/researchview.h"

#include <cstdlib>
#include <string>
#include <utility>
#include <vector>

#include "harness.h"

#ifndef ASCENDANCY_SOURCE_DIR
#define ASCENDANCY_SOURCE_DIR "."
#endif

namespace {
namespace au = ascend::ui;
namespace ag = ascend::game;
const std::string kRepo = ASCENDANCY_SOURCE_DIR;

TEST(research_hit_square_law_trsb1) {
    REQUIRE_DATA();
    std::string err;
    ag::ResearchTree tree = ag::ResearchTree::loadFromFile(
        kRepo + "/extracted/ascend00/restree.txt", err);
    if (tree.mainCount() != 66) { CHECK(tree.mainCount() == 66); return; }
    std::vector<au::TechNode> nodes;
    for (int r = 0; r < tree.mainCount(); ++r) {
        au::TechNode nd;
        nd.row = r;
        nd.state = au::TechNodeState::Available;
        nodes.push_back(nd);
    }

    // The constant itself is the law (researchview.h cites 0x474fb..52d).
    CHECK(au::kResHitHalf == 24);

    // tRS-V1c UPDATE: the probe row is no longer hard-coded (row 30's grid
    // centre is gone; under the vendor circle law some centres overlap).
    // Pick the FIRST visible row with no other centre within 49 px on both
    // axes, then the probe premise holds by construction and the +-24 legs
    // below are answered by THAT row alone.
    const auto G = au::researchTreeGeometry(tree);
    const auto centres = au::researchNodeScreen(G, nodes, 0, 0, au::ResCam{});
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
    if (probe < 0) return;
    const au::ResPoint3 c = centres[size_t(probe)];
    auto hitAt = [&](int dx, int dy) {
        return au::researchHit(tree, nodes, c.x + dx, c.y + dy, 0, 0);
    };
    // INCLUSIVE boundary: axis edges AND corners hit the probe row. The
    // corners are the disc-vs-square discriminator (the r30 disc missed
    // (24,24)).
    for (auto [dx, dy] : std::vector<std::pair<int, int>>{
             {24, 0}, {-24, 0}, {0, 24}, {0, -24},
             {24, 24}, {24, -24}, {-24, 24}, {-24, -24}}) {
        const auto h = hitAt(dx, dy);
        CHECK(h.kind == au::ResHit::Node);
        CHECK(h.row == probe);
    }
    // EXCLUSIVE at 25: the jle/jge legs reject at exactly 25, so the probe
    // row must NEVER answer an axis probe at +-25.
    for (auto [dx, dy] : std::vector<std::pair<int, int>>{
             {25, 0}, {-25, 0}, {0, 25}, {0, -25}}) {
        const auto h = hitAt(dx, dy);
        CHECK(!(h.kind == au::ResHit::Node && h.row == probe));
    }
}
}  // namespace
