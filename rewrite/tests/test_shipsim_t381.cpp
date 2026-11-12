// SPDX-License-Identifier: GPL-3.0-or-later

// t381 GIZMO-USE DECREMENT + INVASION CONSUMPTION pins. Evidence:
// docs/re/_wip_t381.md S1 (FUN_0003a174 0x3a2a2..0x3a38b verbatim),
// S1b/S1c (handler-1 FUN_0004c794 charge law, fresh full read); witnesses
// docs/re/ships.md S64 M2 + the raw word-event stream
// work/r1/t370_slot_events_all.txt (re-read in full this iteration).
// THE MEASURED FACTS these pins encode:
//  * M2 Stainer s14 00:24:08: slot-13 cidx 9 use 3->2 AND power 90->84 IN
//    ONE FRAME. Nanomanipulator gizmos.txt row 9 `0 6 50 13 3 100 0 0 56`
//    (Cat 0, Power 6, Range 50, NumUses 3, flags bits 0..3) — DEC is the
//    dispatcher prologue (0x4a390, mode-1), the -6 is handler-1's charge
//    0x4c958..0x4c960 (design[+0x36] verbatim — the affordable branch makes
//    cost == design power; the unaffordable branch ZEROES the cost).
//    The t364-era "non-gun handlers charge nothing" reading is SUPERSEDED.
//  * M2 Gofriller s34: the same decrement twice (00:26:59, 00:27:51), the
//    ACTIVE slot only — copies of cidx 9 in slots 16/19/22 untouched.
//  * DEC-before-charge ORDER: mode-0 probes DEC (dispatcher precedes the
//    mode cmp) but charge nothing (0x4c947 cmp mode,1); gate-fails DEC and
//    charge nothing (0x4c942). The handler-1 commit gate
//    0x4c91d..0x4c942 = affordable AND inRange AND (design[+0x33] & 0xc)
//    (GZ_TARGETORBIT|GZ_TARGETSURFACE — first cited consumer as a gate).
//  * M2 Ignatz s22 00:28:48: SIX cidx-73 slots, EXACTLY the first TWO
//    cleared at invasion launch, FOUR survive — count-limited consumption
//    (need = min(count, activeShieldUnits + 1), cap 0x3a327; walk-order
//    first-match clearSlot loop 0x3a360..0x3a38b). NOT all-or-nothing.
// NO OQ row closes on these facts (user-gated; OQ-019 family).
#include "game/shipsim.h"
#include "harness.h"

#include <vector>

namespace as = ascend::game;

namespace {

// gizmos.txt row 9 Nanomanipulator VERBATIM (extracted/ascend00/gizmos.txt
// line 116: `0 6 50 13 3 100 0 0    56       0 1 2 3 255`). flag_list bits
// 0..3 -> mask 0xF -> the 0xc commit-gate mask ANDs nonzero (admits).
as::SimDesign nanomanipRow() {
    as::SimDesign d;
    d.cat = 0; d.power = 6; d.range = 50; d.level = 13; d.numUses = 3;
    d.industry = 100;
    d.targetShip = true;            // bit 0
    d.targetOrbitSurface = true;    // bits 2|3 (0xc) — the gate operand
    d.rowWeapon = 13;               // cat-0 derived +0x52 (recalc law)
    return d;
}
// A row shaped like Nanomanipulator but WITHOUT the 0xc bits (bits 0|1
// only) — the gate-denial mutant bait.
as::SimDesign noOrbitRow() {
    as::SimDesign d = nanomanipRow();
    d.targetOrbitSurface = false;
    return d;
}
std::vector<as::SimDesign> mkNanaDesigns(bool orbit = true) {
    std::vector<as::SimDesign> t(0x4a);
    t[9] = orbit ? nanomanipRow() : noOrbitRow();
    t[0x49] = as::SimDesign{};      // Invasion Module shape (pership-spec C1)
    return t;
}
// M2-class ship: Stainer rig — power 90, the gizmo in ACTIVE slot 13 with
// use 3, target triple set (the [+0x68]-deref surrogate).
as::Ship mkNanaShip(int id) {
    as::Ship s;
    s.id = id; s.owner = 0; s.kind = as::OrderKind::InSystem;
    s.systemId = 7;
    s.power = 90; s.powerMax = 90;
    s.integrity = 10; s.maxIntegrity = 10;
    s.invCap = 16; s.invFilled = 1;
    s.inv[13].cidx = 9; s.inv[13].use = 3;
    s.activeSlot = 13;
    s.fireTarget = 2;               // non-null (the assert-0xad stand-in)
    s.targetPos[0] = 32 * 10;       // dist 320 <= 50*32 = 1600 (in range)
    return s;
}
// Ignatz-class transport: the ring BEFORE the 00:28:48 frame verbatim —
// slots 0:(29,0,0) 1:(18,0,0) 2..7:(73,0,0) x6 8,9:(43,0,0), invCap 10.
as::Ship mkIgnatz(int id) {
    as::Ship s;
    s.id = id; s.owner = 0; s.kind = as::OrderKind::Engage;   // raw kind 3
    s.power = 3; s.powerMax = 8;
    s.integrity = 10; s.maxIntegrity = 10;
    s.invCap = 10; s.invFilled = 10;
    s.inv[0].cidx = 29; s.inv[1].cidx = 18;
    for (int i = 2; i <= 7; ++i) s.inv[i].cidx = as::kCidxInvasionModule;
    s.inv[8].cidx = 43; s.inv[9].cidx = 43;
    return s;
}

}  // namespace

TEST(shipsim_gizmo_use_decrement_charge_frame_t381) {
    // Stainer 00:24:08 EXACT: mode-1 commit on the active cidx-9 slot runs
    // DEC (3->2, dispatcher 0x4a390) AND charge 6 (handler-1 0x4c958) in the
    // SAME call — power 90->84. Gate word 1 returned.
    as::ShipSim sim(1);
    sim.setDesigns(mkNanaDesigns());
    sim.addShip(mkNanaShip(14));
    as::Ship* s = sim.findShip(14);
    s->orderType = 1; s->dispatcherGate = 1;
    auto rep = sim.commitShot(14, 1);
    CHECK(rep.handler == 1);                    // +0x67 key -> 0x4c794
    CHECK(s->inv[13].use == 2);                 // DEC 3->2 (witness value)
    CHECK(s->power == 84);                      // 90->84 = 'Power 6' EXACT
    CHECK(rep.flags == 1);                      // gate word (0x4c93e store)
    CHECK(rep.shots == 0);                      // handler-1 runs NO hit call
}

TEST(shipsim_gizmo_use_decrement_twice_active_slot_t381) {
    // Gofriller shape: two commits 2->1, each -6; copies in slots 16/19/22
    // (cidx 9) are NEVER touched — the DEC hits the ACTIVE slot only.
    as::ShipSim sim(1);
    sim.setDesigns(mkNanaDesigns());
    auto ship = mkNanaShip(34);
    ship.inv[16].cidx = 9; ship.inv[16].use = 3;
    ship.inv[19].cidx = 9; ship.inv[19].use = 3;
    ship.inv[22].cidx = 9; ship.inv[22].use = 3;
    ship.invFilled = 4;
    sim.addShip(ship);
    as::Ship* s = sim.findShip(34);
    s->orderType = 1; s->dispatcherGate = 1;
    sim.commitShot(34, 1);
    CHECK(s->inv[13].use == 2 && s->power == 84);   // 00:26:59 frame
    sim.commitShot(34, 1);
    CHECK(s->inv[13].use == 1);                     // 00:27:51 frame
    CHECK(s->power == 78);                          // -6 each, EXACT
    CHECK(s->inv[16].use == 3 && s->inv[19].use == 3 && s->inv[22].use == 3);
}

TEST(shipsim_gizmo_use_mode0_lands_nothing_t381) {
    // The DEC itself is mode-1-gated (0x4a38b cmp edx,1 / jne 0x4a394): a
    // mode-0 probe lands NOTHING at all — no DEC, no charge (t377 twin:
    // shipsim_magnetron_mode0_probe_lands_nothing). The gate-fail DEC law
    // (C7) is mode-1-only: DEC precedes the HANDLER's gates, not the
    // dispatcher's own mode cmp.
    as::ShipSim sim(1);
    sim.setDesigns(mkNanaDesigns());
    sim.addShip(mkNanaShip(14));
    as::Ship* s = sim.findShip(14);
    s->orderType = 1; s->dispatcherGate = 1;
    sim.commitShot(14, 0);
    CHECK(s->inv[13].use == 3);                 // NO DEC on probe
    CHECK(s->power == 90);                      // NO charge
}

TEST(shipsim_gizmo_use_out_of_range_decs_no_charge_t381) {
    // Range gate 0x4c8f4: dist > range<<5 clears the in-range flag -> gate 0
    // -> exit 0x4c942 WITHOUT charge; the DEC (dispatcher) is already paid.
    // Range 0 = UNLIMITED (je 0x4c91d keeps the -1 sentinel) — pinned by the
    // unlimited leg below.
    as::ShipSim sim(1);
    sim.setDesigns(mkNanaDesigns());
    sim.addShip(mkNanaShip(14));
    as::Ship* s = sim.findShip(14);
    s->orderType = 1; s->dispatcherGate = 1;
    s->targetPos[0] = 32 * 60;                  // 1920 > 1600: too far
    sim.commitShot(14, 1);
    CHECK(s->inv[13].use == 2);                 // DEC paid
    CHECK(s->power == 90);                      // gate fail: no charge
    // status bit0x4 DOUBLES the limit (ds:0x85312 == 2.0 file-measured):
    // 1920 <= 3200 -> the same shot commits.
    s->status |= 0x4;
    sim.commitShot(14, 1);
    CHECK(s->inv[13].use == 1);
    CHECK(s->power == 84);                      // 90 - 6
}

TEST(shipsim_gizmo_use_unaffordable_decs_no_charge_t381) {
    // affordable := design[+0x36] <= power (0x4c7cf..0x4c7e2). Power 5 < 6:
    // the cost word is ZEROED and the gate fails -> DEC paid, no charge.
    as::ShipSim sim(1);
    sim.setDesigns(mkNanaDesigns());
    auto ship = mkNanaShip(14);
    ship.power = 5;
    sim.addShip(ship);
    as::Ship* s = sim.findShip(14);
    s->orderType = 1; s->dispatcherGate = 1;
    sim.commitShot(14, 1);
    CHECK(s->inv[13].use == 2);                 // DEC paid (C7 order)
    CHECK(s->power == 5);                       // no charge, never negative
}

TEST(shipsim_gizmo_use_orbit_mask_gate_t381) {
    // The 0xc mask (TARGETORBIT|TARGETSURFACE) is a COMMIT GATE at
    // 0x4c928..0x4c942: a row shaped identically but WITHOUT those bits
    // decrements and charges NOTHING.
    as::ShipSim sim(1);
    sim.setDesigns(mkNanaDesigns(/*orbit=*/false));
    sim.addShip(mkNanaShip(14));
    as::Ship* s = sim.findShip(14);
    s->orderType = 1; s->dispatcherGate = 1;
    auto rep = sim.commitShot(14, 1);
    CHECK(rep.flags == 0);                      // gate word 0
    CHECK(s->inv[13].use == 2);                 // DEC paid
    CHECK(s->power == 90);                      // mask gate: no charge
}

TEST(shipsim_invasion_launch_consumes_need_not_all_t381) {
    // Ignatz 00:28:48 EXACT: SIX modules, one active shield (units=1) ->
    // need = min(6, 1+1) = 2 -> slots 2 and 3 cleared, 4..7 SURVIVE.
    as::ShipSim sim(1);
    sim.setDesigns(mkNanaDesigns());
    sim.addShip(mkIgnatz(22));
    as::Ship* s = sim.findShip(22);
    int consumed = sim.resolveInvasion(22, 1);
    CHECK(consumed == 2);
    CHECK(s->inv[2].cidx == 0xff && s->inv[3].cidx == 0xff);
    CHECK(s->inv[4].cidx == as::kCidxInvasionModule);
    CHECK(s->inv[5].cidx == as::kCidxInvasionModule);
    CHECK(s->inv[6].cidx == as::kCidxInvasionModule);
    CHECK(s->inv[7].cidx == as::kCidxInvasionModule);
    CHECK(s->invFilled == 8);                   // two clearSlot filled-decs
    CHECK(s->inv[0].cidx == 29 && s->inv[1].cidx == 18);   // non-modules kept
    CHECK(s->inv[8].cidx == 43 && s->inv[9].cidx == 43);
}

TEST(shipsim_invasion_need_capped_by_module_count_t381) {
    // Cap law 0x3a327: need := count; if (count > shieldUnits) need :=
    // shieldUnits + 1. shieldUnits 10 >= count 6 -> need stays 6 = ALL
    // consumed (the count, not shieldUnits+1 = 11).
    as::ShipSim sim(1);
    sim.setDesigns(mkNanaDesigns());
    sim.addShip(mkIgnatz(22));
    as::Ship* s = sim.findShip(22);
    CHECK(sim.resolveInvasion(22, 10) == 6);
    for (int i = 2; i <= 7; ++i)
        CHECK(s->inv[i].cidx == 0xff);
    CHECK(s->invFilled == 4);
}

TEST(shipsim_invasion_zero_shields_consumes_one_t381) {
    // Unshielded objective: deficit 0 -> need = 0 + 1 = 1 — exactly the
    // FIRST module in walk order (slot 2), not the last, not all.
    as::ShipSim sim(1);
    sim.setDesigns(mkNanaDesigns());
    sim.addShip(mkIgnatz(22));
    as::Ship* s = sim.findShip(22);
    CHECK(sim.resolveInvasion(22, 0) == 1);
    CHECK(s->inv[2].cidx == 0xff);
    CHECK(s->inv[3].cidx == as::kCidxInvasionModule);
}

TEST(shipsim_invasion_no_modules_consumes_nothing_t381) {
    // count 0 -> need = min(0, x+1) = 0; state untouched (phantom slots are
    // not equipment — the walk window is invCap).
    as::ShipSim sim(1);
    sim.setDesigns(mkNanaDesigns());
    auto ship = mkIgnatz(22);
    for (int i = 2; i <= 7; ++i) { ship.inv[i].cidx = 0xff; }
    ship.invFilled = 4;
    // Phantom module beyond cap: NOT counted, NOT consumed.
    ship.inv[10].cidx = as::kCidxInvasionModule;
    sim.addShip(ship);
    as::Ship* s = sim.findShip(22);
    CHECK(sim.resolveInvasion(22, 5) == 0);
    CHECK(s->inv[10].cidx == as::kCidxInvasionModule);   // phantom survives
    CHECK(s->invFilled == 4);
}
