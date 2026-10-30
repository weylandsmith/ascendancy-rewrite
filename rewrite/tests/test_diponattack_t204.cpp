// t204 DIPLOMACY-ON-ATTACK PIN — FUN_00043a4c (0x43a4c..0x43b0e) + its
// combat call site 0x4b875 (fire precedes the shield/hull subtraction at
// 0x4b87a/0x4b888) + the [0x48304] attacked-bitmap permanence.
// Law source: docs/re/_wip_t204.md S1..S4 (verbatim capstone re-verification
// of work/ascend_restored.bin this session + live pointer-law census:
// byte[0x13bc4]==1 in 20/20 playcap saves, word[0x13b98]==4, global
// [0x48304]==0 in 20/20). Gap map row 13 (ai-dossier.md S8).
#include "game/campaign.h"
#include "game/diplomacy.h"
#include "harness.h"

#include <cstdlib>
#include <filesystem>
#include <string>
#include <vector>

namespace ag = ascend::game;
namespace fs = std::filesystem;

#ifndef ASCENDANCY_SOURCE_DIR
#define ASCENDANCY_SOURCE_DIR "."
#endif
static const fs::path kRepo = ASCENDANCY_SOURCE_DIR;

// ---- T1: pure-law battery, verbatim 0x43a4c ------------------------------
TEST(diponattack_law_battery_t204) {
    ag::DipValues v;  // breakAlliance set per case (word[obj+0x1cf] analog)

    // (A1) AT-WAR GUARD 0x43a90: state==2 -> xor eax,eax;ret — NO attitude
    // write, NO hostility mark (return false is the original's 0 path).
    v.breakAlliance = 0;  // (irrelevant on this path)
    int att = 500;
    CHECK(ag::applyAttackDipCost(v, /*atWar=*/true, /*allied=*/false, 1, &att) ==
          false);
    CHECK(att == 500);

    // (A2) SUBTRAHEND LADDER 0x43a99..0x43aa2: d = 10*(govByte+1).
    // govByte==1 is the LIVE scenario value (censused 20/20 saves).
    for (int gov = 0; gov <= 2; ++gov) {
        att = 1000;
        CHECK(ag::applyAttackDipCost(v, false, false, gov, &att) == true);
        CHECK(att == 1000 - 10 * (gov + 1));  // -10 / -20 / -30
    }

    // (A3) ALLIANCE DOUBLING 0x43aa5: state==3 -> add edx,edx.
    // breakAlliance ABOVE every post-hit attitude here -> the ceiling arm
    // (att > line) never engages. [t204 note: line-10 semantics make a LOW
    // line the ENGAGE condition, not the skip condition — first-draft -500
    // was inverted, fixed same session.]
    v.breakAlliance = 100000;
    att = 1000;
    CHECK(ag::applyAttackDipCost(v, false, true, 1, &att) == true);
    CHECK(att == 960);  // -40
    att = 1000;
    CHECK(ag::applyAttackDipCost(v, false, true, 2, &att) == true);
    CHECK(att == 940);  // -60

    // (A4) CEILING 0x43acc..0x43ae7 (cmp new,bx; JLE skip) — a CEILING, not
    // a floor, applied iff state==3. breakAlliance==510 fixture:
    v.breakAlliance = 510;
    // strictly ABOVE the line -> slam to line-10:
    att = 560;  // 560-40=520 > 510  -> 500
    CHECK(ag::applyAttackDipCost(v, false, true, 1, &att) == true);
    CHECK(att == 500);
    // EXACT boundary: new == line -> JLE skips, value STAYS (550-40=510).
    att = 550;
    CHECK(ag::applyAttackDipCost(v, false, true, 1, &att) == true);
    CHECK(att == 510);
    // below the line: untouched (400-40=360).
    att = 400;
    CHECK(ag::applyAttackDipCost(v, false, true, 1, &att) == true);
    CHECK(att == 360);
    // same numbers WITHOUT the alliance (state != 3): no ceiling ever.
    att = 560;
    CHECK(ag::applyAttackDipCost(v, false, false, 1, &att) == true);
    CHECK(att == 540);

    // (A5) return TRUE is the -1 bitmap path at 0x43b00: set REGARDLESS of
    // the subtrahend magnitude (0x43aee runs after the store unconditionally
    // on the non-war leg) — govByte=-1 (d==0) still marks.
    att = 700;
    CHECK(ag::applyAttackDipCost(v, false, false, -1, &att) == true);
    CHECK(att == 700);

    // (A6) the live scenario constant matches the census value.
    CHECK(ag::kAttackDipGovByte == 1);
}

// Small deterministic fixture: 5-star line, aiCount 1 with race00 (Minions,
// START_ATTITUDE 340, DECLARE_WAR 290, BREAK_ALLIANCE 510, NEG_PLAYER_TURNS
// 99, NO BIO oscillation keys -> mood()==0 makes the attitude arithmetic
// EXACT). s0 player; s1..s4 owner 1 -> the ONLY player-attacker engagement
// pair is s0->s1 (exactly one law call per combat), while the AI's s1->s0
// pair must cost nothing (a != kPlayer, S4/D2).
struct T204Tables {
    ag::StarStats stats;
    std::vector<std::string> names;
    ag::ResearchTree tree;
    std::vector<ag::PlanetItem> items;
    std::vector<ag::Gizmo> gizmos;
};

static ag::Campaign buildFixture(std::vector<ag::DipFile> dips,
                                 std::vector<ag::SpeciesAbility> ab,
                                 std::vector<int> owners = {1, 1, 1, 1}) {
    static T204Tables* tabs = nullptr;
    if (!tabs) {
        tabs = new T204Tables();
        std::string e2;
        auto st = ag::StarStats::load((kRepo / "extracted/ascend00/starstat.txt").string(), &e2);
        if (!st) std::abort();
        tabs->stats = *st;
        tabs->names = ag::loadStarNames((kRepo / "extracted/ascend00/names.txt").string(), &e2);
        if (tabs->names.empty()) std::abort();
        tabs->tree = ag::ResearchTree::loadFromFile(
            (kRepo / "extracted/ascend00/restree.txt").string(), e2);
        tabs->items = ag::loadPlanItems(
            (kRepo / "extracted/ascend00/planitem.txt").string(), e2);
        if (tabs->items.size() != 39) std::abort();
        tabs->gizmos = ag::loadGizmos(
            (kRepo / "extracted/ascend00/gizmos.txt").string(), e2);
        if (tabs->gizmos.size() != 76) std::abort();
    }
    ag::Galaxy g;
    const char* nm[5] = {"Alpha", "Betray", "Gamma", "Delta", "Home"};
    for (int i = 0; i < 5; ++i) {
        ag::Star st;
        ag::Planet pl;
        pl.index = 0;
        pl.name = std::string(nm[i]) + " I";
        st.id = i;
        st.x = 100 * i;
        st.y = 0;
        st.name = nm[i];
        st.planets.push_back(pl);
        g.stars.push_back(st);
    }
    for (int i = 0; i + 1 < 5; ++i) g.lanes.push_back({i, i + 1});
    ag::CampaignConfig cfg;
    cfg.seed = 4242;
    cfg.aiCount = static_cast<int>(dips.size());
    cfg.freeForAll = false;  // war_ bits START CLEARED; pins set them
    std::string err;
    ag::Campaign c(cfg, g, &tabs->tree, tabs->items, tabs->gizmos, std::move(dips),
                   ab, &err);
    if (!err.empty()) std::abort();
    // Owner set: s0 player, s1..s4 per `owners` (default all owner 1).
    const int own[4] = {owners[0], owners.size() > 1 ? owners[1] : 1,
                        owners.size() > 2 ? owners[2] : 1,
                        owners.size() > 3 ? owners[3] : 1};
    for (int s = 1; s < 5; ++s) c.setStarOwnerForTest(s, own[s - 1]);
    return c;
}

// ---- T2: end-to-end at the cited call site 0x4b875 ------------------------
TEST(diponattack_combat_phase_t204) {
    std::string err;
    ag::DipFile df;
    if (!df.loadFromFile((kRepo / "extracted/ascend00/race00.dip").string(), &err))
        std::abort();
    auto c = buildFixture({df}, {ag::SpeciesAbility::HealShips});
    CHECK(c.dipStateAt(0).attitude == 340);      // START_ATTITUDE
    CHECK(c.dipStateAt(0).atWar == false);
    CHECK(c.attackedMarks() == 0);               // mirrors [0x48304]==0 census

    // No war yet -> combatPhase engages nothing -> firing costs nothing.
    c.advance();
    CHECK(c.dipStateAt(0).attitude == 340);
    CHECK(c.attackedMarks() == 0);

    // The player fires on a non-at-war power (symmetric war bit set is the
    // rewrite's engagement gate; dipState_.atWar stays FALSE = desync state
    // the original models directly: shots before any declared-war state).
    c.setWarForTest(ag::kPlayer, 1, true);
    c.advance();  // combatPhase: one s0->s1 pair -> d = 10*(1+1) = 20
    CHECK(c.dipStateAt(0).attitude == 320);      // 340 - 20, EXACT
    CHECK((c.attackedMarks() & (1 << 1)) != 0);  // victim = owner 1
    CHECK(c.dipStateAt(0).allied == false);

    // Cascade to the t189b-adjacent law the cost feeds: 20/turn walks the
    // victim down its own row. t2: 300; t3: 280 < DECLARE_WAR 290 ->
    // diplomacyPhase declares (st.atWar=true, att -= 99/4 = 24 -> 256);
    // t4+: the handler's at-war guard 0x43a90 STOPS charging (att pinned).
    c.advance();
    CHECK(c.dipStateAt(0).attitude == 300);
    c.advance();
    CHECK(c.dipStateAt(0).atWar == true);        // declared at att 280
    CHECK(c.dipStateAt(0).attitude == 256);      // 280 - 99/4 (int div)
    c.advance();
    CHECK(c.dipStateAt(0).attitude == 256);      // AT WAR: no more cost
    c.advance();
    CHECK(c.dipStateAt(0).attitude == 256);

    // PERMANENCE: peace (war table cleared) never clears the mark, and with
    // st.atWar still true re-war fires at zero cost (0x43a90).
    c.setWarForTest(ag::kPlayer, 1, false);
    for (int t = 0; t < 3 && !c.over(); ++t) c.advance();
    CHECK((c.attackedMarks() & (1 << 1)) != 0);  // SURVIVES peace
    CHECK(c.dipStateAt(0).attitude == 256);
    c.setWarForTest(ag::kPlayer, 1, true);
    c.advance();
    CHECK(c.dipStateAt(0).attitude == 256);      // at-war state still sticks
    CHECK((c.attackedMarks() & ~static_cast<unsigned char>(1 << 1)) == 0);
    // No spurious bits: only victim owner 1 was ever marked.
}

// ---- T3: alliance violation (state-3 doubling + ceiling, end-to-end) -----
TEST(diponattack_alliance_violation_t204) {
    std::string err;
    ag::DipFile df;
    if (!df.loadFromFile((kRepo / "extracted/ascend00/race00.dip").string(), &err))
        std::abort();
    df.values.proposeAlliance = 100;  // below START_ATTITUDE 340 -> t1 ally
    // Second AI (Orfa, PROPOSE_ALLIANCE 760, DECLARE_WAR 210, att 420 +-
    // small mood drift): NEVER allies/war-red over the pin window, so
    // checkVictory's end-unit (every LIVE AI allied) cannot fire at t1 and
    // kill the campaign (a 1-AI alliance fixture trips Unification instantly
    // — every later advance() then no-ops; caught by first run).
    ag::DipFile df2;
    if (!df2.loadFromFile((kRepo / "extracted/ascend00/race02.dip").string(), &err))
        std::abort();
    auto c = buildFixture({df, df2},
                          {ag::SpeciesAbility::HealShips, ag::SpeciesAbility::HealShips},
                          {1, 2, 2, 2});
    c.advance();                                   // alliance forms (t189b 3)
    CHECK(c.dipStateAt(0).allied == true);
    CHECK(!c.over());

    // Player fires on the ALLY mid-frame (state-3 row): d doubles to 40.
    // att 340-40 = 300 is BELOW the 510 line -> ceiling does not engage;
    // the same-turn diplomacyPhase sees 300 < BREAK_ALLIANCE and breaks.
    c.setWarForTest(ag::kPlayer, 1, true);
    c.advance();
    CHECK(c.dipStateAt(0).allied == false);        // alliance died of the shot
    CHECK(c.dipStateAt(0).attitude == 276);        // 300 - 99/4 break penalty
    CHECK((c.attackedMarks() & (1 << 1)) != 0);    // hostility mark
}

// ---- T5 (t205): the [0x48304] mirror is a PER-STAR ARRAY ------------------
// t205 adjudication (docs/re/_wip_t205.md): 0x43afa ORs 1<<victim into
// byte[0x48304 + star_index] (dword[edi+2]>>16 == the arg-2 STAR record's own
// index, measured k<50 20/20 saves), NOT one global race-bitmap byte. A
// per-race global would light the bit for every star; the array lights ONLY
// the engagement-location cell. Fixture: s1 owner 1, s2..s4 owner 2 (never
// fired at here) — after the s0->s1 shot, attackedAt(1) carries bit 1<<1 and
// every other cell is zero.
TEST(diponattack_mark_is_per_star_t205) {
    std::string err;
    ag::DipFile df;
    if (!df.loadFromFile((kRepo / "extracted/ascend00/race00.dip").string(), &err))
        std::abort();
    auto c = buildFixture({df}, {ag::SpeciesAbility::HealShips});
    c.setWarForTest(ag::kPlayer, 1, true);
    c.advance();  // one s0->s1 engagement at star 1 -> d=20, mark written
    CHECK((c.attackedMarks() & (1 << 1)) != 0);   // reduce-view still works
    CHECK((c.attackedAt(1) & (1 << 1)) != 0);     // the ENGAGEMENT STAR cell
    CHECK(c.attackedAt(0) == 0);                  // player's own star: clean
    CHECK(c.attackedAt(2) == 0);                  // other stars: clean
    CHECK(c.attackedAt(3) == 0);
    CHECK(c.attackedAt(4) == 0);
    CHECK(c.attackedAt(99) == 0);                 // out-of-range safe
}

TEST(diponattack_alliance_ceiling_t204) {
    // The 0x43acc CEILING end-to-end: attitude high enough that even the
    // doubled hit leaves it ABOVE the victim's break-alliance line.
    std::string err;
    ag::DipFile df;
    if (!df.loadFromFile((kRepo / "extracted/ascend00/race00.dip").string(), &err))
        std::abort();
    df.values.proposeAlliance = 100;
    ag::DipFile df2;
    if (!df2.loadFromFile((kRepo / "extracted/ascend00/race02.dip").string(), &err))
        std::abort();
    auto c = buildFixture({df, df2},
                          {ag::SpeciesAbility::HealShips, ag::SpeciesAbility::HealShips},
                          {1, 2, 2, 2});
    c.advance();
    CHECK(c.dipStateAt(0).allied == true);
    CHECK(!c.over());
    // const_cast is the established harness idiom (planetAt, t45).
    auto& st = const_cast<ag::DipPolicyState&>(c.dipStateAt(0));
    st.attitude = 560;
    c.setWarForTest(ag::kPlayer, 1, true);
    c.advance();
    // 560 - 40 = 520 > 510 -> CEILING slams to 510-10=500 (0x43ae4); then
    // 500 < 510 still breaks the alliance same turn (-99/4 = -24 -> 476).
    // WITHOUT the ceiling the break would NOT have fired (520 > 510) — the
    // handler guarantees alliance death after a violation shot.
    CHECK(c.dipStateAt(0).allied == false);
    CHECK(c.dipStateAt(0).attitude == 476);
    CHECK((c.attackedMarks() & (1 << 1)) != 0);
}

// ---- T6 (t206): CHANNEL SEPARATION — the mirror never carries bit 0 ------
// t206 consumer law (docs/re/diplomacy.md §18): [0x48304]'s bit 0 is a
// SEPARATE contact-notice latch (producers 0x4611c/0x4623e, per-call
// clear-all + re-latch-one in 0x24dd0), NEVER written by the attack handler
// 0x43afa for a non-zero victim. The rewrite models player-attacker
// engagements only (victims are AI races 1+), so its mirror must stay a
// pure victim-bit field: after every fired turn, bit 0 of every cell and of
// the reduced view is 0, and victim bits land exactly on engagement stars.
TEST(mark_channels_separate_t206) {
    std::string err;
    ag::DipFile df;
    if (!df.loadFromFile((kRepo / "extracted/ascend00/race00.dip").string(), &err))
        std::abort();
    auto c = buildFixture({df}, {ag::SpeciesAbility::HealShips});
    CHECK(c.attackedMarks() == 0);
    c.setWarForTest(ag::kPlayer, 1, true);
    for (int t = 0; t < 3 && !c.over(); ++t) c.advance();
    CHECK((c.attackedMarks() & (1 << 1)) != 0);
    CHECK((c.attackedMarks() & 1) == 0);          // latch channel absent
    CHECK((c.attackedAt(1) & 1) == 0);            // per-cell bit 0 never set
    for (int s = 0; s < 5; ++s)
        CHECK((c.attackedAt(s) & static_cast<unsigned char>(~(1 << 1))) == 0);
}
