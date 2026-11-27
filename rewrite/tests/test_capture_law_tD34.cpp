// SPDX-License-Identifier: GPL-3.0-or-later

// tD34 CAPTURE-LAW PIN (D33-L1: "there's no way any player would be able to
// conquer another race on turn 20 ... every player should start out with an
// empty planet"). LAW (FUN_0003a174 re-derived FUN-by-FUN this session,
// docs/re/_wip_tD34.md S2): the success gate 0x3a45c reads EXACTLY three
// operands —
//   count   = cidx-0x49 (Invasion Module) slots on the CARRIER record
//             (walk 0x3a2a2..0x3a2c5, cap +0x15a, stride 7 from +0xab);
//   shields = ACTIVE planet items 18 Surface Shield (+1) / 19 Mega (+2)
//             (deficit walk 0x3a2c9..0x3a325);
//   forced  = attacker ability byte row+0x19d == 0 (SA_SuperMarines;
//             0x3a20b probe, forces need := 1 at 0x3a34e).
// SUCCESS iff count > shields OR forced. POP/POWER/FIREPLAY NEVER ENTER.
// The resolver runs only for a carrier-borne attempt (0x42d09 selects a
// cidx-0x49 ship), and consumption 0x3a360..0x3a38b (need = min(count,
// shields+1), forced 1) runs BEFORE the success test — a repelled invasion
// still burns its modules. The pre-tD34 port decider (bridge C4 garrison
// death) let a pop-rich empire flip owners with ZERO fleet: the illegal
// t20 home-capture class.
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

struct D34Tables {
    ag::StarStats stats;
    std::vector<std::string> names;
    ag::ResearchTree tree;
    std::vector<ag::PlanetItem> items;
    std::vector<ag::Gizmo> gizmos;
    std::vector<ag::DipFile> ai;
};

const D34Tables& d34Tables() {
    static const D34Tables t = [] {
        D34Tables x;
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

// 5-star chain Alpha-Betray-Gamma-Delta-Home; player owns Alpha (0), owner 1
// owns Betray (1) — the contested border; owner 2 owns the rest (a second
// never-allied AI keeps Unification out, t207 fixture law).
ag::Campaign fixtureD34(int playerSpecies = -1) {
    const D34Tables& t = d34Tables();
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
    cfg.aiCount = 2;
    cfg.freeForAll = false;
    cfg.playerSpecies = playerSpecies;
    std::vector<ag::SpeciesAbility> ab{
        ag::SpeciesAbility::HealShips, ag::SpeciesAbility::BuildOnBlack};
    std::string err;
    ag::Campaign c(cfg, g, &t.tree, t.items, t.gizmos,
                   {t.ai[0], t.ai[1]}, ab, &err);
    if (!err.empty()) std::abort();
    c.setStarOwnerForTest(1, 1);
    c.setStarOwnerForTest(2, 2);
    c.setStarOwnerForTest(3, 2);
    c.setStarOwnerForTest(4, 2);
    return c;
}

int itemIdD34(const std::string& name) {
    const D34Tables& t = d34Tables();
    for (size_t i = 0; i < t.items.size(); ++i)
        if (t.items[i].name == name) return static_cast<int>(i);
    std::abort();
}

bool anyCaptureEvent(const ag::Campaign& c) {
    for (const auto& e : c.events())
        if (e.text.find("captured") != std::string::npos) return true;
    return false;
}

}  // namespace

// T1 (L1 LAW, the user's impossibility claim): dense+7 idle-player runs —
// ZERO capture events in the first 60 turns on every seed, and the module
// ledger starts at zero (the resolver operand does not exist yet while
// everyone is still building their first structure).
TEST(capture_impossible_early_tD34) {
    REQUIRE_DATA();
    const D34Tables& t = d34Tables();
    for (unsigned seed : {1u, 2u, 3u}) {
        ag::CampaignConfig cfg;
        cfg.seed = seed;
        cfg.aiCount = 6;
        ag::MapConfig mc;
        mc.seed = seed;
        mc.starCount = 100;
        std::string err;
        ag::Campaign c(cfg, ag::MapGenerator(mc, t.stats, t.names).generate(),
                       &t.tree, t.items, t.gizmos, t.ai,
                       std::vector<ag::SpeciesAbility>(), &err);
        if (!err.empty()) std::abort();
        for (int o = 0; o < 7; ++o) CHECK(c.invasionModules(o) == 0);
        for (int i = 0; i < 60 && !c.over(); ++i) c.advance();
        CHECK(!anyCaptureEvent(c));
        CHECK(c.starsOwned(0) >= 1);
    }
}

// T2 (0x3a45c POSITIVE, non-forced): count(2) > shields(0) -> capture;
// consumption need = min(2, 0+1) = 1 leaves one module (0x3a360..0x3a38b).
TEST(capture_count_gt_shields_tD34) {
    REQUIRE_DATA();
    auto c = fixtureD34();
    c.setWarForTest(ag::kPlayer, 1, true);
    c.setInvasionModulesForTest(ag::kPlayer, 2);
    c.advance();
    CHECK(c.starOwner(1) == ag::kPlayer);
    CHECK(c.invasionModules(ag::kPlayer) == 1);
    CHECK(anyCaptureEvent(c));
}

// T3 (0x3a45c NEGATIVE + burn + attempt-time clamp): count(1) <= shields(1)
// -> NO capture, but the modules are consumed BEFORE the success test, and
// the guarantee-war clamp fires on the ATTEMPT (t209 position law): 340 ->
// gun -20 -> clamp 280 -> chooser DeclareWar.
TEST(repelled_invasion_burns_and_clamps_tD34) {
    REQUIRE_DATA();
    ag::DipFile df;
    std::string err;
    if (!df.loadFromFile((kRepo / "extracted/ascend00/race00.dip").string(), &err))
        std::abort();
    CHECK(df.values.declareWar == 290);
    auto c = fixtureD34();
    c.addItemForTest(1, itemIdD34("Surface Shield"));   // shields = 1
    c.setWarForTest(ag::kPlayer, 1, true);
    c.setInvasionModulesForTest(ag::kPlayer, 1);
    c.advance();
    CHECK(c.starOwner(1) == 1);                        // repelled
    CHECK(c.invasionModules(ag::kPlayer) == 0);        // burned at 0x3a360
    CHECK(!anyCaptureEvent(c));
    // The clamp discriminator (t208 shape): WITHOUT the attempt-time clamp
    // the cell would sit at 320 - neg/4 >= 290 -> chooser None; WITH it,
    // 280 (DECL-10) -> DeclareWar subtracts negPlayerTurns/4.
    CHECK(c.dipStateAt(0).attitude == 280 - df.values.negPlayerTurns / 4);
}

// T4 (forced leg is NOT a decider-override): SA_SuperMarines with ZERO
// modules cannot capture — the resolver never runs without a carrier-borne
// module (0x42d09). The port's forced power is need := 1 (0x3a34e), i.e.
// "always succeeds AT AN ATTEMPT", not "always has an attempt".
TEST(supermarines_without_modules_cannot_capture_tD34) {
    REQUIRE_DATA();
    auto c = fixtureD34(static_cast<int>(0));          // specnum 0 = Minions
    c.setAbilityForTest(ag::kPlayer, ag::SpeciesAbility::SuperMarines);
    c.setWarForTest(ag::kPlayer, 1, true);
    c.setIndustryForTest(ag::kPlayer, 50.0);
    c.advance();
    CHECK(c.starOwner(1) == 1);                        // no modules: no attempt
    CHECK(!anyCaptureEvent(c));
    // The gun-engagement price still rides (t204 per-engagement charge);
    // the clamp must NOT fire (resolver never ran).
    CHECK(!c.dipStateAt(0).atWar);
}

// T5 (producer gate): modules accrue ONLY once the Invasion Module row is
// research-legal (gizmos.txt resReq 8 == Spectral Analysis); at scenario
// init the ledger is zero for every owner (the day-20 operand does not
// exist). Cap-6 census bound is the producer constant (ships.md S69(a)).
TEST(module_producer_gates_tD34) {
    REQUIRE_DATA();
    auto c = fixtureD34();
    // No research, no shipyard: the ledger stays 0 across turns.
    for (int i = 0; i < 5; ++i) c.advance();
    CHECK(c.invasionModules(ag::kPlayer) == 0);
    CHECK(c.invasionModules(1) == 0);
}

// T6 (forced leg, the ONLY pin where count <= shields AND capture happens):
// SA_SuperMarines count(1) vs Surface Shield(1) -> 0x3a46a would be the fail
// tail for a normal race; the ability byte == 0 forces need := 1 (0x3a34e)
// and the capture lands, consuming exactly one module.
TEST(supermarines_forced_through_shield_tD34) {
    REQUIRE_DATA();
    auto c = fixtureD34(static_cast<int>(0));          // specnum 0 = Minions
    c.setAbilityForTest(ag::kPlayer, ag::SpeciesAbility::SuperMarines);
    c.addItemForTest(1, itemIdD34("Surface Shield"));  // shields = 1 >= count
    c.setWarForTest(ag::kPlayer, 1, true);
    c.setIndustryForTest(ag::kPlayer, 50.0);
    c.setInvasionModulesForTest(ag::kPlayer, 1);
    c.advance();
    CHECK(c.starOwner(1) == ag::kPlayer);              // forced leg fired
    CHECK(c.invasionModules(ag::kPlayer) == 0);        // need=1 consumed
    CHECK(anyCaptureEvent(c));
}
