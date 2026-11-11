// SPDX-License-Identifier: GPL-3.0-or-later

// t362 MIXED-FLEET DEPARTURE LAW pins — the executor DRIVER repeat
// (FUN_0002547c 0x2550c..0x25527: re-run the whole per-race pass while any
// race reports work) and the commit-exit return law (FUN_00041260 tail
// 0x41b8f..0x41ba6: work iff remaining walk > 0). Law sources:
// docs/re/_wip_t362.md S4/S6/S7 (verbatim disasm, work/r331_disasm.txt),
// witness census work/r362_witness.out B2 (3 same-owner kind flips in ONE
// boundary, owners 1 and 2 — piecemeal departure fired in the vendor).
// Mutation-campaign mandates (ships.md S60): power-clamp-operand path and
// march-spends-NEITHER, both pinned here. NO OQ row closes on these facts.
#include "game/shipsim.h"
#include "harness.h"

#include <cmath>
#include <vector>

namespace as = ascend::game;

namespace {

constexpr float kEps = 1e-3f;
bool nearf(float a, float b) { return std::fabs(a - b) < kEps; }

as::SimStar mkStar(int id, float x, float y, float z) {
    as::SimStar s;
    s.id = id; s.pos[0] = x; s.pos[1] = y; s.pos[2] = z;
    return s;
}
as::SimLane mkLane(int id, int a, int b, float len, bool third = false) {
    as::SimLane l;
    l.id = id; l.a = a; l.b = b; l.len = len; l.thirdSpeed = third;
    return l;
}
as::Ship mkShip(int id, int owner, as::OrderKind k) {
    as::Ship s;
    s.id = id; s.owner = owner; s.kind = k;
    return s;
}

}  // namespace

TEST(shipsim_piecemeal_departure_t362) {
    // Three same-owner queued ships, all act set, targets 1 sugar away
    // (early arrival with moves left -> commit exit reports work). Driver
    // repeat: ONE pick per sweep, MIN POWER first, until the race reports
    // silent. This is the piecemeal-departure shape of the corpus witness
    // (work/r362_witness.out B2: slots 17/20/29 flipping in one boundary).
    as::ShipSim sim(1);
    sim.addStar(mkStar(0, 0, 0, 0));
    auto mk = [&](int id, int x, int pm) {
        auto s = mkShip(id, 0, as::OrderKind::InSystem);
        s.pos[0] = static_cast<float>(x);
        s.targetPos[0] = static_cast<float>(x + 160);   // d = 1 sugar
        s.act = 2; s.orderType = 1;
        s.driveStat = 10; s.powerMax = pm;              // refill delta 0 -> power pm
        sim.addShip(s);
    };
    mk(10, 0, 30);      // richest
    mk(20, 3200, 20);
    mk(30, 6400, 10);   // poorest -> departs FIRST (S17 T4 MIN, strict <)

    auto rep = sim.advanceBoundary();
    CHECK(rep.acted.size() == 3);
    if (rep.acted.size() == 3) {
        CHECK(rep.acted[0] == 30);          // ascending-POWER departure order
        CHECK(rep.acted[1] == 20);          // is the piecemeal law, verbatim
        CHECK(rep.acted[2] == 10);
    }
    CHECK(rep.sweeps == 4);                 // 3 work sweeps + 1 silent drain
    CHECK(!rep.executorStalled);
    CHECK(rep.asserts == 0);
    CHECK(rep.landed.size() == 3);          // all arrive (orderType 1, T-6)
    // Each ship burned exactly 1 step; MOVES re-grant per sweep made the
    // remaining word 9 at every commit exit (status work).
    CHECK(sim.findShip(10)->power == 29);
    CHECK(sim.findShip(20)->power == 19);
    CHECK(sim.findShip(30)->power == 9);
    CHECK(sim.findShip(10)->act == 0);      // orders CONSUMED at landing
    // The next boundary is silent: no re-departure (S24 dwell stasis).
    auto rep2 = sim.advanceBoundary();
    CHECK(rep2.acted.empty());
    CHECK(rep2.sweeps == 1);
}

TEST(shipsim_sweep_stops_on_exhausted_budget_t362) {
    // Commit exit 0x41b9b: work is reported iff REMAINING > 0. A ship that
    // spends its FULL moves budget (target beyond reach: walk == moves ->
    // remaining 0) reports 0 -> NO second sweep this boundary; it continues
    // next boundary on the refill.
    as::ShipSim sim(1);
    sim.addStar(mkStar(0, 0, 0, 0));
    auto s = mkShip(11, 0, as::OrderKind::InSystem);
    s.pos[0] = 0; s.targetPos[0] = 3200;     // d = 20 sugar > moves 10
    s.act = 2; s.orderType = 1;
    s.driveStat = 10; s.powerMax = 100;
    sim.addShip(s);
    auto rep = sim.advanceBoundary();
    CHECK(rep.acted.size() == 1);
    CHECK(rep.sweeps == 1);                  // remaining 0 -> no repeat
    CHECK(nearf(sim.findShip(11)->pos[0], 1600.f));   // walked 10 sugar
    CHECK(sim.findShip(11)->power == 90);
    CHECK(sim.findShip(11)->moves == 0);     // full budget spent
    auto rep2 = sim.advanceBoundary();       // next boundary continues
    CHECK(rep2.acted.size() == 1 && rep2.landed.size() == 1);
    CHECK(sim.findShip(11)->act == 0);
}

TEST(shipsim_sweep_power_gate_noop_sweep_t362) {
    // POWER clamp to 0 mid-sweep, target NOT reached: the commit reports work
    // (remaining 9 > 0), the driver re-runs the pass, the re-pick finds the
    // ship POWER-gated (0x4134e cmpl $0x0,+0x88; jle) -> silent sweep, then
    // drain. One acted entry, TWO sweeps, no state from the no-op sweep.
    as::ShipSim sim(1);
    sim.addStar(mkStar(0, 0, 0, 0));
    auto s = mkShip(12, 0, as::OrderKind::InSystem);
    s.pos[0] = 0; s.targetPos[0] = 320;      // d = 2 sugar, moves 10
    s.act = 2; s.orderType = 1;
    s.driveStat = 10; s.powerMax = 1;        // power 1 < steps 2 -> clamp
    sim.addShip(s);
    auto rep = sim.advanceBoundary();
    CHECK(rep.acted.size() == 1 && rep.acted[0] == 12);
    CHECK(rep.sweeps == 2);                  // work sweep + gated silent sweep
    CHECK(!rep.executorStalled);
    CHECK(sim.findShip(12)->power == 0);     // clamp: steps := power (1)
    CHECK(nearf(sim.findShip(12)->pos[0], 160.f));  // walk 2*1/2 = 1 sugar
    // MOVES is 10 again, NOT the remaining 9: the silent sweep still ran the
    // prologue re-grant (0x412cf is unconditional inside every executor
    // invocation, and the driver re-invokes it) — the remaining word is a
    // commit-exit status only, not durable state across a re-grant.
    CHECK(sim.findShip(12)->moves == 10);
    CHECK(sim.findShip(12)->act == 2);       // NOT arrived: order kept
}

TEST(shipsim_dwell_suppress_across_sweeps_t362) {
    // T-10 hoist: the decrement runs ONCE per boundary AFTER all sweeps read
    // the words — a multi-sweep boundary must not re-decrement, and a dwelling
    // ship must stay suppressed while its sibling fleet departs piecemeal.
    as::ShipSim sim(1);
    sim.addStar(mkStar(0, 0, 0, 0));
    auto q = mkShip(13, 0, as::OrderKind::InSystem);
    q.pos[0] = 0; q.targetPos[0] = 160; q.act = 2; q.orderType = 1;
    q.driveStat = 10; q.powerMax = 5; q.dwellTurns = 2;
    sim.addShip(q);
    auto f = mkShip(14, 0, as::OrderKind::InSystem);   // fleet mate, no dwell
    f.pos[0] = 3200; f.targetPos[0] = 3360; f.act = 2; f.orderType = 1;
    f.driveStat = 10; f.powerMax = 8;
    sim.addShip(f);

    auto r1 = sim.advanceBoundary();
    CHECK(r1.acted.size() == 1 && r1.acted[0] == 14);  // dweller suppressed;
    CHECK(r1.landed.size() == 1);                      // mate arrives (power
    CHECK(sim.totalRngDraws() == 3);                   // 8 >= 1 step)
    CHECK(sim.findShip(13)->dwellTurns == 1);          // decremented ONCE
    CHECK(nearf(sim.findShip(13)->pos[0], 0.f));       // never moved
    auto r2 = sim.advanceBoundary();
    CHECK(r2.acted.empty());                           // mate's act consumed
    CHECK(sim.findShip(13)->dwellTurns == 0);          // ONCE again
    auto r3 = sim.advanceBoundary();
    CHECK(r3.acted.size() == 1 && r3.acted[0] == 13);  // dweller fires on expiry
    CHECK(r3.landed.size() == 1);
    CHECK(sim.totalRngDraws() == 6);                   // two scatter triples
}

TEST(shipsim_march_spends_neither_t362) {
    // MUTANT MANDATE (ships.md S60): the T-7 march decrements NEITHER MOVES
    // nor POWER (MEASURED-negative S21 item 1). Invisible at boundary
    // observation (per-sweep re-grant overwrites +0x94 before any read,
    // exactly as the vendor's 0x412cf), so pinned at the seam itself.
    as::ShipSim sim(7);
    sim.addStar(mkStar(0, 0, 0, 0));
    sim.addStar(mkStar(1, 5120, 0, 0));
    sim.addLane(mkLane(0, 0, 1, 100));
    auto s = mkShip(15, 0, as::OrderKind::Placement);
    s.laneId = 0; s.laneStepX = 14; s.laneStepZ = 0;
    s.moves = 5; s.power = 7;
    as::BoundaryReport rep;
    sim.laneMarch(s, rep);
    CHECK(nearf(s.laneX, 14.f));
    CHECK(s.moves == 5);                     // march did NOT spend MOVES
    CHECK(s.power == 7);                     // march did NOT spend POWER
    CHECK(s.kind == as::OrderKind::Placement);
    CHECK(rep.placed.empty());
    // Third-speed lane: step *= 1/3 (pool word MEASURED, S22 L1).
    sim.addLane(mkLane(1, 0, 1, 100, true));
    auto t = mkShip(16, 0, as::OrderKind::Placement);
    t.laneId = 1; t.laneStepX = 30; t.moves = 4; t.power = 4;
    as::BoundaryReport rep2;
    sim.laneMarch(t, rep2);
    CHECK(nearf(t.laneX, 10.f));
    CHECK(t.moves == 4 && t.power == 4);
}

TEST(shipsim_power_clamp_operand_t362) {
    // MUTANT MANDATE (ships.md S60): the clamp fires on `power < STEPS`, not
    // `power < walk`. Non-integer walk forces the difference observable:
    // d = 416 world = 2.6 sugar, moves 10 -> walk 2.6, steps = x86round(2.6)
    // = 3; power 2 < 3 -> walk = 2.6*2/3 = 1.73333, steps = 2. The mutant
    // (operand walk: 2 < 2.6 fires but scales walk *= power/walk = 2/2.6 ->
    // walk 2.0) lands pos 320, NOT 277.333 — this pin separates the readings.
    float pos[3] = {0, 0, 0};
    const float delta[3] = {416, 0, 0};
    int32_t power = 2, moves = 10;
    bool arrived = true;
    const int32_t steps = as::ShipSim::walkLaw(pos, &power, &moves, delta, &arrived);
    CHECK(steps == 2);
    CHECK(!arrived);
    CHECK(nearf(pos[0], 277.33333f));        // 1.73333 sugar * 160
    CHECK(power == 0);                       // steps := power, burned
    CHECK(moves == 8);                       // round(10 - 1.73333) = round(8.26667)
    // Guard side: power >= steps -> NO scale (d=320 world = 2 sugar, steps 2).
    float pos2[3] = {0, 0, 0};
    const float delta2[3] = {320, 0, 0};
    int32_t p2 = 2, m2 = 10;
    bool a2 = false;
    CHECK(as::ShipSim::walkLaw(pos2, &p2, &m2, delta2, &a2) == 2);
    CHECK(a2 && nearf(pos2[0], 320.f) && p2 == 0 && m2 == 8);
}

TEST(shipsim_driver_stall_cap_neg_t362) {
    // Safety cap must never fire on legal states: a fleet that drains to
    // zero POWER across sweeps terminates by the 0x4134e gate, not the cap.
    as::ShipSim sim(3);
    sim.addStar(mkStar(0, 0, 0, 0));
    for (int i = 0; i < 6; ++i) {
        auto s = mkShip(20 + i, 0, as::OrderKind::InSystem);
        s.pos[0] = static_cast<float>(i * 6400);
        s.targetPos[0] = static_cast<float>(i * 6400 + 320);   // d = 2 sugar
        s.act = 2; s.orderType = 1;
        s.driveStat = 2; s.powerMax = 1;      // clamp to steps==1 each walk
        sim.addShip(s);
    }
    // Each ship walks 1 sugar per boundary (clamp steps:=power==1), so a
    // 2-sugar trip takes TWO boundaries: day 1 six piecemeal walks (six
    // sweeps, one ship each, ascending slot on the all-tied power), day 2 six
    // arrivals, days 3+ silent. Termination is the 0x4134e POWER gate and the
    // act-consumption law, never the cap.
    int totalActs = 0;
    for (int day = 0; day < 6; ++day) {
        auto rep = sim.advanceBoundary();
        CHECK(!rep.executorStalled);
        totalActs += static_cast<int>(rep.acted.size());
        if (day >= 2) CHECK(rep.acted.empty());
    }
    CHECK(totalActs == 12);                  // 6 walks + 6 arrivals
    // Positions are NOT the targets: landing (orderType 1) fires the T-6
    // no-slot scatter (+ j%1000-500 per axis, pinned in t361). Pin the
    // arrival FLAG and order consumption instead.
    for (int i = 0; i < 6; ++i) {
        CHECK(sim.findShip(20 + i)->act == 0);
        CHECK(sim.findShip(20 + i)->arrivedFlag);
    }
}
