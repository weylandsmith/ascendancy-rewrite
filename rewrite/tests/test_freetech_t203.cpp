// t203 FREE-TECH GRANT PIN — FUN_00046e84 (0x46e84..0x46f9d) + its sole
// caller gate inside the build-completion tail (0x3913b..0x3917a) + checker
// rule-D dig placement (FUN_0003830c 0x38533..0x38552).
// Law source: docs/re/_wip_t203.md S1..S3 (verbatim disasm of
// work/ascend_restored.bin this session). Gap map row 7 (ai-dossier.md S8).
#include "harness.h"
#include "game/campaign.h"

namespace ag = ascend::game;

ag::Campaign makeCampaignForDemolish(unsigned seed);  // test_campaign.cpp

TEST(campaign_free_tech_grant_law_t203) {
    // (G1) candidates = NOT-owned rows minus the QUEUED TARGET; uniform.
    // Run N grants on one empire: every pick is previously-unowned at pick
    // time (owned-mask skip 0x46eff), the target row is NEVER granted while
    // queued (0x46ee6), and owned count advances exactly +1 per grant.
    auto c = makeCampaignForDemolish(202);
    const int owner = 1;
    const int target = 7;
    // leave queuedTech as-is after a turn: researchPhase owns that field;
    // instead pin through repeated grants + the owned-count bookkeeping.
    int before = c.techsOwned(owner);
    int granted = 0;
    for (int k = 0; k < 30; ++k) {
        int g = c.freeTechGrantFor(owner);
        if (g < 0) break;
        ++granted;
        CHECK(c.techsOwned(owner) == before + granted);  // +0x4a/+0x4b mark
    }
    CHECK(granted > 0);
    // (G2) EXHAUSTION: after all rows owned, -1 and NO state change
    // (0x46f1c empty-guard returns before the rng draw at 0x46f23).
    c.setAllTechs(owner, true);
    CHECK(c.freeTechGrantFor(owner) == -1);
    CHECK(c.techsOwned(owner) == c.techCountTotal());
}

TEST(campaign_free_tech_grant_skips_queued_target_t203) {
    // The candidate loop reads ONLY [base+race*2+0x1d4e] == DAT_00076492
    // (t91 field identity) — the research TARGET word — so the row a race
    // is currently researching is excluded from the uniform pool while
    // queued. Pure-grant pin (no advance(): researchPhase rewrites the
    // target word on its own schedule): set target 3, grant 12 times, row 3
    // must never be the granted row and stays unowned.
    auto c = makeCampaignForDemolish(202);
    const int owner = 2;
    c.setQueuedTechFor(owner, 3);
    for (int k = 0; k < 12; ++k) {
        c.freeTechGrantFor(owner);                       // 0x46f23 draws
        CHECK(c.techRowOwnedFor(owner, 3) == false);     // 0x46ee6 keeps it out
    }
    // The TARGET word itself is untouched by the grant channel (S1 step 5:
    // NEVER writes DAT_00076492 — sole +0x1d4e ref is the READ):
    CHECK(c.isTechQueuedFor(owner, 3));
}

TEST(campaign_dig_completion_grants_tech_t203) {
    // END-TO-END through buildPhase: a queued dig (item 38) on an AI planet
    // completes into a ROCK cell: rock bit cleared, dig CONSUMED (item list
    // unchanged minus the dig), exactly ONE free tech granted. Seed a tech
    // state so the grant is observable as owned-count +1.
    auto c = makeCampaignForDemolish(2024);
    int star = -1;
    for (int s = 0; s < static_cast<int>(c.galaxy().stars.size()); ++s)
        if (c.starOwner(s) >= 1) { star = s; break; }
    CHECK(star >= 0);
    auto& ps = const_cast<ag::PlanetState&>(c.planetAt(star));
    // force one clean rock cell with an ACTIVE neighbour (rule G applies to
    // the dig: exemptions are items 5/35 only). Size class 1 (11 cells):
    // kRowStart {.,.,.,4,3,4,5,6} kRowW {.,.,.,1,3,3,3,1} -> r3={cell0},
    // r4={1,2,3}, r5={4,5,6}, r6={7,8,9}, r7={10}. Cell 0 (row 3 col 4) is
    // vertically adjacent to row-4 col-4 == cell 2; the CB sits there ACTIVE.
    ps.surfaceCells = 11;              // size class 1
    for (int k = 0; k < 11; ++k) ps.cellClasses[k] = 1;
    ps.cellClasses[0] = 1 | 8;         // the rock (cell 0)
    ps.items = {5};                    // CB only
    ps.itemCells = {2};                // CB on cell 2 (active neighbour of 0)
    ps.capBase = 8;
    ps.pop = 7;
    ps.pendingItem = 38;
    ps.buildAcc = 10000;               // completes on next tick
    const int owner = c.starOwner(star);
    const int owned0 = c.techsOwned(owner);
    c.advance();
    CHECK((ps.cellClasses[0] & 8) == 0);   // 0x39156 and 0xF7
    for (int it : ps.items) CHECK(it != 38);  // 0x39164 slot emptied
    CHECK(c.techsOwned(owner) == owned0 + 1);  // FUN_00046e84 fired once
}

TEST(campaign_dig_on_nonrock_no_grant_t203) {
    // S3: the gate is the ROCK bit, not the item id. A dig completing where
    // NO rock exists (degenerate rewrite case; the original's buy could not
    // queue without legal rock) takes the normal activation tail 0x3917a:
    // the item STANDS and NO tech is granted.
    auto c = makeCampaignForDemolish(2024);
    int star = -1;
    for (int s = 0; s < static_cast<int>(c.galaxy().stars.size()); ++s)
        if (c.starOwner(s) >= 1) { star = s; break; }
    CHECK(star >= 0);
    auto& ps = const_cast<ag::PlanetState&>(c.planetAt(star));
    ps.surfaceCells = 11;
    for (int k = 0; k < 11; ++k) ps.cellClasses[k] = 1;   // ZERO rock
    ps.items = {5};
    ps.itemCells = {1};
    ps.capBase = 8;
    ps.pop = 7;
    ps.pendingItem = 38;
    ps.buildAcc = 10000;
    const int owner = c.starOwner(star);
    const int owned0 = c.techsOwned(owner);
    c.advance();
    bool digStands = false;
    for (int it : ps.items) if (it == 38) digStands = true;
    CHECK(digStands);                          // 0x3917a activation branch
    CHECK(c.techsOwned(owner) == owned0);      // no grant, no rng on grant
}

TEST(campaign_free_tech_grant_determinism_t203) {
    // Seeded determinism: two campaigns with identical seed produce the
    // identical grant sequence (rng_ stream, law-faithful uniform pick).
    auto a = makeCampaignForDemolish(99);
    auto b = makeCampaignForDemolish(99);
    for (int k = 0; k < 20; ++k)
        CHECK(a.freeTechGrantFor(1) == b.freeTechGrantFor(1));
}
