// SPDX-License-Identifier: GPL-3.0-or-later

// t365 ENGINE FLIP BRIDGE — implementation. Cited law executes INSIDE
// ShipSim (shipsim.cpp); this file is pure integration + the flagged
// surrogate ledger S1..S11 documented in campaign_fleet_bridge.h. No new law
// claims.
#include "game/campaign_fleet_bridge.h"

#include "game/economy.h"  // Gizmo, GizmoCat, requiresAvailable

#include <algorithm>

namespace ascend {
namespace game {

namespace {
constexpr int kSynthBase = 76;   // synthetic pop-reserve rows live at 76..83
constexpr int kMaxOwners = 8;
}  // namespace

CampaignFleetBridge::CampaignFleetBridge(unsigned campaignSeed)
    : sim_(campaignSeed) {}

void CampaignFleetBridge::ensureDesigns(const std::vector<Gizmo>& gizmos) {
    if (designsReady_) return;
    // Rows 0..75: the Gizmo parse of gizmos.txt IS the design table
    // (_wip_t363 S3b: loadGizmos reproduces the RAM-measured gate/cost/level
    // multisets EXACTLY). Derived-slot fields = recalc cat-switch law
    // (0x49b52..0x49b8e, shipsim.cpp recalcShip).
    designs_.assign(kSynthBase + kMaxOwners, SimDesign{});
    for (size_t i = 0; i < gizmos.size() && i < static_cast<size_t>(kSynthBase); ++i) {
        const Gizmo& g = gizmos[i];
        SimDesign& d = designs_[i];
        d.cat = static_cast<int>(g.cat);
        d.power = g.power;
        d.range = g.range;
        d.level = g.level;
        d.numUses = g.numUses;
        d.industry = g.industry;
        d.special1 = g.special1;
        d.upkeepGate = (g.flags & 32) != 0;   // TOGGLEABLE (gizmos.md §1)
        d.targetShip = (g.flags & 1) != 0;    // GZ_TARGETSHIP bitpos 0
        d.targetLane = (g.flags & 2) != 0;    // GZ_TARGETLANE bitpos 1
                                              // (row 60 Lane Magnetron
                                              // MEASURED flags=0x2, t377)
        switch (d.cat) {
            case 0: d.rowWeapon = g.level; break;
            case 1: d.rowShield = g.level; break;
            case 2: d.rowDrive = g.level; break;
            case 3: d.rowScanner = g.level; break;
            case 4: d.rowGenPower = g.power; break;
            default: break;
        }
    }
    // Rows 76..83: synthetic pop-reserve guns (S2). Range 0 = UNLIMITED is
    // the CITED C9 leg (0x4b9a3 je keeps the -1 sentinel); numUses 1 rides
    // the cited ammo law; targetShip true so the cited engage flag admits it
    // (the flag SET of a surrogate row is itself part of S2, flagged).
    for (int o = 0; o < kMaxOwners; ++o) {
        SimDesign& d = designs_[kSynthBase + o];
        d.cat = 0; d.power = 0; d.range = 0; d.numUses = 1;
        d.targetShip = true;
    }
    sim_.setDesigns(designs_);
    designsReady_ = true;
}

int CampaignFleetBridge::syncRows(int shipId, int owner, int cat,
                                  const std::vector<Gizmo>& gizmos,
                                  int techCount,
                                  const std::vector<bool>& owned,
                                  int* sumOut) {
    Ship* s = sim_.findShip(shipId);
    if (!s) return 0;
    auto& map = slotMap_[shipId];
    int nextSlot = 0, sum = 0;
    auto slotFor = [&](int row) {
        auto it = map.find(row);
        if (it != map.end()) return it->second;
        uint32_t slot = static_cast<uint32_t>(nextSlot++);
        map[row] = slot;
        // FUN_00049698 guard is idx > invCap (idx == cap ADMITTED,
        // shipsim.cpp:315) — the window must GROW WITH the fill or every
        // idx past the stale cap is silently refused (t365 first-run bug 4:
        // 11 slots requested, 1 filled).
        s->invCap = static_cast<uint32_t>(nextSlot);
        return slot;
    };
    for (size_t i = 0; i < gizmos.size() && i < static_cast<size_t>(kSynthBase); ++i) {
        const Gizmo& g = gizmos[i];
        if (static_cast<int>(g.cat) != cat) continue;
        if (cat == 0 && g.numUses == 0) continue;  // engage guard (combat.md S2g)
        if (!requiresAvailable(g.resReq, techCount, owned)) continue;
        // Cited mutator FUN_00049698: same-cidx-in-target refusal makes the
        // per-engagement refresh idempotent; the map keeps syncs duplicate-
        // free; the mutator runs recalcShip (stats re-materialise, 0x496d3).
        sim_.setSlot(*s, slotFor(static_cast<int>(i)), static_cast<uint8_t>(i));
        // Cited upkeep consumer 0x4a6f9 skips slots with payload != -1
        // (shipsim.h:100-103: measured save-side, -1 sits on upkeep-gate
        // rows; the -1 test is the ONLY cited consumer, so a uniform -1 on
        // synced slots is observably equivalent — ledger S12).
        s->inv[slotFor(static_cast<int>(i))].payload = 0xffffffffu;
        if (cat == 0) sum += g.level;
    }
    if (cat == 0) {
        // The synthetic pop row always occupies a slot (even at level 0 the
        // cited handler runs and the zero-damage skip 0x4bb64 applies —
        // matches the aggregate zero-pop volley exactly).
        const int synth = kSynthBase + (owner % kMaxOwners);
        sim_.setSlot(*s, slotFor(synth), static_cast<uint8_t>(synth));
        s->inv[slotFor(synth)].payload = 0xffffffffu;
    }
    s->invCap = static_cast<uint32_t>(nextSlot);        // S10 window
    if (sumOut) *sumOut = sum;
    return nextSlot;
}

void CampaignFleetBridge::resetShipRecord(int shipId, int owner, int star) {
    slotMap_.erase(shipId);
    if (Ship* s = sim_.findShip(shipId)) {
        s->owner = owner;
        s->kind = OrderKind::InSystem;                  // K1 precondition
        s->systemId = static_cast<uint32_t>(star) + 1;  // 0 == no system
        for (auto& sl : s->inv) sl = InvSlot{};
        s->invCap = 0;
        s->invFilled = 0;
        s->dispatcherGate = 0;
        s->orderType = 0;
        s->fireTarget = -1;
        s->activeSlot = -1;
        s->power = 0;
        s->shields = 0;
        s->status = 0;
        s->act = 0;
    }
}

void CampaignFleetBridge::advanceBoundary() {
    // ShipSim turn frame verbatim (status zero, t101 refill, slot refresh,
    // march, upkeep, executor driver). Our records never act (act==0) and
    // never march (kind 4), so the frame is bookkeeping-only — the refill +
    // refresh + shield upkeep materialisation are exactly what the cited
    // laws would do to real fleet records.
    sim_.advanceBoundary();
}

CampaignFleetBridge::Outcome CampaignFleetBridge::resolveEngagement(
    int attacker, int defender, int star, double ownedPopAttacker,
    double localPopDefender, int fleetDamageAttacker, bool doublePower,
    const std::vector<Gizmo>& gizmos, int techCount,
    const std::vector<bool>& ownedTechA, const std::vector<bool>& ownedTechB) {
    Outcome out;
    ensureDesigns(gizmos);

    const int sid = shooterId(attacker, star);
    const int gid = garrisonId(defender, star);

    // RESET-PER-ENGAGEMENT (docs/re/_wip_t365b.md fix 5): both records are
    // rebuilt clean every resolution — the pre-flip aggregate was stateless
    // per engagement, and corpse/stale-slotMap persistence produced
    // cap=0/shots=0 pathologies. All verdict-relevant state is
    // re-materialised below by the cited laws (syncRows -> recalcShip,
    // upkeep -> shields, setStance -> gate/stance/activeSlot).
    resetShipRecord(sid, attacker, star);
    resetShipRecord(gid, defender, star);

    // --- shooter record (created once; engagement state persists across
    //     boundaries as engine state, digest-visible) ---
    if (!sim_.findShip(sid)) {
        Ship s;
        s.id = sid; s.owner = attacker;
        s.kind = OrderKind::InSystem;                    // K1 precondition
        s.systemId = static_cast<uint32_t>(star) + 1;    // 0 == no system
        s.integrity = 1000000; s.maxIntegrity = 1000000; // S11
        s.etaDay = sim_.turn();
        sim_.addShip(s);
    }
    Ship* shooter = sim_.findShip(sid);
    // NOTE: ships_ is a std::vector<Ship> (shipsim.h:555) — addShip may
    // reallocate and invalidate every Ship*. NEVER hold a pointer across
    // addShip; re-lookup (this was the t365 first-run bug: writes to a
    // dangling shooter silently lost power/targetPos).
    // Co-located records: every shipped cat-0 row has Range >= 25 (gizmos.txt
    // census; the sim's C9 range-0 leg covers the synthetic row anyway), and
    // the chase leg is S6 decision (a) — targetPos set below, no walk modelled.
    shooter->pos[0] = static_cast<float>(star) * 32.0f;
    shooter->pos[1] = 0.0f; shooter->pos[2] = 0.0f;
    shooter->owner = attacker;

    int weaponSum = 0;
    syncRows(sid, attacker, /*cat=*/0, gizmos, techCount, ownedTechA, &weaponSum);

    // Synthetic pop-reserve row level (S2): the SAME empire operand the
    // aggregate used (ownedPop/10), flowing through the cited volley law.
    const int popTen = static_cast<int>(ownedPopAttacker / 10.0);
    const int synth = kSynthBase + (attacker % kMaxOwners);
    designs_[synth].level = popTen;
    designs_[synth].rowWeapon = popTen;
    sim_.setDesigns(designs_);           // the sim copies the table

    // --- garrison record (S1) ---
    if (!sim_.findShip(gid)) {
        Ship g;
        g.id = gid; g.owner = defender;
        g.kind = OrderKind::InSystem;
        g.systemId = static_cast<uint32_t>(star) + 1;
        sim_.addShip(g);
        shooter = sim_.findShip(sid);          // re-lookup post-realloc
    }
    Ship* garrison = sim_.findShip(gid);
    garrison->owner = defender;                // resurrect (C4 zeroed both)
    garrison->kind = OrderKind::InSystem;
    const int hullDefense = static_cast<int>(localPopDefender / 10.0) + 2;
    garrison->integrity = hullDefense + 1;     // death <=> hullHit > that (P2)
    garrison->maxIntegrity = garrison->integrity;
    garrison->pos[0] = shooter->pos[0];
    garrison->pos[1] = shooter->pos[1];
    garrison->pos[2] = shooter->pos[2];

    // S8 shield materialisation through the CITED upkeep law (FUN_0004a6a6:
    // +0x90 := 0, then += row[+0x56] per AFFORDABLE cat-1 slot). Power is
    // topped so every researched slot is affordable; the value therefore
    // equals shieldChargesFor(defender) row-for-row (same table, same gate).
    syncRows(gid, defender, /*cat=*/1, gizmos, techCount, ownedTechB, nullptr);
    int shieldCostTotal = 0, shieldCharges = 0;
    for (const Gizmo& g : gizmos) {
        if (g.cat != GizmoCat::Shield) continue;
        if (!requiresAvailable(g.resReq, techCount, ownedTechB)) continue;
        shieldCostTotal += g.power;
        shieldCharges += g.level;
    }
    // Top-up must cover the FULL scan burn (every affordable slot burns,
    // shipsim.cpp:286-287) — +1 only afforded nothing and left shields 0
    // (t365 first-run bug 2). No upkeep row costs >1000, so this fully
    // pays the shield law; leftover power is unread by any cited consumer.
    garrison->power = shieldCostTotal + 1000000;
    garrison->status = 0;
    sim_.upkeep(*garrison);                    // cited materialisation
    out.shieldCharges = static_cast<int>(garrison->shields);

    // sim-measured single-pass volley base (pre-fd, pre-double).
    out.volleyBase = weaponSum + popTen;

    // S3 power gate (cited: setStance refuses power==0 verbatim,
    // 0x4a561..0x4a56f — refusal = no engagement, no capture).
    const int power = out.volleyBase - fleetDamageAttacker;
    shooter->power = power > 0 ? power : 0;

    EngFact f;
    f.turn = turn_; f.attacker = attacker; f.defender = defender; f.star = star;
    f.popATen = popTen; f.weaponSum = weaponSum;
    f.shieldCharges = out.shieldCharges; f.hullDefense = hullDefense;
    f.fleetDamage = fleetDamageAttacker; f.doublePower = doublePower;
    f.volleyBase = out.volleyBase;

    if (shooter->power == 0) {                 // S3 suppression
        census_.push_back(f);
        return out;                            // ran == false
    }
    out.ran = true;

    // Readiness (S4): slot use words := design[+0x42] (the cited refresh
    // operand) before the round. THE FIRST PASS NEEDS THIS TOO — without it
    // every use word is 0 and the ammo skip (0x4a37b) drops every shot
    // (t365 first-run bug 3: 11 slots, 0 shots).
    sim_.refreshUseCounts(*shooter);

    // S6 chase decision (a): targetPos := victim pos at stance time.
    shooter->targetPos[0] = garrison->pos[0];
    shooter->targetPos[1] = garrison->pos[1];
    shooter->targetPos[2] = garrison->pos[2];

    // S5: resolver probe at mode 0 (Leg B eligibility kind-4 + companionScan
    // + stance volley — the cited no-apply semantics C3; the stance stores
    // +0x62/+0x67/+0x68 and leaves activeSlot on the last cat-0 scanned, C5).
    // Leg A entered via the skip flag TRUE (S7). Then the per-slot commit
    // loop at mode 1 (t210 stacking law: one charge per committed weapon).
    sim_.engageRound(attacker, gid, /*objectivePlanetShielded=*/true, 0);
    std::vector<std::pair<uint32_t, int>> bySlot;
    for (const auto& kv : slotMap_[sid]) bySlot.emplace_back(kv.second, kv.first);
    std::sort(bySlot.begin(), bySlot.end());
    for (int pass = 0; pass < (doublePower ? 2 : 1); ++pass) {
        if (pass > 0) sim_.refreshUseCounts(*shooter);   // S4 re-arm
        for (const auto& e : bySlot) {
            shooter->activeSlot = static_cast<int>(e.first);
            auto rep = sim_.commitShot(sid, 1);
            out.shots += rep.shots;
            out.hullHit += rep.hullAbsorb;
            if (rep.destroyed == gid) { out.captured = true; break; }
        }
    }

    f.shots = out.shots;
    f.simCaptured = out.captured;
    census_.push_back(f);
    return out;
}

}  // namespace game
}  // namespace ascend
