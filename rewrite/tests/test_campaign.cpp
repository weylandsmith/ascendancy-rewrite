// Campaign turn-loop tests. Constants: docs/re/turnloop.md (end-*.txt vendor
// comments, planitem rows, gizmo levels) — never memory (STATE rule).
#include "game/campaign.h"
#include "harness.h"

#include <cstdio>
#include <cstdlib>
#include <filesystem>
#include <string>

#ifndef ASCENDANCY_SOURCE_DIR
#define ASCENDANCY_SOURCE_DIR "."
#endif

namespace {
namespace ag = ascend::game;
namespace fs = std::filesystem;

const fs::path kRepo = ASCENDANCY_SOURCE_DIR;

struct Tables {
    ag::StarStats stats;
    std::vector<std::string> names;
    ag::ResearchTree tree;
    std::vector<ag::PlanetItem> items;
    std::vector<ag::Gizmo> gizmos;
    std::vector<ag::DipFile> ai;
};

Tables& tables() {
    static Tables t = [] {
        Tables x;
        std::string err;
        auto st = ag::StarStats::load(kRepo / "extracted/ascend00/starstat.txt", &err);
        if (!st) std::abort();
        x.stats = *st;
        x.names = ag::loadStarNames(kRepo / "extracted/ascend00/names.txt", &err);
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

ag::Campaign makeCampaign(unsigned seed, int aiCount = 6, bool ffa = true) {
    ag::CampaignConfig cfg;
    cfg.seed = seed;
    cfg.aiCount = aiCount;
    cfg.freeForAll = ffa;
    ag::MapConfig mc;
    mc.seed = seed;
    ag::Galaxy g = ag::MapGenerator(mc, tables().stats, tables().names).generate();
    std::string err;
    return ag::Campaign(cfg, g, &tables().tree, tables().items, tables().gizmos,
                        tables().ai, &err);
}

}  // namespace

TEST(campaign_homes_distinct) {
    auto c = makeCampaign(7);
    for (int o = 0; o <= 6; ++o) CHECK(c.starsOwned(o) == 1);
    CHECK(c.turn() == 0);
    CHECK(c.victory() == ag::Victory::None);
}

TEST(campaign_total_owned_grows) {
    // Expansion: total claimed stars must strictly grow over 20 turns
    // (some owner always has surplus industry; turnloop.md §4).
    auto c = makeCampaign(42);
    int totalPrev = 7;
    for (int t = 0; t < 20 && !c.over(); ++t) {
        c.advance();
        int total = 0;
        for (int o = 0; o <= 6; ++o) total += c.starsOwned(o);
        CHECK(total >= totalPrev);
        totalPrev = total;
    }
    CHECK(totalPrev > 7);
}

TEST(campaign_research_progresses) {
    auto c = makeCampaign(3);
    for (int t = 0; t < 40 && !c.over(); ++t) c.advance();
    CHECK(c.techsOwned(ag::kPlayer) > 0);  // home lab researches within 40 turns
}

TEST(campaign_deterministic_same_seed) {
    auto a = makeCampaign(1234);
    auto b = makeCampaign(1234);
    for (int t = 0; t < 30 && !a.over(); ++t) {
        a.advance();
        b.advance();
        CHECK(a.traceLine() == b.traceLine());
        CHECK(a.victory() == b.victory());
    }
}

TEST(campaign_reaches_a_victory) {
    // CONTRACT: a seeded run reaches a victory condition (docs/PLAYTHROUGH.md
    // is generated from such a run). Combat (turnloop.md §5) makes Control or
    // LastAlive reachable; 400-turn cap bounds the search.
    bool anyVictory = false;
    for (unsigned seed : {1u, 2u, 2024u}) {
        auto c = makeCampaign(seed);
        for (int t = 0; t < 400 && !c.over(); ++t) c.advance();
        if (c.over()) { anyVictory = true; break; }
    }
    CHECK(anyVictory);
}

TEST(campaign_victory_files_named) {
    CHECK(std::string(ag::victoryConditionFile(ag::Victory::Control)) == "end-ctrl");
    CHECK(std::string(ag::victoryConditionFile(ag::Victory::Extinct)) == "end-xtnc");
    CHECK(std::string(ag::victoryConditionFile(ag::Victory::LastAlive)) == "end-dest");
    CHECK(std::string(ag::victoryName(ag::Victory::Control)) == "Control");
}

TEST(campaign_advance_after_victory_is_noop) {
    auto c = makeCampaign(1);
    ag::Victory v = ag::Victory::None;
    for (int t = 0; t < 400; ++t) {
        v = c.advance();
        if (v != ag::Victory::None) break;
    }
    if (v == ag::Victory::None) { CHECK(false); return; }  // contract data
    int turn = c.turn();
    size_t evs = c.events().size();
    c.advance();
    CHECK(c.turn() == turn);
    CHECK(c.events().size() == evs);
}
