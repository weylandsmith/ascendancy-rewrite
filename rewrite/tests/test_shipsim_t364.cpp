// t364 PER-SHIP COMBAT ROUND pins — the stance setter + volley tail
// (FUN_0004a55c 0x4a55c..0x4a601), the companion scan (FUN_0004a604), the
// dispatcher ammo law (0x4a360 0x4a373..0x4a397), the gun handler gates
// (0x4b8e4: same-system 0x4b982, range 0x4b9bd incl. the C9 range-0
// unlimited leg, engage flag 0x4bad4), the two-layer clamped absorb
// (0x4b740 0x4b7a7..0x4b890), the mode law (C3: APPLY + death behind the
// 0x4b7f1 mode==1 cmp; charge 0x4c614 fires even on zero damage), the death
// finalizer (C4: 0x49d2c -> 0x249b4 owner 0xffff/kind 0) and the resolver
// legs (C6 exclusive Leg A, C8 Leg B first-eligible). Law sources:
// docs/re/_wip_t364.md S1..S5 (verbatim disasm, both backends) + combat.md
// S2h/S2k. NO OQ row closes on these facts (user-gated; OQ-019 residue).
#include "game/shipsim.h"
#include "harness.h"

#include <vector>

namespace as = ascend::game;

namespace {

// Cat-0 gun row (damage = rowWeapon == derived +0x52 law; Range/Power per
// the file columns; GZ_TARGETSHIP set — all 10 shipped cat-0 rows carry it).
as::SimDesign gunRow(int32_t power, int32_t range, int32_t dmg,
                     int32_t uses = 0) {
    as::SimDesign d;
    d.cat = 0; d.power = power; d.range = range; d.level = dmg;
    d.numUses = uses; d.targetShip = true; d.rowWeapon = dmg;
    return d;
}
as::SimDesign shieldRow(int32_t cost, int32_t level) {
    as::SimDesign d;
    d.cat = 1; d.power = cost; d.level = level;
    d.upkeepGate = true; d.rowShield = level;
    return d;
}
std::vector<as::SimDesign> mkCombatDesigns() {
    std::vector<as::SimDesign> t(0x4a);
    t[10] = gunRow(2, 25, 6);                     // the engagement gun
    t[11] = gunRow(1, 10, 3);                     // SHORT range (volley order)
    t[12] = gunRow(2, 0, 5);                      // C9 range-0 = UNLIMITED
    t[13] = gunRow(3, 25, 0);                     // zero-damage gun (charge pin)
    t[0x2f] = gunRow(4, 40, 2); t[0x2f].special1 = 20;   // Carbonizer override
    t[0x49] = as::SimDesign{}; t[0x49].cat = 5; t[0x49].power = 10;
    return t;
}
as::Ship mkCombatShip(int id, int owner, uint32_t sysId, float x) {
    as::Ship s;
    s.id = id; s.owner = owner; s.kind = as::OrderKind::InSystem;
    s.systemId = sysId;
    s.pos[0] = x;
    s.integrity = 10; s.maxIntegrity = 10;
    s.power = 10; s.powerMax = 10;
    s.invCap = 1;
    return s;
}

}  // namespace

TEST(shipsim_stance_map_t364) {
    // C2 map 0->2, 1->1, 2->1, 3->0 (the banked "arg2->0" is SUPERSEDED);
    // power==0 refuses with ZERO state change (ret 0x4a56f precedes stores).
    as::ShipSim sim(1);
    sim.setDesigns(mkCombatDesigns());
    auto a = mkCombatShip(1, 0, 7, 0);
    auto b = mkCombatShip(2, 1, 7, 32 * 20);      // range 25*32 = 800 covers it
    a.inv[0].cidx = 10; a.inv[0].use = 1;
    sim.addShip(a); sim.addShip(b);
    as::Ship* pa = sim.findShip(1);
    // Handler-1/2 returns are NOT banked (C8) — the sim only claims the GUN
    // handler's bit0; non-gun stances are checked on STATE, not the return.
    // ORDER MATTERS: each step starts from a DIFFERENT handler value than
    // the arg-under-test writes, so a wrong-map mutant cannot hide behind
    // the previous stance (t364 M1 triage).
    sim.setStance(1, 1, 2); CHECK(pa->orderType == 1);
    sim.setStance(1, 0, 2); CHECK(pa->orderType == 2);   // arg0 -> 2
    sim.setStance(1, 2, 2); CHECK(pa->orderType == 1);   // arg2 -> 1 (NOT 0)
    CHECK(sim.setStance(1, 3, 2)); CHECK(pa->orderType == 0);  // arg3 -> 0
    CHECK(!sim.setStance(1, 9, 2));               // vendor asserts; sim refuses
    CHECK(pa->dispatcherGate == 1);               // [+0x62] set by every accept
    CHECK(pa->fireTarget == 2);
    // Refusal arm: zero state change.
    auto z = mkCombatShip(3, 0, 7, 0); z.power = 0; z.invCap = 0;
    sim.addShip(z);
    CHECK(!sim.setStance(3, 3, 2));
    as::Ship* pz = sim.findShip(3);
    CHECK(pz->dispatcherGate == 0 && pz->orderType == 0 && pz->fireTarget == -1);
}

TEST(shipsim_volley_active_slot_last_scanned_t364) {
    // C5 QUIRK: the [+0x63] store runs for EVERY cat-0 slot BEFORE its call
    // (0x4a5ee precedes 0x4a5f1, result ignored) — after the volley,
    // activeSlot == the LAST cat-0 scanned (slot 1), while the RETURN value
    // is the last slot with bit0 (slot 0, the in-range gun). Mutant "store
    // only on hit" must fail HERE.
    as::ShipSim sim(1);
    sim.setDesigns(mkCombatDesigns());
    auto a = mkCombatShip(1, 0, 7, 0);
    auto b = mkCombatShip(2, 1, 7, 32 * 20);
    a.invCap = 2; a.inv[0].cidx = 10; a.inv[0].use = 1;   // range 25: HITS
    a.inv[1].cidx = 11; a.inv[1].use = 1;         // range 10 (limit 320): MISSES
    sim.addShip(a); sim.addShip(b);
    as::Ship* pa = sim.findShip(1);
    pa->orderType = 0; pa->dispatcherGate = 1; pa->fireTarget = 2; pa->activeSlot = 0;
    CHECK(sim.volleyTail(*pa) == 0);              // edi: last bit0 slot == 0
    CHECK(pa->activeSlot == 1);                   // LAST SCANNED, not last hit
}

TEST(shipsim_mode0_probe_no_state_t364) {
    // C3: mode != 1 exits at 0x4b7f6 before APPLY and death; NO charge
    // (0x4bb6c routes to 0x4c614 only on mode==1); NO DEC (0x4a38b jne).
    // Flags DO set (hypothetical chain): dmg 6 vs shields 4 -> bit2.
    as::ShipSim sim(1);
    sim.setDesigns(mkCombatDesigns());
    auto a = mkCombatShip(1, 0, 7, 0);
    auto b = mkCombatShip(2, 1, 7, 32 * 20);
    b.shields = 4;
    std::vector<as::SimDesign> t = mkCombatDesigns();
    t[10].numUses = 1;                            // FINITE ammo: a mode-0 DEC
                                                  // becomes observable (M5)
    sim.setDesigns(t);
    a.inv[0].cidx = 10; a.inv[0].use = 1;
    sim.addShip(a); sim.addShip(b);
    as::Ship* pa = sim.findShip(1);
    pa->orderType = 0; pa->dispatcherGate = 1; pa->fireTarget = 2; pa->activeSlot = 0;
    auto r = sim.commitShot(1, 0);
    CHECK(r.shots == 1);
    CHECK((r.flags & 2) != 0);
    CHECK(pa->power == 10);                       // no charge
    CHECK(pa->inv[0].use == 1);                   // no DEC
    as::Ship* pb = sim.findShip(2);
    CHECK(pb->shields == 4 && pb->integrity == 10);   // nothing lands
}

TEST(shipsim_two_layer_absorb_t364) {
    // K5 verbatim: absorb = MIN(dmg, shield) spill spills to hull (clamped);
    // flags bit2 on shield overflow ONLY; charge MIN(cost, power) on mode 1.
    as::ShipSim sim(1);
    sim.setDesigns(mkCombatDesigns());
    auto a = mkCombatShip(1, 0, 7, 0);
    auto b = mkCombatShip(2, 1, 7, 32 * 20);
    b.shields = 4; b.integrity = 10;              // dmg 6: 4 shield + 2 hull
    std::vector<as::SimDesign> t = mkCombatDesigns();
    t[10].numUses = 1;                            // finite ammo: DEC observable
    sim.setDesigns(t);
    a.inv[0].cidx = 10; a.inv[0].use = 1;
    sim.addShip(a); sim.addShip(b);
    as::Ship* pa = sim.findShip(1);
    pa->orderType = 0; pa->dispatcherGate = 1; pa->fireTarget = 2; pa->activeSlot = 0;
    auto r = sim.commitShot(1, 1);
    CHECK(r.shieldAbsorb == 4 && r.hullAbsorb == 2);
    CHECK((r.flags & 2) != 0 && (r.flags & 4) == 0);  // spill 2 < hull 10
    as::Ship* pb = sim.findShip(2);
    CHECK(pb->shields == 0 && pb->integrity == 8);
    CHECK(pa->power == 8);                        // cost MIN(2, 10)
    CHECK(pa->inv[0].use == 0);                   // THE DEC (0x4a390)
}

TEST(shipsim_lethal_clamp_death_t364) {
    // Hull clamp flags when spill >= hull (0x4b7e0 jl: flag leg on NOT-less);
    // hull < 1 -> death finalizer C4: owner -1 (0xffff), kind 0, act 0.
    as::ShipSim sim(1);
    sim.setDesigns(mkCombatDesigns());
    auto a = mkCombatShip(1, 0, 7, 0);
    auto b = mkCombatShip(2, 1, 7, 32 * 20);
    b.shields = 0; b.integrity = 3;               // dmg 6: clamp 3, flags bit4
    b.act = 2;
    a.inv[0].cidx = 10;
    sim.addShip(a); sim.addShip(b);
    as::Ship* pa = sim.findShip(1);
    pa->orderType = 0; pa->dispatcherGate = 1; pa->fireTarget = 2; pa->activeSlot = 0;
    auto r = sim.commitShot(1, 1);
    CHECK(r.destroyed == 2);
    CHECK((r.flags & 4) != 0);
    CHECK(r.hullAbsorb == 3);                     // clamped, never negative
    as::Ship* pb = sim.findShip(2);
    CHECK(pb->owner == -1);                       // 0xffff mirror (law A3)
    CHECK(pb->kind == as::OrderKind::NoOrder);    // finalizer 0x24a00
    CHECK(pb->act == 0);
    CHECK(sim.firstCarrier(0x49) == nullptr);     // corpse filter (C4/A3)
}

TEST(shipsim_ammo_law_t364) {
    // NumUses != 0: use word is the ammo. DEC on mode-1 ONLY, BEFORE the
    // handler; use==0 pre-shot skips the handler ENTIRELY (no charge, no
    // damage, no shot). numUses==0 == unlimited (vendor esi law 0x4a37b).
    as::ShipSim sim(1);
    sim.setDesigns(mkCombatDesigns());            // t[10] numUses 0 -> make 2
    std::vector<as::SimDesign> t = sim.designs();
    t[10].numUses = 2;
    sim.setDesigns(t);
    auto a = mkCombatShip(1, 0, 7, 0);
    auto b = mkCombatShip(2, 1, 7, 32 * 20);
    a.inv[0].cidx = 10; a.inv[0].use = 2;
    sim.addShip(a); sim.addShip(b);
    as::Ship* pa = sim.findShip(1);
    pa->orderType = 0; pa->dispatcherGate = 1; pa->fireTarget = 2; pa->activeSlot = 0;
    CHECK(sim.companionScan(*pa) == -1);          // eligible (use != 0)
    CHECK(sim.commitShot(1, 1).shots == 1);       // use 2 -> 1
    CHECK(pa->inv[0].use == 1);
    CHECK(sim.commitShot(1, 1).shots == 1);       // use 1 -> 0 (last shot)
    CHECK(pa->inv[0].use == 0);
    auto r = sim.commitShot(1, 1);                // out of ammo
    CHECK(r.shots == 0 && r.hullAbsorb == 0 && r.shieldAbsorb == 0);
    CHECK(pa->power == 10 - 2 - 2);               // no third charge
    CHECK(sim.companionScan(*pa) == 0);           // ineligible sentinel
}

TEST(shipsim_gates_k1_range_t364) {
    // K1 same-system (both kind 4 + equal systemId, 0x4b982..0x4b997); range
    // gate design[+0x3a]<<5 with boundary INCLUSIVE (0x4baae jbe) and the
    // status bit-2x [inferred]; range-0 = UNLIMITED (C9, je 0x4bad4 keeps the
    // -1 sentinel). Gate failures charge NOTHING (exit 0x4c780).
    as::ShipSim sim(1);
    sim.setDesigns(mkCombatDesigns());
    auto a = mkCombatShip(1, 0, 7, 0);
    auto b = mkCombatShip(2, 1, 8, 32 * 20);      // DIFFERENT system
    a.inv[0].cidx = 10;
    sim.addShip(a); sim.addShip(b);
    as::Ship* pa = sim.findShip(1);
    pa->orderType = 0; pa->dispatcherGate = 1; pa->fireTarget = 2; pa->activeSlot = 0;
    CHECK(sim.commitShot(1, 1).shots == 0);
    CHECK(pa->power == 10);                       // gate fail: no charge
    sim.setSystemId(2, 7);                        // same system now
    sim.findShip(2)->pos[0] = 801;                // 1 past limit 800
    CHECK(sim.commitShot(1, 1).shots == 0);
    sim.findShip(2)->pos[0] = 800;                // exactly ON limit: hits
    CHECK(sim.commitShot(1, 1).shots == 1);
    // C9: range-0 gun hits across the map.
    sim.findShip(2)->pos[0] = 500000;
    sim.findShip(2)->integrity = 10;              // reset the earlier 6-chip
    pa->inv[0].cidx = 12;                         // Range 0, dmg 5
    auto r = sim.commitShot(1, 1);
    CHECK(r.shots == 1 && r.hullAbsorb == 5);
}

TEST(shipsim_charge_even_zero_damage_t364) {
    // 0x4bb64 or 0x10 (damage==0 skip) FALLS THROUGH to 0x4bb6c — the mode-1
    // charge runs anyway; only the HIT is skipped (shots == 0, flags 0x10).
    as::ShipSim sim(1);
    sim.setDesigns(mkCombatDesigns());            // t[13]: dmg 0, cost 3
    auto a = mkCombatShip(1, 0, 7, 0);
    auto b = mkCombatShip(2, 1, 7, 32 * 20);
    a.inv[0].cidx = 13;
    sim.addShip(a); sim.addShip(b);
    as::Ship* pa = sim.findShip(1);
    pa->orderType = 0; pa->dispatcherGate = 1; pa->fireTarget = 2; pa->activeSlot = 0;
    auto r = sim.commitShot(1, 1);
    CHECK(r.shots == 0);
    CHECK((r.flags & 0x10) != 0);
    CHECK(pa->power == 7);                        // MIN(3, 10) charged
    as::Ship* pb = sim.findShip(2);
    CHECK(pb->integrity == 10 && pb->shields == 0);
}

TEST(shipsim_carbonizer_override_t364) {
    // cidx 0x2f: damage := design[+0x4a] Special1 (0x4bb40), NOT +0x52.
    as::ShipSim sim(1);
    sim.setDesigns(mkCombatDesigns());
    auto a = mkCombatShip(1, 0, 7, 0);
    auto b = mkCombatShip(2, 1, 7, 32 * 30);      // range 40*32 covers
    b.integrity = 30;                             // survive the 20 (clamp!)
    a.inv[0].cidx = 0x2f;
    sim.addShip(a); sim.addShip(b);
    as::Ship* pa = sim.findShip(1);
    pa->orderType = 0; pa->dispatcherGate = 1; pa->fireTarget = 2; pa->activeSlot = 0;
    auto r = sim.commitShot(1, 1);
    CHECK(r.hullAbsorb == 20);                    // Special1, not rowWeapon 2
}

TEST(shipsim_leg_a_exclusive_t364) {
    // C6: carrier found -> engagement stores [+0x62]:=0, [+0x63]:=0,
    // [+0x67]:=1, [+0x68]:=objective, RETURN — NO gunfire in the same
    // resolution even at mode 1, even with a shooter present. Mutant
    // "fall through to Leg B" must fail HERE.
    as::ShipSim sim(1);
    sim.setDesigns(mkCombatDesigns());
    auto carrier = mkCombatShip(1, 0, 7, 0);
    carrier.inv[0].cidx = 0x49;                   // Invasion Module
    auto shooter = mkCombatShip(2, 0, 7, 100);
    shooter.inv[0].cidx = 10;
    auto victim = mkCombatShip(3, 1, 7, 32 * 20);
    sim.addShip(carrier); sim.addShip(shooter); sim.addShip(victim);
    auto r = sim.engageRound(0, 3, /*objectivePlanetShielded=*/false, 1);
    CHECK(r.carrier == 1 && r.legACommitted);
    CHECK(r.shooter == -1 && r.shots == 0);
    as::Ship* pc = sim.findShip(1);
    CHECK(pc->dispatcherGate == 0 && pc->activeSlot == -1);
    CHECK(pc->orderType == 1 && pc->fireTarget == 3);
    as::Ship* pv = sim.findShip(3);
    CHECK(pv->integrity == 10);                   // nothing fired
}

TEST(shipsim_leg_b_first_eligible_t364) {
    // C8: FIRST ship in list order passing kind-4 + companionScan + stance
    // (volley engage bit0 on THIS target). The out-of-ammo ship is skipped
    // (companionScan sentinel 0); the first ELIGIBLE one is picked even if a
    // later ship is stronger — no ranking anywhere (ai-dossier §6).
    as::ShipSim sim(1);
    sim.setDesigns(mkCombatDesigns());
    std::vector<as::SimDesign> t = mkCombatDesigns();
    t[9] = gunRow(6, 50, 13);
    t[10].numUses = 2;                            // so dry (use 0) is ineligible
    sim.setDesigns(t);
    auto dry = mkCombatShip(1, 0, 7, 0);          // gun with use 0, numUses 2
    dry.inv[0].cidx = 10; dry.inv[0].use = 0;
    auto first = mkCombatShip(2, 0, 7, 100);      // eligible, damage 6
    first.inv[0].cidx = 10; first.inv[0].use = 1;
    auto strong = mkCombatShip(3, 0, 7, 150);     // eligible too, later in list
    strong.inv[0].cidx = 9;                       // Nanomanipulator dmg 13
    auto victim = mkCombatShip(4, 1, 7, 32 * 20);
    sim.addShip(dry); sim.addShip(first); sim.addShip(strong);
    sim.addShip(victim);
    auto r = sim.engageRound(0, 4, true, 1);      // shielded -> Leg A skipped
    CHECK(r.shooter == 2);                        // FIRST eligible, not strongest
    CHECK(r.hullAbsorb == 6);                     // first's gun, not the 13
    as::Ship* pf = sim.findShip(2);
    CHECK(pf->dispatcherGate == 1 && pf->orderType == 0);
    CHECK(pf->fireTarget == 4);
    as::Ship* pd = sim.findShip(1);
    CHECK(pd->dispatcherGate == 0);               // skipped ships untouched
    CHECK(pd->fireTarget == -1);
}

TEST(shipsim_engagement_digest_t364) {
    // The engagement quadruple is engine state: identical runs agree; a
    // stance change diverges the digest.
    as::ShipSim A(5), B(5);
    A.setDesigns(mkCombatDesigns()); B.setDesigns(mkCombatDesigns());
    auto mk = []() {
        auto a = mkCombatShip(1, 0, 7, 0);
        a.inv[0].cidx = 10;
        auto b = mkCombatShip(2, 1, 7, 32 * 20);
        return std::pair<as::Ship, as::Ship>(a, b);
    };
    auto p = mk(); A.addShip(p.first); A.addShip(p.second);
    auto q = mk(); B.addShip(q.first); B.addShip(q.second);
    CHECK(A.digest() == B.digest());
    A.setStance(1, 3, 2);
    CHECK(A.digest() != B.digest());
}
