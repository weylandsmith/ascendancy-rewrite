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

    // Row 30's +-24 box probes below must be answered by row 30 (or, at
    // the 25-legs, by nobody-but-30): verify no other centre lies within
    // 49 px of row 30's centre on the free axes first (pitch 96/78 makes
    // this hold by construction; the CHECK makes the premise explicit).
    const auto c = au::researchNodePos(tree, 30, 0, 0);
    for (const auto& nd : nodes) {
        if (nd.row == 30) continue;
        const auto o = au::researchNodePos(tree, nd.row, 0, 0);
        if (std::abs(o.x - c.x) <= 49 && std::abs(o.y - c.y) <= 49) {
            CHECK(!"neighbour premise broken for row probe");
        }
    }
    auto hitAt = [&](int dx, int dy) {
        return au::researchHit(tree, nodes, c.x + dx, c.y + dy, 0, 0);
    };
    // INCLUSIVE boundary: axis edges AND corners hit row 30. The corners
    // are the disc-vs-square discriminator (the r30 disc missed (24,24)).
    for (auto [dx, dy] : std::vector<std::pair<int, int>>{
             {24, 0}, {-24, 0}, {0, 24}, {0, -24},
             {24, 24}, {24, -24}, {-24, 24}, {-24, -24}}) {
        const auto h = hitAt(dx, dy);
        CHECK(h.kind == au::ResHit::Node);
        CHECK(h.row == 30);
    }
    // EXCLUSIVE at 25: the jle/jge legs reject at exactly 25, so row 30
    // must NEVER answer an axis probe at +-25.
    for (auto [dx, dy] : std::vector<std::pair<int, int>>{
             {25, 0}, {-25, 0}, {0, 25}, {0, -25}}) {
        const auto h = hitAt(dx, dy);
        CHECK(!(h.kind == au::ResHit::Node && h.row == 30));
    }
}
}  // namespace
