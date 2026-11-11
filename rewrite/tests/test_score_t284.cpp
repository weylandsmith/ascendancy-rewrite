// SPDX-License-Identifier: GPL-3.0-or-later

// t284 CONTROLLED-SYSTEMS producer pins (DAT_000482fb analog).
// Law: Ghidra FUN_00024274 (payload file 0x24274..0x243fc) + the FUN_00024f24
// tail, cross-checked instruction-for-instruction against objdump of
// work/ascend_payload.bin, WITNESSED LIVE by a t283 write watchpoint on guest
// 0x28A2FB, and corpus-replayed at 295/409 EXACT with a 409/409 lane-mark
// footprint (every miss is a pre-first-end-turn slot whose stored V is 0).
// Citations: docs/re/_wip_t284.md (the law + validation), docs/re/score.md
// S2/S6/S10/S17, docs/re/dosbox-wp-t283.md, docs/re/ships.md S23,
// docs/re/debugflags.md (STAR/LANE REVEAL mask identities).
#include "harness.h"
#include "game/campaign.h"

namespace ag = ascend::game;

// Seeded campaign factory (defined in test_campaign.cpp; t202b precedent).
ag::Campaign makeCampaignForDemolish(unsigned seed);

namespace {

// The player's home star: each owner holds exactly one star pre-expansion.
int playerHome(const ag::Campaign& c) {
    for (size_t s = 0; s < c.galaxy().stars.size(); ++s)
        if (c.starOwner(static_cast<int>(s)) == ag::kPlayer) return static_cast<int>(s);
    return -1;
}

// Reveal everything to the player and clear every AI claim, leaving only the
// player's home claimed: the flood's maximal operating point.
void openGalaxy(ag::Campaign& c) {
    for (size_t s = 0; s < c.galaxy().stars.size(); ++s) {
        c.setStarSelVisForTest(static_cast<int>(s), ag::kPlayer);
        if (c.starOwner(static_cast<int>(s)) > 0)
            c.setStarOwnerForTest(static_cast<int>(s), -1);
    }
}

}  // namespace

// 1. CADENCE: 0 at construction (DERIVED state, never restored — t283: scratch
// AND production 51.sav read 0 at load; recompute runs ONLY in the end-of-turn
// pass), and >=1 after the first advance while the home star is the player's
// (the FUN_00024f24 seed V=1 branch).
TEST(score_cadence_zero_then_one_t284) {
    auto c = makeCampaignForDemolish(7);
    CHECK(c.scoreStars() == 0);
    c.advance();
    CHECK(c.scoreStars() >= 1);
}

// 2. HOME-PRESENCE GATE (FUN_00024f24 reset branch): home star loses the
// player's presence bit -> V := 0, flood never runs. The pass always REWRITES
// the dword; no partial value survives.
TEST(score_home_loss_zeroes_t284) {
    auto c = makeCampaignForDemolish(7);
    c.advance();
    CHECK(c.scoreStars() >= 1);
    c.setStarOwnerForTest(playerHome(c), -1);
    c.recomputeScoreStarsForTest();
    CHECK(c.scoreStars() == 0);
}

// 3. FULL FLOOD + PRESENCE PRUNING. Revealed + unclaimed everywhere on a
// connected galaxy -> every lane is admitted, so V == 1 + laneCount. NOTE the
// unit: the producer increments PER ADMITTED LANE (the +0x21 mark is per-lane
// and a star reachable by two lanes is entered twice), so V is NOT bounded by
// the star count on a cyclic map — MEASURED against the original's own +0x2c
// lists (50 stars, distinct per-star incident-lane sets of size 1..4, 58 lanes;
// the corpus V=23 == 22 marked lanes + home). A hostile claim on a degree>=2
// star strictly lowers V, pruning whatever hangs behind it — the S6 t912
// 11->22 / S10 23->14 branch-jump mechanism.
TEST(score_flood_and_presence_prune_t284) {
    auto c = makeCampaignForDemolish(2026);
    const int n = static_cast<int>(c.galaxy().stars.size());
    const int lanes = static_cast<int>(c.galaxy().lanes.size());
    openGalaxy(c);
    c.recomputeScoreStarsForTest();
    CHECK(c.scoreStars() == 1 + lanes);

    int plant = -1, bestDeg = 0;
    for (int s = 0; s < n; ++s) {
        if (s == playerHome(c)) continue;
        int deg = 0;
        for (const auto& l : c.galaxy().lanes)
            if (l.a == s || l.b == s) ++deg;
        if (deg > bestDeg) { bestDeg = deg; plant = s; }
    }
    CHECK(plant >= 0 && bestDeg >= 2);
    c.setStarOwnerForTest(plant, 1);          // AI owner, un-allied
    c.recomputeScoreStarsForTest();
    CHECK(c.scoreStars() < 1 + lanes);
    CHECK(c.scoreStars() >= 1);               // the home side still floods
}

// 4. VISIBILITY GATE IS PLAYER-BIT-ONLY: with the map unclaimed but every
// star INVISIBLE to the player, the flood cannot cross a single lane -> V==1.
TEST(score_visibility_gate_is_player_bit_t284) {
    auto c = makeCampaignForDemolish(2026);
    const int n = static_cast<int>(c.galaxy().stars.size());
    for (int s = 0; s < n; ++s)
        if (c.starOwner(s) > 0) c.setStarOwnerForTest(s, -1);
    // NOTE: seedVisibility granted the home star's own bit; lanes never carry
    // the +0x17 test — the FAR STAR does, and unclaimed invisible stars fail.
    // The home's own bit does not help the far star, so V pins at 1 (+ any
    // far star that happens to be a claimed-visible one: none here).
    c.recomputeScoreStarsForTest();
    CHECK(c.scoreStars() == 1);
}

// 5. CONTEST GATE: an enemy transit crossing the home's lane prunes it even
// with the far star visible and unowned (the original compares the lane
// POINTER at ship+0x59; kind-5 lane orders measurably hold lane-pool
// pointers). Direction-free: either orientation contests.
TEST(score_contest_gate_t284) {
    auto c = makeCampaignForDemolish(2026);
    const int n = static_cast<int>(c.galaxy().stars.size());
    openGalaxy(c);
    const int home = playerHome(c);
    int la = -1, lb = -1;
    for (const auto& l : c.galaxy().lanes)
        if (l.a == home || l.b == home) { la = l.a; lb = l.b; break; }
    CHECK(la >= 0);
    c.recomputeScoreStarsForTest();
    const int free_ = c.scoreStars();
    CHECK(free_ == 1 + static_cast<int>(c.galaxy().lanes.size()));
    c.setFleetForTest({{1, la, lb}});
    c.recomputeScoreStarsForTest();
    CHECK(c.scoreStars() < free_);            // lane 1 cut
    c.setFleetForTest({{1, lb, la}});
    c.recomputeScoreStarsForTest();
    CHECK(c.scoreStars() < free_);            // reverse direction: same cut
    c.setFleetForTest({{0, la, lb}});         // the player's OWN traffic never
    c.recomputeScoreStarsForTest();           // contests (owner != player)
    CHECK(c.scoreStars() == free_);
}

// 6. DISPLAY PERCENT LAW (score.md S2 integer chain 0x280c4..0x280e3):
// percent = TRUNC(100*V/T), T = total stars. HONEST LIMIT: the corpus is ALL
// T=50 galaxies (S14 T census {50: 71023}), and 100*V/50 == 2V is always
// integral, so truncation-vs-rounding is NOT observable in any captured frame
// — this pin locks the FORMULA and the exact factor, not the rounding mode.
TEST(score_pct_formula_t284) {
    auto d = makeCampaignForDemolish(2026);
    const int n = static_cast<int>(d.galaxy().stars.size());
    openGalaxy(d);
    const int home = playerHome(d);
    for (int s = 0; s < n; ++s)              // partial flood: hostile claims
        if (s != home && (s % 7) == 0) d.setStarOwnerForTest(s, 1);
    d.recomputeScoreStarsForTest();
    const int v = d.scoreStars();
    CHECK(v > 0);
    CHECK(d.playerScorePct() == (100 * v) / n);
    CHECK(d.playerScorePct() == 2 * v);      // the measured T=50 specialisation
}

// 7. THE UNIT OF V IS LANES, NOT STARS. The producer marks the LANE record
// (+0x21) and increments once per admitted lane, so a star reachable by two
// lanes counts twice — the clean explanation for the S6 census oddity
// (V=22 while systems_any=14: the lane graph has cycles). Upper bound is
// therefore 1 + laneCount, NOT the star count.
TEST(score_unit_is_lanes_not_stars_t284) {
    auto c = makeCampaignForDemolish(2026);
    const int n = static_cast<int>(c.galaxy().stars.size());
    const int lanes = static_cast<int>(c.galaxy().lanes.size());
    CHECK(lanes > n);                        // seeded galaxy has cycles
    openGalaxy(c);
    c.recomputeScoreStarsForTest();
    CHECK(c.scoreStars() == 1 + lanes);      // > n: stars alone cannot reach it
    // and a single owned star (home only, everything else invisible) is V=1.
    auto d = makeCampaignForDemolish(2026);
    for (int s = 0; s < n; ++s)
        if (d.starOwner(s) > 0 && s != playerHome(d)) d.setStarOwnerForTest(s, -1);
    d.recomputeScoreStarsForTest();
    CHECK(d.scoreStars() == 1);
}
