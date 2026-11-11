// SPDX-License-Identifier: GPL-3.0-or-later

#include "game/aggregate_oracle.h"
#include "game/economy.h"  // Gizmo, GizmoCat, requiresAvailable (income-law.md S4)

#include <algorithm>

namespace ascend::game {

int aggregateVolley(double ownedPop, int weaponLevelSum, int fleetDamage) {
    // Body MOVED VERBATIM from Campaign::attackScore (campaign.cpp, t89
    // cited law) at t365 — see header for the address-level citations.
    return std::max(0, static_cast<int>(ownedPop / 10.0) + weaponLevelSum -
                           fleetDamage);
}

int weaponLevelSum(const std::vector<Gizmo>& gizmos, int techCount,
                   const std::vector<bool>& ownedTech) {
    int volley = 0;
    for (const Gizmo& g : gizmos) {
        if (g.cat != GizmoCat::Weapon) continue;
        bool ok = requiresAvailable(g.resReq, techCount, ownedTech);
        // NumUses gate [gizmos.txt header + dispatcher 0x4a373..0x4a390,
        // combat.md S2g]: a 0-use row engages nothing (every shipped cat-0 row
        // has NumUses >= 1 — {1,1,1,1,5,1,2,2,2,3} — so this arm never fires
        // on shipped data, it refuses a hypothetical 0-use row).
        if (ok && g.numUses != 0) volley += g.level;
    }
    return volley;
}

int aggregateHullDefense(double localPop) {
    // Body MOVED VERBATIM from Campaign::defenseScore at t365. Shield charges
    // are NOT folded in (two-layer absorb law, header). Fortify +2 is the
    // rewrite's documented capture-protection term.
    return static_cast<int>(localPop / 10.0) + 2;
}

}  // namespace ascend::game
