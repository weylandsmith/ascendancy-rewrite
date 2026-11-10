// t363R GIZMO INVENTORY + CARRIER/CARGO pins — the upkeep burn (FUN_0004a658),
// the turn-tail slot refresh (0x4a772..0x4a7a4), the recalc carrier law
// (FUN_00049acc), the ring mutators (FUN_00049698/0x496e4/0x49624), the
// kind-2 completion (FUN_00049a34 + admission FUN_000499f8) and the C2
// carrier shape (0x42d09..0x42d5b). Law sources: docs/re/_wip_t363.md
// S1a/S1c/S3a/S3d/S4/S6 (verbatim disasm, work/r331_disasm.txt) + the re-land
// contract S5; census corroboration work/r363_gizmo_census.out. Design rows
// below mirror the MEASURED shapes (_wip S3b: upkeep gate == flag bit 5,
// costs/levels on cat-1 rows only) — the pin values are law shapes, the
// vendor's 76-row table is the rewrite Gizmo parse (economy.cpp), cross-
// validated file-vs-RAM. NO OQ row closes on these facts (user-gated).
#include "game/shipsim.h"
#include "harness.h"

#include <vector>

namespace as = ascend::game;

namespace {

// Shield row shape (cat 1, upkeep gate SET, cost 4, Level 2, NumUses 3):
// matches the MEASURED cat-1 family (rows 10..15: gate bit AND cat==1
// EXACTLY, costs {0,1,2,2,3,4}, levels {1,2,1,3,4,5} — ships.md §12).
as::SimDesign shieldRow(int32_t cost, int32_t level) {
    as::SimDesign d;
    d.cat = 1; d.power = cost; d.level = level; d.numUses = 3;
    d.upkeepGate = true; d.rowShield = level;
    return d;
}
as::SimDesign plainRow(int cat, int32_t power, int32_t level, int32_t uses) {
    as::SimDesign d;
    d.cat = cat; d.power = power; d.level = level; d.numUses = uses;
    if (cat == 0) d.rowWeapon = level;
    if (cat == 2) d.rowDrive = level;
    if (cat == 3) d.rowScanner = level;
    if (cat == 4) d.rowGenPower = power;
    return d;
}
// Install a table covering every cidx the laws key on (indices below the
// keys stay zero cat-5 rows — the honest default per shipsim.h designRow).
std::vector<as::SimDesign> mkDesigns(const as::SimDesign& shield) {
    std::vector<as::SimDesign> t(0x4a);
    t[0x2a] = plainRow(5, 0, 0, 0);                       // Cloaker
    t[0x2b] = plainRow(2, 1, 1, 0);                       // Star Lane Drive
    t[0x2c] = plainRow(2, 2, 2, 0);                       // Hyperdrive
    t[0x3c] = plainRow(5, 0, 0, 1);                       // Lane Magnetron
    t[0x47] = plainRow(5, 0, 0, 0);                       // Colonizer
    t[0x49] = plainRow(5, 10, 0, 0);                      // Invasion Module (C1)
    t[10] = shield;
    return t;
}

as::Ship mkBase(int id, int owner) {
    as::Ship s;
    s.id = id; s.owner = owner;
    return s;
}

}  // namespace

TEST(shipsim_upkeep_burn_orders_pick_t363) {
    // (a) The burn lands BEFORE the MIN-POWER pick of its sweep (_wip S1b:
    // 0x4a658 sits inside the re-invoked executor prologue). Ship A: power
    // 28 + affordable shield (cost 4); ship B: power 22, no shield. The TAIL
    // burn (0x4a95b) takes A to 24 — still ABOVE B. Only the SWEEP burn (the
    // 0x412cf call) takes A to 20 < 22 => A departs FIRST. A bare re-grant
    // (the t361/t362 seam, mutation M1) leaves A at 24 > 22 and picks B —
    // the ORDER at acted[0] is the pin.
    as::ShipSim sim(1);
    sim.setDesigns(mkDesigns(shieldRow(4, 2)));
    sim.addStar({0, {0, 0, 0}});
    auto a = mkBase(1, 0);
    a.kind = as::OrderKind::InSystem;
    a.act = 2; a.orderType = 1;
    a.targetPos[0] = 160;                       // d = 1 sugar
    a.driveStat = 10; a.powerMax = 28;
    a.invCap = 1; a.inv[0].cidx = 10; a.inv[0].payload = 0xffffffffu;
    auto b = mkBase(2, 0);
    b.kind = as::OrderKind::InSystem;
    b.act = 2; b.orderType = 1;
    b.targetPos[0] = 160;
    b.driveStat = 10; b.powerMax = 22;          // 28-8 < 22 < 28-4: sweep-visible
    sim.addShip(a); sim.addShip(b);
    auto rep = sim.advanceBoundary();
    CHECK(rep.acted.size() >= 2);
    CHECK(rep.acted[0] == 1);                   // shielded ship FIRST (burned to 20)
    as::Ship* pa = sim.findShip(1);
    CHECK(pa->shields == 2);                    // recharge == row[+0x56] (0x4a71c)
}

TEST(shipsim_upkeep_unaffordable_t363) {
    // (b) PAYABLE gate 0x4a70a `jl next`: cost > power skips the slot
    // ENTIRELY — NO burn AND NO charges (charges are NESTED under
    // affordability, 0x4a716 is below the burn). Mutant: charges-unnested.
    as::ShipSim sim(1);
    sim.setDesigns(mkDesigns(shieldRow(4, 2)));
    auto s = mkBase(1, 0);
    s.power = 3; s.invCap = 1;
    s.inv[0].cidx = 10; s.inv[0].payload = 0xffffffffu;
    sim.addShip(s);
    as::Ship* p = sim.findShip(1);
    const int32_t burn = sim.upkeep(*p);
    CHECK(burn == 0);
    CHECK(p->power == 3);                       // no partial burn, no clamp
    CHECK(p->shields == 0);                     // NESTED: unaffordable => no charges
}

TEST(shipsim_upkeep_payload_gate_t363) {
    // (c) Slot payload != -1 skips the slot (0x4a6f9). MEASURED: 5860/5940
    // slots carry payload 0 (never burn-eligible); the 80 payload==-1 slots
    // ALL sit on upkeep-gate rows (work/r363_gizmo_census.out, _wip S4/S5) —
    // the gate is SELECTIVE in real data.
    as::ShipSim sim(1);
    sim.setDesigns(mkDesigns(shieldRow(4, 2)));
    auto s = mkBase(1, 0);
    s.power = 100; s.invCap = 1;
    s.inv[0].cidx = 10; s.inv[0].payload = 0;   // affordable but payload 0
    sim.addShip(s);
    as::Ship* p = sim.findShip(1);
    CHECK(sim.upkeep(*p) == 0);
    CHECK(p->power == 100);
    CHECK(p->shields == 0);
    p->inv[0].payload = 0xffffffffu;            // flip to the eligible value
    CHECK(sim.upkeep(*p) == 4);
    CHECK(p->shields == 2);
}

TEST(shipsim_upkeep_bit0_ring_runs_t363) {
    // (d) Status bit0 zeroes MOVES but the RING SCAN STILL RUNS: 0x4a67b is
    // `jmp 0x4a6a6` (shields zeroing), NOT the loop-exit 0x4a727 (_wip S4
    // item 1 — the earlier "skip ring scan" reading is RETRACTED). Mutant:
    // skip-ring-on-bit0 must fail the burn check here.
    as::ShipSim sim(1);
    sim.setDesigns(mkDesigns(shieldRow(4, 2)));
    auto s = mkBase(1, 0);
    s.status = 0x1;                             // bit0 SET
    s.moves = 99;                               // pre-set garbage
    s.power = 10; s.invCap = 1;
    s.inv[0].cidx = 10; s.inv[0].payload = 0xffffffffu;
    sim.addShip(s);
    as::Ship* p = sim.findShip(1);
    const int32_t burn = sim.upkeep(*p);
    CHECK(p->moves == 0);                       // [+0x94] := 0 (0x4a671)
    CHECK(burn == 4);                           // burn STILL runs (0x4a710)
    CHECK(p->shields == 2);                     // recharge still runs
    // bit3 zeroes charges AFTER the scan (0x4a73a):
    p->status = 0x8;
    sim.upkeep(*p);
    CHECK(p->shields == 0);
}

TEST(shipsim_slot_refresh_t363) {
    // (e) Turn-tail refresh 0x4a772..0x4a7a4: use word := design[+0x42]
    // (numUses; operand CORRECTED from +0x4e, _wip S1c — MEASURED 5940/5940
    // save-side). Zero NumUses refreshes to 0 (the "unlimited/no-decrement"
    // column guard, spec G7). Mutant: refresh operand +0x3e (Level) would
    // write 2 into the shield slot here.
    as::ShipSim sim(1);
    sim.setDesigns(mkDesigns(shieldRow(4, 2)));  // shield: numUses 3, level 2
    auto s = mkBase(1, 0);
    s.kind = as::OrderKind::InSystem;
    s.invCap = 2;
    s.inv[0].cidx = 10;  s.inv[0].use = 1;      // garbage pre-state
    s.inv[1].cidx = 0x2a; s.inv[1].use = 7;     // Cloaker: numUses 0
    s.inv[2].cidx = 10;  s.inv[2].use = 9;      // PHANTOM zone (idx >= cap): untouched
    sim.addShip(s);
    sim.advanceBoundary();                      // tail runs the refresh
    as::Ship* p = sim.findShip(1);
    CHECK(p->inv[0].use == 3);                  // := design[+0x42] == numUses
    CHECK(p->inv[1].use == 0);                  // 0-for-unlimited
    CHECK(p->inv[2].use == 9);                  // window i < cap EXCLUSIVE
}

TEST(shipsim_recalc_carrier_law_t363) {
    // (f) FUN_00049acc carrier law: one Star Lane Drive -> laneStepX 14, one
    // Hyperdrive -> laneStepZ 28 (pools DERIVED from the MEASURED live pairs
    // (14,0)/(0,28), _wip S3a); Colonizer -> targetSlot -1 (0x49b9b);
    // Cloaker -> specialCount++ (0x49bc9); driveTotal := hullBaseDrive +
    // cat-2 levels (0x49ae4/0x49b29/0x49b67); cat2PowerCarry += row[+0x36]
    // for cat==2 (0x49b85). Mutant: window inclusive would absorb the 5th
    // phantom LaneDrive below.
    as::ShipSim sim(1);
    sim.setDesigns(mkDesigns(shieldRow(4, 2)));
    auto s = mkBase(1, 0);
    s.hullBaseDrive = 5;
    sim.addShip(s);
    as::Ship* p = sim.findShip(1);
    p->invCap = 4;
    CHECK(sim.setSlot(*p, 0, as::kCidxLaneDrive));
    CHECK(p->laneStepX == 14);                  // ONE drive => step X 14
    CHECK(p->laneStepZ == 0);
    CHECK(sim.setSlot(*p, 1, as::kCidxHyperdrive));
    CHECK(p->laneStepX == 14 && p->laneStepZ == 28);
    CHECK(p->driveStat == 5 + 1 + 2);           // hull base + drive levels
    CHECK(p->cat2PowerCarry == 1 + 2);          // row[+0x36] for cat==2
    CHECK(sim.setSlot(*p, 2, as::kCidxColonizer));
    CHECK(p->targetSlot == -1);                 // 0x49b9b verbatim
    CHECK(sim.setSlot(*p, 3, as::kCidxCloaker));
    CHECK(p->specialCount == 1);                // 0x49bc9 verbatim
    // Phantom beyond cap: ADMITTED by set-slot (idx==cap) but INERT — the
    // recalc window is i<cap (0x49bae jge exit):
    CHECK(sim.setSlot(*p, 4, as::kCidxLaneDrive));
    CHECK(p->laneStepX == 14);                  // window EXCLUSIVE
    CHECK(p->specialCount == 1);
}

TEST(shipsim_setslot_phantom_t363) {
    // (g) FUN_00049698 gates verbatim: idx > cap REJECT; idx == cap ADMITTED
    // (0x4969b `jg`, not `jge`) -> phantom slot, filled +1, stats INERT;
    // same-cidx-in-target-slot REJECT; duplicates across slots LEGAL.
    as::ShipSim sim(1);
    sim.setDesigns(mkDesigns(shieldRow(4, 2)));
    auto s = mkBase(1, 0);
    s.hullBaseDrive = 3;
    sim.addShip(s);
    as::Ship* p = sim.findShip(1);
    p->invCap = 1; p->invFilled = 0;
    CHECK(!sim.setSlot(*p, 2, as::kCidxLaneDrive));   // idx > cap REJECT
    CHECK(p->invFilled == 0);
    CHECK(sim.setSlot(*p, 1, as::kCidxLaneDrive));    // idx == cap ADMITTED
    CHECK(p->inv[1].cidx == as::kCidxLaneDrive);
    CHECK(p->invFilled == 1);                         // inc [+0x15e]
    CHECK(p->driveStat == 3);                         // INERT: window i<cap
    CHECK(p->laneStepX == 0);
    CHECK(!sim.setSlot(*p, 1, as::kCidxLaneDrive));   // same-cidx-same-slot REJECT
    CHECK(sim.setSlot(*p, 0, as::kCidxLaneDrive));    // duplicate ACROSS slots LEGAL
    CHECK(p->invFilled == 2);
    CHECK(p->driveStat == 3 + 1);                     // now IN-WINDOW: counted
    CHECK(p->laneStepX == 14);
    CHECK(sim.clearSlot(*p, 1));                      // phantom clearable (no bound)
    CHECK(p->invFilled == 1);
    CHECK(!sim.clearSlot(*p, 1));                     // already empty -> false
    // fillFirstEmpty window is CAP (0x4964a), not all-25 (spec G3 shorthand):
    p->inv[0].cidx = 0xff; p->invFilled = 0;
    CHECK(sim.fillFirstEmpty(*p, as::kCidxColonizer));
    CHECK(p->inv[0].cidx == as::kCidxColonizer);
    CHECK(!sim.fillFirstEmpty(*p, as::kCidxColonizer));  // cap window now full
    CHECK(p->inv[1].cidx == 0xff);                       // phantom zone NOT scanned
    CHECK(p->invFilled == 1);                            // second fill stored nothing
}

TEST(shipsim_first_carrier_t363) {
    // (h) C2 shape (0x42d09..0x42d5b verbatim): FIRST ship in LIST order
    // with kind==4 (InSystem) AND a slot == code; no strength comparison.
    // Residue HOME = carriesCode accessors (magnetron/Phase-Bomb are
    // ZERO-carried in the corpus, _wip S4 item 5 — the model gets the FIELDS;
    // the C5 chooser stays a non-goal, no OQ row closes here).
    as::ShipSim sim(1);
    sim.setDesigns(mkDesigns(shieldRow(4, 2)));
    auto c1 = mkBase(1, 0); c1.kind = as::OrderKind::InSystem;   // no module
    c1.invCap = 1;                                // real window for the
                                                  // magnetron HOME below
    auto c2 = mkBase(2, 0); c2.kind = as::OrderKind::Placement;  // carries, WRONG kind
    c2.invCap = 1; c2.inv[0].cidx = as::kCidxInvasionModule;
    auto c3 = mkBase(3, 0); c3.kind = as::OrderKind::InSystem;   // carries, qualifies
    c3.invCap = 1; c3.inv[0].cidx = as::kCidxInvasionModule;
    auto c4 = mkBase(4, 0); c4.kind = as::OrderKind::InSystem;   // PHANTOM module only
    c4.invCap = 0; c4.inv[0].cidx = as::kCidxInvasionModule;
    sim.addShip(c1); sim.addShip(c2); sim.addShip(c3); sim.addShip(c4);
    const as::Ship* fc = sim.firstCarrier(as::kCidxInvasionModule);
    CHECK(fc && fc->id == 3);                   // list order, InSystem-only
    CHECK(!sim.carriesCode(*sim.findShip(4), as::kCidxInvasionModule));  // phantom != equipment
    CHECK(sim.carriesCode(*sim.findShip(3), as::kCidxInvasionModule));
    // Magnetron HOME: the field exists and reads back; no chooser is modelled.
    sim.setSlot(*sim.findShip(1), 0, as::kCidxMagnetron);
    CHECK(sim.carriesCode(*sim.findShip(1), as::kCidxMagnetron));
    CHECK(sim.carriesCode(*sim.findShip(1), as::kCidxPhaseBomb) == false);  // zero-carried
}

TEST(shipsim_lane_arrival_t363) {
    // Kind-2 completion FUN_00049a34 (contract item 3): an orderType-2 walk
    // that ARRIVES calls the completion INSIDE the commit (switch 0x4a333..
    // 0x4a33d); admitted leg: kind := 5 (0x49a74), lane-local x := 0
    // (0x49a78), laneId := lane (0x49a82), direction := (target == lane.a)
    // (0x49a85). The assert leg then sees kind 5 -> COUNTED 0x93e (S4 item
    // 4), never fatal. Admission FUN_000499f8: lane gear (stepX+stepZ > 0)
    // OR the NEVER-SEEN species form (flag, default off); lane bit 0x2 SET
    // == DENIED (polarity S4 item 3).
    as::ShipSim sim(1);
    sim.setDesigns(mkDesigns(shieldRow(4, 2)));
    as::SimStar s0; s0.id = 0; s0.pos[0] = 0; s0.pos[1] = 0; s0.pos[2] = 0;
    as::SimStar s1; s1.id = 1; s1.pos[0] = 1000; s1.pos[1] = 0; s1.pos[2] = 0;
    sim.addStar(s0); sim.addStar(s1);
    as::SimLane ln; ln.id = 0; ln.a = 0; ln.b = 1; ln.len = 500;
    sim.addLane(ln);
    auto s = mkBase(1, 0);
    s.kind = as::OrderKind::InSystem;           // walk guard is kind 4 (T-9)
    s.act = 2; s.orderType = 2;                 // star-target order
    s.targetStar = 0;                           // the OLD target [+0x59]
    s.orderPayloadLane = 0;                     // the lane RECORD (+0x68)
    s.laneStepX = 14;                           // lane gear admits (0x499fb)
    s.driveStat = 10; s.powerMax = 100;
    s.pos[0] = 160;                             // d = 1 sugar to star 0
    sim.addShip(s);
    auto rep = sim.advanceBoundary();
    as::Ship* p = sim.findShip(1);
    CHECK(rep.laned == std::vector<int>{1});
    CHECK(p->kind == as::OrderKind::Placement); // 0x49a74
    CHECK(p->laneId == 0);                      // 0x49a82
    CHECK(p->laneX == 0.0f);                    // 0x49a78
    CHECK(p->laneToB == true);                  // target == lane.a => 1.0f
    CHECK(rep.asserts == 1);                    // assert leg sees kind 5: COUNTED
    // DENIED legs: closed lane (bit 0x2 SET) and no lane gear.
    as::ShipSim sim2(1);
    sim2.setDesigns(mkDesigns(shieldRow(4, 2)));
    sim2.addStar(s0); sim2.addStar(s1);
    as::SimLane closed = ln; closed.closed = true;
    sim2.addLane(closed);
    auto s2 = s; s2.id = 2;
    sim2.addShip(s2);
    auto rep2 = sim2.advanceBoundary();
    CHECK(rep2.laned.empty());
    CHECK(sim2.findShip(2)->kind == as::OrderKind::InSystem);  // state untouched
    CHECK(rep2.asserts == 0);
    as::ShipSim sim3(1);
    sim3.setDesigns(mkDesigns(shieldRow(4, 2)));
    sim3.addStar(s0); sim3.addStar(s1); sim3.addLane(ln);
    auto s3 = s; s3.id = 3; s3.laneStepX = 0;   // no gear, species flag false
    sim3.addShip(s3);
    auto rep3 = sim3.advanceBoundary();
    CHECK(rep3.laned.empty());
    CHECK(sim3.findShip(3)->kind == as::OrderKind::InSystem);
}
