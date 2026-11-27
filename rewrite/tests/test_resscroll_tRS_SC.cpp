// tRS-SC — D32-L4 RESEARCH UP/DOWN BUTTONS SCROLL, NOT ZOOM (2026-11-27).
// Law docs/re/research.md S17 + docs/re/_wip_tRS-SC.md P0-P3:
//  * [win+0xe3] (camera position triplet cam+0x34 = win+0xdf/e3/e7, init
//    0x4710e-0x47123 x=0 y=0 z=-150) is POSITION Y; the MOVE pair pump
//    0x47cd0..0x47d12 fadds +-1.0*[0x9f108] into +0xe3 (NOT the depth
//    word +0xe7 — zero write sites there in the whole reswin window).
//  * The per-paint clamp 0x47ef1..0x47fc3 (draw fn 0x47eac): posY is
//    clamped to the Y-extent of the rows PASSING THE 0x46d3c DRAW SCOPE
//    (min/max seeded from row 0's world Y at win+0x147).
//  * Projection 0x53374 consumes vY = world.y - cam.y through the SAME
//    pinhole: rows slide, depth (vZ) is untouched by the scroll.
#include "harness.h"
#include "ui/researchview.h"

#include <cmath>
#include <cstdio>
#include <iterator>
#include <string>
#include <vector>

namespace au = ascend::ui;
using au::ResearchGeom;
using au::ResWorld;
using au::TechNode;
using au::TechNodeState;

namespace {
// A synthetic geometry: world Y spans [0, 90], rows 0..5.
ResearchGeom fixtureGeom(std::vector<TechNode>& nodes) {
    ResearchGeom G;
    G.depth = {0, 0, 1, 1, 2, 2};
    G.slot = {0, 1, 0, 1, 0, 1};
    G.esi = 3;
    G.C = {2, 2, 2};
    G.world.resize(6);
    for (int r = 0; r < 6; ++r) {
        G.world[size_t(r)].x = (r & 1) ? 23.0f : 4.0f;
        G.world[size_t(r)].y = float(15 * r);
        G.world[size_t(r)].z = (r & 1) ? -4.0f : 23.0f;
        TechNode nd;
        nd.row = r;
        nd.state = TechNodeState::Available;
        nodes.push_back(nd);
    }
    return G;
}
}  // namespace

TEST(scroll_field_role_tRS_SC) {
    // The MOVE pair moves posY only; posZ (depth) is NEVER pumped
    // (0x47d03/0x47d12 target [esi+0xe3] = position Y per the init triplet
    // 0x4710e-0x47123: the -150.0 immediate lands at eax+8 == win+0xe7).
    au::ResCam c;
    CHECK(c.posY == 0.0);
    CHECK(c.posZ == -150.0);
    c.pressMove(false);
    c.tick();
    CHECK(c.posY == -1.0);
    CHECK(c.posZ == -150.0);
    c.releaseMove();
    c.pressMove(true);
    for (int t = 0; t < 10; ++t) c.tick();
    CHECK(c.posY == 9.0);
    CHECK(c.posZ == -150.0);
    // The ROT pair never touches either position field (release the move
    // pair first — a latched MOVE keeps pumping posY by law).
    c.releaseMove();
    double y0 = c.posY, z0 = c.posZ;
    c.pressRot(false);
    c.tick();
    CHECK(c.posY == y0 && c.posZ == z0);
    CHECK(c.yawDeg == 3.0);
}

TEST(scroll_slides_rows_not_scale_tRS_SC) {
    // A scroll shifts projected Y through vY = world.y - posY and leaves
    // the camera-space depth z2 EXACTLY invariant (a dolly would change
    // z2 and scale X too — the pre-fix defect).
    std::vector<TechNode> nodes;
    const auto G = fixtureGeom(nodes);
    const auto rest = au::researchNodeScreen(G, nodes, 0, 0, au::ResCam{});
    au::ResCam up;
    up.posY = 20.0;  // camera up => rows project HIGHER (smaller y)
    const auto sUp = au::researchNodeScreen(G, nodes, 0, 0, up);
    au::ResCam dn;
    dn.posY = -20.0;
    const auto sDn = au::researchNodeScreen(G, nodes, 0, 0, dn);
    for (size_t i = 0; i < nodes.size(); ++i) {
        CHECK(sUp[i].z2 == rest[i].z2);
        CHECK(sDn[i].z2 == rest[i].z2);
        // X is a function of (vX, vZ) only — a scroll must not move it.
        CHECK(sUp[i].x == rest[i].x);
        CHECK(sDn[i].x == rest[i].x);
        CHECK(sUp[i].y < rest[i].y);
        CHECK(sDn[i].y > rest[i].y);
    }
}

TEST(scroll_clamp_law_tRS_SC) {
    // 0x47ef1..0x47fc3: min/max over the DRAW SCOPE (non-Blocked rows),
    // seeded from row 0's world Y; posY clamped into [min, max].
    std::vector<TechNode> nodes;
    const auto G = fixtureGeom(nodes);  // Y range [0, 75]
    CHECK(au::resClampPosY(G, nodes, 0.0) == 0.0);
    CHECK(au::resClampPosY(G, nodes, 40.0) == 40.0);
    CHECK(au::resClampPosY(G, nodes, 75.0) == 75.0);
    CHECK(au::resClampPosY(G, nodes, 76.0) == 75.0);
    CHECK(au::resClampPosY(G, nodes, 1e15) == 75.0);   // 0x47a7a idiom
    CHECK(au::resClampPosY(G, nodes, -100.0) == 0.0);  // 0x47a53 idiom
    // The scope gate: block the two extreme rows and the UPPER bound
    // shrinks to the frontier (visible rows 1..4: top Y 60). The SEED law
    // (0x47ef1 seeds BOTH min and max from row 0's Y, win+0x147, whether or
    // not row 0 passes scope) keeps the LOWER bound at row 0's Y=0 — the
    // vendor clamps with a stale seed, faithfully ported.
    nodes[0].state = TechNodeState::Blocked;
    nodes[5].state = TechNodeState::Blocked;
    CHECK(au::resClampPosY(G, nodes, 100.0) == 60.0);
    CHECK(au::resClampPosY(G, nodes, -100.0) == 0.0);  // seed law
    // Owned rows are IN scope (0x46d3c is the frontier predicate; owned
    // rows pass — research.md S8e): blocking is the only exclusion.
    nodes[0].state = TechNodeState::Owned;
    CHECK(au::resClampPosY(G, nodes, -100.0) == 0.0);
}

TEST(scroll_clamp_wired_painter_tRS_SC) {
    // Source law: the PAINT path clamps resCam.posY through resClampPosY
    // before projecting (the vendor clamp runs inside the draw fn, before
    // 0x53374 writes the words the hit sub consumes). Anchor on the
    // STATEMENT itself, comments excluded (tESC-1/tSPEC-1 law).
    const char* path = "src/ui/ui.cpp";
    FILE* f = fopen(path, "rb");
    if (!f) path = "../src/ui/ui.cpp", f = fopen(path, "rb");
    if (!f) path = "rewrite/src/ui/ui.cpp";
    f = fopen(path, "rb");
    CHECK(f != nullptr);
    if (!f) return;
    std::string src;
    {
        fseek(f, 0, SEEK_END);
        const long n = ftell(f);
        fseek(f, 0, SEEK_SET);
        src.resize(size_t(n > 0 ? n : 0));
        if (n > 0 && fread(src.data(), 1, size_t(n), f) != size_t(n))
            src.clear();
    }
    fclose(f);
    const std::string needle =
        "resCam.posY = resClampPosY(resGeom, nodes, resCam.posY);";
    const size_t at = src.find(needle);
    CHECK(at != std::string::npos);
    if (at == std::string::npos) return;
    // Not inside a comment: the line containing it must not start with //.
    const size_t bol = src.rfind('\n', at);
    const std::string line = src.substr(bol + 1, at - bol - 1);
    CHECK(line.find("//") == std::string::npos);
    // And it runs BEFORE the projection pass (researchNodeScreen call).
    CHECK(src.find("researchNodeScreen(", at) != std::string::npos);
    CHECK(src.compare(at, needle.size(), needle) == 0);
}
