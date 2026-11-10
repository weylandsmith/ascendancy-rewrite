#pragma once
// t365 ENGINE FLIP BRIDGE (user ruling D2=(b), docs/DECISIONS.md USER RULING
// 2026-11-09: "per-ship becomes THE engine ... aggregate demotes to a test
// oracle during the transition, removed after seeds agree"; design
// docs/re/_wip_t365.md S1). Campaign::combatPhase() calls advanceBoundary()
// once + resolveEngagement() per border engagement: the PER-SHIP engine
// (ShipSim) executes the cited engagement law at every engagement (stance
// 0x4a55c + volley 0x4a5c1 + dispatcher 0x4a360 + gun handler 0x4b8e4 + hit
// path 0x4b740 + resolver legs 0x42cd7, combat.md S2g/S2h/S2k,
// docs/re/_wip_t364.md C1..C9), owns all per-ship state (engagement quadruple
// +0x62/+0x63/+0x67/+0x68, ammo DEC, MIN-charge, two-layer clamped absorb,
// shield materialisation 0x4a6a6 via upkeep, death finalizer C4), and THE
// CAPTURE VERDICT IS ITS OWN: a star is taken iff the round destroys the
// garrison record (hull < 1, C4). The aggregate score code moved to
// game/aggregate_oracle.{h,cpp} — production consumes NONE of it (the
// delegators attackScore/defenseScore remain public for the pinned tests);
// the census below is the seed-comparison evidence the ruling names.
// test_campaign_fleet_t365 P2/P5 MEASURE the equivalence claim: with
// fleetDamage == 0 the per-ship verdict equals the aggregate comparison
// hullHit > defenseScore engagement-for-engagement (sequential per-slot
// absorb telescopes; garrison hull := defenseScore+1, S1). The ONE named
// divergence class is partially-sapped attackers (S3), recorded per fact.
//
// SURROGATE LEDGER — every INFERRED mapping, flagged; cited law lives ONLY
// inside ShipSim, this file adds no law claims:
//   S1 GARRISON RECORD synthesised per (defender, star): hull :=
//      localPop/10 + 2 + 1 RE-ARMED every engagement (defenseScore's
//      DOCUMENTED-DEFAULT formula moved here as a per-ship hull seed — not a
//      vendor law; +1 so death <=> spill >= hull <=> hullHit > defenseScore);
//      owner/kind re-set every engagement (the C4 finalizer zeroes both).
//   S2 POP RESERVE rides the shooter inventory as ONE synthetic cat-0 row per
//      owner (rowWeapon := ownedPop/10 — the SAME empire operand the
//      aggregate used, Range 0 = UNLIMITED per the cited C9 leg, NumUses 1,
//      TARGETSHIP set so the cited engage flag admits it), assigned through
//      the cited setSlot mutator: the pop term flows THROUGH the cited volley
//      law, not around it.
//   S3 SA_SapAlienPower fleetDamage gates the engagement via the cited POWER
//      GATE (setStance refuses power==0 verbatim, 0x4a561..0x4a56f):
//      engagement power := pop/10 + weaponSum - fleetDamage; <= 0 == nothing
//      runs == no capture (matches the aggregate max(0,...) zero-volley
//      outcome EXACTLY). A PARTIALLY sapped volley still fires FULL row
//      damage (damage := design[+0x52] is cited and unscaleable; help.txt
//      L2012 "wipe out the power" reads as suppression, not attenuation) —
//      NAMED DIVERGENCE vs the aggregate's subtraction, census-recorded
//      (fleetDamage != 0 facts), the ONLY divergence class (P2 pins it).
//   S4 SA_DoublePower = a SECOND commit pass over every cat-0 slot (help.txt
//      L1917); slot use words re-armed to the cited refresh operand
//      (design[+0x42]) before each pass so the ammo law cannot shrink the
//      doubled volley: 2 full passes == the aggregate volley*2 exactly.
//   S5 COMMIT EDGE: the vendor's mode-1 edges are player-command-exec
//      (0x25560/0x25570); the headless rewrite has no such edge and mode-0
//      combat could never capture (C3), so the bridge IS the commit edge:
//      engageRound runs at mode 0 (Leg B eligibility + stance volley probe,
//      verbatim no-apply) and the per-slot commit loop fires at mode 1 (t210
//      stacking law: one charge per committed weapon). INFERRED, pinned.
//   S6 CHASE LEG (t364 named t365 scope): DECISION (a) — shooter targetPos
//      := victim pos at stance time, set by the bridge; the walk-toward-+0x68
//      leg is uncited so ShipSim does NOT model it; pressure re-issues each
//      boundary. Pinned (targetPos observable).
//   S7 LEG A / cargo-invasion: the resolver enters through the
//      objectivePlanetShielded skip flag (true) — carrier/cargo engagement
//      needs invasion payload semantics that are user-gated residues
//      (pership-spec §4 C5 non-goal); Leg B (firepower) runs. Named, not
//      silently dropped: engageRound still models Leg A verbatim for callers
//      that supply carriers (t364 pins).
//   S8 SHIELDS ARE PER-SHIP LAW: the garrison carries the defender's
//      researched cat-1 rows in its OWN inventory (cited setSlot); upkeep
//      FUN_0004a6a6 materialises +0x90 per affordable slot each boundary
//      (powerMax := 1<<20 makes every slot affordable). The value equals
//      shieldChargesFor (same rows, same gate) — census-recorded.
//   S9 RNG: ShipSim's Lcg is ISOLATED (shipsim.h header law) — zero campaign
//      rng_ draws added or skipped; the bridge itself draws nothing.
//   S10 ENGAGEMENT WINDOW: invCap is pinned to the synced row count — the
//      volley scans ONLY that owner's rows, so the C5 last-scanned quirk
//      cannot leave an out-of-window slot active mid-round (the t210
//      one-arm-per-gizmo shape holds).
//   S11 SHOOTER HULL is a fixed 1,000,000 (return fire is a SEPARATE,
//      owner-filtered run, K10; the aggregate never modelled attacker
//      attrition either — one side per resolution). TRAJECTORY NOTE
//      (honest): full pinned-seed runs DO shift wherever the sapping
//      divergence fires (S3) — P4 pins DETERMINISM (equal seeds, equal
//      traces), not pre-t365 preservation; the agreement claim is per-
//      engagement at fd==0 (P2/P5) and the census quantifies the rest.
//      PLAYTHROUGH.md regenerated from the flipped binary.
#include <cstdint>
#include <map>
#include <vector>

#include "game/shipsim.h"

namespace ascend {
namespace game {

class Gizmo;

class CampaignFleetBridge {
  public:
    explicit CampaignFleetBridge(unsigned campaignSeed);

    const ShipSim& sim() const { return sim_; }
    ShipSim& simForTest() { return sim_; }
    static int shooterId(int attacker, int star) { return attacker * 1000 + star; }
    static int garrisonId(int defender, int star) { return 100000 + defender * 1000 + star; }

    // One per-ship engagement resolution at the turn boundary (called from
    // Campaign::combatPhase per border pair, AFTER all pre-existing gates).
    // Ensures/refreshes the two records (S1/S2/S8), applies the S3 power
    // gate, then runs S5 (probe + per-slot commit loop).
    struct Outcome {
        bool ran = false;        // false == S3 suppression, no engagement
        bool captured = false;   // garrison record destroyed (C4)
        int shots = 0;           // mode-1 hit calls that passed the gates
        int volleyBase = 0;      // sim-measured single-pass damage sum
        int shieldCharges = 0;   // garrison +0x90 materialised (S8)
        int hullHit = 0;         // total spill applied to garrison +0x8c
    };
    Outcome resolveEngagement(int attacker, int defender, int star,
                              double ownedPopAttacker, double localPopDefender,
                              int fleetDamageAttacker, bool doublePower,
                              const std::vector<Gizmo>& gizmos, int techCount,
                              const std::vector<bool>& ownedTechA,
                              const std::vector<bool>& ownedTechB);

    // One boundary step of the per-ship turn frame (status zero, t101 refill,
    // march, upkeep, executor driver) — ShipSim::advanceBoundary verbatim.
    // Called ONCE per combatPhase before the engagement loop.
    void advanceBoundary();

    // CENSUS (seed-comparison oracle evidence, D2 ruling). One record per
    // engagement resolution; the campaign writes its final verdict back via
    // recordDecider() (differs from simCaptured only on the SuperMarines
    // guaranteed-capture branch); the pin test recomputes the aggregate
    // expectation from the recorded inputs and counts agreement.
    struct EngFact {
        int turn = 0, attacker = -1, defender = -1, star = -1;
        int popATen = 0, weaponSum = 0, shieldCharges = 0, hullDefense = 0;
        int fleetDamage = 0;
        bool doublePower = false;
        bool guaranteed = false;      // SA_SuperMarines branch (campaign sets)
        bool ran = false;
        int volleyBase = 0, shots = 0;
        bool simCaptured = false;     // per-ship garrison death (C4)
        bool deciderCaptured = false; // campaign's final verdict
    };
    std::vector<EngFact>& census() { return census_; }
    const std::vector<EngFact>& census() const { return census_; }
    void recordDecider(bool captured, bool guaranteed = false) {
        if (!census_.empty()) {
            census_.back().deciderCaptured = captured || guaranteed;
            census_.back().guaranteed = guaranteed;
        }
    }
    void setTurn(int t) { turn_ = t; }

  private:
    // SimDesign table built once: rows 0..75 verbatim-mapped from gizmos.txt
    // (_wip_t363 S3b: the Gizmo parse IS the design table), rows 76..83 =
    // per-owner synthetic pop-reserve guns (S2).
    void ensureDesigns(const std::vector<Gizmo>& gizmos);
    // Assign/refresh one record's window through the cited setSlot mutator
    // (FUN_00049698; the same-cidx-in-target refusal makes refresh
    // idempotent). Persistent row->slot map keeps syncs duplicate-free.
    // cat == 0: the owner's weapon rows + the synthetic pop row (shooter);
    // cat == 1: the owner's shield rows (garrison). Returns row count
    // (S10 engagement invCap) and writes the weapon Level sum into sumOut.
    int syncRows(int shipId, int owner, int cat, const std::vector<Gizmo>& gizmos,
                 int techCount, const std::vector<bool>& owned, int* sumOut);
    // Reset-per-engagement (docs/re/_wip_t365b.md fix 5): wipe the record's
    // inventory/window/stance and its row->slot map; every verdict-relevant
    // field is re-materialised by the cited laws afterwards.
    void resetShipRecord(int shipId, int owner, int star);

    ShipSim sim_;
    std::vector<SimDesign> designs_;
    bool designsReady_ = false;
    std::map<int, std::map<int, uint32_t>> slotMap_;  // shipId -> (row -> slot)
    int turn_ = 0;
    std::vector<EngFact> census_;
};

}  // namespace game
}  // namespace ascend
