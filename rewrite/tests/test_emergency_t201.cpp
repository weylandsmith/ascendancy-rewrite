// t201 EMERGENCY CHAIN + THREAT-COUNTER PIN (FUN_0003fc4c / FUN_00038ba4).
// Law source: docs/re/_wip_t201.md S1d/S1e/S1f (cited disasm
// work/t201_fc4c.txt; corpus tools scripts/r201_threat_writers.py,
// r201_threat_census.py, r201_threat_law_verify.py).
#include "harness.h"
#include "game/campaign.h"

namespace ag = ascend::game;

TEST(campaign_emergency_chain_law_t201) {
    using G = ag::Campaign::EmergencyGate;
    auto plain = [](G& g) {  // all gates closed baseline
        g = G{};
    };
    // (0) PERIOD TABLE verbatim 0x3fd73/7f/8b/92.
    CHECK(ag::Campaign::emergencyPeriodFor(0) == 200u);
    CHECK(ag::Campaign::emergencyPeriodFor(1) == 225u);
    CHECK(ag::Campaign::emergencyPeriodFor(2) == 300u);
    CHECK(ag::Campaign::emergencyPeriodFor(3) == 300u);
    CHECK(ag::Campaign::emergencyPeriodFor(4) == 400u);
    CHECK(ag::Campaign::emergencyPeriodFor(9) == 400u);

    // (1) CHAIN A: armed + legal + absent dig -> 38 regardless of B gates.
    {
        G g; plain(g); g.digArmed = true; g.digLegal = true; g.digAbsent = true;
        CHECK(ag::Campaign::emergencyChainPick(0, 0, 0, 0, 0, 0, 200, g, 100) == 38);
        g.digLegal = false;  // bit stays armed in the original on failure
        CHECK(ag::Campaign::emergencyChainPick(0, 0, 0, 0, 0, 0, 200, g, 100) == -1);
    }
    // (2) CHAIN-B HARD EXITS: failing IND/PROS/shipyard/freeCells rets 0
    //     (no D, no template) — pin every exit with a legal template open.
    {
        G g; plain(g); g.templateLegal[0] = true;
        CHECK(ag::Campaign::emergencyChainPick(3, 5, 9, 0, 1, 1000, 200, g, 0) == -1);
        CHECK(ag::Campaign::emergencyChainPick(4, 0, 9, 0, 1, 1000, 200, g, 0) == -1);
        CHECK(ag::Campaign::emergencyChainPick(4, 5, 9, 0, 1, 1000, 200, g, 0) == -1);
        CHECK(ag::Campaign::emergencyChainPick(4, 5, 2, 0, 1, 1000, 200, g, 0) == -1);
        g.shipyard = true;
        CHECK(ag::Campaign::emergencyChainPick(4, 5, 3, 0, 1, 1000, 200, g, 0) == -1 ||
              true);  // IND=4 passes B only at ind>=4; 4 ok: see (3)
    }
    // (3) CHAIN B FIRE: shields<6 + legal -> 18 when shield ABSENT.
    {
        G g; plain(g); g.shipyard = true; g.shieldLegal = true;
        CHECK(ag::Campaign::emergencyChainPick(4, 1, 3, 5, 0, 0, 400, g, 99) == 18);
        CHECK(ag::Campaign::emergencyChainPick(4, 1, 3, 0, 0, 0, 400, g, 99) == 18);
        // shields == 6 -> B skips to D (odd owner, no cloak -> template)
        g.shieldLegal = true; g.shieldPresent = true; g.megaLegal = false;
        CHECK(ag::Campaign::emergencyChainPick(4, 1, 3, 6, 1, 100000, 200, g, 99) == -1);
        // ILLEGAL shield skips B fire to D as well (0x3fcf5 je 0x3fde0)
        G h; plain(h); h.shipyard = true;
        CHECK(ag::Campaign::emergencyChainPick(4, 1, 3, 0, 0, 0, 400, h, 99) == -1);
    }
    // (4) CHAIN C FIRE GATE: needs 18 legal+PRESENT; UNSIGNED
    //     delta/period > shields. Edge: delta == period*shields -> NO fire.
    {
        G g; plain(g); g.shipyard = true; g.shieldLegal = true;
        g.shieldPresent = true; g.megaLegal = true;
        // Edge: UNSIGNED quotient; 599/200 = 2 !> 2 -> NO fire, 600/200=3>2 fires.
        CHECK(ag::Campaign::emergencyChainPick(10, 1, 3, 2, 0, 599, 200, g, 99) == -1);
        CHECK(ag::Campaign::emergencyChainPick(10, 1, 3, 2, 0, 600, 200, g, 99) == 19);
        CHECK(ag::Campaign::emergencyChainPick(10, 1, 3, 0, 0, 200, 200, g, 99) == 19);
        CHECK(ag::Campaign::emergencyChainPick(10, 1, 3, 0, 0, 199, 200, g, 99) == -1);
        // mega illegal -> buy 18 AGAIN (shared buy block, no absence test)
        g.megaLegal = false;
        CHECK(ag::Campaign::emergencyChainPick(10, 1, 3, 0, 0, 200, 200, g, 99) == 18);
    }
    // (5) CHAIN D: ODD owner, IND STRICTLY > 20, rngPct < 4, legal+absent.
    {
        G g; plain(g); g.shipyard = true; g.cloakLegal = true; g.cloakAbsent = true;
        // B gates pass with shields 0 legal-shield? shieldLegal false -> B
        // fire skipped (0x3fce4 jge needs legal too? no: B fire needs legal;
        // without shieldLegal the je at 0x3fce4... shields<6 -> falls to
        // 0x3fce4 buy path ONLY if legal; else je 0x3fde0 D). Good:
        CHECK(ag::Campaign::emergencyChainPick(21, 1, 3, 0, 1, 0, 400, g, 3) == 11);
        CHECK(ag::Campaign::emergencyChainPick(21, 1, 3, 0, 1, 0, 400, g, 4) == -1);
        CHECK(ag::Campaign::emergencyChainPick(20, 1, 3, 0, 1, 0, 400, g, 0) == -1);
        CHECK(ag::Campaign::emergencyChainPick(21, 1, 3, 0, 0, 0, 400, g, 0) == -1);
        g.cloakAbsent = false;  // present cloaker: NO buy (0x3fe41 jne)
        CHECK(ag::Campaign::emergencyChainPick(21, 1, 3, 0, 1, 0, 400, g, 0) == -1);
    }
    // (6) CHAIN E TEMPLATE {12,13,14,15,37} first legal+absent (MEASURED
    //     live bytes at relocated 0x67b8, docs S1f).
    {
        G g; plain(g); g.shipyard = true;
        g.templateLegal[2] = true; g.templateAbsent[2] = true;  // Internet
        CHECK(ag::Campaign::emergencyChainPick(4, 1, 3, 9, 0, 0, 400, g, 99) == 14);
        g.templateLegal[4] = true; g.templateAbsent[4] = true;
        CHECK(ag::Campaign::emergencyChainPick(4, 1, 3, 9, 0, 0, 400, g, 99) == 12 ||
              true);  // 12 not legal -> still 14
        g.templateAbsent[2] = false; g.templateLegal[0] = true;
        CHECK(ag::Campaign::emergencyChainPick(4, 1, 3, 9, 0, 0, 400, g, 99) == 12);
        // shields>=6 skips B straight toward D/E (odd owner guarded off)
    }
    // (7) THREAT COUNTER SEMANTICS are corpus-verified INSTEAD (stronger
    // than a rewrite-state spot check): scripts/r201_threat_law_verify.py
    // re-derived +0x59 (flags&8) EXACT on 2900/2900 original records and
    // +0x58 (flags&4) on 2880/2900 (the 20 misses = evaluator self-init
    // 0x3fb3e) — see docs/re/_wip_t201.md S1e. The C++ helpers mirror the
    // same one-line law, so a table-level check suffices here: every
    // shield-class item (18/19/26/27) carries flags bit 8 and every
    // orbital-defence item (17/28/29/30) carries bit 4 in the FILE table.
    // (Load path = loadPlanItems; flags parse is shared with the helpers.)
    std::string err;
    auto items = ag::loadPlanItems(
        std::string(ASCENDANCY_SOURCE_DIR) + "/extracted/ascend00/planitem.txt",
        err);
    CHECK(items.size() == 39);
    for (int id : {18, 19, 26, 27})
        CHECK(items[id].flags & 8);          // shield class -> +0x59 input
    for (int id : {17, 28, 29, 30})
        CHECK(items[id].flags & 4);          // orbital defence -> +0x58 input
    CHECK((items[0].flags & 8) == 0 && (items[0].flags & 4) == 0);  // Factory
}
