// SPDX-License-Identifier: GPL-3.0-or-later

// t291 END-CTRL COMPARATOR PINS (OQ-021).
// Law: the vendor evaluator FUN_00024a34 (payload file 0x24b9c..0x24bbe, read
// verbatim — docs/re/_wip_t290.md S1, distilled to docs/re/score.md S19):
//
//     mov edx,[state+0x3333]; sar edx,16   ; T   == DAT_00016143 (total stars)
//     add edx,edx; idiv 3                  ; floor(2T/3)
//     inc eax                              ; floor(2T/3)+1
//     mov edi,[state+0x354eb]              ; V   == DAT_000482fb (controlled)
//     cmp eax,edi ; jg skip ; -> result 5  ; *** Control ***
//
// => Control victory iff V >= floor(2T/3)+1  <=>  V > 2T/3, strictly greater.
// The operand is the PRODUCED controlled-systems count V (score.md S17/S18 —
// a pruned lane flood from the home star), NOT the owned-star count. These
// pins stage V exactly and call the arm directly, so the boundary values are
// measured rather than inferred from ~1300 turns of dynamics.
#include "harness.h"
#include "game/campaign.h"

namespace ag = ascend::game;

// Seeded campaign factories (test_campaign.cpp; t202b/t284 extern-wrapper
// precedent). makeCampaignSized lets the boundary be tested at a galaxy size T
// where floor(2T/3)+1 differs from the >half bar (impossible at T=50).
ag::Campaign makeCampaignForDemolish(unsigned seed);
ag::Campaign makeCampaignSized(unsigned seed, int aiCount, int starCount);

namespace {

// t1 and earlier arms must be silent so checkVictory reaches end-ctrl:
// Extinct needs mine!=0 (the home colony is player's at t1), LastAlive needs
// >1 live power (all AI hold homes), Captured needs every AI home (none taken),
// Unification needs every live AI allied and no player war bit (FFA: none).
// Returns the campaign one turn in, with the caller free to stage V.
ag::Campaign stagedT1(unsigned seed, int aiCount, int stars) {
    auto c = makeCampaignSized(seed, aiCount, stars);
    c.advance();
    return c;
}

}  // namespace

// 1. THE T=50 BOUNDARY (the corpus galaxy size, score.md S14 T census
// {50: 71023}): threshold floor(100/3)+1 = 33+1 = 34. V=33 (66%) must NOT win;
// V=34 (68%) must. This is the value the whole OQ-021 chase chased: the corpus
// max V=23 was 11 steps away from arming, not 4.
TEST(control_threshold_t50_t291) {
    REQUIRE_DATA();
    auto c = stagedT1(2024, 6, 50);
    const int total = static_cast<int>(c.galaxy().stars.size());
    CHECK(total == 50);
    const int thr = (2 * total) / 3 + 1;
    CHECK(thr == 34);
    c.setScoreStarsForTest(thr - 1);
    CHECK(c.checkVictoryForTest() == ag::Victory::None);
    c.setScoreStarsForTest(thr);
    CHECK(c.checkVictoryForTest() == ag::Victory::Control);
}

// 2. THE LAW IS 2T/3, NOT T/2 — DISCRIMINATED ON A SMALL MAP. T=14:
// floor(28/3)+1 = 9+1 = 10, while the >half default arms at V=8. V=9 (64% of
// the galaxy, comfortably over half) must NOT win; V=10 must. Any galaxy where
// 2T mod 3 != 0 separates the two readings; T=14 is one.
TEST(control_bar_is_two_thirds_not_half_t291) {
    REQUIRE_DATA();
    auto c = stagedT1(7, 2, 14);
    const int total = static_cast<int>(c.galaxy().stars.size());
    CHECK(total == 14);
    CHECK((2 * total) % 3 != 0);              // discriminating galaxy size
    const int thr = (2 * total) / 3 + 1;      // 10
    const int halfBar = total / 2 + 1;        // 8 (the refuted default)
    CHECK(halfBar < thr);
    c.setScoreStarsForTest(halfBar);          // over half...
    CHECK(c.checkVictoryForTest() == ag::Victory::None);   // ...still not Control
    c.setScoreStarsForTest(thr - 1);          // 9 = 64% of the galaxy
    CHECK(c.checkVictoryForTest() == ag::Victory::None);
    c.setScoreStarsForTest(thr);
    CHECK(c.checkVictoryForTest() == ag::Victory::Control);
}

// 3. THE OPERAND IS V, NOT OWNED STARS. Claiming every non-home star for the
// player (so starsOwned is large: 12/14) while the flood reads low must NOT
// win. This is the arm's other half: the vendor compares DAT_482fb, which a
// contested map keeps far below the owned count (score.md S10: V=23 with the
// player owning more stars; S6 branch-jumps 11<->22).
TEST(control_operand_is_v_not_owned_t291) {
    REQUIRE_DATA();
    auto c = stagedT1(7, 2, 14);
    const int total = static_cast<int>(c.galaxy().stars.size());
    int home = -1;
    for (int s = 0; s < total; ++s)
        if (c.starOwner(s) == ag::kPlayer) home = s;
    CHECK(home >= 0);
    int claimed = 0;
    for (int s = 0; s < total; ++s) {
        if (s == home) continue;
        if (c.starOwner(s) > 0) continue;     // leave AI homes alone (end-capt)
        c.setStarOwnerForTest(s, ag::kPlayer);
        ++claimed;
    }
    CHECK(claimed >= 8);                      // a big owned share...
    c.setScoreStarsForTest(1);                // ...but a home-only flood.
    CHECK(c.checkVictoryForTest() == ag::Victory::None);
    c.setScoreStarsForTest((2 * total) / 3 + 1);
    CHECK(c.checkVictoryForTest() == ag::Victory::Control);
}

// 4. END-TO-END CADENCE: the arm reads the value the producer wrote THIS turn
// (advance() runs recomputeScoreStars() then checkVictory(), the vendor's
// end-turn order, _wip_t290 S2). A SINGLE AI keeps the other arms silent while
// its home star stays hostile (no LastAlive, no Captured); revealing the whole
// map lets the flood flood every lane except those ending on that home, which
// on a 50-star cyclic map is far above the bar. The exact flood value is the
// producer's business (test_score_t284 pins it); this pin locks the WIRING:
// a real advance() whose recomputed V >= floor(2T/3)+1 reports Control.
TEST(control_end_to_end_flood_wins_t291) {
    REQUIRE_DATA();
    auto c = makeCampaignSized(2026, 1, 50);
    const int total = static_cast<int>(c.galaxy().stars.size());
    const int thr = (2 * total) / 3 + 1;
    CHECK(thr == 34);
    for (size_t s = 0; s < c.galaxy().stars.size(); ++s)
        c.setStarSelVisForTest(static_cast<int>(s), ag::kPlayer);
    ag::Victory v = c.advance();
    CHECK(c.scoreStars() >= thr);             // producer ran first, V is high
    CHECK(v == ag::Victory::Control);         // comparator saw this turn's V
}
