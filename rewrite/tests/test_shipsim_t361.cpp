// t361 per-ship engine skeleton pins — build contract docs/re/pership-spec.md
// (2); law sources docs/re/ships.md S17/S21/S22/S24/S59, docs/re/combat.md §1,
// docs/re/ai-dossier.md §5; session adjudications docs/re/_wip_t361.md S1.
// Golden LCG values computed offline from the banked FUN_0007824f law
// (income-law.md S10 t29b) — determinism pins FIRST, per the queue row.
// NO OQ row closes on these facts (strict-close lives in the ledger).
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

TEST(shipsim_lcg_law_t361) {
    // FUN_0007824f verbatim: golden outputs (state*0x41C64E6D+0x3039,
    // (state>>16)&0x7fff) computed offline for seeds 1/7/2024.
    const int want1[] = {16838, 5758, 10113, 17515, 31051, 5627};
    const int want7[] = {19564, 9806, 10868, 22674, 32531, 3365};
    const int want2024[] = {2012, 10608, 2336, 14785, 205, 18486};
    as::Lcg l1{1}, l7{7}, l24{2024};
    for (int i = 0; i < 6; ++i) {
        const int v1 = l1.next(), v7 = l7.next(), v24 = l24.next();
        CHECK(v1 == want1[i]);
        CHECK(v7 == want7[i]);
        CHECK(v24 == want2024[i]);
        CHECK(v1 >= 0 && v1 <= 0x7fff);   // 15-bit range law
        CHECK(v7 >= 0 && v7 <= 0x7fff);
    }
    // Draw-shape consumers (T-3 %200 x2, T-6 %1000-500 x3) on the golden seed-7 stream.
    as::Lcg l7b{7};
    const int d0 = l7b.next(), d1 = l7b.next();
    CHECK(l7b.state == 0x264e4f5du);       // state pin after exactly 2 draws (seed 7)
    CHECK(d0 % 200 == 164);               // golden placement jitter pair
    CHECK(d1 % 200 == 6);
    as::Lcg l7c{7};
    const int e0 = l7c.next(), e1 = l7c.next(), e2 = l7c.next();
    CHECK(e0 % 1000 - 500 == 64);         // golden scatter triple
    CHECK(e1 % 1000 - 500 == 306);
    CHECK(e2 % 1000 - 500 == 368);
}

TEST(shipsim_x86round_t361) {
    // x87 fistp default = round-half-to-EVEN; C round() is half-AWAY.
    CHECK(as::ShipSim::x86Round(1.5f) == 2);
    CHECK(as::ShipSim::x86Round(2.5f) == 2);   // the divergence case
    CHECK(as::ShipSim::x86Round(0.5f) == 0);
    CHECK(as::ShipSim::x86Round(3.5f) == 4);
    CHECK(as::ShipSim::x86Round(-0.5f) == 0);
    CHECK(as::ShipSim::x86Round(7.5f) == 8);
    CHECK(as::ShipSim::x86Round(8.5f) == 8);
    CHECK(as::ShipSim::x86Round(2.4f) == 2);
    CHECK(as::ShipSim::x86Round(2.6f) == 3);
    CHECK(as::ShipSim::x86Round(3.0f) == 3);
}

TEST(shipsim_power_refill_t361) {
    // trunc([+0x18] * (1 + clamp((T-[+0x52])//100, 0, 10)/10)) (combat.md §1).
    CHECK(as::ShipSim::powerRefill(100, 0) == 100);
    CHECK(as::ShipSim::powerRefill(100, 99) == 100);
    CHECK(as::ShipSim::powerRefill(100, 100) == 110);
    CHECK(as::ShipSim::powerRefill(35, 150) == 38);    // trunc(35*1.1)=38
    CHECK(as::ShipSim::powerRefill(100, 500) == 150);
    CHECK(as::ShipSim::powerRefill(100, 1000) == 200);
    CHECK(as::ShipSim::powerRefill(100, 5000) == 200); // clamp 10 caps 2.0x
    CHECK(as::ShipSim::powerRefill(100, -50) == 100);  // clamp floor 0
    CHECK(as::ShipSim::powerRefill(0, 1000) == 0);
}

TEST(shipsim_walk_law_t361) {
    // S17 T1/T2 golden vectors (1 sugar == 160 world units).
    // (a) full arrival: d = 480*0.00625 = 3.0, moves 10, power 100.
    float pos[3] = {0, 0, 0};
    int32_t power = 100, moves = 10;
    const float delta[3] = {480, 0, 0};
    bool arrived = false;
    CHECK(as::ShipSim::walkLaw(pos, &power, &moves, delta, &arrived) == 3);
    CHECK(arrived);
    CHECK(power == 97);                    // -= steps (commit law)
    CHECK(moves == 7);                     // := round(remaining walk)
    CHECK(nearf(pos[0], 480.f) && pos[1] == 0 && pos[2] == 0);
    // (b) MOVES-limited: walk 1, one step, NOT arrived.
    float p2[3] = {0, 0, 0};
    int32_t pw2 = 100, mv2 = 1;
    arrived = true;
    CHECK(as::ShipSim::walkLaw(p2, &pw2, &mv2, delta, &arrived) == 1);
    CHECK(!arrived);
    CHECK(nearf(p2[0], 160.f));            // 1 sugar -> 160 world
    CHECK(pw2 == 99 && mv2 == 0);
    // (c) POWER clamp (operand is STEPS, verbatim): d=3 steps=3 > power=2 ->
    //     walk = 3*2/3 = 2, steps = 2.
    float p3[3] = {0, 0, 0};
    int32_t pw3 = 2, mv3 = 10;
    arrived = true;
    CHECK(as::ShipSim::walkLaw(p3, &pw3, &mv3, delta, &arrived) == 2);
    CHECK(!arrived);
    CHECK(nearf(p3[0], 320.f));
    CHECK(pw3 == 0 && mv3 == 8);
    // (d) .5 tie through x86 round: d = 400/160 = 2.5 -> steps 2 (half-even;
    //     C round() would give 3 — the divergence pin), arrived (walk==d),
    //     MOVES := round(7.5) = 8. Start OFF-grid (10) so the arrival snap
    //     (410/32 = 12.8125 -> 13 -> 416) does not itself land on a tie: the
    //     quantizer's tie semantics are not banked (S17 T3 says only
    //     "round(coord/g)*g, sign-directed"), so no test may depend on them.
    float p4[3] = {10, 0, 0};
    int32_t pw4 = 100, mv4 = 10;
    const float delta4[3] = {400, 0, 0};
    arrived = false;
    CHECK(as::ShipSim::walkLaw(p4, &pw4, &mv4, delta4, &arrived) == 2);
    CHECK(arrived);
    CHECK(mv4 == 8 && pw4 == 98);
    CHECK(nearf(p4[0], 416.f));            // 410 snapped to the 32-grid
    // (e) zero distance: steps floor 1, arrived.
    float p5[3] = {10, 10, 10};
    int32_t pw5 = 5, mv5 = 0;
    const float zero[3] = {0, 0, 0};
    arrived = false;
    CHECK(as::ShipSim::walkLaw(p5, &pw5, &mv5, zero, &arrived) == 1);
    CHECK(arrived && pw5 == 4);
}

TEST(shipsim_order_transitions_t361) {
    // Table-driven from pership-spec (2): issuer validation T-4, retreat T-5.
    as::ShipSim sim(1);
    sim.addStar(mkStar(0, 1000, 500, 1000));
    sim.addLane(mkLane(0, 0, 0, 100));

    // T-4 issueTravel: kind 1/2 admitted -> kind 5 + orderType 5; others refused.
    const as::OrderKind admitted[] = {as::OrderKind::Move, as::OrderKind::StarTarget};
    const as::OrderKind refused[] = {as::OrderKind::NoOrder, as::OrderKind::Engage,
                                     as::OrderKind::InSystem, as::OrderKind::Placement};
    int id = 0;
    for (as::OrderKind k : admitted) {
        auto s = mkShip(++id, 0, k);
        sim.addShip(s);
        CHECK(sim.issueTravel(id, 0));
        const as::Ship* p = sim.findShip(id);
        CHECK(p->kind == as::OrderKind::Placement);
        CHECK(p->orderType == 5);          // issuer sets +0x67 := 5 (delayed move)
        CHECK(p->laneX == 0.f);
    }
    for (as::OrderKind k : refused) {
        auto s = mkShip(++id, 0, k);
        sim.addShip(s);
        CHECK(!sim.issueTravel(id, 0));
        CHECK(sim.findShip(id)->kind == k);   // state unchanged on refusal
    }
    CHECK(!sim.issueTravel(id, 99));       // unknown lane refused

    // T-5 retreatToSystem: {3,1,2} -> 4; {4,5} refused (0x220f2 law).
    const as::OrderKind back[] = {as::OrderKind::Engage, as::OrderKind::Move,
                                  as::OrderKind::StarTarget};
    for (as::OrderKind k : back) {
        auto s = mkShip(++id, 0, k);
        sim.addShip(s);
        CHECK(sim.retreatToSystem(id));
        CHECK(sim.findShip(id)->kind == as::OrderKind::InSystem);
    }
    const as::OrderKind stay[] = {as::OrderKind::InSystem, as::OrderKind::Placement,
                                  as::OrderKind::NoOrder};
    for (as::OrderKind k : stay) {
        auto s = mkShip(++id, 0, k);
        sim.addShip(s);
        CHECK(!sim.retreatToSystem(id));
    }
}

TEST(shipsim_lane_march_and_placement_t361) {
    // T-7 march + T-3 arrival placement with the golden seed-7 jitter pair.
    as::ShipSim sim(7);
    sim.addStar(mkStar(0, 1000, 500, 1000));
    sim.addLane(mkLane(0, 0, 0, 100));
    auto s = mkShip(1, 0, as::OrderKind::Placement);
    s.laneId = 0;
    s.laneStepX = 100;                     // step0 = [+8]+[+c] = 100
    sim.addShip(s);
    auto rep = sim.advanceBoundary();
    CHECK(rep.placed.size() == 1);
    CHECK(sim.totalRngDraws() == 2);       // exactly the two %200 draws
    as::Ship* p = sim.findShip(1);
    CHECK(p->kind == as::OrderKind::InSystem);          // byte[+0x58] := 4 (0x2202f)
    CHECK(nearf(p->pos[0], 1164.f));       // star.x + 164 (golden draw 1 %200)
    CHECK(nearf(p->pos[1], 300.f));        // star.y - 200 (LIVE jitter const)
    CHECK(nearf(p->pos[2], 1006.f));       // star.z + 6   (golden draw 2 %200)
    CHECK(p->laneId == -1);

    // Third-speed gate (S22 L1: byte[H+0x23] bit0 -> step *= 1/3, pool word
    // MEASURED): step0 14 -> 4.6667/turn, no arrival before the lane fills.
    as::ShipSim sim2(7);
    sim2.addStar(mkStar(0, 0, 0, 0));
    sim2.addLane(mkLane(0, 0, 0, 28, /*third=*/true));
    auto s2 = mkShip(1, 0, as::OrderKind::Placement);
    s2.laneId = 0;
    s2.laneStepX = 14;                     // measured live pair (14,0)
    sim2.addShip(s2);
    sim2.advanceBoundary();
    CHECK(nearf(sim2.findShip(1)->laneX, 14.f / 3.f));
    CHECK(sim2.findShip(1)->kind == as::OrderKind::Placement);
    CHECK(sim2.totalRngDraws() == 0);      // march spends NO rng, NO fuel
    // The march spends NEITHER MOVES nor POWER (S21 item 1 MEASURED-negative).
    as::ShipSim sim3(7);
    sim3.addStar(mkStar(0, 0, 0, 0));
    sim3.addLane(mkLane(0, 0, 0, 1000));
    auto s3 = mkShip(1, 0, as::OrderKind::Placement);
    s3.laneId = 0; s3.laneStepX = 28; s3.powerMax = 100; s3.driveStat = 9;
    sim3.addShip(s3);
    sim3.advanceBoundary();
    CHECK(sim3.findShip(1)->power == 100);   // refill, no march burn
    CHECK(sim3.findShip(1)->moves == 9);     // re-grant, no march burn
}

TEST(shipsim_dwell_law_and_expiry_t361) {
    // T-8 stasis: an act-idle kind-4 ship does not move, burn rng, or change
    // state across boundaries (ships.md S24 item 1, 150-turn witness).
    as::ShipSim sim(7);
    sim.addStar(mkStar(0, 0, 0, 0));
    auto s = mkShip(1, 0, as::OrderKind::InSystem);
    s.pos[0] = 160;
    sim.addShip(s);
    const uint64_t d0 = sim.digest();
    for (int i = 0; i < 5; ++i) {
        auto rep = sim.advanceBoundary();
        CHECK(rep.acted.empty());
        CHECK(rep.asserts == 0);
    }
    // digest differs only via the turn counter; ship state untouched:
    as::Ship* p = sim.findShip(1);
    CHECK(nearf(p->pos[0], 160.f) && p->kind == as::OrderKind::InSystem);
    CHECK(sim.totalRngDraws() == 0);
    CHECK(d0 != sim.digest());             // turn advanced (counter is state)

    // T-10 expiry: dwellTurns 2 suppresses TWO boundaries, then the order runs.
    as::ShipSim sim2(7);
    sim2.addStar(mkStar(0, 0, 0, 0));
    auto q = mkShip(2, 0, as::OrderKind::InSystem);
    q.act = 2;
    q.orderType = 1;                       // ptr-triple target
    q.targetPos[0] = 160;                  // d = 1 sugar -> 1 step
    q.driveStat = 10;
    q.powerMax = 100;
    q.dwellTurns = 2;
    sim2.addShip(q);
    auto r1 = sim2.advanceBoundary();
    CHECK(r1.acted.empty());               // suppressed, word decremented
    CHECK(sim2.findShip(2)->dwellTurns == 1);
    auto r2 = sim2.advanceBoundary();
    CHECK(r2.acted.empty());
    CHECK(sim2.findShip(2)->dwellTurns == 0);
    auto r3 = sim2.advanceBoundary();
    CHECK(r3.acted.size() == 1 && r3.acted[0] == 2);
    CHECK(r3.landed.size() == 1);          // T-6 completion (no-slot branch)
    CHECK(sim2.totalRngDraws() == 3);      // exactly the scatter triple
    auto r4 = sim2.advanceBoundary();
    CHECK(r4.acted.empty());               // order CONSUMED: act cleared
    CHECK(sim2.findShip(2)->act == 0);
    CHECK(sim2.totalRngDraws() == 3);      // no re-draw while dwelling
}

TEST(shipsim_executor_pick_min_power_t361) {
    // S17 T4 (t183 decompile): MIN POWER, strict <, first-in-list ties;
    // eligibility POWER>0 && kind!=1 && act set (raw 0x4134e/0x41357/0x419a7).
    as::ShipSim sim(1);
    sim.addStar(mkStar(0, 0, 0, 0));
    auto a = mkShip(1, 0, as::OrderKind::InSystem);
    a.act = 2; a.orderType = 0; a.powerMax = 100;
    auto b = mkShip(2, 0, as::OrderKind::InSystem);
    b.act = 2; b.orderType = 0; b.powerMax = 50;   // strictly lower -> always picked
    sim.addShip(a);
    sim.addShip(b);
    auto rep = sim.advanceBoundary();
    CHECK(rep.acted.size() == 1 && rep.acted[0] == 2);   // MIN wins, one per race
    auto rep2 = sim.advanceBoundary();
    CHECK(rep2.acted.size() == 1 && rep2.acted[0] == 2); // sticky while power stays min
    // Raise b above a: the pick flips to a (strict <, not hysteresis).
    sim.findShip(2)->powerMax = 200;
    auto rep3 = sim.advanceBoundary();
    CHECK(rep3.acted.size() == 1 && rep3.acted[0] == 1);

    // Tie -> first-in-list (etaDay equal, stable insertion order).
    as::ShipSim sim2(1);
    sim2.addStar(mkStar(0, 0, 0, 0));
    auto x = mkShip(7, 0, as::OrderKind::InSystem);
    x.act = 2; x.powerMax = 100;
    auto y = mkShip(8, 0, as::OrderKind::InSystem);
    y.act = 2; y.powerMax = 100;
    sim2.addShip(x);
    sim2.addShip(y);
    auto trep = sim2.advanceBoundary();
    CHECK(trep.acted.size() == 1 && trep.acted[0] == 7);

    // POWER==0 refused (cmpl $0x0,+0x88; jle): no act processed, no assert noise.
    as::ShipSim sim3(1);
    sim3.addStar(mkStar(0, 0, 0, 0));
    auto z = mkShip(9, 0, as::OrderKind::InSystem);
    z.act = 2; z.powerMax = 0;
    sim3.addShip(z);
    auto zrep = sim3.advanceBoundary();
    CHECK(zrep.acted.empty());

    // Stale act (0x41a1c..0x41a45): actTarget != race focus -> act cleared,
    // ship not processed (re-decide is the caller's decider hook).
    as::ShipSim sim4(1);
    sim4.addStar(mkStar(0, 0, 0, 0));
    auto w = mkShip(3, 0, as::OrderKind::InSystem);
    w.act = 2; w.actTarget = 5; w.powerMax = 100;
    sim4.addShip(w);
    sim4.setFocus(0, 7);                   // focus moved on
    auto wrep = sim4.advanceBoundary();
    CHECK(wrep.acted.empty());
    CHECK(sim4.findShip(3)->act == 0);     // 0x41a30 verbatim
}

TEST(shipsim_assert_law_t361) {
    // 0x419cf..0x419f1: after movement kind must be 3 or 4 (dossier reading:
    // kind 3 tolerated). A kind-2 pick that cannot walk counts a violation —
    // the t362 departure-law seam, counted not crashed.
    as::ShipSim sim(1);
    sim.addStar(mkStar(0, 0, 0, 0));
    auto s = mkShip(1, 0, as::OrderKind::StarTarget);
    s.act = 2; s.orderType = 0; s.powerMax = 100;   // no walkable order
    sim.addShip(s);
    auto rep = sim.advanceBoundary();
    CHECK(rep.acted.size() == 1);
    CHECK(rep.asserts == 1);
    // Kind 3 tolerated (targetability leg is engagement scope):
    as::ShipSim sim2(1);
    sim2.addStar(mkStar(0, 0, 0, 0));
    auto e = mkShip(1, 0, as::OrderKind::Engage);
    e.act = 2; e.powerMax = 100;
    sim2.addShip(e);
    auto rep2 = sim2.advanceBoundary();
    CHECK(rep2.acted.size() == 1);
    CHECK(rep2.asserts == 0);
}

TEST(shipsim_determinism_digest_t361) {
    // Same seed + same inputs => identical digest at every boundary; a
    // different seed diverges once rng-consuming laws fire (T-3 placement).
    auto build = [](unsigned seed) {
        as::ShipSim sim(seed);
        sim.addStar(mkStar(0, 0, 0, 0));
        sim.addStar(mkStar(1, 640, 0, 0));
        sim.addLane(mkLane(0, 0, 1, 400));
        auto m = mkShip(1, 0, as::OrderKind::Placement);
        m.laneId = 0; m.laneStepX = 14; m.laneStepZ = 0;
        sim.addShip(m);
        auto w = mkShip(2, 0, as::OrderKind::InSystem);
        w.act = 2; w.orderType = 1; w.targetPos[0] = 320; w.driveStat = 10;
        w.powerMax = 100;
        sim.addShip(w);
        auto g = mkShip(3, 1, as::OrderKind::InSystem);   // other race, idle
        g.pos[1] = 64;
        sim.addShip(g);
        return sim;
    };
    as::ShipSim A = build(7);
    as::ShipSim B = build(7);
    as::ShipSim C = build(8);
    bool divergedFromC = false;
    for (int i = 0; i < 12; ++i) {
        auto ra = A.advanceBoundary();
        auto rb = B.advanceBoundary();
        C.advanceBoundary();
        CHECK(ra.acted == rb.acted);
        CHECK(ra.placed == rb.placed);
        CHECK(A.lcgState() == B.lcgState());
        CHECK(A.digest() == B.digest());
        CHECK(A.turn() == B.turn());
        if (A.digest() != C.digest()) divergedFromC = true;
        CHECK(ra.asserts == 0);            // sim commits never violate 0x93e
    }
    CHECK(divergedFromC);                  // seed-8 stream differs once T-3 fires
    CHECK(A.totalRngDraws() == B.totalRngDraws());
}

TEST(shipsim_from_record_t361) {
    // Record -> Ship field mapping (pership-spec (1) offsets via the t360
    // parser's Record; eta stamped to the import turn — INFERRED seam).
    ascend::formats::ShipSave::Record r;
    r.slot = 12;
    r.dead = false;
    r.ownerRace = 2;
    r.ownerHandle = (2u << 16) | 0x3412u;
    r.orderKind = 5;
    r.orderTarget = 0x25c1a0;
    r.actEnum = 1;
    r.actTarget = 0x260040;
    r.orderType = 5;
    r.pos[0] = 416.f; r.pos[1] = -128.f; r.pos[2] = 288.f;
    r.power = 40; r.powerMax = 100; r.moves = 4; r.driveTotal = 7;
    r.integrity = 30; r.maxIntegrity = 30; r.statusFlags = 0x10;
    r.laneStepX = 14; r.laneStepZ = 0;
    const as::Ship s = as::Ship::fromRecord(r, 42);
    CHECK(s.id == 12);
    CHECK(s.owner == 2);
    CHECK(s.kind == as::OrderKind::Placement);
    CHECK(s.orderTarget == 0x25c1a0u);     // raw guest-physical value, not derefed
    CHECK(s.act == 1);
    CHECK(s.orderType == 5);
    CHECK(s.pos[0] == 416.f && s.pos[1] == -128.f && s.pos[2] == 288.f);
    CHECK(s.power == 40 && s.powerMax == 100 && s.moves == 4 && s.driveStat == 7);
    CHECK(s.integrity == 30 && s.maxIntegrity == 30 && s.status == 0x10);
    CHECK(s.laneStepX == 14 && s.laneStepZ == 0);
    CHECK(s.etaDay == 42);                 // import stamp (INFERRED full-refill)
    // Out-of-range kind maps to NoOrder defensively (live set is {1..5}, A4).
    auto bad = r;
    bad.orderKind = 9;
    CHECK(as::Ship::fromRecord(bad, 1).kind == as::OrderKind::NoOrder);
}
