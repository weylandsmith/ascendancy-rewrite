// SPDX-License-Identifier: GPL-3.0-or-later

// t207 GUARANTEE-WAR CLAMP PIN — FUN_0003a174's post-handler site
// 0x3a25a..0x3a291 (invasion resolution) + the caller-thread closure
// (E8 census EXACTLY {0x39fba, 0x3a255, 0x4b875} edges into 0x43a4c).
// Law source: docs/re/_wip_t207.md S7a..S7e — verbatim capstone windows
// work/t207_w1..w16 + operand identities MEASURED 20/20 playcap saves
// (scripts/r207_opinion_census.py RC=0: [eax*2+0x12fb3]/eax=247a is
// diplo-row(a)+0x19d ability byte (distribution {0,2,11,19} == t202
// census); 0x12fdf+494v = row(v)+0x1c9 DECLARE_WAR; 0x12fc8+494v+2a = the
// attitude cell attacker->victim; 200/200 non-war pairs above their line).
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

// ---- T1: pure-law battery, verbatim 0x3a25a..0x3a291 ---------------------
TEST(invasion_guarantee_war_battery_t207) {
    ag::DipValues v;
    v.declareWar = 200;

    // (A1) AT-WAR SKIP 0x3a25d: the handler returned 0 (state==2 WAR guard
    // 0x43a97) -> jne taken -> NO clamp, cell untouched.
    int att = 600;
    ag::guaranteeWarOnInvasion(v, /*atWar=*/true, &att);
    CHECK(att == 600);

    // (A2) SLAM: not at war and cell STILL strictly above the line ->
    // := line - 10 (0x3a28c mov eax,edi; 0x3a28e sub eax,0xa; 0x3a291 store).
    att = 600;  // the MEASURED fresh-campaign state: START_ATTITUDE > DECL
    ag::guaranteeWarOnInvasion(v, false, &att);
    CHECK(att == 190);

    // (A3) EXACT BOUNDARY: cmp di,cell; jge skip — cell == line SKIPS.
    att = 200;
    ag::guaranteeWarOnInvasion(v, false, &att);
    CHECK(att == 200);

    // (A4) BELOW the line: untouched (the chooser owns it from here).
    att = 195;
    ag::guaranteeWarOnInvasion(v, false, &att);
    CHECK(att == 195);
    att = -5000;
    ag::guaranteeWarOnInvasion(v, false, &att);
    CHECK(att == -5000);

    // (A5) idempotence: a second invasion attempt against the SAME victim
    // (still not at war) changes NOTHING (190 is not > 200). The law is a
    // one-shot clamp to a line, NOT a repeated subtraction (contrast the
    // handler's -20 per shot).
    att = 190;
    ag::guaranteeWarOnInvasion(v, false, &att);
    CHECK(att == 190);

    // (A6) CEILING shape, not a floor: a cell far above lands at line-10
    // and NEVER below it (the t204 0x43acc family shape).
    v.declareWar = 510;
    att = 100000;
    ag::guaranteeWarOnInvasion(v, false, &att);
    CHECK(att == 500);
}

// ---- T2: chooser consequence — the clamp makes DA_DeclareWar fire --------
TEST(invasion_declare_war_cascade_t207) {
    ag::DipValues v;
    v.declareWar = 290;             // race00's live DECLARE_WAR (t204 pins)
    v.proposeAlliance = 1000000;    // keep the propose arm out of the way
    ag::DipPolicyState st;
    st.attitude = 340;              // START_ATTITUDE (race00, t204 pins)
    st.atWar = false;
    st.allied = false;
    ag::AttitudeModel mood(v);
    // Pre-clamp chooser at 340: declare-war needs att < 290 -> no.
    CHECK(ag::decideDipAction(v, mood, 1, &st) != ag::DipAction::DeclareWar);
    st.attitude = 340;              // decideDipAction may have moved it
    // Invasion attempt pays -20 (t204 handler 0x43abc leg): 320 >= 290.
    CHECK(ag::applyAttackDipCost(v, false, false, ag::kAttackDipGovByte,
                                 &st.attitude) == true);
    CHECK(st.attitude == 320);
    // ... clamp (0x3a291): 320 > 290 -> 280, strictly BELOW the line.
    ag::guaranteeWarOnInvasion(v, false, &st.attitude);
    CHECK(st.attitude == 280);
    CHECK(ag::decideDipAction(v, mood, 2, &st) == ag::DipAction::DeclareWar);
}

// ---- T3: end-to-end at the wired site (capture branch of combatPhase) ----
// Fixture mirrors test_diponattack_t204 (race00 att 340, DECLARE_WAR 290).
// The player invades with SA_SuperMarines (guaranteed capture, so the
// clamp site is reached deterministically): the FIRST capture advance pays
// -20 THEN clamps 320 -> 280 (the t204 pin's 320 becomes 280 exactly).
namespace {
struct T207Tables {
    ag::StarStats stats;
    std::vector<std::string> names;
    ag::ResearchTree tree;
    std::vector<ag::PlanetItem> items;
    std::vector<ag::Gizmo> gizmos;
};

ag::Campaign buildFixture207(std::vector<ag::DipFile> dips,
                             std::vector<ag::SpeciesAbility> ab,
                             int playerSpecies = -1) {
    static T207Tables* tabs = nullptr;
    if (!tabs) {
        tabs = new T207Tables();
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
    cfg.freeForAll = false;
    cfg.playerSpecies = playerSpecies;  // t208: -1 keeps T3's no-ability player
    std::string err;
    ag::Campaign c(cfg, g, &tabs->tree, tabs->items, tabs->gizmos, std::move(dips),
                   ab, &err);
    if (!err.empty()) std::abort();
    c.setStarOwnerForTest(1, 1);
    c.setStarOwnerForTest(2, 2);
    c.setStarOwnerForTest(3, 2);
    c.setStarOwnerForTest(4, 2);
    return c;
}
}  // namespace

TEST(invasion_combat_phase_clamp_t207) {
    std::string err;
    ag::DipFile df;
    if (!df.loadFromFile((kRepo / "extracted/ascend00/race00.dip").string(), &err))
        std::abort();
    ag::DipFile df2;
    if (!df2.loadFromFile((kRepo / "extracted/ascend00/race02.dip").string(), &err))
        std::abort();
    // Second never-allied AI (race02) keeps end-unit/Unification out (t204
    // fixture pitfall). NOTE (self-caught this session): the ability vector
    // is indexed by OWNER and the fixture gives owner 1 SuperMarines -- the
    // PLAYER (owner 0) has none, and no player capture occurs here, so this
    // pin covers the NEGATIVE side of the wiring: the clamp site (capture
    // branch) is NOT reached by a mere engagement -> att walks -20 only.
    // A positive e2e needs a guaranteed PLAYER capture (ability_[0]) --
    // banked for the next iteration (_wip_t207 S7e residue).
    auto c = buildFixture207({df, df2},
                             {ag::SpeciesAbility::SuperMarines,
                              ag::SpeciesAbility::HealShips});
    CHECK(c.dipStateAt(0).attitude == 340);
    c.setWarForTest(ag::kPlayer, 1, true);   // engagement gate open (t204 style)
    c.advance();                              // one s0->s1 engagement, repelled
    CHECK(c.dipStateAt(0).attitude == 320);   // -20 handler, NO clamp (no capture)
    CHECK((c.attackedMarks() & (1 << 1)) != 0);
}

// ---- T4 (t208): POSITIVE end-to-end — the clamp fires at the capture
// branch and the chooser cascade runs. Closes _wip_t207 S7e residue (a)
// (the ability vector indexes OWNER, so the player needs the ability via
// CampaignConfig::playerSpecies -> ability_[kPlayer], campaign.cpp:234-235,
// plus industry over the invasion ship-cost gate at campaign.cpp:1895 —
// setIndustryForTest makes that deterministic instead of riding turn-1
// accrual). Law: 340 -> handler -20 = 320 (still > DECL 290) -> clamp
// 0x3a291 -> 280 (strictly below the line) -> t180 chooser DeclareWar.
TEST(invasion_capture_war_e2e_t208) {
    std::string err;
    ag::DipFile df;
    if (!df.loadFromFile((kRepo / "extracted/ascend00/race00.dip").string(), &err))
        std::abort();
    ag::DipFile df2;
    if (!df2.loadFromFile((kRepo / "extracted/ascend00/race02.dip").string(), &err))
        std::abort();
    // PLAYER = SA_SuperMarines (invadesAlwaysSucceeds -> the capture branch
    // at campaign.cpp:1946 is reached regardless of the hull math).
    auto c = buildFixture207({df, df2},
                             {ag::SpeciesAbility::SuperMarines,
                              ag::SpeciesAbility::HealShips},
                             /*playerSpecies=*/static_cast<int>(
                                 ag::SpeciesAbility::SuperMarines));
    CHECK(c.dipStateAt(0).attitude == 340);
    CHECK(!c.dipStateAt(0).atWar);            // diplo STATE still peace
    c.setWarForTest(ag::kPlayer, 1, true);    // engagement gate (scenario war bit)
    c.setIndustryForTest(ag::kPlayer, 50.0);  // clears the 1895 ship-cost gate
    c.advance();
    // (E1) the capture RAN: star1 flipped to the player (owner flip 1969).
    CHECK(c.starOwner(1) == ag::kPlayer);
    // (E2) diplo STATE flipped: mood(1)==0 is already proven by T3's exact
    // 320 post-advance reading (green CI), so the full expected cascade
    // value is exact: clamp 280, chooser DeclareWar subtracts
    // negPlayerTurns/4 (diplomacy.cpp:243). Without the clamp the cell
    // would sit at 320 - neg/4 >= 290 -> act None -> atWar STAYS false;
    // both arms below are therefore distinguishing witnesses of the clamp.
    CHECK(c.dipStateAt(0).atWar);
    CHECK(c.dipStateAt(0).attitude == 280 - df.values.negPlayerTurns / 4);
    // (E3) the t204 mark still rides the engagement.
    CHECK((c.attackedMarks() & (1 << 1)) != 0);
}
