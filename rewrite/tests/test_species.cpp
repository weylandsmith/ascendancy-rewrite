// Species special abilities: roster cross-check + per-ability behaviour.
// Effect citations: extracted/ascend00/help.txt L1713-2511 through
// docs/re/abilities.md; roster docs/re/species.md. Numeric effects are
// [documented default] there — tests assert BEHAVIOUR (event fired, flag set,
// war ended), never a memorised constant beyond the documented ones.
#include "game/campaign.h"
#include "game/species.h"
#include "harness.h"

#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <filesystem>
#include <string>
#include <vector>

#ifndef ASCENDANCY_SOURCE_DIR
#define ASCENDANCY_SOURCE_DIR "."
#endif

namespace {
namespace ag = ascend::game;
namespace fs = std::filesystem;

const fs::path kDir = fs::path(ASCENDANCY_SOURCE_DIR) / "extracted" / "ascend00";

// Loaded once; Campaign stores pointers into tree/items/gizmos, so these
// must outlive every campaign (function-local statics, never temporaries).
struct Shared {
    ag::ResearchTree tree;
    std::vector<ag::PlanetItem> items;
    std::vector<ag::Gizmo> gizmos;
    std::vector<ag::SpeciesInfo> roster;
    std::vector<ag::DipFile> dip;  // all 21, indexed by specnum
    ag::StarStats stats;
    std::vector<std::string> names;
};
Shared& shared() {
    static Shared s = [] {
        Shared x;
        std::string err;
        x.tree = ag::ResearchTree::loadFromFile((kDir / "restree.txt").string(), err);
        x.items = ag::loadPlanItems((kDir / "planitem.txt").string(), err);
        if (x.items.size() != 39) std::abort();
        x.gizmos = ag::loadGizmos((kDir / "gizmos.txt").string(), err);
        if (x.gizmos.size() != 76) std::abort();
        if (!ag::loadAbilities(kDir.string(), &x.roster, &err)) std::abort();
        auto st = ag::StarStats::load(kDir / "starstat.txt", &err);
        if (!st) std::abort();
        x.stats = *st;
        x.names = ag::loadStarNames(kDir / "names.txt", &err);
        if (x.names.empty()) std::abort();
        for (int i = 0; i < 21; ++i) {
            ag::DipFile df;
            char p[256];
            std::snprintf(p, sizeof(p), "%s/race%02d.dip", kDir.string().c_str(), i);
            if (!df.loadFromFile(p, &err)) std::abort();
            x.dip.push_back(std::move(df));
        }
        return x;
    }();
    return s;
}

// Build a campaign where AI owner k (1-based) has ability `ab` and no other
// owner has one (unless playerSpecies >= 0, which also grants the player's).
ag::Campaign makeCrafted(unsigned seed, int aiOwner, ag::SpeciesAbility ab,
                         int playerSpecies = -1, int aiCount = 6) {
    Shared& s = shared();
    std::vector<ag::SpeciesAbility> abilities(aiCount, ag::SpeciesAbility::Unknown);
    abilities[aiOwner - 1] = ab;
    ag::CampaignConfig cfg;
    cfg.seed = seed;
    cfg.aiCount = aiCount;
    cfg.playerSpecies = playerSpecies;
    ag::MapConfig mc;
    mc.seed = seed;
    ag::Galaxy g = ag::MapGenerator(mc, s.stats, s.names).generate();
    // Use the first aiCount dip files (roster-order; contents only feed the
    // DIPVALUES policy model here — abilities are set explicitly above).
    std::vector<ag::DipFile> dip;
    for (int i = 0; i < aiCount; ++i) dip.push_back(s.dip[i]);
    std::string err;
    ag::Campaign c(cfg, g, &s.tree, s.items, s.gizmos, std::move(dip), abilities, &err);
    return c;
}

bool hasEvent(const ag::Campaign& c, const std::string& needle) {
    for (const auto& e : c.events())
        if (e.text.find(needle) != std::string::npos) return true;
    return false;
}
int homeOf(const ag::Campaign& c, int owner) {
    for (size_t s = 0; s < c.galaxy().stars.size(); ++s)
        if (c.starOwner((int)s) == owner) return (int)s;
    return -1;
}
}  // namespace

TEST(species_roster_three_source) {
    std::vector<ag::SpeciesInfo> r;
    std::string err;
    CHECK(ag::loadAbilities(kDir.string(), &r, &err));
    CHECK(r.size() == 21);
    // Tokened-header identities match help.txt by position (probe gate 3m
    // asserts all 20; spot-check the edges + the tokenless Orfa entry).
    CHECK(r[0].ability == ag::SpeciesAbility::SuperMarines);
    CHECK(r[1].ability == ag::SpeciesAbility::DoubleHull);
    CHECK(r[2].ability == ag::SpeciesAbility::BuildOnBlack);  // tokenless dip header
    CHECK(r[10].ability == ag::SpeciesAbility::Cornucopia);
    CHECK(r[20].ability == ag::SpeciesAbility::IndustryBoost);
    for (const auto& si : r) CHECK(si.ability != ag::SpeciesAbility::Unknown);
}

TEST(species_roster_rejects_bad_dir) {
    std::vector<ag::SpeciesInfo> r;
    std::string err;
    CHECK(!ag::loadAbilities("/nonexistent-ascendancy-dir", &r, &err));
    CHECK(!err.empty());
}

TEST(species_charge_split_verified) {
    // 7 passive blocks (no amass line) [verified help.txt; gate 3m re-checks
    // the split against the file]; 14 charged at the 30-turn documented
    // default (kNotes cites the choice).
    const int passive[] = {0, 1, 2, 3, 4, 15, 18};
    for (int p : passive) {
        auto a = static_cast<ag::SpeciesAbility>(p);
        CHECK(!ag::abilityIsCharged(a));
        CHECK(ag::abilityChargeTurns(a) == 0);
    }
    int charged = 0;
    for (int i = 0; i < (int)ag::SpeciesAbility::kCount; ++i) {
        auto a = static_cast<ag::SpeciesAbility>(i);
        if (ag::abilityIsCharged(a)) { ++charged; CHECK(ag::abilityChargeTurns(a) == 30); }
    }
    CHECK(charged == 14);
    CHECK(ag::abilityFromToken("SA_BuildOnBlack") == ag::SpeciesAbility::BuildOnBlack);
    CHECK(ag::abilityFromToken("SA_Nonsense") == ag::SpeciesAbility::Unknown);
}

TEST(species_every_token_has_effect_or_filed_noop) {
    // C++ mirror of gate 3m: no token is silently unhandled, and every note
    // cites a help.txt line block.
    int filedNoops = 0;
    for (int i = 0; i < (int)ag::SpeciesAbility::kCount; ++i) {
        const char* n = ag::abilityEffectNote(static_cast<ag::SpeciesAbility>(i));
        CHECK(n && *n);
        CHECK(std::strstr(n, "[help.txt L") != nullptr);
        if (std::strstr(n, "FILED NO-OP")) ++filedNoops;
    }
    CHECK(filedNoops == 4);  // BuildOnBlack + the three knowledge abilities
}

TEST(species_charged_ability_fires_on_schedule) {
    // charge 30 -> first activation on turn 30 [documented default].
    auto c = makeCrafted(11, 1, ag::SpeciesAbility::HealShips);
    for (int t = 0; t < 29; ++t) c.advance();
    CHECK(!hasEvent(c, "SA_HealShips"));
    c.advance();  // turn 30
    CHECK(hasEvent(c, "SA_HealShips"));
    CHECK(c.chargeFor(1) == 30);  // reset for the next cycle
}

TEST(species_force_peace_ends_the_owner_wars) {
    auto c = makeCrafted(12, 1, ag::SpeciesAbility::ForcePeace);
    CHECK(c.atWar(1, 0));  // free-for-all start
    for (int t = 0; t < 30; ++t) c.advance();
    CHECK(!c.atWar(1, 0));
    CHECK(hasEvent(c, "forced peace"));
}

TEST(species_shield_planets_blocks_captures_that_turn) {
    auto c = makeCrafted(13, 1, ag::SpeciesAbility::ShieldPlanets);
    for (int t = 0; t < 30; ++t) c.advance();
    CHECK(c.invincibleStar(homeOf(c, 1)));
    CHECK(hasEvent(c, "colonies invincible"));
    c.advance();  // next turn clears the one-shot flag
    CHECK(!c.invincibleStar(homeOf(c, 1)));
}

TEST(species_block_star_lanes_flag_set_on_activation) {
    auto c = makeCrafted(14, 1, ag::SpeciesAbility::BlockStarLanes);
    for (int t = 0; t < 30; ++t) c.advance();
    CHECK(c.laneBlockedStar(homeOf(c, 1)));
    CHECK(hasEvent(c, "blocked lanes"));
}

TEST(species_more_max_pop_raises_caps_and_cornucopia_adds_pros) {
    auto c = makeCrafted(15, 1, ag::SpeciesAbility::MoreMaxPop);
    for (int t = 0; t < 30; ++t) c.advance();
    CHECK(c.popCapBonusFor(homeOf(c, 1)) > 0);
    auto d = makeCrafted(16, 1, ag::SpeciesAbility::Cornucopia);
    for (int t = 0; t < 30; ++t) d.advance();
    bool enriched = false;
    for (size_t s = 0; s < d.galaxy().stars.size(); ++s)
        if (d.richProsFor((int)s) > 0) enriched = true;
    CHECK(enriched);
    CHECK(hasEvent(d, "enriched"));
}

TEST(species_steal_research_fires_and_is_capped_by_ownership_rule) {
    auto c = makeCrafted(17, 1, ag::SpeciesAbility::StealResearch);
    const int before = c.techsOwned(1);
    for (int t = 0; t < 30; ++t) c.advance();
    CHECK(hasEvent(c, "SA_StealResearch"));
    CHECK(c.techsOwned(1) >= before);  // never loses techs
    // Steal fires again after recharge and must not grow unboundedly beyond
    // tree size: run 30 more turns, still a legal count.
    for (int t = 0; t < 30; ++t) c.advance();
    CHECK(c.techsOwned(1) <= 106);  // 66 main + 40 variant rows (research.md)
}

TEST(species_player_species_selection) {
    // Chronomyst (specnum 18, passive FastLaneTravel): the player gets it and
    // no AI keeps a duplicate of the player's own species set-up.
    auto c = makeCrafted(31, 1, ag::SpeciesAbility::Unknown, /*playerSpecies=*/18);
    CHECK(c.abilityOf(0) == ag::SpeciesAbility::FastLaneTravel);
    std::string line = (c.advance(), c.traceLine());
    CHECK(line.find("SA_FastLaneTravel") != std::string::npos);
    // Passive FastLaneTravel only shows its effect once a drive is researched
    // (hops gate, ships.md §3); driveHopsFor must stay inside its clamp.
    for (int t = 0; t < 80 && c.driveHopsFor(0) == 0; ++t) c.advance();
    CHECK(c.driveHopsFor(0) >= 1);
    CHECK(c.driveHopsFor(0) <= 3);
}

TEST(species_unknown_ability_campaign_is_silent) {
    auto c = makeCrafted(7, 1, ag::SpeciesAbility::Unknown);
    for (int t = 0; t < 95; ++t) c.advance();  // past two full charge cycles
    for (const auto& e : c.events()) CHECK(e.text.find("SA_") == std::string::npos);
}

TEST(species_campaign_with_abilities_reaches_victory) {
    // The abilities must not deadlock the loop (no-victory-in-600 is the bar
    // earlier turn-loop bugs died on).
    auto c = makeCrafted(2024, 1, ag::SpeciesAbility::SuperMarines);
    ag::Victory v = ag::Victory::None;
    int t = 0;
    for (; t < 600 && v == ag::Victory::None; ++t) v = c.advance();
    CHECK(v != ag::Victory::None);
}

TEST(species_determinism_with_abilities) {
    auto a = makeCrafted(555, 2, ag::SpeciesAbility::SapAlienPower);
    auto b = makeCrafted(555, 2, ag::SpeciesAbility::SapAlienPower);
    for (int t = 0; t < 120 && !a.over(); ++t) {
        a.advance();
        b.advance();
        if (a.traceLine() != b.traceLine()) break;
    }
    CHECK(a.traceLine() == b.traceLine());
    CHECK(a.turn() == b.turn());
}
