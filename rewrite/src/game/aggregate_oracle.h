#pragma once
#include <vector>

namespace ascend::game {
// AGGREGATE COMBAT ORACLE — demoted from Campaign at t365 per user ruling
// D2=(b) (docs/DECISIONS.md USER RULING 2026-11-09: "per-ship becomes THE
// engine once it passes the pinned-seed suite; aggregate demotes to a test
// oracle during the transition, removed after seeds agree").
//
// ROLE (t365, docs/re/_wip_t365.md S1 D-2/D-4): these are the empire-level
// combat operands the pinned seeds validated through t364. They remain the
// CAPTURE DECIDER inside Campaign::combatPhase (the per-ship sim executes the
// cited engagement law verbatim but does not yet drive capture — conversion
// is post-acceptance, pership-spec N10), and they are the seed-comparison
// ORACLE the bridge measures the per-ship resolver against
// (oracleAgreements/oracleDisagreements, test_campaign_fleet_t365).
// REMOVAL is only due after the user accepts the per-ship engine; until then
// Campaign delegates here verbatim — zero behavioural delta (the bodies are
// byte-for-byte the t89/cited laws, docs/re/combat.md S2d/S2f/S2g/S2i).

// VOLLEY LAW (0x4a5c1..0x4a5fc volley fires EVERY cat-0 slot in stored order;
// damage per hit = design[+0x52] == file Level, map CLOSED 76/76 t87; NO hit
// roll — measured-negative, combat.md S2g). Aggregate mapping (S2i): empire
// reserves scale with owned pop /10, plus the SUM of researched cat-0 Levels;
// NumUses==0 rows engage nothing (dispatcher ammo guard 0x4a373..0x4a390).
// `fleetDamage` = SA_SapAlienPower-sapped power (abilities.md §2).
int aggregateVolley(double ownedPop, int weaponLevelSum, int fleetDamage);

// Sum of cat-0 (Weapon) gizmo Levels passing the REQUIRES gate and the
// NumUses!=0 engage guard — the weaponLevelSum operand of aggregateVolley.
// `techCount` = tree size for requiresAvailable (income-law.md S4).
int weaponLevelSum(const std::vector<class Gizmo>& gizmos, int techCount,
                   const std::vector<bool>& ownedTech);

// HULL-LAYER DEFENSE (the original NEVER folds shields into one total —
// two-layer clamped absorb 0x4b7c4..0x4b8a6; defenseScore is the HULL layer
// only: local-pop reserves /10, plus the rewrite's own capture-protection
// term +2 [documented default, unchanged since t89]).
int aggregateHullDefense(double localPop);

}  // namespace ascend::game
