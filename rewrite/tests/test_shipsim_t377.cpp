// SPDX-License-Identifier: GPL-3.0-or-later

// t377R MAGNETRON USE-SITE pins — ShipSim::useMagnetron, the dispatcher-
// entry composition of the orderType-2 handler (FUN_0004ca50) magnetron leg
// (case tree 0x4cd0d..0x4cd43). Evidence: docs/re/_wip_t377.md S2 (C1..C8
// verbatim static + three corrections) / S3 (landing contract); witness M1
// docs/re/ships.md S64 (s28 INSTANT jump, POWER 90->80 = gizmos.txt row 60
// 'Power 10' EXACT, ring slot REMOVED same event). Laws pinned:
//   C7 prologue DEC BEFORE the handler, mode-1-only, ungated by handler-side
//     gates (gate-fail still consumes);
//   C1 CORRECTED range polarity (FAIL iff dist < Range*32; Range==0 skips);
//   C2 commit tests bit0 ONLY (TARGETLANE is a return flag);
//   C3 charge min(power,cost) at entry;
//   C4 single-use via clearSlot; mode-0 probe lands nothing.
// NO vendor coordinates are pinned (S64 neg-(a): which star is unreconciled)
// — the placement pin asserts the FORM (star triple + (0,-200,0) + two LCG
// draws %200, snapped to the 32-grid) computed from the sim's own seed.
// NO OQ row closes on these facts (user-gated; OQ-019 residue).
#include "game/shipsim.h"
#include "harness.h"

#include <cmath>
#include <utility>
#include <vector>

namespace as = ascend::game;

namespace {

// gizmos.txt row 60 Lane Magnetron as MEASURED in loaded RAM
// (scripts/r377_design_rows.py, t377: cat=5 flags=0x0002(TARGETLANE)
// power=10 range=50 level=0 numUses=1).
as::SimDesign magnetronRow(int32_t uses = 1) {
    as::SimDesign d;
    d.cat = 5; d.power = 10; d.range = 50; d.numUses = uses;
    d.targetLane = true;
    return d;
}
std::vector<as::SimDesign> mkMagDesigns(int32_t uses = 1) {
    std::vector<as::SimDesign> t(0x4a);
    t[0x3c] = magnetronRow(uses);
    return t;
}
// M1-class ship: s28 Guandagnini Vernunft, power 90, InSystem, magnetron in
// ring slot 14 (M1's slot), invCap 16.
as::Ship mkMagShip(int id, uint16_t use = 1) {
    as::Ship s;
    s.id = id; s.owner = 0; s.kind = as::OrderKind::InSystem;
    s.pos[0] = -1184; s.pos[1] = 1344; s.pos[2] = -1184;   // M1 start
    s.power = 90; s.powerMax = 90;
    s.invCap = 16; s.invFilled = 1;
    s.inv[14].cidx = 0x3c; s.inv[14].use = use;
    s.activeSlot = 14;
    return s;
}
// A target star far enough to pass the CORRECTED gate (dist ~4500 >= 1600).
// y = -1560 so star.y + (-200) = -1760 (M1's landing y, form corroboration —
// the pin computes the expected value from the LCG, never asserts M1's x/z).
as::SimStar farStar(int id) {
    as::SimStar st;
    st.id = id; st.pos[0] = 1280; st.pos[1] = -1560; st.pos[2] = 1344;
    return st;
}
float snapRef(float v) {
    const float a = v < 0 ? -v : v;
    const float r = std::round(a / 32.0f) * 32.0f;
    return v < 0 ? -r : r;
}

}  // namespace

TEST(shipsim_magnetron_commit_burn_exact_t377) {
    // M1: mode-1 commit on the active magnetron slot burns EXACTLY
    // min(design power, power) = 10 (90 -> 80), sets flags bit0 (affordable
    // && rangeOK) + bit1 (TARGETLANE return flag), kind byte stays 4.
    as::ShipSim sim(1, 1253);
    sim.setDesigns(mkMagDesigns());
    sim.addStar(farStar(0));
    sim.addShip(mkMagShip(28));
    as::Ship* s = sim.findShip(28);
    s->targetStar = 0;
    s->targetPos[0] = 1280; s->targetPos[1] = -1560; s->targetPos[2] = 1344;
    auto rep = sim.useMagnetron(28, 1);
    CHECK(rep.ranHandler);
    CHECK(rep.committed);
    CHECK(rep.cost == 10);
    CHECK(s->power == 80);                    // 90 -> 80 = 'Power 10' EXACT
    CHECK((rep.flags & 1) != 0);              // C2 bit0 commit condition
    CHECK((rep.flags & 2) != 0);              // TARGETLANE flag in the word
    CHECK(s->kind == as::OrderKind::InSystem);
    CHECK(rep.placed);
}

TEST(shipsim_magnetron_slot_consumed_once_t377) {
    // C4 + M1: the ring slot is REMOVED in the same event (single-use).
    as::ShipSim sim(1, 1253);
    sim.setDesigns(mkMagDesigns());
    sim.addStar(farStar(0));
    sim.addShip(mkMagShip(28));
    as::Ship* s = sim.findShip(28);
    s->targetStar = 0;
    s->targetPos[0] = 1280; s->targetPos[1] = -1560; s->targetPos[2] = 1344;
    auto rep = sim.useMagnetron(28, 1);
    CHECK(rep.placed);
    CHECK(s->inv[14].cidx == 0xff);           // slot GONE same event
    CHECK(s->invFilled == 0);                 // filled dec (0x496f7)
}

TEST(shipsim_magnetron_placement_form_t377) {
    // FUN_00021f58 FORM (never vendor coordinates — S64 neg-(a)): pos :=
    // star triple + (0,-200,0) + TWO draws %200 on x/z, quantizer-snapped on
    // ALL THREE axes (M1 landing on the 32-grid). Expected value computed
    // from the sim's own isolated LCG stream (seed 1, first two draws).
    as::ShipSim sim(1, 1253);
    sim.setDesigns(mkMagDesigns());
    sim.addStar(farStar(0));
    sim.addShip(mkMagShip(28));
    as::Ship* s = sim.findShip(28);
    s->targetStar = 0;
    s->targetPos[0] = 1280; s->targetPos[1] = -1560; s->targetPos[2] = 1344;
    as::Lcg l; l.state = 1;
    const int jx = l.next();
    const int jz = l.next();
    const float ex = snapRef(1280.0f + static_cast<float>(jx % 200));
    const float ey = snapRef(-1560.0f - 200.0f);
    const float ez = snapRef(1344.0f + static_cast<float>(jz % 200));
    auto rep = sim.useMagnetron(28, 1);
    CHECK(rep.placed);
    CHECK(s->pos[0] == ex);
    CHECK(s->pos[1] == ey);
    CHECK(s->pos[2] == ez);
    CHECK(std::fmod(s->pos[0], 32.0f) == 0.0f);   // quantizer g=32 at rest
    CHECK(std::fmod(s->pos[1], 32.0f) == 0.0f);
    CHECK(std::fmod(s->pos[2], 32.0f) == 0.0f);
    CHECK(sim.totalRngDraws() == 2);              // exactly two draws
}

TEST(shipsim_magnetron_no_second_use_t377) {
    // numUses 1: after the commit the slot is 0xff, so a repeat call runs
    // NOTHING (no DEC, no charge, no placement) — digest identical.
    as::ShipSim sim(1, 1253);
    sim.setDesigns(mkMagDesigns());
    sim.addStar(farStar(0));
    sim.addShip(mkMagShip(28));
    as::Ship* s = sim.findShip(28);
    s->targetStar = 0;
    s->targetPos[0] = 1280; s->targetPos[1] = -1560; s->targetPos[2] = 1344;
    auto r1 = sim.useMagnetron(28, 1);
    CHECK(r1.committed);
    const uint64_t d1 = sim.digest();
    const int32_t p1 = s->power;
    auto r2 = sim.useMagnetron(28, 1);
    CHECK(!r2.ranHandler);                   // 0xff active slot: refused
    CHECK(!r2.committed);
    CHECK(s->power == p1);
    CHECK(sim.digest() == d1);
}

TEST(shipsim_magnetron_zero_carried_t377) {
    // A ship that carries no magnetron never fires the seam: activeSlot -1
    // (never selected; the vendor entry derefs [+0x63] — named divergence)
    // and an empty 0xff active slot both refuse with ZERO state change.
    as::ShipSim sim(1, 1253);
    sim.setDesigns(mkMagDesigns());
    sim.addStar(farStar(0));
    as::Ship a = mkMagShip(1);
    a.activeSlot = -1;
    sim.addShip(a);
    as::Ship b = mkMagShip(2);
    b.inv[14].cidx = 0xff; b.invFilled = 0;
    sim.addShip(b);
    const uint64_t d0 = sim.digest();
    auto ra = sim.useMagnetron(1, 1);
    auto rb = sim.useMagnetron(2, 1);
    CHECK(!ra.ranHandler && !ra.committed);
    CHECK(!rb.ranHandler && !rb.committed);
    CHECK(sim.findShip(1)->power == 90);
    CHECK(sim.findShip(2)->power == 90);
    CHECK(sim.digest() == d0);
}

TEST(shipsim_magnetron_gate_fail_decs_still_t377) {
    // C7 (the mutant-visible seam): the prologue DEC runs BEFORE the
    // handler and is UNGATED by handler-side gates — a use rejected by the
    // CORRECTED range gate (dist 800 < Range*32 = 1600, TOO-CLOSE) still
    // consumes a charge (use 3 -> 2) and charges NO power (bit0 fail -> the
    // charge tail is behind the commit test). Zero-witness law, flagged.
    as::ShipSim sim(1, 1253);
    sim.setDesigns(mkMagDesigns(3));          // numUses 3 (M2-shape row)
    sim.addStar(farStar(0));
    sim.addShip(mkMagShip(28, 3));
    as::Ship* s = sim.findShip(28);
    s->targetStar = 0;
    // target 800 away on x: dist 800 < 1600 -> rangeOK false (TOO-CLOSE).
    s->targetPos[0] = -1184.0f + 800.0f;
    s->targetPos[1] = 1344.0f; s->targetPos[2] = -1184.0f;
    auto rep = sim.useMagnetron(28, 1);
    CHECK(rep.ranHandler);
    CHECK(!rep.committed);                    // bit0 clear -> fail leg
    CHECK((rep.flags & 1) == 0);
    CHECK(s->power == 90);                    // NO charge on gate fail
    CHECK(s->inv[14].use == 2);               // DEC STILL APPLIED (C7)
    CHECK(s->inv[14].cidx == 0x3c);           // slot NOT consumed
    CHECK(s->pos[0] == -1184.0f);             // nothing placed
}

TEST(shipsim_magnetron_unaffordable_decs_still_t377) {
    // C7 on the affordability axis: power 5 < cost 10 -> bit0 clear, no
    // charge, DEC still consumed.
    as::ShipSim sim(1, 1253);
    sim.setDesigns(mkMagDesigns(3));
    sim.addStar(farStar(0));
    as::Ship s0 = mkMagShip(28, 3);
    s0.power = 5;
    sim.addShip(s0);
    as::Ship* s = sim.findShip(28);
    s->targetStar = 0;
    s->targetPos[0] = 1280; s->targetPos[1] = -1560; s->targetPos[2] = 1344;
    auto rep = sim.useMagnetron(28, 1);
    CHECK(rep.ranHandler);
    CHECK(!rep.committed);
    CHECK((rep.flags & 1) == 0);
    CHECK(s->power == 5);                     // cost = min(10,5) NOT charged
    CHECK(s->inv[14].use == 2);               // DEC STILL APPLIED
}

TEST(shipsim_magnetron_mode0_probe_lands_nothing_t377) {
    // 0x4cbcd: mode != 1 exits BEFORE any store — flags + cost reported,
    // no DEC, no charge, no placement (digest identical after the probe).
    as::ShipSim sim(1, 1253);
    sim.setDesigns(mkMagDesigns());
    sim.addStar(farStar(0));
    sim.addShip(mkMagShip(28));
    as::Ship* s = sim.findShip(28);
    s->targetStar = 0;
    s->targetPos[0] = 1280; s->targetPos[1] = -1560; s->targetPos[2] = 1344;
    const uint64_t d0 = sim.digest();
    auto rep = sim.useMagnetron(28, 0);
    CHECK(rep.ranHandler);
    CHECK(!rep.committed);                    // mode-1-only commit edges
    CHECK(rep.cost == 10);                    // entry value reported
    CHECK((rep.flags & 1) != 0);              // probe sees the gates
    CHECK((rep.flags & 2) != 0);
    CHECK(s->power == 90);
    CHECK(s->inv[14].use == 1);               // no DEC on probe
    CHECK(s->inv[14].cidx == 0x3c);
    CHECK(s->pos[0] == -1184.0f);
    CHECK(sim.totalRngDraws() == 0);          // no draws before the store leg
    CHECK(sim.digest() == d0);
}

TEST(shipsim_magnetron_nonmagnetron_cidx_no_leg_t377) {
    // Case-tree shape (0x4cd51): a DIFFERENT cidx under this seam passes the
    // generic gates (charge lands) but runs NO magnetron leg — no placement,
    // no slot consumption (the 0x20/0x34../0x3e bookkeeping legs are named
    // non-goals OUTSIDE the ship model; the sim returns for them).
    as::ShipSim sim(1, 1253);
    std::vector<as::SimDesign> t(0x4a);
    t[0x49] = as::SimDesign{};                // Invasion Module shape: cat 5
    t[0x49].power = 6; t[0x49].numUses = 3;   // cost 6 (M2's decrement)
    sim.setDesigns(t);
    sim.addStar(farStar(0));
    as::Ship s0 = mkMagShip(22, 3);
    s0.inv[14].cidx = 0x49;
    sim.addShip(s0);
    as::Ship* s = sim.findShip(22);
    s->targetStar = 0;
    s->targetPos[0] = 1280; s->targetPos[1] = -1560; s->targetPos[2] = 1344;
    auto rep = sim.useMagnetron(22, 1);
    CHECK(rep.ranHandler);
    CHECK(rep.committed);
    CHECK(rep.cost == 6);
    CHECK(s->power == 84);                    // 90 - 6 (M2-class decrement)
    CHECK(!rep.placed);
    CHECK(s->pos[0] == -1184.0f);
    CHECK(s->inv[14].cidx == 0x49);           // NOT consumed
    CHECK(s->inv[14].use == 2);               // DEC law is cidx-independent
}

TEST(shipsim_magnetron_targetlane_not_a_gate_t377) {
    // C2: the commit test 0x4cbd4 tests bit0 ONLY. A magnetron row WITHOUT
    // the TARGETLANE flag commits exactly like the flagged row (flags carry
    // bit0, no bit1; burn exact; slot consumed). Pin exists so the
    // "gate also tests bit1" mutant cannot survive (flag consumers are
    // elsewhere, unbanked).
    as::ShipSim sim(1, 1253);
    std::vector<as::SimDesign> t = mkMagDesigns();
    t[0x3c].targetLane = false;
    sim.setDesigns(t);
    sim.addStar(farStar(0));
    sim.addShip(mkMagShip(28));
    as::Ship* s = sim.findShip(28);
    s->targetStar = 0;
    s->targetPos[0] = 1280; s->targetPos[1] = -1560; s->targetPos[2] = 1344;
    auto rep = sim.useMagnetron(28, 1);
    CHECK(rep.committed);
    CHECK((rep.flags & 1) != 0);
    CHECK((rep.flags & 2) == 0);              // flag word, not a gate
    CHECK(s->power == 80);
    CHECK(rep.placed);
    CHECK(s->inv[14].cidx == 0xff);
}

TEST(shipsim_magnetron_target_gate_shape_t377) {
    // FUN_000220a8 target-gate surrogate shape (S3): a ship OUTSIDE the
    // cited InSystem kind pays DEC + charge (both precede the case tree in
    // the bytes) and lands NOTHING (placement refused). Zero-witness
    // composition consequence, flagged at the declaration.
    as::ShipSim sim(1, 1253);
    sim.setDesigns(mkMagDesigns(3));
    sim.addStar(farStar(0));
    as::Ship s0 = mkMagShip(28, 3);
    s0.kind = as::OrderKind::Move;
    sim.addShip(s0);
    as::Ship* s = sim.findShip(28);
    s->targetStar = 0;
    s->targetPos[0] = 1280; s->targetPos[1] = -1560; s->targetPos[2] = 1344;
    auto rep = sim.useMagnetron(28, 1);
    CHECK(rep.ranHandler);
    CHECK(rep.committed);                     // gates passed (kind is not a
                                              // handler gate, only a leg gate)
    CHECK(!rep.placed);
    CHECK(s->power == 80);                    // charge PAID
    CHECK(s->inv[14].use == 2);               // DEC PAID
    CHECK(s->inv[14].cidx == 0x3c);           // slot NOT consumed
    CHECK(s->pos[0] == -1184.0f);             // no placement
    CHECK(s->kind == as::OrderKind::Move);
}

TEST(shipsim_magnetron_determinism_t377) {
    // Same seed + same inputs -> same digest AND same landing point; seed 2
    // lands elsewhere (the draws feed the placement).
    auto run = [](unsigned seed) {
        as::ShipSim sim(seed, 1253);
        sim.setDesigns(mkMagDesigns());
        sim.addStar(farStar(0));
        sim.addShip(mkMagShip(28));
        as::Ship* s = sim.findShip(28);
        s->targetStar = 0;
        s->targetPos[0] = 1280; s->targetPos[1] = -1560;
        s->targetPos[2] = 1344;
        sim.useMagnetron(28, 1);
        return std::pair<uint64_t, float>(sim.digest(), s->pos[0]);
    };
    auto a = run(1), b = run(1), c = run(2);
    CHECK(a.first == b.first);
    CHECK(a.second == b.second);
    CHECK(a.first != c.first);
}
