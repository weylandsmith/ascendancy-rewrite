// SPDX-License-Identifier: GPL-3.0-or-later

// tRS-V1d THE VENDOR BLITTER ANCHOR LAW (seam TRSV1c-E CLOSED; law docs/re/
// _wip_tRSV1d.md P0-P2). The vendor passes the projected word to the shape
// blitter VERBATIM (research window 0x4849f/0x484a5: word[win+0x5f1/0x6b9]
// sar 16, no centring arithmetic anywhere in the caller), and FUN_0005caac
// composes the destination from the record's SIGNED BBOX:
//   dest_left = rec[+0x08] + passed_x ; dest_top = rec[+0x0c] + passed_y
//   dest_right = rec[+0x10] + passed_x ; dest_bottom = rec[+0x14] + passed_y
// (decompile work/combat_decomp/5caac.c lines 58-64; 0x5cf96 twin at
// 0x5d04b..0x5d057). The passed point is an ANCHOR, not a top-left.
// resring.shp's four records are MEASURED (-30,-30,29,29) => the ring
// content spans anchor-30..anchor+29 on both axes: it CENTRES on the anchor
// word by construction, so the vendor's drawn centre and hit centre share
// the word. Our blitShape draws its rect top-left at the blit point, so the
// port must blit at (x + rec.left, y + rec.top).
#include "formats/shp.h"
#include "ui/researchview.h"

#include <cstdio>
#include <fstream>
#include <sstream>
#include <string>

#include "harness.h"

#ifndef ASCENDANCY_SOURCE_DIR
#define ASCENDANCY_SOURCE_DIR "."
#endif

namespace {
namespace au = ascend::ui;
const std::string kRepo = ASCENDANCY_SOURCE_DIR;
}  // namespace

TEST(researchanchor_resring_centred_records_tRSV1d) {
    ascend::formats::ShapeLibrary lib;
    std::string err;
    if (!lib.load(kRepo + "/extracted/ascend01/data/resring.shp", &err)) {
        std::printf("  note: resring.shp unavailable (%s)\n", err.c_str());
        return;
    }
    CHECK(lib.count() == 4);
    for (int i = 0; i < lib.count(); ++i) {
        const auto& r = lib.record(i);
        // MEASURED bbox quad (-30,-30,29,29): dims 60x60 by the bbox-diff
        // law, and the dims are EVEN so the anchor sits on the content's
        // central 2x2 junction: L == -W/2, T == -H/2.
        CHECK(r.width == 60);
        CHECK(r.height == 60);
        CHECK(r.left == -int(r.width) / 2);
        CHECK(r.top == -int(r.height) / 2);
        // Drawn span under the port's top-left blit semantics at anchor
        // (x,y): [x-30, x+29] — the anchor is inside the content and the
        // centre offset is |(-30 + 29 + 1)/2| = 0 (the same half-pixel
        // quantisation the vendor has on a 60 px record).
        const int lo = int(r.left), hi = int(r.left) + int(r.width) - 1;
        CHECK(lo <= 0 && hi >= 0);
        CHECK(std::abs(lo + hi) <= 1);
    }
}

TEST(researchanchor_ui_wiring_uses_bbox_offset_tRSV1d) {
    // Source-text wiring pin (tngs_s29 precedent): the research-screen node
    // blit must use the record's bbox offset, never the dead 29x29 -14
    // constant. Reverting the fix fails this pin.
    std::ifstream f(kRepo + "/rewrite/src/ui/ui.cpp");
    std::stringstream ss;
    ss << f.rdbuf();
    const std::string src = ss.str();
    const size_t node = src.find("NODES: resring.shp");
    CHECK(node != std::string::npos);
    if (node == std::string::npos) return;
    // The block runs from the NODES comment to the clip-rect restore.
    const size_t end = src.find("SDL_RenderSetClipRect(ren, nullptr)", node);
    CHECK(end != std::string::npos);
    const std::string block = src.substr(node, end - node);
    CHECK(block.find("c.x + rr.left") != std::string::npos);
    CHECK(block.find("c.y + rr.top") != std::string::npos);
    CHECK(block.find("c.x - 14") == std::string::npos);
    CHECK(block.find("c.y - 14") == std::string::npos);
}

TEST(researchanchor_hit_and_draw_share_the_word_tRSV1d) {
    // The hit law (0x474fb..0x4752d, +-24 square) reads the SAME projected
    // words the draw passes to the blitter; under the anchor law the drawn
    // content centres on that word, so a click on the VISIBLE disk centre
    // must hit. Scenario: all rows Available, rest camera; the drawn centre
    // of row 2 (the t252 centre disk) is the anchor point, and researchHit
    // at exactly that pixel resolves row 2.
    std::string err;
    auto tree = ascend::game::ResearchTree::loadFromFile(
        kRepo + "/extracted/ascend00/restree.txt", err);
    if (tree.mainCount() != 66) { CHECK(tree.mainCount() == 66); return; }
    std::vector<au::TechNode> nodes;
    for (int r = 0; r < 66; ++r) {
        au::TechNode nd;
        nd.row = r;
        nd.state = au::TechNodeState::Available;
        nodes.push_back(nd);
    }
    const auto G = au::researchTreeGeometry(tree);
    const auto c = au::researchNodeScreen(G, nodes, 0, 0, au::ResCam{});
    CHECK(c[2].visible);
    const auto h = au::researchHit(tree, nodes, c[2].x, c[2].y, 0, 0);
    CHECK(h.kind == au::ResHit::Node);
    CHECK(h.row == 2);
}
