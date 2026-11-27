// SPDX-License-Identifier: GPL-3.0-or-later

// tXT-1 PEACE-START PIN (D32: "very dense cluster + seven species -> exits
// t20; average density -> survives"). ROOT CAUSE MEASURED: the arcade
// default CampaignConfig::freeForAll=true wrote war_[x][y]=1 for EVERY pair
// at scenario init, so a border AI invaded the idle player's home and took
// it (seed 1, stars=100: '[t20] owner 1 captured Phoebe' -> checkVictory
// mine==0 -> Victory::Extinct, campaign.cpp:2270). Vendor law says fresh
// campaigns are NOT at war:
//   - docs/re/diplomacy.md §19: "measured: 200/200 fresh-campaign non-war
//     pairs sit at START_ATTITUDE 600 > DECL 210" (r207_opinion_census.py,
//     20 playcap saves);
//   - §13.3 enum law: the AT-WAR writer is the dialogue action case bl=2
//     (0x455cb) — scenario seeding never writes war;
//   - §11 live witness: pre-war every pair sat at relation state 1.
// The cited escalation channel (guaranteeWarOnInvasion, FUN_0003a174
// post-handler 0x3a25a..0x3a291) NO-OPS against an already-at-war victim,
// so the FFA default also pre-empted the vendor's only war-start path.
#include "game/campaign.h"
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

namespace {

struct Txt1Tables {
    ag::StarStats stats;
    std::vector<std::string> names;
    ag::ResearchTree tree;
    std::vector<ag::PlanetItem> items;
    std::vector<ag::Gizmo> gizmos;
    std::vector<ag::DipFile> ai;
};

const Txt1Tables& txt1Tables() {
    static const Txt1Tables t = [] {
        Txt1Tables x;
        std::string err;
        auto st = ag::StarStats::load((kRepo / "extracted/ascend00/starstat.txt").string(), &err);
        if (!st) std::abort();
        x.stats = *st;
        x.names = ag::loadStarNames((kRepo / "extracted/ascend00/names.txt").string(), &err);
        if (x.names.empty()) std::abort();
        x.tree = ag::ResearchTree::loadFromFile((kRepo / "extracted/ascend00/restree.txt").string(), err);
        x.items = ag::loadPlanItems((kRepo / "extracted/ascend00/planitem.txt").string(), err);
        if (x.items.size() != 39) std::abort();
        x.gizmos = ag::loadGizmos((kRepo / "extracted/ascend00/gizmos.txt").string(), err);
        if (x.gizmos.size() != 76) std::abort();
        for (int i = 0; i < 6; ++i) {
            ag::DipFile df;
            char path[256];
            std::snprintf(path, sizeof(path), "%s/extracted/ascend00/race%02d.dip",
                          ASCENDANCY_SOURCE_DIR, i);
            if (!df.loadFromFile(path, &err)) std::abort();
            x.ai.push_back(std::move(df));
        }
        return x;
    }();
    return t;
}

// The D32 repro shape: density-highest rung (100 stars, mapgen.md OQ-012(a)
// measured ladder) + seven species (aiCount 6 + player = 7 owners == the
// wheel word domain max, menulaw.h B2). freeForAll left at the STRUCT
// DEFAULT on purpose — the pin must fail the moment the default flips back
// to true (mutation M1).
ag::Campaign denseSeven(unsigned seed) {
    const Txt1Tables& t = txt1Tables();
    ag::CampaignConfig cfg;
    cfg.seed = seed;
    cfg.aiCount = 6;
    ag::MapConfig mc;
    mc.seed = seed;
    mc.starCount = 100;
    std::string err;
    ag::Campaign c(cfg, ag::MapGenerator(mc, t.stats, t.names).generate(),
                   &t.tree, t.items, t.gizmos, t.ai, std::vector<ag::SpeciesAbility>(), &err);
    if (!err.empty()) std::abort();
    return c;
}

}  // namespace

// T1: a fresh campaign starts at PEACE on every pair (the vendor init law;
// the FFA default removal is the shipped fix).
TEST(peace_start_default_tXT1) {
    REQUIRE_DATA();
    const Txt1Tables& t = txt1Tables();
    ag::CampaignConfig cfg;
    cfg.seed = 1;
    cfg.aiCount = 6;
    ag::MapConfig mc;
    mc.seed = 1;
    std::string err;
    ag::Campaign c(cfg, ag::MapGenerator(mc, t.stats, t.names).generate(),
                   &t.tree, t.items, t.gizmos, t.ai, std::vector<ag::SpeciesAbility>(), &err);
    if (!err.empty()) std::abort();
    for (int a = 0; a < 7; ++a)
        for (int b = 0; b < 7; ++b)
            if (a != b) CHECK(!c.atWar(a, b));
}

// T2: the D32 soak. dense+7, idle player, 60 turns: the player still owns
// >=1 star and no Extinct fired on ANY of the three seeds the repro matrix
// ran (seed 1 stars=100 DIED t20 pre-fix).
TEST(dense_seven_survives_60_tXT1) {
    REQUIRE_DATA();
    for (unsigned seed : {1u, 2u, 3u}) {
        ag::Campaign c = denseSeven(seed);
        ag::Victory v = ag::Victory::None;
        for (int i = 0; i < 60 && v == ag::Victory::None; ++i) v = c.advance();
        CHECK(v != ag::Victory::Extinct);
        CHECK(c.starsOwned(0) >= 1);
    }
}

// T3: war still STARTS through the cited channel, not through init: the
// guarantee-war clamp slams a peace victim under its declare line (pure law,
// verbatim 0x3a291) and the chooser then fires DeclareWar. (The end-to-end
// wired-site leg is pinned in test_invasion_war_t207 T3; this leg pins that
// retiring the FFA default left the vendor path as the ONLY entry.)
TEST(war_starts_via_clamp_not_init_tXT1) {
    REQUIRE_DATA();
    ag::DipValues v;
    v.declareWar = 290;               // race00's live DECLARE_WAR (t204 pins)
    v.proposeAlliance = 1000000;      // keep the propose arm out of the way
    int att = v.declareWar + 50;      // a peace-time cell above the line
    ag::guaranteeWarOnInvasion(v, /*victimAtWar=*/false, &att);
    CHECK(att == 280);                // line - 10, strictly below
    ag::DipPolicyState st;
    st.attitude = att;
    ag::AttitudeModel mood(v);
    CHECK(ag::decideDipAction(v, mood, 5, &st) == ag::DipAction::DeclareWar);
    // The at-war victim keeps its cell untouched (0x3a25d) — an existing war
    // needs no clamp.
    att = 280;
    ag::guaranteeWarOnInvasion(v, /*victimAtWar=*/true, &att);
    CHECK(att == 280);
}
