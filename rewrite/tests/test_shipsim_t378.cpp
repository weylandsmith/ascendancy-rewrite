// SPDX-License-Identifier: GPL-3.0-or-later

// t378 DESTINATION-TRIPLE ATOMICITY pins — ShipSim::issueDestination /
// clearDestination, the sim-level seam for the EMPTY-SPACE destination
// order (witness M3, docs/re/ships.md S64 + work/r1/t370_slot_events_all.txt
// re-read docs/re/_wip_t378.md S1).
// MEASURED PAIR (4 in-window issue frames: s16 00:15:29, s38 00:20:19,
//   s25 00:22:29, s18 00:24:49): order TYPE (+0x67) := 3 AND destination
//   triple (+0x6c) written IN ONE FRAME; kind (+0x58) stays 4 (NOT part of
//   the pair); prior type was 2/0/1/1 — no cited gate on prior type, none
//   imposed.
// MEASURED ORDER-END LEG (s14 Stainer 00:24:02): type 3->0 with trip :=
//   (0,0,0) SAME FRAME — both fields clear together.
// OBJECT ORDERS (type 1/2) never own +0x6c (every object swap frame shows
//   type+pay only, trip untouched): clearDestination refuses them.
// SENTINELS: unknown ship id -> false, state untouched (sim-level no-target
//   sentinel). The CITED 0xffff sentinel lives on the OWNER half at the
//   0x24a00 command-clear / 0x249b4 death finalizer (aicode.md:505, ships.md
//   L3 u32@+0x54 == 0xffff0000) — pinned by the death law in
//   test_shipsim_t364/test_shipsave_t360, NOT duplicated here; the order
//   fields themselves never read 0xffff in the corpus (honest negative,
//   _wip_t378 S2).
// CADENCE LAW: the two-click x/y-then-z testimony is CADENCE-BLIND
//   (adjacent XY->Z census = 0, S64) — NO two-step internal model exists
//   here and none may be inferred from these pins (pership-spec N8).
#include "game/shipsim.h"
#include "harness.h"

#include <cmath>
#include <vector>

namespace as = ascend::game;

namespace {

bool nearf(float a, float b) { return std::fabs(a - b) < 0.01f; }
bool tripIs(const float* t, float x, float y, float z) {
    return nearf(t[0], x) && nearf(t[1], y) && nearf(t[2], z);
}

as::SimStar mkStar(int id, float x, float y, float z) {
    as::SimStar s;
    s.id = id; s.pos[0] = x; s.pos[1] = y; s.pos[2] = z;
    return s;
}
as::Ship mkShip(int id, as::OrderKind k) {
    as::Ship s;
    s.id = id; s.owner = 0; s.kind = k;
    s.power = 100; s.powerMax = 100; s.driveStat = 10;
    return s;
}

}  // namespace

TEST(shipsim_issue_destination_atomic_pair_t378) {
    // The PAIR law: one call writes type 3 + the exact triple; kind is NOT
    // touched. Witness-valued: the four MEASURED M3 destination triples
    // round-trip exactly (all integer f32s).
    as::ShipSim sim(1);
    sim.addStar(mkStar(0, 0, 0, 0));
    struct W { int id; float x, y, z; };
    const W w[] = {
        {16, -1664.f, -1568.f,   64.f},   // s16 Erchamion 00:15:29
        {38,  -672.f,    32.f, -2112.f},  // s38 Ilmarinen 00:20:19
        {25,  -192.f,  1504.f, -1280.f},  // s25 Ipshitz   00:22:29
        {18,   608.f,    32.f,  -416.f},  // s18 Sparrowhawk 00:24:49
    };
    for (const auto& e : w) {
        auto s = mkShip(e.id, as::OrderKind::InSystem);
        s.orderType = 0;                      // pre-issue type (s38 shape)
        sim.addShip(s);
        CHECK(sim.issueDestination(e.id, e.x, e.y, e.z));
        as::Ship* p = sim.findShip(e.id);
        CHECK(p->orderType == 3);             // +0x67 := 3
        CHECK(tripIs(p->targetPos, e.x, e.y, e.z));   // +0x6c := dest
        CHECK(p->kind == as::OrderKind::InSystem);    // kind NOT in the pair
    }
}

TEST(shipsim_issue_destination_refusal_writes_nothing_t378) {
    // Refusal is TOTAL: no torn type-3-with-stale-triple state is reachable
    // through the seam. Kinds 1/2/5 are sticky in the decider (ai-dossier
    // §5) and kind != 4 fails the cited walk-guard family — refuse.
    as::ShipSim sim(1);
    sim.addStar(mkStar(0, 0, 0, 0));
    struct C { int id; as::OrderKind k; uint8_t t; float tx, ty, tz; };
    const C c[] = {
        {1, as::OrderKind::Move,       1, 100.f, 0.f, 0.f},
        {2, as::OrderKind::StarTarget, 2, 0.f,   0.f, 0.f},
        {3, as::OrderKind::Engage,     1, 0.f,   0.f, 0.f},
        {4, as::OrderKind::Placement,  5, 0.f,   0.f, 0.f},
    };
    for (const auto& e : c) {
        auto s = mkShip(e.id, e.k);
        s.orderType = e.t;
        s.targetPos[0] = 4.f; s.targetPos[1] = 5.f; s.targetPos[2] = 6.f;
        sim.addShip(s);
        CHECK(!sim.issueDestination(e.id, 9.f, 9.f, 9.f));
        as::Ship* p = sim.findShip(e.id);
        CHECK(p->orderType == e.t);           // unchanged
        CHECK(tripIs(p->targetPos, 4.f, 5.f, 6.f));   // unchanged
    }
    // No-target sentinel: an id the sim does not hold -> false (the cited
    // 0xffff order-field sentinel does NOT exist, _wip_t378 S2; the 0xffff
    // law lives on the owner half at death/clear, pinned in t364/t360).
    CHECK(!sim.issueDestination(999, 1.f, 0.f, 0.f));
    CHECK(sim.findShip(999) == nullptr);
}

TEST(shipsim_clear_destination_order_end_leg_t378) {
    // s14 00:24:02 shape: type 3->0 AND trip := (0,0,0) in one call.
    as::ShipSim sim(1);
    sim.addStar(mkStar(0, 0, 0, 0));
    auto s = mkShip(14, as::OrderKind::InSystem);
    s.orderType = 3;
    s.targetPos[0] = 352.f; s.targetPos[1] = -672.f; s.targetPos[2] = 800.f;
    sim.addShip(s);
    CHECK(sim.clearDestination(14));
    as::Ship* p = sim.findShip(14);
    CHECK(p->orderType == 0);
    CHECK(tripIs(p->targetPos, 0.f, 0.f, 0.f));

    // Object orders never own +0x6c: refuse, state untouched (s28/s34 swap
    // frames write type+pay only; the triple field is inert for them).
    auto o = mkShip(28, as::OrderKind::InSystem);
    o.orderType = 1;
    o.targetPos[0] = 7.f; o.targetPos[1] = 8.f; o.targetPos[2] = 9.f;
    sim.addShip(o);
    CHECK(!sim.clearDestination(28));
    CHECK(sim.findShip(28)->orderType == 1);
    CHECK(tripIs(sim.findShip(28)->targetPos, 7.f, 8.f, 9.f));
    auto o2 = mkShip(34, as::OrderKind::InSystem);
    o2.orderType = 2;
    sim.addShip(o2);
    CHECK(!sim.clearDestination(34));
    CHECK(sim.findShip(34)->orderType == 2);
    CHECK(!sim.clearDestination(999));        // sentinel
}

TEST(shipsim_executor_consumes_the_atomic_pair_t378) {
    // The executor's type-3 arm (S17 T1: abs triple at +0x6c) consumes
    // EXACTLY what the seam wrote: issue -> the boundary walks toward the
    // issued triple; clear -> silent (the Stainer order-end shape at the
    // frame level). A torn state (type 3, stale triple) cannot be produced
    // through the API, so the executor can never observe one.
    as::ShipSim sim(1);
    sim.addStar(mkStar(0, 0, 0, 0));
    auto s = mkShip(11, as::OrderKind::InSystem);
    s.pos[0] = 0; s.pos[1] = 0; s.pos[2] = 0;
    s.act = 2;
    sim.addShip(s);

    // Beyond reach: d = 3200/160 = 20 sugar > moves 10 -> partial walk.
    CHECK(sim.issueDestination(11, 3200.f, 0.f, 0.f));
    auto rep = sim.advanceBoundary();
    CHECK(rep.acted.size() == 1 && rep.acted[0] == 11);
    CHECK(nearf(sim.findShip(11)->pos[0], 1600.f));    // walked TOWARD target
    CHECK(sim.findShip(11)->power == 90);              // 10 steps burned
    CHECK(sim.findShip(11)->orderType == 3);           // order intact (not arrived)

    // Order-end leg: the pick law is ACT-driven (0x4134e family; clearing the
    // destination does NOT clear act — no cited law does), so the ship is
    // still picked, but the commit's type-0 arm reports 0 and walks NOTHING
    // (the Stainer order-end shape: type 3->0, trip 0, position inert).
    CHECK(sim.clearDestination(11));
    auto rep2 = sim.advanceBoundary();
    CHECK(rep2.acted.size() == 1 && rep2.acted[0] == 11);
    CHECK(nearf(sim.findShip(11)->pos[0], 1600.f));    // frozen at last pos
    CHECK(nearf(sim.findShip(11)->pos[1], 0.f));
    CHECK(nearf(sim.findShip(11)->pos[2], 0.f));
    CHECK(sim.findShip(11)->power == 100);   // refill only, zero steps burned
}
