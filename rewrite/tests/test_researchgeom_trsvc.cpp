// SPDX-License-Identifier: GPL-3.0-or-later

// tRS-V1c THE VENDOR TREE GEOMETRY pins (law docs/re/_wip_tRSV1.md P1-P12,
// research.md S8/S8-CORRECTION). Replaces the t419 grid/rest-equality pins
// (that law is superseded: the vendor tree is a chain of circles seen
// through a 7-9x perspective window, not a flat grid at scale 1).
//
//   1. C[k] census + esi (MEASURED replay of the P1b/P1c law on the shipped
//      restree.txt — the SAME table tRS-V1 measured independently).
//   2. Worked world triples: column 0 (R0=23, d=3), column 8 (R0=23, d=2),
//      column 15 (odd-k C=3 -> R0=4 then 23, d=2 open circle).
//   3. 0x76e08 chop rounding asymmetry (trunc toward zero, NOT round-away).
//   4. SCOPE law: Blocked rows are neither visible nor hittable (0x46d3c).
//   5. dat_764c4 latch transition table + pump deltas (+-3 deg, +-1 dolly).
//   6. Frame esi law (0x483fa..0x48470) + edge colour index law (P11).
#include "ui/researchview.h"

#include <cmath>
#include <cstdio>
#include <string>
#include <vector>

#include "game/research.h"
#include "harness.h"

#ifndef ASCENDANCY_SOURCE_DIR
#define ASCENDANCY_SOURCE_DIR "."
#endif

namespace {
namespace au = ascend::ui;
namespace ag = ascend::game;
const std::string kRepo = ASCENDANCY_SOURCE_DIR;

ag::ResearchTree loadedTree() {
    std::string err;
    return ag::ResearchTree::loadFromFile(kRepo + "/extracted/ascend00/restree.txt", err);
}
}  // namespace

TEST(researchgeom_ctable_esi_trsvc) {
    auto tree = loadedTree();
    if (tree.mainCount() != 66) { CHECK(tree.mainCount() == 66); return; }
    const auto G = au::researchTreeGeometry(tree);
    // MEASURED (tRS-V1 replay + this iteration's independent replay):
    const std::vector<int> kC = {3, 4, 3, 5, 6, 5, 3, 4, 2, 4, 4, 4, 4, 4, 5,
                                 3, 2, 1};
    CHECK(G.esi == 18);
    CHECK(G.C == kC);
    int sum = 0;
    for (int c : G.C) sum += c;
    CHECK(sum == 66);
    // Slots are 0..C[k]-1 per column, file order (the vendor inner loop).
    std::vector<int> seen(size_t(G.esi), 0);
    for (int r = 0; r < 66; ++r) {
        CHECK(G.slot[r] >= 0 && G.slot[r] < G.C[size_t(G.depth[r])]);
        if (G.slot[r] == 0) seen[size_t(G.depth[r])] = 1;
    }
    for (int k = 0; k < G.esi; ++k) CHECK(seen[size_t(k)] == 1);
    // Every circle point has radius 23 except first-node radii {23,4}:
    for (int r = 0; r < 66; ++r) {
        const double rad = std::sqrt(double(G.world[r].x) * G.world[r].x +
                                     double(G.world[r].z) * G.world[r].z);
        const bool first = G.slot[r] == 0;
        CHECK(std::fabs(rad - 23.0) < 1e-3 ||
              (first && std::fabs(rad - 4.0) < 1e-3));
    }
}

TEST(researchgeom_worked_columns_trsvc) {
    auto tree = loadedTree();
    if (tree.mainCount() != 66) { CHECK(tree.mainCount() == 66); return; }
    const auto G = au::researchTreeGeometry(tree);
    auto near = [](float a, double b) { return std::fabs(double(a) - b) < 0.02; };
    // COLUMN 0: three ROOTS (rows 0, 2, 6 in FILE order — row 1 has prereq
    // 0 so it sits at depth 1), R0=23 d=3, acc 240/360/480 deg.
    // 23*sin(240)=-19.919, 23*cos(240)=-11.5.
    CHECK(G.depth[0] == 0 && G.slot[0] == 0);
    CHECK(near(G.world[0].x, -19.9186));
    CHECK(near(G.world[0].y, 0.0));
    CHECK(near(G.world[0].z, -11.5));
    CHECK(G.depth[1] == 1);            // prereq 0 -> depth 1
    CHECK(G.depth[2] == 0 && G.slot[2] == 1);
    CHECK(near(G.world[2].y, 15.0));   // Y = 30k + 15*(i&1)
    CHECK(near(G.world[2].x, -0.0) || near(std::fabs(G.world[2].x), 0.0));
    CHECK(near(G.world[2].z, 23.0));   // acc 360: sin~0, cos=23
    CHECK(G.depth[6] == 0 && G.slot[6] == 2);
    CHECK(near(G.world[6].y, 0.0));
    CHECK(near(G.world[6].x, 19.9186));  // acc 480 = 120 mod 360
    // COLUMN 8 (k even, C=2): R0=23, d=2 -> 180 deg apart. Rows 28, 36.
    CHECK(G.depth[28] == 8 && G.slot[28] == 0);
    CHECK(near(G.world[28].x, 19.9186));
    CHECK(near(G.world[28].y, 240.0));
    CHECK(near(G.world[28].z, -11.5));
    CHECK(G.depth[36] == 8 && G.slot[36] == 1);
    CHECK(near(G.world[36].x, -19.9186));
    CHECK(near(G.world[36].y, 255.0));
    CHECK(near(G.world[36].z, 11.5));
    // COLUMN 15 (k ODD, C=3 > 2): R0=4 for node 0 then 23; d = C-1 = 2
    // (open circle — the vendor quirk). Rows 54, 55, 60.
    CHECK(G.depth[54] == 15 && G.slot[54] == 0);
    CHECK(near(G.world[54].x, -2.0));   // 4*sin(450)=4*1? acc0=240+450=690
    CHECK(near(G.world[54].z, 3.4641)); // 4*cos(690)=4*cos(330)
    CHECK(G.depth[55] == 15 && G.slot[55] == 1);
    CHECK(near(G.world[55].x, 11.5));   // 23*sin(870)=23*sin(150)=11.5
    CHECK(near(G.world[55].z, -19.9186));
    CHECK(G.depth[60] == 15 && G.slot[60] == 2);
    CHECK(near(G.world[60].x, -11.5));  // acc 1050 = 30 mod 360 -> -sin? 
    CHECK(near(G.world[60].z, 19.9186));
}

TEST(researchgeom_chop_rounding_trsvc) {
    // 0x76e08: frndint with RC=chop == trunc TOWARD ZERO (P10). With the
    // +0.5 bias the vendor rounds positives to nearest but chops negatives
    // asymmetrically. The discriminator vs round-half-away: v = -2.7.
    CHECK(au::resVendorRound(-2.7) == -2);   // NOT -3
    CHECK(au::resVendorRound(2.7) == 2);     // trunc(2.7)
    CHECK(au::resVendorRound(2.5 + 0.0) == 2);
    CHECK(au::resVendorRound(-0.5) == 0);
    CHECK(au::resVendorRound(0.0) == 0);
    // Focal law (0x203e4): 320/tan(15deg) = 1194.2562 in f64. (The law
    // docs cite "1194.19" — that is the f32-tan value the vendor's x87
    // path lands on; the f64 difference is 0.065 px at z=150, sub-pixel.)
    CHECK(std::fabs(au::resFocal() - 1194.2562) < 0.001);
}

TEST(researchgeom_scope_law_trsvc) {
    // THE SCOPE GATE (0x46d3c via 0x48566 draw + 0x474fb hit): BLOCKED rows
    // are neither drawn nor hittable. Scenario: all Available EXCEPT one
    // Blocked row placed at a busy centre — clicking that centre must never
    // resolve the Blocked row.
    auto tree = loadedTree();
    if (tree.mainCount() != 66) { CHECK(tree.mainCount() == 66); return; }
    std::vector<au::TechNode> nodes;
    for (int r = 0; r < 66; ++r) {
        au::TechNode nd;
        nd.row = r;
        nd.state = au::TechNodeState::Available;
        nodes.push_back(nd);
    }
    const auto G = au::researchTreeGeometry(tree);
    const auto rest = au::researchNodeScreen(G, nodes, 0, 0, au::ResCam{});
    // At rest exactly THREE disks land inside the RESWIN rect 7..476 x
    // 46..472 (rows 0, 2, 6 — the t252 "three disks" corroboration).
    int visible = 0;
    for (int r = 0; r < 66; ++r)
        if (rest[r].visible && rest[r].x >= 7 && rest[r].x <= 476 &&
            rest[r].y >= 46 && rest[r].y <= 472)
            ++visible;
    CHECK(visible == 3);
    // Blocked row 30 (centre (251,2440)): not legal, not visible.
    nodes[30].state = au::TechNodeState::Blocked;
    const auto s2 = au::researchNodeScreen(G, nodes, 0, 0, au::ResCam{});
    CHECK(!s2[30].legal);
    CHECK(!s2[30].visible);
    // A click at row 2's centre (235,344) hits row 2 while all-visible...
    auto h = au::researchHit(tree, nodes, 235, 344, 0, 0);
    CHECK(h.kind == au::ResHit::Node);
    CHECK(h.row == 2);
    // ... and NEVER a Blocked row: block EVERY row whose +-24 box touches
    // row 2's centre except row 2 itself; the hit must still resolve row 2.
    for (auto& nd : nodes) {
        if (nd.row == 2) continue;
        const auto& c = s2[size_t(nd.row)];
        if (c.visible && std::abs(c.x - 235) <= 49 &&
            std::abs(c.y - 344) <= 49)
            nd.state = au::TechNodeState::Blocked;
    }
    h = au::researchHit(tree, nodes, 235, 344, 0, 0);
    CHECK(h.kind == au::ResHit::Node && h.row == 2);
    // Now block row 2 too: the same point resolves ONLY another still-legal
    // overlapping row or nothing — never row 2.
    nodes[2].state = au::TechNodeState::Blocked;
    h = au::researchHit(tree, nodes, 235, 344, 0, 0);
    CHECK(!(h.kind == au::ResHit::Node && h.row == 2));
}

TEST(researchgeom_scan_order_trsvc) {
    // HIGH->low FIRST-hit law (SELECT sub 0x47478 walks the row list
    // downward): find an OVERLAPPING pair (lower row r, higher row q with
    // centres within the +-24 box), click q's centre — the scan meets q
    // first, so q wins even though r also contains the point. A low->high
    // scan would answer r. (Overlaps are observable only under the vendor
    // perspective law — the old grid was non-overlapping by construction.)
    auto tree = loadedTree();
    if (tree.mainCount() != 66) { CHECK(tree.mainCount() == 66); return; }
    std::vector<au::TechNode> nodes;
    for (int r = 0; r < 66; ++r) {
        au::TechNode nd;
        nd.row = r;
        nd.state = au::TechNodeState::Available;
        nodes.push_back(nd);
    }
    const auto G = au::researchTreeGeometry(tree);
    // At REST the 66 centres are mutually >24 px apart (measured); an
    // overlap appears under yaw — at yaw 45 rows 64/65 collide (measured
    // replay). Drive the camera there with the latched pump law itself.
    au::ResCam cam;
    cam.pressRot(false);  // (1,0) => +3 deg/tick
    for (int t = 0; t < 15; ++t) cam.tick();  // yaw = +45
    CHECK(std::fabs(cam.yawDeg - 45.0) < 1e-9);
    const auto c = au::researchNodeScreen(G, nodes, 0, 0, cam);
    int lo = -1, hi = -1;
    for (int q = 0; q < 66 && hi < 0; ++q) {
        if (!c[q].visible) continue;
        for (int r = 0; r < q; ++r) {
            if (!c[r].visible) continue;
            if (std::abs(c[q].x - c[r].x) <= 24 &&
                std::abs(c[q].y - c[r].y) <= 24) { lo = r; hi = q; break; }
        }
    }
    CHECK(hi >= 0);  // yaw -45 MUST contain an overlap (else the geometry
                     // changed and this pin needs re-derivation)
    if (hi < 0) return;
    // Click LO's centre: it is inside BOTH boxes, so the scan direction is
    // the discriminator — high->low meets hi first (vendor answer hi); a
    // low->high scan would answer lo. (Mutation-verified: flipping the
    // researchHit loop fails exactly this CHECK.)
    const auto h = au::researchHit(tree, nodes, c[lo].x, c[lo].y, 0, 0, cam);
    CHECK(h.kind == au::ResHit::Node);
    CHECK(h.row == hi);  // NOT lo
}

TEST(researchgeom_latch_pump_trsvc) {
    // dat_764c4 transition table (0x47b44..0x47c42, P11). Encoding:
    // 0=(0,0) 1=(1,0) 2=(1,1) 3=(0,1).
    CHECK(au::ResCam::pressPair(0, false) == 1);
    CHECK(au::ResCam::pressPair(1, false) == 0);
    CHECK(au::ResCam::pressPair(2, false) == 3);
    CHECK(au::ResCam::pressPair(3, false) == 1);
    CHECK(au::ResCam::pressPair(0, true) == 2);
    CHECK(au::ResCam::pressPair(1, true) == 2);
    CHECK(au::ResCam::pressPair(2, true) == 1);
    CHECK(au::ResCam::pressPair(3, true) == 2);
    // Pump deltas (0x47c88/0x47cdb): rot +3/-3 deg, dolly -1/+1.
    au::ResCam cam;
    cam.pressRot(false);   // (1,0)
    CHECK(cam.moving());
    cam.tick();
    CHECK(std::fabs(cam.yawDeg - 3.0) < 1e-9);
    cam.pressRot(true);    // (1,1)
    cam.tick();
    CHECK(std::fabs(cam.yawDeg - 0.0) < 1e-9);  // +3 then -3
    cam.pressRot(false);   // (1,1)->(0,1) DEAD
    CHECK(cam.latchRot == 3);
    cam.tick();
    CHECK(std::fabs(cam.yawDeg - 0.0) < 1e-9);  // DEAD pumps nothing
    // Dolly: MOVEUP (pair A) => posZ -= 1 (camera backs away, tree SHRINKS;
    // the fadd chain 0x47d03..0x47d12 is the authority, _wip P12 note).
    au::ResCam d;
    d.pressMove(false);
    d.tick();
    CHECK(std::fabs(d.posZ - (-151.0)) < 1e-9);
    d.pressMove(true);     // (1,1) => +1 per tick
    d.tick();
    CHECK(std::fabs(d.posZ - (-150.0)) < 1e-9);
    // The dolly is OBSERVABLE through the projection: scale grows as the
    // camera nears the tree plane (posZ -> 0-).
    auto tree = loadedTree();
    if (tree.mainCount() != 66) { CHECK(tree.mainCount() == 66); return; }
    std::vector<au::TechNode> nodes;
    for (int r = 0; r < 66; ++r) {
        au::TechNode nd;
        nd.row = r;
        nd.state = au::TechNodeState::Available;
        nodes.push_back(nd);
    }
    const auto G = au::researchTreeGeometry(tree);
    au::ResCam nearCam;
    nearCam.posZ = -140.0;
    const auto far = au::researchNodeScreen(G, nodes, 0, 0, au::ResCam{});
    const auto nn = au::researchNodeScreen(G, nodes, 0, 0, nearCam);
    // Row 0's world X is negative: nearer camera spreads it further out.
    CHECK(nn[0].x < far[0].x);
}

TEST(researchgeom_frame_edge_laws_trsvc) {
    // Frame esi law (0x483fa..0x48470): 1 default; 0 studied-unowned; 3
    // owned; 2 selected overrides.
    CHECK(au::resNodeFrame(5, false, false, false) == 1);
    CHECK(au::resNodeFrame(5, true, false, false) == 0);
    CHECK(au::resNodeFrame(5, false, true, false) == 3);
    CHECK(au::resNodeFrame(5, true, true, false) == 3);
    CHECK(au::resNodeFrame(5, false, true, true) == 2);
    CHECK(au::resNodeFrame(5, false, false, true) == 2);
    // Edge colour (P11 corrected): 0x6b - clamp(chop(0.25*(0.5*(zt+zp)+posz)),
    // -3, +3). At rest posz=-150, depths ~[127,173]: equal depths give k=0.
    CHECK(au::resEdgeColorIndex(150.0, 150.0, -150.0) == 0x6b - 0);
    // 0.5*(154+154) - 150 = 4; x0.25 = 1.0 -> k=1. (0.65 would chop to 0 —
    // the chop-vs-round boundary is the point of this pin.)
    CHECK(au::resEdgeColorIndex(154.0, 154.0, -150.0) == 0x6b - 1);
    CHECK(au::resEdgeColorIndex(153.8, 153.8, -150.0) == 0x6b - 0);
    CHECK(au::resEdgeColorIndex(173.0, 173.0, -150.0) == 0x6b - 3);  // clamped
    CHECK(au::resEdgeColorIndex(127.0, 127.0, -150.0) == 0x6b + 3);  // clamped
}
